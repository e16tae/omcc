# Codex Companion Call Template

Reference for invoking the codex-companion plugin to render a single
image zone, including the prompt format, the result-path conventions,
and the cwd-resolution / dispatch caveats discovered during integration
verification.

This document is the canonical source for the call mechanics referenced
by `skills/poster-render/SKILL.md`. The per-zone lifecycle (gate, history
versioning, accept/skip handling) lives in SKILL.md; this file does
not duplicate it.

---

## Pre-flight check

Before invoking the companion, confirm three things:

```bash
# 1. node on PATH
command -v node >/dev/null 2>&1 || { echo "node not installed"; exit 1; }

# 2. codex CLI installed
codex --version || { echo "codex CLI not installed"; exit 1; }

# 3. codex app-server invokable
codex app-server --help >/dev/null || { echo "codex app-server unavailable"; exit 1; }
```

If any of these fails, surface a one-line notice and exit clean (the
codex plugin's broader `Optional dependency` policy applies — see
`skills/poster-render/SKILL.md` Optional dependency section).

The pre-flight does NOT detect codex authentication state — the
`codex --version` and `codex app-server --help` commands succeed for
unauthenticated installs. Authentication failures appear only at
runtime; SKILL.md per-zone gate Step 6 handles them as session-fatal.

## Locating the companion script

The companion lives inside the codex plugin's cache directory.
Multiple versions may coexist; pick the highest version. **Use a
glob that accepts any marketplace** — hardcoded marketplace names
(e.g., `omcc/codex`) exclude users who installed the codex plugin
from a fork or alternate marketplace.

```bash
COMPANION=$(ls -d ~/.claude/plugins/cache/*/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
[ -n "$COMPANION" ] && [ -f "$COMPANION" ] && echo "found: $COMPANION"
```

If `$COMPANION` is empty after this check, the codex plugin is not
installed in any marketplace — apply the graceful-degrade path from
`skills/poster-render/SKILL.md`.

## Canonical call form

For each zone:

```bash
timeout 300 node "$COMPANION" task --write --cwd "$OUTPUT_DIR" "$PROMPT"
```

Where:

- `$COMPANION` — absolute path resolved above.
- `--write` — **mandatory**. The companion's `task` subcommand defaults
  to a read-only sandbox; without `--write`, codex generates the image
  internally but the disk write is blocked, and the final PNG never
  appears.
- `--cwd "$OUTPUT_DIR"` — the project directory (e.g.,
  `./output/2026-04-26_my-poster/`). **However, codex resolves cwd to
  the enclosing git repository root** (see "cwd resolution caveat"
  below); this argument is informational. The actual save location is
  controlled by the absolute path embedded in the prompt.
- `"$PROMPT"` — a single positional argument. Quote it once so the
  shell does not split on spaces. Do not pass image-related options as
  flags (e.g., do not invent `--imagegen`); the companion's
  `lib/args.mjs` treats unknown long flags as positional tokens, so
  invented flags become part of the prompt and confuse the model.
- `timeout 300` — bounds the call to 5 minutes. Exit code 124 indicates
  a hang (codex auth flow stalled, model timeout, network failure); the
  caller treats this as a render failure for the zone.

## cwd resolution caveat (verified 2026-04-26)

When `$OUTPUT_DIR` is inside a git repository (the common `/start` setup
in any user's workspace), codex's app-server **does not honor `--cwd`
literally**. Instead, it walks up to the git repository root and uses
that as the working directory. Verification in this repo:

- Requested `--cwd /Users/lmuffin/Workspace/omcc/tmp-cwd-test/output/test-project`
  with prompt `Save zone_a.png in the current working directory`.
- Result: file saved at `/Users/lmuffin/Workspace/omcc/zone_a.png`
  (repo root), not in the requested cwd.
- Fix: include the absolute path of the desired save location directly
  in the prompt (see "Prompt template" below). Verified to work — file
  lands at the prompt-specified path.

This is not a companion bug; it is codex CLI's intended sandbox
behavior. The absolute-path workaround is the supported integration
pattern.

## Prompt template

The prompt sent to codex must:

1. End with an explicit absolute-path save instruction (so the file
   lands where the caller expects, regardless of cwd resolution).
2. End with a literal SAVED_PATH= line (so the companion's final
   agentMessage — captured as `payload.rawOutput` — contains the
   absolute path of the rendered file for the caller to parse).

Template:

```
<Designer's Vision narrative — multi-paragraph, derived from poster_spec.md Layer 3>

<Image Generation Guide notes — universal tips from poster_spec.md>

<Optional dispatch hint — see "Dispatch caveat" below for when to add it>

Save the result to the absolute path <ABSOLUTE_TARGET_PATH> — write to that exact absolute path; do not use a relative path.
At the end of your response, print exactly one line in this format: SAVED_PATH=<absolute path of the saved PNG>
```

Where `<ABSOLUTE_TARGET_PATH>` is the full path the caller wants the
file to land at (e.g.,
`/abs/path/to/output/2026-04-26_my-poster/.history/zone_a/v1.png`).

## Result parsing

After the companion exits, parse its stdout:

1. Find **the last** line matching `^SAVED_PATH=(.+)$` (codex
   reasoning may emit intermediate scratch lines containing
   `SAVED_PATH=`; only the final agentMessage SAVED_PATH is canonical).
2. Strip trailing whitespace and CR characters from the captured
   path (defends against CRLF line endings on certain pipelines).
3. Verify the captured path equals `<ABSOLUTE_TARGET_PATH>` (the
   value the prompt requested). If not, treat as render failure.
4. Verify the file exists with `test -f "$path"`.
5. Verify it is a real PNG: `file "$path"` should report
   `PNG image data, <W> x <H>, 8-bit/color RGB(A), non-interlaced`.
6. If any check fails, treat as a render failure for this zone — see
   the consumer chain-tail's SKILL.md per-zone gate "Recovery after
   a render failure" subsection (offers `e/s/d`, no `a`; on N
   consecutive failures, escape the loop). The canonical example is
   `skills/poster-render/SKILL.md` Step 7.

### Chain-specific validation hook

Steps 1–6 are the **shared** validation contract — every chain-tail
that consumes this template MUST implement them. A consumer chain
MAY add **chain-specific** validation steps **after** Step 6's
PNG-type check, before the gate fires. Such steps are advisory
(they annotate the gate) — they MUST NOT auto-retry, MUST NOT
re-invoke the companion, and MUST NOT block the user from accepting
a partially-conforming output. The "no auto-regeneration" rule
below is preserved unconditionally.

Examples of legitimate chain-specific validation:

- **Dimension validation** (used by `social-graphics-render`): after
  the PNG-type check, run `sips -g pixelWidth -g pixelHeight "$path"`
  (macOS) and compare against the variant's expected canvas. On
  mismatch, record a non-blocking annotation that the chain's gate
  step prepends to its prompt (e.g., `dim mismatch: actual <WxH>
  vs expected <WxH>`). The user's `e` action becomes the natural
  retry path.
- **Color-mode validation** (hypothetical future): same shape —
  detect, annotate, defer to gate.

Chain-specific validation steps MUST gracefully degrade when their
detection tool is unavailable (e.g., `sips` is macOS-only). On the
non-supported platform, the step records a "validation skipped:
<reason>" annotation rather than failing the render.

The shared template intentionally does not enumerate the exact
chain-specific steps — each chain's SKILL.md is the source of
truth for its own annotations.

Auth-failure pattern: if companion stdout/stderr contains tokens like
`auth`, `login`, `401`, or `unauthorized`, treat the failure as
**session-fatal** (do not retry or re-invoke); see SKILL.md Step 6.

## Two-step image storage (informational)

Internally, codex writes the imagegen result twice:

1. **Raw**: `~/.codex/generated_images/<thread-id>/<filename>` — created
   by the imagegen tool itself.
2. **Absolute target**: codex then runs `sips` (or `cp` for already-
   sized renders) to copy/resize the raw file to the absolute path
   the prompt requested.

The caller never needs to read `~/.codex/generated_images/`. The
prompt's absolute-path instruction together with the SAVED_PATH=
return line is the supported interface.

Codex's `payload.touchedFiles` is unreliable for image outputs (the
imagegen tool does not always emit a `fileChange` event). Use the
`SAVED_PATH=` line, not `touchedFiles`.

## Dispatch caveat — imagegen tool vs deterministic script

The codex CLI ships a system imagegen skill at
`~/.codex/skills/.system/imagegen/SKILL.md` that codex consults for
every image-generation request. Codex then **decides on its own**
whether to:

- Invoke the imagegen model (returns a generated raster), or
- Synthesize the image deterministically with a small script (e.g.,
  Python `struct`+`zlib` for a 64×64 flat icon).

For poster zones — typically photography, illustration, or rich
illustrative content — codex naturally picks the imagegen model. But
for simple, vector-friendly subjects (small flat icons, geometric
marks, single-color shapes), codex may pick the deterministic script
path even when the user clearly wants a model-rendered image.

To guard against this for borderline cases, append the following
directive to the prompt:

> Use the imagegen tool to produce a raster image. Do not write a
> deterministic script.

Use the directive when the brief's `Imagery approach` is anything other
than `photography`, `illustration`, `mixed`, or another raster-intent
term — i.e., when codex's self-judgment is most likely to favor a
script. For raster-intent imagery, omit the directive (codex will
choose imagegen on its own).

## Cost and latency

Each codex `task` call counts toward the user's codex usage limits.
For larger images (512×512 or above), a single call commonly takes
20–60 seconds. The `timeout 300` guard above bounds the worst case.

### Rule: no auto-regeneration

The companion MUST be invoked **at most once per render attempt**,
where each attempt is triggered by exactly one of:

- The initial render call entering Step 5 for a zone (one attempt per
  zone, per loop entry).
- A user gate action of `e` / `edit` (one attempt per gate decision —
  see SKILL.md Step 7 for prefill semantics). This is the only
  legitimate re-invocation trigger besides the initial render.

Background re-runs, retry loops without intervening user input, or
auto-regeneration on parse failure (mismatched SAVED_PATH, missing
PNG, auth error) are forbidden. The two auto-exit paths in
`skills/poster-render/SKILL.md` —
- Step 6 imagegen escape (3 consecutive zones with no SAVED_PATH →
  exit clean), and
- Step 7 invalid-attempt counter (3 invalid gate inputs in a row →
  abort the loop, mirroring the Ctrl+C path)
— never call the companion. They terminate the loop without
re-invoking it. This makes "one user action =
at most one billed codex call" a hard guarantee, independent of
failure modes.
