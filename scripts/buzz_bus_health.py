#!/usr/bin/env python3.12
"""Health-check local de coherence du bus Buzz (BUZZ-X / Buzz@block).

Ce script valide, **sans aucune connexion reseau ni base live**, la
coherence locale du bus Buzz en croisant trois sources de verite :

1. ``schema/schema.sql`` (Buzz@block) - schema Postgres source de verite.
2. ``buzz-core/src/kind.rs`` (Buzz@block) - registre des kinds Buzz.
3. Le PRD MOC ``PRD-MOC-BUZZ-X-BUS-2026-08-17.md`` - kinds operationnels
   cibles (section 3.2) et tables attendues (section 2.1 / 3.1).

Le script ne lit que des fichiers locaux. Il produit un rapport de sante
au format JSON ou Markdown listant :

- les tables ``core`` attendues et leur presence dans le schema ;
- les colonnes critiques manquantes par table ;
- les kinds du PRD couverts par ``kind.rs`` vs non couverts ;
- les avertissements (presence/typing = Redis, kinds [WARN] du PRD, etc.).

Usage :
    python buzz_bus_health.py --schema PATH [--kindrs PATH]
                              [--prd PATH] [--out json|md]
                              [--buzzblock PATH] [--quiet]

Aucun effet de bord reseau. Ne modifie aucun fichier.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# -- Modele de donnees ----------------------------------------------------------

@dataclass
class HealthReport:
    """Rapport de sante agrege du bus Buzz.

    Attributes:
        schema_path: Chemin du fichier ``schema.sql`` analyse.
        kindrs_path: Chemin du fichier ``kind.rs`` analyse (peut etre None).
        prd_path: Chemin du PRD analyse (peut etre None).
        tables_checked: Tables core attendues et leur statut.
        missing_tables: Tables core absentes du schema.
        kinds_prd: Kinds operationnels declares dans le PRD.
        kinds_covered: Kinds PRD trouves dans ``kind.rs``.
        kinds_uncovered: Kinds PRD absents de ``kind.rs``.
        warnings: Liste d'avertissements textuels.
        errors: Liste d'erreurs bloquantes (fichiers manquants, etc.).
    """

    schema_path: str = ""
    kindrs_path: Optional[str] = None
    prd_path: Optional[str] = None
    tables_checked: dict[str, bool] = field(default_factory=dict)
    missing_tables: list[str] = field(default_factory=list)
    kinds_prd: list[int] = field(default_factory=list)
    kinds_covered: list[int] = field(default_factory=list)
    kinds_uncovered: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        """Retourne ``True`` si aucune erreur ni table manquante."""
        return not self.errors and not self.missing_tables


# -- Tables core attendues (PRD S2.1 / S3.1) ----------------------------------
# Cle = nom de la table Postgres ; valeur = colonnes critiques attendues.
# `presence`/`typing` sont Redis (hors schema Postgres) -> geres comme warnings.

EXPECTED_CORE_TABLES: dict[str, list[str]] = {
    "events": ["id", "pubkey", "kind", "tags", "content", "created_at", "community_id"],
    "channels": ["id", "community_id", "name", "channel_type"],
    "tokens": [],  # resolu vers api_tokens
    "workflows": ["id", "community_id", "name", "definition", "status"],
    "audit": [],  # resolu vers audit_log
}

# Resolution des noms " logiques " PRD vers noms reels de tables Postgres.
TABLE_ALIASES: dict[str, str] = {
    "tokens": "api_tokens",
    "audit": "audit_log",
}

# Kinds du PRD (section 3.2) operationnels - cle = kind, libelle = usage.
PRD_KINDS: dict[int, str] = {
    0: "Profile",
    5: "Deletion",
    7: "Reaction",
    9: "Message",
    20001: "Presence",
    20002: "Typing",
    40002: "Rich content",
    9000: "Add user",
    9001: "Remove user",
    9002: "Edit group",
    9005: "Admin delete",
    9007: "Group creation",
    9008: "Group deletion",
    9009: "Create invite",
    9021: "Join request",
    9022: "Leave group",
    1059: "DM gift wrap",
    39000: "Group metadata",
    39001: "Group admins",
    39002: "Group members",
    44100: "Membership added",
    44101: "Membership removed",
}

# Kinds proposes TRIX/KIX (PRD v1.1) - non deployes, ADR en attente.
PROPOSED_KINDS: dict[int, str] = {
    50001: "TRIX governance event",
    50002: "TRIX arbiter lock",
    60001: "KIX runner lifecycle",
}

# Kinds du PRD stockes en Redis (ephemeres) -> non attendus en Postgres.
REDIS_BACKED_KINDS: set[int] = {20001, 20002}


# -- Parsing SQL ----------------------------------------------------------------

def parse_sql_tables(schema_text: str) -> dict[str, set[str]]:
    """Extrait les tables ``CREATE TABLE`` et leurs colonnes depuis un schema SQL.

    Args:
        schema_text: Contenu textuel du fichier ``schema.sql``.

    Returns:
        Dictionnaire ``{nom_table: {colonnes}}`` (partitions exclues).
    """
    tables: dict[str, set[str]] = {}
    # Capture CREATE TABLE <nom> ( ... );  - multiline non greedy.
    table_pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][\w]*)\s*\((.*?)\);",
        re.DOTALL | re.IGNORECASE,
    )
    column_pattern = re.compile(r"^\s*([A-Za-z_][\w]*)\s+", re.MULTILINE)

    for match in table_pattern.finditer(schema_text):
        name = match.group(1)
        body = match.group(2)
        # Ignore les partitions PARTITION OF.
        if re.search(r"\bPARTITION\s+OF\b", body, re.IGNORECASE):
            continue
        cols = {cm.group(1).lower() for cm in column_pattern.finditer(body)}
        tables[name] = cols
    return tables


# -- Parsing kind.rs -----------------------------------------------------------

def parse_kind_constants(kindrs_text: str) -> set[int]:
    """Extrait les valeurs numeriques des constantes ``KIND_*`` depuis ``kind.rs``.

    Args:
        kindrs_text: Contenu textuel du fichier ``kind.rs``.

    Returns:
        Ensemble des valeurs de kinds (``u32``) declarees.
    """
    kinds: set[int] = set()
    # pub const KIND_XXX: u32 = <nombre>;
    pattern = re.compile(
        r"pub\s+const\s+KIND_[A-Z0-9_]+\s*:\s*u32\s*=\s*(\d+)\s*;",
    )
    for match in pattern.finditer(kindrs_text):
        kinds.add(int(match.group(1)))
    return kinds


# -- Parsing PRD (section 3.2) -------------------------------------------------

def parse_prd_kinds(prd_text: str) -> Optional[dict[int, str]]:
    """Tente d'extraire les kinds operationnels depuis la table PRD S3.2.

    Args:
        prd_text: Contenu textuel du PRD MOC.

    Returns:
        Dictionnaire ``{kind: libelle}`` ou ``None`` si la section est absente.
    """
    # La section 3.2 est une table markdown " | <kind> | <libelle> | ... ".
    section = re.search(
        r"###\s*3\.2\s*Kinds Buzz operationnels(.*?)(?:\n###|\n---|\Z)",
        prd_text,
        re.DOTALL,
    )
    if not section:
        return None
    result: dict[int, str] = {}
    row_pattern = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
    for row in row_pattern.finditer(section.group(1)):
        kind = int(row.group(1))
        label = row.group(2).strip()
        result[kind] = label
    return result or None


# -- Logique de health-check ---------------------------------------------------

def check_schema(report: HealthReport, schema_text: str) -> None:
    """Valide la presence des tables core et de leurs colonnes critiques.

    Args:
        report: Rapport a muter (erreurs/tables_checked/missing_tables).
        schema_text: Contenu du ``schema.sql``.
    """
    tables = parse_sql_tables(schema_text)

    for logical, expected_cols in EXPECTED_CORE_TABLES.items():
        real_name = TABLE_ALIASES.get(logical, logical)
        if real_name in tables:
            report.tables_checked[logical] = True
            present = tables[real_name]
            missing_cols = [c for c in expected_cols if c.lower() not in present]
            if missing_cols:
                report.warnings.append(
                    f"Table '{real_name}' presente mais colonnes critiques "
                    f"manquantes : {', '.join(missing_cols)}"
                )
        else:
            report.tables_checked[logical] = False
            report.missing_tables.append(real_name)

    # Presence/typing sont Redis (PRD S2.1) -> pas en Postgres.
    report.warnings.append(
        "Kinds presence (20001) et typing (20002) : stockage Redis attendu "
        "(pub/sub), non present en Postgres - conforme au PRD S2.1."
    )


def check_kinds(report: HealthReport, kindrs_text: Optional[str], prd_kinds: dict[int, str]) -> None:
    """Compare les kinds du PRD avec le registre ``kind.rs``.

    Args:
        report: Rapport a muter (kinds_* / warnings).
        kindrs_text: Contenu de ``kind.rs`` ou ``None`` si illisible.
        prd_kinds: Kinds operationnels declares dans le PRD.
    """
    report.kinds_prd = sorted(prd_kinds.keys())

    if kindrs_text is None:
        report.warnings.append(
            "buzz-core/src/kind.rs illisible ou non fourni - "
            "couverture des kinds non verifiee."
        )
        report.kinds_uncovered = report.kinds_prd
        return

    registered = parse_kind_constants(kindrs_text)
    for kind in report.kinds_prd:
        if kind in registered:
            report.kinds_covered.append(kind)
        else:
            report.kinds_uncovered.append(kind)

    # Kinds ephemeres Redis absents de kind.rs en tant que stockes = normal.
    for kind in list(report.kinds_uncovered):
        if kind in REDIS_BACKED_KINDS:
            report.kinds_uncovered.remove(kind)
            report.warnings.append(
                f"Kind {kind} ({prd_kinds[kind]}) : ephemere Redis, "
                "non stocke en Postgres - absence dans kind.rs non bloquante."
            )

    if report.kinds_uncovered:
        uncovered_labels = ", ".join(
            f"{k} ({prd_kinds[k]})" for k in report.kinds_uncovered
        )
        report.warnings.append(
            f"Kinds PRD non couverts par kind.rs : {uncovered_labels}"
        )


# -- Rendu des rapports --------------------------------------------------------

def render_json(report: HealthReport) -> str:
    """Serialise le rapport au format JSON."""
    payload = {
        "healthy": report.healthy,
        "schema_path": report.schema_path,
        "kindrs_path": report.kindrs_path,
        "prd_path": report.prd_path,
        "tables": {
            "checked": report.tables_checked,
            "missing": report.missing_tables,
        },
        "kinds": {
            "prd_total": len(report.kinds_prd),
            "covered": report.kinds_covered,
            "uncovered": report.kinds_uncovered,
            "coverage_pct": (
                round(100.0 * len(report.kinds_covered) / len(report.kinds_prd), 1)
                if report.kinds_prd else 0.0
            ),
        },
        "warnings": report.warnings,
        "errors": report.errors,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def render_markdown(report: HealthReport) -> str:
    """Serialise le rapport au format Markdown lisible."""
    status = "[OK] SAIN" if report.healthy else "[WARN] DEGRADE"
    lines: list[str] = []
    lines.append("# Rapport de sante - Bus Buzz (coherence locale)\n")
    lines.append(f"**Statut global** : {status}\n")
    lines.append(f"- Schema : `{report.schema_path}`")
    lines.append(f"- kind.rs : `{report.kindrs_path or 'N/A'}`")
    lines.append(f"- PRD : `{report.prd_path or 'N/A'}`\n")

    lines.append("## Tables core (PRD S2.1 / S3.1)\n")
    if report.tables_checked:
        lines.append("| Table logique | Presente |")
        lines.append("|---|---|")
        for name, ok in report.tables_checked.items():
            lines.append(f"| {name} | {'[OK]' if ok else '[X]'} |")
    if report.missing_tables:
        lines.append(f"\n**Tables manquantes** : {', '.join(report.missing_tables)}")
    lines.append("")

    lines.append("## Kinds operationnels (PRD S3.2)\n")
    total = len(report.kinds_prd) or 1
    cov = round(100.0 * len(report.kinds_covered) / total, 1)
    lines.append(f"- Total kinds PRD : **{len(report.kinds_prd)}**")
    lines.append(f"- Couverts par `kind.rs` : **{len(report.kinds_covered)}** ({cov} %)")

    lines.append("\n### Kinds couverts\n")
    if report.kinds_covered:
        for k in report.kinds_covered:
            lines.append(f"- `{k}` - {PRD_KINDS.get(k, 'kind PRD')}")
    else:
        lines.append("_Aucun kinds couvert (kind.rs non fourni)._")

    lines.append("\n### Kinds non couverts\n")
    if report.kinds_uncovered:
        for k in report.kinds_uncovered:
            lines.append(f"- `{k}` - {PRD_KINDS.get(k, 'kind PRD')}")
    else:
        lines.append("_Tous les kinds operationnels du PRD sont couverts._")
    lines.append("")

    # Section TRIX/KIX proposes
    lines.append("## Kinds proposes (TRIX/KIX - PRD v1.1)\n")
    lines.append("_Ces kinds ne sont pas encore deployes. Ils necessitent des ADR dedies._\n")
    lines.append("| Kind | Libelle | Statut | ADR associe |")
    lines.append("|------|---------|--------|-------------|")
    lines.append("| 50001 | TRIX governance event | PROPOSED | ADR-TRIX-GOVERNANCE |")
    lines.append("| 50002 | TRIX arbiter lock | PROPOSED | ADR-TRIX-ARBITER |")
    lines.append("| 60001 | KIX runner lifecycle | PROPOSED | ADR-KIX-LIFECYCLE |")
    lines.append("")

    lines.append("## Avertissements\n")
    if report.warnings:
        for w in report.warnings:
            lines.append(f"- {w}")
    else:
        lines.append("_Aucun._")

    lines.append("\n## Erreurs bloquantes\n")
    if report.errors:
        for e in report.errors:
            lines.append(f"- {e}")
    else:
        lines.append("_Aucune._")

    return "\n".join(lines) + "\n"


# -- Point d'entree ------------------------------------------------------------

def build_default_paths(buzzblock: Path) -> tuple[Path, Path, Path]:
    """Construit les chemins par defaut Buzz@block depuis un repertoire racine.

    Args:
        buzzblock: Repertoire racine ``Buzz@block``.

    Returns:
        Tuple ``(schema.sql, kind.rs, PRD MOC)``.
    """
    schema = buzzblock / "schema" / "schema.sql"
    kindrs = buzzblock / "crates" / "buzz-core" / "src" / "kind.rs"
    # Le PRD vit dans BUZZ-X/PRD-MOC (remonte d'un niveau depuis Buzz@block).
    prd = buzzblock.parent / "PRD-MOC" / "PRD-MOC-BUZZ-X-BUS-2026-08-17.md"
    return schema, kindrs, prd


def main(argv: Optional[list[str]] = None) -> int:
    """CLI principal du health-check.

    Args:
        argv: Arguments de ligne de commande (defaut : ``sys.argv[1:]``).

    Returns:
        Code de sortie (0 = sain, 1 = degrade/erreurs).
    """
    parser = argparse.ArgumentParser(
        prog="buzz_bus_health",
        description="Health-check local de coherence du bus Buzz (sans reseau).",
    )
    parser.add_argument("--schema", type=Path, help="Chemin vers schema/schema.sql")
    parser.add_argument("--kindrs", type=Path, help="Chemin vers buzz-core/src/kind.rs")
    parser.add_argument("--prd", type=Path, help="Chemin vers le PRD MOC Buzz")
    parser.add_argument(
        "--buzzblock", type=Path,
        help="Repertoire racine Buzz@block (deduit les chemins par defaut)",
    )
    parser.add_argument(
        "--out", choices=["json", "md"], default="md",
        help="Format de sortie (defaut : md)",
    )
    parser.add_argument("--quiet", action="store_true", help="Supprime la sortie stdout")
    args = parser.parse_args(argv)

    # Resolution des chemins.
    # BUZZ-X repo root = parents[4] depuis scripts/ (scripts -> worktree ->
    # .kilo -> worktrees -> BUZZ-X). Buzz@block et PRD-MOC y sont inclus.
    buzzblock_root = Path(__file__).resolve().parents[4]
    buzzblock = args.buzzblock or buzzblock_root / "Buzz@block"
    default_schema, default_kindrs, default_prd = build_default_paths(buzzblock)
    schema_path = args.schema or default_schema
    kindrs_path = args.kindrs or default_kindrs
    prd_path = args.prd or default_prd

    report = HealthReport(
        schema_path=str(schema_path),
        kindrs_path=str(kindrs_path) if kindrs_path.exists() else None,
        prd_path=str(prd_path) if prd_path.exists() else None,
    )

    # Lecture schema.sql.
    if not schema_path.exists():
        report.errors.append(f"Schema introuvable : {schema_path}")
    else:
        schema_text = schema_path.read_text(encoding="utf-8", errors="replace")
        check_schema(report, schema_text)

    # Lecture kind.rs (optionnel mais recommande).
    kindrs_text: Optional[str] = None
    if kindrs_path.exists():
        kindrs_text = kindrs_path.read_text(encoding="utf-8", errors="replace")

    # Lecture PRD (kinds operationnels).
    prd_kinds: dict[int, str] = dict(PRD_KINDS)
    if prd_path.exists():
        prd_text = prd_path.read_text(encoding="utf-8", errors="replace")
        parsed = parse_prd_kinds(prd_text)
        if parsed:
            prd_kinds = parsed
    else:
        report.warnings.append(
            "PRD MOC non trouve - utilisation de la liste statique des kinds S3.2."
        )

    check_kinds(report, kindrs_text, prd_kinds)

    # Rendu.
    output = render_json(report) if args.out == "json" else render_markdown(report)
    if not args.quiet:
        # Re-encode la sortie stdout en UTF-8 pour eviter les erreurs
        # d'encodage console (emoji) sous Windows (cp1252).
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        print(output)

    return 0 if report.healthy else 1


if __name__ == "__main__":
    sys.exit(main())
