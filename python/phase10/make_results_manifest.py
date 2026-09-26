#!/usr/bin/env python3
"""Record the identity of every result file in a tracked manifest.

Why this exists
---------------
Result JSONs are not tracked by git: `.gitignore` excludes `03_解析/**/*.json`
apart from `03_解析/preregistration/*.json`, because activations and sweeps are
too large for the pre-registration repository. That left the results with no
timestamp of any kind, so a later edit to a result file would be invisible.

This script writes a manifest that IS tracked: for every result file it records
the relative path, the sha256 of the bytes, the byte count, and the
`generated_utc` field the producing script wrote inside the JSON. Committing the
manifest fixes the content of the results as of that commit. It does not prove
when a result was produced -- only that the bytes have not changed since the
commit that recorded them.

Append-only by design
---------------------
Entries are keyed by (path, sha256), not by path. If a path reappears with
different bytes, the new entry is appended and the older one is marked
`superseded: true`; nothing is ever dropped. A manifest that silently replaced
the old hash would let a rewrite pass unnoticed, which is the failure this
script exists to prevent.

Usage
-----
    python3 make_results_manifest.py                 # update the manifest
    python3 make_results_manifest.py --check         # verify, write nothing
    python3 make_results_manifest.py --self-test     # run the checks only

Exit status is non-zero if --check finds a recorded file whose bytes changed or
which has disappeared.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT = Path("/path/to/research/論文/NativeAffect_AI固有の感情軸")
REPO = Path.home() / "git" / "nativeaffect-prereg"
MANIFEST_REL = Path("03_解析/preregistration/results_manifest_20260926.json")
SCAN_ROOT_REL = Path("03_解析")

# Keys that producing scripts have used for their own generation timestamp.
# Order matters: the first present key wins, so the most specific comes first.
TIME_KEYS = ("generated_utc", "generated_at_utc", "generated", "timestamp_utc",
             "created_utc", "run_utc", "utc")


def sha256_and_size(path: Path) -> tuple[str, int]:
    """Hash a file in chunks and return (hex digest, byte count)."""
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


def read_generated_utc(path: Path) -> tuple[str | None, str]:
    """Return (timestamp, source) read from inside the JSON, never from mtime.

    mtime is deliberately not used as a fallback: a file's mtime says nothing
    about when its contents were computed and is trivially rewritten, so
    recording it would dress up an unverifiable claim as a measurement.
    """
    try:
        doc = json.loads(path.read_text())
    except Exception as exc:                       # noqa: BLE001 - report, don't crash
        return None, f"unreadable: {type(exc).__name__}"
    if not isinstance(doc, dict):
        return None, "json root is not an object"
    for key in TIME_KEYS:
        val = doc.get(key)
        if isinstance(val, str) and val:
            return val, f"JSON field '{key}'"
    # A few scripts nest it under an environment/manifest block.
    for outer in ("env_log", "env", "manifest", "meta", "provenance"):
        blk = doc.get(outer)
        if isinstance(blk, dict):
            for key in TIME_KEYS:
                val = blk.get(key)
                if isinstance(val, str) and val:
                    return val, f"JSON field '{outer}.{key}'"
    return None, "absent from the JSON"


def read_flags(path: Path) -> dict[str, Any]:
    """Pick up self-declared status fields so the manifest does not imply validity."""
    out: dict[str, Any] = {}
    try:
        doc = json.loads(path.read_text())
    except Exception:                              # noqa: BLE001
        return out
    if not isinstance(doc, dict):
        return out
    if "INVALID" in doc:
        out["INVALID"] = doc["INVALID"]
    for key in ("canonical_location", "computed_before_G1",
                "computed_before_any_G4_measurement"):
        if key in doc:
            out[key] = doc[key]
    return out


def tracked_paths(repo: Path) -> set[str]:
    """Paths git actually tracks, asked of git rather than inferred from .gitignore."""
    try:
        res = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                             capture_output=True, check=True)
    except Exception:                              # noqa: BLE001
        return set()
    return {p for p in res.stdout.decode().split("\0") if p}


def scan(project: Path, repo: Path) -> list[dict[str, Any]]:
    """Build one entry per result JSON found under the scan root."""
    tracked = tracked_paths(repo)
    entries: list[dict[str, Any]] = []
    for path in sorted((project / SCAN_ROOT_REL).rglob("*.json")):
        rel = path.relative_to(project).as_posix()
        if rel == MANIFEST_REL.as_posix():
            continue                               # never hash the manifest itself
        digest, size = sha256_and_size(path)
        gen, src = read_generated_utc(path)
        entry: dict[str, Any] = {
            "path": rel,
            "sha256": digest,
            "bytes": size,
            "generated_utc": gen,
            "generated_utc_source": src,
            "tracked_in_git": rel in tracked,
            "archived": "_archive" in rel or "_server_archives" in rel,
        }
        flags = read_flags(path)
        if flags:
            entry["self_declared"] = flags
        entries.append(entry)
    return entries


def merge(old: list[dict[str, Any]], new: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    """Append-only merge keyed by (path, sha256); nothing recorded is removed."""
    seen = {(e["path"], e["sha256"]): i for i, e in enumerate(old)}
    merged = [dict(e) for e in old]
    report: dict[str, list[str]] = {"added": [], "unchanged": [], "changed": [],
                                    "missing_now": []}
    new_by_key = {(e["path"], e["sha256"]) for e in new}
    new_paths = {e["path"] for e in new}
    for e in new:
        key = (e["path"], e["sha256"])
        if key in seen:
            report["unchanged"].append(e["path"])
            continue
        # Same path, different bytes: keep both, mark the earlier ones superseded.
        prior = [i for i, o in enumerate(merged) if o["path"] == e["path"]]
        for i in prior:
            merged[i]["superseded"] = True
        entry = dict(e)
        entry["first_recorded_in_manifest_utc"] = dt.datetime.now(dt.UTC).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        merged.append(entry)
        report["changed" if prior else "added"].append(e["path"])
    for o in merged:
        if o["path"] not in new_paths and not o.get("superseded"):
            o["missing_at_last_scan"] = True
            report["missing_now"].append(o["path"])
        elif o.get("missing_at_last_scan") and (o["path"], o["sha256"]) in new_by_key:
            del o["missing_at_last_scan"]          # reappeared with the same bytes
    merged.sort(key=lambda e: (e["path"], e["sha256"]))
    return merged, report


def self_test() -> None:
    """Checks that must hold for the manifest to mean anything."""
    fails: list[str] = []

    def ck(name: str, cond: bool) -> None:
        print(f"  [{'ok' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        f = tmp / "a.json"
        f.write_text('{"generated_utc": "2026-09-26T00:00:00Z", "x": 1}')
        d1, n1 = sha256_and_size(f)
        ck("sha256 is 64 hex chars", len(d1) == 64 and all(c in "0123456789abcdef" for c in d1))
        ck("byte count matches the file", n1 == f.stat().st_size)
        ck("generated_utc read from the JSON",
           read_generated_utc(f) == ("2026-09-26T00:00:00Z", "JSON field 'generated_utc'"))

        f.write_text('{"generated_utc": "2026-09-26T00:00:00Z", "x": 2}')
        d2, _ = sha256_and_size(f)
        ck("editing the file changes the hash", d1 != d2)

        (tmp / "b.json").write_text('{"env_log": {"generated_utc": "Z1"}}')
        ck("nested generated_utc found",
           read_generated_utc(tmp / "b.json")[0] == "Z1")
        (tmp / "c.json").write_text('{"x": 1}')
        ck("absent timestamp is null, not an mtime",
           read_generated_utc(tmp / "c.json") == (None, "absent from the JSON"))
        (tmp / "d.json").write_text("{not json")
        ck("unreadable JSON is reported, not fatal",
           read_generated_utc(tmp / "d.json")[0] is None)
        (tmp / "e.json").write_text('{"INVALID": "axis 2 sweep, wrong padding"}')
        ck("INVALID field carried into the manifest",
           read_flags(tmp / "e.json").get("INVALID", "").startswith("axis 2"))

    # merge semantics
    old = [{"path": "p", "sha256": "a" * 64, "bytes": 1}]
    new = [{"path": "p", "sha256": "b" * 64, "bytes": 2}]
    m, r = merge(old, new)
    ck("a rewritten result keeps both entries", len(m) == 2)
    ck("the earlier entry is marked superseded",
       any(e["sha256"] == "a" * 64 and e.get("superseded") for e in m))
    ck("a rewrite is reported as changed, not added", r["changed"] == ["p"])
    m2, r2 = merge(old, old)
    ck("re-running adds nothing", len(m2) == 1 and r2["added"] == [])
    m3, r3 = merge(old, [])
    ck("a vanished result is flagged, not deleted",
       len(m3) == 1 and m3[0].get("missing_at_last_scan") and r3["missing_now"] == ["p"])

    print(f"\nself-test: {len(fails)} failure(s)")
    if fails:
        raise SystemExit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="verify recorded hashes; write nothing")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    print("self-test:")
    self_test()
    if a.self_test:
        return

    manifest_path = REPO / MANIFEST_REL
    if manifest_path.exists():
        doc = json.loads(manifest_path.read_text())
        old = doc.get("files", [])
    else:
        doc, old = {}, []

    new = scan(PROJECT, REPO)
    merged, report = merge(old, new)

    print(f"\nscanned {len(new)} result JSON(s) under {SCAN_ROOT_REL}")
    for k in ("added", "changed", "missing_now"):
        if report[k]:
            print(f"  {k}: {len(report[k])}")
            for p in report[k]:
                print(f"    {p}")
    print(f"  unchanged: {len(report['unchanged'])}")

    if a.check:
        bad = len(report["changed"]) + len(report["missing_now"])
        print(f"\n--check: {bad} discrepanc(y/ies); nothing written")
        raise SystemExit(1 if bad else 0)

    doc.update({
        "what_this_is": (
            "Identity record for the result files of the NativeAffect project. "
            "Result JSONs are excluded by .gitignore, so this tracked manifest "
            "fixes their bytes as of the commit that records them."
        ),
        "what_this_does_not_establish": (
            "It does not establish when a result was produced. generated_utc is "
            "copied from inside each JSON and is only as trustworthy as the script "
            "that wrote it; mtime is deliberately not recorded. Only the commit "
            "date of this manifest is externally witnessed, and it bounds the "
            "bytes from above, not the computation."
        ),
        "append_only": (
            "Entries are keyed by (path, sha256). A path that reappears with "
            "different bytes is appended and the earlier entry is marked "
            "superseded; entries are never removed."
        ),
        "generator": "python/phase10/make_results_manifest.py",
        "last_updated_utc": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_files": len(merged),
        "files": merged,
    })
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {manifest_path}")


if __name__ == "__main__":
    main()
