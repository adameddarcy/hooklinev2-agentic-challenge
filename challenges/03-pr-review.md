# Challenge 3: Pull request review (about 10 minutes)

## Ticket

| Field    | Value                                                           |
|----------|-----------------------------------------------------------------|
| ID       | **HL04**                                                       |
| Type     | Code review                                                     |
| Priority | P2                                                              |
| Reporter | Engineering lead                                                |
| Summary  | Review PR "Add filtering and pagination to GET /subscriptions"  |

> A teammate has opened a pull request from `HL06_subscription_search` (ticket HL06). You're the
> required approver. Review it and decide whether it can be merged.
>
> **Acceptance criteria**
> - A clear verdict: **approve**, **approve with comments**, or **request changes / do not
>   merge**.
> - Specific issues, ordered by severity, each with the file/line and a suggested fix.

## Your task

This ticket is a review only. **You don't need to change code, so you don't need a branch.**
If you want to try out the PR's code, check it out locally; don't push to it.

```bash
git fetch origin
git diff main...origin/HL06_subscription_search
# or: gh pr view --web / gh pr diff / gh pr checkout
```

1. Decide on your verdict.
2. Write the review you would post: a short summary and the issues, ordered by severity.
3. Be ready to explain how you checked each issue you raise. Don't just repeat what Claude
   said.
