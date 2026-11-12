#!/usr/bin/env python3
"""Checks for SHIFT-LOCK-20261112-001A (research/SHIFT-LOCK-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part one|two|square|control|ringties|summary [--write]
one: the 45 harmonies on n x m repeats with unmixed knots, n, m = 3 to 8: locked against "ring n and ring m both lock" (G1).
two: the 45 harmonies on n x m repeats with the mixed knot, n, m = 2 to 9: locked against "some non-constant state is invariant,
up to a symmetry of the harmony, along a short step" (H0); a non-constant state invariant along no short step (H0'); stepped
states checked to be states (G2); the increments of each orbit. square: n x n mixed repeats, n = 2 to 16: H0 (and H0' to 12). control: the linear law over two values,
x(r, c) + x(r, c+1) + x(r+1, c) = 0 on n x n, n = 1 to 32 (rank), against the advisor's criterion. ringties: the copies tied to copy 0
on rings of n knots, n in RING_NS. summary: the frozen items. Referee: the background referee thread (referee pending)."""
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
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("shift_lib.py", "check.py")] + \
       ["proofs/LOOP-LOCK-20261112-001A/LOOP-LOCK-20261112-001A-P001_loop_locking/loop_lib.py",
        "proofs/ENDLESS-BLOCK-20261112-001A/ENDLESS-BLOCK-20261112-001A-P001_endless_blocks/endless_lib.py",
        "research/LOOP-LOCK-20261112-001/referee-R1/result_rings.json",
        "research/SHIFT-LOCK-20261112-001/preregistration.md"]
CAP = 20000
ONE = range(3, 9)
TWO = range(2, 10)
SQUARE = range(2, 17)
RING_NS = (6, 8, 12, 16, 24, 30, 36, 48, 60)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Rings:
    """whether the ring of k knots has a non-constant state (k = 1, 2 as closed walks of the pair transfer)"""
    def __init__(self, S):
        self.S, self.cache = S, {}

    def unlocks(self, k):
        import shift_lib as L
        if k not in self.cache:
            S = self.S
            if k == 1:
                v = False
            elif k == 2:
                n = len(S["W"])
                v = any((a, b, a) in S["Rset"] and (b, a, b) in S["Rset"] for a in range(n) for b in range(n) if a != b)
            else:
                v = L.unlocking_state(S, L.E.ring(k)) is not None
            self.cache[k] = v
        return self.cache[k]


def one_job(i):
    import shift_lib as L
    h = L.harmonies()[i]
    S = L.setup(h)
    rings = Rings(S)
    rows = []
    for n in ONE:
        for m in ONE:
            if m < n:
                continue
            unl = L.unlocking_state(S, L.one_shift_pattern(n, m)) is not None
            rows.append({"n": n, "m": m, "unlocks": unl, "predicted": rings.unlocks(n) or rings.unlocks(m)})
    return {"i": i, "harmony": L.name(h), "states": len(S["W"]), "rows": rows,
            "rings 3..8 unlock": {k: rings.unlocks(k) for k in ONE}}


def two_cell(L, S, n, m, broad_to):
    """the mixed-knot repeat n x m: locked or not; whether a non-constant state invariant along a short step exists (H0); a state
    invariant along no short step (H0'); stepped states (G2)"""
    Ppat = L.two_shift_pattern(n, m)
    X = L.unlocking_state(S, Ppat)
    row = {"n": n, "m": m, "unlocks": X is not None}
    st = L.stepped_states(S, n, m)
    row["stepped states that are not states"] = sum(1 for Y in st if not L.is_state(S, n, m, Y))
    row["a non-constant stepped state"] = any(len(set(Y)) > 1 for Y in st)
    if X is None:
        row["short"] = False
        return row
    short = True if L.invariances(S, X, n, m, L.short_steps(n, m)) else None
    if n <= broad_to and m <= broad_to:
        Y, rounds = L.broad_state(S, n, m, Ppat)
        row["rounds"] = rounds
        if Y is None:
            row["H0'"] = "every state invariant along a short step"
            short = True
        elif Y == "not settled":
            row["H0'"] = "not settled"
        else:
            row["H0'"] = "a state invariant along no short step"
            row["broad state"] = list(Y)
            row["its values"] = len(set(Y))
            row["its shortest invariant step"] = L.shortest_invariance(S, Y, n, m)
    if short is None:
        Z = L.short_state(S, n, m, Ppat)
        short = "not settled" if Z == "not settled" else Z is not None
    row["short"] = short
    return row


def two_job(arg):
    import shift_lib as L
    i, n = arg
    h = L.harmonies()[i]
    S = L.setup(h)
    rows = [two_cell(L, S, n, m, 9) for m in TWO]
    return {"i": i, "n": n, "harmony": L.name(h), "states": len(S["W"]), "increments": L.increments(S), "rows": rows}


def square_job(arg):
    import shift_lib as L
    i, n = arg
    h = L.harmonies()[i]
    S = L.setup(h)
    t = time.time()
    r = two_cell(L, S, n, n, 12)
    r["seconds"] = round(time.time() - t, 1)
    return {"i": i, "n": n, "harmony": L.name(h), "rows": [r]}


def ringties_job(i):
    import shift_lib as L
    from pysat.solvers import Solver
    h = L.harmonies()[i]
    S = L.setup(h)
    rows = []
    for n in RING_NS:
        Ppat = L.E.ring(n)
        cl, nv, var = L.E.build(Ppat, h, "one order")
        P = S["P"]
        cand = set(range(1, n))
        tied = [0]
        while cand:
            d = min(cand)
            aux, extra, nxt = [], [], nv + 1
            for p in range(P):
                y = nxt
                nxt += 1
                a, b = var(0, p), var(d, p)
                extra += [[-y, a, b], [-y, -a, -b]]
                aux.append(y)
            with Solver(name="cadical153", bootstrap_with=cl + extra + [aux]) as s:
                if s.solve():
                    X = L.decode(S, s.get_model(), var, n)
                    cand = {c for c in cand if X[c] == X[0]}
                else:
                    tied.append(d)
                    cand.discard(d)
        rows.append({"n": n, "tied to copy 0": len(tied), "tied distances": tied[:20]})
    return {"i": i, "harmony": L.name(h), "rows": rows}


def run_part(part):
    import shift_lib as L
    n = len(L.harmonies())
    job = {"one": one_job, "two": two_job, "square": square_job, "ringties": ringties_job}.get(part)
    if part == "control":
        return {"rows": [{"n": k, "dimension": L.ledrappier_kernel_dim(k), "unlocks": L.ledrappier_kernel_dim(k) > 0,
                          "advisor's criterion": L.gf2_polymod_gcd_nontrivial(k),
                          "short-step dimensions": L.ledrappier_short_dims(k)} for k in range(1, 33)]}
    part_dir = HERE / "partial"
    part_dir.mkdir(exist_ok=True)
    if part == "two":
        args = [(i, k) for k in reversed(TWO) for i in range(n)]
    elif part == "square":
        args = [(i, k) for k in reversed(SQUARE) for i in range(n)]
    else:
        args = list(range(n))
    pieces = []
    with Pool(12) as pool:
        for row in pool.imap_unordered(job, args, chunksize=1):
            tag = "%02d" % row["i"] + ("_%02d" % row["n"] if "n" in row else "")
            (part_dir / ("%s_%s.json" % (part, tag))).write_text(json.dumps(row, default=str) + "\n")
            pieces.append(row)
    return {"rows": merge(pieces)}


def merge(pieces):
    """one row per harmony, its cells in order"""
    by = {}
    for p in pieces:
        r = by.setdefault(p["i"], {k: v for k, v in p.items() if k not in ("rows", "n")})
        r.setdefault("rows", []).extend(p.get("rows", []))
    for r in by.values():
        r["rows"].sort(key=lambda x: (x.get("n", 0), x.get("m", 0)))
    return [by[i] for i in sorted(by)]


def load(part):
    return json.loads((HERE / ("result_%s.json" % part)).read_text())["checks"]["result"]["rows"]


def summary():
    out = {}
    referee = {"+".join(r["orbits"]) if isinstance(r["orbits"], list) else r["orbits"]: r
               for r in json.loads((ROOT / "research/LOOP-LOCK-20261112-001/referee-R1/result_rings.json").read_text())["rows"]}
    one = load("one")
    cells = [x for r in one for x in r["rows"]]
    out["G1 unmixed knots: locked exactly when both rings lock"] = [sum(x["unlocks"] == x["predicted"] for x in cells), len(cells)]
    agree = 0
    total = 0
    for r in one:
        ref = referee.get(r["harmony"].replace(" + ", "+"))
        if ref is None:
            continue
        for k, v in r["rings 3..8 unlock"].items():
            total += 1
            agree += (not v) == (int(k) in ref["ring lengths 3..nmax that lock"])
    out["rings 3..8: my locks against the referee's"] = [agree, total]
    two = load("two")
    cells = [(r["harmony"], x) for r in two for x in r["rows"]]
    out["H0 mixed repeats 2..9: unlocks exactly when a non-constant state is invariant along a short step"] = [sum(x["unlocks"] == x["short"] for _, x in cells), len(cells)]
    out["H0 failures (unlocked, no short state)"] = [[h, x["n"], x["m"]] for h, x in cells if x["unlocks"] and x["short"] is False]
    out["H0 not settled"] = [[h, x["n"], x["m"]] for h, x in cells if x["short"] == "not settled"]
    out["G2 stepped states that are not states"] = sum(x["stepped states that are not states"] for _, x in cells)
    out["H0' every state invariant along a short step"] = sum(1 for _, x in cells if x.get("H0'") == "every state invariant along a short step")
    out["H0' a state invariant along no short step"] = [[h, x["n"], x["m"], x.get("its values"), x.get("its shortest invariant step")] for h, x in cells if x.get("H0'") == "a state invariant along no short step"]
    out["H0' not settled"] = [[h, x["n"], x["m"]] for h, x in cells if x.get("H0'") == "not settled"]
    out["harmonies with a state invariant along no short step"] = sorted({h for h, x in cells if x.get("H0'") == "a state invariant along no short step"})
    out["unlocked without a non-constant stepped state"] = len([1 for _, x in cells if x["unlocks"] and not x["a non-constant stepped state"]])
    out["orbits with a graph subgroup (lambda not 0, 1) in their increments"] = [[r["harmony"], o["period"], o["graph subgroups inside (lambda not 0 or 1)"]] for r in two for o in r["increments"] if o["graph subgroups inside (lambda not 0 or 1)"]]
    out["orbits passing the triple test"] = [[r["harmony"], o["period"]] for r in two for o in r["increments"] if o["passes the triple test"]]
    out["single-orbit harmonies passing the triple test: a state invariant along no short step"] = [[r["harmony"], x["n"], x["m"]] for r in two if len(r["increments"]) == 1 and r["increments"][0]["passes the triple test"] for x in r["rows"] if x.get("H0'") == "a state invariant along no short step"]
    out["locked mixed cells"] = [[r["harmony"], [[x["n"], x["m"]] for x in r["rows"] if not x["unlocks"]]] for r in two if any(not x["unlocks"] for x in r["rows"])]
    ringlocked = {r["harmony"] for r in one if not any(r["rings 3..8 unlock"].values())}
    out["harmonies whose rings 3..8 all lock: mixed cells that unlock"] = [[r["harmony"], sum(x["unlocks"] for x in r["rows"])] for r in two if r["harmony"] in ringlocked]
    sq = load("square")
    cells = [(r["harmony"], x) for r in sq for x in r["rows"]]
    out["square H0: n x n, n = 2..16"] = [sum(x["unlocks"] == x["short"] for _, x in cells), len(cells)]
    out["square H0 failures"] = [[h, x["n"]] for h, x in cells if x["unlocks"] and x["short"] is False]
    out["square H0 not settled"] = [[h, x["n"]] for h, x in cells if x["short"] == "not settled"]
    out["square H0' not settled"] = [[h, x["n"]] for h, x in cells if x.get("H0'") == "not settled"]
    out["square locked sizes"] = [[r["harmony"], [x["n"] for x in r["rows"] if not x["unlocks"]]] for r in sq if any(not x["unlocks"] for x in r["rows"])]
    out["square H0' a state invariant along no short step"] = [[h, x["n"], x.get("its shortest invariant step")] for h, x in cells if x.get("H0'") == "a state invariant along no short step"]
    ctl = load("control")
    out["control: rank against the advisor's criterion"] = [sum(x["unlocks"] == x["advisor's criterion"] for x in ctl), len(ctl)]
    out["control: sizes that unlock"] = [x["n"] for x in ctl if x["unlocks"]]
    out["control: the advisor's list to 32"] = [x["n"] for x in ctl if x["unlocks"]] == [3, 6, 7, 9, 12, 14, 15, 18, 21, 24, 27, 28, 30, 31]
    out["control: unlocking sizes with no non-zero state invariant along a short step"] = [x["n"] for x in ctl if x["unlocks"] and max(x["short-step dimensions"].values() or [0]) == 0]
    out["control: unlocking sizes whose states are not all invariant along a short step"] = [x["n"] for x in ctl if x["unlocks"] and x["dimension"] > max(x["short-step dimensions"].values() or [0])]
    rt = load("ringties")
    out["ring ties"] = [[r["harmony"], [[x["n"], x["tied to copy 0"]] for x in r["rows"]]] for r in rt]
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS if (ROOT / p).exists()}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if "--write" in sys.argv:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")


if __name__ == "__main__":
    main()
