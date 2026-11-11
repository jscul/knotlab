"""Supplement to OVERLAP-READ-20261111-001A-E001 (after the run; not registered).

1. The frozen census's incomplete_pasch took the complementary triples to be those meeting each Pasch knot in one distinction; they
   are the other four transversals of the three pairs the Pasch never joins. This recomputes C2's six-distinction marks with the
   corrected test (every labeled connected base on 6 distinctions with states and without adjacent apices).
2. The registered failures of P3 and P4, described: the smallest forcing sets found, their sizes, and for P4 the locality radius and
   a greedy forcing set's spread.

Run from the repository root with the workspace .venv; writes research/OVERLAP-READ-20261111-001/supplement.json.
"""
import itertools, json, os, random, sys
from collections import Counter
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "OVERLAP-READ-20261111-001A", "OVERLAP-READ-20261111-001A-E001_emergence_census"))
import census as c  # noqa: E402
c.OUT = os.path.join(ROOT, "research", "OVERLAP-READ-20261111-001", "supplement_scratch")
os.makedirs(c.OUT, exist_ok=True)
ka = c.ka


def pasch_complements(T):
    """Every Pasch among the knots T, with its four complementary transversals."""
    ks = set(frozenset(t) for t in T)
    pts = sorted({v for t in T for v in t})
    out = []
    for six in itertools.combinations(pts, 6):
        sub = [t for t in ks if t <= set(six)]
        for P in itertools.combinations(sub, 4):
            cnt = Counter(v for t in P for v in t)
            if len(cnt) != 6 or any(x != 2 for x in cnt.values()):
                continue
            if any(len(s & t) != 1 for s, t in itertools.combinations(P, 2)):
                continue
            joined = {frozenset(q) for t in P for q in itertools.combinations(sorted(t), 2)}
            anti = [frozenset(q) for q in itertools.combinations(six, 2) if frozenset(q) not in joined]
            if len(anti) != 3:
                continue
            trans = [frozenset(x) for x in itertools.product(*[sorted(a) for a in anti])]
            comp = [t for t in trans if t not in set(P)]
            out.append((P, comp))
    return out


def incomplete_pasch(T):
    ks = set(frozenset(t) for t in T)
    return any(any(t not in ks for t in comp) for _, comp in pasch_complements(T))


def six_marks():
    n = 6
    trip = list(itertools.combinations(range(n), 3))
    tab = Counter()
    for m in range(1, 1 << len(trip)):
        T = [trip[k] for k in range(len(trip)) if (m >> k) & 1]
        if len({v for t in T for v in t}) < n or not ka.connected(n, T) or c.adjacent_apices(T):
            continue
        st = c.states_brute(n, T)
        if len(st) == 0:
            continue
        fr, ti, ex, na = c.emergent_brute(n, T, st)
        f = na and not fr and not ti and not ex
        tab[f"faithful={f} incomplete_pasch={incomplete_pasch(T)}"] += 1
    return dict(tab)


def main():
    out = {"six distinctions, no adjacent apices": six_marks()}
    print(out, flush=True)
    d = json.load(open(os.path.join(ROOT, "artifacts", "OVERLAP-READ-20261111-001A", "OVERLAP-READ-20261111-001A-E001_emergence_census",
                                    "census.json")))
    p3 = d["summary"]["P3"]["failures"]
    desc = []
    for f in p3:
        fs = f["forcing set"]
        V, T = 10, [tuple(t) for t in f["base"]]
        rng = random.Random(1)
        best = None
        for S in c.emergent_brute(V, T, c.states_brute(V, T))[1] + c.emergent_brute(V, T, c.states_brute(V, T))[2]:
            for _ in range(20):
                g = c.greedy_forcing_set(V, T, S, rng)
                if best is None or len(g) < len(best[1]):
                    best = (S, g)
        K = best[1]
        deg = Counter(v for t in K for v in t)
        desc.append({"base knots": len(T), "forcing set": [list(t) for t in K], "S": list(best[0]), "size": len(K),
                     "distinctions": len(deg), "degrees": dict(sorted(Counter(deg.values()).items())),
                     "relation": c.relation(c.states_brute(V, T), best[0])[1]})
    out["P3 failures, 20 greedy orders per emergent set"] = desc
    print(json.dumps(desc)[:2000], flush=True)
    ns = [r for r in d["C3"] if r["family"] == "NAE-SURFACE" and r.get("states") and not r["faithful"]
          and not any(x is not None and x <= 3 for x in r.get("locality radii", []))]
    out["P4 failures"] = [{k: r[k] for k in ("V", "torus", "swaps", "rep", "locality radii", "emergent knots", "ties")} for r in ns]
    print(json.dumps(out["P4 failures"])[:1500], flush=True)
    json.dump(out, open(os.path.join(ROOT, "research", "OVERLAP-READ-20261111-001", "supplement.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
