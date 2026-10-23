# InvoiceLens

A small, spec-driven service for client invoice status. It is built as a
portfolio project that shows the workflow: **business need -> spec -> AI-ready
instructions -> tested code -> docs.**

## Run
```bash
python -m unittest -v                    # tests
WEBHOOK_SECRET=dev python -m app.server  # http://localhost:8000
```

## Layout
- `docs/SPEC.md`: the spec (start here)
- `docs/API.md`: endpoints and examples
- `CLAUDE.md`: standing instructions for Claude Code / Codex (copy to `AGENTS.md` for Codex)
- `prompts/`: structured task prompts to hand to a coding tool
- `app/`: code; `tests/`: tests

## Your exercise
1. Read the spec and challenge it (find a gap, then add it to Open questions).
2. Run `prompts/01-add-pagination.md` through Claude Code or Codex. Review the
   diff yourself before accepting it.
3. Use `prompts/02` to practise changing a spec before changing code.
4. Write your own prompt for a new feature (e.g. a `due_soon` status) and
   compare the tool's output against your acceptance criteria.
5. Keep a short `docs/DECISIONS.md` noting what the AI got right and wrong.
