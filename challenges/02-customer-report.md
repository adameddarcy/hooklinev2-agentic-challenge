# Challenge 2: Customer bug report (about 10 minutes)

## Ticket

| Field    | Value                                              |
|----------|----------------------------------------------------|
| ID       | **HL03**                                          |
| Type     | Bug (customer-reported)                            |
| Priority | P1, blocking a customer's order sync               |
| Reporter | Support, on behalf of Northwind Retail             |
| Summary  | Webhooks stopped after the subscription was paused |

> **From:** Priya N., platform engineer at Northwind Retail
> **Subject:** Webhooks stopped after we paused them
>
> Hi team,
>
> Last week we paused our order webhook during a deploy. We called
>
> ```
> PATCH /subscriptions/12
> {"active": false}
> ```
>
> and the next morning we turned it back on with `{"active": true}`. Both calls returned
> 200 and the subscription says it's active, but we haven't received a single webhook since,
> even though orders are definitely being created. Nothing appears in `/deliveries` for that
> subscription either.
>
> We have other subscriptions we haven't touched and they're working fine. Could you take a
> look? This is blocking our order sync.
>
> Thanks,
> Priya

**Acceptance criteria**
- The problem is reproduced, then fixed, and it can't silently come back.
- There's a short reply to the customer.
- All checks in `AGENTS.md` pass.

## Your task

1. **Create a branch for this ticket** before changing any code. It must be named
   `HL03_<short_description>`, e.g. `HL03_fix_partial_update`.
2. Reproduce the problem.
3. Fix it, and commit your work to your branch. Commit messages must start with `HL03: `.
4. Write a short (2–3 sentence) reply to Priya explaining what happened and anything she
   needs to do.
