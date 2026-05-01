---
description: Dispatch a Codex task on a user-specified question while a workflow is active, then synthesize Codex's answer with Claude's understanding.
argument-hint: <question>
---

# Codex-now

$ARGUMENTS

`/omcc-dev:codex-now` is the user-initiated escape hatch for the Codex
ensemble — see `ensemble-protocol.md`'s Codex-now Ensemble Point Type
for the prompt shape and synthesis rule. The command requires an
active workflow as the bookkeeping anchor; behavior precedent is
`commands/checkpoint.md`.

---

## Step 1: Locate the target workflow

Mirror `commands/checkpoint.md` Step 1 in full:

1. Read the active registry at `<cwd>/.claude/omcc-dev/active.md`.
2. If no active workflow is recorded, inform the user and exit.
   Suggest `/omcc-dev:start` or `/omcc-dev:resume` first.
3. If multiple active workflows exist, follow the same selection UX
   as `/omcc-dev:resume` Step 1 (interactive pick — `/codex-now` does
   not parse a workflow-id selector from `$ARGUMENTS`; the entire
   argument is treated as the question text per the v1 grammar).
4. If the selected root is **sharded** (directory
   `workflows/<root_id>/` exists via `resolveShardDirectoryPath`):
   - The pending_ensemble entry writes to the **active shard**
     (first `in_progress` in `plan.deliverables[]`, else first
     `pending`), not the root.

## Step 2: Validate the question text

1. Reject if `$ARGUMENTS` is empty or whitespace-only.
2. Reject if the raw length exceeds
   `SANITIZE_FIELD_CAPS.codex_question` (registered in
   `hooks/_utils.mjs`). `sanitize` truncates on overflow, so length
   must be checked **before** sanitization — silent truncation would
   change the user's prompt.
3. Apply `sanitizeField("codex_question", $ARGUMENTS)` for
   control-character stripping.
4. **Backtick rule**: if the sanitized text contains a backtick
   (U+0060), reject with the same wording as
   `commands/checkpoint.md` Step 2.4. Do NOT silently strip.
5. **CDATA terminator rule**: if the sanitized text contains the
   literal three-byte sequence `]]>`, reject with a diagnostic
   ("question contains the CDATA terminator `]]>` which would break
   the prompt wrapper — please rephrase"). Do NOT split-and-rejoin —
   the rejection posture matches steps 1-4 and avoids transforming
   the user's prompt.

## Step 3: Compose and write the Codex prompt

1. Build the prompt body using the Codex-now template documented in
   `ensemble-protocol.md`. The template wraps the user question in
   `<![CDATA[ ... ]]>` so XML-meaningful characters (`<`, `>`, `&`,
   stray closing tags) inside the question remain literal data. The
   wrapper assumes the question does NOT contain the three-byte
   sequence `]]>` (rejected by Step 2.5); the wrapper alone is not
   sufficient injection defense without that rejection step.
2. Resolve a per-dispatch temp path. Format:
   `${TMPDIR:-/tmp}/omcc-codex-now-<session-id>-<dispatch-id>.txt`.
3. Use Claude's `Write` tool to write the prompt body to that path
   verbatim. The Write tool never invokes a shell, so the prompt
   content does not pass through any shell parser.

## Step 4: Launch Codex and append pending_ensemble

Order of operations (load-bearing — see Failure Handling for crash
windows):

1. Verify the prompt file exists; if missing, abort with a diagnostic
   and **do not** write any pending_ensemble entry.
2. Register the EXIT trap to remove the prompt file on any exit path
   (preflight rejection, dispatch error, normal completion).
3. Run preflight guards: `CODEX_HOME` resolution, codex-companion.mjs
   presence, `valueOptions.*"prompt-file"` grep for older-build
   guarding, `node` availability. Each guard exits 0 (graceful
   degradation) on miss.
4. Dispatch via background Bash:
   `CLAUDE_PLUGIN_ROOT="$CODEX_HOME" node "$CODEX_HOME/scripts/codex-companion.mjs" task --prompt-file "$PROMPT_FILE"`.
   The launch follows the trap-before-preflight pattern documented
   in the omcc-research plugin's research-ensemble-protocol document
   (prose-only cross-plugin reference).
5. Capture the **Bash background task id** returned by Claude Code.
   This id (not any Codex-internal session id) is what
   `pending_ensemble.job_id` records — `commands/resume.md` Step 5b
   strips entries by Bash id.
6. **Only after the launch returns a job id**, append the pending
   entry via `atomicModifyFile(targetPath, appendMutator)` per the
   State Bookkeeping rule in `ensemble-protocol.md`.

**`appendMutator`** (hand-rolled because `parseNestedList` keys list
entries on `- id:` and `pending_ensemble` uses `- job_id:`; the
read side in `commands/resume.md` Step 5b also hand-rolls for the
same reason):

```
appendMutator(current):
  if current === null: return null
  { prefix, fmBody, suffix, body } = parseFrontmatter(current)
  if !fmBody: return null

  newEntry =
    "  - job_id: <bash-job-id>\n" +
    "    ensemble_type: codex-now\n" +
    "    dispatched_at: <ISO 8601 UTC>\n"

  if fmBody contains a line "pending_ensemble:":
    locate the block: the run of lines starting with that header,
    terminated by the first line whose first character is
    non-whitespace OR by the line "---" (frontmatter terminator),
    whichever comes first. Insert newEntry immediately before that
    terminator. Existing entries use "  - job_id: …" (two-space
    dash) plus children at "    <key>: <value>" (four-space indent);
    the new entry MUST use the same indentation grammar.
  else if fmBody contains "pending_ensemble: []" (inline-empty):
    replace that single line with "pending_ensemble:\n" + newEntry.
  else:
    insert "pending_ensemble:\n" + newEntry into fmBody at the
    field-order position dictated by `continuity-protocol.md`:
    AFTER `presentation_mode:` if present, else after the last line
    of `task_profile:`, and BEFORE `latest_checkpoint:` if present.

  fmBody = updateUpdatedAt(fmBody, ISO_NOW)
  return prefix + fmBody + suffix + body
```

`atomicModifyFile` owns the advisory lock, tempfile, fsync, rename,
and 0600 chmod. The mutator stays inside the YAML subset documented
in `continuity-protocol.md` State File Schema.

## Step 5: Collect and remove pending_ensemble

1. Wait for the background Bash completion notification — do NOT
   poll, sleep, or proactively check.
2. Read the codex-companion output from the completed Bash task.
3. If Codex failed, returned empty, or produced unparseable output,
   record the failure mode internally and proceed to Step 6 with a
   Claude-only fallback. The pending entry is removed regardless.
4. Run `atomicModifyFile(targetPath, removeMutator)` to strip the
   entry by `job_id`.

**`removeMutator`** (idempotent — `commands/resume.md` Step 5b may
strip the same entry if a session compact happens between Step 4
and Step 5):

```
removeMutator(current):
  if current === null: return null
  { prefix, fmBody, suffix, body } = parseFrontmatter(current)
  if !fmBody: return null
  if fmBody contains no line "pending_ensemble:": return null

  scan the pending_ensemble: block (delimited by the first
  non-whitespace line OR "---" after the header). Build entries[]
  from the block, dropping ALL entries whose job_id matches (not
  just the first — defensive for a corrupted-state case).

  if entries.length === 0:
    remove the entire block — the line "pending_ensemble:" plus
    every subsequent line whose first character is whitespace,
    plus the trailing newline of the header so no orphan blank
    line remains. Do NOT leave "pending_ensemble:" or
    "pending_ensemble: []" — the spec requires absence when no
    Codex job is in flight.
  else:
    rewrite the block with the remaining entries.

  fmBody = updateUpdatedAt(fmBody, ISO_NOW)
  return prefix + fmBody + suffix + body
```

## Step 6: Present the answer

Treat the Codex output and Claude's own reading as the two sources,
classified by `ensemble-protocol.md` Synthesis (the Codex-now
subsection notes the deviation from the four-category taxonomy).
Present in **batch** unconditionally — `/codex-now` does not read
the workflow's `presentation_mode` and does not prompt for it. If
Codex was unavailable, surface "Codex unavailable for this
question — proceeding with Claude's reading only." per
`ensemble-protocol.md` Failure Handling.

---

## Failure Handling

Crash windows are bounded by the ordering in Step 4:

| Failure point | State | Action |
|---|---|---|
| Prompt-file write fails | No Bash launched, no pending entry | Abort with diagnostic. Best-effort `unlink` of any partial path; OS tmp-cleanup also reaps the per-session-id namespace eventually. |
| Preflight guard rejects (CODEX_HOME / node / file / grep) | Bash exits 0 (graceful), trap removes prompt file, no job id | No pending entry written. Surface "Codex unavailable" to user. |
| Background Bash exits non-zero before backgrounding | No job id returned | No pending entry written. Surface error. |
| Host crash between launch-success (4.5) and append (4.6) | Background job runs to orphan completion; output abandoned | The job's output is harmless cruft in the Bash background task store; user re-invokes `/codex-now` if still needed. |
| Codex run errors after launch | Pending entry exists with the job id | Step 5 collect path runs the remove mutator regardless of outcome. |
| Session compact between Step 4 and Step 5 | Pending entry exists; Bash id uncollectable across sessions | `commands/resume.md` Step 5b strips the entry. User re-invokes if needed. |
| Workflow archived between Step 1 and Step 4/5 | Mutator's `current === null` branch fires | Abort the mutation; report to user that the target workflow no longer exists. |

---

## Idempotency

Re-invocation while a prior `/codex-now` is still in flight creates a
second pending entry with a distinct `job_id`. Each collect's remove
mutator filters by matching `job_id` only, so concurrent jobs do not
interfere.
