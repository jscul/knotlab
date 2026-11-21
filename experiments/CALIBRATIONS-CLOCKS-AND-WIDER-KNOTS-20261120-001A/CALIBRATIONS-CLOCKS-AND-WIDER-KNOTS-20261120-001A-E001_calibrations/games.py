"""Compare archived free flips with rule-keeping acts and separately supplied answer games."""

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from functools import cache, reduce
import gzip
import hashlib
from io import BytesIO
from itertools import combinations, permutations, product
import json
from math import gcd, prod
import os
from pathlib import Path
import resource
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "games.json.gz"
ARCHIVED_SIX = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/games.json"
PREVIOUS_SPLIT = ROOT / "artifacts/READS-HOLDERS-SOURCES-20261120-001A/READS-HOLDERS-SOURCES-20261120-001A-E001_reads_changes"
ARCHIVED_TRIPLES = ROOT / "artifacts/THREE-READERS-AND-GROWTH-20261120-001A/THREE-READERS-AND-GROWTH-20261120-001A-E001_three_readers/lead.json"
SIX_CONTEXTS = tuple(product(range(3), repeat=2))
TRIPLE_CONTEXTS = tuple(product(range(2), repeat=3))
TERNARY_TERMS = {(0, 0, 0): 1, (0, 1, 1): -1, (1, 0, 1): -1, (1, 1, 0): -1}
LAWS = ("parity", "nae")


def sign(value):
    return (-1)**(value.bit_count() % 2)


def allowed_words(copies, law):
    one = [w for w in range(8) if (sign(w) == 1 if law == "parity" else w not in (0, 7))]
    return tuple(w for w in range(8**copies) if all(((w >> (3*i)) & 7) in one for i in range(copies)))


@dataclass(frozen=True)
class Action:
    target: tuple
    phase: tuple

    def on(self, vector):
        result = [0] * len(vector)
        for i, j in enumerate(self.target):
            result[j] = self.phase[i] * vector[i]
        return tuple(result)

    def scaled(self, scalar):
        return Action(self.target, tuple(scalar * v for v in self.phase))


def compose(left, right):
    """The right factor acts first, as in the archived ordered words."""
    return Action(tuple(left.target[j] for j in right.target),
                  tuple(right.phase[i] * left.phase[j] for i, j in enumerate(right.target)))


@cache
def identity(dimension):
    return Action(tuple(range(dimension)), (1,) * dimension)


def monomial(domain, flip, read, orientation=1):
    positions = {word: i for i, word in enumerate(domain)}
    return Action(tuple(positions.get(word ^ flip, i) for i, word in enumerate(domain)),
                  tuple(orientation * sign(word & read) for word in domain))


def multiply_monomials(left, right):
    t, z, a = left
    u, v, b = right
    return t ^ u, z ^ v, a * b * sign(z & u)


def action_product(actions, dimension):
    return reduce(compose, actions, identity(dimension))


GRID = {
    "XI": (1, ("X1",)), "IX": (1, ("X2",)), "XX": (1, ("X1", "X2")),
    "IZ": (1, ("Z2",)), "ZI": (1, ("Z1",)), "ZZ": (1, ("Z1", "Z2")),
    "XZ": (1, ("X1", "Z2")), "ZX": (1, ("Z1", "X2")),
    "YY": (-1, ("X1", "Z1", "X2", "Z2")),
}
YY_WORDS = {
    "ordered": GRID["YY"],
    "row_product": (1, ("X1", "Z2", "Z1", "X2")),
    "column_product": (-1, ("X1", "X2", "Z1", "Z2")),
}
ITEMS = tuple(GRID)
LEFT_MASK, RIGHT_MASK = 0b011011, 0b100100


def primitives(role):
    if role == "A":
        return {"X1": (1, 0, 1), "X2": (8, 0, 1), "Z1": (0, 3, 1), "Z2": (0, 24, 1)}
    return {"X1": (4, 0, 1), "X2": (32, 0, 1), "Z1": (0, 4, 1), "Z2": (0, 32, 1)}


def six_actions(domain, method, yy="ordered"):
    rules = dict(GRID, YY=YY_WORDS[yy])
    built = {}
    for role in ("A", "B"):
        raw = primitives(role)
        for label, (orientation, word) in rules.items():
            if method == "substituted":
                ops = (monomial(domain, *raw[name]) for name in word)
                built[f"{role}.{label}"] = action_product(ops, len(domain)).scaled(orientation)
            else:
                t, z, phase = reduce(multiply_monomials, (raw[name] for name in word), (0, 0, orientation))
                built[f"{role}.{label}"] = monomial(domain, t, z, phase)
    return built


def six_context(context):
    row, column = context
    return (*("A." + ITEMS[3*row+j] for j in range(3)),
            *("B." + ITEMS[3*i+column] for i in range(3)))


def triple_context(context):
    return tuple(f"{'XZ'[choice]}{i}" for i, choice in enumerate(context))


def compare_actions(domain, left, right):
    different = [i for i in range(len(domain)) if (left.target[i], left.phase[i]) != (right.target[i], right.phase[i])]
    result = {"different_words": len(different)}
    if different:
        i = different[0]
        result["witness"] = {"word": domain[i], "left": [domain[left.target[i]], left.phase[i]],
                             "right": [domain[right.target[i]], right.phase[i]]}
    return result


def locality(domain, action, own):
    observed = {}
    for i, word in enumerate(domain):
        output = domain[action.target[i]]
        if (word ^ output) & ~own:
            return {"local": False, "outside_move": [word, output]}
        local_input = word & own
        effect = (output & own, action.phase[i])
        earlier, earlier_effect = observed.setdefault(local_input, (word, effect))
        if effect != earlier_effect:
            return {"local": False, "same_own_word": local_input,
                    "words": [earlier, word], "own_outputs_and_signs": [earlier_effect, effect]}
    return {"local": True}


def inspect_actions(domain, actions, local_masks):
    ident = identity(len(domain))
    individual = {}
    for label, op in actions.items():
        assert sorted(op.target) == list(range(len(domain))) and set(op.phase) <= {-1, 1}
        square = compare_actions(domain, compose(op, op), ident)
        individual[label] = {"square": square, "self_adjoint": square["different_words"] == 0,
                             "moved_words": sum(i != j for i, j in enumerate(op.target)),
                             "minus_word_signs": op.phase.count(-1),
                             "ordinary_word_dependence": locality(domain, op, local_masks[label])}
    pairs = {}
    for left, right in combinations(actions, 2):
        a, b = actions[left], actions[right]
        pairs[left, right] = compare_actions(domain, compose(a, b), compose(b, a))
    return individual, pairs


def prepared_orbit(preparation, actions):
    found = {preparation}
    pending = deque([preparation])
    while pending:
        vector = pending.popleft()
        for action in actions:
            moved = action.on(vector)
            if moved not in found:
                found.add(moved)
                pending.append(moved)
    return sorted(found)


def prepared_span(preparation, actions):
    echelon = {}
    generating_vectors = []
    pending = deque([preparation])
    while pending:
        vector = pending.popleft()
        residual = list(map(Fraction, vector))
        for i, unit in sorted(echelon.items()):
            coefficient = residual[i]
            if coefficient:
                residual = [v - coefficient*w for v, w in zip(residual, unit, strict=True)]
        first = next((i for i, v in enumerate(residual) if v), None)
        if first is None:
            continue
        echelon[first] = [v / residual[first] for v in residual]
        generating_vectors.append(vector)
        pending.extend(op.on(vector) for op in actions)
    return generating_vectors


def orbit_compatibility(preparation, actions, full_orbit):
    vectors = prepared_orbit(preparation, actions) if full_orbit else prepared_span(preparation, actions)
    pair_failures = []
    for (i, a), (j, b) in combinations(enumerate(actions), 2):
        for v in vectors:
            if a.on(b.on(v)) != b.on(a.on(v)):
                pair_failures.append(dict(pair=[i, j], vector=v, orders=[a.on(b.on(v)), b.on(a.on(v))]))
                break
    square_failures = [i for i, action in enumerate(actions) if any(action.on(action.on(v)) != v for v in vectors)]
    return {"compatible": not pair_failures and not square_failures, "generated_vectors": vectors,
            "vectors_are": "complete signed orbit" if full_orbit else "independent basis of generated span",
            "pair_failures": pair_failures, "square_failures": square_failures}


def dot(a, b):
    return sum(x*y for x, y in zip(a, b, strict=True))


def outcome_order(n):
    if n == 3:
        return tuple(range(8))
    assert n == 6
    reverse = (0, 4, 2, 6, 1, 5, 3, 7)
    return tuple(a | (b << 3) for a, b in product(reverse, repeat=2))


def project(preparation, actions, application_order):
    branches = {0: preparation}
    for i in application_order:
        expanded = {}
        for answer, v in branches.items():
            transformed = actions[i].on(v)
            expanded[answer] = tuple(x+y for x, y in zip(v, transformed, strict=True))
            expanded[answer | (1 << i)] = tuple(x-y for x, y in zip(v, transformed, strict=True))
        branches = expanded
    n = len(actions)
    return [dot(branches[b], branches[b]) for b in outcome_order(n)], dot(preparation, preparation) * 4**n


def row_from_counts(numerators, denominator):
    assert denominator > 0 and sum(numerators) == denominator and min(numerators) >= 0
    common = gcd(denominator, *numerators)
    return dict(raw_numerators=numerators, raw_denominator=denominator,
                numerators=[x // common for x in numerators], denominator=denominator // common)


def probabilities(row):
    return tuple(Fraction(n, row["denominator"]) for n in row["numerators"])


def product_moments(preparation, actions):
    vectors = [preparation]
    for op in actions:
        vectors += [op.on(v) for v in vectors]
    return tuple(dot(preparation, v) for v in vectors)


def measurement_row(preparation, actions, order, compatible=False):
    nums, den = project(preparation, actions, order)
    row = row_from_counts(nums, den)
    if compatible:
        n = len(actions)
        moments = product_moments(preparation, actions)
        for i, answer in enumerate(outcome_order(n)):
            value = sum(sign(answer & subset) * m for subset, m in enumerate(moments))
            assert value * (1 << n) == nums[i], (answer, value, nums[i])
        row["unnormalized_product_moments"] = moments
    return row


def tables_from_actions(domain, preparation, actions, context_ids, select, masks, *, sequential=False, orbit=False):
    individual, pairs = inspect_actions(domain, actions, masks)
    product_checks = {}
    all_checks = {}
    literal = {}
    sequences = {"alice_first": {}, "bob_first": {}} if sequential else {}
    prepared = {} if orbit else None
    pair_order = {key: i for i, key in enumerate(actions)}
    for context in context_ids:
        labels = select(context)
        operators = [actions[label] for label in labels]
        bad_squares = [label for label in labels if not individual[label]["self_adjoint"]]
        bad_pairs = []
        for pair in combinations(labels, 2):
            pair_key = tuple(sorted(pair, key=pair_order.__getitem__))
            if pairs[pair_key]["different_words"]:
                bad_pairs.append(pair_key)
        compatible = not bad_squares and not bad_pairs
        all_checks[context] = dict(compatible=compatible, non_involutions=bad_squares, noncommuting_pairs=bad_pairs)
        natural = tuple(range(len(operators)))
        literal[context] = measurement_row(preparation, operators, natural, compatible=True) if compatible else None
        if len(operators) == 6:
            expected = {"alice": 1, "bob": 1 - 2 * (context[1] == 2)}
            for side, group in (("alice", operators[:3]), ("bob", operators[3:])):
                key = (side, context[0 if side == "alice" else 1])
                target = identity(len(domain)).scaled(expected[side])
                forward = action_product(group, len(domain))
                reversed_order = action_product(reversed(group), len(domain))
                product_checks[key] = dict(required_sign=expected[side], product=compare_actions(domain, forward, target),
                                           reverse_product=compare_actions(domain, reversed_order, target),
                                           order_comparison=compare_actions(domain, forward, reversed_order))
        if sequential:
            for label, order in (("alice_first", natural), ("bob_first", natural[3:] + natural[:3])):
                sequences[label][context] = measurement_row(preparation, operators, order) if not bad_squares else None
                if compatible:
                    assert sequences[label][context]["raw_numerators"] == literal[context]["raw_numerators"]
        if orbit:
            test = orbit_compatibility(preparation, operators, len(operators) == 3)
            all_checks[context]["preparation_subspace"] = test
            prepared[context] = measurement_row(preparation, operators, natural, compatible=True) if test["compatible"] else None
            if test["compatible"] and len(operators) == 3:
                for order in permutations(natural):
                    assert project(preparation, operators, order)[0] == prepared[context]["raw_numerators"]
    audit = dict(individual=individual, pairs=pairs, contexts=all_checks, context_products=product_checks)
    return literal, sequences, prepared, audit


@cache
def responses_for(radices):
    if radices == (2, 2, 2):
        return tuple(tuple((word >> i) & 1 for i in range(3)) for word in range(8))
    assert radices == (8, 8)
    return tuple(product(range(8), repeat=2))


def marginals(table, radices):
    records = {}
    by_setting = defaultdict(list)
    for context, row in table.items():
        if row is None:
            continue
        masses = [[Fraction(0)] * n for n in radices]
        for answers, p in zip(responses_for(radices), probabilities(row), strict=True):
            for reader, value in enumerate(answers):
                masses[reader][value] += p
        records[context] = masses
        for i, values in enumerate(masses):
            by_setting[i, context[i]].append((context, values))
    variation = [Fraction(0)] * len(radices)
    witness = None
    for (reader, own_setting), compatible in by_setting.items():
        for (first, p), (second, q) in combinations(compatible, 2):
            distance = sum(abs(a-b) for a, b in zip(p, q, strict=True)) / 2
            if distance > variation[reader]:
                variation[reader] = distance
                index = next(i for i, (a, b) in enumerate(zip(p, q, strict=True)) if a != b)
                witness = dict(reader=reader, fixed_choice=own_setting, settings=[first, second],
                               response=index, chances=[p[index], q[index]])
    return records, variation, witness


def histogram_table(contexts, radices, instructions):
    index = {values: i for i, values in enumerate(responses_for(radices))}
    table = {}
    for context in contexts:
        counts = [0] * len(index)
        for response_list, multiplicity in instructions.items():
            values = tuple(response_list[i][setting] for i, setting in enumerate(context))
            counts[index[values]] += multiplicity
        table[context] = row_from_counts(counts, sum(instructions.values()))
    return table


def verify_mixture(table, radices, mixture):
    index = {values: i for i, values in enumerate(responses_for(radices))}
    assert sum(mixture.values()) == 1 and all(p >= 0 for p in mixture.values())
    for context, expected in table.items():
        numbers = [Fraction(0)] * len(index)
        for response_list, p in mixture.items():
            values = tuple(response_list[i][setting] for i, setting in enumerate(context))
            numbers[index[values]] += p
        assert tuple(numbers) == expected


def ordinary_certificate(table, radices, instructions):
    size = sum(instructions.values())
    mixture = {key: Fraction(n, size) for key, n in instructions.items()}
    verify_mixture(table, radices, mixture)
    return dict(local=True, method="verified ordinary-word mixture", mixture=list(mixture.items()))


def exact_solution(matrix, target, active, approximate):
    candidate = [Fraction(float(approximate[i])).limit_denominator(1 << 18) for i in active]
    block = matrix[:, active].tocsr()

    def matches(weights):
        return all(w >= 0 for w in weights) and all(
            sum(weights[i] for i in block.indices[block.indptr[j]:block.indptr[j+1]]) == p
            for j, p in enumerate(target))

    if matches(candidate):
        return candidate
    import sympy
    exact = sympy.Matrix(block.toarray().astype(int)).gauss_jordan_solve(
        sympy.Matrix([sympy.Rational(p.numerator, p.denominator) for p in target]))[0]
    values = [Fraction(int(q.p), int(q.q)) for q in exact]
    assert matches(values)
    return values


@cache
def finite_certificate(table_key, radices):
    """Find a witness numerically if needed and verify it against exact masses."""
    table = dict(table_key)
    contexts = tuple(table)
    outcomes = responses_for(radices)
    shape = tuple(max(s[i] for s in contexts) + 1 for i in range(len(radices)))
    slots = [(i, setting) for i, n in enumerate(shape) for setting in range(n)]
    possible = {slot: set(range(radices[slot[0]])) for slot in slots}
    by_context = []
    target = []
    for context, row in table.items():
        positive = {}
        for site, value in zip(outcomes, row, strict=True):
            if value:
                positive[site] = len(target)
                target.append(value)
        by_context.append(positive)
        for i, setting in enumerate(context):
            possible[i, setting].intersection_update(site[i] for site in positive)

    admissible = []
    occupied_rows = []
    for record in product(*(sorted(possible[slot]) for slot in slots)):
        start = 0
        responses = []
        for n in shape:
            responses.append(tuple(record[start:start+n]))
            start += n
        induced = [lookups.get(tuple(responses[i][s] for i, s in enumerate(context)))
                   for context, lookups in zip(contexts, by_context, strict=True)]
        if all(i is not None for i in induced):
            admissible.append(tuple(responses))
            occupied_rows.extend(induced)

    budget = prod(map(len, possible.values()))
    if not admissible:
        return dict(local=False, method="all deterministic lists hit a zero cell", lists_checked=budget,
                    local_answer_domains=possible)

    import numpy as np
    from scipy import sparse
    from scipy.optimize import linprog

    size = len(contexts)
    matrix = sparse.csc_matrix((np.ones(len(occupied_rows)),
                                (occupied_rows, np.repeat(np.arange(len(admissible)), size))),
                               shape=(len(target), len(admissible)))
    proposed = linprog(np.zeros(len(admissible)), A_eq=matrix, b_eq=list(map(float, target)),
                       bounds=(0, None), method="highs-ds")
    if proposed.success:
        active = [i for i, w in enumerate(proposed.x) if w > 1e-10]
        weights = exact_solution(matrix, target, active, proposed.x)
        mixture = {admissible[i]: p for i, p in zip(active, weights, strict=True) if p}
        verify_mixture(table, radices, mixture)
        return dict(local=True, method="verified rational mixture", lists_checked=budget,
                    support_compatible_lists=len(admissible), mixture=list(mixture.items()))

    inequalities = sparse.hstack((matrix.T, -np.ones((len(admissible), 1))), format="csr")
    dual = linprog([-float(p) for p in target] + [1], A_ub=inequalities, b_ub=np.zeros(len(admissible)),
                   bounds=[(-1, 1)] * len(target) + [(None, None)], method="highs-ds")
    assert dual.success
    coef = [Fraction(float(x)).limit_denominator(1 << 18) for x in dual.x[:-1]]
    maximum = max(sum(coef[i] for i in rows)
                  for rows in (occupied_rows[i:i+size] for i in range(0, len(occupied_rows), size)))
    measured = dot(coef, target)
    assert measured > maximum
    return dict(local=False, method="verified rational separator on support-compatible lists", lists_checked=budget,
                support_compatible_lists=len(admissible), bound=maximum, value=measured,
                coefficients=[(contexts[j], site, coef[cell]) for j, lookup in enumerate(by_context)
                              for site, cell in lookup.items() if coef[cell]])


def six_row_stats(context, row):
    i, j = context
    left_valid = right_valid = agreement = legal = win = Fraction(0)
    for (left, right), p in zip(responses_for((8, 8)), probabilities(row), strict=True):
        a = left.bit_count() % 2 == 0
        b = right.bit_count() % 2 == (j == 2)
        equal = ((left >> (2-j)) & 1) == ((right >> (2-i)) & 1)
        left_valid += p * a
        right_valid += p * b
        agreement += p * equal
        legal += p * (a and b)
        win += p * (a and b and equal)
    return dict(alice_rule=left_valid, bob_rule=right_valid, both_rules=legal, agreement=agreement, win=win)


def game_report(table, radices, *, instructions=None):
    available = {c: row for c, row in table.items() if row is not None}
    size = len(table)
    missing = [context for context in table if context not in available]
    observed_marginals, variations, witness = marginals(table, radices)
    if instructions is not None:
        common = ordinary_certificate({c: probabilities(row) for c, row in available.items()}, radices, instructions)
    elif witness:
        common = dict(local=False, method="inconsistent fixed-reader marginal", witness=witness)
    elif available:
        common = finite_certificate(tuple((c, probabilities(row)) for c, row in sorted(available.items())), radices)
    else:
        common = None
    if common is not None:
        common = dict(common, scope="defined contexts" if missing else "whole game")
    record = dict(rows=table, defined_settings=len(available), missing_settings=missing,
                  undefined_weight=Fraction(len(missing), size), marginals=observed_marginals,
                  marginal_variation=variations, common_explanation=common)
    if radices == (8, 8):
        cells = {c: six_row_stats(c, row) for c, row in available.items()}
        wins = sum((cell["win"] for cell in cells.values()), Fraction(0)) / size
        agreement = sum((cell["agreement"] for cell in cells.values()), Fraction(0)) / size
        record.update(context_answers=cells, known_win_mass=wins, score=None if missing else wins,
                      known_agreement_mass=agreement, game_average_agreement=None if missing else agreement)
    else:
        correlations = {c: sum(sign(answer)*p for answer, p in enumerate(probabilities(row))) for c, row in available.items()}
        terms = {c: weight*correlations[c] if c in correlations else None for c, weight in TERNARY_TERMS.items()}
        record.update(correlations=correlations, score_terms=terms,
                      score=sum(terms.values()) if all(v is not None for v in terms.values()) else None)
    return record


def six_responses(labels):
    row = tuple(sum(labels[3*i+j] << (2-j) for j in range(3)) for i in range(3))
    column = tuple(sum(labels[3*i+j] << (2-i) for i in range(3)) for j in range(3))
    return row, column


def shared_scalar_games():
    strategies = [six_responses([(w >> i) & 1 for i in range(9)]) for w in range(512)]
    outcomes = []
    for left, right in strategies:
        assert all((left[i] >> (2-j)) & 1 == (right[j] >> (2-i)) & 1 for i, j in SIX_CONTEXTS)
        good_left = sum(w.bit_count() % 2 == 0 for w in left)
        good_right = sum(w.bit_count() % 2 == (j == 2) for j, w in enumerate(right))
        outcomes.append(good_left * good_right)
    peak = max(outcomes)
    winning_word = outcomes.index(peak)
    uniform = Counter(strategies)
    best = Counter({strategies[winning_word]: 1})
    # Every left row and the first two right columns are even. Set the last
    # answer to minus at the last right column, as an explicit local rule.
    local_parity_adjustment = Counter({((0, 0, 0), (0, 0, 1)): 1})
    results = dict(best_shared_word_little_endian=winning_word,
                   universal_shared_word_win_count_histogram=Counter(outcomes))
    even = tuple(i for i in range(8) if sign(i) == 1)
    odd = tuple(i for i in range(8) if sign(i) == -1)
    legal_histogram = Counter()
    for *left, b0, b1, b2 in product(even, even, even, even, even, odd):
        right = (b0, b1, b2)
        wins = sum(((left[i] >> (2-j)) & 1) == ((right[j] >> (2-i)) & 1) for i, j in SIX_CONTEXTS)
        legal_histogram[wins] += 1
    results["legal_whole_setting_win_count_histogram"] = legal_histogram
    for name, instructions in (("uniform_nine_signs", uniform), ("best_shared_word", best),
                               ("local_parity_adjustment", local_parity_adjustment)):
        table = histogram_table(SIX_CONTEXTS, (8, 8), instructions)
        results[name] = game_report(table, (8, 8), instructions=instructions)
    return results


def always_plus_split(words):
    by_role = {}
    for role in ("A", "B"):
        raw = primitives(role)
        by_role[role] = []
        for w in words:
            results = []
            for orientation, expression in GRID.values():
                phase = orientation * prod(sign(w & raw[name][1]) for name in expression if name.startswith("Z"))
                results.append(int(phase < 0))
            by_role[role].append(six_responses(results))
    # Keep each role's own output in the order of its archived question.
    instructions = Counter((a[0], b[1]) for a, b in zip(by_role["A"], by_role["B"], strict=True))
    table = histogram_table(SIX_CONTEXTS, (8, 8), instructions)
    return game_report(table, (8, 8), instructions=instructions)


def movement_controls(domain, named_flips):
    acts = {}
    for name, flip in named_flips.items():
        action = monomial(domain, flip, 0)
        uniform = (1,) * len(domain)
        assert action.on(uniform) == uniform
        acts[name] = dict(flip=flip, allowed_word_action=tuple(domain[j] for j in action.target),
                          movement_report_plus_words=[w for i, w in enumerate(domain) if i != action.target[i]],
                          spectral_plus_mass=Fraction(1),
                          actual_move_mass=Fraction(sum(i != j for i, j in enumerate(action.target)), len(domain)))
    return acts


def check_archive(table, old_rows, offset=0, count_field="numerators", fixed_denominator=None):
    contexts = set()
    checked = 0
    for old in old_rows:
        setting = list(old["settings"] if "settings" in old else old["inputs"])
        setting[-1] -= offset
        context = tuple(setting)
        assert context not in contexts
        contexts.add(context)
        fresh = table[context]
        old_denominator = fixed_denominator or old["denominator"]
        values = tuple(Fraction(a, old_denominator) for a in old[count_field])
        actual = probabilities(fresh)
        for i, (a, b) in enumerate(zip(actual, values, strict=True)):
            assert a == b, ("archive probability mismatch", context, i, a, b)
            checked += 1
        if "raw_denominator" in old:
            assert old["raw_denominator"] == fresh["raw_denominator"], context
    assert contexts == set(table)
    return checked


def run_six(law, archives):
    words = allowed_words(2, law)
    ambient = tuple(range(64))
    full_preparation = tuple(int(w in words) for w in ambient)
    restricted_preparation = (1,) * len(words)
    masks = {f"{role}.{label}": mask for role, mask in (("A", LEFT_MASK), ("B", RIGHT_MASK)) for label in ITEMS}
    archived, split, alt = archives

    full = six_actions(ambient, "lumped")
    baseline, _, _, full_audit = tables_from_actions(ambient, full_preparation, full, SIX_CONTEXTS, six_context, masks)
    for alternate in YY_WORDS:
        assert six_actions(ambient, "lumped", alternate) == full
        assert six_actions(ambient, "substituted", alternate) == full
    baseline_checks = {"split_law_variant": check_archive(baseline, alt[law]["2"]["six"]["rows"])}
    if law == "parity":
        assert archived["order"] == [f"{w:03b}" for w in range(8)]
        baseline_checks.update(original_frequencies=check_archive(baseline, archived["six"], 3, "numerator"),
                               original_projector_counts=check_archive(baseline, archived["six"], 3, "born_numerators_over_256", 256),
                               physical_replay=check_archive(baseline, split["main"]["rows"]))

    variants = {"lumped": {}, "substituted": {}}
    operators = {}
    for method, by_route in variants.items():
        for route in YY_WORDS:
            actions = six_actions(words, method, route)
            operators[method, route] = actions
            if method == "lumped" and route != "ordered":
                assert actions == operators[method, "ordered"]
                continue
            literal, sequential, prepared, audit = tables_from_actions(
                words, restricted_preparation, actions, SIX_CONTEXTS, six_context, masks, sequential=True, orbit=True)
            by_route[route] = dict(literal=game_report(literal, (8, 8)), audit=audit,
                                   preparation_subspace=game_report(prepared, (8, 8)),
                                   sequential={k: game_report(v, (8, 8)) for k, v in sequential.items()})

    comparisons = {}
    for route in YY_WORDS:
        single = operators["lumped", route]
        substituted = operators["substituted", route]
        comparisons[route] = {name: compare_actions(words, single[name], substituted[name]) for name in single}
    yy_comparisons = {}
    for method in variants:
        yy_comparisons[method] = {}
        for left, right in combinations(YY_WORDS, 2):
            yy_comparisons[method][left, right] = {
                role: compare_actions(words, operators[method, left][f"{role}.YY"], operators[method, right][f"{role}.YY"])
                for role in ("A", "B")}
    return dict(physical_words=words, baseline=game_report(baseline, (8, 8)), baseline_checks=baseline_checks,
                baseline_audit=full_audit, rule_keeping=variants, literal_method_comparisons=comparisons,
                yy_construction_comparisons=yy_comparisons, scalar_same_word=always_plus_split(words),
                ordinary_movement=movement_controls(words, {f"{role}.{key}": t for role in ("A", "B")
                                                    for key, (t, _, _) in primitives(role).items() if t}))


def ternary_deterministic_check(words):
    scores = Counter()
    scores_with_allowed_ordinary_answers = Counter()
    for bits in product(range(2), repeat=6):
        answers = tuple((bits[2*i], bits[2*i+1]) for i in range(3))
        value = sum(coeff * (-1)**sum(answers[i][q] for i, q in enumerate(context))
                    for context, coeff in TERNARY_TERMS.items())
        scores[value] += 1
        if sum(z << i for i, (_, z) in enumerate(answers)) in words:
            scores_with_allowed_ordinary_answers[value] += 1
    return dict(all_64=scores, sorted_ordinary_words_required=scores_with_allowed_ordinary_answers)


def run_triples(law, archive):
    words = allowed_words(1, law)
    ambient = tuple(range(8))
    mask_by_label = {f"{q}{i}": 1 << i for i in range(3) for q in "XZ"}

    def candidates(domain):
        return {f"{q}{i}": monomial(domain, (1 << i) if q == "X" else 0, (1 << i) if q == "Z" else 0)
                for i in range(3) for q in "XZ"}

    baseline, _, _, baseline_audit = tables_from_actions(
        ambient, tuple(int(w in words) for w in ambient), candidates(ambient), TRIPLE_CONTEXTS, triple_context, mask_by_label)
    archived = check_archive(baseline, archive[law]["attachments"]["0"]["rows"])
    restricted = candidates(words)
    literal, _, prepared, audit = tables_from_actions(
        words, (1,) * len(words), restricted, TRIPLE_CONTEXTS, triple_context, mask_by_label, orbit=True)
    fiber_bases = {}
    for context in TRIPLE_CONTEXTS:
        read_mask = sum(1 << i for i, q in enumerate(context) if q == 1)
        fibers = defaultdict(list)
        for w in words:
            fibers[w & read_mask].append(w)
        indicators = [tuple(int(w in values) for w in words) for values in fibers.values()]
        operators = [restricted[label] for label in triple_context(context)]
        for i, op in enumerate(operators):
            for vector in indicators:
                w = words[vector.index(1)]
                factor = sign(w & (1 << i)) if context[i] else 1
                assert op.on(vector) == tuple(factor*v for v in vector)
        assert len(indicators) == len(prepared_span((1,) * len(words), operators))
        fiber_bases[context] = dict(read_mask=read_mask, allowed_words_by_read_answer=dict(fibers))
    ordinary = Counter(tuple((0, (w >> i) & 1) for i in range(3)) for w in words)
    scalar = histogram_table(TRIPLE_CONTEXTS, (2, 2, 2), ordinary)
    assert all(probabilities(prepared[context]) == probabilities(scalar[context]) for context in TRIPLE_CONTEXTS)
    moves = movement_controls(words, {f"X{i}": 1 << i for i in range(3)})
    # Source words are sampled once, and each possible offered move is
    # separately tested on that same source. This reports moves, not spectra.
    instructions = Counter(tuple((int(w not in moves[f"X{i}"]["movement_report_plus_words"]), (w >> i) & 1)
                                 for i in range(3)) for w in words)
    reports = histogram_table(TRIPLE_CONTEXTS, (2, 2, 2), instructions)
    return dict(physical_words=words, baseline=game_report(baseline, (2, 2, 2)), baseline_checks=archived,
                baseline_audit=baseline_audit, literal=game_report(literal, (2, 2, 2)), audit=audit,
                preparation_subspace=game_report(prepared, (2, 2, 2), instructions=ordinary),
                preparation_subspace_basis=fiber_bases,
                scalar_same_word=game_report(scalar, (2, 2, 2), instructions=ordinary),
                movement_report_from_same_initial_word=game_report(reports, (2, 2, 2), instructions=instructions),
                ordinary_movement=moves, deterministic=ternary_deterministic_check(words))


def summarize_game(record):
    return {key: record[key] for key in ("defined_settings", "missing_settings", "undefined_weight", "score", "marginal_variation")} | {
        "common_explanation": record["common_explanation"]["local"],
        "common_explanation_scope": record["common_explanation"]["scope"],
    }


def summarize(six, triples, controls):
    laws = {}
    for law in LAWS:
        study = six[law]
        restriction = {}
        for method, routes in study["rule_keeping"].items():
            for route, row in routes.items():
                section = {key: summarize_game(row[key]) for key in ("literal", "preparation_subspace")}
                section.update((key, summarize_game(data)) for key, data in row["sequential"].items())
                restriction[method, route] = section
        laws[law] = dict(six_rule={"archived_replay": summarize_game(study["baseline"]),
                                    "scalar_same_word": summarize_game(study["scalar_same_word"]),
                                    "rule_keeping": restriction},
                         ternary={key: summarize_game(triples[law][key])
                                  for key in ("baseline", "literal", "preparation_subspace",
                                              "movement_report_from_same_initial_word")})
    return dict(laws=laws, shared_scalar_controls={key: summarize_game(controls[key])
                                                   for key in ("uniform_nine_signs", "best_shared_word",
                                                               "local_parity_adjustment")})


def json_value(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_value(item) for item in (sorted(value) if isinstance(value, set) else value)]
    return value


def compressed(record):
    content = (json.dumps(json_value(record), sort_keys=True, separators=(",", ":")) + "\n").encode()
    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, filename="", mode="wb", mtime=0) as writer:
        writer.write(content)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Require byte-identical replay of the saved receipt.")
    args = parser.parse_args()
    for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[variable] = "1"
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    cap = 4 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap if soft == resource.RLIM_INFINITY else min(cap, soft), hard))
    source_paths = (ARCHIVED_SIX, PREVIOUS_SPLIT / "split_parity.json", PREVIOUS_SPLIT / "alternate_law.json", ARCHIVED_TRIPLES)
    original, split, alternate, ternaries = (json.loads(path.read_bytes()) for path in source_paths)
    six = {law: run_six(law, (original, split, alternate)) for law in LAWS}
    triples = {law: run_triples(law, ternaries) for law in LAWS}
    controls = shared_scalar_games()
    assert max(controls["universal_shared_word_win_count_histogram"]) == original["classical"]["scalar_best_game"]
    assert max(controls["legal_whole_setting_win_count_histogram"]) == original["classical"]["local_best"]
    assert controls["local_parity_adjustment"]["score"] == Fraction(original["classical"]["local_best"], 9)
    for law in LAWS:
        assert six[law]["baseline"]["score"] == Fraction(alternate[law]["2"]["six"]["equal_at_shared"])
        assert triples[law]["baseline"]["score"] == Fraction(ternaries[law]["attachments"]["0"]["m"])
    summary = summarize(six, triples, controls)
    sources = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
               for path in (*source_paths, Path(__file__).resolve())}
    record = dict(schema=1, inputs=sources,
                  conventions=dict(six_rules="Alice lexicographic three-bit answers, then Bob lexicographic three-bit answers",
                                   ternary="separate X/Z, little endian by reader, 0 means plus",
                                   raw_counts="integer squared norms at denominator |S| times 4^k for k recorded signs",
                                   spectral_order="for sequential games, inherited item order within each reader",
                                   comparison_scope="each law is a fixed built uniform source, with settings independent and uniform"),
                  six_rule=six, ternary=triples, shared_scalar_controls=controls, summary=summary)
    result = compressed(record)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != result:
            print("Saved game receipt differs from replay.", file=sys.stderr)
            return 1
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(result)
    print(json.dumps(dict(receipt=str(OUTPUT.relative_to(ROOT)), sha256=hashlib.sha256(result).hexdigest(),
                          archive_counts={law: dict(six=six[law]["baseline_checks"], ternary=triples[law]["baseline_checks"])
                                          for law in LAWS}), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
