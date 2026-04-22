# Continuity Protocol

Defines how omcc-dev preserves workflow state across sessions, how `/start`,
`/fix`, `/audit` write and read that state, how hooks reinforce continuity
at session boundaries, and how fresh-session agents rehydrate deterministically.

The user never reconstructs workflow context by hand. The `/omcc-dev:resume`
command reads the state file, verifies git integrity, restores task tracking,
and continues at the recorded phase. Hooks provide automation UX but are not
required — the command-level path always works as a fallback.

**Status**: this spec is introduced as a framework document only. The actual
wiring — `/omcc-dev:resume` command, Phase 0 continuity checks in `/start`
/ `/fix` / `/audit`, and hook scripts under `hooks/` — lands in subsequent
commits of the same feature branch (`feat/continuity-protocol`). Until
those commits merge, the MUST/SHOULD rules below are the contract to be
implemented, not observable live behavior.

---

## When This Protocol Applies

Activates whenever `/start`, `/fix`, `/audit`, or `/omcc-dev:resume` runs.
Each of these commands must:

1. Check for existing workflow state at Phase 0 before performing
   command-specific work.
2. Write required state fields at every phase boundary defined below.
3. Archive state on terminal success per the Archive Lifecycle.

Does NOT apply to:

- Skills invoked in auto-activated mode (outside a command).
- Internal orchestration decisions (Task Profile construction, Ensemble
  Affinity evaluation, agent dispatch).
- Binary confirmations or progress updates in conversation.

---

## Directory Layout

All state lives in the user's cwd under `<cwd>/.claude/omcc-dev/`. The
repository's `.gitignore` already excludes `.claude/`, so state is local
to each checkout and never committed.

```
<cwd>/.claude/omcc-dev/        # created with mode 0700
├── active.md                  # registry of currently-active workflows  (0600)
├── workflows/
│   └── <workflow_id>.md       # one file per active workflow             (0600)
└── archive/
    └── <workflow_id>.md       # completed workflows                      (0600)
```

The first command creates the directory with `mkdir -p` followed by explicit
`chmod 0700`. All state files are written with `chmod 0600`. Commands and
hooks MUST apply these permissions explicitly — do not rely on umask.

### Workflow IDs

Format pin: `^(start|fix|audit)-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}$`

- `<type>` = `start`, `fix`, or `audit`
- `<timestamp>` = ISO 8601 UTC compact, `YYYYMMDDTHHMMSSZ`
- `<shortid>` = 6 lowercase hex characters for uniqueness under concurrent creation

Example: `fix-20260422T142512Z-a3f091`

**Path-safety invariant**: consumers (commands, hooks, `/omcc-dev:resume`)
MUST validate every `workflow_id` and `parent_workflow` reference against
the workflow-id regex before using it as a filesystem path component.
Values that fail the regex MUST be rejected with a diagnostic — never used
as a path.

**Migration exception**: legacy-migrated workflow files use a widened
format `<type>-<timestamp>-migrated-[0-9a-f]{6}` where `migrated` is a
literal string. Consumers MUST accept this extended form but MUST NOT
otherwise relax the regex.

### Finding IDs

`originating_finding` is NOT a workflow id. It refers to an audit finding
id from a parent `/audit` workflow's `findings[].id` array. Format pin:

`^finding-[0-9]+$`

Consumers MUST validate `originating_finding` against this separate regex.
Finding ids are never used as file-path components — only as lookup keys
into the parent workflow's `findings` array.

### Active Registry

The file `<cwd>/.claude/omcc-dev/active.md` is a YAML-frontmatter registry
of currently-active workflows. Schema:

```yaml
---
schema: 1
updated_at: 2026-04-22T14:30:00Z
active:                                  # required; empty list when no workflows active
  - id: <workflow_id>                    # required
    type: start | fix | audit            # required
    phase: <phase-state-enum value>      # required; cached from workflow file
    parent: <workflow_id or null>        # required (null when no parent)
    children: []                         # required (empty list when no children)
    originating_finding: <string or null># required for fix with parent=audit; null otherwise (registry uses explicit null for tabular uniformity, distinct from workflow-file omit-vs-null rule)
---
```

Ordering: `active` list MUST be sorted by `id` ASCII ascending (deterministic
for diffs). Empty file semantics: when no workflows are active, the file
contains exactly the frontmatter above with `active: []` — it is never
absent once created.

Reconciliation rule: the active registry's `phase` is a cached index of the
workflow file's `current_phase`. When they disagree, the workflow file is
authoritative; `/omcc-dev:resume` re-syncs on next read.

---

## State File Schema

Each `<cwd>/.claude/omcc-dev/workflows/<workflow_id>.md` file is YAML
frontmatter + Markdown body. Only the frontmatter is machine-parsed; the
body is human/agent context.

### YAML subset

Frontmatter MUST be parseable as **YAML 1.2 core schema** (JSON-compat).
Timestamps use the `Z` suffix (UTC). All `id` fields throughout the schema
are **opaque strings**; consumers MUST NOT parse them as integers.

### Field-order rule

Fields MUST appear in the order shown in the schema below. Schema-minor
additions are appended at the end of their group. This keeps diffs stable
across implementations.

### Always-required frontmatter (present from Phase 0 onward)

```yaml
---
schema: 1                              # integer; protocol version
workflow_id: <type>-<timestamp>-<shortid>
workflow_type: start | fix | audit
original_request: <summary; see Security>
started_at: <ISO 8601 UTC, Z suffix>
updated_at: <ISO 8601 UTC, Z suffix>
repo_root: <absolute path; git rev-parse --show-toplevel>
git_baseline:
  branch: <branch name at start>
  head: <full SHA at start>
  status_digest: <sha256 hex; see algorithm pin>
current_phase: <see Phase State Enum>
next_action: <short imperative sentence>
tasks: []                              # empty list at bootstrap; updated from TaskCreate/TaskUpdate
---
```

### Conditionally-required frontmatter (present iff condition holds)

- `parent_workflow`: string OR absent. Required with a workflow_id value
  when this workflow was spawned from another (`/fix` from `/audit`).
  Absent otherwise.
- `originating_finding`: string OR absent. Required with a finding id
  when `parent_workflow` is present AND parent is `/audit`. Absent otherwise.
- `pending_ensemble`: list OR absent. When present, each entry:
  ```yaml
  pending_ensemble:
    - job_id: <codex job id>
      ensemble_type: <one of ensemble-protocol.md Ensemble Point Types>
      dispatched_at: <ISO 8601 UTC, Z suffix>
  ```
  `ensemble_type` enum (from `ensemble-protocol.md` Ensemble Point Types):
  `brainstorm | explore | plan-verify | review | investigate | fix-verify | audit-scan`.
  Absent when no Codex job is in flight.

**Rule**: optional/conditional fields MUST NOT be written as literal `null`.
If the condition does not hold, omit the field entirely.

### Workflow-type-specific frontmatter

Present only when `workflow_type` matches; absent for other types.

**`/start`** (appears after Phase 1/2/3 respectively):

```yaml
decision:                              # after Phase 1 Brainstorm approved
  chosen: <approach>
  rationale: <why>
  rejected: <list + why>
architecture:                          # after Phase 2 Explore
  patterns: <list>
  integration_points: <list>
  pitfalls: <list>
plan:                                  # after Phase 3 Plan approved
  deliverables:                        # only in deliverable mode
    - id: A
      status: pending | in_progress | completed
      tasks: [...]
```

**`/fix`** (populated progressively):

```yaml
symptom: <observed behavior>           # after Phase 1 started
hypotheses:                            # after Phase 1 hypotheses generated
  - text: <hypothesis>
    verdict: confirmed | refuted | untested
    evidence: <file:line references>
root_cause: <string>                   # after Phase 1 root cause confirmed
fix_approach: <short description>      # after Phase 1 root cause confirmed
failing_test:                          # after Phase 2
  path: <test file path>
  status: failing-as-expected | passing | framework-absent
similar_pattern_grep:                  # after Phase 3 similar-pattern search
  pattern: <regex or literal>
  matches: [<file:line>, ...]
```

**`/audit`** (populated progressively):

```yaml
audit_type: security | performance | code-quality | tech-debt | full
target_scope: <dir or "all">
task_profile:
  scope: <string>
  ensemble_affinity: LOW | MEDIUM | HIGH
findings:                              # after Phase 2
  - id: finding-1
    severity: critical | high | medium | low | observation
    decision: undecided | fix-now | defer | accept | investigate
    location: <file:line>
    child_workflow: <workflow_id or absent>   # present when decision=fix-now and /fix spawned
    resolved_commit: <sha or absent>          # present when child_workflow archived with commit
```

**`decision: undecided`** is the default when a finding is first added.
Workflow MUST NOT transition to `summary-complete` while any finding is
`undecided` — the summary table step forces a decision.

### Phase State Enum (authoritative)

All legal `current_phase` values by workflow type. Downstream consumers
(commands, hooks, `/omcc-dev:resume`) MUST validate `current_phase`
against this enum and MUST use **exact string equality** — no glob, no
suffix matching.

| workflow_type | Legal `current_phase` values (in forward order) |
|---|---|
| `start` | `brainstorm` → `explore` → `plan` → `implement` → `review` → `resolve` → `commit-complete` |
| `fix` | `investigate` → `failing-test` → `fix-and-verify` → `commit-complete` |
| `audit` | `scope` → `scan` → `integrate` → `present` → `remediation-discussion` → `summary-complete` |

**Terminal states** (exact whitelist for auto-archive matching):
`commit-complete`, `summary-complete`.

**Adding a new terminal state** is a schema major bump. Non-terminal
additions within a workflow_type are a schema minor bump.

### Body sections

Markdown body after frontmatter. Free-form context — not machine-parsed.
Each command writes narrative detail per the Phase-boundary Write Rules.
Body must remain safe to re-read in a fresh session.

**Body growth cap**: the body contains at most **50** PreCompact snapshot
blocks. On overflow, the oldest block is removed atomically during the
next PreCompact write. Snapshot blocks are delimited by the literal comment
`<!-- pre-compact snapshot -->` on a line by itself; anything between two
such markers (exclusive) is one snapshot.

### Atomic write discipline

Consumers (commands, hooks) MUST apply this discipline to every write of
the active registry and any workflow file.

**Initial creation** (target does not exist):

1. Acquire best-effort advisory lock via `fs.openSync(<file>.lock, 'wx')`
   (exclusive create). On `EEXIST`, retry every 100ms up to 5s, then error.
2. Write new content to `<file>.tmp`.
3. `fsync` the tempfile.
4. Rename `<file>.tmp` → `<file>` (atomic on POSIX).
5. `chmod 0600 <file>`.
6. Remove the `<file>.lock` sentinel.

**Update** (target exists):

1. Acquire lock as above.
2. Write new content to `<file>.tmp`.
3. `fsync` the tempfile.
4. Rename `<file>` → `<file>.bak` (replaces any previous `.bak`).
5. Rename `<file>.tmp` → `<file>` (atomic on POSIX).
6. `chmod 0600 <file>` (tempfile inherits umask; explicitly restore mode
   after rename so subsequent updates cannot relax permissions).
7. Remove the `<file>.lock` sentinel.

On failure at any step: remove `<file>.tmp` if it exists, leave `<file>`
and `<file>.bak` intact. Surface the error to the caller.

**Directory durability**: on filesystems where directory-entry durability
after rename is not guaranteed (older ext3 `data=writeback`, some network
FSes), implementors SHOULD `fsync` the parent directory after the final
rename. On modern ext4/APFS with default mount options this is unnecessary.

**Rationale**: Rename-based atomicity is the actual integrity guarantee.
The lock sentinel is best-effort and may be skipped on systems without
exclusive-create semantics (e.g., some NFS configurations); rename
atomicity still holds.

**Update trigger for `updated_at`**: MUST be refreshed on every atomic
write that produces a new `<file>`, including PreCompact body-only updates.
(PreCompact thus reads current frontmatter, updates `updated_at`, appends
snapshot to body, and writes through the full Update sequence — no
append-only shortcut exists.)

### Parser rules

- Frontmatter fields not in the schema: consumers MUST **preserve them
  verbatim on round-trip write** (no silent drop). Writers MUST NOT
  introduce new frontmatter fields without bumping `schema`.
- Unknown `schema` version `schema > 1`: `/omcc-dev:resume` and hooks MUST
  warn the user and offer archive/abort — never silently proceed.
- Older `schema < 1` is undefined (1 is the initial); treat as corrupt.
- Missing required field: treat as corrupt; fall back to `<file>.bak` if
  available AND `.bak` passes validation (schema + workflow_id regex +
  required fields present); else prompt user.

### Schema evolution rules

- **Minor bump** (schema stays integer; documentation tracks minor
  revision): new field added to existing section; new non-terminal
  `current_phase` value; new `ensemble_type` entry. Backward compatible.
- **Major bump** (`schema: 1` → `schema: 2`): field renamed or removed;
  terminal state added; `workflow_id` format changed. Non-backward-compatible.
- Readers of schema `N` MAY read files where `schema <= N` and SHOULD
  migrate on write. Readers MUST NOT read files where `schema > N`.

---

## Phase-boundary Write Rules

Every command writes state at these boundaries. The bootstrap write at
Phase 0 establishes the workflow file; subsequent writes update
frontmatter (atomic full-file replace, not append).

### `/start` (7 phases)

| Phase | Write trigger | Updates |
|---|---|---|
| 0 | After continuity check | bootstrap; `current_phase="brainstorm"`, `next_action`, `tasks: []` |
| 1 | Brainstorm approved | `decision`; `current_phase="explore"` |
| 2 | Explore synthesis | `architecture`; `current_phase="plan"` |
| 3 | Plan approved | `plan.deliverables` (if deliverable mode), `tasks`; `current_phase="implement"` |
| 4 | Each TaskUpdate | `tasks`; `current_phase`/`next_action` when deliverable boundary crossed |
| 5 | Review complete | body: findings summary; `current_phase="review"` |
| 6 | Convergence | body: findings resolution; `current_phase="resolve"` |
| 7 | Commit complete | `current_phase="commit-complete"`, `next_action="archive"` |

### `/fix` (4 phases)

| Phase | Write trigger | Updates |
|---|---|---|
| 0 | Before Phase 1 | bootstrap; `current_phase="investigate"` |
| 1 | Hypotheses generated | `hypotheses` |
| 1 | Root cause confirmed | `root_cause`, `fix_approach` |
| 2 | Failing test status | `failing_test`; `current_phase="failing-test"` |
| 3 | Similar-pattern search | `similar_pattern_grep` |
| 3 | Ensemble dispatch | `pending_ensemble` append |
| 3 | Ensemble collected | `pending_ensemble` remove; `current_phase="fix-and-verify"` |
| 4 | Commit complete | `current_phase="commit-complete"`, `next_action="archive"` |

### `/audit` (5 phases)

| Phase | Write trigger | Updates |
|---|---|---|
| 0 | Before Phase 1 | bootstrap; `current_phase="scope"` |
| 1 | Scope locked | `audit_type`, `target_scope`, `task_profile` (no phase transition — stays `scope`) |
| 2 | Scan dispatch | `pending_ensemble` append; `current_phase="scan"` |
| 2 | Scan results collected | `findings` (initial); `pending_ensemble` remove |
| 3 | Integrate built-in results | body: integrated findings; `current_phase="integrate"` |
| 4 | Synthesis complete | `findings` (synthesized); `current_phase="present"` |
| 5 | Enter remediation | `current_phase="remediation-discussion"` |
| 5 | Per-finding decision | `findings[i].decision` |
| Terminal | Summary table written | `current_phase="summary-complete"`, `next_action="archive"` |

---

## Drift Classification

When `/omcc-dev:resume` loads a workflow file, compare `git_baseline`
against current git state. Classification:

| Classification | Condition | Action |
|---|---|---|
| `clean` | Branch unchanged AND HEAD equals `git_baseline.head` AND `status_digest` equals current digest | Resume directly at recorded phase |
| `compatible` | Same branch AND current HEAD descends from `git_baseline.head` (fast-forward) AND no state-referenced file renamed/deleted | Surface drift summary; re-verify assumptions; continue |
| `conflicting` | Any of: branch changed, HEAD not reachable from baseline OR baseline not reachable from HEAD (diverged / rewound), state-referenced file renamed/deleted/conflictingly modified | Invoke `skills/investigate/SKILL.md` with state-analyzer custom mission per `agent-taxonomy.md`; user chooses adapt or archive |

**Rewound HEAD** (`git merge-base --is-ancestor <HEAD> <baseline.head>` succeeds
AND HEAD ≠ baseline.head) is classified **conflicting** — the baseline commit
is ahead of the current HEAD in history, so changes recorded against baseline
are no longer reflected in the working tree; resume MUST NOT proceed without
user confirmation.

**Renamed files**: when checking state-referenced paths, use
`git log --follow --oneline <path>` AND `git log --diff-filter=R --name-status <baseline.head>..HEAD`.
A path listed in the state body that was renamed between baseline and HEAD
is treated as **conflicting**.

### `status_digest` algorithm (pinned)

Semantically: SHA-256 hex (lowercase) of the byte-for-byte output of
`LC_ALL=C git status --porcelain=v1 -z` with no trailing newline added.

Cross-platform implementation (POSIX shell):

```
LC_ALL=C git status --porcelain=v1 -z | { sha256sum 2>/dev/null || shasum -a 256; } | awk '{print $1}'
```

Node.js implementation (for `.mjs` hooks):

```
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
const buf = execFileSync("git", ["status", "--porcelain=v1", "-z"],
  { env: { ...process.env, LC_ALL: "C" } });
const digest = createHash("sha256").update(buf).digest("hex");
```

- `LC_ALL=C` removes locale variation.
- `--porcelain=v1` is the stable format (pinned since git 2.11).
- `-z` uses NUL line terminators (avoids whitespace ambiguity).
- `sha256sum` (GNU coreutils) and `shasum -a 256` (BSD/macOS) produce the
  same lowercase hex; the fallback makes the shell pipeline cross-platform.
- Node's `crypto.createHash("sha256")` produces the same digest byte-for-byte.

Consumers MUST produce an identical digest regardless of implementation.
Variations produce different digests and will cause false drift.

---

## Archive and Completion Lifecycle

A workflow reaches terminal state when `current_phase` enters a whitelist
terminal value.

On terminal state:

1. Update frontmatter: `current_phase` → terminal value, `next_action: "archive"`.
2. Move the workflow file from `workflows/<id>.md` to `archive/<id>.md`
   (atomic rename).
3. Remove the entry from the active registry.
4. If active registry has no more entries, leave the active registry with
   `active: []` — do not delete the file.

**Auto-archive** (performed by Stop hook) requires the applicable subset
of these conditions per workflow type:

- A1 (all types): `current_phase` equals one of the terminal whitelist
  (`commit-complete`, `summary-complete`).
- A2 (`/start` and `/fix` only; NOT `/audit`): `git rev-parse HEAD`
  differs from `git_baseline.head` (real progress occurred).
- A3 (`/start` and `/fix` only; NOT `/audit`):
  `git log baseline.head..HEAD --format=%s` contains at least one
  commit whose subject matches the workflow's convention:
  - `/start`: `^feat(\(.+\))?!?:`
  - `/fix`: `^fix(\(.+\))?!?:`
- A4 (all types): no other entry in the active registry has `parent`
  (the registry's field name for the parent workflow id) equal to this
  workflow's id — no active children blocking archival.

For `/start` and `/fix`: all four conditions apply (A1 + A2 + A3 + A4).
For `/audit`: only A1 + A4 apply (audit reaches `summary-complete`
without requiring a commit; its terminal is a summary table in body).

If any condition fails, the Stop hook exits silently. No spammy repetition
per Stop event — state stays intact; user may trigger manual archive via
`/omcc-dev:resume archive <id>`.

**Range-based commit scan** (A3): scans the full range
`baseline.head..HEAD`, so squash-merge commits on the target branch are
handled correctly — the original feat/fix commit is discovered. Amended
commits (subject changed after workflow completion) fail A3, and the
workflow requires manual archive.

**Auto-archive idempotency**: a Stop hook event for a workflow already in
`archive/` (registry still has stale entry) detects the inconsistency and
updates the active registry to remove the stale entry. Archive operations are
idempotent at the file-system level (rename of already-absent source is a
no-op with specific error code; hooks handle this case explicitly).

**Manual archive**: `/omcc-dev:resume archive <id>` moves any workflow
into `archive/` with user confirmation, bypassing all auto-archive
conditions — including the "no active children" check (with a warning).

---

## Cross-workflow Handoff

Scenario: during `/audit` Phase 5 remediation, a finding is marked
`fix-now` and the user transitions to `/fix`.

**Write ownership** (pinned):

1. Child `/fix` command owns **both** writes — bootstrap of the child
   file AND update of the parent's `findings[i].decision`. This avoids
   requiring the parent `/audit` to be actively running.
2. Child's parent write:
   - Acquires a separate lock on the parent file
   - Sets `findings[i].decision = "fix-now"` and
     `findings[i].child_workflow = <child_id>`
   - Releases the lock
3. If the parent file is not in `workflows/`, child checks `archive/` as a
   fallback. If parent is found in `archive/`, child writes a warning to
   stderr and proceeds with bootstrap but `parent_workflow` is recorded as
   `<parent_id>` and `originating_finding` recorded — the parent's
   findings field is NOT updated (parent already archived).
4. On child's terminal archive, child updates the parent's
   `findings[i].resolved_commit` with the child's commit SHA.

**Parent archive gating**: when Stop hook evaluates a parent workflow for
auto-archive, condition A4 checks the active registry for entries with
`parent: <this id>`. Parent cannot auto-archive while active children
exist. Manual archive bypasses A4 with a warning; child's
`parent_workflow` reference becomes a pointer into `archive/` — child
resolution MUST search both `workflows/` and `archive/`.

---

## Hook Responsibilities

Plugin-level hooks live at `hooks/hooks.json` with `.mjs` scripts.
Event names pin to the Claude Code hook spec; see the hooks guide at
[code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide)
for the authoritative event catalog.

### Execution contract (common to all hooks)

Hooks MUST:

- Read and write only under `<cwd>/.claude/omcc-dev/`.
- Shell out only to `git` and only with the subcommands listed below.
- Make no network requests.
- Validate stdin JSON shape with try/catch; on unexpected input, exit 0
  with a diagnostic to stderr (non-blocking).
- Validate every `workflow_id` read from state or registry against the
  pinned regex before using it as a path component.
- Emit no stdout except as defined per-hook (SessionStart emits summary;
  PreCompact and Stop emit nothing on success).
- Exit 0 on any unexpected internal error (non-blocking by default).

Allowed git subcommands (hook context only; commands may additionally
invoke other git subcommands such as `check-ignore` during Phase 0):
`branch --show-current`, `rev-parse HEAD`, `rev-parse --show-toplevel`,
`status --porcelain=v1 -z`, `log -1 --format=%H`, `log -1 --format=%s`,
`log <range> --format=%s`, `merge-base --is-ancestor`,
`log --follow --oneline`, `log --diff-filter=R --name-status`.

### SessionStart (matcher: `compact`)

- **Purpose**: Re-inject active workflow summary after compaction.
- **Reads**: the active registry + each listed active workflow file's frontmatter.
- **Writes**: none.
- **Stdout** (injected into Claude context as plain UTF-8):

  When ≥1 active workflow:
  ```
  Active omcc-dev workflow(s):
  - <id> (<type>) phase=<current_phase> next="<next_action>"
  ... one line per active workflow ...
  If this hook did not fire, run /omcc-dev:resume for full rehydration.
  ```

  When zero active workflows: **no output** (silent exit 0). SessionStart
  fires on every compaction, so the silent path is the common case.

- **Frontmatter sanitization** (applied to every string value before
  injection): length cap 512 chars, strip control characters (`\x00-\x08`,
  `\x0b-\x1f`, `\x7f`), refuse to echo backtick-quoted shell content
  (reject backticks).
- **Body content is NOT injected** via SessionStart.

### PreCompact (no matcher)

- **Purpose**: Append mechanical snapshot to each active workflow's body
  before compaction loses context.
- **Per workflow**: use the Update atomic-write sequence (not an
  append-only shortcut). Read current file, build new content with
  updated `updated_at` + new snapshot appended to body + oldest snapshot
  removed if body would exceed the 50-snapshot cap, then atomic write.
- **Snapshot block format**:

  ```
  <!-- pre-compact snapshot -->
  timestamp: <ISO 8601 UTC, Z suffix>
  branch: <current>
  head: <current HEAD SHA>
  status: <git status --porcelain=v1 output; filtered>
  ```

- **Status filter**: lines whose path matches any of `.env*`, `*.pem`,
  `*.key`, `id_rsa*`, `*.p12`, `*.pfx` are omitted to reduce sensitive
  filename leakage.
- **Idempotency**: if the last snapshot timestamp is within the past 60
  seconds, skip the write entirely (avoids duplicates under rapid recompact).

### Stop (no matcher)

- **Purpose**: Validate required state fields; auto-archive on terminal commit.
- **First**: if stdin JSON's `stop_hook_active == true`, exit 0
  immediately to avoid infinite loops (per Claude Code docs).
- **Validation**: for each active workflow, verify `current_phase` and
  `next_action` are non-empty. If empty, write a diagnostic to stderr and
  continue (non-blocking; stderr is debug-log only per Claude Code hook
  conventions, not user-visible).
- **Auto-archive**: apply the four-condition check (A1–A4) from Archive
  and Completion Lifecycle. All must pass. If so, atomically move the
  workflow file into `archive/` and update the active registry.
- **Reconciliation**: if a workflow is listed in the active registry but the file
  is already in `archive/`, the Stop hook removes the stale entry — this
  is the idempotent recovery path.

### Fallback principle

Hook execution is best-effort. If hooks do not fire (Claude Code version
differences, plugin load issues, first-run timing), command behavior MUST
still work via `/omcc-dev:resume`. Do not rely on hooks for correctness —
they smooth UX only.

---

## Legacy design-context.md Migration

When a command's Phase 0 detects a file at `<cwd>/.claude/design-context.md`:

1. Acquire a lock via `fs.openSync('<cwd>/.claude/design-context.md.migrate.lock', 'wx')`
   to serialize concurrent sessions attempting migration. On `EEXIST`,
   wait up to 10s before aborting with a diagnostic.
2. Present the user with three choices:
   - **Import**: parse the four sections (Decision / Architecture / Plan /
     Deliverable Progress) and create a new workflow file at
     `<cwd>/.claude/omcc-dev/workflows/start-<now-timestamp>-migrated-<shortid>.md`.
     Required fields on the new file: `schema: 1`; `workflow_type: start`;
     `workflow_id` follows the migration exception format; `started_at`
     and `updated_at` = migration time; `git_baseline` = current repo
     state (baseline is unknowable from legacy); imported sections are
     sanitized (512-char cap, control-char strip) before writing into
     their respective workflow-type-specific fields. Remove the legacy
     file on success.
   - **Archive**: move the legacy file into
     `<cwd>/.claude/omcc-dev/archive/design-context-<now-timestamp>.md`
     unchanged.
   - **Delete**: remove the file. Warn the user that any in-flight
     workflow context is lost.
3. If the file has no parseable sections, offer only Archive or Delete.
4. Release the lock. Migration happens at most once per Phase 0 per cwd
   per session; state file is authoritative thereafter.

Treat legacy file content as **untrusted user-writable input**: a hostile
repository clone may contain adversarial content. Sanitize before writing
to the new frontmatter.

---

## Failure Handling

| Condition | Detection | Action |
|---|---|---|
| Missing state on `/omcc-dev:resume` | active registry not found | Inform user. Suggest `claude --continue` (native), fresh `/start`, or manual restore guide |
| Corrupt state (parse error) | YAML frontmatter parse fails | Attempt `<file>.bak`. If `.bak` passes validation (schema + workflow_id regex + required fields present), offer restore. Otherwise archive corrupt file and treat as missing |
| Partial write | Tempfile exists but rename failed | Remove tempfile. `.bak` is authoritative. Retry once; if still failing, surface error |
| Stale state (referenced files absent or inconsistent) | Drift classification returns `conflicting` | Invoke `skills/investigate/SKILL.md` with state-analyzer mission per `agent-taxonomy.md`; user decides adapt/archive |
| Unknown schema version | `schema` field exceeds latest known | Warn user. Offer archive/abort. Never silently proceed |
| Hook does not fire | No detection possible from inside the agent | `/omcc-dev:resume` is the fallback. Command docs remind users at phase boundaries |
| Native `/rewind` or `claude --continue` leaves state newer than transcript | `updated_at` post-dates conversation context (compared against `CLAUDE_CONVERSATION_LOG` file mtime if available, else user-confirmed) | `/omcc-dev:resume` warns and offers roll-back to `<file>.bak` or archive of divergent state |
| `.bak` restoration | User accepts restore | Validate `.bak` against schema + id regex + required fields BEFORE promoting. Show a diff to the user; user confirms before rename |
| `flock`/advisory lock unavailable | Exclusive-create of lock sentinel fails for reasons other than `EEXIST` | Degrade to rename-only atomicity; log that locking is unavailable |

---

## Security Considerations

State files live in the user's cwd and are writable by any process with
filesystem access. Hooks inject state content into Claude's context.
State is therefore treated as **untrusted input**.

### Filesystem boundary

- Directory created with `chmod 0700`; workflow files `chmod 0600`.
  Explicit — never rely on umask.
- Symlink defense: before writing `workflows/<id>.md` or similar, hooks
  and commands MUST verify the path is not a pre-existing symlink via
  `lstat`, or use `fs.openSync(path, 'wx')` to fail on existing
  non-regular targets.
- `<cwd>/.claude/omcc-dev/` MUST be gitignored. Commands SHOULD run
  `git check-ignore .claude/omcc-dev/` at Phase 0 and warn if unignored.

### Path safety

- Every `workflow_id` used as a path component MUST match the regex in
  the Workflow IDs subsection (or the migration exception). Reject
  otherwise.
- `parent_workflow` MUST be validated against the workflow-id regex
  before use.
- `originating_finding` MUST be validated against the **finding-id
  regex** from the Finding IDs subsection (`^finding-[0-9]+$`), NOT the
  workflow-id regex. Finding ids are never used as file-path components.

### Secrets hygiene

- `$ARGUMENTS` (user input) MUST be scrubbed before being stored as
  `original_request`. Apply the scrub below. Patterns are designed to
  work in **both PCRE and ECMAScript / Node.js `RegExp`** — no inline
  flag modifiers (`(?i:...)` or `(?i)`) are used, because ECMAScript
  does not support them. Case-insensitivity is specified via an
  engine-level flag (e.g., `new RegExp(pattern, "i")` in Node.js, or
  `(?i)`-style flag at construction time in Python/PCRE).

  Apply each pattern and replace matches with `[REDACTED]`:
  - `(sk|pk|ghp|gho|ghu|ghs|ghr|github_pat|xoxb|xoxp|AKIA)[_A-Za-z0-9-]{8,}`
    (case-sensitive; covers `sk-ant-api…`, `github_pat_…`, GitHub
    classic tokens, Slack, AWS access keys)
  - `Bearer\s+[A-Za-z0-9._~+/=-]+` (case-sensitive; HTTP header
    convention is title-cased)
  - `(password|token|secret|api[_-]?key|authorization)\s*[:=]\s*\S+`
    — applied with engine-level **case-insensitive flag** (e.g.,
    `new RegExp(..., "i")`)
- The scrub is lossy and not perfect; commands MAY additionally shorten
  `original_request` to a semantic summary. State body also follows the
  scrub rule.
- `git status --porcelain` in PreCompact snapshots filters sensitive
  filename patterns (see PreCompact hook).
- Do NOT log environment variables, PII, or token values into state.

### Injection defense

- SessionStart injects only **sanitized frontmatter strings** (512-char
  cap, control-chars stripped, backticks rejected) — body is never
  auto-injected.
- `/omcc-dev:resume` reads body via the `Read` tool, which frames content
  as tool output rather than instructions; agent prompts treat this as
  descriptive context only.
- Hooks never echo body content to stdout.

### Integrity

- `status_digest` is a **change detector**, not a cryptographic
  integrity check. State files are not signed. A hostile process with
  write access to `<cwd>/.claude/omcc-dev/` can arbitrarily manipulate
  workflow state; the filesystem permission recommendation (0700/0600) is
  the actual trust boundary.
- `.bak` files are trusted only after the validation in Failure Handling
  (schema + id regex + required-fields). Never silently promoted.

### Hook constraints

See the "Execution contract" subsection under Hook Responsibilities.
If the plugin cache itself is compromised, hook integrity is lost — this
is out of scope; Claude Code plugin trust is the declared boundary.

### Body size DoS

Body is capped at 50 PreCompact snapshots; oldest trimmed atomically on
overflow. This bounds file size and protects consumers that `Read` the
full file.

---

## Related

- `orchestration.md` — agent composition (subagents used during resume
  drift analysis)
- `ensemble-protocol.md` — Codex ensemble semantics; source of the
  `ensemble_type` enum
- `presentation-protocol.md` — mode persistence across resume (state
  records the user's chosen presentation mode in the body)
- `ensemble-affinity.md` — Ensemble Affinity is recorded in state as
  `task_profile.ensemble_affinity`
- `agent-taxonomy.md` — `state-analyzer` pattern is the default
  investigation mission for conflicting drift
