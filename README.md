# NativeAffect — pre-registration, amendments and code

This repository is the time-stamping record for a study on activation steering of emotion in
large language models. Its purpose is narrow and specific: **every criterion, statistic and pass
condition was committed and pushed before the judgement it governs was executed.** The commit
dates are the evidence; the text is the claim.

## Layout

| Directory | Contents |
|---|---|
| `preregistration/` | the base pre-registration documents and the fixed data splits |
| `amendments/` | the amendments, 106 files, **as registered** |
| `amendments_en/` | faithful English translations of the amendments |
| `release/` | the code that produces every measurement and every number in the paper |
| `code/`, `python/` | earlier implementation, kept for the record |
| `stimuli/`, `stimuli_e5/` | stimulus specifications |
| `manuscript_figures/` | figures and tables of an earlier manuscript |
| `draft_ja/` | an early Japanese draft, superseded |

## On the two amendment directories

**`amendments/` holds the originals.** They are in Japanese because that is the language in which
they were written and committed; the commit that carries each file is what establishes when its
criteria were fixed. They are not edited.

**`amendments_en/` holds translations added on 2026-10-15**, after the fact, so that readers can
follow the record. A translation is not the registered text. Where the two differ, the Japanese
file is authoritative. The translations were checked against the originals for heading structure,
for the set of numbers they contain, and for the preservation of every commitment and every
admission of error; two defects found in that check were corrected.

Personal and team names were replaced by roles in the translations. Cited authors are unchanged.

## Numbering

Amendments run from 1 to 108 with 30 and 31 unused. Each file names, at its head, what it governs
and whether it had been executed at the time of writing. Several record failures: measurements that
could not be judged, a control that failed its own validity check, a threshold set after seeing
degenerate values, and a half of a sweep lost to a filename collision. These are part of the record
and are not removed.

## Code

See `release/README.md`. The measurement scripts need a GPU; the analysis scripts recompute every
reported number from the stored archives and do not. No number in the paper is entered by hand.
