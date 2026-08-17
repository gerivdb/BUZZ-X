---
type: "PRD_MOC"
version: "1.0.0"
date: "2026-08-17"
status: "PROPOSED"
intent_hash: "0xBUZZ_BUS_OPERATIONALIZATION_20260817"
inherits: ["moc-governance"]
mox_gates:
  - P-108
  - P-109
---

# PRD MOC - BUZZ-X - Operationnalisation du Bus Buzz

## 1. RESUME EXECUTIF

Ce PRD MOC couvre la mise en oeuvre operationnelle du **bus Buzz** tel qu'heberge dans `BUZZ-X` / `Buzz@block` :
- **Relay Rust** (`buzz-relay` Axum) : source de verite unique
- **Stockage** : Postgres (events, channels, tokens, workflows, audit, search) + Redis (presence, typing, pub/sub)
- **Protocole** : Nostr NIP-01/NIP-29/NIP-42/NIP-98/NIP-50/NIP-10/NIP-17
- **Integrations cibles** : TALEX (`BuzzEventReader`), GeriCode, BUZZ-X overlay, KIX, NEXUS, KIVA, ONTOLOGY, GOVERNANCE-HUB

**Source** : `BUZZ-X/Buzz@block/ARCHITECTURE.md`, `schema/schema.sql`, `NOSTR.md`, `design.yaml`
**IntentHash** : `0xBUZZ_BUS_OPERATIONALIZATION_20260817`
**Statut** : Genere le 2026-08-17

---

## 2. CONTEXTE ET PERIMETRE

### 2.1 Contexte

`BUZZ-X` est le repo hote qui integre **Buzz@block** comme bus de communication du systeme gerivdb. Buzz@block est un relay Nostr Rust qui constitue le **canal unifie** entre :
- les runners cognitifs (LLUX, TIMX, TLM-LANG, ROOTX, RLM-243, KIX, TRIX)
- l'Agent Manager V9.10
- KiloCode / Kilo
- les humains via clients Nostr

TALEX dispose deja d'un `BuzzEventReader` capable de parser des events Buzz simules. Ce PRD MOC vise a **rendre le bus Buzz pleinement operationnel** pour alimenter TALEX et les autres consumers.

### 2.2 Perimetre

| Strate | Composants | Impact |
|--------|------------|--------|
| L4-TOOLS | BUZZ-X (`Buzz@block` relay, overlay GeriCode) | Extension majeure du bus |
| L4-TOOLS | TALEX (`BuzzEventReader`, `ConversationNarrator`) | Consumer operationnel |
| L2-PLATFORM | GeriCode (callbacks Agent Manager) | Integration callbacks |
| L2-PLATFORM | KIX (verification statut runners) | Point d'integration cognitif |
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
     +------------+
```

### 3.2 Kinds Buzz operationnels

| Kind | Libelle | Statut | Usage TALEX |
|------|---------|--------|-------------|
| 0 | Profile | [OK] | metadonnee agent |
| 5 | Deletion | [OK] | audit suppression |
| 7 | Reaction | [OK] | metrique engagement |
| 9 | Message | [OK] | evenement principal |
| 20001 | Presence | [OK] | sante runners |
| 20002 | Typing | [OK] | activite temps reel |
| 40002 | Rich content | [WARN] | contenu structure |
| 9000 | Add user | [OK] | gestion canaux |
| 9001 | Remove user | [OK] | gestion canaux |
| 9002 | Edit group | [OK] | metadonnees |
| 9005 | Admin delete | [OK] | moderation |
| 9007 | Group creation | [OK] | creation workspace |
| 9008 | Group deletion | [OK] | suppression workspace |
| 9009 | Create invite | [WARN] | invitation |
| 9021 | Join request | [OK] | demande adhesion |
| 9022 | Leave group | [OK] | depart membre |
| 1059 | DM gift wrap | [OK] | messagerie privee |
| 39000 | Group metadata | [OK] | discovery |
| 39001 | Group admins | [OK] | discovery |
| 39002 | Group members | [OK] | discovery |
| 44100 | Membership added | [OK] | notification |
| 44101 | Membership removed | [OK] | notification |

---

## 4. PLAN D'IMPLEMENTATION

### 4.1 Phases

| Phase | Actions | Duree | Dependances |
|-------|---------|-------|------------|
| **P0** | Infrastructure Buzz@block (Docker, migrations, Redis, Postgres) | [OK] Fait | - |
| **P1** | Relay Rust operationnel (NIP-42, EVENT, REQ, fan-out) | [OK] Fait | P0 |
| **P2** | kinds core (9, 7, 20001, 20002, 9000-9002, 39000-39002) | [OK] Fait | P1 |
| **P3** | Integration TALEX (`BuzzEventReader` local) | [OK] Fait | P2 |
| **P4** | Adapteur Postgres/Redis pour `BuzzEventReader` | ~5 jours | P3, Buzz@block deploye |
| **P5** | Integration runners cognitifs (LLUX, TIMX, TLM-LANG, ROOTX, RLM-243, KIX, TRIX) | ~4 jours | P4 |
| **P6** | CLI `x-forge analyze buzz` + health-check bus | ~3 jours | P4 |
| **P7** | Rapport integre Agent Manager + Buzz | ~3 jours | P6 |

**Total estime** : ~15 jours apres deploiement operationnel de Buzz@block.

### 4.2 Livrables

| Livrable | Format | Validation |
|----------|--------|------------|
| `buzz-relay` deploye (Docker Compose) | Rust / Docker | Tests integration passants |
| `schema/schema.sql` + migrations | SQL | `sqlx migrate run` OK |
| `src/talex/readers/buzz_events.py` adapteur Postgres/Redis | Python | Tests unitaires + integration |
| `src/talex/cli.py` - `analyze buzz` / `analyze integrated` | Python | CLI fonctionnelle |
| `reports/buzz-conversation-integration.md` | Markdown | Revue HITL |
| `BUZZ-X/PRD-MOC/PRD-MOC-BUZZ-X-BUS-2026-08-17.md` | Markdown | Gouvernance validee |

---

## 5. TESTS ET VALIDATION

### 5.1 Tests prevus

| Type | Cible | Outil |
|------|-------|-------|
| Integration | `buzz-relay` + Postgres + Redis | `cargo test`, `buzz-test-client` |
| API | NIP-42, EVENT, REQ, HTTP bridge | `nak` CLI, pytest |
| Performance | Fan-out multi-connections | Load test local |
| TALEX | `BuzzEventReader` sur vraie DB | pytest + Postgres testcontainers |
| E2E | CLI TALEX + bus Buzz reel | Pipeline integration |

### 5.2 Metriques

| Metrique | Cible | Mesure |
|----------|-------|--------|
| Latence EVENT -> fan-out | < 50 ms p95 | `buzz-test-client` |
| Throughput REQ | > 1000 events/s | Load test |
| Couverture kinds Buzz | 100% kinds core | Nombre de kinds testes / total |
| Integration TALEX | 7/7 runners | Nombre de runners avec point d'integration |
| Disponibilite bus | 99.9% | Monitoring Redis/Postgres |

---

## 6. DEPENDANCES

| Dependance | Type | Justification |
|------------|------|---------------|
| `buzz-relay` deploye | Repo / Infrastructure | Source des events Buzz pour TALEX |
| Postgres + Redis | Infrastructure | Stockage events, presence, pub/sub |
| `gerivdb/GOVERNANCE-HUB/known_repositories.yaml` v5.1 | SOT | Source de verite des repos actifs |
| ADR-2026-08-14-PIPELINE-ASCENDANT-KG | ADR | Architecture pipeline KG |
| ADR-2026-08-15-TALEX-CIR-ADAPTER-ARCHITECTURE | ADR | Architecture adaptateurs TALEX |
| ONTOLOGY concepts YAML | Ontologie | Cadre semantique pour les narratifs |
| `nak` CLI | Outil | Tests NIP-01/NIP-29 |

---

## 7. RISQUES

| Risque | Impact | Probabilite | Mitigation |
|--------|--------|-------------|------------|
| `buzz-relay` non deploye a la date prevue | HIGH | Moyenne | Reporter P4-P7 ; maintenir P0-P3 fonctionnels |
| Schema Postgres instable (breaking changes) | HIGH | Faible | Versionner les migrations ; adapter `BuzzEventReader` |
| Performance fan-out sous charge | MEDIUM | Moyenne | Implementer batching + cache Redis |
| Complexite integration 7 runners cognitifs | MEDIUM | Faible | Decomposer en sprints atomiques (P5) |
| Dependance Nostr third-party clients | LOW | Faible | Tester avec `nak` ; maintenir compatibilite NIP-29 |

---

## 8. TRACABILITE

### 8.1 Thought Chain

```yaml
thought_chain:
  - source: "Chat / Expression utilisateur"
    artifact: "PRD-MOC-BUZZ-X-BUS-2026-08-17.md"
    intent_hash: "0xBUZZ_BUS_OPERATIONALIZATION_20260817"
  - source: "PRD MOC"
    artifact: "Implementation commits"
    commit_hashes: []
  - source: "Implementation"
    artifact: "Production ready"
    benchmark_results: "JSON"
```

### 8.2 References

- **Repo source** : `D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\Buzz@block`
- **Architecture** : `ARCHITECTURE.md`
- **Schema** : `schema/schema.sql`
- **Nostr** : `NOSTR.md`
- **Design** : `design.yaml`
- **PRD MOC lie** : `PRD-MOC-TALEX-BUZZ-CONVERSATION-ANALYSIS-2026-08-17.md`
- **ADR** : ADR-2026-08-14-PIPELINE-ASCENDANT-KG (cree 2026-08-17, `proposed`, non commite - Arbiter Git bloquant)
- **ADR** : ADR-2026-08-15-TALEX-CIR-ADAPTER-ARCHITECTURE (cree 2026-08-17, `proposed`, non commite - Arbiter Git bloquant)
- **MOX gates** : P-108, P-109
- **Implementation** : lancee 2026-08-17 via Agent Manager (3 worktrees) - scope local seul (P3/P4 adapteur + CLI + scripts), **sans deploiement Docker/Postgres/Redis** (BDCP respecte). ADR requis desormais presents.

---

*Genere automatiquement depuis l'architecture Buzz@block le 2026-08-17.*
