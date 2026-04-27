---
name: poster-render
description: "Renders raw zone images for a poster_spec.md by invoking codex-companion's image generation, with per-zone confirmation gates and versioned history. Use this skill (or its /omcc-designer:start / /omcc-designer:poster chain-tail dispatch) when the user wants automated image rendering for a poster spec produced by the poster skill, with the codex plugin installed."
---

# Phase 4: Poster Image Rendering

Render raw image assets for each image zone declared in poster_spec.md,
using the codex CLI's built-in imagegen tool via the codex-companion
plugin. This skill is a Phase 4 chain-tail to `poster` — it runs after
the poster skill returns, conditional on the user's opt-in via the
Tool dispatch decision (always prompted; never silent).

**Note on doc structure** — because this skill is invoked as a
chain-tail in nearly every real session, the procedure below is the
mainline doc; the "When auto-activated" / "When invoked by command"
sections at the end describe entry-point variations.

## Scope and boundary

This skill produces **raw zone images only** — no typography composition,
no layer flattening, no production-ready composite. The poster_spec.md's
Layer 2 (typography) remains a vector-layer responsibility for the human
designer or external tools (InDesign, Figma, Sketch, etc.).

This boundary preserves omcc-designer's identity as a **specification
authoring** plugin (not a production tooling plugin) and aligns with the
principle in `skills/poster/references/poster-guide.md` that "AI image
generators cannot reliably render text" — text remains Layer 2.

## Optional dependency: codex plugin

This skill depends on the **codex** plugin (same marketplace, optional).
This is an explicit, sanctioned cross-plugin dependency (see
`CLAUDE.md` "Cross-plugin sanctioned dependencies").

If the codex plugin is not installed, or its runtime is incomplete:

- Do not error.
- Leave poster_spec.md unchanged.
- Output a one-line notice: `"Codex plugin not installed or runtime
  incomplete — poster rendering skipped. The poster_spec.md contains
  image generation prompts for manual use with any image generation
  tool."`
- Exit clean.

Detection — three checks (all must pass):

1. The codex-companion script exists at any
   `~/.claude/plugins/cache/*/codex/*/scripts/codex-companion.mjs`
   (any marketplace, any installed version). Pick the highest version
   via `sort -V`. Hardcoded marketplace names (e.g., `omcc/codex`)
   must NOT be used — that excludes valid forks.
2. Node.js is on PATH (`command -v node` succeeds).
3. The codex CLI itself is invokable: `codex --version` exits 0 AND
   `codex app-server --help` exits 0.

If any check fails, run the graceful-degrade path above.

Note: the pre-flight does not detect codex authentication state —
authentication failures surface only at runtime (see Per-zone gate
Step 6 below).

## Tool dispatch decision (one prompt per render session — always)

Before entering the render loop, **always** prompt the user once,
regardless of the brief's `Image generation tools` field value. This
ensures informed consent — the codex render incurs API quota and time,
and the spec layer must surface that explicitly. (The brief field
informs the prompt wording but never substitutes for consent.)

Field normalization: lowercase the value, split on commas, trim
whitespace per token. Match `codex` case-insensitively. Treat the
result as **empty** when it is missing, blank, `none`, `none specified`,
or composed only of stop-words.

Prompt wording by field state:

- **Includes `codex`** (any tool list containing `codex`): `"The brief
  lists codex among Image generation tools. Render zone images now via
  codex? (y) render with codex / (n) skip — the poster_spec.md prompts
  remain available for manual use."`
- **Lists only non-codex tools** (e.g., `Midjourney`, `Stable Diffusion`):
  `"The brief lists [<tools>] but not codex. Render anyway via codex?
  (y) render — note: codex output may differ from the listed tools'
  style / (n) skip"`
- **Empty / missing / `none specified`**: `"The brief has no Image
  generation tools specified. Render via codex now? (y) render / (n)
  skip — recommend updating the brief on next pass"`

Input validation: accept `y`, `yes`, `n`, `no` (case-insensitive). Any
other input → re-prompt with the prompt text. After 3 invalid attempts
in a row, treat as `n` and exit clean.

If the user chooses `n`, exit clean with the same fallback message as
the codex-not-installed path. Do not write any zone files.

## Per-zone gate (seven actions)

For each image zone listed in poster_spec.md Layer 3, in order:

### Step 1 — determine next version number `N`

Scan `.history/<zone-id>/` for files matching `v<N>(-suffix)?\.png`
(suffixes include `-skipped`, `-loaded`, `-prior`, `-orphan`). Set
`N = max(<existing N values>) + 1`. If the directory is empty or
absent, `N = 1`. This rule is gap-tolerant (missing v2 between v1
and v3 still yields N = 4).

### Step 2 — resume / orphan handling (first entry of this zone)

- If `<output-dir>/<zone-id>.png` exists from a prior session, move
  it to `.history/<zone-id>/v<N>-prior.png` and increment N.
- If `.history/<zone-id>/v<X>.png` exists for some X but no
  `<output-dir>/<zone-id>.png` exists, that X is the latest no-final
  state — proceed to render v<N>.
- If a previous session was interrupted between codex's write and the
  spec's mv (extremely rare with the absolute-path approach below,
  but possible), an orphaned file at `<output-dir>/<zone-id>.png`
  with no matching `v<X>.png` is treated as the prior-session final
  per the first bullet.

### Step 3 — compose the codex prompt

From the zone's Designer's Vision and Image Generation Guide, append
two literal lines:

- `Save the result to the absolute path <output-dir>/.history/<zone-id>/v<N>.png — write to that exact absolute path; do not use a relative path.`
- `At the end of your response, print exactly one line in this format: SAVED_PATH=<absolute path of the saved PNG>`

**The absolute-path requirement is load-bearing.** Codex's app-server
resolves `--cwd` to the enclosing git repository root (verified
2026-04-26 in this repo), so a relative filename like `zone_a.png`
writes to the repo root, not the project directory. The absolute path
in the prompt bypasses this. See
`skills/poster-render/references/codex-call-template.md` for the
verification trace and the cwd-vs-absolute-path discussion.

### Step 4 — pick a prompt strategy

Based on the brief's Imagery approach:

- `photography`, `illustration`, `mixed`, or any raster-intent term:
  prompt naturally.
- Simple shape / vector-friendly subject (small flat icon, geometric
  mark): append "Use the imagegen tool to produce a raster image; do
  not write a deterministic script." This guards against codex's
  self-judgment fallback to script output for simple subjects.

### Step 5 — invoke codex-companion

Via Bash:

```
timeout 300 node <codex-companion-path> task --write --cwd <output-dir> "<prompt>"
```

- `--write` is mandatory (sandbox would block writes otherwise).
- `--cwd <output-dir>` is informational (codex resolves to repo root
  anyway); the prompt's absolute path is the load-bearing target.
- `timeout 300` (5 minutes) bounds hangs. Exit code 124 → treat as
  render failure for this zone (offer redo / edit / skip in the gate
  below).

### Step 6 — parse and validate

Parse the companion output:

1. Capture **the last** line matching `^SAVED_PATH=(.+)$` (codex
   reasoning may emit intermediate scratch lines; only the final
   agentMessage SAVED_PATH is canonical). Strip trailing whitespace
   and CR characters from the captured path.
2. Verify the captured path equals the requested absolute path
   (`<output-dir>/.history/<zone-id>/v<N>.png`). If not, log the
   mismatch and treat as render failure.
3. Verify the file exists and `file <path>` reports "PNG image data".
4. If the companion stdout/stderr contains an authentication error
   pattern (e.g., "auth", "login", "401", "unauthorized"), treat as
   **session-fatal**: surface "Codex CLI requires authentication —
   run `codex login` and retry" and exit clean (do not loop).
5. **Imagegen-not-available escape**: if 3 consecutive zones fail to
   produce a SAVED_PATH or a valid PNG with no clear cause (likely
   the imagegen tool is not exposed in this codex build), exit clean
   with "Codex imagegen tool unavailable in this build — rendering
   skipped." Already-accepted zones remain.

### Step 7 — present and gate

Present the version to the user (a preview of the rendered PNG) and
wait for the gate decision. The gate accepts seven actions:

| Key | Action | Effect |
|---|---|---|
| `a` / `accept` | Accept | Copy `.history/<zone-id>/v<N>.png` to `<output-dir>/<zone-id>.png` (overwriting any prior final). The history file remains. Proceed to the next zone. |
| `r` / `redo` | Regenerate (same prompt) | Run the same codex call again with the same prompt. The previous version stays in `.history`; the new version becomes v<N+1>. |
| `e` / `edit` | Regenerate with edit | Ask the user for a modified prompt, then re-invoke codex. The previous version stays in `.history`; the new version becomes v<N+1>. |
| `s` / `skip` | Skip this zone | Rename the latest version to `v<N>-skipped.png`. Do not create a final `<zone-id>.png` — the spec's prompt remains the canonical artifact for this zone. Proceed to the next zone. |
| `l` / `load` | Load existing | Ask the user for an absolute path to an external PNG. Verify it is a PNG and copy it to `<output-dir>/<zone-id>.png` AND `.history/<zone-id>/v<N+1>-loaded.png`. Proceed to the next zone. |
| `f` / `abort` | Abort all | Stop the render loop entirely. Already-accepted zones remain. Pending versions in `.history` are preserved. |
| `d` / `defer` | Defer to end | Move the candidate into a deferred queue (latest version preserved in `.history/<zone-id>/v<N>.png`). Proceed to the next zone. |

Input validation: accept the keys above (case-insensitive `a/r/e/s/l/f/d`,
or the spelled-out word). Any other input → re-prompt the gate. After
3 invalid attempts in a row, treat as `f` (abort all).

### After all non-deferred zones complete

If the deferred queue is non-empty, re-enter the gate for each
deferred zone in **original order**. **`d` (defer) is unavailable on
re-entry** — the re-entry gate accepts only `a / r / e / s / l / f`
(six actions). This bounds gate processing — the deferred queue is
processed exactly once, never recursively.

After all zones (and re-entered deferred zones) complete, present a
summary table: zone → final action → final filename (or `skipped`).

## Concurrent renders not supported

This skill assumes a single render session per `<output-dir>` at a
time. Running two `/start` or `/poster` invocations against the same
project directory concurrently produces races on the version counter
and on the `<zone-id>.png` filename, with no defense in this spec.
The user is responsible for serialization.

## File layout

Inside the project directory:

```
./output/<date>_<project>/
├── poster_spec.md             # unchanged input
├── design_brief.md            # unchanged input
├── zone_a.png                 # final accepted (or loaded) zone image
├── zone_b.png
├── ...
└── .history/
    ├── zone_a/
    │   ├── v1.png             # first codex render
    │   ├── v2.png             # second render after redo/edit
    │   ├── v3-skipped.png     # render after which user chose skip
    │   ├── v4-loaded.png      # external PNG loaded after a render
    │   └── ...
    ├── zone_b/
    │   └── v1.png
    └── ...
```

Rules:

- `<zone-id>` is the lowercase identifier from the poster_spec.md zone
  table (Zone A → `zone_a`, Zone B → `zone_b`).
- Every codex render writes `v<N>.png` (no suffix) under
  `.history/<zone-id>/`. N is determined per per-zone gate Step 1
  (max-existing + 1, gap-tolerant, suffix-aware).
- Existing versions are never overwritten; suffixed files (`-skipped`,
  `-loaded`, `-prior`, `-orphan`) are also counted by Step 1.
- On `accept`: copy the latest `v<N>.png` to
  `<output-dir>/<zone-id>.png` (overwriting any previous final). The
  history file remains.
- On `skip`: rename the latest version to `v<N>-skipped.png`.
- On `load`: copy the user-provided file to
  `<output-dir>/<zone-id>.png` AND record a
  `.history/<zone-id>/v<N+1>-loaded.png` snapshot.
- On `abort`: leave history files in place; the final `<zone-id>.png`
  exists only for already-accepted zones.

## Codex companion call pattern

See `skills/poster-render/references/codex-call-template.md` for:

- The exact companion command form
  (`timeout 300 node <companion> task --write --cwd <out> '<prompt>'`).
- The absolute-path requirement in the prompt and the cwd-vs-repo-root
  resolution behavior (verified 2026-04-26).
- The required `SAVED_PATH=` literal and last-match parsing rules.
- The codex two-step image storage path (raw under
  `~/.codex/generated_images/<thread>/...` → absolute target via
  `sips`).
- Behavior caveats — codex's self-judgment between imagegen model and
  deterministic script for simple subjects.

## Output language

Gate prompts and user-facing messages follow the user's request
language (consistent with the rest of omcc-designer). The codex
prompt itself follows the brief's Designer's Vision language —
usually English, which the imagegen tools handle best.

---

## When auto-activated (without /start or /poster command)

The user invokes the skill directly, supplying (or letting it
discover) a poster_spec.md path. Apply the full procedure above.
Requires both poster_spec.md and a sibling design_brief.md in the
same directory.

If design_brief.md is absent, ask the user to provide it or to
specify the Image generation tools field interactively (comma-separated
tool list, or `none`). If the user types `cancel` or leaves the input
empty 3 times in a row, exit clean.

## When invoked by command (/start, /poster)

`commands/start.md` Phase 4 and `commands/poster.md` Optional chain
both dispatch this skill as a chain-tail after the `poster` skill
returns, **always** running the Tool dispatch decision prompt above
(no silent dispatch — informed consent is required regardless of
brief field value).

If the user chooses to skip in the Tool dispatch decision, this skill
exits clean and the pipeline completes with poster_spec.md only.

The pipeline's "✓ Design pipeline complete." message is emitted by
`commands/start.md` after this skill returns (or after the `poster`
skill when this skill is not dispatched). For `/poster`, the
completion message is emitted by `commands/poster.md`.
