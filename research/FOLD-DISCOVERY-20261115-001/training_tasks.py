"""Twenty-four target-only training rules for blind two-gate motif discovery."""

import hashlib
import json
import random
import struct
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REUSE = "FOLD-REUSE-20261115-001"
GATE = "FOLD-GATE-20261115-001"
RELABEL_SEED = 11390217
ORDER_SEED = 11390341
ID_SEED = 11390519
A, B, C, D, E, F, G, H = range(8)


def both(a, b):
    return "AND", a, b


def either(a, b):
    return "OR", a, b


def xor(a, b):
    return "XOR", a, b


def planted(a, b, c):
    return "F", a, b, c


def shifted(a, b, c):
    return "R", a, b, c


def substituted(a, b, c):
    return "Q", a, b, c


def _templates():
    # The order is fixed before any candidate enumeration or learner evaluation.
    # Q replaces the planted AND by OR. R changes the connection of AND and XOR.
    f, q, r = planted, substituted, shifted
    return {
        4: (
            both(f(A, B, C), D), either(f(A, B, C), D),
            f(either(A, B), C, D), f(A, B, either(C, D)),
            xor(f(A, B, C), D), f(xor(A, B), C, D),
            both(q(A, B, C), D), either(r(A, B, C), D),
        ),
        6: (
            either(f(f(A, B, C), D, E), F), f(A, both(f(B, C, D), E), F),
            either(f(A, B, C), f(D, E, F)), f(either(A, B), f(C, D, E), F),
            f(A, B, both(r(C, D, E), F)), f(q(A, B, C), D, either(E, F)),
            either(r(A, B, C), r(D, E, F)), both(q(A, B, C), q(D, E, F)),
        ),
        8: (
            f(either(f(f(A, B, C), D, E), F), G, H),
            f(f(A, B, C), f(D, E, F), either(G, H)),
            f(either(f(A, B, C), D), f(E, F, G), H),
            both(f(A, either(B, C), D), f(E, either(F, G), H)),
            f(r(A, B, C), either(D, E), f(F, G, H)),
            f(q(A, B, C), f(D, E, both(F, G)), H),
            either(r(A, B, C), both(r(D, E, F), either(G, H))),
            both(q(A, B, C), either(q(D, E, F), xor(G, H))),
        ),
    }


def _expand(expr, style, level=0):
    if isinstance(expr, int):
        return expr
    op, *children = expr
    args = [_expand(child, style, level + 1) for child in children]
    if op in ("AND", "OR", "XOR"):
        return (op, *args)
    a, b, c = args
    local = 1 + level % 2 if style == "alternating" else style
    if op == "R":
        if local == 0:
            return both(a, xor(b, c))
        if local == 1:
            return both(a, either(both(b, ("NOT", c)), both(("NOT", b), c)))
        return both(a, both(either(b, c), either(("NOT", b), ("NOT", c))))
    term = both(a, b) if op == "F" else either(a, b)
    if local == 0:
        return xor(term, c)
    neg = either(("NOT", a), ("NOT", b)) if op == "F" else both(("NOT", a), ("NOT", b))
    if local == 1:
        return either(both(term, ("NOT", c)), both(neg, c))
    return both(either(term, c), either(neg, ("NOT", c)))


def _rename(expr, order):
    if isinstance(expr, int):
        return order[expr]
    return (expr[0], *(_rename(child, order) for child in expr[1:]))


@lru_cache(maxsize=None)
def _columns(n):
    return tuple(sum(1 << x for x in range(1 << n) if x & (1 << i)) for i in range(n))


def _evaluate(expr, n):
    if isinstance(expr, int):
        return _columns(n)[expr]
    op, *args = expr
    a = _evaluate(args[0], n)
    if op == "NOT":
        return ((1 << (1 << n)) - 1) ^ a
    b = _evaluate(args[1], n)
    if op == "AND":
        return a & b
    if op == "OR":
        return a | b
    return a ^ b


def _shape(expr):
    if isinstance(expr, int):
        return ("leaf",)
    op, *args = expr
    children = []
    for e in args:
        child = _shape(e)
        children.extend(child[1:] if child[0] == op else (child,))
    return (op, *sorted(children))


def _subshapes(shape):
    """Every complete subtree permitted by reassociation and commutation."""
    op, *kids = shape
    result = {shape}
    for child in kids:
        result.update(_subshapes(child))
    for k in range(2, len(kids)):
        result.update((op, *group) for group in combinations(kids, k))
    return result


def _admits_f(shape):
    return ((shape[0] == "XOR" and any(k[0] == "AND" for k in shape[1:]))
            or any(_admits_f(child) for child in shape[1:]))


def _planted_count(expr):
    if isinstance(expr, int):
        return 0
    return int(expr[0] == "F") + sum(_planted_count(e) for e in expr[1:])


@lru_cache(maxsize=1)
def _old_tables():
    # Target identities only, without any predecessor actions, scores or choices.
    source = ROOT / "artifacts" / REUSE / (REUSE + "-E001_second_learner") / "panel.json"
    tables = {(r["n"], r["truth"]) for r in json.loads(source.read_bytes()) if r["n"] == 4}
    directory = ROOT / "artifacts" / GATE / (GATE + "-E001_gated_stream")
    for split in ("train", "held"):
        with (directory / (split + ".bin")).open("rb") as record:
            header = json.loads(record.readline())
            words = record.read()
        if header["split"] != split or hashlib.sha256(words).hexdigest() != header["ordered_truths_sha256"]:
            raise ValueError("Unexpected archived target stream")
        tables.update((6, v) for v, in struct.iter_unpack("<Q", words))
    return frozenset(tables)


@lru_cache(maxsize=1)
def _rows():
    records = []
    used = set(_old_tables())
    ids = random.Random(ID_SEED)
    for n, templates in _templates().items():
        for index, template in enumerate(templates):
            chooser = random.Random(RELABEL_SEED + 127 * n + index)
            for attempt in range(1024):
                order = chooser.sample(range(n), n)
                private_tree = _rename(template, order)
                base = _expand(private_tree, 0)
                truth = _evaluate(base, n)
                if (n, truth) not in used:
                    break
            else:
                raise AssertionError("No fresh labeling found for the predeclared mechanism")
            used.add((n, truth))
            row = {"id": f"{ids.getrandbits(96):024x}", "n": n, "truth": truth}
            meta = {"primitive_source": base, "generator_source": private_tree,
                    "planted_calls": _planted_count(template), "ones": truth.bit_count(),
                    "shape": _shape(base), "label_draws": attempt + 1}
            records.append((row, meta))
    random.Random(ORDER_SEED).shuffle(records)
    return tuple(records)


def training_tasks():
    """Opaque bookkeeping ID, number of essential inputs, and labels packed at bit x."""
    return tuple(dict(row) for row, _ in _rows())


def grading():
    """Generator witnesses; the fitting path receives none of these fields."""
    return {r["id"]: dict(meta) for r, meta in _rows()}


def _reserved_families():
    # From the preceding frozen placement split: X at five, MM at seven.
    # Include all balanced one-site variants in these families. This is a
    # superset of their actual reserved controls and reads no reserved labels.
    forbidden = set()
    for steps in ("X", "MM"):
        depth = len(steps) + 1
        n = 2 * depth + 1
        for sides in product((False, True), repeat=depth):
            for edited in range(-1, depth):
                for variant in ("rotate_a", "rotate_b", "or"):
                    def term(i, a, b, c):
                        if i != edited:
                            return planted(a, b, c)
                        if variant == "or":
                            return substituted(a, b, c)
                        return shifted(a, b, c) if variant == "rotate_a" else shifted(b, a, c)

                    expr = term(0, 0, 1, 2)
                    for i, position in enumerate(steps, 1):
                        a, b = 2 * i + 1, 2 * i + 2
                        if position == "X":
                            expr = term(i, b, a, expr) if sides[i] else term(i, a, b, expr)
                        else:
                            expr = term(i, a, expr, b) if sides[i] else term(i, expr, a, b)
                    source = _expand(expr, 0)
                    if _evaluate(source, n).bit_count() == 1 << (n - 1):
                        forbidden.add(_shape(source))
    return forbidden


def audit():
    """Fixture checks only. No candidate extraction, solving, ranking or held evaluations."""
    rows = _rows()
    forbidden = _reserved_families()
    summary = {}
    for n in (4, 6, 8):
        local = [(r, m) for r, m in rows if r["n"] == n]
        if len(local) != 8 or len({m["shape"] for _, m in local}) != 8:
            raise AssertionError(f"Expected eight different mechanisms at {n} inputs")
        for r, m in local:
            truth = r["truth"]
            if (n, truth) in _old_tables() or _admits_f(m["shape"]) != bool(m["planted_calls"]):
                raise AssertionError("Old target or misclassified planted/near-miss task")
            if any(((truth ^ (truth >> (1 << i))) & (((1 << (1 << n)) - 1) ^ c)) == 0
                   for i, c in enumerate(_columns(n))):
                raise AssertionError("An input was inessential")
            sources = [_expand(m["generator_source"], style) for style in (0, 1, 2, "alternating")]
            if len(set(sources[:3])) != 3 or any(_evaluate(s, n) != truth for s in sources):
                raise AssertionError("Non-equivalent source spellings")
            if forbidden.intersection(_subshapes(m["shape"])):
                raise AssertionError(f"A complete reserved-family subtree occurs in the training template: {m['generator_source']}")
        summary[n] = {"tasks": len(local), "distinct_mechanisms": len({m["shape"] for _, m in local}),
                      "planted_calls_histogram": dict(Counter(m["planted_calls"] for _, m in local)),
                      "ones_per_truth_table": sorted(m["ones"] for _, m in local),
                      "balanced_tasks": sum(m["ones"] == 1 << (n - 1) for _, m in local),
                      "exact_older_labels_skipped": sum(m["label_draws"] - 1 for _, m in local)}
    if len({r["id"] for r, _ in rows}) != 24:
        raise AssertionError("Duplicate task identifier")
    digest = hashlib.sha256(json.dumps(training_tasks(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"per_arity": summary, "targets_sha256": digest, "reserved_family_shapes_checked": len(forbidden)}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
