"""Two-output tasks with a hidden three-variable boundary. Only the two packed truth tables are public."""

import hashlib
import json
import random
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations


H = "inner"
FORM_SEED, RENAME_SEED, ORDER_SEED, ID_SEED = 816271, 816283, 816301, 816317


def _both(a, b):
    return "AND", a, b


def _either(a, b):
    return "OR", a, b


def _xor(a, b):
    return "XOR", a, b


def _full(n):
    return (1 << (1 << n)) - 1


@lru_cache(maxsize=None)
def _columns(n):
    return tuple(sum(1 << x for x in range(1 << n) if x & (1 << i)) for i in range(n))


def _evaluate(expr, n):
    if isinstance(expr, int):
        return _columns(n)[expr]
    gate, *args = expr
    a = _evaluate(args[0], n)
    if gate == "NOT":
        return _full(n) ^ a
    b = _evaluate(args[1], n)
    if gate == "AND":
        return a & b
    if gate == "OR":
        return a | b
    return a ^ b


def _substitute(expr, core, rename):
    if expr == H:
        return core
    if isinstance(expr, int):
        return rename[expr]
    return (expr[0], *(_substitute(child, core, rename) for child in expr[1:]))


def _core(operation, a, b, c, changed):
    if operation == "fold":
        return _xor(_both(a, c), b) if changed else _xor(_both(a, b), c)
    selector, yes = (b, a) if changed else (a, b)
    return _either(_both(selector, yes), _both(("NOT", selector), c))


def _sources(n, consumers, operation, rename, order):
    a, b, c = rename[:3]
    original = _core(operation, a, b, c, False)
    altered = _core(operation, a, b, c, True)
    first = _substitute(consumers[0], original, rename)
    common = (first, _substitute(consumers[1], original, rename))
    rewired = (first, _substitute(consumers[1], altered, rename))
    return tuple(tuple(pair[k] for k in order) for pair in (common, rewired))


def _support(n, truth):
    return tuple(i for i, column in enumerate(_columns(n))
                 if (truth ^ (truth >> (1 << i))) & (_full(n) ^ column))


@lru_cache(maxsize=32768)
def _split(n, truth, axis):
    width = 1 << axis
    mask = (1 << width) - 1
    low = high = 0
    for k in range(1 << (n - axis - 1)):
        old = 2 * k * width
        low |= ((truth >> old) & mask) << (k * width)
        high |= ((truth >> (old + width)) & mask) << (k * width)
    return low, high


def _residuals(n, truth, triple):
    cofactors = (truth,)
    for axis in sorted(triple, reverse=True):
        cofactors = tuple(new for old in cofactors for new in _split(n, old, axis))
        n -= 1
    return cofactors


def _partition(values):
    classes = {}
    return tuple(classes.setdefault(v, len(classes)) for v in values)


def _histogram(outputs):
    a, b = outputs
    return (a.bit_count(), b.bit_count(), (a & b).bit_count())


def _influences(n, outputs):
    return tuple(tuple(((truth ^ (truth >> (1 << i))) & (_full(n) ^ col)).bit_count()
                       for i, col in enumerate(_columns(n))) for truth in outputs)


def characterize(n, outputs):
    """All eligible boundaries, evaluated without a source expression or planted group."""
    supports = [_support(n, out) for out in outputs]
    common = sorted(set(supports[0]).intersection(supports[1]))
    ranks = {}
    for triple in combinations(common, 3):
        a, b = (_residuals(n, out, triple) for out in outputs)
        ranks[triple] = len(set(zip(a, b)))
    if not ranks:
        raise ValueError("No eligible three-variable boundary")
    best = min(ranks.values())
    width = (best - 1).bit_length()
    first = tuple(common[:3])
    return {"supports": supports, "common_essential": common, "eligible_count": len(ranks),
            "minimum_classes": best, "minimum_bits": width,
            "minimizers": [triple for triple, count in ranks.items() if count == best],
            "minimum_width_triples": [triple for triple, count in ranks.items() if (count - 1).bit_length() == width],
            "class_count_histogram": dict(sorted(Counter(ranks.values()).items())),
            "support_first_triple": first, "support_first_classes": ranks[first],
            "support_first_bits": (ranks[first] - 1).bit_length()}


def _random_consumer(n, rng):
    """Read-once over its one ternary input and every outside input."""
    forest = [H, *range(3, n)]
    while len(forest) > 1:
        left = forest.pop(rng.randrange(len(forest)))
        right = forest.pop(rng.randrange(len(forest)))
        forest.append((rng.choice(("AND", "OR", "XOR")), left, right))
    return forest[0]


@lru_cache(maxsize=None)
def _context_perms(k):
    n = k + 1  # distinguished ternary value is argument 0
    return tuple(tuple((x & 1) | sum(((x >> new) & 1) << old for old, new in enumerate(order, 1))
                       for x in range(1 << n)) for order in permutations(range(1, n)))


def _consumer_key(n, consumers):
    k = n - 3
    external = {i: i - 2 for i in range(3, n)}
    values = [_evaluate(_substitute(expr, 0, external), k + 1) for expr in consumers]
    def signature(mapping):
        return tuple(sorted(sum(((table >> old) & 1) << new for new, old in enumerate(mapping)) for table in values))
    return min(signature(mapping) for mapping in _context_perms(k))


def _select(n, index, operation, seen_keys):
    rng = random.Random(FORM_SEED + 997 * n + 13 * index + (0 if operation == "fold" else 130001))
    if n == 5 and index == 0 and operation == "fold":
        fixed = (_both(H, 3), _either(H, 4))
        stratum = "anchor"
    elif n == 5 and ((index == 1 and operation == "fold") or operation == "mux"):
        fixed = (_xor(H, _both(3, 4)), _xor(H, _either(3, 4)))
        stratum = "matched_histogram"
    else:
        fixed = None
        stratum = "matched_histogram" if index == 0 else ("asymmetric" if index in (3, 5, 7) else "masked")
    rejected = Counter()
    for attempt in range(1, 4097):
        consumers = fixed if fixed else (_random_consumer(n, rng), _random_consumer(n, rng))
        sources = _sources(n, consumers, operation, range(n), (0, 1))
        pairs = [tuple(_evaluate(source, n) for source in pair) for pair in sources]
        a, b = pairs[0]
        if a == b or a == (_full(n) ^ b):
            rejected["identical_or_complementary_consumers"] += 1
            continue
        if stratum == "matched_histogram" and _histogram(pairs[0]) != _histogram(pairs[1]):
            rejected["joint_output_histogram_changed"] += 1
            continue
        if stratum == "asymmetric" and a.bit_count() == b.bit_count():
            rejected["consumer_output_counts_equal"] += 1
            continue
        first = characterize(n, pairs[0])
        if first["minimum_classes"] != 2 or first["minimizers"] != [(0, 1, 2)]:
            rejected["shared_boundary_not_unique"] += 1
            continue
        second = characterize(n, pairs[1])
        if second["minimum_classes"] != 4:
            rejected[f"rewired_minimum_{second['minimum_classes']}_classes"] += 1
            continue
        if stratum != "anchor" and any(len(row["class_count_histogram"]) < 2 for row in (first, second)):
            rejected["no_suboptimal_decoy"] += 1
            continue
        key = _consumer_key(n, consumers)
        if key not in seen_keys:
            seen_keys.add(key)
            return consumers, stratum, attempt, key, dict(rejected)
        rejected["duplicate_consumer_mechanism"] += 1
    raise AssertionError(f"Cannot populate structural fixture slot {operation}/{n}/{index}")


@lru_cache(maxsize=2)
def _build(split):
    if split not in ("primary", "sensitivity"):
        raise ValueError("Expected primary or sensitivity")
    extra = 0 if split == "primary" else 130001
    operation = "fold" if split == "primary" else "mux"
    plan = {5: 8, 7: 8, 9: 8} if split == "primary" else {5: 1, 7: 1}
    ids = random.Random(ID_SEED + extra)
    rows = []
    for n, count in plan.items():
        seen_keys = set()
        for index in range(count):
            consumers, stratum, attempt, mechanism, rejected = _select(n, index, operation, seen_keys)
            names = tuple(random.Random(RENAME_SEED + 71 * n + index + extra).sample(range(n), n))
            swap = (index + (n - 5) // 2) % 2
            order = (swap, 1 - swap)
            pair_id = f"{ids.getrandbits(80):020x}"
            row_ids = [f"{ids.getrandbits(96):024x}" for _ in range(2)]
            sources = _sources(n, consumers, operation, names, order)
            for side, source_pair in enumerate(sources):
                outputs = [_evaluate(expr, n) for expr in source_pair]
                triple = tuple(sorted(names[:3]))
                residuals = [_residuals(n, out, triple) for out in outputs]
                details = characterize(n, outputs)
                meta = {"n": n, "pair": pair_id, "partner": row_ids[1 - side], "kind": ("shared", "rewired")[side],
                        "stratum": stratum, "split": split, "core_operation": operation,
                        "source": source_pair, "logical_consumers": consumers, "source_order": names,
                        "port_order": order, "changed_output": order.index(1), "planted_triple": triple,
                        "planted_single_partitions": [_partition(word) for word in residuals],
                        "planted_joint_partition": _partition(zip(*residuals)),
                        "consumer_permutation_key": mechanism, "construction_draw": attempt,
                        "construction_rejections": rejected, "triple": triple, "width": details["minimum_bits"],
                        "min_classes": details["minimum_classes"], "common_support": details["common_essential"], **details}
                rows.append(({"id": row_ids[side], "n": n, "outputs": outputs}, meta))
    random.Random(ORDER_SEED + extra).shuffle(rows)
    return tuple(rows)


def tasks():
    return [{"id": r["id"], "n": r["n"], "outputs": list(r["outputs"])} for r, _ in _build("primary")]


def sensitivity_tasks():
    return [{"id": r["id"], "n": r["n"], "outputs": list(r["outputs"])} for r, _ in _build("sensitivity")]


def grading(split="primary"):
    return {r["id"]: dict(meta) for r, meta in _build(split)}


def sensitivity_grading():
    return grading("sensitivity")


def _scalar(expr, raw):
    if isinstance(expr, int):
        return (raw >> expr) & 1
    op, *args = expr
    a = _scalar(args[0], raw)
    if op == "NOT":
        return 1 - a
    b = _scalar(args[1], raw)
    return {"AND": a & b, "OR": a | b, "XOR": a ^ b}[op]


@lru_cache(maxsize=None)
def _assignments(inputs):
    return tuple(sum(((x >> j) & 1) << i for j, i in enumerate(inputs)) for x in range(1 << len(inputs)))


def _independent_ranks(n, outputs):
    """Build the full four-symbol row for each boundary assignment by literal input positions."""
    labels = tuple(((outputs[0] >> x) & 1) + 2 * ((outputs[1] >> x) & 1) for x in range(1 << n))
    common = [i for i in range(n) if all(any((labels[x] ^ labels[x ^ (1 << i)]) & (1 << port)
                                               for x in range(1 << n)) for port in (0, 1))]
    counts = {}
    for group in combinations(common, 3):
        outside = _assignments(tuple(i for i in range(n) if i not in group))
        signatures = {tuple(labels[inner | ext] for ext in outside) for inner in _assignments(group)}
        counts[group] = len(signatures)
    return counts


def audit():
    summary = {}
    all_outputs, all_ids = set(), set()
    for split in ("primary", "sensitivity"):
        rows = _build(split)
        by_id = {r["id"]: (r, m) for r, m in rows}
        by_width = {}
        for n in sorted({r["n"] for r, _ in rows}):
            same_n = [(r, m) for r, m in rows if r["n"] == n]
            pairs = [(r, m) for r, m in same_n if m["kind"] == "shared"]
            hist = 0
            influence = 0
            for r, m in same_n:
                if set(r) != {"id", "n", "outputs"} or r["id"] in all_ids or (n, *r["outputs"]) in all_outputs:
                    raise AssertionError("Repeated identity/table pair or leaked grading fields")
                all_ids.add(r["id"])
                all_outputs.add((n, *r["outputs"]))
                other, om = by_id[m["partner"]]
                changed = m["changed_output"]
                if (other["outputs"][1 - changed] != r["outputs"][1 - changed] or other["outputs"][changed] == r["outputs"][changed]
                        or om["partner"] != r["id"] or om["supports"] != m["supports"] or om["pair"] != m["pair"]):
                    raise AssertionError("Unmatched public control")
                if len(set().union(*m["supports"])) != n or (m["stratum"] != "anchor" and len(m["common_essential"]) != n):
                    raise AssertionError("Inactive inputs or incorrectly exposed boundary")
                should = 2 if m["kind"] == "shared" else 4
                if (m["minimum_classes"] != should or len(set(m["planted_joint_partition"])) != should
                        or any(len(set(p)) != 2 for p in m["planted_single_partitions"])):
                    raise AssertionError("Unexpected minimum or individual/joint partition")
                for j, expr in enumerate(m["source"]):
                    if any(_scalar(expr, x) != ((r["outputs"][j] >> x) & 1) for x in range(1 << n)):
                        raise AssertionError("Scalar truth mismatch")
                direct = _independent_ranks(n, r["outputs"])
                if (dict(Counter(direct.values())) != m["class_count_histogram"] or min(direct.values()) != should
                        or [g for g, v in direct.items() if v == should] != m["minimizers"]):
                    raise AssertionError("Independent scalar residual classification disagrees")
                if m["kind"] == "shared":
                    hist += _histogram(r["outputs"]) == _histogram(other["outputs"])
                    influence += _influences(n, r["outputs"]) == _influences(n, other["outputs"])
            rejections = Counter()
            for _, m in pairs:
                rejections.update(m["construction_rejections"])
            by_width[n] = {"pairs": len(pairs), "totally_common_support_pairs": sum(len(m["common_essential"]) == n for _, m in pairs),
                           "consumer_mechanisms": len({m["consumer_permutation_key"] for _, m in pairs}),
                           "output_histogram_matched_pairs": hist, "coordinate_influence_matched_pairs": influence,
                           "eligible_triples_per_case": sorted({m["eligible_count"] for _, m in same_n}),
                           "minimizer_counts_shared": sorted(len(m["minimizers"]) for _, m in pairs),
                           "minimizer_counts_rewired": sorted(len(m["minimizers"]) for _, m in same_n if m["kind"] == "rewired"),
                           "support_first_attains_width": sum(m["support_first_bits"] == m["minimum_bits"] for _, m in same_n),
                           "sum_minimum_bits": sum(m["minimum_bits"] for _, m in same_n),
                           "sum_support_first_bits": sum(m["support_first_bits"] for _, m in same_n),
                           "rejected_design_draws": dict(rejections),
                           "total_cases": len(same_n)}
        data = json.dumps([r for r, _ in rows], sort_keys=True, separators=(",", ":")).encode()
        summary[split] = {"by_width": by_width, "public_sha256": hashlib.sha256(data).hexdigest()}
    return summary


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
