# MetaGit Conventions — BUZZ-X

> Conventions de méta-orchestration Git pour BUZZ-X.
> Références : ADR-007, INTENT-077.

## 1. Pas de submodules

L'écosystème gerivdb n'utilise PAS de submodules Git. Utiliser `git subtree` si nécessaire, avec ADR.

## 2. Verrouillage

Quand un agent travaille sur ce repo, il doit le verrouiller pour éviter les conflits.

## 3. Commits atomiques

- ≤ 3 fichiers modifiés entre deux commits.
- ≤ 30 minutes sans commit.
- Pas de `git add .` avec plus de 10 fichiers.

## 4. Remote Safety

Avant tout push :
1. `git remote -v`
2. `git branch`
3. `git log origin/main --oneline -5`
4. Push sans force.
