# Output File Rules

Shared output-file conventions for skills that write design documents
(`brief-generation`, `poster`, `design-planning`, and future domain skills).

## Directory structure

Each design project is saved in its own directory:

```
./output/YYYY-MM-DD_project-name/
├── design_brief.md
├── poster_spec.md
└── design_plan.md
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

- Filenames within the directory are fixed: design_brief.md, poster_spec.md, design_plan.md
- **Naming convention**: multi-word filenames use `snake_case` (lowercase with
  underscore separator). Single-word filenames stay lowercase. Apply this rule
  when introducing new output file types.
- Do not use `_2`, `_3` suffixes. Separate projects by directory.

## Overwrite protection

If the target output directory already exists, ask the user before overwriting.

## Other

- Create the `output` directory if it does not exist.
- File encoding: UTF-8
