# DAG Patterns — BUZZ-X

> Conventions Git pour BUZZ-X.

Trouver l'ancêtre commun entre deux branches :

```bash
git merge-base <branche_a> <branche_b>
git diff $(git merge-base main feature/<nom>)..feature/<nom>
```

## 2. Ancestry-path

Tracer la lignée des commits :

```bash
git log --oneline --ancestry-path <commit_a>..<commit_b>
```

## 3. Invariant IDS-1

Le graphe des commits est un DAG. Aucun cycle n'est toléré.
