# Output File Rules

Shared output-file conventions for skills that write design documents
(`brief-generation`, `poster`, `design-planning`, `poster-render`,
`social-graphics`, `social-graphics-render`, and future domain
skills).

## Directory structure

Each design project is saved in its own directory. The brief is
always present; the domain spec and render artifacts depend on
which pipeline ran.

**Single-canvas pipeline** (e.g., `poster` + `poster-render`):

```
./output/YYYY-MM-DD_project-name/
├── design_brief.md
├── poster_spec.md
├── design_plan.md          # if /omcc-designer:plan ran
├── zone_a.png              # rendered images (poster-render chain)
├── zone_b.png
├── ...
└── .history/               # versioned render history
    ├── zone_a/
    │   ├── v1.png
    │   └── ...
    └── ...
```

**Multi-variant pipeline** (e.g., `social-graphics` +
`social-graphics-render`):

```
./output/YYYY-MM-DD_project-name/
├── design_brief.md
├── social_graphics_spec.md      # single doc with H2 variant sub-blocks
├── design_plan.md               # if /omcc-designer:plan ran
├── instagram_post/              # one directory per variant (snake_case)
│   ├── zone_a.png               # rendered images (social-graphics-render chain)
│   ├── zone_b.png
│   └── .history/
│       └── zone_a/v1.png ...
├── instagram_story/
│   └── ...
└── youtube_thumbnail/
    └── ...
```

A given project directory holds one pipeline's spec at a time
(driven by the brief's canonical `Target medium`); the two trees
above are not expected to coexist.

## Directory naming

- `YYYY-MM-DD` is the project creation date.
- `project-name` is derived from the project title collected in Phase 2 (max 15 characters).
- If the project name is unknown, use time-based fallback: `YYYY-MM-DD_HHMM`

## Directory name sanitization

Before using a project name as a directory component, apply these rules:
- `/` → `-` (hyphen)
- Spaces → `_` (underscore)
- Remove filesystem-forbidden characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)
- If longer than 15 characters, truncate at 15 and remove trailing `_`

## Filenames

- **Document filenames** within the directory are fixed:
  design_brief.md, poster_spec.md, social_graphics_spec.md,
  design_plan.md.
- **Asset filenames** (e.g., rendered zone PNGs from chain-tail
  render skills like `poster-render` or `social-graphics-render`)
  follow the shared conventions in `Rendered zone images` below.
  Both single-canvas and multi-variant forms are documented there.
- **Naming convention**: multi-word filenames use `snake_case` (lowercase with
  underscore separator). Single-word filenames stay lowercase. Apply this rule
  when introducing new output file types.
- Do not use `_2`, `_3` suffixes for documents. Separate projects by
  directory. Asset filenames follow their own per-skill versioning rules
  (see `Rendered zone images` below).

### Rendered zone images (chain-tail render skills)

These conventions apply to all chain-tail render skills
(`poster-render`, `social-graphics-render`, and future render
chains). The form depends on whether the source spec defines
multi-variant `## Variant:` H2 sub-blocks (the spec's structural
discriminator — `Variants:` is a brief field, not a spec field;
the spec carries the variant set as H2 sub-blocks instead).

**Single-canvas form** (source spec has no `## Variant:` H2
sub-blocks — e.g., poster_spec.md):

- `<output-dir>/<zone-id>.png` — current final version per zone
  (accepted render or manually replaced; e.g., `zone_a.png`).
- `<output-dir>/.history/<zone-id>/v1.png`, `v2.png`, ... —
  versioned history per zone.

**Multi-variant form** (source spec defines `## Variant: <id>
(<W>×<H>)` H2 sub-blocks — e.g., social_graphics_spec.md):

- `<output-dir>/<variant_id>/<zone-id>.png` — current final per
  zone, scoped under the per-variant directory.
- `<output-dir>/<variant_id>/.history/<zone-id>/v1.png`, `v2.png`,
  ... — versioned history per variant × zone.
- `<variant_id>` on the filesystem is the **snake_case** form of
  the canonical kebab-case variant id (e.g., spec text
  `instagram-post` → filesystem `instagram_post/`). Translation
  is `s/-/_/g`, one-way. The canonical kebab list is defined in
  `skills/brief-generation/references/design-brief-spec.md`
  "Target medium aliases".

**Common rules** (both forms):

- `<zone-id>` is the lowercase snake_case identifier from the
  spec's zone table: Zone A → `zone_a`, Zone B → `zone_b`, etc.
- Versions are never overwritten; the chosen final is copied
  (not moved) to the top-level `<zone-id>.png` (or
  `<variant_id>/<zone-id>.png`) on accept.
- The `.history/` directory may be added to project-level
  `.gitignore` if the project uses git, since render artifacts
  can be regenerated from the spec at any time.

**Backward compatibility — poster-render**: existing poster
projects that produced `<output-dir>/zone_a.png` and
`<output-dir>/.history/zone_a/v1.png` continue to work unchanged.
The multi-variant form applies only to chain-tails whose source
spec defines `## Variant:` H2 sub-blocks. `poster-render` never
produces the multi-variant form (poster_spec.md has no variant
sub-blocks).

### Variant id normalization and collision

When a spec contains `## Variant:` H2 sub-blocks:

- Variant ids in spec text use kebab-case from the canonical
  whitelist (`instagram-post`, `instagram-story`,
  `youtube-thumbnail`). Filesystem representation translates to
  snake_case via `s/-/_/g`, one-way.
- A spec MUST NOT contain two variants whose canonical
  (post-alias-normalized) ids collide. The chain-tail MUST detect
  collisions at the spec-parsing step and surface a repair prompt
  before invoking codex — never silently merge or rename.
- Aliases that normalize to the same canonical id (e.g.,
  `Instagram Post` vs `instagram-post`) are also a collision for
  this rule. Alias normalization is brief-generation's
  responsibility, but defensive collision detection at the
  chain-tail catches malformed briefs.

## Overwrite protection

If the target output directory already exists, ask the user before overwriting.

Per-asset overrides:

- Rendered zone PNGs (chain-tail render skills — `poster-render`,
  `social-graphics-render`, etc.): the per-zone gate's `accept`
  action unconditionally overwrites the final zone PNG (or, for
  multi-variant chains, `<variant_id>/<zone-id>.png`) — the user
  explicitly chose to promote the new version. The directory-level
  prompt does not apply to this per-zone overwrite.
- `.history/` files are append-only by spec design — every render
  writes a new `v<N>.png` and never overwrites an existing version.
- Manual external-PNG drops at `<output-dir>/<zone-id>.png` or
  `<output-dir>/<variant_id>/<zone-id>.png` (per the post-render
  drop rule below) are an explicit user gesture and override any
  prior render without prompting.

## External PNG replacement (post-render drop rule)

To replace a rendered zone with an external PNG, drop the file
directly at the zone's final-PNG path. This is a manual file
operation, not a per-zone gate action.

Drop paths:

- **Single-canvas chain (poster-render)**:
  `<output-dir>/<zone-id>.png`
- **Multi-variant chain (social-graphics-render)**:
  `<output-dir>/<variant_id>/<zone-id>.png`

Rules:

- **Timing**: drop the PNG **after** the render loop completes (or
  after pressing `s`/skip on the specific zone). If dropped while
  the loop is still running, the final summary may still report the
  in-loop action (`accepted` / `skipped` / `deferred`) for that
  zone (or variant × zone) — the summary reflects gate-time
  decisions, not later filesystem state.
- **Overwrite**: dropping a PNG at the final-PNG path overrides any
  previously accepted render. The corresponding
  `.history/<zone-id>/v<N>.png` (or
  `<variant_id>/.history/<zone-id>/v<N>.png`) files are not touched
  by the drop.
- **Rollback semantics**: on a future re-render of the same
  (variant ×) zone, the per-zone gate's Step 2 will treat the
  dropped PNG as a prior-session final and archive it as
  `.history/<zone-id>/v<N>-prior.png` (or under the variant
  directory). The legacy `-loaded` suffix is no longer produced.
  See the chain's own SKILL.md ("Step 2 — resume / orphan
  handling") for the canonical contract.

## Other

- Create the `output` directory if it does not exist.
- File encoding: UTF-8
