#!/usr/bin/env python3
"""Checks for FOUR-PLACE-20261031-001D: no value-free four-place law has mutual selection.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Uses ticket A's library (bound by hash). Run with the repository's .venv."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "proofs/FOUR-PLACE-20261031-001A/FOUR-PLACE-20261031-001A-P001_the_value_free_four_place_knots"
B_DIR = ROOT / "proofs/FOUR-PLACE-20261031-001B/FOUR-PLACE-20261031-001B-P001_value_free_not_all_equal_never_fails_at_four_places"
C_DIR = ROOT / "proofs/FOUR-PLACE-20261031-001C/FOUR-PLACE-20261031-001C-P001_the_other_value_free_laws_build_equality"
sys.path.insert(0, str(A_DIR))
import four_lib as F  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings and upstream results
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]}
check("0 dependency artifacts bound by hash; tickets A, B, C and PARITY-CORRECTION B Proved and passed",
      not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})


def checks_of(d):
    return json.loads((d / "result.json").read_text())["checks"]


A, B, C = checks_of(A_DIR), checks_of(B_DIR), checks_of(C_DIR)
first = lambda res, prefix: next(v for k, v in res.items() if k.startswith(prefix))  # noqa: E731

# ------------------------------------------------------------------------------------------------ 1. parity's count
census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
rng = random.Random(20261031)
par = F.classes()["parity"]
bad_count, tried = [], 0
for n in (4, 5, 6, 7):
    for lines in F.systems(n, census):
        rows = [0] * n
        for i, L in enumerate(lines):
            for p in L:
                rows[p] ^= 1 << i
        basis = {}
        for v in rows:
            while v:
                t = v.bit_length() - 1
                if t in basis:
                    v ^= basis[t]
                else:
                    basis[t] = v
                    break
        r = len(basis)
        for _ in range(4):
            choice = [rng.choice(par) for _ in lines]
            b = sum((0 if (0, 0, 0, 0) in R else 1) << i for i, R in enumerate(choice))   # odd parity on a line: right-hand side 1
            v = b
            while v and (v.bit_length() - 1) in basis:
                v ^= basis[v.bit_length() - 1]
            formula = 2 ** (n - r) if v == 0 else 0
            direct = sum(all(tuple(c >> p & 1 for p in L) in R for L, R in zip(lines, choice)) for c in range(1 << n))
            tried += 1
            if formula != direct:
                bad_count.append((lines, choice))
check("1 parity's count on 4-regular systems is 2^(n-r) or 0 (Gaussian elimination), checked against brute force on every system with "
      "n <= 7 and four random signings each: its count is polynomial, so it fails (M2)", not bad_count and tried == 80,
      {"systems x signings": tried, "mismatches": len(bad_count)})

# ------------------------------------------------------------------------------------------------ 2. the classification
TABLE = {
    "parity": {"fails on 4-regular systems": first(A, "6 ")["pass"], "failures recognisable": "yes (linear algebra)",
               "count #P-hard in general": False, "mutually selecting": "no: (M2) fails (count 2^(n-r) or 0, check 1)"},
    "not-exactly-two": {"fails on 4-regular systems": True, "failures recognisable": "no unless P = NP (coNP-complete, C)",
                        "count #P-hard in general": "not needed", "mutually selecting": "no: (M1) fails unless P = NP"},
    "twelve": {"fails on 4-regular systems": True, "failures recognisable": "no unless P = NP (coNP-complete, C)",
               "count #P-hard in general": "not needed", "mutually selecting": "no: (M1) fails unless P = NP"},
    "not-all-equal": {"fails on 4-regular systems": False, "failures recognisable": "vacuous (never fails, B)",
                      "count #P-hard in general": "not needed", "mutually selecting": "no: (M1) fails (empty failing class)"},
}
ok2 = first(A, "1 ")["pass"] and first(A, "6 ")["pass"] and first(B, "2 ")["pass"] and first(B, "3 ")["pass"] \
    and first(C, "1 ")["pass"] and first(C, "3 ")["pass"] and set(TABLE) == set(F.classes()) \
    and not any(v["mutually selecting"].startswith("yes") for v in TABLE.values())
check("2 the four value-free four-place classes: none is mutually selecting on 4-regular systems (unless NP-complete problems are "
      "polynomial): parity's count is polynomial, not-exactly-two and twelve have coNP-complete failures, not-all-equal never fails",
      ok2, TABLE)

# ------------------------------------------------------------------------------------------------ 3. only three places
fano = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
fano_fails = not any(all(len({c >> p & 1 for p in L}) == 2 for L in fano) for c in range(1 << 7))
check("3 value-free not-all-equal on regular systems fails at three places (the Fano plane, the smallest knot's space) and never at k >= 4 "
      "(B): among value-free laws, failures that can be recognised occur only at three places", fano_fails and first(B, "2 ")["pass"],
      {"Fano fails not-all-equal": fano_fails, "B, the k >= 4 theorem": "Thomassen's even digraphs (in- and out-degree >= 3)"})

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
