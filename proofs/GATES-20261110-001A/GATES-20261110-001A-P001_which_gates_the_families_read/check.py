#!/usr/bin/env python3
"""Checks for GATES-20261110-001A: which gates the families read (research/GATES-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. For each frozen family (F1, F2, F3, F4, F4') and each network in it (components, three parity names, one top constraint),
the reading O (1 when the network has no satisfying state) in every class pair of the two thin-torus leaves, by SAT; then whether O is a
function of the stored acting bits, and which."""
import hashlib
import itertools
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(NA))
T0 = time.time()
OUT = {}
DEPS = ["proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "research/GATES-20261110-001/preregistration.md"]
TOPS = [("nae", sg) for sg in itertools.product((0, 1), repeat=3)] + [("xor", 0), ("xor", 1)]
NAMES2 = {(0, 0, 0, 0): "0", (0, 0, 0, 1): "AND", (0, 0, 1, 0): "a1 and not a2", (0, 0, 1, 1): "a1", (0, 1, 0, 0): "not a1 and a2",
          (0, 1, 0, 1): "a2", (0, 1, 1, 0): "XOR", (0, 1, 1, 1): "OR", (1, 0, 0, 0): "NOR", (1, 0, 0, 1): "equivalence",
          (1, 0, 1, 0): "not a2", (1, 0, 1, 1): "a1 or not a2", (1, 1, 0, 0): "not a1", (1, 1, 0, 1): "not a1 or a2", (1, 1, 1, 0): "NAND",
          (1, 1, 1, 1): "1"}
NAMES1 = {(0, 0): "0", (0, 1): "a1", (1, 0): "not a1", (1, 1): "1"}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


class CNF:
    def __init__(self):
        self.cl, self.top = [], 0

    def add_space(self, K, s):
        off = self.top
        for i in range(K.n):
            L = [(K.pt[i][k] + 1 + off) * (1 if s[3 * i + k] == 0 else -1) for k in range(3)]
            self.cl += [L, [-a for a in L]]
        self.top += K.n
        return off

    def new(self):
        self.top += 1
        return self.top


def readings(cnf, pairs, triples):
    """O for each (triple, top): 1 when no satisfying state; pairs maps a pair to its name variable"""
    from pysat.solvers import Solver
    out = {}
    with Solver(name="cadical153", bootstrap_with=cnf.cl) as so:
        top = cnf.top
        for tri in triples:
            ys = [pairs[p] for p in tri]
            for t in TOPS:
                top += 1
                sel = top
                if t[0] == "nae":
                    L = [y if b == 0 else -y for y, b in zip(ys, t[1])]
                    so.add_clause([-sel] + L)
                    so.add_clause([-sel] + [-a for a in L])
                else:
                    for bits in itertools.product((0, 1), repeat=3):
                        if sum(bits) % 2 != t[1]:
                            so.add_clause([-sel] + [(-ys[k] if bits[k] else ys[k]) for k in range(3)])
                out[(tri, t)] = int(not so.solve(assumptions=[sel]))
    return out


def define_names(cnf, offs_pts):
    """a name variable for every pair of the given (variable) points"""
    pairs = {}
    for a, b in itertools.combinations(sorted(offs_pts), 2):
        y = cnf.new()
        A, B = a, b
        cnf.cl += [[-y, A, B], [-y, -A, -B], [y, -A, B], [y, A, -B]]
        pairs[(a, b)] = y
    return pairs


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import spaces_lib as SP
    N, SL, A = SP.N, SP.SL, SP.A
    H = A.H
    T = H.Torus(2, 1, 2)
    labs = list(H.LABELS)
    omega = tuple(T.forced[0])
    act = {lab: int(tuple(lab) == omega) for lab in labs}

    def leaf(lab):
        atom = A.Atom((2, 1, 2))
        atom.s = list(T.classes[lab])
        return atom
    S2, s2 = SP.SPH[2].S, SP.SPH[2].s0
    l0, l1 = SP.lines_of(2)
    Hh = H.Torus(2, 0, 2)
    host_s = list(Hh.classes[labs[0]])
    host_line = Hh.K.lines[0]

    def comp_A(kind, lab1):
        """component A of F3 (K_2 with leaf 1) or F4 (the torus (2,0,2) with leaf 1), and its points for names"""
        Y = N.Nested(S2, s2) if kind == "F3" else N.Nested(Hh.S, host_s)
        Y.grow_leaf(Y.where[l0 if kind == "F3" else host_line], leaf(lab1))
        K = Y.K()
        lines, outer, _ = Y.group_parts(K, (0,))
        inner = sorted({K.pt[i][k] for i in lines for k in range(3)} - set(outer))
        pts = (inner + outer) if kind == "F3" else list(range(K.n))
        return K, Y.s, pts

    results, tables = {}, {}
    t1 = time.time()
    # F1
    tab = {}
    for la, lb in itertools.product(labs, labs):
        Y = N.Nested(S2, s2)
        Y.grow_leaf(Y.where[l0], leaf(la))
        Y.grow_leaf(Y.where[l1], leaf(lb))
        tab[(la, lb)] = int(not Y.K().sat(Y.s)[0])
    tables["F1"] = {("none", "none"): tab}
    # F2, F3, F4
    for fam in ("F2", "F3", "F4"):
        per = {}
        for la, lb in itertools.product(labs, labs):
            cnf = CNF()
            if fam == "F2":
                offA = cnf.add_space(T.K, T.classes[la])
                ptsA = [offA + p + 1 for p in range(T.K.n)]
            else:
                KA, sA, pa = comp_A(fam, la)
                offA = cnf.add_space(KA, sA)
                ptsA = [offA + p + 1 for p in pa]
            offB = cnf.add_space(T.K, T.classes[lb])
            ptsB = [offB + p + 1 for p in range(T.K.n)]
            pairs = define_names(cnf, ptsA)
            pairs.update(define_names(cnf, ptsB))
            pA = [p for p in pairs if p[0] in ptsA]
            pB = [p for p in pairs if p[0] in ptsB]
            if fam == "F2":
                triples = [(x, y, z) for x in pA for y in pB for z in pA + pB]
                key = lambda tri: tuple((("A" if p[0] in ptsA else "B"), ptsA.index(p[0]) if p[0] in ptsA else ptsB.index(p[0]),
                                         ptsA.index(p[1]) if p[1] in ptsA else ptsB.index(p[1])) for p in tri)  # noqa: E731
            else:
                triples = [(x, y, z) for i, x in enumerate(pA) for y in pA[i:] for z in pB]
                key = lambda tri: tuple((("A" if p[0] in ptsA else "B"), ptsA.index(p[0]) if p[0] in ptsA else ptsB.index(p[0]),
                                         ptsA.index(p[1]) if p[1] in ptsA else ptsB.index(p[1])) for p in tri)  # noqa: E731
            for (tri, t), o in readings(cnf, pairs, triples).items():
                per.setdefault((key(tri), t), {})[(la, lb)] = o
        tables[fam] = per
        print(round(time.time() - T0, 1), fam, len(per), "networks", flush=True)
    # F4'
    per = {}
    for la in labs:
        cnf = CNF()
        KA, sA, pa = comp_A("F4", la)
        offA = cnf.add_space(KA, sA)
        ptsA = [offA + p + 1 for p in pa]
        pairs = define_names(cnf, ptsA)
        pl = sorted(pairs)
        triples = list(itertools.combinations_with_replacement(pl, 3))
        for (tri, t), o in readings(cnf, pairs, triples).items():
            per.setdefault((tuple((ptsA.index(p[0]), ptsA.index(p[1])) for p in tri), t), {})[la] = o
    tables["F4'"] = per
    print(round(time.time() - T0, 1), "F4'", len(per), "networks", flush=True)
    # classify
    summary = {}
    for fam, per in tables.items():
        funcs, sensitive, p2bad = Counter(), 0, 0
        examples = {}
        for net, tab in per.items():
            if fam == "F4'":
                vals = {}
                for la, o in tab.items():
                    vals.setdefault(act[la], set()).add(o)
                if any(len(v) > 1 for v in vals.values()):
                    sensitive += 1
                    continue
                f = NAMES1[(vals[0].pop(), vals[1].pop())]
            else:
                vals = {}
                for (la, lb), o in tab.items():
                    vals.setdefault((act[la], act[lb]), set()).add(o)
                    # P2: O = 1 wherever a component has no satisfying state
                    unsat_comp = (fam in ("F2", "F3") and (act[la] or act[lb])) or (fam == "F4" and act[lb])
                    if unsat_comp and o != 1:
                        p2bad += 1
                if any(len(v) > 1 for v in vals.values()):
                    sensitive += 1
                    continue
                f = NAMES2[tuple(vals[k].pop() for k in ((0, 0), (0, 1), (1, 0), (1, 1)))]
            funcs[f] += 1
            examples.setdefault(f, str(net))
        summary[fam] = {"networks": len(per), "functions of the acting bits read (networks)": dict(funcs),
                        "networks whose reading depends on more than the acting bits": sensitive, "P2 violations": p2bad, "one example per function": examples}
    check("1 the census: functions of the stored acting bits read by each frozen family", True, {"summary": summary})
    f = lambda fam, name: summary[fam]["functions of the acting bits read (networks)"].get(name, 0) > 0  # noqa: E731
    OUT["predictions"] = {
        "P1: F1 reads AND": summary["F1"]["functions of the acting bits read (networks)"] == {"AND": 1},
        "P2: no violation (O = 1 wherever a component is unsatisfiable)": all(s["P2 violations"] == 0 for s in summary.values()),
        "P3: OR read in F2": f("F2", "OR"), "P3: OR read in F3": f("F3", "OR"),
        "P4: NOT a1 read in F4'": f("F4'", "not a1"),
        "failure line crossed": not (summary["F1"]["functions of the acting bits read (networks)"] == {"AND": 1}) or any(s["P2 violations"] for s in summary.values())}
    print(json.dumps(summary, indent=1, default=str)[:3000], json.dumps(OUT["predictions"], indent=1), flush=True)
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info") if isinstance(old.get(k), dict) and "info" in old.get(k, {}) else old.get(k), sort_keys=True)
                != json.dumps(fresh[k]["info"] if isinstance(fresh[k], dict) and "info" in fresh[k] else fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
