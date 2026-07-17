#!/usr/bin/env python3
"""Compare claimed browser-validator rules with the official Python validator."""

import argparse
import json
import re
import shlex
import subprocess
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "standalone" / "rule-manifest.json"
SUPPORTED_CODES = set(json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["claimedCodes"])


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = ""

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append(" ".join(self.cell.split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def official_results(source: Path, presentation: str, validator_command: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "official.json"
        command = shlex.split(validator_command) + [
            "-ttml_in", str(source), "-results_out", str(output)
        ]
        if presentation == "vertical":
            command.append("-vertical")
        command.append("-json")
        subprocess.run(
            command,
            check=False, capture_output=True, text=True,
        )
        if not output.exists():
            raise RuntimeError("The official validator did not produce JSON.")
        return json.loads(output.read_text(encoding="utf-8"))


def browser_results(report: Path) -> list[dict]:
    parser = TableParser()
    parser.feed(report.read_text(encoding="utf-8"))
    results = []
    for row in parser.rows:
        if len(row) == 5 and row[0].isdigit() and row[1] in {"Error", "Warning"}:
            results.append({"status": 3 if row[1] == "Error" else 2,
                            "code": row[2], "message": row[3], "location": row[4]})
        elif len(row) == 4 and row[0] in {"Error", "Warning"}:
            results.append({"status": 3 if row[0] == "Error" else 2,
                            "code": row[1], "message": row[2], "location": row[3]})
    if not results:
        raise RuntimeError("No standalone occurrence records found in the report.")
    return results


def expanded_signature(results: list[dict], official: bool) -> Counter:
    output = Counter()
    for item in results:
        if item.get("code") not in SUPPORTED_CODES or int(item.get("status", -1)) < 2:
            continue
        count = 1
        if official:
            match = re.fullmatch(r"(\d+) locations", str(item.get("location", "")))
            if match:
                count = int(match.group(1))
        output[(int(item["status"]), item["code"], item["message"])] += count
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ttml", required=True, type=Path)
    parser.add_argument("--standalone-report", required=True, type=Path)
    parser.add_argument("--presentation", choices=("horizontal", "vertical"), required=True)
    parser.add_argument("--validator-command", default="validate-ttml")
    args = parser.parse_args()
    expected = expanded_signature(
        official_results(args.ttml, args.presentation, args.validator_command), True
    )
    actual = expanded_signature(browser_results(args.standalone_report), False)
    keys = sorted(set(expected) | set(actual), key=lambda item: (item[1], item[0], item[2]))
    mismatches = []
    for key in keys:
        if expected[key] != actual[key]:
            mismatches.append((key, expected[key], actual[key]))
    print(f"Claimed rule signatures: official={sum(expected.values())}, browser={sum(actual.values())}")
    if mismatches:
        for (status, code, message), wanted, got in mismatches:
            print(f"MISMATCH {code} status={status}: official={wanted}, browser={got}\n  {message}")
        return 1
    print("PASS: all claimed rule signatures and occurrence counts match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
