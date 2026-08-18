---
type: PRD_MOC
version: "1.0.0"
date: "2026-08-18"
status: proposed
intent_hash: 0xPRD_WAZAA_ECOSYSTEM_BUS_KIX_GERICODE_GOV_20260818
inherits:
  - PRD-MOC-KG-L-WAZAA-BRIDGE-2026-08-18
  - INTENT-2026-08-18-ECOSYSTEM-BUS-WAZAA-KIX-GERICODE
mox_gates:
  - P-106
  - P-107
repo: gerivdb/BUZZ-X
author: gerivdb
created: "2026-08-18"
---

# PRD MOC — WAZAA Écosystème Bus : Intégration KIX / GeriCode / GOVERNANCE-HUB

**Rôle** : Définir WAZAA comme **bus central unifié** de l'écosystème gerivdb, en intégrant KIX (L2-PLATFORM), GeriCode (L2-PLATFORM) et GOVERNANCE-HUB (L0-CANON) via la triade Publisher / Bus Core / Subscriber.

**Contexte** : WAZAA existe comme bus async Python. KIX orchestre les runners RLM mais **écrit directement dans KG-L** en by-passant WAZAA. GeriCode (extension VS Code + formats) est **isolé du bus**. GOVERNANCE-HUB publie des topics governance mais n'a **aucun subscriber**.

**Source** : Audit direct du code source WAZAA, KIX, GeriCode, GOVERNANCE-HUB — 2026-08-18

---

## 1. VISION

### 1.1 Définition

**WAZAA Écosystème Bus** = bus d'événements unifié + triade pub/sub + intégration de tous les repos via des publishers/subscribers dédiés.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GOVERNANCE-HUB (L0-CANON)                    │
│  SOT, ADR, INTENT, repo registry                                    │
│         │                                                           │
│    publish "adr_update" / "intent_update" / "repo_registry_changed" │
└────────┼─────────────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────────────┐
│                         WAZAA Bus Central (L4-TOOLS)                 │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────────┐ │
│  │ Publishers   │   │ Bus Core     │   │ Subscribers              │ │
│  │ ─ WazaaMsg   │──►│ WazaaBusCore │──►│ ─ Handler Async         │ │
│  │   per repo   │   │ Persistence  │   │   per repo               │ │
│  │   KIX,       │   │ Store(WAL)   │   │   KG-L, KIX, GeriCode,   │ │
│  │   GeriCode,  │   │ Search(FTS)  │   │   GOVERNANCE-HUB, etc.   │ │
│  │   GovHub     │   │              │   │                          │ │
│  └──────────────┘   └──────────────┘   └─────────────────────────┘ │
└────────┼─────────────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────────────┐
│                         KIX (L2-PLATFORM)                            │
│  Orchestrateur runners RLM (Flask, port 8800)                        │
│  publie "runner_started / stopped / zeta_detected"                  │
└────────┼─────────────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────────────┐
│                         GeriCode (L2-PLATFORM)                        │
│  Extension VS Code + formats (PSL, piano-diff, q243)                  │
│  publie "format_parsed / validation_failed / extension_activated"   │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Principe fondamental

- **WAZAA** = canal de communication pub/sub temps réel entre **tous** les repos
- **Bus Core** = `WazaaBusCore` — dispatcher async, persistance SQLite+JSONL, recherche FTS5
- **Publisher** = repo source qui publie un message sur topic `{strate}/{repo}/{event}`
- **Subscriber** = repo consommateur qui reçoit le message via handler async
- **KG-L** = bridge optionnel du bus (UN seul : `WazaaKGSubscriber`), jamais d'écriture directe

---

## 2. ARCHITECTURE — LA TRIADE PUB/SUB

### 2.1 Triade fondamentale

```
┌──────────────┐       ┌─────────────────┐       ┌──────────────┐
│  Publisher   │ ────► │   Bus Core      │ ────► │  Subscriber  │
│  (Repo A)    │       │   (WazaaBusCore)│       │  (Repo B)    │
└──────────────┘       └─────────────────┘       └──────────────┘
     Topic                    Topic                      Topic
   L2-PLATFORM/               ANY                        ANY
   KIX/runner_started       L4-TOOLS/*              L2-PLATFORM/KIX/health_check

                    ┌──────────────┐
                    │  WazaaMessage  │ ◄── Persistance WAL (SQLite + JSONL)
                    └──────────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │    KG-L      │ ◄── UN SEUL bridge (WazaaKGSubscriber)
                    └──────────────┘
```

### 2.2 Publisher (Source → Bus)

| Aspect | Détail |
|---|---|
| **Rôle** | Émettre un `WazaaMessage` sur un topic spécifique |
| **Emplacement** | Code métier du repo source (ex: Flask endpoint KIX) |
| **Implémentation** | `WazaaClient` (async HTTP pub) ou `WazaaBusCore` direct (in-process) |
| **Pattern** | `await bus.publish(topic, WazaaMessage(payload, msg_type, intent_hash))` |
| **Responsabilité repo** | Chaque repo possède un publisher dédié dans WAZAA (`src/publishers/`) |

### 2.3 Bus Core (Broker central)

| Composant | Fichier | Rôle |
|---|---|---|
| `WazaaBusCore` | `src/bus/wazaabus.py` | Dispatcher async, wildcard topics |
| `InProcessBackend` | `src/bus/wazaabus.py` | Queue asyncio (dev mode) |
| `PersistentStore` | `src/bus/persistent_store.py` | SQLite + JSONL append-only |
| `BusSearch` | `src/bus/search.py` | FTS5 full-text search |
| `WazaaKGSubscriber` | `src/bus/wazaa_kg_subscriber.py` | **UN SEUL** bridge vers KG-L |
| `AuditChain` | `src/bus/audit_chain.py` | Hash-chain tamper-evident |

### 2.4 Subscriber (Bus → Destination)

| Aspect | Détail |
|---|---|
| **Rôle** | Recevoir les messages et déclencher l'action métier |
| **Emplacement** | Citizen dans WAZAA (`src/wazaa_bus_citizens/`) ou service repo |
| **Implémentation** | Handler async enregistré via `bus.subscribe(topic, handler)` |
| **Pattern** | `@bus.subscribe("L0-CANON/GOVERNANCE-HUB/restart_policy")` |
| **Responsabilité repo** | Chaque repo possède un subscriber dédié dans WAZAA |

---

## 3. TOPICS WAZAA PAR REPO INTÉGRÉ

### 3.1 KIX (L2-PLATFORM)

| Topic | Direction | Message Type | Contenu |
|-------|-----------|--------------|---------|
| `L2-PLATFORM/KIX/runner_started` | KIX → WAZAA | ACTION | `runner`, `pid`, `port`, `timestamp` |
| `L2-PLATFORM/KIX/runner_stopped` | KIX → WAZAA | ACTION | `runner`, `exit_code`, `uptime` |
| `L2-PLATFORM/KIX/runner_restarted` | KIX → WAZAA | ACTION | `runner`, `old_pid`, `new_pid` |
| `L2-PLATFORM/KIX/zombie_detected` | KIX → WAZAA | FRICTION | `pid`, `name`, `cpu_percent` |
| `L2-PLATFORM/KIX/phi_cps_update` | KIX → WAZAA | DRIFT | `service`, `phi_cps`, `delta` |
| `L2-PLATFORM/KIX/health_status` | KIX → WAZAA | HEALTH | `overall`, `runners`, `uptime` |
| `L2-PLATFORM/KIX/alert_triggered` | KIX → WAZAA | FRICTION | `alert_type`, `severity`, `details` |
| `L2-PLATFORM/KIX/restart_policy` | WAZAA → KIX | ACTION | Commande de restart depuis governance |
| `L2-PLATFORM/KIX/health_check` | WAZAA → KIX | ACTION | Demande de health check cross-service |

### 3.2 GeriCode (L2-PLATFORM)

> **Note** : Le SOT enregistre GeriCode avec `layer: L4_TOOLS` mais `local_path: L2-PLATFORM`. Voir §9.3 pour la correction.

| Topic | Direction | Message Type | Contenu |
|-------|-----------|--------------|---------|
| `L2-PLATFORM/GeriCode/format_parsed` | GeriCode → WAZAA | ACTION | `path`, `format`, `symbols_count` |
| `L2-PLATFORM/GeriCode/validation_failed` | GeriCode → WAZAA | DRIFT | `path`, `rule`, `severity`, `message` |
| `L2-PLATFORM/GeriCode/extension_activated` | GeriCode → WAZAA | ACTION | `extension_id`, `version`, `timestamp` |
| `L2-PLATFORM/GeriCode/extension_deactivated` | GeriCode → WAZAA | ACTION | `extension_id`, `reason` |
| `L2-PLATFORM/GeriCode/dag_updated` | GeriCode → WAZAA | DRIFT | `dag_name`, `nodes_added`, `edges_added` |

### 3.3 GOVERNANCE-HUB (L0-CANON)

| Topic | Direction | Message Type | Contenu |
|-------|-----------|--------------|---------|
| `L0-CANON/GOVERNANCE-HUB/adr_update` | GOVERNANCE-HUB → WAZAA | INTENT | `adr_id`, `title`, `status`, `author` |
| `L0-CANON/GOVERNANCE-HUB/intent_update` | GOVERNANCE-HUB → WAZAA | INTENT | `intent_hash`, `title`, `status` |
| `L0-CANON/GOVERNANCE-HUB/repo_registry_changed` | GOVERNANCE-HUB → WAZAA | DRIFT | `repo_name`, `layer`, `local_path` |
| `L0-CANON/GOVERNANCE-HUB/command` | WAZAA → GOVERNANCE-HUB | ACTION | Policy commands for other repos |
| `L0-CANON/GOVERNANCE-HUB/strate_audit` | GOVERNANCE-HUB → WAZAA | DRIFT | Audit résultats, discrepancies |

### 3.4 Topics WAZAA existants (intacts)

| Topic | Source | Status |
|-------|--------|--------|
| `L4-TOOLS/*/friction` | WAZAA citizens | ✅ Existant |
| `L4-TOOLS/*/action` | WAZAA citizens | ✅ Existant |
| `L4-TOOLS/*/drift` | WAZAA citizens | ✅ Existant |
| `L4-TOOLS/*/trix_execution` | TRIX | ✅ Existant |
| `L3-CITIZENS/*/llux_inference` | LLUX | ✅ Existant |
| `L4-TOOLS/*/korx_state` | KORX | ✅ Existant |
| `L4-TOOLS/*/flex_numa` | FLEX | ✅ Existant |
| `L4-TOOLS/*/flex_cache` | FLEX | ✅ Existant |
| `L4-TOOLS/*/flex_thermal` | FLEX | ✅ Existant |
| `L1-INFRA/*/nexus_command` | NEXUS | ✅ Existant |
| `L1-INFRA/*/wal_entry` | NEXUS | ✅ Existant |
| `L0-CANON/*/adr_update` | GOVERNANCE-HUB | ✅ Existant (publisher) |
| `L0-CANON/*/intent_update` | GOVERNANCE-HUB | ✅ Existant (publisher) |

### 3.5 Nouveaux topics à créer

| Topic | Catégorie | Priorité |
|-------|-----------|----------|
| `L2-PLATFORM/KIX/*` | Runner lifecycle | P0 |
| `L2-PLATFORM/GeriCode/*` | Format/Extension | P1 |
| `L0-CANON/GOVERNANCE-HUB/repo_registry_changed` | SOT sync | P1 |
| `L0-CANON/GOVERNANCE-HUB/command` | Gouvernance dispatch | P1 |

---

## 4. RESPONSABILITÉS PAR COMPOSANT

### 4.1 WAZAA (L4-TOOLS) — Bus Central

| Responsabilité | Statut |
|---|---|
| Pub/Sub async inter-repos | ✅ `WazaaBusCore` implémenté |
| Persistance événementielle | ✅ `PersistentStore` (SQLite + JSONL) |
| Full-text search | ✅ `BusSearch` (FTS5) |
| Bridge KG-L | ✅ `WazaaKGSubscriber` (UN SEUL) |
| `KixPublisher` | ❌ À créer |
| `GericodePublisher` | ❌ À créer |
| `GovernanceHubSubscriber` | ❌ À créer |
| `KixSubscriber` | ❌ À créer |
| `GericodeSubscriber` | ❀ À créer |

### 4.2 KIX (L2-PLATFORM) — Orchestrateur Runners

| Responsabilité | Statut |
|---|---|
| Start/Stop/Restart runners | ✅ Flask endpoints |
| Health-check cross-service | ✅ `/healthz`, `/readyz` |
| Détection zombies | ✅ `zombie_monitor` |
| Calcul φ-CPS | ✅ `immune.py` |
| Publication WAZAA (runner_started etc.) | ❌ À migrer |
| Réception commandes WAZAA | ❌ À créer |
| Écriture directe KG-L (`kg_l_kix_bridge.py`) | ⚠️ À **supprimer** |

### 4.3 GeriCode (L2-PLATFORM) — Extension VS Code + Formats

| Responsabilité | Statut |
|---|---|
| Extension VS Code ACT Protocol | ✅ `act-protocol/` |
| Formats PSL / piano-diff / q243 | ✅ `src/` |
| Publication événements WAZAA | ❌ À créer |
| Réception politiques governance | ❌ À créer |

### 4.4 GOVERNANCE-HUB (L0-CANON) — Source de Vérité

| Responsabilité | Statut |
|---|---|
| SOT (`known_repositories.yaml`) | ✅ v5.1 |
| Publication ADR/INTENT → WAZAA | ✅ `GovernancePublisher` |
| Consommation événements WAZAA | ❌ À créer |
| Audit cohérence strates | ✅ `Selina` |

---

## 5. INTÉGRATION KIX — MIGRATION VERS WAZAA

### 5.1 Contexte

KIX utilise actuellement `kg_l_kix_bridge.py` pour écrire **directement** dans KG-L :

```python
# ❌ PATTERN ACTUEL (interdit)
from kg_l import KGLRuntime
runtime = KGLRuntime(name="kix-live")
runtime.add_node(id=f"runner:{name}", kind="runner", **metadata)
```

### 5.2 Migration cible

```python
# ✅ PATTERN CIBLE (obligatoire)
from wazaa.bus import WazaaBusCore
bus = WazaaBusCore()

# Publication WAZAA
await bus.publish("L2-PLATFORM/KIX/runner_started", WazaaMessage(
    msg_type=MessageType.ACTION,
    source="L2-PLATFORM/KIX",
    target="L4-TOOLS/KG-L",
    intent_hash="0xKIX_RUNNER_LIFECYCLE_20260818",
    payload={
        "runner": name,
        "pid": process.pid,
        "port": runner.port,
        "timestamp": utcnow().isoformat()
    }
))
# KG-L subscriber WAZAA convertit automatiquement en KGNode/KGEdge
```

### 5.3 Subscriber KIX (contrôle governance)

Le subscriber KIX écoute les topics governance pour exécuter des actions :

```python
# Dans WAZAA/src/wazaa_bus_citizens/kix_subscriber.py
class KixSubscriber:
    """Subscriber pour les topics governance dirigés vers KIX."""
    
    async def handle_restart_policy(self, msg: WazaaMessage):
        """Restart policy reçue de GOVERNANCE-HUB."""
        runner = msg.payload["runner"]
        await self.restart_runner(runner)
        await bus.publish("L2-PLATFORM/KIX/runner_restarted", WazaaMessage(
            msg_type=MessageType.ACTION,
            source="L2-PLATFORM/KIX",
            payload={"runner": runner, "new_pid": new_pid}
        ))
    
    async def handle_health_check(self, msg: WazaaMessage):
        """Health check request reçue."""
        status = self.get_cross_service_status()
        await bus.publish("L2-PLATFORM/KIX/health_status", WazaaMessage(
            msg_type=MessageType.HEALTH,
            source="L2-PLATFORM/KIX",
            payload=status
        ))
```

---

## 6. INTÉGRATION GERICODE — BRANCHEMENT BUS

### 6.1 Contexte

GeriCode n'a **aucune** intégration WAZAA. L'extension VS Code et les formats PSL/piano-diff/q243 sont totalement isolés.

### 6.2 Integration pattern

GeriCode utilisera le `wazaa-client` HTTP pour publier des événements depuis le processus Node.js :

```typescript
// Dans act-protocol/src/extension.ts
import { WazaaClient } from 'wazaa-client';

const bus = new WazaaClient({ host: 'localhost', port: 8799 });

// Publier lors du parsing d'un fichier PSL
bus.publish('L2-PLATFORM/GeriCode/format_parsed', {
  path: document.uri.path,
  format: 'psl',
  symbols_count: ast.symbols.size,
  intent_hash: '0xGERICODE_FORMAT_PSL_20260818'
});

// Publier sur validation échouée
bus.publish('L2-PLATFORM/GeriCode/validation_failed', {
  path: document.uri.path,
  rule: 'PSL-001',
  severity: 'error',
  message: 'Missing intent_hash in frontmatter'
});
```

### 6.3 Subscriber GeriCode

GeriCode consomme les topics governance pour appliquer des politiques :

```python
# Dans WAZAA/src/wazaa_bus_citizens/gericode_subscriber.py
async def handle_adr_update(msg: WazaaMessage):
    """Appliquer une nouvelle ADR dans VS Code."""
    adr_id = msg.payload["adr_id"]
    # Trigger VS Code notification via extension API
    pass

async def handle_intent_update(msg: WazaaMessage):
    """Mettre à jour le contexte IntentHash dans l'extension."""
    intent_hash = msg.payload["intent_hash"]
    # Update extension state
    pass
```

---

## 7. INTÉGRATION GOVERNANCE-HUB — SUBSCRIBER

### 7.1 Contexte

GOVERNANCE-HUB publie déjà via `GovernancePublisher` mais **n'a aucun subscriber** pour consommer les événements des autres repos.

### 7.2 Subscriber à créer

```python
# Dans WAZAA/src/wazaa_bus_citizens/governance_hub_subscriber.py
class GovernanceHubSubscriber:
    """Subscriber pour GOVERNANCE-HUB — consomme les événements cross-repos."""
    
    async def handle_kix_runner_started(self, msg: WazaaMessage):
        """KIX publie un runner_started — enrichir SOT."""
        runner_name = msg.payload["runner"]
        pid = msg.payload["pid"]
        port = msg.payload["port"]
        # Update runner registry in SOT
        self.update_runner_sot(runner_name, pid, port)
    
    async def handle_gericode_format_parsed(self, msg: WazaaMessage):
        """GeriCode parse un format — logger pour audit."""
        path = msg.payload["path"]
        fmt = msg.payload["format"]
        # Log pour SOT registry
        self.log_format_activity(path, fmt)
```

---

## 8. TOPOLOGIE DE COMMUNICATION

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WAZAA Bus Central (L4-TOOLS)                   │
│                                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐ │
│  │ KixPublisher│   │ GovPub      │   │ GeriPub     │   │ ...         │ │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘ │
│         │                 │                 │                 │        │
│         ▼                 ▼                 ▼                 ▼        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     WazaaBusCore                                 │   │
│  │  Topics: {strate}/{repo}/{event} avec wildcards                  │   │
│  │  Persistence: SQLite + JSONL WAL                                  │   │
│  │  Search: FTS5                                                      │   │
│  └──────────────────────────┬──────────────────────────┬─────────────┘   │
│                             │                          │               │
│         ┌────────────────────┼────────────────────┐     │               │
│         ▼                    ▼                    ▼     ▼               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ KG-L Sub    │  │ KIX Sub     │  │ GeriCode Sub │  │ GovHub Sub  │   │
│  │ (UN SEUL)   │  │ (new)       │  │ (new)        │  │ (new)       │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
        │               │              │                │
┌───────▼───────┐  ┌────▼─────┐  ┌─────▼──────┐  ┌────▼────┐
│ KG-L (L4)     │  │ KIX (L2) │  │ GeriCode(L2) │  │ GOV-HUB │
│ Graph engine  │  │ Runners  │  │ VS Code     │  │ SOT/L0  │
└───────────────┘  └──────────┘  └────────────┘  └─────────┘
```

### 8.1 Flux de communication

```
1. KIX publie → L2-PLATFORM/KIX/runner_started → WAZAA → KG-L + GOVERNANCE-HUB
2. GeriCode publie → L2-PLATFORM/GeriCode/format_parsed → WAZAA → GOVERNANCE-HUB
3. GOVERNANCE-HUB publie → L0-CANON/GOVERNANCE-HUB/adr_update → WAZAA → KIX + GeriCode
4. WAZAA KG-L bridge → convertit WazaaMessage → KGNode/KGEdge (UN SEUL point d'écriture KG-L)
```

---

## 9. CORRECTIONS DE SÊTE

### 9.1 Suppression du bridge direct KIX → KG-L

**Supprimer** : `D:\DO\WEB\TOOLS\L2-PLATFORM\KIX\src\kg_l_kix_bridge.py`
- Remplacé par : `KixPublisher` dans WAZAA (`src/publishers/kix_publisher.py`)
- KIX publie sur WAZAA → `WazaaKGSubscriber` convertit → KG-L

### 9.2 Correction Gericode dans le SOT

Le `known_repositories.yaml` enregistre GeriCode avec un `layer` incohérent :

```yaml
# Actuel (INCORRECT)
name: GeriCode
layer: L4_TOOLS          # ❌ Ne correspond pas à local_path
local_path: D:\DO\WEB\TOOLS\L2-PLATFORM\GeriCode  # ✅ L2-PLATFORM

# Corrigé
name: GeriCode
layer: L2_PLATFORM       # ✅ Coherent avec local_path
local_path: D:\DO\WEB\TOOLS\L2-PLATFORM\GeriCode
```

### 9.3 Stratification claire

| Repo | Strate | Layer logique | Rôle |
|---|---|---|---|
| WAZAA | L4-TOOLS | N3 | Bus central pub/sub |
| KIX | L2-PLATFORM | N3 | Orchestrateur runners RLM |
| GeriCode | L2-PLATFORM | — | Extension VS Code + formats |
| GOVERNANCE-HUB | L0-CANON | N1/N4 | SOT, ADR, INTENT |
| KG-L | L4-TOOLS | N2 | Langage + moteur graphe (bridge via WAZAA) |

---

## 10. PLAN D'IMPLÉMENTATION

### Phase 1 — Publishers (P0)

| Sprint | Livrable | Repo | Dépendance |
|--------|----------|------|------------|
| 1.1 | `KixPublisher` dans WAZAA | WAZAA | WazaaBusCore |
| 1.2 | `GericodePublisher` dans WAZAA | WAZAA | WazaaBusCore |
| 1.3 | Topics KIX ajoutés à `wazaa_kg_config.yaml` | WAZAA | — |
| 1.4 | Topics GeriCode ajoutés à config | WAZAA | — |

### Phase 2 — Subscribers (P0)

| Sprint | Livrable | Repo | Dépendance |
|--------|----------|------|------------|
| 2.1 | `KixSubscriber` (control commands) | WAZAA | Phase 1 |
| 2.2 | `GericodeSubscriber` (policy apply) | WAZAA | Phase 1 |
| 2.3 | `GovernanceHubSubscriber` (cross-repo events) | WAZAA | Phase 1 |

### Phase 3 — Migration KIX (P0)

| Sprint | Livrable | Repo | Dépendance |
|--------|----------|------|------------|
| 3.1 | Supprimer `kg_l_kix_bridge.py` | KIX | Phase 1 |
| 3.2 | Intégrer `KixPublisher` dans Flask endpoints | KIX | Phase 1 |
| 3.3 | Intégrer `KixSubscriber` pour commands | KIX | Phase 2 |
| 3.4 | Tests e2e WAZAA ↔ KIX | WAZAA + KIX | Phases 1-3 |

### Phase 4 — Intégration GeriCode (P1)

| Sprint | Livrable | Repo | Dépendance |
|--------|----------|------|------------|
| 4.1 | `gericode-wazaa-client` npm package | GeriCode | Phase 1 |
| 4.2 | Intégrer publisher dans extension VS Code | GeriCode | Phase 4.1 |
| 4.3 | Intégrer subscriber pour ADR/INTENT updates | GeriCode | Phase 2 |
| 4.4 | Tests e2e WAZAA ↔ GeriCode | WAZAA + GeriCode | Phases 1-4 |

### Phase 5 — Gouvernance (P1)

| Sprint | Livrable | Repo | Dépendance |
|--------|----------|------|------------|
| 5.1 | `GovernanceHubSubscriber` actif | GOVERNANCE-HUB | Phase 2 |
| 5.2 | Corriger `layer: L4_TOOLS` → `L2_PLATFORM` GeriCode | GOVERNANCE-HUB | — |
| 5.3 | SOTA sync via `repo_registry_changed` topic | GOVERNANCE-HUB | Phase 5.1 |

---

## 11. RÈGLES D'INTÉGRATION

### RÈGLE-1 — WAZAA est le seul chemin vers KG-L

> KIX, GeriCode et tous autres composants **NE DOIVENT PAS** importer `kg_l` directement.
> Toute donnée KG-L passe par `WazaaKGSubscriber` → `WazaaToKGAdapter`.

```python
# ❌ INTERDIT
from kg_l import KGLRuntime
runtime = KGLRuntime()  # Direct write to KG-L

# ✅ OBLIGATOIRE  
from wazaa.bus import WazaaBusCore
bus = WazaaBusCore()
await bus.publish("L2-PLATFORM/KIX/runner_started", msg)
# WazaaKGSubscriber convertit automatiquement
```

### RÈGLE-2 — Un publisher = un repo source

Chaque repo possède son publisher dédié dans WAZAA. Le publisher encapsule la logique métier du repo et publie sur topics `{strate}/{repo}/{event}`.

### RÈGLE-3 — Un subscriber = un repo consommateur

Chaque repo possède son subscriber dédié dans WAZAA. Le subscriber reçoit les messages et déclenche les actions métier.

### RÈGLE-4 — Naming convention stricte

| Composant | Strate | Pattern topic |
|---|---|---|
| KIX | L2-PLATFORM | `L2-PLATFORM/KIX/<event>` |
| GeriCode | L2-PLATFORM | `L2-PLATFORM/GeriCode/<event>` |
| GOVERNANCE-HUB | L0-CANON | `L0-CANON/GOVERNANCE-HUB/<event>` |
| WAZAA interne | L4-TOOLS | `L4-TOOLS/WAZAA/<event>` |

### RÈGLE-5 — KIX ne peut plus écrire KG-L directement

> Toute migration de `kg_l_kix_bridge.py` vers WAZAA publisher doit passer par :
> 1. Création du `KixPublisher`
> 2. Ajout des topics au config YAML
> 3. Tests e2e sur topics existants
> 4. Suppression du bridge direct

---

## 12. CRITÈRES DE SUCCÈS

| Critère | Cible | Mesure |
|---|---|---|
| Couverture bus | 100% des événements cross-repos transitent par WAZAA | Audit topics WAZAA |
| Isolation KG-L | 0 composants écrivant directement dans KG-L | Grep `from kg_l` hors WAZAA |
| Latence pub/sub | < 50ms publish→deliver | Benchmark WazaaBusCore |
| Traçabilité WAL | 100% des événements avec WAL entry | Audit JSONL |
| SOT cohérence | 0 repos avec `layer` ≠ `local_path` strate | Audit known_repositories.yaml |
| Tests e2e | 100% passants | pytest coverage |
| Migration KIX | 100% des runner events via WAZAA | Audit KIX endpoints |
| Intégration GeriCode | Événements publiés depuis VS Code extension | Test extension activation |

---

## 13. RISQUES

| Risque | Impact | Probabilité | Mitigation |
|---|---|---|---|
| Migration KIX casse KG-L bridge existant | HIGH | MOYENNE | Migration progressive + tests e2e sur topics existants |
| GeriCode Node.js → WAZAA integration | MEDIUM | MOYENNE | `wazaa-client` npm package, fallback in-process |
| Subscriber GOVERNANCE-HUB overload | MEDIUM | FAIBLE | Filtrage par topic + backpressure |
| SOT correction GeriCode layer | LOW | FAIBLE | Validation post-commit via selina_ci |
| BDCP constraint | HIGH | ÉLEVÉE | WAZAA/KIX/GeriCode/GovHub en BDCP — topics locaux seulement |

---

## 14. TRACABILITÉ

### Thought Chain

```yaml
thought_chain:
  - source: "Vérification post-PRD MOC KG-L-WAZAA (2026-08-18)"
    observation: "KIX écrit directement dans KG-L via kg_l_kix_bridge.py"
    observation: "GeriCode n'a aucune intégration WAZAA"
    observation: "GOVERNANCE-HUB publie mais ne consomme pas"
    result: "Écosystème fragmenté: 3 composants hors bus central"
  - source: "INTENT-2026-08-18-ECOSYSTEM-BUS-WAZAA-KIX-GERICODE"
    action: "Formaliser la triade Publisher/Bus/Subscriber"
    result: "Tous les repos intègrent un publisher + subscriber via WAZAA"
  - source: "Règle BDCP (bdcp-kiva-workflow.md)"
    constraint: "Bus inter-repo local, pas de sortie BDCP"
    result: "Tous les topics WAZAA sont locaux (localhost)"
```

### Références

| Document | Repo | Path |
|----------|------|------|
| PRD MOC KG-L ↔ WAZAA Bridge | BUZZ-X | `PRD-MOC/PRD-MOC-KG-L-WAZAA-BRIDGE-2026-08-18.md` |
| INTENT Écosystème Bus | GOVERNANCE-HUB | `INTENTS/INTENT-2026-08-18-ECOSYSTEM-BUS-WAZAA-KIX-GERICODE.md` |
| WAZAA bus core | WAZAA | `src/bus/wazaabus.py` |
| WAZAA message schema | WAZAA | `src/bus/message.py` |
| WAZAA KG subscriber | WAZAA | `src/bus/wazaa_kg_subscriber.py` |
| WAZAA KG config | WAZAA | `config/wazaa_kg_config.yaml` |
| KIX kg_l_bridge | KIX | `src/kg_l_kix_bridge.py` |
| KIX Flask app | KIX | `service.py` |
| KIX ADR | KIX | `ADR-2026-07-27-002-KIX.md` |
| GeriCode act-protocol | GeriCode | `act-protocol/` |
| Governance publisher | WAZAA | `src/publishers/governance_publisher.py` |
| ADR KIX orchestrator | GOVERNANCE-HUB | `ADR-2026-07-27-016-kix-orchestrator` |
| LLM_BOOT_PROTOCOL | GOVERNANCE-HUB | `LLM_BOOT_PROTOCOL.md` |

---

*Document généré le 2026-08-18 — IntentHash: 0xPRD_WAZAA_ECOSYSTEM_BUS_KIX_GERICODE_GOV_20260818*
