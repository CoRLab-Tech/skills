# MCP Tooling Scripts (TypeScript)

## Project Structure

```text
src/
├─ mcp-node.ts              # Server entry (env injection here only)
├─ registerTools.ts         # Calls registerAllTools(server, env)
├─ tools/index.ts           # Manual registry of all tools
└─ utils/                   # Utility methods and helpers
```

## Usage

### Create a new tool
```bash
./scripts/new_tool.sh <ToolFolder> <toolNameString> <registerFnName>
```

Example:
```bash
./scripts/new_tool.sh getChartData get_chart_data registerGetChartData
```

### Validate a tool
```bash
./scripts/validate_tool.sh <ToolFolder>
```

Example:
```bash
./scripts/validate_tool.sh getChartData
```

### Check if tool is registered
```bash
./scripts/check_tool_registered.sh <toolNameString>
```

Example:
```bash
./scripts/check_tool_registered.sh get_chart_data
```

## Notes

- All scripts require execute permissions: `chmod +x scripts/*.sh`
- This is a **TypeScript** project - all files use `.ts` extensions
- Tools must be manually registered in `src/tools/index.ts`
- `src/registerTools.ts` should contain the `registerAllTools` function
- `src/utils/` directory contains utility methods and helpers
- Always run `pnpm build` after adding/modifying tools
- Use `pnpm dev` for development with hot reload
