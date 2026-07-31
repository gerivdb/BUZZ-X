# Cross-Repo Flow — BUZZ-X

> Conventions Git inter-répos pour BUZZ-X.

Ne jamais utiliser `cd` / `Set-Location` pour changer de repo. Chaque appel shell démarre dans le workspace root.

```bash
# OBLIGATOIRE
git -C "D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X" add "fichier"
git -C "D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X" commit -m "message"
git -C "D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X" push origin main
```

## 2. Cherry-pick inter-strates

Sens autorisé : descendant (L0 → L4) ou latéral (L1 → L1). Sens interdit : ascendant (L4 → L0) sans ADR.

```bash
# 1. Identifier le commit source
git -C "<path_source>" log --oneline -10

# 2. Dry-run du cherry-pick
git -C "<path_cible>" cherry-pick --no-commit <commit_sha>

# 3. Vérifier les conflits
git -C "<path_cible>" diff --cached --stat

# 4. Si clean → committer
git -C "<path_cible>" commit -m "cherry-pick(<strate_source>): <description>"
```

## 3. Remote Safety

Avant tout push :
1. `git remote -v`
2. `git branch`
3. `git log origin/main --oneline -5`
4. Push sans force.
