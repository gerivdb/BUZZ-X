---
type: "PRD_MOC"
version: "1.2.0"
date: "2026-08-17"
status: "PROPOSED"
intent_hash: "0xBUZZ_BUS_OPERATIONALIZATION_20260817"
inherits: ["moc-governance"]
mox_gates:
  - P-108
  - P-109
---

# PRD MOC - BUZZ-X - Operationnalisation du Bus Buzz (v1.1 - TRIX/KIX)

## 1. RESUME EXECUTIF

Ce PRD MOC couvre la mise en oeuvre operationnelle du **bus Buzz** tel qu'heberge dans `BUZZ-X` / `Buzz@block` :
- **Relay Rust** (`buzz-relay` Axum) : source de verite unique
- **Stockage** : Postgres (events, channels, tokens, workflows, audit, search) + Redis (presence, typing, pub/sub)
- **Protocole** : Nostr NIP-01/NIP-29/NIP-42/NIP-98/NIP-50/NIP-10/NIP-17
- **Integrations cibles** : TALEX (`BuzzEventReader`), GeriCode, BUZZ-X overlay, KIX, NEXUS, KIVA, ONTOLOGY, GOVERNANCE-HUB, **TRIX**

**Nouveaute v1.1** :prise en compte explicite de **TRIX** (runtime N+4, Git Arbiter, pattern-router) et **KIX** (orchestrateur cycle de vie runners RLM) comme gouvernants du bus Buzz, pas seulement comme consommateurs.

**Source** : `BUZZ-X/Buzz@block/ARCHITECTURE.md`, `schema/schema.sql`, `NOSTR.md`, `design.yaml`
**IntentHash** : `0xBUZZ_BUS_OPERATIONALIZATION_20260817`
**Statut** : Genere le 2026-08-17

---

## 2. CONTEXTE ET PERIMETRE

### 2.1 Contexte

`BUZZ-X` est le repo hote qui integre **Buzz@block** comme bus de communication du systeme gerivdb. Buzz@block est un relay Nostr Rust qui constitue le **canal unifie** entre :
- les runners cognitifs (LLUX, TIMX, TLM-LANG, ROOTX, RLM-243)
- l'Agent Manager V9.10
- KiloCode / Kilo
- les humains via clients Nostr
- **TRIX** (runtime d'execution N+4) - gouverne l'execution et valide les commits via Git Arbiter
- **KIX** (orchestrateur cycle de vie N+2/N+3) - gere les runners RLM et leur health-check

TALEX dispose deja d'un `BuzzEventReader` capable de parser des events Buzz simules. Ce PRD MOC vise a **rendre le bus Buzz pleinement operationnel** pour alimenter TALEX et les autres consumers, y compris TRIX et KIX.

### 2.2 Perimetre

| Strate | Composants | Impact |
|--------|------------|--------|
| L4-TOOLS | BUZZ-X (`Buzz@block` relay, overlay GeriCode) | Extension majeure du bus |
| L4-TOOLS | TALEX (`BuzzEventReader`, `ConversationNarrator`) | Consumer operationnel |
| L4-TOOLS | **TRIX** (runtime N+4, dispatch table 243, Git Arbiter, pattern-router) | **Gouvernant execution + validation commits** |
| L2-PLATFORM | GeriCode (callbacks Agent Manager) | Integration callbacks |
| L2-PLATFORM | **KIX** (orchestrateur cycle de vie runners RLM) | **Point d'integration cognitif + health-check** |
| L3-CITIZENS | NEXUS (WAL sessions) | Tracabilite sessions |
| L1-INFRA | KIVA (runtime logs) | Execution effective |
| L0-CANON | GOVERNANCE-HUB (SOT, ADR) | Conformite governance |
| L0-CANON | ONTOLOGY (concepts YAML) | Cadre semantique |

---

## 3. ARCHITECTURE CIBLE

### 3.1 Composants principaux

```
+---------------------------------------------------------------------+
|                           CLIENTS                                    |
|  Human (Nostr app, web, mobile)    Agent (buzz-cli, TALEX, KIX)     |
+---------------------------------------------------------------------+
                                |
                                v
+---------------------------------------------------------------------+
|                         buzz-relay (Axum)                          |
|  NIP-42 auth | EVENT pipeline | REQ handler | HTTP bridge           |
|  SubscriptionRegistry | Fan-out | Workflow engine                   |
+----------+--------------+------------------------------------------+
            |              |
      +-----v------+  +----v------+
      |  Postgres  |  |   Redis   |
      |  events,   |  | presence, |
      |  channels, |  | typing,   |
      |  tokens,   |  | pub/sub   |
      |  workflows |  +-----------+
      |  audit     |
      |  arbiter_locks (TRIX) |
      +------------+
            |
            v
+---------------------------------------------------------------------+
|  TRIX (N+4) - Runtime execution + Gouvernance                      |
|  - Dispatch table 243 (3^5)                                         |
|  - Git Arbiter (port 8742) - validation commits                     |
|  - Pattern-router (ADR-2026-06-28-001)                              |
|  - ADR gate + governance                                            |
+---------------------------------------------------------------------+
            ^
            |
+---------------------------------------------------------------------+
|  KIX (N+2/N+3) - Orchestrateur cycle de vie runners RLM            |
|  - Health-check runners (ports 8786-8799)                           |
|  - Start/stop runners via REQ Nostr vers buzz-relay                 |
|  - Heartbeat presence (kind 20001)                                  |
+---------------------------------------------------------------------+
```

### 3.2 Kinds Buzz operationnels

| Kind | Libelle | Statut | Usage TALEX | Usage TRIX/KIX |
|------|---------|--------|-------------|----------------|
| 0 | Profile | [OK] | metadonnee agent | identite runner (TRIX) |
| 5 | Deletion | [OK] | audit suppression | audit suppression (TRIX arbiter) |
| 7 | Reaction | [OK] | metrique engagement | feedback execution (TRIX) |
| 9 | Message | [OK] | evenement principal | log execution, session events |
| 20001 | Presence | [OK] | sante runners | **heartbeat KIX** (health-check runners) |
| 20002 | Typing | [OK] | activite temps reel | activite runner (KIX) |
| 40002 | Rich content | [WARN] | contenu structure | contenu structure (TALEX+TRIX) |
| 9000 | Add user | [OK] | gestion canaux | ajout runner au canal (KIX) |
| 9001 | Remove user | [OK] | gestion canaux | suppression runner (KIX) |
| 9002 | Edit group | [OK] | metadonnees | mise a jour metadata runner (KIX) |
| 9005 | Admin delete | [OK] | moderation | moderation (TRIX governance) |
| 9007 | Group creation | [OK] | creation workspace | creation session runner (KIX) |
| 9008 | Group deletion | [OK] | suppression workspace | suppression session runner (KIX) |
| 9009 | Create invite | [WARN] | invitation | invitation runner (KIX) |
| 9021 | Join request | [OK] | demande adhesion | demande adhesion runner (KIX) |
| 9022 | Leave group | [OK] | depart membre | depart runner (KIX) |
| 1059 | DM gift wrap | [OK] | messagerie privee | communication privee TRIX/KIX |
| 39000 | Group metadata | [OK] | discovery | metadata runners (KIX discovery) |
| 39001 | Group admins | [OK] | discovery | admins runners (KIX) |
| 39002 | Group members | [OK] | discovery | membres runners (KIX) |
| 44100 | Membership added | [OK] | notification | notification adhesion runner (KIX) |
| 44101 | Membership removed | [OK] | notification | notification depart runner (KIX) |
| **TRIX-GOV-001** | **Governance event** | **PROPOSED** | **N/A** | **ADR validation, pattern-router decision** |
| **TRIX-ARB-001** | **Arbiter lock** | **PROPOSED** | **N/A** | **Git Arbiter lock acquisition/release** |
| **KIX-LC-001** | **Runner lifecycle** | **PROPOSED** | **N/A** | **Start/stop/heartbeat runners RLM** |

**Note** : Les kinds TRIX-GOV-001, TRIX-ARB-001 et KIX-LC-001 sont proposes pour couvrir les processus gouvernants TRIX et KIX. Ils necessitent une validation HITL et des ADR dedies.

### 3.3 Architecture TRIX/KIX - Bus Buzz

TRIX et KIX ne sont pas de simples consommateurs du bus Buzz. Ils en sont les **gouvernants** :

- **TRIX (N+4)** definit :
  - Quels runners s'executent (dispatch table 243)
  - Comment les commits sont valides (Git Arbiter port 8742)
  - Quelle ADR est acceptee (ADR gate)
  - Quel pattern est route (pattern-router)

- **KIX (N+2/N+3)** definit :
  - Quand les runners demarrent/arretent (lifecycle)
  - Quel runner est en bonne sante (health-check)
  - Quelle tache est assignee a quel runner (orchestration)

**Implication pour BUZZ-X** : le bus Buzz doit supporter des events de **gouvernance** (TRIX) et de **lifecycle** (KIX) en plus des events standards (messages, reactions, presence).

---

## 4. PLAN D'IMPLEMENTATION

### 4.1 Phases

| Phase | Actions | Duree | Dependances |
|-------|---------|-------|------------|
| **P0** | Infrastructure Buzz@block (Docker, migrations, Redis, Postgres) | [OK] Fait | - |
| **P1** | Relay Rust operationnel (NIP-42, EVENT, REQ, fan-out) | [OK] Fait | P0 |
| **P2** | kinds core (9, 7, 20001, 20002, 9000-9002, 39000-39002) | [OK] Fait | P1 |
| **P3** | Integration TALEX (`BuzzEventReader` local) | [OK] Fait | P2 |
| **P4** | Adapteur Postgres/Redis pour `BuzzEventReader` | [OK] Fait | P3 |
| **P5** | Integration runners cognitifs (LLUX, TIMX, TLM-LANG, ROOTX, RLM-243) | [OK] Implante | P4 |
| **P5.5** | **Integration TRIX + KIX (gouvernance + lifecycle)** | **[OK] Implante** | **P4, TRIX deploye, KIX deploye** |
| **P6** | CLI `x-forge analyze buzz` + health-check bus | [OK] Fait | P4 |
| **P7** | Rapport integre Agent Manager + Buzz | [OK] Fait | P6 |

**Total estime** : ~22 jours apres deploiement operationnel de Buzz@block (P0-P7 + P5.5).

### 4.2 Livrables

| Livrable | Format | Validation |
|----------|--------|------------|
| `buzz-relay` deploye (Docker Compose) | Rust / Docker | Tests integration passants |
| `schema/schema.sql` + migrations | SQL | `sqlx migrate run` OK |
| `src/talex/readers/buzz_events.py` adapteur Postgres/Redis | Python | Tests unitaires + integration |
| `src/talex/readers/buzz_store.py` (PostgresBuzzStore + RedisBuzzStore) | Python | Tests unitaires (8 tests) |
| `src/talex/cli.py` - `analyze buzz` / `analyze integrated` | Python | CLI fonctionnelle |
| `scripts/buzz_bus_health.py` | Python | Health-check local, 100% couverture 22 kinds core + 3 kinds proposes TRIX/KIX |
| `reports/buzz-conversation-integration.md` | Markdown | Revue HITL |
| `reports/agent-manager-buzz-integration.md` | Markdown | Revue HITL |
| `tests/test_buzz_kinds.py` | Python | 6 tests unitaires (mapping 25 kinds, ingest TRIX/KIX) |
| `tests/test_runners_p5.py` | Python | 7 tests unitaires (LLUX, TIMX, TLM-LANG, ROOTX, RLM-243, KIX, TRIX) |
| `docs/trix-kix-extension-schema.md` | Markdown | Schema SQL optionnel pour kinds proposes TRIX/KIX |
| **Kinds TRIX/KIX** : TRIX-GOV-001 (50001), TRIX-ARB-001 (50002), KIX-LC-001 (60001) | **Mapping TALEX + schema optionnel** | **Mapping TALEX valide (13 tests passent), schema documente, ADR propose** |
| **ADR-TRIX-GIT-ARBITER** | **ADR** | **Proposed (commit e7ddfd47, GOVERNANCE-HUB)** |
| **BUZZ-X/PRD-MOC/PRD-MOC-BUZZ-X-BUS-2026-08-17.md** | Markdown | Gouvernance validee (v1.2, TRIX/KIX ajoutes) |

---

## 5. TESTS ET VALIDATION

### 5.1 Tests prevus

| Type | Cible | Outil |
|------|-------|-------|
| Integration | `buzz-relay` + Postgres + Redis | `cargo test`, `buzz-test-client` |
| API | NIP-42, EVENT, REQ, HTTP bridge | `nak` CLI, pytest |
| Performance | Fan-out multi-connections | Load test local |
| TALEX | `BuzzEventReader` sur vraie DB | pytest + Postgres testcontainers |
| TALEX | `BuzzEventReader` mapping 25 kinds | pytest (19 tests passent, 0 regression) |
| TRIX | Git Arbiter + pattern-router + dispatch table | pytest + trixd |
| KIX | Health-check runners + lifecycle events | pytest + KIX REST API |
| E2E | CLI TALEX + bus Buzz reel + TRIX + KIX | Pipeline integration |

### 5.2 Metriques

| Metrique | Cible | Mesure |
|----------|-------|--------|
| Latence EVENT -> fan-out | < 50 ms p95 | `buzz-test-client` |
| Throughput REQ | > 1000 events/s | Load test |
| Couverture kinds Buzz | 25 kinds (22 core + 3 proposes TRIX/KIX) | Mapping TALEX + tests unitaires |
| Integration TALEX | 25/25 kinds reconnus | test_buzz_kinds.py (6 tests) |
| Disponibilite bus | 99.9% | Monitoring Redis/Postgres |
| TRIX Arbiter latency | < 100 ms | Git Arbiter /git/locks/status |
| KIX health-check coverage | 13/13 services | Nombre de services monitors / total |

---

## 6. DEPENDANCES

| Dependance | Type | Justification |
|------------|------|---------------|
| `buzz-relay` deploye | Repo / Infrastructure | Source des events Buzz pour TALEX |
| Postgres + Redis | Infrastructure | Stockage events, presence, pub/sub |
| `gerivdb/GOVERNANCE-HUB/known_repositories.yaml` v5.1 | SOT | Source de verite des repos actifs |
| ADR-2026-08-14-PIPELINE-ASCENDANT-KG | ADR | Architecture pipeline KG (commit 6da261f4) |
| ADR-2026-08-15-TALEX-CIR-ADAPTER-ARCHITECTURE | ADR | Architecture adaptateurs TALEX (commit 6da261f4) |
| **ADR-TRIX-GIT-ARBITER** | **ADR** | **Proposed (commit e7ddfd47, GOVERNANCE-HUB) - Git Arbiter port 8742** |
| **ADR-KIX-LIFECYCLE** | **ADR** | **Proposed (commit ADR-2026-07-27-016) - Orchestrateur cycle de vie runners** |
| ONTOLOGY concepts YAML | Ontologie | Cadre semantique pour les narratifs |
| `nak` CLI | Outil | Tests NIP-01/NIP-29 |
| **TRIX** (`D:\DO\WEB\TOOLS\L4-TOOLS\TRIX`) | **Repo** | **Runtime N+4, dispatch table 243, Git Arbiter - deploye localement** |
| **KIX** (`D:\DO\WEB\TOOLS\L2-PLATFORM\KIX`) | **Repo** | **Orchestrateur cycle de vie runners RLM - deploye localement** |
| **GeriCode** (`D:\DO\WEB\TOOLS\L2-PLATFORM\GeriCode`) | **Repo** | **Meta-repo L2-PLATFORM : config Agent Manager, KIX, TRIX bridges** |
| `Buzz@block/crates/buzz-core/src/kind.rs` | Rust | **Kinds TRIX/KIX ajoutes (50001, 50002, 60001)** |
| `Buzz@block/schema/trix-kix-extension.sql` | SQL | **Tables optionnelles TRIX/KIX (proposees, non deployees)** |

---

## 7. RISQUES

| Risque | Impact | Probabilite | Mitigation |
|--------|--------|-------------|------------|
| `buzz-relay` non deploye a la date prevue | HIGH | Moyenne | Reporter P4-P7 ; maintenir P0-P3 fonctionnels |
| Schema Postgres instable (breaking changes) | HIGH | Faible | Versionner les migrations ; adapter `BuzzEventReader` |
| Performance fan-out sous charge | MEDIUM | Moyenne | Implementer batching + cache Redis |
| Complexite integration 7 runners cognitifs | MEDIUM | Faible | Decomposer en sprints atomiques (P5) |
| Dependance Nostr third-party clients | LOW | Faible | Tester avec `nak` ; maintenir compatibilite NIP-29 |
| **TRIX non integre au bus Buzz (gouvernance manquante)** | **HIGH** | **FAIBLE** | **P5.5 implante : mapping 25 kinds TALEX, schema TRIX/KIX documente** |
| **KIX non integre au bus Buzz (lifecycle manquant)** | **HIGH** | **FAIBLE** | **P5.5 implante : kind KIX-LC-001 reconnu, health-check BUZZ-X etendu** |
| **Git Arbiter TRIX (port 8742) bloque sans preavis** | **MEDIUM** | **Faible** | **Demarrage automatique via `git_arbiter_server.py` (TRIX) - valide** |

---

## 8. TRACABILITE

### 8.1 Thought Chain

```yaml
thought_chain:
  - source: "Chat / Expression utilisateur"
    artifact: "PRD-MOC-BUZZ-X-BUS-2026-08-17.md"
    intent_hash: "0xBUZZ_BUS_OPERATIONALIZATION_20260817"
  - source: "PRD MOC v1.0"
    artifact: "Implementation commits (P4, P6, P7)"
    commit_hashes: ["cdd3b2c", "ea69c21", "c971d5a", "1d7830d"]
  - source: "Audit TRIX/KIX"
    artifact: "PRD MOC v1.1 - Ajout TRIX/KIX comme gouvernants"
    commit_hashes: ["e74180e"]
  - source: "Implementation v1.1"
    artifact: "P5.5 + kinds TRIX/KIX + integration complete"
    commit_hashes: ["5c8e70e", "fa37746"]
```

### 8.2 References

- **Repo source** : `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\Buzz@block`
- **Architecture** : `ARCHITECTURE.md`
- **Schema** : `schema/schema.sql`
- **Nostr** : `NOSTR.md`
- **Design** : `design.yaml`
- **PRD MOC lie** : `PRD-MOC-TALEX-BUZZ-CONVERSATION-ANALYSIS-2026-08-17.md`
- **ADR** : ADR-2026-08-14-PIPELINE-ASCENDANT-KG (proposed)
- **ADR** : ADR-2026-08-15-TALEX-CIR-ADAPTER-ARCHITECTURE (proposed)
- **ADR TRIX** : ADR-2026-06-28-001-LOGICAL-ARCHITECTURE-N1-N4 (pattern-router N+1/N+2/N+3/N+4)
- **ADR TRIX** : ADR-2026-06-27-017-GIT-ARBITER (Git Arbiter port 8742)
- **ADR KIX** : ADR-2026-07-27-002-KIX (orchestrateur cycle de vie runners)
- **TRIX** : `D:\DO\WEB\TOOLS\L4-TOOLS\TRIX` (runtime N+4, dispatch table 243)
- **KIX** : `D:\DO\WEB\TOOLS\L2-PLATFORM\KIX` (orchestrateur N+2/N+3)
- **MOX gates** : P-108, P-109
- **Implementation** : lancee 2026-08-17 via direct (P4, P6, P7, P5.5) - Agent Manager V9.9 buggue
- **Commits TALEX** : ea69c21, cdd3b2c, 5c8e70e (mapping 25 kinds + tests)
- **Commits BUZZ-X** : c971d5a, 1d7830d, e74180e (PRD v1.1), fa37746 (health-check TRIX/KIX)
- **Commits GOVERNANCE-HUB** : 6da261f4 (2 ADR proposed)
- **GeriCode** : D:\DO\WEB\TOOLS\L2-PLATFORM\GeriCode (meta-repo, config Agent Manager, KIX, TRIX bridges)
- **Agent Manager** : version issue de GeriCode V9.9 - worktree placement bug + silent failure

---

*Genere automatiquement depuis l'architecture Buzz@block le 2026-08-17.
v1.2 - 2026-08-17 : Mise a jour etat implementation - P5.5 termine, commits documentes, tests passes.
v1.1 - 2026-08-17 : Ajout section TRIX/KIX comme gouvernants du bus Buzz.*
