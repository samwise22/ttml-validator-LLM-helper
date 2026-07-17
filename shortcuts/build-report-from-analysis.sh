#!/bin/bash
set -u

helper_dir="/Users/rosss16/ttml-validator/llm-helper"
analysis_file="$1"

notify() {
  /usr/bin/osascript - "$1" <<'APPLESCRIPT'
on run argv
  display notification (item 1 of argv) with title "TTML Report"
end run
APPLESCRIPT
}

if [[ ! -f "$analysis_file" ]]; then
  notify "The selected LLM analysis file could not be read"
  exit 1
fi

analysis_dir="$(dirname "$analysis_file")"
analysis_name="$(basename "$analysis_file")"

if [[ "$analysis_name" != *.llm-analysis.json ]]; then
  notify "Select a file ending in .llm-analysis.json"
  exit 1
fi

source_name="${analysis_name%.llm-analysis.json}"
package_file="${analysis_dir}/${source_name}.llm-package.json"
report_file="${analysis_dir}/${source_name}.validation-report.html"
errors_file="${analysis_dir}/${source_name}.llm-analysis.errors.txt"

if [[ ! -f "$package_file" ]]; then
  notify "Matching ${source_name}.llm-package.json was not found"
  exit 1
fi

cd "$helper_dir" || exit 1
if ! ./scripts/render-report.sh \
  --package "$package_file" \
  --analysis "$analysis_file" \
  --output "$report_file" \
  --errors "$errors_file" >/dev/null; then
  notify "LLM analysis failed validation; an errors file was created"
  /usr/bin/open -R "$errors_file"
  exit 1
fi

notify "$(basename "$report_file") created"
/usr/bin/open "$report_file"
printf '%s\n' "$report_file"
