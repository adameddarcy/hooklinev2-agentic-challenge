# Challenge 1: Failing test (about 10 minutes)

## Ticket

| Field    | Value                                      |
|----------|--------------------------------------------|
| ID       | **HL02**                                  |
| Type     | Bug                                        |
| Priority | P1, CI is red on `main`                    |
| Reporter | CI                                         |
| Summary  | Test suite failing on `main`               |

> The nightly CI run on `main` is failing. Nobody has changed the tests recently, and the
> pre-commit hook now rejects every commit. Find out what broke, and when, and fix it.
>
> **Acceptance criteria**
> - The root cause is fixed. Tests are only changed if you can explain why they were wrong.
> - You can explain the root cause and how you made sure the fix is complete.
> - All checks in `AGENTS.md` pass.

## Your task

1. **Create a branch for this ticket** before changing any code. It must be named
   `HL02_<short_description>`, e.g. `HL02_fix_event_matching`.
2. Run the tests and find out why they fail and when it started:

   ```bash
   uv run pytest
   ```

3. Fix the cause and commit your work to your branch. Commit messages must start with `HL02: `. The pre-commit hook runs the tests.
