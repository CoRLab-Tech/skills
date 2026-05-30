---
name: mcp-tooling-ts
description: Manage and maintain a TypeScript MCP server using @modelcontextprotocol/sdk with Express and Streamable HTTP/SSE. Supports setup, adding new MCP tools (handler.ts/prompt.ts/type.ts/index.ts), enforcing strict Zod schemas, token-lean prompts (Claude/Grok friendly), manual tool registration, and transport-level API key injection (query/header → env, never in tool params). All code examples use TypeScript (.ts files). Triggers: "setup MCP server", "add MCP tool", "create handler.ts prompt.ts type.ts", "register tool", "refactor MCP prompt", "API key via header/query".
allowed-tools: bash, view, str_replace, grep, ls, git, create_file
user-invocable: true
context: fork
---

# MCP Tooling TS

## Purpose
Standardize development of a TypeScript MCP server with:
- Manual tool registration
- Strict Zod schemas
- Token-efficient prompts
- Transport-level API key injection

---

## Canonical Project Structure (Minimal)

```text
src/
├─ mcp-node.ts              # Server entry (env injection here only)
├─ registerTools.ts         # Calls registerAllTools(server, env)
├─ tools/index.ts           # Manual registry of all tools
└─ utils/                   # Utility methods and helpers
```

---

## Server Setup (Express + SSE + Streamable HTTP)

### mcp-node.ts - Server Entry Point

All transport endpoints (SSE and Streamable HTTP) are implemented directly in `mcp-node.ts`:

```typescript
import express from 'express';
import cors from 'cors';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp';
import { registerTools } from './registerTools';

// Environment injection
function buildEnvOverrides(req: express.Request) {
  const queryApiKey = typeof req.query.apiKey === "string" ? req.query.apiKey : undefined;
  const headerApiKey = req.get("x-api-key") ?? req.get("X-API-Key");
  const fusedashApiKey = queryApiKey ?? headerApiKey;

  return {
    ...process.env,
    ...(fusedashApiKey ? { FUSEDASH_API_KEY: fusedashApiKey } : {}),
  };
}

// Express app setup
const app = express();
app.use(cors()); // Enable CORS for MCP clients

// Health check endpoint
app.get("/", (_req, res) => {
  res.status(200).json({
    status: "healthy",
    endpoints: {
      mcp: "POST /mcp",
      sse: "GET /sse",
      health: "GET /"
    },
    timestamp: new Date().toISOString()
  });
});
```

---

## Transport Types

### 1. Streamable HTTP (Stateless)

```typescript
app.post("/mcp", express.json({ limit: "5mb" }), async (req, res) => {
  // Stateless: fresh server+transport per request
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined, // No sessions
  });

  const server = new McpServer({
    name: "your-mcp-server",
    version: "1.0.0",
  });

  try {
    const envOverrides = buildEnvOverrides(req);
    registerTools(server, envOverrides);

    await server.connect(transport);
    await transport.handleRequest(req as any, res as any, req.body);

    res.on("close", () => {
      try { transport.close(); } catch {}
      try { server.close(); } catch {}
    });
  } catch (err) {
    if (!res.headersSent) res.status(500).json({ error: "MCP request failed" });
    try { transport.close(); } catch {}
    try { server.close(); } catch {}
  }
});
```

### 2. Server-Sent Events (Stateful Sessions)

```typescript
const sessions = new Map<string, SessionData>();

interface SessionData {
  transport: SSEServerTransport;
  server: McpServer;
  lastActivity: number;
}

// SSE endpoint - creates persistent session
app.get('/sse', async (req, res) => {
  const sessionId = req.query?.sessionId as string | undefined;

  if (sessionId) {
    res.status(400).send('Session already exists');
    return;
  }

  const transport = new SSEServerTransport('/sse/message', res as any);
  const sessionServer = new McpServer({ name: 'MCP-Server', version: '1.0.0' });

  registerTools(sessionServer, buildEnvOverrides(req));
  await sessionServer.connect(transport);

  const sid = transport.sessionId;
  sessions.set(sid, {
    transport,
    server: sessionServer,
    lastActivity: Date.now(),
  });

  let isClosing = false;
  transport.onclose = async () => {
    if (isClosing) return;
    isClosing = true;

    const session = sessions.get(sid);
    if (!session) return;

    try { await session.server.close(); } catch {}
    try {
      if (typeof session.transport.close === 'function') session.transport.close();
    } catch {}

    sessions.delete(sid);
  };
});

// SSE message endpoint - handles messages within session
app.post('/sse/message', async (req, res) => {
  const sessionId = req.query?.sessionId as string;
  const session = sessions.get(sessionId);

  if (session) {
    try {
      session.lastActivity = Date.now();
      await session.transport.handlePostMessage(req as any, res as any);
    } catch (err) {
      if (!res.headersSent) res.status(500).send('Failed to handle message');
    }
  } else {
    if (!res.headersSent) res.status(404).send('No session found for sessionId');
  }
});
```

## Session Management & Cleanup

### Session Timeout Handling

```typescript
const getMilliseconds = (minutes: number) => minutes * 60 * 1000;

// Read from .env, fall back to sensible defaults
const CLEAN_INACTIVE_SESSIONS_INTERVAL = getMilliseconds(
  Number(process.env.SESSION_CLEANUP_INTERVAL_MINUTES ?? 5)
);

setInterval(async () => {
  const now = Date.now();
  const SESSION_TIMEOUT = getMilliseconds(
    Number(process.env.SESSION_TIMEOUT_MINUTES ?? 30)
  );

  for (const [sessionId, sessionData] of sessions.entries()) {
    if (now - sessionData.lastActivity > SESSION_TIMEOUT) {
      console.log(`[CLEANUP] Inactive session: ${sessionId}`);

      try {
        await sessionData.server.close();
      } catch (e) {
        console.error(`[CLEANUP_ERROR]:`, e);
      }

      try {
        if (typeof sessionData.transport.close === 'function') {
          sessionData.transport.close();
        }
      } catch (e) {
        console.error(`[CLEANUP_ERROR]:`, e);
      }

      sessions.delete(sessionId);
    }
  }
}, CLEAN_INACTIVE_SESSIONS_INTERVAL);
```

---

## Transport Comparison

| Feature         | Streamable HTTP         | Server-Sent Events               |
|-----------------|-------------------------|----------------------------------|
| **State**       | Stateless (per request) | Stateful (persistent session)    |
| **Use Case**    | One-off tool calls      | Chat conversations, streaming    |
| **Performance** | Lower overhead          | Higher overhead but persistent   |
| **Cleanup**     | Automatic (per request) | Manual (session timeout)         |
| **Complexity**  | Simple                  | Complex (session management)     |
| **Endpoint**    | `POST /mcp`             | `GET /sse` + `POST /sse/message` |

---

## API Key Injection (Transport Level)

### Query Parameter
```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
  -G -d "apiKey=your-api-key-here"
```

### Header Injection
```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### SSE with API Key
```bash
curl -N "http://localhost:3000/sse?apiKey=your-api-key-here"
```

---

## Single Tool Structure (Minimal)

```text
src/tools/<ToolFolder>/
├─ handler.ts   # registerX(server, env) + server.tool(...)
├─ prompt.ts    # short (10–20 lines) prompt string
├─ type.ts      # Zod schema (.strict()) + inferred type
└─ index.ts     # re-exports
```

---

## Architectural Invariants

1. API key is NEVER part of tool params.
2. API key is provided via:
    - `/mcp?apiKey=...`
    - `x-api-key` header
3. Only `mcp-node.ts` may parse query/header.
4. `mcp-node.ts` injects:
    - `env.FUSEDASH_API_KEY`
5. Tools read:
    - `env.FUSEDASH_API_KEY`
6. All tools must be manually registered in `src/tools/index.ts`.
7. All schemas must use `.strict()`.
8. Utility methods are stored in `src/utils/`.
9. `src/registerTools.ts` contains the main registration logic.
10. Session cleanup timing is configured via `.env`:
    - `SESSION_CLEANUP_INTERVAL_MINUTES` (default: `5`)
    - `SESSION_TIMEOUT_MINUTES` (default: `30`)

---

## Workflow

### Add a New Tool
1. Create folder under `src/tools/<ToolFolder>/`
2. Add: `type.ts`, `prompt.ts`, `handler.ts`, `index.ts`
3. Import and call `registerX(server, env)` inside `src/tools/index.ts`
4. Ensure `src/registerTools.ts` calls `registerAllTools(server, env)`
5. Run `pnpm build`

### Verify Tool Registration
- Confirm import exists in `src/tools/index.ts`
- Confirm `server.tool("<toolName>", ...)` exists
- Ensure `src/registerTools.ts` exists and is imported
- Run `pnpm build`

---

## Prompt Rules
- 10–20 lines maximum
- No XML blocks
- Must include:
    - Purpose
    - Call when
    - Do NOT call when
    - Args summary
    - Rules: never invent args, no extra keys
<!-- TODO: Working on automated tool description generation from prompts -->

---

## Schema Rules
- Always `.strict()`
- Required strings: `.min(1)`
- Required arrays: `.min(1)`
- Use defaults to reduce prompt verbosity
- Never include apiKey

---

## Output Format
```
STATUS: SUCCESS / FAILED / BLOCKED
Summary: ...
Files: ...
Commands: ...
Notes: ...
```

---