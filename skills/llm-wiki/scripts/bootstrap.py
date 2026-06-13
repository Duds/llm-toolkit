#!/usr/bin/env python3
"""
Bootstrap an llm-wiki.

Cross-platform (Windows / macOS / Linux). Pure stdlib, no third-party deps.

Idempotent: existing files are preserved unless --reinit is passed.

Usage:
    python bootstrap.py <target-path> [options]

Options:
    --scenario {research,consulting,design,dcceew,general}
                          Seed purpose.md from this scenario template (default: general)
    --name NAME           Wiki name used in templates (default: derived from path)
    --reinit              Overwrite template files (preserves atoms/wiki/raw content)
    --dry-run             Print plan, write nothing
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / 'templates'

BRANCHES = ['people', 'process', 'policy', 'platform', 'product', 'meta']
PAGE_TYPES = ['synthesis', 'comparisons', 'queries']
SCENARIOS = ['research', 'consulting', 'design', 'dcceew', 'general']

SCHEMA_MARKER_FILE = 'schema.md'  # Presence indicates a wiki exists


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('target', nargs='?', default='./_llm-wiki', help='Target path for the wiki')
    parser.add_argument('--scenario', choices=SCENARIOS, default='general')
    parser.add_argument('--name', default=None)
    parser.add_argument('--reinit', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    target = Path(args.target).resolve()
    name = args.name or derive_name(target)

    print(f'Target:   {target}')
    print(f'Scenario: {args.scenario}')
    print(f'Name:     {name}')
    print()

    # Existing wiki guard
    schema_path = target / SCHEMA_MARKER_FILE
    if schema_path.exists() and not args.reinit:
        print(f'ERROR: Wiki already exists at {target}', file=sys.stderr)
        print('       Run /llm-wiki lint to check health, or pass --reinit to refresh templates.', file=sys.stderr)
        return 1

    # Build the action plan
    plan = build_plan(target, args.scenario, name, reinit=args.reinit)

    if args.dry_run:
        print('DRY RUN — would perform:')
        for action in plan:
            print(f'  {action.describe()}')
        return 0

    # Execute
    preserved: list[str] = []
    created: list[str] = []
    for action in plan:
        result = action.execute()
        if result == 'preserved':
            preserved.append(action.describe_target())
        elif result == 'created':
            created.append(action.describe_target())

    print_report(target, args.scenario, name, created, preserved)
    return 0


# ---- Action plan ---------------------------------------------------------

class Action:
    def describe(self) -> str: ...
    def describe_target(self) -> str: ...
    def execute(self) -> str: ...  # returns 'created' | 'preserved' | 'skipped'


class MakeDir(Action):
    def __init__(self, path: Path):
        self.path = path

    def describe(self) -> str:
        return f'mkdir  {self.path}'

    def describe_target(self) -> str:
        return f'{self.path}/'

    def execute(self) -> str:
        if self.path.exists():
            return 'preserved'
        self.path.mkdir(parents=True, exist_ok=True)
        return 'created'


class WriteFile(Action):
    def __init__(self, path: Path, content: str, overwrite: bool = False):
        self.path = path
        self.content = content
        self.overwrite = overwrite

    def describe(self) -> str:
        mode = 'overwrite' if self.overwrite else 'write'
        return f'{mode}  {self.path}'

    def describe_target(self) -> str:
        return str(self.path)

    def execute(self) -> str:
        if self.path.exists() and not self.overwrite:
            return 'preserved'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.content, encoding='utf-8')
        return 'created'


def build_plan(target: Path, scenario: str, name: str, reinit: bool) -> list[Action]:
    plan: list[Action] = []

    # Directory structure
    plan.append(MakeDir(target))
    plan.append(MakeDir(target / 'raw'))
    plan.append(MakeDir(target / 'raw' / 'assets'))
    plan.append(MakeDir(target / 'atoms'))
    for branch in BRANCHES:
        plan.append(MakeDir(target / 'atoms' / branch))
    plan.append(MakeDir(target / 'atoms' / '_review'))
    plan.append(MakeDir(target / 'wiki'))
    for branch in BRANCHES:
        plan.append(MakeDir(target / 'wiki' / branch))
    for page_type in PAGE_TYPES:
        plan.append(MakeDir(target / 'wiki' / page_type))
    plan.append(MakeDir(target / '.obsidian'))
    plan.append(MakeDir(target / '.llm-wiki'))

    # Template files
    today = date.today().isoformat()
    subs = {
        'WIKI_NAME': name,
        'DATE': today,
        'SCENARIO': scenario,
    }

    template_files = [
        ('schema.md', target / 'schema.md'),
        ('claude-md.md', target / 'CLAUDE.md'),
        ('readme.md', target / 'README.md'),
        (f'purpose-{scenario}.md', target / 'purpose.md'),
        ('index.md', target / 'index.md'),
        ('provenance.md', target / 'raw' / '_provenance.md'),
        ('atom-template.md', target / 'atoms' / '_template.md'),
        ('wiki-readme.md', target / 'wiki' / '_README.md'),
        ('obsidian-app.json', target / '.obsidian' / 'app.json'),
        ('obsidian-appearance.json', target / '.obsidian' / 'appearance.json'),
        ('obsidian-core-plugins.json', target / '.obsidian' / 'core-plugins.json'),
    ]

    for template_name, dest in template_files:
        src = TEMPLATES_DIR / template_name
        if not src.exists():
            print(f'WARNING: template missing: {src}', file=sys.stderr)
            continue
        content = render(src.read_text(encoding='utf-8'), subs)
        plan.append(WriteFile(dest, content, overwrite=reinit))

    # Initial log.md
    log_content = f'# Wiki Log\n\nAppend-only chronology of significant wiki events.\n\n## {today}\n\n- Wiki bootstrapped at `{target}`\n- Scenario: `{scenario}`\n- Initial structure created\n'
    plan.append(WriteFile(target / 'log.md', log_content, overwrite=reinit))

    return plan


# ---- Substitution --------------------------------------------------------

def render(content: str, subs: dict[str, str]) -> str:
    """Replace {{KEY}} markers with substitution values."""
    for key, value in subs.items():
        content = content.replace('{{' + key + '}}', value)
    return content


def derive_name(target: Path) -> str:
    """Make a human-readable wiki name from the path."""
    base = target.name
    if base == '_llm-wiki' and target.parent.name != 'Projects':
        # Project-level wiki — use the parent dir name
        base = target.parent.name
    # Convert kebab/snake to Title Case
    parts = base.replace('_', ' ').replace('-', ' ').split()
    return ' '.join(p.capitalize() for p in parts) or 'Wiki'


# ---- Reporting -----------------------------------------------------------

def print_report(target: Path, scenario: str, name: str, created: list[str], preserved: list[str]) -> None:
    print()
    print(f'LLM-wiki bootstrapped at {target}')
    print()
    print(f'Name:     {name}')
    print(f'Scenario: {scenario}')
    print()

    if created:
        print(f'Created ({len(created)}):')
        for item in created[:20]:
            print(f'  + {item}')
        if len(created) > 20:
            print(f'  ... and {len(created) - 20} more')
        print()

    if preserved:
        print(f'Preserved ({len(preserved)}, already existed):')
        for item in preserved[:10]:
            print(f'  = {item}')
        if len(preserved) > 10:
            print(f'  ... and {len(preserved) - 10} more')
        print()

    print('Next steps:')
    print('  1. Edit purpose.md — at minimum write 3-7 specific key questions.')
    print('  2. Add a source to raw/ and run: /llm-wiki ingest raw/<file>')
    print('  3. Or scan a folder: /llm-wiki crawl <path>')


if __name__ == '__main__':
    sys.exit(main())
