# TTML Validation Guide

A local browser application that turns a TTML subtitle file into a professional,
standalone HTML validation guide. It runs the BBC TTML Validator, preserves its
output losslessly, uses OpenAI for source-aware remediation analysis, and renders
the final report deterministically.

## Run the application

1. Open `.env` and place your OpenAI API key after `OPENAI_API_KEY=`.
2. From this directory, run `docker compose up --build`.
3. Open [http://localhost:8080](http://localhost:8080).
4. Select horizontal or vertical presentation, then drop an `.xml` or `.ttml`
   file into the page. This is an explicit editorial choice: the application
   shall not infer intended presentation from TTML styling.

The generated HTML, validator JSON, structured analysis, original TTML and logs
are stored under `data/jobs/`. Every output filename contains the complete
original input filename.

To exercise the complete workflow without making an API call, set
`ANALYSIS_MODE=mock` in `.env`. This produces a structurally complete but
deliberately generic report.

## Design guarantees

- Validator output is authoritative. Report code never asks the model to
  reproduce codes, severities, messages or locations.
- Every actionable finding group shall be covered exactly once by structured
  model analysis before a report is rendered.
- BBC excerpts and deep links come only from the curated repository knowledge
  base; the model may select them but may not create them.
- The HTML renderer is deterministic and the output is a standalone HTML5 file
  with embedded report CSS.
- Proposed corrections are guidance, not an automatic mutation of the source.

## Configuration

See `.env.example`. The Docker image pins the BBC validator source revision so a
deployment remains reproducible. This first release is intended for a trusted,
single-user local installation; do not expose it directly to the public internet.

A model-agnostic engineering standard and knowledge bundle for producing professional, standalone HTML5 reports from:

1. an original TTML subtitle document;
2. unmodified BBC TTML Validator output; and
3. the reusable specification, guidance, and template in this repository.

The validator is the authority for validation findings. An LLM may explain a finding and use the TTML source to infer a likely cause or propose a corrected example, but it must not alter validator codes, severities, messages, or locations.

## Repository map

- `spec/REPORTING-STANDARD.md` — normative model-independent requirements.
- `templates/report.html` — standalone HTML5 report contract and visual template.
- `knowledge/` — curated supporting material and source-verification records.
- `prompts/` — thin task instructions; these do not define the standard.
- `examples/` — synthetic inputs for development and evaluation.
- `scripts/build-dist.sh` — creates the three-attachment-friendly `DIST.md` bundle.

## Intended three-attachment workflow

Attach the original `.ttml`, the validator output, and generated `DIST.md`. Instruct the model to apply the bundled standard and return only the completed HTML report.

## Build

```sh
./scripts/build-dist.sh
```

The build is deterministic and uses only standard shell tools. `DIST.md` is generated and is not hand-edited.

## Two-Shortcut pipeline

The current pipeline keeps authoritative data and HTML generation out of the LLM:

1. `shortcuts/validate-and-prepare-package.sh` accepts an original TTML file, runs the BBC validator, and creates `<original-filename>.validation.json` plus `<original-filename>.llm-package.json`.
2. The user attaches the single package to an LLM. The embedded task requires a structured `<original-filename>.llm-analysis.json` response, not HTML.
3. `shortcuts/build-report-from-analysis.sh` accepts that analysis file, finds its sibling package, validates all IDs and actionable-group coverage, and renders `<original-filename>.validation-report.html` deterministically.

The complete original TTML filename, including its extension, is present in every derived filename and embedded in every structured artifact.

The Shortcut scripts currently contain local paths for the validator, helper checkout, and `uv` binary. Adjust those three variables if the repositories are installed elsewhere.

### Command-line equivalents

```sh
./scripts/prepare-package.sh \
  --ttml /path/programme.ttml \
  --validator /path/programme.ttml.validation.json

./scripts/render-report.sh \
  --package /path/programme.ttml.llm-package.json \
  --analysis /path/programme.ttml.llm-analysis.json
```

## Project status

This foundation defines the trust boundary, reporting contract, template, knowledge-source governance, and a curated BBC guidance-routing map. Parser-specific examples, conformance fixtures, and automated HTML checks remain future work.

## Licence and source material

Repository-authored material is provided under the licence in `LICENSE`. Third-party material remains the property of its respective owner. Keep BBC extracts concise, attributed, and traceable; do not copy or imply a licence to redistribute an entire external guide.
