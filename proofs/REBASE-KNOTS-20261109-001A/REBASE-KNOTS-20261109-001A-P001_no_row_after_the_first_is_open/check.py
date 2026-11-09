#!/usr/bin/env python3
"""Checks for REBASE-KNOTS-20261109-001A: no row after the first is open, so knots cannot be read from the last growth event.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, about a minute. Exact linear algebra over GF(2) on GROW-RUN-20261109-001A's growrun_lib: a cell's value at a lag is a
vector over the born cells, the first row and any band. Read from row t0, a contact c binds ring X at lag T > t0 natively unless c's
value at T, a linear function of row t0, equals on every row t0 the history allows a function of the other cells of row t0: unless the
vector of c at T lies in the span of the vectors of the cells of row t0 that are not X's own cells. Read as if row t0 were open, c binds
X when its row under the fixed network from t0 meets X's own cells."""
import collections
import copy
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIBDIR = ROOT / "proofs/GROW-RUN-20261109-001A/GROW-RUN-20261109-001A-P001_a_band_inserted_while_running_keeps_only_the_knots_it_has_not_reached"
sys.path.insert(0, str(LIBDIR))
import growrun_lib as GR  # noqa: E402

N = GR.N
T0_CLOCK = time.time()
OUT = {}
DEPS = {
    "proofs/GROW-RUN-20261109-001A/GROW-RUN-20261109-001A-P001_a_band_inserted_while_running_keeps_only_the_knots_it_has_not_reached/manifest.json":
        "57f8f58178ab5b3077c2e61c2db89f31713299ccb1cbf78aa27507710951bb91",
    "proofs/GROW-RUN-20261109-001A/GROW-RUN-20261109-001A-P001_a_band_inserted_while_running_keeps_only_the_knots_it_has_not_reached/growrun_lib.py":
        "7a19713eb6eac7a21b5add9ca126b3acd7295e51051c32b658326c19b68c4691",
    "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns/manifest.json":
        "ea82b4fbe792a325ce481430b65203894505095f86c54798973cb5a58d1134e5",
}
SPLITS = ("lower", "upper", "fresh", "copy")


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0_CLOCK, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def reduce(basis, v):
    while v:
        h = v.bit_length() - 1
        if h not in basis:
            return v
        v ^= basis[h]
    return 0


def span(vecs):
    b = {}
    for v in vecs:
        v = reduce(b, v)
        if v:
            b[v.bit_length() - 1] = v
    return b


def apply(row, state):
    v, x = 0, row
    while x:
        low = x & -x
        v ^= state[low.bit_length() - 1]
        x ^= low
    return v


# ---------- check 1: the lemma (every cell is read by exactly two cells, so every later row has even total parity)
def networks():
    sys.path.insert(0, str(ROOT / "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns"))
    import loopnet_lib as LN
    out = []
    for name, (rot, edges) in [("loop of %d" % k, LN.dihedron(k)) for k in (3, 4, 7)] + \
            [("two rings sharing %d" % k, LN.hosohedron(k)) for k in (2, 3, 5)] + \
            [(p, LN.platonic(p)) for p in ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron")] + \
            [("square torus %d" % k, LN.square_torus(k)) for k in (3, 4, 5)] + \
            [("triangular torus 4", LN.triangular_torus(4)), ("honeycomb torus 3", LN.honeycomb_torus(3))]:
        for g in (2, 3, 5):
            sizes, contacts = LN.network(rot, edges, g)
            rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts)
            reads = collections.Counter()
            for row in rows:
                x = row
                while x:
                    low = x & -x
                    reads[low.bit_length() - 1] += 1
                    x ^= low
            total = 0
            for row in rows:
                total ^= row
            out.append((name, g, Nb, total == 0, sorted(set(reads.values()))))
    return out


def tube_ranks():
    res = {}
    for n, m, g in ((3, 3, 2), (3, 4, 2), (4, 4, 2), (3, 3, 3), (5, 4, 2), (3, 8, 2)):
        run = GR.Run(GR.Tube(n, list(range(m)), g))
        ranks = []
        for t in range(1, 9):
            run.step()
            parity = 0
            for s in run.state:
                parity ^= s
            ranks.append((len(span(run.state)), parity == 0))
        res["%d x %d, g = %d" % (n, m, g)] = {"cells": len(run.state), "rank, even parity at lags 1 to 8": ranks}
    return res


# ---------- checks 2 and 3: the two readings from row t0
def readings(n, m, g, t0s, split):
    """{t0: Counter of (as if open, native) verdicts over (contact, ring) pairs}; split None reads the static network"""
    out = {}
    run = GR.Run(GR.Tube(n, list(range(m)), g))
    for t0 in range(max(t0s) + 1):
        if t0 in t0s:
            r2 = copy.deepcopy(run)
            if split is not None:
                r2.insert_band(0, 0.5, split)
            tb, A = r2.tube, r2.state
            own = collections.defaultdict(set)
            for b, k in enumerate(tb.keys):
                if k[0] == 'o':
                    own[k[1]].add(b)
            bases = {R: span([A[b] for b in range(len(A)) if b not in own[R]]) for R in own}
            cnt = collections.Counter()
            for c, (ra, pa, rb, pb, law) in enumerate(tb.contacts):
                seq, T1, p = N.orbit(tb.M, 1 << c, 10 ** 6)
                for R in (tb.rings[ra], tb.rings[rb]):
                    as_open = all(any(row >> b & 1 for b in own[R]) for row in seq)
                    native = all(reduce(bases[R], apply(row, A)) for row in seq)
                    cnt[("as if open: " + ("binds" if as_open else "fails"), "native: " + ("binds" if native else "fails"))] += 1
            out[t0] = {" / ".join(k): v for k, v in sorted(cnt.items())}
        run.step()
    return out


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    nets = networks()
    check("1 Lemma: in every network every cell is read by exactly two cells, so the cells' new values sum to 0 (loops, pairs of rings, "
          "Platonic networks, square, triangular and honeycomb tori; g = 2, 3, 5)",
          all(ok and reads == [2] for name, g, Nb, ok, reads in nets), {"networks": len(nets)})
    ranks = tube_ranks()
    check("1b the rank of the row at lags 1 to 8 on six tubes (at most cells - 1), every row of even parity",
          all(all(p for r, p in v["rank, even parity at lags 1 to 8"]) and all(r < v["cells"] for r, p in v["rank, even parity at lags 1 to 8"])
              for v in ranks.values()), ranks)
    static, grown = {}, {}
    for n, m, g in ((3, 3, 2), (3, 4, 2), (4, 3, 2), (3, 3, 3)):
        static["%d x %d, g = %d" % (n, m, g)] = readings(n, m, g, set(range(0, 8)), None)
        for split in SPLITS:
            grown["%d x %d, g = %d, %s" % (n, m, g, split)] = readings(n, m, g, set(range(0, 8)), split)
    ok_open = all(sum(v for k, v in c.items() if k.startswith("as if open: fails")) == 0 for d in (static, grown) for r in d.values()
                  for c in r.values())
    check("2 Read as if row t0 were open, every contact binds both of its rings at every lag after t0, with a band inserted at t0 or "
          "without (t0 = 0 to 7, four tubes, four splits)", ok_open, {"cases": sum(len(r) for d in (static, grown) for r in d.values())})
    ok_native0 = all(r[0].get("as if open: binds / native: fails", 0) == 0 for d in (static, grown) for r in d.values())
    ok_native_static = all(set(k for k in c) == {"as if open: binds / native: fails"} for r in static.values() for t0, c in r.items() if t0 >= 1)
    check("3 Read natively, binding from the first row holds (t0 = 0), and from any later row of a network that does not grow every "
          "contact fails to bind each of its rings at some lag", ok_native0 and ok_native_static,
          {"static": static, "with a band at t0, lower split": {k: v for k, v in grown.items() if k.endswith("lower")}})
    OUT["3 detail, every split"] = grown
    result = {"ticket": "REBASE-KNOTS-20261109-001A", "artifact_id": "REBASE-KNOTS-20261109-001A-P001", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        return 0
    old = json.loads(path.read_text())
    same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
    print("result.json matches" if same else "result.json differs")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
