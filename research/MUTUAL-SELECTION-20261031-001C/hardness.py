"""Lane C (MUTUAL-SELECTION-20261031-001C): the signed Fibonacci law is NP-complete on cubic systems.

1. A constant gadget: a small system of signed no-lone lines with three ports (one incidence each inside) that accepts exactly the port
   assignments with one port at a fixed value (the other two free). Found by search, then verified.
2. An equality line: a no-lone line (a, y, z) in which a is seen as 0 accepts exactly y = z.
3. A full gadget (accepts every port assignment) absorbs spare occurrences.
4. The reduction: any instance of signed no-lone constraints (each variable any number of times; NP-complete by Schaefer, since the
   signed relations are not all 0-valid, 1-valid, Horn, dual-Horn, bijunctive or affine) becomes a cubic system: every variable becomes
   a chain of copies joined by equality lines whose first point is a constant port, each copy carrying one original occurrence; spare
   occurrences go into full gadgets. The script builds the cubic system for random instances and checks that solvability is preserved.
Run: .venv/bin/python -B hardness.py [--write]"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
T0 = time.time()
OUT = {}
src = (HERE / "gadget.py").read_text()
ns = {"__name__": "lib", "__file__": str(HERE / "gadget.py")}
exec(compile(src[:src.index("found, tried = [], 0")], str(HERE / "gadget.py"), "exec"), ns)
structures, masks_for = ns["structures"], ns["masks_for"]


def find_gadget(target_fn, kmax=5):
    """first (simple) gadget whose accepted port set satisfies target_fn"""
    for k in range(2, kmax + 1):
        for lines in structures(k, True):
            line_masks, port_masks = masks_for(lines, k)
            first = {}
            for li, l in enumerate(lines):
                for pi, p in enumerate(l):
                    if isinstance(p, int):
                        first.setdefault(p, (li, pi))
            fixed = set(first.values())
            free = [(li, pi) for li in range(len(lines)) for pi in range(3) if (li, pi) not in fixed]
            for bits in itertools.product((0, 1), repeat=len(free)):
                sg = dict(zip(free, bits))
                m = -1
                for li in range(len(lines)):
                    m &= line_masks[li][tuple(sg.get((li, pi), 0) for pi in range(3))]
                    if not m:
                        break
                acc = {pt for pt, pm in port_masks.items() if m & pm}
                if target_fn(acc):
                    return k, lines, [tuple(sg.get((li, pi), 0) for pi in range(3)) for li in range(len(lines))], sorted(acc)
    return None


def accepted(lines, signs, k):
    acc = set()
    for ports in itertools.product((0, 1), repeat=3):
        for inner in itertools.product((0, 1), repeat=k):
            val = dict(zip(('a', 'b', 'c'), ports))
            val.update(enumerate(inner))
            if all(sum(val[p] ^ s for p, s in zip(l, sg)) != 1 for l, sg in zip(lines, signs)):
                acc.add(ports)
                break
    return acc


ALL = set(itertools.product((0, 1), repeat=3))
FACES = {(i, v): {x for x in ALL if x[i] == v} for i in range(3) for v in (0, 1)}
const = find_gadget(lambda acc: any(acc == F for F in FACES.values()), kmax=4)
CONST_PORT, CONST_VALUE = next(key for key, F in FACES.items() if set(map(tuple, const[3])) == F)
full = find_gadget(lambda acc: len(acc) == 8, kmax=4)
OUT["1 constant gadget (one port forced, the other two free)"] = {
    "k": const[0], "lines": [list(map(str, l)) for l in const[1]], "signs": const[2], "accepted": const[3],
    "forced port and value": ["abc"[CONST_PORT], CONST_VALUE],
    "re-verified by enumeration": accepted(const[1], const[2], const[0]) == FACES[(CONST_PORT, CONST_VALUE)]}
OUT["3 full gadget"] = {"k": full[0], "lines": [list(map(str, l)) for l in full[1]], "signs": full[2],
                        "re-verified": len(accepted(full[1], full[2], full[0])) == 8}
eq_ok = {(y, z) for y in (0, 1) for z in (0, 1) if sum((0, y, z)) != 1} == {(0, 0), (1, 1)}
OUT["2 equality line: no-lone(0, y, z) accepts exactly y = z"] = eq_ok


# ------------------------------------------------------------------------------------------------ the reduction
class Builder:
    """a growing cubic system: lines are (points, signs); every point must end with exactly three incidences"""
    def __init__(self):
        self.lines, self.deg, self.fresh = [], {}, 0

    def point(self, tag):
        self.fresh += 1
        p = (tag, self.fresh)
        self.deg[p] = 0
        return p

    def line(self, pts, signs):
        assert len(set(pts)) == 3
        for p in pts:
            self.deg[p] += 1
            assert self.deg[p] <= 3, p
        self.lines.append((tuple(pts), tuple(signs)))

    def gadget(self, g, ports):
        """instantiate a found gadget with the given three port points"""
        k, glines, gsigns = g[0], g[1], g[2]
        inner = {i: self.point('in') for i in range(k)}
        name = dict(zip(('a', 'b', 'c'), ports))
        name.update(inner)
        for l, sg in zip(glines, gsigns):
            self.line([name[p] for p in l], sg)


def to_cubic(n, constraints):
    """constraints: list of (three variables, three signs) of the signed no-lone law, variables 0..n-1, any number of occurrences"""
    B = Builder()
    occ = {v: [] for v in range(n)}
    for ci, (vs, sg) in enumerate(constraints):
        for j, v in enumerate(vs):
            occ[v].append((ci, j))
    slot_point = {}
    zero_pool = []                                   # free incidences of points forced to 0

    def zero_incidence():
        """an incidence of a point forced to CONST_VALUE; the equality line negates it so that the line sees 0"""
        if not zero_pool:
            ports = [B.point('d'), B.point('d'), B.point('d')]
            B.gadget(const, ports)                   # the port CONST_PORT is forced; the other two are free dummies
            forced = ports[CONST_PORT]
            zero_pool.extend([forced, forced])       # two incidences left
            dummies.extend([q for i, q in enumerate(ports) if i != CONST_PORT for _ in range(2)])
        return zero_pool.pop()

    dummies = []
    for v in range(n):
        copies = [B.point(('v', v)) for _ in range(max(1, len(occ[v])))]
        for x, y in zip(copies, copies[1:]):
            B.line([zero_incidence(), x, y], (CONST_VALUE, 0, 0))   # the forced point is seen as 0, so x = y
        for (ci, j), p in zip(occ[v], copies):
            slot_point[(ci, j)] = p
        # spare incidences of the copies: ends of the chain have one more, a lone copy has three minus its uses
        for p in copies:
            spare = 3 - B.deg[p] - sum(1 for q in slot_point.values() if q == p)
            dummies.extend([p] * spare)
    for ci, (vs, sg) in enumerate(constraints):
        B.line([slot_point[(ci, j)] for j in range(3)], sg)
    dummies.extend(zero_pool)
    zero_pool.clear()
    # absorb the spare incidences with full gadgets: each takes one incidence from three distinct points. With demand d(p) = number of
    # spare incidences of p, add fresh pad points (demand 3) until the total is a multiple of 3 and no demand exceeds total/3; then
    # repeatedly take the three points of largest remaining demand.
    demand = {}
    for p in dummies:
        demand[p] = demand.get(p, 0) + 1
    total = sum(demand.values())
    assert total % 3 == 0, total
    while demand and max(demand.values()) > total // 3:
        demand[B.point('pad')] = 3
        total += 3
    while demand:
        trio = sorted(demand, key=lambda q: (-demand[q], repr(q)))[:3]
        assert len(trio) == 3
        B.gadget(full, trio)
        for q in trio:
            demand[q] -= 1
            if not demand[q]:
                del demand[q]
    return B


def solvable_lines(lines):
    """SAT check: a signed no-lone line on views v_i = x_p xor s_i is the three clauses (not v_i or v_j or v_k)"""
    from pysat.solvers import Minisat22
    pts = sorted({p for l, s in lines for p in l}, key=repr)
    var = {p: i + 1 for i, p in enumerate(pts)}
    with Minisat22() as solver:
        for l, sg in lines:
            lits = [var[p] if t == 0 else -var[p] for p, t in zip(l, sg)]
            for i in range(3):
                j, k = [x for x in range(3) if x != i]
                solver.add_clause([-lits[i], lits[j], lits[k]])
        return solver.solve()


def solvable_direct(n, constraints):
    for x in itertools.product((0, 1), repeat=n):
        if all(sum(x[v] ^ t for v, t in zip(vs, sg)) != 1 for vs, sg in constraints):
            return True
    return False


rng = random.Random(20261031)
agree, sizes, unsat_seen = 0, [], 0
for t in range(60):
    n = rng.randint(3, 6)
    m = rng.randint(2, 9)
    cons = [(tuple(rng.sample(range(n), 3)), tuple(rng.randint(0, 1) for _ in range(3))) for _ in range(m)]
    B = to_cubic(n, cons)
    cubic = all(d == 3 for d in B.deg.values())
    a, b = solvable_direct(n, cons), solvable_lines(B.lines)
    agree += (a == b) and cubic
    unsat_seen += not a
    sizes.append(len(B.lines))
OUT["4 the reduction: random signed no-lone instances (any occurrences) become cubic systems with the same solvability"] = {
    "instances": 60, "agree and cubic": agree, "unsolvable sources among them": unsat_seen, "largest cubic system (lines)": max(sizes)}
ok = (OUT["1 constant gadget (one port forced, the other two free)"]["re-verified by enumeration"] and OUT["3 full gadget"]["re-verified"]
      and eq_ok and agree == 60 and unsat_seen > 0)
OUT["seconds"] = round(time.time() - T0, 1)
print(json.dumps(OUT, indent=1))
print("ALL OK" if ok else "FAIL")
if "--write" in sys.argv:
    (HERE / "hardness.json").write_text(json.dumps(OUT, indent=1) + "\n")
