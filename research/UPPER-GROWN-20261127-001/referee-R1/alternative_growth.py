"""Check the ordinary birth and agreement relations on a chosen open start."""

import argparse
from collections import Counter
import contextlib
from functools import reduce
import io
import json
from itertools import combinations, product
from operator import and_
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/NAE-LAYER-20261127-001/referee-R1"))
sys.path.insert(0, str(ROOT / "tools"))
from growth_rule import advance
from knotlab.cli import main as check_knot


# The twelve-knot start in the previous referee's layer_notes.md, with
# its first law removed and variable 1 at its other occurrence renamed 0.
START = ((0, 2, 9), (3, 4, 8), (4, 5, 11), (6, 7, 12), (7, 8, 15),
         (9, 10, 14), (10, 11, 17), (12, 13, 0), (13, 14, 3),
         (15, 16, 2), (16, 17, 5))
CARRIERS = ((0, 2, 18, 19), (3, 4, 5), (6, 7, 8), (9, 10, 11),
            (12, 13, 14), (15, 16, 17))
TRIPLES = tuple(product((0, 1), (2, 3), (4, 5)))


def stage_and_readings(exact):
    if exact:
        start = ((1, 2, 9), *START[1:])
        carriers = ((0, 1, 2, 18), CARRIERS[1], (6, 7, 8, 19), *CARRIERS[3:])
        expected = [((0,), (1,), 0, (18, 19)), ((3,), (6,), 0, (20, 21)),
                    ((7,), (0,), 0, (22, 23))]
    else:
        start, carriers = START, CARRIERS
        expected = [((3,), (6,), 0, (18, 19))]
    before = Counter(x for law in start for x in law)
    expected_loose = {birth[1][0]: 1 for birth in expected}
    assert {x: count for x, count in before.items() if count != 2} == expected_loose
    result = advance(start)
    assert result.status == "funded"
    assert [(b.parents, b.inputs, b.demand, b.fresh) for b in result.births] == expected
    assert result.supports == start + tuple(inputs + fresh for _, inputs, _, fresh in expected)
    return start, result.supports, carriers, expected


def columns(labels, prefix=None):
    labels = sorted(labels)
    count = 1 << len(labels) if prefix is None else min(prefix, 1 << len(labels))
    universe = (1 << count) - 1
    masks = {}
    for index, key in enumerate(labels):
        width = 1 << index
        size = min(width, max(0, count - width))
        mask = ((1 << size) - 1) << width
        offset = width * 2
        while offset < count:
            mask |= mask << offset
            offset *= 2
        masks[key] = mask & universe
    return universe, masks


def agreement(labels, values, universe):
    ones = reduce(and_, (values[x] for x in labels), universe)
    zeros = reduce(and_, (universe ^ values[x] for x in labels), universe)
    return ones | zeros


def cells(allowed, readings):
    current = {"": allowed}
    for reading in readings:
        updated = {}
        for prefix, rows in current.items():
            for bit, members in (("0", rows & ~reading), ("1", rows & reading)):
                if members:
                    updated[prefix + bit] = members
        current = updated
    return current


def forget(allowed, indices):
    return sorted({"".join(word[i] for i in indices) for word in allowed})


def upper(word):
    return "".join(str(int(word[i] == word[i + 1])) for i in (0, 2, 4))


def source_data(laws, prefix=None, carriers=CARRIERS):
    labels = sorted({x for law in laws for x in law})
    universe, values = columns(labels, prefix)
    law_masks = [universe ^ agreement(law, values, universe) for law in laws]
    allowed = reduce(and_, law_masks, universe)
    lower = [agreement(c, values, universe) for c in carriers]
    upper_cols = [universe ^ (lower[i] ^ lower[i + 1]) for i in (0, 2, 4)]
    return labels, universe, values, law_masks, allowed, lower, upper_cols


def mixed(allowed, places, readings):
    fixed = cells(allowed, places)
    return [sum(bool(rows & reading) and bool(rows & ~reading) for rows in fixed.values())
            for reading in readings]


def cnf_check(cnf, witnesses=()):
    reports = []
    for contact in "PQR":
        loops = [place for place in "PQR" if place != contact]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = check_knot(["check", "--cnf", cnf, "--loops", *loops,
                                 "--contact", contact, "--witnesses", *witnesses, "--json"])
        report = json.loads(out.getvalue())
        assert status == 0 and report["is_knot"]
        reports.append({k: report[k] for k in ("variables", "allowed", "is_knot")})
    return reports


def cnf_with_readings():
    names = ("A0", "A1", "B0", "B1", "C0", "C1")
    parts = [" ".join("~" + names[i] for i in triple) for triple in TRIPLES]
    for i, out in enumerate("PQR"):
        for a, b in product((0, 1), repeat=2):
            rejected = (a, b, int(a != b))
            places = (*names[2*i:2*i + 2], out)
            parts.append(" ".join(("~" if v else "") + name for name, v in zip(places, rejected)))
    return "; ".join(parts), names


def checksum_of_prefix(laws, prefix, carriers):
    labels, _, _, _, allowed, lower, _ = source_data(laws, prefix, carriers)
    literal = Counter()
    for assignment in range(prefix):
        raw = {x: (assignment >> i) & 1 for i, x in enumerate(labels)}
        if all(len({raw[x] for x in law}) >= 2 for law in laws):
            literal["".join(str(int(len({raw[x] for x in c}) == 1)) for c in carriers)] += 1
    assert literal == {w: rows.bit_count() for w, rows in cells(allowed, lower).items()}
    return {"assignments": prefix, "allowed_source_states": sum(literal.values()),
            "lower_words": len(literal)}


def analyze(exact):
    start, laws, carriers, births = stage_and_readings(exact)
    labels, universe, values, obey, allowed, lower, upper_cols = source_data(laws, carriers=carriers)
    used = set().union(*map(set, carriers))
    assert len(used) == sum(map(len, carriers)) and used.issubset(labels)
    reached = {0}
    while True:
        more = reached | {j for j, law in enumerate(laws) if any(set(law) & set(laws[r]) for r in reached)}
        if more == reached:
            break
        reached = more
    assert len(reached) == len(laws)

    counts = {word: rows.bit_count() for word, rows in cells(allowed, lower).items()}
    lower_words = sorted(counts)
    all_words = ["".join(w) for w in product("01", repeat=6)]
    presented = [w for w in all_words if all(any(w[i] == "0" for i in triple) for triple in TRIPLES)]
    assert all(w in presented for w in lower_words)
    source_upper = sorted(map(str, cells(allowed, upper_cols)))
    assert source_upper == sorted({upper(w) for w in presented}) == [f"{k:03b}" for k in range(1, 8)]

    lower_checks = {}
    deletion_sources = {}
    omitted_masks = [reduce(and_, obey[:j] + obey[j+1:], universe) for j in range(len(laws))]
    other_nonfull = {}
    for triple in combinations(range(6), 3):
        image = forget(lower_words, triple)
        if triple in TRIPLES:
            assert image == [f"{k:03b}" for k in range(7)]
            missing = [w for w in all_words if all(w[i] == "1" for i in triple) and
                       all(any(w[i] == "0" for i in t) for t in TRIPLES if t != triple)]
            assert {upper(w) for w in missing} == {"000"}
            delete_law = [j for j, rows in enumerate(omitted_masks) if
                          rows & lower[triple[0]] & lower[triple[1]] & lower[triple[2]]]
            deletion_sources[str(triple)] = delete_law
            lower_checks[str(triple)] = {"allowed": image, "additional_words_on_lower_deletion": missing}
        elif len(image) != 8:
            other_nonfull[str(triple)] = image

    lower_mixed = [mixed(allowed, [values[x] for x in law], lower) for law in laws]
    assert all(all(tally) for tally in lower_mixed)
    lower_changes = []
    for parts, reading in zip(carriers, lower):
        changes = []
        for x in parts:
            shift = 1 << labels.index(x)
            both = allowed & ~values[x] & (allowed >> shift)
            changes.append((both & (reading ^ (reading >> shift))).bit_count())
        assert all(changes)
        lower_changes.append(changes)

    upper_mixed = {}
    for triple in TRIPLES:
        key = str(triple)
        by_source = mixed(allowed, [lower[i] for i in triple], upper_cols)
        by_conjunction = []
        for p in range(3):
            fixed = {key: set() for key in forget(presented, triple)}
            for word in presented:
                fixed["".join(word[i] for i in triple)].add(upper(word)[p])
            by_conjunction.append(sum(len(poss) == 2 for poss in fixed.values()))
        assert all(by_source) and all(by_conjunction)
        upper_mixed[key] = {"on_source": by_source, "on_lower_conjunction": by_conjunction}

    upper000_rows = universe & ~upper_cols[0] & ~upper_cols[1] & ~upper_cols[2]
    deletion = []
    for j, rows in enumerate(omitted_masks):
        restored = upper000_rows & rows
        witness = None
        lower_word = None
        if restored:
            index = (restored & -restored).bit_length() - 1
            witness = "".join(str((index >> i) & 1) for i in range(len(labels)))
            lower_word = "".join(str(int(bool(read & (1 << index)))) for read in lower)
        deletion.append({"omitted_law": j, "restored_000_source_states": restored.bit_count(),
                         "witness_in_label_order": witness, "lower_word_at_witness": lower_word})
    assert deletion[len(start)]["restored_000_source_states"]

    short = []
    for i, carrier in enumerate(carriers):
        if len(carrier) != 4:
            continue
        for size in (2, 3):
            for parts in combinations(carrier, size):
                reduced = lower.copy()
                reduced[i] = agreement(parts, values, universe)
                reduced_top = [universe ^ (reduced[k] ^ reduced[k+1]) for k in (0, 2, 4)]
                short.append({"reading": i, "carrier": parts, "upper_image": sorted(cells(allowed, reduced_top))})

    upper_cnf, names = cnf_with_readings()
    origin = "Previous twelve-knot witness with (0,1,6) removed"
    if not exact:
        origin += " and old 1 identified with old 0"
    return {"source_of_start": origin, "start": start, "selected_birth_index": len(start),
            "births": [{"parents": p, "input": x, "demand": d, "fresh": f} for p, x, d, f in births],
            "all_laws": laws, "labels_for_source_words": labels, "carriers": carriers,
            "source_states_tested": 1 << len(labels), "allowed_source_states": allowed.bit_count(),
            "number_of_lower_words": len(lower_words), "lower_word_counts": counts,
            "number_of_words_from_eight_lower_laws": len(presented),
            "same_six_reading_image": lower_words == presented, "upper_image": source_upper,
            "lower_laws": lower_checks, "other_nonfull_triples_on_the_six_readings": other_nonfull,
            "source_law_deletions_breaking_each_lower_law": deletion_sources,
            "source_law_fixes_leaving_both_values_by_lower_reading": lower_mixed,
            "allowed_single_changes_by_reading_and_member": lower_changes,
            "lower_law_fixes_leaving_both_values_by_upper_reading": upper_mixed,
            "source_single_law_deletions": deletion, "shorten_each_four_place_carrier_on_its_own": short,
            "canonical_for_each_lower_image": cnf_check("~P ~Q ~R"),
            "upper_cnf_with_lower_witnesses": upper_cnf,
            "canonical_from_eight_lower_laws": cnf_check(upper_cnf, names)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=int, help="compare the first assignments with a literal check")
    parser.add_argument("--exact", action="store_true", help="use two four-place carriers and keep the full lower image")
    options = parser.parse_args()
    if options.prefix:
        _, laws, carriers, _ = stage_and_readings(options.exact)
        result = checksum_of_prefix(laws, options.prefix, carriers)
    else:
        result = analyze(options.exact)
    print(json.dumps(result, indent=2))
