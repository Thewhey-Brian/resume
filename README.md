# CV — Xinyu (Brian) Guo

My CV, written once in HTML/CSS and built to both PDF and Word from that single source.

**[→ Download the PDF](dist/Xinyu_Guo_CV.pdf)** &nbsp;·&nbsp; [Word version](dist/Xinyu_Guo_CV.docx)

Computational biology · genomic foundation models · scientific AI agents.

---

## Why not just write it in Word

Word can't hold a two-column date rail without drifting, and its PDF export degrades
hairline rules and letterspacing. But recruiters and application portals still ask for
`.docx`. So the content lives in one HTML file and two renderers read it:

| Output | Renderer | Purpose |
|---|---|---|
| `dist/Xinyu_Guo_CV.pdf` | headless Chrome, CSS print layout | what I actually send |
| `dist/Xinyu_Guo_CV.docx` | `python-docx`, Word-native styles | portals that reject PDFs |

The two can't drift, because `make_docx.py` parses `cv.html` rather than keeping its own copy
of the text.

## Build

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./build.sh
```

Outputs land in `dist/`. To also copy them somewhere else:

```bash
CV_OUT=~/Documents/applications ./build.sh
```

`build.sh` prints the page count and warns if the layout has spilled past two pages.

Requires macOS with Google Chrome (for `--headless --print-to-pdf`) and Python 3.

## Editing

Almost everything is content, not code. Bullets look like this:

```html
<li>Built <b>OncoS2F</b>, a scientific agent that translates natural-language
    research requests into executable workflows ...</li>
```

Rewrite the text between `<li>` and `</li>`; wrap emphasis in `<b>` or `<i>`. Other landmarks:

| What | Where |
|---|---|
| Role title | `<div class="role">` |
| Employer / institution | `<span class="org">` |
| Dates (right rail) | `<div class="when">` |
| Context line under a role | `<div class="sub">` |
| Skills rows | `<div class="kv">` |

Then run `./build.sh`.

## Design notes

- **Charter** for body and name, **Helvetica Neue** for section labels and the date rail.
  A serif wordmark over sans navigation reads as scholarly rather than templated.
- 9.2pt type on 1.36 leading — smaller type with more air beats larger type packed tight.
- One accent colour (deep oxblood, `#7a1f2b`) on section labels and the tagline. Nothing else
  is coloured.
- Bold is rationed to roughly one item per bullet: the number or method an interviewer should
  stop on. Comparison baselines stay unbolded so the headline figure wins.
- Lining tabular figures on dates so the right rail aligns optically.
- Entries may split across a page break, but `break-after: avoid` on the role line means a
  heading is never stranded at the foot of a page.

## Layout

```
cv.html          content + print CSS — the single source of truth
make_docx.py     parses cv.html, emits a styled .docx
build.sh         renders both, reports page count
requirements.txt python-docx, pypdf
dist/            build output (committed, so the PDF is linkable)
```

## License

Layout and build tooling: MIT — reuse them freely. The CV content itself is mine.
