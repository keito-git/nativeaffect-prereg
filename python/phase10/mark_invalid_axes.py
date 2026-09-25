"""Add an INVALID field to every artefact derived from PAD-position activations.

Nothing is deleted or moved. Each JSON gets a backup (.orig_backup) the first
time it is touched, and only a new top-level "INVALID" key is inserted. The .npz
activation caches cannot carry a JSON field, so a sidecar INVALID_README.json is
written next to them instead.
"""
import json
import shutil
from pathlib import Path

BASE = Path("/path/to/work/results")
SLUG = "swiss-ai__Apertus-v1_1-1_5B"
LAYERS = (5, 7, 10, 12)

REASON = {
    "marked_by": "中村 (experiment, team Nomura)",
    "marked_utc": "2026-09-25",
    "verdict": ("INVALID: the ICA axes behind this artefact were estimated from "
                "PAD-position activations. Do not cite or interpret. Retained as "
                "a record of the old axes' behaviour only."),
    "root_cause": (
        "extract_activations.py tokenises with padding=True at batch_size=8 "
        "(launch_extract.sh:12) and then reads hs[:, -1, :] "
        "(extract_activations.py:77). The Apertus tokeniser pads on the RIGHT "
        "(padding_side='right'), and the E1 stimuli are 4-47 tokens long, so for "
        "any stimulus that is not the longest in its batch index -1 is a PAD "
        "position, not the final content token. A stimulus's stored vector "
        "therefore also depends on which other stimuli shared its batch."),
    "evidence": {
        "stimuli_reading_PAD": "258 / 300 (86.0%) of E1 stimuli",
        "pad_offset_mean": 12.59,
        "pad_offset_max": 40,
        "token_len_range": "4-47",
        "diagnosis_confirmed": (
            "The buggy code path was re-run in-process and compared row-by-row "
            "with the archived .npz: cosine = 1.0000 at all four layers, i.e. the "
            "archived activations are exactly what the buggy path produces."),
        "activation_cos_correct_vs_buggy": {
            "layer5": 0.5631, "layer7": 0.5701,
            "layer10": 0.6546, "layer12": 0.7559},
        "axis_matched_abs_cos_top5_old_vs_new": {
            "layer5": {"mean": 0.1330, "min": 0.0105, "old_K": 20, "new_K": 6},
            "layer7": {"mean": 0.1450, "min": 0.0025, "old_K": 10, "new_K": 8},
            "layer10": {"mean": 0.1785, "min": 0.0331, "old_K": 18, "new_K": 5},
            "layer12": {"mean": 0.3159, "min": 0.0246, "old_K": 14, "new_K": 19}},
        "chance_level_abs_cos_2048d": 0.0176,
    },
    "superseded_by": {
        "activations": "results/activations_nopad/ (batch_size=1, no padding)",
        "ica_axes": "results/ica_nopad/",
        "damage_report": ("results/axes_nopad/"
                          "axis_damage_report_20260925T110342Z.json"),
        "code": "code/phase10/rebuild_axes_nopad.py",
    },
    "retained_because": "Lab rule: invalid output is never deleted.",
}

targets: list[Path] = []
for L in LAYERS:
    targets += sorted((BASE / "ica" / SLUG).glob(f"layer{L:02d}_seed0042_K*.json"))
for sub in ("c1/" + SLUG, "_archive_c1_before_axis2_20260925_065809",
            "c1_archive_main_sweep_20260925_053514", "axis_stability/" + SLUG,
            "axis_stability", "response_inverse"):
    d = BASE / sub
    if d.is_dir():
        targets += sorted(p for p in d.glob("*.json") if p.is_file())

seen = set()
for p in targets:
    if p in seen:
        continue
    seen.add(p)
    bak = p.with_suffix(".json.orig_backup")
    try:
        obj = json.loads(p.read_text())
    except Exception as exc:  # noqa: BLE001
        print(f"SKIP (unparseable) {p}: {exc}")
        continue
    if not isinstance(obj, dict):
        print(f"SKIP (not an object) {p}")
        continue
    if "INVALID" in obj:
        print(f"already marked: {p}")
        continue
    if not bak.exists():
        shutil.copy2(p, bak)
    new = {"INVALID": REASON}
    new.update(obj)
    p.write_text(json.dumps(new, indent=2, ensure_ascii=False))
    print(f"marked: {p}")

# sidecar for the .npz caches, which cannot hold a JSON field
side = BASE / "activations" / SLUG / "INVALID_README.json"
side.write_text(json.dumps(
    {"INVALID": REASON,
     "applies_to": [f"layer{L:02d}_seed0042.npz" for L in LAYERS]
                   + ["seed0042_manifest.json"],
     "note": ("These .npz caches hold PAD-position activations. They are kept "
              "unmodified; use results/activations_nopad/ instead.")},
    indent=2, ensure_ascii=False))
print(f"sidecar written: {side}")
print(f"\ntotal JSON files marked: {len(seen)}")
