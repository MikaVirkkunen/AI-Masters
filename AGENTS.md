# Agents Operating Model

## Roles
- Builder agent: Implements scoped code changes.
- Verifier agent (or verification workflow): Checks tests, lint, type checks, and safety rules.
- Human reviewer: Final judgment and merge approval.

## Default Policy
- One issue can use one or multiple agents depending on task decomposition.
- Use one agent for linear/small tasks.
- Use multiple agents only when work splits into independent tracks with clear file boundaries.

## Parallelization Rules
- Each agent track owns distinct files/modules.
- If dependencies exist, declare execution order explicitly.
- Avoid concurrent edits to the same file unless intentionally serialized.

## Done Criteria
- Acceptance criteria from issue are met.
- Required validation checks pass.
- No CI weakening.
- PR includes concise risk/rollback notes for medium/high-risk changes.