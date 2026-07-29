# CV — Xinyu (Brian) Guo

**[→ Download PDF](dist/Xinyu_Guo_CV.pdf)** &nbsp;·&nbsp; [Word version](dist/Xinyu_Guo_CV.docx)

Computational biology · genomic foundation models · scientific AI agents.

One HTML file is the source of truth. The PDF and the Word document are both generated from
it, and edits made in Word come back to it — so the two outputs can never drift apart.

```
cv.html  ──┬──→  Chrome headless  ──→  dist/Xinyu_Guo_CV.pdf     ← what I send
           └──→  python-docx      ──→  dist/Xinyu_Guo_CV.docx    ← for portals that reject PDFs
                                            │
                        review.py  ←────────┘  tracked changes + comments back into cv.html
```

---

## Why not just write it in Word

Word can't hold a two-column date rail without drifting, and its PDF export degrades hairline
rules and letterspacing. But recruiters and application portals still ask for `.docx`. So the
content lives in one place and two renderers read it: Chrome for the layout I actually want,
`python-docx` for a Word file with native styles rather than a flattened export.

Word remains a good place to *mark up* a CV, which is what `review.py` is for.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./build.sh
```

Outputs land in `dist/`. `build.sh` prints the page count and warns if the layout has spilled
past two pages. Requires macOS with Google Chrome and Python 3.

To also copy the results somewhere:

```bash
CV_OUT=~/Documents/applications ./build.sh
```

## Editing

Almost everything is content, not code:

```html
<li>Built <b>OncoS2F</b>, a scientific agent that translates natural-language
    research requests into executable workflows ...</li>
```

Rewrite the text between `<li>` and `</li>`; wrap emphasis in `<b>` or `<i>`. Then `./build.sh`.

| What | Where |
|---|---|
| Bullet | `<li>` inside `<ul>` |
| Role title / employer | `<div class="role">` / `<span class="org">` |
| Date (right rail) | `<div class="when">` |
| Context line under a role | `<div class="sub">` |
| Skills row | `<div class="kv">` |
| Publication | `<li>` inside `<ol class="pubs">` |

## Review loop

```bash
./build.sh                              # then open the DOCX in Word,
                                        # turn on Track Changes, edit, leave comments

python review.py reviewed.docx          # report what changed → REVIEW.md
python review.py reviewed.docx --apply  # rewrite cv.html with the tracked edits
./build.sh                              # regenerate both outputs
```

`review.py` reads `word/document.xml` directly, splits `w:ins`/`w:del` into before/after text,
and reconstructs bold and italic from the Word runs so styling survives the round trip.

**Tracked insertions and deletions apply automatically** wherever a Word paragraph maps onto a
single HTML fragment — every bullet, context line, and publication.

**Comments never apply automatically.** A comment like *"use the results of that, like across
48 tissues, and potential impact"* is a rewrite instruction, not a substitution; a tool that
guessed would corrupt the document quietly. Comments are listed in `REVIEW.md` with the text
they were anchored to.

Anything that can't be mapped safely — headings, and the composite lines that pack a role title
and its date into one Word paragraph — is reported under *Needs manual edit* with both the
before and after text. Nothing is dropped silently.

`build.sh` also syncs the outputs to `~/Downloads/Xinyu_CV/` under the name used for
applications, so each review round starts from current content. It detects Word's lock file and
skips the copy if the document is open, rather than overwriting an in-progress review.

## Claude Code skill

`.claude/skills/cv-edit/` packages the whole workflow — both editing paths, the house style,
the claim guardrails, and the safe-replacement pattern for `cv.html` — so an agent picks up the
conventions instead of rediscovering them. Symlink it to use it anywhere:

```bash
ln -s "$PWD/.claude/skills/cv-edit" ~/.claude/skills/cv-edit
```

## Design notes

- **Charter** for body and name, **Helvetica Neue** for section labels and the date rail. A
  serif wordmark over sans navigation reads as scholarly rather than templated.
- 9.2pt on 1.36 leading. Smaller type with more air beats larger type packed tight.
- One accent colour (deep oxblood, `#7a1f2b`) on section labels and the tagline. Nothing else
  is coloured.
- Bold is rationed to about one item per bullet: the number or method a reviewer should stop on.
  Comparison baselines stay unbolded so the headline figure wins.
- Lining tabular figures on dates so the right rail aligns optically.
- Entries may split across a page break, but `break-after: avoid` on the role line means a
  heading is never stranded at the foot of a page. Making entries unsplittable instead causes
  whole blocks to jump pages and cascades into a third page.

## Files

```
cv.html                      content + print CSS — the single source of truth
make_docx.py                 parses cv.html, emits a styled .docx
review.py                    pulls Word tracked-changes + comments back into cv.html
build.sh                     renders both, reports page count, syncs the review copy
requirements.txt             python-docx, pypdf
.claude/skills/cv-edit/      Claude Code skill for this workflow
dist/                        build output (committed, so the PDF link resolves)
REVIEW.md                    generated review report (gitignored)
```

## License

Layout and build tooling: MIT — reuse them freely. The CV content itself is mine.
