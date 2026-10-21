# Git workflow for the lab

Infrastructure is code, so it is managed like code.

1. **Make a private copy** of the upstream repo, clone it on `admin01`, and add `upstream` as a second
   remote. `scripts/create-private-copy.sh` does all of it. GitHub forks of public repos are always public,
   so a copy that keeps the history is used instead. By hand:

   ```bash
   git clone --bare https://github.com/LibreOpsLab/server-security-lab.git
   gh repo create server-security-lab --private          # or create an empty private repo in the web UI
   git -C server-security-lab.git push --mirror https://github.com/<you>/server-security-lab.git
   git clone https://github.com/<you>/server-security-lab.git && cd server-security-lab
   git remote add upstream https://github.com/LibreOpsLab/server-security-lab.git
   ```

2. **Branch per week** (`week-04`), commit as you go, open a pull request into your own `main`, and
   merge it after your own review. A partner or your instructor can review at assessment checkpoints.
3. **Sync weekly:** `git fetch upstream`, read the change log, then merge `upstream/main` into `main`
   before starting the next week.
4. **Tag the finished week** (`week-04-done`). A wiped PC is rebuilt from the tags.
5. **Secrets** live in a gitignored `.env` and an Ansible vault, never in your repo.

```mermaid
flowchart LR
  U[upstream] -- fetch and merge --> M[your main]
  M -- branch --> W[week-NN]
  W -- pull request, your review --> M
  M -- tag week-NN-done --> T((tag))
  M -- push --> F[your private copy]
```

## A merge conflict is expected once

If you edited a file under `scaffold/`, `weeks/` or `docs/`, merging upstream may conflict. That is the
exercise: why you branch, how a conflict looks, and how to resolve it. Keep your own work in `build/`
and `portfolio/` to avoid it.
