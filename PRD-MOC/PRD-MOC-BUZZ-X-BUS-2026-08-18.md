---
type: "PRD_MOC"
version: "3.0.0"
date: "2026-08-18"
status: "PROPOSED"
intent_hash: "0xBUZZ_BUS_WAZAA_AUTONOMOUS_20260818"
inherits: ["moc-governance"]
mox_gates:
  - P-108
  - P-109
---

# PRD MOC - BUZZ-X - Bus Buzz / WAZAA Autonome (v3.0 - État Réel)

## 1. RESUME EXECUTIF

Ce PRD MOC couvre la **tentative d'intégration de Buzz@block** dans l'écosystème gerivdb et son abandon.

**Conclusion v3.0** :
- **WAZAA est autonome** — son bus agents (`WazaaBusCore`) fonctionne sans Buzz@block
- **Buzz@block n'est pas déployable sur ENV2** — nécessite Postgres+Redis+WSL2/Hyper-V, tous indisponibles sur le Z600
- **L'overlay BUZZ-X a été retiré** — il n'apportait aucune valeur à WAZAA
- **Dette effacée** — PRD MOC v1.5 et v2.0 contenaient des claims "implémenté" non fondés

**Leçon** : Buzz@block est une infrastructure serveur qui nécessite des services externes lourds. Sur ENV2, la seule voie réaliste reste WAZAA seul.

**Source** : Audit BUZZ-X/WAZAA/TRIX du 2026-08-18
**IntentHash** : `0xBUZZ_BUS_WAZAA_AUTONOMOUS_20260818`
**Statut** : Généré le 2026-08-18 — reflète l'état réel après suppression de l'overlay

---

## 2. CONTEXTE ET PERIMETRE

### 2.1 Contexte

`BUZZ-X` était le repo destiné à intégrer `Buzz@block` (relay Nostr Rust) dans l'écosystème gerivdb.

**Buzz@block** est un clone upstream de `block/buzz` — relay Nostr Rust nécessitant :
- Postgres 17 (event store)
- Redis 7 (pub/sub, presence, typing)
- Docker / Podman / WSL2 pour orchestrer les services

**WAZAA** (`D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA`) est le **système d'orchestration multi-agents** de l'écosystème. Il contient déjà :
- `src/bus/WazaaBusCore` — bus async pub/sub in-process opérationnel
- `src/buzz/` — couche d'intégration Buzz (relay WebSocket, ACP, workflow, audit)
- `src/event_server.py` — serveur WebSocket pour events push
- `src/gitsem_bus.py` — bus sémantique git
- `agents/` — crewai + evolution engines

### 2.2 Pourquoi Buzz@block ne tourne pas sur ENV2

| Composant requis | Disponible sur ENV2 ? | Bloquant ? |
|------------------|----------------------|------------|
| Postgres 17 | ❌ Non installé | ✅ OUI |
| Redis 7 | ❌ Non installé | ✅ OUI |
| Docker Desktop | ❌ Non installé | ✅ OUI |
| Podman Desktop | ❌ Non installé | ✅ OUI |
| WSL2 | ❌ Hyper-V désactivé sur Z600 | ✅ OUI |
| WSL1 | ✅ Installé, mais incompatible avec containers | ❌ Insuffisant |

**Racine du blocage** : le Z600 a Hyper-V désactivé (instable sur Westmere). WSL2 nécessite Hyper-V. Sans WSL2, ni Docker ni Podman ne peuvent tourner nativement sur Windows.

### 2.3 Tentatives d'overlay BUZZ-X

| Version | Élément | Résultat |
|---------|---------|----------|
| v1.5 | PRD MOC prétendait "P0-P7 implémentés" | ❌ **Dette** — commits référencés sont dans TALEX, pas BUZZ-X |
| v1.5 | `.integration-marker` daté 2026-07-31 | ❌ **Dette** — aucune infrastructure confirmée |
| v2.0 | Création overlay `packages/buzz_ecos-integration/` | ❌ **Dette** — code retiré car il n'apporte rien à WAZAA |
| v2.0 | Tests overlay + demo JSONL | ❌ **Dette** — valide un bypass Buzz@block, pas une intégration |

**Conclusion** : l'overlay n'a jamais connecté WAZAA à Buzz@block. Il écrivait dans un fichier JSONL indépendant.

### 2.4 État actuel (v3.0)

| Composant | Rôle | État |
|-----------|------|------|
| **WAZAA `WazaaBusCore`** | Bus primaire agents | ✅ OPÉRATIONNEL |
| **WAZAA `BusMemoryBridge`** | Mémoire événementielle | ✅ OPÉRATIONNEL |
| **WAZAA `event_server.py`** | WebSocket server | ✅ OPÉRATIONNEL |
| **WAZAA `gitsem_bus.py`** | Bus sémantique git | ✅ OPÉRATIONNEL |
| **WAZAA `src/buzz/`** | Pont Buzz (relay, ACP, workflow) | ⚠️ Code présent, non connecté |
| **BUZZ-X overlay** | Intégration BUZZ-X ↔ WAZAA ↔ Buzz@block | ❌ SUPPRIMÉ |
| **Buzz@block relay** | Gateway Nostr | ❌ NON DÉPLOYABLE sur ENV2 |
| **C:\DevTools\bus\events.jsonl** | Event log | ✅ EXISTANT (indépendant de Buzz@block) |
| **C:\DevTools\bin\EventBus.ps1** | EventBus PowerShell | ✅ EXISTANT |

---

## 3. CE QUE WAZAA APPORTE SANS BUZZ-X

WAZAA est **déjà complet** sans aucun composant BUZZ-X :

| Fonctionnalité | Module WAZAA | Statut |
|----------------|--------------|--------|
| Bus agents pub/sub | `src/bus/wazaabus.py` | ✅ Opérationnel |
| Mémoire événementielle | `src/bus/bus_memory_bridge.py` | ✅ Opérationnel |
| WebSocket real-time | `src/event_server.py` | ✅ Opérationnel |
| Bus sémantique git | `src/gitsem_bus.py` | ✅ Opérationnel |
| Client Buzz relay | `src/buzz/relay.py` | ⚠️ Code présent, nécessite Buzz@block UP |
| ACP runners Zig | `src/buzz/acp.py` | ⚠️ Code présent, nécessite Buzz@block UP |
| Workflow Nostr | `src/buzz/workflow.py` | ⚠️ Code présent, nécessite Buzz@block UP |
| Audit WAL | `src/buzz/audit.py` | ✅ Opérationnel (local) |

**Aucune fonctionnalité WAZAA ne dépend de BUZZ-X ou de Buzz@block.**

---

## 4. COMPARAISON BUZZ-X vs WAZAA

| Critère | BUZZ-X (overlay) | WAZAA natif |
|---------|------------------|-------------|
| Bus agents | ❌ Nécessite overlay | ✅ `WazaaBusCore` |
| Persistance événements | ❌ JSONL via overlay | ✅ `BusMemoryBridge` |
| WebSocket server | ❌ Nécessite overlay | ✅ `event_server.py` |
| Git semantic bus | ❌ Nécessite overlay | ✅ `gitsem_bus.py` |
| Connectivité Buzz@block | ❌ Implémentée mais retirée | ⚠️ `BuzzRelayClient` existe, non connecté |
| Dépendance externe | ❌ Buzz@block requis | ✅ Aucune |

**L'overlay BUZZ-X ne résout aucun problème que WAZAA n'a pas déjà résolu.**

---

## 5. LEÇONS APPRISES

### 5.1 Erreurs commises

| Erreur | Impact | Correction |
|--------|--------|------------|
| PRD MOC v1.5 a claimé "implémenté" sans preuve | Dette documentaire | v3.0 corrige |
| Overlay créé sans valider la nécessité | Dette de code | Overlay supprimé |
| Documentation devancé l'implémentation | Fausse confiance | v3.0 reflète l'état réel |

### 5.2 Pourquoi l'overlay était inutile

1. **WAZAA est déjà autonome** — son bus fonctionne sans Buzz
2. **Buzz@block n'est pas déployable** — pas de Postgres/Redis/Docker sur ENV2
3. **L'overlay ne fait que du mapping** — pas de valeur ajoutée, juste de la translation
4. **Pas de consumer de l'overlay** — rien dans WAZAA ne l'utilisait

### 5.3 Règle retenue

> **Ne pas créer d'intégration sans consumer identifiable.**

Si WAZAA ne peut pas se connecter à Buzz@block (car ce dernier est down), l'intégration n'a pas de raison d'être.

---

## 6. ÉTAT FINAL DES DÉPENDANCES

### 6.1 Disponibles maintenant

| Dépendance | Localisation | Utilisation |
|------------|-------------|-------------|
| `WazaaBusCore` | `D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA\src\bus\` | Bus agents primaire |
| `BusMemoryBridge` | `D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA\src\bus\bus_memory_bridge.py` | Mémoire événementielle |
| `BuzzRelayClient` | `D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA\src\buzz\relay.py` | Client WebSocket (inactif) |
| `AcpClient` | `D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA\src\buzz\acp.py` | Invocation runners (inactif) |
| `cargo` | `C:\DevTools\.cargo\bin\cargo.exe` | Compilation Buzz@block (ne sert plus) |
| `events.jsonl` | `C:\DevTools\bus\events.jsonl` | Event log file-based |
| `EventBus.ps1` | `C:\DevTools\scripts\...\EventBus.ps1` | Event bus PowerShell |

### 6.2 Requis mais non disponibles

| Dépendance | Nécessaire pour | Bloquant ? |
|------------|----------------|-----------|
| Postgres 17 | Buzz@block event store | ✅ OUI |
| Redis 7 | Buzz@block pub/sub | ✅ OUI |
| Docker/Podman | Orchestration services | ✅ OUI |
| WSL2 | Alternative conteneurs | ✅ OUI — Hyper-V requis |

### 6.3 Jamais nécessaires

| Dépendance | Raison |
|------------|--------|
| Overlay BUZZ-X | WAZAA est autonome |
| LeCore | N'existe pas dans l'écosystème |
| SQLite embarqué | Nécessite fork Buzz@block, pas d'upstream |

---

## 7. RECOMMANDATIONS

### 7.1 Court terme (immédiat)

1. **WAZAA seul** — utiliser `WazaaBusCore` + `BusMemoryBridge` comme bus agents
2. **Supprimer l'overlay** — fait
3. **Corriger le PRD MOC** — ce document v3.0 remplace v1.5 et v2.0

### 7.2 Moyen terme (si infra disponible)

1. **Installer Docker Desktop** sur une autre machine
2. **Démarrer Buzz@block** sur cette machine
3. **Connecter `BuzzRelayClient`** de WAZAA vers Buzz@block
4. **Pas d'overlay nécessaire** — WAZAA se connecte directement

### 7.3 Long terme (hypothétique)

1. Upgrader ENV2 vers hardware supportant Hyper-V
2. Installer WSL2 + Podman
3. Déployer Buzz@block localement

---

## 8. TRACABILITE

### 8.1 Thought Chain

```yaml
thought_chain:
  - source: "Création overlay BUZZ-X (2026-08-18)"
    artifact: "packages/buzz_ecos_integration/ + tests + demo"
    result: "Code fonctionnel mais inutile — WAZAA est déjà autonome"
  - source: "Audit dépendances ENV2"
    artifact: "Docker/Postgres/Redis absents, Hyper-V désactivé"
    result: "Buzz@block non déployable sur Z600"
  - source: "Suppression overlay (2026-08-18)"
    artifact: "packages/ et scripts/demo_bus_degraded.py supprimés"
    result: "BUZZ-X redevient un clone upstream inerte"
  - source: "PRD MOC v3.0"
    artifact: "Document honnête sur l'état réel"
    intent_hash: "0xBUZZ_BUS_WAZAA_AUTONOMOUS_20260818"
```

### 8.2 References

- **Repo source** : `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X`
- **Buzz@block** : `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\Buzz@block`
- **WAZAA** : `D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA`
- **C:\DevTools** : `C:\DevTools` (cargo, bus, EventBus.ps1)
- **PRD MOC précédent** : `PRD-MOC-BUZZ-X-BUS-2026-08-18.md` (v2.0, avec overlay)
- **PRD MOC original** : `PRD-MOC-BUZZ-X-BUS-2026-08-17.md` (v1.5, état souhaité)
- **ADR TRIX** : ADR-2026-06-28-001 (pattern-router N+1/N+2/N+3/N+4)
- **ADR KIX** : ADR-2026-07-27-002 (orchestrateur cycle de vie runners)
- **ADR TRIX Git Arbiter** : ADR-2026-08-17-001 (accepted)

---

*Généré le 2026-08-18 — v3.0 : Overlay supprimé. WAZAA autonome. Buzz@block non déployable sur ENV2. Dette documentaire effacée.*
