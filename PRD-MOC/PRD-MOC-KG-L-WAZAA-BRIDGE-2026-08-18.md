---
type: PRD_MOC
version: "2.0.0"
date: "2026-08-18"
status: PROPOSED
intent_hash: "0xKG_WAZAA_FULL_STACK_20260818"
inherits: ["moc-governance", "PRD-MOC-BUZZ-X-BUS-2026-08-18", "PRD-MOC-KG-L-WAZAA-BRIDGE-2026-08-18"]
mox_gates:
  - P-108
  - P-109
---

# PRD MOC — KG-WAZAA : Bus Écosystème Complet

**Rôle** : Définir WAZAA/KG-WAZAA comme **bus d’événements transverse** de l’écosystème gerivdb, couvrant toutes les couches depuis le bare metal ENV2 jusqu’à la production, avec canaux de communication structurés et Knowledge Graphs par environnement.

**Contexte** : WAZAA existe déjà comme bus Python + orchestration multi-agents. Ce PRD MOC étend sa portée pour en faire l’**épine dorsale événementielle** de tout l’écosystème, remplaçant l’architecture KG-BUZZ abandonnée.

**Source** : Audit direct du code WAZAA, KG-L, CTULU, KORX, LLUX, TRIX, NEXUS, FLEX, GeriCode — 2026-08-18

---

## 1. VISION

### 1.1 Définition

**KG-WAZAA** = bus événementiel unifié + graphes de connaissance par environnement, couvrant :

```
Bare Metal (ENV2)
    ↓
Runtime (TRIX, KORX, LLUX)
    ↓
Bus/Events (WAZAA + KG-L)
    ↓
Orchestration (NEXUS, SABRE, OUROBOROS)
    ↓
Governance (ADRs, INTENTs, WAL)
    ↓
Production (CrewAI, monitoring, dashboards)
```

### 1.2 Principe

- **WAZAA** = canal de communication temps réel entre toutes les couches
- **KG-L** = moteur de graphe optionnel pour structurer les événements en connaissances
- **FLEX** = fournisseur de métadonnées matérielles (NUMA, cache, thermal)
- **KORX/LLUX/TRIX** = consommateurs/producteurs d’événements WAZAA
- **NEXUS** = orchestrateur central
- **SABRE/OUROBOROS** = outils de génération/maintenance

---

## 2. ARCHITECTURE EN COUCHES

### 2.1 Vue d’ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION / ORCHESTRATION                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ CrewAI Agents│  │ Dashboards  │  │ TALEX / HOLMES          │  │
│  │ (WAZAA)     │  │ (Grafana)   │  │ (narration / causal)    │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                     │                │
│         └────────────────┼─────────────────────┘                │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    WAZAA (Bus Central)                      │ │
│  │  Topics:                                                     │ │
│  │   L4-TOOLS/*/friction  | L4-TOOLS/*/action  | L4-TOOLS/*/drift│ │
│  │   L4-TOOLS/*/urn_validate | L4-TOOLS/*/guard | L4-TOOLS/*/health│ │
│  │   L4-TOOLS/*/propagation | L4-TOOLS/*/governance            │ │
│  │   L3-CITIZENS/*/llux_inference | L4-TOOLS/*/trix_execution  │ │
│  │   L4-TOOLS/*/flex_numa | L4-TOOLS/*/flex_cache             │ │
│  └───────────────────────────┬─────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐              │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐    │
│  │ KG-L        │  │ NEXUS (KIVA-CLI)│  │ AuditChain       │    │
│  │ (graphe)    │  │ (orchestration) │  │ (WAL hash-chain) │    │
│  └─────────────┘  └─────────────────┘  └──────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RUNTIME / EXECUTION                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ TRIX        │  │ KORX        │  │ LLUX                    │  │
│  │ (WSL1)      │  │ (state machine)│  │ (GGML/SSE4.2)          │  │
│  │ dispatch 243│  │ .kbin mmap  │  │ kernels Westmere       │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                     │                │
│         └────────────────┼─────────────────────┘                │
│                          ▼                                       │
│  ┌─────────────┐  ┌─────────────────────────────────────────┐   │
│  │ FLEX        │  │ CodeDB-E5620                             │   │
│  │ (Harmony    │  │ (Code Intelligence / MCP server)          │   │
│  │ Topology)   │  │ Trigram search | Dep graph | MCP tools    │   │
│  │ NUMA/cache  │  │ Zig 0.15 | MCP + HTTP | Zero-deps         │   │
│  │ thermal     │  └───────────────────┬─────────────────────┘   │
│  └──────┬──────┘                     │                           │
│         │                            │                           │
│         └────────────────────────────┼───────────────────────────┘
│                                      ▼
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    ENV2 (Bare Metal)                         │ │
│  │  HP Z600 | 2× Xeon E5620 | 24 Go DDR3 | SSD                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Couches et responsabilités

| Couche | Composants | Rôle | Communications |
|--------|-----------|------|----------------|
| **Bare Metal** | ENV2 (Z600), NUMA, CPU, RAM, SSD | Infrastructure physique | Métriques → FLEX |
| **Runtime** | TRIX, KORX, LLUX, FLEX, CodeDB-E5620 | Exécution souveraine + intelligence code | Événements → WAZAA |
| **Bus/Events** | WAZAA, KG-L (langage + moteur), AuditChain | Communication + graphe | Topics WAZAA + KG-L edges |
| **Orchestration** | NEXUS, SABRE, OUROBOROS | Coordination + génération | CLI + WAZAA events |
| **Governance** | ADRs, INTENTs, WAL, POOP | Décisions + traçabilité | WAL + KG-L governed_by |
| **Production** | CrewAI, Grafana, TALEX/HOLMES | Agents + monitoring + narration | WAZAA consume + KG-L query |

### 2.3 Distinction KG-L : Langage vs Moteur

KG-L est composé de **deux responsabilités distinctes** :

#### 2.3.1 KG-L Langage (spécification)

| Élément | Location | Rôle |
|---------|----------|------|
| **EdgeKind registry** | `KG-L/src/runtime/edge_kind_registry.py` | 15 EdgeKind canoniques (10 Pipeline Ascendant + 5 causaux) |
| **Node schema** | `KGNode` (dataclass) | `id`, `kind`, `metadata` |
| **Edge schema** | `KGEdge` (dataclass) | `src`, `dst`, `kind`, `metadata` |
| **Query syntax** | `KG-L/src/query/kg_l_query.py` | `MATCH`, `WHERE`, `RETURN` |
| **Backends** | JSON, YAML, SQLite | Formats de sérialisation |

**Rôle** : Définir le **contrat** du graphe — quels nœuds, quels edges, quelles relations sont autorisés.

#### 2.3.2 KG-L Moteur (exécution)

| Élément | Location | Rôle |
|---------|----------|------|
| **KGRuntime** | `KG-L/src/runtime/kg_l.py` | `add_node()`, `add_edge()`, `query()`, `visualize()`, `validate()`, `proof()` |
| **Query executor** | `KG-L/src/query/kg_l_query.py` | `active_instances()`, `zombie_instances()`, `dependency_chain()` |
| **Adapters** | `kg_l_trix_adapter.py`, `kg_l_worktree_adapter.py`, `kg_l_kix_adapter.py` | Conversion d’états runtime → nœuds KG-L |
| **Governance** | `kg_l_governance.py` | Évaluation des edges `prevents` |
| **Backends impl** | JSON/YAML/SQLite | Implémentation concrète |

**Rôle** : **Exécuter** le langage — stocker, requêter, visualiser, valider les graphes.

#### 2.3.3 Responsabilités WAZAA vis-à-vis de KG-L

| Couche | Responsabilité |
|--------|----------------|
| **WAZAA** | Produire des événements (`WazaaMessage`) avec `msg_type`, `source`, `target`, `intent_hash` |
| **KG-L Langage** | Définir les EdgeKind (`causes`, `governed_by`, `depends_on`) et les node kinds (`FRICTION`, `ACTION`, `DRIFT`, etc.) |
| **KG-L Moteur** | Exécuter la conversion `WazaaMessage → KGNode/KGEdge` via adapters |
| **WAZAA→KG-L Bridge** | `kg_l_wazaa_adapter.py` + `WazaaKGSubscriber` — pont entre les deux |

---

## 3. CANAUX DE COMMUNICATION

### 3.1 Topics WAZAA par couche

| Couche | Topics WAZAA | Direction | Contenu |
|--------|--------------|-----------|---------|
| **Bare Metal** | `L4-TOOLS/*/flex_numa`<br>`L4-TOOLS/*/flex_cache`<br>`L4-TOOLS/*/flex_thermal` | FLEX → WAZAA | NUMA topology, cache hit rate, thermal state |
| **Runtime** | `L4-TOOLS/*/trix_execution`<br>`L3-CITIZENS/*/llux_inference`<br>`L4-TOOLS/*/korx_state` | TRIX/LLUX/KORX → WAZAA | Runner status, inference metrics, state transitions |
| **Bus/Events** | `L4-TOOLS/*/friction`<br>`L4-TOOLS/*/action`<br>`L4-TOOLS/*/drift`<br>`L4-TOOLS/*/urn_validate`<br>`L4-TOOLS/*/propagation`<br>`L4-TOOLS/*/guard`<br>`L4-TOOLS/*/governance` | WAZAA → KG-L + NEXUS | Événements métier filtrés |
| **Orchestration** | `L1-INFRA/*/nexus_command`<br>`L4-TOOLS/*/sabre_topology`<br>`L4-TOOLS/*/ouroboros_factory` | NEXUS/SABRE/OUROBOROS → WAZAA | CLI commands, topology plans, factory runs |
| **Governance** | `L1-INFRA/*/wal_entry`<br>`L0-CANON/*/adr_update`<br>`L0-CANON/*/intent_update` | WAL/ADRs/INTENTs → WAZAA | WAL entries, ADR changes, intent updates |
| **Production** | `L3-CITIZENS/*/agent_status`<br>`L4-TOOLS/*/dashboard_metric`<br>`L4-TOOLS/*/holmes_narration` | CrewAI/Grafana/HOLMES → WAZAA | Agent heartbeats, metrics, narratives |

### 3.2 Direction des flux

```
Bare Metal ──[métriques]──► FLEX ──[events]──► WAZAA
Runtime ────[events]──────► WAZAA
WAZAA ──────[filtered]────► KG-L (optionnel)
WAZAA ──────[events]──────► NEXUS/SABRE/OUROBOROS
WAZAA ──────[events]──────► CrewAI/Grafana/HOLMES
KG-L ───────[queries]─────► TALEX/HOLMES
NEXUS ──────[commands]────► TRIX/KORX/LLUX
```

---

## 4. KNOWLEDGE GRAPHS PAR ENVIRONNEMENT

### 4.1 Concept

KG-WAZAA supporte plusieurs **graphes de connaissance spécialisés** selon l’environnement :

| KG | Environnement | Contenu | Usage |
|----|---------------|---------|-------|
| **KG-ENV2** | ENV2 (production) | Hardware state, runners, NUMA, cache, thermal | Optimisation temps réel |
| **KG-DEV** | Développement | Workflows, tests, branches, commits | Debug, reconstitution |
| **KG-PROD** | Production | Incidents, déploiements, agents | Gouvernance, audit |
| **KG-GOV** | Governance | ADRs, INTENTs, WAL, POOP | Décisions, traçabilité |

### 4.2 Structure commune

Tous les KGs partagent :
- **EdgeKind** : `causes`, `confounds`, `prevents`, `extends`, `depends_on`, `governed_by`, `implemented_by`, `tested_by`
- **Node kinds** : `FRICTION`, `ACTION`, `DRIFT`, `RUNNER`, `CONTAINER`, `WORKTREE`, `ADR`, `INTENT`, `WAL_ENTRY`, `NUMA_NODE`, `CACHE_STATS`, `THERMAL_STATE`
- **Backends** : JSON, YAML, SQLite (via KG-L)

### 4.3 Exemple : KG-ENV2

```python
# Nœuds matériels
KGNode(id="env2:numa:0", kind="NUMA_NODE", metadata={"cpus": [0,1,2,3,4,5,6,7], "mem_gb": 12})
KGNode(id="env2:numa:1", kind="NUMA_NODE", metadata={"cpus": [8,9,10,11,12,13,14,15], "mem_gb": 12})

# Événements FLEX
KGNode(id="wazaa:flex:001", kind="THERMAL_STATE", metadata={"temp_c": 65, "fan_speed": 1200})
KGNode(id="wazaa:flex:002", kind="CACHE_STATS", metadata={"l1_hit_rate": 0.92, "l2_hit_rate": 0.87})

# Edges causaux
KGEdge(src="env2:numa:0", dst="wazaa:flex:001", kind="affects")
KGEdge(src="wazaa:flex:002", dst="L4-TOOLS:LLUX:inference", kind="causes")
```

---

## 5. INTÉGRATION FLEX (BARE METAL)

### 5.1 Rôle

FLEX est le **fournisseur de métadonnées matérielles** pour KG-WAZAA.

### 5.2 Topics FLEX → WAZAA

| Topic | Contenu | Fréquence |
|-------|---------|-----------|
| `L4-TOOLS/*/flex_numa` | NUMA topology, CPU affinity | On change |
| `L4-TOOLS/*/flex_cache` | L1/L2/L3 cache stats, hit rates | 1s |
| `L4-TOOLS/*/flex_thermal` | Température CPU, fan speed | 5s |

### 5.3 Adapter FLEX → KG-L

```python
# À créer dans FLEX/src/bus/flex_kg_adapter.py
class FlexToKGAdapter:
    def numa_to_kg_node(self, numa_info: Dict) -> KGNode:
        return KGNode(
            id=f"env2:numa:{numa_info['node_id']}",
            kind="NUMA_NODE",
            metadata={
                "cpus": numa_info["cpus"],
                "mem_gb": numa_info["mem_gb"],
                "source": "FLEX"
            }
        )

    def cache_to_kg_node(self, cache_stats: Dict) -> KGNode:
        return KGNode(
            id=f"wazaa:flex:cache:{uuid4()}",
            kind="CACHE_STATS",
            metadata={
                "l1_hit_rate": cache_stats["l1_hit_rate"],
                "l2_hit_rate": cache_stats["l2_hit_rate"],
                "source": "FLEX"
            }
        )
```

---

## 5.4 Intégration CodeDB-E5620 (Code Intelligence)

### 5.4.1 Rôle

**CodeDB-E5620** est le **serveur d'intelligence code** de l'écosystème.

Contrairement à FLEX (qui fournit les métriques **matérielles** : NUMA, cache, thermal), CodeDB-E5620 fournit les métriques **logicielles** : indexation structurelle, recherche trigram, graphe de dépendances, MCP tools.

### 5.4.2 Distinction FLEX vs CodeDB-E5620

| Dimension | FLEX | CodeDB-E5620 |
|-----------|------|--------------|
| **Domaine** | Bare metal / hardware | Code / software |
| **Métriques** | NUMA, cache, thermal, affinity | Index, search, deps, outlines |
| **Output** | `L4-TOOLS/*/flex_*` topics | `codedb_*` MCP tools + HTTP |
| **Consommateurs** | FLEX → WAZAA → KG-L | Agents (CrewAI, Kilo) via MCP |
| **Stockage** | Runtime (pas de persistance) | `~/.codedb/` + `codedb.snapshot` |
| **Langage** | Python | Zig 0.15 (core) + Python (integration) |
| **Complémentarité** | Oui — CodeDB-E5620 interroge FLEX via `flex_integration.py` |

### 5.4.3 Responsabilités CodeDB-E5620

| Responsabilité | Mécanisme |
|----------------|-----------|
| **Indexation structurelle** | Parse Zig, Python, TS/JS, Rust, PHP, C# — tree-sitter |
| **Recherche trigram** | O(1) trigram index — 538x plus rapide que ripgrep |
| **Graphe de dépendances** | Reverse dep graph — quel fichier importe quoi |
| **MCP tools** | 16 outils MCP (tree, outline, search, word, deps, read, edit, ...) |
| **File watcher** | Polling 2s + FilteredWalker (.git, node_modules, etc.) |
| **Snapshot portable** | `codedb.snapshot` — index complet en un fichier |

### 5.4.4 Topics WAZAA (potentiels)

| Topic | Direction | Contenu |
|-------|-----------|---------|
| `L4-TOOLS/*/codedb_index` | CodeDB-E5620 → WAZAA | Indexation terminée, fichier scanné |
| `L4-TOOLS/*/codedb_search` | WAZAA → CodeDB-E5620 | Requête de recherche |
| `L4-TOOLS/*/codedb_deps` | CodeDB-E5620 → WAZAA | Graphe de dépendances mis à jour |
| `L4-TOOLS/*/codedb_edit` | WAZAA → CodeDB-E5620 | Édition atomique de fichier |

### 5.4.5 Adapter CodeDB-E5620 → KG-L

```python
# À créer dans CodeDB-E5620/codedb/kg_l_adapter.py
class CodeDBToKGAdapter:
    def index_event_to_node(self, event: Dict) -> KGNode:
        return KGNode(
            id=f"codedb:index:{event['path']}",
            kind="CODE_INDEX",
            metadata={
                "path": event["path"],
                "language": event["language"],
                "symbols": event["symbols"],
                "source": "CodeDB-E5620"
            }
        )

    def search_event_to_edge(self, event: Dict, target_node_id: str) -> KGEdge:
        return KGEdge(
            src=f"codedb:search:{event['query']}",
            dst=target_node_id,
            kind="references",
            metadata={"query": event["query"], "results": event["results"]}
        )
```

### 5.4.6 Intégration FLEX → CodeDB-E5620

Le fichier `flex_integration.py` dans CodeDB-E5620 démontre la complémentarité :

```python
# CodeDB-E5620 interroge FLEX pour configurer son worker pool
from flex_integration import get_topology, get_worker_config, get_thermal_status

topology = get_topology()        # NUMA topology depuis FLEX
worker_config = get_worker_config(workers=16)  # Affinity pools depuis FLEX
thermal = get_thermal_status()   # Seuils thermiques depuis FLEX
```

Cela permet à CodeDB-E5620 d'ajuster sa worker pool selon la topology matérielle d'ENV2.

### 5.4.7 Nodes KG-L dérivés

| Événement CodeDB-E5620 | Topic WAZAA | KG-L Node |
|------------------------|-------------|-----------|
| File indexed | `L4-TOOLS/*/codedb_index` | `kind=CODE_INDEX`, `language=zig/python/ts` |
| Symbol found | `L4-TOOLS/*/codedb_search` | `kind=SYMBOL`, `name=AgentRegistry` |
| Dep graph updated | `L4-TOOLS/*/codedb_deps` | `kind=DEP_GRAPH`, `edges=N` |
| File edited | `L4-TOOLS/*/codedb_edit` | `kind=CODE_EDIT`, `path=src/foo.zig` |

---

## 6. INTÉGRATION TRIX / KORX / LLUX (RUNTIME)

### 6.1 TRIX

| Événement | Topic WAZAA | KG-L Node |
|-----------|-------------|-----------|
| Container started | `L4-TOOLS/*/trix_execution` | `kind=RUNNER`, `state=RUNNING` |
| Container stopped | `L4-TOOLS/*/trix_execution` | `kind=RUNNER`, `state=STOPPED` |
| Syscall dispatch | `L4-TOOLS/*/trix_execution` | `kind=DISPATCH`, `table_entry=243` |

### 6.2 KORX

| Événement | Topic WAZAA | KG-L Node |
|-----------|-------------|-----------|
| State compiled | `L4-TOOLS/*/korx_state` | `kind=STATE_MACHINE`, `state=COMPILED` |
| .kbin loaded | `L4-TOOLS/*/korx_state` | `kind=KBIN`, `size_bytes=512` |
| @Q PRUNE triggered | `L4-TOOLS/*/korx_state` | `kind=PRUNE`, `reduced_paths=N` |

### 6.3 LLUX

| Événement | Topic WAZAA | KG-L Node |
|-----------|-------------|-----------|
| Inference started | `L3-CITIZENS/*/llux_inference` | `kind=INFERENCE`, `state=RUNNING` |
| Inference completed | `L3-CITIZENS/*/llux_inference` | `kind=INFERENCE`, `state=COMPLETED` |
| Kernel SSE4.2 executed | `L3-CITIZENS/*/llux_inference` | `kind=KERNEL`, `type=SSE4.2` |

---

## 7. INTÉGRATION NEXUS / SABRE / OUROBOROS (ORCHESTRATION)

### 7.1 NEXUS (KIVA-CLI)

| Événement | Topic WAZAA | KG-L Node |
|-----------|-------------|-----------|
| Project created | `L1-INFRA/*/nexus_command` | `kind=PROJECT`, `action=CREATE` |
| φ-CPS drift detected | `L1-INFRA/*/nexus_command` | `kind=DRIFT`, `score=φ` |
| WAL entry written | `L1-INFRA/*/wal_entry` | `kind=WAL_ENTRY`, `hash=0x...` |

### 7.2 SABRE

| Événement | Topic WAZAA | KG-L Node |
|-----------|-------------|-----------|
| Topology planned | `L4-TOOLS/*/sabre_topology` | `kind=TOPOLOGY`, `action=PLAN` |
| Topology applied | `L4-TOOLS/*/sabre_topology` | `kind=TOPOLOGY`, `action=APPLY` |
| Topology diff computed | `L4-TOOLS/*/sabre_topology` | `kind=TOPOLOGY`, `action=DIFF` |

### 7.3 OUROBOROS

| Événement | Topic WAZAA | KG-L Node |
|-----------|-------------|-----------|
| Factory scan started | `L4-TOOLS/*/ouroboros_factory` | `kind=FACTORY`, `action=SCAN` |
| Artefacts generated | `L4-TOOLS/*/ouroboros_factory` | `kind=ARTEFACT`, `type=INTENT/PRD/EPIC/ADR` |
| Integrity validated | `L4-TOOLS/*/ouroboros_factory` | `kind=INTEGRITY`, `score=1.0` |

---

## 8. GOVERNANCE

### 8.1 Topics gouvernance

| Topic | Source | Contenu |
|-------|--------|---------|
| `L1-INFRA/*/wal_entry` | NEXUS | Entrées WAL (hash-chain) |
| `L0-CANON/*/adr_update` | GOVERNANCE-HUB | Création/modification ADR |
| `L0-CANON/*/intent_update` | GOVERNANCE-HUB | Création/modification INTENT |
| `L0-CANON/*/poop_cycle` | POOP | Cycles @day/@twilight/@night |

### 8.2 Edges gouvernance dans KG-L

```
ADR ──[governed_by]──► ACTION
INTENT ──[governed_by]──► ACTION
WAL_ENTRY ──[traces]──► ACTION
POOP_CYCLE ──[regulates]──► DRIFT
```

---

## 9. PRODUCTION

### 9.1 CrewAI Agents

| Agent | Topics consommés | Topics produits |
|-------|------------------|-----------------|
| **DevTools Agent** | `L4-TOOLS/*/action`<br>`L4-TOOLS/*/friction` | `L4-TOOLS/*/action`<br>`L4-TOOLS/*/propagation` |
| **BRAIN Agent** | `L4-TOOLS/*/drift`<br>`L3-CITIZENS/*/llux_inference` | `L4-TOOLS/*/action`<br>`L4-TOOLS/*/governance` |
| **CTULU Agent** | `L4-TOOLS/*/friction`<br>`L4-TOOLS/*/urn_validate` | `L4-TOOLS/*/action`<br>`L4-TOOLS/*/propagation` |

### 9.2 Monitoring

| Métrique | Source | Topic WAZAA | KG-L Node |
|----------|--------|-------------|-----------|
| Bus latency | WAZAA | `L4-TOOLS/*/health` | `kind=METRIC`, `type=LATENCY` |
| Event throughput | WAZAA | `L4-TOOLS/*/health` | `kind=METRIC`, `type=THROUGHPUT` |
| Queue depth | WAZAA | `L4-TOOLS/*/health` | `kind=METRIC`, `type=QUEUE_DEPTH` |
| φ-CPS drift | NEXUS | `L1-INFRA/*/nexus_command` | `kind=DRIFT`, `score=φ` |

---

## 10. CANAUX DE COMMUNICATION STRUCTURÉS

### 10.1 Modèle de publication/abonnement

```
WAZAA Bus = message broker central
  ├── Publishers : TRIX, KORX, LLUX, FLEX, NEXUS, SABRE, OUROBOROS, CrewAI
  ├── Subscribers : KG-L, NEXUS, CrewAI, Grafana, TALEX/HOLMES
  └── Topics : hiérarchie strate/repo/event
```

### 10.2 Garanties

| Propriété | Mécanisme |
|-----------|-----------|
| **At-least-once** | PersistentEventStore (SQLite + JSONL) |
| **Ordering** | Timestamp + WAL trace dans WazaaMessage |
| **Idempotence** | `id` UUID + `intent_hash` |
| **Backpressure** | `max_queue_size` dans InProcessBackend |
| **Audit** | AuditChain hash-chain sur tous les événements |

### 10.3 Formats

| Format | Usage | Exemple |
|--------|-------|---------|
| **WazaaMessage** | Bus temps réel | `{topic, msg_type, source, target, payload, intent_hash}` |
| **KG-L JSON** | Graphe persistant | `{nodes: [...], edges: [...]}` |
| **WAL entry** | Audit | `{entity, state, intent_hash, timestamp}` |
| **FLEX metrics** | Hardware | `{numa_node, cache_hit_rate, thermal_state}` |

---

## 11. DÉPLOIEMENT PAR ENVIRONNEMENT

### 11.1 ENV2 (Production)

```
HP Z600
├── TRIX (WSL1 runtime)
├── KORX (state machine)
├── LLUX (GGML inference)
├── FLEX (NUMA/cache/thermal)
├── WAZAA (bus central)
│   ├── WazaaBusCore (in-process)
│   ├── PersistentEventStore (SQLite)
│   ├── KG-L (optionnel, SQLite backend)
│   └── AuditChain
├── NEXUS (KIVA-CLI)
├── CrewAI Agents
└── Grafana (monitoring)
```

**Configuration** : `WAZAA_KG_L_ENABLED=1` pour activer KG-L

### 11.2 DEV (Développement)

```
Même architecture mais :
├── WAZAA avec backend in-process seulement
├── KG-L avec backend JSON/YAML (pas SQLite)
├── Pas de FLEX (métadonnées mockées)
└── Tests unitaires only
```

### 11.3 CI/CD

```
Pipeline KIVA-CLI
├── Build TRIX/KORX/LLUX
├── Tests WAZAA (bus + bridge)
├── Tests KG-L (adapter + queries)
└── Validation FLEX (config NUMA)
```

---

## 12. SÉCURITÉ

### 12.1 Isolation des canaux

| Canal | Isolation | Raison |
|-------|-----------|--------|
| `L0-CANON/*` | Read-only pour L4+ | ADRs/INTENTs ne doivent pas être modifiés par des tools |
| `L1-INFRA/*` | CLI only | NEXUS est le seul writer autorisé |
| `L4-TOOLS/*` | Read-write | Bus principal |
| `L3-CITIZENS/*` | Read-write | Agents peuvent publier |

### 12.2 Authentification

- **NIP-42/NIP-98** : déjà implémenté dans WAZAA (`Nip42Auth`/`Nip98Auth`)
- **IntentHash** : chaque événement WAZAA doit avoir un `intent_hash` valide
- **WAL trace** : chaque événement KG-L est tracé dans l’AuditChain

---

## 13. MONITORING ET OBSERVABILITÉ

### 13.1 Métriques WAZAA

| Métrique | Source | Alerte |
|----------|--------|--------|
| Queue depth | `WazaaBusCore._stats` | > 1000 messages |
| Error rate | `WazaaBusCore._stats["errors"]` | > 1% |
| Latency P95 | EventServer | > 50ms |
| KG-L conversion rate | `WazaaKGSubscriber` | < 95% |

### 13.2 Métriques KG-L

| Métrique | Source | Alerte |
|----------|--------|--------|
| Node count | `KG-Runtime` | Croissance anormale |
| Edge count | `KG-Runtime` | Croissance anormale |
| Query latency | `kg_l_query.py` | > 100ms |
| Storage size | SQLite/JSONL | > 1 Go |

### 13.3 Métriques FLEX

| Métrique | Source | Alerte |
|----------|--------|--------|
| Thermal state | `FLEX/MODULE-04` | > 80°C |
| NUMA imbalance | `FLEX/MODULE-01` | Cross-NUMA traffic > 30% |
| Cache hit rate | `FLEX/MODULE-03` | L1 < 85% |

---

## 14. ÉVOLUTIVITÉ

### 14.1 Scaling horizontal

```
Multi-instance WAZAA (futur)
├── Instance 1 : L4-TOOLS (CTULU, TRIX, KORX)
├── Instance 2 : L3-CITIZENS (LLUX, CrewAI)
├── Instance 3 : L1-INFRA (NEXUS)
└── Shared : KG-L (SQLite centralisé ou PostgreSQL)
```

### 14.2 Scaling vertical

- **Topics** : ajout de nouveaux topics sans breaking change
- **KG-L backends** : JSON → YAML → SQLite → PostgreSQL
- **FLEX modules** : ajout de MODULE-05, MODULE-06, etc.

---

## 15. PLAN D’IMPLÉMENTATION

### Phase 0 — Fondations (P0)

| # | Action | Composant | Dépendance |
|---|--------|-----------|------------|
| 1 | Valider ce PRD MOC | KG-WAZAA | Équipe WAZAA + KG-L + NEXUS |
| 2 | Créer `KG-L/src/runtime/kg_l_wazaa_adapter.py` | KG-L | kg_l.py existant |
| 3 | Créer `WAZAA/src/bus/wazaa_kg_subscriber.py` | WAZAA | WazaaBusCore existant |
| 4 | Créer `WAZAA/config/wazaa_kg_config.yaml` | WAZAA | - |
| 5 | Tests unitaires adapter + subscriber | KG-L + WAZAA | pytest |

### Phase 1 — Intégration couches (P1)

| # | Action | Composant | Dépendance |
|---|--------|-----------|------------|
| 1 | Intégrer FLEX → WAZAA topics | FLEX + WAZAA | Phase 0 |
| 2 | Intégrer TRIX → WAZAA topics | TRIX + WAZAA | Phase 0 |
| 3 | Intégrer KORX → WAZAA topics | KORX + WAZAA | Phase 0 |
| 4 | Intégrer LLUX → WAZAA topics | LLUX + WAZAA | Phase 0 |
| 5 | Intégrer NEXUS → WAZAA topics | NEXUS + WAZAA | Phase 0 |

### Phase 2 — KGs par environnement (P2)

| # | Action | Composant | Dépendance |
|---|--------|-----------|------------|
| 1 | Créer KG-ENV2 (hardware + runtime) | KG-L + FLEX | Phase 1 |
| 2 | Créer KG-DEV (workflows + tests) | KG-L + WAZAA | Phase 1 |
| 3 | Créer KG-PROD (incidents + déploiements) | KG-L + WAZAA | Phase 1 |
| 4 | Créer KG-GOV (ADRs + INTENTs + WAL) | KG-L + GOVERNANCE-HUB | Phase 1 |

### Phase 3 — Production (P3)

| # | Action | Composant | Dépendance |
|---|--------|-----------|------------|
| 1 | Monitoring Grafana (métriques WAZAA + KG-L + FLEX) | Grafana | Phase 2 |
| 2 | CrewAI Agents intégrés au bus | CrewAI + WAZAA | Phase 1 |
| 3 | TALEX/HOLMES narration depuis KG-L | TALEX + KG-L | Phase 2 |
| 4 | Dashboard KG-WAZAA unifié | GeriCode + WAZAA | Phase 2 |

---

## 16. RISQUES ET MITIGATION

| Risque | Impact | Mitigation |
|--------|--------|------------|
| **Complexité** | Trop de couches à intégrer | Approche incrémentale (Phase 0 → 3) |
| **Performance** | Latence bus événementiel | KG-L optionnel, filtres stricts |
| **Dépendances circulaires** | FLEX → WAZAA → FLEX | FLEX ne dépend pas de WAZAA ; adapter unidirectionnel |
| **Bruit KG** | Trop de nœuds KG-L | Filtres par environnement + seuils |
| **Sécurité** | Fuite d’événements sensibles | Isolation par strate + authentification NIP-42 |

---

## 17. CRITÈRES DE SUCCÈS

| Critère | Cible | Mesure |
|---------|-------|--------|
| **Couverture événementielle** | 100% des événements WAZAA filtrables | Count topics WAZAA |
| **KG-L conversion rate** | > 95% (hors HEALTH/CUSTOM) | Count KG-L nodes / Count WAZAA events |
| **Latence bus** | < 5ms par événement | Benchmark WAZAA |
| **KG-L query latency** | < 100ms | Benchmark kg_l_query.py |
| **FLEX integration** | 100% des métriques matérielles disponibles | Count FLEX topics |
| **Tests passants** | 100% | pytest |
| **Documentation** | 100% des composants documentés | Docs coverage |

---

## 18. DÉCISION

**Proposition** : Valider ce PRD MOC et engager la Phase 0.

**Alternative** : Rester sur WAZAA seul sans KG-L ni intégration multi-couches.

**Décideurs** : Équipe WAZAA + Équipe KG-L + NEXUS (KIVA-CLI) + FLEX + GeriCode

---

## 19. RÉFÉRENCES

| Document | Repo | Path |
|----------|------|------|
| KG-L runtime | KG-L | `src/runtime/kg_l.py` |
| KG-L langage (EdgeKind) | KG-L | `src/runtime/edge_kind_registry.py` |
| KG-L query engine | KG-L | `src/query/kg_l_query.py` |
| KG-L adapters existants | KG-L | `src/runtime/kg_l_trix_adapter.py`, `kg_l_worktree_adapter.py` |
| WAZAA bus core | WAZAA | `src/bus/wazaabus.py` |
| WAZAA message schema | WAZAA | `src/bus/message.py` |
| WAZAA advanced subscription | WAZAA | `src/bus/advanced_subscription.py` |
| WAZAA ARCHITECTURE.md | WAZAA | `docs/ARCHITECTURE.md` |
| KG-WAZAA architecture | WAZAA | `docs/KG-WAZAA-ARCHITECTURE.md` |
| PRD MOC BUZZ-X v3.0 | BUZZ-X | `PRD-MOC/PRD-MOC-BUZZ-X-BUS-2026-08-18.md` |
| PRD MOC KG-L ↔ WAZAA Bridge | BUZZ-X | `PRD-MOC/PRD-MOC-KG-L-WAZAA-BRIDGE-2026-08-18.md` |
| KORX README | KORX | `README.md` |
| LLUX README | LLUX | `README.md` |
| TRIX README | TRIX | `README.md` |
| NEXUS README | NEXUS | `README.md` |
| FLEX README | FLEX | `README.md` |
| FLEX REPO.yaml | FLEX | `REPO.yaml` |
| CTULU SABRE engine | CTULU | `tools/sabre-anything/sabre_engine.py` |
| CTULU OUROBOROS factory | CTULU | `tools/oourobouros/factory.py` |
| CTULU OUROBOROS ADR | CTULU | `ADR/ADR-2026-07-05-002-dcg-ourobouros-bridge.md` |
| GeriCode architecture | GeriCode | `docs/architecture.md` |
| GeriCode KG-L runtime | GeriCode | `.kilo/skills/kg-l-runtime/runtime/kg_l.py` |

---

*Document généré le 2026-08-18 — Audit direct du code source. Pas de LLM externe.*
