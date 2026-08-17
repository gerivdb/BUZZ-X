# Rapport d'integration - Bus Buzz <-> TALEX

**Date** : 2026-08-17
**Repo hote** : `BUZZ-X` (`Buzz@block` relay Rust)
**Consumer cible** : `TALEX` - `BuzzEventReader` (WT1)
**Source de verite** : `PRD-MOC-BUZZ-X-BUS-2026-08-17.md`
**IntentHash** : `0xBUZZ_BUS_OPERATIONALIZATION_20260817`
**Statut** : Proposition (revue HITL requise)

---

## 1. Objectif

Documenter l'architecture cible de l'integration entre le **bus Buzz**
(`Buzz@block`, relay Nostr Rust) et le moteur narratif **TALEX**, et preciser
comment le composant `BuzzEventReader` (TALEX Work-Task 1) se branche sur le
flux d'events du bus pour alimenter l'analyse de conversation et le
`ConversationNarrator`.

Aucune dependance reseau n'est requise pour la phase locale (WT1) : le
`BuzzEventReader` consomme des events Buzz **simules ou rejoues** depuis
Postgres/Redis, conformement au mode BDCP (aucune sortie reseau).

---

## 2. Architecture cible (PRD S3.1)

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
                ^
                | flux events (fan-out / REQ)
+---------------+-----------------------------------------------------+
|  TALEX - BuzzEventReader (WT1) -> ConversationNarrator -> narratif     |
+---------------------------------------------------------------------+
```

Le `buzz-relay` est la **source de verite unique**. TALEX ne parle jamais
directement aux clients : il lit le flux d'events persistant (Postgres) et le
flux ephemere (Redis pub/sub pour presence/typing), puis projette ces events
en narratifs de conversation.

---

## 3. Kinds operationnels (PRD S3.2)

TALEX consomme les kinds suivants. Le `BuzzEventReader` doit pouvoir parser et
router chacun d'eux vers le bon type de narratif.

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

**Stockage attendu** (PRD S2.1) :
- **Postgres** : events (kinds persistants), channels, tokens (`api_tokens`),
  workflows, audit (`audit_log`).
- **Redis** : presence (20001), typing (20002), pub/sub - ephemeres, jamais
  stockes tels quels.

> Note de coherence : le health-check local (`scripts/buzz_bus_health.py`)
> confirme 100 % de couverture des kinds PRD dans `buzz-core/src/kind.rs`,
> et la presence des tables core (`events`, `channels`, `api_tokens`,
> `workflows`, `audit_log`) dans `schema/schema.sql`. Les kinds 20001/20002
> sont ephemeres Redis et ne sont pas attendus en Postgres.

---

## 4. Branchement de `BuzzEventReader` (TALEX WT1)

### 4.1 Responsabilite

`BuzzEventReader` est la **couche d'ingestion** cote TALEX. Il :
1. lit les events Buzz depuis la source (simulee en local, ou Postgres/Redis en
  phase P4+).
2. Parse chaque event selon son `kind` (mapping S3).
3. Normalise en structure `BuzzEvent` interne (pubkey, kind, tags, content,
   channel_id, created_at).
4. Emet un flux ordonne vers le `ConversationNarrator`.

### 4.2 Contrat d'interface (proposition)

```
BuzzEvent
  +-- id: bytes
  +-- pubkey: bytes
  +-- kind: u32
  +-- tags: list[tuple[str, ...]]
  +-- content: str
  +-- channel_id: uuid | None
  +-- created_at: datetime

BuzzEventReader.read(source) -> Iterator[BuzzEvent]
  +-- route(kind) -> handler de narratif
```

- **Kind 9** -> evenement de message principal -> `ConversationNarrator`.
- **Kinds 0 / 9000-9002 / 9007-9009 / 9021-9022 / 39000-39002 / 44100-44101**
  -> evenements de gestion de canal/membres -> metadonnees de conversation
  (sans contenu narratif direct).
- **Kinds 7 / 20001 / 20002** -> signaux d'engagement/presence/typing ->
  annotations temporelles, non persistes comme messages.
- **Kind 5** -> suppression -> marquage " deleted " cote narratif (audit).
- **Kind 1059** -> DM gift wrap -> dechiffrement cote owner (hors perimetre WT1).

### 4.3 Mode local (WT1, sans deploiement)

En l'absence de `buzz-relay` deploye, `BuzzEventReader` consomme un corpus
d'events **simules** (fixtures JSON) reproduisant la forme des events Buzz.
Cela permet de valider le parsing et le routage sans Docker/Postgres/Redis -
conformement au mode BDCP (aucun `docker`, aucun `cargo run` reel, aucune
sortie reseau).

### 4.4 Passage a l'adapteur live (P4)

La phase P4 remplace la source simulee par un adapteur Postgres/Redis :
- **Postgres** : requete `events` filtree par `community_id` + `channel_id`,
  tri par `created_at`.
- **Redis** : abonnement pub/sub pour 20001/20002 (presence/typing temps reel).
Le contrat `BuzzEventReader.read()` reste inchange - seul le backend de source
est substitue.

---

## 5. Tracabilite et conformite

- **SOT** : `PRD-MOC-BUZZ-X-BUS-2026-08-17.md` (section 3).
- **ADR lies** : `ADR-2026-08-14-PIPELINE-ASCENDANT-KG`,
  `ADR-2026-08-15-TALEX-CIR-ADAPTER-ARCHITECTURE`.
- **Health-check** : `scripts/buzz_bus_health.py` (coherence locale du bus,
  sans reseau).
- **Mode BDCP** : respecte - aucune sortie reseau, aucun deploiement
  Docker/Postgres/Redis reel dans cette phase.

---

*Genere localement le 2026-08-17 - revue HITL requise avant merge.*
