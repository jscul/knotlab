"""Check the claims about which unrecorded schedules lose the contradiction.

Three readers. Operators act by left exterior multiplication, in the listing
x_a,y_a,z_a,x_b,y_b,z_b,x_c,y_c,z_c. Collapse the fresh alternatives only
after checking every grown coefficient within a reader block.
"""
import argparse
import json
import math
import subprocess
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORDERS = tuple(permutations("abc"))
SIGNS = {0: 1, 3: -1, 5: -1, 6: -1}
ALL_SETTINGS = range(8)


def create(modes, added, coefficient):
    for mode in added:
        if mode in modes:
            return None
        if sum(i < mode for i in modes) % 2:
            coefficient = -coefficient
        modes = modes | {mode}
    return modes, coefficient


def state(schedule):
    old_signs = {}
    for old in range(8):
        if old.bit_count() % 2:
            continue
        terms = [(frozenset(), 1)]
        for event, reader in schedule:
            j = "abc".index(reader)
            x = 3 * j
            occupied = (old >> j) & 1
            if event == "c":
                choices = [(x,)] if occupied else [()]
            else:
                # In the written product y+ z+, the right creator acts first.
                choices = [(x + 1,), (x + 2,)] if occupied else [(), (x + 2, x + 1)]
            terms = [create(modes, added, coeff) for modes, coeff in terms for added in choices]
        assert len({modes for modes, _ in terms}) == 8
        signs = {value for _, value in terms}
        assert len(signs) == 1
        old_signs[old] = signs.pop()
    return old_signs


def round_events(sigma, pi):
    return [('c', j) for j in sigma] + [('b', j) for j in pi]


def correlations(amp):
    # F1 exchanges the two local old states with coefficient +1 in this listing.
    norms = sum(a * a for a in amp.values())
    return tuple(Fraction(sum(a * amp.get(x ^ t, 0) * (-1) ** ((x & ~t).bit_count())
                              for x, a in amp.items()), norms) for t in ALL_SETTINGS)


def average(rows):
    rows = tuple(rows)
    return tuple(sum(values) / len(rows) for values in zip(*rows))


def is_odd(order):
    return sum(a > b for i, a in enumerate(order) for b in order[i + 1:]) % 2 == 1


def nonconstant_schedule_sign():
    """At four readers, ask only whether *any* two-one old word has minus sign."""
    pairs = list(combinations(range(4), 2))

    def pairings(remaining):
        if not remaining:
            yield []
            return
        first, *others = remaining
        for j, end in enumerate(others):
            for rest in pairings(others[:j] + others[j+1:]):
                yield [(first, end)] + rest

    any_minus = 0
    count = 0
    for events in pairings(list(range(8))):
        count += 1
        # Starts are in order. A single crossing gives a negative coefficient
        # on the old word with those two readers occupied and the others blank.
        any_minus += any(events[j][0] < events[i][1] < events[j][1] for i, j in pairs)
    return {"labelled_schedules": count * 24, "nonconstant_sign": any_minus * 24,
            "flat_sign": (count - any_minus) * 24}


def score(mean, directions):
    """Absolute four-term score for arbitrary normalized real readings."""
    score_sum = 0
    for settings, sign in SIGNS.items():
        for term, corr in enumerate(mean):
            coeffs = (directions[j][settings >> j & 1][term >> j & 1] for j in range(3))
            score_sum += sign * corr * math.prod(coeffs)
    return abs(score_sum)


def freeze():
    def git(*args):
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

    ticket = HERE.parent.name
    family = f"artifacts/{ticket}/{ticket}-E001_schedules"
    frozen = "8515665ca6"
    paths = [f"research/{ticket}/preregistration.md", f"experiments/{ticket}/{ticket}-E001_schedules/contract.json",
             f"research/{ticket}/advisor/question_1.md", f"research/{ticket}/advisor/answer_1.md"]
    def blob(path):
        stored = git("rev-parse", f"{frozen}:{path}")
        current = git("hash-object", str(ROOT / path))
        assert stored == current
        return current

    blobs = {path: blob(path) for path in paths}
    first_receipt = git("log", "-1", "--diff-filter=A", "--format=%H", "--", f"{family}/results.json")
    assert git("merge-base", frozen, first_receipt) == git("rev-parse", frozen)
    assert not git("ls-tree", "-r", "--name-only", frozen, "--", family)
    return {"freeze": git("rev-parse", frozen), "first_committed_receipt": first_receipt,
            "unchanged_blobs": blobs, "study_implementation_files_in_freeze": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    start = perf_counter()
    base = ORDERS[0]
    by_order = {p: correlations(state(round_events(base, p))) for p in ORDERS}
    if args.pilot:
        print(f"Six chronological tables: {perf_counter() - start:.6f} s")
        return

    mean = {label: average(c for p, c in by_order.items() if select(p)) for label, select in
            [('chronological_even', lambda p: not is_odd(p)), ('chronological_odd', is_odd),
             ('all', lambda p: True)]}
    prev = next((ROOT / 'research/REORDER-SIGN-20261126-001/referee-R1').glob('*/block.json'))
    previous = json.loads(prev.read_text())['equal_mixtures_with_order_unavailable']
    witness = {}
    for label, previous_label in [('chronological_even', 'odd_orders'), ('all', 'all_orders')]:
        row = previous[previous_label]
        old = tuple(Fraction(row['full_correlations'][format(i, '03b')[::-1]]) for i in ALL_SETTINGS)
        assert old == mean[label]
        old_witness = row['real_reading_change_witness']
        dirs = [[[Fraction(z), Fraction(x)] for z, x in reader]
                for reader in old_witness['unnormalized_z_x_directions']]
        numerator = score(old, dirs)
        squared = numerator ** 2 / Fraction(old_witness['mermin_denominator_squared'])
        assert squared == Fraction(old_witness['mermin_squared'])
        u = 4 if label == 'chronological_even' else 7
        dirs = (((u, 1), (-u, 1)), ((1, 0), (0, 1)), ((u, -1), (u, 1)))
        # Readers a and c each contribute one factor 1/sqrt(u^2+1).
        independent_score = score(mean[label], dirs) / (u * u + 1)
        witness[label] = {"predecessor_witness_score_squared": str(squared),
                          "independent_unnormalized_Z_X_directions": dirs,
                          "attained_score": str(independent_score)}
    assert mean['chronological_odd'] == (1, 0, 0, 0, 0, 0, 0, 0)
    # Two distinct unknown schedules with the same creation order and different
    # birth orders. Both have just the occupied pair a,b contributing a minus.
    first = 'ca cb ba bb cc bc'.split()
    second = 'ca cb cc bc ba bb'.split()
    assert state(first) == state(second)
    common = correlations(state(first))
    assert math.prod(common[t] for t in SIGNS) == -1
    # An unobserved common permutation for creation and commit always gives
    # exactly the same old amplitudes, hence all the same probabilities.
    aligned = {tuple(state(round_events(p, p)).items()) for p in ORDERS}
    assert len(aligned) == 1
    output = {
        'setting_index': 'bit j is 1 for the real flip at reader j (a is bit 0); 0 for Z',
        'freeze_check': freeze(),
        'unknown_schedule_same_creation_order': {
            'schedules': [first, second], 'states_equal': True,
            'correlations': list(map(str, common)), 'product_of_four_scored_correlations': -1},
        'unknown_common_creation_and_commit_order': {'hidden_orders': 6, 'distinct_old_states': 1,
                                                      'old_amplitudes': dict(aligned.pop())},
        'equal_mixtures_by_chronological_commit_parity': {k: list(map(str, v)) for k, v in mean.items()},
        'changed_real_readings': witness,
        'four_reader_nonconstant_sign': nonconstant_schedule_sign(),
    }
    (HERE / 'order_record.json').write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
