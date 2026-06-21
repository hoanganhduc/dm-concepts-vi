#!/usr/bin/env bash
# Finalize one panel-approved chapter: encode -> validate -> build -> commit ->
# advance the autonomous loop. Prints "NEXT=<letter|DONE>".
# Usage: finalize-letter.sh <letter>
set -euo pipefail
RAW="$1"
L="$(printf '%s' "$RAW" | tr '[:upper:]' '[:lower:]')"
U="$(printf '%s' "$RAW" | tr '[:lower:]' '[:upper:]')"
cd /home/ubuntu/DM-Concepts
PY="$HOME/.venvs/pretext/bin/python"
export PATH="$HOME/.venvs/pretext/bin:$PATH"
GIT() { git -c user.name="Duc A. Hoang" -c user.email="anhduchoang1990@googlemail.com" "$@"; }

FINAL="workflow/panels/chapter-${L}-final.json"
N=$("$PY" -c "import json;print(len(json.load(open('$FINAL'))['final_entries']))" 2>/dev/null || echo 0)

if [ "$N" -lt 1 ]; then
  echo "SKIP $U (no entries)"
  NEXT=$("$PY" workflow/scripts/loop-advance.py "$U" --skip)
  GIT add -A; GIT commit -q -m "Chapter $U skipped (no DM terms) [autonomous]" || true
  bash workflow/scripts/notify-telegram.sh "⏭️ Chương $U bỏ qua (không có thuật ngữ toán rời rạc). Tiếp theo: $NEXT." || true
  echo "NEXT=$NEXT"; exit 0
fi

"$PY" workflow/scripts/encode-chapter.py "$L"
"$PY" workflow/scripts/validate-entry.py > "/tmp/val-$L.log" 2>&1 || { echo "VALIDATE FAILED $U"; tail -25 "/tmp/val-$L.log"; exit 1; }
tail -1 "/tmp/val-$L.log"
"$PY" workflow/scripts/build-search-index.py >/dev/null
pretext build web > "/tmp/ptxbuild-$L.log" 2>&1 || { echo "BUILD FAILED $U"; tail -25 "/tmp/ptxbuild-$L.log"; exit 1; }

NEXT=$("$PY" workflow/scripts/loop-advance.py "$U")
GIT add -A
GIT commit -q -m "Chapter $U: $N verified entries [autonomous Phase 2]"
DONEN=$("$PY" -c "import json;s=json.load(open('workflow/loop/loop_state.json'));print(len(s['done']))" 2>/dev/null || echo '?')
bash workflow/scripts/notify-telegram.sh "✅ Chương $U xong: $N mục đã kiểm chứng (có trích dẫn + số trang). Đã xong $DONEN chữ. Tiếp theo: $NEXT. — Một số thuật ngữ trong Toán rời rạc" || true
echo "COMMITTED $U ($N entries). NEXT=$NEXT"
