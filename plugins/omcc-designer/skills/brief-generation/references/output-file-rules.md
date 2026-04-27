# Output File Rules

Shared output-file conventions for skills that write design documents
(`brief-generation`, `poster`, `design-planning`, `poster-render`, and
future domain skills).

## Directory structure

Each design project is saved in its own directory:

```
./output/YYYY-MM-DD_project-name/
├── design_brief.md
├── poster_spec.md
├── design_plan.md
├── zone_a.png             # rendered images (poster-render chain only)
├── zone_b.png
├── ...
└── .history/              # versioned render history (poster-render only)
    ├── zone_a/
    │   ├── v1.png
    │   └── ...
    └── ...
```

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

- **Document filenames** within the directory are fixed: design_brief.md,
  poster_spec.md, design_plan.md.
- **Asset filenames** (e.g., rendered zone PNGs from `poster-render`)
  follow per-skill conventions — see the subsections below.
- **Naming convention**: multi-word filenames use `snake_case` (lowercase with
  underscore separator). Single-word filenames stay lowercase. Apply this rule
  when introducing new output file types.
- Do not use `_2`, `_3` suffixes for documents. Separate projects by
  directory. Asset filenames follow their own per-skill versioning rules
  (see `Rendered zone images` below).

### Rendered zone images (`poster-render` chain only)

- `<zone-id>.png` — current final version per zone (accepted render or manually replaced; e.g., `zone_a.png`).
- `<zone-id>` is the lowercase identifier from the poster_spec.md zone
  table: Zone A → `zone_a`, Zone B → `zone_b`, etc.
- `.history/<zone-id>/v1.png`, `v2.png`, ... — every render produces a
  new versioned file under `.history/<zone-id>/`. Versions are never
  overwritten; the chosen final is copied (not moved) to the top-level
  `<zone-id>.png` on accept.
- The `.history/` directory may be added to project-level `.gitignore`
  if the project uses git, since render artifacts can be regenerated
  from the spec at any time.

## Overwrite protection

If the target output directory already exists, ask the user before overwriting.

Per-asset overrides:

- Rendered zone PNGs (`poster-render` skill): the per-zone gate's
  `accept` action unconditionally overwrites `<zone-id>.png` — the
  user explicitly chose to promote the new version. The directory-level
  prompt does not apply to this per-zone overwrite.
- `.history/` files are append-only by spec design — every render
  writes a new `v<N>.png` and never overwrites an existing version.
- Manual external-PNG drops at `<output-dir>/<zone-id>.png` (per the
  post-render drop rule below) are an explicit user gesture and
  override any prior render without prompting.

## External PNG replacement (post-render drop rule)

To replace a rendered zone with an external PNG, drop the file
directly at `<output-dir>/<zone-id>.png`. This is a manual file
operation, not a per-zone gate action.

- **Timing**: drop the PNG **after** the render loop completes (or
  after pressing `s`/skip on the specific zone). If dropped while
  the loop is still running, the final summary may still report the
  in-loop action (`accepted` / `skipped` / `deferred`) for that zone
  — the summary reflects gate-time decisions, not later filesystem
  state.
- **Overwrite**: dropping a PNG at the top-level `<zone-id>.png`
  overrides any previously accepted render. The corresponding
  `.history/<zone-id>/v<N>.png` files are not touched by the drop.
- **Rollback semantics**: on a future re-render of the same zone,
  the per-zone gate's Step 2 will treat the dropped PNG as a
  prior-session final and archive it as
  `.history/<zone-id>/v<N>-prior.png`. (The legacy `-loaded` suffix
  is no longer produced — see Step 1's backward-compat note in
  `skills/poster-render/SKILL.md`.)

## Other

- Create the `output` directory if it does not exist.
- File encoding: UTF-8
