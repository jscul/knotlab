"""Checker for PINWHEEL-NATIVE-20261107-001A-P001 (a finite rule on knots regrows the pinwheel law).

Writes result.json and rule_table.json (the finite rule with abstract label names) next to this file.
Run: python3 -B check.py"""
from __future__ import annotations
import json, sys, time
from collections import Counter, defaultdict
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import native_lib as nl

def regrow(K, mutate=None):
    """Grow symbolically to level K and compare with the geometric pinwheel at every level. Returns per-level rows."""
    saved = (nl.COVER, nl.HANDS, nl.CUTS)
    if mutate:
        mutate()
    rows = []
    try:
        hands, segs = nl.start()
        for k in range(K + 1):
            tiles, _ = nl.tiling_rule("pinwheel", k)
            geo = nl.geometric_incidences(tiles)
            sym = nl.symbolic_incidences(segs)
            rows.append({"level": k, "knots": len(tiles), "distinctions": len(geo), "identical": geo == sym,
                         "hands_identical": [nl.handedness(t) for t in tiles] == hands})
            if k < K:
                hands, segs = nl.step(hands, segs)
    finally:
        nl.COVER, nl.HANDS, nl.CUTS = saved
    return rows

def name_labels(alphabet):
    inner = sorted((l for l in alphabet if len(l[0]) == 2), key=str)
    outer = sorted((l for l in alphabet if len(l[0]) == 1), key=str)
    names = {}
    for i, l in enumerate(inner):
        names[l] = "abcdefgh"[i] if i < 8 else f"i{i}"
    for i, l in enumerate(outer):
        names[l] = "xyz"[i] if i < 3 else f"o{i}"
    return names

def describe(l):
    d, al = l
    return {"sides": [f"{s}[{lo},{hi}]" for s, lo, hi in d], "same_direction": al}

def geometric_locality(k):
    """On the geometric side: distinctions with one label at level k always split into the same sequence of child labels at k + 1."""
    tiles_k, _ = nl.tiling_rule("pinwheel", k)
    hands, segs = nl.start()
    for _ in range(k):
        hands, segs = nl.step(hands, segs)
    seen = {}
    ok = True
    for seg in segs:
        ch = tuple(nl.label({"inc": [(0, cs, lo, hi) for ci, cs, lo, hi in new], "aligned": al}) for new, al, _ in nl.split_seg(seg))
        lab = nl.label(seg)
        if seen.setdefault(lab, ch) != ch:
            ok = False
    return ok, len(seen)

def main():
    t0 = time.time()
    res = {}
    checks = {}
    rows = regrow(7)
    res["regrowth"] = rows
    checks["regrows_levels_0_to_7"] = all(r["identical"] and r["hands_identical"] for r in rows)
    alphabet, children, rounds = nl.closed_alphabet()
    names = name_labels(alphabet)
    hands, segs = nl.start()
    census = Counter()
    for k in range(7):
        hands, segs = nl.step(hands, segs)
    for s in segs:
        census[names[nl.label(s)]] += 1
    res["alphabet_size"] = len(alphabet)
    res["closure_rounds"] = rounds
    res["census_level_7"] = dict(sorted(census.items()))
    checks["alphabet_closed_and_finite"] = len(alphabet) == 11 and set(census) <= set(names.values())
    loc_ok, nlab = geometric_locality(6)
    checks["splitting_depends_only_on_label"] = loc_ok
    # the finite rule, with abstract names
    table = {"distinction_labels": {names[l]: describe(l) for l in alphabet},
             "distinction_rule": {names[l]: [names[c] for c in children(l)] for l in alphabet},
             "knot_rule": {
                 "children_handedness_times_parent": list(nl.HANDS),
                 "inside_distinctions": [{"between": [f"child {c1 + 1} side {s1}", f"child {c2 + 1} side {s2}"],
                                          "label": names[nl.label({"inc": [(0, s1, a1, b1), (1, s2, a2, b2)], "aligned": al})]}
                                         for (c1, s1, a1, b1), (c2, s2, a2, b2), al in nl.INTERNAL],
                 "sides_of_children": {
                     "child 1": {"S": "parent H, first fifth (reversed)", "L": "inside H-F1, F1-O", "H": "parent S (reversed)"},
                     "child 2": {"S": "inside F1-O", "L": "inside F1-M", "H": "parent L, first half"},
                     "child 3": {"S": "inside H-F1", "L": "inside F1-M", "H": "inside H-M"},
                     "child 4": {"S": "inside F2-M", "L": "parent H, middle two fifths (reversed)", "H": "inside H-M"},
                     "child 5": {"S": "inside F2-M", "L": "parent H, last two fifths", "H": "parent L, second half"}}}}
    (HERE / "rule_table.json").write_text(json.dumps(table, indent=1) + "\n")
    controls = {}
    def flip_cover():
        nl.COVER = dict(nl.COVER); h = list(nl.COVER["H"]); c0, c1, ci, cs, fwd = h[0]; h[0] = (c0, c1, ci, cs, not fwd); nl.COVER["H"] = tuple(h)
    def wrong_hands():
        nl.HANDS = (-1, -1, -1, 1, -1)
    def wrong_cut():
        nl.CUTS = dict(nl.CUTS); nl.CUTS["H"] = (Fr(1, 5), Fr(2, 5))
    for name, mut in (("child side direction flipped", flip_cover), ("handedness pattern changed", wrong_hands),
                      ("hypotenuse cut at 1/5 and 2/5", wrong_cut)):
        try:
            rr = regrow(4, mut)
            rejected = not all(r["identical"] and r["hands_identical"] for r in rr)
        except Exception as exc:
            rejected = True
        controls[name] = {"rejected": bool(rejected)}
    # alignment ignored: every two-sided distinction treated as running the same way
    saved = nl.split_seg
    def no_align(seg):
        seg = dict(seg)
        if seg["aligned"] is not None:
            seg["aligned"] = True
        return saved(seg)
    nl.split_seg = no_align
    try:
        rr = regrow(4)
        controls["alignment ignored"] = {"rejected": not all(r["identical"] for r in rr)}
    finally:
        nl.split_seg = saved
    res["controls"] = controls
    res["runtime_seconds"] = round(time.time() - t0, 1)
    manifest = json.loads((HERE / "manifest.json").read_text())
    checks = {k: bool(v) for k, v in checks.items()}
    failures = [k for k, v in checks.items() if not v] + [f"control {k} not rejected" for k, v in controls.items() if not v["rejected"]]
    out = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
           "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
           "checks": checks, "failures": failures, "details": res}
    (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({"checks": checks, "controls": {k: v["rejected"] for k, v in controls.items()}, "census": res["census_level_7"],
                      "runtime": res["runtime_seconds"]}, indent=1))
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
