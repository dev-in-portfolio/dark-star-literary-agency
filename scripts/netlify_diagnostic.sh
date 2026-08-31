#!/usr/bin/env sh
set +e
{
  echo "NETLIFY BUILD DIAGNOSTIC"
  echo "PWD=$(pwd)"
  echo "PYTHON:"
  python3 --version
  echo "RUNNING RELEASE CHECK"
  python3 scripts/release_check.py
  code=$?
  echo "RELEASE_EXIT_CODE=$code"
} > netlify-build-diagnostic.txt 2>&1
exit 0
