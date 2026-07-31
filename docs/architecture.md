# Architecture — BUZZ-X

**Dernière mise à jour :** 2026-07-31  
**Strate :** L4 — Interfaces utilisateur & Dev  
**Référence :** `STRATUM_RELAY.md` | `REPO.yaml`

---

## Posture

BUZZ-X est un **overlay ECOS-CLI** sur Buzz@block — une extension Nostr agnostique
de version qui se branche dans l'IDE via l'API `Nostr ^1.0.0`.

- Pas un fork Git de `Buzz@block`
- Pas de code Buzz@block embarqué
- Compatible avec toute version Buzz@block installée
- Intégration écosystème L* via ECOS-CLI

Voir `STRATUM_RELAY.md` R1 pour le détail de cette posture.

---

## Structure

```
BUZZ-X/
├── packages/
│   ├── buzz-ecos-integration/   ← ACTIF (CONFORME_NEXUS)
│   ├── github-copilot-ecos-integration/  ← SUSPENDU (HORS_NEXUS)
│   └── roo-code-ecos-integration/   ← ARCHIVÉ (HORS_NEXUS)
├── docs/                            ← documentation
├── src/                             ← scripts utilitaires
├── config/                          ← configuration
├── tests/                           ← tests
├── STRATUM_RELAY.md                 ← gouvernance L4
├── REPO.yaml                        ← identité RSS-v2
├── citizens.yaml                    ← contexte IA
└── ONTOLOGY_DECLARATION.yaml        ← déclaration ontologique
```

---

## Dépendances

- **Upstream :** BRAIN-DOCS, SKILLS, MIMIR, DOC-UNIV-DEV  
  (fournissent documentation, compétences, mémoire, universalité des documents)

- **Downstream :** Gitnote, GERIBOOKING, ECOS-VISION, COMET  
  (reçoivent les fonctionnalités de BUZZ-X)

- **IDE cible :** Buzz@block (Nostr client) — version `v7.3.54` au 2026-07-31

---

## Fonctionnement

BUZZ-X agit comme un **parasite agnostique intentionnel** (L4) qui :

1. S'installe **dans** Buzz@block installé via l'API Nostr/NIP-34
2. Fournit un accès aux **événements signés** (Nostr Event) pour la traçabilité
3. Connecte l'écosystème gerivdb via ECOS-CLI
4. Reste compatible avec **toute version** de Buzz@block grâce à l'API stable

---

## Avantages de l'overlay

- **Indépendance totale** vis-à-vis des mises à jour de Buzz@block
- **Compatibilité permanente** avec toute version Nostr-compatible
- **Intégration profonde** de l'écosystème gerivdb dans l'expérience de développement
- **Maintenance simplifiée** car aucun code upstream n'est dupliqué

---

## Migration depuis GeriCode

La structure de BUZZ-X est un calque adapté de GeriCode :

| Élément GeriCode | Équivalent BUZZ-X |
|---|---|
| L7 — Interfaces UI/Dev | L4 — Extensions & Intégrations |
| Kilo Code (VSCode) | Buzz@block (Nostr) |
| vscode ^1.80.0 API | Nostr ^1.0.0 API |
| kilocode-ecos-integration | buzz-ecos-integration |
