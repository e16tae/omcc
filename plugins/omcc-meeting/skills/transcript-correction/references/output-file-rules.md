# Output File Rules

Shared output-file conventions for skills that write meeting documents
(`transcript-correction`, `minutes`, `report`).

## Directory structure

Each meeting is saved in its own directory:

```
./output/YYYY-MM-DD_meeting-name/
├── corrected_transcript.md
├── minutes.md
└── report.md
```

## Directory naming

- `YYYY-MM-DD` is based on the meeting date. If unknown, use the processing date.
- `meeting-name` is derived from the agenda or topic collected in Phase 2 (max 15 characters).
- If the meeting name is unknown, use time-based fallback: `YYYY-MM-DD_HHMM`
- For standalone `/omcc-meeting:minutes` or `/omcc-meeting:report`: derive from input file metadata,
  or default to `YYYY-MM-DD_meeting`.

## Directory name sanitization

Before using a meeting name as a directory component, apply these rules:
- `/` → `-` (hyphen)
- Spaces → `_` (underscore)
- Remove filesystem-forbidden characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)
- If longer than 15 characters, truncate at 15 and remove trailing `_`

## Filenames

- Filenames within the directory are fixed: corrected_transcript.md, minutes.md, report.md
- **Naming convention**: multi-word filenames use `snake_case` (lowercase with
  underscore separator). Single-word filenames stay lowercase. Apply this rule
  when introducing new output file types.
- Do not use `_2`, `_3` suffixes. Separate meetings by directory.

## Overwrite protection

If the target output directory already exists, ask the user before overwriting.

## Other

- Create the `output` directory if it does not exist.
- File encoding: UTF-8
