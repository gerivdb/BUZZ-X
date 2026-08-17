# TRIX/KIX Kind Extension - BUZZ-X Overlay

## Statut
ACCEPTED - ADR-2026-08-17-001-TRIX-GIT-ARBITER + ADR-2026-07-27-016-kix-orchestrator

## Contexte
Buzz@block est un repo encapsule non modifiable par gerivdb.
BUZZ-X le parasite positivement via overlay local.
Les kinds TRIX/KIX sont donc definis dans BUZZ-X, pas dans Buzz@block.

## Nouveaux kinds

| Kind | Libelle | ADR | Usage |
|------|---------|-----|-------|
| 50001 | TRIX governance event | ADR-2026-08-17-001 | ADR validation, pattern-router decisions |
| 50002 | TRIX arbiter lock | ADR-2026-08-17-001 | Git Arbiter locks (port 8742) |
| 60001 | KIX runner lifecycle | ADR-2026-07-27-016 | Runner RLM start/stop/heartbeat |

## Schema SQL local (BUZZ-X)

Ce schema est stocke dans BUZZ-X, pas dans Buzz@block.
Voir `docs/trix-kix-extension-schema.md` pour le SQL complet.

## Integration TALEX

TALEX reconnait ces kinds via `src/talex/readers/buzz_events.py` (mapping 25 kinds).
Tests: `tests/test_buzz_kinds.py` (6 tests) + `tests/test_runners_p5.py` (7 tests).

## References

- PRD MOC: `PRD-MOC/PRD-MOC-BUZZ-X-BUS-2026-08-17.md` v1.5
- ADR: `ADR-2026-08-17-001-TRIX-GIT-ARBITER` (accepted)
- ADR: `ADR-2026-07-27-016-kix-orchestrator` (accepted)
