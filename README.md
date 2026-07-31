# BUZZ-X — Hôte de Buzz@block pour N243

**Version** : 1.0
**Statut** : ACTIVE
**Strate** : L4-TOOLS

---

## Objectif

BUZZ-X contient **Buzz@block** (clone upstream de `block/buzz`) **non suivi** par git.

## Structure

BUZZ-X/
├── .gitignore          # Ignore Buzz@block/
├── .rssignore          # Exclut Buzz@block/ du RSS
├── README.md
└── Buzz@block/         # Clone upstream (non suivi)

## Intégration N243

N243 dépend de `BUZZ-X/Buzz@block` via `Cargo.toml` :

buzz-core = { path = "../../BUZZ-X/Buzz@block/crates/buzz-core" }

## Mise à jour

cd D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X/Buzz@block
git fetch upstream
git merge upstream/main
