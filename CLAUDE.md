# Project instructions (also usable as AGENTS.md for Codex)

## What this is
InvoiceLens: a small service letting clients check invoice status. Read
`docs/SPEC.md` before changing behaviour; the spec is the source of truth.

## Conventions
- Python 3.10+, standard library only unless the task says otherwise.
- Business rules live in `app/store.py`. HTTP concerns live in `app/api.py`.
  `app/server.py` stays a thin wrapper with no logic.
- Inject `today` and secrets; never call `date.today()` inside business logic.
- Money is integer minor units. Never use floats.

## Definition of done
1. `python -m unittest` passes.
2. New behaviour has tests, including at least one failure case.
3. `docs/API.md` updated if an endpoint or response changed.
4. Summary of what changed and anything you were unsure about.

## Don'ts
- Don't add dependencies or rewrite files unrelated to the task.
- Don't weaken a test to make it pass; explain the conflict instead.
