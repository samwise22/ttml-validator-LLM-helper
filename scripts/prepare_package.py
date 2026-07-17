#!/usr/bin/env python3
"""Create a self-contained LLM analysis package from TTML and validator JSON."""

import argparse
import hashlib
import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path


STATUS = {0: "pass", 1: "info", 2: "warning", 3: "error"}


def read_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_groups(results: list[dict]) -> tuple[list[dict], dict[str, int]]:
    groups: OrderedDict[tuple, dict] = OrderedDict()
    counts = {name: 0 for name in STATUS.values()}

    for index, item in enumerate(results, start=1):
        status_value = int(item.get("status", -1))
        severity = STATUS.get(status_value, f"status-{status_value}")
        counts[severity] = counts.get(severity, 0) + 1
        code = str(item.get("code", ""))
        message = str(item.get("message", ""))
        key = (status_value, code, message)

        if key not in groups:
            group_number = len(groups) + 1
            groups[key] = {
                "id": f"G-{group_number:04d}",
                "status": status_value,
                "severity": severity,
                "code": code,
                "message": message,
                "occurrences": [],
            }

        groups[key]["occurrences"].append(
            {
                "id": f"F-{index:04d}",
                "order": index,
                "location": str(item.get("location", "")),
            }
        )

    output = list(groups.values())
    for group in output:
        group["occurrenceCount"] = len(group["occurrences"])
        group["requiresAnalysis"] = (
            group["severity"] in {"warning", "error"}
            and not group["code"].endswith("_document_validity")
        )
    return output, counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ttml", required=True, type=Path)
    parser.add_argument("--validator", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--knowledge", type=Path)
    args = parser.parse_args()

    ttml_text = args.ttml.read_text(encoding="utf-8")
    results = read_json(args.validator)
    if not isinstance(results, list) or not all(isinstance(x, dict) for x in results):
        raise SystemExit("Validator JSON must be a list of objects.")

    groups, counts = build_groups(results)
    source_filename = args.ttml.name
    canonical = json.dumps(results, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256((source_filename + "\0" + ttml_text + "\0" + canonical).encode()).hexdigest()
    package_id = f"ttml-{digest[:20]}"
    output = args.output or args.ttml.with_name(f"{source_filename}.llm-package.json")

    knowledge_path = args.knowledge or Path(__file__).resolve().parents[1] / "knowledge" / "BBC-SUBTITLE-GUIDANCE.md"
    knowledge = knowledge_path.read_text(encoding="utf-8")
    required_groups = [g["id"] for g in groups if g["requiresAnalysis"]]

    package = {
        "schemaVersion": "1.0",
        "packageId": package_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "source": {"filename": source_filename, "ttml": ttml_text},
        "validation": {
            "filename": args.validator.name,
            "raw": results,
            "occurrenceCount": len(results),
            "counts": counts,
            "findingGroups": groups,
            "requiredAnalysisGroupIds": required_groups,
        },
        "bbcGuidance": knowledge,
        "task": {
            "purpose": "Analyse actionable validator groups and return structured fix recipes. Do not generate HTML.",
            "outputFilename": f"{source_filename}.llm-analysis.json",
            "requirements": [
                "Return one JSON object and no commentary.",
                "Repeat schemaVersion, packageId and sourceFilename exactly.",
                "Cover every requiredAnalysisGroupId in exactly one recipe.",
                "Use only findingGroupIds and BBC guidance IDs present in this package.",
                "Base proposed TTML on the supplied source and preserve unrelated markup.",
                "Do not copy, modify or recreate validator evidence.",
            ],
            "responseShape": {
                "schemaVersion": "1.0",
                "packageId": package_id,
                "sourceFilename": source_filename,
                "executiveSummary": "string",
                "deliveryStatus": "string",
                "priorities": ["string (maximum three)"],
                "recipes": [
                    {
                        "id": "R-001",
                        "title": "string",
                        "findingGroupIds": ["G-0001"],
                        "impact": "string",
                        "likelyCause": "string",
                        "action": "imperative string",
                        "beforeTtml": "contextual string",
                        "proposedTtml": "contextual string",
                        "expectedOutcome": "string",
                        "guidanceIds": ["registered ID"],
                    }
                ],
                "editorialObservations": [],
                "limitations": ["string"],
            },
        },
    }

    output.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
