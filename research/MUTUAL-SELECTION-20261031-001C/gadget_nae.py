"""Lane C (MUTUAL-SELECTION-20261031-001C): the converse search - gadgets built from signed not-all-equal lines.

If some gadget of signed not-all-equal lines (ports of degree one) accepts exactly the no-lone relation up to port flips and
permutations, then deciding the signed no-lone law on cubic systems reduces to deciding signed not-all-equal on cubic systems, which is
polynomial (a signing is unsolvable iff it is Pfaffian). The catalogue of relations reachable from not-all-equal is recorded too.

Original search description follows.

A gadget has three ports a, b, c (one incidence each inside the gadget) and k internal points (three incidences each), so it has k + 1
lines of three distinct points. With signs on its incidences it accepts a port assignment when some assignment of the internal points
satisfies every line ("no lone one": the signed weight of each line is not 1). If some gadget accepts exactly the weight-one assignments
(up to flipping ports, i.e. up to signs on the port incidences), then cubic positive 1-in-3 SAT (NP-complete, Moore and Robson 2001)
reduces to deciding the signed no-lone law on cubic systems: every variable of the source becomes a point, every clause a gadget.

Run: .venv/bin/python -B gadget.py [--write]"""
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
T0 = time.time()
ONE_IN_THREE = {(1, 0, 0), (0, 1, 0), (0, 0, 1)}


def structures(k, simple=True):
    """incidence structures: k internal points (degree 3) and ports 'a', 'b', 'c' (degree 1) in k + 1 lines of 3 distinct points;
    lines are generated in sorted order to cut symmetric duplicates"""
    pts = list(range(k)) + ['a', 'b', 'c']
    need = {p: (3 if isinstance(p, int) else 1) for p in pts}
    triples = list(itertools.combinations(pts, 3))
    out = []

    def rec(start, chosen, deg):
        if len(chosen) == k + 1:
            if all(deg[p] == need[p] for p in pts):
                out.append(list(chosen))
            return
        for t in range(start if simple else 0, len(triples)):
            tri = triples[t]
            if any(deg[p] + 1 > need[p] for p in tri):
                continue
            if not simple and chosen and t < triples.index(chosen[-1]):
                continue
            for p in tri:
                deg[p] += 1
            chosen.append(tri)
            rec(t + 1 if simple else t, chosen, deg)
            chosen.pop()
            for p in tri:
                deg[p] -= 1
    rec(0, [], {p: 0 for p in pts})
    return out


def masks_for(lines, k):
    """bitsets over the 2^(k+3) joint assignments: per line and sign triple, the satisfying ones; per port assignment, its members"""
    pts = list(range(k)) + ['a', 'b', 'c']
    idx = {p: i for i, p in enumerate(pts)}
    N = 1 << (k + 3)
    line_masks = []
    for l in lines:
        per = {}
        for sg in itertools.product((0, 1), repeat=3):
            m = 0
            for x in range(N):
                if sum(((x >> idx[p]) & 1) ^ s for p, s in zip(l, sg)) in LAW:
                    m |= 1 << x
            per[sg] = m
        line_masks.append(per)
    port_masks = {}
    for ports in itertools.product((0, 1), repeat=3):
        m = 0
        for x in range(N):
            if all(((x >> idx[q]) & 1) == v for q, v in zip(('a', 'b', 'c'), ports)):
                m |= 1 << x
        port_masks[ports] = m
    return line_masks, port_masks


found, tried = [], 0
FLIPS = list(itertools.product((0, 1), repeat=3))
LAW = {1, 2}
NO_LONE = {st for st in itertools.product((0, 1), repeat=3) if sum(st) != 1}
TARGETS = {"no-lone (any port order)": [{tuple(st[perm[i]] ^ f[i] for i in range(3)) for st in NO_LONE} for f in FLIPS
                                        for perm in itertools.permutations(range(3))]}


CANON = {}


def canonical(acc):
    """the accepted set up to port flips and port permutations (memoized)"""
    if acc in CANON:
        return CANON[acc]
    best = None
    for f in FLIPS:
        for perm in itertools.permutations(range(3)):
            key = tuple(sorted(tuple(st[perm[i]] ^ f[i] for i in range(3)) for st in acc))
            best = key if best is None or key < best else best
    CANON[acc] = best
    return best


CATALOGUE = {}
TARGET_SETS = {name: {frozenset(t) for t in tl} for name, tl in TARGETS.items()}
for simple in (True, False):
    for k in range(2, 6):
        structs = structures(k, simple)
        hit = None
        for lines in structs:
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
                tried += 1
                acc = frozenset(pt for pt, pm in port_masks.items() if m & pm)
                key = (simple, k)
                CATALOGUE.setdefault(key, set()).add(canonical(acc))
                for tname, tl in TARGETS.items():
                    if acc in TARGET_SETS[tname]:
                        hit = {"target": tname, "simple lines": simple, "k": k, "lines": [list(map(str, l)) for l in lines],
                               "signs": [list(tuple(sg.get((li, pi), 0) for pi in range(3))) for li in range(len(lines))],
                               "accepted": sorted(acc)}
                        break
                if hit:
                    break
            if hit:
                break
        if hit:
            found.append(hit)
        print(f"simple={simple} k={k}: structures {len(structs)}, gadget {hit['target'] + ' FOUND' if hit else 'none'}, "
              f"achievable relations (up to flips, permutations) {len(CATALOGUE.get((simple, k), ()))}, signings tried {tried}",
              round(time.time() - T0, 1), "s", flush=True)
        if hit:
            break
OUT = {"gadgets found": found, "signings tried": tried, "seconds": round(time.time() - T0, 1),
       "achievable relations": {f"simple={a}, k={b}": sorted(str(list(r)) for r in v) for (a, b), v in CATALOGUE.items()}}
print(json.dumps(found[:2], indent=1))
if "--write" in sys.argv:
    (HERE / "gadget_nae.json").write_text(json.dumps(OUT, indent=1) + "\n")
