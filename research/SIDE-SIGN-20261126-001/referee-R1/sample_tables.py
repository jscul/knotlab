"""Replay the census readings against the compressed per-placement record."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
import gzip
from hashlib import file_digest
import json
from pathlib import Path
import random
import resource
from time import perf_counter

import numpy as np

from blowup_rebuild import distinction_lift, knot_automorphisms, transpositions
from census_rebuild import exchanged_parts, holder_classes
from table_rebuild import GROWTH, allowed_words, forbid, score


HERE = Path(__file__).resolve().parent
ARCHIVE_PATH = HERE.parent / "census_results.jsonl.gz"
LAWS = ("parity", "nae")
READINGS = ("R1", "R2")
GATES = ("placements", "G0", "G1", "G2", "G3")
PRIMARY_INPUTS = tuple(range(100)) + (3097,)
PILOT = (0, 14, 60, 89, 1212, 6765)
ROUND_TWO_SEED = 2026112601
ROUND_TWO_TARGETED = (14, 35, 87, 3097)
WITNESS_TARGETS = {
    (1212, "nae", 1): ((0, 2, 1, 4, 3, 6, 5), "min", (2, 3), (4, 11)),
    (6765, "nae", 2): ((0, 2, 1, 4, 3, 5, 6), "max", (0, 12), (6, 7)),
}


def staged_inputs(starts, selection):
    for start, rounds in sorted(selection.items()):
        for law in LAWS:
            supports = forbid.supports_of(starts[start])
            for depth in range(max(rounds) + 1):
                if depth in rounds:
                    yield (start, law, depth), supports
                if depth < max(rounds):
                    supports, _ = forbid.grow(supports, law, "ordinary", forbid.ENGINE)
                    if supports is None:
                        break


def parity_basis(supports, width):
    pivots = {}
    for support in supports:
        equation = sum(1 << d for d in support)
        while equation and (pivot := equation.bit_length() - 1) in pivots:
            equation ^= pivots[pivot]
        if equation:
            pivots[pivot] = equation
    nonpivots = [d for d in range(width) if d not in pivots]
    basis = []
    for d in nonpivots:
        word = 1 << d
        for pivot, equation in sorted(pivots.items()):
            word |= ((word & equation).bit_count() % 2) << pivot
        basis.append(word)
    return basis


def state_words(supports, width, law):
    if law == "parity":
        basis = parity_basis(supports, width)
        if len(basis) > 23:
            raise ValueError(f"Parity dimension {len(basis)} exceeds this replay's bound")
        words = np.zeros(1 << len(basis), dtype=np.uint64)
        for dimension, word in enumerate(basis):
            size = 1 << dimension
            words[size:2 * size] = words[:size] ^ np.uint64(word)
        return words, len(basis)
    words = np.arange(1 << width, dtype=np.uint64)
    for support in supports:
        mask = np.uint64(sum(1 << d for d in support))
        counts = words & mask
        words = words[(counts != 0) & (counts != mask)]
    return words, width


def representatives(automorphisms):
    involutions = {p for p in automorphisms if any(k != p[k] for k in range(len(p)))
                   and all(p[p[k]] == k for k in range(len(p)))}
    count = len(involutions)
    reps = []
    while involutions:
        rep = min(involutions)
        reps.append(rep)
        for permutation in automorphisms:
            conjugate = [None] * len(rep)
            for k, partner in enumerate(rep):
                conjugate[permutation[k]] = permutation[partner]
            involutions.discard(tuple(conjugate))
    return count, reps


def candidate_settings(classes, owners, knots, action):
    parts = exchanged_parts(classes, knots, action, include_fixed_distinctions=False)
    if parts["invariant_components"]:
        kind = "one"
    elif len(parts["exchanged_components"]) == 1:
        kind = "two"
    else:
        kind = "several"
    sides = sorted([c for pair in parts["exchanged_components"] for c in pair]
                   + parts["invariant_components"])
    if kind == "two":
        # The archived loop visits a shared distinction once per holder.
        columns = tuple(tuple(sorted(d for d, h in owners.items() if set(h) <= set(side) for _ in h))
                        for side in sides)
    else:
        moved = tuple(d for d, image in enumerate(action) if image != d)
        columns = (moved, moved)
    return kind, sides, columns


def placements(candidates, owners):
    left, right = [np.array(list(combinations(col, 2)), dtype=np.intp).reshape(-1, 2)
                   for col in candidates]
    disjoint = np.array([[not set(owners[i]).intersection(owners[j]) for j in range(len(owners))]
                         for i in range(len(owners))])
    available = np.ones((len(left), len(right)), dtype=bool)
    for i, j in product(range(2), repeat=2):
        available &= disjoint[left[:, i, None], right[None, :, j]]
    a, b = np.nonzero(available)
    reads = np.column_stack((left[a], right[b]))
    distinct = (reads[:, 0] != reads[:, 1]) & (reads[:, 2] != reads[:, 3])
    unique_reads = reads[distinct]
    distinct_index = np.zeros(len(reads), dtype=bool)
    if len(unique_reads):
        _, first = np.unique(unique_reads, axis=0, return_index=True)
        distinct_index[np.flatnonzero(distinct)[first]] = True
    return reads, distinct_index


def state_weights(words, action, candidates, kind):
    both_one = np.zeros(len(words), dtype=bool)
    both_zero = both_one.copy()
    unanimous = ~both_one
    opposite = unanimous.copy()
    moved = 0
    pairs = transpositions(action)
    for a, b in pairs:
        left = ((words >> a) & 1).astype(bool)
        right = ((words >> b) & 1).astype(bool)
        both_one ^= left & right
        both_zero ^= ~left & ~right
        unanimous &= left == right
        opposite &= left != right
        moved |= (1 << a) | (1 << b)
    kept = unanimous
    flipped = opposite if 2 * len(pairs) == len(action) else np.zeros(len(words), dtype=bool)
    weights = {
        "U": np.ones(len(words), dtype=np.int8),
        "W1": 1 - 2 * both_one.astype(np.int8),
        "W1c": 1 - 2 * both_zero.astype(np.int8),
    }
    if kept.any():
        weights["W1k"] = weights["W1"] * kept
    if flipped.any():
        weights["W3"] = kept.astype(np.int8) - flipped
    if opposite.any() and not np.array_equal(opposite, flipped):
        weights["W3m"] = kept.astype(np.int8) - opposite
    if kind == "two":
        a, b = [np.bitwise_count(words & np.uint64(sum(1 << d for d in set(side)))).astype(np.int8)
                for side in candidates]
        weights["W2"] = 1 - 2 * (a & b & 1)
        weights["W4"] = np.sign(a - b)
    moved_even = np.bitwise_count(words & np.uint64(moved)) & 1
    fixed = int(kept.sum())
    labels = {
        "N": len(words), "n_S": fixed, "n_A": int(flipped.sum()), "n_A_moved": int(opposite.sum()),
        "pairs": len(pairs), "fixed_distinctions": len(action) - 2 * len(pairs),
        "W1c is plus or minus W1": bool((moved_even == 0).all() or (moved_even == 1).all()),
        "det": (-1) ** ((len(words) - fixed) // 2),
    }
    return weights, labels


def pack(mask):
    return int.from_bytes(np.packbits(mask, bitorder="little").tobytes(), "little")


def pair_counts(distinction_masks, weights, readers, owners):
    positives = pack(weights == 1)
    negatives = pack(weights == -1)
    total = positives.bit_count() - negatives.bit_count()
    present_positive = [(m & positives) for m in distinction_masks]
    present_negative = [(m & negatives) for m in distinction_masks]
    singles = [p.bit_count() - n.bit_count() for p, n in zip(present_positive, present_negative, strict=True)]
    width = len(owners)
    table = np.zeros((width, width, 4), dtype=np.int64)
    for a, b in product(*(sorted(set(col)) for col in readers)):
        if set(owners[a]).intersection(owners[b]):
            continue
        both = ((present_positive[a] & present_positive[b]).bit_count()
                - (present_negative[a] & present_negative[b]).bit_count())
        table[a, b] = (total - singles[a] - singles[b] + both, singles[b] - both, singles[a] - both, both)
    return total, table


def summarize(mask, gates, numerator, denominator, above_two):
    summary = {gate: int(np.count_nonzero(condition & mask)) for gate, condition in zip(GATES, gates, strict=True)}
    summary["hits"] = int(np.count_nonzero(above_two & mask))
    valid = gates[-1] & mask
    best = max((Fraction(int(n), int(d)) for n, d in set(zip(numerator[valid], denominator[valid]))), default=None)
    summary["best"] = str(best) if best is not None else None
    return summary


def evaluate(rows, reads, distinct, reading):
    masses = rows if reading == "R1" else rows * rows
    denominators = masses.sum(axis=2)
    g0 = (denominators != 0).all(axis=1)
    g1 = g0 & ((masses * np.sign(denominators[:, :, None])) >= 0).all(axis=(1, 2))
    g2 = g1 & (denominators == denominators[:, :1]).all(axis=1)
    marginal_left = masses[:, :, 0] + masses[:, :, 1]
    marginal_right = masses[:, :, 0] + masses[:, :, 2]
    g3 = (g2 & (marginal_left[:, 0] == marginal_left[:, 1]) & (marginal_left[:, 2] == marginal_left[:, 3])
          & (marginal_right[:, 0] == marginal_right[:, 2]) & (marginal_right[:, 1] == marginal_right[:, 3]))
    correlation = masses[:, :, 0] + masses[:, :, 3] - masses[:, :, 1] - masses[:, :, 2]
    numerator = np.abs(correlation.sum(axis=1)[:, None] - 2 * correlation).max(axis=1)
    denominator = np.abs(denominators[:, 0])
    above_two = g3 & (numerator > 2 * denominator)
    gates = (np.ones(len(reads), dtype=bool), g0, g1, g2, g3)
    archived = summarize(gates[0], gates, numerator, denominator, above_two)
    deduplicated = summarize(distinct, gates, numerator, denominator, above_two)
    values = {pair: str(Fraction(int(pair[0]), int(pair[1])))
              for pair in set(zip(numerator[above_two], denominator[above_two]))}
    hits = [(*map(int, read), values[n, d]) for read, n, d in
            zip(reads[above_two], numerator[above_two], denominator[above_two], strict=True)]
    return archived, deduplicated, hits


def fibre_witness(supports, words, weights, action, a, b, owners, table):
    # Cross-check the packed two-read counts through the sixteen full-read classes.
    fibres = {"".join(map(str, bits)): Counter() for bits in product(range(2), repeat=4)}
    for word, weight in zip(words, weights, strict=True):
        key = "".join(str((int(word) >> d) & 1) for d in a + b)
        fibres[key][int(weight)] += 1
    counts = {key: {"positive": row[1], "negative": row[-1], "zero": row[0], "sum": row[1] - row[-1]}
              for key, row in fibres.items()}
    raw = []
    per_setting_fibres = []
    for i, j in product(range(2), range(2, 4)):
        by_outcome = {}
        for u, v in product(range(2), repeat=2):
            matching = [row for key, row in counts.items() if int(key[i]) == u and int(key[j]) == v]
            by_outcome[f"{u}{v}"] = {label: sum(row[label] for row in matching)
                                     for label in ("positive", "negative", "zero", "sum")}
        per_setting_fibres.append(by_outcome)
        cells = [row["sum"] for row in by_outcome.values()]
        raw.append(cells)
    assert raw == [table[i, j].tolist() for i, j in product(a, b)]
    squared = [[m * m for m in row] for row in raw]
    assert score(raw) == score(squared) == (5, Fraction(4))
    h_a = {k for d in a for k in owners[d]}
    h_b = {k for d in b for k in owners[d]}
    holders_meet = any(set(supports[i]).intersection(supports[j]) for i, j in product(h_a, h_b))
    return {
        "supports": supports, "distinction_swap": action, "readers": (a, b), "holder_sets": (sorted(h_a), sorted(h_b)),
        "holders_meet": holders_meet, "fibres_in_reader_setting_order": counts,
        "nonzero_states": sum(row["positive"] + row["negative"] for row in counts.values()),
        "mixed_positive_and_negative_fibres": [key for key, row in counts.items() if row["positive"] and row["negative"]],
        "mixed_zero_and_nonzero_fibres": [key for key, row in counts.items()
                                           if row["zero"] and (row["positive"] or row["negative"])],
        "two_distinction_fibres_by_setting_pair": per_setting_fibres,
        "signed_count_outcomes_00_01_10_11": raw,
        "squared_count_outcomes_00_01_10_11": squared,
        "signed_normalizers": list(map(sum, raw)), "squared_normalizers": list(map(sum, squared)), "CHSH_R1_R2": (4, 4),
    }


def compare(expected, actual, key, field, mismatches):
    if expected != actual:
        mismatches.append({"case": key, "field": field, "archive": expected, "replay": actual})


def archive_for(selection):
    with gzip.open(ARCHIVE_PATH, "rt") as stream:
        result = {}
        for line in stream:
            batch = json.loads(line)
            assert batch["status"] == "ok"
            for row in batch["result"]["rows"]:
                i, law, depth = key = row["start"], row["law"], row["round"]
                if depth in selection.get(i, ()):
                    assert key not in result
                    result[key] = row
        return result


def add_summary(aggregate, result):
    aggregate.update({k: result[k] for k in (*GATES, "hits")})
    best = result["best"]
    if best is not None and ("best" not in aggregate or Fraction(best) > Fraction(aggregate["best"])):
        aggregate["best"] = best


def stage_replay(stage_key, supports, reference, comparison, aggregate, witnesses):
    _, law, depth = stage_key
    classes = holder_classes(supports)
    owners = {d: h for h, ds in classes.items() for d in ds}
    width = len(owners)
    automorphisms = knot_automorphisms(len(supports), classes)
    number, reps = representatives(automorphisms)
    mismatch = comparison["mismatches"]
    compare(bool(reference), bool(reps), stage_key, "archived stage with a swap", mismatch)
    if not reference or not reps:
        return "no swap", 0, 0, width
    compare((reference["K"], reference["D"], reference["swaps"], reference["truncated"]),
            (len(supports), width, number, False), stage_key, "knots, distinctions, swaps, truncated", mismatch)
    if law == "nae" and width > 22:
        compare(reference["classes"], "not run: too many states", stage_key, "study state bound", mismatch)
        return "archive state bound", 0, 0, width
    words, dimension = state_words(supports, width, law)
    exact_quadratic_comparison = law == "parity" and dimension > 22
    if width <= 12:
        assert set(allowed_words(supports, law)) == set(words.tolist())
    masks = [pack(((words >> d) & 1).astype(bool)) for d in range(width)]
    archived_classes = {(tuple(row["perm"]), row["lift"]): row for row in reference["classes"]}
    lifted = 0
    for p in reps:
        minimal = distinction_lift(classes, width, p, False)
        maximal = distinction_lift(classes, width, p, True)
        for lift_name, action in (("min", minimal), ("max", maximal)):
            if lift_name == "max" and minimal == maximal:
                continue
            lifted += 1
            key = (*stage_key, p, lift_name)
            expected = archived_classes.pop((p, lift_name), None)
            if expected is None:
                compare(False, True, key, "lift record present", mismatch)
                continue
            kind, sides, candidates = candidate_settings(classes, owners, p, action)
            compare((expected["kind"], expected["sides"], expected["readers"]),
                    (kind, list(map(len, sides)), list(map(len, candidates))), key, "kind, sides, readers", mismatch)
            if any(len(set(c)) != len(c) for c in candidates):
                comparison["lifts_with_repeated_candidate_distinctions"] += 1
            reads, distinct = placements(candidates, owners)
            repeated = (reads[:, 0] == reads[:, 1]) | (reads[:, 2] == reads[:, 3])
            comparison["placement_rows_with_identical_settings"] += int(repeated.sum())
            comparison["extra_placement_rows_with_distinct_settings"] += len(reads) - int(repeated.sum()) - int(distinct.sum())
            weights, labels = state_weights(words, action, candidates, kind)
            if exact_quadratic_comparison:
                weights = {w: masses for w, masses in weights.items() if w in {"U", "W1", "W1c", "W2"}}
            else:
                compare(expected["labels"], labels, key, "state labels", mismatch)
            compare(sorted(expected["weightings"]), sorted(weights), key, "available weightings", mismatch)
            for name, masses in weights.items():
                weight_archive = expected["weightings"].get(name)
                if weight_archive is None:
                    continue
                total, table = pair_counts(masks, masses, candidates, owners)
                compare(weight_archive["Z"], total, (*key, name), "signed normalizer", mismatch)
                a, b, c, d = reads.T
                raw = table[np.column_stack((a, a, b, b)), np.column_stack((c, d, c, d))]
                for reading in READINGS:
                    recorded, dedup, hits = evaluate(raw, reads, distinct, reading)
                    group = (law, depth, name, reading)
                    add_summary(aggregate[group]["archived choices"], recorded)
                    add_summary(aggregate[group]["distinct choices"], dedup)
                    archived = weight_archive[reading]
                    archived_fields = {k: archived[k] for k in (*GATES, "best")}
                    archived_fields["hits"] = len(archived["hits"])
                    compare(archived_fields, recorded, (*key, name, reading), "gates, hit count and maximum", mismatch)
                    actual_hits = [(*a, *b, val) for a, b, val, *_ in archived["hits"]]
                    compare(actual_hits, hits, (*key, name, reading), "ordered hit settings and scores", mismatch)
                    comparison["weighting_reading_rows"] += 1
                    comparison["ordered_hit_rows"] += len(hits)
                    comparison["distinct_hit_rows"] += dedup["hits"]
                    comparison["hit_rows_with_identical_settings"] += sum(a == b or c == d for a, b, c, d, _ in hits)
                    if recorded != dedup:
                        comparison["weighting_reading_rows_changed_by_deduplication"] += 1
                        if recorded["best"] != dedup["best"]:
                            comparison["maximum_changes"].append({"case": (*key, name, reading),
                                                                   "archived": recorded, "distinct": dedup})
                target = WITNESS_TARGETS.get(stage_key)
                if name == "W1k" and target and (p, lift_name) == target[:2]:
                    witness_a, witness_b = target[2:]
                    assert set(witness_a) <= set(candidates[0]) and set(witness_b) <= set(candidates[1])
                    assert all(not set(owners[i]).intersection(owners[j]) for i, j in product(witness_a, witness_b))
                    witness = fibre_witness(supports, words, masses, action, witness_a, witness_b, owners, table)
                    witness["case"] = key
                    for reading in READINGS:
                        assert [list(witness_a), list(witness_b), "4"] in [h[:3] for h in weight_archive[reading]["hits"]]
                    witnesses.append(witness)
    compare([], sorted(archived_classes), stage_key, "unmatched archived lifts", mismatch)
    return "quadratic subset" if exact_quadratic_comparison else "all available signs", lifted, len(words), width


def selection_of(args):
    if args.pilot:
        return {i: (0, 1, 2) for i in PILOT}
    if args.round_two_size is None:
        selection = {i: [0, 1, 2] for i in PRIMARY_INPUTS}
    else:
        selection = {i: [0, 1] for i in PRIMARY_INPUTS}
        remaining = sorted(set(PRIMARY_INPUTS) - set(ROUND_TWO_TARGETED))
        selected = random.Random(ROUND_TWO_SEED).sample(remaining, args.round_two_size)
        for i in (*ROUND_TWO_TARGETED, *selected):
            selection[i].append(2)
    selection.update({1212: [1], 6765: [2]})
    return selection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--round-two-size", type=int, help="Round-two sample size beyond targeted inputs")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    resource.setrlimit(resource.RLIMIT_AS, (2_000_000_000, 2_000_000_000))
    starts = json.loads((GROWTH / "starts.json").read_text())
    selection = selection_of(args)
    start_time = perf_counter()
    archive = archive_for(selection)
    aggregate = defaultdict(lambda: {"archived choices": Counter(), "distinct choices": Counter()})
    comparison = {"mismatches": [], "lifts_with_repeated_candidate_distinctions": 0, "weighting_reading_rows": 0,
                  "placement_rows_with_identical_settings": 0, "extra_placement_rows_with_distinct_settings": 0,
                  "ordered_hit_rows": 0, "distinct_hit_rows": 0, "hit_rows_with_identical_settings": 0,
                  "weighting_reading_rows_changed_by_deduplication": 0, "maximum_changes": []}
    witnesses = []
    cases = []
    for key, supports in staged_inputs(starts, selection):
        t0 = perf_counter()
        result, lifts, words, width = stage_replay(key, supports, archive.pop(key, None), comparison, aggregate, witnesses)
        cases.append({"input": key, "result": result, "lifts": lifts, "allowed_states": words if lifts else None,
                      "distinctions": width, "seconds": round(perf_counter() - t0, 5)})
    assert not archive, list(archive)
    assert {tuple(row["case"][:3]) for row in witnesses} == {key for key in WITNESS_TARGETS if key[0] in selection}
    for columns in aggregate.values():
        for group in columns.values():
            group.setdefault("best", None)
    totals = {"/".join(map(str, key)): columns for key, columns in sorted(aggregate.items())}
    with ARCHIVE_PATH.open("rb") as source:
        checksum = file_digest(source, "sha256").hexdigest()
    result = {
        "archive": ARCHIVE_PATH.name, "archive_sha256": checksum, "start_roster": "FORBID-EDITS-20261126-001/starts.json",
        "method": "Enumerate allowed states and count positive and negative states using packed bit sets. "
                  "Count gate passage and compare all archived hit settings and exact scores. The distinct choices "
                  "count each setting pair once and require two different distinctions per reader.",
        "coverage": {"requested_rounds_by_roster_index": selection,
                     "round_two_seed_if_sampled": ROUND_TWO_SEED if args.round_two_size is not None else None,
                     "cases_per_result": [{"law": law, "round": depth, "outcome_counts": dict(Counter(
                         row["result"] for row in cases if row["input"][1:] == (law, depth)))}
                         for law, depth in product(LAWS, range(3))], "cases_reached": cases},
        "comparison": comparison, "totals": totals, "W1k_witnesses_in_both_readings": witnesses,
        "execution": {"seconds": round(perf_counter() - start_time, 3),
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"coverage": result["coverage"]["cases_per_result"], "comparison": {
        **comparison, "mismatches": comparison["mismatches"][:5], "maximum_changes": comparison["maximum_changes"][:5]},
        "witnesses": [w["case"] for w in witnesses], "execution": result["execution"],
        "slowest": sorted(cases, key=lambda row: -row["seconds"])[:5]}, indent=2))
    if comparison["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
