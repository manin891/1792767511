---
description: Conventions for co-located unit tests
paths:
  - "**/*.test.tsx"
  - "**/*.test.ts"
---

# Test file rules

Loads for co-located test files anywhere in the repository.

- Prefer behavior-focused assertions over broad snapshots for React trees and API payloads.
- Do not use `setTimeout`-driven waiting in tests; use deterministic async helpers from the test framework.
- For API handler tests, mock repository boundaries (`src/db/*`) and external clients, not internal validation helpers.
- In component tests under `src/components/*`, assert user-visible behavior and accessible roles instead of implementation details.
- Keep test setup local to each file; shared factories should live in `fixtures/` and be imported explicitly.
- Name test cases with domain intent (for example refund success vs refund failure) rather than generic labels like "works".
- For API route tests in `src/api/*`, assert status code and response contract shape from `src/api/_schemas/*`.
- Prefer one assertion topic per test block; split large multi-branch tests into focused scenarios.
- Avoid hidden global state between tests; reset mocks and test doubles in `beforeEach` or equivalent hooks.
- For async service tests, assert both success path and typed error path from `src/api/_lib/error.ts`.
- Keep test doubles close to call sites and avoid deep stubbing chains that mirror production internals.
- When adding a bugfix test, include the regression case first, then the normal path to document expected behavior.
