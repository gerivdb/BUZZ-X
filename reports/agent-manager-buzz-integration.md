# Rapport d'integration Agent Manager + Bus Buzz

**Statut** : PROPOSED
**IntentHash** : 0xBUZZ_BUS_AGENT_MANAGER_INTEGRATION_20260817
**Source** : PRD-MOC-BUZZ-X-BUS-2026-08-17.md (sections 3, 4, 6, 7)
**Refs ADR** : ADR-2026-08-14-PIPELINE-ASCENDANT-KG, ADR-2026-08-15-TALEX-CIR-ADAPTER-ARCHITECTURE

---

## 1. Contexte

Agent Manager V9.10 gere les sessions KiloCode paralleles (worktrees git,
sessions locales, modeles). Le bus Buzz (relay Nostr Rust, stockage Postgres +
Redis) devient le canal unifie entre :

- Agent Manager (evenements de session : start, end, error, retry)
- Runners cognitifs (LLUX, TIMX, TLM-LANG, ROOTX, RLM-243, KIX, TRIX)
- KiloCode / Kilo (hooks, prompts, resultats)
- Humains (clients Nostr)

Ce rapport documente l'integration cote BUZZ-X (scripts, health-check) et
cote TALEX (BuzzEventReader, CLI analyze buzz).

---

## 2. Architecture cible

```
+-------------------+       +-------------------------+
|  Agent Manager    |       |    Humain / CLI         |
|  (V9.10)          |       |  (buzz-cli, nak, web)   |
+--------+----------+       +-----------+-------------+
         |                            |
         | evenements Buzz (Nostr)    |
         v                            v
+--------------------------------------------------+
|           buzz-relay (Axum / Rust)               |
|  NIP-42 auth | EVENT pipeline | REQ handler      |
|  SubscriptionRegistry | Fan-out | Workflow engine |
+--------+---------------------+--------------------+
         |                            |
    +----v----+                +------v------+
    | Postgres|                |    Redis    |
    | events  |                | presence    |
    | channels|                | typing      |
    | tokens  |                | pub/sub     |
    | workflows|               |             |
    | audit   |                |             |
    +---------+                +-------------+
         |                            |
         +------------+---------------+
                      v
            +---------------------+
            |  TALEX BuzzEventReader|
            |  (buzz_store.py)     |
            +----------+----------+
                       |
                       v
            +---------------------+
            |  UnifiedSemanticGraph|
            |  + NexusNarrator     |
            +---------------------+
```

---

## 3. Mapping evenements Buzz -> hooks Agent Manager

| Kind Buzz | Libelle         | Hook Agent Manager               | Action Buzz                         |
|-----------|-----------------|----------------------------------|-------------------------------------|
| 9         | Message         | session.log                      | evenement de conversation           |
| 7         | Reaction        | session.feedback                 | metrique d'engagement               |
| 20001     | Presence        | runner.health_check              | etat presence du runner             |
| 20002     | Typing          | session.activity                 | indicateur d'activite temps reel    |
| 9000      | Add user        | session.add_participant          | ajout d'un membre au canal          |
| 9001      | Remove user     | session.remove_participant       | suppression d'un membre             |
| 9002      | Edit group      | session.update_metadata          | modification des metadonnees groupe |
| 9007      | Group creation  | session.create_workspace         | creation d'un workspace             |
| 9008      | Group deletion  | session.archive_workspace        | suppression d'un workspace          |
| 39000     | Group metadata  | runner.discovery                 | decouverte de groupes               |
| 39001     | Group admins    | runner.discovery                 | decouverte des admins               |
| 39002     | Group members   | runner.discovery                 | decouverte des membres              |
| 44100     | Membership added| session.membership_update        | notification adhesion               |
| 44101     | Membership removed| session.membership_update      | notification depart                 |
| 0         | Profile         | runner.identity                  | metadonnees d'identite agent        |
| 5         | Deletion        | audit.log                        | suppression d'event (audit)         |
| 1059      | DM gift wrap    | session.private_message          | messagerie privee securisee         |

---

## 4. Securite et BDCP

Le mode BDCP (Behind CDP) protege l'anonymat reseau et le quota de tokens.
Le bus Buzz ne sort JAMAIS du reseau local :

- Relay Rust ecoute sur localhost uniquement (pas d'exposition externe)
- Redis presence/typing : TTL court (60s presence, 5s typing), pas de
  persistence, donnees ephemeres uniquement
- Postgres : stockage local, pas de replication externe
- Credentials : NIP-42 auth, tokens api stockes dans api_tokens (table
  securisee), jamais en clair dans les events
- Agent Manager injecte les credentials via variables d'environnement
  (BUZZ_RELAY_URL, BUZZ_PRIVATE_KEY, BUZZ_AUTH_TAG) - pas de fichier
  de config sur disque

Regle absolue : aucune connexion sortante vers l'exterieur n'est autorisee
sans ordre explicite de l'utilisateur (mots-cles : "ouvre le clapet",
"passe en FREE").

---

## 5. Plan de test integration

### 5.1 Tests unitaires (existants)

- TALEX `tests/test_buzz_store.py` : 8 tests (Postgres mock, Redis mock)
- TALEX `tests/test_cli_buzz.py` : 5 tests (CLI analyze buzz, monkeypatch)

### 5.2 Tests d'integration (locaux, sans reseau)

1. **Health-check schema** : `scripts/buzz_bus_health.py --schema PATH --out md`
   Verifie que schema.sql contient les tables attendues et que kind.rs couvre
   les kinds du PRD.

2. **Validation SQL** : verifier que les requetes generees par PostgresBuzzStore
   respectent le schema multi-tenant (community_id, parametres lies).

3. **Validation Redis** : mock redis-py, verifier get/setex/publish pour
   presence, typing, events.

### 5.3 Tests E2E (deploiement futur, P5-P7)

- Lancer buzz-relay localement (Docker Compose)
- Publier des events Nostr via `nak` CLI
- Lancer TALEX CLI : `x-forge analyze buzz --root PATH`
- Verifier les outputs JSON/MD

---

## 6. References

- PRD MOC : PRD-MOC-BUZZ-X-BUS-2026-08-17.md
- Architecture : Buzz@block/ARCHITECTURE.md
- Schema : Buzz@block/schema/schema.sql
- Nostr : Buzz@block/NOSTR.md
- ADR : ADR-2026-08-14-PIPELINE-ASCENDANT-KG
- ADR : ADR-2026-08-15-TALEX-CIR-ADAPTER-ARCHITECTURE
- Health-check : scripts/buzz_bus_health.py
- TALEX reader : src/talex/readers/buzz_store.py, src/talex/readers/buzz_events.py
- TALEX CLI : src/talex/cli.py (cmd_analyze_buzz, cmd_analyze_integrated)

---

*Genere le 2026-08-17 - scope local, BDCP respecte.*
