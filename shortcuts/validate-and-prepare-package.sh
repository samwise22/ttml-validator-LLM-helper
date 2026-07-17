#!/bin/bash
set -u

export UV_CACHE_DIR="/tmp/ttml-validator-uv-cache"

validator_dir="/Users/rosss16/ttml-validator"
helper_dir="/Users/rosss16/ttml-validator-LLM-helper"
uv_bin="/Users/rosss16/.local/bin/uv"
source_file="$1"

notify() {
  /usr/bin/osascript - "$1" <<'APPLESCRIPT'
on run argv
  display notification (item 1 of argv) with title "TTML Validator"
end run
APPLESCRIPT
}

if [[ ! -f "$source_file" ]]; then
  notify "The selected TTML file could not be read"
  exit 1
fi

source_dir="$(dirname "$source_file")"
source_name="$(basename "$source_file")"
validation_file="${source_dir}/${source_name}.validation.json"
package_file="${source_dir}/${source_name}.llm-package.json"

cd "$validator_dir" || exit 1
"$uv_bin" run validate-ttml \
  -ttml_in "$source_file" \
  -results_out "$validation_file" \
  -vertical \
  -json >/dev/null 2>&1
validator_status=$?

if [[ ! -s "$validation_file" ]]; then
  notify "Validator did not create ${source_name}.validation.json"
  exit 1
fi

cd "$helper_dir" || exit 1
if ! ./scripts/prepare-package.sh \
  --ttml "$source_file" \
  --validator "$validation_file" \
  --output "$package_file" >/dev/null; then
  notify "Validation succeeded, but the LLM package could not be created"
  exit 1
fi

if [[ $validator_status -ne 0 ]]; then
  notify "${source_name}: validator returned findings; JSON and LLM package created"
else
  notify "${source_name}: validation JSON and LLM package created"
fi

# The final line becomes the Run Shell Script action's output in Shortcuts.
printf '%s\n' "$package_file"
