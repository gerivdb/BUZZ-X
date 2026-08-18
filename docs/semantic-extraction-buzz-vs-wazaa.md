# Extraction sémantique Buzz@block vs WAZAA

## 1. Sémantique Buzz@block (extraite du code)

### 1.1 Architecture générale

Buzz@block est un **relay Nostr** (NIP-01) avec extensions communautaires.

```
Clients (humains + agents)
        │
        ▼ WebSocket + HTTP
┌─────────────────────────────────────┐
│         buzz-relay (Axum)          │
│  ┌─────────────────────────────┐   │
│  │   Protocol handlers        │   │
│  │  NIP-42 auth, EVENT, REQ   │   │
│  │  HTTP bridge /events       │   │
│  │  Media (Blossom/S3)        │   │
│  │  Git (smart HTTP)          │   │
│  │  NIP-05, health, admin     │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │   SubscriptionRegistry     │   │
│  │   DashMap: (channel, kind) │   │
│  │   → conns                  │   │
│  └─────────────────────────────┘   │
└──────────┬────────────┬────────────┘
           │            │
     ┌─────▼──────┐ ┌──▼──────────┐
     │  Postgres  │ │   Redis     │
     │  events,   │ │  presence,  │
     │  channels, │ │  typing,    │
     │  tokens,   │ │  pub/sub    │
     │  workflows │ │             │
     └────────────┘ └─────────────┘
```

### 1.2 Fonctionnalités par crate

| Crate | Rôle | Fonctionnalités clés |
|-------|------|---------------------|
| **buzz-core** | Types, vérification, matching | Event verification, filter matching, kind registry, NIP-01/NIP-29 types |
| **buzz-db** | Stockage Postgres | Events, channels, tokens, workflows, audit trail, migrations |
| **buzz-pubsub** | Pub/Sub Redis | Fan-out events, presence (SETEX), typing (ZADD), pub/sub |
| **buzz-auth** | Authentification | NIP-42 auth, NIP-98 API tokens, scopes, rate limiting |
| **buzz-search** | Recherche full-text | Postgres FTS (search_tsv + GIN), scoped by community |
| **buzz-audit** | Audit hash-chain | Tamper-evident log, hash chain |
| **buzz-workflow** | Workflow engine | YAML-as-code, triggers (message_posted, reaction_added, webhook), sequential executor, template resolution |
| **buzz-acp** | Agent harness | ACP/JSON-RPC over stdio, MCP server config, session management, observer, pool lifecycle |
| **buzz-agent** | Agent minimal | ACP-compliant agent, non-streaming, tool-calls-as-output |
| **buzz-media** | Stockage média | Blossom/S3 media, validation, thumbnails |
| **buzz-relay** | Serveur WebSocket | Axum router, WebSocket handler, HTTP bridge (/events, /query, /count), health probes, metrics |
| **buzz-relay-mesh** | Mesh inter-relay | QUIC transport, membership, fenced wire contract |
| **buzz-sdk** | SDK événements | Typed Nostr event builders |
| **buzz-cli** | CLI agent-first | CLI pour interagir avec le relay |
| **buzz-admin** | Admin CLI | Operator CLI: membership, key generation |
| **buzz-push-gateway** | Push notifications | NIP-PL gateway, capability-gated |
| **buzz-persona** | Personas | Parser/loader .persona.md |
| **buzz-conformance** | Conformance | Runtime trace schema + replay checker |
| **buzz-test-client** | Tests | Integration test harness |
| **buzz-ws-client** | WebSocket client | YAML-as-code workflow engine |
| **git-credential-nostr** | Git credentials | NIP-98 auth headers for git |
| **git-sign-nostr** | Git signing | NIP-GS commit/tag signing |
| **sprig** | All-in-one | ACP harness + agent + developer MCP |
| **buzz-dev-mcp** | MCP dev | Postgres event store (doublon?) |
| **buzz-pair-relay** | Pairing | Ephemeral sidecar relay for NIP-AB |
| **buzz-pairing-cli** | Pairing CLI | NIP-AB device pairing testing |

### 1.3 Fonctionnalités protocolaires

| Feature | Protocol | Description |
|---------|----------|-------------|
| Auth | NIP-42 | Challenge-response auth |
| HTTP auth | NIP-98 | Bearer token auth for HTTP endpoints |
| Events | NIP-01 | Signed Nostr events (kind, tags, content) |
| Subscriptions | NIP-01 | REQ/CLOSE filters |
| Communities | Propriétaire | Multi-tenant, host-derived community |
| Media | Blossom | Upload/download media blobs |
| Git | Propriétaire | Smart HTTP git transport |
| NIP-05 | NIP-05 | DNS-based pubkey resolution |
| Search | Propriétaire | Full-text search over events |
| Workflow | Propriétaire | YAML-as-code automation |
| ACP | ACP/JSON-RPC | Agent harness for AI subprocesses |
| Push | NIP-PL | Push notifications gateway |
| Pairing | NIP-AB | Device pairing handshakes |
| Mesh | Propriétaire | Inter-relay QUIC mesh |

### 1.4 Extensions N243 (BUZZ-X patches)

| Kind | Nom | Usage |
|------|-----|-------|
| 40050 | RUNNER_STATUS | État d'un runner L* |
| 40051 | RUNNER_INVOCATION | Invocation d'un runner |
| 40052 | TERNARY_DECISION | Décision ternaire |
| 40053 | TERNARY_WAL | Entrée WAL ternaire |
| 40054 | PERSONA_VERSE | Persona-Verse invoqué |
| 40055 | VFT_LEVEL | Niveau VFT (fractal) |
| 40056 | BDCP_ENFORCEMENT | Événement BDCP |
| 40057 | COMMUNITY_STRATUM | Strate L* d'une community |

## 2. Sémantique WAZAA (extraite du code)

### 2.1 Architecture générale

WAZAA est un **système d'orchestration multi-agents** avec bus interne.

```
Agents (crewai, evolution engines)
        │
        ▼ publish/subscribe
┌─────────────────────────────────────┐
│         WazaaBusCore               │
│  InProcessBackend (asyncio.Queue)  │
│  ou DaemonBackend (TCP/WebSocket) │
└──────────┬────────────┬────────────┘
           │            │
     ┌─────▼──────┐ ┌──▼────────────┐
     │ BusMemory  │ │ EventServer   │
     │  Bridge    │ │ (WebSocket    │
     │ (remember) │ │  port 8765)   │
     └────────────┘ └──────────────┘
           │
     ┌─────▼──────┐
     │ GitsemBus  │
     │ (git sém.) │
     └────────────┘
```

### 2.2 Fonctionnalités par module

| Module | Rôle | Fonctionnalités clés |
|--------|------|---------------------|
| **WazaaBusCore** | Bus async pub/sub | subscribe, publish, unsubscribe, wildcard topics, asyncio backend |
| **WazaaMessage** | Message format | topic, msg_type, source, target, payload, intent_hash |
| **MessageType** | Types de messages | FRICTION, ACTION, DRIFT, GUARD, URN_VALIDATE, PROPAGATION, HEALTH, CUSTOM |
| **StrateLevel** | Niveaux de strate | L0 à L5 |
| **BusMemoryBridge** | Mémoire événementielle | remember, predict_friction, event_log, friction_history |
| **EventServer** | WebSocket server | Real-time events push, port 8765 |
| **GitsemBus** | Bus sémantique git | Git commit semantic events |
| **BuzzRelayClient** | Client Buzz relay | WebSocket client vers Buzz@block, subscription/publishing |
| **AcpClient** | ACP client | Invoke Zig runners, JSON-RPC over stdio |
| **WorkflowEngine** | Workflow | Nostr events → WAZAA actions |
| **TernaryWalClient** | Audit WAL | Hash-chain tamper-evident log |

## 3. Mapping comparatif Buzz@block vs WAZAA

| Fonctionnalité | Buzz@block | WAZAA | Écart |
|---------------|------------|-------|-------|
| **Bus pub/sub** | Redis pub/sub | WazaaBusCore (asyncio) | WAZAA: in-process seulement |
| **Event store** | Postgres (events, channels, tokens, workflows) | BusMemoryBridge (in-memory list) | WAZAA: pas de persistance disque |
| **Full-text search** | Postgres FTS (GIN) | ❌ Absent | GAP |
| **Authentication** | NIP-42 + NIP-98 + API tokens | ❌ Absent | GAP |
| **Multi-tenant** | Communities (host-derived) | ❌ Absent | GAP |
| **Workflow engine** | YAML-as-code, triggers, executor | WorkflowEngine (basique) | WAZAA: limité |
| **Agent harness** | ACP/JSON-RPC over stdio | AcpClient (Zig runners) | Partiel |
| **Media storage** | Blossom/S3 | ❌ Absent | GAP |
| **Git integration** | Smart HTTP, NIP-GS signing | GitsemBus (sémantique) | Partiel |
| **Audit log** | Hash-chain (buzz-audit) | TernaryWalClient | Similaire |
| **Push notifications** | NIP-PL gateway | ❌ Absent | GAP |
| **Device pairing** | NIP-AB | ❌ Absent | GAP |
| **Relay mesh** | QUIC inter-relay | ❌ Absent | GAP |
| **NIP-05** | DNS-based pubkey | ❌ Absent | GAP |
| **Presence/Typing** | Redis SETEX/ZADD | ❌ Absent | GAP |
| **WebSocket server** | Axum (buzz-relay) | EventServer (port 8765) | WAZAA: limité |
| **CLI** | buzz-cli, buzz-admin | ❌ Absent | GAP |
| **SDK** | buzz-sdk (event builders) | ❌ Absent | GAP |
| **Conformance** | Runtime trace + replay | ❌ Absent | GAP |
| **Metrics** | Prometheus, OpenTelemetry | ❌ Absent | GAP |
| **Kinds N243** | 40050-40057 | ✅ Mapping dans overlay (supprimé) | WAZAA: conceptuellement prêt |

## 4. ARGUS diff — Fonctions à déduire pour WAZAA

### 4.1 Gaps critiques (bloquants pour l'écosystème)

| # | Fonctionnalité manquante | Priorité | Pourquoi WAZAA en a besoin |
|---|-------------------------|----------|---------------------------|
| 1 | **Persistance événementielle** (disk) | P0 | BusMemoryBridge est in-memory seulement. Perte au restart. |
| 2 | **Full-text search** | P1 | Recherche dans l'historique des events agents. |
| 3 | **Multi-topic wildcard avancé** | P1 | WazaaBusCore a `*/*/*` mais pas de filtres complexes. |
| 4 | **Workflow engine YAML** | P1 | Automatisation des séquences agents. |
| 5 | **NIP-42 auth + NIP-98** | P2 | Authentification des agents et humains. |

### 4.2 Gaps importants (amélioration qualité)

| # | Fonctionnalité manquante | Priorité | Pourquoi WAZAA en a besoin |
|---|-------------------------|----------|---------------------------|
| 6 | **Metrics & observabilité** | P2 | Monitoring du bus, debug, performance. |
| 7 | **Audit hash-chain** | P2 | Traçabilité des actions agents. |
| 8 | **Media storage** | P3 | Partage de fichiers entre agents. |
| 9 | **Push notifications** | P3 | Alertes temps réel. |
| 10 | **Device pairing** | P3 | Pairing NIP-AB pour devices. |

### 4.3 Gaps optionnels (nice-to-have)

| # | Fonctionnalité manquante | Priorité | Pourquoi WAZAA en a besoin |
|---|-------------------------|----------|---------------------------|
| 11 | **Relay mesh QUIC** | P4 | Interconnecter plusieurs WAZAA. |
| 12 | **NIP-05 resolution** | P4 | Identité décentralisée. |
| 13 | **Presence/Typing indicators** | P4 | UX temps réel. |
| 14 | **SDK event builders** | P4 | Developer experience. |
| 15 | **Conformance testing** | P4 | Qualité protocolaire. |

## 5. Mapping sémantique détaillé

### 5.1 Équivalences fonctionnelles

| Buzz@block | WAZAA | Mapping |
|-----------|-------|---------|
| `buzz-core` (types, verification) | `WazaaMessage`, `MessageType` | WAZAA: types propres, pas Nostr natif |
| `buzz-db` (Postgres) | `BusMemoryBridge` (in-memory) | WAZAA: limité, pas de SQL |
| `buzz-pubsub` (Redis) | `WazaaBusCore` (asyncio) | WAZAA: in-process, pas de fan-out multi-process |
| `buzz-auth` (NIP-42/NIP-98) | ❌ Absent | WAZAA: aucune auth |
| `buzz-search` (FTS) | ❌ Absent | WAZAA: aucune recherche |
| `buzz-workflow` (YAML) | `WorkflowEngine` | WAZAA: basique vs YAML-as-code |
| `buzz-acp` (ACP/JSON-RPC) | `AcpClient` | WAZAA: Zig runners seulement |
| `buzz-audit` (hash-chain) | `TernaryWalClient` | Similaire |
| `buzz-media` (Blossom) | ❌ Absent | WAZAA: pas de média |
| `buzz-relay` (Axum server) | `EventServer` | WAZAA: limité, pas de REST API |
| `buzz-cli` | ❌ Absent | WAZAA: pas de CLI dédiée |
| `buzz-sdk` | ❌ Absent | WAZAA: pas de SDK |

### 5.2 Fonctionnalités Buzz@block sans équivalent WAZAA

1. **Postgres event store** — WAZAA n'a pas de persistance structurée
2. **Redis pub/sub** — WAZAA n'a pas de fan-out multi-process
3. **NIP-42/NIP-98 auth** — WAZAA n'a pas d'authentification
4. **Full-text search** — WAZAA n'a pas de recherche
5. **YAML-as-code workflows** — WAZAA a un moteur basique
6. **Blossom media storage** — WAZAA n'a pas de gestion média
7. **NIP-PL push gateway** — WAZAA n'a pas de push
8. **NIP-AB pairing** — WAZAA n'a pas de pairing
9. **Inter-relay mesh** — WAZAA n'a pas de mesh
10. **NIP-05 resolution** — WAZAA n'a pas d'identité DNS
11. **Prometheus metrics** — WAZAA n'a pas d'observabilité
12. **CLI dédiée** — WAZAA n'a pas de CLI agent-first

### 5.3 Fonctionnalités WAZAA sans équivalent Buzz@block

1. **BusMemoryBridge** — mémoire événementielle + prédiction friction (spécifique WAZAA)
2. **GitsemBus** — bus sémantique git (spécifique WAZAA)
3. **StrateLevel** — niveaux de strate L0-L5 (spécifique WAZAA)
4. **DaemonBackend** — TCP/WebSocket backend (en dev)

## 6. Conclusion

### 6.1 Buzz@block apporte-t-il quelque chose à WAZAA ?

**Oui, mais seulement si Postgres+Redis sont disponibles.**

| Apport Buzz@block | Utilité pour WAZAA |
|-------------------|---------------------|
| Persistance structurée (Postgres) | ✅ Critique — WAZAA perd tout au restart |
| Fan-out multi-process (Redis) | ✅ Important — WAZAA est single-process |
| Auth (NIP-42/NIP-98) | ✅ Important — sécurité agents |
| FTS search | ✅ Utile — recherche historique |
| Workflow YAML | ✅ Amélioration — WAZAA a basique |
| Media storage | ⚠️ Optionnel |
| Push gateway | ⚠️ Optionnel |
| Mesh, pairing, NIP-05 | ❌ Non critiques pour WAZAA |

### 6.2 Peut-on réimplémenter ces fonctionnalités dans WAZAA sans Buzz@block ?

**Partiellement.**

| Fonctionnalité | Réimplémentation WAZAA | Effort |
|---------------|------------------------|--------|
| Persistance événementielle | JSONL + SQLite | Moyen |
| Fan-out multi-process | Redis embarqué ou multiprocessing | Moyen |
| Auth | Implémenter NIP-42/NIP-98 | Élevé |
| FTS search | SQLite FTS5 | Faible |
| Workflow YAML | Améliorer WorkflowEngine | Moyen |
| Media storage | MinIO ou filesystem | Faible |
| Push gateway | WebSocket push | Faible |
| Mesh, pairing | NIP-AB, QUIC | Élevé |

### 6.3 Recommandation

**Option A : Attendre l'infra (Docker/Postgres/Redis)**
- Avantages : Buzz@block fonctionne tel quel
- Inconvénients : Dépend de matériel/OS non disponible sur ENV2

**Option B : Réimplémenter dans WAZAA**
- Avantages : Autonome, pas de dépendance externe
- Inconvénients : Effort de dev, maintenance

**Option C : Mode hybride**
- WAZAA garde son bus in-process
- Ajoute SQLite pour persistance
- Ajoute FTS pour recherche
- Garde Buzz@block comme "option serveur" quand infra dispo

**Recommandation : Option C** — WAZAA devient autonome avec persistance minimale (SQLite), et Buzz@block reste une option serveur pour quand l'infra sera disponible.
