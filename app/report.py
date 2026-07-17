import html
import re
from pathlib import Path

from .models import Analysis


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def render_report(source: str, validation_name: str, presentation: str, ledger: dict, analysis: Analysis,
                  guidance: dict, template_path: Path) -> str:
    groups = {item["id"]: item for item in ledger["findingGroups"]}
    counts = ledger["counts"]
    metrics = "".join(
        f'<div class="metric {kind}"><strong>{counts.get(kind, 0)}</strong><span>{kind.title()}</span></div>'
        for kind in ("error", "warning", "info", "pass")
    )
    priorities = "".join(f"<li><span>{esc(item)}</span></li>" for item in analysis.priorities)
    fix_plan = "".join(
        f'<li><a href="#{esc(recipe.id)}"><strong>{index}</strong><span>{esc(recipe.title)}</span>'
        f'<span class="fix-count">{sum(groups[g]["occurrenceCount"] for g in recipe.finding_group_ids)} occurrences</span></a></li>'
        for index, recipe in enumerate(analysis.recipes, 1)
    ) or "<li><span>No repair recipes are required.</span></li>"

    cards = []
    for index, recipe in enumerate(analysis.recipes, 1):
        linked = [groups[group_id] for group_id in recipe.finding_group_ids]
        severity = "error" if any(g["severity"] == "error" for g in linked) else "warning"
        guidance_cards = []
        for guidance_id in recipe.guidance_ids:
            item = guidance[guidance_id]
            quote = (f'<blockquote>“{esc(item["Verified excerpt"])}”</blockquote>'
                     if item.get("Verified excerpt") else "")
            link = item.get("Link", "")
            guidance_cards.append(
                f'<aside class="guidance"><h4>BBC guidance · {esc(guidance_id)}</h4>'
                f'<p>{esc(item.get("Guidance", ""))}</p>{quote}'
                f'<p><a href="{esc(link)}">Open this section of the BBC Subtitle Guidelines</a></p></aside>'
            )
        cards.append(f'''<article class="finding {severity}" id="{esc(recipe.id)}">
<div class="finding-head"><span class="finding-number">{index:02d}</span><div><h3>{esc(recipe.title)}</h3><p class="finding-code">Covers {esc(", ".join(recipe.finding_group_ids))}</p></div><span class="badge">{severity}</span></div>
<div class="finding-body"><p class="impact"><strong>Why this matters:</strong> {esc(recipe.impact)}</p>
<div class="analysis-grid"><section class="panel"><h4>Likely cause</h4><p>{esc(recipe.likely_cause)}</p></section><section class="panel"><h4>Recommended action</h4><p>{esc(recipe.action)}</p></section></div>
<section class="panel"><h4>Contextual correction</h4><span class="change-label">Before</span><pre><code>{esc(recipe.before_ttml)}</code></pre><span class="change-label">Proposed — revalidate after applying</span><pre><code>{esc(recipe.proposed_ttml)}</code></pre></section>
<p class="expected"><strong>Expected on revalidation:</strong> {esc(recipe.expected_outcome)}</p>{''.join(guidance_cards)}</div></article>''')

    rows = []
    for group in ledger["findingGroups"]:
        locations = "<ol>" + "".join(
            f'<li value="{occ["order"]}"><code>{esc(occ["id"])}</code> {esc(occ["location"])}</li>'
            for occ in group["occurrences"]
        ) + "</ol>"
        rows.append(f'<tr><td>{esc(group["id"])}</td><td>{esc(group["severity"])}</td><td><code>{esc(group["code"])}</code></td><td>{esc(group["message"])}</td><td>{locations}</td></tr>')
    record = '<table class="validator-record"><thead><tr><th>Group</th><th>Severity</th><th>Code</th><th>Message</th><th>Every location</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    editorial = ""
    if analysis.editorial_observations:
        editorial = '<section><div class="section-heading"><h2>Editorial observations</h2><p>Helpful observations, kept separate from authoritative validator findings.</p></div><ul>' + "".join(f"<li>{esc(x)}</li>" for x in analysis.editorial_observations) + "</ul></section>"

    replacements = {
        "{{REPORT_TITLE}}": f"TTML validation guide — {esc(source)}",
        "{{EXECUTIVE_SUMMARY}}": esc(analysis.executive_summary),
        "{{REPORT_METADATA}}": f"<span>Source: <strong>{esc(source)}</strong></span><span>Presentation: <strong>{esc(presentation.title())}</strong></span>",
        "{{DELIVERY_STATUS}}": esc(analysis.delivery_status),
        "{{SEVERITY_METRICS}}": metrics, "{{PRIORITY_ACTIONS}}": priorities,
        "{{PROVENANCE}}": f"<p>Original TTML: <strong>{esc(source)}</strong></p><p>Presentation format selected by user: <strong>{esc(presentation.title())}</strong></p><p>Validator output: <strong>{esc(validation_name)}</strong></p>",
        "{{FIX_PLAN}}": fix_plan, "{{FIX_RECIPES}}": "".join(cards),
        "{{EDITORIAL_OBSERVATIONS}}": editorial, "{{VALIDATOR_RECORD}}": record,
        "{{LIMITATIONS}}": "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in analysis.limitations) + "</ul>",
        "{{SOURCES}}": '<p><a href="https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/">BBC Subtitle Guidelines</a>. Each selected excerpt above links to its verified section.</p>',
        "{{FOOTER_NOTE}}": f"Generated from {esc(source)}. Apply proposed edits to a copy and revalidate.",
    }
    output = template_path.read_text(encoding="utf-8")
    for token, value in replacements.items():
        output = output.replace(token, value)
    leftovers = re.findall(r"\{\{[A-Z_]+\}\}", output)
    if leftovers:
        raise ValueError(f"Unpopulated report tokens: {leftovers}")
    return output
