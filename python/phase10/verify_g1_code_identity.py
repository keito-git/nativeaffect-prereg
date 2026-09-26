#!/usr/bin/env python3
"""Refuse a G1 re-run unless the code is byte-identical to what produced 11 and 16.

Layers 11 and 16 were computed by one exact file. If layers 22 and 27 are later
recomputed from a different file -- even a file changed only to add a diagnostic
-- the four layers no longer share a condition, and a per-layer comparison across
them is not a comparison of layers. That is the failure mode of reporting a
conditioned result as an unconditioned one.

So the hash is recorded here rather than remembered, and this script is the gate.

    python3 verify_g1_code_identity.py <path to g1_jacobian.py>

Exit 0 only if the file matches. Anything else is a refusal.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# sha256 of /path/to/work/code/phase10/g1_jacobian.py on the server, which
# is the file that produced all four layers. Established from the outputs, not
# from mtime: all four layer JSONs carry pca_and_direction_rows, split_file and
# split_group, and ONLY this version writes those three fields. The server holds
# exactly one copy of the file, and its mtime (2026-09-26 11:07:31Z) precedes
# layer 11 (11:30:26Z) and is unchanged through layer 27 (12:19:31Z).
EXPECTED = "e2df51deacef345fc3b5ad153e2b52f278cc4c96639a21a74ddc92b66478e816"

# The value recorded here first, febe1971..., was WRONG. It was the hash of the
# stale local copy, taken from before the addendum-13 split edits were made on
# the server, and it was never checked against the machine that ran the job.
# Recording a provenance claim from the convenient copy is the error this file
# exists to prevent, so the wrong value is kept visible rather than deleted.
SUPERSEDED_WRONG_VALUE = "febe19716e043cee84c036e2d75eadab176ce8e12fed7c54923b2ff7858911c9"
FIELDS_ONLY_THIS_VERSION_WRITES = ("pca_and_direction_rows", "split_file",
                                   "split_group")
PRODUCED = ("layer11.json sha256 e894e7cfa2dc094876f4f295f9a7b57a9d3a519101f2852"
            "ea129824e415c69cd; layer16.json sha256 1f787b95f220f9d5...")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    p = Path(argv[1])
    if not p.exists():
        print(f"REFUSING: {p} does not exist")
        return 1
    got = sha256(p)
    print(f"expected {EXPECTED}\ngot      {got}")
    if got == SUPERSEDED_WRONG_VALUE:
        print("\nREFUSING: this is the stale pre-addendum-13 copy. It does not draw\n"
              "the discovery half and does not write split_file or split_group, so\n"
              "it is not the file that produced any of the four layers.")
        return 1
    if got != EXPECTED:
        print("\nREFUSING: this is not the file that produced the four layers.\n"
              "Recomputing some layers with it would leave them without a shared\n"
              "condition while still looking like four layers of one run. Either\n"
              "restore the file, or recompute ALL FOUR layers - not two and two.")
        return 1
    print("\nOK: byte-identical to the file that produced all four layers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
