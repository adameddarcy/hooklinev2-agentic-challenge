# Challenge 2: Customer bug report (about 10 minutes)

The following arrived through the support queue:

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

## Your task

1. Reproduce the problem.
2. Fix it, and make sure it can't silently come back.
3. Write a short (2–3 sentence) reply to Priya explaining what happened and anything she
   needs to do.
