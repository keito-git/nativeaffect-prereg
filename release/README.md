# Code for "Emotion Steering Is Specific to the Human Emotion Partition yet Remains Bound to Its Output Encoding"

This directory holds the code that produces every measurement and every number in the paper and
its supplementary material. The pre-registration and its amendments live in the parent repository;
each amendment was committed before the judgement it governs was executed.

## Layout

```
code/        measurement: one script per gate and per validity check (needs a GPU)
analysis/    statistics and tables: recomputes every reported number (no GPU)
figures/     the figures of the paper (no GPU)
```

The split is deliberate. The measurement scripts write one archive per model holding every
measured profile, by family, readout and floor; the analysis scripts read those archives and
recompute the statistics. A correction to a statistic therefore never requires a GPU, and no
number in the paper is typed by hand.

## Data

The stimuli are crowd-enVENT (Troiano, Oberländer and Klinger, *Computational Linguistics* 49(1),
2023), obtained from the authors' distribution. Place the corpus so that

```
$NA_ROOT/data/raw/crowd_envent/corpus/crowd-enVent_generation.tsv
```

exists, and set `NA_ROOT` to the directory you want the scripts to read and write
(it defaults to `work/` beside this README). The models are the published instruction-tuned
checkpoints named in the paper, loaded from their public identifiers.

## Measurement

Each script takes `--model` and `--tag`; `--budget` sets the Jensen-Shannon budget and defaults to
the value used in the paper.

| Script | What it measures |
|---|---|
| `extract_activations.py`, `audit_stageA.py` | hidden states at the chosen layer |
| `intervene_core.py` | the forward hook and the bisection that equalises the intervention |
| `stageC3.py` | Gate I, the variance-matched floor, readout A |
| `stageC3app.py` | Gate I, readout B |
| `stageSC2.py` | Gate III, the output encoding, with the same-context and gradient controls |
| `stageLP.py` | Gate II, random partitions of the same grain |
| `stageSPact.py` | Gate II, activation-clustered partitions at least as decodable as the emotion partition |
| `stageL2.py` | the subspace level |
| `actcheck.py`, `appcheck.py`, `emocheck.py`, `cecheck.py`, `roauc.py` | readout validity checks |
| `vmatch_holdout.py` | the floor's variance matching against a held-out covariance |

`stageSPact.py` separates search from measurement. `--search-only` finds comparison partitions
using activations and probes alone, with no forward pass, so the search parallelises across cores;
`--shard N` gives a worker an independent proposal stream without moving the data split;
`--labels FILE` measures the partitions a search produced.

## Analysis

`final_tables.py`, `scjudge.py`, `cestats.py`, `encoding_vocabulary.py`, `category_wise.py` and
`budget_sweep.py` read the stored archives and print the tables of the paper. None of them needs a
GPU. `NA_DATA` points them at the archives.

## Reproducing a gate

```
export NA_ROOT=/path/to/work
python code/stageC3.py --model <hf-id> --tag <model>_L<layer>      # measure
python analysis/final_tables.py                                     # tabulate
```

## Note on the activation caches

The caches for some additional measurements were rebuilt after the originals were lost. Those
measurements are kept internally self-contained and are not joined to the main tables; the paper
states where this applies.
