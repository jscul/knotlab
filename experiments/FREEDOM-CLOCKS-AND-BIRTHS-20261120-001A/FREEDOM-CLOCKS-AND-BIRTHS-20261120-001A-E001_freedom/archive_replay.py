"""Replay archived answer probabilities from unsigned physical words and their pairs."""

import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
import hashlib
from io import BytesIO
from itertools import combinations, product
import json
from math import gcd, lcm, prod
import os
from pathlib import Path
from random import Random
import resource
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "archive_replay.json.gz"
THREE = "THREE-READERS-AND-GROWTH-20261120-001A"
SPLIT = "READS-HOLDERS-SOURCES-20261120-001A"
FOUR = "FOUR-READINGS-20261120-001A"
FAMILIES = {THREE: "three_readers", SPLIT: "reads_changes", FOUR: "signed_rules"}


def family(parent, ticket):
    return ROOT / parent / ticket / f"{ticket}-E001_{FAMILIES[ticket]}"


def mask(names):
    return sum(1 << name for name in names)


def pack(word, names):
    return sum(((word >> name) & 1) << i for i, name in enumerate(names))


def sign(word):
    return 1 - 2 * (word.bit_count() & 1)


def frozen(holders):
    return tuple(map(tuple, holders))


@cache
def physical_words(holders, law):
    masks = tuple(map(mask, holders))
    width = max(map(max, holders)) + 1
    if law == "parity":
        return tuple(word for word in range(1 << width)
                     if all(sign(word & h) == 1 for h in masks))
    if law == "nae":
        return tuple(word for word in range(1 << width)
                     if all(word & h not in (0, h) for h in masks))
    raise ValueError(law)


def literal_pairs(words, marks):
    """An entry counts physical words at both ends with the same unread values."""
    marked = mask(marks)
    fibers = defaultdict(list)
    for word in words:
        fibers[word & ~marked].append(pack(word, marks))
    dimension = 1 << len(marks)
    counts = [[0] * dimension for _ in range(dimension)]
    for fiber, multiplicity in Counter(map(tuple, fibers.values())).items():
        for first in fiber:
            for second in fiber:
                counts[first][second] += multiplicity
    return frozen(counts)


@cache
def physical_pairs(holders, marks, law):
    if max(map(max, holders)) < 16:
        return literal_pairs(physical_words(holders, law), marks)
    # The archived counter sees holders and physical names only. No archived
    # answer table or probability function enters the calculation below.
    previous_modules()
    from completions import gram
    return tuple(tuple(map(int, row)) for row in gram(holders, marks, law))


def previous_modules():
    source = str(family("experiments", THREE))
    if source not in sys.path:
        sys.path.insert(0, source)


def trace(counts):
    return sum(row[i] for i, row in enumerate(counts))


def diagonal(counts):
    return tuple(tuple(value if i == j else 0 for j, value in enumerate(row))
                 for i, row in enumerate(counts))


def walsh(values):
    """Signed subset sums, indexed by the little-endian answer word."""
    values = list(values)
    width = 1
    while width < len(values):
        for first in range(0, len(values), 2 * width):
            for i in range(first, first + width):
                a, b = values[i], values[i + width]
                values[i], values[i + width] = a + b, a - b
        width *= 2
    return values


def disjoint_row(counts, questions):
    """Condition on ordinary answers, then sum oriented pairs in each change orbit."""
    changes = [(i, bits) for i, (kind, bits) in enumerate(questions) if kind == "X"]
    reads = [(i, bits) for i, (kind, bits) in enumerate(questions) if kind == "Z"]
    assert not any(t & z for _, t in changes for _, z in reads)
    flips = [0]
    change_answers = [0]
    for i, bits in changes:
        flips += [t ^ bits for t in flips]
        change_answers += [answer | (1 << i) for answer in change_answers]
    counts_by_read = defaultdict(lambda: [0] * len(flips))
    for first, partners in enumerate(counts):
        if not partners[first]:
            continue
        answer = sum((1 << i) for i, bits in reads if sign(first & bits) < 0)
        bins = counts_by_read[answer]
        for i, change in enumerate(flips):
            bins[i] += partners[first ^ change]
    numerators = [0] * (1 << len(questions))
    for read_answer, bins in counts_by_read.items():
        for change_answer, number in zip(change_answers, walsh(bins), strict=True):
            numerators[read_answer | change_answer] = number
    denominator = trace(counts) * len(flips)
    assert min(numerators) >= 0 and sum(numerators) == denominator > 0
    return tuple(Fraction(v, denominator) for v in numerators)


def singletons(n):
    return tuple((("X", 1 << i), ("Z", 1 << i)) for i in range(n))


@cache
def disjoint_table(counts, choices):
    return {settings: disjoint_row(counts, tuple(q[i] for i, q in zip(settings, choices)))
            for settings in product(*(range(len(q)) for q in choices))}


def archive_rows(table):
    return {tuple(row["settings"]): tuple(Fraction(v, row["denominator"])
                                         for v in row["numerators"])
            for row in table["rows"]}


def encoded_rows(table):
    rows = []
    for settings, values in sorted(table.items()):
        denominator = lcm(*(v.denominator for v in values))
        rows.append(dict(settings=settings, denominator=denominator,
                         numerators=[int(v * denominator) for v in values]))
    return rows


def digest(data):
    return hashlib.sha256(data).hexdigest()


def moment(row, subset):
    return sum(sign(subset & answer) * p for answer, p in enumerate(row))


def score(table, rotated=False):
    mask = len(next(iter(table.values()))) - 1
    return sum((-1)**(sum(context) // 2) * moment(row, mask)
               for context, row in table.items() if rotated or sum(context) % 2 == 0)


@cache
def strategies(sizes):
    """Probability cells selected by each predetermined list of whole answers."""
    settings = tuple(product(*(range(len(party)) for party in sizes)))
    starts = [sum(map(len, sizes[:i])) for i in range(len(sizes))]
    locations = [[start + q for start, q in zip(starts, context)] for context in settings]
    strides = []
    offset = 0
    for context in settings:
        lengths = [choices[i] for choices, i in zip(sizes, context)]
        strides.append((offset, [prod(lengths[:i]) for i in range(len(lengths))]))
        offset += prod(lengths)
    return tuple(tuple(start + sum(responses[i] * m for i, m in zip(slots, multiples))
                       for slots, (start, multiples) in zip(locations, strides))
                 for responses in product(*(range(n) for party in sizes for n in party)))


def validate_certificate(replay, path, table, certificate, sizes):
    columns = strategies(sizes)
    target = tuple(p for _, row in sorted(table.items()) for p in row)
    replay.check(f"{path}/list_count", len(columns), certificate["lists"])
    if certificate["local"]:
        rebuilt = [Fraction(0)] * len(target)
        total = Fraction(0)
        for column, raw_weight in certificate["mixture"]:
            weight = Fraction(raw_weight)
            replay.check(f"{path}/nonnegative/{column}", weight >= 0, True)
            total += weight
            for cell in columns[column]:
                rebuilt[cell] += weight
        replay.check(f"{path}/total", total, Fraction(1))
        for cell, (a, b) in enumerate(zip(rebuilt, target, strict=True)):
            replay.check(f"{path}/mixture/{cell}", a, b)
    else:
        coefficients = dict(certificate["inequality"])
        bound = max(sum(coefficients.get(i, 0) for i in support) for support in columns)
        value = sum(target[i] * c for i, c in coefficients.items())
        replay.check(f"{path}/bound", bound, certificate["bound"])
        replay.check(f"{path}/value", value, Fraction(certificate["value"]))
        replay.check(f"{path}/separated", value > bound, True)


def inventory_paths(record, path):
    if isinstance(record, dict):
        if "rows" in record and isinstance(record["rows"], list) and record["rows"] and all(
                isinstance(record["rows"][0], dict) and key in record["rows"][0]
                for key in ("settings", "numerators", "denominator")):
            yield path
        for name, item in record.items():
            yield from inventory_paths(item, f"{path}/{name}")
    elif isinstance(record, list):
        for i, item in enumerate(record):
            yield from inventory_paths(item, f"{path}/{i}")


class Replay:
    def __init__(self):
        self.sources = {}
        self.checked_paths = set()
        self.inventory = defaultdict(Counter)
        self.tables = {}
        self.references = {}
        self.mismatches = []
        self.summary = {}

    def read(self, path):
        payload = path.read_bytes()
        self.sources[str(path.relative_to(ROOT))] = digest(payload)
        return json.loads(payload)

    def check(self, path, actual, expected):
        if actual != expected:
            self.mismatches.append(dict(path=path, actual=actual, expected=expected))

    def probabilities(self, path, actual, stored=None, kind="reconstructed"):
        rows = encoded_rows(actual)
        key = digest(json.dumps(rows, separators=(",", ":")).encode())
        self.tables[key] = rows
        self.references[path] = key
        group = self.inventory[path.split("/", 1)[0]]
        group[f"{kind}_tables"] += 1
        group[f"{kind}_cells"] += sum(map(len, actual.values()))
        if stored is None:
            return
        self.checked_paths.add(path)
        expected = archive_rows(stored)
        self.check(f"{path}/duplicate_settings", len(stored["rows"]) - len(expected), 0)
        self.check(f"{path}/settings", sorted(actual), sorted(expected))
        for settings in sorted(actual.keys() & expected.keys()):
            a, b = actual[settings], expected[settings]
            row = f"{path}/{','.join(map(str, settings))}"
            self.check(f"{row}/outcome_count", len(a), len(b))
            for outcome, (computed, archived) in enumerate(zip(a, b)):
                self.check(f"{row}/{outcome}", computed, archived)

    def behavior(self, path, actual, stored, sizes=None):
        self.probabilities(path, actual, stored, "stored")
        if sizes is None:
            sizes = ((2, 2),) * len(next(iter(actual)))
        if len(sizes) == 3:
            self.inventory[path.split("/", 1)[0]]["stored_three_reader_tables"] += 1
        expected = stored.get("m")
        if expected is not None:
            self.check(f"{path}/score", score(actual), Fraction(expected))
        if "rotated" in stored:
            self.check(f"{path}/rotated", score(actual, rotated=True), Fraction(stored["rotated"]))
        if "common" in stored:
            validate_certificate(self, f"{path}/common", actual, stored["common"], sizes)
        archived_margins = stored.get("margins", {})
        for settings, row in actual.items():
            stride = 1
            for i, (choice, choices) in enumerate(zip(settings, sizes, strict=True)):
                dimension = choices[choice]
                binary_key = f"{i}/{choice}"
                grouped_key = str([i, choice])
                if binary_key in archived_margins:
                    p = sum(p for j, p in enumerate(row) if (j // stride) % dimension == 0)
                    self.check(f"{path}/{settings}/margins/{binary_key}", p,
                               Fraction(archived_margins[binary_key]))
                elif grouped_key in archived_margins:
                    observed = [Fraction(0)] * dimension
                    for j, p in enumerate(row):
                        observed[(j // stride) % dimension] += p
                    self.check(f"{path}/{settings}/margins/{grouped_key}", observed,
                               list(map(Fraction, archived_margins[grouped_key])))
                stride *= dimension

    def cover_file(self, path, document):
        expected = set(inventory_paths(document, path))
        actual = {p for p in self.checked_paths if p.startswith(path + "/")}
        self.check(f"{path}/missing_probability_tables", sorted(expected - actual), [])
        self.check(f"{path}/unmatched_probability_tables", sorted(actual - expected), [])


def operation(kind, bits):
    return 1, ((kind, bits),)


def apply(word, ops):
    scalar, instructions = ops
    for kind, bits in instructions:
        if kind == "X":
            word ^= bits
        else:
            assert kind == "Z"
            scalar *= sign(word & bits)
    return word, scalar


def six_questions(first, second, role):
    x, z = first
    u, v = second

    def sequence(*words, phase=1):
        return phase * prod(ops[0] for ops in words), tuple(word for ops in words for word in ops[1])

    shared = ((x, u, sequence(x, u)),
              (v, z, sequence(z, v)),
              (sequence(x, v), sequence(z, u), sequence(v, u, z, x, phase=-1)))
    return shared if role == "alice" else tuple(zip(*shared))


def combined_row(words, questions, *, keep_distinct_pairs=True):
    # Each subset visits its ordered physical partner, checking support only at
    # the end. Intermediate actions can leave the allowed set.
    words = frozenset(words)
    moments = [0] * (1 << len(questions))
    for source in words:
        states = [(source, 1)]
        for question in questions:
            previous = states.copy()
            for word, weight in previous:
                partner, phase = apply(word, question)
                states.append((partner, weight * phase))
        for i, (partner, phase) in enumerate(states):
            if partner in words and (keep_distinct_pairs or partner == source):
                moments[i] += phase
    denominator = len(words) * len(moments)
    numerators = walsh(moments)
    assert min(numerators) >= 0 and sum(numerators) == denominator > 0
    return tuple(Fraction(v, denominator) for v in numerators)


def combined_table(words, alice, bob, *, keep_distinct_pairs=True):
    def order(size):
        return tuple(pack(i, reversed(range(size))) for i in range(1 << size))

    result = {}
    for i, left in enumerate(alice):
        for j, right in enumerate(bob):
            values = combined_row(words, left + right, keep_distinct_pairs=keep_distinct_pairs)
            result[i, j] = tuple(values[a | (b << len(left))]
                                 for a, b in product(order(len(left)), order(len(right))))
    return result


def split_questions(n, pad=False):
    alice = [(operation("X", 1 << (3 * i)), operation("Z", 3 << (3 * i))) for i in range(n)]
    bob = [(operation("X", 4 << (3 * i)), operation("Z", 4 << (3 * i))) for i in range(n)]
    if pad:
        alice.append((operation("X", 8), operation("Z", 8)))
        bob.append((operation("X", 16), operation("Z", 16)))
    return alice, bob


def six_score(table):
    order = tuple(product((0, 1), repeat=3))
    return sum(p for (i, j), row in table.items()
               for p, (a, b) in zip(row, product(order, repeat=2), strict=True)
               if sum(a) % 2 == 0 and sum(b) % 2 == (j == 2) and a[j] == b[i]) / 9


def marginal_variation(table, left, right):
    margins = defaultdict(list)
    for (i, j), row in table.items():
        margins[0, i].append(tuple(sum(row[right * a:right * (a + 1)]) for a in range(left)))
        margins[1, j].append(tuple(sum(row[b::right]) for b in range(right)))
    return tuple(max(sum(abs(x - y) for x, y in zip(a, b)) / 2
                     for (side, _), rows in margins.items() if side == role
                     for a, b in combinations(rows, 2)) for role in range(2))


def replay_six(replay):
    main = replay.read(family("artifacts", SPLIT) / "split_parity.json")
    earlier = replay.read(family("artifacts", FOUR) / "games.json")
    replay.check("six/original/word_order", earlier["order"], [f"{i:03b}" for i in range(8)])
    physical = physical_words(((0, 1, 2), (3, 4, 5)), "parity")
    a, b = split_questions(2)
    alice, bob = six_questions(*a, "alice"), six_questions(*b, "bob")
    for party, questions in (("alice", alice), ("bob", bob)):
        for index, question in enumerate(questions):
            for word in range(64):
                for first, second in combinations(question, 2):
                    moved_a, sign_a = apply(word, first)
                    moved_ab, sign_ab = apply(moved_a, second)
                    moved_b, sign_b = apply(word, second)
                    moved_ba, sign_ba = apply(moved_b, first)
                    assert (moved_ab, sign_a * sign_ab) == (moved_ba, sign_b * sign_ba)
                partner, scalar = word, 1
                for op in question:
                    partner, phase = apply(partner, op)
                    scalar *= phase
                expected = (word, -1 if party == "bob" and index == 2 else 1)
                assert (partner, scalar) == expected
    calculated = combined_table(physical, alice, bob)
    replay.probabilities("six/physical/main", calculated, main["main"], "stored")
    for key, den in (("numerator", "denominator"), ("born_numerators_over_256", None)):
        rows = [dict(settings=[r["inputs"][0], r["inputs"][1] - 3], numerators=r[key],
                     denominator=r[den] if den else 256) for r in earlier["six"]]
        replay.probabilities(f"six/original/{key}", calculated, {"rows": rows}, "stored")
    dephased = combined_table(physical, alice, bob, keep_distinct_pairs=False)
    replay.probabilities("six/physical/ordinary_mixture", dephased,
                         main["ordinary_mixture"], "stored")
    for label, table in (("main", calculated), ("ordinary_mixture", dephased)):
        replay.check(f"six/physical/{label}/score", six_score(table), Fraction(main[label]["equal_at_shared"]))
    variation = marginal_variation(calculated, 8, 8)
    replay.check("six/marginal_variation", variation, tuple(map(Fraction, earlier["six_TV"])))
    replay.check("six/physical/main/marginal_variation", variation,
                 tuple(map(Fraction, main["main"]["marginal_total_variation"])))
    replay.summary["six_rules"] = dict(physical_allowed_words=len(physical), joint_cells=576,
                                       original_archive_encodings=2, score=six_score(calculated),
                                       diagonal_score=six_score(dephased), marginal_variation=variation)


def replay_lead(replay):
    source = replay.read(family("artifacts", THREE) / "lead.json")
    for law, record in source.items():
        for attachment, stored in record["attachments"].items():
            counts = physical_pairs(frozen(stored["stars"]), (0, 1, 2), law)
            prefix = f"lead/{law}/attachments/{attachment}"
            replay.check(f"{prefix}/common_completions", counts, frozen(stored["gram"]))
            table = disjoint_table(counts, singletons(3))
            replay.behavior(prefix, table, stored)
        counts = physical_pairs(((0, 1, 2),), (0, 1, 2), law)
        isolated = disjoint_table(counts, singletons(3))
        sparse = ((("X", 1), ("Z", 1), ("X", 2), ("Z", 2)), singletons(3)[2])
        grouped = {(2 * a + b, c): row for (a, b, c), row in isolated.items()}
        controls = {"single_per_reader": disjoint_table(counts, sparse),
                    "joint_at_two_place_reader": grouped,
                    "incoherent_diagonal": disjoint_table(diagonal(counts), singletons(3))}
        sizes = {"single_per_reader": ((2, 2, 2, 2), (2, 2)),
                 "joint_at_two_place_reader": ((4, 4, 4, 4), (2, 2))}
        for label, table in controls.items():
            replay.behavior(f"lead/{law}/{label}", table, record[label], sizes.get(label))
    replay.cover_file("lead", source)


def replay_widths(replay):
    source = replay.read(family("artifacts", THREE) / "widths.json")
    for width in (3, 4, 5):
        names = tuple(range(width))
        for law, record in source[str(width)].items():
            base = f"widths/{width}/{law}"
            full = disjoint_table(physical_pairs((names,), names, law), singletons(width))
            replay.behavior(f"{base}/all_marks", full, record["all_marks"])
            expected_sets = list(combinations(names, 3))
            replay.check(f"{base}/subset_inventory", [tuple(r["marks"]) for r in record["subsets"]],
                         expected_sets)
            for i, stored in enumerate(record["subsets"]):
                marks = tuple(stored["marks"])
                table = disjoint_table(physical_pairs((names,), marks, law), singletons(3))
                replay.behavior(f"{base}/subsets/{i}", table, stored)
    two = disjoint_table(literal_pairs((1, 2, 3), (0, 1)), singletons(2))
    replay.behavior("widths/conditional_two_mark_control", two, source["conditional_two_mark_control"])
    replay.cover_file("widths", source)


def replay_alternate_split(replay):
    source = replay.read(family("artifacts", SPLIT) / "alternate_law.json")
    scores = {}
    for law, record in source.items():
        one = physical_words(((0, 1, 2),), law)
        two = physical_words(((0, 1, 2), (3, 4, 5)), law)
        a, b = split_questions(1)
        intrinsic = combined_table(one, tuple((x,) for x in a[0]), tuple((x,) for x in b[0]))
        a, b = split_questions(1, pad=True)
        padded = combined_table(one, six_questions(*a, "alice"), six_questions(*b, "bob"))
        a, b = split_questions(2)
        complete = combined_table(two, six_questions(*a, "alice"), six_questions(*b, "bob"))
        scores[law] = dict(one_padded=six_score(padded), two_unpadded=six_score(complete))
        for key, label, table in (("1", "intrinsic", intrinsic), ("1", "six_with_local_zeros", padded),
                                  ("2", "six", complete)):
            stored = record[key][label]
            path = f"alternate_split/{law}/{key}/{label}"
            replay.probabilities(path, table, stored, "stored")
            width = 2 if label == "intrinsic" else 8
            replay.check(f"{path}/marginal_variation", marginal_variation(table, width, width),
                         tuple(map(Fraction, stored["marginal_total_variation"])))
            if "equal_at_shared" in stored:
                replay.check(f"{path}/score", six_score(table), Fraction(stored["equal_at_shared"]))
    replay.summary["split_controls"] = scores
    replay.cover_file("alternate_split", source)


def replay_separation(replay):
    source = replay.read(family("artifacts", THREE) / "separation.json")
    for law, fixtures in source.items():
        for label, stored in fixtures.items():
            physical = physical_words(frozen(stored["stars"]), law)
            marks = tuple(name for reader in stored["parties"] for name in reader)
            outside = tuple(stored["unread"])
            lengths = [len(reader) for reader in stored["parties"]]
            blocks = [((1 << size) - 1) << sum(lengths[:i]) for i, size in enumerate(lengths)]
            choices = tuple((("X", m), ("Z", m)) for m in blocks)
            table = disjoint_table(literal_pairs(physical, marks), choices)
            path = f"separation/{law}/{label}"
            replay.behavior(f"{path}/readings", table, stored["readings"])
            for row in stored["conditional"]:
                conditioned = [w for w in physical if pack(w, outside) == row["unread_word"]]
                supports = [sorted({pack(w, names) for w in conditioned}) for names in stored["parties"]]
                prefix = f"{path}/conditional/{row['unread_word']}"
                replay.check(f"{prefix}/mass", Fraction(len(conditioned), len(physical)), Fraction(row["mass"]))
                replay.check(f"{prefix}/local_supports", supports, row["local_supports"])
                replay.check(f"{prefix}/product_count", prod(map(len, supports)), len(conditioned))
    replay.cover_file("separation", source)
    source = replay.read(family("artifacts", SPLIT) / "separation.json")
    for law, stored in source.items():
        physical = physical_words(((0, 1, 2), (2, 3, 4)), law)
        alice = ((operation("X", 1),), (operation("Z", 3),))
        bob = ((operation("X", 16),), (operation("Z", 24),))
        table = combined_table(physical, alice, bob)
        replay.probabilities(f"split_separation/{law}", table, stored, "stored")
    replay.cover_file("split_separation", source)


def plus_mass(row, selected):
    return sum(p for answer, p in enumerate(row) if not answer & selected)


def ternary_comparisons(table):
    px, pz = table[0, 0, 0], table[1, 1, 1]
    assert pz[0] == pz[-1] == 0
    minority = tuple(pz[1 << i] + pz[7 ^ (1 << i)] for i in range(3))
    excess = {m: plus_mass(px, m) + sum(minority[i] / 2 for i in range(3) if m >> i & 1) - 1
              for m in (6, 5, 3, 7)}
    return minority, excess


@cache
def full_list_certificate(table_key):
    # Used only for the unstored witness on a reconstructed wider triple. The
    # candidate probabilities were already computed from physical pairs.
    previous_modules()
    from three import full_certificate
    return full_certificate(encoded_rows(dict(table_key)), ((2, 2),) * 3)


def local_verdict(replay, path, table, law):
    px, pz = table[0, 0, 0], table[1, 1, 1]
    if law == "parity":
        for context, row in table.items():
            z = mask(i for i, s in enumerate(context) if s)
            x = 7 ^ z
            for answer, p in enumerate(row):
                mx = sum(q for a, q in enumerate(px) if a & x == answer & x)
                mz = sum(q for a, q in enumerate(pz) if a & z == answer & z)
                replay.check(f"{path}/parity_product/{context}/{answer}", p, mx * mz)
        return True
    if pz[0] == pz[-1] == 0:
        _, excess = ternary_comparisons(table)
        return max(excess.values()) <= 0
    certificate = full_list_certificate(tuple(sorted(table.items())))
    validate_certificate(replay, f"{path}/reconstructed_common", table, certificate, ((2, 2),) * 3)
    return certificate["local"]


def reconstruct_placements(replay, path, holders, law, placements):
    reports = []
    for idx, row in enumerate(placements):
        marks = tuple(row.get("marks", holders[row["i"]]))
        prefix = f"{path}/{idx}"
        table = disjoint_table(physical_pairs(holders, marks, law), singletons(3))
        replay.probabilities(prefix, table)
        m = score(table)
        local = local_verdict(replay, prefix, table, law)
        replay.check(f"{prefix}/score", m, Fraction(row["m"]))
        replay.check(f"{prefix}/local", local, row["local"])
        if "loose" in row:
            replay.check(f"{prefix}/loose", sum(sum(b in h for h in holders) == 1 for b in marks), row["loose"])
        reports.append((m, local))
    return reports


def reconstruct_roster(replay, path, holders, law, report):
    expected_ternaries = [i for i, h in enumerate(holders) if len(h) == 3]
    expected_wide = [(i, m) for i, h in enumerate(holders) if len(h) > 3 for m in combinations(h, 3)]
    replay.check(f"{path}/ternary_names", [r["i"] for r in report["marked"]], expected_ternaries)
    replay.check(f"{path}/wider_names", [(r["i"], tuple(r["marks"])) for r in report["wide"]], expected_wide)
    marked = reconstruct_placements(replay, f"{path}/marked", holders, law, report["marked"])
    wide = reconstruct_placements(replay, f"{path}/wide", holders, law, report["wide"])
    replay.check(f"{path}/ternary", len(marked), report["ternary"])
    replay.check(f"{path}/wide_triples", len(wide), report["wide_triples"])
    replay.check(f"{path}/nonlocal_ternary", sum(not local for _, local in marked), report["nonlocal_ternary"])
    replay.check(f"{path}/nonlocal_wide_triples", sum(not local for _, local in wide), report["nonlocal_wide_triples"])
    replay.check(f"{path}/largest", max((m for m, _ in marked + wide), default=Fraction(0)), Fraction(report["largest"]))


def aggregate(records):
    total = sum(p for p, _ in records)
    if not total:
        return None
    settings = next(iter(records))[1]
    return {s: tuple(sum(p * table[s][y] for p, table in records) / total for y in range(8))
            for s in settings}


def replay_heralds(replay, prefix, counts, law, basis, stored):
    central = singletons(3)
    remote = tuple(((basis, 1 << i),) for i in range(3, 9))
    joint = disjoint_table(counts, central + remote)
    groups = {}
    reports, corrected, accepted = [], [], []
    report_groups = []
    probabilities = []
    for h, old in enumerate(stored["heralds"]):
        replay.check(f"{prefix}/herald_number/{h}", h, old["herald"])
        joint_rows = {s[:3]: row[8 * h:8 * (h + 1)] for s, row in joint.items()}
        masses = {sum(row) for row in joint_rows.values()}
        assert len(masses) == 1, (prefix, h, masses)
        p = next(iter(masses))
        probabilities.append(p)
        replay.check(f"{prefix}/herald_mass/{h}", p, Fraction(old["probability"]))
        if not p:
            replay.check(f"{prefix}/undefined_conditional/{h}", "conditional" in old, False)
            continue
        conditional = {s: tuple(q / p for q in row) for s, row in joint_rows.items()}
        ident = old["conditional"]
        replay.check(f"{prefix}/repeated_conditional/{h}", conditional, groups.setdefault(ident, conditional))
        reports.append((p, conditional))
        report_groups.append((p, ident))
        if basis == "X":
            pairs = [(h >> (2 * i)) & 3 for i in range(3)]
            changed = mask(i for i, pair in enumerate(pairs)
                           if (sign(pair) < 0 if law == "nae" else pair & 1))
            accept = h == 0
        else:
            changed = 0
            accept = all(((h >> (2 * i)) & 3) in (1, 2) for i in range(3))
        replay.check(f"{prefix}/correction/{h}", changed, old["correction_mask"])
        replay.check(f"{prefix}/accepted/{h}", accept, old["accepted"])
        relabeled = {}
        for s, row in conditional.items():
            changed_outputs = changed & mask(i for i, choice in enumerate(s) if choice == 0)
            relabeled[s] = tuple(row[y ^ changed_outputs] for y in range(8))
        corrected.append((p, relabeled))
        if accept:
            accepted.append((p, conditional))

    replay.check(f"{prefix}/conditional_inventory", sorted(groups), list(range(len(stored["distinct_tables"]))))
    for i, table in sorted(groups.items()):
        replay.behavior(f"{prefix}/distinct_tables/{i}", table, stored["distinct_tables"][i])
    nonlocal_mass = sum(p for p, ident in report_groups if not stored["distinct_tables"][ident]["common"]["local"])
    replay.check(f"{prefix}/nonlocal_conditional_probability", nonlocal_mass,
                 Fraction(stored["nonlocal_conditional_probability"]))
    replay.behavior(f"{prefix}/ignored", aggregate(reports), stored["ignored"])
    replay.behavior(f"{prefix}/all_trial_corrected", aggregate(corrected), stored["all_trial_corrected"])
    p_accept = sum(p for p, _ in accepted)
    replay.check(f"{prefix}/accepted_probability", p_accept, Fraction(stored["accepted_probability"]))
    if p_accept:
        replay.behavior(f"{prefix}/accepted_table", aggregate(accepted), stored["accepted_table"])
    else:
        replay.check(f"{prefix}/absent_accepted_table", stored["accepted_table"], None)
    return dict(conditional_reports=len(stored["heralds"]), positive_reports=len(reports),
                accepted_probability=Fraction(p_accept), individual_report_probabilities=probabilities)


def replay_branches(replay, law, stored):
    holders = frozen(stored["stars"])
    central = tuple(stored["central_reads"])
    remote = tuple(stored["remote_marks"])
    counts = physical_pairs(holders, central + remote, law)
    changes = [mask(holders[i + 1] if law == "nae" else (i, 3 + 2 * i)) for i in range(3)]
    prefix = f"holders/protocols/{law}"
    replay.check(f"{prefix}/enlarged_changes", changes, stored["enlarged_changes"])
    assert central + remote == tuple(range(9))
    enlarged = disjoint_table(counts, tuple((("X", t), ("Z", 1 << z)) for t, z in zip(changes, central)))
    replay.behavior(f"{prefix}/enlarged_table", enlarged, stored["enlarged_table"])
    for key, expected in stored["enlarged_moments"].items():
        t, z = ast.literal_eval(key)
        context = tuple((z >> i) & 1 for i in range(3))
        replay.check(f"{prefix}/enlarged_moments/{key}", moment(enlarged[context], t | z), Fraction(expected))
    return {basis: replay_heralds(replay, f"{prefix}/heralds/{basis}", counts, law, basis, heralds)
            for basis, heralds in stored["heralds"].items()}


def replay_three_holder_bounds(replay, stored):
    for label, row in stored.items():
        left, right, _ = ast.literal_eval(label)
        for i, (u, v, w, expected) in enumerate(row["physical_crosschecks"]):
            shared = tuple(range(3, 3 + w))
            first = tuple(range(3 + w, 3 + w + u))
            second = tuple(range(3 + w + u, 3 + w + u + v))
            holders = ((0, 1, 2), left + shared + first, right + shared + second)
            counts = physical_pairs(holders, (0, 1, 2), "nae")
            table = disjoint_table(counts, singletons(3))
            prefix = f"holders/three_holder_proof/{label}/physical_crosschecks/{i}"
            replay.probabilities(prefix, table)
            _, excess = ternary_comparisons(table)
            value = excess[3 if len(left) == 2 else 7] * 8 * trace(counts)
            replay.check(f"{prefix}/eight_trace_excess", value, expected)


def replay_holders(replay):
    source = replay.read(family("artifacts", THREE) / "holders.json")
    for label, row in source["core"].items():
        counts = physical_pairs(frozen(row["stars"]), tuple(row["marks"]), row["law"])
        table = disjoint_table(counts, singletons(3))
        path = f"holders/core/{label}"
        replay.check(f"{path}/common_completions", counts, frozen(row["gram"]))
        replay.behavior(f"{path}/behavior", table, row["behavior"])
        if row["criterion"]:
            minority, excess = ternary_comparisons(table)
            replay.check(f"{path}/minority", minority, tuple(map(Fraction, row["criterion"]["minority"])))
            replay.check(f"{path}/hall_excess", tuple(excess.values()), tuple(map(Fraction, row["criterion"]["plus_probability_minus_bound"])))
    replay.summary["heralds"] = {law: replay_branches(replay, law, row) for law, row in source["protocols"].items()}
    for i, row in enumerate(source["all_ternary"]):
        reconstruct_placements(replay, f"holders/all_ternary/{i}/knots", frozen(row["stars"]), "nae", row["knots"])
    for label, row in source["named_growth"].items():
        law = label.rsplit("_", 1)[1]
        path = f"holders/named_growth/{label}"
        reconstruct_roster(replay, f"{path}/source_report", frozen(row["source"]), law, row["source_report"])
        reached = frozen(row["reached"])
        if "representatives" in row:
            reconstruct_placements(replay, f"{path}/representatives", reached, law, row["representatives"])
        else:
            reconstruct_roster(replay, f"{path}/reached_report", reached, law, row["reached_report"])
    for label, row in source["width_search"]["minima"].items():
        reconstruct_roster(replay, f"holders/width_search/minima/{label}/checks", frozen(row["target"]), "nae", row["checks"])
    wider = disjoint_table(physical_pairs(((0, 1, 2, 3),), (0, 1, 2), "nae"), singletons(3))
    replay.behavior("holders/wider_model/verified_full_table", wider, source["wider_model"]["verified_full_table"])
    replay_three_holder_bounds(replay, source["three_holder_proof"])
    replay.cover_file("holders", source)


def sampling_random(seed, vote, purpose):
    key = f"{seed}|{vote['label']}|{vote['n']}|{vote['index']}|{purpose}"
    return Random(int(digest(key.encode()), 16))


def archived_placements(replay, source):
    """Recover all referenced physical counts and check their archived multiplicities."""
    tables = source["tables"]
    cases = source["cases"]
    variants = {}
    normalized = {}
    placements_by_rate = defaultdict(list)
    n_placements = 0
    for v, vote in enumerate(source["votes"]):
        age, law = vote["age"], vote["law"]
        case = cases[vote["case"]]
        holders = frozen(case["laws"][law]["next_stars"] if age else case["stars"])
        eligible = [i for i, h in enumerate(holders) if len(h) >= 3]
        ternary = [i for i in eligible if len(holders[i]) == 3]
        path = f"samples/votes/{v}"
        replay.check(f"{path}/holder_count", len(holders), vote["holder_count"])
        replay.check(f"{path}/eligible_ternary", len(ternary), vote["eligible_ternary"])
        replay.check(f"{path}/eligible_wide", len(eligible), vote["eligible_wide"])

        def reference(label, item, holder):
            nonlocal n_placements
            n_placements += 1
            prefix = f"{path}/{label}"
            replay.check(f"{prefix}/holder", item["holder"], holder)
            marks = tuple(sorted(holders[holder]))
            if len(marks) > 3:
                chooser = sampling_random(source["seed"], vote, f"wide:{age}:{holder}")
                marks = chooser.choice(list(combinations(marks, 3)))
            replay.check(f"{prefix}/marks", list(marks), item["marks"])
            key = (holders, marks, law)
            if key not in variants:
                counts = physical_pairs(holders, marks, law)
                flat = tuple(x for row in counts for x in row)
                scale = gcd(*flat)
                signature = tuple(x // scale for x in flat)
                ident = law + "-" + digest(str(signature).encode())[:20]
                if ident not in normalized:
                    normalized[ident] = (signature, disjoint_table(counts, singletons(3)))
                else:
                    replay.check(f"{prefix}/signature_collision", signature, normalized[ident][0])
                variants[key] = ident, scale
            ident, scale = variants[key]
            replay.check(f"{prefix}/signature", ident, item["table"])
            replay.check(f"{prefix}/common_completion_unit", scale, item["common_completion_unit"])
            return ident

        rates = {}
        if vote["mode"] != "fixed_vote":
            records = vote.get("all_holders", [])
            replay.check(f"{path}/holder_roster", [r["holder"] for r in records], eligible)
            ids = [reference(f"all_holders/{i}", item, h)
                   for i, (item, h) in enumerate(zip(records, eligible))]
            rates["all_holders"] = ids
            rates["all_ternaries"] = [t for h, t in zip(eligible, ids) if h in ternary]
        if vote["mode"] != "fixed_roster":
            for label, selected in (("uniform", eligible), ("ternary", ternary)):
                item = vote[label]
                replay.check(f"{path}/{label}/eligible", item is not None, bool(selected))
                if item is not None and selected:
                    holder = sampling_random(source["seed"], vote, f"{label}:{age}").choice(selected)
                    rates[label] = [reference(label, item, holder)]
        sizes = [vote["n"], 0] if vote["mode"] == "draw" else [vote["n"]]
        for size in sizes:
            for label, ids in rates.items():
                placements_by_rate[vote["label"], size, law, age, label].extend(ids)
    replay.check("samples/missing_library_entries", sorted(tables.keys() - normalized.keys()), [])
    replay.check("samples/extra_library_entries", sorted(normalized.keys() - tables.keys()), [])
    replay.summary["sample_inventory"] = dict(case_count=len(cases), vote_count=len(source["votes"]),
                                              placement_references=n_placements,
                                              distinct_physical_readings=len(variants),
                                              literal_physical_readings=sum(max(map(max, h)) < 16 for h, _, _ in variants),
                                              physical_count_sha256=digest(json.dumps(sorted(variants.items())).encode()),
                                              library_size=len(normalized))
    return normalized, placements_by_rate


def replay_samples(replay):
    source = replay.read(family("artifacts", THREE) / "samples.json")
    normalized, placements = archived_placements(replay, source)
    summaries = {}
    certificate_methods = Counter()
    for ident in sorted(normalized.keys() & source["tables"].keys()):
        signature, calculated = normalized[ident]
        stored = source["tables"][ident]
        path = f"samples/tables/{ident}"
        replay.check(f"{path}/primitive_pair_counts", signature, tuple(stored["gram"]))
        replay.behavior(path, calculated, stored)
        pz = calculated[1, 1, 1]
        law = ident.split("-", 1)[0]
        local = stored["common"]["local"]
        if law == "parity" or (not pz[0] and not pz[-1]):
            replay.check(f"{path}/constructive_local", local_verdict(replay, path, calculated, law), local)
        summaries[ident] = score(calculated), local
        certificate_methods[stored["method"]] += 1
    replay.cover_file("samples", source)
    rate_rows = []
    for i, row in enumerate(source["rates"]):
        key = tuple(row[k] for k in ("label", "size", "law", "age", "weighting"))
        evaluated = [summaries[t] for t in placements.pop(key, []) if t in summaries]
        measures = dict(n=len(evaluated), nonlocal_count=sum(not local for _, local in evaluated),
                        above_two=sum(m > 2 for m, _ in evaluated),
                        maximum=max((m for m, _ in evaluated), default=None))
        for k, value in measures.items():
            expected = Fraction(row[k]) if k == "maximum" and row[k] is not None else row[k]
            replay.check(f"samples/rates/{i}/{k}", value, expected)
        rate_rows.append(dict(label=key[0], size=key[1], law=key[2], age=key[3], weighting=key[4], **measures))
    replay.check("samples/unreported_rate_groups", sorted(placements), [])
    distinct_arrays = {key for path, key in replay.references.items() if path.startswith("samples/tables/")}
    replay.summary["sample_inventory"].update(rates=len(rate_rows), certificate_methods=certificate_methods,
                                               distinct_outcome_arrays=len(distinct_arrays))
    replay.summary["sample_rates"] = rate_rows
    return source


def replay_validation(replay, samples):
    source = replay.read(family("artifacts", THREE) / "validation.json")
    qs = singletons(3)
    by_width = source["tree_arity_checks"]
    for label, record in by_width["thresholds"].items():
        for j, raw_holders in enumerate(record["physical_stars"]):
            counts = physical_pairs(frozen(raw_holders), (0, 1, 2), "nae")
            table = disjoint_table(counts, qs)
            path = f"validation/tree_arity_checks/{label}/{j}"
            replay.probabilities(path, table)
            replay.check(f"{path}/score", score(table), Fraction(record["score"]))
            replay.check(f"{path}/pair_excesses",
                         [plus_mass(table[0, 0, 0], pair) - Fraction(2, 3) for pair in (3, 5, 6)],
                         list(map(Fraction, record["pair_excesses"])))
            replay.check(f"{path}/triple_excess", table[0, 0, 0][0] - Fraction(1, 2), Fraction(record["triple_excess"]))
            validate_certificate(replay, f"{path}/common", table, record["common"], ((2, 2),) * 3)
    tree_ternaries = sum(vote["eligible_ternary"] for vote in samples["votes"]
                         if (vote["label"], vote["law"], vote["age"]) == ("tree", "nae", 0))
    replay.check("validation/tree_arity_checks/tree_source_ternaries", tree_ternaries,
                 by_width["all_drawn_tree_source_ternaries"])
    methods = replay.summary["sample_inventory"]["certificate_methods"]
    replay.check("validation/sample_library", sum(methods.values()), source["sample_comparisons"]["every_cell_rational"])
    replay.check("validation/sample_ternary_transport", methods["minority assignment transport"],
                 source["sample_comparisons"]["transport_vs_independent_full_list"])


def replay_parent_summary(replay):
    source = replay.read(ROOT / "research/THREE-READERS-AND-GROWTH-20261120-001/reading_replay.json")
    for label, law in (("not-all-equal", "nae"), ("parity", "parity")):
        for count in range(4):
            raw = replay.tables[replay.references[f"lead/{law}/attachments/{count}"]]
            table = archive_rows({"rows": raw})
            record = source[label][f"attached_ternaries_{count}"]
            path = f"reading_replay/{label}/attached_ternaries_{count}"
            replay.check(f"{path}/score", score(table), Fraction(record["score"]))
            if law == "nae":
                _, excess = ternary_comparisons(table)
                replay.check(f"{path}/shortfall", max(Fraction(0), *excess.values()),
                             Fraction(record["common_list_mass_shortfall"]))
        for width in (4, 5):
            path = f"reading_replay/{label}/isolated_{width}"
            record = source[label][f"isolated_{width}"]
            rows = replay.tables[replay.references[f"widths/{width}/{law}/all_marks"]]
            full = archive_rows({"rows": rows})
            rows = replay.tables[replay.references[f"widths/{width}/{law}/subsets/0"]]
            reduced = archive_rows({"rows": rows})
            replay.check(f"{path}/full_score", score(full), Fraction(record["full_score"]))
            replay.check(f"{path}/three_reader_score", score(reduced), Fraction(record["three_reader_score"]))
            if "rotated_full_score" in record:
                replay.check(f"{path}/rotated_full_score", score(full, rotated=True), Fraction(record["rotated_full_score"]))
    holder_path = "holders/core/([[0], [1], [2]], [4, 4, 4], 'nae')/behavior"
    rows = replay.tables[replay.references[holder_path]]
    replay.check("reading_replay/three_attached_four_place_score", score(archive_rows({"rows": rows})),
                 Fraction(source["three_attached_four_place_score"]))


def json_value(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_value(item) for item in (sorted(value) if isinstance(value, set) else value)]
    return value


def compressed_result(replay):
    inputs = dict(replay.sources)
    for module in tuple(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT):
                rel = path.relative_to(ROOT)
                if rel.parts[0] in ("experiments", "tools") and path.suffix == ".py":
                    inputs[str(rel)] = digest(path.read_bytes())
    result = dict(schema=1, inputs=inputs, inventory=replay.inventory,
                  orientations=dict(three_reader="little endian, 0 is plus; X then Z",
                                    six_rules="Alice then Bob; each three-bit word in lexicographic 000...111 order"),
                  summaries=replay.summary, references=replay.references,
                  tables=replay.tables, mismatches=replay.mismatches)
    payload = json.dumps(json_value(result), sort_keys=True, separators=(",", ":")).encode() + b"\n"
    output = BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        gz.write(payload)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Require byte-identical replay of the saved archive receipt.")
    args = parser.parse_args()
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    limit = 4 * 1024**3
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (limit if soft == resource.RLIM_INFINITY else min(soft, limit), hard))

    replay = Replay()
    replay_six(replay)
    replay_alternate_split(replay)
    replay_lead(replay)
    replay_widths(replay)
    replay_holders(replay)
    replay_separation(replay)
    samples = replay_samples(replay)
    replay_validation(replay, samples)
    replay_parent_summary(replay)
    predecessor = [replay.inventory[k] for k in ("lead", "widths", "holders", "separation", "samples")]
    replay.check("three_reader_predecessor/all_stored_tables", sum(r["stored_tables"] for r in predecessor), 382)
    replay.check("three_reader_predecessor/three_reader_tables", sum(r["stored_three_reader_tables"] for r in predecessor), 371)
    replay.check("sample_library/distinct_tables", replay.summary["sample_inventory"]["library_size"], 260)
    replay.check("sample_library/distinct_outcome_arrays", replay.summary["sample_inventory"]["distinct_outcome_arrays"], 260)
    output = compressed_result(replay)
    if args.check:
        if output != OUTPUT.read_bytes():
            print("The replay receipt differs from the saved artifact.", file=sys.stderr)
            for mismatch in replay.mismatches[:5]:
                print(json.dumps(json_value(mismatch), sort_keys=True), file=sys.stderr)
            return 1
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(output)
    print(json.dumps(json_value(dict(inventory=replay.inventory, mismatches=len(replay.mismatches),
                                     archive_sha256=digest(output))), sort_keys=True))
    for mismatch in replay.mismatches[:5]:
        print(json.dumps(json_value(mismatch), sort_keys=True), file=sys.stderr)
    return int(bool(replay.mismatches))


if __name__ == "__main__":
    sys.exit(main())
