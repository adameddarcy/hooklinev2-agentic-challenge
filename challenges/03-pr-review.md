# Challenge 3: Pull request review (about 10 minutes)

A teammate has opened a pull request from the branch `feature/subscription-search`:
**"Add filtering and pagination to GET /subscriptions"**. Find it in the repository's open
pull requests on GitHub.

```bash
git fetch origin
git diff main...origin/feature/subscription-search
# or: gh pr view --web / gh pr diff
```

## Your task

Review the PR as if you were the required approver.

1. Decide: **approve**, **approve with comments**, or **request changes / do not merge**.
2. Write the review you would post: a short summary and the specific issues, ordered by
   severity, each with the file/line and a suggested fix.
3. Be ready to explain how you checked each issue you raise. Don't just repeat what Claude
   said.

You don't need to fix the PR.
