#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./scripts/new_tool.sh <ToolFolder> <toolNameString> <registerFnName>

FOLDER="${1:-}"
TOOL_NAME="${2:-}"
REGISTER_FN="${3:-}"

if [[ -z "$FOLDER" || -z "$TOOL_NAME" || -z "$REGISTER_FN" ]]; then
  echo "Usage: $0 <ToolFolder> <toolNameString> <registerFnName>"
  exit 1
fi

BASE="src/tools/${FOLDER}"
mkdir -p "$BASE"

cat > "$BASE/type.ts" <<EOF
import { z } from "zod";

export const ToolSchema = z.object({
  // define params here (never include apiKey)
}).strict();

export type ToolParams = z.infer<typeof ToolSchema>;
EOF

cat > "$BASE/prompt.ts" <<EOF
export const TOOL_PROMPT = [
  "Use this tool to: TODO purpose.",
  "Call when: TODO.",
  "Do NOT call when: TODO.",
  "Args must match schema.",
  "Never invent missing args."
].join("\\n");
EOF

cat > "$BASE/handler.ts" <<EOF
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp";
import { ToolSchema, type ToolParams } from "./type";
import { TOOL_PROMPT } from "./prompt";

export function ${REGISTER_FN}(server: McpServer, env: Record<string, string | undefined>) {
  server.tool("${TOOL_NAME}", TOOL_PROMPT, ToolSchema.shape, async (args: ToolParams) => {
    try {
      // TODO: Implement tool logic here
      // Access API key via env.FUSEDASH_API_KEY if needed
      
      const result = "TODO"; // Your tool's result
      
      return { content: [{ type: "text", text: result }] };
    } catch (err) {
      return { 
        content: [{ 
          type: "text", 
          text: \`Error: \${err instanceof Error ? err.message : "Unknown error"}\`
        }],
        isError: true
      };
    }
  });
}
EOF

cat > "$BASE/index.ts" <<EOF
export { ${REGISTER_FN} } from "./handler";
export { TOOL_PROMPT } from "./prompt";
export { ToolSchema, type ToolParams } from "./type";
EOF

echo "Tool scaffold created at $BASE"
