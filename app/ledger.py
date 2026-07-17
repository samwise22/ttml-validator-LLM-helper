from collections import OrderedDict


STATUS = {0: "pass", 1: "info", 2: "warning", 3: "error"}


def build_ledger(results: list[dict]) -> dict:
    groups: OrderedDict[tuple, dict] = OrderedDict()
    counts = {name: 0 for name in STATUS.values()}

    for index, item in enumerate(results, start=1):
        status = int(item.get("status", -1))
        severity = STATUS.get(status, f"status-{status}")
        counts[severity] = counts.get(severity, 0) + 1
        code = str(item.get("code", ""))
        message = str(item.get("message", ""))
        key = (status, code, message)

        if key not in groups:
            groups[key] = {
                "id": f"G-{len(groups) + 1:04d}",
                "status": status,
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

    return {
        "counts": counts,
        "occurrenceCount": len(results),
        "findingGroups": output,
        "requiredAnalysisGroupIds": [
            group["id"] for group in output if group["requiresAnalysis"]
        ],
    }
