"""Check all five ways that three cross pairs can be absent on six separated knots."""
from collections import Counter
from itertools import combinations, permutations
import json

from record_check import HERE, paired


def fixed_case(absent):
    knots = tuple(range(6))
    remaining = set(combinations(knots, 2)) - set(absent)
    cycles = []
    for a, b, c, d in combinations(knots, 4):
        for x, y, z in ((b,c,d),(b,d,c),(c,b,d)):
            cycle = (a,x,y,z)
            if set(paired.walk_data([cycle])) <= remaining:
                cycles.append(cycle)
    cross = [set(paired.walk_data([c])) for c in cycles]
    totals = Counter()
    good = []
    for ids in combinations(range(len(cycles)), 6):
        visits = Counter(p for i in ids for p in cross[i])
        if set(visits) != remaining or set(visits.values()) != {2}:
            continue
        chosen = [cycles[i] for i in ids]
        attachment = paired.paired_reading(chosen, paired.walk_data(chosen).values())
        if attachment["components through attached cross pairs"] != 1 or attachment["knots"] != 6:
            continue
        sign = paired.interleaving(paired.as_terms(chosen), dict(zip(knots,knots)))
        orientable = attachment["orientable"]
        totals[sign,orientable] += 1
        if sign==0 and not orientable:
            good.append(chosen)
    permutations_of_absent = set()
    orbits = set()
    for g in permutations(knots):
        relabelled = {tuple(sorted((g[u],g[v]))) for u,v in absent}
        permutations_of_absent.add(frozenset(relabelled))
        if relabelled != set(absent) or not good:
            continue
        # Every even, non-orientable listing for this fixed complement is
        # compared against the first one under all its allowed relabellings.
        image = [tuple(g[k] for k in cycle) for cycle in good[0]]
        orbits.add(tuple(sorted(tuple(sorted(s)) for s in
                                (paired.walk_data([cycle]) for cycle in image))))
    assert len(orbits) == len(good)
    return {"three absent cross pairs":absent,"four-cycles available":len(cycles),
            "ways to label the absent pairs":len(permutations_of_absent),
            "fixed-case listings by sign and orientation":[[s,o,n] for (s,o),n in sorted(totals.items())],
            "even nonorientable classes":int(bool(good)),"representative":good[:1]}


if __name__ == "__main__":
    missing = [[(0,1),(2,3),(4,5)], [(0,1),(1,2),(3,4)], [(0,1),(1,2),(2,3)],
               [(0,1),(0,2),(0,3)], [(0,1),(0,2),(1,2)]]
    result = [fixed_case(m) for m in missing]
    (HERE/"six_pair_cases.json").write_text(json.dumps(result,indent=2)+"\n")
    print([(r["ways to label the absent pairs"],r["fixed-case listings by sign and orientation"])
           for r in result])
