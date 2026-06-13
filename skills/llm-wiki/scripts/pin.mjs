#!/usr/bin/env node
/**
 * Pin/unpin llm-wiki sub-commands as standalone slash-command shortcuts.
 *
 * Usage:
 *   node pin.mjs pin <command>
 *   node pin.mjs unpin <command>
 *
 * `pin query` creates a tiny /query skill that delegates to /llm-wiki query.
 * `unpin query` removes that shortcut.
 *
 * Pins are written into every harness directory that already has llm-wiki
 * installed (.claude/skills/llm-wiki, .cursor/skills/llm-wiki, etc).
 *
 * The script reads command-metadata.json for description and arg-hint so
 * pinned shortcuts have accurate trigger text without hand-editing.
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// All known harness skills directories
const HARNESS_DIRS = [
  '.claude', '.cursor', '.gemini', '.codex', '.agents',
  '.trae', '.opencode', '.kiro',
];

const VALID_COMMANDS = [
  'bootstrap', 'crawl', 'ingest', 'compile', 'query', 'lint', 'report',
];

const PIN_MARKER = '<!-- llm-wiki-pinned-skill -->';

/**
 * Walk up to find a project root. Stops at the first directory with
 * package.json, .git, or a parent .claude/. Defaults to home dir if nothing
 * matches — pin still works at the user's global skills directory.
 */
function findProjectRoot(startDir = process.cwd()) {
  let dir = resolve(startDir);
  while (true) {
    if (
      existsSync(join(dir, 'package.json')) ||
      existsSync(join(dir, '.git')) ||
      existsSync(join(dir, '.claude'))
    ) {
      return dir;
    }
    const parent = resolve(dir, '..');
    if (parent === dir) return startDir;
    dir = parent;
  }
}

/**
 * Find harness skill directories that have llm-wiki installed.
 */
function findHarnessSkillsDirs(projectRoot) {
  const dirs = [];
  for (const harness of HARNESS_DIRS) {
    const skillsDir = join(projectRoot, harness, 'skills');
    if (existsSync(join(skillsDir, 'llm-wiki'))) dirs.push(skillsDir);
  }
  return dirs;
}

function loadCommandMetadata() {
  const metadataPath = join(__dirname, 'command-metadata.json');
  if (existsSync(metadataPath)) {
    return JSON.parse(readFileSync(metadataPath, 'utf-8'));
  }
  return {};
}

function generatePinnedSkill(command, metadata) {
  const desc = metadata[command]?.description || `Shortcut for /llm-wiki ${command}.`;
  const hint = metadata[command]?.argumentHint || '[target]';

  return `---
name: ${command}
description: "${desc}"
argument-hint: "${hint}"
user-invocable: true
---

${PIN_MARKER}

This is a pinned shortcut for \`{{command_prefix}}llm-wiki ${command}\`.

Invoke {{command_prefix}}llm-wiki ${command}, passing along any arguments provided here, and follow its instructions.
`;
}

function pin(command, projectRoot) {
  const metadata = loadCommandMetadata();
  const harnessDirs = findHarnessSkillsDirs(projectRoot);

  if (harnessDirs.length === 0) {
    console.error('No harness directories with llm-wiki installed found.');
    return false;
  }

  const content = generatePinnedSkill(command, metadata);
  let created = 0;

  for (const skillsDir of harnessDirs) {
    const skillDir = join(skillsDir, command);
    if (existsSync(skillDir)) {
      const existingMd = join(skillDir, 'SKILL.md');
      if (existsSync(existingMd)) {
        const existing = readFileSync(existingMd, 'utf-8');
        if (!existing.includes(PIN_MARKER)) {
          console.log(`  SKIP: ${skillDir} (non-pinned skill already exists)`);
          continue;
        }
      }
    }

    mkdirSync(skillDir, { recursive: true });
    writeFileSync(join(skillDir, 'SKILL.md'), content, 'utf-8');
    console.log(`  + ${skillDir}`);
    created++;
  }

  if (created > 0) {
    console.log(`\nPinned '${command}' in ${created} location(s). Use /${command} directly.`);
  }
  return created > 0;
}

function unpin(command, projectRoot) {
  const harnessDirs = findHarnessSkillsDirs(projectRoot);
  let removed = 0;

  for (const skillsDir of harnessDirs) {
    const skillDir = join(skillsDir, command);
    if (!existsSync(skillDir)) continue;

    const skillMd = join(skillDir, 'SKILL.md');
    if (!existsSync(skillMd)) continue;

    const content = readFileSync(skillMd, 'utf-8');
    if (!content.includes(PIN_MARKER)) {
      console.log(`  SKIP: ${skillDir} (not a pinned skill)`);
      continue;
    }

    rmSync(skillDir, { recursive: true, force: true });
    console.log(`  - ${skillDir}`);
    removed++;
  }

  if (removed > 0) {
    console.log(`\nUnpinned '${command}' from ${removed} location(s). Use /llm-wiki ${command} instead.`);
  } else {
    console.log(`No pinned '${command}' shortcut found.`);
  }
  return removed > 0;
}

// --- CLI ------------------------------------------------------------------

const [,, action, command] = process.argv;

if (!action || !command) {
  console.log('Usage: node pin.mjs <pin|unpin> <command>');
  console.log(`\nAvailable commands: ${VALID_COMMANDS.join(', ')}`);
  process.exit(1);
}

if (action !== 'pin' && action !== 'unpin') {
  console.error(`Unknown action: ${action}. Use 'pin' or 'unpin'.`);
  process.exit(1);
}

if (!VALID_COMMANDS.includes(command)) {
  console.error(`Unknown command: ${command}`);
  console.error(`Available: ${VALID_COMMANDS.join(', ')}`);
  process.exit(1);
}

const root = findProjectRoot();

if (action === 'pin') {
  pin(command, root);
} else {
  unpin(command, root);
}
