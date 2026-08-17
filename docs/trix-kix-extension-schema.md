# Extension schema TRIX/KIX - Bus Buzz

## Statut
PROPOSED - Non deploye. Requiert ADR dedies avant integration.

## Contexte
Le PRD MOC v1.1 (PRD-MOC-BUZZ-X-BUS-2026-08-17.md) definit 3 nouveaux kinds
pour TRIX (N+4, L4-TOOLS) et KIX (N+2/N+3, L2-PLATFORM) comme gouvernants
du bus Buzz. Cette extension schema propose les tables Postgres optionnelles
correspondantes.

## Nouveaux kinds

| Kind | Libelle | Composant | Usage |
|------|---------|-----------|-------|
| 50001 | TRIX governance event | TRIX | Evenements de gouvernance (validation ADR, pattern-router, gates) |
| 50002 | TRIX arbiter lock | TRIX | Verrous Git Arbiter (port 8742), etat du clapet BDCP |
| 60001 | KIX runner lifecycle | KIX | Cycle de vie des runners RLM (start/stop/heartbeat) |

## Schema SQL propose

### trix_governance_events
```sql
CREATE TABLE trix_governance_events (
    id BIGSERIAL PRIMARY KEY,
    kind INT NOT NULL DEFAULT 50001,
    pubkey TEXT NOT NULL,
    content TEXT,
    tags JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    adr_hash TEXT,
    gate_status TEXT, -- proposed | accepted | deprecated | superseded
    source_repo TEXT,
    community_id UUID REFERENCES communities(id) ON DELETE CASCADE
);
CREATE INDEX idx_trix_governance_events_created_at ON trix_governance_events(created_at);
CREATE INDEX idx_trix_governance_events_adr_hash ON trix_governance_events(adr_hash);
```

### arbiter_locks
```sql
CREATE TABLE arbiter_locks (
    id BIGSERIAL PRIMARY KEY,
    kind INT NOT NULL DEFAULT 50002,
    pubkey TEXT NOT NULL,
    content TEXT,
    tags JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    lock_key TEXT NOT NULL, -- cle du lock (ex: commit-hash, branch-name)
    lock_type TEXT NOT NULL, -- commit | branch | tag | workflow
    acquired_by TEXT, -- identifiant du composant TRIX
    released_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active', -- active | released | expired | revoked
    community_id UUID REFERENCES communities(id) ON DELETE CASCADE
);
CREATE INDEX idx_arbiter_locks_lock_key ON arbiter_locks(lock_key);
CREATE INDEX idx_arbiter_locks_status ON arbiter_locks(status);
CREATE INDEX idx_arbiter_locks_created_at ON arbiter_locks(created_at);
```

### kix_runner_lifecycle
```sql
CREATE TABLE kix_runner_lifecycle (
    id BIGSERIAL PRIMARY KEY,
    kind INT NOT NULL DEFAULT 60001,
    pubkey TEXT NOT NULL,
    content TEXT,
    tags JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    runner_id TEXT NOT NULL, -- identifiant du runner (ex: RLM-243, TIMX-007)
    runner_type TEXT NOT NULL, -- cognitive | orchestrator | gateway | monitoring
    event_type TEXT NOT NULL, -- start | stop | heartbeat | error | timeout
    port INT, -- port d'ecoute du runner (8786-8799)
    status TEXT NOT NULL, -- running | stopped | error | timeout | degraded
    duration_ms INT, -- duree d'execution en millisecondes
    error_message TEXT,
    community_id UUID REFERENCES communities(id) ON DELETE CASCADE
);
CREATE INDEX idx_kix_runner_lifecycle_runner_id ON kix_runner_lifecycle(runner_id);
CREATE INDEX idx_kix_runner_lifecycle_event_type ON kix_runner_lifecycle(event_type);
CREATE INDEX idx_kix_runner_lifecycle_status ON kix_runner_lifecycle(status);
CREATE INDEX idx_kix_runner_lifecycle_created_at ON kix_runner_lifecycle(created_at);
```

## Mapping vers hooks existants

### TRIX
- ADR-2026-06-28-001 (pattern-router) -> trix_governance_events.gate_status
- ADR-2026-05-14-004 (KILO-CODE-HOTL-OPERATIONAL-STD) -> arbiter_locks.lock_type
- ADR-2026-07-28-020 (CTULU-TRIX-ECOS-CLI-ORCHESTRATION) -> trix_governance_events.source_repo

### KIX
- ADR-2026-07-27-002 (KIX-LIFECYCLE-ARCHITECTURE) -> kix_runner_lifecycle.runner_type
- PRD MOC v1.1 P5.5 -> kix_runner_lifecycle.event_type

## Integration avec le health-check existant

Le script scripts/buzz_bus_health.py inclut deja ces kinds dans PROPOSED_KINDS
avec statut PROPOSED. La section "Kinds proposes (TRIX/KIX)" du rapport Markdown
liste ces kinds avec leurs ADR associees.

## Notes
- Ces tables sont OPTIONNELLES et ne sont pas dans schema.sql tant que les ADR
  ne sont pas acceptees.
- Les kinds 50001, 50002, 60001 sont deja reconnus par TALEX
  (src/talex/readers/buzz_events.py) avec labels et classification RLM-243.
- Aucune migration Alembic ne doit etre cree avant acceptation des ADR.
