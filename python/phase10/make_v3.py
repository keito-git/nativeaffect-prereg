"""Derive run_pos_ctrl_v3_newaxes.py from v2 by parameterising the axis source.

v2 is left untouched so that the layer-5/7 output it produced keeps a matching
script_sha256 in its manifest.
"""
from pathlib import Path

SRC = Path("/path/to/scratch"
           "e3064739-5181-43fd-9b23-e940f47ad402/scratchpad/run_pos_ctrl_v2.py")
DST = SRC.with_name("run_pos_ctrl_v3_newaxes.py")

s = SRC.read_text()
subs = 0


def rep(old: str, new: str, count: int = 1) -> None:
    global s, subs
    assert s.count(old) >= 1, f"pattern not found: {old[:70]!r}"
    s = s.replace(old, new, count)
    subs += 1


# ---- header note -------------------------------------------------------
rep('"""Positive control, rebuilt: does the Warriner-valence direction move the',
    '"""Positive control on the REBUILT (PAD-free) ICA axes.\n\n'
    'v3 = v2 with the axis source parameterised (--ica-dir / --act-dir).  v2 is\n'
    'kept unchanged because its manifest sha256 belongs to the layer-5/7 output.\n'
    'Conditions (a) last-token pos, (b) mean-pool pos and (c) random do NOT depend\n'
    'on the ICA axes, so the v2 layer-5/7 findings for those conditions stand.\n'
    'Only condition (d) ortho_* and cos(pos, axis) depend on the axes, which is\n'
    'why this rerun exists: the old axes were estimated from PAD-position\n'
    'activations (right padding + index -1) and are invalid.\n\n'
    'Positive control, rebuilt: does the Warriner-valence direction move the')

# ---- load_axes_top5: take explicit dirs, pick K by silhouette ----------
rep('''def load_axes_top5(model_id: str, layer: int, seed: int,
                   n_axes: int) -> tuple[np.ndarray, list[float]]:
    """Top-`n_axes` ICA axes by split-half reproducibility.

    Identical code path to the main sweep (axis_selection=split_repro,
    top_k_axes=5): run_intervention.py:736-763.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_ica import compute_split_reproducibility, load_ica, model_slug

    data = load_ica(model_id, layer, seed)
    comps = np.array(data["components"], dtype=np.float32)   # (K, D)
    act_path = (ACT_DIR / model_slug(model_id)
                / f"layer{layer:02d}_seed{seed:04d}.npz")
    if not act_path.exists():
        raise FileNotFoundError(act_path)
    scores = compute_split_reproducibility(act_path, comps, seed=seed)
    order = np.argsort(-scores)
    comps = comps[order][:n_axes]
    return comps, [float(x) for x in scores[order][:n_axes]]''',
    '''def load_axes_top5(model_id: str, layer: int, seed: int, n_axes: int,
                   ica_dir: Path, act_dir: Path) -> tuple[
                       np.ndarray, list[float], str, int]:
    """Top-`n_axes` ICA axes by split-half reproducibility, from explicit dirs.

    Same selection rule as the main sweep (axis_selection=split_repro,
    top_k_axes=5, run_intervention.py:736-763) and the same K-by-silhouette
    choice as run_ica.load_ica, but reading whichever axis tree is passed in so
    the rebuilt PAD-free axes can be used.
    """
    import glob as _glob

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_ica import compute_split_reproducibility, model_slug

    slug = model_slug(model_id)
    pattern = str(ica_dir / slug / f"layer{layer:02d}_seed{seed:04d}_K*.json")
    files = sorted(_glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"no ICA file matching {pattern}")
    best: dict[str, Any] | None = None
    best_sil = -2.0
    best_fp = ""
    for fp in files:
        d = json.loads(Path(fp).read_text())
        sils = d.get("silhouettes") or [-1.0]
        s_ = max(sils)
        if s_ > best_sil:
            best_sil, best, best_fp = s_, d, fp
    assert best is not None
    comps = np.array(best["components"], dtype=np.float32)   # (K, D)
    act_path = act_dir / slug / f"layer{layer:02d}_seed{seed:04d}.npz"
    if not act_path.exists():
        raise FileNotFoundError(act_path)
    scores = compute_split_reproducibility(act_path, comps, seed=seed)
    order = np.argsort(-scores)
    if comps.shape[0] < n_axes:
        raise RuntimeError(
            f"layer {layer}: ICA gave K={comps.shape[0]} components but "
            f"{n_axes} control directions are required. Reduce --n-ctrl-dirs.")
    return (comps[order][:n_axes],
            [float(x) for x in scores[order][:n_axes]], best_fp, int(best["k"]))''')

# ---- call site ---------------------------------------------------------
rep('        axes, repro = load_axes_top5(args.model, layer, args.seed, K)',
    '        axes, repro, axis_file, axis_k = load_axes_top5(\n'
    '            args.model, layer, args.seed, K, args.ica_dir, args.act_dir)')

# ---- record provenance in the per-layer output -------------------------
rep('            "axis_split_repro_top5": repro,',
    '            "axis_split_repro_top5": repro,\n'
    '            "axis_source_file": axis_file,\n'
    '            "axis_ica_k": axis_k,\n'
    '            "axis_tree": str(args.ica_dir),\n'
    '            "activation_tree": str(args.act_dir),')

# ---- new CLI args ------------------------------------------------------
rep('    ap.add_argument("--output-dir", type=Path)',
    '    ap.add_argument("--output-dir", type=Path)\n'
    '    ap.add_argument("--ica-dir", type=Path,\n'
    '                    default=Path("/path/to/work/results/ica_nopad"),\n'
    '                    help="ICA axis tree (default: rebuilt PAD-free axes)")\n'
    '    ap.add_argument("--act-dir", type=Path,\n'
    '                    default=Path("/path/to/work/results/'
    'activations_nopad"),\n'
    '                    help="activation tree used for split-half repro")')

# ---- stamp the axis tree into the env manifest -------------------------
rep('''                "data_hash_stimuli": data_hash,
                "alphas_rel": args.alphas_rel,
                "n_ctrl_dirs": K,
                "rand_rng"''',
    '''                "data_hash_stimuli": data_hash,
                "axis_tree": str(args.ica_dir),
                "activation_tree": str(args.act_dir),
                "alphas_rel": args.alphas_rel,
                "n_ctrl_dirs": K,
                "rand_rng"''', count=2)

DST.write_text(s)
print(f"wrote {DST}  ({subs} substitutions, {len(s.splitlines())} lines)")
import ast
ast.parse(s)
print("AST OK")
