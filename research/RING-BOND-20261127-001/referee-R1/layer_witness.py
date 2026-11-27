"""Check a higher agreement bond on a constructed twelve-knot start."""

import argparse
import contextlib
import io
import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from layer_readings import agreement, fibers, mixed_fibers, occurring, source_table, truth_columns


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
from knotlab.cli import main as canonical_check


def setup():
    """Each of the six lower readings uses three separate distinctions."""
    carriers = [tuple(range(3 * r, 3 * r + 3)) for r in range(6)]
    laws = []
    for group, i, j in product(range(3), range(2), range(2)):
        first = carriers[2 * group + i]
        second = carriers[2 * ((group + 1) % 3) + j]
        laws.append((first[j], first[j + 1], second[2 * i]))
    cross = list(product((0, 1), (2, 3), (4, 5)))
    return carriers, laws, cross


def connected(sets):
    reached = {0}
    while True:
        grown = reached | {j for j, support in enumerate(sets)
                           if any(set(support).intersection(sets[i]) for i in reached)}
        if grown == reached:
            return len(grown) == len(sets)
        reached = grown


def conjunction(universe, law_sets):
    result = universe
    for allowed in law_sets:
        result &= allowed
    return result


def word_set(rows, columns):
    return [format(n, f"0{len(columns)}b") for n in sorted(occurring(rows, columns))]


def project(words, places):
    return {"".join(w[i] for i in places) for w in words}


def code_at_knot(law_text, visible, witnesses):
    reports = []
    for contact in visible:
        loops = [x for x in visible if x != contact]
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            status = canonical_check(["check", "--cnf", law_text, "--loops", *loops, "--contact", contact,
                                      "--witnesses", *witnesses, "--json"])
        if status:
            raise RuntimeError(capture.getvalue())
        report = json.loads(capture.getvalue())
        assert report["is_knot"]
        reports.append({key: report[key] for key in ("variables", "allowed", "is_knot")})
    return reports


def upper_cnf(cross):
    names = ["A0", "A1", "B0", "B1", "C0", "C1"]
    visible = ["P", "Q", "R"]
    clauses = [" ".join("~" + names[x] for x in law) for law in cross]
    for i, reading in enumerate(visible):
        local = (*names[2*i:2*i+2], reading)
        for values in product((0, 1), repeat=3):
            if values[2] != (values[0] == values[1]):
                clauses.append(" ".join(("~" if value else "") + label
                                        for label, value in zip(local, values, strict=True)))
    return "; ".join(clauses), visible, names


def literal_prefix(stop):
    carriers, knots, _ = setup()
    counts = Counter()
    for w in range(stop):
        if any(len({(w >> x) & 1 for x in k}) == 1 for k in knots):
            continue
        code = "".join("1" if len({(w >> x) & 1 for x in carrier}) == 1 else "0"
                       for carrier in carriers)
        counts[code] += 1
    return dict(sorted(counts.items()))


def inspect():
    carriers, knots, cross = setup()
    universe, raw, obey, rows = source_table(knots)
    lower = [agreement(universe, [raw[x] for x in carrier]) for carrier in carriers]
    joint = word_set(rows, lower)
    counts = {format(n, "06b"): states.bit_count()
              for n, states in enumerate(fibers(rows, lower)) if states}
    assert literal_prefix(1 << 18) == counts
    assert connected(knots)
    assert all(count == 2 for count in Counter(x for k in knots for x in k).values())
    assert set(joint) == {w for w in map("".join, product("01", repeat=6))
                          if all(any(w[x] == "0" for x in triple) for triple in cross)}
    lower_mixed = [[mixed_fibers(col, fibers(rows, [raw[x] for x in knot])) for col in lower] for knot in knots]
    assert all(all(row) for row in lower_mixed)

    lower_single_changes = []
    for carrier, read in zip(carriers, lower, strict=True):
        counts_by_place = []
        for x in carrier:
            # Pair each state with bit x = 0 to its state after flipping x.
            current = rows & ~raw[x] & (rows >> (1 << x))
            counts_by_place.append((current & (read ^ (read >> (1 << x)))).bit_count())
        assert all(counts_by_place)
        lower_single_changes.append(counts_by_place)

    raw_deletions = [conjunction(universe, obey[:i] + obey[i+1:]) for i in range(len(obey))]
    first_bonds = []
    for places in combinations(range(6), 3):
        selected = [lower[x] for x in places]
        image = word_set(rows, selected)
        if places not in cross:
            assert len(image) == 8
            continue
        assert set(image) == set(format(i, "03b") for i in range(7))
        restored = [i for i, allowed in enumerate(raw_deletions) if len(occurring(allowed, selected)) == 8]
        assert len(restored) == 3
        holder_knots = [knots[i] for i in restored]
        reduced = conjunction(universe, [obey[i] for i in restored])
        assert word_set(reduced, selected) == image
        numbered = set().union(*(set(c) for c in holder_knots))
        excluded = [sorted(set(carriers[x]) - numbered) for x in places]
        first_bonds.append({"readings": places, "forbidden": "111",
                            "source_laws_whose_separate_deletion_restores_111": restored,
                            "those_three_laws_alone_have_same_relation": True,
                            "those_laws_connected_by_shared_distinctions": connected(holder_knots),
                            "carrier_members_outside_those_laws": excluded})

    all_words, lower_vars = truth_columns(6)
    eight_laws = [all_words & ~(lower_vars[a] & lower_vars[b] & lower_vars[c]) for a, b, c in cross]
    conj = conjunction(all_words, eight_laws)
    assert sorted(joint) == word_set(conj, lower_vars)
    upper = [agreement(all_words, lower_vars[i:i+2]) for i in (0, 2, 4)]
    upper_image = word_set(conj, upper)
    assert upper_image == [format(i, "03b") for i in range(1, 8)]
    top_pairs = {f"{i}{j}": sorted(project(upper_image, (i, j))) for i, j in combinations(range(3), 2)}
    upper_mixed = [[mixed_fibers(mask, fibers(conj, [lower_vars[x] for x in k])) for mask in upper]
                   for k in cross]
    assert all(all(row) for row in upper_mixed)
    deletion = []
    for i, law in enumerate(cross):
        without = conjunction(all_words, eight_laws[:i] + eight_laws[i+1:])
        word = "".join("1" if j in law else "0" for j in range(6))
        assert set(word_set(without, lower_vars)) - set(joint) == {word}
        assert len(word_set(without, upper)) == 8
        deletion.append({"omitted": law, "additional_lower_word": word, "additional_upper_word": "000"})
    assert connected(cross)
    cnf, visible, witnesses = upper_cnf(cross)
    canonical = code_at_knot(cnf, visible, witnesses)
    return {
        "raw_distinctions": 18, "source_knots_not_all_equal": knots,
        "source_connected": True, "each_distinction_held_twice": True, "loose_distinctions": 0,
        "ordinary_growth": "closed at the start",
        "allowed_source_states": rows.bit_count(), "lower_carriers_in_A0_A1_B0_B1_C0_C1_order": carriers,
        "source_state_counts_by_lower_word": counts,
        "single_source_knot_fixes_leaving_both_values_per_lower_reading": lower_mixed,
        "allowed_single_changes_flipping_each_member_of_each_lower_carrier": lower_single_changes,
        "triples_of_the_six_readings_examined": 20, "first_bonds": first_bonds,
        "canonical_check_of_each_identical_lower_image": code_at_knot("~P ~Q ~R", ["P", "Q", "R"], []),
        "upper_carriers_on_lower_readings": [(0, 1), (2, 3), (4, 5)], "connected_lower_bonds": True,
        "all_eight_lower_laws_present_exact_six_reading_image": True,
        "words_allowed_by_eight_lower_laws": conj.bit_count(),
        "upper_image_number_of_lower_words": {format(i, "03b"): part.bit_count()
                                              for i, part in enumerate(fibers(conj, upper))},
        "upper_pair_projections": top_pairs,
        "single_lower_bond_fixes_leaving_both_values_per_upper_reading": upper_mixed,
        "deletion_of_each_lower_law_with_six_distinctions_free": deletion,
        "upper_cnf_whose_witnesses_are_six_lower_readings": cnf,
        "canonical_check_from_the_eight_lower_laws_with_witnesses": canonical,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    if args.pilot:
        counts = literal_prefix(8192)
        print(json.dumps({"source_states_examined": 8192, "allowed": sum(counts.values()),
                          "observed_words": len(counts)}))
    else:
        out = inspect()
        (HERE / "layer_witness.json").write_text(json.dumps(out, indent=2) + "\n")
        print(json.dumps({"source_states": out["allowed_source_states"],
                          "lower_words": out["words_allowed_by_eight_lower_laws"],
                          "upper_words": sum(bool(v) for v in out["upper_image_number_of_lower_words"].values())}))


if __name__ == "__main__":
    main()
