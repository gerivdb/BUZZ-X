# Relation BUZZ-X ↔ N243

**Date** : 2026-07-31  
**Auteur** : N243 Engineering  
**Objet** : Intégration BUZZ-X ↔ N243 — couche overlay ↔ meta-orchestrateur

---

## 1. Contexte

BUZZ-X est l’overlay ECOS-CLI sur Buzz@block (API Nostr/NIP-34).  
N243 est le méta-orchestrateur L* qui pilote BUZZ-X via runners Zig/ACP et WAL ternaire.

---

## 2. Architecture cible

```
N243 (L4)
  │
  │  runners Zig + WAL ternaire
  ▼
BUZZ-X (L4)
  │
  │  API Nostr/NIP-34
  ▼
Buzz@block
  │
  │  Protocole Nostr
  ▼
Relay Nostr
```

---

## 3. Points de jonction

| Point | BUZZ-X | N243 |
|-------|--------|------|
| **Strate** | L4-TOOLS | L4-TOOLS |
| **Hub** | gerivdb/GOVERNANCE-HUB | gerivdb/GOVERNANCE-HUB |
| **Intent partagé** | INTENT-260 | INTENT-260 (buzz-workflow-binder) |
| **Overlay / Orchestrateur** | Overlay Nostr via API | Méta-orchestrateur Zig/ACP |
| **Persistance** | Buzz@block / WAL | wal.rs + buzz-audit |
| **Dépendance** | upstream : BRAIN-DOCS, SKILLS, MIMIR, DOC-UNIV-DEV | upstream : BUZZ-X, BRAIN-DOCS, SKILLS |

---

## 4. Règles de collaboration

1. **R1** — BUZZ-X n’est PAS un fork de Buzz@block ; N243 n’est PAS un fork de BUZZ-X.  
2. **R2** — N243 pilote BUZZ-X uniquement via API Nostr/NIP-34 et ACP/subprocess.  
3. **R3** — WAZAA est consommateur facultatif de BUZZ-X ; N243 orchestrateurs neutres.  
4. **R4** — Les événements Nostr `kind 40050-40057` sont définis par N243, transportés par BUZZ-X.

---

## 5. Actions validées

- [x] Scaffolding BUZZ-X + WAZAA bridge
- [x] Scaffolding N243 + dépendance BUZZ-X
- [x] Tests WAZAA ↔ BUZZ-X (11/11 passent)
- [x] Push branche `feat/rlm-wazaa` vers GitHub

---

*Document généré le 2026-07-31 — session CTULU Phase 28 / N243 Phase 1*
