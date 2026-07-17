import json
import os
import subprocess
from pathlib import Path


def run_validator(source: Path, output: Path, vertical: bool) -> tuple[list[dict], int, str]:
    command = os.getenv("VALIDATOR_COMMAND", "validate-ttml").split()
    arguments = command + ["-ttml_in", str(source), "-results_out", str(output)]
    if vertical:
        arguments.append("-vertical")
    arguments.append("-json")
    completed = subprocess.run(
        arguments,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if not output.exists() or output.stat().st_size == 0:
        detail = (completed.stdout + "\n" + completed.stderr).strip()
        raise RuntimeError(f"Validator did not produce JSON. {detail}")
    results = json.loads(output.read_text(encoding="utf-8"))
    if not isinstance(results, list):
        raise RuntimeError("Validator JSON is not a list.")
    log = (completed.stdout + "\n" + completed.stderr).strip()
    return results, completed.returncode, log
