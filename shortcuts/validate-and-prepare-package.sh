#!/bin/bash
set -u

export UV_CACHE_DIR="/tmp/ttml-validator-uv-cache"

validator_dir="/Users/rosss16/ttml-validator"
helper_dir="/Users/rosss16/ttml-validator/llm-helper"
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
log_file="${source_dir}/${source_name}.llm-package.log"

{
  printf '\n=== TTML validation/package run: %s ===\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'Source: %s\n' "$source_file"
  printf 'Validation output: %s\n' "$validation_file"
  printf 'Package output: %s\n' "$package_file"
} >>"$log_file"

cd "$validator_dir" || exit 1
if "$uv_bin" run validate-ttml \
  -ttml_in "$source_file" \
  -results_out "$validation_file" \
  -vertical \
  -json >>"$log_file" 2>&1
then
  validator_status=0
else
  # A non-zero status is expected when the document has findings. Continue
  # whenever the validator still produced a usable JSON result.
  validator_status=$?
  printf 'Validator exit status: %s\n' "$validator_status" >>"$log_file"
fi

if [[ ! -s "$validation_file" ]]; then
  printf 'ERROR: Validator did not create a non-empty JSON file.\n' >>"$log_file"
  notify "Validator failed; ${source_name}.llm-package.log contains details"
  /usr/bin/open -R "$log_file"
  exit 1
fi

if ! cd "$helper_dir"; then
  printf 'ERROR: Helper directory not found: %s\n' "$helper_dir" >>"$log_file"
  notify "Package failed; helper directory was not found"
  /usr/bin/open -R "$log_file"
  exit 1
fi
if ! ./scripts/prepare-package.sh \
  --ttml "$source_file" \
  --validator "$validation_file" \
  --output "$package_file" >>"$log_file" 2>&1; then
  printf 'ERROR: LLM package preparation failed.\n' >>"$log_file"
  notify "Package failed; ${source_name}.llm-package.log contains details"
  /usr/bin/open -R "$log_file"
  exit 1
fi

printf 'SUCCESS: LLM package created.\n' >>"$log_file"

if [[ $validator_status -ne 0 ]]; then
  notify "${source_name}: validator returned findings; JSON and LLM package created"
else
  notify "${source_name}: validation JSON and LLM package created"
fi

# The final line becomes the Run Shell Script action's output in Shortcuts.
printf '%s\n' "$package_file"
