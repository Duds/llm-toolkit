/**
 * Centralised path helper for llm-wiki sidecars and conventional locations.
 *
 * One source of truth for "where does state live". Every script that needs
 * to read or write something under .llm-wiki/ or inside the wiki itself
 * goes through this module.
 *
 * Conventions:
 *   Wiki root: ./_llm-wiki/ (project) or ~/Projects/_llm-wiki/ (portfolio)
 *   Sidecars:  <wikiRoot>/.llm-wiki/<feature>/
 *
 * The .llm-wiki/ sidecar holds machinery (caches, queues) that we don't
 * want polluting the Obsidian vault view but want colocated with the wiki.
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

export const SIDECAR_DIR = '.llm-wiki';
export const RAW_DIR = 'raw';
export const ATOMS_DIR = 'atoms';
export const WIKI_DIR = 'wiki';
export const TEMPLATES_DIR = 'templates';

export const BRANCHES = ['people', 'process', 'policy', 'platform', 'product', 'meta'];
export const PAGE_TYPES = ['synthesis', 'comparisons', 'queries'];

/**
 * Walk up from startDir looking for an llm-wiki/ directory. Returns the
 * llm-wiki root (the directory itself, not its parent), or null if not found.
 *
 * Also accepts being already inside the wiki root.
 */
export function findWikiRoot(startDir = process.cwd()) {
  // 1. Explicit env override
  const envRoot = process.env.LLM_WIKI_ROOT;
  if (envRoot && envRoot.trim()) {
    const trimmed = envRoot.trim();
    const abs = path.isAbsolute(trimmed) ? trimmed : path.resolve(startDir, trimmed);
    if (looksLikeWikiRoot(abs)) return abs;
  }

  // 2. cwd is the wiki root
  if (looksLikeWikiRoot(startDir)) return startDir;

  // 3. Walk up looking for a sibling llm-wiki/
  let dir = path.resolve(startDir);
  while (true) {
    const candidate = path.join(dir, '_llm-wiki');
    if (looksLikeWikiRoot(candidate)) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }

  // 4. Fall back to portfolio location ~/Projects/_llm-wiki/
  const portfolio = path.join(os.homedir(), 'Projects', '_llm-wiki');
  if (looksLikeWikiRoot(portfolio)) return portfolio;

  return null;
}

/**
 * A directory looks like a wiki root if it contains at minimum a schema.md
 * file and an atoms/ directory. Bootstrap creates both; we test against
 * them rather than the directory name so a wiki renamed to something else
 * still resolves.
 */
export function looksLikeWikiRoot(dir) {
  if (!dir || !fs.existsSync(dir)) return false;
  const stat = fs.statSync(dir);
  if (!stat.isDirectory()) return false;
  return fs.existsSync(path.join(dir, 'schema.md')) &&
         fs.existsSync(path.join(dir, 'atoms'));
}

/**
 * Detect whether a wiki root is portfolio-level or project-level.
 * Portfolio-level wikis sit at ~/Projects/_llm-wiki/ (or whatever
 * LLM_WIKI_PORTFOLIO_ROOT points to). Everything else is project-level.
 */
export function wikiLevel(wikiRoot) {
  const portfolioParent = process.env.LLM_WIKI_PORTFOLIO_ROOT
    || path.join(os.homedir(), 'Projects');
  const expected = path.join(portfolioParent, '_llm-wiki');
  return path.resolve(wikiRoot) === path.resolve(expected) ? 'portfolio' : 'project';
}

// ---- Sidecar paths --------------------------------------------------------

export function getSidecarDir(wikiRoot) {
  return path.join(wikiRoot, SIDECAR_DIR);
}

export function getIngestCachePath(wikiRoot) {
  return path.join(getSidecarDir(wikiRoot), 'ingest-cache.json');
}

export function getReviewDir(wikiRoot) {
  return path.join(wikiRoot, ATOMS_DIR, '_review');
}

export function getQueriesDir(wikiRoot) {
  return path.join(wikiRoot, WIKI_DIR, 'queries');
}

export function getProvenancePath(wikiRoot) {
  return path.join(wikiRoot, RAW_DIR, '_provenance.md');
}

export function getOverviewPath(wikiRoot) {
  return path.join(wikiRoot, WIKI_DIR, 'overview.md');
}

export function getIndexPath(wikiRoot) {
  return path.join(wikiRoot, 'index.md');
}

export function getPurposePath(wikiRoot) {
  return path.join(wikiRoot, 'purpose.md');
}

export function getSchemaPath(wikiRoot) {
  return path.join(wikiRoot, 'schema.md');
}

// ---- Branch paths ---------------------------------------------------------

export function getBranchDir(wikiRoot, branch) {
  if (!BRANCHES.includes(branch)) {
    throw new Error(`Unknown branch: ${branch}. Expected one of: ${BRANCHES.join(', ')}`);
  }
  return path.join(wikiRoot, ATOMS_DIR, branch);
}

export function getWikiBranchDir(wikiRoot, branch) {
  if (!BRANCHES.includes(branch)) {
    throw new Error(`Unknown branch: ${branch}. Expected one of: ${BRANCHES.join(', ')}`);
  }
  return path.join(wikiRoot, WIKI_DIR, branch);
}

export function getPageTypeDir(wikiRoot, pageType) {
  if (!PAGE_TYPES.includes(pageType)) {
    throw new Error(`Unknown page type: ${pageType}. Expected one of: ${PAGE_TYPES.join(', ')}`);
  }
  return path.join(wikiRoot, WIKI_DIR, pageType);
}

// ---- Counts ---------------------------------------------------------------

export function countAtoms(wikiRoot) {
  let total = 0;
  for (const branch of BRANCHES) {
    const dir = getBranchDir(wikiRoot, branch);
    if (!fs.existsSync(dir)) continue;
    total += fs.readdirSync(dir).filter((f) => f.endsWith('.md') && !f.startsWith('_')).length;
  }
  return total;
}

export function countWikiPages(wikiRoot) {
  let total = 0;
  const walk = (dir) => {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.name.endsWith('.md') && !entry.name.startsWith('_')) {
        total++;
      }
    }
  };
  walk(path.join(wikiRoot, WIKI_DIR));
  return total;
}
