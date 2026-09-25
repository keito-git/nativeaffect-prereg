"""Record the axis-2 intensity sweep's partial state as INVALID.

The sweep wrote no result JSON: run_intervention.py writes its output once, at
the end, and the process died at 720/1200 records. Its only surviving record is
the log, so the INVALID note is written as a sidecar next to it. Nothing is
deleted.
"""
import json
from pathlib import Path

LOG_DIR = Path("/path/to/work/results/logs")
OUT = LOG_DIR / "axis2_intensity_sweep_INVALID.json"

note = {
    "INVALID": {
        "marked_by": "中村 (experiment, team Nomura)",
        "marked_utc": "2026-09-25",
        "verdict": ("INVALID: this sweep intervened along ICA axes estimated from "
                    "PAD-position activations. Its results are not interpretable "
                    "and are not to be cited."),
        "run": {
            "script": "code/phase10/run_axis2_intensity_sweep.sh",
            "command": ("run_intervention.py --model swiss-ai/Apertus-v1.1-1.5B "
                        "--layer 5 --seed 42 --alphas 0.01 0.03 0.05 0.10 0.20 "
                        "--stimuli stimuli_e4.json --stimuli-indices 0..39 "
                        "--n-generate 40 --top-k-axes 3 "
                        "--axis-selection split_repro"),
            "pid": 212648,
            "started_utc": "2026-09-25T06:58 (approx, from process start time)",
            "progress_at_death": "720 / 1200 records",
            "result_json_written": False,
            "surviving_records": [
                "results/logs/axis2_intensity_sweep_L5_s42.log",
                "results/logs/axis2_sweep_nohup_rerun.out"],
        },
        "why_it_stopped": {
            "cause": "OOM-killed, NOT a clean finish and NOT a deliberate stop",
            "detail": (
                "At 2026-09-25 ~10:54 UTC the container exceeded its cgroup RAM "
                "limit (memory.max = 8589934592 B = 8 GiB) because 中村 started "
                "rebuild_axes_nopad.py while this sweep and run_pos_ctrl_v2.py "
                "were already running. The kernel OOM killer terminated this "
                "process (\"212648 Killed\" in the launcher log) and also "
                "run_pos_ctrl_v2.py at its layer 10. Reported to the coordinator; "
                "model-loading jobs are now run strictly one at a time."),
            "responsibility": ("中村 launched the third process without checking "
                               "the RAM budget."),
        },
        "note_on_scheduling": (
            "The coordinator subsequently directed that this sweep be stopped "
            "anyway, since results on the old axes are uninterpretable. The "
            "process was already dead from the OOM by the time that instruction "
            "arrived, so no kill was issued by 中村."),
        "superseded_by": ("a rerun on the rebuilt PAD-free axes "
                          "(results/ica_nopad/), to be pre-registered before it "
                          "is launched"),
        "retained_because": "Lab rule: invalid output is never deleted.",
    }
}
OUT.write_text(json.dumps(note, indent=2, ensure_ascii=False))
print(f"wrote {OUT}")
for p in ("axis2_intensity_sweep_L5_s42.log", "axis2_sweep_nohup_rerun.out"):
    f = LOG_DIR / p
    print(f"  {p}: exists={f.exists()} size={f.stat().st_size if f.exists() else 0}")
