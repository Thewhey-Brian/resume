#!/bin/bash
# Build the CV to PDF + DOCX from cv.html.
#
#   ./build.sh              build into ./dist
#   CV_OUT=~/somewhere ./build.sh   also copy the results there
#
# Requires: Google Chrome (PDF rendering), python3, and .venv (see README).
set -euo pipefail
cd "$(dirname "$0")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAME="Xinyu_Guo_CV"
DIST="dist"

[ -x "$CHROME" ] || { echo "✗ Google Chrome not found at $CHROME"; exit 1; }
[ -x .venv/bin/python ] || { echo "✗ .venv missing — run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"; exit 1; }

mkdir -p "$DIST"

# PDF — Chrome renders the CSS print layout
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$DIST/$NAME.pdf" "file://$PWD/cv.html" 2>/dev/null

# DOCX — python-docx rebuilds the same content with Word-native styling
.venv/bin/python make_docx.py "$DIST/$NAME.docx"

PAGES=$(.venv/bin/python -c "import pypdf,sys;print(len(pypdf.PdfReader('$DIST/$NAME.pdf').pages))" 2>/dev/null \
        || python3 -c "import fitz;print(fitz.open('$DIST/$NAME.pdf').page_count)")

echo "✓ built — PDF is $PAGES page(s)"
echo "  $DIST/$NAME.pdf"
echo "  $DIST/$NAME.docx"

# keep the review copy in sync, under the name used for applications
REVIEW_DIR="${CV_OUT:-$HOME/Downloads/Xinyu_CV}"
REVIEW_NAME="${CV_REVIEW_NAME:-Xinyu_Guo_Anthropic_LifeSci}"
if [ -d "$REVIEW_DIR" ]; then
  if [ -e "$REVIEW_DIR/~\$${REVIEW_NAME#?}.docx" ]; then
    echo "  ⚠︎ $REVIEW_NAME.docx is open in Word — close it, then re-run to sync"
  else
    cp "$DIST/$NAME.pdf"  "$REVIEW_DIR/$REVIEW_NAME.pdf"
    cp "$DIST/$NAME.docx" "$REVIEW_DIR/$REVIEW_NAME.docx"
    echo "  synced → $REVIEW_DIR/$REVIEW_NAME.{pdf,docx}"
  fi
fi

if [ "$PAGES" -gt 2 ]; then
  echo "  ⚠︎ over 2 pages — trim content, or tighten .entry / h2 margins in cv.html"
fi
