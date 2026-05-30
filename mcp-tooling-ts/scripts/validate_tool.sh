#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/validate_tool.sh <ToolFolder>

FOLDER="${1:-}"
BASE="src/tools/${FOLDER}"

if [[ -z "$FOLDER" ]]; then
  echo "Usage: $0 <ToolFolder>"
  exit 1
fi

if [[ ! -d "$BASE" ]]; then
  echo "ERROR: Tool directory $BASE does not exist"
  exit 1
fi

# Check required files
FILES=("type.ts" "prompt.ts" "handler.ts" "index.ts")
for file in "${FILES[@]}"; do
  if [[ ! -f "$BASE/$file" ]]; then
    echo "ERROR: Missing $file"
    exit 1
  fi
done

# Check type.ts for .strict()
if ! grep -q "\.strict()" "$BASE/type.ts"; then
  echo "ERROR: Schema must use .strict()"
  exit 1
fi

# Check prompt.ts line count
LINES=$(wc -l < "$BASE/prompt.ts")
if [[ $LINES -gt 20 ]]; then
  echo "WARNING: Prompt too long ($LINES lines, should be 10-20)"
fi

# Check handler.ts has server.tool call
if ! grep -q "server\.tool" "$BASE/handler.ts"; then
  echo "ERROR: Handler must register tool with server.tool()"
  exit 1
fi

# Check if registerTools.ts exists
if [[ ! -f "src/registerTools.ts" ]]; then
  echo "WARNING: src/registerTools.ts does not exist"
fi

# Check if utils directory exists
if [[ ! -d "src/utils" ]]; then
  echo "INFO: src/utils directory does not exist (optional)"
fi

# Check if registered in index.ts (look for an import from the tool folder)
if ! grep -qE "from ['\"].*${FOLDER}" "src/tools/index.ts" 2>/dev/null; then
  echo "WARNING: Tool folder '${FOLDER}' not imported in src/tools/index.ts"
fi

# Check if a register function from this folder is called in index.ts
if ! grep -qE "register[A-Za-z]+" "src/tools/${FOLDER}/handler.ts" 2>/dev/null; then
  echo "WARNING: No register function found in handler.ts"
else
  REGISTER_FN=$(grep -oE "export function register[A-Za-z]+" "src/tools/${FOLDER}/handler.ts" | awk '{print $3}')
  if [[ -n "$REGISTER_FN" ]] && ! grep -q "$REGISTER_FN" "src/tools/index.ts" 2>/dev/null; then
    echo "WARNING: Register function '${REGISTER_FN}' not called in src/tools/index.ts"
  fi
fi

echo "✅ Tool $FOLDER validation passed"
