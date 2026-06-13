---
name: gitflow-diagram
description: |
  Generate publication-ready SVG gitflow diagrams from JSON, YAML, plain English,
  or git log input. This skill handles auto-layout of commit nodes, branch tracks,
  fork curves, merge connections, rebase annotations, cherry-pick indicators,
  annotation callouts, and branch labels. Use this skill whenever the user asks
  for a git diagram, branch visualisation, commit history chart, gitflow diagram,
  branching strategy diagram, or any SVG diagram of git branches, merges, rebases,
  feature branches, release branches, or hotfixes. Also trigger when the user
  provides a git log output and wants it visualised, or describes a branching
  workflow in plain English and wants a diagram.
---

# Gitflow SVG Diagram Skill

## Coordinate System

| Axis | Direction | Origin | Viewer Z |
|------|-----------|--------|----------|
| X    | Right     | Top-left | Toward viewer |
| Y    | Down      | Top-left | Toward viewer |

**Viewer perspective rule:** Arc direction is judged from the viewer's eye (Z toward viewer), not mathematical orientation. "Top-right arc" curves **down and right** on screen (increasing X, increasing Y).

- `sweep-flag=1` = clockwise on screen
- `sweep-flag=0` = counter-clockwise on screen

## Base Grid Unit

Define `g` (grid pitch) as the base spacing unit. Default `g = 80`. All coordinates are integer multiples of `g/4`.

```
r_node      = g / 4      # regular commit node radius (default 20)
r_special   = g / 2      # special node radius (default 40)
track_w     = g / 2      # branch track stroke-width (default 40)
track_rx    = g * 3      # fork curve Bezier radius X
track_ry    = g * 2      # fork curve Bezier radius Y
branch_dy   = g * 3      # perpendicular offset for forked branches
```

## Node Definitions

Add these to the SVG `<defs>` section:

```svg
<g id="commit-node" fill="currentColor" stroke="none">
  <circle cx="0" cy="0" r="20"/>
</g>

<g id="special-node" fill="currentColor" stroke="white" stroke-width="3">
  <circle cx="0" cy="0" r="40"/>
</g>

<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3"
        orient="auto" markerUnits="strokeWidth">
  <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
</marker>
```

## Branch Track Rendering

A branch is a thick stroke with rounded caps. Commits are centred on the track centreline.

```svg
<line x1="x1" y1="y" x2="x2" y2="y"
      stroke="currentColor" stroke-width="40" stroke-linecap="round"/>
```

## Fork Curve Algorithm

Connect parent branch to child branch with a smooth S-curve using a cubic Bezier.

**Horizontal flow, child above parent:**

```svg
<path d="M x_fork y_parent
         C x_fork y_child, x_fork y_child, x_fork+track_rx y_child"
      fill="none" stroke="currentColor" stroke-width="40" stroke-linecap="round"/>
```

**Vertical flow:** Swap X and Y roles.

## Merge Connections

Merges **must be exact mirrors of forks** — arc → vertical → arc, traversed upward. Never use straight lines. Distinguish merges from forks with `stroke-dasharray="5 3"`.

### Column Allocation Rule (Critical)

Each fork and each merge occupies a **vertical column** at `x = node_x + 2*r_node`. If a fork column and a merge column would overlap, **shift all nodes to the right of the overlap rightward** until every fork and merge has its own column.

```
Fork column:   x_fork   = parent_fork_x  + 2*r
Merge column:  x_merge  = child_last_x   + 2*r

if x_merge overlaps any existing fork column:
    shift child_last_x and all subsequent nodes right by g (or more)
    recompute x_merge
```

### Mirror-Pattern Merge (standard)

A merge is the fork pattern flipped vertically:

1. **Bottom-right arc** (r=20) from child right edge, curving up-right
2. **Vertical line** up at `x = child_last_x + 2*r`
3. **Top-left arc** (r=20) into parent left edge

```svg
<!-- feature/login (last node at 420,420) merging into develop (500,260) -->
<path d="M 440 420 A 20 20 0 0 1 460 400" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="5 3"/>
<line x1="460" y1="400" x2="460" y2="280" stroke="#555" stroke-width="2" stroke-dasharray="5 3"/>
<path d="M 460 280 A 20 20 0 0 1 480 260" fill="none" stroke="#555" stroke-width="2"
      stroke-dasharray="5 3" marker-end="url(#arrow)"/>
```

**Geometric constraint:** For the mirror pattern to close cleanly with r=20 quarter circles, the parent merge commit must sit at `parent_x = child_last_x + 4*r` (80 px to the right of the child branch's last node). If this conflicts with existing develop commits, insert the merge commit as a new node on the develop track.

### Vertical Merge (same x column)

When child and parent share the same x column (e.g. release → main), use a larger radius for the final arc:

```svg
<!-- release (980,420) merging into main (1020,100) -->
<path d="M 1000 420 A 20 20 0 0 0 980 400" ... />   <!-- bottom-left arc -->
<line x1="980" y1="400" x2="980" y2="140" ... />   <!-- vertical -->
<path d="M 980 140 A 40 40 0 0 0 940 100" ... />   <!-- top-left arc, r=40 -->
```

### Multi-Parent Merge (Type C)

Both parent branches curve into the merge commit node.

```svg
<!-- Parent 1 arc into merge node -->
<path d="M x1 y1 A r r 0 0 0 x_merge-r y_merge" ... />
<!-- Parent 2 arc into merge node -->
<path d="M x2 y2 A r r 0 0 1 x_merge y_merge-r" ... />
```

## Rebase Rendering

1. Special node on the feature branch at the rebase point.
2. Diagonal dotted arrow from special node pointing to target commit on base branch.
3. Optional label (e.g. "rebase onto main").

```svg
<use href="#special-node" x="x_rebase" y="y_rebase" fill="branch_color"/>
<line x1="x_rebase" y1="y_rebase" x2="x_target" y2="y_target"
      stroke="#666" stroke-width="2" stroke-dasharray="4 4" marker-end="url(#arrow)"/>
```

## Cherry-Pick / Cross-Branch Copy

Dotted stroke between original and copied commit with a label.

```svg
<line x1="x_source" y1="y_source" x2="x_dest" y2="y_dest"
      stroke="currentColor" stroke-width="2" stroke-dasharray="4 2"/>
<text x="mid_x" y="mid_y - 10" font-size="10" fill="#666">cherry-pick</text>
```

## Annotation Callouts

Group commits with a dotted bracket and descriptive text.

1. Identify leftmost and rightmost commits in the group.
2. Draw vertical drops from each end commit down to bracket level.
3. Draw horizontal bracket connecting the drops.
4. Draw vertical drop from bracket centre to text baseline.
5. Render text label.

```svg
<line x1="x_left"  y1="y_commit-r" x2="x_left"  y2="y_text+20" stroke="#666" stroke-dasharray="3 3"/>
<line x1="x_right" y1="y_commit-r" x2="x_right" y2="y_text+20" stroke="#666" stroke-dasharray="3 3"/>
<line x1="x_left"  y1="y_text+20"  x2="x_right" y2="y_text+20" stroke="#666" stroke-dasharray="3 3"/>
<text x="(x_left+x_right)/2" y="y_text" text-anchor="middle" font-size="12" fill="#333">Label</text>
```

## Label Positioning

### Branch Labels

Below the branch track (horizontal flow) or to the left (vertical flow), rotated 30 degrees pointing toward the node centre.

```svg
<text x="x_node" y="y_node + r_special + 20"
      transform="rotate(30, x_node, y_node + r_special + 20)"
      font-family="monospace" font-size="11" fill="#444">branch-name</text>
```

### Commit Labels (SHAs / Messages)

To the left of the node for horizontal flow, horizontally aligned.

```svg
<text x="x_node - r_node - 8" y="y_node + 4"
      text-anchor="end" font-family="monospace" font-size="9" fill="#666">abc1234</text>
```

## Standard Colour Conventions

| Branch Type | Track/Node Fill | Stroke | Icon |
|-------------|-----------------|--------|------|
| `main` / `master` | `#e04040` | `#c03030` | `git-commit` |
| `develop` | `#40a0e0` | `#3080c0` | `git-commit` |
| `feature/*` | `#40c040` | `#30a030` | `git-branch` |
| `release/*` | `#e0a040` | `#c08030` | `tag` |
| `hotfix/*` | `#e040e0` | `#c030c0` | `git-merge` |
| Remote tracking | Same as local | dashed `stroke-dasharray="6 4"` | `cloud` |
| Merge commit | Same branch | `fill="#333"` | `git-merge` |
| HEAD | `#ffcc00` | `#cc9900` | `arrow-right` |

**Override rule:** If a `DESIGN.md` file is present, read its `tokens.colors` or `brand` section and use those values instead.

## Tabler Icons

Embed as SVG `<symbol>` definitions in `<defs>`.

| Icon ID | Tabler Name | Usage |
|---------|-------------|-------|
| `icon-git-commit` | `git-commit` | Regular commit nodes |
| `icon-git-branch` | `git-branch` | Branch points, feature branches |
| `icon-git-merge` | `git-merge` | Merge commits |
| `icon-git-pull-request` | `git-pull-request` | PR annotations |
| `icon-tag` | `tag` | Release tags |
| `icon-arrow-right` | `arrow-right` | HEAD pointer, flow direction |
| `icon-cloud` | `cloud` | Remote branch indicator |

Render inside nodes with:
```svg
<use href="#icon-{name}" x="-12" y="-12" width="24" height="24" fill="white"/>
```

### Handling Unspecified Icons

When a branch type or element needs an icon not listed above:

1. **Search Tabler Icons:** Visit `https://tabler.io/icons` and search by keyword. The URL slug is the ID.
2. **Embed as symbol:** Add the SVG path as a new symbol following the naming convention `icon-{tabler-name}`.
3. **Fallback rule:** If no suitable icon exists, use `git-commit` for all commit nodes and a plain `circle` dot for unknown branch indicators.
4. **Custom icons:** For project-specific icons, embed the full SVG path inline inside the node group at `transform="translate(-12, -12) scale(0.05)"`.

## Layout Engine (Auto-Grid)

### Input JSON Schema

```json
{
  "direction": "horizontal",
  "aspect_ratio": "1:sqrt2",
  "branches": [
    {
      "name": "main",
      "type": "main",
      "base_commit": null,
      "commits": ["a1b2c3d", "e4f5g6h", "i7j8k9l"]
    },
    {
      "name": "feature/login",
      "type": "feature",
      "base_commit": "e4f5g6h",
      "commits": ["m1n2o3p", "q4r5s6t"],
      "merged_into": "i7j8k9l"
    }
  ],
  "annotations": [
    {"commits": ["m1n2o3p", "q4r5s6t"], "text": "Login feature work"}
  ]
}
```

### Algorithm

```
function layout(diagram):
  g = diagram.grid_pitch || 80
  direction = diagram.direction || "horizontal"

  // Step 1: Position main branch
  main = find_branch(type="main")
  main.y = 0
  for i, commit in main.commits:
    commit.x = i * g
    commit.y = main.y
    commit.r = g/4

  // Step 2: Position child branches
  branch_index = 1
  for branch in branches where branch.base_commit:
    base = find_commit(branch.base_commit)
    branch.fork_x = base.x
    branch.fork_y = base.y
    branch.y = base.y - branch_index * (g * 3)
    for j, commit in branch.commits:
      commit.x = branch.fork_x + (j + 1) * g
      commit.y = branch.y
      commit.r = g/4
    branch_index++

  // Step 3: Position merge points
  for branch in branches where branch.merged_into:
    target = find_commit(branch.merged_into)
    merge_commit = create_merge_commit(branch, target)
    merge_commit.x = target.x
    merge_commit.y = (branch.y + target.y) / 2
    merge_commit.r = g/2

  // Step 4: Compute canvas bounds
  min_x = min(all commits.x - r) - g
  max_x = max(all commits.x + r) + g
  min_y = min(all commits.y - r) - g
  max_y = max(all commits.y + r) + g * 4

  // Step 5: Apply aspect ratio
  width = max_x - min_x
  height = max_y - min_y
  if aspect == "1:sqrt2" and width/height > 1/sqrt(2):
    height = width * sqrt(2)
  else if aspect == "sqrt2:1" and height/width > 1/sqrt(2):
    width = height * sqrt(2)

  return {commits, branches, bounds}
```

### Rendering Order (Painter's Algorithm)

1. Branch tracks
2. Fork curves
3. Commit nodes
4. Icons inside nodes
5. Special nodes
6. Connection arrows
7. Annotation callouts
8. Labels and text

## Input Parsers

### Plain English

Use keyword extraction:
- `branch off {commit}` / `fork from {commit}` → creates feature branch
- `merge into {branch}` → merge connection
- `rebase onto {commit}` → rebase annotation
- `cherry-pick {commit} into {branch}` → cherry-pick connection
- `{N} commits` → creates N commit nodes on current branch

### Git Log

Parse `git log --graph --oneline --decorate --all` output:
- `*` = commit
- `|` = vertical branch line
- `/` and `\` = merge forks
- `()` = branch names (decorators)

### YAML

```yaml
direction: horizontal
aspect_ratio: 1:sqrt2
branches:
  - name: main
    type: main
    commits:
      - abc123: Initial commit
      - def456: Add CI
      - ghi789: Release v1.0
  - name: feature/auth
    type: feature
    base: def456
    commits:
      - jkl012: Add login
      - mno345: Add OAuth
    merged_into: ghi789
annotations:
  - commits: [jkl012, mno345]
    text: Authentication feature
```

## Output Format

Generate a **single self-contained `.svg` file** with:
- All definitions in `<defs>`
- No external dependencies (icons embedded as symbols)
- `viewBox` computed from layout bounds
- `width` and `height` matching the viewBox for 1:1 pixel mapping
- Optional `<style>` block for hover effects

## Quality Checklist

Before returning the SVG, verify:
- [ ] All commit nodes are centred on their branch tracks
- [ ] Fork curves are smooth (no sharp corners at track junctions)
- [ ] Merge arcs meet the target node exactly on its stroke
- [ ] No overlapping nodes (minimum spacing = g)
- [ ] Aspect ratio matches requested format
- [ ] All branch labels are readable
- [ ] Annotation brackets clearly group their commits
- [ ] HEAD pointer is visible and points to the correct commit
- [ ] Colours match conventions or DESIGN.md override
