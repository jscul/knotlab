"""Test (d): the smallest two-sided stall (S_cycle_five) and the smallest parity closing (C_binary) of the whole-stage-
settings study, with its edits as settings, its readings and its weights on the start, under ordinary growth and under R
(conventions O and N, and every allowed choice).  Supplementary, not judged: C_ternary.

Set-ups, edits and readings are those of experiments/WHOLE-STAGE-SETTINGS-20261120-001B/.../edits.py (imported):
setting 1 at a side adds the optional loose distinction at that side's holder; the round is one complete round; S reads,
at each side, whether the side's mark has two holders after the round; C reads at Alice whether a birth with no fresh
distinction takes her mark, at Bob whether his optional distinction gains a holder (edits.responses, re-expressed here
on full holdings).  Weights: uniform over the allowed words of the unedited start, the added distinction carried at zero
under parity and fair under not-all-equal, each word splitting its mass equally among its extensions; outcomes do not
depend on values, so each cell is a point mass on one outcome pair; the denominators are computed by enumeration and
every allowed word of every edited stage is checked to extend.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
import time
from fractions import Fraction
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402
import words  # noqa: E402

sys.path.insert(0, str(rlaw.ROOT / "experiments/WHOLE-STAGE-SETTINGS-20261120-001B/"
                                   "WHOLE-STAGE-SETTINGS-20261120-001B-E001_ordinary_edits"))
import edits  # noqa: E402

SETTINGS = tuple(product((0, 1), repeat=2))
NAMES = ("S_cycle_five", "C_binary", "C_ternary")


def readings(prep, edited, g, r):
    """edits.responses on full holdings.  g: the structure after the round (or the edited one if no round)."""
    owners = g.holders
    if prep.mechanism == "S":
        return tuple(int(len(owners.get(mark, ())) == 2) for mark in prep.marks)
    a = prep.marks[0]
    b = prep.optional[1]
    alice = False
    if r is not None and r.status == "extend":
        alice = any(f == 0 and a in row for row, f in zip(r.inputs, r.fresh, strict=True))
    bob = any(b in s for s in edited) and len(owners.get(b, ())) == 2
    return int(alice), int(bob)


def one_round(prep, settings, law, rule, conv="O"):
    edited = prep.edited(settings)
    g = rlaw.Growth(edited, law, rule, conv)
    r = g.plan()
    if r.status == "extend":
        g.apply(r)
    return edited, g, r


def all_choice_outcomes(prep, settings, law):
    edited = prep.edited(settings)
    g0 = rlaw.Growth(edited, law, "R", "O")
    r = g0.plan()
    if r.status == "closed" or not r.shortages:
        g = g0.clone()
        if r.status == "extend":
            g.apply(r)
        return {"choices": 1, "outcomes": {str(readings(prep, edited, g, r)): 1}, "statuses": {r.status: 1}}
    per = g0.allowed_choices(r)
    import itertools
    import math
    total = math.prod(len(o) for _, o in per)
    outs, stats = {}, {}
    for combo in itertools.product(*[o for _, o in per]):
        ch = dict(zip([k for k, _ in per], combo))
        p = g0.plan_with(r, ch)
        g = g0.clone()
        g.apply(p)
        key = str(readings(prep, edited, g, p))
        outs[key] = outs.get(key, 0) + 1
        stats["extend"] = stats.get("extend", 0) + 1
    if total == 0:
        stats["residual_stall under every choice"] = 1
        key = str(readings(prep, edited, g0, None))
        outs[key] = 1
    return {"choices": total, "outcomes": outs, "statuses": stats}


def table(bits):
    """bits: {settings: (alice, bob)} in setting order.  Dependence of each side on its own and on the far edit,
    correlations, signed and largest four-correlation value (the recorded edits/run.py `table`)."""
    rows = [bits[s] for s in SETTINGS]
    effects = [(-1) ** sum(b) for b in rows]
    signs = [w for w in product((-1, 1), repeat=4) if w.count(-1) % 2]
    scores = [sum(e * s for e, s in zip(effects, sign)) for sign in signs]
    # side 0 (Alice) own setting x: compare (0,y) with (1,y); far: (x,0) with (x,1).
    own = [any(bits[(0, y)][0] != bits[(1, y)][0] for y in (0, 1)), any(bits[(x, 0)][1] != bits[(x, 1)][1] for x in (0, 1))]
    far = [any(bits[(x, 0)][0] != bits[(x, 1)][0] for x in (0, 1)), any(bits[(0, y)][1] != bits[(1, y)][1] for y in (0, 1))]
    return {"outcome_pairs": ["".join(map(str, b)) for b in rows], "own_edit_dependence": {"alice": own[0], "bob": own[1]},
            "far_edit_dependence": {"alice": far[0], "bob": far[1]}, "correlations": effects,
            "signed": effects[0] + effects[1] + effects[2] - effects[3], "largest": max(scores)}


def main():
    t0 = time.time()
    preps = {p.name: p for p in edits.built_cases() if p.name in NAMES}
    out, prefixes = {}, []
    for name in NAMES:
        prep = preps[name]
        out[name] = {"base_knots": len(prep.base), "base_distinctions": len({d for s in prep.base for d in s}),
                     "readers": prep.readers, "marks": prep.marks, "optional": prep.optional, "laws": {}}
        for law in rlaw.LAWS:
            base = words.Stage(list(prep.base), law)
            entry = {"prepared_words": base.n_ok, "rules": {}}
            for rule, conv in (("ordinary", None), ("R", "O"), ("R", "N")):
                bits, detail = {}, {}
                for s in SETTINGS:
                    edited, g, r = one_round(prep, s, law, rule, conv or "O")
                    bits[s] = readings(prep, edited, g, r)
                    st = words.Stage(list(edited), law)
                    ext = None
                    if r.status == "extend":
                        bad, _ = st.extends(list(zip(r.inputs, r.fresh)))
                        ext = {"edited_words": st.n_ok, "failing": bad}
                        prefixes.append({"test": "d", "name": name, "law": law, "rule": rule, "conv": conv,
                                         "settings": s, "n_at": [len(edited), len(g.stars)],
                                         "stars": [list(x) for x in g.stars],
                                         "paid_births": [sum(1 for prow in r.paid if any(prow))]})
                    detail["".join(map(str, s))] = {
                        "status": r.status, "births": len(r.parents or ()),
                        "parents": [list(p) for p in (r.parents or ())], "fresh": list(r.fresh or ()),
                        "paid_births": (sum(1 for prow in r.paid if any(prow)) if r.status == "extend" else None),
                        "shortages": [list(x) for x in (r.shortages or ())], "bits": bits[s], "extension": ext,
                        "cell_mass": [base.n_ok if [a, b] == list(bits[s]) else 0 for a, b in SETTINGS]}
                tab = table(bits)
                if not (tab["own_edit_dependence"]["alice"] or tab["own_edit_dependence"]["bob"]):
                    tab["signed"] = tab["largest"] = None  # reported only where own-edit dependence is present
                    tab["four_correlation_note"] = "not reported: no side depends on its own edit"
                key = rule if rule == "ordinary" else f"R_{conv}"
                entry["rules"][key] = {"table": tab, "cells": detail}
            choice = {"".join(map(str, s)): all_choice_outcomes(prep, s, law) for s in SETTINGS}
            entry["rules"]["R_every_choice"] = choice
            out[name]["laws"][law] = entry
    out["seconds"] = round(time.time() - t0, 1)
    rlaw.OUT.mkdir(parents=True, exist_ok=True)
    (rlaw.OUT / "d_tables.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    rlaw.dump(rlaw.OUT / "prefixes" / "d.jsonl.gz", prefixes)
    for name in NAMES:
        for law in rlaw.LAWS:
            for key, v in out[name]["laws"][law]["rules"].items():
                if key == "R_every_choice":
                    print(name, law, key, {s: (c["choices"], c["outcomes"]) for s, c in v.items()})
                else:
                    t = v["table"]
                    print(name, law, key, t["outcome_pairs"], "own", t["own_edit_dependence"], "far",
                          t["far_edit_dependence"], "signed", t["signed"], "largest", t["largest"],
                          [c["status"] for c in v["cells"].values()])


if __name__ == "__main__":
    main()
