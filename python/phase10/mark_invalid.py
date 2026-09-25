"""Record an INVALID field on the previous positive-control output.

Nothing is deleted. A byte-for-byte backup is written first, and only a new
top-level "INVALID" key is added to the JSON.
"""
import json
import shutil
from pathlib import Path

TARGET = Path("/path/to/work/results/pos_ctrl/"
              "pos_ctrl_pooling_20260925T070936Z.json")
BACKUP = TARGET.with_suffix(".json.orig_backup")

REASON = {
    "marked_by": "中村 (experiment, team Nomura)",
    "marked_utc": "2026-09-25",
    "verdict": "INVALID as a positive control. Do not cite these numbers.",
    "reasons": [
        {
            "id": "D2_silent_fit_set_collapse",
            "severity": "fatal",
            "detail": (
                "stimulus_valence() in run_pos_ctrl_pooling_check.py looks Warriner "
                "words up with re.findall(r\"[a-z']+\") and no suffix stripping. The "
                "VAD file /path/to/work/affectgeometry/data/vad_norms/warriner_2013_en_vad.csv "
                "holds only 2298 words, so 'joyful', 'elated', 'excited', 'hopeless', "
                "'contemptuous', 'assistant', 'situation', 'feels' all miss. "
                "valence_direction() skips a stimulus whose valence is None WITHOUT "
                "warning, so the regression fit set silently collapsed from 30 to 8 "
                "stimuli (first30) and from 40 to 10 (all40). Measured composition: "
                "first30 -> n=8 (6 positive, 2 negative); all40 -> n=10 (6 positive, "
                "4 negative). All three 'pos' directions in this file are therefore "
                "regressions on 8-10 stimuli, not on the intended 30/40."),
        },
        {
            "id": "D2b_pooling_contrast_confounded",
            "severity": "fatal",
            "detail": (
                "Because of D2, 'pos_meanpool_first30' in this file does NOT reproduce "
                "the main sweep's positive control. run_intervention.py uses a "
                "suffix-stripping lookup (run_intervention.py:418-446) giving n_fit=30. "
                "This file's meanpool variant used n_fit=8. The intended comparison "
                "(last-token vs mean-pool pooling, everything else held equal) is thus "
                "confounded by a different fit set, so the pooling question this file "
                "was written to answer is not answered by it."),
        },
        {
            "id": "D2c_pass_verdict_uninformative",
            "severity": "fatal",
            "detail": (
                "Every layer and every variant is reported as main=True/secondary=True. "
                "A direction fitted to 8-10 real activation vectors lies inside the "
                "high-variance data subspace regardless of its regression target, so it "
                "beats an isotropic random direction almost by construction. The "
                "all-pass verdict therefore does not establish that the HUMAN VALENCE "
                "direction specifically is recovered."),
        },
    ],
    "non_fatal_notes": [
        "env.gpu_uuid_visible lists both physical GPU uuids because nvidia-smi "
        "ignores CUDA_VISIBLE_DEVICES; only index 0 was actually visible to the run.",
        "env.git_commit is empty: /path/to/work is not a git repository.",
        "Condition (d), a direction orthogonal to the ICA axis, was not implemented "
        "in this script at all.",
    ],
    "superseded_by": (
        "/path/to/work/code/phase10/run_pos_ctrl_v2.py -> "
        "/path/to/work/results/pos_ctrl_v2/pos_ctrl_v2_*.json"),
    "retained_because": (
        "Lab rule: invalid output is never deleted. Kept for audit; the raw JS "
        "values remain on disk and the backup .json.orig_backup is byte-identical "
        "to the file as produced."),
}

if not BACKUP.exists():
    shutil.copy2(TARGET, BACKUP)
    print(f"backup written -> {BACKUP}")
else:
    print(f"backup already exists -> {BACKUP}")

obj = json.loads(TARGET.read_text())
if "INVALID" in obj:
    print("INVALID field already present; leaving as is.")
else:
    new = {"INVALID": REASON}
    new.update(obj)
    TARGET.write_text(json.dumps(new, indent=2, ensure_ascii=False))
    print(f"INVALID field added -> {TARGET}")

chk = json.loads(TARGET.read_text())
print("layers still present:", [L["layer"] for L in chk["layers"]])
print("INVALID.verdict:", chk["INVALID"]["verdict"])
