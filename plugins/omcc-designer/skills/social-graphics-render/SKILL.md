---
name: social-graphics-render
description: "Renders raw zone images per variant for a social_graphics_spec.md by invoking codex-companion's image generation, with a variant-outer / zone-inner gate, versioned history, and dimension validation. Use this skill (or its /omcc-designer:start / /omcc-designer:social-graphics chain-tail dispatch) when the user wants automated image rendering for a multi-variant social-graphics spec produced by the social-graphics skill, with the codex plugin installed."
---

# Phase 4: Social Graphics Image Rendering

Render raw image assets for each image zone declared in
social_graphics_spec.md, **per variant**, using the codex CLI's
built-in imagegen tool via the codex-companion plugin. This skill
is a Phase 4 chain-tail to `social-graphics` — it runs after the
social-graphics skill returns, conditional on the user's opt-in via
the Tool dispatch decision (always prompted; never silent).

**Note on doc structure** — because this skill is invoked as a
chain-tail in nearly every real session, the procedure below is the
mainline doc; the "When auto-activated" / "When invoked by command"
sections at the end describe entry-point variations.

The codex invocation contract — pre-flight, command form, prompt
template, parsing rules, no-auto-regeneration rule, chain-specific
validation hook — is shared with `poster-render` and lives in
`skills/poster-render/references/codex-call-template.md`. This file
references that template; do not duplicate its content.

## Scope and boundary

This skill produces **raw zone images only** — no typography
composition, no layer flattening, no production-ready composite.
Each variant's Layer 2 (typography) remains a vector / overlay-
layer responsibility for the human designer or external tools.

This boundary preserves omcc-designer's identity as a
**specification authoring** plugin (not a production tooling
plugin) and aligns with the principle in
`skills/social-graphics/references/social-graphics-guide.md` —
"AI image generators cannot reliably render text" — text remains
Layer 2.

**Reinforcement for social formats**: the temptation to bake
headline / CTA / overlay text into the rendered image is high
for YT thumbnails and IG stories specifically. This skill MUST
NOT relax the text-free constraint for any variant. If a
generated image contains visible text and the user wants it,
that's a Layer 2 / external compositing decision — not a
re-render with different prompt language.

## Optional dependency: codex plugin

This skill depends on the **codex** plugin (same marketplace,
optional). This is an explicit, sanctioned cross-plugin
dependency (see `CLAUDE.md` "Cross-plugin sanctioned
dependencies").

If the codex plugin is not installed, or its runtime is incomplete:

- Do not error.
- Leave social_graphics_spec.md unchanged.
- Output a one-line notice: `"Codex plugin not installed or runtime
  incomplete — social-graphics rendering skipped. The
  social_graphics_spec.md contains image generation prompts for
  manual use with any image generation tool."`
- Exit clean.

Detection — three checks (all must pass), identical to
`poster-render`'s pre-flight:

1. The codex-companion script exists at any
   `~/.claude/plugins/cache/*/codex/*/scripts/codex-companion.mjs`
   (any marketplace, any installed version). Pick the highest
   version via `sort -V`.
2. Node.js is on PATH (`command -v node` succeeds).
3. The codex CLI itself is invokable: `codex --version` exits 0
   AND `codex app-server --help` exits 0.

If any check fails, run the graceful-degrade path above.

Note: the pre-flight does not detect codex authentication state —
authentication failures surface only at runtime (see Step 6 below).

## Tool dispatch decision (one prompt per render session — always)

Before entering the render loop, **always** prompt the user once,
regardless of the brief's `Image generation tools` field value.

**Runtime ordering**: this section is presented before the
"Variant set parsing and collision check" section below for
readability, but at runtime it MUST be invoked AFTER variant
set parsing has produced the resolved set (post empty-variant
skip). The K disclosure depends on the post-parse, post-empty-skip
total — running Tool dispatch before parsing would over-count if
any variant turns out to be empty.

Calculate the planned call count from the resolved set:
total = Σ (zones per variant) across all variants in the resolved
set (variants may have differing zone counts). Disclose this in
the prompt so the user can weigh codex API quota and time.

Field normalization: lowercase the value, split on commas, trim
whitespace per token. Match `codex` case-insensitively. Treat the
result as **empty** when it is missing, blank, `none`,
`none specified`, or composed only of stop-words.

Prompt wording by field state (substitute `<N variants>` and
`<K total renders>` from the spec):

- **Includes `codex`**: `"The brief lists codex among Image
  generation tools. Render zone images now via codex across <N
  variants> (<K total renders>)? (y) render with codex / (n) skip
  — the social_graphics_spec.md prompts remain available for
  manual use."`
- **Lists only non-codex tools**: `"The brief lists [<tools>] but
  not codex. Render anyway via codex across <N variants> (<K total
  renders>)? (y) render — note: codex output may differ from the
  listed tools' style / (n) skip"`
- **Empty / missing / `none specified`**: `"The brief has no Image
  generation tools specified. Render via codex across <N variants>
  (<K total renders>) now? (y) render / (n) skip — recommend
  updating the brief on next pass"`

Input validation: accept `y`, `yes`, `n`, `no` (case-insensitive).
Any other input → re-prompt. After 3 invalid attempts in a row,
treat as `n` and exit clean.

If the user chooses `n`, exit clean with the same fallback message
as the codex-not-installed path. Do not write any zone files.

## Variant id mapping

The spec text uses **kebab-case** canonical variant ids
(`instagram-post`, `instagram-story`, `youtube-thumbnail`) per
`skills/brief-generation/references/design-brief-spec.md`
"Target medium aliases".

The filesystem uses **snake_case** (one-way `s/-/_/g`):
`instagram-post` → `instagram_post/`. This skill applies the
mapping before any filesystem operation. The mapping is identical
in shape to the zone-id rule in
`skills/brief-generation/references/output-file-rules.md` (`Zone A`
→ `zone_a`).

## Variant set parsing and collision check

Before entering the render loop:

1. Parse the spec's variant H2 sub-blocks (`## Variant: <id>
   (<W>×<H>)`). Extract each variant's id, dimensions, and
   image-zone list (Layer 3).
2. Validate every variant id against the canonical whitelist. A
   non-whitelisted id is a fatal parse error — exit clean with a
   repair prompt naming the unknown id.
3. Detect duplicate variant ids — including aliases that
   normalize to the same canonical id. A collision is a fatal
   parse error — exit clean with a repair prompt naming both
   conflicting ids.
4. **Empty-variant skip**: if a variant defines zero image zones
   (Layer 3 has no zones), skip it entirely — do not invoke codex
   for that variant. Record `<variant-id> → 0 zones (skipped)`
   in the final summary.

The variant set after parsing + collision check + empty-skip is
the **resolved set** the loop iterates over.

## Per-variant, per-zone gate (2D loop)

For each variant in the resolved set (outer), for each image zone
in that variant's Layer 3 (inner), in spec order. The action set
is the gate table in Step 7 below — that table is the source of
truth for the available keys and their effects.

The 2D loop preserves all already-accepted (variant, zone) pairs
on abort. There is no per-variant abort key — Ctrl+C and the 3-
invalid-input fallback abort the entire 2D loop, mirroring
`poster-render`'s single-abort semantics.

### Step 1 — determine next version number `N`

Scan `<output-dir>/<variant_id_snake>/.history/<zone-id>/` for
files matching `v<N>(-suffix)?\.png` (suffixes include `-skipped`,
`-deferred`, `-loaded`, `-prior`, `-orphan`). Set
`N = max(<existing N values>) + 1`. If the directory is empty or
absent, `N = 1`. This rule is gap-tolerant.

The `-loaded` suffix is retained for backward compatibility; new
renders never produce this suffix. External PNG replacement is
the post-render drop rule documented in
`skills/brief-generation/references/output-file-rules.md`.

### Step 2 — resume / orphan handling (first entry of this variant × zone)

- If `<output-dir>/<variant_id_snake>/<zone-id>.png` exists from
  a prior session, **prompt the user before treating it as an
  orphan** — a previously-accepted PNG from a prior `/start` or
  `/social-graphics` invocation against the same project
  directory should not be silently demoted to history.
  Prompt: `"Detected existing PNG at
  <output-dir>/<variant_id_snake>/<zone-id>.png from a prior
  session. (r) re-render — archive existing as v<N>-prior.png /
  (k) keep — skip this (variant, zone) entirely (no re-render)
  / (a) abort the loop"`. Default on 3 invalid attempts: `k`
  (preserve work). On `r`, move the file to
  `<output-dir>/<variant_id_snake>/.history/<zone-id>/v<N>-prior.png`
  and increment N. On `k`, append a "kept (no re-render)" row
  to the final summary and proceed to the next zone. On `a`,
  exit the loop preserving all already-accepted state.
- Other orphan / partial cases (orphan in `.history/` with no
  final, partial render from interrupted prior session): same
  semantics as `poster-render` Step 2, scoped under the
  per-variant directory.

### Step 3 — compose the codex prompt

From the variant's zone Designer's Vision and Image Generation
Guide, append the two literal trailer lines defined in the
**Prompt template** section of
`skills/poster-render/references/codex-call-template.md`
(absolute-path save instruction + `SAVED_PATH=` return line). The
absolute target is per-variant:
`<output-dir>/<variant_id_snake>/.history/<zone-id>/v<N>.png`.

The absolute-path requirement is load-bearing — see the same
template file for the cwd-vs-repo-root resolution behavior.

### Step 4 — pick a prompt strategy

Based on the brief's Imagery approach (same logic as
`poster-render`):

- raster-intent (`photography`, `illustration`, `mixed`, etc.):
  prompt naturally.
- vector-friendly subject (small flat icon, geometric mark):
  append "Use the imagegen tool to produce a raster image; do
  not write a deterministic script."

### Step 5 — invoke codex-companion

Via Bash:

```
timeout 300 node <codex-companion-path> task --write --cwd <output-dir> "<prompt>"
```

- `--write` is mandatory.
- `--cwd <output-dir>` is informational (codex resolves to repo
  root anyway); the prompt's absolute path is the load-bearing
  target.
- `timeout 300` (5 minutes) bounds hangs. Exit code 124 → render
  failure for this variant × zone.

### Step 6 — parse and validate

Apply the **shared validation contract** from
`skills/poster-render/references/codex-call-template.md`
"Result parsing":

1. Capture the last `^SAVED_PATH=(.+)$` line; strip whitespace / CR.
2. Verify the captured path equals the requested absolute path.
3. Verify the file exists and `file <path>` reports "PNG image data".
4. Auth-failure detection (session-fatal).
5. Imagegen-not-available escape — exact counter semantics for
   the 2D loop:
   - Counter **increments** on each codex render that fails parse
     (Step 6 items 1-3) or returns no valid PNG.
   - Counter **resets to 0** when a codex render produces a valid
     PNG, regardless of the subsequent gate action.
   - Counter is **unchanged** by gate actions that did NOT invoke
     codex this iteration (`s/skip`, `d/defer`, `a/accept`).
   - Counter is **unchanged** by empty-variant skips (the variant
     was excluded by Variant set parsing — no codex call occurred).
   - When the counter reaches 3 in a row, **across any variant
     boundaries**, exit clean ("Codex imagegen tool unavailable
     in this build — rendering skipped"). Already-accepted
     (variant, zone) pairs are preserved.

#### Step 6b — dimension validation (chain-specific hook)

After the shared Step 6 PNG-type check, run dimension validation:

1. Determine the variant's expected dimensions from the spec's
   `## Variant: <id> (<W>×<H>)` header (e.g.,
   `instagram-post (1080×1080)` → `1080×1080`).
2. Probe the rendered file via the following fallback chain
   (try each in order; advance to the next on
   `command -v <tool>` failing OR the tool exiting non-zero OR
   stdout being unparseable):
   - `sips -g pixelWidth -g pixelHeight "$path"` (macOS) →
     parse `pixelWidth: <N>` and `pixelHeight: <N>` from stdout.
   - `identify -format "%w %h" "$path"` (ImageMagick — Linux,
     macOS via Homebrew) → parse two whitespace-separated ints.
   - `python3 -c 'import sys; from PIL import Image; im=Image.open(sys.argv[1]); print(im.size[0], im.size[1])' "$path"`
     (Pillow — passes the path via `sys.argv` so the shell
     expands `"$path"` correctly outside the Python `-c` string).
3. Compare actual vs expected. Four outcomes:
   - **Exact match**: no annotation. Proceed to Step 7 normally.
   - **Mismatch**: record annotation
     `dim mismatch: actual <W>×<H> vs expected <W>×<H>`. Step 7
     prepends this to the gate prompt. Do NOT auto-retry, do NOT
     re-invoke codex — the user's `e` action is the natural retry
     path. This preserves the no-auto-regeneration rule.
   - **Probe failed** (probe tool was present but exited non-zero
     or returned unparseable output — likely the rendered file is
     corrupt / truncated / wrong format): record annotation
     `dim check: probe failed — file may be corrupt`. Step 7
     prepends this; the user can still accept (their judgment
     overrides) but is informed of the corruption signal.
   - **All probe tools absent** (none of the three is installed):
     record annotation `dim check: skipped (no validation tool)`.
     Step 7 prepends this. The user can still accept the file —
     **never block** on the absence of a probe tool.

Dimension validation is **advisory** — the gate user can still
`a/accept` a mismatched file (e.g., user judges the composition
acceptable despite scaling, or platform tolerates the off-spec
output). The annotation surfaces the discrepancy; the decision
remains user-controlled.

### Step 7 — present and gate

Present the version to the user (a preview of the rendered PNG)
along with any Step 6b annotation. Wait for the gate decision via
one of the actions below:

| Key | Action | Effect (success path — `v<N>.png` exists) |
|---|---|---|
| `a` / `accept` | Accept | Copy `<output-dir>/<variant_id_snake>/.history/<zone-id>/v<N>.png` to `<output-dir>/<variant_id_snake>/<zone-id>.png` (overwriting any prior final). The history file remains. Proceed to the next zone. |
| `e` / `edit` | Regenerate (optional edit) | Display the prefilled prompt for editing; submit it (with or without changes) to regenerate. The previous version stays in `.history`; the new version becomes `v<N+1>`. |
| `s` / `skip` | Skip this zone | Rename `v<N>.png` to `v<N>-skipped.png` under the variant's `.history`. No final `<zone-id>.png` for this variant × zone. Proceed to the next zone. |
| `d` / `defer` | Defer (skip with reminder) | Rename `v<N>.png` to `v<N>-deferred.png` under the variant's `.history`. Append a "deferred — re-render recommended" row to the final summary table. Proceed to the next zone. |

When a Step 6b annotation is present, the gate prompt prepends:

```
[<variant>] zone <zone-id> v<N>: dim mismatch: actual <W>×<H> vs expected <W>×<H>
```

or

```
[<variant>] zone <zone-id> v<N>: dim check: skipped (no validation tool)
```

The action set is unchanged. `e/edit` regenerates with the
existing prompt; the regenerated `v<N+1>.png` undergoes the same
Step 6b check and the gate fires again.

**Input validation** — accept the keys `a/e/s/d` (case-insensitive
single letter or spelled-out word). Validator rejects `a` when no
`v<N>.png` exists. Any other input → re-prompt the gate. After 3
invalid attempts in a row, abort the entire 2D loop — exit clean
per "Aborting the loop" below.

**External PNG replacement** — manual file drops at
`<output-dir>/<variant_id_snake>/<zone-id>.png` are documented in
`skills/brief-generation/references/output-file-rules.md` as a
post-render drop rule, not a gate action.

**Aborting the loop** — press Ctrl+C, or exhaust the 3-invalid-
input fallback. Already-accepted (variant, zone) pairs across
**all variants** are preserved (the per-variant final
`<zone-id>.png` files survive). Pending versions in
`<variant_id_snake>/.history/` are also preserved. The loop does
not roll back any prior variant when aborted in a later variant.

**Recovery after a render failure** — same shape as
`poster-render`. The gate offers `e/s/d` only (no `a`); `e`
triggers a fresh render attempt; the new attempt's slot is
computed by Step 1 (gap-tolerant). Failure-path summary rows are
annotated `(no render)`.

### After all (variant, zone) pairs complete

Present a summary table with one row per (variant, zone):

| Variant | Zone | Action | Final filename | Dim status |
|---------|------|--------|---------------|------------|
| `instagram-post` | `zone_a` | accepted | `instagram_post/zone_a.png` | ok |
| `instagram-post` | `zone_b` | deferred | (none — recommend re-render) | n/a |
| `instagram-story` | `zone_a` | accepted | `instagram_story/zone_a.png` | mismatch (1024×1024 vs 1080×1920) |
| `youtube-thumbnail` | `zone_a` | skipped | (none) | n/a |
| ... | ... | ... | ... | ... |

The `Dim status` column reflects Step 6b's annotation at the time
of the gate. If the user accepted a mismatched render, the row
shows `mismatch (<actual> vs <expected>)` — the user knows what
they accepted.

There is no in-loop re-entry — the gate is single-pass across the
entire 2D set.

## Concurrent renders not supported

This skill assumes a single render session per `<output-dir>` at
a time. Running two `/start` or `/social-graphics` invocations
against the same project directory concurrently produces races on
the per-variant version counter and on the per-variant final
filename, with no defense in this spec. The user is responsible
for serialization.

## File layout

Inside the project directory:

```
./output/<date>_<project>/
├── social_graphics_spec.md           # unchanged input
├── design_brief.md                   # unchanged input
├── instagram_post/                   # per-variant subdirectory (snake_case)
│   ├── zone_a.png                    # current final per zone
│   ├── zone_b.png
│   └── .history/
│       ├── zone_a/
│       │   ├── v1.png
│       │   ├── v2.png                # second render after edit
│       │   └── v3-skipped.png
│       └── zone_b/
│           └── v1.png
├── instagram_story/
│   └── (same structure)
└── youtube_thumbnail/
    └── (same structure)
```

Rules:

- `<variant_id_snake>` is the snake_case form of the canonical
  kebab-case variant id (`s/-/_/g`, one-way).
- `<zone-id>` is the lowercase identifier from the variant's zone
  table inside its H2 sub-block.
- Every codex render writes `v<N>.png` (no suffix) under the
  per-variant `.history/<zone-id>/`. N is per (variant, zone).
- Existing versions are never overwritten; suffixed files are
  also counted by Step 1.
- On `accept`: copy the latest `v<N>.png` to
  `<variant_id_snake>/<zone-id>.png`.
- On `skip`/`defer`: rename the latest version with the
  appropriate suffix; no final per-variant `<zone-id>.png`.
- On Ctrl+C (mid-loop abort): leave history files in place; the
  per-variant final exists only for already-accepted (variant,
  zone) pairs.

## Codex companion call pattern

See `skills/poster-render/references/codex-call-template.md` for:

- The exact companion command form
  (`timeout 300 node <companion> task --write --cwd <out> '<prompt>'`).
- The absolute-path requirement and the cwd-vs-repo-root behavior.
- The `SAVED_PATH=` literal and last-match parsing rules.
- The two-step image storage path
  (`~/.codex/generated_images/<thread>/...` → absolute target).
- The imagegen-vs-script dispatch caveat.
- The "Chain-specific validation hook" section (which authorizes
  this skill's Step 6b dimension validation).

## Output language

Gate prompts and user-facing messages follow the user's request
language. The codex prompt itself follows the variant's
Designer's Vision language — usually English, which the imagegen
tools handle best.

---

## When auto-activated (without /start or /social-graphics command)

The user invokes the skill directly, supplying (or letting it
discover) a social_graphics_spec.md path. Apply the full
procedure above. Requires both social_graphics_spec.md and a
sibling design_brief.md in the same directory.

If design_brief.md is absent, ask the user to provide it or to
specify the Image generation tools field interactively
(comma-separated tool list, or `none`). If the user types
`cancel` or leaves the input empty 3 times in a row, exit clean.

## When invoked by command (/start, /social-graphics)

`commands/start.md` Phase 4 and `commands/social-graphics.md`
Optional chain both dispatch this skill as a chain-tail after the
`social-graphics` skill returns, **always** running the Tool
dispatch decision prompt above.

If the user chooses to skip in the Tool dispatch decision, this
skill exits clean and the pipeline completes with
social_graphics_spec.md only.

The pipeline's "✓ Design pipeline complete." message is emitted
by `commands/start.md` after this skill returns. For
`/social-graphics`, the completion message is emitted by
`commands/social-graphics.md`.
