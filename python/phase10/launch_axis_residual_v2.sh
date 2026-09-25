#!/bin/bash
# launch_axis_residual_v2.sh  2026-09-25  中村
# Intensity sweep + residual-axis test on the rebuilt axes, DISCOVERY set only.
#
# RAM rule (Nomura, 2026-09-25): the cgroup limit is 8 GiB and is SHARED with
# other projects (/path/to/work/caupsi_eaai/train.py is running and must never be
# stopped). Measure free RAM first and do not start if
#   expected RSS + current anon usage > 6 GiB
# (leaving 2 GiB of headroom). `anon` from memory.stat is the right figure:
# memory.current also counts reclaimable page cache.
#
# A watchdog kills ONLY THIS job if anon later climbs past 7.0 GiB, so that a
# growing neighbour is never the one that gets OOM-killed because of us.
set -euo pipefail
export CUDA_VISIBLE_DEVICES=0

VENV=/path/to/work/affectgeometry/venv/bin/python3
CODE=/path/to/work/code/phase10
OUT=/path/to/work/results/axis_residual_v2
LOG=/path/to/work/results/logs/axis_residual_v2_discovery.log
PREREG_COMMIT="${1:-}"

EXPECT=$((2 * 1024 * 1024 * 1024))   # ~2 GiB, measured from the earlier OOM dump
THRESH=$((6 * 1024 * 1024 * 1024))
WATCHDOG_MAX=$(( (7 * 1024 * 1024 * 1024) + (1024 * 1024 * 1024 / 2) ))  # 7.5 GiB

mkdir -p "$OUT" "$(dirname "$LOG")"

anon_now() { grep -E '^anon ' /sys/fs/cgroup/memory.stat | awk '{print $2}'; }

# serial rule: no other model job of ours
OTHER=$(pgrep -af "(run_intervention|run_pos_ctrl_v2|run_pos_ctrl_v3_newaxes|rebuild_axes_nopad|run_axis_residual|intervention_paper1_tokenprob)\.py" \
        | grep -vE "bash -c|pgrep|grep " | awk '{print $1}' || true)
if [ -n "$OTHER" ]; then
  echo "[launch] ABORT: our own model job already running (PIDs: $OTHER)" | tee -a "$LOG"
  exit 9
fi

A=$(anon_now)
TOTAL=$((A + EXPECT))
{
  echo "[launch] $(date -u) host=$(hostname) CVD=$CUDA_VISIBLE_DEVICES"
  # `bc` is not installed in this container; use awk for the human-readable line.
  # NOTE: the guard itself uses shell integer arithmetic below, never this line.
  awk -v a="$A" -v e="$EXPECT" -v t="$TOTAL" -v th="$THRESH" 'BEGIN{
    printf "[launch] anon now = %.2f GiB, expected = %.2f GiB, sum = %.2f GiB, threshold = %.2f GiB\n",
      a/1073741824, e/1073741824, t/1073741824, th/1073741824}'
  echo "[launch] neighbours (never stop these):"
  ps -eo pid,rss,args --sort=-rss | head -4
} >> "$LOG" 2>&1

if [ "$TOTAL" -gt "$THRESH" ]; then
  echo "[launch] ABORT: RAM rule -- would exceed 6 GiB. Not starting." | tee -a "$LOG"
  exit 10
fi

cd "$CODE"
"$VENV" run_axis_residual_v2.py \
  --model swiss-ai/Apertus-v1.1-1.5B \
  --layers 5 7 10 12 \
  --seed 42 \
  --prereg-commit "$PREREG_COMMIT" \
  --output-dir "$OUT" >> "$LOG" 2>&1 &
JOB=$!
echo "[launch] job pid=$JOB" >> "$LOG"

# watchdog: protect the neighbours by sacrificing OUR job if RAM gets tight
(
  while kill -0 "$JOB" 2>/dev/null; do
    A2=$(anon_now)
    if [ "$A2" -gt "$WATCHDOG_MAX" ]; then
      echo "[watchdog] anon=$A2 > $WATCHDOG_MAX; terminating OUR job $JOB only" \
        >> "$LOG"
      kill -TERM "$JOB" 2>/dev/null || true
      break
    fi
    sleep 20
  done
) &

wait "$JOB"
RC=$?
{
  echo "[launch] job exit=$RC"
  awk -v a="$(anon_now)" 'BEGIN{printf "[launch] anon after = %.2f GiB\n", a/1073741824}'
  echo "[launch] finished $(date -u)"
} >> "$LOG" 2>&1
exit $RC
