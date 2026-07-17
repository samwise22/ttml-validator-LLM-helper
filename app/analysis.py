import json
import os

from openai import OpenAI

from .models import Analysis


SYSTEM_PROMPT = """You are a senior TTML remediation specialist.
The validator evidence is authoritative and is rendered by application code.
Analyse only the supplied actionable finding groups. Group related causes into
practical recipes, use contextual source TTML, and select only supplied BBC
guidance IDs. Write for subtitle practitioners. Do not recreate validator data.
Every actionable group ID must appear exactly once across the recipes.
Treat errors as delivery-blocking and materially more urgent than warnings.
Prioritise error remediation before warning review. Do not describe warnings as
equivalent to errors or imply that a warning alone is a formal validation failure.
Proposed markup must preserve unrelated content and must be labelled through
the structured fields, not prose caveats."""


def _validate_coverage(analysis: Analysis, required: set[str], valid_guidance: set[str]) -> None:
    covered = [group_id for recipe in analysis.recipes for group_id in recipe.finding_group_ids]
    missing = required - set(covered)
    unknown = set(covered) - required
    duplicates = {item for item in covered if covered.count(item) > 1}
    selected_guidance = {
        guidance_id
        for recipe in analysis.recipes
        for guidance_id in recipe.guidance_ids
    }
    invalid_guidance = selected_guidance - valid_guidance
    problems = []
    if missing:
        problems.append(f"missing groups: {sorted(missing)}")
    if unknown:
        problems.append(f"unknown groups: {sorted(unknown)}")
    if duplicates:
        problems.append(f"duplicate groups: {sorted(duplicates)}")
    if invalid_guidance:
        problems.append(f"unknown guidance: {sorted(invalid_guidance)}")
    if problems:
        raise ValueError("Invalid model analysis: " + "; ".join(problems))


def analyse(ttml: str, ledger: dict, guidance: dict, presentation: str) -> Analysis:
    if os.getenv("ANALYSIS_MODE", "openai") == "mock":
        return mock_analysis(ledger)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    actionable = [
        group for group in ledger["findingGroups"] if group["requiresAnalysis"]
    ]
    compact_guidance = [
        {
            "id": item["id"],
            "signals": item.get("Signals", ""),
            "guidance": item.get("Guidance", ""),
        }
        for item in guidance.values()
    ]
    payload = {
        "presentationFormat": presentation,
        "sourceTtml": ttml,
        "actionableFindingGroups": actionable,
        "bbcGuidanceOptions": compact_guidance,
    }
    client = OpenAI()
    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        text_format=Analysis,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model did not return structured analysis.")
    result = response.output_parsed
    _validate_coverage(
        result,
        set(ledger["requiredAnalysisGroupIds"]),
        set(guidance),
    )
    return result


def mock_analysis(ledger: dict) -> Analysis:
    recipes = []
    for index, group in enumerate(
        (g for g in ledger["findingGroups"] if g["requiresAnalysis"]),
        start=1,
    ):
        recipes.append(
            {
                "id": f"R-{index:03d}",
                "title": group["code"].replace("_", " ").title(),
                "findingGroupIds": [group["id"]],
                "impact": "This validator finding requires review before delivery.",
                "likelyCause": "Mock analysis mode does not infer a source-specific cause.",
                "action": "Review the identified TTML location and apply the applicable requirement.",
                "beforeTtml": "<!-- Source context available in OpenAI mode -->",
                "proposedTtml": "<!-- Proposed correction available in OpenAI mode -->",
                "expectedOutcome": "Revalidate after making the confirmed correction.",
                "guidanceIds": [],
            }
        )
    return Analysis.model_validate(
        {
            "executiveSummary": "Validation completed. Mock analysis mode generated structural report content without calling OpenAI.",
            "deliveryStatus": "Review validator errors and warnings before delivery.",
            "priorities": ["Resolve validator errors", "Review warnings", "Revalidate"],
            "recipes": recipes,
            "editorialObservations": [],
            "limitations": ["Mock analysis mode was used; source-specific AI analysis is absent."],
        }
    )
