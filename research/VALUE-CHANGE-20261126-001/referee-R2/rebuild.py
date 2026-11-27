"""Rebuild the direct-link start and the joint law of its three readers.

No probability, sign, rank, or verdict is taken from the study. Its selector
supplies only the supports of the questions, to audit the questions it chose.
Run with -B. Bit 1 in a read record means answer -1.
"""
import argparse
from collections import Counter
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def direct_links():
    # Rebuild using the published distinction numbers, so masks can be compared.
    knots = [[] for _ in range(21)]
    next_name = 0

    def add(*holders):
        nonlocal next_name
        for holder in holders:
            knots[holder].append(next_name)
        next_name += 1

    for start in (0, 5, 10):
        for i in range(5):
            add(start + i, start + (i + 1) % 5)
    for k in range(15):
        add(k)
        add(k)
    ports = [0, 0, 0]
    for j, (r, s) in enumerate(combinations(range(3), 2)):
        c = 15 + 2 * j
        for ring, connector in ((r, c), (s, c + 1)):
            p = ports[ring]
            ports[ring] += 1
            add(5 * ring + p, connector)
            add(5 * ring + (p + 2) % 5, connector)
        add(c, c + 1)
        add(c, c + 1)
    assert next_name == 63
    return knots


def bits(mask):
    return [i for i in range(mask.bit_length()) if mask >> i & 1]


def mask(names):
    return sum(1 << i for i in names)


def parity(x):
    return x.bit_count() % 2


def remainder(vector, pivots):
    for row in pivots:
        vector = min(vector, vector ^ row)
    return vector


def law_basis(knots):
    pivots = []
    for knot in knots:
        row = remainder(mask(knot), pivots)
        if row:
            pivots.append(row)
            pivots.sort(reverse=True)
    return pivots


def question_supports(knots, a, b):
    # square() exposes only two summary fields. Take its chosen masks from
    # the return frame, before applying any of our sign or probability rules.
    spec = spec_from_file_location("study_questions", HERE.parent / "css.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    selected = {}

    def on_return(frame, event, arg):
        if event == "return" and frame.f_code is module.square.__code__:
            for key in ("names", "X1", "X2", "Z1", "Z2", "cells"):
                selected[key] = frame.f_locals[key]

    previous = sys.getprofile()
    try:
        sys.setprofile(on_return)
        module.square(knots, bits(a), bits(b))
    finally:
        sys.setprofile(previous)

    def named_mask(value):
        return mask(selected["names"][i] for i in bits(value))
    gens = [named_mask(selected[k]) for k in ("X1", "X2", "Z1", "Z2")]
    cells = [[(named_mask(x), named_mask(z), int((i, j) == (2, 2)))
              for j, (x, z) in enumerate(row)] for i, row in enumerate(selected["cells"])]
    return gens, cells


# A real Pauli product is (-1)^s X^x Z^z, in precisely that order.
def multiply(p, q):
    x, z, s = p
    u, v, t = q
    return x ^ u, z ^ v, s ^ t ^ parity(z & u)


def on_reader(cell, reader):
    x, z, sign = cell
    return x & reader, z & reader, sign


def expand_middle(m, middle):
    return mask(d for i, d in enumerate(middle) if (m >> i) & 1)


def prepare():
    knots = direct_links()
    ring = [mask(set().union(*knots[start:start + 5])) for start in (0, 5, 10)]
    a, b = ring[0] | ring[2], ring[1]
    assert not (a & b)
    assert all(not (mask(k) & a and mask(k) & b) for k in knots)
    middle = bits(((1 << 63) - 1) ^ (a | b))
    laws = law_basis(knots)
    gens, cells = question_supports(knots, a, b)
    x1, x2, z1, z2 = gens

    def allowed(x):
        return all(not parity(x & law) for law in laws)

    lifts = []
    for x in (x1, x2):
        lift = next(m for m in range(1 << len(middle))
                    if allowed(x | expand_middle(m, middle)))
        lifts.append(lift)
    for i, x in enumerate((x1, x2)):
        for j, z in enumerate((z1, z2)):
            assert remainder(z, laws) == 0
            assert parity(x & z & a) == parity(x & z & b) == int(i == j)

    # An open loose distinction absent from both changes, and one A distinction
    # present in a change. Their relative phase will be varied independently.
    holders = Counter(d for k in knots for d in k)
    quiet = next(d for d in bits(a & ~(x1 | x2)) if holders[d] == 1
                 and remainder(1 << d, laws))
    active = next(d for d in bits(a & (x1 | x2)) if remainder(1 << d, laws))
    assert a.bit_count() == 38 and b.bit_count() == 19 and len(middle) == 6
    return laws, gens, cells, lifts, a, b, middle, quiet, active


def contexts(cells, a, b, i, j, middle):
    row = [on_reader(cell, a) for cell in cells[i]]
    column = [on_reader(line[j], b) for line in cells]
    all_reads = row + column + [(1 << d, 0, 0) for d in middle]
    for p, q in combinations(all_reads, 2):
        assert multiply(p, q) == multiply(q, p)
    assert all(multiply(p, p) == (0, 0, 0) for p in all_reads)
    assert multiply(multiply(row[0], row[1]), row[2]) == (0, 0, 0)
    assert multiply(multiply(column[0], column[1]), column[2]) == (0, 0, int(j == 2))
    return all_reads


def outcome_weights(reads, laws, state, quiet, active):
    # Walsh inversion of the complete set of commuting product expectations.
    products = [(0, 0, 0)]
    for read in reads:
        products += [multiply(p, read) for p in products]
    weights = []
    for x, z, s in products:
        survives = not any(parity(x & law) for law in laws) and not remainder(z, laws)
        if state == "mixture":
            survives = survives and x == 0
        elif state == "quiet sign":
            s ^= (x >> quiet) & 1
        elif state == "active sign":
            s ^= (x >> active) & 1
        elif state == "active quarter turn" and (x >> active) & 1:
            # Diag(1,i) conjugates this real Hermitian product to a purely
            # imaginary Hermitian product. Its expectation on a real vector is 0.
            survives = False
        weights.append((1 - 2 * s) if survives else 0)

    half = 1
    while half < len(weights):
        for base in range(0, len(weights), 2 * half):
            for left in range(base, base + half):
                right = left + half
                u, v = weights[left], weights[right]
                weights[left], weights[right] = u + v, u - v
        half *= 2
    assert min(weights) >= 0 and sum(weights) == len(weights)
    return {(k & 7, (k >> 3) & 7, k >> 6): w
            for k, w in enumerate(weights) if w}


def marginal(table, keep):
    counts = Counter()
    for record, weight in table.items():
        counts[tuple(record[k] for k in keep)] += weight
    return counts


def compare_contexts(tables):
    # All proper subsets of A,B,M, including the empty record. Equality is
    # required between settings agreeing on the retained readers' settings.
    for size in range(3):
        for keep in combinations(range(3), size):
            seen = {}
            for setting, joint in tables.items():
                key = tuple(setting[k] for k in keep if k < 2)
                counts = marginal(joint, keep)
                assert counts == seen.setdefault(key, counts)


def check_sorted(tables):
    # Repeat the tests after conditioning, with exact normalization; keep the
    # whole three-bit reader record even if it has the wrong line parity.
    middles = {m for table in tables.values() for _, _, m in table}
    for m in middles:
        conditional = {}
        for setting, table in tables.items():
            keep = {q: w for q, w in table.items() if q[2] == m}
            total = sum(keep.values())
            assert total
            conditional[setting] = {q: Fraction(w, total) for q, w in keep.items()}
        compare_contexts(conditional)


def correct_answers(raw, i, cells, lifts, gens, extra=0):
    x1, x2 = gens[:2]
    x_lifts = {0: 0, x1: lifts[0], x2: lifts[1], x1 ^ x2: lifts[0] ^ lifts[1]}
    corrected = {}
    for (a, b, m), weight in raw.items():
        flips = sum((parity(x_lifts[x] & m) ^ parity(extra & x)) << j
                    for j, (x, z, sign) in enumerate(cells[i]))
        assert parity(flips) == 0
        corrected[a ^ flips, b, m] = weight
    assert sum(raw.values()) == sum(corrected.values())
    return corrected


def win(i, j, a, b):
    return parity(a) == 0 and parity(b) == int(j == 2) and ((a >> j) ^ (b >> i)) & 1 == 0


def scores(tables):
    all_weight = Counter()
    wins = Counter()
    for (i, j), table in tables.items():
        for (a, b, m), w in table.items():
            all_weight[m] += w
            wins[m] += w * win(i, j, a, b)
    return (str(Fraction(sum(wins.values()), sum(all_weight.values()))),
            {m: str(Fraction(wins[m], total)) for m, total in sorted(all_weight.items())})


def reader_table(counts):
    return [[int(counts.get((a, b), 0)) for b in range(8)] for a in range(8)]


def full_tables(raw, corrected, middle, gens, lifts):
    details = {
        "family": "Three rings of five, direct links, before growth, all places of each ring",
        "preparation": "coherent counting state; combined questions; middle reader measuring changes and sorting",
        "encoding": "Settings are zero-based. Answer bit j is 1 for sign -1 on read j, least significant bit first. Matrices are indexed by A's whole answer then B's. Absent middle records have probability zero.",
        "middle_distinctions_least_significant_first": middle,
        "supports_in_order_X1_X2_Z1_Z2": [bits(g) for g in gens],
        "middle_lift_masks_X1_X2": lifts,
        "settings": [],
    }
    for (i, j), t in raw.items():
        c = corrected[i, j]
        weight = sum(t.values())
        tm, cm = marginal(t, (2,)), marginal(c, (2,))
        assert tm == cm
        entry = {"row": i, "column": j, "joint_denominator": weight,
                 "raw_unsorted": reader_table(marginal(t, (0, 1))),
                 "corrected_unsorted": reader_table(marginal(c, (0, 1))),
                 "by_middle_record": {}}
        for (m,), total in sorted(tm.items()):
            local = {(a, b): v for (a, b, k), v in t.items() if k == m}
            calibrated = {(a, b): v for (a, b, k), v in c.items() if k == m}
            assert total == weight // 8 and len(local) == len(calibrated) == 8
            assert set(local.values()) == set(calibrated.values()) == {total // 8}
            for pair_table in (local, calibrated):
                for reader in range(2):
                    marginal_counts = marginal(pair_table, (reader,))
                    assert len(marginal_counts) == 4
                    assert set(marginal_counts.values()) == {total // 4}
            entry["by_middle_record"][str(m)] = {
                "conditional_denominator": total, "raw": reader_table(local),
                "corrected": reader_table(calibrated)}
        details["settings"].append(entry)
    return details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="One setting at the full configuration")
    parser.add_argument("--tables", action="store_true", help="Save all coherent-state tables")
    args = parser.parse_args()
    if args.pilot and args.tables:
        parser.error("Use --tables for the full nine-setting run")
    laws, gens, cells, lifts, a, b, middle, quiet, active = prepare()
    print("Independent laws:", len(laws), "allowed words:", 2 ** (63 - len(laws)))
    print("Middle:", middle, "lift masks:", lifts, "phase distinctions (quiet, active):", quiet, active)
    print("Question supports (X1, X2, Z1, Z2):", [bits(g) for g in gens])
    settings = [(2, 2)] if args.pilot else list(product(range(3), repeat=2))
    coherent_tables = None
    for state in ("coherent", "mixture", "quiet sign", "active sign", "active quarter turn"):
        raw, corrected, recalibrated = {}, {}, {}
        for i, j in settings:
            reads = contexts(cells, a, b, i, j, middle)
            t = outcome_weights(reads, laws, state, quiet, active)
            raw[i, j] = t
            assert all(parity(aa) == 0 and parity(bb) == int(j == 2) for aa, bb, m in t)
            corrected[i, j] = correct_answers(t, i, cells, lifts, gens)
            if state == "active sign":
                recalibrated[i, j] = correct_answers(t, i, cells, lifts, gens, 1 << active)
        for tables in (raw, corrected):
            compare_contexts(tables)
            check_sorted(tables)
        raw_score, per_m = scores(raw)
        score, _ = scores(corrected)
        print(state, "raw:", raw_score, "sorted & calibrated:", score,
              "raw scores by middle (counts):", dict(Counter(per_m.values())))
        if state == "coherent":
            coherent_tables = full_tables(raw, corrected, middle, gens, lifts)
            if not args.pilot:
                assert score == "1" and raw_score == "2/3"
                print("Raw scores by record:", per_m)
                print("Raw joint support per setting:", [len(t) for t in raw.values()])
        if state == "quiet sign":
            assert full_tables(raw, corrected, middle, gens, lifts) == coherent_tables
        if state == "active sign":
            assert scores(recalibrated)[0] == "1"
        if not args.pilot:
            expected = {"coherent": "1", "quiet sign": "1", "active sign": "5/9",
                        "active quarter turn": "7/9", "mixture": "2/3"}
            assert score == expected[state]
    if args.tables:
        with (HERE / "tables.json").open("w") as f:
            json.dump(coherent_tables, f, separators=(",", ":"))
            f.write("\n")


if __name__ == "__main__":
    main()
