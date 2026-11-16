"""Anonymous signed-clause wirings and the grader's allowed-relation oracle."""

import hashlib
import json
import random
from collections import Counter
from itertools import combinations, permutations, product


Clause = tuple[int, ...]
Question = tuple[Clause, ...]
Wiring = tuple[Question, ...]
MASKS = range(512)
TRAIN_FAMILIES = ("any", "one_exclusion", "two_exclusions", "independent", "alias", "repeat_any")
CORE_FAMILIES = ("any", "exactly_one", "independent", "matched_negative")
EXTRA_FAMILIES = CORE_FAMILIES + ("alias", "repeat_any", "xor_known", "xor_new")
PORT_PERMUTATIONS = tuple(permutations(range(4)))


def truth(wiring: Wiring, raw_mask: int) -> tuple[int, ...]:
    """Return all four port answers in their physical order for one 9-bit relation."""
    if not 0 <= raw_mask < 512:
        raise ValueError("Expected a 9-bit raw relation")
    def literal_value(literal):
        raw_bit = (raw_mask >> (abs(literal) - 1)) & 1
        return raw_bit == int(literal > 0)
    return tuple(int(all(any(literal_value(pin) for pin in clause) for clause in question))
                 for question in wiring)


def _tautologies(cells):
    return [(v, -v) for v in cells]


def _unit(v, decoys, style):
    if style == "expanded_units":
        # If v is false the binary rows force both decoys false, violating the triple.
        s, t = decoys[:2]
        return [(v, s, t), (v, -s), (v, -t), (s, -s)]
    pads = (v, v, v) if style == "local_padding" else decoys
    return [(v, v, v)] + _tautologies(pads)


def _any(a, b, c, decoys, style):
    pads = (a, b, c) if style == "local_padding" else decoys
    return [(a, b, c)] + _tautologies(pads)


def _shuffle_question(question, seed):
    rng = random.Random(seed)
    clauses = []
    for row in question:
        pins = list(row)
        rng.shuffle(pins)
        clauses.append(tuple(pins))
    rng.shuffle(clauses)
    return tuple(clauses)


def _logical_ports(family, cells, style, variant):
    a, b, c, d = (v + 1 for v in cells)
    decoys = [v for v in range(1, 10) if v not in (a, b, c, d)][:3]
    singles = [_unit(v, decoys, style) for v in (a, b, c)]
    any_read = _any(a, b, c, decoys, style)
    edges = ((-a, -b), (-a, -c), (-b, -c))
    if family == "repeat_any":
        return [any_read] * 4
    if family == "any":
        extra = any_read
    elif family == "one_exclusion":
        extra = [(a, b, c)] + [edges[variant % 3]] * 3
    elif family == "two_exclusions":
        extra = [(a, b, c), edges[variant % 3]] + [edges[(variant + 1) % 3]] * 2
    elif family == "exactly_one":
        extra = [(a, b, c), *edges]
    elif family == "matched_negative":
        # The three negative rows have the same signed degree at every cell as exactly_one.
        extra = [(a, b, c), (-a, -a), (-b, -c), (-b, -c)]
    elif family in ("independent", "alias"):
        extra = _unit(d if family == "independent" else c, decoys, style)
    elif family in ("xor_known", "xor_new"):
        v = b if family == "xor_known" else d
        pads = (a, v) if style == "local_padding" else tuple(decoys[:2])
        extra = [(a, v, v), (-a, -v)] + _tautologies(pads)
    else:
        raise ValueError(f"Unknown wiring family {family}")
    return singles + [extra]


def _group(split, layout_id, cells, port_order, style, variant, families):
    specs = []
    for family in families:
        ports = _logical_ports(family, cells, style, variant)
        # These seeds are the same for every member of a matched rewire group.
        ports = [_shuffle_question(port, 1301 + 43 * variant + i) for i, port in enumerate(ports)]
        wiring = tuple(ports[i] for i in port_order)
        wire_id = hashlib.sha256(json.dumps(wiring, separators=(",", ":")).encode()).hexdigest()[:16]
        metadata = {
            "split": split, "family": family, "layout": layout_id, "padding": style,
            "source_cells": cells, "port_order": port_order, "varied_port": port_order.index(3),
            "pair_variant": variant % 3,
        }
        specs.append((wire_id, wiring, metadata))
    partners = {meta["family"]: key for key, _, meta in specs}
    for _, _, meta in specs:
        meta["partners"] = {name: key for name, key in partners.items() if name != meta["family"]}
    return specs


def _rotated_order(i):
    base = (2, 0, 3, 1)
    k = i % len(base)
    return base[k:] + base[:k]


def training_panel():
    """Return (opaque id, raw wiring, grader-only metadata) for 36 training menus."""
    items = []
    for i in range(6):
        cells = tuple((v + i) % 9 for v in (0, 2, 6, 8))
        style = ("local_padding", "tautological_decoys")[i % 2]
        items.extend(_group("train", f"training-{i}", cells, _rotated_order(i), style, i, TRAIN_FAMILIES))
    return tuple(items)


def held_panel():
    """Return 168 assessment menus, including matched physical interventions."""
    items = []
    for i, order in enumerate(PORT_PERMUTATIONS):
        # Leave the pins and clause order unchanged across all 24 port permutations.
        items.extend(_group("held", f"port-permutation-{i}", (0, 1, 4, 7), order,
                            "local_padding", 9, CORE_FAMILIES))
    for i in range(9):
        cells = tuple((v + i) % 9 for v in (0, 2, 4, 8))
        style = ("local_padding", "tautological_decoys", "expanded_units")[i % 3]
        items.extend(_group("held", f"source-placement-{i}", cells, _rotated_order(i), style, 12+i, EXTRA_FAMILIES))
    return tuple(items)


def stress_panel():
    """Two assessment-only menus whose four questions are all composed."""
    cells = (7, 2, 5, 0, 8, 4, 6, 1, 3)
    order = (2, 3, 0, 1)
    a, b, c, d, e, f, g, h, i = (v+1 for v in cells)
    specs = []
    for family, last in (("stress_repeat_exactly_one", (a, c, b)), ("stress_cross_exactly_one", (a, d, g))):
        ports = []
        for slot, (x, y, z) in enumerate(((a, b, c), (d, e, f), (g, h, i), last)):
            clauses = [(x, y, z), (-x, -y), (-x, -z), (-y, -z)]
            ports.append(_shuffle_question(clauses, 3413 + slot))
        wiring = tuple(ports[logical] for logical in order)
        key = hashlib.sha256(json.dumps(wiring, separators=(",", ":")).encode()).hexdigest()[:16]
        specs.append((key, wiring, {
            "split": "stress", "family": family, "layout": "four-composed-questions", "padding": "composed",
            "source_cells": cells, "port_order": order, "varied_port": order.index(3), "pair_variant": 0,
        }))
    for _, _, meta in specs:
        meta["partners"] = {ref["family"]: key for key, _, ref in specs if ref["family"] != meta["family"]}
    return tuple(specs)


def _expected(meta, mask):
    if meta["split"] == "stress":
        a, b, c, d, e, f, g, h, i = ((mask >> j) & 1 for j in meta["source_cells"])
        fourth = a+b+c == 1 if meta["family"] == "stress_repeat_exactly_one" else a+d+g == 1
        logical = (a+b+c == 1, d+e+f == 1, g+h+i == 1, fourth)
        return tuple(int(logical[j]) for j in meta["port_order"])
    a, b, c, d = ((mask >> i) & 1 for i in meta["source_cells"])
    some = int(bool(a or b or c))
    family = meta["family"]
    if family == "repeat_any":
        return (some,) * 4
    sums = (a+b, a+c, b+c)
    k = meta["pair_variant"]
    fourth = {
        "any": some, "one_exclusion": some and sums[k] < 2,
        "two_exclusions": some and sums[k] < 2 and sums[(k+1) % 3] < 2,
        "exactly_one": a+b+c == 1, "matched_negative": not a and b+c == 1,
        "independent": d, "alias": c, "xor_known": a ^ b, "xor_new": a ^ d,
    }[family]
    logical = (a, b, c, int(fourth))
    return tuple(logical[i] for i in meta["port_order"])


def _signed_exact_one_tables():
    universe = (1 << len(MASKS)) - 1
    cols = [sum(1 << m for m in MASKS if (m >> i) & 1) for i in range(9)]
    tables = set()
    for triple in combinations(cols, 3):
        for signs in product((False, True), repeat=3):
            a, b, c = (x ^ (universe if flip else 0) for x, flip in zip(triple, signs))
            table = (a & ~b & ~c) | (b & ~a & ~c) | (c & ~a & ~b)
            tables.add(table)
            tables.add(table ^ universe)
    return tables


def _stress_audit():
    reports = {}
    degree_profiles = []
    specs = stress_panel()
    for key, wiring, meta in specs:
        answers = [truth(wiring, m) for m in MASKS]
        if any(v != _expected(meta, m) for m, v in enumerate(answers)):
            raise AssertionError(f"Composed questions disagree with their raw oracle at {key}")
        counts = Counter(pin for question in wiring for row in question for pin in row)
        degree_profiles.append(sorted((counts[cell], counts[-cell]) for cell in range(1, 10)))
        signature_counts = Counter("".join(map(str, v)) for v in answers)
        reports[meta["family"]] = {
            "id": key, "distinct_answer_vectors": len(signature_counts),
            "answer_vector_multiplicities": dict(sorted(signature_counts.items())),
            "essential_raw_cells": [cell for cell in range(9)
                                    if any(answers[m] != answers[m ^ (1 << cell)] for m in MASKS)],
        }
    _, w, meta = specs[0]
    other = specs[1][1]
    if degree_profiles[0] != degree_profiles[1] or any(
            w[i] != other[i] for i in range(4) if i != meta["varied_port"]):
        raise AssertionError("Composed intervention changed a control feature")
    return {"menus": reports, "shared_signed_degree_multiset": degree_profiles[0],
            "changed_port_answers": sum(truth(w, m) != truth(other, m) for m in MASKS)}


def audit():
    """Audit construction and leakage without fitting an encoder or decoder."""
    train, held = training_panel(), held_panel()
    all_menus = train + held
    lookup = {key: (wiring, meta) for key, wiring, meta in all_menus}
    if len(lookup) != len(all_menus) or len({w for _, w, _ in all_menus}) != len(all_menus):
        raise AssertionError("Duplicate menu identity or raw wiring")
    training_ports = set()
    family_counts = Counter()
    signature_counts = {}
    for key, wiring, meta in all_menus:
        if len(wiring) != 4 or any(sorted(map(len, q)) != [2, 2, 2, 3] for q in wiring):
            raise AssertionError(f"Unexpected raw shape for {key}")
        if any(not 1 <= abs(pin) <= 9 for q in wiring for row in q for pin in row):
            raise AssertionError(f"Unexpected cell index for {key}")
        answers = [truth(wiring, m) for m in MASKS]
        if any(value != _expected(meta, m) for m, value in enumerate(answers)):
            raise AssertionError(f"Raw clauses disagree with intended reader for {key}")
        family = meta["family"]
        family_counts[meta["split"], family] += 1
        signature_counts.setdefault(family, set()).add(len(set(answers)))
        if meta["split"] == "train":
            for values in zip(*answers):
                training_ports.add(sum(bit << m for m, bit in enumerate(values)))
    leaks = training_ports & _signed_exact_one_tables()
    if leaks:
        raise AssertionError("A training question computes signed exactly-one or its complement")
    controls = {}
    for target, control in (("exactly_one", "matched_negative"), ("alias", "independent"), ("xor_known", "xor_new")):
        pairs = changed = 0
        for _, w, meta in held:
            if meta["family"] != target or control not in meta["partners"]:
                continue
            other, ref = lookup[meta["partners"][control]]
            q = meta["varied_port"]
            if any(w[i] != other[i] for i in range(4) if i != q) or meta["port_order"] != ref["port_order"]:
                raise AssertionError("Counterfactual changed another port")
            if target == "exactly_one" and Counter(pin for row in w[q] for pin in row) != Counter(
                    pin for row in other[q] for pin in row):
                raise AssertionError("Matched negative rows changed a signed incidence count")
            if target == "xor_known":
                _, b, _, d = meta["source_cells"]
                replaced = tuple(tuple((d+1 if pin > 0 else -d-1) if abs(pin) == b+1 else pin
                                       for pin in row) for row in w[q])
                if replaced != other[q]:
                    raise AssertionError("The XOR rewire changed more than the one operand")
            pairs += 1
            changed += sum(_expected(meta, m)[q] != _expected(ref, m)[q] for m in MASKS)
        controls[target + "__" + control] = {"pairs": pairs, "changed_port_answers": changed}
    return {
        "training_wirings": len(train), "held_wirings": len(held), "masks_per_wiring": len(MASKS),
        "wiring_counts": {s: {f: n for (stage, f), n in family_counts.items() if stage == s} for s in ("train", "held")},
        "distinct_answer_vector_counts": {f: sorted(ns) for f, ns in signature_counts.items()},
        "unique_training_port_truths": len(training_ports), "training_signed_exactly_one_or_complement_leaks": len(leaks),
        "matched_controls": controls, "separate_stress": _stress_audit(),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
