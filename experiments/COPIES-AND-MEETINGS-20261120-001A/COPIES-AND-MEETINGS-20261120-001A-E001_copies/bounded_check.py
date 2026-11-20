"""Bounded physical ancestor profiles and witnessed reading controls."""

from collections import Counter
from itertools import combinations
from pathlib import Path
from random import Random
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = "GENERATORS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_generators")))
from controls import Frame, book, certify_source, check_relabeling, grow, owners_of, ring_stars, supports
from end_operator import End, step

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "bounded_check.json"
LIMITS = {"funded_steps": 9, "live_births_in_step": 512,
          "accumulated_knots": 2048, "distinctions": 16000,
          "enumerate_launch_subsets_at_width_at_most": 12}
LAWS = ("parity", "nae")
ROUTES = {"A": (4, 0, 2, 5), "B": (4, 0, 3, 6)}
ROSTERS = ((0, 4), (4, 6), (4, 5), (0, 2, 3), (3, 6), (2, 5))
BLOCK = {frozenset(pair): (i, len(row)) for i, row in enumerate(ROSTERS)
         for pair in combinations(row, 2)}
DEGREES = Counter(x for pair in BLOCK for x in pair)
SWAP = {0: 0, 4: 4, 2: 3, 3: 2, 5: 6, 6: 5}


def frames_for(stars, law):
    frames = [Frame(stars, {}, {})]
    stop = {"status": "fixed_step_limit"}
    for _ in range(LIMITS["funded_steps"]):
        old = frames[-1]
        planned = step(old.end, law, max_births=LIMITS["live_births_in_step"])
        if planned.status != "extend":
            stop = {"status": planned.status, "next_live_births_lower": planned.planned_births_lower}
            break
        size = book(old)
        if len(old.stars) + len(planned.parents) > LIMITS["accumulated_knots"]:
            stop = {"status": "accumulated_knot_cap"}
            break
        if size["distinct_positions"] + sum(planned.fresh) > LIMITS["distinctions"]:
            stop = {"status": "distinction_cap"}
            break
        frames.append(grow(old, law))
    return frames, stop


def no_smaller(value, other):
    return value if other is None else min(value, other)


def subset_row(width, min_by_exact_ancestor):
    values = [None] * (1 << width)
    for mask, peak in min_by_exact_ancestor.items():
        values[mask] = peak
    for i in range(width):
        bit = 1 << i
        for mask in range(len(values)):
            if mask & bit and values[mask ^ bit] is not None:
                values[mask] = no_smaller(values[mask ^ bit], values[mask])
    hist = Counter(max(mask.bit_count(), peak) for mask, peak in enumerate(values) if peak is not None)
    return {"all_subsets": len(values), "subsets_reaching_horizon": sum(hist.values()),
            "minimum_possible_peak_width_by_subsets": dict(sorted(hist.items()))}


def ancestor_panel(frames):
    live = [tuple(frame.end.opens) for frame in frames]
    all_rows = []
    example = None
    for horizon, targets in enumerate(live):
        # Per target, gather exactly the mandatory holders at every earlier size.
        ancestors = [tuple({v} for v in targets)]
        for age in range(horizon, 0, -1):
            inherited = tuple({p for v in row for p in frames[age].parents[v]}
                              for row in ancestors[-1])
            assert all(row and row <= set(live[age - 1]) for row in inherited)
            ancestors.append(inherited)
        ancestors.reverse()
        peaks = [1] * len(targets)
        by_launch = []
        for launch in reversed(range(horizon + 1)):
            masks = {v: 1 << j for j, v in enumerate(live[launch])}
            widths = []
            minimum_by_mask = {}
            for j, actual in enumerate(ancestors[launch]):
                width = len(actual)
                widths.append(width)
                peaks[j] = max(peaks[j], width)
                mask = sum(masks[v] for v in actual)
                minimum_by_mask[mask] = no_smaller(peaks[j], minimum_by_mask.get(mask))
                gap = peaks[j] - width
                if gap and (example is None or gap > example["peak_excess"]):
                    example = {"launch_age": launch, "horizon_age": horizon,
                               "terminal_scorer_id": targets[j], "terminal_support": frames[horizon].stars[targets[j]],
                               "width_profile": [len(age[j]) for age in ancestors[launch:]],
                               "mandatory_holders_each_size": [sorted(age[j]) for age in ancestors[launch:]],
                               "mandatory_launch_holders": sorted(actual), "peak_excess": gap}
            row = {"launch_age": launch, "launch_width": len(masks),
                   "horizon_births": len(targets), "distinct_exact_launch_sets": len(minimum_by_mask),
                   "launch_only_minimum": min(widths), "all_sizes_minimum_cap": min(peaks),
                   "maximum_mandatory_launch_width": max(widths),
                   "maximum_mandatory_peak_width": max(peaks)}
            if len(masks) <= LIMITS["enumerate_launch_subsets_at_width_at_most"]:
                row.update(subset_row(len(masks), minimum_by_mask))
            by_launch.append(row)
        all_rows.append({"horizon_age": horizon, "launches": sorted(by_launch, key=lambda r: r["launch_age"])})
    return all_rows, example


def inverse_end(end):
    """Attempt to recover a predecessor from full witnessed blocks and positive opens."""
    blocks = list(map(frozenset, end.blocks))
    old_parents = {child: {i for i, block in enumerate(blocks) if child in block}
                   for child in end.opens}
    if any(not group for group in old_parents.values()):
        return None
    unheld = {tuple(q) for group in old_parents.values() for q in combinations(sorted(group), 3)}
    adjacency = {i: set() for i in range(len(blocks))}
    for group in old_parents.values():
        for i, j in combinations(sorted(group), 2):
            adjacency[i].add(j)
            adjacency[j].add(i)
    witnessed = []
    for i, links in adjacency.items():
        for j in links:
            if j <= i:
                continue
            held = [k for k in links & adjacency[j] if tuple(sorted((i, j, k))) not in unheld]
            witnessed.append((i, j, *held))
    return End({i: len(block) for i, block in enumerate(blocks)}, tuple(witnessed))


def inverse_panel(frames):
    rows = []
    for age, (old, frame) in enumerate(zip(frames, frames[1:]), 1):
        previous = old.end
        current = frame.end
        got = inverse_end(current)
        current_labels = list(current.opens)
        recoded_labels = current_labels.copy()
        Random(20261120763 + age).shuffle(recoded_labels)
        recoding = dict(zip(current_labels, recoded_labels, strict=True))
        recoded = End({recoding[v]: h for v, h in current.opens.items()},
                      tuple(tuple(recoding[v] for v in block) for block in current.blocks))
        reconstructed_after_recoding = inverse_end(recoded)
        if got is None:
            assert reconstructed_after_recoding is None
        else:
            trans = {i: recoded.blocks.index(tuple(sorted(recoding[v] for v in group)))
                     for i, group in enumerate(current.blocks)}
            assert reconstructed_after_recoding == End({trans[i]: h for i, h in got.opens.items()},
                                                       tuple(tuple(trans[i] for i in w) for w in got.blocks))
        rosters = {p: tuple(sorted(v for v, parents in frame.parents.items() if p in parents))
                   for p in previous.opens}
        missing = [p for p, group in rosters.items() if group not in current.blocks]
        expected = None
        if not missing:
            to_role = {p: current.blocks.index(group) for p, group in rosters.items()}
            assert len(set(to_role.values())) == len(to_role)
            expected = End({to_role[p]: n for p, n in previous.opens.items()},
                           tuple(tuple(to_role[p] for p in group) for group in previous.blocks))
            assert got == expected, (age, got, expected)
        rows.append({"age": age, "exact_previous_live_supply_and_witnesses": expected is not None,
                     "previous_holders_with_invisible_child_roster": missing,
                     "solely_current_witnessed_end_input": True,
                     "joint_relabeling_verified": True})
    return rows


def peel_origins(stars):
    """Full physical reader on complete cuts of the tested positive families."""
    present = list(enumerate(stars))
    peels = []
    while present:
        ownership = owners_of([star for _, star in present])
        live = {holders[0] for holders in ownership.values() if len(holders) == 1}
        assert live
        if any(set(holders) <= live for holders in ownership.values() if len(holders) == 2):
            return present, peels
        peels.append({present[i][0] for i in live})
        present = [row for i, row in enumerate(present) if i not in live]
    raise AssertionError("no original boundary with live physical meetings")


def check_peeling(frames, stars):
    for age, frame in enumerate(frames):
        rng = Random(20261120779 + age)
        order = list(range(len(frame.stars)))
        rng.shuffle(order)
        bits = sorted(owners_of(frame.stars))
        names = bits.copy()
        rng.shuffle(names)
        renaming = dict(zip(bits, names, strict=True))
        recoded = [tuple(renaming[bit] for bit in frame.stars[i]) for i in order]
        retained, peels = peel_origins(recoded)
        assert len(peels) == age
        assert {order[i] for i, _ in retained} == set(range(len(stars)))
        assert all(star == tuple(renaming[bit] for bit in stars[order[i]]) for i, star in retained)
        assert [{order[i] for i in selection} for selection in peels] == [
            set(old.parents) for old in reversed(frames[1:age + 1])]
    return len(frames)


def canonical_cycle(word):
    return min(seq[i:] + seq[:i] for seq in (word, word[::-1]) for i in range(len(word)))


def shortest_cyclic_words(cap):
    adjacent = {v: sorted(next(iter(edge - {v})) for edge in BLOCK if v in edge)
                for v in DEGREES}
    cycles = set()
    steps = 0

    def walk(path, previous_block):
        nonlocal steps
        steps += 1
        current, start = path[-1], path[0]
        for neighbor in adjacent[current]:
            block = BLOCK[frozenset((current, neighbor))][0]
            if block == previous_block:
                continue
            if neighbor == start and len(path) >= 3 and block != BLOCK[frozenset(path[:2])][0]:
                primitive = all(path != path[:i] * (len(path) // i)
                                for i in range(1, len(path)) if len(path) % i == 0)
                if primitive:
                    cycles.add(canonical_cycle(path))
            if len(path) < cap:
                walk((*path, neighbor), block)

    for origin in adjacent:
        walk((origin,), None)
    by_period = {}
    for width in range(1, cap + 1):
        chosen = sorted(path for path in cycles if len(path) == width)
        by_period[width] = {"point_words_up_to_shift_and_reversal": chosen,
                            "also_quotiented_by_source_exchange": len({
                                min(path, canonical_cycle(tuple(SWAP[x] for x in path))) for path in chosen}),
                            "cumulative_physical_words": sum(len(path) <= width for path in cycles)}
    return {"maximum_period": cap, "finite_walk_prefixes": steps, "counts": by_period}


def phase_data(sequence):
    word = tuple(v for letter in sequence for v in ROUTES[letter])
    p = len(word)
    assert all(word != word[:i] * (p // i) for i in range(1, p) if p % i == 0)

    def window(phase, size):
        return tuple(word[(phase + j) % p] for j in range(size))

    def key(interval):
        return min(interval, interval[::-1])

    def loose(interval):
        traversed = [BLOCK[frozenset(pair)] for pair in zip(interval, interval[1:])]
        assert all(a[0] != b[0] for a, b in zip(traversed, traversed[1:]))
        return sum(DEGREES[v] for v in interval) - sum(size for _, size in traversed)

    cuts = []
    for size in (p, 2 * p, 3 * p):
        keys = [key(window(i, size)) for i in range(p)]
        assert len(set(keys)) == p
        next_keys = [window(i, size + 1) for i in range(p)]
        weights = tuple(loose(window(i, size)) for i in range(p))
        for i, child in enumerate(next_keys):
            assert {key(child[1:]), key(child[:-1])} == {keys[i], keys[(i + 1) % p]}
        maxima = []
        for delay in range(p + 1):
            counts = [len({key(window((i + k) % p, size)) for k in range(delay + 1)})
                      for i in range(p)]
            assert set(counts) == {min(delay + 1, p)}
            maxima.append(counts[0])
        cuts.append({"cluster_size": size, "phase_count": p,
                     "current_phase_cycle_budget_profile": canonical_cycle(weights),
                     "mandatory_launch_width_by_delay": maxima})
    increment = p // 2
    for smaller, larger in zip(cuts, cuts[1:]):
        assert tuple(h + increment for h in smaller["current_phase_cycle_budget_profile"]) == (
            larger["current_phase_cycle_budget_profile"])
    return {"return_word": sequence, "physical_period": p,
            "cost_increase_per_period": increment,
            "word_up_to_reversal_rotation_and_source_exchange": min(
                canonical_cycle(word), canonical_cycle(tuple(SWAP[x] for x in word))),
            "symbolic_cuts": cuts}


def main():
    seven = supports(7, ((0, 1), (0, 1), (0, 4), (1, 4), (2, 4), (2, 6),
                         (3, 4), (3, 5), (5, 6)),
                     (0, 0, 0, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6))
    relay = supports(4, ((0, 1), (0, 2), (0, 3)), (0, 1, 1, 2, 2, 3, 3))
    cases = {}
    for name, stars in (("seven_25", seven), ("bare_five", ring_stars(5)), ("relay_star", relay)):
        row = {"source": certify_source(stars), "laws": {}}
        for law in LAWS:
            frames, stop = frames_for(stars, law)
            ancestry, gap = ancestor_panel(frames)
            inverse = inverse_panel(frames)
            if name in ("seven_25", "bare_five"):
                assert all(x["exact_previous_live_supply_and_witnesses"] for x in inverse), inverse
            if name == "relay_star":
                assert any(not x["exact_previous_live_supply_and_witnesses"] for x in inverse)
            row["laws"][law] = {"stop": stop, "layers": [book(frame) for frame in frames],
                               "profiles": ancestry, "strict_width_gap_example": gap,
                               "inverse_witnessed_end": inverse,
                               "anonymous_physical_origin_peels_verified": check_peeling(frames, stars),
                               "holdings_renaming_verified_through_next_birth": check_relabeling(frames[2], law)}
        assert row["laws"]["parity"] == row["laws"]["nae"]
        cases[name] = row
    finite_words = shortest_cyclic_words(7)
    assert [r["cumulative_physical_words"] for r in finite_words["counts"].values()] == [0, 0, 0, 2, 3, 3, 3]
    phase_words = [phase_data(w) for w in ("AB", "AAB", "AAAB", "AAAAB", "AAABBB", "AABABB")]
    first, second = phase_words[-2:]
    assert first["word_up_to_reversal_rotation_and_source_exchange"] != (
           second["word_up_to_reversal_rotation_and_source_exchange"])
    assert first["symbolic_cuts"] == second["symbolic_cuts"]
    result = {"caps": LIMITS, "literal_cases": cases,
              "primitive_interval_words_seven_25": finite_words,
              "symbolic_interval_factor_checks": phase_words}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
