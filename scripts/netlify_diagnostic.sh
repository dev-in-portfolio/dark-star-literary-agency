#!/usr/bin/env sh
set +e

marker() {
  name="$1"
  code="$2"
  file="000_NETLIFY_FAILURE_${name}_EXIT_${code}.html"
  printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Netlify diagnostic</title></head><body><h1>FAILURE: %s</h1><p>Exit code: %s</p></body></html>\n' "$name" "$code" > "$file"
  exit 0
}

run_stage() {
  name="$1"
  shift
  "$@"
  code=$?
  if [ "$code" -ne 0 ]; then
    marker "$name" "$code"
  fi
}

python3 --version || marker "python_version" "$?"
run_stage reconcile_catalog python3 scripts/reconcile_catalog.py --write
run_stage update_seo_write python3 scripts/update_seo.py --write
run_stage update_structured_data_write python3 scripts/update_structured_data.py --write
run_stage update_media_inventory_write python3 scripts/update_media_inventory.py --write

python3 scripts/validate_library_master.py > netlify-validator-output.txt 2>&1
code=$?
if [ "$code" -ne 0 ]; then
  first="$(grep '^- ' netlify-validator-output.txt | head -1 | sed 's/^- //' | tr '[:upper:]' '[:lower:]' | sed 's#[^a-z0-9][^a-z0-9]*#_#g' | cut -c1-120)"
  [ -n "$first" ] || first="unknown_error"
  marker "validate_library_master_${first}" "$code"
fi

run_stage validate_site python3 scripts/validate_site.py
run_stage validate_source_manifest python3 scripts/validate_source_manifest.py
run_stage validate_marketplace python3 scripts/validate_marketplace.py
run_stage update_seo_check python3 scripts/update_seo.py --check
run_stage update_structured_data_check python3 scripts/update_structured_data.py --check
run_stage update_media_inventory_check python3 scripts/update_media_inventory.py --check
run_stage validate_pdf_accessibility python3 scripts/validate_pdf_accessibility.py
run_stage validate_interaction_semantics python3 scripts/validate_interaction_semantics.py

printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Netlify diagnostic</title></head><body><h1>ALL RELEASE STAGES PASSED</h1></body></html>\n' > 000_NETLIFY_DIAGNOSTIC_ALL_PASSED.html
exit 0
