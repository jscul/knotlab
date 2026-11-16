"""Anonymous public wirings, archival replay fixtures, and evaluation-only construction checks."""

import hashlib
import importlib.util
import json
import random
from collections import Counter
from functools import lru_cache
from itertools import permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIOR = "BIT-DECODER-20261114-001"
RESULT = ROOT / "artifacts" / PRIOR / (PRIOR + "-E001_atomic_codec") / "result.json"
ORDERS = tuple(permutations(range(4)))
MASKS = range(512)
UNIVERSE = (1 << 512) - 1
COLUMNS = tuple(sum(1 << m for m in MASKS if m & (1 << i)) for i in range(9))


def _clauses(op, pins):
    a = pins[0]
    taut = (a, -a)
    if op == "unit":
        return [(a, a, a), taut, taut, taut]
    b = pins[1]
    if op == "xor":
        return [(a, b, b), (-a, -b), taut, (b, -b)]
    if op == "or2":
        return [(a, b, b), taut, (b, -b), taut]
    c = pins[2]
    if op == "e":
        return [(a, b, c), (-a, -b), (-a, -c), (-b, -c)]
    if op == "o":
        return [(a, b, c), taut, (b, -b), (c, -c)]
    if op == "a":
        return [(a, a, a), (b, b), (c, c), taut]
    if op == "m":
        return [(a, b, c), (a, b), (b, c), (c, a)]
    if op == "s":
        return [(a, -a, b), (-a, b), (a, c), (c, -c)]
    if op == "g":
        return [(a, a, -b), (-a, b), (b, -c), (-b, c)]
    if op == "p":
        return [(a, b, c), (-a, -b), (b, -b), (c, -c)]
    if op == "padded_unit":
        return [(a, b, c), (a, -b), (a, -c), (b, -b)]
    raise ValueError(f"Unknown question {op}")


# e = exactly one, o/a = any/all, m = majority, s = if a then b else c,
# g = all three equal, p = at least one and not both a and b.
TRAIN = {
    "four_joint_five": (("e", (1,2,3)), ("e", (1,2,4)), ("e", (3,4,5)), ("e", (1,2,5))),
    "two_disjoint_groups": (("e", (1,2,3)), ("o", (1,2,3)), ("s", (4,5,6)), ("m", (4,5,6))),
    "one_computed_two_raw": (("unit", (1,)), ("unit", (2,)), ("or2", (1,2)), ("e", (3,4,5))),
    "three_raw": (("unit", (1,)), ("unit", (2,)), ("unit", (3,)), ("m", (1,2,3))),
    "one_repeated": (("e", (1,2,3)), ("e", (3,2,1)), ("e", (2,1,3)), ("e", (3,1,2))),
    "four_independent": (("unit", (1,)), ("unit", (-2,)), ("unit", (3,)), ("unit", (-4,))),
    "padded_sources": (("padded_unit", (1,5,6)), ("padded_unit", (2,5,6)),
                       ("padded_unit", (3,5,6)), ("padded_unit", (4,5,6))),
}


ALL_PAIRS = ((1,2,3), (1,4,5), (2,4,6), (3,5,6))
DOUBLE_PAIRS = ((1,2,5), (1,2,6), (3,4,5), (3,4,6))
EIGHT = (
    ("all_pairs_exactly_one", ALL_PAIRS, "eeee", (0,0,0,0)),
    ("all_pairs_mixed", ALL_PAIRS, "emso", (0,1,4,2)),
    ("all_pairs_grouping", ALL_PAIRS, "ppsg", (2,4,1,6)),
    ("all_pairs_conditional", ALL_PAIRS, "mspp", (0,2,5,3)),
    ("double_pairs_threshold", DOUBLE_PAIRS, "omma", (1,2,4,7)),
    ("double_pairs_conditional", DOUBLE_PAIRS, "spge", (0,6,1,2)),
    ("double_pairs_select", DOUBLE_PAIRS, "ssss", (0,0,0,0)),
    ("double_pairs_equality", DOUBLE_PAIRS, "ggmp", (5,0,3,2)),
)


HELD = {
    "mixed_raw_xor": (("unit", (1,)), ("unit", (2,)), ("xor", (1,2)), ("e", (3,4,5))),
    "mixed_two_compounds": (("e", (1,2,3)), ("e", (-1,-2,3)), ("unit", (4,)), ("unit", (-4,))),
    "uphill_proper_pair": (("e", (1,2,3)), ("o", (1,2,3)), ("unit", (4,)), ("unit", (-4,))),
    "neutral_proper_pair": (("e", (1,2,3)), ("e", (1,2,4)), ("unit", (5,)), ("unit", (-5,))),
    "neutral_proper_three": (("e", (1,2,3)), ("e", (1,2,4)), ("e", (1,2,5)), ("unit", (6,))),
    "majority_repeat": (("m", (1,2,3)), ("m", (4,5,6)), ("m", (7,8,9)), ("m", (1,3,2))),
    "majority_cross": (("m", (1,2,3)), ("m", (4,5,6)), ("m", (7,8,9)), ("m", (1,4,7))),
    "xor_closed": (("xor", (1,2)), ("xor", (2,3)), ("xor", (3,4)), ("xor", (4,1))),
    "xor_open": (("xor", (1,2)), ("xor", (2,3)), ("xor", (3,4)), ("xor", (4,5))),
    "raw_three": (("unit", (1,)), ("unit", (2,)), ("unit", (3,)), ("xor", (1,3))),
    "raw_four": (("unit", (1,)), ("unit", (2,)), ("unit", (3,)), ("xor", (1,4))),
}


def _row(spec, seed, order, split, family, template, layout):
    rng = random.Random(seed)
    rename = rng.sample(range(1, 10), 9)
    questions = []
    for op, labels in spec:
        cells = [rename[abs(v)-1] * (1 if v > 0 else -1) for v in labels]
        rows = []
        for clause in _clauses(op, cells):
            shuffled = list(clause)
            rng.shuffle(shuffled)
            rows.append(tuple(shuffled))
        rng.shuffle(rows)
        questions.append(tuple(rows))
    wiring = tuple(questions[i] for i in order)
    key = hashlib.sha256(json.dumps(wiring, separators=(",", ":")).encode()).hexdigest()[:16]
    meta = {"split": split, "family": family, "template": template, "layout": layout,
            "port_order": list(order), "cell_order": [x-1 for x in rename]}
    return key, wiring, meta


def training_panel():
    return tuple(_row(spec, 20341 + 13*i, ORDERS[(7*i) % 24], "train", name, name, f"train-{i}")
                 for i in range(4) for name, spec in TRAIN.items())


def _eight_spec(index):
    name, supports, ops, flips = EIGHT[index]
    return name, tuple((op, tuple(-v if flip & (1 << i) else v for i, v in enumerate(links)))
                       for op, links, flip in zip(ops, supports, flips))


def held_panel():
    rows = []
    for i in range(len(EIGHT)):
        name, spec = _eight_spec(i)
        rows.append(_row(spec, 41987 + 23*i, ORDERS[(5*i+3) % 24], "held", "plateau_eight", name, f"eight-{i}"))
    name, spec = _eight_spec(0)
    for i, order in enumerate(ORDERS):
        row = _row(spec, 51361 + 17*i, order, "held", "plateau_relabel", name, f"relabel-{i}")
        row[2]["relabel_of"] = rows[0][0]
        rows.append(row)
    for i in range(4):
        # Paired controls use identical raw source, port, clause, and pin permutations.
        group = [_row(spec, 62533 + 19*i, ORDERS[(5*i+9) % 24], "held", name, name, f"controlled-{i}")
                 for name, spec in HELD.items()]
        keys = {meta["family"]: key for key, _, meta in group}
        twins = {"majority_repeat": "majority_cross", "xor_closed": "xor_open", "raw_three": "raw_four"}
        twins.update({v: k for k, v in twins.items()})
        for _, _, meta in group:
            if meta["family"] in twins:
                meta["partner"] = keys[twins[meta["family"]]]
        rows.extend(group)
    return tuple(rows)


@lru_cache(maxsize=1)
def _archived_inputs():
    path = ROOT / "research" / PRIOR / "wirings.py"
    spec = importlib.util.spec_from_file_location("group_sender_archived_wiring", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return tuple(module.held_panel()) + tuple(module.stress_panel())


def historical_panel():
    """Replay saved baseline records. This does not fit or execute the preceding sender."""
    records = json.loads(RESULT.read_bytes())["conditions"]["varied"]
    source = {key: (w, meta) for key, w, meta in _archived_inputs()}
    rows = []
    for section in ("held", "stress"):
        for record in records[section]["menus"]:
            if section == "held" and record["width"] == record["minimum"]:
                continue
            key = record["id"]
            wiring, original = source[key]
            meta = dict(original, split="historical", template=record["family"],
                        original_section=section, earlier_width=record["width"],
                        earlier_minimum=record["minimum"], earlier_correct_bits=record["correct_bits"])
            rows.append((key, wiring, meta))
    return tuple(rows)


@lru_cache(maxsize=None)
def _table(question):
    value = UNIVERSE
    for clause in question:
        row = 0
        for literal in clause:
            col = COLUMNS[abs(literal)-1]
            row |= col if literal > 0 else UNIVERSE ^ col
        value &= row
    return value


def truth(wiring, raw_mask):
    if not 0 <= raw_mask < 512:
        raise ValueError("Expected a 9-bit relation")
    return tuple((_table(q) >> raw_mask) & 1 for q in wiring)


def _support(table):
    return {i for i, col in enumerate(COLUMNS) if (table ^ (table >> (1 << i))) & (UNIVERSE ^ col)}


def _incidence_key(support):
    return min(tuple(sorted(sum((cell in support[q]) << i for i, q in enumerate(order))
                            for cell in set.union(*support))) for order in ORDERS)


def measure(wiring):
    tables = [_table(q) for q in wiring]
    support = [_support(table) for table in tables]
    identity = [tuple(sorted(tuple(sorted(c)) for c in q)) for q in wiring]
    widths = []
    for mask in range(16):
        computed = {identity[i] for i in range(4) if mask & (1 << i)}
        sources = set().union(*(s for i, s in enumerate(support) if identity[i] not in computed))
        widths.append(len(computed) + len(sources))
    counts = Counter(truth(wiring, raw) for raw in MASKS)
    return {
        "distinct_answers": len(counts), "minimum_bits": (len(counts)-1).bit_length(),
        "essential_sources_by_port": [sorted(s) for s in support],
        "source_incidence_key": list(_incidence_key(support)),
        "answer_multiplicity_multiset": sorted(counts.values()),
        "recompute_or_copy_widths_by_mask": widths,
        "minimum_recompute_or_copy": min(widths),
        "all_computed_slots": widths[15], "all_raw_slots": widths[0],
        "profitable_singletons": sum(widths[1 << i] < widths[0] for i in range(4)),
        "least_profitable_group_size": min((m.bit_count() for m in range(1,16) if widths[m] < widths[0]), default=None),
    }


def audit():
    train, held, historical = training_panel(), held_panel(), historical_panel()
    if len({w for _, w, _ in train+held+historical}) != len(train+held+historical):
        raise AssertionError("A raw wiring was reused")
    train_topologies = {tuple(measure(w)["source_incidence_key"]) for _, w, _ in train}
    eight = {}
    references = {}
    for key, w, meta in train + held:
        if len(w) != 4 or any(sorted(map(len, q)) != [2,2,2,3] for q in w):
            raise AssertionError(f"Malformed raw clauses for {key}")
        row = measure(w)
        widths = row["recompute_or_copy_widths_by_mask"]
        if meta["family"] == "plateau_eight":
            if widths[0] != 6 or any(widths[1 << i] != 7 for i in range(4)) or row["minimum_bits"] != widths[15] or widths[15] != 4:
                raise AssertionError(f"The six-to-four group test failed at {key}")
            if tuple(row["source_incidence_key"]) in train_topologies:
                raise AssertionError("A held coordinated incidence pattern was seen in training")
            eight[key] = row
        references.setdefault(meta["template"], row)
    if len(eight) != 8:
        raise AssertionError("Expected eight newly constructed coordinated fixtures")
    old_counts = Counter((r["earlier_width"], r["earlier_minimum"]) for _, _, r in historical)
    if old_counts != {(5,3):12, (6,4):6, (3,3):1, (9,4):1}:
        raise AssertionError(f"Historical baseline drift: {old_counts}")
    return {"training": len(train), "held": len(held), "historical": len(historical),
            "earlier_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
            "historical_six_ids": [k for k, _, m in historical if m["earlier_width"] == 6],
            "eight_new": eight, "representative_by_template": references}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
