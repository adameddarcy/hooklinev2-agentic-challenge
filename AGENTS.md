# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

Hookline is a FastAPI + SQLAlchemy 2.0 + Pydantic v2 webhook service. See `README.md`
for the API and the domain rules (event type patterns, signatures).

## Commands

```bash
uv sync                      # install
uv run pytest                # tests
uv run pytest --cov          # tests with coverage
uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy src tests scripts  # type check (strict)
```

All four checks must pass before a change is finished.

## Git workflow

- Work is tracked as tickets `HL[num][num]`. Before changing code for a ticket, create
  a branch named after it: ticket `HL12` → branch `HL12_<short_description>`
  (e.g. `HL12_fix_patch_semantics`). GitHub rejects any other branch name on push.
- Every commit message must start with the ticket ID: `HL12: Short description`. The
  `commit-msg` hook rejects anything else, including git's default revert and merge
  messages.
- Never commit to `main` directly; open a pull request.
- A pre-commit hook (`.pre-commit-config.yaml`) runs the full test suite on every commit.
  If it fails, fix the tests. **Never bypass the hooks with `--no-verify`.**

## Conventions

- Keep routers thin: HTTP concerns live in `routers/`, persistence in `repository.py`,
  and domain logic in `services/`.
- Request/response bodies are Pydantic models in `schemas.py`. Request models use
  `extra="forbid"`.
- **Never expose a subscription's `secret`**, except in the `SubscriptionCreated` response.
- Use full type hints; mypy runs in strict mode.
- Every behaviour change comes with a test. For bug fixes, write a failing test first.
- Tests go through the HTTP API with the `client` fixture where possible, and use the
  `receiver` (respx) fixture for outbound webhooks. Never make real network calls.
