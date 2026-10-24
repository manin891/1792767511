# Plan mode vs direct execution

This note explains when this team should choose plan mode, direct execution, and the Explore subagent while working in this monorepo.

Knight-Webb's talk "SWE Is Becoming Plan and Review" is our framing reference, and we use it through the course curriculum (Module 8 anchor-talk context) as the decision baseline.

## Plan-mode example

Use plan mode when one change spans multiple surfaces and there are multiple valid implementation shapes.

Example: extracting shared cart behavior across `src/components/Cart/Cart.tsx`, `src/components/Checkout/Checkout.tsx`, and `src/components/MiniCart/MiniCart.tsx` while aligning API use with `src/services/payment.ts`.

This should start in plan mode because you need to compare options, define sequence, and prevent costly rework before editing files.

A good plan outputs: target files, dependency order, rollback strategy, and acceptance checks.

## Direct-execution example

Use direct execution when the change is narrow and obvious.

Example: add a single validation guard in one function inside `src/api/orders/handler.ts` and adjust one schema line in `src/api/_schemas/orders.ts`.

This is a one function scope and does not need architectural comparison, so direct execution is faster and clearer.

## Explore example

Use the Explore subagent when the goal is discovery and inventory.

Example: map all references to a payment flow by scanning `src/api/`, `src/services/`, and `src/db/` before changing anything.

Explore is valuable because it isolates verbose discovery output out of the main session and returns only the summarized findings.

Capture intermediate findings in a scratchpad (for example `docs/plan-mode-vs-direct-execution.md` notes section or a temporary analysis note) so follow-up questions do not require repeating the full search.

## Combined-workflow example

A combined workflow is often best: plan-mode then direct execution.

Example: first run plan mode to map the impact of renaming an API contract across `src/api/orders/refund.ts`, `src/db/orders.ts`, and `src/types/cart.ts`; then perform direct execution for the approved mechanical edits.

This gives architectural confidence first, then efficient implementation.

## Skill vs CLAUDE.md quick rubric

Use a skill when the task is on-demand, task-specific, or fork-friendly.

Use `CLAUDE.md` and `.claude/rules/` for always-loaded universal guidance that should apply in every session.

When unsure, prefer plan mode first, then switch to direct execution once scope and risk are explicit.
