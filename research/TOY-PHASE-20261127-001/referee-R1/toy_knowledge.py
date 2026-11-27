"""Recount the parity knot and the three-reader closure using finite sets.

Run from the repository root:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 prlimit --as=1879048192 -- \
        .venv/bin/python -B research/TOY-PHASE-20261127-001/referee-R1/toy_knowledge.py

The 2007 calculation uses the three explicit types of pure state in
Spekkens, Sec. V.A, Eqs. (123), (125), (127). A separate calculation uses
the 2016 bracket. Remote conditioning tests unmeasured readers only.
"""

from collections import Counter, deque
from functools import cache, reduce
from itertools import combinations, permutations, product
import json
from operator import xor
from pathlib import Path


KNOTS = ((0, 1, 2), (1, 3, 4), (0, 3, 5), (2, 4, 5))
READERS = ((3, 2), (0, 4), (1, 5))
BITS = (0, 1)
SETTINGS = tuple(product(BITS, repeat=3))
ONTIC = tuple(product(range(4), repeat=3))
# A local underlying state is the two bits qp. A question is a mask.
Q, P, Q_PLUS_P = 2, 1, 3
QUESTIONS = (Q, P, Q_PLUS_P)
LOCAL_BASES = tuple(permutations(QUESTIONS, 2))
ASSIGNMENTS = tuple(product(LOCAL_BASES, repeat=3))


def parity(mask):
    return mask.bit_count() % 2


def pack(digits):
    value = 0
    for digit in digits:
        value = 4 * value + digit
    return value


def encode_support(points):
    return sum(1 << pack(w) for w in points)


def indices(support):
    while support:
        one = support & -support
        yield one.bit_length() - 1
        support ^= one


# Bit i in this 64-bit set means that the question's answer on state i is one.
YES = tuple(sum(1 << i for i in range(64) if parity(mask & i)) for mask in range(64))
ALL = (1 << 64) - 1


def bracket(a, b):
    # In one reader's two bits any two different nonzero questions have bracket 1.
    pairs = zip(ONTIC[a], ONTIC[b])
    return sum(x != 0 and y != 0 and x != y for x, y in pairs) % 2


BRACKET = tuple(tuple(bracket(a, b) for b in range(64)) for a in range(64))


def constant_changes(words):
    return [d for d in range(1, 8) if {w ^ d for w in words} == words]


def one_knot():
    rows = []
    for law in BITS:
        words = {w for w in range(8) if parity(w) == law}
        for first, second, third in permutations(range(3)):
            def read(w, place):
                return w >> place & 1

            def local(w):
                return 2 * read(w, first) + read(w, second)

            questions = {first: Q, second: P, third: Q_PLUS_P}
            flip = {first: 0, second: 0, third: law}
            state_reads = all(
                read(w, place) == parity(local(w) & question) ^ flip[place]
                for w in words for place, question in questions.items()
            )
            changes = constant_changes(words)
            changes_match = all(
                local(w ^ d) == local(w) ^ local(d)
                and all(read(d, place) == parity(local(d) & question)
                        for place, question in questions.items())
                for w in words for d in changes
            )
            partial_states = {
                tuple(sorted(local(w) for w in words if read(w, place) == value))
                for place in range(3) for value in BITS
            }
            rows.append({
                "law": law, "q_p_remaining_places": [first, second, third],
                "underlying_states": sorted(local(w) for w in words),
                "nonidentity_shifts": sorted(local(d) for d in changes),
                "distinct_two_point_reads": len(partial_states),
                "all_six_pure_single_reader_states": partial_states == set(combinations(range(4), 2)),
                "all_state_and_change_incidences": state_reads and changes_match,
                "raw_third_equals_q_plus_p": all(read(w, third) == parity(local(w)) for w in words),
                "outcome_flip_for_remaining_read": law,
            })
    nae = set(range(8)) - {0, 7}
    return {
        "encoding": "The place numbered i is bit i. The remaining read is q+p+law before relabelling.",
        "choices": rows,
        "not_all_equal": {
            "states": len(nae), "nonidentity_changes": constant_changes(nae),
            "possible_c_at_A0_B1": sorted(w >> 2 for w in nae if w & 3 == 2),
        },
    }


def action_order(images):
    state = tuple(range(len(images)))
    for count in range(1, 25):
        state = tuple(images[x] for x in state)
        if state == tuple(range(len(images))):
            return count
    raise ValueError("order outside the tested group")


def phases():
    rows = []
    all_perms = list(permutations(range(4)))
    flip_p = (1, 0, 3, 2)
    for images in all_perms:
        if any((old >> 1) != (new >> 1) for old, new in enumerate(images)):
            continue
        changed_at = sorted({old >> 1 for old, new in enumerate(images) if old != new})
        xor_with_c = sorted({(new & 1) ^ parity(old) for old, new in enumerate(images)})
        rows.append({
            "images_of_00_01_10_11": images, "order": action_order(images),
            "q_values_at_which_p_flips": changed_at, "p_after_xor_original_c": xor_with_c,
            "constant_translation": len({x ^ y for x, y in enumerate(images)}) == 1,
        })
    preserving = {tuple(row["images_of_00_01_10_11"]) for row in rows}
    closed = all(tuple(f[g[x]] for x in range(4)) in preserving for f, g in product(preserving, repeat=2))
    commute = all(f[g[x]] == g[f[x]] for x in range(4) for f, g in product(preserving, repeat=2))

    # q may be relabelled here. F(q,p)=(q+1,p+q) has order four on four values.
    relabel = tuple(2 * ((q ^ 1)) + (p ^ q) for q, p in product(BITS, repeat=2))
    even_words = [((x >> 1), x & 1, parity(x)) for x in range(4)]

    # A second toy bit suffices even when the answer to q must stay fixed.
    # The linear part is symplectic, and adding the fixed translation is allowed.
    def with_second(z):
        q, p, r, t = ((z >> j) & 1 for j in (3, 2, 1, 0))
        return pack((2 * q + (p ^ r), 2 * (r ^ 1) + (t ^ q)))

    two = tuple(with_second(z) for z in range(16))
    linear = tuple(y ^ two[0] for y in two)
    s = (0, 1)  # exponents of i on |0>, |1> for the diagonal qubit phase
    sxsd = [(1 - j, (s[1 - j] - s[j]) % 4) for j in BITS]
    return {
        "all_single_reader_permutations": len(all_perms), "fixing_q_answers": rows,
        "closed_under_composition": closed, "all_four_commute": commute,
        "four_state_counterexample_with_q_outcomes_exchanged": {
            "map": "F(q,p)=(q+1,p+q)", "order": action_order(relabel),
            "square_flips_p": tuple(relabel[relabel[x]] for x in range(4)) == flip_p,
            "p_after_equals_c": all((relabel[x] & 1) == word[2] for x, word in enumerate(even_words)),
            "q_after_equals_one_plus_q": all((relabel[x] >> 1) == (word[0] ^ 1)
                                             for x, word in enumerate(even_words)),
        },
        "two_toy_bit_counterexample_with_q_fixed": {
            "map": "F(q,p,r,t)=(q,p+r,r+1,t+q)", "order": action_order(two),
            "bijective": len(set(two)) == 16,
            "linear_part_additive": all(linear[a ^ b] == linear[a] ^ linear[b]
                                        for a, b in product(range(16), repeat=2)),
            "linear_part_preserves_bracket": all(BRACKET[linear[a]][linear[b]] == BRACKET[a][b]
                                                 for a, b in product(range(16), repeat=2)),
            "fixes_q": all((two[z] >> 3) == (z >> 3) for z in range(16)),
            "square_flips_only_p": all(two[two[z]] == z ^ 4 for z in range(16)),
            "p_after_depends_on_other_bit": all(((two[z] ^ two[z ^ 2]) & 4) == 4 for z in range(16)),
        },
        "qubit": {"S_order": next(k for k in range(1, 5) if all(k * t % 4 == 0 for t in s)),
                  "S_squared_phase_exponents": [2 * t % 4 for t in s],
                  "SX_S_adjoint_output_and_i_exponent": sxsd, "SX_S_adjoint_is_Y": sxsd == [(1, 1), (0, 3)]},
    }


def pure_states_2007():
    # Local permutations are generated by swapping consecutive ontic values.
    # Reader exchanges allow the correlated pair to occupy any two places.
    generators = []
    for site in range(3):
        for left in range(3):
            def image(w):
                v = list(w)
                if v[site] == left:
                    v[site] += 1
                elif v[site] == left + 1:
                    v[site] -= 1
                return pack(v)
            generators.append(tuple(image(w) for w in ONTIC))
    for i, j in ((0, 1), (1, 2)):
        def exchange(w):
            v = list(w)
            v[i], v[j] = v[j], v[i]
            return pack(v)
        generators.append(tuple(exchange(w) for w in ONTIC))

    # The labels in the paper are 1 through 4, here represented by 0 through 3.
    triplet = ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0),
               (2, 2, 2), (2, 3, 3), (3, 2, 3), (3, 3, 2))
    seeds = {
        "product_Eq123": tuple(product((0, 1), repeat=3)),
        "pair_Eq125": tuple((x, x, y) for x in range(4) for y in (0, 1)),
        "triplet_Eq127": triplet,
    }
    classes = {}
    for name, seed in seeds.items():
        start = encode_support(seed)
        orbit = {start}
        work = deque([start])
        while work:
            pending = tuple(indices(work.popleft()))
            for transform in generators:
                moved = sum(1 << transform[x] for x in pending)
                if moved not in orbit:
                    orbit.add(moved)
                    work.append(moved)
        classes[name] = orbit
    return classes, encode_support(triplet)


def independent_question_triples():
    # One reduced row echelon basis of each three-dimensional binary subspace.
    for pivots in combinations(range(6), 3):
        slots = [(i, j) for i, pivot in enumerate(pivots)
                 for j in range(pivot + 1, 6) if j not in pivots]
        for choices in product(BITS, repeat=len(slots)):
            rows = [1 << i for i in pivots]
            for (row, column), bit in zip(slots, choices):
                rows[row] |= bit << column
            yield rows


def pure_states_2016():
    all_bases = accepted = 0
    supports = set()
    for basis in independent_question_triples():
        all_bases += 1
        if any(BRACKET[a][b] for a, b in combinations(basis, 2)):
            continue
        accepted += 1
        cells = {}
        for point in range(64):
            answers = tuple(parity(q & point) for q in basis)
            cells[answers] = cells.get(answers, 0) | 1 << point
        assert len(cells) == 8 and all(s.bit_count() == 8 for s in cells.values())
        supports.update(cells.values())
    return supports, all_bases, accepted


def unordered_pairings(distinctions):
    if not distinctions:
        yield ()
        return
    head, *tail = distinctions
    for i, partner in enumerate(tail):
        for remaining in unordered_pairings(tail[:i] + tail[i + 1:]):
            yield ((head, partner),) + remaining


@cache
def known_questions(support):
    return tuple(mask for mask, yes in enumerate(YES)
                 if (support & yes) == 0 or (support & yes) == support)


def mapped_questions(pairs, assignment):
    questions = [0] * 6
    for i, ((a, b), (u, v)) in enumerate(zip(pairs, assignment)):
        questions[a] = u << (4 - 2 * i)
        questions[b] = v << (4 - 2 * i)
    return questions


def questions_of_knots(questions):
    return tuple(reduce(xor, (questions[d] for d in knot)) for knot in KNOTS)


def simultaneous_answers(questions, answers):
    support = ALL
    for question, answer in zip(questions, answers):
        support &= YES[question] if answer else ALL ^ YES[question]
    return support


@cache
def smaller_states_2007():
    """Original one- and two-reader states, from Secs. III.A, IV.A and IV.C."""
    four = tuple(range(4))
    halves = tuple(combinations(four, 2))
    one = {frozenset((i,) for i in subset) for subset in (*halves, four)}
    two = {frozenset(product(a, b)) for a in (*halves, four) for b in (*halves, four)}
    two.update(frozenset(enumerate(relabel)) for relabel in permutations(four))
    for a, b in product(halves, repeat=2):
        two.add(frozenset((x, y) for x, y in product(four, repeat=2) if (x in a) == (y in b)))
    return {1: one, 2: two}


@cache
def all_remote_outcomes(support):
    """Every allowed one- or two-reader outcome on the complementary readers.

    The 2007 state types for one and two readers are also all possible outcome
    supports of reproducible measurements there. This includes joint pair
    measurements. Test the full distribution on the undisturbed readers.
    """
    valid = smaller_states_2007()
    points = [ONTIC[i] for i in indices(support)]
    tested = failures = 0
    for size in (1, 2):
        for kept in combinations(range(3), size):
            measured = tuple(j for j in range(3) if j not in kept)
            by_parts = [(tuple(w[j] for j in measured), tuple(w[i] for i in kept)) for w in points]
            for outcome in valid[len(measured)]:
                possible = Counter(part for observed, part in by_parts if observed in outcome)
                if possible:
                    tested += 1
                    failures += frozenset(possible) not in valid[size] or len(set(possible.values())) != 1
    return tested, failures


@cache
def remote_balance(support, available):
    """Check all results of at most one allowed read per *other* reader.

    Uniform affine supports give uniform marginals after each such result.
    k unmeasured toy bits need at least 2**k remaining underlying states.
    A singleton for one unmeasured bit is a direct contradiction of Sec. III.A.
    """
    points = [ONTIC[i] for i in indices(support)]
    marginal_sizes = []
    failing_contexts = failing_outcomes = 0
    witness = None
    for size in (1, 2, 3):
        for kept in combinations(range(3), size):
            others = tuple(i for i in range(3) if i not in kept)
            projected = [tuple(point[i] for i in kept) for point in points]
            marginal_sizes.append(len(set(projected)))
            menus = [(0,) + tuple(available[i]) for i in others]
            for choice in product(*menus):
                possible = {}
                for point, part in zip(points, projected):
                    readout = tuple(parity(q & point[j]) for q, j in zip(choice, others) if q)
                    possible.setdefault(readout, set()).add(part)
                failures = {label: opts for label, opts in possible.items() if len(opts) < 2**size}
                failing_contexts += bool(failures)
                failing_outcomes += len(failures)
                if failures and witness is None:
                    outcome = min(failures)
                    witness = {
                        "unmeasured_reader_indices": kept, "remote_reader_indices": others,
                        "remote_questions_q2_p1_qplusp3": choice, "outcomes": outcome,
                        "possible_unmeasured_ontic_tuples": sorted(failures[outcome]),
                    }
    return tuple(marginal_sizes), failing_contexts, failing_outcomes, witness


def pairings_check(catalogue):
    rows = []
    all_readings = (QUESTIONS,) * 3
    for pairs in unordered_pairings(list(range(6))):
        hits = Counter()
        bracket_patterns = set()
        remote_failures = set()
        joint_remote_failures = set()
        marginal_shapes = set()
        held = tuple(i for i, knot in enumerate(KNOTS) if any(set(pair) <= set(knot) for pair in pairs))
        absent = sum(not any(set(pair) <= set(knot) for knot in KNOTS) for pair in pairs)
        first_witness = None
        for assignment in ASSIGNMENTS:
            laws = questions_of_knots(mapped_questions(pairs, assignment))
            support = simultaneous_answers(laws, (0, 0, 0, 0))
            known = known_questions(support)
            fail = tuple((i, j) for i, j in combinations(range(4), 2) if BRACKET[laws[i]][laws[j]])
            bracket_patterns.add(fail)
            bracket_pure = len(known) == 8 and all(BRACKET[a][b] == 0 for a, b in combinations(known, 2))
            hits["bracket_2016"] += bracket_pure
            hits["catalogue_2007"] += support in catalogue
            margins, named_bad, _, _ = remote_balance(support, assignment)
            _, bad, bad_outcomes, witness = remote_balance(support, all_readings)
            marginal_shapes.add(margins)
            hits["bare_support_counts"] += all(m >= floor for m, floor in zip(margins, (2, 2, 2, 4, 4, 4, 8)))
            hits["conditional_two_named_reads"] += named_bad == 0
            hits["conditional_all_three_toy_questions"] += bad == 0
            tested_joint, bad_joint = all_remote_outcomes(support)
            hits["conditional_all_allowed_single_or_joint_remote_outcomes"] += bad_joint == 0
            remote_failures.add((bad, bad_outcomes))
            joint_remote_failures.add((tested_joint, bad_joint))
            if assignment == ASSIGNMENTS[0]:
                first_witness = witness
            assert (not fail) == bracket_pure == (support in catalogue) == (bad == 0) == (bad_joint == 0)
        rows.append({
            "pairing": pairs, "pairs_held_together_by_no_knot": absent,
            "number_of_assignments": len(ASSIGNMENTS), "passes_per_test": dict(hits),
            "marginal_support_sizes_singles_pairs_all": sorted(marginal_shapes),
            "knots_holding_both_reads_of_some_reader": held,
            "pairs_of_knot_indices_with_nonzero_bracket_across_assignments": sorted(bracket_patterns),
            "invalid_remote_contexts_and_outcomes_across_assignments": sorted(remote_failures),
            "possible_and_invalid_single_or_joint_remote_outcomes_across_assignments": sorted(joint_remote_failures),
            "example_with_q_then_p_assigned_to_each_pair": first_witness,
        })
    return rows


def readings_table(points):
    # Counts out of 8; each of the eight underlying states has equal weight.
    table = []
    for choice in SETTINGS:
        reads = [pair[i] for i, pair in zip(choice, READERS)]
        counts = Counter(tuple(point[j] for j in reads) for point in points)
        table.extend(counts[word] for word in SETTINGS)
    return table


def declared_closure(catalogue):
    even_words = [word for word in product(BITS, repeat=6)
                  if all(sum(word[d] for d in knot) % 2 == 0 for knot in KNOTS)]
    target = []
    for choice in SETTINGS:
        for value in SETTINGS:
            if sum(choice) % 2:
                target.append(2 * (sum(value) % 2 == int(sum(choice) == 3)))
            else:
                target.append(1)
    word_table = readings_table(even_words)
    direct_target_matches = sum(a == b for a, b in zip(word_table, target))
    counts = Counter()
    score_profiles = Counter()
    closure_favorable = Counter()
    for assignment in ASSIGNMENTS:
        questions = mapped_questions(READERS, assignment)
        laws = questions_of_knots(questions)
        even = simultaneous_answers(laws, (0, 0, 0, 0))
        odd = simultaneous_answers(laws, (0, 0, 0, 1))
        known = known_questions(even)
        counts["all_known_questions_commute_and_three_are_independent"] += (
            len(known) == 8 and all(BRACKET[a][b] == 0 for a, b in combinations(known, 2)))
        counts["even_is_a_pure_state_with_eight_points"] += even in catalogue and even.bit_count() == 8
        counts["odd_is_empty"] += odd == 0
        recovered = [tuple(parity(q & point) for q in questions) for point in indices(even)]
        toy_table = readings_table(recovered)
        counts["same_64_probabilities"] += toy_table == word_table
        counts["same_eight_evaluated_words"] += set(recovered) == set(even_words)
        good = [YES[laws[3]]] + [ALL ^ YES[q] for q in laws[:3]]
        # The denominator is 4 equally weighted contexts times 8 equiprobable states.
        profile = Counter(sum((support & win).bit_count() for win in good) for support in catalogue)
        score_profiles[tuple(sorted(profile.items()))] += 1
        closure_favorable[sum((even & win).bit_count() for win in good)] += 1
    return {
        "readers_shared_then_loose": READERS, "knots": KNOTS, "assignments": len(ASSIGNMENTS),
        "pure_states_scored_per_assignment": len(catalogue), "assignment_counts": dict(counts),
        "actual_word_count": len(even_words), "even_table_counts_out_of_eight": word_table,
        "odd_target_counts_out_of_eight": target, "entry_order": "lexicographic setting, then outcome",
        "raw_closure_matches_odd_target_out_of_64": direct_target_matches,
        "scores_as_successes_out_of_32": [
            {"number_of_assignments": n, "states_by_success_count": dict(profile)}
            for profile, n in score_profiles.items()
        ],
        "closure_successes_out_of_32_by_number_of_assignments": dict(closure_favorable),
    }


def main():
    original_classes, ghz = pure_states_2007()
    original = set.union(*original_classes.values())
    bracket_states, examined, accepted = pure_states_2016()
    assert original == bracket_states
    invalid_single = simultaneous_answers((Q, P), (0, 0))
    pair_rows = pairings_check(original)
    report = {
        "primary_sources": {
            "single_reader_and_measurement_conditioning": "https://arxiv.org/pdf/quant-ph/0401052#page=12",
            "three_pure_state_types": "https://arxiv.org/pdf/quant-ph/0401052#page=22",
            "bracket_and_maximal_knowledge": "https://arxiv.org/pdf/1409.5041#page=12",
            "known_pure_state_count_Eq10": "https://arxiv.org/pdf/1103.5037#page=7",
            "inductive_conditioning_criterion_Pusey_Lemma7": "https://arxiv.org/pdf/1103.5037#page=8",
        },
        "one_knot": one_knot(), "one_reader_phases": phases(),
        "pure_state_catalogues": {
            "2007_orbits": {name: len(orbit) for name, orbit in original_classes.items()},
            "2007_union": len(original),
            "2007_smaller_state_catalogues_for_full_remote_conditioning": {
                size: len(states) for size, states in smaller_states_2007().items()},
            "2016_distinct_three_generator_question_spans_examined": examined,
            "2016_maximal_commuting_question_sets": accepted,
            "2016_unique_pure_supports": len(bracket_states),
            "size_of_symmetric_difference": len(bracket_states ^ original),
        },
        "gates": {
            "toy_GHZ_explicit_Eq127_in_2016_catalogue": ghz in bracket_states,
            "toy_GHZ_support_size": ghz.bit_count(),
            "toy_GHZ_is_equal_q_and_even_p": ghz == encode_support(
                w for w in ONTIC if len({i >> 1 for i in w}) == 1 and sum(i & 1 for i in w) % 2 == 0),
            "q_and_p_have_nonzero_bracket": BRACKET[Q][P] == 1,
            "knowing_q_and_p_of_one_reader_leaves_local_ontic_values": sorted(
                {ONTIC[x][-1] for x in indices(invalid_single)}),
        },
        "registered_readers": declared_closure(original),
        "all_pairings": {
            "tests_on": "The eight equally weighted all-even words; pair order sets reader names.",
            "conditioning": "Test the unmeasured readers. Compare the two named questions, all three local questions separately, and every allowed single or joint outcome on the complement.",
            "counts_passing_under_every_assignment": {
                key: sum(row["passes_per_test"][key] == len(ASSIGNMENTS) for row in pair_rows)
                for key in pair_rows[0]["passes_per_test"]},
            "rows": pair_rows,
        },
    }
    destination = Path(__file__).with_suffix(".json")
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{len(original)} pure toy states; {accepted} maximal commuting question sets")
    print(report["all_pairings"]["counts_passing_under_every_assignment"])
    print(report["registered_readers"]["scores_as_successes_out_of_32"])


if __name__ == "__main__":
    main()
