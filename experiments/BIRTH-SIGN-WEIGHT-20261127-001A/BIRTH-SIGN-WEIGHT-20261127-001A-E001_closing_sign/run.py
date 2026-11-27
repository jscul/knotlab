"""Exact pre-birth sign and reader controls on the two registered fixtures."""

import argparse
import itertools
import json
import resource
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "FORBID-EDITS-20261126-001"))
import forbid  # The same ordinary proposal used by the archived four-knot example.


def mask(places):
    return sum(1 << v for v in places)


def parity(word):
    return word.bit_count() % 2


def sign(bit):
    return 1 if bit == 0 else -1


def places(word):
    return [v for v in range(word.bit_length()) if word & (1 << v)]


@dataclass
class Old:
    parents: tuple
    loose: tuple
    shared: int
    words: tuple
    changes: tuple


def prebirth(parents, proposed_inputs):
    """Use only the old laws and distinctions named in the proposal."""
    holders = Counter(v for row in parents for v in row)
    shared = mask(v for v, count in holders.items() if count == 2)
    loose = tuple(next(v for v in row if holders[v] == 1) for row in parents)
    assert set(loose) == set(proposed_inputs) and all(count <= 2 for count in holders.values())
    assert all(sum(holders[v] == 1 for v in row) == 1 for row in parents)
    rows = tuple(mask(row) for row in parents)
    words = tuple(w for w in range(1 << (1 + max(holders))) if not any(parity(w & row) for row in rows))
    changes = []
    for row in rows:
        # Hold the parent's places fixed, flip every shared distinction outside
        # its places and require each old parity to survive.
        possible = [w for w in words if w & row == 0 and w & shared == shared & ~row]
        assert len(possible) == 1 and possible[0] != 0
        changes.append(possible[0])
    return Old(rows, loose, shared, words, tuple(changes))


def proposal(parents):
    after, info = forbid.grow(parents, "parity", "ordinary", forbid.ENGINE)
    assert len(info["births"]) == 1 and info["following_funding"]["status"] == "closed"
    born = info["births"][0]
    assert born["f"] == 0 and born["old_inputs_already_imply_law"]
    assert tuple(sorted(born["inputs"])) == tuple(sorted(after[-1]))
    return tuple(born["inputs"])


def four_parents():
    pairs = list(itertools.combinations(range(4), 2))
    return tuple(tuple(i for i, pair in enumerate(pairs) if p in pair) + (len(pairs) + p,)
                 for p in range(4))


def apply_questions(word, questions):
    """(change, value) multiplies by the current value sign, then changes word."""
    coefficient = 1
    for change, value in questions:
        coefficient *= sign(parity(word & value))
        word ^= change
    return word, coefficient


def parent_questions(old):
    return tuple((change, 1 << v) for change, v in zip(old.changes, old.loose, strict=True))


def phase_solution(old):
    """Solve the supplied transport equations separately on each orbit."""
    result = {}
    orbit_sizes = []
    for seed in old.words:
        if seed in result:
            continue
        result[seed] = 1
        queue = [seed]
        size = 0
        while queue:
            w = queue.pop()
            size += 1
            for question in parent_questions(old):
                successor, coefficient = apply_questions(w, [question])
                desired = coefficient * result[w]
                if successor in result:
                    assert result[successor] == desired
                else:
                    result[successor] = desired
                    queue.append(successor)
        orbit_sizes.append(size)
    return result, orbit_sizes


def closure(old, orders):
    """Compare successive value reads with the same reads on the original word."""
    counts = Counter()
    questions = parent_questions(old)
    for order in orders:
        ordered = [questions[i] for i in order]
        for w in old.words:
            final, sequential = apply_questions(w, ordered)
            original, simultaneous = apply_questions(w, [(0, v) for _, v in ordered])
            assert original == w and final & mask(old.loose) == w & mask(old.loose)
            counts[sequential * simultaneous] += 1
    return dict(counts)


def interleavings(parents, new, paired):
    listing = [v for row in (*parents, new) for v in sorted(row)]
    positions = defaultdict(list)
    for position, v in enumerate(listing):
        positions[v].append(position)
    count = 0
    for a, b in paired:
        i, k = positions[a]
        j, l = positions[b]
        count += (i < j < k < l) or (j < i < l < k)
    return count


def sign_comparison(parents, inputs, old):
    # Finished holdings are used here ONLY for the archived rival R.
    candidate = {tuple(sorted((v, shared))) for v, change in zip(old.loose, old.changes, strict=True)
                 for shared in places(change & old.shared)}
    finished = (*parents, inputs)
    all_places = places(mask(set().union(*finished)))
    finished_rule = {pair for pair in itertools.combinations(all_places, 2)
                     if not any(set(pair) <= set(row) for row in finished)}
    result = {}
    for name, pairs in (("all_commute", set()), ("prebirth", candidate), ("finished_R", finished_rule)):
        result[name] = {"pairs": sorted(pairs), "interleavings": interleavings(parents, inputs, pairs)}
        result[name]["closing_sign"] = sign(result[name]["interleavings"] % 2)
    return result


def expectation(words, questions, phases):
    total = 0
    for w in words:
        successor, coefficient = apply_questions(w, questions)
        if phases is None:
            total += coefficient * (successor == w)
        else:
            # A supplied pair-local question may send an allowed word outside
            # the old relation. The six-bit preparation has zero amplitude there.
            total += coefficient * phases[w] * phases.get(successor, 0)
    return Fraction(total, len(words))


BITS = tuple(itertools.product(range(2), repeat=3))


def probability_table(old, alternatives, phases):
    rows = {}
    for settings in BITS:
        questions = [pair[s] for pair, s in zip(alternatives, settings, strict=True)]
        for first, second in itertools.combinations(questions, 2):
            assert parity(first[0] & second[1]) == parity(second[0] & first[1])
        moments = [expectation(old.words, [q for q, use in zip(questions, subset, strict=True) if use], phases)
                   for subset in BITS]
        probabilities = []
        for answers in BITS:
            terms = [m * sign(sum(a * b for a, b in zip(answers, subset, strict=True)) % 2)
                     for m, subset in zip(moments, BITS, strict=True)]
            probabilities.append(sum(terms) / 8)
        assert sum(probabilities) == 1 and min(probabilities) >= 0
        rows[settings] = probabilities
    return rows


def fixed_target(settings):
    changed = sum(settings)
    if changed not in (1, 3):
        return [Fraction(1, 8)] * 8
    required = int(changed == 3)
    return [Fraction(int(sum(a) % 2 == required), 4) for a in BITS]


def game_summary(table):
    matches = 0
    winning = Fraction(0)
    for settings, chances in table.items():
        target = fixed_target(settings)
        matches += sum(p == q for p, q in zip(chances, target, strict=True))
        if sum(settings) in (1, 3):
            winning += sum(p for p, q in zip(chances, target, strict=True) if q) / 4
    return {"matching_entries_of_64": matches, "four_context_win": str(winning),
            "probabilities": {"".join(map(str, s)): [str(p) for p in row] for s, row in table.items()}}


def verify_pair_projectors(old, phases, alternatives, observed):
    """Use three full 64-component outcome projectors, separate from the moment expansion."""
    width = (old.shared | mask(old.loose)).bit_length()
    basis = range(1 << width)
    preparations = {
        "transport_phase": [[phases.get(w, 0) for w in basis]],
        "constant_phase": [[int(w in old.words) for w in basis]],
        "diagonal_mixture": [[int(w == original) for w in basis] for original in old.words],
    }
    checked = 0
    for name, vectors in preparations.items():
        stored = observed[f"{name}_supplied_pair_local"]["probabilities"]
        for settings in BITS:
            context = "".join(map(str, settings))
            for index, answers in enumerate(BITS):
                norm = 0
                for starting in vectors:
                    vector = starting
                    for pair, setting, answer in zip(alternatives, settings, answers, strict=True):
                        change, value = pair[setting]
                        projected = vector.copy()
                        for w, amplitude in enumerate(vector):
                            projected[w ^ change] += sign(answer ^ parity(w & value)) * amplitude
                        vector = projected
                    norm += sum(a * a for a in vector)
                # Each of three projectors contributes 1/2 to the amplitude.
                probability = Fraction(norm, len(old.words) * 4**3)
                assert probability == Fraction(stored[context][index])
                checked += 1
    return checked


def reader_controls(old, phases):
    opposites = [places(old.shared & ~row)[0] for row in old.parents]
    assert all((old.shared & ~row).bit_count() == 1 for row in old.parents)
    values = [((0, 1 << s), (0, 1 << loose)) for s, loose in zip(opposites, old.loose, strict=True)]
    changes = [((0, 1 << s), (change, 0)) for s, change in zip(opposites, old.changes, strict=True)]
    rephased = [((0, 1 << s), (change, 1 << loose))
                for s, change, loose in zip(opposites, old.changes, old.loose, strict=True)]
    pair_local = [((1 << loose, 1 << s), (1 << s, 0)) for s, loose in zip(opposites, old.loose, strict=True)]
    flat = dict.fromkeys(old.words, 1)
    observed = {}
    overall_minus = {w: -phase for w, phase in phases.items()}
    for name, prep in (("transport_phase", phases), ("diagonal_mixture", None),
                       ("constant_phase", flat), ("overall_minus", overall_minus)):
        for access, questions in (("ordinary_values", values), ("supplied_change", changes),
                                  ("supplied_pair_local", pair_local), ("rephased_change", rephased)):
            observed[f"{name}_{access}"] = game_summary(probability_table(old, questions, prep))
    assert observed["transport_phase_supplied_change"] == observed["overall_minus_supplied_change"]
    assert observed["transport_phase_supplied_change"] == observed["transport_phase_supplied_pair_local"]
    assert observed["transport_phase_supplied_change"] == observed["constant_phase_rephased_change"]
    assert observed["constant_phase_supplied_change"] == observed["transport_phase_rephased_change"]
    rows = []
    for s, loose, row, change in zip(opposites, old.loose, old.parents, old.changes, strict=True):
        pair = mask((s, loose))
        rows.append({"parent": places(row), "reader_places": [s, loose], "candidate_flip": places(change),
                     "flip_outside_reader": places(change & ~pair), "flip_inside_parent": places(change & row),
                     "supplied_local_setting_0": {"value": s, "flip": loose},
                     "supplied_local_setting_1": {"flip": s},
                     "words_left_allowed_by_local_flips":
                         [sum((w ^ (1 << v)) in old.words for w in old.words) for v in (loose, s)],
                     "allowed_nonzero_flips_inside_reader": [places(w) for w in old.words if w and not w & ~pair]})
    by_input = defaultdict(list)
    for w in old.words:
        shared = tuple((w >> v) & 1 for v in opposites)
        loose = "".join(str((w >> v) & 1) for v in old.loose)
        exponent = sum(a * b for a, b in itertools.combinations(shared, 2)) % 2
        assert phases[w] == sign(exponent)
        by_input[loose].append({"shared": "".join(map(str, shared)), "phase": phases[w]})
    assert all(sorted(r["phase"] for r in group) == [-1, 1] for group in by_input.values())
    # Changing the old word used for the zero labels multiplies each transport
    # coefficient by its loose sign at the new origin. Their product stays +1.
    recodings = 0
    for origin in old.words:
        assert parity(origin & mask(old.loose)) == 0
        for w in old.words:
            for question in parent_questions(old):
                destination, original_sign = apply_questions(w, [question])
                translated, actual_sign = apply_questions(w ^ origin, [question])
                assert translated == destination ^ origin
                assert actual_sign == original_sign * sign(parity(origin & question[1]))
                assert phases[translated] == actual_sign * phases[w ^ origin]
                recodings += 1
    return {"readers": rows, "words_by_proposed_input": by_input, "tables": observed,
            "full_six_bit_projector_comparisons": verify_pair_projectors(old, phases, pair_local, observed),
            "value_recoding_parent_equations": recodings}


def symmetric_invisible(old):
    """Count nonzero invisible flips fixed by all permutations fixing a parent."""
    holders = {v: tuple(i for i, p in enumerate(old.parents) if p & (1 << v))
               for v in places(old.shared | mask(old.loose))}
    place_for = {h: v for v, h in holders.items()}
    assert len(place_for) == len(holders)
    fixed = []
    for i, parent in enumerate(old.parents):
        candidates = {w for w in old.words if w and not (w & parent)}
        for permutation in itertools.permutations(range(len(old.parents))):
            if permutation[i] != i:
                continue
            moved = {v: place_for[tuple(sorted(permutation[j] for j in h))] for v, h in holders.items()}
            candidates = {w for w in candidates if mask(moved[v] for v in places(w)) == w}
        assert candidates == {old.changes[i]}
        fixed.append(len(candidates))
    return fixed


def relabel_check(parents, inputs, old):
    width = max(itertools.chain.from_iterable(parents)) + 1
    checked = 0
    for p in itertools.permutations(range(width)):
        moved = tuple(tuple(p[v] for v in row) for row in parents)
        moved_inputs = tuple(p[v] for v in inputs)
        other = prebirth(moved, moved_inputs)
        expected = tuple(mask(p[v] for v in places(x)) for x in old.changes)
        assert other.changes == expected and other.loose == tuple(p[v] for v in old.loose)
        checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path, help="Write JSON here. The default is stdout.")
    args = parser.parse_args()
    start = perf_counter()
    result = {}
    for n, parents in ((3, ((0, 1, 2), (1, 3, 4), (3, 0, 5))), (4, four_parents())):
        inputs = proposal(parents)
        old = prebirth(parents, inputs)
        phases, orbit_sizes = phase_solution(old)
        orders = [tuple(range(n))] if args.pilot else itertools.permutations(range(n))
        row = {"parents": parents, "proposed_inputs": inputs, "allowed_words": len(old.words),
               "allowed_invisible_nonzero_per_parent": [sum(bool(w) and (w & p) == 0 for w in old.words)
                                                        for p in old.parents],
               "fixed_nonzero_invisible_per_parent": symmetric_invisible(old),
               "selected_changes": [places(w) for w in old.changes], "phase_orbit_sizes": orbit_sizes,
               "sequential_to_simultaneous": closure(old, orders), "exchange_rules": sign_comparison(parents, inputs, old)}
        if n == 3:
            signal_time = perf_counter() - start
            row["readers_and_probabilities"] = reader_controls(old, phases)
            if not args.pilot:
                row["distinct_renamings_checked"] = relabel_check(parents, inputs, old)
        result[f"{n}_parents"] = row
    result["resources"] = {"pilot": args.pilot, "first_sign_seconds": signal_time,
                           "elapsed_seconds_excluding_import": perf_counter() - start,
                           "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
