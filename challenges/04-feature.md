# Challenge 4: New feature (about 10 minutes)

## Ticket

| Field    | Value                                             |
|----------|---------------------------------------------------|
| ID       | **HL05**                                         |
| Type     | Feature                                           |
| Priority | P2                                                |
| Reporter | Product                                           |
| Summary  | Let customers rotate a subscription's signing secret |

> Customers who suspect their signing secret has leaked currently have to delete their
> subscription and create a new one, which loses their delivery history. Add a way to
> rotate the secret in place.
>
> **Acceptance criteria**
> - `POST /subscriptions/{id}/rotate-secret` generates a new random signing secret for the
>   subscription.
> - The response is `200 OK` with the subscription **including the new secret**, in the
>   same shape as the create response. This is the only time the new secret is shown.
> - Every other endpoint still never returns the secret.
> - Deliveries made after rotation are signed with the new secret. The old secret no
>   longer produces valid signatures.
> - An unknown id returns `404` with the same error body as the other subscription
>   endpoints.
> - `updated_at` changes. Everything else about the subscription (URL, event types, active
>   state, delivery history) is unchanged.
> - Tests cover the behaviour above. All checks in `AGENTS.md` pass.

## Your task

1. **Create a branch for this ticket** before changing any code. It must be named
   `HL05_<short_description>`, e.g. `HL05_rotate_secret`.
2. Implement the feature following the existing patterns in the codebase.
3. Commit your work to your branch. Commit messages must start with `HL05: `.
