# Git Engineering — BUZZ-X

> Conventions Git minimales pour BUZZ-X.

Utiliser `git -C` pour toute opération sur ce repo depuis un autre chemin :

```bash
git -C "D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X" status
git -C "D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X" add <fichier>
git -C "D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X" commit -m "message"
git -C "D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X" push origin main
```

Ne jamais utiliser `cd` / `Set-Location` entre appels shell.

## 2. DAG Patterns

- Vérifier `git merge-base` avant tout merge.
- Utiliser `git log --ancestry-path` pour tracer les cherry-picks.
- Respecter la hiérarchie des strates : L0 → L1 → L2 → L3 → L4 → L5.

## 3. Dry-Run Protocol

- Tout `git push` vers `main` passe d'abord par `git push --dry-run origin main`.
- Tout `git cherry-pick` inter-strate passe d'abord par `git cherry-pick --no-commit`.
- Tout `git merge` passe d'abord par `git merge --no-commit --no-ff`.

## 4. Hooks Catalog

- `pre-commit` : vérification d'encodage UTF-8.
- `pre-push` : vérifications avant push distant.

## 5. MetaGit Conventions

- Pas de submodules.
- Pas de `git add .` dans ce repo.
- Commits atomiques : ≤ 3 fichiers, ≤ 30 min.
