#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./scripts/check_tool_registered.sh <toolNameString>

NAME="${1:-}"

if [[ -z "$NAME" ]]; then
  echo "Usage: $0 <toolNameString>"
  exit 1
fi

grep -R --line-number "$NAME" src/tools || true
echo "If not found in src/tools/index.ts, add registry entry."
