"""Decide the carried six agreements on the full stage, including each deletion."""

import argparse
import gzip
import json
import resource
import time
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
NAMED = ((3, 4, 5), (11, 12, 13), (0, 1, 10), (6, 15, 16), (7, 8, 9), (2, 14))
DEFINING = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
WORDS = tuple(product((0, 1), repeat=6))


def chain_carriers(supports, chain):
    knots = [set(supports[i]) for i in chain]
    common = [(a & b).pop() for a, b in zip(knots, knots[1:])]
    assert len(set(common)) == 7
    shared = set(common)
    labels = sorted(knots[0] - shared)
    for i in range(1, 7):
        labels.append(common[i - 1])
        only, = knots[i] - shared
        labels.append(only)
    labels.append(common[-1])
    labels.extend(sorted(knots[-1] - shared))
    assert len(labels) == len(set(labels)) == 17
    return tuple(tuple(sorted(labels[j] for j in carrier)) for carrier in NAMED)


class Formula:
    """Build supplementary equivalences once, with distinct Boolean variables."""

    def __init__(self, raw_count):
        self.next_id = raw_count
        self.solver = Solver()
        self.agreements = {}
        self.eithers = {}

    def new(self):
        self.next_id += 1
        return self.next_id

    def not_all_equal(self, members, enabled=None):
        guard = [] if enabled is None else [-enabled]
        self.solver.add_clause(guard + list(members))
        self.solver.add_clause(guard + [-x for x in members])

    def agree(self, members):
        if members in self.agreements:
            return self.agreements[members]
        out = self.new()
        # The two constant words force agreement. Every differing pair forbids it.
        self.solver.add_clause([out, *members])
        self.solver.add_clause([out, *(-x for x in members)])
        first = members[0]
        for member in members[1:]:
            self.solver.add_clause([-out, first, -member])
            self.solver.add_clause([-out, -first, member])
        self.agreements[members] = out
        return out

    def either(self, a, b):
        key = tuple(sorted((a, b)))
        if key not in self.eithers:
            out = self.new()
            self.solver.add_clause([-out, a, b])
            self.solver.add_clause([out, -a])
            self.solver.add_clause([out, -b])
            self.eithers[key] = out
        return self.eithers[key]

    def allows(self, literals):
        return self.solver.solve(assumptions=literals)


def tuple_index(values):
    result = 0
    for value in values:
        result = 2 * result + value
    return result


def upper_values(word, both):
    return tuple((a & b) if pair == both else (a | b)
                 for pair, (a, b) in enumerate(zip(word[::2], word[1::2])))


def word_information(word):
    lower = [tuple_index(word[i] for i in group) for group in DEFINING]
    upper = [tuple_index(upper_values(word, both)) for both in range(3)]
    return lower, upper


INFO = tuple(word_information(word) for word in WORDS)


@lru_cache(maxsize=1024)
def projections(image):
    """Each three-place relation is an eight-bit mask in lexical word order."""
    lower = [0] * 4
    upper = [0] * 3
    # At each defining lower triple and each of its possible fixes, track each
    # of the two values of each individual upper function (both and either).
    fixes = [[[[0, 0] for _ in range(3)] for _ in range(8)] for _ in DEFINING]
    for i, word in enumerate(WORDS):
        if not (image >> i) & 1:
            continue
        low, up = INFO[i]
        for group, val in enumerate(low):
            lower[group] |= 1 << val
            for pair in range(3):
                a, b = word[2 * pair:2 * pair + 2]
                fixes[group][val][pair][0] |= 1 << (a & b)
                fixes[group][val][pair][1] |= 1 << (a | b)
        for role, val in enumerate(up):
            upper[role] |= 1 << val
    readable = [[any(all(fixes[group][val][pair][kind] != 3 for val in range(8))
                     for group in range(4)) for kind in (0, 1)] for pair in range(3)]
    return lower, upper, readable


class StageCheck:
    def __init__(self, supports):
        self.supports = supports
        names = sorted(set(x for s in supports for x in s))
        self.var = {x: i + 1 for i, x in enumerate(names)}
        self.n = len(names)
        self.full = Formula(self.n)
        self.deletion = Formula(self.n)
        self.paired = Formula(2 * self.n)
        self.law_selectors = []
        self.fix_selectors = []
        self.law_opaque = {}
        self.images = {}
        for law in supports:
            v = [self.var[x] for x in law]
            self.full.not_all_equal(v)
            active = self.deletion.new()
            self.law_selectors.append(active)
            self.deletion.not_all_equal(v, active)
            self.paired.not_all_equal(v)
            self.paired.not_all_equal([x + self.n for x in v])
            same = self.paired.new()
            for x in v:
                self.paired.solver.add_clause([-same, x, -(x + self.n)])
                self.paired.solver.add_clause([-same, -x, x + self.n])
            self.fix_selectors.append(same)
        self.delete_assumptions = [[(-lit if i == q else lit) for i, lit in enumerate(self.law_selectors)]
                                   for q in range(len(supports))]

    def close(self):
        for form in (self.full, self.deletion, self.paired):
            form.solver.delete()

    def source_failures(self, carrier):
        if carrier not in self.law_opaque:
            on = self.paired.agree(carrier)
            off = self.paired.agree(tuple(x + self.n for x in carrier))
            self.law_opaque[carrier] = tuple(i for i, same in enumerate(self.fix_selectors)
                                             if not self.paired.allows([same, on, -off]))
        return self.law_opaque[carrier]

    def image(self, carriers):
        if carriers not in self.images:
            bits = tuple(self.full.agree(c) for c in carriers)
            image = 0
            for i, word in enumerate(WORDS):
                if self.full.allows([b if w else -b for b, w in zip(bits, word)]):
                    image |= 1 << i
            self.images[carriers] = image
        return self.images[carriers]

    def restored(self, chain, carriers):
        bits = [self.deletion.agree(c) for c in carriers]
        eithers = [self.deletion.either(a, b) for a, b in zip(bits[::2], bits[1::2])]
        roles = [bits[2 * i:2 * i + 2] + [u for j, u in enumerate(eithers) if j != i] for i in range(3)]
        return [sum(1 << i for i, clause in enumerate(roles) if self.deletion.allows(self.delete_assumptions[q] + clause))
                for q in chain]

    def check(self, chain):
        carried = chain_carriers(self.supports, chain)
        carriers = tuple(tuple(self.var[x] for x in c) for c in carried)
        image = self.image(carriers)
        lower, upper, defining_read = projections(image)
        source_failures = [self.source_failures(c) for c in carriers]
        restore = self.restored(chain, carriers)
        frozen = all(u.bit_count() == 7 for u in upper) and all(l == 127 for l in lower) and not any(source_failures)
        every_law = all(mask == 7 for mask in restore)
        return {"image": image, "lower": lower, "upper": upper, "defining_reads": defining_read,
                "source_failures": source_failures, "restore": restore, "frozen": frozen, "every_law": every_law}


def open_rows(path):
    with gzip.open(path, "rt") as handle:
        for line in handle:
            yield json.loads(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    suffix = "_pilot" if args.pilot else ""
    timer = time.perf_counter()
    totals = Counter()
    rows = open_rows(HERE / f"step_stages{suffix}.jsonl.gz")
    with gzip.open(HERE / f"step_reading_rows{suffix}.jsonl.gz", "wt") as out:
        for stage in rows:
            checks = StageCheck(stage["supports"])
            totals["stages"] += 1
            try:
                for rank, chain in enumerate(stage["chains"]):
                    result = checks.check(chain)
                    result.update(stage=stage["id"], chain_index=rank)
                    print(json.dumps(result, separators=(",", ":")), file=out)
                    totals["chains"] += 1
                    totals["frozen"] += result["frozen"]
                    totals["frozen_and_every_law"] += result["frozen"] and result["every_law"]
                    totals["source_comparisons"] += 6 * len(stage["supports"])
                    totals["determining_source_comparisons"] += sum(map(len, result["source_failures"]))
                    totals["successful_individual_law_role_tests"] += sum(m.bit_count() for m in result["restore"])
                    totals["law_role_tests"] += 24
                    totals["upper_relations_missing_111_only"] += result["upper"].count(127)
                    totals["lower_relations_missing_111_only"] += result["lower"].count(127)
                    totals["defining_lower_determines_upper_function"] += sum(map(sum, result["defining_reads"]))
            finally:
                checks.close()
    stats = {"counts": totals, "wall_seconds": time.perf_counter() - timer,
             "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (HERE / f"step_readings{suffix}.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
