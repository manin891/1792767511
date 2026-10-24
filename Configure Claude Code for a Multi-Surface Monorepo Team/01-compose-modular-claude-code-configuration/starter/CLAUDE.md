# E-Commerce Platform — Shared Claude Code Conventions

This file is the **project-level** entry point for the e-commerce monorepo. Every teammate's Claude session loads it automatically.

## Scope: what belongs here vs. elsewhere

<!--
TODO: Add a side-by-side table distinguishing project-level (`./CLAUDE.md`, `.claude/`),
      user-level (`~/.claude/`), and directory-level (subdir `CLAUDE.md`) scopes. The table
      MUST explicitly state that user-level settings are NOT shared with teammates via
      version control, and MUST include one concrete example of content that belongs at
      user-level (e.g. preferred commit message style).
-->

<!-- TODO: Add a short paragraph tying the table back to the team's intent. -->

## Shared standards (modular via @-imports)

The actual conventions live in focused files so this entry point stays scannable:

@.claude/standards/frontend.md
@.claude/standards/api.md
@.claude/standards/database.md
@.claude/standards/testing.md

Path-scoped rules in [.claude/rules/](.claude/rules/) layer on top of these standards and activate only when Claude is editing matching files (React components, API handlers, test files).

## Repository layout

```
src/components/   React components (functional + hooks)
src/pages/        Top-level routes
src/api/          Node.js API handlers
src/db/           PostgreSQL repository-pattern modules
```

Tests are co-located: `Foo.tsx` lives next to `Foo.test.tsx`.

## Troubleshooting

If a CLAUDE.md instruction is not being followed, run `/memory` to inspect which configuration files are active in the current session.

## Team workflows

- `/review <pr-ref>` — codified PR review checklist. (You will author this in Exercise 2.)
- `/deploy-check` — read-only pre-deployment validation. (You will author this in Exercise 3.)

For decisions about when to use plan mode vs. direct execution on this codebase, you will produce a team decision doc in Exercise 4.
 