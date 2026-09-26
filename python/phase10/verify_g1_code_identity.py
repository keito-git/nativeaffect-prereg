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

# sha256 of python/phase10/g1_jacobian.py as it produced layer11.json and
# layer16.json (prereg_commit stamp 1078240, repository commit cee5b24).
EXPECTED = "febe19716e043cee84c036e2d75eadab176ce8e12fed7c54923b2ff7858911c9"
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
    if got != EXPECTED:
        print("\nREFUSING: this is not the file that produced layers 11 and 16.\n"
              "Recomputing layers 22 and 27 with it would leave the four layers\n"
              "without a shared condition. Restore the file from commit cee5b24,\n"
              "or recompute all four layers with the new file - not two and two.")
        return 1
    print("\nOK: byte-identical to the file that produced layers 11 and 16.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
