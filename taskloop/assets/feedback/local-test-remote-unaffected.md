---
name: feedback-local-test-remote-unaffected
description: "For local test requests, run only the patched service via node (no Docker), point everything else at staging, and verify the UI with Playwright MCP"
metadata:
  type: feedback
---

When a reviewer or the user asks for a **local test** of a fix, do **not** spin up the entire stack via docker-compose. Run only the patched service(s) on the local machine via `node` / `npm run start:dev` / `yarn start:dev` (no Docker), and configure them to talk to the **remote/staging** equivalents for every service the fix did not touch.

**Why:** Booting the whole microservice graph plus databases plus auth/cert chains locally takes hours and often fails (missing certs, broken seed data, port collisions). Pointing the local service at staging dependencies gives a real-data, end-to-end test in minutes while still exercising the modified code path. Docker is only worth it when you genuinely need an isolated, reproducible network — which a "test on local" request is not.

**How to apply:**
1. Run only the patched service(s) via `node` / `npm run start:dev` / `yarn start:dev` directly — no `docker-compose up`.
2. Configure their `.env` so every upstream dependency points at the staging URLs (gRPC, REST, DB hosts, auth servers). Keep these `.env` files local-only; do not commit.
3. Acquire a valid auth token (e.g., admin JWT) from the staging auth service and use it against the locally-running gateway/service.
4. Hit the affected endpoint with curl/HTTPie from localhost and verify behavior end-to-end against real staging data.
5. **Use Playwright MCP for the user-facing verification** — drive the locally-running UI through Playwright per [[feedback-ui-verification-and-evidence]] and capture screenshots as PR evidence.
6. When the reviewer says "test on local", spin up only the patched service(s) and verify; do not touch docker-compose unless explicitly asked.
7. Save this pattern as the default unless the user overrides for a specific test.
