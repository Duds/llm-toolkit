/**
 * Shared context loader for every llm-wiki command.
 *
 * Resolves the wiki root, reads purpose.md and schema.md, and reports
 * atom and wiki-page counts. Sub-commands call this once at start and
 * consume the JSON output.
 *
 * Input: process.cwd() (or LLM_WIKI_ROOT env var)
 *
 * Output (JSON to stdout):
 *   {
 *     found: boolean,         // wiki root resolved
 *     wikiRoot: string|null,  // absolute path to wiki root
 *     level: 'portfolio' | 'project' | null,
 *     hasPurpose: boolean,
 *     purpose: string|null,   // full file contents
 *     purposePath: string|null,
 *     hasSchema: boolean,
 *     schema: string|null,
 *     schemaPath: string|null,
 *     atomCount: number,
 *     wikiPageCount: number,
 *     cwd: string,            // where we looked from
 *   }
 *
 * If the wiki root cannot be resolved, `found: false` and most fields
 * are null. Sub-commands should refuse to operate in that state except
 * bootstrap.
 */

import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import {
  findWikiRoot,
  wikiLevel,
  getPurposePath,
  getSchemaPath,
  countAtoms,
  countWikiPages,
} from './wiki-paths.mjs';

export function loadWiki(cwd = process.cwd()) {
  const wikiRoot = findWikiRoot(cwd);
  if (!wikiRoot) {
    return {
      found: false,
      wikiRoot: null,
      level: null,
      hasPurpose: false,
      purpose: null,
      purposePath: null,
      hasSchema: false,
      schema: null,
      schemaPath: null,
      atomCount: 0,
      wikiPageCount: 0,
      cwd,
    };
  }

  const purposePath = getPurposePath(wikiRoot);
  const schemaPath = getSchemaPath(wikiRoot);
  const purpose = safeRead(purposePath);
  const schema = safeRead(schemaPath);

  return {
    found: true,
    wikiRoot,
    level: wikiLevel(wikiRoot),
    hasPurpose: !!purpose && !looksLikePlaceholder(purpose),
    purpose,
    purposePath: path.relative(cwd, purposePath),
    hasSchema: !!schema,
    schema,
    schemaPath: path.relative(cwd, schemaPath),
    atomCount: countAtoms(wikiRoot),
    wikiPageCount: countWikiPages(wikiRoot),
    cwd,
  };
}

function safeRead(p) {
  try { return fs.readFileSync(p, 'utf-8'); } catch { return null; }
}

/**
 * A file is "placeholder" if it's empty, contains only frontmatter, or
 * its body is just TODO markers. Sub-commands use this to decide whether
 * to nudge the user to fill in purpose.md.
 */
function looksLikePlaceholder(content) {
  if (!content || content.trim().length < 100) return true;
  const body = content.replace(/^---[\s\S]*?---\s*/, '').trim();
  if (body.length < 80) return true;
  const todoCount = (body.match(/\bTODO\b|\bFIXME\b|\{\{[^}]+\}\}/g) || []).length;
  // Body looks like template if it has more TODO markers than full sentences
  const sentenceCount = (body.match(/[.!?]\s/g) || []).length;
  return todoCount > sentenceCount;
}

// ---- CLI -----------------------------------------------------------------

function cli() {
  const result = loadWiki(process.cwd());
  console.log(JSON.stringify(result, null, 2));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  cli();
}
