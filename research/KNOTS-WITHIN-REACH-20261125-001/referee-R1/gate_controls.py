"""Build the supplied count controls and replay the fixed-ration birth control."""

import argparse
from collections import Counter, defaultdict, deque
import gzip
from itertools import combinations, pairwise
import json
from math import comb
import resource
from time import monotonic

from gate_readings import gate, power, recurrence
from gate_recount import ARTIFACTS, HERE, ROOT, TICKET


def holder_steps(stars):
    holders = defaultdict(list)
    for knot, places in enumerate(stars):
        for place in places:
            holders[place].append(knot)
    steps = [set() for _ in stars]
    for knot, places in enumerate(stars):
        for place in places:
            steps[knot].update(other for other in holders[place] if other != knot)
    return steps


def count_steps(neighbors, source, end):
    seen = {source}
    counts = [1]
    next_knots = deque([(source, 0)])
    new_at_step = [0] * (end + 1)
    while next_knots:
        knot, step = next_knots.popleft()
        if step >= end:
            continue
        for next_knot in neighbors[knot]:
            if next_knot not in seen:
                seen.add(next_knot)
                new_at_step[step + 1] += 1
                next_knots.append((next_knot, step + 1))
    for count in new_at_step[1:]:
        counts.append(counts[-1] + count)
    return counts


def six_regular_weave(n):
    stars = []
    for i in range(n):
        for j in range(n):
            u = (i, j)
            v = ((i + 1) % n, j)
            w = (i, (j + 1) % n)
            x = ((i + 1) % n, (j + 1) % n)
            stars.extend([(u, v, w), (v, w, x)])
    return stars


def take_groups(roster, parents):
    """The newest knots meet through their immediately preceding parents."""
    met_sets = defaultdict(set)
    for u in roster:
        for p in parents[u]:
            met_sets[p].add(u)
    neighbors = {u: set().union(*(met_sets[p] for p in parents[u])) - {u} for u in roster}
    groups = []
    used_pairs = set()
    for u in roster:
        successors = sorted(v for v in neighbors[u] if u < v)
        for size in range(2, len(successors) + 1):
            for subset in combinations(successors, size):
                if not all(right in neighbors[left] for left, right in combinations(subset, 2)):
                    continue
                group = (u, *subset)
                if set.intersection(*(parents[v] for v in group)):
                    continue
                if set.intersection(*(neighbors[v] for v in group)):
                    continue
                groups.append(group)
                used_pairs.update(combinations(group, 2))
    groups.extend((u, v) for u in roster for v in sorted(neighbors[u]) if u < v and (u, v) not in used_pairs)
    return groups


def fixed_ration(rounds):
    """L8 from one three-place knot. With release, each roster is the latest births."""
    parents = [set()]
    roster = range(1)
    births = []
    for elapsed in range(rounds):
        groups = take_groups(roster, parents) if elapsed else []
        due = Counter(u for group in groups for u in group)
        assert max(due.values(), default=0) <= 3, (elapsed, "the fixed ration stalled")
        groups.extend((u,) for u in roster for _ in range(3 - due[u]))
        roster = range(len(parents), len(parents) + len(groups))
        parents.extend(map(set, groups))
        births.append(len(roster))
    meetings = [ps.copy() for ps in parents]
    for knot, ps in enumerate(parents):
        for parent in ps:
            meetings[parent].add(knot)
    history = count_steps(meetings, 0, rounds)
    assert births == [comb(t + 2, 2) for t in range(1, rounds + 1)]
    assert history == [comb(r + 3, 3) for r in range(rounds + 1)]
    assert power(births) == (2, 1, 0) and power(history) == (3, 1, 0)
    return {"rounds": rounds, "knots": len(parents), "births": births, "H": history}


def bare_ring(n, rounds):
    """Each member joins its neighbor in the witness order, with no extra birth."""
    neighbors = [set() for _ in range(n * (rounds + 1))]
    for i in range(n):
        neighbors[i].update(((i - 1) % n, (i + 1) % n))
    for t in range(1, rounds + 1):
        for i in range(n):
            knot = t * n + i
            for j in (i, (i + 2) % n):
                parent = (t - 1) * n + j
                neighbors[parent].add(knot)
                neighbors[knot].add(parent)
    return neighbors


def ring_controls(raw_controls, pilot):
    results = {}
    for n_str, original in raw_controls.items():
        n = int(n_str)
        if pilot and n != 33:
            continue
        t_max = 3 * n
        neighbors = bare_ring(n, t_max)
        truncations = 0
        for t in range(n, 2 * n + 1):
            for knot in range(n * t, n * (t + 1)):
                kept = t_max - t
                actual = count_steps(neighbors, knot, kept)
                expected = [2*r*r + 2*r + 1 if r < n else n*(min(r, t) + r + 1) for r in range(kept + 1)]
                assert actual == expected, (n, t, knot)
                truncations += kept > t
        assert truncations == original["made_checked"] - original["made_registered_whole_range"]
        results[n] = {"all eligible made knots": n * (n + 1), "past the knot's birth round": truncations}
    # Check every stored radius for each sampled stage knot by representative of its round.
    with gzip.open(ARTIFACTS / "run2.jsonl.gz", "rt") as rows:
        for line in rows:
            row = json.loads(line)
            if row["kind"] != "bare ring":
                continue
            n = int(row["start"].split("(")[1].split(",")[0])
            if n not in results:
                continue
            results[n]["run2 curves compared"] = 0
            for phase in ("at_T", "at_2T"):
                stage = row[phase]
                neighbors = bare_ring(n, stage["round"])
                representatives = {}
                for knot, counts in stage["H"].items():
                    t = int(knot) // n
                    if t not in representatives:
                        representatives[t] = count_steps(neighbors, n * t, len(counts) - 1)
                    assert representatives[t] == counts, (n, phase, knot)
                results[n]["run2 curves compared"] += len(stage["H"])
    return results


def check(rounds, pilot):
    definitions = ROOT / "research" / TICKET / "named_starts.json"
    supplied = json.loads(definitions.read_text())["controls"]
    recorded = json.loads((ARTIFACTS / "run0_controls.json").read_text())["controls"]
    output = {"L8 from one three-place knot": fixed_ration(rounds)}
    ring = holder_steps(supplied["R_400"])
    ring_curves = {source: count_steps(ring, source, 64) for source in range(len(ring))}
    assert all(H == [2*r+1 for r in range(65)] for H in ring_curves.values())
    output["ring of 400 knots"] = gate(ring_curves, 8, 2)
    assert output["ring of 400 knots"]["j"] == 1 and output["ring of 400 knots"]["range"] == [4, 64]

    tree = holder_steps(supplied["T_12"])
    history = count_steps(tree, 0, 12)
    assert history == recorded["T_12"]["H"] == [3 * 2**r - 2 for r in range(13)]
    increment_reading = recurrence([b - a for a, b in pairwise(history)])
    assert increment_reading == (1, 0, [2])
    output["branching control"] = {"knots": len(tree), "H": history, "S recurrence root": 2}

    weave = six_regular_weave(99)
    neighbors = holder_steps(weave)
    sources = recorded["W_99"]["sources"]
    assert len(sources) == len(set(sources)) == 16
    weave_curves = {source: count_steps(neighbors, source, 32) for source in sources}
    assert all(H == [6*r*r+6*r+1 for r in range(33)] for H in weave_curves.values())
    output["six-regular weave"] = {"knots": len(weave), "distinctions": 99**2, "gate": gate(weave_curves, 8, 2)}
    assert output["six-regular weave"]["gate"]["j"] == 2

    neighbors = holder_steps(supplied["comb_64_64"])
    comb_sources = list(range(64)) + [64 + 64*i + j for i in range(64) for j in (31, 63)]
    comb_curves = {source: count_steps(neighbors, source, 63) for source in comb_sources}
    assert comb_curves[0] == [comb(r + 2, 2) for r in range(64)]
    assert all(comb_curves[64 + 64*i + 63] == list(range(1, 65)) for i in range(64))
    output["comb"] = gate(comb_curves, 8, 2)
    assert output["comb"]["state"] == "no gate"
    output["bare ring growth"] = ring_controls(recorded["bare_rings"], pilot)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=int, metavar="ROUNDS")
    args = parser.parse_args()
    start = monotonic()
    output = check(args.pilot if args.pilot is not None else 65, args.pilot is not None)
    output["execution"] = {"seconds": round(monotonic() - start, 3),
                           "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.pilot is None:
        (HERE / "gate_controls.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(output["execution"])


if __name__ == "__main__":
    main()
