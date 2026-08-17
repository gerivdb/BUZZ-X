# `buzz_bus_health.py` - Health-check local du bus Buzz

CLI Python 3.12 (type hints, docstrings FR) qui valide la **coherence locale**
du bus Buzz (`BUZZ-X` / `Buzz@block`) **sans aucune connexion reseau ni base
live**. Il croise trois sources de verite lues depuis le disque :

- `Buzz@block/schema/schema.sql` - schema Postgres source de verite ;
- `Buzz@block/crates/buzz-core/src/kind.rs` - registre des kinds Buzz ;
- `PRD-MOC/PRD-MOC-BUZZ-X-BUS-2026-08-17.md` - kinds operationnels (S3.2)
  et tables core attendues (S2.1 / S3.1).

Aucun effet de bord reseau. Le script ne lit que des fichiers et ne modifie
rien. Mode BDCP respecte (aucun `docker`, `cargo run` ou appel reseau).

---

## Usage

```bash
# Chemin par defaut (Buzz@block + PRD resolus depuis le repo BUZZ-X) -> Markdown
python buzz_bus_health.py

# Sortie JSON
python buzz_bus_health.py --out json

# Forcer des chemins explicites
python buzz_bus_health.py \
    --schema "D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\Buzz@block\schema\schema.sql" \
    --kindrs "D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\Buzz@block\crates\buzz-core\src\kind.rs" \
    --prd    "D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\PRD-MOC\PRD-MOC-BUZZ-X-BUS-2026-08-17.md" \
    --out md

# Supprimer la sortie stdout (sortie uniquement fichier/capture)
python buzz_bus_health.py --quiet
```

---

## Arguments

| Argument | Type | Defaut | Description |
|---|---|---|---|
| `--schema PATH` | chemin | `Buzz@block/schema/schema.sql` (auto) | Fichier SQL source de verite du schema Postgres. |
| `--kindrs PATH` | chemin | `Buzz@block/crates/buzz-core/src/kind.rs` (auto) | Registre Rust des kinds Buzz. Optionnel mais recommande. |
| `--prd PATH` | chemin | `PRD-MOC/PRD-MOC-BUZZ-X-BUS-2026-08-17.md` (auto) | PRD MOC definissant les kinds operationnels. |
| `--buzzblock PATH` | chemin | repo BUZZ-X (auto) | Racine `Buzz@block` pour deduire tous les chemins par defaut. |
| `--out FORMAT` | `json` \| `md` | `md` | Format de rapport produit. |
| `--quiet` | flag | off | Supprime l'affichage stdout. |

Si un chemin par defaut n'est pas resolu (fichier absent), le script emet un
avertissement et bascule sur la liste statique des kinds PRD S3.2 ; un
schema manquant genere une erreur bloquante.

---

## Sortie

### Markdown (`--out md`)
Rapport lisible :
- **Statut global** [OK] SAIN / [WARN] DEGRADE.
- **Tables core** : presence de `events`, `channels`, `api_tokens`,
  `workflows`, `audit_log` et colonnes critiques.
- **Kinds operationnels** : couverture PRD <-> `kind.rs` (pourcentage).
- **Avertissements** : kinds ephemeres Redis (presence 20001, typing 20002),
  colonnes manquantes, fichiers non resolus.
- **Erreurs bloquantes** : schema introuvable, etc.

### JSON (`--out json`)
Objet structure :
```json
{
  "healthy": true,
  "tables": { "checked": {...}, "missing": [] },
  "kinds": { "prd_total": 22, "covered": [...], "uncovered": [], "coverage_pct": 100.0 },
  "warnings": [...],
  "errors": []
}
```

### Code de retour
- `0` - sain (aucune erreur, aucune table core manquante).
- `1` - degrade (erreurs ou tables manquantes).

---

## Couverture verifiee

Le health-check valide :
1. **Tables core** (PRD S2.1/S3.1) : `events` (`id`, `pubkey`, `kind`,
   `tags`, `content`, `created_at`, `community_id`), `channels`,
   `api_tokens` (alias `tokens`), `workflows`, `audit_log` (alias `audit`).
2. **Kinds PRD S3.2** : les 22 kinds operationnels, compares aux constantes
   `KIND_*` de `kind.rs`. Les kinds 20001/20002 (Redis) sont exclus des
   manquants car non persistes en Postgres.

Rapport d'integration associe :
`reports/buzz-conversation-integration.md`.

---

## Integration Agent Manager V9.10

### Principe

Agent Manager V9.10 publie et consomme des evenements Buzz pour tracer
son cycle de vie de session. Tout passe par le `buzz-relay` : aucune
session ne communique directement avec Postgres ou Redis.

### Kinds utilises par Agent Manager

| Kind | Libelle | Hook Agent Manager |
|------|---------|--------------------|
| 9007 | Group creation | start_session |
| 9008 | Group deletion | end_session |
| 9 | Stream message | start_session, retry, error |
| 7 | Reaction | end_session (success) |
| 20001 | Presence | start_session, end_session |
| 20002 | Typing | start_session |
| 5 | Deletion | error |
| 44100 | Membership added | start_session |
| 44101 | Membership removed | end_session |

### Workflow type

```
start_session
  -> EVENT kind=9007 (group creation)
  -> EVENT kind=9000 (add user)
  -> EVENT kind=39000 (group metadata)
  -> EVENT kind=39002 (group members)
  -> EVENT kind=44100 (membership added)
  -> EVENT kind=20002 (typing)
  -> EVENT kind=20001 (presence)

end_session
  -> EVENT kind=9008 (group deletion)
  -> EVENT kind=9001 (remove user)
  -> EVENT kind=44101 (membership removed)
  -> EVENT kind=7 (reaction confirmation)

error
  -> EVENT kind=5 (deletion / audit)
  -> EVENT kind=9 (message explicatif)

retry
  -> EVENT kind=9 (message de retry avec delai)
```

### Securite BDCP

Le bus Buzz ne sort pas du reseau local. Le health-check local
(`python buzz_bus_health.py`) valide la coherence sans Docker ni reseau.
Les credentials sont stockes en `.env` local (non commite). Redis presence
(20001) et typing (20002) sont ephemeres (TTL respectif 180s et 60s) et
ne sont jamais persistes en Postgres.

### Rapport detaille

Voir `reports/agent-manager-buzz-integration.md` pour :
- Mapping complet kinds -> hooks
- Architecture de securite BDCP
- Plan de test integration (pytest)
- Diagramme ASCII du flux
- References ADR-2026-08-14 et ADR-2026-08-15
