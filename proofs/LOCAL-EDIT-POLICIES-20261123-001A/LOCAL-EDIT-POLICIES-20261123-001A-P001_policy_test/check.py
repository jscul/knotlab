"""Exact checks for local pre-edit policies. No growth producer is imported."""

import argparse
from collections import Counter, namedtuple
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BITS = (0, 1)
CELLS = tuple(product(BITS, repeat=2))
Observation = namedtuple("Observation", "i j h a b extra_a extra_b", defaults=((), ()))


def make_tables(states, read, actions=BITS):
    """Prepare each weighted state once and apply every pair of actual addresses."""
    tables = {cell: Counter() for cell in product(actions, repeat=2)}
    for (x, y), table in tables.items():
        for state, weight in states:
            if weight:
                table[read(state, x, y)] += weight
    return tables


def tv(p, q):
    left, right = sum(p.values()), sum(q.values())
    return sum(abs(Fraction(p[key], left) - Fraction(q[key], right)) for key in p.keys() | q.keys()) / 2


def policies(menus):
    keys = tuple(sorted(menus))
    return [dict(zip(keys, choices)) for choices in product(*(menus[k] for k in keys))]


def setup(tables, side, menus=None):
    home, far = ("i", "j") if side == 0 else ("j", "i")
    arm = next(iter(tables.values()))
    addresses = sorted({cell[0] for cell in tables})
    default = {k: addresses for k in {getattr(row, home) for row in arm}}
    other = {k: addresses for k in {getattr(row, far) for row in arm}}
    if menus is not None:
        default, other = menus if side == 0 else menus[::-1]
    return home, far, default, other


def receiver(row, action, side, project):
    i, mark, extra = (row.i, row.a, row.extra_a) if side == 0 else (row.j, row.b, row.extra_b)
    if project == "full":
        return (i, action, row.h, mark, extra)
    if project == "gain":
        return row.h
    if project == "bit":
        return mark
    if project == "decoder":
        return int(i) ^ row.h
    raise ValueError(project)


def run_policy(tables, side, own, other, project="full"):
    result = Counter()
    home, far = ("i", "j") if side == 0 else ("j", "i")
    for cell, prepared in tables.items():
        x, y = cell if side == 0 else cell[::-1]
        for row, weight in prepared.items():
            if own[getattr(row, home)] == x and other[getattr(row, far)] == y:
                result[receiver(row, x, side, project)] += weight
    return result


def direct_max(tables, side, menus=None):
    _, _, own_menu, other_menu = setup(tables, side, menus)
    best = Fraction(0)
    for own in policies(own_menu):
        possible = [run_policy(tables, side, own, far) for far in policies(other_menu)]
        assert len({sum(record.values()) for record in possible}) == 1
        for i, record in enumerate(possible):
            best = max([best] + [tv(record, other) for other in possible[:i]])
    return best


def conditional_gaps(tables, side, menus=None):
    """Compare old-record strata and maximize the signed sum by a separate calculation."""
    home, far, own_menu, other_menu = setup(tables, side, menus)
    strata = {}
    prior = None
    total = sum(next(iter(tables.values())).values())
    for cell, prepared in tables.items():
        x, y = cell if side == 0 else cell[::-1]
        masses = Counter()
        for row, weight in prepared.items():
            i, j = getattr(row, home), getattr(row, far)
            masses[i, j] += weight
            stratum = strata.setdefault((i, j, x, y), Counter())
            stratum[receiver(row, x, side, "full")] += weight
        assert prior is None or masses == prior
        prior = masses
    changes = {}
    for (i, j), mass in prior.items():
        for x in own_menu[i]:
            controls = other_menu[j]
            if len(controls) > 2:
                raise ValueError("signed maximization here checks up to two addresses")
            lo, hi = controls[0], controls[-1]
            d = strata[i, j, x, hi].copy()
            d.subtract(strata[i, j, x, lo])
            changes[i, j, x] = d
            assert sum(d.values()) == 0 and sum(strata[i, j, x, lo].values()) == mass
    conditional_failure = any(any(d.values()) for d in changes.values())
    maximum = 0
    for signs in product((-1, 1), repeat=len(other_menu)):
        choices = dict(zip(sorted(other_menu), signs))
        cost = 0
        for i, menu in own_menu.items():
            by_action = []
            for x in menu:
                combined = Counter()
                for j, sign in choices.items():
                    for record, diff in changes.get((i, j, x), {}).items():
                        combined[record] += sign * diff
                by_action.append(sum(map(abs, combined.values())))
            cost += max(by_action)
        maximum = max(maximum, cost)
    return conditional_failure, Fraction(maximum, 2 * total)


def summary(tables):
    counts, es = [], []
    for cell in CELLS:
        bin_counts = Counter()
        for row, weight in tables[cell].items():
            bin_counts[row.a, row.b] += weight
        counts.append([bin_counts[ab] for ab in CELLS])
        a, b, c, d = counts[-1]
        es.append(Fraction(a + d - b - c, a + b + c + d))
    scores = [sum(s * e for s, e in zip(signs, es)) for signs in product((-1, 1), repeat=4)
              if signs.count(-1) % 2]
    return dict(raw=counts, denominators=[sum(row) for row in counts], correlations=es,
                signed=sum(es[:3]) - es[3], maximum=max(scores))


def mark_test(tables, side, fixed):
    _, _, own_menu, far_menu = setup(tables, side)
    own = {i: fixed for i in own_menu}
    signed = {}
    for project in ("gain", "bit", "decoder"):
        pairs = [run_policy(tables, side, own, {j: j ^ m for j in far_menu}, project) for m in BITS]
        divisor = sum(pairs[0].values())
        signed[project] = Fraction(pairs[1][1] - pairs[0][1], divisor)
    const = [run_policy(tables, side, own, {j: m for j in far_menu}, "gain") for m in BITS]
    signed["constant_gain"] = Fraction(const[1][1] - const[0][1], sum(const[0].values()))
    e = summary(tables)["correlations"]
    gap = e[2 * fixed + 1] - e[2 * fixed] if side == 0 else e[2 + fixed] - e[fixed]
    assert gap == signed["decoder"] - signed["constant_gain"]
    assert signed["decoder"] == signed["gain"] - 2 * signed["bit"]
    return signed


def calibration(q2, *, visible, actions=BITS):
    # q2 is twice the conditional sign correlation of payloads i,j at each readiness pair.
    states = []
    for (s, t), (i, j) in product(CELLS, repeat=2):
        weight = 2 + (-1) ** (i + j) * q2[2 * s + t]
        states.append(((s, t, i, j), weight))

    def read(state, x, y):
        s, t, i, j = state
        h = int(x == s and y == t)
        return Observation(i if visible else 0, j if visible else 0, h, h * i, h * j)

    return make_tables(states, read, actions)


def check_mark_fixtures():
    sharp = calibration((2, 2, 2, -2), visible=True)
    headline = summary(sharp)
    assert headline["maximum"] == Fraction(5, 2)
    explicit = []
    for side in BITS:
        assert direct_max(sharp, side) == conditional_gaps(sharp, side)[1] == Fraction(1, 2)
        explicit.append([mark_test(sharp, side, own) for own in BITS])
        assert explicit[-1][1] == {"gain": 0, "bit": Fraction(1, 4), "decoder": Fraction(-1, 2),
                                    "constant_gain": 0}
    weak = []
    for n in range(1, 5):
        def read(ready, x, y):
            h = int(ready and x and y)
            return Observation(0, 1, h, 0, h)
        table = make_tables([(False, 4 - n), (True, n)], read)
        s = summary(table)["maximum"]
        eps = [direct_max(table, side) for side in BITS]
        assert eps == [Fraction(n, 4)] * 2 and s - 2 == 2 * eps[0]
        for side, own in CELLS:
            mark_test(table, side, own)
        weak.append(dict(mixing_weight=Fraction(n, 4), score=s, policy_TV=eps))
    return dict(nominal_privacy=headline, optimal_each_direction=Fraction(1, 2),
                xor_mark_messages=explicit, unequal_funding_sharpness=weak)


def check_scope():
    quantum = calibration((2, 1, 1, -1), visible=False)
    quantum_open = calibration((2, 1, 1, -1), visible=True)
    quantum_veto = calibration((2, 1, 1, -1), visible=False, actions=(0, 1, 2))
    scores = summary(quantum)
    assert scores["correlations"] == [1, Fraction(7, 8), Fraction(7, 8), Fraction(5, 8)]
    assert scores["maximum"] == Fraction(17, 8)
    for side in BITS:
        assert direct_max(quantum, side) == 0 and conditional_gaps(quantum, side) == (False, 0)
        assert direct_max(quantum_open, side) == Fraction(1, 4)
        assert direct_max(quantum_veto, side) == Fraction(1, 4)
    # Check q against the 2 Pauli coefficients (Z, sqrt(3) X), scaled by two.
    alice = [(2, 0), (1, 1)]
    bob = [(2, 0), (1, -1)]
    q = [Fraction(a[0] * b[0] + 3 * a[1] * b[1], 4) for a, b in product(alice, bob)]
    assert q == [1, Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2)]
    hidden_coin = {}
    for disclose in (False, True):
        def read(c, x, y):
            h = int(c == y)
            return Observation(0, 0, h, 0, 0, (c,) if disclose else (), ())
        wards = make_tables([(0, 1), (1, 1)], read)
        actual = [direct_max(wards, side) for side in BITS]
        assert actual == [int(disclose), 0]
        hidden_coin["revealed_after" if disclose else "flag_only"] = actual
    def separate(selector, x, y):
        h = (x, y)[selector]
        return Observation(0, 0, h, h * x, h * (1 - y))
    address_reader = make_tables([(0, 1), (1, 1)], separate)
    assert summary(address_reader)["maximum"] == 4
    assert [direct_max(address_reader, side) for side in BITS] == [Fraction(1, 2)] * 2
    return dict(post_only_quantum=scores, quantum_branch_correlations=q,
                post_only_compulsory_TV=0, earlier_payload_TV=Fraction(1, 4),
                new_veto_TV=Fraction(1, 4), hidden_funding_bit=hidden_coin,
                address_dependent_negative_control=dict(score=4, each_TV=Fraction(1, 2)))


def check_policy_criterion():
    count = private = conditional_failures = 0
    # Every pair of binary flags on each of four supported pairs of prestates.
    # The two receiver choices select different rows. A second menu contains singleton actions.
    states = [(ij, 1 + ij[0] + 2 * ij[1]) for ij in CELLS]
    smaller_menus = ({0: (0,), 1: BITS}, {0: BITS, 1: (1,)})
    for digits in product(range(4), repeat=4):
        def read(old, x, y):
            i, j = old
            pair = digits[2 * (i ^ x) + j]
            h = (pair >> y) & 1
            return Observation(i, j, h, h * i, h * j)
        table = make_tables(states, read)
        for menu in (None, smaller_menus):
            for side in BITS:
                failure, optimum = conditional_gaps(table, side, menu)
                brute = direct_max(table, side, menu)
                assert (brute > 0) == failure and brute == optimum
                private += brute == 0
                conditional_failures += failure
                count += 1
        for side, own in CELLS:
            mark_test(table, side, own)
    assert private and conditional_failures
    return dict(directed_menu_tests=count, private=private, signalling=conditional_failures,
                source_weights=[w for _, w in states], mark_message_identities=256 * 4)


def check_arbitrary_readings():
    # Optimize over every branch- and address-dependent sign at each local prestate.
    # At fixed Bob signs the eight coefficients of Alice signs can be optimized separately.
    keys = tuple(product(BITS, repeat=3))
    cases = {}
    for label in ("nominal_agreement", "one_hidden_selector", "irregular"):
        states = [((i, j, z), 1) for i, j in CELLS for z in range(4)]
        def read(state, x, y):
            i, j, z = state
            if label == "nominal_agreement":
                chance = 4 * int((i ^ j) == x * y)
            elif label == "one_hidden_selector":
                chance = 2 * (x + y)
            else:
                chance = (2 * i + 3 * j + x + 2 * x * y + y * i) % 5
            return Observation(i, j, int(z < chance), 0, 0)
        tables = make_tables(states, read)
        eps = [direct_max(tables, side) for side in BITS]
        maximum = 0
        for bob in product((-1, 1), repeat=len(keys)):
            b = dict(zip(keys, bob))
            coefficients = Counter()
            for (x, y), table in tables.items():
                sign = -1 if x * y else 1
                for row, weight in table.items():
                    coefficients[x, row.i, row.h] += weight * sign * b[y, row.j, row.h]
            maximum = max(maximum, sum(map(abs, coefficients.values())))
        best_score = Fraction(maximum, len(states))
        a, b = eps
        assert best_score <= 2 + min(4 * a + 2 * b, 2 * a + 4 * b)
        if label == "nominal_agreement":
            assert best_score == 4 and best_score <= 2 + 4 * min(a, b)
        if label == "one_hidden_selector":
            assert best_score == 4 and a == b == Fraction(1, 2)
        cases[label] = dict(complete_detector_pairs=2 ** (2 * len(keys)),
                            optimal_score=best_score, policy_TV=eps)
    return cases


def obeys(word, law):
    return sum(word) % 2 == 0 if law == "parity" else 0 < sum(word) < len(word)


def pair_groups(witnesses):
    """For this fixture every clique has at most two members at both stages."""
    pairs = {tuple(pair) for witness in witnesses for pair in combinations(sorted(witness), 2)}
    nodes = set().union(*witnesses)
    assert not any(all(pair in pairs for pair in combinations(triple, 2))
                   for triple in combinations(sorted(nodes), 3))
    return sorted(pairs)


def native_groups_and_fresh(stars):
    copies = Counter(v for holder in stars for v in holder)
    loose = {i: [v for v in row if copies[v] == 1] for i, row in enumerate(stars)}
    live = {i for i in loose if loose[i]}
    witness_sets = [{k for k in live if k != i and set(holder) & set(stars[k])}
                    for i, holder in enumerate(stars)]
    groups = pair_groups(witness_sets)
    assert groups == [(0, 1), (2, 3)]
    births = []
    for group in groups:
        births.append((group, tuple(loose[k].pop(0) for k in group)))
    births.extend(((k,), (v,)) for k in sorted(live) for v in loose[k])
    assert len(births) >= 2
    next_witnesses = [{i for i, (parents, _) in enumerate(births) if k in parents} for k in live]
    next_groups = pair_groups(next_witnesses)
    demands = Counter(i for group in next_groups for i in group)
    return [(parents, old, max(demands[i], 3 - len(parents), 1))
            for i, (parents, old) in enumerate(births)]


def canonical_projection(stars, on, law):
    variables = sorted({v for holder in stars for v in holder})
    names = {v: f"d{v}" for v in variables}
    clauses = []
    for holder in stars:
        for word in product(BITS, repeat=len(holder)):
            if not obeys(word, law):
                clauses.append(" ".join(("~" if bit else "") + names[v] for v, bit in zip(holder, word)))
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "; ".join(clauses),
               "--loops", *(names[v] for v in on[:-1]), "--contact", names[on[-1]],
               "--witnesses", *(names[v] for v in variables if v not in on), "--json"]
    run = subprocess.run(command, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                         check=True, text=True, capture_output=True)
    parsed = json.loads(run.stdout)
    assert parsed["is_knot"] and all(parsed[k] for k in ("binding", "coexistence", "invisible_in_parts"))
    return len(parsed["allowed"])


def check_native_components():
    # Four ternary live parents and two spent witnesses joined at distinction 12.
    stars = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11),
             (0, 1, 3, 4, 12), (6, 7, 9, 10, 12)]
    results = {}
    for law in ("parity", "not_all_equal"):
        solutions = [bits for bits in product(BITS, repeat=13)
                     if all(obeys([bits[k] for k in holder], law) for holder in stars)]
        counts = []
        for holder in stars:
            projected = {tuple(bits[k] for k in holder) for bits in solutions}
            expected = {bits for bits in product(BITS, repeat=len(holder)) if obeys(bits, law)}
            assert projected == expected
            counts.append(len(projected))
        assert canonical_projection(stars, stars[0], law) == counts[0]
        assert canonical_projection(stars, stars[4], law) == counts[4]
        z_by_pre = {}
        for bits in solutions:
            pre = tuple(bits[k] for k in stars[0] + stars[2])
            z_by_pre.setdefault(pre, set()).add(bits[12])
            if law == "parity":
                assert bits[2] ^ bits[5] == bits[12] == bits[8] ^ bits[11]
        assert all(tags == {0, 1} for tags in z_by_pre.values())
        arms = {}
        for x, y in CELLS:
            edited = list(stars)
            if x:
                edited[0] += (13,)
            if y:
                edited[2] += (14,)
            births = native_groups_and_fresh(edited)
            expected = [((0, 1), (2, 5), 1), ((2, 3), (8, 11), 1)]
            if x:
                expected.append(((0,), (13,), 2))
            if y:
                expected.append(((2,), (14,), 2))
            assert births == expected
            # Include every possible old input of the two pair births and optional unary births.
            # This superset also covers all values obtainable under the registered old-state lifts.
            old_names = sorted({d for _, names, _ in births for d in names})
            fresh = 0
            holdings = []
            for parents, old, n in births:
                holdings.append((old, tuple(range(fresh, fresh + n))))
                fresh += n
            joint_words = tuple(product(BITS, repeat=fresh))
            for old_values in product(BITS, repeat=len(old_names)):
                assignment = dict(zip(old_names, old_values))
                literal = {word for word in joint_words
                           if all(obeys(tuple(assignment[v] for v in old) + tuple(word[v] for v in indices), law)
                                  for old, indices in holdings)}
                by_birth = [[new for new in product(BITS, repeat=len(indices))
                             if obeys(tuple(assignment[v] for v in old) + new, law)] for old, indices in holdings]
                independently = {sum(local, ()) for local in product(*by_birth)}
                assert literal and literal == independently
            arms[f"{x}{y}"] = dict(old_input_patterns=2 ** len(old_names),
                                     fresh_per_birth=[n for _, _, n in births])
        results[law] = dict(old_solutions=len(solutions), old_projections=counts,
                            canonical_support_arities=[3, 5], both_z_values_at_joint_prestates=len(z_by_pre),
                            arms=arms)
    return results


def result():
    protocol = ROOT / "research/LOCAL-EDIT-POLICIES-20261123-001/preregistration.md"
    files = (protocol, HERE / "proof.md", Path(__file__).resolve())
    digests = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in files}
    assert digests[str(protocol.relative_to(ROOT))] == "a12a5a3f567cf79639d61e16920b8096979d87ff60fee3dbe2a4c4aff119f389"
    return dict(proof="LOCAL-EDIT-POLICIES-20261123-001A-P001", ticket="LOCAL-EDIT-POLICIES-20261123-001A",
                status="Proved", referee="pending",
                claim="Exact conditional-record criterion for every local address policy. Sharp signalling bounds for visible old marks and a common gain. A supplied post-only quantum control. Ordinary optional additions on separated persistent live components admit a common model even for newly revealed inputs if their visible common funding decision has invariant marginals.",
                validation="V1 finite exact policy enumeration, direct conditional comparison and independent signed-sum maximization; separate in-task reconstruction for the sharp calibration and broader bounds. The physical growth source is tested separately.",
                source_sha256=digests, proof_sha256=digests[str((HERE / "proof.md").relative_to(ROOT))],
                checks=dict(policy_criterion=check_policy_criterion(), marked_bits=check_mark_fixtures(),
                            information_and_action_controls=check_scope(), arbitrary_readings=check_arbitrary_readings(),
                            ordinary_two_components=check_native_components()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = json.loads(json.dumps(result(), default=str))
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        assert data == json.loads((HERE / "result.json").read_text())
        print("Passed full-policy, sharpness and information controls; reproduced result.json.")
