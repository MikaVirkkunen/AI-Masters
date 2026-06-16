# Repository Copilot Instructions

## Mission
- Prioritize correctness, maintainability, and minimal diffs.
- Preserve existing architecture and coding style unless explicitly asked to change it.

## Guardrails
- Do not weaken CI, tests, security, or lint/type checks to make builds pass.
- Avoid broad refactors unless requested.
- Keep changes scoped to the stated task and acceptance criteria.

## Task Workflow
- Start by confirming scope and constraints from the issue/PR description.
- Propose a short plan when tasks are non-trivial.
- Implement in small, reviewable commits.
- Validate with available tests/lint/type checks.

## Code Review Expectations
- Add or update tests for non-trivial logic changes.
- Reuse existing helpers/utilities; avoid duplicate abstractions.
- Highlight risky paths (auth, permissions, secrets, workflows).

## Pull Request Output
- Summarize what changed and why.
- List verification performed.
- Call out known limitations and follow-up tasks.