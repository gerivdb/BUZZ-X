---
relay_version: 7
repo: gerivdb/BUZZ-X
strate: L4
lifecycle: ACTIVE
vague: 7
synchro: '2026-07-31'
hub: gerivdb/GOVERNANCE-HUB
intent_hash: '0xA7B8C9D0E1F2G3H4'
stratum_relay: STRATUM_RELAY.md
rss_compliance:
  version: v2.3
  profile: CITIZEN
  score: 11/11
  status: CONFORME
  last_audit: '2026-07-31'
rules:
  - id: R1
    assertion: >-
      BUZZ-X n'est PAS un fork Git de Buzz@block.
      C'est un overlay ECOS-CLI : une extension Nostr-compatible qui s'installe DANS Buzz@block
      via l'API Nostr/NIP-34, sans embarquer de code upstream.
      Posture : parasite agnostique intentionnel (L4 — interface dev).
      Compatibilite upstream = compatibilite API Nostr stable, pas suivi de version Buzz@block.
    status: VERIFIED
    severity: MEDIUM
    decision_date: '2026-07-31'
  - id: R2
    assertion: COMET gere l'automation browser — pas de scraping ailleurs.
    status: UNVERIFIED
    severity: HIGH
  - id: R3
    assertion: appflowy-mcp-server remplace Notion — pas d'API Notion.
    status: UNVERIFIED
    severity: MEDIUM
---

# STRATUM RELAY — BUZZ-X (L4)

**VAGUE**: 7 | **Synchro**: 2026-07-31 | **Hub**: gerivdb/GOVERNANCE-HUB

---

## Identité stratique

- **Strate** : `L4-TOOLS` — Extensions & Intégrations
- **Role canonique** : Overlay ECOS-CLI sur Buzz@block — extension Nostr agnostique qui intègre l'écosystème gerivdb dans l'IDE via l'API Nostr/NIP-34
- **Posture** : Parasite agnostique intentionnel (extension Nostr-compatible, API `Nostr ^1.0.0`)
- **Parent** : L3
- **Enfants** : L5

---

## Navigation rapide

- PRD canonique : `GOVERNANCE-HUB/PRD/PRD_BUZZ-X_INTEGRATION.md`
- Substrat cognitif : `gerivdb/LLM-REPO` (L1b — privé)
- Standards repo : `REPO-STANDARDS-L4.md`
- Transit map : `VERSUS/urban_ontology_verse/TRANSIT/transit_map.yaml`

---

## Architecture (clarifie Vague 7)

BUZZ-X **n'est pas un fork Git** de `Buzz@block`. C'est un **overlay ECOS-CLI** :
une extension Nostr-compatible (`packages/buzz-ecos-integration`) qui se branche *dans*
Buzz@block via l'API Nostr stable (`Nostr ^1.0.0`), sans embarquer de code upstream.

- Buzz@block est installé séparément sur la machine (Nostr client v7.3.54)
- BUZZ-X est agnostique de la version Buzz@block - compatibilité via API Nostr uniquement
- Aucun suivi de version upstream requis - pas de risque de drift sémantique

---

## Conformite RSS-v2.3 (Vague 7)

| Exigence CITIZEN | Statut |
|---|---|
| `README.md` | ✅ |
| `.gitignore` | ✅ |
| `.rssignore` | ✅ (exception `packages/` documentee) |
| `REPO.yaml` | ✅ |
| `citizens.yaml` | ✅ |
| `ONTOLOGY_DECLARATION.yaml` | ✅ |
| `docs/` | ✅ |
| `src/` | ✅ |
| `config/` | ✅ |
| `tests/` | ✅ |
| `.github/` | ✅ |
| **Score** | **11/11** |

---

## Statut packages

| Package | Statut | Raison |
|---|---|---|
| `buzz-ecos-integration` | ✅ CONFORME_NEXUS | Cable CTULU INTENT-260 |
| `github-copilot-ecos-integration` | ❌ HORS_NEXUS | Copilot Pro non souscrit |
| `roo-code-ecos-integration` | ❌ HORS_NEXUS | Roo Code archive 2026-05-15 |

---

## Dependances directes

**Parents (amont)** :
- BRAIN-DOCS
- SKILLS
- MIMIR
- DOC-UNIV-DEV

**Enfants (aval)** :
- Gitnote
- GERIBOOKING
- ECOS-VISION
- COMET

---

## Vague de mise a jour

| Vague | Contenu | Statut |
|---|---|---|
| **5** | Frontmatter YAML + regles structurees + phi_cps null honnete | Deploye |
| **6** | R4+R5+R6 neutralisation Copilot+Roo Code + R1 clarifie overlay vs fork + CTULU INTENT-260 | Deploye |
| **7 (courante)** | RSS-v2.3 CITIZEN 11/11 + R7 + rss_compliance block + section conformite | Deploye |

---

*Mise a jour manuelle 2026-07-31 — session CTULU Phase 28*
