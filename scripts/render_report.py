#!/usr/bin/env python3
"""Validate LLM analysis and render a deterministic standalone HTML report."""

import argparse
import html
import json
import re
import sys
from pathlib import Path


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def guidance_entries(markdown: str) -> dict[str, dict[str, str]]:
    entries = {}
    chunks = re.split(r"(?m)^### ", markdown)[1:]
    for chunk in chunks:
        lines = chunk.splitlines()
        guidance_id = lines[0].strip()
        data = {}
        for line in lines[1:]:
            match = re.match(r"^- (Guidance|Verified excerpt|Link):\s*(.*)$", line)
            if match:
                data[match.group(1)] = match.group(2).strip().strip("“”")
        entries[guidance_id] = data
    return entries


def validate(package: dict, analysis: dict) -> None:
    errors = []
    required_top = {
        "schemaVersion", "packageId", "sourceFilename", "executiveSummary",
        "deliveryStatus", "priorities", "recipes", "editorialObservations", "limitations",
    }
    missing = required_top - analysis.keys()
    if missing:
        errors.append("Missing analysis fields: " + ", ".join(sorted(missing)))
    if analysis.get("schemaVersion") != "1.0":
        errors.append("schemaVersion must be 1.0")
    if analysis.get("packageId") != package.get("packageId"):
        errors.append("packageId does not match the package")
    if analysis.get("sourceFilename") != package.get("source", {}).get("filename"):
        errors.append("sourceFilename does not match the original TTML filename")
    if not isinstance(analysis.get("priorities"), list) or len(analysis.get("priorities", [])) > 3:
        errors.append("priorities must be an array containing at most three items")
    if not isinstance(analysis.get("recipes"), list):
        errors.append("recipes must be an array")
        recipes = []
    else:
        recipes = analysis["recipes"]

    known_groups = {g["id"] for g in package["validation"]["findingGroups"]}
    required_groups = set(package["validation"]["requiredAnalysisGroupIds"])
    covered = []
    valid_guidance = set(guidance_entries(package["bbcGuidance"]))
    recipe_fields = {
        "id", "title", "findingGroupIds", "impact", "likelyCause", "action",
        "beforeTtml", "proposedTtml", "expectedOutcome", "guidanceIds",
    }
    for index, recipe in enumerate(recipes, start=1):
        if not isinstance(recipe, dict):
            errors.append(f"Recipe {index} is not an object")
            continue
        absent = recipe_fields - recipe.keys()
        if absent:
            errors.append(f"Recipe {index} missing fields: {', '.join(sorted(absent))}")
        ids = recipe.get("findingGroupIds", [])
        if not isinstance(ids, list) or not ids:
            errors.append(f"Recipe {index} must contain findingGroupIds")
            ids = []
        covered.extend(ids)
        unknown = set(ids) - known_groups
        if unknown:
            errors.append(f"Recipe {index} contains unknown finding groups: {sorted(unknown)}")
        unknown_guidance = set(recipe.get("guidanceIds", [])) - valid_guidance
        if unknown_guidance:
            errors.append(f"Recipe {index} contains unknown guidance IDs: {sorted(unknown_guidance)}")

    missing_groups = required_groups - set(covered)
    duplicate_groups = sorted({group_id for group_id in covered if covered.count(group_id) > 1})
    if missing_groups:
        errors.append("Actionable groups not covered: " + ", ".join(sorted(missing_groups)))
    if duplicate_groups:
        errors.append("Actionable groups covered more than once: " + ", ".join(duplicate_groups))
    if set(covered) - required_groups:
        errors.append("Recipes may cover only required actionable groups")
    if errors:
        raise ValueError("\n".join(errors))


def render_guidance(ids: list[str], entries: dict[str, dict[str, str]]) -> str:
    cards = []
    for guidance_id in ids:
        item = entries[guidance_id]
        quote = f'<blockquote>“{esc(item["Verified excerpt"])}”</blockquote>' if item.get("Verified excerpt") else ""
        link = item.get("Link", "")
        cards.append(
            f'<aside class="guidance"><h4>BBC guidance · {esc(guidance_id)}</h4>'
            f'<p>{esc(item.get("Guidance", ""))}</p>{quote}'
            f'<p><a href="{esc(link)}">Open the relevant BBC Subtitle Guidelines section</a></p></aside>'
        )
    return "".join(cards)


def render(package: dict, analysis: dict, template: str) -> str:
    source = package["source"]["filename"]
    groups = {g["id"]: g for g in package["validation"]["findingGroups"]}
    counts = package["validation"]["counts"]
    guidance = guidance_entries(package["bbcGuidance"])

    metrics = "".join(
        f'<div class="metric {kind}"><strong>{int(counts.get(kind, 0))}</strong><span>{esc(kind.title())}</span></div>'
        for kind in ("error", "warning", "info", "pass")
    )
    priorities = "".join(f"<li><span>{esc(item)}</span></li>" for item in analysis["priorities"])
    fix_plan = "".join(
        f'<li><a href="#{esc(recipe["id"])}"><strong>{index}</strong><span>{esc(recipe["title"])}</span>'
        f'<span class="fix-count">{sum(groups[g]["occurrenceCount"] for g in recipe["findingGroupIds"])} findings</span></a></li>'
        for index, recipe in enumerate(analysis["recipes"], start=1)
    )

    recipes = []
    for index, recipe in enumerate(analysis["recipes"], start=1):
        linked = [groups[group_id] for group_id in recipe["findingGroupIds"]]
        severity = "error" if any(g["severity"] == "error" for g in linked) else "warning"
        refs = ", ".join(recipe["findingGroupIds"])
        recipes.append(f'''
<article class="finding {severity}" id="{esc(recipe['id'])}">
  <div class="finding-head"><span class="finding-number">{index:02d}</span><div><h3>{esc(recipe['title'])}</h3><p class="finding-code">Covers {esc(refs)}</p></div><span class="badge">{severity}</span></div>
  <div class="finding-body">
    <p class="impact"><strong>Why this matters:</strong> {esc(recipe['impact'])}</p>
    <div class="analysis-grid"><section class="panel"><h4>Likely cause</h4><p>{esc(recipe['likelyCause'])}</p></section><section class="panel"><h4>Recommended action</h4><p>{esc(recipe['action'])}</p></section></div>
    <section class="panel"><h4>Contextual correction</h4><span class="change-label">Before</span><pre><code>{esc(recipe['beforeTtml'])}</code></pre><span class="change-label">Proposed — revalidate after applying</span><pre><code>{esc(recipe['proposedTtml'])}</code></pre></section>
    <p class="expected"><strong>Expected on revalidation:</strong> {esc(recipe['expectedOutcome'])}</p>
    {render_guidance(recipe['guidanceIds'], guidance)}
  </div>
</article>''')

    rows = []
    for group in package["validation"]["findingGroups"]:
        locations = "<ol>" + "".join(
            f'<li value="{occ["order"]}"><code>{esc(occ["id"])}</code> {esc(occ["location"])}</li>'
            for occ in group["occurrences"]
        ) + "</ol>"
        rows.append(
            f'<tr id="record-{esc(group["id"])}"><td>{esc(group["id"])}</td><td>{esc(group["severity"])}</td>'
            f'<td><code>{esc(group["code"])}</code></td><td>{esc(group["message"])}</td><td>{locations}</td></tr>'
        )
    record = '<table class="validator-record"><thead><tr><th>Group</th><th>Severity</th><th>Code</th><th>Message</th><th>All locations in original order</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    limitations = "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in analysis["limitations"]) + "</ul>"
    editorial = ""
    if analysis["editorialObservations"]:
        editorial = '<section aria-labelledby="editorial-heading"><div class="section-heading"><h2 id="editorial-heading">Editorial observations</h2><p>Separate from validator findings.</p></div><ul>' + "".join(f"<li>{esc(x)}</li>" for x in analysis["editorialObservations"]) + "</ul></section>"

    replacements = {
        "{{REPORT_TITLE}}": f"TTML validation guide — {source}",
        "{{EXECUTIVE_SUMMARY}}": esc(analysis["executiveSummary"]),
        "{{REPORT_METADATA}}": f"<span>Source: <strong>{esc(source)}</strong></span><span>Package: <code>{esc(package['packageId'])}</code></span>",
        "{{DELIVERY_STATUS}}": esc(analysis["deliveryStatus"]),
        "{{SEVERITY_METRICS}}": metrics,
        "{{PRIORITY_ACTIONS}}": priorities,
        "{{PROVENANCE}}": f"<p>Original TTML: <strong>{esc(source)}</strong></p><p>Validator input: <strong>{esc(package['validation']['filename'])}</strong></p>",
        "{{FIX_PLAN}}": fix_plan,
        "{{FIX_RECIPES}}": "".join(recipes),
        "{{EDITORIAL_OBSERVATIONS}}": editorial,
        "{{VALIDATOR_RECORD}}": record,
        "{{LIMITATIONS}}": limitations,
        "{{SOURCES}}": '<p><a href="https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/">BBC Subtitle Guidelines</a></p>',
        "{{FOOTER_NOTE}}": f"Generated from {esc(source)}. Apply proposed edits to a copy and revalidate.",
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    leftovers = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", template)))
    if leftovers:
        raise ValueError("Unpopulated template tokens: " + ", ".join(leftovers))
    return template


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--errors", type=Path)
    args = parser.parse_args()
    source_name = args.package.name.removesuffix(".llm-package.json")
    output = args.output or args.package.with_name(f"{source_name}.validation-report.html")
    errors_path = args.errors or args.package.with_name(f"{source_name}.llm-analysis.errors.txt")
    try:
        package = load(args.package)
        analysis = load(args.analysis)
        validate(package, analysis)
        template_path = Path(__file__).resolve().parents[1] / "templates" / "report.html"
        output.write_text(render(package, analysis, template_path.read_text(encoding="utf-8")), encoding="utf-8")
        if errors_path.exists():
            errors_path.unlink()
        print(output)
        return 0
    except Exception as exc:
        errors_path.write_text(f"Report generation failed\n\n{exc}\n", encoding="utf-8")
        print(errors_path, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
