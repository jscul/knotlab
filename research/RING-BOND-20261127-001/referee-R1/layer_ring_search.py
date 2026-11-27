"""Find eight ring bonds with the signed pattern of the twelve-knot witness."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

from layer_readings import agreement, fibers, mixed_fibers, occurring, source_table, truth_columns
from ring_recount import find_bonds, ring_stages


HERE = Path(__file__).resolve().parent


def seek(hypotheses, strict, tally):
    """For each prospective first pair, find two further pairs meeting it in all eight ways.

    A signed reading encodes the value it has in the forbidden word. Equalities
    of the printed readings themselves, without any sign changes, are tested.
    """
    carriers = sorted({s for triple in hypotheses for s in triple})
    numbers = {c: i for i, c in enumerate(carriers)}
    signatures = [sum(1 << x for x in c) for c in carriers]
    others = defaultdict(set)
    links = defaultdict(set)
    for support, words in hypotheses.items():
        assert len(words) == 1
        signed = sorted(2 * numbers[c] + int(b) for c, b in zip(support, words[0], strict=True))
        for i, v in enumerate(signed):
            pair = tuple(signed[:i] + signed[i + 1:])
            others[pair].add(v)
            links[v].add(pair)

    def pair_admitted(a, b):
        return a // 2 != b // 2 and (not strict or not signatures[a // 2] & signatures[b // 2])

    share = Counter()
    for neighbours in others.values():
        for a, b in combinations(sorted(neighbours), 2):
            if pair_admitted(a, b):
                share[a, b] += 1
    eligible = sorted(ab for ab, n in share.items() if n >= 4)
    tally["pairs_with_at_least_four_common_signed_pairs"] = len(eligible)
    for a0, a1 in eligible:
        tally["first_pairs_examined"] += 1
        together = links[a0] & links[a1]
        near = defaultdict(set)
        for x, y in together:
            near[x].add(y)
            near[y].add(x)
        last = defaultdict(list)
        for c, adjacent in near.items():
            for b0, b1 in combinations(sorted(adjacent), 2):
                if (a0, a1) < (b0, b1) and pair_admitted(b0, b1):
                    last[b0, b1].append(c)
        for (b0, b1), choices in sorted(last.items()):
            for c0, c1 in combinations(sorted(choices), 2):
                if (b0, b1) >= (c0, c1) or not pair_admitted(c0, c1):
                    continue
                grouped = ((a0, a1), (b0, b1), (c0, c1))
                assert len({v // 2 for pair in grouped for v in pair}) == 6
                tally["patterns_checked_until_first_witness"] += 1
                yield tuple(tuple((carriers[v // 2], v % 2) for v in pair) for pair in grouped)


def certificate(grouped, stage, archive):
    flat = [s for pair in grouped for s in pair]
    names = [s for s, _ in flat]
    signs = [v for _, v in flat]
    assert len(set(names)) == 6
    selected = []
    for ijk in product((0, 1), (2, 3), (4, 5)):
        key = tuple(sorted(names[i] for i in ijk))
        signs_by_carrier = {names[i]: signs[i] for i in ijk}
        word = "".join(str(signs_by_carrier[x]) for x in key)
        assert archive[key] == (word,)
        selected.append((ijk, "".join(str(signs[i]) for i in ijk)))

    universe, columns, _, source = source_table(stage)
    lower = [agreement(universe, [columns[x] for x in c]) for c in names]
    physical = occurring(source, lower)
    conj = sorted("".join(w) for w in product("01", repeat=6)
                  if all("".join(w[i] for i in ijk) != missing for ijk, missing in selected))
    joint = [format(x, "06b") for x in sorted(physical)]
    assert set(joint) <= set(conj) and len(conj) == 37
    upper = [agreement(universe, lower[i:i+2]) for i in (0, 2, 4)]
    missing = "".join(str(int(signs[i] != signs[i+1])) for i in (0, 2, 4))
    physical_words = [format(x, "03b") for x in sorted(occurring(source, upper))]
    assert missing not in physical_words
    implied = sorted({"".join(str(int(w[i] == w[i+1])) for i in (0, 2, 4)) for w in conj})
    assert set(implied) == {format(x, "03b") for x in range(8)} - {missing}
    ideal, lower_bits = truth_columns(6)
    laws = []
    for ijk, excluded in selected:
        local_words = fibers(ideal, [lower_bits[i] for i in ijk])
        laws.append(ideal & ~local_words[int(excluded, 2)])
    def without(whole, restrictions, erased=None):
        for i, law in enumerate(restrictions):
            if i != erased:
                whole &= law
        return whole
    permitted = without(ideal, laws)
    upper_bits = [agreement(ideal, lower_bits[i:i+2]) for i in (0, 2, 4)]
    single_deletions = [len(occurring(without(ideal, laws, i), upper_bits)) for i in range(8)]
    assert single_deletions == [8] * 8
    ideal_mixed = [[mixed_fibers(x, fibers(permitted, [lower_bits[i] for i in ijk])) for x in upper_bits]
                   for ijk, _ in selected]
    assert all(all(row) for row in ideal_mixed)
    actual_mixed = [[mixed_fibers(x, fibers(source, [lower[i] for i in ijk])) for x in upper]
                    for ijk, _ in selected]
    extra_source_constraints = [triple for triple in combinations(names, 3) if tuple(sorted(triple)) in archive]
    all_inside = []
    for triple in extra_source_constraints:
        sorted_set = tuple(sorted(triple))
        all_inside.append((tuple(names.index(c) for c in sorted_set), archive[sorted_set][0]))
    complete = ["".join(w) for w in product("01", repeat=6)
                if all("".join(w[i] for i in idx) != forbid for idx, forbid in all_inside)]
    return {"six_lower_carriers_grouped_into_upper_pairs": [names[i:i+2] for i in (0, 2, 4)],
            "signed_values_in_the_eight_forbidden_words": signs, "lower_laws": selected,
            "lower_carriers_all_disjoint": all(set(x).isdisjoint(y) for x, y in combinations(names, 2)),
            "three_upper_carriers_disjoint_in_raw_distinctions": all(
                set().union(*names[i:i+2]).isdisjoint(set().union(*names[j:j+2]))
                for i, j in combinations((0, 2, 4), 2)),
            "eight_bonds_allow_lower_words": len(conj), "actual_lower_words": joint,
            "first_bonds_on_six_readings": len(all_inside), "all_bonds_allow_lower_words": len(complete),
            "single_upper_word_excluded_by_eight_bonds": missing,
            "upper_image_size_after_each_lower_bond_deletion": single_deletions,
            "mixed_lower_bond_fixes_on_eight_law_conjunction": ideal_mixed,
            "mixed_lower_bond_fixes_on_physical_stage": actual_mixed,
            "upper_source_word_counts": {format(i, "03b"): n.bit_count() for i, n in enumerate(fibers(source, upper))},
            "upper_words_on_source": physical_words}


def positive_control():
    # All eight choices on six physically disjoint carriers. Repeat after
    # changing three different carrier values in every forbidden word.
    six = [tuple(range(3*i, 3*i + 3)) for i in range(6)]
    results = []
    for values in ("111111", "010011"):
        indices = product((0, 1), (2, 3), (4, 5))
        clauses = {tuple(six[i] for i in chosen): ("".join(values[i] for i in chosen),)
                   for chosen in indices}
        matches = list(seek(clauses, True, Counter()))
        assert len(matches) == 1
        for omit in clauses:
            remaining = {law: word for law, word in clauses.items() if law != omit}
            assert not list(seek(remaining, True, Counter()))
        results.append({"signs": values, "patterns": len(matches), "single_deletions_destroying_pattern": 8})
    return results


def run(through, pilot=False):
    out = {"positive_controls": positive_control()}
    stages = ring_stages(through)
    for turn in range(1, through + 1):
        stage = stages[turn]
        started = perf_counter()
        found = find_bonds(stage)
        reconstruction_seconds = perf_counter() - started
        for strict in (True, False):
            tally = Counter({"first_pairs_examined": 0, "patterns_checked_until_first_witness": 0})
            started = perf_counter()
            earliest = next(seek(found, strict, tally), None)
            row = {"first_bonds": len(found), "stage": stage, "summary": dict(tally),
                   "search_stopped_at_first_witness": earliest is not None,
                   "search_seconds": round(perf_counter() - started, 5),
                   "source_reconstruction_seconds": round(reconstruction_seconds, 5)}
            if earliest is not None:
                row["witness"] = certificate(earliest, stage, found)
            out[f"round_{turn}_" + ("disjoint" if strict else "overlap")] = row
            print(turn, "disjoint" if strict else "overlap", dict(tally), "witness", bool(earliest), flush=True)
        if pilot and turn == 1:
            break
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=4, choices=range(1, 5))
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    result = run(args.through, args.pilot)
    if not args.pilot:
        (HERE / "layer_ring_search.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
