#!/usr/bin/env python3
"""Checks for BASES-WITHIN-20261112-001A (research/BASES-WITHIN-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part axial|offsets|box|gasket|summary [--write]
axial (E1): every harmony with P <= 16: levels 2 and 3, states (capped at 100,000), the linear and mirror-lift states, the ties of
the origin at level 2 against the product lemma. offsets (E2): every harmony against every connected outer pattern of up to 6
distinctions and 4 knots, the Fano plane less one knot and the Fano plane: a binding at one place and 60 sampled bindings with
offsets (every offset for the alternation, against signed not-all-equal). box (E3): five finite seeds, levels 1 to 4: lives, the
ties of each diagonal origin against the product lemma, the farthest tie and the distance to the farthest distinction. gasket (E4):
the drawn three-copy nesting of one knot, levels 0 to 7: lives, ties of a corner and of a shared corner, farthest tie, distances.
summary: the frozen items. The independent referee is the background referee thread's (referee pending)."""
import hashlib
import itertools
import json
import os
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("nest_lib.py", "check.py")] + \
       ["proofs/HARMONY-ARITH-20261112-001A/HARMONY-ARITH-20261112-001A-P001_binding_and_harmonies/harm_lib.py",
        "research/BASES-WITHIN-20261112-001/preregistration.md"]
SAMPLES = 60


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def axial_job(n):
    import nest_lib as N
    h = N.harmonies()[n]
    P = h["P"]
    row = {"n": n, "orbits": h["orbits"], "P": P, "states": len(N.states(h))}
    for k in (2, 3):
        t = time.time()
        c = N.axial_count(h, k, cap=100000)
        known = N.known_arrays(h, k) if (k == 2 or len(N.states(h)) ** 3 * P ** 3 <= 3 * 10 ** 7) else None
        row["level %d" % k] = {"states": c, "known": known,
                               "rigid (only linear states)": None if (c is None or known is None) else c == known["linear"],
                               "seconds": round(time.time() - t, 1)}
    line = N.harmony_line_ties(h)
    knots, idx = N.axial_knots(h, 2)
    tied = N.tie_class(knots, len(idx), idx[(0, 0)])
    inv = {v: c for c, v in idx.items()}
    pred = {(i, j) for i in line for j in line}
    row["ties"] = {"line ties of place 0": sorted(line), "level 2 tied to the origin": len(tied),
                   "level 2 ties = product of line ties": {inv[v] for v in tied} == pred}
    return row


def offsets_job(n):
    import nest_lib as N
    h = N.harmonies()[n]
    P = h["P"]
    pats = N.outer_patterns() + [(7, N.FANO[:-1]), (7, N.FANO)]
    rng = random.Random(1000 * n + 7)
    out = []
    for pi, (m, E) in enumerate(pats):
        O = N.outer_states(E, m)
        one_place = N.lives(E, m, h)
        if P == 2:
            assigns = [tuple((0, s, t) for (s, t) in combo) for combo in itertools.product([(0, 0), (0, 1), (1, 0), (1, 1)], repeat=len(E))]
        else:
            assigns = [tuple((0, rng.randrange(P), rng.randrange(P)) for _ in E) for _ in range(SAMPLES)]
        lived = ended = signed_agree = 0
        for off in assigns:
            ok = N.lives(E, m, h, off)
            lived += ok
            ended += (not ok) and len(O) > 0
            if P == 2:
                signed_agree += ok == N.signed_nae_lives(E, m, [tuple(x % 2 for x in o) for o in off])
        out.append({"outer": [m, E], "outer lives": len(O) > 0, "chain-free": N.chain_free(E), "one place lives": one_place,
                    "offset bindings": len(assigns), "lived": lived, "ended while the outer lives": ended,
                    "signed NAE agrees": signed_agree if P == 2 else None})
    return {"n": n, "orbits": h["orbits"], "P": P, "patterns": out}


def box_job(name):
    import nest_lib as N
    m, E = N.SEEDS[name]
    rel, nst = N.seed_ties(m, E)
    rows = []
    for k in range(1, 5):
        t = time.time()
        knots, idx = N.box_power(m, E, k)
        inv = {v: d for d, v in idx.items()}
        per = []
        for a in range(m):
            d = (a,) * k
            tied = N.tie_class(knots, len(idx), idx[d])
            if tied is None:
                per.append({"origin": a, "lives": False})
                continue
            dist = N.bond_distances(knots, len(idx), idx[d])
            per.append({"origin": a, "lives": True, "tied": len(tied), "share": round(len(tied) / len(idx), 6),
                        "farthest tie": max(dist[v] for v in tied), "farthest distinction": max(dist.values()),
                        "matches the product lemma": {inv[v] for v in tied} == N.predicted_box_ties(m, E, k, d)})
        rows.append({"level": k, "distinctions": len(idx), "knots": len(knots), "origins": per, "seconds": round(time.time() - t, 1)})
    return {"seed": name, "seed states": nst, "rows": rows}


def gasket_job(level):
    import nest_lib as N
    knots, n, (A, B, C) = N.gasket(level)
    res = {"level": level, "distinctions": n, "knots": len(knots)}
    for name, root in (("corner", A), ("shared corner", 2 if level >= 1 else B)):
        tied = N.tie_class(knots, n, root)
        if tied is None:
            res[name] = {"lives": False}
            continue
        dist = N.bond_distances(knots, n, root)
        res[name] = {"lives": True, "tied": len(tied), "farthest tie": max(dist[v] for v in tied), "farthest distinction": max(dist.values())}
    return res


def run_part(part):
    import nest_lib as N
    n = len(N.harmonies())
    if part == "axial":
        with Pool(12) as pool:
            return {"rows": pool.map(axial_job, range(n), chunksize=1)}
    if part == "offsets":
        with Pool(12) as pool:
            return {"control (exactly one, the advisor's)": N.control(), "rows": pool.map(offsets_job, range(n), chunksize=1)}
    if part == "box":
        with Pool(5) as pool:
            return {"rows": pool.map(box_job, list(N.SEEDS), chunksize=1)}
    if part == "gasket":
        with Pool(8) as pool:
            return {"rows": pool.map(gasket_job, range(8), chunksize=1)}


def summary():
    ax = json.loads((HERE / "result_axial.json").read_text())["checks"]["result"]["rows"]
    of = json.loads((HERE / "result_offsets.json").read_text())["checks"]["result"]
    bx = json.loads((HERE / "result_box.json").read_text())["checks"]["result"]["rows"]
    gs = json.loads((HERE / "result_gasket.json").read_text())["checks"]["result"]["rows"]
    by = {"+".join(r["orbits"]): r for r in ax}
    cells = [p for r in of["rows"] for p in r["patterns"]]
    alt = [r for r in of["rows"] if r["orbits"] == ["01"]][0]
    return {
        "E1 states at levels 1, 2, 3": {k: [r["states"], r["level 2"]["states"], r["level 3"]["states"]] for k, r in by.items()},
        "P1 0011: 16 at level 2, 256 at level 3": [by["0011"]["level 2"]["states"], by["0011"]["level 3"]["states"]],
        "P2 000111: 102 at level 2": by["000111"]["level 2"]["states"],
        "P3 rigid at level 2 exactly for the alternation": sorted(k for k, r in by.items() if r["level 2"]["rigid (only linear states)"]),
        "check: no level below the known states (code flag)": all(r["level %d" % k]["states"] is None or r["level %d" % k]["known"] is None
                                                                   or r["level %d" % k]["states"] >= r["level %d" % k]["known"]["union"]
                                                                   for r in ax for k in (2, 3)),
        "check L7: level-2 ties are products of line ties": all(r["ties"]["level 2 ties = product of line ties"] for r in ax),
        "check L4: a binding at one place lives exactly when the outer does": all(p["one place lives"] == p["outer lives"] for p in cells),
        "check L8: chain-free patterns never end under offsets": all(p["ended while the outer lives"] == 0 for p in cells if p["chain-free"]),
        "check L9: the alternation's offsets read as signed NAE": all(p["signed NAE agrees"] == p["offset bindings"] for p in alt["patterns"]),
        "control: exactly one ends a living outer": of["control (exactly one, the advisor's)"],
        "P4 every harmony has a binding with offsets that ends a living outer": all(any(p["ended while the outer lives"] for p in r["patterns"]) for r in of["rows"]),
        "E2 harmonies with an ending binding": sum(any(p["ended while the outer lives"] for p in r["patterns"]) for r in of["rows"]),
        "E2 ended share per harmony": {"+".join(r["orbits"]): [sum(p["ended while the outer lives"] for p in r["patterns"]), sum(p["offset bindings"] for p in r["patterns"] if p["outer lives"])] for r in of["rows"]},
        "check E3: box ties match the product lemma": all(o.get("matches the product lemma", True) for s in bx for row in s["rows"] for o in row["origins"]),
        "E3 farthest tie / farthest distinction by seed and level": {s["seed"]: [[(o["origin"], o.get("farthest tie"), o.get("farthest distinction")) for o in row["origins"]] for row in s["rows"]] for s in bx},
        "P5 gasket: lives at every level, no ties": all(r[c]["lives"] and r[c]["tied"] == 1 for r in gs for c in ("corner", "shared corner")),
        "E4 gasket": [[r["level"], r["corner"].get("tied"), r["corner"].get("farthest tie"), r["corner"].get("farthest distinction"), r["shared corner"].get("tied")] for r in gs],
    }


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if write:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")
    else:
        old = json.loads(path.read_text())["checks"]
        same = json.dumps(old["result"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(res["result"], default=str)), sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
