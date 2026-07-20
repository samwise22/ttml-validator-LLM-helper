import json
import os
import traceback
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .analysis import analyse
from .bbc_import import BBCImportError, import_bbc_ttml
from .guidance import load_guidance
from .jobs import JobStore
from .ledger import build_ledger
from .report import render_report
from .validator import run_validator

BASE = Path(__file__).resolve().parents[1]
DATA = Path(os.getenv("APP_DATA_DIR", BASE / "data"))
STORE = JobStore(DATA / "jobs")
app = FastAPI(title="TTML Validation Guide")
app.mount("/static", StaticFiles(directory=BASE / "app" / "static"), name="static")


def process_job(job_id: str, source: Path, presentation: str) -> None:
    folder = source.parent
    validation = folder / f"{source.name}.validation.json"
    analysis_path = folder / f"{source.name}.analysis.json"
    report = folder / f"{source.name}.validation-report.html"
    try:
        STORE.update(job_id, status="working", stage="Validating TTML")
        results, return_code, validator_log = run_validator(source, validation, presentation == "vertical")
        ledger = build_ledger(results)
        STORE.update(job_id, stage="Creating a helpful review", counts=ledger["counts"])
        guidance = load_guidance(BASE / "knowledge" / "BBC-SUBTITLE-GUIDANCE.md")
        result = analyse(source.read_text(encoding="utf-8"), ledger, guidance, presentation)
        analysis_path.write_text(result.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
        STORE.update(job_id, stage="Building the report")
        report.write_text(render_report(source.name, validation.name, presentation, ledger, result, guidance,
                                        BASE / "templates" / "report.html"), encoding="utf-8")
        (folder / "validator.log").write_text(validator_log, encoding="utf-8")
        STORE.update(job_id, status="complete", stage="Ready", validatorReturnCode=return_code,
                     downloads={"report": report.name, "validation": validation.name,
                                "analysis": analysis_path.name, "source": source.name})
    except Exception as exc:
        (folder / "application.log").write_text(traceback.format_exc(), encoding="utf-8")
        STORE.update(job_id, status="failed", stage="Could not finish", error=str(exc))


@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(BASE / "app" / "static" / "index.html")


@app.get("/standalone", response_class=HTMLResponse)
def standalone():
    return FileResponse(BASE / "standalone" / "ttml-guide.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/import-bbc")
def import_bbc(url: str):
    try:
        imported = import_bbc_ttml(url)
    except BBCImportError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "pageUrl": imported.page_url,
        "programmePid": imported.programme_pid,
        "versionPid": imported.version_pid,
        "title": imported.title,
        "orientation": imported.orientation,
        "subtitlesUrl": imported.subtitles_url,
        "filename": f"{imported.version_pid}.xml",
        "ttml": imported.ttml,
    }


@app.post("/api/jobs", status_code=202)
async def create_job(background_tasks: BackgroundTasks, file: UploadFile = File(...),
                     presentation: str = Form(...)):
    filename = Path(file.filename or "").name
    if not filename or Path(filename).suffix.lower() not in {".xml", ".ttml"}:
        raise HTTPException(400, "Choose a TTML file ending in .xml or .ttml.")
    if presentation not in {"horizontal", "vertical"}:
        raise HTTPException(400, "Choose horizontal or vertical presentation.")
    limit = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024
    content = await file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(413, "That file is larger than the configured upload limit.")
    job_id = uuid.uuid4().hex
    source = DATA / "jobs" / job_id / filename
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(content)
    STORE.update(job_id, status="queued", stage="Waiting to start", sourceFilename=filename,
                 presentation=presentation)
    background_tasks.add_task(process_job, job_id, source, presentation)
    return {"id": job_id, "sourceFilename": filename, "presentation": presentation}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    job = STORE.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return job


@app.get("/api/jobs/{job_id}/report")
def view_report(job_id: str):
    return download(job_id, "report", inline=True)


@app.get("/api/jobs/{job_id}/download/{kind}")
def download(job_id: str, kind: str, inline: bool = False):
    job = STORE.get(job_id)
    if not job or job.get("status") != "complete" or kind not in job.get("downloads", {}):
        raise HTTPException(404, "File not available.")
    path = DATA / "jobs" / job_id / job["downloads"][kind]
    media = "text/html" if kind == "report" else "application/json" if kind in {"validation", "analysis"} else "application/xml"
    return FileResponse(path, media_type=media, filename=None if inline else path.name,
                        content_disposition_type="inline" if inline else "attachment")
