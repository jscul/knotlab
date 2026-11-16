"""Concealed read-once Boolean tasks. Only n and queried input/output pairs reach a learner."""

import hashlib
import itertools
import json
import operator
import random
from collections import Counter
from functools import lru_cache


OPS = {"AND": operator.and_, "OR": operator.or_, "XOR": operator.xor}
NEUTRAL_SEED = 41269
EDIT_SEED = 52883
RENAME_SEED = 64217
INITIAL_SEED = 87019
ID_SEED = 95339
ORDER_SEED = 103483

# A span is the number of leaves in a selected XOR with an immediate AND operand.
# A span of three gives a bare fold inside a larger rule. A full span places
# extra structure inside the fold. A four-leaf span at n=5 does both at once.
SLOTS = {4: ((3, "rotation"), (4, "substitution"), (4, "rotation"), (4, "substitution")),
         5: ((3, "substitution"), (5, "rotation"), (4, "substitution"), (4, "rotation"))}


@lru_cache(maxsize=None)
def _column(n, i):
    return sum(1 << x for x in range(1 << n) if x & (1 << i))


@lru_cache(maxsize=None)
def _truth(tree, n):
    if isinstance(tree, int):
        return _column(n, tree)
    gate, left, right = tree
    return OPS[gate](_truth(left, n), _truth(right, n))


@lru_cache(maxsize=None)
def _syntax(first, count):
    if count == 1:
        return (first,)
    return tuple((op, left, right) for size in range(1, count)
                 for left in _syntax(first, size) for right in _syntax(first + size, count - size)
                 for op in OPS)


def _partitions(subset):
    part = (subset - 1) & subset
    while part:
        other = subset ^ part
        if part < other:
            yield part, other
        part = (part - 1) & subset


@lru_cache(maxsize=None)
def _universe(n):
    """All primitive truth functions, possible semantic fold spans and a primitive witness.

    Replacing an occurrence of the saved fold with its two primitive gates
    creates an XOR with an AND child. Conversely each such occurrence packages
    into one call. Rejoining every disjoint bipartition finds equivalent trees
    too, including witnesses different from the first primitive representative.
    """
    spans, and_roots, witnesses = {}, {}, {}
    for size in range(1, n + 1):
        for leaves in itertools.combinations(range(n), size):
            subset = sum(1 << i for i in leaves)
            if size == 1:
                col = _column(n, leaves[0])
                spans[subset], and_roots[subset], witnesses[subset] = {col: 0}, set(), {col: leaves[0]}
                continue
            possible, rooted, first = {}, set(), {}
            for a, b in _partitions(subset):
                for x, xs in spans[a].items():
                    for y, ys in spans[b].items():
                        for op, apply in OPS.items():
                            value = apply(x, y)
                            sizes = xs | ys
                            if op == "AND":
                                rooted.add(value)
                            if op == "XOR" and (x in and_roots[a] or y in and_roots[b]):
                                sizes |= 1 << size
                            possible[value] = possible.get(value, 0) | sizes
                            if value not in first:
                                first[value] = (op, witnesses[a][x], witnesses[b][y])
            spans[subset], and_roots[subset], witnesses[subset] = possible, rooted, first
    full = (1 << n) - 1
    return spans[full], witnesses[full]


@lru_cache(maxsize=None)
def _orbits(n):
    functions, _ = _universe(n)
    maps = [tuple(sum(((x >> new) & 1) << old for old, new in enumerate(p)) for x in range(1 << n))
            for p in itertools.permutations(range(n))]
    by_table, classes = {}, {}
    for truth in sorted(functions):
        if truth in by_table:
            continue
        members = {sum(((truth >> old) & 1) << new for new, old in enumerate(mapping)) for mapping in maps}
        if not members.issubset(functions):
            raise AssertionError("Primitive class is not closed under input renaming")
        classes[truth] = tuple(sorted(members))
        by_table.update(dict.fromkeys(members, truth))
    return by_table, classes


@lru_cache(maxsize=None)
def _explicit_sites(tree):
    if isinstance(tree, int):
        return 1, ()
    gate, left, right = tree
    nl, sl = _explicit_sites(left)
    nr, sr = _explicit_sites(right)
    site = gate == "XOR" and any(isinstance(child, tuple) and child[0] == "AND" for child in (left, right))
    return nl + nr, sl + sr + ((nl + nr,) if site else ())


def _edits(tree, path=()):
    if isinstance(tree, int):
        return
    gate, left, right = tree
    for op in OPS:
        if op != gate:
            yield "substitution", path, (op, left, right)
    if isinstance(left, tuple):
        lower, a, b = left
        yield "rotation", path, (lower, a, (gate, b, right))
    if isinstance(right, tuple):
        lower, b, c = right
        yield "rotation", path, (lower, (gate, left, b), c)
    for kind, where, new in _edits(left, path + (0,)):
        yield kind, where, (gate, new, right)
    for kind, where, new in _edits(right, path + (1,)):
        yield kind, where, (gate, left, new)


def _gates(tree):
    if isinstance(tree, int):
        return ()
    op, left, right = tree
    return (op,) + _gates(left) + _gates(right)


def _rename(tree, order):
    if isinstance(tree, int):
        return order[tree]
    op, left, right = tree
    return op, _rename(left, order), _rename(right, order)


def _initial(n):
    """Independent of task identity and class: draw distinct rows of predetermined Hamming weights."""
    rng = random.Random(INITIAL_SEED + 137 * n)
    weights = {4: (1, 2, 3, 2, 4), 5: (1, 4, 2, 3, 2, 3, 5)}[n]
    rows = []
    for weight in weights:
        eligible = [x for x in range(1, 1 << n) if x.bit_count() == weight and x not in rows]
        rows.append(rng.choice(eligible))
    return tuple(rows)


@lru_cache(maxsize=2)
def _matched(n, reserved):
    semantic, _ = _universe(n)
    by_table, _ = _orbits(n)
    pools = {slot: {} for slot in SLOTS[n]}
    for tree in _syntax(0, n):
        _, sites = _explicit_sites(tree)
        if not sites:
            continue
        truth = _truth(tree, n)
        pos = by_table[truth]
        if pos in reserved:
            continue
        for kind, where, control in _edits(tree):
            other = _truth(control, n)
            neg = by_table[other]
            if semantic[other] or neg in reserved:
                continue
            for span in set(sites):
                slot = (span, kind)
                if slot not in pools:
                    continue
                # The rank uses fixture properties only. Prefer matched output
                # frequencies, a span with no other semantic placement, and a
                # control which still contains AND and XOR after the edit.
                tie = hashlib.sha256(repr((EDIT_SEED, n, slot, tree, control)).encode()).digest()
                rank = (abs(truth.bit_count() - other.bit_count()), semantic[truth].bit_count(),
                        int(not {"AND", "XOR"}.issubset(_gates(control))), tie)
                entry = (rank, pos, neg, tree, control, where)
                previous = pools[slot].get((pos, neg))
                if previous is None or rank < previous[0]:
                    pools[slot][pos, neg] = entry
    candidates = {slot: sorted(rows.values()) for slot, rows in pools.items()}

    def choose(index, used):
        if index == len(SLOTS[n]):
            return []
        for _, pos, neg, tree, control, where in candidates[SLOTS[n][index]]:
            if pos in used or neg in used:
                continue
            rest = choose(index + 1, used | {pos, neg})
            if rest is not None:
                return [(tree, control, where)] + rest
        return None

    selected = choose(0, reserved)
    if selected is None:
        raise AssertionError(f"Cannot fill matched classes at n={n}")
    return selected


def _rows(n):
    by_table, classes = _orbits(n)
    semantic, witnesses = _universe(n)
    neutral_rng = random.Random(NEUTRAL_SEED + n)
    # Every mechanism has the same chance before any positive/control is
    # chosen. Within a selected mechanism, choose a labeled truth table uniformly.
    neutral = neutral_rng.sample(sorted(classes), 8)
    neutral_tables = [neutral_rng.choice(classes[key]) for key in neutral]
    ids = random.Random(ID_SEED + n)
    initial = _initial(n)
    rows = []

    def append(tree, group, details):
        truth = _truth(tree, n)
        orbit = by_table[truth]
        spans = [size for size in range(3, n + 1) if semantic[truth] & (1 << size)]
        meta = {"primitive_witness": tree, "canonical_truth": orbit, "labeled_tables_in_class": len(classes[orbit]),
                "fold_realizable": bool(spans), "possible_fold_spans": spans, "ones": truth.bit_count(), **details}
        row = {"id": f"{ids.getrandbits(96):024x}", "n": n, "truth": truth,
               "initial": list(initial), "group": group, "metadata": meta}
        rows.append(row)
        return row

    for truth in neutral_tables:
        append(witnesses[truth], "neutral", {"sampling": "uniform-input-permutation-class"})
    for index, (positive, negative, path) in enumerate(_matched(n, frozenset(neutral))):
        perm = random.Random(RENAME_SEED + 37 * n + index).sample(range(n), n)
        span, kind = SLOTS[n][index]
        common = {"pair": f"n{n}-p{index}", "edit": kind, "edit_path": list(path), "positive_witness_fold_span": span}
        pos = append(_rename(positive, perm), "positive", common)
        neg = append(_rename(negative, perm), "negative", common)
        pos["metadata"]["partner"], neg["metadata"]["partner"] = neg["id"], pos["id"]
    return rows


def tasks():
    """Input bit i is (x >> i) & 1; target answer is (truth >> x) & 1.

    The grading record contains the concealed truth, pair and group. Neither
    those fields nor the opaque record ID are predictor features.
    """
    records = _rows(4) + _rows(5)
    random.Random(ORDER_SEED).shuffle(records)
    return records


def audit():
    """Verify the task generator without running either target learner."""
    records = tasks()
    by_id = {r["id"]: r for r in records}
    summary = {}
    if len(by_id) != len(records):
        raise AssertionError("Duplicate opaque ID")
    for n in (4, 5):
        rows = [r for r in records if r["n"] == n]
        semantic, _ = _universe(n)
        _, classes = _orbits(n)
        if Counter(r["group"] for r in rows) != {"positive": 4, "negative": 4, "neutral": 8}:
            raise AssertionError("Incorrect group sizes")
        if len({r["metadata"]["canonical_truth"] for r in rows}) != 16:
            raise AssertionError("Two tasks differ only by variable names")
        if any(r["initial"] != list(_initial(n)) for r in rows):
            raise AssertionError("Initial input rows must be common to the arity")
        pairs = []
        for row in rows:
            table, meta = row["truth"], row["metadata"]
            if table not in semantic or table != _truth(meta["primitive_witness"], n):
                raise AssertionError("Missing or incorrect primitive expression")
            for i in range(n):
                if not any(((table >> x) ^ (table >> (x ^ (1 << i)))) & 1 for x in range(1 << n)):
                    raise AssertionError("Unused input")
            if row["group"] != "positive":
                continue
            other = by_id[meta["partner"]]
            control = other["metadata"]["primitive_witness"]
            edit = (meta["edit"], tuple(meta["edit_path"]), control)
            if (not semantic[table] or semantic[other["truth"]] or other["group"] != "negative"
                    or edit not in _edits(meta["primitive_witness"])):
                raise AssertionError("Unmatched edit or incorrect semantic fold status")
            if meta["edit"] == "rotation" and Counter(_gates(control)) != Counter(_gates(meta["primitive_witness"])):
                raise AssertionError("Rotation changed the primitive gate inventory")
            delta = table ^ other["truth"]
            pairs.append({"pair": meta["pair"], "edit": meta["edit"], "span": meta["positive_witness_fold_span"],
                          "positive_possible_spans": meta["possible_fold_spans"],
                          "ones": [table.bit_count(), other["truth"].bit_count()], "different_rows": delta.bit_count(),
                          "different_initial": sum((delta >> x) & 1 for x in row["initial"])})
        summary[n] = {"labeled_universe": len(semantic), "labeled_foldable": sum(bool(v) for v in semantic.values()),
                      "classes": len(classes), "foldable_classes": sum(bool(semantic[t]) for t in classes),
                      "initial": list(_initial(n)), "pair_differences": sorted(pairs, key=lambda p: p["pair"]),
                      "neutral_foldable": sum(bool(semantic[r["truth"]]) for r in rows if r["group"] == "neutral")}
    return summary


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
