"""Compare structural lower candidates and the four-clause join with unconditional finite enumeration."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from time import perf_counter

from omitted_search import HERE, advance, bits, candidate_clauses, choices, make_mask, peel, roster


def projection(supports):
    names = sorted(set().union(*map(set, supports)))
    laws = list(map(make_mask, supports))
    assert names == list(range(len(names)))
    states = [s for s in range(1 << len(names)) if all(0 < (s & k) < k for k in laws)]
    full = (1 << len(states)) - 1
    eq = {}
    eligible = set()
    for z in (2, 3):
        for sub in combinations(names, z):
            m = make_mask(sub)
            e = 0
            for i, s in enumerate(states):
                value = (s & m) in (0, m)
                e |= int(value) << i
            eq[m] = e
            if not 0 < e < full:
                continue
            for k in laws:
                table = {}
                read_at_k = True
                for s in states:
                    v = (s & m) in (0, m)
                    fixed = s & k
                    if v != table.setdefault(fixed, v):
                        read_at_k = False
                        break
                if read_at_k:
                    break
            else:
                eligible.add(m)
    candidates, _ = candidate_clauses(supports)
    def occurs(triple):
        states_for_word = full
        for reading in triple:
            m, v = reading >> 1, reading & 1
            states_for_word &= eq[m] if v else ~eq[m]
        return bool(states_for_word)
    assert all(not occurs(triple) for triple in candidates)
    actual = set()
    one_word = 0
    multiple = 0
    tested = 0
    signatures = Counter()
    for a, b, c in combinations(sorted(eligible), 3):
        if a & b or a & c or b & c:
            continue
        tested += 1
        images = {}
        for w in product(range(2), repeat=3):
            signed = tuple((m << 1) | v for m, v in zip((a, b, c), w))
            images[w] = occurs(signed)
        missing = [w for w, seen in images.items() if not seen]
        if not missing:
            continue
        if any(len({(w[i], w[j]) for w in images if images[w]}) < 4
               for i, j in combinations(range(3), 2)):
            continue
        one_word += len(missing) == 1
        multiple += len(missing) > 1
        for w in missing:
            actual.add(tuple((m << 1) | v for m, v in zip((a, b, c), w)))
            signatures["".join(map(str, w))] += 1
    assert not (actual - candidates)
    return {"knots": len(supports), "distinctions": len(names), "allowed_states": len(states),
            "unread_carriers": len(eligible), "disjoint_triples_tested": tested,
            "genuine_single_word_bonds": one_word, "genuine_multiple_word_bonds": multiple,
            "genuine_signed_missing_words": len(actual), "signed_words_by_bits": signatures,
            "structural_candidates": len(candidates), "genuine_words_omitted": len(actual - candidates),
            "candidate_words_present_in_full_system": sum(occurs(triple) for triple in candidates)}


def clause_set(pattern):
    return frozenset(tuple(sorted((pattern[0][i], pattern[1][j], pattern[2][i ^ j])))
                     for i, j in product(range(2), repeat=2))


def direct_four(triples, masks):
    out = set()
    for four in combinations(triples, 4):
        freq = Counter(x for t in four for x in t)
        if len(freq) != 6 or set(freq.values()) != {2}:
            continue
        if any(len(set(a) & set(b)) != 1 for a, b in combinations(four, 2)):
            continue
        if any(masks[a] & masks[b] for a, b in combinations(freq, 2)):
            continue
        out.add(frozenset(four))
    return out


def join_control(pilot):
    masks = [(3 << (2 * i)) for i in range(6)]
    triples = [tuple(2 * i + v for i, v in enumerate(words)) for words in product(range(2), repeat=3)]
    n = 2 if pilot else 256
    histogram = Counter()
    for subset in range(n):
        chosen = {t for j, t in enumerate(triples) if subset & (1 << j)}
        expected = direct_four(chosen, masks)
        peel(chosen, masks)
        output = [clause_set(pattern) for pattern in choices(chosen, masks)]
        assert len(output) == len(set(output)) and set(output) == expected
        histogram[len(output)] += 1
    # This raw distinction now belongs to two of the otherwise separate carriers.
    conflict = masks.copy()
    conflict[4] |= masks[2] & -masks[2]
    chosen = set(triples)
    expected = direct_four(chosen, conflict)
    peel(chosen, conflict)
    assert set(clause_set(pattern) for pattern in choices(chosen, conflict)) == expected == set()
    return {"all_clause_subsets": n, "patterns_per_subset": histogram,
            "overlapping_control_patterns": len(expected)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", action="store_true")
    args = p.parse_args()
    start = perf_counter()
    rings = [((0, 1, 3), (1, 2, 4), (0, 2, 5))]
    for _ in range(2):
        rings.append(advance(rings[-1]).supports)
    cases = {f"three-knot start and ordinary round {r}": laws for r, laws in enumerate(rings)}
    cases["closed four-knot start with repeated shared distinctions"] = ((0,1,4), (0,1,5), (2,3,4), (2,3,5))
    _, stages = roster()
    cases["first grown stage with twelve distinctions from the sample"] = next(
        laws for (idx, r), (laws, _) in sorted(stages.items())
        if len(set().union(*map(set, laws))) == 12 and r > 0)
    cases["first round of census entry 61, largest archived bond count among grown twelve-distinction stages"] = stages[61, 1][0]
    rows = {}
    for name, case in cases.items():
        rows[name] = projection(case)
        if args.pilot:
            break
    data = {"direct_projection_cases": rows, "four_clause_join": join_control(args.pilot),
            "elapsed_seconds": round(perf_counter() - start, 4)}
    path = HERE / ("omitted_controls_pilot.json" if args.pilot else "omitted_controls.json")
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(path.name, data["elapsed_seconds"])


if __name__ == "__main__":
    main()
