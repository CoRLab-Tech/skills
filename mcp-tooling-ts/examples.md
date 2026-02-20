# Examples

## Example 1 — Add Tool

User: "Add tool getRadarChartData."

Actions:
- Create folder
- Add 4 files
- Register in src/tools/index.ts
- Build project

Output:
STATUS: SUCCESS

---

## Example 2 — Tool Not Visible

User: "Tool exists but client cannot see it."

Actions:
- Check src/tools/index.ts
- Missing import/register
- Add it
- Rebuild

Output:
STATUS: SUCCESS

---

## Example 3 — Blocked (Auth Contract Change)

User: "Move apiKey into tool params."

Action:
- Refuse (breaks architecture)
- Keep transport-level injection

Output:
STATUS: BLOCKED

---