#!/usr/bin/env python3
"""Checks for HIDDEN-COPY-20261112-001A (research/HIDDEN-COPY-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part endo|binary|gadgets|summary [--write]
endo: for each of the 40 harmonies (period <= 16, at most 36 states) and each of its 1,267 kind sets of span <= 8: a non-injective
non-constant endomorphism (E-large) or none (E-small); automorphisms beyond the shifts and flips; the number of Aut-orbits. binary: for
each E-small (harmony, kind set) with at most 12 states, an essential binary polymorphism (affine branch) or none (essentially unary).
gadgets: for each harmony with at most 12 states, its census kind set, every gadget with 3 observed copies, 1 or 2 hidden copies and 2 or
3 stitches among distinct copies (every copy used): its relation and whether Z_2 readouts constant on the shift-and-flip classes make it
factor-permutive; the same for 3 random baseline relations per harmony (the diagonal, shift-and-flip invariant, as many triples as R).
summary: the frozen items. Referee: the background referee thread (pending)."""
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("hidden_lib.py", "check.py")] + \
       ["proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series/nest_lib.py",
        "proofs/LOOP-LOCK-20261112-001A/LOOP-LOCK-20261112-001A-P001_loop_locking/loop_lib.py",
        "research/HIDDEN-COPY-20261112-001/preregistration.md"]
ROUNDS = 3000
BASELINES = 3


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def endo_job(arg):
    import hidden_lib as L
    i, j = arg
    h = L.harmonies_with_kind_sets()[i]
    kinds = h["kind sets"][j]
    st = L.setup(h["orbits"], h["P"], kinds)
    f, settled = L.endo_large_witness(st, ROUNDS)
    auts, complete = L.automorphisms(st, cap=200)
    norb, _ = L.orbits(st["n"], auts)
    ng, _ = L.orbits(st["n"], st["G"])
    return {"i": i, "j": j, "harmony": " + ".join(h["orbits"]), "kinds": kinds, "census kind set": j == 0, "states": st["n"],
            "stitch triples": len(st["R"]), "E": ("large" if f is not None else ("small" if settled else "not settled")),
            "witness": f, "automorphisms": len(auts), "beyond shifts and flips": len(auts) - len(st["G"]), "automorphisms complete": complete,
            "Aut-orbits": norb, "shift-and-flip classes": ng}


def binary_job(arg):
    import hidden_lib as L
    i, j = arg
    h = L.harmonies_with_kind_sets()[i]
    st = L.setup(h["orbits"], h["P"], h["kind sets"][j])
    t = time.time()
    f, settled = L.essential_binary(st, ROUNDS)
    return {"i": i, "j": j, "harmony": " + ".join(h["orbits"]), "states": st["n"],
            "essential binary": (None if not settled else f is not None),
            "example": None if f is None else {"%d,%d" % k: v for k, v in f.items()}, "seconds": round(time.time() - t, 1)}


def gadget_job(arg):
    import hidden_lib as L
    i, which = arg
    h = L.harmonies_with_kind_sets()[i]
    st = L.setup(h["orbits"], h["P"], h["kind sets"][0])
    if which >= 0:
        st = dict(st)
        st["R"] = L.random_relation(st, "HIDDEN-COPY|%d|%d" % (i, which))
        st["Rl"] = sorted(st["R"])
    _, cells = L.orbits(st["n"], st["G"])
    t = time.time()
    seen = {}
    counts = {}
    first = None
    for hh, stitches, T in L.gadget_relations(st, 2, 3):
        key = T.tobytes()
        if key not in seen:
            seen[key] = bool(L.factor_permutive_z2(st, T, cells))
        c = counts.setdefault("%d hidden, %d stitches" % (hh, len(stitches)), [0, 0])
        c[0] += 1
        c[1] += seen[key]
        if seen[key] and first is None:
            first = {"hidden": hh, "stitches": [list(x) for x in stitches]}
    return {"i": i, "harmony": " + ".join(h["orbits"]), "states": st["n"], "baseline": which, "gadgets": counts,
            "distinct relations": len(seen), "factor-permutive relations": sum(seen.values()), "first factor-permutive gadget": first,
            "seconds": round(time.time() - t, 1)}


def run_part(part):
    import hidden_lib as L
    hs = L.harmonies_with_kind_sets()
    part_dir = HERE / "partial"
    part_dir.mkdir(exist_ok=True)
    if part == "endo":
        args = [(i, j) for i, h in enumerate(hs) for j in range(len(h["kind sets"]))]
        job = endo_job
    elif part == "binary":
        endo = json.loads((HERE / "result_endo.json").read_text())["checks"]["result"]["rows"]
        args = [(r["i"], r["j"]) for r in endo if r["E"] == "small" and 3 <= r["states"] <= 12]
        job = binary_job
    else:
        args = [(i, b) for i, h in enumerate(hs) if len(L.setup(h["orbits"], h["P"], h["kind sets"][0])["W"]) <= 12
                for b in range(-1, BASELINES)]
        job = gadget_job
    rows = []
    with Pool(8) as pool:
        for k, row in enumerate(pool.imap_unordered(job, args, chunksize=1)):
            rows.append(row)
            if k % 50 == 0:
                (part_dir / ("%s.json" % part)).write_text(json.dumps(rows, default=str) + "\n")
    (part_dir / ("%s.json" % part)).write_text(json.dumps(rows, default=str) + "\n")
    return {"rows": sorted(rows, key=lambda r: (r["i"], r.get("j", 0), r.get("baseline", 0)))}


def load(part):
    return json.loads((HERE / ("result_%s.json" % part)).read_text())["checks"]["result"]


def summary():
    out = {}
    endo = load("endo")["rows"]
    out["kind sets"] = len(endo)
    out["harmonies"] = len({r["i"] for r in endo})
    for key in ("small", "large", "not settled"):
        out["(harmony, kind set) pairs E-" + key] = sum(1 for r in endo if r["E"] == key)
    census = [r for r in endo if r["census kind set"]]
    out["census kind sets: E-small harmonies"] = [r["harmony"] for r in census if r["E"] == "small"]
    out["census kind sets: E-large harmonies"] = [r["harmony"] for r in census if r["E"] == "large"]
    out["harmonies E-small under every kind set"] = sorted({r["harmony"] for r in endo} - {r["harmony"] for r in endo if r["E"] != "small"})
    out["harmonies E-small under some kind set"] = sorted({r["harmony"] for r in endo if r["E"] == "small"})
    out["automorphisms beyond the shifts and flips (pairs)"] = sum(1 for r in endo if r["beyond shifts and flips"] > 0)
    out["E-small pairs with at least 3 Aut-orbits"] = sum(1 for r in endo if r["E"] == "small" and r["Aut-orbits"] >= 3)
    try:
        b = load("binary")["rows"]
        out["binary: E-small pairs searched"] = len(b)
        out["binary: essentially unary (no essential binary polymorphism)"] = sum(1 for r in b if r["essential binary"] is False)
        out["binary: affine branch (an essential binary polymorphism)"] = [[r["harmony"], r["j"]] for r in b if r["essential binary"]]
        out["binary: not settled"] = sum(1 for r in b if r["essential binary"] is None)
        eu = {(r["i"], r["j"]) for r in b if r["essential binary"] is False}
        out["essentially unary with at least 3 Aut-orbits (gadget-definable factor-permutive relations exist)"] = sorted({r["harmony"] for r in endo if (r["i"], r["j"]) in eu and r["Aut-orbits"] >= 3})
    except FileNotFoundError:
        out["binary"] = "not run"
    try:
        g = load("gadgets")["rows"]
        out["gadgets: harmonies"] = len({r["i"] for r in g if r["baseline"] < 0})
        out["gadgets: harmonies with a factor-permutive gadget (h <= 2, s <= 3)"] = [[r["harmony"], r["first factor-permutive gadget"]] for r in g if r["baseline"] < 0 and r["factor-permutive relations"]]
        out["gadgets: baselines with one"] = sum(1 for r in g if r["baseline"] >= 0 and r["factor-permutive relations"])
        out["gadgets: baselines"] = sum(1 for r in g if r["baseline"] >= 0)
        tot = lambda rows: [sum(sum(v[0] for v in r["gadgets"].values()) for r in rows), sum(sum(v[1] for v in r["gadgets"].values()) for r in rows)]
        out["gadgets: harmonies' gadgets (all, factor-permutive)"] = tot([r for r in g if r["baseline"] < 0])
        out["gadgets: baselines' gadgets (all, factor-permutive)"] = tot([r for r in g if r["baseline"] >= 0])
    except FileNotFoundError:
        out["gadgets"] = "not run"
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if "--write" in sys.argv:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")


if __name__ == "__main__":
    main()
