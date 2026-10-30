# Issues

How to report a bug, ask for a feature, and what happens after you open an issue.

**Security problems are never reported in a public issue.** Follow [`../SECURITY.md`](../SECURITY.md).

## Before opening an issue

1. Search [existing issues](https://github.com/Jayantkhandebharad/user-adoption-tool/issues),
   including closed ones.
2. Check you are on the latest release, or say which version / commit you run.
3. For a bug in the SDK, open the on-page debugger (`Guide.debug()`) — it often shows why a Flow
   did or did not appear.

## Choosing a form

New issues use forms ([`.github/ISSUE_TEMPLATE/`](../../.github/ISSUE_TEMPLATE/)):

| Form | Use it for |
|---|---|
| **Bug report** | Something behaves differently from the docs or from how it worked before |
| **Feature request** | A new capability or a change to existing behaviour |
| **Docs** | Missing, wrong or unclear documentation |

Blank issues are disabled so every issue has the information needed to act on it.

## Writing a good issue

- **One problem per issue.** Split unrelated things.
- **Title:** the symptom, not the guess — "Tooltip step renders behind sticky header", not
  "z-index bug".
- **Bug:** exact steps to reproduce, what you expected, what happened, versions (instance,
  browser, OS), and logs or screenshots. A minimal host page that reproduces it is the fastest
  route to a fix.
- **Feature:** the problem you are trying to solve and who has it, before the solution you have
  in mind. Say what you do today as a workaround.
- Never paste secrets, session cookies, identity-verification secrets or real end-user data.

## Labels

| Group | Labels | Meaning |
|---|---|---|
| Type | `bug`, `feature`, `docs`, `chore` | What kind of work |
| Area | `area:sdk`, `area:studio`, `area:backend`, `area:infra`, `area:builder`, `area:docs` | Which part of the code |
| Status | `needs-triage`, `needs-info`, `accepted`, `blocked` | Where the issue is in its life |
| Priority | `p0` (broken for everyone), `p1` (important), `p2` (normal), `p3` (nice to have) | Set during triage |
| Contributors | `good first issue`, `help wanted` | Good places to start |

## Lifecycle

```
opened ──► needs-triage ──► accepted ──► in progress (assigned, linked PR) ──► closed by PR
                 │
                 ├──► needs-info  (closed after 14 days without a reply)
                 └──► closed: duplicate / won't do / works as intended (with a reason)
```

1. **Triage** (maintainers, aim for within a week): add type, area and priority; ask for
   missing details; close duplicates with a link.
2. **Accepted** means we agree it should be done. Large features may need a spec in
   [`../specs/`](../specs/) or an ADR in [`../adr/`](../adr/) first — the issue will say so.
3. **Working on it:** comment that you are picking it up so a maintainer can assign you. If
   there is no activity for 30 days the issue is unassigned so someone else can take it.
4. **Closing:** reference the issue in the PR description (`Closes #123`) so it closes on merge.
