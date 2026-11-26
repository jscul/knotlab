"""Match the members of a regrown roster with ordered sums and extra members."""

import argparse
import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from time import monotonic

from regrow_engine import Growth
from regrow_rosters import CHECKS, FAMILY_OF, HERE, TICKET, greatest_counts, reach_counts, stars_of


def mutually_sharing(m):
    stars = [[] for _ in range(m)]
    sharing = list(combinations(range(m), 2))
    for distinction, (left, right) in enumerate(sharing):
        stars[left].append(distinction)
        stars[right].append(distinction)
    next_name = len(sharing)
    for row in stars:
        row.extend((next_name, next_name + 1))
        next_name += 2
    return stars


def steps_from(neighbors, source):
    distance = {source: 0}
    pending = [source]
    for u in pending:
        for v in neighbors[u]:
            if v not in distance:
                distance[v] = distance[u] + 1
                pending.append(v)
    return distance


def recover_matching(neighbors, m, t):
    extra_members = sorted(u for u, adjacent in neighbors.items() if len(adjacent) == 1)
    if len(extra_members) != m:
        return {"matches": False, "extra_members": len(extra_members)}
    steps = [steps_from(neighbors, u) for u in extra_members]
    sum_to_member = {}
    for u in set(neighbors) - set(extra_members):
        # A sum is t - x_i steps from the extra member for term i.
        if any(u not in d for d in steps):
            return {"matches": False, "unreached_member": u}
        earned = tuple(t - d[u] for d in steps)
        if min(earned) < 0 or sum(earned) != t - 1 or earned in sum_to_member:
            return {"matches": False, "invalid_sum": list(earned), "member": u}
        sum_to_member[earned] = u
    expected = math.comb(t + m - 2, m - 1)
    if len(sum_to_member) != expected:
        return {"matches": False, "sums": len(sum_to_member), "expected": expected}
    for counts, u in sum_to_member.items():
        linked = set()
        for source in range(m):
            if counts[source] == 0:
                continue
            for destination in range(m):
                if destination == source:
                    continue
                moved = list(counts)
                moved[source] -= 1
                moved[destination] += 1
                linked.add(sum_to_member[tuple(moved)])
            if counts[source] == t - 1:
                linked.add(extra_members[source])
        if linked != neighbors[u]:
            return {"matches": False, "incorrect_memberships": u}
    return {"matches": True, "sums": expected, "extra_members": m}


def grow(stars, t):
    growth = Growth(stars)
    members = [len(growth.members)]
    for _ in range(t):
        if not growth.step():
            break
        members.append(len(growth.members))
    return growth, members


def first_round_classification(census):
    expected = {
        "six": [1, 1, 1],
        "twelve": [1, 1, 1, 1],
        "thirteen": [1, 1, 1, 2],
        "twenty-two": [1, 1, 1, 2, 2],
    }
    for start, family in FAMILY_OF.items():
        stars = stars_of(census, start)
        growth, _ = grow(stars, 1)
        births = growth.parents[len(stars):]
        joins = [p for p in births if len(p) > 1]
        offshoots = Counter(p[0] for p in births if len(p) == 1)
        counts = sorted(offshoots.values())
        yield {
            "start": start, "stars": stars, "joins": [list(p) for p in joins],
            "offshoot_counts_omitting_zeros": counts,
            "matches_class": len(joins) == 1 and counts == expected[family],
        }


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--pilot", action="store_true")
    args.add_argument("--output", type=Path, default=HERE / "regrow_sum_match.json")
    args = args.parse_args()
    records = json.loads((CHECKS / "roster_probe" / "model_check.json").read_text())
    census = json.loads((TICKET / "census_starts.json").read_text())
    matched = []
    larger = []
    start_time = monotonic()
    for result in records["matching"][:1 if args.pilot else None]:
        m, t = result["m"], result["round"]
        start = result.get("start")
        stars = stars_of(census, start) if start else mutually_sharing(m)
        growth, _ = grow(stars, t)
        neighbors = growth.roster().neighbors
        proof = recover_matching(neighbors, m, t)
        pairs = sum(map(len, neighbors.values())) // 2
        matched.append({
            "start": start, "m": m, "round": growth.round, "members": len(neighbors),
            "one_step_pairs": pairs, "matching": proof,
            "record_agreement": (
                growth.round == t and proof["matches"] == result["the same up to renaming"]
                and len(neighbors) == result["members"]
                and pairs == result.get("one-step pairs", pairs)
            ),
        })
    for result in records["touching starts"][:1 if args.pilot else None]:
        m, t = result["m"], result["rounds done"]
        growth, per_round = grow(mutually_sharing(m), t)
        neighbors = growth.roster().neighbors
        proof = recover_matching(neighbors, m, t)
        degree = max(map(len, neighbors.values()))
        counts = None
        if result["greatest count at each r"] is not None:
            counts = greatest_counts([curve for _, curve in reach_counts(neighbors, sorted(neighbors))])
            counts = counts[:len(result["greatest count at each r"])]
        larger.append({
            "m": m, "round": growth.round, "knots": len(growth.places), "members": len(neighbors),
            "maximum_neighbor_count": degree, "greatest_counts": counts, "matching": proof,
            "record_agreement": (
                growth.round == t and len(growth.places) == result["knots"]
                and per_round[:len(result["members per round"])] == result["members per round"]
                and len(neighbors) == result["members"] and degree == result["most within one step"]
                and counts == result["greatest count at each r"]
            ),
        })
    summary = {
        "matching_stages": matched, "larger_stages": larger,
        "first_round_classification": list(first_round_classification(census)),
        "elapsed_seconds": round(monotonic() - start_time, 3),
    }
    args.output.write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
