"""Matched blind two-output problems. Only build_train()[0] and build_test()[0] are public.

Each member's training labels are joint residual-class counts at *all* triples, obtained
from its two truth tables. The lexicographic order is combinations(range(n), 3).
build_test does not construct or read training data. audit() alone compares both splits.
"""

import hashlib
import importlib.util
import json
import math
import random
from collections import Counter
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OLD_TICKET = "FOLD-TWO-OUTPUT-20261115-001"
OLD_ARTIFACT = ROOT / "artifacts" / OLD_TICKET / (OLD_TICKET + "-E001_joint_tables")
_spec = importlib.util.spec_from_file_location(
    "_triple_order_boolean_fixtures", ROOT / "research" / OLD_TICKET / "tasks.py"
)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

ARITIES = (7, 8, 9)
PER_ARITY = {"train": 8, "test": 32}
SEEDS = {"train": 9271843, "test": 7520181}
OPERATIONS = ("fold", "mux")
KINDS = ("shared", "rewired")
ARCHIVE_DIGESTS = {
    "primary": "9a221c8946269dc6196bfa80ee480554b1df2d886fd7566872e30a5a97dcc314",
    "sensitivity": "878e9768b5876166f39f222e818899cee3038997d7f9ac97d570881bdf9769d3",
    "grades": "252b7b3696b1b726be3a2a935effd12676b1bf59cffe3953132d2f624159e00f",
}


def _digest(data):
    packed = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(packed).hexdigest()


def _rng(split, purpose, n=0):
    return random.Random(_digest([SEEDS[split], purpose, n]))


def _side(key):
    return "test" if int(key[:2], 16) & 1 else "train"


def _table_summary(n, table):
    """Invariant of a truth table under any permutation of the raw variables."""
    count = table.bit_count()
    coordinates = []
    for i, high in enumerate(_base._columns(n)):
        high_ones = (table & high).bit_count()
        low = _base._full(n) ^ high
        changes = ((table ^ (table >> (1 << i))) & low).bit_count()
        coordinates.append((count - high_ones, high_ones, changes))
    return count, tuple(sorted(coordinates))


def _raw_family(n, outputs):
    # Each output may EVEN permute its own inputs independently. Thus twins have
    # the same key, and equivalent public problems cannot enter opposite domains.
    outputs = sorted(_table_summary(n, table) for table in outputs)
    return _digest(("raw pair domain v1", n, outputs))


def _consumer_family(n, consumers):
    # Remove raw names and evaluate downstream only; argument 0 is the common bit.
    # Cofactor summaries forget external variable names independently and the
    # ordering of the two consumers. A simultaneous reversal of the common bit
    # exchanges the two cofactors, which is removed explicitly.
    k = n - 3
    names = {i: i - 2 for i in range(3, n)}
    descriptors = []
    for consumer in consumers:
        expr = _base._substitute(consumer, 0, names)
        table = _base._evaluate(expr, k + 1)
        left, right = _base._split(k + 1, table, 0)
        descriptors.append((_table_summary(k, left), _table_summary(k, right),
                            (left ^ right).bit_count()))
    orientation1 = tuple(sorted(descriptors))
    orientation2 = tuple(sorted((b, a, d) for a, b, d in descriptors))
    return _digest(("downstream domain v1", n, min(orientation1, orientation2)))


def _archive_keys():
    data = {}
    for name, expected in ARCHIVE_DIGESTS.items():
        packed = (OLD_ARTIFACT / (name + ".json")).read_bytes()
        if hashlib.sha256(packed).hexdigest() != expected:
            raise ValueError(f"Previously frozen {name} panel has changed")
        data[name] = json.loads(packed)
    raw_keys, structures = set(), set()
    for name in ("primary", "sensitivity"):
        for public in data[name]:
            n = public["n"]
            if n not in ARITIES:
                continue
            grade = data["grades"][name][public["id"]]
            raw_keys.add(_raw_family(n, public["outputs"]))
            if grade["kind"] == "shared":
                structures.add(_consumer_family(n, grade["logical_consumers"]))
    return raw_keys, structures


def _grade(n, shared, changed, changed_port):
    """All joint and single-output ranks, derived from the observable truth tables."""
    stable = shared[1 - changed_port]
    before = shared[changed_port]
    after = changed[changed_port]
    triples = tuple(combinations(range(n), 3))
    joint_ranks = [[], []]
    single_ranks = [[], [], []]
    for triple in triples:
        a, b, c = (_base._residuals(n, t, triple) for t in (stable, before, after))
        for ranks, cofactor in zip(single_ranks, (a, b, c)):
            ranks.append(len(set(cofactor)))
        joint_ranks[0].append(len(set(zip(a, b))))
        joint_ranks[1].append(len(set(zip(a, c))))
    details = []
    for side, ranks in enumerate(joint_ranks):
        best = min(ranks)
        widths = [(rank - 1).bit_length() for rank in ranks]
        best_width = min(widths)
        singly_simple = [i for i in range(len(triples))
                         if min(single_ranks[0][i], single_ranks[1 + side][i]) == 2]
        details.append({
            "min_classes": best,
            "width": best_width,
            "candidate_classes": ranks,
            "candidate_widths": widths,
            "minimizers": [t for t, width in zip(triples, widths) if width == best_width],
            "class_minimizers": [t for t, rank in zip(triples, ranks) if rank == best],
            "single_output_decoys": [triples[i] for i in singly_simple if widths[i] > best_width],
        })
    return details


def _sample(split, n, index, forms, names_rng, known_raw, known_structures):
    operation = OPERATIONS[index % 2]
    swap = (index // 2 + n) % 2
    port_order = (swap, 1 - swap)
    changed_port = port_order.index(1)
    # Relabel once for this slot. All rejection criteria are invariant under this draw.
    names = tuple(names_rng.sample(range(n), n))
    group = tuple(sorted(names[:3]))
    match_histogram = (index // 2) % 4 == 0
    rejects = Counter()
    for trial in range(1, 8193):
        consumers = tuple(_base._random_consumer(n, forms) for _ in range(2))
        structure = _consumer_family(n, consumers)
        if _side(structure) != split or structure in known_structures:
            rejects["downstream_domain_or_duplicate"] += 1
            continue
        sources = _base._sources(n, consumers, operation, names, port_order)
        shared = [_base._evaluate(expr, n) for expr in sources[0]]
        if shared[0] == shared[1] or (shared[0] ^ shared[1]) == _base._full(n):
            rejects["identical_or_complement_outputs"] += 1
            continue
        raw_family = _raw_family(n, shared)
        if _side(raw_family) != split or raw_family in known_raw:
            rejects["raw_domain_or_duplicate"] += 1
            continue
        changed = list(shared)
        changed[changed_port] = _base._evaluate(sources[1][changed_port], n)
        hist_equal = _base._histogram(shared) == _base._histogram(changed)
        if match_histogram and not hist_equal:
            rejects["reserved_joint_histogram_match"] += 1
            continue
        details = _grade(n, shared, changed, changed_port)
        if details[0]["min_classes"] != 2 or details[0]["minimizers"] != [group]:
            rejects["shared_minimum_not_unique"] += 1
            continue
        if details[1]["min_classes"] != 4 or group not in details[1]["class_minimizers"]:
            rejects["rewired_minimum_not_four"] += 1
            continue
        if any(not d["single_output_decoys"] for d in details):
            rejects["no_inferior_singly_simple_alternative"] += 1
            continue
        if _raw_family(n, changed) != raw_family:
            raise AssertionError("The single-output rewire must preserve both permutation invariants")
        for table in set(shared + changed):
            if len(_base._support(n, table)) != n:
                raise AssertionError("A public output did not use every input")
        known_raw.add(raw_family)
        known_structures.add(structure)
        both = {
            "n": n, "operation": operation, "structure": structure, "truth_family": raw_family,
            "triple": group, "source_order": names, "port_order": port_order,
            "logical_consumers": consumers, "changed_output": changed_port,
            "common_support": tuple(range(n)), "joint_histogram_matched": hist_equal,
            "construction_draw": trial, "construction_rejections": dict(rejects),
        }
        return [(outputs, {**both, **data, "kind": kind, "source": source})
                for outputs, data, kind, source in zip((shared, changed), details, KINDS, sources)]
    raise RuntimeError(f"Could not fill {split} slot n={n}, slot={index} within the fixed bound")


def _build(split):
    # A charged training build cannot borrow residual calculations from an earlier audit.
    _base._split.cache_clear()
    known_raw, known_structures = _archive_keys()
    records = []
    for n in ARITIES:
        forms = _rng(split, "consumer draws", n)
        names = _rng(split, "physical labels", n)
        for i in range(PER_ARITY[split]):
            pair = _sample(split, n, i, forms, names, known_raw, known_structures)
            records.append(pair)

    pair_ids = _rng(split, "private pair names")
    public_ids = _rng(split, "opaque public names")
    tagged = []
    for pair in records:
        pair_id = f"{pair_ids.getrandbits(96):024x}"
        ids = [f"{public_ids.getrandbits(128):032x}" for _ in pair]
        for side, (outputs, grade) in enumerate(pair):
            public = {"id": ids[side], "n": grade["n"], "outputs": outputs}
            tagged.append((public, {**grade, "pair": pair_id, "partner": ids[1 - side]}))
    _rng(split, "public interleave").shuffle(tagged)
    public = [r for r, _ in tagged]
    grades = {r["id"]: meta for r, meta in tagged}
    if len(grades) != len(public):
        raise AssertionError("Duplicate public identity")
    return public, grades


def build_train():
    """24 pairs, including all supervised rank labels, with no held construction."""
    return _build("train")


def build_test():
    """96 independent held pairs, with labels for the assessor alone."""
    return _build("test")


def _check_split(split, public, grades):
    by_id = {r["id"]: r for r in public}
    seen_tables = set()
    counts = Counter()
    pairs = set()
    shared, rewired = [], []
    for row in public:
        key, n, outputs = row["id"], row["n"], row["outputs"]
        g = grades[key]
        if set(row) != {"id", "n", "outputs"} or (n, *outputs) in seen_tables:
            raise AssertionError("Repeated table or private fields in a public task")
        seen_tables.add((n, *outputs))
        opposite = by_id[g["partner"]]
        other = grades[g["partner"]]
        changed = g["changed_output"]
        if not (other["pair"] == g["pair"] and other["partner"] == key
                and opposite["outputs"][1 - changed] == outputs[1 - changed]
                and opposite["outputs"][changed] != outputs[changed]):
            raise AssertionError("Mismatched paired controls")
        direct = _base._independent_ranks(n, outputs)
        triples = tuple(combinations(range(n), 3))
        ranks = [direct[t] for t in triples]
        widths = [(rank - 1).bit_length() for rank in ranks]
        minimum = min(widths)
        minimizers = [t for t, width in zip(triples, widths) if width == minimum]
        if (any(len(_base._support(n, t)) != n for t in outputs)
                or len(direct) != math.comb(n, 3) or ranks != g["candidate_classes"]
                or widths != g["candidate_widths"] or minimum != g["width"]
                or minimizers != g["minimizers"] or direct[g["triple"]] != min(ranks)
                or min(ranks) != (2 if g["kind"] == "shared" else 4)):
            raise AssertionError("The independent scalar grading disagrees")
        for out, expr in zip(outputs, g["source"]):
            if any(((out >> x) & 1) != _base._scalar(expr, x) for x in range(1 << n)):
                raise AssertionError("Scalar source disagrees with public data")
        if _raw_family(n, outputs) != g["truth_family"] or _side(g["truth_family"]) != split:
            raise AssertionError("Raw whole-task fingerprint disagrees with split")
        if _consumer_family(n, g["logical_consumers"]) != g["structure"] or _side(g["structure"]) != split:
            raise AssertionError("Downstream fingerprint disagrees with split")
        counts[n, g["operation"], g["kind"], changed] += 1
        pairs.add(g["pair"])
        (shared if g["kind"] == "shared" else rewired).append(g)
    expected = PER_ARITY[split] // 4
    if len(pairs) != 3 * PER_ARITY[split] or len(counts) != 24 or set(counts.values()) != {expected}:
        raise AssertionError("Unbalanced arity, hidden operation, kind, or changed output")
    if (len({g["structure"] for g in shared}) != len(pairs)
            or len({g["truth_family"] for g in shared}) != len(pairs)):
        raise AssertionError("Two twins in different pairs have an equivalent family signature")
    return {
        "public_sha256": _digest(public), "grades_sha256": _digest(grades),
        "tasks": len(public), "pairs": len(pairs),
        "pairs_per_arity": PER_ARITY[split], "distinct_downstream_keys": len(pairs),
        "distinct_raw_family_keys": len(pairs),
        "candidate_labels": sum(len(g["candidate_classes"]) for g in grades.values()),
        "consumer_pairs_drawn": sum(g["construction_draw"] for g in shared),
        "pairs_with_matched_joint_histograms": sum(g["joint_histogram_matched"] for g in shared),
        "rewired_with_tied_minimum": sum(len(g["minimizers"]) > 1 for g in rewired),
        "shared_single_output_decoys_range": [min(len(g["single_output_decoys"]) for g in shared),
                                             max(len(g["single_output_decoys"]) for g in shared)],
        "rewired_single_output_decoys_range": [min(len(g["single_output_decoys"]) for g in rewired),
                                              max(len(g["single_output_decoys"]) for g in rewired)],
    }


def audit():
    """Post-construction scalar audit, intentionally outside either charged constructor."""
    raw_keys, structures = _archive_keys()
    ids = set()
    report = {}
    for split, build in (("train", build_train), ("test", build_test)):
        public, grades = build()
        report[split] = _check_split(split, public, grades)
        these = {g["structure"] for g in grades.values()}
        raw = {g["truth_family"] for g in grades.values()}
        if set(grades) & ids or these & structures or raw & raw_keys:
            raise AssertionError("Repeated identity, downstream family, or raw-truth family across panels")
        structures.update(these)
        raw_keys.update(raw)
        ids.update(grades)
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
