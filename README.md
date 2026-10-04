# Hookline

Hookline is a small webhook service. Clients register **subscriptions** (a URL plus the
event types they care about), publish **events**, and Hookline delivers each event to every
matching subscription as a signed HTTP POST, recording every **delivery** attempt.

> **Interviewers:** the interview key (rubric, answers, hints and timings for each
> challenge) is available here (password protected):
> [Hookline Interview](https://app.notion.com/p/Hookline-Interview-3ef5cf3c9bcf809186a4f53614a4e146?source=copy_link)

## Welcome, candidate 👋

Thanks for taking the time to interview with us. This repository is a small but realistic
codebase, and for the next 50 minutes or so it's yours to work in.

### What to expect

| Time       | What happens                                                  |
|------------|---------------------------------------------------------------|
| 5 minutes  | **Set up and get to know the repo** (see below)               |
| 40 minutes | Four challenges, about 10 minutes each                        |
| 5 minutes  | Wrap-up: we'll talk about how it went                         |

**You can use Claude throughout. We expect you to.** This isn't a test of how fast you
type or what you can recall from memory. We're interested in:

- **How you direct Claude**: the context, constraints and standards you give it.
- **How you check its work**: running things, reading diffs, not taking "done" on trust.
- **Engineering judgement**: finding root causes, writing meaningful tests, and spotting
  when something isn't right.
- **Following the team's standards**: this repo has conventions, like any real team. Work
  the way a new teammate would be expected to.
- **Communication**: please think out loud. Explaining your reasoning matters as much as
  the result.

Partial progress is fine. We'd rather see a careful approach to part of a challenge than
a rushed one that isn't checked. You're welcome to ask us questions at any point, as you
would a teammate.

### Start here: your first 5 minutes

Before opening any challenge, take about **5 minutes** to set up and understand the
repository and its standards:

1. Set up your environment:

   ```bash
   uv sync
   uv run pre-commit install
   uv run pytest
   ```

2. Read this README, especially the [Development workflow](#development-workflow): how
   we name branches, write commit messages, and structure pull requests.
3. Skim [`AGENTS.md`](AGENTS.md) (the instructions Claude gets in this repo) and the
   [Architecture](#architecture) section, so you know where things live.

Time spent here pays off in every challenge.

### The challenges

Each challenge is written as a ticket in [`challenges/`](challenges/). Work through them
in order. The [development workflow](#development-workflow) applies throughout: if a
ticket needs code changes, create its branch first (ticket `HL02` → branch
`HL02_<short_description>`) and start every commit message with the ticket ID
(`HL02: ...`).

| # | Ticket | Challenge                                                            | What it's about                                    |
|---|--------|----------------------------------------------------------------------|----------------------------------------------------|
| 1 | HL02   | [Failing test](challenges/01-failing-test.md)                        | CI is red on `main`. Find out why and fix it.      |
| 2 | HL03   | [Customer bug report](challenges/02-customer-report.md)              | A customer's webhooks stopped. Reproduce and fix it, and reply to them. |
| 3 | HL04   | [Pull request review](challenges/03-pr-review.md) (no branch needed) | Review a teammate's PR and decide whether it can be merged. |
| 4 | HL05   | [New feature](challenges/04-feature.md)                              | Add a small feature to the spec.                   |

Good luck, and enjoy it!

## Tech stack

| Concern        | Choice                                                             |
|----------------|--------------------------------------------------------------------|
| Language       | Python 3.12 (pinned in `.python-version`)                          |
| Packaging      | [uv](https://docs.astral.sh/uv/), `pyproject.toml` + `uv.lock`     |
| Web framework  | FastAPI                                                            |
| Validation     | Pydantic v2, pydantic-settings for configuration                   |
| Persistence    | SQLAlchemy 2.0 (typed `Mapped[]` models) on SQLite                 |
| Outbound HTTP  | httpx (async)                                                      |
| Tests          | pytest, pytest-asyncio, pytest-cov, respx (mocks outbound HTTP)    |
| Quality        | ruff (lint + format), mypy in strict mode, pre-commit hooks        |

## Quick start

Requires [uv](https://docs.astral.sh/uv/). It installs Python 3.12 if needed.

```bash
uv sync                                   # install dependencies
uv run pre-commit install                 # install the git hooks (see below)
uv run pytest                             # run the test suite
uv run uvicorn hookline.main:app --reload # serve on http://127.0.0.1:8000 (docs at /docs)
```

### Quality checks

All of these must pass before a change is finished:

```bash
uv run ruff check .            # lint
uv run ruff format --check .   # formatting
uv run mypy src tests scripts  # type check (strict)
uv run pytest --cov            # tests with coverage
```

### Configuration

Settings come from environment variables with the `HOOKLINE_` prefix, or a `.env` file
(see `src/hookline/config.py`):

| Variable                            | Default                    | Meaning                          |
|-------------------------------------|----------------------------|----------------------------------|
| `HOOKLINE_DATABASE_URL`             | `sqlite:///./hookline.db`  | SQLAlchemy database URL          |
| `HOOKLINE_DELIVERY_TIMEOUT_SECONDS` | `5.0`                      | Timeout per webhook POST (0–30s) |
| `HOOKLINE_USER_AGENT`               | `Hookline/0.1`             | User-Agent on outbound requests  |

## Development workflow

### Tickets

Work is tracked as tickets with IDs of the form `HL[num][num]`, e.g. `HL07`. Every branch
and commit refers to a ticket.

### Branches

- Before changing code, create a branch named after the ticket:
  `HL[num][num]_<short_description>`, e.g. `HL07_rotate_secret`. If the work depends on
  another unmerged ticket, branch from that ticket's branch (see
  [Stacked pull requests](#stacked-pull-requests)).
- GitHub **rejects any push that creates a branch with a different name**. This is enforced
  by a repository ruleset, defined in
  [`.github/rulesets/branch-naming.json`](.github/rulesets/branch-naming.json).
- `main` is protected by a second ruleset: no direct pushes, no force-pushes, and no
  deletion. Changes reach `main` through a pull request with one approval and all review
  conversations resolved.

### Stacked pull requests

**This repo prefers stacked PRs.** Rather than one large PR, or several PRs that each
branch from `main` and duplicate each other's changes, build a stack of small PRs, one
ticket each, where each branch starts from the branch it depends on:

```
main
 └── HL02_fix_event_matching        PR #10 → base: main
      └── HL03_fix_partial_update   PR #11 → base: HL02_fix_event_matching
           └── HL05_rotate_secret   PR #12 → base: HL03_fix_partial_update
```

How to work with a stack:

1. **Branch from the branch you depend on.** Start from `main` only when your work doesn't
   need anything that hasn't been merged yet.

   ```bash
   git switch HL02_fix_event_matching
   git switch -c HL03_fix_partial_update
   ```

2. **Point each PR at its parent branch**, not `main`, so reviewers only see that ticket's
   changes:

   ```bash
   gh pr create --base HL02_fix_event_matching --title "HL03: Keep unset fields on PATCH"
   ```

3. **Describe the stack** at the top of each PR description, e.g.
   `Stacked on #10 (HL02). Followed by #12 (HL05).`
4. **Keep every PR small and green.** Each one should be reviewable on its own, and the
   hooks must pass on every branch in the stack.
5. **Merge from the bottom up.** When the parent PR merges, GitHub retargets the next PR
   to `main` once the parent branch is deleted. Then rebase the child so it only carries
   its own commits:

   ```bash
   git fetch origin
   git rebase --onto origin/main HL02_fix_event_matching HL03_fix_partial_update
   git push --force-with-lease
   ```

6. **When a lower PR changes after review**, rebase each branch above it onto the updated
   branch, from the bottom up.

Force-pushing your own ticket branches after a rebase is fine. Use `--force-with-lease`.
Force-pushing `main` is blocked.

### Commits

Every commit message must start with the ticket ID, a colon and a space:

```
HL07: Add secret rotation endpoint
```

### Git hooks

`uv run pre-commit install` installs two hooks, configured in
[`.pre-commit-config.yaml`](.pre-commit-config.yaml):

| Hook         | What it does                                                                 |
|--------------|------------------------------------------------------------------------------|
| `pre-commit` | Runs the full test suite. The commit is rejected if any test fails.          |
| `commit-msg` | Rejects the commit unless the message starts with `HL[num][num]: ` ([`scripts/check_commit_msg.py`](scripts/check_commit_msg.py)). |

Don't bypass the hooks with `--no-verify`. Note that git's default messages for
`git revert` and merges don't have the prefix, so edit them before committing.

### Rulesets

The rulesets live on GitHub. To recreate the branch-naming ruleset from its definition,
for example on a fork:

```bash
gh api -X POST repos/<owner>/<repo>/rulesets --input .github/rulesets/branch-naming.json
```

### Working with AI agents

[`AGENTS.md`](AGENTS.md) holds the rules for coding agents: commands, conventions, the git
workflow above, and files they must not read. [`CLAUDE.md`](CLAUDE.md) imports it so
Claude Code picks it up automatically.

## Architecture

```
src/hookline/
  main.py          app factory (create_app) and lifespan: DB engine, HTTP client
  config.py        Settings, from HOOKLINE_* environment variables
  db.py            engine and session factory
  models.py        SQLAlchemy ORM models: Subscription, Delivery
  schemas.py       Pydantic request/response models
  repository.py    persistence: SubscriptionRepository, DeliveryRepository
  deps.py          FastAPI dependencies (sessions, repositories, 404 lookups)
  routers/         HTTP endpoints: subscriptions, events, deliveries
  services/
    matching.py    event type pattern matching
    signing.py     HMAC-SHA256 signatures and secret generation
    dispatcher.py  concurrent, signed delivery to subscribers
tests/             pytest suite
scripts/           developer tooling (commit message check)
challenges/        interview tickets
.github/rulesets/  GitHub ruleset definitions
```

Design rules:

- **Thin routers.** HTTP concerns live in `routers/`, persistence in `repository.py`, and
  domain logic in `services/`.
- **Pydantic at the edges.** Request models use `extra="forbid"`. Responses are built from
  ORM objects with `from_attributes=True`.
- **Secrets are write-once.** A subscription's signing secret only appears in the create
  response (`SubscriptionCreated`). Every other response uses `SubscriptionRead`, which
  has no secret.
- **Testable by construction.** `create_app(settings)` builds an isolated app, with its
  database and HTTP client on `app.state`.

### Testing approach

- Each test gets a fresh app with an in-memory SQLite database (`client` fixture in
  `tests/conftest.py`).
- Tests go through the HTTP API where possible. `make_subscription` creates subscriptions
  through the API.
- Outbound webhooks are intercepted by respx (`receiver` fixture), and any request to an
  unmocked host fails, so tests never touch the network.
- Warnings are errors (`filterwarnings = ["error"]`).

## API

| Method   | Path                  | Description                                           |
|----------|-----------------------|-------------------------------------------------------|
| `GET`    | `/health`             | Liveness check                                        |
| `POST`   | `/subscriptions`      | Create a subscription (returns the secret once)       |
| `GET`    | `/subscriptions`      | Search subscriptions (`?active=&target_url=&event_type=&page=&size=`) |
| `GET`    | `/subscriptions/{id}` | Fetch a subscription                                  |
| `PATCH`  | `/subscriptions/{id}` | Partially update a subscription                       |
| `DELETE` | `/subscriptions/{id}` | Delete a subscription and its deliveries              |
| `POST`   | `/events`             | Publish an event to matching subscriptions (`202`)    |
| `GET`    | `/deliveries`         | List deliveries, newest first (`?subscription_id=&success=&limit=`) |
| `GET`    | `/deliveries/{id}`    | Fetch a delivery                                      |

Interactive docs are served at `/docs` when the app is running.

### Event type patterns

Event types are lowercase dot-separated segments, e.g. `order.created`. Subscriptions list
one or more patterns:

| Pattern         | Matches                               | Does not match                      |
|-----------------|---------------------------------------|-------------------------------------|
| `order.created` | `order.created`                       | `order.updated`, `order.created_v2` |
| `order.*`       | `order.created`, `order.item.added`   | `order`, `orders.created`           |
| `*`             | everything                            |                                     |

### Signatures

Each delivery is a `POST` with a JSON body `{"id", "type", "payload"}` and these headers:

- `X-Hookline-Event`: the event type
- `X-Hookline-Event-Id`: a unique id for the event
- `X-Hookline-Timestamp`: Unix seconds
- `X-Hookline-Signature`: `sha256=` + hex HMAC-SHA256 of `"{timestamp}.{raw body}"`,
  keyed with the subscription's secret

Receivers should check the signature with a constant-time comparison (see
`hookline.services.signing.verify_signature`) and reject old timestamps.
