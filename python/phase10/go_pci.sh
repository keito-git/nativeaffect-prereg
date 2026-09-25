#!/bin/bash
# Launch the positive-control in-plane retest once.
#
# Guards use a PID FILE, not pattern matching. Reason, recorded because it cost
# several wasted cycles: an ssh one-liner's own command line contains the script
# name (in heredocs, in log paths), and pgrep scans every process including that
# shell, so "is it already running?" matched the checking command itself and
# aborted. The same hazard made an earlier `pkill -f` kill my own ssh session.
# A pidfile has no pattern to collide with.
#
# The paper-1 check can stay as a pattern because this script's own command line
# is just its path, and the caller is told never to echo that pattern.
set -u
PIDF=/path/to/work/results/logs/pos_ctrl_inplane.pid
S=/path/to/work/results/logs/pos_ctrl_inplane.log
G=/path/to/work/results/logs/go_pci.log
PREREG=${1:-}

log() { echo "[go] $(date -u) $*" >> "$G"; }

n_p1=$(pgrep -c -f "[i]ntervention_paper1_tokenprob" || true)
anon=$(grep -E '^anon ' /sys/fs/cgroup/memory.stat | awk '{print $2}')
log "paper1=$n_p1 anon=$anon prereg=$PREREG"

if [ "${n_p1:-0}" != "0" ]; then
  log "ABORT paper1 running"; echo "ABORT paper1"; exit 0
fi
if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then
  log "ABORT already running pid=$(cat "$PIDF")"; echo "ABORT already running"; exit 0
fi
if [ "${anon:-0}" -gt 6442450944 ]; then
  log "ABORT anon over 6GiB"; echo "ABORT ram"; exit 0
fi

cd /path/to/work/code/phase10 || exit 1
CUDA_VISIBLE_DEVICES=0 setsid nohup /path/to/work/affectgeometry/venv/bin/python3 \
  ./pos_ctrl_inplane.py --prereg-commit "$PREREG" > "$S" 2>&1 < /dev/null &
echo $! > "$PIDF"
log "launched pid=$(cat "$PIDF")"
echo "LAUNCHED pid=$(cat "$PIDF")"
