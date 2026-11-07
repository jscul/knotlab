#!/usr/bin/env python3
"""Checks for PENDANT-LINE-20261106-001C: what one line completes.

The ticket's results are consequences of cited theorems. This checker confirms the cited evidence: the bound proofs are Proved and their
checks passed with the statements used (no violation in ticket A's local verification, no counterexample in ticket B's, TWO-BIT-SCREEN
A's reduction and no-loss theorem checked, TWO-BIT-SCREEN B's chains all following the touching rule), and it re-derives the touching rule
from TWO-BIT-SCREEN B's recorded place tables.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
A = "proofs/PENDANT-LINE-20261106-001A/PENDANT-LINE-20261106-001A-P001_creation_is_decided_at_the_gluing_line"
B = "proofs/PENDANT-LINE-20261106-001B/PENDANT-LINE-20261106-001B-P001_one_new_line_never_adds_creation"
TBA = "proofs/TWO-BIT-SCREEN-20261105-001A/TWO-BIT-SCREEN-20261105-001A-P001_hidden_points_and_the_two_bit_screening_lemma"
TBB = "proofs/TWO-BIT-SCREEN-20261105-001B/TWO-BIT-SCREEN-20261105-001B-P001_what_screening_gives_the_brace_dictionary"


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def result(d):
    return json.loads((ROOT / d / "result.json").read_text())["checks"]


def touching(name):
    if name.startswith("same atom"):
        return "mutual"
    m = re.match(r"atoms \d apart, arrows \S+: (.+) to (.+)", name)
    ao, bo = m.group(1) in ("emitter", "cut line"), m.group(2) in ("emitter", "cut line")
    return {(True, True): "mutual", (False, True): "forward", (True, False): "backward", (False, False): "silent"}[(ao, bo)]


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    ra, rb, rta, rtb = result(A), result(B), result(TBA), result(TBB)
    a3 = next(v for k, v in ra.items() if k.startswith("3 "))["info"]["totals"]
    b1 = next(v for k, v in rb.items() if k.startswith("1 "))["info"]["totals"]
    check("1 the cited theorems' checks: ticket A's local verification has no violation, ticket B's none counterexample, and "
          "TWO-BIT-SCREEN A's no-loss theorem and reduction (its checks 3 and 3b) and TWO-BIT-SCREEN B's chains (checks 2, 3 and 6) passed",
          a3["violations of the two-round rule"] == 0 and b1["... and one through it not reached (counterexample)"] == 0
          and all(rta[k]["pass"] for k in rta if k.startswith("3")) and all(rtb[k]["pass"] for k in rtb if k[:2] in ("2 ", "3 ", "6 ")),
          {"ticket A violations": a3["violations of the two-round rule"], "ticket B counterexamples":
           b1["... and one through it not reached (counterexample)"]})

    places = {}
    for k, v in rtb.items():
        if k[:2] in ("2 ", "3 "):
            places.update({p: rel[0] for p, rel in v["info"]["place: (relation here, relation in BRACE-TREE)"].items()})
        if k[:2] == "5 ":
            places.update({p: rel[0] for p, rel in v["info"]["distance-three places: (relation here, relation in BRACE-TREE)"].items()})
    agree = {p: (r == [touching(p)]) for p, r in places.items()}
    check("2 the touching rule re-derived from TWO-BIT-SCREEN B's recorded tables: at every place of every chain of two and three atoms, "
          "and at distance three on the four-atom paths, the relation is the touching rule's",
          all(agree.values()), {"places": len(agree), "distance at most two": sum(1 for p in agree if not p.startswith("atoms 3")),
                                "distance three": sum(1 for p in agree if p.startswith("atoms 3"))})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    res = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
           "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
           "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(res, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
