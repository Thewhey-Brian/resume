"""Pull Word tracked-changes and comments back into cv.html.

Round-trip:  build.sh  →  edit the .docx in Word (track changes + comments)  →  review.py

    python review.py reviewed.docx              # report only, writes REVIEW.md
    python review.py reviewed.docx --apply      # also rewrite cv.html

Tracked insertions/deletions are applied automatically when the paragraph maps
cleanly onto a single HTML fragment. Comments are never applied — they need a
judgement call — so they are listed in REVIEW.md with the text they anchor to.
"""
import re
import sys
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


# ── read the .docx ──────────────────────────────────────────────────────
def load(path):
    import xml.etree.ElementTree as ET

    z = zipfile.ZipFile(path)
    doc = ET.fromstring(z.read("word/document.xml"))
    comments = {}
    if "word/comments.xml" in z.namelist():
        for c in ET.fromstring(z.read("word/comments.xml")).iter(f"{W}comment"):
            comments[c.get(f"{W}id")] = "".join(t.text or "" for t in c.iter(f"{W}t")).strip()
    return doc, comments


def is_bold(run):
    rpr = run.find(f"{W}rPr")
    if rpr is None:
        return False
    b = rpr.find(f"{W}b")
    return b is not None and b.get(f"{W}val") not in ("0", "false")


def is_italic(run):
    rpr = run.find(f"{W}rPr")
    if rpr is None:
        return False
    i = rpr.find(f"{W}i")
    return i is not None and i.get(f"{W}val") not in ("0", "false")


def read_para(p):
    """→ (original_runs, revised_runs, comment_ids) where a run is (text, bold, italic)."""
    orig, rev, cids, open_c = [], [], [], []
    for el in p.iter():
        tag = el.tag
        if tag == f"{W}commentRangeStart":
            open_c.append(el.get(f"{W}id"))
        elif tag == f"{W}commentRangeEnd":
            cid = el.get(f"{W}id")
            if cid in open_c:
                open_c.remove(cid)
        elif tag == f"{W}commentReference":
            cids.append(el.get(f"{W}id"))
        elif tag == f"{W}r":
            parent_tags = {a.tag for a in p.iter() if el in list(a)}
            inserted = any(t == f"{W}ins" for t in parent_tags)
            deleted = any(t == f"{W}del" for t in parent_tags)
            text = "".join((t.text or "") for t in el.findall(f"{W}t"))
            dtext = "".join((t.text or "") for t in el.findall(f"{W}delText"))
            run = (text or dtext, is_bold(el), is_italic(el))
            if not run[0]:
                continue
            if deleted:
                orig.append(run)
            elif inserted:
                rev.append(run)
            else:
                orig.append(run)
                rev.append(run)
    # drop the leading "–" bullet-marker run: it is layout, not content
    for lst in (orig, rev):
        while lst and lst[0][0].strip() in ("–", "-", ""):
            lst.pop(0)
    return orig, rev, cids


def flat(runs):
    return norm("".join(t for t, _, _ in runs))


def norm(t):
    return re.sub(r"\s+", " ", t).replace(" ", " ").strip()


def to_html(runs):
    """Re-emit runs as HTML, merging adjacent runs with the same style."""
    out, merged = [], []
    for text, b, i in runs:
        if merged and merged[-1][1] == b and merged[-1][2] == i:
            merged[-1] = (merged[-1][0] + text, b, i)
        else:
            merged.append((text, b, i))
    for text, b, i in merged:
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if b:
            text = f"<b>{text}</b>"
        if i:
            text = f"<i>{text}</i>"
        out.append(text)
    return "".join(out).strip()


# ── locate the matching fragment in cv.html ─────────────────────────────
FRAG = re.compile(r"<(li|div)\b[^>]*>(.*?)</\1>", re.S)


ENT = {"&amp;": "&", "&nbsp;": " ", "&lt;": "<", "&gt;": ">", "&times;": "×", "&rho;": "ρ"}


def unescape(t):
    for a, b in ENT.items():
        t = t.replace(a, b)
    return t


def plain(html):
    return norm(unescape(re.sub(r"<[^>]+>", "", html)))


def find_fragment(html, target):
    """Return (start, end, inner) of the fragment whose text equals target."""
    for m in FRAG.finditer(html):
        if plain(m.group(2)) == target:
            return m.start(2), m.end(2), m.group(2)
    return None


# ── main ────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    docx, apply = sys.argv[1], "--apply" in sys.argv
    doc, comments = load(docx)
    html = open("cv.html", encoding="utf-8").read()

    edits, notes, skipped, matched_any = [], [], [], []
    for p in doc.iter(f"{W}p"):
        orig, rev, cids = read_para(p)
        o, r = flat(orig), flat(rev)
        o, r = (re.sub(r"^\d+\.\s*", "", x) for x in (o, r))
        if not o and not r:
            continue
        for cid in cids:
            if cid in comments:
                notes.append((comments[cid], r or o))
        matched_any.append(find_fragment(html, o) is not None or find_fragment(html, r) is not None)
        if o == r:
            continue
        hit = find_fragment(html, o)
        if not hit:
            skipped.append((o, r, "no matching fragment in cv.html"))
            continue
        start, end, inner = hit
        if "<a " in inner or "<span" in inner:
            skipped.append((o, r, "fragment contains a link or span — edit by hand"))
            continue
        edits.append((o, r))
        if apply:
            html = html[:start] + to_html(rev) + html[end:]

    with open("REVIEW.md", "w", encoding="utf-8") as f:
        f.write(f"# Review extracted from `{docx}`\n\n")
        f.write(f"## Tracked edits ({len(edits)} applied)\n\n" if apply
                else f"## Tracked edits ({len(edits)} pending)\n\n")
        for o, r in edits:
            f.write(f"- **was:** {o}\n- **now:** {r}\n\n")
        if skipped:
            f.write(f"## Needs manual edit ({len(skipped)})\n\n")
            for o, r, why in skipped:
                f.write(f"- _{why}_\n  - **was:** {o}\n  - **now:** {r}\n\n")
        f.write(f"## Comments ({len(notes)}) — judgement required, never auto-applied\n\n")
        for text, anchor in notes:
            f.write(f"- **{text}**\n  - anchored to: {anchor[:200]}\n\n")

    if apply:
        open("cv.html", "w", encoding="utf-8").write(html)
        print(f"cv.html updated — {len(edits)} edit(s) applied")
    else:
        print(f"{len(edits)} edit(s) ready to apply (re-run with --apply)")
    print(f"{len(skipped)} need manual work, {len(notes)} comment(s) → see REVIEW.md")
    if matched_any:
        hits = sum(matched_any)
        print(f"paragraph→fragment match rate: {hits}/{len(matched_any)}")


if __name__ == "__main__":
    main()
