"""Referee R1 for MODE-BOND-20261117-001 (own code; the study's growth13.py and joined_census.py are not imported).

  ../../../.venv/bin/python -B referee_mode.py > referee_mode.json      (from this directory)

1. Components, by union-find on the knot triples of the census's pattern(key, N), for the 5 distinct patterns at N = 9, 11, 13:
   the components holding a level-3 address, how many addresses they hold at each level, and whether the orbit that carries the
   non-product link (found by SAT in TWO-ENDS-R1: [3, 7, 9, 15] at level 4 and its line) or any of its descendants lies in them.
2. On the top's components, by SAT at N = 11: for every orbit O at level 3 or 4 inside them and every orbit O' 5 or 6 levels below
   inside its subtree and inside them, whether the joint of O and O' is a product; and, for contrast, the same for the orbits
   outside them.
3. Lemma J's sanity: the two certified bonds of 7 at depth 12 lie inside one component, the top's.
5. The owner's point (b) on composites: the projection of the knots inside O's subtree alone onto O and O' 5 levels below, for O at
   level 3 or 4 and O' both in the top's component: a product?
4. "All 583 decided": the 2,380 small-orbit descriptions of KEEP-REACH grouped into identical clause sets at N = 9, the verdict
   class of each (forgets; two-orbit bond at every s; third class), whether any group mixes classes, and the counts by distinct
   pattern.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CARRIER-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"))
import referee_carrier as C  # noqa: E402  (the referee's own SAT tools, CARRIER-R1)
from pattern import pattern  # noqa: E402

FIVE = ["8db5da810c00-73", "8db5da810c00-76", "8db5da810c00-81", "8db5da810c00-89", "8db5da810c00-100"]


def level_of(a):
    n = 0
    while (1 << (n + 1)) - 1 <= a:
        n += 1
    return n


def components(key, N):
    K = pattern(key, N).tolist()
    nv = (1 << (N + 1)) - 1
    par = list(range(nv))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for a, b, c in K:
        for x, y in ((a, b), (a, c)):
            rx, ry = find(x), find(y)
            if rx != ry:
                par[rx] = ry
    return find


def part1():
    out = {}
    for idx in FIVE:
        key = C.THIRD[idx]["key"]
        rows = {}
        for N in (9, 11, 13):
            find = components(key, N)
            top = {find(C.vid(3, y)) for y in range(8)}
            per_level = [sum(1 for y in range(1 << n) if find(C.vid(n, y)) in top) for n in range(N + 1)]
            line = [(4, [3, 7, 9, 15])]
            carried_in_top = any(find(C.vid(4, y)) in top for y in (3, 7, 9, 15))
            desc_in_top = sum(1 for n in range(5, N + 1) for y in range(1 << n)
                              if (y >> (n - 4)) in (3, 7, 9, 15) and find(C.vid(n, y)) in top)
            rows[N] = {"components_with_level3": len(top), "top_addresses_by_level": per_level,
                       "carried_orbit_in_top": carried_in_top, "its_descendants_in_top": desc_in_top}
        out[idx] = rows
        print("part1", idx, json.dumps(rows), file=sys.stderr, flush=True)
    return out


def part2(N=11):
    out = {}
    for idx in FIVE:
        P = C.Pattern(idx, N)
        find = components(P.key, N)
        top = {find(C.vid(3, y)) for y in range(8)}
        intop = lambda n, O: all(find(C.vid(n, y)) in top for y in O)
        res = Counter()
        nonprod_outside = 0
        for j in (3, 4):
            for O in P.orb[j]:
                for d in (5, 6):
                    lv = j + d
                    if lv > N:
                        continue
                    sub = {(u << d) | t for u in O for t in range(1 << d)}
                    for O2 in P.orb[lv]:
                        if not set(O2) <= sub:
                            continue
                        both_top = intop(j, O) and intop(lv, O2)
                        if not both_top and j == 3:
                            continue
                        vars_ = [C.vid(j, u) for u in O] + [C.vid(lv, v) for v in O2]
                        proj = {int(r) for r in P.project(vars_)}
                        m = len(O)
                        A = {r & ((1 << m) - 1) for r in proj}
                        B = {r >> m for r in proj}
                        prod = len(proj) == len(A) * len(B)
                        if both_top:
                            res["top: product" if prod else "top: NOT product"] += 1
                        else:
                            res["outside: product" if prod else "outside: not product"] += 1
        out[idx] = dict(res)
        print("part2", idx, json.dumps(out[idx]), file=sys.stderr, flush=True)
    return out


def part3():
    cert = json.load(open(ROOT / "research/CARRIER-20261117-001/threshold_deep_8db5da810c00-79_N12_c7.json"))
    find = components(C.THIRD["8db5da810c00-73"]["key"], 12)
    top = {find(C.vid(3, y)) for y in range(8)}
    return [{"s": c["s"], "bond": c["bond"], "one_component": len({find(v) for v in c["bond"]}) == 1,
             "in_top_component": all(find(v) in top for v in c["bond"])} for c in cert["cells"]]


def part4():
    KR = ROOT / "research/KEEP-REACH-20261117-001"
    rows = [json.loads(l) for f in ("sample_keep.jsonl", "mutants_keep.jsonl") for l in open(KR / f)]
    alive = [r for r in rows if r.get("small_orbits") and r.get("alive_every_depth")]
    third = {v["key"] and json.dumps(v["key"]): k for k, v in C.THIRD.items()}

    def cls(r):
        if r.get("r_all") is not None:
            return "forgets (Theorem F)"
        if r.get("two_orbit_every_s"):
            return "two-orbit bond at every s (Theorem K)"
        return "third class"
    g = defaultdict(list)
    for r in alive:
        g[frozenset(tuple(sorted(t)) for t in pattern(r["key"], 9).tolist())].append(cls(r))
    mixed = sum(1 for v in g.values() if len(set(v)) > 1)
    return {"descriptions": len(alive), "distinct": len(g), "groups_with_mixed_classes": mixed,
            "descriptions_by_class": dict(Counter(cls(r) for r in alive)),
            "distinct_by_class": dict(Counter(v[0] for v in g.values()))}


def part5(N=11):
    """The owner's point (b), directly on composites: for O at level 3 or 4 in the top's component and O' 5 levels below in its
    subtree and in the top's component, the projection onto (O, O') of the knots inside O's subtree alone (every other branch of the
    subtree quantified, nothing above O).  That is the saturated composite; is it a product?"""
    from pysat.solvers import Cadical195
    out = {}
    for idx in FIVE:
        key = C.THIRD[idx]["key"]
        K = pattern(key, N).tolist()
        find = components(key, N)
        top = {find(C.vid(3, y)) for y in range(8)}
        orb = {n: C.orbits(key, n) for n in range(N + 1)}
        res = Counter()
        for j in (3, 4):
            for O in orb[j]:
                if not all(find(C.vid(j, y)) in top for y in O):
                    continue
                d = 5
                lv = j + d
                desc = lambda a: any((a - ((1 << n) - 1)) >> (n - j) in set(O) for n in range(j, N + 1)
                                     if (1 << n) - 1 <= a < (1 << (n + 1)) - 1)
                cl = [t for t in K if all(desc(x) for x in t)]
                sub = {(u << d) | t for u in O for t in range(1 << d)}
                for O2 in orb[lv]:
                    if not set(O2) <= sub or not all(find(C.vid(lv, y)) in top for y in O2):
                        continue
                    vars_ = [C.vid(j, u) for u in O] + [C.vid(lv, v) for v in O2]
                    clauses = [[a + 1, b + 1, c + 1] for a, b, c in cl] + [[-(a + 1), -(b + 1), -(c + 1)] for a, b, c in cl]
                    rows = set()
                    with Cadical195(bootstrap_with=clauses) as S:
                        for v in vars_:
                            S.add_clause([v + 1, -(v + 1)])
                        while S.solve():
                            m = S.get_model()
                            bits = [1 if m[v] > 0 else 0 for v in vars_]
                            rows.add(sum(b << i for i, b in enumerate(bits)))
                            S.add_clause([-(v + 1) if b else (v + 1) for v, b in zip(vars_, bits)])
                    mm = len(O)
                    A = {r & ((1 << mm) - 1) for r in rows}
                    B = {r >> mm for r in rows}
                    res["product" if len(rows) == len(A) * len(B) else "NOT product"] += 1
        out[idx] = dict(res)
        print("part5", idx, json.dumps(out[idx]), file=sys.stderr, flush=True)
    return out


def main():
    out = {"1_components": part1(), "3_bonds_of_7_in_one_component": part3(), "4_population": part4()}
    print("part3/4 done", file=sys.stderr, flush=True)
    out["2_pair_joints_N11"] = part2()
    out["5_composites_on_the_top_component_N11"] = part5()
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
