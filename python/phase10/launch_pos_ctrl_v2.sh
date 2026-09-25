#!/bin/bash
# launch_pos_ctrl_v2.sh  2026-09-25  中村
# Positive-control rebuild only. No axis sweep, no judge LLM.
# GPU: 0 only (PI rule). PID 212648 (axis-2 intensity sweep) must NOT be touched.
set -euo pipefail
export CUDA_VISIBLE_DEVICES=0

VENV=/path/to/work/affectgeometry/venv/bin/python3
CODE=/path/to/work/code/phase10
STIMULI=/path/to/work/code/stimuli/stimuli_e4.json
OUT=/path/to/work/results/pos_ctrl_v2
LOG=/path/to/work/results/logs/pos_ctrl_v2.log

mkdir -p "$OUT" "$(dirname "$LOG")"

{
  echo "[launch] $(date -u) host=$(hostname) CVD=$CUDA_VISIBLE_DEVICES"
  echo "[launch] nvidia-smi BEFORE:"
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv
  nvidia-smi --query-gpu=index,uuid,memory.used --format=csv,noheader
} >> "$LOG" 2>&1

cd "$CODE"
"$VENV" run_pos_ctrl_v2.py \
  --model swiss-ai/Apertus-v1.1-1.5B \
  --layers 5 7 10 12 \
  --seed 42 \
  --alphas-rel 0.01 0.05 \
  --n-stim 40 \
  --n-pos-fit 30 \
  --stimuli "$STIMULI" \
  --output-dir "$OUT" >> "$LOG" 2>&1

{
  echo "[launch] nvidia-smi AFTER:"
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv
  echo "[launch] finished $(date -u)"
} >> "$LOG" 2>&1
