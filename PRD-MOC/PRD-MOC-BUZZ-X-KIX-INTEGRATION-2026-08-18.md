---
type: "PRD_MOC"
version: "0.2.0"
date: "2026-08-18"
status: "PROPOSED"
intent_hash: "0xBUZZ_X_KIX_INTEGRATION_20260818"
inherits: ["moc-governance"]
mox_gates:
  - P-108
  - P-109
  - P-110
---

# PRD MOC - BUZZ-X - Intégration KIX (Non Fonctionnel)

## 1. RESUME EXECUTIF

Ce PRD MOC couvre l'intégration planifiée de **BUZZ-X comme runner Python dans KIX** dans le cadre de l'architecture KIX Generic Runner Wrapper.

**Rôle BUZZ-X dans l'architecture** :
- **Cible** : BUZZ-X est intégré comme runner `python` dans KIX (Phase 4)
- **Pattern** : Runner Wrapper minimaliste — KIX démarre/arrête/supervise `busrunner.py`
- **Statut actuel** : ❌ **NON FONCTIONNEL** — `busrunner.py` non opérationnel
- **Condition** : Intégration dans KIX **seulement après réparation** de BUZZ-X
- **Gate P-110** : BUZZ-X doit être fonctionnel avant intégration dans KIX

**Source** : ADR-2026-08-18-002-KIX-GENERIC-RUNNER-WRAPPER.md
**IntentHash** : `0xBUZZ_X_KIX_INTEGRATION_20260818`
**Statut** : Généré le 2026-08-18 — reflète l'état cible, pas l'état actuel

---

## 2. CONTEXTE ET PERIMETRE

### 2.1 Contexte

`BUZZ-X` (`D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X`) était le repo destiné à intégrer `Buzz@block` (relay Nostr Rust) dans l'écosystème gerivdb.

**Buzz@block** est un clone upstream de `block/buzz` — relay Nostr Rust nécessitant :
- Postgres 17 (event store)
- Redis 7 (pub/sub, presence, typing)
- Docker / Podman / WSL2 pour orchestrer les services

**Problème** : ENV2 (Z600) n'a aucune de ces dépendances. Le bus principal `busrunner.py` n'est pas opérationnel.

### 2.2 Périmètre BUZZ-X

| Composant | Rôle | État |
|-----------|------|------|
| **PythonRunner** | Wrapper `busrunner.py` | ❌ NON FONCTIONNEL |
| **runners.yaml** | Entrée `buzz` commentée | ⚠️ En attente |
| **Lifecycle** | `runner_lifecycle.py` | ⚠️ Code prêt, non testé |
| **Governance** | `governance_bus.py` | ⚠️ Code prêt, non testé |
| **Bridge** | `buzz_waazaa_bridge.py` | ⚠️ Code prêt, non testé |

---

## 3. ETAT ACTUEL BUZZ-X

| Élément | Fichier | Statut | Usage |
|---------|---------|--------|-------|
| Bus runner | `scripts/busrunner.py` | ❌ | Démarrage manuel, **non fonctionnel** |
| Lifecycle | `packages/buzz-ecos-integration/runner_lifecycle.py` | ⚠️ | Code prêt, **non testé car BUZZ-X non démarré** |
| Governance | `packages/buzz-ecos-integration/governance_bus.py` | ⚠️ | Code prêt, **non testé** |
| Bridge | `packages/buzz-ecos-integration/buzz_waazaa_bridge.py` | ⚠️ | Code prêt, **non testé** |

**Couverture BUZZ-X** : ❌ **NON FONCTIONNEL**. Les modules `packages/buzz-ecos-integration/` existent mais ne sont pas testés car le bus principal `busrunner.py` n'est pas opérationnel. Aucun événement Kind 60001 n'est émis dans l'état actuel.

**Impact sur l'architecture KIX** : BUZZ-X ne peut pas être intégré comme runner dans `runners.yaml` tant qu'il n'est pas fonctionnel. Les événements de cycle de vie KIX vers Buzz (Kind 60001) sont en attente de la mise en service de BUZZ-X.

---

## 4. ARCHITECTURE CIBLE BUZZ-X

### 4.1 Intégration comme runner `python` (Phase 4)

Une fois réparé, BUZZ-X sera intégré comme runner `python` dans KIX :

```yaml
runners:
  - name: buzz
    runner_type: python
    port: 60001
    working_dir: D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X
    entrypoint: scripts/busrunner.py
    depends_on: [kix, trixd]
    restart_policy: on-failure
```

### 4.2 Caractéristiques

- **Runner Python** : BUZZ-X est démarré comme service Python par KIX
- **Dépendances** : Dépend de KIX et TRIX (`depends_on: [kix, trixd]`)
- **Restart policy** : `on-failure` — redémarre uniquement en cas de crash
- **Événements Kind 60001** : Une fois fonctionnel, BUZZ-X émettra des événements de cycle de vie vers KIX

---

## 5. CONFIGURATION DECLARATIVE

### `config/runners.yaml` — Extrait BUZZ-X (commenté)

```yaml
runners:
  # BUS
  # - name: buzz
  #   runner_type: python
  #   port: 60001
  #   working_dir: D:/DO/WEB/TOOLS/L4-TOOLS/BUZZ-X
  #   entrypoint: scripts/busrunner.py
  #   depends_on: [kix, trixd]
  #   restart_policy: on-failure
  #   ⚠️ BUZZ-X NON FONCTIONNEL — à activer quand busrunner.py sera opérationnel
```

---

## 6. PLAN D'IMPLEMENTATION

### Phase 4 : WAZAA Integration + BUZZ-X Repair (Semaine 5)

| Action | Dépendance |
|--------|-----------|
| Réparer `busrunner.py` | — |
| Tester `runner_lifecycle.py` | busrunner.py fonctionnel |
| Tester `governance_bus.py` | busrunner.py fonctionnel |
| Tester `buzz_waazaa_bridge.py` | busrunner.py fonctionnel |
| Activer entrée `buzz` dans `runners.yaml` | busrunner.py fonctionnel |
| Tester événements Kind 60001 | busrunner.py fonctionnel |
| **Gate P-110** : BUZZ-X fonctionnel avant intégration dans KIX | **BLOCANT** |

---

## 7. DEPENDANCES

### 7.1 Non disponibles / non fonctionnels

| Dépendance | Localisation | Statut | Impact |
|------------|-------------|--------|--------|
| `busrunner.py` | `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\scripts\busrunner.py` | ❌ NON FONCTIONNEL | BUZZ-X exclu de la Phase 1 |
| `runner_lifecycle.py` | `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\packages\buzz-ecos-integration\runner_lifecycle.py` | ⚠️ Non testé | Événements Kind 60001 indisponibles |
| `governance_bus.py` | `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\packages\buzz-ecos-integration\governance_bus.py` | ⚠️ Non testé | Gouvernance bus indisponible |
| `buzz_waazaa_bridge.py` | `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\packages\buzz-ecos-integration\buzz_waazaa_bridge.py` | ⚠️ Non testé | Bridge WAZAA indisponible |

### 7.2 Requis Mais Non Disponibles

| Dépendance | Nécessaire pour | Bloquant ? |
|------------|----------------|-----------|
| `busrunner.py` fonctionnel | Runner `buzz` dans KIX | ✅ OUI — Phase 4 |
| `runners.yaml` entrée `buzz` | Configuration déclarative | ✅ OUI — Phase 4 |

---

## 8. RISQUES

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| BUZZ-X non fonctionnel | HIGH | CONFIRMÉ | **BUZZ-X exclu de la Phase 1** — réparation prioritaire avant intégration |

---

## 9. TRACABILITE

### 9.1 Thought Chain

```yaml
thought_chain:
  - source: "Diagnostic BUZZ-X : busrunner.py non fonctionnel"
    artifact: "BUZZ-X exclu de la Phase 1 — réparation prioritaire"
    intent_hash: "0xBUZZ_X_KIX_INTEGRATION_20260818"
  - source: "Proposition architecture Runner Wrapper"
    artifact: "Pattern : python runner pour BUZZ-X (Phase 4)"
```

### 9.2 References

- **ADR** : `ADR-2026-08-18-002-KIX-GENERIC-RUNNER-WRAPPER.md` (`D:\DO\WEB\TOOLS\L0-CANON\GOVERNANCE-HUB\ADR\`)
- **Repo BUZZ-X** : `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X`
- **Repo KIX** : `D:\DO\WEB\TOOLS\L2-PLATFORM\KIX`
- **PRD MOC BUZZ-X** : `PRD-MOC-BUZZ-X-BUS-2026-08-18.md` (BUZZ-X)
- **PRD MOC Principal** : `PRD-MOC-KIX-GENERIC-RUNNER-WRAPPER-2026-08-18.md` (TRIX)
- **MOX gates** : P-108, P-109, P-110

---

## 10. GOUVERNANCE

### 10.1 Règles d'acceptation

- [ ] Review par Lead BUZZ-X — **BUZZ-X doit être fonctionnel avant intégration**
- [ ] Review par Lead KIX
- [ ] Tests d'intégration Phase 4 passants

### 10.2 Gates

| Gate | Critère |
|------|---------|
| P-108 | ADR accepted par tous les leads |
| P-109 | Phase 1 implémentée et testée |
| P-110 | **BUZZ-X fonctionnel avant intégration dans KIX** |

### 10.3 Rollback

- Entrée `buzz` dans `runners.yaml` peut être commentée sans impact
- Les modules `packages/buzz-ecos-integration/` sont isolés

---

*Généré le 2026-08-18 — v0.2 : PRD MOC BUZZ-X KIX Integration. BUZZ-X NON FONCTIONNEL — réparation prioritaire avant intégration.*
