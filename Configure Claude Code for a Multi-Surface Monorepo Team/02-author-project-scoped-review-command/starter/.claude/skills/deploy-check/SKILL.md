---
name: deploy-check
description: Run read-only pre-deployment validation in a forked sub-agent and return one concise verdict
context: fork
argument-hint: "[target-branch] (defaults to main)"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git rev-parse:*)
  - Bash(git ls-files:*)
  - Bash(gh pr view:*)
  - Bash(gh pr checks:*)
---

# /deploy-check

Runs the team's pre-deployment validation checklist against the current working tree and the branch you are about to ship. Read-only by design: this skill never modifies files, never pushes, and never deploys. It returns a single structured summary so the calling session can decide whether to proceed.

## Why this is a skill (not a CLAUDE.md addition)

`/deploy-check` is on-demand, forked, and task-specific: you only need it right before a deploy and it produces verbose intermediate output (file enumeration, diff parsing, check traces) that has little value after the verdict is known. That is exactly the shape of a skill.

`CLAUDE.md` is always-loaded and universal; persistent conventions that should apply in every session belong there. Rule of thumb: on-demand, forked, task-specific belongs in a skill, while always-loaded, universal guidance belongs in `CLAUDE.md`.

## Why `context: fork`

The goal of `context: fork` is to keep verbose intermediate output out of the main session. A deploy check inspects diffs, enumerates files, and runs multiple discovery commands, but the main conversation usually needs only the final pass or fail summary.

`context: fork` is a Claude Code product feature at the skill invocation layer. Conceptually, it is analogous to the Architect's Playbook Branching Reality pattern, where isolated branches perform analysis without polluting the parent context.

## Checks

Run all checks. If any check fails, the overall verdict is **fail**.

### 1. Uncommitted changes

- **Detect:** run `git status --porcelain`.
- **Pass:** output is empty and the working tree is clean.
- **Fail:** any file appears in output; return the first changed paths in the summary so the author can commit or stash.

### 2. Migrations aligned with DB-impacting code

- **Detect:** compare `git diff <target-branch>..HEAD --name-only` for changes in `src/db/` or DB-facing API handlers, and verify matching migration updates under `src/db/migrations/`.
- **Pass:** each DB-affecting change has a corresponding migration or explicit no-migration rationale in the PR.
- **Fail:** DB-affecting code changed with no migration evidence; report the changed files and missing migration expectation.

### 3. CI status on the open PR

- **Detect:** if a PR exists for this branch, query checks via `gh pr checks` or `gh pr view --json statusCheckRollup`.
- **Pass:** required checks are successful.
- **Fail:** any required check is failing, cancelled, or still blocking; report failing check names and status.

## Output format

Return exactly this shape to the main session:

```text
verdict: pass | fail
checks:
  - name: uncommitted-changes
    status: pass | fail
    detail: <one line or empty>
  - name: migrations
    status: pass | fail
    detail: <one line or empty>
  - name: ci
    status: pass | fail | skipped
    detail: <one line or empty>
```

Do not return raw command dumps (full `git status`, full diff hunks, or full CI logs). Keep that detail in the fork and only return actionable summary lines.

## Personalization

This skill is project-scoped (`.claude/skills/deploy-check/`) so the team shares one deploy gate. If you want a stricter personal variant, create a parallel skill under `~/.claude/skills/deploy-check-strict/` with a different name; it stays local and does not affect teammates.

## What this skill deliberately does not do

- It never pushes, deploys, or runs migrations.
- It does not run the full test suite; CI owns the canonical gate.
- It does not perform secret scanning; that is handled by dedicated hooks and security pipelines.
