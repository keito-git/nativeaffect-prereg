#!/bin/bash
# C1/C2 seed stability: run the pos/floor comparison once per floor seed (prereg 37.2).
# Guarded by a pidfile (never by pattern matching - see prereg 33).
PIDF=/path/to/work/results/logs/go_seeds.pid
G=/path/to/work/results/logs/go_seeds.log
if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then
  echo "ABORT already running"; exit 0
fi
if [ "$(pgrep -c -f "[i]ntervention_paper1_tokenprob" || true)" != "0" ]; then
  echo "ABORT paper1"; exit 0
fi
echo $$ > "$PIDF"
cd /path/to/work/code/phase10 || exit 1
for S in 42 43 44 45 46; do
  echo "[seeds] $(date -u) floor-seed $S start" >> "$G"
  CUDA_VISIBLE_DEVICES=0 /path/to/work/affectgeometry/venv/bin/python3 ./pos_ctrl_inplane.py \
    --floor-seed "$S" --prereg-commit 6d1370f7582f3a1758c53b898fbac744a89f6095 \
    --out-dir /path/to/work/results/pos_ctrl_inplane_seeds \
    >> /path/to/work/results/logs/pos_ctrl_inplane_seeds.log 2>&1
  echo "[seeds] $(date -u) floor-seed $S exit=$?" >> "$G"
done
echo "[seeds] ALL DONE $(date -u)" >> "$G"
rm -f "$PIDF"
