"""Knot-side check on the three closed parts met in P3 with at most 14 distinctions (the last three of the five structures of
gate row G; the first two are checked in gates.py).

Selection rule, fixed here before the parts are looked at: read the parity-law P3 files in the order arm 0, 1, 2, 3; within a
file in line order; take each closed part with at most 14 distinctions whose incidence pattern is not isomorphic to one already
taken; stop at three.  (If fewer than three different patterns exist, the remainder is filled with the earliest repeats and the
note says so.)

For each: the chance of every change-answer word on every distinction under the recorded counting rule (words.counts_table of
single-mark change questions) against the chance from drawing a uniform set of knots and reading each distinction as the parity
of its drawn holders.  Exact fractions.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gates  # noqa: E402
import lib  # noqa: E402


def typed(stars):
    g = lib.incidence_graph([tuple(s) for s in stars])
    for node in g:
        g.nodes[node]["kind"] = node[0]
    return g


def main():
    words = lib.load_module("ks_words", gates.WORDS_PY)
    chosen, notes = [], []
    repeats = []
    for arm in (0, 1, 2, 3):
        path = lib.OUT / f"p3_parity_arm{arm}_000-256.jsonl"
        for line in path.open():
            r = json.loads(line)
            if r["kind"] != "closed_part" or r["stars"] is None or r["distinctions"] > 14:
                continue
            g = typed(r["stars"])
            entry = {"arm": r["arm"], "draw": r["draw"], "t": r["t"], "knots": r["knots"], "distinctions": r["distinctions"],
                     "stars": r["stars"], "T": r["T"], "admits": r["admits"]}
            if any(nx.is_isomorphic(g, typed(c["stars"]), node_match=lambda a, b: a["kind"] == b["kind"]) for c in chosen):
                repeats.append(entry)
                continue
            chosen.append(entry)
            if len(chosen) == 3:
                break
        if len(chosen) == 3:
            break
    while len(chosen) < 3 and repeats:
        chosen.append(repeats.pop(0))
        notes.append("filled with a repeat of an earlier pattern")
    results = []
    for c in chosen:
        # the stars use the engine's distinction names; rename to 0..m-1 for the word tables
        check = gates.knot_side(words, [tuple(s) for s in c["stars"]])
        results.append({**{k: c[k] for k in ("arm", "draw", "t", "knots", "distinctions", "T", "admits")}, **check})
    out = {"selected": len(results), "notes": notes, "structures": results, "pass": len(results) == 3 and all(r["agree"] for r in results)}
    (lib.OUT / "knotside.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
