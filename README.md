# BUZZ-X — Hôte de Buzz@block pour N243

**Version** : 1.0
**Statut** : ACTIVE
**Strate** : L4-TOOLS

---

## Objectif

BUZZ-X contient **Buzz@block** (clone upstream de `block/buzz`) **non suivi** par git.

---

## Structure

BUZZ-X/
├── .gitignore          # Ignore Buzz@block/
├── .rssignore          # Exclut Buzz@block/ du RSS
├── README.md
├── patches/            # Patches L* appliqués à Buzz@block
│   └── prd-001-kind-registry.diff
└── Buzz@block/         # Clone upstream (non suivi)

---

## Stratégie de patch

Les modifications L* sont appliquées à `Buzz@block/` via des patches stockés dans `patches/`.

**Patch PRD-001** : `patches/prd-001-kind-registry.diff`
- Ajoute les kinds N243 (40050-40057) à `buzz-core/src/kind.rs`

**Application** :
cd Buzz@block
git apply ../patches/prd-001-kind-registry.diff

**Mise à jour depuis upstream** :
cd Buzz@block
git fetch upstream
git merge upstream/main
git apply ../patches/prd-001-kind-registry.diff  # si conflit

## Intégration N243

N243 dépend de `BUZZ-X/Buzz@block` via `Cargo.toml` :

buzz-core = { path = "../../BUZZ-X/Buzz@block/crates/buzz-core" }

## Mise à jour

cd D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X/Buzz@block
git fetch upstream
git merge upstream/main
