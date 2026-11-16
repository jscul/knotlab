"""Opaque truth-table tasks for successive ternary composition. All metadata are grader-only."""

import hashlib
import json
import random
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIOR = "FOLD-REUSE-20261115-001"
PRIOR_PANEL = ROOT / "artifacts" / PRIOR / (PRIOR + "-E001_second_learner") / "panel.json"
# Each character acts from the inside outward. M puts the preceding answer at
# an AND port of F. X places it at the remaining, XOR, port. Swapping the AND
# arguments separately at each M placement adds no new positive mechanism.
PLACEMENTS = {"primary": {2: ("M",), 3: ("MX", "XM", "XX"),
                          4: ("MMM", "MMX", "MXM", "MXX", "XMM", "XMX")},
              "stage2": {2: ("X",), 3: ("MM",), 4: ("XXM", "XXX")}}
SEEDS = {"primary": 41083, "fixed9": 70217, "stage2": 99787}


def _full(n):
    return (1 << (1 << n)) - 1


@lru_cache(maxsize=None)
def _columns(n):
    return tuple(sum(1 << x for x in range(1 << n) if x & (1 << i)) for i in range(n))


def _eval(tree, n):
    if isinstance(tree, int):
        return _columns(n)[tree]
    op, *args = tree
    a = _eval(args[0], n)
    if op == "NOT":
        return _full(n) ^ a
    b = _eval(args[1], n)
    if op == "AND":
        return a & b
    if op == "OR":
        return a | b
    return a ^ b


def _circuit(path, sides, groups, edit, style):
    leaves = [group[0] if len(group) == 1 else ("OR", *group) for group in groups]

    def gate(i, a, b, c):
        local_style = style[i] if isinstance(style, tuple) else style
        op = edit[1] if edit and edit[0] == i else "F"
        if op in ("rotate-a", "rotate-b"):
            x, y = (a, b) if op == "rotate-a" else (b, a)
            if local_style == 0:
                return ("AND", x, ("XOR", y, c))
            if local_style == 1:
                parity = ("AND", ("OR", y, c), ("OR", ("NOT", y), ("NOT", c)))
            else:
                parity = ("OR", ("AND", y, ("NOT", c)), ("AND", ("NOT", y), c))
            return ("AND", x, parity)
        inner = "AND" if op == "F" else "OR"
        term = (inner, a, b)
        if local_style == 0:
            return ("XOR", term, c)
        other = "OR" if inner == "AND" else "AND"
        complement = (other, ("NOT", a), ("NOT", b))
        if local_style == 1:
            return ("OR", ("AND", term, ("NOT", c)), ("AND", complement, c))
        return ("AND", ("OR", term, c), ("OR", complement, ("NOT", c)))

    result = gate(0, *leaves[:3])
    for i, placement in enumerate(path, 1):
        u, v = leaves[2 * i + 1:2 * i + 3]
        if placement == "X":
            result = gate(i, v, u, result) if sides[i] else gate(i, u, v, result)
        else:
            result = gate(i, u, result, v) if sides[i] else gate(i, result, u, v)
    return result


def _shape(tree):
    if isinstance(tree, int):
        return ("leaf",)
    op, *args = tree
    children = []
    for expr in args:
        child = _shape(expr)
        children.extend(child[1:] if child[0] == op else (child,))
    return (op, *sorted(children))


@lru_cache(maxsize=None)
def _indices(n, i, j):
    rest = [k for k in range(n) if k not in (i, j)]
    return tuple(sum(((x >> bit) & 1) << old for bit, old in enumerate(rest)) for x in range(1 << (n - 2)))


def _cofactors(table, n, i, j):
    bases = _indices(n, i, j)
    return tuple(sum(((table >> (x | fixed)) & 1) << small for small, x in enumerate(bases))
                 for fixed in (0, 1 << i, 1 << j, (1 << i) | (1 << j)))


@lru_cache(maxsize=256)
def _gate_class(table):
    return min(sum(((table >> sum(((x >> k) & 1) << old for k, old in enumerate(order))) & 1) << x
                   for x in range(8)) for order in permutations(range(3)))


F_CLASS = _gate_class(sum((((x & 1) & ((x >> 1) & 1)) ^ ((x >> 2) & 1)) << x for x in range(8)))


@lru_cache(maxsize=None)
def repeated_gate_classes(table, n):
    """All single ternary operations whose full chain equals table, modulo six port permutations.

    At any proposed outer pair, a nonconstant cofactor must be the inner
    function or its complement. Both orientations are tested. All other
    cofactors must then be its two phases or constants, fixing the outer
    gate's full eight entries. The same gate must also realize the inner chain.
    The caller supplies a full-support table on an odd number of inputs.
    """
    if n == 3:
        return frozenset((_gate_class(table),))
    matches = set()
    rest_full = _full(n - 2)
    for i, j in combinations(range(n), 2):
        cofactors = _cofactors(table, n, i, j)
        varying = next((c for c in cofactors if c not in (0, rest_full)), None)
        if varying is None or any(c not in (0, rest_full, varying, rest_full ^ varying) for c in cofactors):
            continue
        for inner in (varying, rest_full ^ varying):
            unary = {0: 0, rest_full: 3, inner: 2, rest_full ^ inner: 1}
            outer = _gate_class(sum(unary[c] << (2 * k) for k, c in enumerate(cofactors)))
            if outer in repeated_gate_classes(inner, n - 2):
                matches.add(outer)
    return frozenset(matches)


@lru_cache(maxsize=None)
def _with_or_leaves(table, n, logical):
    """All pure repeated-gate covers after any partition into disjoint OR leaves."""
    if n == logical:
        return repeated_gate_classes(table, n)
    matches = set()
    smaller = set()
    for i, j in combinations(range(n), 2):
        a, b, c, d = _cofactors(table, n, i, j)
        if b == c == d:
            # The OR of the pair becomes the final variable of this smaller truth table.
            smaller.add(a | (b << (1 << (n - 2))))
    for collapsed in smaller:
        matches.update(_with_or_leaves(collapsed, n - 1, logical))
    return frozenset(matches)


def _groups(logical, expanded):
    extra = iter(range(logical, logical + len(expanded)))
    return tuple((i, next(extra)) if i in expanded else (i,) for i in range(logical))


def _digest(*values):
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


def _prior_truths():
    return {(r["n"], r["truth"]) for r in json.loads(PRIOR_PANEL.read_bytes()) if r["n"] == 5}


def _one_pair(split, depth, index, path, used, forbidden):
    n = 9 if split == "fixed9" else 2 * depth + 1
    logical = 2 * depth + 1
    rng = random.Random(SEEDS[split] + depth * 401 + index * 17)
    sides = tuple(rng.getrandbits(1) for _ in range(depth))
    expansions = list(combinations(range(logical), n - logical))
    rng.shuffle(expansions)
    edits = [(i, e) for i in range(depth) for e in ("rotate-a", "rotate-b", "replace-and-with-or")]
    rng.shuffle(edits)
    prefer_rotation = index % 4 != 3
    edits.sort(key=lambda e: e[1].startswith("rotate") != prefer_rotation)
    for edit in edits:
        for expanded in expansions:
            groups = _groups(logical, expanded)
            pos_tree = _circuit(path, sides, groups, None, 0)
            neg_tree = _circuit(path, sides, groups, edit, 0)
            key = _shape(neg_tree)
            if (n, key) in forbidden:
                continue
            pos, neg = _eval(pos_tree, n), _eval(neg_tree, n)
            if pos.bit_count() != 1 << (n - 1) or neg.bit_count() != pos.bit_count():
                continue
            if _with_or_leaves(neg, n, logical) or F_CLASS not in _with_or_leaves(pos, n, logical):
                continue
            for _ in range(64):
                rename = rng.sample(range(n), n)
                physical = tuple(tuple(rename[v] for v in group) for group in groups)
                items = []
                for mutation in (None, edit):
                    # The fourth expression changes spelling at successive calls,
                    # starting with primitive gates at the innermost site.
                    mixed_style = tuple(i % 3 for i in range(depth))
                    styles = [((style,) * depth) for style in range(3)] + [mixed_style]
                    trees = [_circuit(path, sides, physical, mutation, style) for style in styles]
                    values = [_eval(tree, n) for tree in trees]
                    if len(set(values)) != 1 or len(set(trees)) != 4 or len(set(mixed_style)) < 2:
                        raise AssertionError("Expected four distinct equivalent source forms including a mixed form")
                    truth = values[0]
                    identifier = _digest("anonymous", SEEDS[split], depth, index, mutation is not None)[:20]
                    row = {"id": identifier, "n": n, "truth": truth}
                    meta = {"depth": depth, "kind": "positive" if mutation is None else "negative",
                            "pair": _digest("pair", split, depth, index)[:16], "placement": path,
                            "and_sides": list(sides), "logical_inputs": logical, "source_groups": physical,
                            "mutation": mutation, "paired_edit": edit, "balanced_ones": truth.bit_count(),
                            "primitive_gates": n - 1, "primitive_shape": _shape(trees[0]), "sources": trees,
                            "source_styles_innermost_first": styles,
                            "equal_gate_inventory": edit[1].startswith("rotate"),
                            "full_gate_classes_with_or_leaves": sorted(_with_or_leaves(pos if mutation is None else neg, n, logical))}
                    items.append((row, meta))
                if any((n, r["truth"]) in used for r, _ in items):
                    continue
                for row, meta in items:
                    used.add((n, row["truth"]))
                    meta["partner"] = next(r["id"] for r, _ in items if r["id"] != row["id"])
                return items
    raise AssertionError(f"No balanced semantic control for {split}, depth {depth}, index {index}, path {path}")


@lru_cache(maxsize=3)
def _build(split):
    if split not in SEEDS:
        raise ValueError("Expected primary, fixed9 or stage2")
    used = _prior_truths()
    forbidden = set()
    if split != "primary":
        primary = _build("primary")
        used.update((r["n"], r["truth"]) for r, _ in primary)
        if split == "stage2":
            previous = primary + _build("fixed9")
            used.update((r["n"], r["truth"]) for r, _ in previous)
            forbidden.update((r["n"], m["primitive_shape"]) for r, m in previous)
    count = {"primary": 8, "fixed9": 3, "stage2": 4}[split]
    rows = []
    for depth in (2, 3, 4):
        if split == "fixed9" and depth == 4:
            chosen = sorted({m["pair"] for _, m in primary if m["depth"] == 4})[:count]
            rows.extend((r, dict(m, reference=r["id"])) for r, m in primary if m["pair"] in chosen)
            continue
        choices = PLACEMENTS["stage2" if split == "stage2" else "primary"][depth]
        for index in range(count):
            path = choices[index % len(choices)]
            rows.extend(_one_pair(split, depth, index, path, used, forbidden))
    random.Random(SEEDS[split] + 5003).shuffle(rows)
    return tuple(rows)


def tasks():
    return tuple(dict(row) for row, _ in _build("primary"))


def fixed_width_tasks():
    return tuple(dict(row) for row, _ in _build("fixed9"))


def stage2_tasks():
    return tuple(dict(row) for row, _ in _build("stage2"))


def grading(split="primary"):
    return {row["id"]: dict(meta) for row, meta in _build(split)}


def audit():
    previous = _prior_truths()
    summary = {}
    for split in SEEDS:
        records = _build(split)
        per_depth = {}
        for depth in (2, 3, 4):
            rows = [(r, m) for r, m in records if m["depth"] == depth]
            classes = {kind: {m["primitive_shape"] for _, m in rows if m["kind"] == kind} for kind in ("positive", "negative")}
            for row, meta in rows:
                n, truth = row["n"], row["truth"]
                if (n, truth) in previous or truth.bit_count() != 1 << (n - 1):
                    raise AssertionError("An old or unbalanced target appeared")
                if any(((truth ^ (truth >> (1 << i))) & (_full(n) ^ col)) == 0 for i, col in enumerate(_columns(n))):
                    raise AssertionError("Input is inessential")
                actual = _with_or_leaves(truth, n, meta["logical_inputs"])
                if sorted(actual) != meta["full_gate_classes_with_or_leaves"] or (meta["kind"] == "positive") != bool(actual):
                    raise AssertionError("Physical recoding changed truth-only cover verdict")
            per_depth[depth] = {"pairs": len(rows) // 2, "positive_shapes": len(classes["positive"]),
                                "negative_shapes": len(classes["negative"]),
                                "equal_gate_inventory_pairs": sum(m["equal_gate_inventory"] for _, m in rows) // 2,
                                "case_references": sum("reference" in m for _, m in rows),
                                "edit_counts": dict(Counter(m["paired_edit"][1] for _, m in rows if m["kind"] == "negative"))}
        summary[split] = {"depths": per_depth, "public_sha256": _digest([r for r, _ in records])}
    first = {(r["n"], m["primitive_shape"]) for split in ("primary", "fixed9") for r, m in _build(split)}
    second = {(r["n"], m["primitive_shape"]) for r, m in _build("stage2")}
    if not first.isdisjoint(second):
        raise AssertionError("Reserved stage shares a normalized structure with a prior target")
    return summary


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
