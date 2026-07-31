# Dry-Run Protocol — BUZZ-X

> Simulation avant action Git.

| Opération | Dry-run |
|---|---|
| `git push` vers `main` | ✅ Oui |
| `git push --force` | ✅ Oui + HITL |
| `git merge` (feature → main) | ✅ Oui |
| `git cherry-pick` inter-strate | ✅ Oui |
| `git rebase` sur branche partagée | ✅ Oui + HITL |
| `git reset --hard` | ✅ Oui + HITL |
| `git clean -fd` | ✅ Oui |

## 2. Commandes dry-run

```bash
# Push dry-run
git push --dry-run origin main
git log origin/main..HEAD --oneline

# Merge dry-run
git merge --no-commit --no-ff <branche>
git diff --cached --stat
git merge --abort

# Cherry-pick dry-run
git cherry-pick --no-commit <commit_sha>
git diff --cached --stat
git cherry-pick --abort
```
