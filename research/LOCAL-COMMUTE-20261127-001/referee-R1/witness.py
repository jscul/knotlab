"""Construct and replay both signed choices in argument A6 of the birth study.

The only growth operation used is the archived ordinary parity round. The
census list is the archived input. Each support and each holder count is
rebuilt from it. Knot and distinction numbers in the output are zero-based.
"""

import argparse
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1] / "FORBID-EDITS-20261126-001"
sys.path.insert(0, str(ARCHIVE))
import forbid


def supports(start):
    count, meetings, loose = start
    knots = [[] for _ in range(count)]
    d = 0
    for a, b, multiplicity in meetings:
        for _ in range(multiplicity):
            knots[a].append(d)
            knots[b].append(d)
            d += 1
    for knot, number in zip(knots, loose, strict=True):
        knot.extend(range(d, d + number))
        d += number
    return tuple(tuple(knot) for knot in knots)


def holders(knots):
    result = defaultdict(list)
    for knot, row in enumerate(knots):
        for d in row:
            result[d].append(knot)
    return dict(result)


def later_closure(start):
    stages = [supports(start)]
    for t in range(1, 5):
        knots, status, births = forbid.grown(stages[-1], "parity", "ordinary")
        if status != "funded" or len(knots) > 40:
            break
        stages.append(knots)
        if all(len(pair) == 2 for pair in holders(knots).values()):
            if t >= 2:
                assert len(births) == 1
                assert births[0]["old_inputs_already_imply_law"]
                return stages
            break
    return None


def meetings(knots):
    """For each meeting, keep all distinctions that support it."""
    linked = [dict() for _ in knots]
    for d, owners in holders(knots).items():
        if len(owners) == 2:
            a, b = owners
            linked[a].setdefault(b, []).append(d)
            linked[b].setdefault(a, []).append(d)
    return linked


def in_one_block(linked, triple):
    """A triple lies in one block iff no single deletion separates its survivors."""
    for missing in range(len(linked)):
        a, *others = [v for v in triple if v != missing]
        reached = {a}
        todo = [a]
        while todo:
            for neighbor in linked[todo.pop()]:
                if neighbor != missing and neighbor not in reached:
                    reached.add(neighbor)
                    todo.append(neighbor)
        if not reached.issuperset(others):
            return False
    return True


def simple_paths(linked, a, b, forbidden):
    """Shortest first, with ties in knot order."""
    todo = deque([(a,)])
    while todo:
        path = todo.popleft()
        if path[-1] == b:
            yield path
            continue
        for knot in sorted(linked[path[-1]]):
            if knot not in path and knot not in forbidden:
                todo.append(path + (knot,))


def cycle_paths(linked, triple):
    """Paths opposite a, b, c, each avoiding the remaining parent."""
    a, b, c = triple
    for ab in simple_paths(linked, a, b, {c}):
        for bc in simple_paths(linked, b, c, set(ab[:-1])):
            ca = next(simple_paths(linked, c, a, set(ab[1:]) | set(bc[:-1])), None)
            if ca is not None:
                return (bc, ca, ab)
    return None


def common_knot_paths(linked, triple):
    """Three arms with no meeting except the common knot."""
    a, b, c = triple
    for common in range(len(linked)):
        if common in triple:
            continue
        for first in simple_paths(linked, a, common, {b, c}):
            for second in simple_paths(linked, b, common, set(first[:-1]) | {c}):
                excluded = set(first[:-1]) | set(second[:-1])
                third = next(simple_paths(linked, c, common, excluded), None)
                if third is not None:
                    return (first, second, third)
    return None


def distinctions_on(linked, paths):
    # One distinction suffices at each meeting with parallel alternatives.
    return [[min(linked[a][b]) for a, b in itertools.pairwise(path)] for path in paths]


def make_choice(spokes, distinctions, form):
    failing = set()
    for i, spoke in enumerate(spokes):
        for j, path in enumerate(distinctions):
            if (form == "cycle" and i == j) or (form == "common knot" and i != j):
                failing.update((spoke, d) for d in path)
    return sorted(failing)


def reorder(knots, failing):
    """Move each second occurrence back to its first occurrence and cancel both."""
    word = [d for knot in knots for d in knot]
    swaps = 0
    while word:
        d = word.pop(0)
        mate = word.index(d)
        swaps += sum(frozenset((d, e)) in failing for e in word[:mate])
        word.pop(mate)
    return -1 if swaps % 2 else 1


def sign_on_state(knot, read):
    """Evaluate the signed check directly on all eight integer amplitudes."""
    # Divide these amplitudes by sqrt(8) for a normalized state.
    original = [(-1) ** (x.bit_count() * (x.bit_count() - 1) // 2) for x in range(8)]
    amplitudes = original.copy()
    for d in reversed(knot):
        change, phase = read[d]
        new = [0] * 8
        for x, amplitude in enumerate(amplitudes):
            sign = -1 if (x & phase).bit_count() % 2 else 1
            new[x ^ change] = sign * amplitude
        amplitudes = new
    if amplitudes == original:
        return 1
    if amplitudes == [-n for n in original]:
        return -1
    return 0


def evaluate(stages, spokes, pairs):
    knots = stages[-1]
    held = [holders(stage) for stage in stages]
    born = {}
    for t, owners in enumerate(held):
        for d in owners:
            born.setdefault(d, t)

    illegal = []
    pair_ages = set()
    holder_counts = set()
    for spoke, older in pairs:
        at = max(born[spoke], born[older])
        a, b = held[at][spoke], held[at][older]
        pair_ages.add((born[spoke], born[older]))
        holder_counts.add((len(a), len(b)))
        if set(a).intersection(b) or max(len(a), len(b)) != 2:
            illegal.append((spoke, older))

    failing = {frozenset(pair) for pair in pairs}
    noncommuting = []
    for i, j in itertools.combinations(range(len(knots)), 2):
        crossings = sum(frozenset((a, b)) in failing for a in knots[i] for b in knots[j])
        if crossings % 2:
            noncommuting.append((i, j))
    within = [[i, a, b] for i, k in enumerate(knots) for a, b in itertools.combinations(k, 2)
              if frozenset((a, b)) in failing]

    # The three closing distinctions act by X on different bits. Each other
    # distinction acts by Z on the bits it fails to commute with. Tensoring
    # each with Z on its own additional bit in state |0> makes all reads
    # distinct and gives each both eigenvalues without changing the checks.
    read = {d: [0, 0] for d in held[-1]}
    for i, spoke in enumerate(spokes):
        read[spoke][0] = 1 << i
    for spoke, older in pairs:
        read[older][1] |= read[spoke][0]
    realized = set()
    for a, b in itertools.combinations(read, 2):
        xa, za = read[a]
        xb, zb = read[b]
        if ((xa & zb) ^ (xb & za)).bit_count() % 2:
            realized.add(frozenset((a, b)))
    assert realized == failing

    return {
        "rounds of the closing and older distinctions in a failing pair": sorted(pair_ages),
        "holder counts for the same ordering at decision": sorted(holder_counts),
        "illegal failing pairs at decision": illegal,
        "failing pairs in a single knot": within,
        "noncommuting knot pairs": noncommuting,
        "reordering sign": reorder(knots, failing),
        "successive checks on the supplied state (0 means it is not an eigenstate)":
            [sign_on_state(knot, read) for knot in knots],
    }


def record(stages, linked, triple, spokes, paths, form):
    distinctions = distinctions_on(linked, paths)
    pairs = make_choice(spokes, distinctions, form)
    result = evaluate(stages, spokes, pairs)
    t = len(stages) - 1
    ages = result["rounds of the closing and older distinctions in a failing pair"]
    assert all(later == t - 1 and earlier < later for later, earlier in ages)
    assert result["holder counts for the same ordering at decision"] == [(1, 2)]
    assert not result["illegal failing pairs at decision"]
    assert not result["failing pairs in a single knot"]
    assert not result["noncommuting knot pairs"]
    assert result["reordering sign"] == -1
    signs = result["successive checks on the supplied state (0 means it is not an eigenstate)"]
    assert signs == [1] * (len(stages[-1]) - 1) + [-1]
    return {
        "form": form,
        "parents in order": triple,
        "closing distinctions in the same order": spokes,
        "paths of knots": paths,
        "distinctions used on those paths": distinctions,
        "failing pairs (closing distinction first)": pairs,
        **result,
    }


def overlapping_control(stages):
    """Read 'three paths ... to one common knot' allowing a repeated last step."""
    # In the four-knot start with a single central knot and two loose
    # distinctions at each other knot, the closing parents are 4, 5 and 6.
    # The first two paths below share their step from knot 1 to knot 0.
    linked = meetings(stages[-2])
    paths = ((4, 1, 0), (5, 1, 0), (6, 2, 0))
    distinctions = distinctions_on(linked, paths)
    spokes = (9, 10, 11)
    pairs = make_choice(spokes, distinctions, "common knot")
    result = evaluate(stages, spokes, pairs)
    assert not result["illegal failing pairs at decision"]
    assert not result["failing pairs in a single knot"]
    assert result["noncommuting knot pairs"]
    return {"census index": 61, "paths of knots": paths, "distinctions on paths": distinctions,
            "failing pairs (closing distinction first)": pairs, **result}


def parallel_control(stages, witness):
    """Take both shared distinctions at a meeting for which the path uses one."""
    linked = meetings(stages[-2])
    paths = witness["paths of knots"]
    distinctions = [[d for a, b in itertools.pairwise(path) for d in linked[a][b]]
                    for path in paths]
    assert distinctions != witness["distinctions used on those paths"]
    spokes = witness["closing distinctions in the same order"]
    pairs = make_choice(spokes, distinctions, witness["form"])
    result = evaluate(stages, spokes, pairs)
    assert not result["illegal failing pairs at decision"]
    assert not result["failing pairs in a single knot"]
    assert result["noncommuting knot pairs"]
    return {"census index": 65, "paths of knots": paths, "distinctions taken at each path": distinctions,
            "failing pairs (closing distinction first)": pairs, **result}


def census(starts):
    outcomes = []
    controls = {}
    all_later = Counter()
    for number, start in enumerate(starts):
        stages = later_closure(start)
        if stages is None:
            continue
        before, closed = stages[-2:]
        assert len(closed) == len(before) + 1
        old_owners = holders(before)
        per_parent = {}
        for d in closed[-1]:
            (parent,) = old_owners[d]
            assert parent not in per_parent
            per_parent[parent] = d
        t = len(stages) - 1
        all_later[t, len(per_parent)] += 1
        linked = meetings(before)
        choices = []
        for triple in itertools.combinations(sorted(per_parent), 3):
            if not in_one_block(linked, triple):
                continue
            spokes = [per_parent[k] for k in triple]
            first = cycle_paths(linked, triple)
            second = common_knot_paths(linked, triple)
            assert first or second
            if first:
                choices.append(record(stages, linked, triple, spokes, first, "cycle"))
            if second:
                choices.append(record(stages, linked, triple, spokes, second, "common knot"))
        if choices:
            added = [stages[0], *[new[len(old):] for old, new in itertools.pairwise(stages)]]
            outcomes.append({"census index": number, "closing round": t, "knots born in each round": added,
                             "closing parents": sorted(per_parent), "constructions": choices})
            if number == 61:
                controls["arms meeting before the common knot"] = overlapping_control(stages)
            if number == 65:
                common = next(case for case in choices if case["form"] == "common knot")
                controls["taking every distinction shared at one path step"] = parallel_control(stages, common)

    forms = Counter(w["form"] for case in outcomes for w in case["constructions"])
    return {
        "starts checked": len(starts),
        "later closures by round and number of closing parents":
            [{"round": t, "parents": p, "closures": n} for (t, p), n in sorted(all_later.items())],
        "closures with three parents in one block": len(outcomes),
        "constructions checked by form": forms,
        "how to read": [
            "The census index refers to the start whose full knot supports appear in the same entry. Knot and distinction numbers start at zero.",
            "Cycle paths are listed opposite each parent. Common-knot paths are listed from each parent to the common knot. Each parent fails with the distinctions on the other two arms.",
            "Only the listed distinction pairs fail. The reordering sign is computed by moving each second occurrence to its first and cancelling them.",
            "For bits x, the supplied state has amplitude (-1)^(x0*x1 + x1*x2 + x2*x0)/sqrt(8). Closing distinction i acts by X on bit i. Every path distinction acts by Z on each bit whose closing distinction it fails with. Each distinction also carries Z on its own additional bit in state |0>.",
            "Checks are in birth order. The final sign belongs to the closing knot. The signs for each earlier round form the corresponding initial part of the list.",
        ],
        "closures": outcomes,
        "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="run a census prefix without writing the full output")
    parser.add_argument("--rebuild-starts", action="store_true", help="also compare the archived roster with its generator")
    args = parser.parse_args()
    starts = json.loads((ARCHIVE / "starts.json").read_text())
    if args.rebuild_starts:
        assert json.loads(json.dumps(forbid.starts())) == starts
    result = census(starts[:args.limit])
    if args.limit is None:
        (HERE / "witnesses.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in
                      {"how to read", "closures", "controls"}}, indent=1))


if __name__ == "__main__":
    main()
