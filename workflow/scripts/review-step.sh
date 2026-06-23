#!/usr/bin/env bash
# Apply finished batch <i>, advance the ledger, and prepare batch <i+1>.
# Prints NEXT=<i+1> (or ALL_BATCHES_DONE). Usage: review-step.sh <i>
set -uo pipefail
i="${1:?usage: review-step.sh <batch-number>}"
cd /home/ubuntu/DM-Concepts
PY="$HOME/.venvs/pretext/bin/python"
R=workflow/loop/review
TOTAL=$("$PY" -c "import glob;print(len(glob.glob('$R/batch-*.json')))")

if [ -f "$R/findings-$i.json" ]; then
  "$PY" workflow/scripts/apply-review.py "$i"
else
  echo "WARN: no findings-$i.json"; tail -2 "$R/codex-out-$i.txt" 2>/dev/null
fi
next=$((i+1))
"$PY" -c "import json;p='$R/loop_state.json';s=json.load(open(p));s['done_loops']=sorted(set(s.get('done_loops',[])+[$i]));s['current']=$next;json.dump(s,open(p,'w'),ensure_ascii=False,indent=1)"
if [ "$next" -le "$TOTAL" ]; then
  bash workflow/scripts/codex-review-prompt.sh "$next" > "/tmp/rp$next.txt"
  rm -f "$R/findings-$next.json" "$R/codex-out-$next.txt"
  echo "NEXT=$next ready (of $TOTAL)"
else
  echo "ALL_BATCHES_DONE ($TOTAL batches)"
fi
