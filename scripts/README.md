# scripts

Developer and CI helper scripts. Each script prints its usage when run without arguments.

| Script | What |
|---|---|
| [`dev-services.sh`](dev-services.sh) | Start / stop / reset the local emulators (Postgres, Mailpit) |
| [`install-git-hooks.sh`](install-git-hooks.sh) | Point this clone at `git-hooks/` (run once after cloning) |
| [`check-blocked-terms.py`](check-blocked-terms.py) | Fails on blocked terms in files, staged changes or commit messages. Used by the hooks and CI |
| [`git-hooks/`](git-hooks/) | `pre-commit` and `commit-msg` hooks |

Scripts that belong to one part of the code live in that part's folder instead.
