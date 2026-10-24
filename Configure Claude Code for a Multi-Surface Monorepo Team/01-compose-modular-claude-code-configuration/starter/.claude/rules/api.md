---
description: Conventions for API handlers under src/api/
paths:
  - "src/api/**/*"
---

# API handler rules

Loads when editing any file under `src/api/`.

- Handler files should expose one async handler with explicit request/response typing from `src/api/_lib/types.ts`.
- Translate domain failures to typed API errors from `src/api/_lib/error.ts`; do not bubble raw DB or payment SDK errors to the edge.
- Keep database access behind `src/db/*` repository modules; API handlers orchestrate, but must not embed SQL or transaction plumbing directly.
- Validate request payloads with schemas from `src/api/_schemas/*` before calling service or repository code.
- Keep HTTP mapping at the edge: status codes and response shape are decided in `src/api/*`, not in `src/services/*`.
- Import business logic from `src/services/*` and keep handlers thin; avoid embedding cross-step workflow logic in route files.
- For create/update flows, perform idempotency checks before side effects and return deterministic error payloads for duplicate requests.
- Normalize unknown exceptions into a safe internal error response and avoid leaking stack traces or provider error details.
- Keep each handler focused on one route concern; shared helpers belong in `src/api/_lib/*`.
- Prefer explicit named exports for helper functions used by handlers; keep default export reserved for the route handler itself.
- When calling repository methods, pass a typed input object rather than positional arguments to keep call sites stable.
