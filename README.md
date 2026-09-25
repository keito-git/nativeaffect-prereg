# NativeAffect (paper 2) — pre-registrations and analysis code

Timestamping repository for the NativeAffect project (AI-native emotion axes).
It holds the pre-registration documents and the code that implements them.
**Results JSON and activation caches are deliberately not tracked** (size); they
live on the GPU server under `/path/to/work/results/` and are mirrored into
the project tree under `03_解析/`.

Each results file records `env.prereg_commit` (a commit of this repo) and
`env.script_sha256`, so any number in the paper can be traced to the exact
pre-registration text and the exact script that produced it.

## Layout

- `03_解析/preregistration/` — pre-registrations, including dated amendments and
  invalidation notes. Nothing here is ever deleted or silently rewritten; a
  superseded registration keeps its text and gains an invalidation section.
- `python/phase10/` — extraction, ICA rebuild, intervention and positive-control
  code, plus the self-checks.

## Status (2026-09-25)

- The original ICA axes were estimated from PAD-position activations
  (`padding=True`, `padding_side="right"`, `batch_size=8`, then `hs[:, -1, :]`);
  258/300 stimuli were affected. Those axes and every result derived from them
  are marked INVALID and were rebuilt from `batch_size=1`, unpadded activations.
- The judge-free positive control (next-token JS divergence) passes at layers
  5/7/10/12 on the rebuilt axes when the valence direction is regressed from
  last-token activations; the older mean-pooled direction passes only at layer 12.
- No judge LLM is used anywhere in these measurements (PI directive: judges
  trained on human emotion frameworks make the argument circular).
