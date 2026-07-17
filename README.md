# TTML Validator LLM Helper

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

## Project status

This first foundation defines the trust boundary, reporting contract, template, and knowledge-source governance. Parser-specific examples, a larger verified BBC guidance subset, conformance fixtures, and automated HTML checks remain future work.

## Licence and source material

Repository-authored material is provided under the licence in `LICENSE`. Third-party material remains the property of its respective owner. Keep BBC extracts concise, attributed, and traceable; do not copy or imply a licence to redistribute an entire external guide.
