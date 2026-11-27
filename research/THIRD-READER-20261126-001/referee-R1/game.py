"""Rebuild the round-zero game and the setting-aware lists.

The inputs are the documented four family specifications and the original
named-read rule. The family instances are built from the holding recipe in
BUILT-BINDING-20261126-001/repro.py (rings_start). No fixture or study function
is imported. The joint probabilities come from exact uniform word sums and
local spectral projectors. The optional archive check runs after the rebuild.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from itertools import combinations, count, product
import json
from math import prod
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
from time import perf_counter


FAMILIES = (
    ("three rings of five, detour (the referee's 30 knots)", 5, True, False),
    ("three rings of five, direct links", 5, False, False),
    ("three rings of four, detour", 4, True, False),
    ("three rings of five, detour, one loose distinction at the first chain's middle knot", 5, True, True),
)
READERS = "AMB"
SETTINGS = tuple(product((0, 1), repeat=3))
ANSWERS = tuple(product((1, -1), repeat=3))
GROUPS = tuple(group for size in (1, 2) for group in combinations(range(3), size))
SCORED = {(0, 0, 0): 1, (0, 1, 1): -1, (1, 0, 1): -1, (1, 1, 0): -1}
PHASE = (1, 1j, -1, -1j)


def mask(distinctions):
    return sum(1 << distinction for distinction in distinctions)


def distinctions(bits):
    return [i for i in range(bits.bit_length()) if bits >> i & 1]


def build_start(length, detour, middle_loose):
    """Use the source distinction order so named supports remain traceable."""
    assert detour or not middle_loose
    next_name = count()
    knots = [set() for _ in range(3 * length)]
    rings = [tuple(range(i * length, (i + 1) * length)) for i in range(3)]

    def share(*holders):
        name = next(next_name)
        for knot in holders:
            knots[knot].add(name)

    def append_knots(size):
        index = len(knots)
        knots.extend(set() for _ in range(size))
        return tuple(range(index, index + size))

    for members in rings:
        for knot, successor in zip(members, (*members[1:], members[0])):
            share(knot, successor)
    for members in rings:
        for knot in members:
            share(knot)
            share(knot)

    attachments = Counter()
    for pair in combinations(range(3), 2):
        left, right = append_knots(2)
        for ring, connector in zip(pair, (left, right)):
            start = attachments[ring]
            for offset in (0, 2):
                share(rings[ring][(start + offset) % length], connector)
            attachments[ring] += 1
        share(left, right)
        chain = append_knots(3) if detour else ()
        holding_order = (left, *chain, right)
        for first, second in zip(holding_order, holding_order[1:]):
            share(first, second)
            if detour:
                share(first, second)
        if detour and pair == (0, 1):
            first_middle = chain[1]
    if middle_loose:
        share(first_middle)

    return knots, rings


def named_reads(knots, rings):
    """Find the two settings per reader in A, M, B order by holding."""
    left_ring, right_ring = rings[:2]
    left = set().union(*(knots[knot] for knot in left_ring))
    right = set().union(*(knots[knot] for knot in right_ring))
    middle = set().union(*knots) - left - right
    assert left.isdisjoint(right)
    assert all(not (knot & left and knot & right) for knot in knots)

    attached_left = [knot for knot in knots if knot & left and knot & middle]
    attached_right = [knot for knot in knots if knot & right and knot & middle]
    (left_law, right_law), = [
        (a, b) for a in attached_left for b in attached_right if a & b
    ]
    shared_link = min(left_law & right_law)
    left_attachment = min(left_law & left)
    right_attachment = min(right_law & right)
    holders = Counter(d for knot in knots for d in knot)

    def loose(members, attachment):
        owner, = [knots[knot] for knot in members if attachment in knots[knot]]
        return min(d for d in owner if holders[d] == 1)

    change_through_link = (
        loose(left_ring, left_attachment), left_attachment, shared_link,
        right_attachment, loose(right_ring, right_attachment),
    )
    change = set(change_through_link)
    regions = (left, middle, right)
    read_pairs = []
    for region, law in zip(regions, (left_law, left_law, right_law)):
        changed = change & region
        value = law & region
        # Exactly one shared distinction supplies the i in the quarter-turn read.
        assert len(changed & value) == 1
        read_pairs.append(((mask(changed), 0, 0), (mask(changed), mask(value), 1)))

    return change_through_link, (left_law, right_law), regions, read_pairs


def parity_system(knots):
    """Eliminate homogeneous laws and construct one allowed word per free bit."""
    laws = tuple(map(mask, knots))
    width = max(laws).bit_length()
    pivots = {}
    for law in laws:
        while law:
            pivot = law.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = law
                break
            law ^= pivots[pivot]

    allowed_directions = []
    for index in range(width):
        if index in pivots:
            continue
        word = 1 << index
        for pivot, equation in sorted(pivots.items()):
            if (word & equation).bit_count() % 2:
                word |= 1 << pivot
        assert all((word & law).bit_count() % 2 == 0 for law in laws)
        allowed_directions.append(word)
    return laws, width, allowed_directions


def projected_words(directions, value_support):
    """A linear projection gives equal multiplicity to every projected word."""
    words = {0}
    for direction in directions:
        projection = direction & value_support
        words |= {word ^ projection for word in words}
    return words


def projector_probability(reads, answers, allowed_projections, laws):
    """Average the diagonal and translated terms of three local projectors.

    Apply each I + answer*read to a word, tracking only its displacement.
    Terms translating it to an illegal word have zero overlap with the state.
    The Gaussian integers below are at most eight units per projected word.
    """
    total = 0
    for word in allowed_projections:
        translated = {0: 1}
        for answer, (change, values, phase) in zip(answers, reads):
            updated = translated.copy()
            for shift, amplitude in translated.items():
                sign = -1 if ((word ^ shift) & values).bit_count() % 2 else 1
                moved = shift ^ change
                updated[moved] = updated.get(moved, 0) + answer * sign * PHASE[phase] * amplitude
            translated = updated
        total += sum(
            amplitude for shift, amplitude in translated.items()
            if all((shift & law).bit_count() % 2 == 0 for law in laws)
        )
    assert total.imag == 0 and total.real == int(total.real)
    return Fraction(int(total.real), 8 * len(allowed_projections))


def product_mean(reads, directions, laws):
    """Check the product separately by character cancellation on allowed words."""
    changed, values, phase = (sum(parts) for parts in zip(*reads))
    if any((changed & law).bit_count() % 2 for law in laws):
        return 0
    if any((values & direction).bit_count() % 2 for direction in directions):
        return 0
    assert phase % 2 == 0
    return (-1) ** (phase // 2)


def contact_list(settings, certainties):
    """The middle receives both ring settings and the list's fair signs."""
    counts = Counter()
    for left, independent, right in ANSWERS:
        target = certainties[settings]
        middle = target * left * right if target else independent
        counts[(left, middle, right)] += 1
    return {answer: Fraction(counts[answer], len(ANSWERS)) for answer in ANSWERS}


def one_message_list(settings, certainties):
    """Only the first ring gives its setting to the middle."""
    a, m, b = settings
    predicted_b = a ^ m
    target = certainties[(a, m, predicted_b)]
    counts = Counter()
    for left, b0, b1, independent in product((1, -1), repeat=4):
        right_answers = (b0, b1)
        middle = target * left * right_answers[predicted_b] if target else independent
        counts[(left, middle, right_answers[b])] += 1
    return {answer: Fraction(counts[answer], 16) for answer in ANSWERS}


def loose_local_list(settings):
    """Every output uses only the reader's own setting and shared fair signs."""
    a, m, b = settings
    counts = Counter()
    for a0, a1, b0, b1 in product((1, -1), repeat=4):
        middle_answers = (a0 * b0, -a1 * b0)
        counts[((a0, a1)[a], middle_answers[m], (b0, b1)[b])] += 1
    return {answer: Fraction(counts[answer], 16) for answer in ANSWERS}


def loose_quantum_control(laws, directions, regions, right_law, right_reads):
    """Use alternative local observables on the loose-chain starting state."""
    middle_change = {54, 56, 84}
    middle_value = right_law & regions[1]
    assert middle_change <= regions[1] and len(middle_change & middle_value) == 1
    assert right_reads[1][0] & right_reads[1][1] != 0
    middle_paulis = ((mask(middle_change), 0, 0), (0, mask(middle_value), 0))
    right_paulis = (right_reads[0], (0, right_reads[1][1], 0))
    means = [[product_mean((m, b), directions, laws) for b in right_paulis] for m in middle_paulis]
    assert means == [[1, 0], [0, 1]]

    # A always gives +1. The two middle reads combine its anticommuting
    # X and Z with these coefficients, normalized by sqrt(2).
    coefficients = ((1, -1), (-1, -1))
    correlations = {
        "".join(map(str, (a, m, b))): sum(c * pair[b] for c, pair in zip(coefficients[m], means))
        for a, m, b in SCORED
    }
    assert all(correlations["".join(map(str, setting))] == target for setting, target in SCORED.items())
    return {
        "middle change and value supports": [sorted(middle_change), sorted(middle_value)],
        "right change and value supports": [distinctions(right_paulis[0][0]), distinctions(right_paulis[1][1])],
        "middle-right Pauli means in X,Z order": means,
        "scored product means in units of 1/sqrt(2)": correlations,
        "game score with alternative standard quantum observables": "1/2 + 1/(2 sqrt(2))",
    }


def local_score_histogram():
    """Count each fixed answer list by wins among the four scored settings."""
    counts = Counter()
    for answers in product((1, -1), repeat=6):
        wins = sum(
            prod(answers[2 * i + setting] for i, setting in enumerate(settings)) == target
            for settings, target in SCORED.items()
        )
        counts[wins] += 1
    return dict(sorted(counts.items()))


def game(family):
    label, length, detour, middle_loose = family
    knots, rings = build_start(length, detour, middle_loose)
    change, linking_laws, regions, read_pairs = named_reads(knots, rings)
    laws, width, directions = parity_system(knots)
    value_support = sum(pair[1][1] for pair in read_pairs)
    words = projected_words(directions, value_support)
    table = {}
    certainties = {}
    for settings in SETTINGS:
        reads = tuple(pair[setting] for pair, setting in zip(read_pairs, settings))
        probabilities = {
            answer: projector_probability(reads, answer, words, laws) for answer in ANSWERS
        }
        assert sum(probabilities.values()) == 1 and min(probabilities.values()) >= 0
        table[settings] = probabilities
        certainty = sum(prod(answer) * chance for answer, chance in probabilities.items())
        assert certainty in (-1, 0, 1) and certainty == product_mean(reads, directions, laws)
        certainties[settings] = int(certainty)

    marginal_history = {}
    setting_rows = {}
    win_sum = Fraction(0)
    for settings, probabilities in table.items():
        target = SCORED.get(settings)
        win = sum(p for answer, p in probabilities.items() if prod(answer) == target) if target else None
        if win is not None:
            win_sum += win
        marginal_row = {}
        for keep in GROUPS:
            reduced = Counter()
            for answer, chance in probabilities.items():
                reduced[tuple(answer[i] for i in keep)] += chance
            local_settings = tuple(settings[i] for i in keep)
            marginal_history.setdefault((keep, local_settings), []).append(reduced)
            assert all(chance == Fraction(1, 2 ** len(keep)) for chance in reduced.values())
            group = "".join(READERS[i] for i in keep)
            marginal_row[group] = [str(reduced[outcome]) for outcome in product((1, -1), repeat=len(keep))]
        setting_rows["".join(map(str, settings))] = {
            "three-reader product mean": certainties[settings],
            "probabilities": [str(probabilities[answer]) for answer in ANSWERS],
            "winning probability": str(win) if win is not None else None,
            "marginals": marginal_row,
        }

    assert all(all(row == rows[0] for row in rows) for rows in marginal_history.values())
    assert all(contact_list(s, certainties) == table[s] for s in SETTINGS)
    assert all(one_message_list(s, certainties) == table[s] for s in SETTINGS)
    quantum_control = None
    if middle_loose:
        assert all(loose_local_list(s) == table[s] for s in SETTINGS)
        quantum_control = loose_quantum_control(laws, directions, regions, linking_laws[1], read_pairs[2])

    return {
        "family": label,
        "knots": len(knots),
        "distinctions": width,
        "allowed word count": 1 << len(directions),
        "projected word count": len(words),
        "reader sizes": list(map(len, regions)),
        "ordered change through the first pair's link": change,
        "connecting knots' laws": list(map(sorted, linking_laws)),
        "reads": {
            reader: [dict(change=distinctions(x), value=distinctions(z), i_exponent=p) for x, z, p in pair]
            for reader, pair in zip(READERS, read_pairs)
        },
        "win with all four scored settings equally weighted": str(win_sum / len(SCORED)),
        "settings": setting_rows,
        "probabilities nonnegative, normalized, and proper marginals independent of omitted settings": True,
        "contact list matches all 64 answer probabilities": True,
        "list where only the first ring reports its setting to the middle matches all 64 answer probabilities": True,
        "loose-chain setting-local list matches all 64 answer probabilities": True if middle_loose else None,
        "alternative loose-chain quantum strategy": quantum_control,
    }


def compare_archive(rows):
    path = Path(__file__).resolve().parents[1] / "tripartite_out.jsonl.gz"
    field = "the three-reader game, rings 0 and 1 and the middle"
    with gzip.open(path, "rt") as archive:
        source = {row["family"]: row[field] for row in map(json.loads, archive) if field in row}
    assert source.keys() == {row["family"] for row in rows}
    checked = 0
    for row in rows:
        archived = source[row["family"]]
        assert archived["win"] == row["win with all four scored settings equally weighted"]
        for settings, results in row["settings"].items():
            for answer, rebuilt in zip(ANSWERS, results["probabilities"]):
                signs = "".join("+" if sign == 1 else "-" for sign in answer)
                assert Fraction(archived["table"][settings].get(signs, "0")) == Fraction(rebuilt)
                checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--pilot", action="store_true")
    modes.add_argument("--compare-archive", action="store_true")
    args = parser.parse_args()
    started = perf_counter()
    rows = [game(case) for case in (FAMILIES[-1:] if args.pilot else FAMILIES)]
    histogram = local_score_histogram()
    assert max(histogram) == 3 and sum(histogram.values()) == 64
    archive_checked = compare_archive(rows) if args.compare_archive else None
    summary = {
        "order": READERS,
        "settings": ["X", "Y"],
        "answer order": ["".join("+" if sign == 1 else "-" for sign in answer) for answer in ANSWERS],
        "marginal array order": "same sign ordering as the full probability arrays, restricted to the kept readers",
        "deterministic lists by number of scored settings won": histogram,
        "quantum game optimum": "1 (attained on the three closed-link families)",
        "archive probabilities matched after reconstruction": archive_checked,
        "elapsed_seconds": round(perf_counter() - started, 6),
        "peak_resident_kib": getrusage(RUSAGE_SELF).ru_maxrss,
        "families": rows,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
