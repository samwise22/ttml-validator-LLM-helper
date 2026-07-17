#!/bin/sh
set -eu

output="DIST.md"
tmp="${output}.tmp"

{
  printf '%s\n\n' '# TTML Validator LLM Helper — Distribution Bundle'
  printf '%s\n\n' 'This file is generated. Do not edit it directly.'
  for file in spec/REPORTING-STANDARD.md spec/HELPFUL-REPORT-GUIDE.md knowledge/SOURCES.md knowledge/BBC-SUBTITLE-GUIDANCE.md prompts/GENERATE-REPORT.md templates/report.html; do
    printf '%s\n\n' "## Bundled file: $file"
    case "$file" in
      *.html) printf '%s\n' '```html' ;;
      *) printf '%s\n' '```markdown' ;;
    esac
    sed 's/^```$/````/' "$file"
    printf '%s\n\n' '```'
  done
} > "$tmp"

mv "$tmp" "$output"
printf '%s\n' "Wrote $output"
