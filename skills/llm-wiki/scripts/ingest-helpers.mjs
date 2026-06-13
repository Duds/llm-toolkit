#!/usr/bin/env node
/**
 * ingest-helpers.mjs — mechanical helpers for /llm-wiki ingest.
 *
 * The ingest flow itself is LLM-driven (two-step chain-of-thought,
 * stop gates). These helpers do the parts the LLM shouldn't reinvent:
 *
 *   sha256 <file>                           Compute SHA256 of a file.
 *   cache-get <wiki-root> <raw-rel-path>    Look up the cache entry for a source.
 *   cache-set <wiki-root> <raw-rel-path>    Write a cache entry (reads JSON from
 *                                           --json <file> or stdin).
 *   next-atom-id <wiki-root>                Print the next available atom id
 *                                           for today (atom-YYYYMMDD-NNN).
 *   slug <claim>                            Print a kebab-case slug from a claim.
 *   write-atom <wiki-root> <branch> <slug>  Write an atom file. Body comes from
 *                                           --body <file>. Handles slug collisions.
 *                                           Prints the final relative path written.
 *   append-provenance <wiki-root>           Append a row to raw/_provenance.md.
 *                                           Fields via --raw / --source / --date /
 *                                           --origin / --context / --atoms.
 *   append-log <wiki-root> <message>        Append a line to log.md under today.
 *
 * Each command prints machine-readable output to stdout. Progress and
 * errors go to stderr. Exit codes:
 *   0  success
 *   1  expected miss (e.g. cache-get with no entry)
 *   2  invalid arguments or IO error
 *
 * Source format is ES modules. Run with `node ingest-helpers.mjs <cmd>`.
 */

import { createHash } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
  readdirSync,
  createReadStream,
} from 'node:fs';
import { join, dirname, isAbsolute, resolve, basename, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { argv, cwd, stdin } from 'node:process';
import {
  findWikiRoot,
  getIngestCachePath,
  getProvenancePath,
  getBranchDir,
  BRANCHES,
} from './wiki-paths.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ---- Argument parsing ----------------------------------------------------

/** Pull --flag value pairs out of an arg list. Returns [positionals, flags]. */
function splitArgs(args) {
  const positionals = [];
  const flags = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const name = arg.slice(2);
      const next = args[i + 1];
      if (next !== undefined && !next.startsWith('--')) {
        flags[name] = next;
        i++;
      } else {
        flags[name] = true;
      }
    } else {
      positionals.push(arg);
    }
  }
  return [positionals, flags];
}

function fail(msg, code = 2) {
  process.stderr.write(`${msg}\n`);
  process.exit(code);
}

function resolveWikiRoot(arg) {
  // If a wiki root was passed on the CLI, prefer it.
  if (arg) {
    const abs = isAbsolute(arg) ? arg : resolve(cwd(), arg);
    if (looksLikeWikiInline(abs)) return abs;
    // Allow passing a path inside the wiki — walk up
    const found = findWikiRoot(abs);
    if (found) return found;
    fail(`Not a wiki: ${arg}`);
  }
  const found = findWikiRoot(cwd());
  if (!found) fail('Could not resolve wiki root. Pass it as the first argument.');
  return found;
}

function looksLikeWikiInline(path) {
  return existsSync(join(path, 'schema.md')) && existsSync(join(path, 'atoms'));
}

// ---- SHA256 --------------------------------------------------------------

async function sha256OfFile(filePath) {
  return new Promise((resolveFn, rejectFn) => {
    const hash = createHash('sha256');
    const stream = createReadStream(filePath);
    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('end', () => resolveFn(hash.digest('hex')));
    stream.on('error', rejectFn);
  });
}

async function cmdSha256(args) {
  const [positionals] = splitArgs(args);
  const filePath = positionals[0];
  if (!filePath) fail('Usage: sha256 <file>');
  if (!existsSync(filePath)) fail(`File not found: ${filePath}`);
  const sha = await sha256OfFile(filePath);
  process.stdout.write(`${sha}\n`);
}

// ---- Cache ---------------------------------------------------------------

function loadCache(wikiRoot) {
  const path = getIngestCachePath(wikiRoot);
  if (!existsSync(path)) return {};
  try {
    return JSON.parse(readFileSync(path, 'utf-8'));
  } catch (err) {
    fail(`Cache file is corrupt: ${path} (${err.message})`);
    return {};
  }
}

function saveCache(wikiRoot, cache) {
  const path = getIngestCachePath(wikiRoot);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(cache, null, 2)}\n`, 'utf-8');
}

async function cmdCacheGet(args) {
  const [positionals] = splitArgs(args);
  const wikiRoot = resolveWikiRoot(positionals[0]);
  const rawPath = positionals[1];
  if (!rawPath) fail('Usage: cache-get <wiki-root> <raw-relative-path>');
  const cache = loadCache(wikiRoot);
  const entry = cache[rawPath];
  if (!entry) {
    process.stderr.write(`No cache entry for ${rawPath}\n`);
    process.exit(1);
  }
  process.stdout.write(`${JSON.stringify(entry, null, 2)}\n`);
}

async function cmdCacheSet(args) {
  const [positionals, flags] = splitArgs(args);
  const wikiRoot = resolveWikiRoot(positionals[0]);
  const rawPath = positionals[1];
  if (!rawPath) fail('Usage: cache-set <wiki-root> <raw-relative-path> [--json <file>]');

  let payload;
  if (flags.json) {
    try {
      payload = JSON.parse(readFileSync(flags.json, 'utf-8'));
    } catch (err) {
      fail(`Cannot read --json ${flags.json}: ${err.message}`);
    }
  } else {
    payload = await readJsonFromStdin();
  }

  if (!payload.sha256 || !Array.isArray(payload['atom-ids'])) {
    fail('Cache entry must include sha256 and atom-ids (array).');
  }

  const cache = loadCache(wikiRoot);
  cache[rawPath] = {
    sha256: payload.sha256,
    'ingested-at': payload['ingested-at'] || new Date().toISOString(),
    'atom-ids': payload['atom-ids'],
  };
  saveCache(wikiRoot, cache);
  process.stdout.write(`${getIngestCachePath(wikiRoot)}\n`);
}

async function readJsonFromStdin() {
  return new Promise((resolveFn, rejectFn) => {
    let buf = '';
    stdin.setEncoding('utf-8');
    stdin.on('data', (chunk) => { buf += chunk; });
    stdin.on('end', () => {
      if (!buf.trim()) return rejectFn(new Error('Empty stdin'));
      try { resolveFn(JSON.parse(buf)); } catch (err) { rejectFn(err); }
    });
    stdin.on('error', rejectFn);
  });
}

// ---- Next atom ID --------------------------------------------------------

const ATOM_ID_RE = /^atom-(\d{8})-(\d{3})$/;

function todayCompact(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}${m}${d}`;
}

async function cmdNextAtomId(args) {
  const [positionals, flags] = splitArgs(args);
  const wikiRoot = resolveWikiRoot(positionals[0]);
  const dateStr = flags.date || todayCompact();

  let maxN = 0;
  for (const branch of BRANCHES) {
    const dir = getBranchDir(wikiRoot, branch);
    if (!existsSync(dir)) continue;
    for (const file of readdirSync(dir)) {
      if (!file.endsWith('.md') || file.startsWith('_')) continue;
      // Extract id from the file's frontmatter — open the file
      const text = readFileSync(join(dir, file), 'utf-8');
      const idMatch = text.match(/^id:\s*(atom-\d{8}-\d{3})\s*$/m);
      if (!idMatch) continue;
      const match = idMatch[1].match(ATOM_ID_RE);
      if (!match) continue;
      if (match[1] === dateStr) {
        const n = parseInt(match[2], 10);
        if (n > maxN) maxN = n;
      }
    }
  }
  const nextN = String(maxN + 1).padStart(3, '0');
  process.stdout.write(`atom-${dateStr}-${nextN}\n`);
}

// ---- Slug ----------------------------------------------------------------

const SLUG_MAX = 60;

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, SLUG_MAX)
    .replace(/-$/, '');
}

async function cmdSlug(args) {
  const [positionals] = splitArgs(args);
  if (positionals.length === 0) fail('Usage: slug <claim>');
  const claim = positionals.join(' ');
  const slug = slugify(claim);
  if (!slug) fail(`Cannot derive a slug from: ${claim}`);
  process.stdout.write(`${slug}\n`);
}

// ---- Write atom ----------------------------------------------------------

async function cmdWriteAtom(args) {
  const [positionals, flags] = splitArgs(args);
  const wikiRoot = resolveWikiRoot(positionals[0]);
  const branch = positionals[1];
  const desiredSlug = positionals[2];

  if (!branch || !desiredSlug) {
    fail('Usage: write-atom <wiki-root> <branch> <slug> --body <body-file>');
  }
  if (!BRANCHES.includes(branch)) {
    fail(`Unknown branch: ${branch}. Expected one of: ${BRANCHES.join(', ')}`);
  }
  if (!flags.body) {
    fail('Missing --body <file>. Write the atom content (frontmatter + body) to a file and pass the path.');
  }
  if (!existsSync(flags.body)) {
    fail(`Body file not found: ${flags.body}`);
  }

  const branchDir = getBranchDir(wikiRoot, branch);
  mkdirSync(branchDir, { recursive: true });

  // Resolve collisions: if foo.md exists, try foo-2.md, foo-3.md, ...
  let slug = desiredSlug;
  let n = 2;
  while (existsSync(join(branchDir, `${slug}.md`))) {
    slug = `${desiredSlug}-${n}`;
    n++;
    if (n > 999) fail('Too many slug collisions; pick a different slug.');
  }

  const targetPath = join(branchDir, `${slug}.md`);
  const body = readFileSync(flags.body, 'utf-8');
  writeFileSync(targetPath, body, 'utf-8');

  const rel = relative(wikiRoot, targetPath).replace(/\\/g, '/');
  process.stdout.write(`${rel}\n`);
}

// ---- Provenance append ---------------------------------------------------

async function cmdAppendProvenance(args) {
  const [positionals, flags] = splitArgs(args);
  const wikiRoot = resolveWikiRoot(positionals[0]);

  const required = ['raw', 'source', 'date', 'origin', 'context', 'atoms'];
  for (const field of required) {
    if (!flags[field]) fail(`Missing --${field}`);
  }

  const provenancePath = getProvenancePath(wikiRoot);
  if (!existsSync(provenancePath)) {
    fail(`Provenance file not found: ${provenancePath}. Re-run bootstrap to scaffold it.`);
  }

  // Build the row. Escape pipes inside any field so the markdown table stays
  // well-formed. Newlines in any field are collapsed to spaces.
  const cells = required.map((field) => sanitiseCell(flags[field]));
  const row = `| ${cells.join(' | ')} |\n`;

  const existing = readFileSync(provenancePath, 'utf-8');
  // Append at end of file, ensuring a trailing newline before
  const padded = existing.endsWith('\n') ? existing : `${existing}\n`;
  writeFileSync(provenancePath, `${padded}${row}`, 'utf-8');
  process.stdout.write(`${relative(wikiRoot, provenancePath).replace(/\\/g, '/')}\n`);
}

function sanitiseCell(value) {
  return String(value).replace(/\|/g, '\\|').replace(/\r?\n+/g, ' ').trim();
}

// ---- Log append ----------------------------------------------------------

function todayIso(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

async function cmdAppendLog(args) {
  const [positionals] = splitArgs(args);
  const wikiRoot = resolveWikiRoot(positionals[0]);
  if (positionals.length < 2) {
    fail('Usage: append-log <wiki-root> "message text"');
  }
  const message = positionals.slice(1).join(' ');
  const logPath = join(wikiRoot, 'log.md');
  const today = todayIso();

  let existing = '';
  if (existsSync(logPath)) {
    existing = readFileSync(logPath, 'utf-8');
  } else {
    existing = '# Wiki Log\n\nAppend-only chronology of significant wiki events.\n';
  }

  // If today's date heading exists, append under it; else create a new heading
  const headingMarker = `## ${today}`;
  let updated;
  if (existing.includes(headingMarker)) {
    // Insert immediately after the today heading's newlines. Use [\r\n]+
    // because files may use CRLF line endings on Windows.
    const re = new RegExp(`(${headingMarker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\r\\n]+)`, '');
    updated = existing.replace(re, `$1- ${message}\n`);
  } else {
    const padded = existing.endsWith('\n') ? existing : `${existing}\n`;
    updated = `${padded}\n${headingMarker}\n\n- ${message}\n`;
  }
  writeFileSync(logPath, updated, 'utf-8');
  process.stdout.write(`${relative(wikiRoot, logPath).replace(/\\/g, '/')}\n`);
}

// ---- CLI dispatch --------------------------------------------------------

const COMMANDS = {
  sha256: cmdSha256,
  'cache-get': cmdCacheGet,
  'cache-set': cmdCacheSet,
  'next-atom-id': cmdNextAtomId,
  slug: cmdSlug,
  'write-atom': cmdWriteAtom,
  'append-provenance': cmdAppendProvenance,
  'append-log': cmdAppendLog,
};

function usage() {
  process.stderr.write(`Usage: node ingest-helpers.mjs <command> [args]\n\n`);
  process.stderr.write('Commands:\n');
  for (const name of Object.keys(COMMANDS)) {
    process.stderr.write(`  ${name}\n`);
  }
  process.stderr.write('\nSee the docstring at the top of ingest-helpers.mjs for usage.\n');
}

async function main() {
  const [cmd, ...rest] = argv.slice(2);
  if (!cmd || cmd === '--help' || cmd === '-h') {
    usage();
    process.exit(0);
  }
  const fn = COMMANDS[cmd];
  if (!fn) {
    process.stderr.write(`Unknown command: ${cmd}\n`);
    usage();
    process.exit(2);
  }
  try {
    await fn(rest);
  } catch (err) {
    process.stderr.write(`${err.message || err}\n`);
    process.exit(2);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}

// Library exports for any future JS callers
export {
  sha256OfFile,
  loadCache,
  saveCache,
  slugify,
  todayCompact,
  todayIso,
};
