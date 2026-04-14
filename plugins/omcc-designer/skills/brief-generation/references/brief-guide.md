# Brief Generation Guide

Detailed rules for generating design briefs in Phase 3.
This guide ensures briefs are complete, accurate, and usable across sessions.

---

## Assembly Rules

### Confirmed Decision Principle enforcement

For each brief section:

1. **Confirmed fields**: Include with full detail. No `[unconfirmed]` tag.
2. **Unconfirmed fields with recommendation**: Include the designer's
   recommendation with explicit `[unconfirmed]` tag and rationale:
   ```
   - Primary: #2563EB — royal blue [unconfirmed — designer recommendation
     based on professional/trust brand personality]
   ```
3. **Unconfirmed fields with no recommendation**: Mark as pending:
   ```
   - Accent font: [unconfirmed — to be decided]
   ```
4. **Omitted fields**: If the user explicitly said to skip a field,
   omit it entirely. Do not include placeholder text.

### Color code validation

Before writing hex codes to the brief:
- Verify format: `#RRGGBB` (6 characters, valid hex)
- Check contrast ratios for critical pairs:
  - Neutral dark on neutral light: minimum 4.5:1 (WCAG AA)
  - Accent on neutral light: minimum 3:1 (WCAG AA for large text)
- If contrast fails, **do not auto-adjust**. Instead, flag the issue in the
  brief with a warning note and recommend the user revisit the palette.
  The Confirmed Decision Principle prohibits modifying user-approved colors.

### Dimension consistency

Verify that Technical Specifications match the target medium:
- Poster dimensions should be standard poster sizes
- Digital dimensions should use pixels, not mm
- Resolution should match print (300 DPI) or digital (72-150 DPI)
- If bleed is specified for digital, flag as unnecessary

### Content map completeness

Verify:
- Every content element mentioned in the interview is in the Content Map
- Image zones have descriptions specific enough for AI prompt generation
- Content priority list includes all elements
- No duplicate content elements

---

## Decision Log Construction

The Decision Log table must accurately reflect the status of each section:

| Status | Criteria |
|--------|----------|
| confirmed | User explicitly confirmed during interview |
| partial | Some fields confirmed, others unconfirmed |
| unconfirmed | Designer recommendation only, user did not confirm |
| skipped | User explicitly chose to skip this section |

Source column must reference the specific interview step (Step A-E).

---

## Save Rules

### File path construction

```
./output/{YYYY-MM-DD}_{project-name}/design_brief.md
```

1. `YYYY-MM-DD`: Current date (creation date, not deadline)
2. `project-name`: From Step A project title
3. Apply sanitization rules from `CLAUDE.md` Output File Rules

### Overwrite protection

If the output directory already exists:
1. Check if design_brief.md already exists in it
2. If yes, ask: "A brief already exists for this project. Overwrite?"
3. If no, proceed

### Directory creation

Create the output directory if it does not exist.
Create the `output` directory if it does not exist.

---

## Quality Checklist

Before saving the brief, verify all items:

- [ ] All interview-confirmed items are present in the brief
- [ ] No unconfirmed items are encoded without `[unconfirmed]` tag
- [ ] All hex codes are valid 6-digit format
- [ ] Critical color contrast ratios meet WCAG AA
- [ ] Dimensions are consistent with target medium
- [ ] Resolution matches print/digital context
- [ ] Content Map includes all discussed content elements
- [ ] Image zones are descriptive enough for AI prompt generation
- [ ] Content priority list matches interview priority order
- [ ] Decision Log status accurately reflects each section
- [ ] Decision Log source correctly references interview steps
- [ ] File saved to correct output path
- [ ] Brief is self-contained (readable without conversation context)
