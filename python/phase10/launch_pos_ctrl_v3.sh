#!/bin/bash
# launch_pos_ctrl_v3.sh  2026-09-25
# Positive control on the REBUILT (PAD-free) ICA axes. All 4 layers.
# GPU: 0 only. RUN ALONE: the container RAM limit is 8 GiB (memory.max), and
# running a second model-loading process caused an OOM kill at 10:54 UTC.
set -euo pipefail
export CUDA_VISIBLE_DEVICES=0

VENV=/path/to/work/affectgeometry/venv/bin/python3
CODE=/path/to/work/code/phase10
STIMULI=/path/to/work/code/stimuli/stimuli_e4.json
OUT=/path/to/work/results/pos_ctrl_v3_newaxes
LOG=/path/to/work/results/logs/pos_ctrl_v3_newaxes.log

mkdir -p "$OUT" "$(dirname "$LOG")"

# Refuse to start if another of OUR model-loading jobs is alive (RAM guard).
# Match only real python invocations: `pgrep -f` also matches shell waiter loops
# whose command line merely mentions the script name, which is a false positive.
OTHER=$(pgrep -af "(run_intervention|run_pos_ctrl_v2|run_pos_ctrl_v3_newaxes|rebuild_axes_nopad)\.py" \
        | grep -vE "bash -c|pgrep|grep " | awk '{print $1}' | grep -v "^$$\$" || true)
if [ -n "$OTHER" ]; then
  echo "[launch] ABORT: another model job is running (PIDs: $OTHER). Run serially." \
    | tee -a "$LOG"
  exit 9
fi

# Shared-RAM check: this container's cgroup limit is 8 GiB and other projects
# run here too. Report the biggest anon consumers so the log shows what we
# shared the box with, but do not touch anyone else's process.
{
  echo "[launch] top RSS consumers before start:"
  ps -eo pid,rss,etime,args --sort=-rss | head -6
} >> "$LOG" 2>&1

{
  echo "[launch] $(date -u) host=$(hostname) CVD=$CUDA_VISIBLE_DEVICES"
  echo "[launch] cgroup memory.max = $(cat /sys/fs/cgroup/memory.max 2>/dev/null)"
  echo "[launch] memory.current    = $(cat /sys/fs/cgroup/memory.current 2>/dev/null)"
  nvidia-smi --query-gpu=index,uuid,memory.used --format=csv,noheader
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv
} >> "$LOG" 2>&1

cd "$CODE"
"$VENV" run_pos_ctrl_v3_newaxes.py \
  --model swiss-ai/Apertus-v1.1-1.5B \
  --layers 5 7 10 12 \
  --seed 42 \
  --alphas-rel 0.01 0.05 \
  --n-stim 40 \
  --n-pos-fit 30 \
  --stimuli "$STIMULI" \
  --ica-dir /path/to/work/results/ica_nopad \
  --act-dir /path/to/work/results/activations_nopad \
  --output-dir "$OUT" >> "$LOG" 2>&1

{
  echo "[launch] nvidia-smi AFTER:"
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv
  echo "[launch] finished $(date -u)"
} >> "$LOG" 2>&1
