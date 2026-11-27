"""Signed local game on the parity words. Run from the repository root."""

import argparse
import hashlib
import itertools
import json
import resource
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import NamedTuple


HERE = Path(__file__).resolve().parent


def dot(a, b):
    return (a & b).bit_count() & 1


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def pivots(equations, columns):
    """Gauss-Jordan elimination in an explicit order of columns."""
    pending = list(equations)
    finished = {}
    for column in columns:
        index = next((i for i, row in enumerate(pending) if row & column), None)
        if index is None:
            continue
        row = pending.pop(index)
        pending = [r ^ row if r & column else r for r in pending]
        for previous, r in finished.items():
            if r & column:
                finished[previous] = r ^ row
        finished[column] = row
    assert not any(pending)
    return finished


def image(generators, character):
    """One representative per image element. Used only for two sign bits."""
    chosen = {0: 0}
    for g in generators:
        for c, rep in list(chosen.items()):
            chosen.setdefault(c ^ character(g), rep ^ g)
    return chosen


class Read(NamedTuple):
    x: int = 0
    z: int = 0
    sign: int = 0


def times(p, q):
    # A read is (-1)^sign X^x Z^z with Z acting first.
    return Read(p.x ^ q.x, p.z ^ q.z, p.sign ^ q.sign ^ dot(p.z, q.x))


def local_game_rows(x1, x2, z1, z2):
    return [
        [Read(x1), Read(x2), Read(x1 ^ x2)],
        [Read(z=z2), Read(z=z1), Read(z=z1 ^ z2)],
        [Read(x1, z2), Read(x2, z1), Read(x1 ^ x2, z1 ^ z2, 1)],
    ]


def context_sign(reads):
    assert all(times(p, p) == Read() for p in reads)
    assert all(times(p, q) == times(q, p) for p, q in itertools.combinations(reads, 2))
    whole = times(times(reads[0], reads[1]), reads[2])
    assert whole.x == whole.z == 0
    return whole.sign


def subproducts(reads):
    products = [Read()]
    for read in reads:
        products.extend([times(previous, read) for previous in products])
    return products


def outcome_weights(moments):
    # The first two answers of each context determine its third. Denominator 16.
    weights = [sum(-v if dot(answer, mask) else v for mask, v in enumerate(moments))
               for answer in range(16)]
    assert sum(weights) == 16 and min(weights) >= 0
    return weights


def answers(pair, parity):
    a, b = pair & 1, pair >> 1
    return [a, b, a ^ b ^ parity]


def list_histogram():
    def lists(parities):
        return itertools.product(*[[answers(pair, p) for pair in range(4)] for p in parities])

    histogram = Counter()
    for a, b in itertools.product(lists([0, 0, 0]), lists([0, 0, 1])):
        histogram[sum(a[r][c] == b[c][r] for r in range(3) for c in range(3))] += 1
    assert sum(histogram.values()) == 4096 and max(histogram) == 8
    return dict(sorted(histogram.items()))


def check_case(case, explicit_words=False):
    knots = case["knots"]
    a_names, b_names = set(case["A"]), set(case["B"])
    universe = set().union(*map(set, knots))
    assert a_names.isdisjoint(b_names) and a_names | b_names <= universe
    assert all(not (a_names.intersection(k) and b_names.intersection(k)) for k in knots)
    names = sorted(universe)
    index = {d: 1 << i for i, d in enumerate(names)}

    def mask(identities):
        identities = list(identities)
        assert len(identities) == len(set(identities))
        return sum(index[d] for d in identities)

    def members(v):
        return [names[bit.bit_length() - 1] for bit in bits(v)]

    a, b = mask(a_names), mask(b_names)
    y = a | b
    m = mask(universe) ^ y
    laws = [mask(k) for k in knots]
    reduced = pivots(laws, [*bits(m), *bits(y)])
    middle = {p: h for p, h in reduced.items() if p & m}
    local = {p: h for p, h in reduced.items() if p & y}
    assert all(h & m == 0 for h in local.values())
    changes = [f | sum(p for p, h in local.items() if f & h)
               for f in bits(y ^ sum(local))]
    assert all(not dot(x, z) for x in changes for z in local.values())

    def a_pairings(z):
        return sum(dot(z & a, x) << i for i, x in enumerate(changes))

    pairings = {z: a_pairings(z) for z in local.values()}
    independent = pivots(pairings.values(), (1 << i for i in range(len(changes))))
    e = len(independent)
    if e != 2:
        return {"e": e}
    z1 = next(z for z, w in pairings.items() if w)
    z2 = next(z for z, w in pairings.items() if w and w != pairings[z1])
    changes_by_pair = image(changes, lambda x: dot(z1, x & a) + 2 * dot(z2, x & a))
    x1, x2 = changes_by_pair[1], changes_by_pair[2]
    for side in (a, b):
        assert [[dot(x & side, z) for z in (z1, z2)] for x in (x1, x2)] == [[1, 0], [0, 1]]
    x_span = (0, x1, x2, x1 ^ x2)

    # Pick actual middle completions for the two changes and verify on the input knots.
    completions = [sum(p for p, h in middle.items() if dot(h, x)) for x in (x1, x2)]
    for x, t in zip((x1, x2), completions):
        assert all(not dot(x | t, h) for h in laws)

    def signs(h):
        character = dot(h & y, x1) + 2 * dot(h & y, x2)
        assert character == dot(h & m, completions[0]) + 2 * dot(h & m, completions[1])
        return character

    # Full records are middle restrictions of law sums; one independent row per middle pivot.
    representatives = image(middle.values(), signs)
    assert set(representatives) == {0, 1, 2, 3}
    tables = [local_game_rows(*(v & side for v in (x1, x2, z1, z2))) for side in (a, b)]
    for table in tables:
        assert [context_sign(row) for row in table] == [0, 0, 0]
        assert [context_sign(col) for col in zip(*table)] == [0, 0, 1]
        # Omitting the explicit bottom-right sign gives a different legal sign convention.
        plain = [row[:] for row in table]
        plain[2][2] = plain[2][2]._replace(sign=0)
        assert [context_sign(row) for row in plain] == [0, 0, 1]
        assert [context_sign(col) for col in zip(*plain)] == [0, 0, 0]

    def supports(p):
        return all(not dot(z, p.x) for z in local.values()) and all(not dot(x, p.z) for x in changes)

    # A literal sum over allowed words on a six-distinction fixture checks the branch formula.
    def explicit_moments(h, products):
        words = [w for w in range(1 << len(names)) if all(not dot(w, z) for z in laws)]
        amplitudes = Counter()
        for w in words:
            amplitudes[w & y] += (-1) ** dot(w & m, h)
        norm = sum(v * v for v in amplitudes.values())
        assert norm
        result = []
        for p in products:
            numerator = sum(v * amplitudes.get(w ^ p.x, 0) * (-1) ** (p.sign ^ dot(p.z, w))
                            for w, v in amplitudes.items())
            assert numerator % norm == 0
            result.append(numerator // norm)
        return result

    scores = Counter()
    corrected_scores = Counter()
    unread_score = 0
    margins = {}
    for r, c in itertools.product(range(3), repeat=2):
        row, col = tables[0][r], [tables[1][i][c] for i in range(3)]
        products = subproducts([*row[:2], *col[:2]])
        eligible = [supports(p) for p in products]
        assert all(p.x in x_span for p, yes in zip(products, eligible) if yes)
        conditional = []
        for signs_key, h in sorted(representatives.items()):
            moments = [(-1) ** (p.sign ^ dot(h & y, p.x)) if yes else 0
                       for p, yes in zip(products, eligible)]
            if explicit_words:
                assert moments == explicit_moments(h, products)
            weights = outcome_weights(moments)
            conditional.append(weights)
            assert Counter(weights) == {0: 8, 2: 8}
            flips = [signs_key & 1, signs_key >> 1, dot(signs_key, 3)]
            row_flips = flips if r != 1 else [0, 0, 0]
            expected_flip = row_flips[c]
            agree = 0
            corrected_agree = 0
            for answer, weight in enumerate(weights):
                left_answers = answers(answer & 3, 0)
                corrected_answers = [v ^ flip for v, flip in zip(left_answers, row_flips)]
                assert sum(corrected_answers) % 2 == 0
                left = left_answers[c]
                right = answers(answer >> 2, int(c == 2))[r]
                if weight:
                    assert left ^ right == expected_flip
                agree += weight * (left == right)
                corrected_agree += weight * (corrected_answers[c] == right)
            scores[signs_key] += agree // 16
            corrected_scores[signs_key] += corrected_agree // 16
            assert agree in (0, 16) and corrected_agree == 16
            # The middle's two signs flip an even number of outputs of any local context.
            assert sum(flips) % 2 == 0 and (flips[c] ^ 0 ^ flips[c]) == 0
            for party, setting, extract in (("A", r, lambda n: n & 3), ("B", c, lambda n: n >> 2)):
                marginal = [sum(w for n, w in enumerate(weights) if extract(n) == v) for v in range(4)]
                key = (signs_key, party, setting)
                assert margins.setdefault(key, marginal) == marginal == [4] * 4
        # Also calculate the raw unsorted table directly on the original full word space.
        unread = outcome_weights([
            (-1) ** p.sign if yes and all(not dot(p.x, z) for z in laws) else 0
            for p, yes in zip(products, eligible)
        ])
        assert [4 * w for w in unread] == [sum(ws) for ws in zip(*conditional)]
        unread_score += sum(w for n, w in enumerate(unread)
                            if answers(n & 3, 0)[c] == answers(n >> 2, int(c == 2))[r])
    assert [scores[k] for k in range(4)] == [9, 5, 5, 5] and unread_score == 96
    assert set(corrected_scores.values()) == {9}
    return {
        "e": e,
        "number_of_distinctions": len(names),
        "middle_record_rank": len(middle),
        "records_per_sign_pair": 2 ** (len(middle) - 2),
        "change_reads": [{"A": members(x & a), "B": members(x & b), "middle_completion": members(t)}
                         for x, t in zip((x1, x2), completions)],
        "value_reads": [{"A": members(z & a), "B": members(z & b)} for z in (z1, z2)],
        "example_middle_records_by_sign_pair": {
            f"{k & 1}{k >> 1}": members(h & m) for k, h in sorted(representatives.items())
        },
        "ordinary_wins_of_nine_by_sign_pair": {f"{k & 1}{k >> 1}": scores[k] for k in range(4)},
        "ordinary_unread_score": str(Fraction(unread_score, 9 * 16)),
        "corrected_wins_of_nine_by_sign_pair": {
            f"{k & 1}{k >> 1}": corrected_scores[k] for k in range(4)
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="check just the first supplied arrangement")
    parser.add_argument("--fixture-only", action="store_true")
    args = parser.parse_args()
    started = time.process_time()
    wall = time.perf_counter()
    toy = {"knots": [[0, 4], [2, 4], [1, 5], [3, 5]], "A": [0, 1], "B": [2, 3]}
    result = {
        "classical_list_count_by_winning_settings": list_histogram(),
        "six_distinction_explicit_amplitude_control": check_case(toy, explicit_words=True),
    }
    if not args.fixture_only:
        data = (HERE / "joined_square_inputs.json").read_bytes()
        inputs = json.loads(data)
        result["input_sha256"] = hashlib.sha256(data).hexdigest()
        result["cases"] = []
        for item in inputs[:1] if args.pilot else inputs:
            checked = check_case(item)
            checked.update({k: item[k] for k in ("family", "round", "choice")})
            result["cases"].append(checked)
        if not args.pilot:
            found = {(row["family"], row["round"], row["choice"]) for row in result["cases"] if row["e"] == 2}
            families = sorted({family for family, _, _ in found})
            assert len(found) == 18 and found == set(itertools.product(families, range(3), ("places", "own")))
    result["cpu_seconds"] = round(time.process_time() - started, 6)
    result["wall_seconds"] = round(time.perf_counter() - wall, 6)
    result["maximum_resident_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
