#!/usr/bin/env python3
"""
compile.py — regenerate wiki pages from atoms.

Walks atoms/, groups by compile-to target (explicit or inferred), and
writes wiki/<branch-or-page-type>/<page>.md plus index.md and overview.md.

Auto-generated pages carry a frontmatter marker (`type:` + `date-compiled:`).
Pages without that marker are treated as hand-authored and skipped unless
--force is passed.

The compiler is deterministic: same atom state produces byte-identical output
(except when the date rolls over, in which case `date-compiled` updates only
if other content also changed — see _is_content_equivalent below).

Exit codes:
  0 — compiled successfully (or dry-run completed).
  1 — user aborted at the stop gate.
  2 — compile itself failed (wiki not found, IO error, lint criticals present).

Usage:
  python compile.py [WIKI_ROOT] [options]

If WIKI_ROOT is omitted, walks up from cwd or falls back to LLM_WIKI_ROOT
or ~/Projects/_llm-wiki/.

Options:
  --force                Overwrite hand-edited wiki pages (those without
                         the auto-generated frontmatter marker).
  --branch BRANCH        Only compile pages in this branch. Other branches
                         and synthesis/comparisons/queries remain untouched.
  --page PATH            Compile a single page (relative to wiki root,
                         e.g. wiki/process/intake-three-gate-model).
  --dry-run              Show the compile plan, write nothing.
  --yes                  Skip the stop gate (auto-approve).
  --no-drafts            Exclude draft-status atoms from compiled pages.
  --skip-lint            Don't refuse on lint critical errors. Discouraged.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional


# ---- Schema constants (kept in sync with lint.py) ------------------------

BRANCHES = ['people', 'process', 'policy', 'platform', 'product', 'meta']
PAGE_TYPES = ['synthesis', 'comparisons', 'queries']
EXCLUDED_TOP_LEVEL = {'_meta', '_README.md'}   # under wiki/, never touched by compile
ATOM_ID_RE = re.compile(r'^atom-\d{8}-\d{3}$')
FRONTMATTER_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\s*\r?\n', re.DOTALL)
AUTOGEN_TYPES = {'branch-page', 'synthesis', 'comparison', 'query', 'auto-generated'}


# ---- Frontmatter parser (mirrors lint.py — keep in sync) -----------------

def parse_frontmatter(content: str) -> Optional[dict]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None
    block = match.group(1)
    result: dict = {}
    lines = block.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            i += 1
            continue
        if ':' not in line:
            i += 1
            continue
        key, _, raw_value = line.partition(':')
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value == '':
            items: list = []
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith('-'):
                item_str = lines[j].lstrip()[1:].strip()
                items.append(_parse_scalar(item_str))
                j += 1
            if items:
                result[key] = items
                i = j
                continue
            result[key] = None
            i += 1
            continue
        result[key] = _parse_value(raw_value)
        i += 1
    return result


def _parse_value(raw: str):
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
        return [_parse_scalar(item) for item in _split_list(inner)]
    return _parse_scalar(raw)


def _parse_scalar(raw: str):
    raw = raw.strip()
    if not raw:
        return ''
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    if raw.lower() in ('null', '~'):
        return None
    if raw.lower() == 'true':
        return True
    if raw.lower() == 'false':
        return False
    if re.fullmatch(r'-?\d+', raw):
        return int(raw)
    if re.fullmatch(r'-?\d+\.\d+', raw):
        return float(raw)
    return raw


def _split_list(inner: str) -> list[str]:
    items, buf, in_quote = [], [], None
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


# ---- Wiki root resolution (mirrors lint.py + load-wiki.mjs) --------------

def find_wiki_root(start: Path) -> Optional[Path]:
    env_root = os.environ.get('LLM_WIKI_ROOT')
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if _looks_like_wiki(candidate):
            return candidate

    if _looks_like_wiki(start):
        return start

    current = start.resolve()
    while True:
        sibling = current / '_llm-wiki'
        if _looks_like_wiki(sibling):
            return sibling
        parent = current.parent
        if parent == current:
            break
        current = parent

    portfolio = Path.home() / 'Projects' / '_llm-wiki'
    if _looks_like_wiki(portfolio):
        return portfolio
    return None


def _looks_like_wiki(path: Path) -> bool:
    return path.is_dir() and (path / 'schema.md').exists() and (path / 'atoms').is_dir()


# ---- Atom loading --------------------------------------------------------

@dataclass
class Atom:
    id: str
    rel_path: str               # path relative to wiki root, e.g. atoms/process/foo.md
    branch: str                 # frontmatter branch
    folder_branch: str          # folder the file lives in
    claim: str
    confidence: float
    status: str
    date: str
    author: str
    sources: list[str]
    tags: list[str]
    compile_to: Optional[list[str]]  # None if missing, [] if explicitly empty
    contradicts: list[str]
    reinforced_by: list[str]
    superseded_by: Optional[str]
    body: str                   # markdown body sans frontmatter


def load_atoms(wiki_root: Path, include_drafts: bool = True) -> list[Atom]:
    atoms: list[Atom] = []
    atoms_dir = wiki_root / 'atoms'
    if not atoms_dir.exists():
        return atoms

    for branch_dir in sorted(atoms_dir.iterdir()):
        if not branch_dir.is_dir() or branch_dir.name.startswith('_') or branch_dir.name.startswith('.'):
            continue
        folder_branch = branch_dir.name
        for md_file in sorted(branch_dir.glob('*.md')):
            if md_file.name.startswith('_'):
                continue
            try:
                text = md_file.read_text(encoding='utf-8')
            except OSError:
                continue
            fm = parse_frontmatter(text) or {}
            atom_id = fm.get('id')
            if not (isinstance(atom_id, str) and ATOM_ID_RE.match(atom_id)):
                continue  # lint will have flagged this; compile skips silently
            status = fm.get('status') or 'draft'
            if status in ('superseded', 'archived'):
                continue
            if status == 'draft' and not include_drafts:
                continue

            atoms.append(Atom(
                id=atom_id,
                rel_path=str(md_file.relative_to(wiki_root)).replace(os.sep, '/'),
                branch=fm.get('branch') or folder_branch,
                folder_branch=folder_branch,
                claim=str(fm.get('claim') or ''),
                confidence=float(fm.get('confidence') or 0.0),
                status=status,
                date=str(fm.get('date') or ''),
                author=str(fm.get('author') or ''),
                sources=[s for s in (fm.get('sources') or []) if isinstance(s, str)],
                tags=[t for t in (fm.get('tags') or []) if isinstance(t, str)],
                compile_to=fm.get('compile-to'),
                contradicts=[c for c in (fm.get('contradicts') or []) if isinstance(c, str)],
                reinforced_by=[r for r in (fm.get('reinforced-by') or []) if isinstance(r, str)],
                superseded_by=fm.get('superseded-by') if isinstance(fm.get('superseded-by'), str) else None,
                body=FRONTMATTER_RE.sub('', text, count=1),
            ))

    atoms.sort(key=lambda a: a.id)  # deterministic order
    return atoms


# ---- Compile plan --------------------------------------------------------

def determine_targets(atom: Atom) -> list[str]:
    """Return the wiki pages this atom compiles into, without trailing .md."""
    # Explicit compile-to (any non-None value, including the empty list)
    if atom.compile_to is not None:
        if not atom.compile_to:
            return []  # explicit empty → exclude
        return [t.removesuffix('.md') for t in atom.compile_to if isinstance(t, str)]

    # Infer: use first tag, else 'other' within the branch
    if atom.tags:
        slug = _slugify(atom.tags[0])
        return [f'wiki/{atom.branch}/{slug}']
    return [f'wiki/{atom.branch}/other']


def _slugify(text: str, max_len: int = 60) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:max_len].rstrip('-') or 'untitled'


def build_compile_plan(atoms: list[Atom]) -> dict[str, list[Atom]]:
    plan: dict[str, list[Atom]] = {}
    for atom in atoms:
        for target in determine_targets(atom):
            plan.setdefault(target, []).append(atom)
    # Stable order per page: by atom id
    for atoms_list in plan.values():
        atoms_list.sort(key=lambda a: a.id)
    return plan


# ---- Existing-page introspection -----------------------------------------

@dataclass
class ExistingPage:
    rel_path: str               # e.g. wiki/process/foo.md
    content: str                # raw file content
    autogen: bool               # True if frontmatter carries the marker


def load_existing_pages(wiki_root: Path) -> dict[str, ExistingPage]:
    out: dict[str, ExistingPage] = {}
    wiki_dir = wiki_root / 'wiki'
    if not wiki_dir.exists():
        return out

    for md_file in wiki_dir.rglob('*.md'):
        rel = str(md_file.relative_to(wiki_root)).replace(os.sep, '/')
        # Skip the _meta folder (lint reports, health reports) and the
        # top-level _README.md (auto-gen warning). Don't skip everything
        # that happens to start with _ — compiled fallback pages like
        # wiki/<branch>/other.md are legitimate compile output.
        if rel.startswith('wiki/_meta/') or rel == 'wiki/_README.md':
            continue
        if any(part.startswith('.') for part in Path(rel).parts):
            continue
        try:
            text = md_file.read_text(encoding='utf-8')
        except OSError:
            continue
        fm = parse_frontmatter(text) or {}
        autogen = (fm.get('type') in AUTOGEN_TYPES) and ('date-compiled' in fm)
        page_key = rel.removesuffix('.md')
        out[page_key] = ExistingPage(rel_path=rel, content=text, autogen=autogen)
    return out


# ---- Page rendering ------------------------------------------------------

def page_title_for(page_key: str) -> str:
    """Human title from page key. wiki/process/intake-three-gate → 'Intake Three Gate'."""
    leaf = Path(page_key).name
    words = leaf.replace('-', ' ').replace('_', ' ').split()
    return ' '.join(w.capitalize() for w in words) or 'Untitled'


def page_type_for(page_key: str) -> str:
    parts = page_key.split('/')
    if len(parts) >= 2 and parts[0] == 'wiki':
        bucket = parts[1]
        if bucket in PAGE_TYPES:
            mapping = {'synthesis': 'synthesis', 'comparisons': 'comparison', 'queries': 'query'}
            return mapping[bucket]
    return 'branch-page'


def rollup_confidence(atoms: list[Atom]) -> str:
    if not atoms:
        return 'low'
    sorted_conf = sorted(a.confidence for a in atoms)
    n = len(sorted_conf)
    median = sorted_conf[n // 2] if n % 2 else (sorted_conf[n // 2 - 1] + sorted_conf[n // 2]) / 2
    if all(c >= 0.80 for c in sorted_conf):
        return 'high'
    if median >= 0.60:
        return 'medium'
    return 'low'


def rollup_status(atoms: list[Atom]) -> str:
    statuses = {a.status for a in atoms}
    if statuses == {'current'}:
        return 'current'
    return 'mixed'


def render_page(page_key: str, atoms: list[Atom], today: str) -> str:
    title = page_title_for(page_key)
    page_type = page_type_for(page_key)
    atom_ids = [a.id for a in atoms]
    confidence = rollup_confidence(atoms)
    status = rollup_status(atoms)

    # Frontmatter — deterministic key order, deterministic list rendering
    lines: list[str] = []
    lines.append('---')
    lines.append(f'title: "{title}"')
    lines.append(f'type: {page_type}')
    lines.append(f'date-compiled: {today}')
    lines.append(f'atoms: [{", ".join(atom_ids)}]')
    lines.append(f'confidence: {confidence}')
    lines.append(f'status: {status}')
    lines.append('---')
    lines.append('')

    # Lead — deterministic, mechanical
    sources = sorted({src for a in atoms for src in a.sources})
    high_conf = sum(1 for a in atoms if a.confidence >= 0.80)
    lead = (
        f'This page covers **{len(atoms)} atom{"" if len(atoms) == 1 else "s"}** '
        f'drawn from **{len(sources)} source{"" if len(sources) == 1 else "s"}**. '
        f'{high_conf} {"is" if high_conf == 1 else "are"} high-confidence (≥0.80).'
    )
    lines.append(lead)
    lines.append('')

    # Contradictions section (if any contradicts relationships exist within this page)
    page_atom_ids = set(atom_ids)
    contradiction_pairs: list[tuple[str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for atom in atoms:
        for other_id in atom.contradicts:
            if other_id in page_atom_ids:
                pair = tuple(sorted((atom.id, other_id)))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    contradiction_pairs.append(pair)
    if contradiction_pairs:
        lines.append('## Contradictions on this page')
        lines.append('')
        for a_id, b_id in contradiction_pairs:
            n_a = atom_ids.index(a_id) + 1
            n_b = atom_ids.index(b_id) + 1
            lines.append(f'> [[{a_id}]] [{n_a}] contradicts [[{b_id}]] [{n_b}]. Resolution pending review.')
            lines.append('')

    # Atoms section — the meat
    lines.append('## Atoms')
    lines.append('')
    for n, atom in enumerate(atoms, start=1):
        primary_source = atom.sources[0] if atom.sources else 'no source'
        # Citation form: bold claim, atom id wikilink, numeric ref, confidence, source
        lines.append(
            f'{n}. **{atom.claim}** — [[{atom.id}]] (confidence {atom.confidence:.2f}) — `{primary_source}`'
        )
    lines.append('')

    # Sources section — dedup raw
    if sources:
        lines.append('## Sources')
        lines.append('')
        for source in sources:
            lines.append(f'- [[{source}]]')
        lines.append('')

    # Drafts section — only if any drafts present
    drafts = [a for a in atoms if a.status == 'draft']
    if drafts:
        lines.append('## Drafts')
        lines.append('')
        lines.append('The following atoms on this page are still drafts — their claims are not yet reviewed:')
        lines.append('')
        for atom in drafts:
            lines.append(f'- [[{atom.id}]] — {atom.claim}')
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


# ---- Idempotency ---------------------------------------------------------

DATE_COMPILED_LINE_RE = re.compile(r'^date-compiled:\s*\d{4}-\d{2}-\d{2}\s*$', re.MULTILINE)


def is_content_equivalent(new_content: str, existing_content: str) -> bool:
    """Compare two page contents ignoring the date-compiled stamp.

    The compile is idempotent: if atoms haven't changed, output shouldn't
    change byte-for-byte except for the date stamp. That stamp's only role
    is freshness-tracking; we should not write it unless other content
    actually changed.
    """
    normalise = lambda s: DATE_COMPILED_LINE_RE.sub('date-compiled: -', s)
    return normalise(new_content) == normalise(existing_content)


# ---- Compile actions -----------------------------------------------------

@dataclass
class Action:
    kind: str                # 'create' | 'update' | 'unchanged' | 'blocked' | 'delete'
    page_key: str            # e.g. wiki/process/foo
    rel_path: str            # e.g. wiki/process/foo.md
    new_content: Optional[str] = None
    existing_content: Optional[str] = None
    atom_count: int = 0


def build_actions(plan: dict[str, list[Atom]],
                  existing: dict[str, ExistingPage],
                  today: str,
                  force: bool) -> list[Action]:
    actions: list[Action] = []

    plan_keys = set(plan.keys())
    existing_keys = set(existing.keys())

    # Creates and updates from the plan
    for page_key in sorted(plan_keys):
        atoms = plan[page_key]
        rel_path = f'{page_key}.md'
        new_content = render_page(page_key, atoms, today)

        if page_key not in existing:
            actions.append(Action(
                kind='create', page_key=page_key, rel_path=rel_path,
                new_content=new_content, atom_count=len(atoms),
            ))
            continue

        ex = existing[page_key]
        if not ex.autogen and not force:
            actions.append(Action(
                kind='blocked', page_key=page_key, rel_path=rel_path,
                new_content=new_content, existing_content=ex.content,
                atom_count=len(atoms),
            ))
            continue

        if is_content_equivalent(new_content, ex.content):
            actions.append(Action(
                kind='unchanged', page_key=page_key, rel_path=rel_path,
                atom_count=len(atoms),
            ))
        else:
            actions.append(Action(
                kind='update', page_key=page_key, rel_path=rel_path,
                new_content=new_content, existing_content=ex.content,
                atom_count=len(atoms),
            ))

    # Deletions: pages that existed but no atoms compile to them now
    for page_key in sorted(existing_keys - plan_keys):
        ex = existing[page_key]
        # Skip hand-edited pages from deletion — they don't have our marker, treat as untouchable
        if not ex.autogen:
            continue
        # Skip index and overview (handled separately)
        if page_key in ('index', 'wiki/overview'):
            continue
        actions.append(Action(
            kind='delete', page_key=page_key, rel_path=f'{page_key}.md',
        ))

    return actions


# ---- Stop gate -----------------------------------------------------------

def render_plan(actions: list[Action], blocked_no_force: int) -> str:
    by_kind: dict[str, list[Action]] = {'create': [], 'update': [], 'unchanged': [], 'blocked': [], 'delete': []}
    for a in actions:
        by_kind[a.kind].append(a)

    out: list[str] = []
    out.append('Compile plan:')
    out.append('')
    if by_kind['create']:
        out.append(f'  New pages ({len(by_kind["create"])}):')
        for a in by_kind['create']:
            out.append(f'    + {a.rel_path} ({a.atom_count} atoms)')
        out.append('')
    if by_kind['update']:
        out.append(f'  Updated pages ({len(by_kind["update"])}):')
        for a in by_kind['update']:
            out.append(f'    ~ {a.rel_path} (now {a.atom_count} atoms)')
        out.append('')
    if by_kind['unchanged']:
        out.append(f'  Unchanged ({len(by_kind["unchanged"])}): same content, will not be rewritten')
        out.append('')
    if by_kind['blocked']:
        out.append(f'  BLOCKED — hand-edited pages, no auto-gen marker ({len(by_kind["blocked"])}):')
        for a in by_kind['blocked']:
            out.append(f'    ! {a.rel_path} (pass --force to overwrite, or move to wiki-archive/)')
        out.append('')
    if by_kind['delete']:
        out.append(f'  Deletions ({len(by_kind["delete"])}, atoms no longer compile here):')
        for a in by_kind['delete']:
            out.append(f'    - {a.rel_path}')
        out.append('')
    if not any(by_kind.values()) and blocked_no_force == 0:
        out.append('  (Nothing to do — wiki is up to date.)')
        out.append('')
    return '\n'.join(out)


def prompt_yes_no(question: str) -> bool:
    try:
        answer = input(f'{question} [y/N]: ').strip().lower()
    except EOFError:
        return False
    return answer in ('y', 'yes')


# ---- Execution -----------------------------------------------------------

def execute(actions: list[Action], wiki_root: Path) -> dict[str, int]:
    counts = {'create': 0, 'update': 0, 'unchanged': 0, 'delete': 0, 'blocked': 0}
    for action in actions:
        if action.kind == 'unchanged':
            counts['unchanged'] += 1
            continue
        if action.kind == 'blocked':
            counts['blocked'] += 1
            continue
        if action.kind == 'delete':
            target = wiki_root / action.rel_path
            try:
                target.unlink()
                counts['delete'] += 1
            except OSError as exc:
                sys.stderr.write(f'Failed to delete {target}: {exc}\n')
            continue
        if action.kind in ('create', 'update') and action.new_content is not None:
            target = wiki_root / action.rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                target.write_text(action.new_content, encoding='utf-8')
                counts[action.kind] += 1
            except OSError as exc:
                sys.stderr.write(f'Failed to write {target}: {exc}\n')
    return counts


# ---- Index + overview ----------------------------------------------------

def render_index(atoms: list[Atom], plan: dict[str, list[Atom]], today: str) -> str:
    lines: list[str] = []
    lines.append('---')
    lines.append('title: "Index"')
    lines.append('type: auto-generated')
    lines.append(f'last-updated: {today}')
    lines.append(f'atom-count: {len(atoms)}')
    lines.append(f'wiki-page-count: {len(plan)}')
    lines.append('---')
    lines.append('')
    lines.append('# Index')
    lines.append('')
    lines.append('Auto-generated content catalog. Refresh with `/llm-wiki compile`.')
    lines.append('')

    # Pages by branch
    lines.append('## Pages by branch')
    lines.append('')
    for branch in BRANCHES:
        branch_pages = sorted(k for k in plan.keys() if k.startswith(f'wiki/{branch}/'))
        if not branch_pages:
            continue
        lines.append(f'### {branch.title()}')
        lines.append('')
        for page_key in branch_pages:
            n_atoms = len(plan[page_key])
            title = page_title_for(page_key)
            lines.append(f'- [[{page_key}|{title}]] — {n_atoms} atom{"" if n_atoms == 1 else "s"}')
        lines.append('')

    # Pages by page type
    type_pages = {pt: sorted(k for k in plan.keys() if k.startswith(f'wiki/{pt}/')) for pt in PAGE_TYPES}
    if any(type_pages.values()):
        lines.append('## Pages by type')
        lines.append('')
        for page_type in PAGE_TYPES:
            pages = type_pages[page_type]
            if not pages:
                continue
            lines.append(f'### {page_type.title()}')
            lines.append('')
            for page_key in pages:
                n_atoms = len(plan[page_key])
                title = page_title_for(page_key)
                lines.append(f'- [[{page_key}|{title}]] — {n_atoms} atom{"" if n_atoms == 1 else "s"}')
            lines.append('')

    # Atom counts by branch
    lines.append('## Atoms by branch')
    lines.append('')
    branch_counts = {b: sum(1 for a in atoms if a.branch == b) for b in BRANCHES}
    total = sum(branch_counts.values())
    for branch, count in branch_counts.items():
        if count == 0:
            continue
        pct = (count * 100 / total) if total else 0
        lines.append(f'- **{branch}**: {count} ({pct:.0f}%)')
    lines.append('')

    # Tag index
    tag_to_atoms: dict[str, list[str]] = {}
    for atom in atoms:
        for tag in atom.tags:
            tag_to_atoms.setdefault(tag, []).append(atom.id)
    if tag_to_atoms:
        lines.append('## Tags')
        lines.append('')
        for tag in sorted(tag_to_atoms.keys()):
            ids = sorted(tag_to_atoms[tag])
            lines.append(f'- **{tag}** ({len(ids)})')
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def render_overview(atoms: list[Atom], plan: dict[str, list[Atom]], purpose: Optional[str], today: str) -> str:
    lines: list[str] = []
    lines.append('---')
    lines.append('title: "Overview"')
    lines.append('type: auto-generated')
    lines.append(f'last-updated: {today}')
    lines.append('---')
    lines.append('')
    lines.append('# Overview')
    lines.append('')
    lines.append('Auto-generated synthesis from current atoms. Refreshes every `/llm-wiki compile`.')
    lines.append('')

    # Pull "What this wiki is for" from purpose.md if available
    if purpose:
        purpose_intro = _extract_purpose_intro(purpose)
        if purpose_intro:
            lines.append('## What this wiki is for')
            lines.append('')
            lines.append(purpose_intro)
            lines.append('')

    # Top atoms per branch (by confidence, then by id)
    lines.append('## Branches')
    lines.append('')
    for branch in BRANCHES:
        branch_atoms = sorted(
            (a for a in atoms if a.branch == branch),
            key=lambda a: (-a.confidence, a.id),
        )
        if not branch_atoms:
            continue
        lines.append(f'### {branch.title()} ({len(branch_atoms)} atoms)')
        lines.append('')
        for atom in branch_atoms[:5]:
            lines.append(f'- [[{atom.id}]] (confidence {atom.confidence:.2f}) — {atom.claim}')
        if len(branch_atoms) > 5:
            lines.append(f'- *…and {len(branch_atoms) - 5} more.*')
        lines.append('')

    # Open contradictions across the wiki
    seen_pairs: set[tuple[str, str]] = set()
    for atom in atoms:
        for other_id in atom.contradicts:
            pair = tuple(sorted((atom.id, other_id)))
            if pair not in seen_pairs:
                seen_pairs.add(pair)
    if seen_pairs:
        lines.append('## Open contradictions')
        lines.append('')
        for a_id, b_id in sorted(seen_pairs):
            lines.append(f'- [[{a_id}]] ↔ [[{b_id}]]')
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def _extract_purpose_intro(purpose_text: str) -> Optional[str]:
    """Pull the body under '## What this wiki is for' from purpose.md."""
    match = re.search(
        r'^##\s+What this wiki is for\s*\n+(.+?)(?=^##\s|\Z)',
        purpose_text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return None
    text = match.group(1).strip()
    # Strip HTML comments and template placeholders
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL).strip()
    text = re.sub(r'\{\{[^}]+\}\}', '', text).strip()
    return text or None


# ---- Misc ----------------------------------------------------------------

def write_log_entry(wiki_root: Path, counts: dict[str, int], today: str) -> None:
    log_path = wiki_root / 'log.md'
    entry = (
        f'\n## {today}\n\n'
        f'- Compiled wiki: {counts["create"] + counts["update"]} pages written '
        f'({counts["create"]} new, {counts["update"]} updated, {counts["delete"]} deleted, '
        f'{counts["unchanged"]} unchanged, {counts["blocked"]} blocked).\n'
    )
    try:
        existing = log_path.read_text(encoding='utf-8') if log_path.exists() else '# Wiki Log\n'
        log_path.write_text(existing.rstrip() + '\n' + entry, encoding='utf-8')
    except OSError as exc:
        sys.stderr.write(f'Failed to append to log.md: {exc}\n')


def ensure_wiki_readme(wiki_root: Path) -> None:
    """Make sure wiki/_README.md exists with the auto-gen warning. Don't overwrite if user edited."""
    readme = wiki_root / 'wiki' / '_README.md'
    if readme.exists():
        return
    readme.parent.mkdir(parents=True, exist_ok=True)
    readme.write_text(
        '# AUTO-GENERATED FOLDER\n\n'
        'This folder contains compiled wiki pages generated from `atoms/`.\n\n'
        '**DO NOT EDIT FILES IN THIS FOLDER DIRECTLY.**\n\n'
        'To change content:\n\n'
        '1. Edit the source atoms in `atoms/<branch>/`.\n'
        '2. Run `/llm-wiki compile`.\n\n'
        'The compiler regenerates pages here from current atoms. Hand edits will be lost on the next compile.\n',
        encoding='utf-8',
    )


def check_lint_blocking(wiki_root: Path) -> bool:
    """Return True if a recent lint report says compile is blocked, else False."""
    # We don't auto-run lint to avoid surprising the user. If lint.py is available
    # alongside this script, we run it in --json mode.
    lint_script = Path(__file__).parent / 'lint.py'
    if not lint_script.exists():
        return False
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(lint_script), str(wiki_root), '--json'],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if result.returncode == 2:
        return False  # lint itself failed — let compile try
    # Exit 1 means criticals; exit 0 means none.
    return result.returncode == 1


# ---- Main ----------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('wiki_root', nargs='?', default=None)
    parser.add_argument('--force', action='store_true', help='Overwrite hand-edited wiki pages')
    parser.add_argument('--branch', default=None, choices=BRANCHES + [None])
    parser.add_argument('--page', default=None, help='Compile a single page (wiki/branch/slug)')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--yes', action='store_true', help='Skip the stop gate')
    parser.add_argument('--no-drafts', action='store_true')
    parser.add_argument('--skip-lint', action='store_true')
    args = parser.parse_args()

    # Resolve wiki root
    start = Path(args.wiki_root).expanduser().resolve() if args.wiki_root else Path.cwd()
    if args.wiki_root and _looks_like_wiki(start):
        wiki_root = start
    else:
        wiki_root = find_wiki_root(start)
    if wiki_root is None:
        sys.stderr.write('Could not find a wiki root.\n')
        sys.stderr.write('Pass the wiki path explicitly: python compile.py /path/to/_llm-wiki\n')
        return 2

    today = date.today().isoformat()

    # Lint guard
    if not args.skip_lint and check_lint_blocking(wiki_root):
        sys.stderr.write('Lint reports critical errors. Compile refuses to run.\n')
        sys.stderr.write('  Fix: python lint.py "%s" --verbose\n' % wiki_root)
        sys.stderr.write('  Override: --skip-lint (discouraged)\n')
        return 2

    # Load atoms and existing pages
    atoms = load_atoms(wiki_root, include_drafts=not args.no_drafts)
    if args.branch:
        # Keep only atoms in the chosen branch; rest become irrelevant to action planning
        atoms = [a for a in atoms if a.branch == args.branch]
    plan = build_compile_plan(atoms)

    # --page filter: keep only that page
    if args.page:
        wanted = args.page.removesuffix('.md')
        plan = {k: v for k, v in plan.items() if k == wanted}

    existing = load_existing_pages(wiki_root)
    if args.branch:
        existing = {k: v for k, v in existing.items() if k.startswith(f'wiki/{args.branch}/')}
    if args.page:
        wanted = args.page.removesuffix('.md')
        existing = {k: v for k, v in existing.items() if k == wanted}

    actions = build_actions(plan, existing, today, force=args.force)

    # Stop gate
    blocked_count = sum(1 for a in actions if a.kind == 'blocked')
    plan_summary = render_plan(actions, blocked_no_force=blocked_count)
    print(plan_summary)

    if args.dry_run:
        print('(Dry run — no files written.)')
        return 0

    has_destructive = any(a.kind in ('update', 'delete') for a in actions)
    has_blocked_with_force = args.force and any(a.kind == 'blocked' for a in actions)

    if (has_destructive or has_blocked_with_force) and not args.yes:
        if not prompt_yes_no('Proceed?'):
            print('Aborted at stop gate.')
            return 1

    # Execute
    counts = execute(actions, wiki_root)

    # Rebuild index.md and overview.md (unless --page or --branch restricted the run)
    if not args.page and not args.branch:
        purpose_text = None
        purpose_path = wiki_root / 'purpose.md'
        if purpose_path.exists():
            try:
                purpose_text = purpose_path.read_text(encoding='utf-8')
            except OSError:
                purpose_text = None

        # Use the FULL plan + atoms for index/overview, not the filtered ones
        full_atoms = load_atoms(wiki_root, include_drafts=not args.no_drafts)
        full_plan = build_compile_plan(full_atoms)

        index_path = wiki_root / 'index.md'
        index_content = render_index(full_atoms, full_plan, today)
        existing_index = index_path.read_text(encoding='utf-8') if index_path.exists() else ''
        if not is_content_equivalent(index_content, existing_index):
            index_path.write_text(index_content, encoding='utf-8')

        overview_path = wiki_root / 'wiki' / 'overview.md'
        overview_path.parent.mkdir(parents=True, exist_ok=True)
        overview_content = render_overview(full_atoms, full_plan, purpose_text, today)
        existing_overview = overview_path.read_text(encoding='utf-8') if overview_path.exists() else ''
        if not is_content_equivalent(overview_content, existing_overview):
            overview_path.write_text(overview_content, encoding='utf-8')

    # Wiki/_README.md
    ensure_wiki_readme(wiki_root)

    # Log
    write_log_entry(wiki_root, counts, today)

    # Report
    print()
    print('Done.')
    print(f'  Created:   {counts["create"]}')
    print(f'  Updated:   {counts["update"]}')
    print(f'  Unchanged: {counts["unchanged"]}')
    print(f'  Deleted:   {counts["delete"]}')
    print(f'  Blocked:   {counts["blocked"]}')
    if counts['blocked'] and not args.force:
        print()
        print('Hand-edited pages were skipped. Pass --force to overwrite, or move them to wiki-archive/.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
