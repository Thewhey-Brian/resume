---
name: cv-edit
description: Edit, rebuild, or review Xinyu Guo's CV/resume. Use whenever the task touches the CV — changing a bullet, adding a role or publication, applying Word tracked-changes and comments from a reviewed .docx, tailoring the CV to a specific job posting, or rebuilding the PDF/DOCX. Triggers on "CV", "resume", "my CV", "cv.html", "the Word version", "tracked changes", "review comments", "tailor for <company>", "rebuild the CV", or any path under cv_build/.
---

# Editing the CV

The CV lives at `~/Desktop/Reserach/cv_build/` (git remote: `github.com/Thewhey-Brian/resume`).

**`cv.html` is the only source of truth.** It holds both content and print CSS. The PDF and
DOCX are generated from it. Never edit the `.docx` expecting changes to persist — they are
overwritten on the next build unless pulled back through `review.py`.

## The two workflows

### A. Direct edit (default — use this when the user tells you what to change)

```bash
cd ~/Desktop/Reserach/cv_build
# edit cv.html
./build.sh
```

`build.sh` writes `dist/Xinyu_Guo_CV.{pdf,docx}`, syncs both to
`~/Downloads/Xinyu_CV/Xinyu_Guo_Anthropic_LifeSci.{pdf,docx}`, prints the page count, and
warns if the layout has spilled past two pages.

### B. Word review round-trip (use when the user says they edited the .docx)

```bash
.venv/bin/python review.py ~/Downloads/Xinyu_CV/Xinyu_Guo_Anthropic_LifeSci.docx           # report → REVIEW.md
.venv/bin/python review.py ~/Downloads/Xinyu_CV/Xinyu_Guo_Anthropic_LifeSci.docx --apply   # rewrite cv.html
./build.sh
```

Always run report mode first and read `REVIEW.md` before `--apply`.

- **Tracked insertions/deletions** apply automatically (bullets, context lines, publications).
- **Comments never apply automatically** — they are rewrite instructions, not substitutions.
  Read them from `REVIEW.md` and act on each one deliberately.
- **"Needs manual edit"** entries are composite lines (role + date in one Word paragraph),
  headings, education rows, and skills rows. Edit those in `cv.html` by hand.
- If Word has the file open, `build.sh` skips the sync and warns. Tell the user to close it.

## Editing cv.html safely

Whitespace-tolerant replacement, because bullets wrap across lines and exact-match edits fail:

```python
import re
def rep(a, b):
    global s
    m = re.compile(r'\s+'.join(re.escape(w) for w in a.split())).search(s)
    assert m, 'NOT FOUND: ' + a[:70]
    s = s[:m.start()] + b + s[m.end():]
```

Assert on every replacement and write the file only at the end, so a failed match leaves
`cv.html` untouched rather than half-edited.

Landmarks:

| What | Where |
|---|---|
| Bullet | `<li>` inside `<ul>` |
| Role title / employer | `<div class="role">` / `<span class="org">` |
| Date (right rail) | `<div class="when">` |
| Context line under a role | `<div class="sub">` |
| Project year / repo link | `<span class="yr">` |
| Skills row | `<div class="kv">` |
| Publication | `<li>` inside `<ol class="pubs">` |

## House style — match it, do not drift

- **Two pages, hard limit.** `build.sh` warns. To reclaim space, tighten `.entry` and `h2`
  margins or cut words — do not shrink below 9pt body.
- **Plain prose with rationed bold.** Roughly one bolded item per bullet: the number or method
  a reviewer should stop on. Comparison baselines stay unbolded so the headline figure wins.
  Never bold a whole opening clause — that was tried and rejected as "bold everywhere".
- **Verb-first bullets** stating the contribution, not the artifact. Results and impact over
  activity. Never announce a publication in an experience bullet ("Published X in Y") — state
  the finding; the paper belongs in Selected Publications.
- **No unnecessary infrastructure jargon.** "13 hosted genomic model endpoints", not
  "13 scale-to-zero SageMaker async GPU endpoint configurations".
- Entries may split across a page break; `break-after: avoid` keeps headers with their first
  bullet. Do not reintroduce `break-inside: avoid` on entries — it strands whole blocks and
  cascades into a third page.

## Claim guardrails — do not weaken these

- "expanded the reviewable evidence space" / "rescued deprioritized variants", never
  "found N actionable variants".
- "mechanism-level concordance", never "clinically validated".
- "outperformed evaluated implementations on this cohort", never universal SOTA.
- Model predictions are not clinical evidence.
- **Never invent a metric.** Every number must trace to an artifact under
  `~/Desktop/Reserach/` or to something the user stated. If a figure is needed and unverified,
  say so and ask rather than estimating.

## Open items to resolve when the user is available

- `~140 GB` in the FFPE bullet is inferred from
  `ffpe_artifact_filter/docs/data_inventory.md` ("~139 GB, 55 objects"). It excludes the
  internal 21-patient cohort, so the true figure is higher. The user has not confirmed it.
- The CV says the LLM was **560M params on 8×A100**; the linked `nanochat` repo README says
  **1.9B on 8×H100**. One is wrong and the repo is linked from the CV.

## Committing

The repo is public. Content is already published, so incremental commits are fine.

```bash
git add -A && git commit -m "..." && git push origin main
```

`REVIEW.md`, `.venv/`, and `cv.pdf` are gitignored; `dist/` is committed so the README's
PDF link resolves.
