# Hookline

Hookline is a small webhook service. Clients register **subscriptions** (a URL plus the
event types they care about), publish **events**, and Hookline delivers each event to every
matching subscription as a signed HTTP POST, recording every **delivery** attempt.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) (it will install Python 3.12 if needed).

```bash
uv sync                                   # install dependencies
uv run pytest                             # run the test suite
uv run uvicorn hookline.main:app --reload # serve on http://127.0.0.1:8000 (docs at /docs)
```

Quality checks:

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy src tests
uv run pytest --cov
```

## API

| Method   | Path                          | Description                                     |
|----------|-------------------------------|-------------------------------------------------|
| `POST`   | `/subscriptions`              | Create a subscription (returns the secret once) |
| `GET`    | `/subscriptions`              | List subscriptions (`?active=true\|false`)      |
| `GET`    | `/subscriptions/{id}`         | Fetch a subscription                            |
| `PATCH`  | `/subscriptions/{id}`         | Partially update a subscription                 |
| `DELETE` | `/subscriptions/{id}`         | Delete a subscription and its deliveries        |
| `POST`   | `/events`                     | Publish an event to matching subscriptions      |
| `GET`    | `/deliveries`                 | List deliveries (`?subscription_id=&success=&limit=`) |
| `GET`    | `/deliveries/{id}`            | Fetch a delivery                                |

### Event type patterns

Event types are lowercase dot-separated segments, e.g. `order.created`. Subscriptions list
one or more patterns:

| Pattern         | Matches                               | Does not match                   |
|-----------------|---------------------------------------|----------------------------------|
| `order.created` | `order.created`                       | `order.updated`, `order.created_v2` |
| `order.*`       | `order.created`, `order.item.added`   | `order`, `orders.created`        |
| `*`             | everything                            |                                  |

### Signatures

Each delivery is a `POST` with a JSON body `{"id", "type", "payload"}` and these headers:

- `X-Hookline-Event`: the event type
- `X-Hookline-Event-Id`: a unique id for the event
- `X-Hookline-Timestamp`: Unix seconds
- `X-Hookline-Signature`: `sha256=` + hex HMAC-SHA256 of `"{timestamp}.{raw body}"`,
  keyed with the subscription's secret

Receivers should check the signature with a constant-time comparison (see
`hookline.services.signing.verify_signature`) and reject old timestamps.

## Project layout

```
src/hookline/
  main.py          app factory and lifespan (DB engine, HTTP client)
  config.py        settings from HOOKLINE_* environment variables
  db.py, models.py SQLAlchemy engine/session and ORM models
  schemas.py       Pydantic request/response models
  repository.py    persistence logic
  deps.py          FastAPI dependencies
  routers/         HTTP endpoints
  services/        matching, signing and dispatch
tests/             pytest suite (in-memory SQLite, respx for outbound HTTP)
challenges/        interview exercises
```

## Interview challenges

There are four short exercises in [`challenges/`](challenges/). Each takes about 10 minutes.
You may use Claude throughout. We care about how you direct it and how you check its work.

1. [Failing test](challenges/01-failing-test.md)
2. [Customer bug report](challenges/02-customer-report.md)
3. [Pull request review](challenges/03-pr-review.md)
4. [New feature](challenges/04-feature.md)
