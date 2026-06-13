#!/usr/bin/env python3
"""
lint.py — mechanical validation for an llm-wiki.

Walks atoms/, parses YAML frontmatter, applies the rules from
reference/lint.md. Returns a structured report and an exit code that
/llm-wiki compile uses to decide whether to refuse running.

Pure stdlib. Cross-platform.

Exit codes:
  0 — no critical errors. Warnings allowed.
  1 — at least one critical error. Compile must refuse to run.
  2 — lint itself failed (wiki not found, IO error).

Usage:
  python lint.py [WIKI_ROOT] [options]

If WIKI_ROOT is omitted, walks up from cwd looking for a wiki (schema.md +
atoms/ present), then falls back to LLM_WIKI_ROOT env var.

Options:
  --json                 Emit a single JSON object instead of human text.
  --save                 Write the report to wiki/_meta/lint-YYYY-MM-DD.md.
  --verbose              Show every finding, no truncation.
  --severity {critical,warning,all}
                         Filter output to a single severity (all by default).
  --branch BRANCH        Lint only this branch.
  --no-wikilinks         Skip wikilink resolution checks (faster).
  --strict               Promote all warnings to critical.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


# ---- Schema constants ----------------------------------------------------

BRANCHES = {'people', 'process', 'policy', 'platform', 'product', 'meta'}
STATUSES = {'current', 'draft', 'superseded', 'disputed', 'archived'}
AUTHORS = {'extract', 'human', 'synthesis'}
ATOM_ID_RE = re.compile(r'^atom-\d{8}-\d{3}$')
ATOM_REQUIRED_FIELDS = ['id', 'claim', 'branch', 'date', 'author', 'confidence', 'status']

WIKILINK_RE = re.compile(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]')
MD_LINK_RE = re.compile(r'\[([^\]]+?)\]\(([^)]+?)\)')
FRONTMATTER_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\s*\r?\n', re.DOTALL)


# ---- Findings ------------------------------------------------------------

@dataclass
class Finding:
    severity: str          # 'critical' | 'warning'
    file: str              # path relative to wiki root
    rule: str              # short rule slug
    message: str
    line: Optional[int] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# ---- Frontmatter parser --------------------------------------------------

def parse_frontmatter(content: str) -> tuple[Optional[dict], Optional[str]]:
    """Extract the YAML frontmatter block. Returns (parsed_dict, error_msg).

    Hand-rolled parser for the subset we use: scalar strings, ints, floats,
    nulls, inline lists, and block-style lists. Does not handle nested
    objects (we don't use them).
    """
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None, None  # No frontmatter at all — caller decides if that's an error.

    block = match.group(1)
    result: dict[str, Any] = {}
    lines = block.split('\n')
    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            i += 1
            continue

        if ':' not in line:
            return None, f'malformed frontmatter line: {raw_line!r}'

        # Allow indented continuation lines (rare in our schema, but tolerate)
        key, _, raw_value = line.partition(':')
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value == '':
            # Look ahead for block-list items
            items: list[Any] = []
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith('-'):
                item_str = lines[j].lstrip()[1:].strip()
                items.append(parse_scalar(item_str))
                j += 1
            if items:
                result[key] = items
                i = j
                continue
            result[key] = None
            i += 1
            continue

        result[key] = parse_value(raw_value)
        i += 1

    return result, None


def parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw == '' or raw.lower() in ('null', '~'):
        return None
    if raw.lower() == 'true':
        return True
    if raw.lower() == 'false':
        return False
    if raw.startswith('[') and raw.endswith(']'):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in split_list_items(inner)]
    return parse_scalar(raw)


def parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        return ''
    # Quoted string
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    # null / bool
    if raw.lower() in ('null', '~'):
        return None
    if raw.lower() == 'true':
        return True
    if raw.lower() == 'false':
        return False
    # int
    if re.fullmatch(r'-?\d+', raw):
        return int(raw)
    # float
    if re.fullmatch(r'-?\d+\.\d+', raw):
        return float(raw)
    return raw


def split_list_items(inner: str) -> list[str]:
    """Split an inline list like 'a, "b, c", d' respecting quoted strings."""
    items: list[str] = []
    buf: list[str] = []
    in_quote: Optional[str] = None
    for char in inner:
        if in_quote:
            buf.append(char)
            if char == in_quote:
                in_quote = None
            continue
        if char in ('"', "'"):
            in_quote = char
            buf.append(char)
            continue
        if char == ',':
            items.append(''.join(buf).strip())
            buf = []
            continue
        buf.append(char)
    last = ''.join(buf).strip()
    if last:
        items.append(last)
    return items


# ---- Wiki root resolution ------------------------------------------------

def find_wiki_root(start: Path) -> Optional[Path]:
    # 1. Env override
    env_root = os.environ.get('LLM_WIKI_ROOT')
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if looks_like_wiki(candidate):
            return candidate

    # 2. cwd is the wiki root
    if looks_like_wiki(start):
        return start

    # 3. Walk up looking for a sibling llm-wiki/
    current = start.resolve()
    while True:
        sibling = current / '_llm-wiki'
        if looks_like_wiki(sibling):
            return sibling
        parent = current.parent
        if parent == current:
            break
        current = parent

    # 4. Portfolio default ~/Projects/_llm-wiki
    portfolio = Path.home() / 'Projects' / '_llm-wiki'
    if looks_like_wiki(portfolio):
        return portfolio

    return None


def looks_like_wiki(path: Path) -> bool:
    return path.is_dir() and (path / 'schema.md').exists() and (path / 'atoms').is_dir()


# ---- Registry ------------------------------------------------------------

@dataclass
class AtomRecord:
    path: Path
    rel_path: str
    branch_from_folder: str
    frontmatter: dict
    body: str
    wikilinks: list[str] = field(default_factory=list)
    md_links: list[tuple[str, str]] = field(default_factory=list)
    parse_error: Optional[str] = None


class Registry:
    """Loaded state of the wiki for the duration of a lint run."""

    def __init__(self, wiki_root: Path):
        self.wiki_root = wiki_root
        self.atoms: dict[str, AtomRecord] = {}        # by atom id
        self.atoms_by_path: dict[Path, AtomRecord] = {}
        self.atom_files_parsed: list[AtomRecord] = []  # includes those without valid id
        self.wiki_pages: dict[str, Path] = {}          # by relative path (no .md), e.g. 'wiki/process/foo'
        self.raw_files: set[str] = set()               # relative paths under raw/
        self.atoms_referenced_by_pages: set[str] = set()  # atom ids appearing in wiki page frontmatter

    def load(self) -> list[Finding]:
        findings: list[Finding] = []
        findings.extend(self._load_atoms())
        findings.extend(self._load_wiki_pages())
        self._load_raw_files()
        return findings

    def _load_atoms(self) -> list[Finding]:
        findings: list[Finding] = []
        atoms_dir = self.wiki_root / 'atoms'
        if not atoms_dir.exists():
            return findings

        for branch_dir in sorted(atoms_dir.iterdir()):
            if not branch_dir.is_dir():
                continue
            branch_name = branch_dir.name
            if branch_name.startswith('_') or branch_name.startswith('.'):
                continue
            for md_file in sorted(branch_dir.glob('*.md')):
                if md_file.name.startswith('_'):
                    continue
                rec = self._read_atom(md_file, branch_name)
                if rec.parse_error:
                    findings.append(Finding(
                        severity='critical',
                        file=rec.rel_path,
                        rule='frontmatter-parse',
                        message=f'Cannot parse frontmatter: {rec.parse_error}',
                    ))
                self.atom_files_parsed.append(rec)
                self.atoms_by_path[md_file] = rec
                atom_id = rec.frontmatter.get('id')
                if isinstance(atom_id, str):
                    if atom_id in self.atoms:
                        findings.append(Finding(
                            severity='critical',
                            file=rec.rel_path,
                            rule='duplicate-id',
                            message=f'Atom id {atom_id!r} already used by {self.atoms[atom_id].rel_path}',
                        ))
                    else:
                        self.atoms[atom_id] = rec
        return findings

    def _read_atom(self, path: Path, branch_from_folder: str) -> AtomRecord:
        rel = str(path.relative_to(self.wiki_root)).replace(os.sep, '/')
        try:
            text = path.read_text(encoding='utf-8')
        except OSError as exc:
            return AtomRecord(
                path=path, rel_path=rel, branch_from_folder=branch_from_folder,
                frontmatter={}, body='', parse_error=str(exc),
            )

        fm, parse_err = parse_frontmatter(text)
        body = FRONTMATTER_RE.sub('', text, count=1) if fm is not None else text
        wikilinks = WIKILINK_RE.findall(body)
        md_links = MD_LINK_RE.findall(body)

        return AtomRecord(
            path=path, rel_path=rel, branch_from_folder=branch_from_folder,
            frontmatter=fm or {}, body=body,
            wikilinks=wikilinks, md_links=md_links,
            parse_error=parse_err if fm is None and parse_err else parse_err,
        )

    def _load_wiki_pages(self) -> list[Finding]:
        findings: list[Finding] = []
        wiki_dir = self.wiki_root / 'wiki'
        if not wiki_dir.exists():
            return findings

        for md_file in wiki_dir.rglob('*.md'):
            if md_file.name.startswith('_'):
                continue
            rel = str(md_file.relative_to(self.wiki_root)).replace(os.sep, '/')
            key = rel[:-3]  # drop .md
            self.wiki_pages[key] = md_file

            # Read frontmatter to harvest atoms list for orphan detection
            try:
                text = md_file.read_text(encoding='utf-8')
            except OSError:
                continue
            fm, _err = parse_frontmatter(text)
            if not fm:
                continue
            atom_refs = fm.get('atoms')
            if isinstance(atom_refs, list):
                for ref in atom_refs:
                    if isinstance(ref, str):
                        self.atoms_referenced_by_pages.add(ref)
        return findings

    def _load_raw_files(self) -> None:
        raw_dir = self.wiki_root / 'raw'
        if not raw_dir.exists():
            return
        for entry in raw_dir.rglob('*'):
            if not entry.is_file():
                continue
            rel = str(entry.relative_to(self.wiki_root)).replace(os.sep, '/')
            # Skip the provenance file itself and any assets directory; assets are tracked separately
            if rel == 'raw/_provenance.md':
                continue
            if rel.startswith('raw/assets/'):
                continue
            self.raw_files.add(rel)


# ---- Checks --------------------------------------------------------------

def check_frontmatter(registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for rec in registry.atom_files_parsed:
        if rec.parse_error:
            continue  # already reported during load
        fm = rec.frontmatter

        # Required fields
        for required in ATOM_REQUIRED_FIELDS:
            if required not in fm or fm[required] is None:
                findings.append(Finding(
                    severity='critical', file=rec.rel_path,
                    rule='missing-field',
                    message=f'Missing required field: {required}',
                ))

        # id format
        atom_id = fm.get('id')
        if isinstance(atom_id, str) and not ATOM_ID_RE.match(atom_id):
            findings.append(Finding(
                severity='critical', file=rec.rel_path,
                rule='invalid-id-format',
                message=f'Atom id {atom_id!r} does not match atom-YYYYMMDD-NNN',
            ))

        # branch
        branch = fm.get('branch')
        if branch is not None and branch not in BRANCHES:
            findings.append(Finding(
                severity='critical', file=rec.rel_path,
                rule='invalid-branch',
                message=f'Invalid branch: {branch!r} (expected one of: {", ".join(sorted(BRANCHES))})',
            ))

        # branch / folder match
        if isinstance(branch, str) and branch != rec.branch_from_folder:
            findings.append(Finding(
                severity='critical', file=rec.rel_path,
                rule='branch-folder-mismatch',
                message=f'Frontmatter branch ({branch!r}) does not match folder ({rec.branch_from_folder!r})',
            ))

        # confidence
        confidence = fm.get('confidence')
        if confidence is not None:
            if not isinstance(confidence, (int, float)):
                findings.append(Finding(
                    severity='critical', file=rec.rel_path,
                    rule='invalid-confidence-type',
                    message=f'confidence must be a number, got {type(confidence).__name__}: {confidence!r}',
                ))
            elif not 0.0 <= float(confidence) <= 1.0:
                findings.append(Finding(
                    severity='critical', file=rec.rel_path,
                    rule='confidence-out-of-range',
                    message=f'confidence must be in [0.0, 1.0], got {confidence}',
                ))

        # status
        status = fm.get('status')
        if status is not None and status not in STATUSES:
            findings.append(Finding(
                severity='critical', file=rec.rel_path,
                rule='invalid-status',
                message=f'Invalid status: {status!r} (expected one of: {", ".join(sorted(STATUSES))})',
            ))

        # author
        author = fm.get('author')
        if author is not None and author not in AUTHORS:
            findings.append(Finding(
                severity='warning', file=rec.rel_path,
                rule='unknown-author',
                message=f'Unknown author: {author!r} (expected one of: {", ".join(sorted(AUTHORS))})',
            ))

        # date
        date_value = fm.get('date')
        if isinstance(date_value, str) and not _is_iso_date(date_value):
            findings.append(Finding(
                severity='critical', file=rec.rel_path,
                rule='invalid-date',
                message=f'date is not a valid ISO date (YYYY-MM-DD): {date_value!r}',
            ))
        elif isinstance(date_value, date):
            pass  # Already parsed by YAML — accept it.

    return findings


def check_sourcing(registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for rec in registry.atom_files_parsed:
        if rec.parse_error:
            continue
        fm = rec.frontmatter
        branch = fm.get('branch')
        sources = fm.get('sources') or []

        # Empty sources on non-meta atoms
        if branch != 'meta' and not sources:
            findings.append(Finding(
                severity='critical', file=rec.rel_path,
                rule='no-sources',
                message='Atom has no `sources:` entries (only `branch: meta` atoms may omit sources)',
            ))

        # Source files must exist
        if isinstance(sources, list):
            for src in sources:
                if not isinstance(src, str):
                    continue
                src_path = src if src.startswith('raw/') else f'raw/{src}'
                if src_path not in registry.raw_files:
                    findings.append(Finding(
                        severity='critical', file=rec.rel_path,
                        rule='missing-source',
                        message=f'sources references nonexistent file: {src_path}',
                    ))
    return findings


def check_supersession(registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for rec in registry.atom_files_parsed:
        if rec.parse_error:
            continue
        fm = rec.frontmatter
        status = fm.get('status')
        sup_by = fm.get('superseded-by')

        if status == 'superseded':
            if not sup_by:
                findings.append(Finding(
                    severity='critical', file=rec.rel_path,
                    rule='missing-superseded-by',
                    message='Atom has status: superseded but no superseded-by reference',
                ))
            elif isinstance(sup_by, str):
                if sup_by not in registry.atoms:
                    findings.append(Finding(
                        severity='critical', file=rec.rel_path,
                        rule='broken-superseded-by',
                        message=f'superseded-by points to nonexistent atom: {sup_by}',
                    ))
                else:
                    target = registry.atoms[sup_by]
                    if target.frontmatter.get('status') == 'superseded':
                        findings.append(Finding(
                            severity='warning', file=rec.rel_path,
                            rule='superseded-chain',
                            message=f'superseded-by points to another superseded atom ({sup_by}). Chains should be flat.',
                        ))
        elif sup_by:
            findings.append(Finding(
                severity='warning', file=rec.rel_path,
                rule='superseded-by-on-active',
                message=f'Atom has superseded-by but status is {status!r} (expected superseded)',
            ))
    return findings


def check_contradictions(registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for rec in registry.atom_files_parsed:
        if rec.parse_error:
            continue
        fm = rec.frontmatter
        atom_id = fm.get('id')
        if not isinstance(atom_id, str):
            continue

        contradicts = fm.get('contradicts') or []
        status = fm.get('status')

        if status == 'disputed' and not contradicts:
            findings.append(Finding(
                severity='warning', file=rec.rel_path,
                rule='disputed-without-contradicts',
                message='Atom has status: disputed but no contradicts list',
            ))

        if isinstance(contradicts, list):
            for other_id in contradicts:
                if not isinstance(other_id, str):
                    continue
                if other_id not in registry.atoms:
                    findings.append(Finding(
                        severity='warning', file=rec.rel_path,
                        rule='broken-contradicts',
                        message=f'contradicts references nonexistent atom: {other_id}',
                    ))
                    continue
                other = registry.atoms[other_id]
                other_contradicts = other.frontmatter.get('contradicts') or []
                if not (isinstance(other_contradicts, list) and atom_id in other_contradicts):
                    findings.append(Finding(
                        severity='warning', file=rec.rel_path,
                        rule='contradicts-not-bidirectional',
                        message=f'Atom contradicts {other_id} but {other_id} does not reciprocate',
                    ))
    return findings


def check_confidence_status(registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for rec in registry.atom_files_parsed:
        if rec.parse_error:
            continue
        fm = rec.frontmatter
        status = fm.get('status')
        confidence = fm.get('confidence')
        if status == 'current' and isinstance(confidence, (int, float)) and float(confidence) < 0.6:
            findings.append(Finding(
                severity='warning', file=rec.rel_path,
                rule='low-confidence-current',
                message=f'status: current with confidence {confidence} (< 0.6). Promote evidence or demote to draft.',
            ))

        if status == 'draft':
            atom_date = fm.get('date')
            if isinstance(atom_date, str) and _is_iso_date(atom_date):
                created = datetime.strptime(atom_date, '%Y-%m-%d').date()
                age_days = (date.today() - created).days
                if age_days > 30:
                    findings.append(Finding(
                        severity='warning', file=rec.rel_path,
                        rule='stale-draft',
                        message=f'Draft atom is {age_days} days old. Promote or archive.',
                    ))
    return findings


def check_wikilinks(registry: Registry, raw_files: Optional[set[str]] = None) -> list[Finding]:
    findings: list[Finding] = []
    raw_files = raw_files if raw_files is not None else registry.raw_files

    # Lint atoms' wikilinks
    for rec in registry.atom_files_parsed:
        for link in rec.wikilinks:
            target = link.split('#', 1)[0].strip()  # strip anchors
            if not target:
                continue
            severity = _classify_wikilink(target, registry, raw_files)
            if severity:
                findings.append(Finding(
                    severity=severity[0], file=rec.rel_path,
                    rule=severity[1],
                    message=f'Wikilink target does not resolve: [[{link}]]',
                ))

        # Plain markdown links to wiki-internal files
        for label, url in rec.md_links:
            if _is_wiki_internal_md_link(url):
                findings.append(Finding(
                    severity='warning', file=rec.rel_path,
                    rule='md-link-to-wiki-content',
                    message=f'Plain markdown link to wiki content (use a wikilink): [{label}]({url})',
                ))
    return findings


def _classify_wikilink(target: str, registry: Registry, raw_files: set[str]) -> Optional[tuple[str, str]]:
    """Return (severity, rule) if link is broken; None if it resolves."""
    # atom-YYYYMMDD-NNN
    if target.startswith('atom-') and ATOM_ID_RE.match(target):
        if target not in registry.atoms:
            return ('warning', 'broken-atom-link')
        return None

    # wiki/...
    if target.startswith('wiki/'):
        key = target if not target.endswith('.md') else target[:-3]
        if key not in registry.wiki_pages:
            return ('warning', 'broken-wiki-link')
        return None

    # raw/...
    if target.startswith('raw/'):
        target_norm = target if target.endswith(tuple(['.md', '.pdf', '.docx', '.pptx', '.xlsx', '.html', '.htm', '.txt', '.csv', '.json', '.yaml', '.yml', '.svg', '.png', '.jpg', '.jpeg'])) or '.' in target.split('/')[-1] else f'{target}.md'
        if target_norm not in raw_files:
            return ('warning', 'broken-raw-link')
        return None

    # Cross-wiki — best-effort. We don't validate across vault boundaries.
    if target.startswith('../') or '/' in target:
        return None

    # Bare names — ambiguous. Flag as warning (Obsidian resolves them, lint can't reliably).
    return None


def _is_wiki_internal_md_link(url: str) -> bool:
    if url.startswith(('http://', 'https://', 'mailto:', 'ftp://', '#')):
        return False
    return any(url.startswith(prefix) or f'/{prefix}' in url for prefix in ('atoms/', 'wiki/', 'raw/'))


def check_orphans(registry: Registry) -> list[Finding]:
    """An orphan atom is not referenced by any wiki page AND not linked from any other atom."""
    findings: list[Finding] = []
    linked_from_atoms: set[str] = set()
    for rec in registry.atom_files_parsed:
        for link in rec.wikilinks:
            target = link.split('#', 1)[0].strip()
            if ATOM_ID_RE.match(target):
                linked_from_atoms.add(target)
        for other_id in (rec.frontmatter.get('reinforced-by') or []):
            if isinstance(other_id, str):
                linked_from_atoms.add(other_id)
        for other_id in (rec.frontmatter.get('contradicts') or []):
            if isinstance(other_id, str):
                linked_from_atoms.add(other_id)
        for other_id in (rec.frontmatter.get('compile-to') or []):
            if isinstance(other_id, str):
                pass  # compile-to is a wiki page target, not an atom — irrelevant here

    for atom_id, rec in registry.atoms.items():
        fm = rec.frontmatter
        if fm.get('status') in ('archived', 'superseded'):
            continue
        if atom_id in linked_from_atoms or atom_id in registry.atoms_referenced_by_pages:
            continue
        if fm.get('compile-to'):
            continue
        findings.append(Finding(
            severity='warning', file=rec.rel_path,
            rule='orphan-atom',
            message='Atom is not referenced by any wiki page, not linked from any other atom, and has no compile-to target',
        ))
    return findings


def check_filename_hygiene(registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for rec in registry.atom_files_parsed:
        name = rec.path.stem
        if ' ' in name:
            findings.append(Finding(
                severity='warning', file=rec.rel_path,
                rule='filename-has-spaces',
                message='Filename contains spaces; use kebab-case',
            ))
        if any(c.isupper() for c in name):
            findings.append(Finding(
                severity='warning', file=rec.rel_path,
                rule='filename-has-uppercase',
                message='Filename contains uppercase letters; use lowercase kebab-case',
            ))
        if len(name) > 60:
            findings.append(Finding(
                severity='warning', file=rec.rel_path,
                rule='filename-too-long',
                message=f'Filename is {len(name)} characters (max 60)',
            ))
    return findings


def check_raw_orphans(registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    cited_sources: set[str] = set()
    for rec in registry.atom_files_parsed:
        for src in (rec.frontmatter.get('sources') or []):
            if not isinstance(src, str):
                continue
            cited_sources.add(src if src.startswith('raw/') else f'raw/{src}')

    for raw_path in sorted(registry.raw_files):
        if raw_path not in cited_sources:
            findings.append(Finding(
                severity='warning', file=raw_path,
                rule='raw-orphan',
                message='Raw file is not cited by any atom (ingest it or remove)',
            ))
    return findings


# ---- Helpers -------------------------------------------------------------

def _is_iso_date(text: str) -> bool:
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        return False
    try:
        datetime.strptime(text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# ---- Output --------------------------------------------------------------

def render_human(findings: list[Finding], registry: Registry, verbose: bool,
                 severity_filter: str, blocked: bool) -> str:
    crit = [f for f in findings if f.severity == 'critical']
    warn = [f for f in findings if f.severity == 'warning']

    out: list[str] = []
    out.append(f'LLM-Wiki Lint Report — {date.today().isoformat()}')
    out.append(f'Path: {registry.wiki_root}')
    out.append('')
    out.append('Scanned:')
    out.append(f'  Atoms:      {len(registry.atom_files_parsed)}')
    out.append(f'  Wiki pages: {len(registry.wiki_pages)}')
    out.append(f'  Raw files:  {len(registry.raw_files)}')
    out.append('')

    show_crit = severity_filter in ('critical', 'all')
    show_warn = severity_filter in ('warning', 'all')

    if show_crit:
        out.append(f'[CRITICAL] {len(crit)} issues across {len(set(f.file for f in crit))} files')
        if crit:
            out.append('')
            for finding in _truncate(crit, verbose):
                out.append(f'  {finding.file}')
                out.append(f'    - [{finding.rule}] {finding.message}')
            if not verbose and len(crit) > 20:
                out.append(f'  ... and {len(crit) - 20} more (use --verbose to see all)')
        out.append('')

    if show_warn:
        out.append(f'[WARNING] {len(warn)} issues across {len(set(f.file for f in warn))} files')
        if warn:
            out.append('')
            for finding in _truncate(warn, verbose):
                out.append(f'  {finding.file}')
                out.append(f'    - [{finding.rule}] {finding.message}')
            if not verbose and len(warn) > 20:
                out.append(f'  ... and {len(warn) - 20} more (use --verbose to see all)')
        out.append('')

    out.append(f'Compile: {"BLOCKED (critical errors present)" if blocked else "OK"}')

    if blocked:
        out.append('')
        out.append('Recommended actions:')
        out.append('  1. Fix critical errors above — they block compile.')
        out.append('  2. Re-run /llm-wiki lint to confirm clean state.')
        out.append('  3. Then /llm-wiki compile.')

    return '\n'.join(out)


def _truncate(findings: Iterable[Finding], verbose: bool, cap: int = 20) -> Iterable[Finding]:
    if verbose:
        return findings
    return list(findings)[:cap]


def render_json(findings: list[Finding], registry: Registry, blocked: bool) -> str:
    payload = {
        'wiki': str(registry.wiki_root),
        'ranAt': datetime.now(timezone.utc).isoformat(),
        'scanned': {
            'atoms': len(registry.atom_files_parsed),
            'wiki': len(registry.wiki_pages),
            'raw': len(registry.raw_files),
        },
        'critical': [f.to_dict() for f in findings if f.severity == 'critical'],
        'warnings': [f.to_dict() for f in findings if f.severity == 'warning'],
        'summary': {
            'criticalCount': sum(1 for f in findings if f.severity == 'critical'),
            'warningCount': sum(1 for f in findings if f.severity == 'warning'),
            'criticalFiles': len({f.file for f in findings if f.severity == 'critical'}),
            'warningFiles': len({f.file for f in findings if f.severity == 'warning'}),
            'compileBlocked': blocked,
        },
    }
    return json.dumps(payload, indent=2)


# ---- Main ----------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('wiki_root', nargs='?', default=None, help='Wiki root (defaults to walk-up resolution)')
    parser.add_argument('--json', action='store_true', dest='json_out')
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--severity', choices=['critical', 'warning', 'all'], default='all')
    parser.add_argument('--branch', default=None, help='Limit lint to a single branch')
    parser.add_argument('--no-wikilinks', action='store_true')
    parser.add_argument('--strict', action='store_true', help='Promote all warnings to critical')
    args = parser.parse_args()

    # Resolve wiki root
    start = Path(args.wiki_root).expanduser().resolve() if args.wiki_root else Path.cwd()
    if args.wiki_root and looks_like_wiki(start):
        wiki_root = start
    else:
        wiki_root = find_wiki_root(start)
    if wiki_root is None:
        sys.stderr.write('Could not find a wiki root. Tried: cwd, walk-up, LLM_WIKI_ROOT, ~/Projects/_llm-wiki/\n')
        sys.stderr.write('Pass the wiki path explicitly: python lint.py /path/to/_llm-wiki\n')
        return 2

    # Load
    registry = Registry(wiki_root)
    findings: list[Finding] = []
    try:
        findings.extend(registry.load())
    except OSError as exc:
        sys.stderr.write(f'IO error while loading wiki: {exc}\n')
        return 2

    # Run checks
    findings.extend(check_frontmatter(registry))
    findings.extend(check_sourcing(registry))
    findings.extend(check_supersession(registry))
    findings.extend(check_contradictions(registry))
    findings.extend(check_confidence_status(registry))
    if not args.no_wikilinks:
        findings.extend(check_wikilinks(registry))
    findings.extend(check_orphans(registry))
    findings.extend(check_filename_hygiene(registry))
    findings.extend(check_raw_orphans(registry))

    # Filter by branch
    if args.branch:
        if args.branch not in BRANCHES:
            sys.stderr.write(f'Unknown branch: {args.branch}. Expected one of: {", ".join(sorted(BRANCHES))}\n')
            return 2
        findings = [
            f for f in findings
            if f.file.startswith(f'atoms/{args.branch}/') or f.file.startswith(f'wiki/{args.branch}/')
        ]

    # Strict: promote warnings
    if args.strict:
        findings = [Finding(**{**f.__dict__, 'severity': 'critical'}) if f.severity == 'warning' else f for f in findings]

    blocked = any(f.severity == 'critical' for f in findings)

    # Render
    if args.json_out:
        report = render_json(findings, registry, blocked)
    else:
        report = render_human(findings, registry, args.verbose, args.severity, blocked)

    print(report)

    # Save
    if args.save:
        meta_dir = wiki_root / 'wiki' / '_meta'
        meta_dir.mkdir(parents=True, exist_ok=True)
        out_path = meta_dir / f'lint-{date.today().isoformat()}.md'
        crit_count = sum(1 for f in findings if f.severity == 'critical')
        warn_count = sum(1 for f in findings if f.severity == 'warning')
        out_path.write_text(
            f'---\n'
            f'title: "Lint Report"\n'
            f'type: lint-report\n'
            f'date: {date.today().isoformat()}\n'
            f'critical-count: {crit_count}\n'
            f'warning-count: {warn_count}\n'
            f'compile-blocked: {str(blocked).lower()}\n'
            f'---\n\n'
            f'```\n{report}\n```\n',
            encoding='utf-8',
        )
        sys.stderr.write(f'Saved: {out_path.relative_to(wiki_root)}\n')

    return 1 if blocked else 0


if __name__ == '__main__':
    sys.exit(main())
