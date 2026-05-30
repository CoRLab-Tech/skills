# Playbook

## Project Structure

```text
src/
├─ mcp-node.ts              # Server entry (env injection here only)
├─ registerTools.ts         # Calls registerAllTools(server, env)
├─ tools/index.ts           # Manual registry of all tools
└─ utils/                   # Utility methods and helpers
```

---

## Wiring Chain

```
mcp-node.ts
  → registerTools(server, envOverrides)
    → registerAllTools(server, env)
      → registerX(server, env)
```

---

## API Key Flow

1. Client calls MCP:
    - `/mcp?apiKey=...`
    - OR header `x-api-key`
2. `mcp-node.ts` injects:
    - `FUSEDASH_API_KEY`
3. Tool reads:
    - `env.FUSEDASH_API_KEY`

Never define apiKey in tool schema.

---

## Minimal Tool Template

### type.ts
```ts
import { z } from "zod";

export const ToolSchema = z.object({
  name: z.string().min(1),
}).strict();

export type ToolParams = z.infer<typeof ToolSchema>;
```

### prompt.ts
```ts
export const TOOL_PROMPT = [
  "Use this tool to: <purpose>.",
  "",
  "Call when:",
  "- <condition>",
  "",
  "Do NOT call when:",
  "- <condition>",
  "",
  "Args must match schema.",
  "",
  "Rules:",
  "- Never invent missing required args.",
  "- Return only tool arguments.",
].join("\n");
```

### handler.ts
```ts
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp";
import { ToolSchema, type ToolParams } from "./type";
import { TOOL_PROMPT } from "./prompt";

export function registerX(server: McpServer, env: Record<string, string | undefined>) {
  server.tool("tool_name", TOOL_PROMPT, ToolSchema.shape, async (args: ToolParams) => {
    try {
      // TODO: Implement tool logic here
      // Access API key via env.FUSEDASH_API_KEY if needed
      
      const result = "TODO"; // Your tool's result
      
      return { content: [{ type: "text", text: result }] };
    } catch (err) {
      return { 
        content: [{ 
          type: "text", 
          text: `Error: ${err instanceof Error ? err.message : "Unknown error"}` 
        }],
        isError: true
      };
    }
  });
}
```

---

## Server Setup

### Express Server with Both Transports

```typescript
// mcp-node.ts
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

const app = express();
app.use(cors());

// Streamable HTTP (stateless)
app.post("/mcp", express.json({ limit: "5mb" }), async (req, res) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });
  const server = new McpServer({ name: 'MCP-Server', version: '1.0.0' });

  try {
    registerTools(server, buildEnvOverrides(req));
    await server.connect(transport);
    await transport.handleRequest(req as any, res as any, req.body);

    res.on('close', () => {
      try { transport.close(); } catch {}
      try { server.close(); } catch {}
    });
  } catch (err) {
    if (!res.headersSent) res.status(500).send('MCP request failed');
    try { transport.close(); } catch {}
    try { server.close(); } catch {}
  }
});

interface SessionData {
  transport: SSEServerTransport;
  server: McpServer;
  lastActivity: number;
}

const sessions = new Map<string, SessionData>();

// SSE (stateful sessions)
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

---

## Troubleshooting

| Problem              | Cause                  | Fix                                                 |
|----------------------|------------------------|-----------------------------------------------------|
| Tool not visible     | Missing registry entry | Add import + call in src/tools/index.ts             |
| Auth failure         | Missing API key        | Pass query/header                                   |
| Validation error     | Schema mismatch        | Align prompt and schema                             |
| High token usage     | Prompt too verbose     | Reduce prompt size                                  |
| SSE connection drops | Session timeout        | Increase `SESSION_TIMEOUT_MINUTES` in `.env`        |
| HTTP request hangs   | Missing cleanup        | Ensure transport.close() and server.close() called  |
| Memory leak          | Unclosed sessions      | Check session cleanup interval and onclose handlers |
| CORS errors          | Missing headers        | Add proper CORS middleware for SSE/HTTP endpoints   |

---