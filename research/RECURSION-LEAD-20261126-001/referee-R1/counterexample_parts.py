"""A bounded search for two small connected starts that retain two joint class bits."""

import argparse
import json
import resource
from collections import Counter
from itertools import combinations_with_replacement, product
from pathlib import Path
from time import perf_counter

from counterexample import advance, check_stage, columns_of, indices, nine_knots, renumbered
from counterexample_small import shared_generators
from growth import census


def through_three(start):
    stage = start
    for t in range(1, 4):
        stage, status, _ = advance(stage)
        yield t, status, stage
        if status != "funded":
            break


def loose_sets(stage):
    owners = columns_of(stage)
    return [[d for d in sorted(row) if owners[d].bit_count() == 1] for row in stage]


def members(pilot):
    # Include two known positive controls from the frozen 400-start sample.
    # Among the others, choose only starts with a knot holding no loose
    # distinction, as a possible point of attachment for the other start.
    return [(i, stage) for i, stage in enumerate(census()) if len(stage) <= 4
            and (i in (127, 421) or [] in loose_sets(stage))
            and (not pilot or i in (127, 421) or i < 121)]


def join(a, b, port_a, port_b, multiplicity, spent_a, spent_b):
    offset = len(columns_of(a))
    a_bits = loose_sets(a)[port_a]
    b_bits = loose_sets(b)[port_b]
    if spent_a > len(a_bits) or spent_b > len(b_bits):
        return None
    rows = [set(k) for k in a] + [{d + offset for d in k} for k in b]
    rows[port_a].difference_update(a_bits[:spent_a])
    rows[len(a) + port_b].difference_update(d + offset for d in b_bits[:spent_b])
    fresh_id = offset + len(columns_of(b))
    for d in range(fresh_id, fresh_id + multiplicity):
        rows[port_a].add(d)
        rows[len(a) + port_b].add(d)
    renaming = {d: j for j, d in enumerate(sorted(set.union(*rows)))}
    return tuple(frozenset(renaming[d] for d in k) for k in rows)


def classify_bits(source, bit_count):
    by_round = []
    for t, status, stage in through_three(source):
        if status != "funded":
            by_round.append((t, status, None))
            break
        result = shared_generators(stage, min_bits=bit_count)
        by_round.append((t, status, result))
    return by_round


def search(pilot):
    # Include a check capable of detecting a pair in this same search.
    double = nine_knots(True)
    positive = classify_bits(double, 2)
    assert [result is not None for _, _, result in positive] == [False, True, True]
    library = []
    screened = members(pilot)
    screen_counts = Counter()
    for i, source in screened:
        profile = classify_bits(source, 1)
        for t, status, result in profile:
            screen_counts[f"round_{t}_{status}"] += 1
            if result is not None:
                screen_counts[f"round_{t}_positive"] += 1
        found = [t for t, _, row in profile if row is not None]
        if found:
            library.append((i, source, found))
    library.sort(key=lambda entry: (len(entry[1]), entry[0]))
    controls = [x for x in library if x[0] in (127, 421)]
    others = [x for x in library if x[0] not in (127, 421)]
    standins = controls + others[:4]

    counts = Counter()
    candidates = []
    input_candidates = []
    for x, y in combinations_with_replacement(standins, 2):
        for a, b in product(range(len(x[1])), range(len(y[1]))):
            if x[0] == y[0] and a > b:
                continue
            for m in (1, 2):
                for spend_a, spend_b in ((0, 0), (m, m), (0, m), (m, 0)):
                    source = join(x[1], y[1], a, b, m, spend_a, spend_b)
                    if source is None:
                        continue
                    input_candidates.append((x[0], y[0], a, b, m, spend_a, spend_b, source))
    # Lower total distinction counts come first. No prior outcome is used
    # in this ordering, and only the declared number is inspected.
    input_candidates.sort(key=lambda p: (len(columns_of(p[-1])), p[:-1]))
    cap = 12 if pilot else 400
    for x, y, a, b, m, spend_a, spend_b, source in input_candidates[:cap]:
        counts["starts"] += 1
        width = len(columns_of(source))
        if width <= 18:
            counts["starts_with_at_most_18_distinctions"] += 1
        prof = classify_bits(source, 2)
        for t, status, hit in prof:
            counts[f"round_{t}_{status}"] += 1
            if hit is None:
                continue
            labels = hit["shared_independent_labels"]
            stage = next(s for u, _, s in through_three(source) if u == t)
            try:
                certificate = check_stage(stage, labels[:2])
            except ValueError:
                certificate = None
            counts[f"round_{t}_positive"] += 1
            candidates.append({"source_census_indices": [x, y], "joined_holders": [a, b],
                               "new_shared": m, "loose_used": [spend_a, spend_b], "round": t,
                               "source": renumbered(source), "grown": renumbered(stage),
                               "shared_labels_modulo_either_local_span": [list(indices(l)) for l in labels],
                               "shortest": hit["shortest"], "up_to_five": hit["up_to_five"],
                               "certificate": certificate})
    return {
        "weighting": "One count per indicated pair of starts, pair of holders, meeting multiplicity and "
                     "choice of loose distinctions consumed. Renamings can repeat.",
        "nine_knot_positive_control_rounds": [t for t, _, row in positive if row is not None],
        "library_inputs": len(screened), "library_counts": dict(sorted(screen_counts.items())),
        "library_positives": [(i, rounds) for i, _, rounds in library],
        "used_for_joining": [i for i, _, _ in standins], "available_join_specifications": len(input_candidates),
        "join_prefix": cap, "counts": dict(sorted(counts.items())), "positives": candidates,
    }


if __name__ == "__main__":
    cap = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = perf_counter()
    summary = search(args.pilot)
    summary["seconds"] = round(perf_counter() - start, 6)
    summary["peak_resident_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: summary[k] for k in ("library_inputs", "counts", "seconds", "peak_resident_KiB")}))
