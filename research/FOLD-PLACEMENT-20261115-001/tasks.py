"""Four-fold nine-input trees. Public records contain only id, arity, table and an unordered hint."""

import hashlib
import json
import random
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations
from pathlib import Path


N = 9
ALL = (1 << 512) - 1
COLUMNS = tuple(sum(1 << x for x in range(512) if x & (1 << i)) for i in range(N))
ROOT = Path(__file__).resolve().parents[2]
DEPTH = "FOLD-DEPTH-20261115-001"
DISCOVERY = "FOLD-DISCOVERY-20261115-001"
STRUCTURE_SEED, LABEL_SEED, ID_SEED, ORDER_SEED = 520171, 520199, 520207, 520213


def _digest(*values):
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=None)
def _unlabeled(count):
    """The AND arguments of F are interchangeable; its XOR argument is separate."""
    if count == 0:
        return ((),)
    shapes = set()
    for a in range(count):
        for b in range(count - a):
            for first in _unlabeled(a):
                for second in _unlabeled(b):
                    left, right = sorted((first, second))
                    for last in _unlabeled(count - a - b - 1):
                        shapes.add((left, right, last))
    return tuple(sorted(shapes))


def _label(shape, names):
    if not shape:
        return next(names)
    return ("F", *(_label(kid, names) for kid in shape))


def _rename(tree, names):
    if isinstance(tree, int):
        return names[tree]
    return tree[0], *(_rename(kid, names) for kid in tree[1:])


def _sites(tree, path=()):
    if isinstance(tree, int):
        return
    yield path, tree
    for i, child in enumerate(tree[1:]):
        yield from _sites(child, path + (i,))


def _at(tree, path):
    for i in path:
        tree = tree[i + 1]
    return tree


def _change(tree, path, rotation):
    if not path:
        return (rotation, *tree[1:])
    kids = list(tree[1:])
    kids[path[0]] = _change(kids[path[0]], path[1:], rotation)
    return (tree[0], *kids)


def _primitive(tree):
    if isinstance(tree, int):
        return tree
    a, b, c = (_primitive(kid) for kid in tree[1:])
    if tree[0] == "F":
        return "XOR", ("AND", a, b), c
    if tree[0] == "R-a":
        return "AND", a, ("XOR", b, c)
    if tree[0] == "R-b":
        return "AND", b, ("XOR", a, c)
    raise ValueError("Unknown local operation")


def _normal(expr):
    if isinstance(expr, int):
        return ("leaf",)
    gate, *children = expr
    flat = []
    for child in children:
        sub = _normal(child)
        flat.extend(sub[1:] if sub[0] == gate else (sub,))
    return (gate, *sorted(flat))


def _table(expr):
    if isinstance(expr, int):
        return COLUMNS[expr]
    gate, left, right = expr
    a, b = _table(left), _table(right)
    return a & b if gate == "AND" else a ^ b


@lru_cache(maxsize=1)
def _possibilities():
    originals, rotated = defaultdict(set), defaultdict(set)
    families = defaultdict(list)
    for unlabeled in _unlabeled(4):
        tree = _label(unlabeled, iter(range(N)))
        sites = list(_sites(tree))
        depth = 1 + max(len(path) for path, _ in sites)
        shape = _normal(_primitive(tree))
        originals[shape].add(depth)
        families[shape, depth].append(tree)
        for path, _ in sites:
            for name in ("R-a", "R-b"):
                changed = _change(tree, path, name)
                rotated[_normal(_primitive(changed))].add(depth)
    if set(originals).intersection(rotated):
        raise AssertionError("An edited structure still has a full four-F implementation")
    return dict(originals), dict(rotated), dict(families)


def _freeze_shape(raw):
    return tuple(_freeze_shape(v) for v in raw) if isinstance(raw, list) else raw


def _shape_table(shape, columns):
    gate, *children = shape
    if gate == "leaf":
        return next(columns)
    value = _shape_table(children[0], columns)
    for child in children[1:]:
        v = _shape_table(child, columns)
        value = value & v if gate == "AND" else value ^ v
    return value


def _degree_signature(truth):
    """Input-renaming invariant of a table, sufficient on this finite inventory.

    Mobius inversion gives its multilinear GF(2) monomials. Count degrees in
    the whole function and at each variable, then sort the nine variable rows.
    """
    coefficient = [(truth >> x) & 1 for x in range(512)]
    for i in range(N):
        bit = 1 << i
        for x in range(512):
            if x & bit:
                coefficient[x] ^= coefficient[x ^ bit]
    monomials = [x for x, v in enumerate(coefficient) if v]
    degree = tuple(sum(x.bit_count() == k for x in monomials) for k in range(N + 1))
    variables = [tuple(sum(x.bit_count() == k and bool(x & (1 << i)) for x in monomials)
                       for k in range(1, N + 1)) for i in range(N)]
    return degree, tuple(sorted(variables))


@lru_cache(maxsize=1)
def _archives():
    specs = ((DEPTH, "-E001_supplied_fold", "public.json"),
             (DISCOVERY, "-E001_learned_library", "held.json"))
    tables, structures = set(), defaultdict(set)
    for ticket, family, public_name in specs:
        directory = ROOT / "artifacts" / ticket / (ticket + family)
        public = json.loads((directory / public_name).read_bytes())
        grade = json.loads((directory / "grading.json").read_bytes())
        if ticket == DEPTH:
            grade = {**grade["primary"], **grade["fixed9"]}
        for row in public:
            if row["n"] == N:
                tables.add(row["truth"])
                structures[_freeze_shape(grade[row["id"]]["primitive_shape"])].add(ticket)
    return tables, dict(structures)


def _options(pos_shape, depth, edit_at_hint):
    originals, one_edit, families = _possibilities()
    out = []
    for tree in families[pos_shape, depth]:
        sites = list(_sites(tree))
        hint_sites = [path for path, sub in sites if all(isinstance(x, int) for x in sub[1:])]
        for hint in hint_sites:
            for path, _ in sites:
                if (path == hint) != edit_at_hint:
                    continue
                for which in ("R-a", "R-b"):
                    changed = _change(tree, path, which)
                    primitive = _primitive(changed)
                    neg_shape = _normal(primitive)
                    if neg_shape in originals:
                        continue
                    ones = _table(primitive).bit_count()
                    minimum = min(one_edit[neg_shape])
                    out.append((tree, changed, hint, path, which, neg_shape, ones, minimum))
    return out


@lru_cache(maxsize=1)
def _selection():
    originals, one_edit, _ = _possibilities()
    prior_tables, prior_shapes = _archives()
    used = set(prior_tables)
    negative_uses = Counter()
    rng_ids = random.Random(ID_SEED)
    rows = []
    for depth in (2, 3, 4):
        keys = sorted((k for k, ds in originals.items() if min(ds) == depth),
                      key=lambda k: _digest(STRUCTURE_SEED, depth, k))
        for index in range(8):
            pos_shape = keys[index % len(keys)]
            edit_at_hint = index < 4
            options = _options(pos_shape, depth, edit_at_hint)

            def rank(item):
                tree, _, hint, path, which, neg_shape, ones, minimum = item
                # Largest priorities are equal density and retaining the minimum
                # depth in the one-rotation class. Other ties favor novel controls.
                return (abs(ones - 256), int(minimum != depth), int(neg_shape in prior_shapes),
                        negative_uses[neg_shape], _digest(STRUCTURE_SEED, depth, index, tree, hint, path, which))

            positive, negative, hint_path, edit_path, rotation, neg_shape, _, _ = min(options, key=rank)
            negative_uses[neg_shape] += 1
            rng_names = random.Random(LABEL_SEED + 109 * depth + index)
            for _ in range(2048):
                names = rng_names.sample(range(N), N)
                sources = [_rename(tree, names) for tree in (positive, negative)]
                primitives = [_primitive(tree) for tree in sources]
                tables = [_table(expr) for expr in primitives]
                if len(set(tables)) == 2 and used.isdisjoint(tables):
                    break
            else:
                raise AssertionError("Could not find fresh labeled targets for a preselected pair")
            used.update(tables)
            ids = [f"{rng_ids.getrandbits(96):024x}" for _ in sources]
            pair = f"{rng_ids.getrandbits(80):020x}"
            hint = tuple(sorted(_at(sources[0], hint_path)[1:]))
            for k, (tree, expr, truth) in enumerate(zip(sources, primitives, tables)):
                norm = pos_shape if k == 0 else neg_shape
                row = {"id": ids[k], "n": N, "truth": truth, "hint": hint}
                meta = {"depth": depth, "kind": "positive" if k == 0 else "negative", "pair": pair,
                        "partner": ids[1 - k], "edit_at_hint": edit_at_hint, "hint_site": hint_path,
                        "edit_site": edit_path, "paired_rotation": rotation, "source": tree,
                        "primitive_source": expr, "normalized_structure": norm,
                        "four_F_depths": sorted(originals.get(norm, ())),
                        "one_rotation_depths": sorted(one_edit.get(norm, ())),
                        "max_gate_disjoint_F": 4 if k == 0 else 3, "output_ones": truth.bit_count(),
                        "prior_exact_match": truth in prior_tables, "prior_structure_tickets": sorted(prior_shapes.get(norm, ()))}
                rows.append((row, meta))
    random.Random(ORDER_SEED).shuffle(rows)
    return tuple(rows)


def tasks():
    """Return shuffled public rows. Bit x of truth is the target on raw assignment x."""
    return tuple(dict(row) for row, _ in _selection())


def grading():
    """Private pairing, source, edit, equivalence and archive information for the evaluator."""
    return {r["id"]: dict(meta) for r, meta in _selection()}


def _scalar(tree, assignment):
    if isinstance(tree, int):
        return (assignment >> tree) & 1
    a, b, c = [_scalar(kid, assignment) for kid in tree[1:]]
    if tree[0] == "F":
        return (a & b) ^ c
    return a & (b ^ c) if tree[0] == "R-a" else b & (a ^ c)


def _check_hint(row, meta):
    hint = row["hint"]
    subtree = _at(meta["source"], meta["hint_site"])
    if len(set(hint)) != 3 or tuple(sorted(subtree[1:])) != hint:
        raise AssertionError("The public hint does not select exactly the same three-leaf subtree")
    outside = 511 ^ sum(1 << i for i in hint)
    output_by_summary = {}
    for x in range(512):
        actual = (row["truth"] >> x) & 1
        if _scalar(meta["source"], x) != actual:
            raise AssertionError("Scalar source and packed table disagree")
        summary = (x & outside, _scalar(subtree, x))
        if output_by_summary.setdefault(summary, actual) != actual:
            raise AssertionError("All external bits and the hinted local result do not suffice")
    if len(output_by_summary) != 128:
        raise AssertionError("Hinted output does not vary independently of the six remaining raw inputs")


def audit():
    rows = _selection()
    originals, rotated, _ = _possibilities()
    if len(rows) != 48 or len({r["id"] for r, _ in rows}) != 48 or len({r["truth"] for r, _ in rows}) != 48:
        raise AssertionError("Exact task identities or functions repeated")
    if len(_unlabeled(4)) != 19 or len(originals) != 13 or [sum(min(s) == d for s in originals.values()) for d in (2, 3, 4)] != [1, 8, 4]:
        raise AssertionError("Four-fold structural universe changed")
    # Since this truth invariant is distinct for each normalized shape, two
    # different shapes in the entire finite inventory cannot be equivalent by
    # any input renaming. Identical normalized shapes are equivalent by the
    # associative/commutative gate identities and a common numbering of leaves.
    signatures = {shape: _degree_signature(_shape_table(shape, iter(COLUMNS))) for shape in originals.keys() | rotated.keys()}
    if len(set(signatures.values())) != len(signatures):
        raise AssertionError("Truth invariant failed to certify normalized classes")
    prior_signatures = {_degree_signature(t) for t in _archives()[0]}
    by_id = {r["id"]: (r, m) for r, m in rows}
    for r, m in rows:
        twin, other = by_id[m["partner"]]
        if (twin["hint"] != r["hint"] or m["pair"] != other["pair"] or m["edit_at_hint"] != (m["edit_site"] == m["hint_site"])
                or other["partner"] != r["id"] or set(r) != {"id", "n", "truth", "hint"} or m["prior_exact_match"]):
            raise AssertionError("Pair, public interface, or archive match failure")
        if any(((r["truth"] ^ (r["truth"] >> (1 << i))) & (ALL ^ col)) == 0 for i, col in enumerate(COLUMNS)):
            raise AssertionError("Inessential input")
        signature = _degree_signature(r["truth"])
        if signature != signatures[m["normalized_structure"]] or (signature in prior_signatures) != bool(m["prior_structure_tickets"]):
            raise AssertionError("Physical truth / archive overlap differs from the structural certificate")
        _check_hint(r, m)
        if m["kind"] == "positive" and (_change(m["source"], m["edit_site"], m["paired_rotation"]) != other["source"]
                                         or min(m["four_F_depths"]) != m["depth"]):
            raise AssertionError("A pair changed more than the selected local grouping or used excess depth")
        if m["kind"] == "negative" and m["four_F_depths"]:
            raise AssertionError("Edited target has an alternate full four-fold cover")
    summary = {}
    for depth in (2, 3, 4):
        pos = [m for _, m in rows if m["depth"] == depth and m["kind"] == "positive"]
        neg = [m for _, m in rows if m["depth"] == depth and m["kind"] == "negative"]
        if len(pos) != 8 or len(neg) != 8 or sum(m["edit_at_hint"] for m in neg) != 4:
            raise AssertionError("Incorrect matched-pair allocation")
        summary[depth] = {"pairs": len(pos), "edit_at_hint": sum(m["edit_at_hint"] for m in neg),
                          "positive_mechanisms": len({m["normalized_structure"] for m in pos}),
                          "negative_mechanisms": len({m["normalized_structure"] for m in neg}),
                          "prior_positive_mechanisms": len({m["normalized_structure"] for m in pos if m["prior_structure_tickets"]}),
                          "prior_negative_mechanisms": len({m["normalized_structure"] for m in neg if m["prior_structure_tickets"]}),
                          "prior_positive_labels_by_mechanism": sum(bool(m["prior_structure_tickets"]) for m in pos),
                          "prior_negative_labels_by_mechanism": sum(bool(m["prior_structure_tickets"]) for m in neg),
                          "negative_ones": sorted(m["output_ones"] for m in neg),
                          "negative_min_depth_matches": sum(min(m["one_rotation_depths"]) == depth for m in neg)}
    return {"source_trees": len(_unlabeled(4)), "all_four_F_mechanisms": len(originals), "all_one_rotation_mechanisms": len(rotated),
            "distinct_truth_invariant_certificates": len(set(signatures.values())),
            "prior_distinct_nine_input_truths": len(_archives()[0]), "prior_exact_overlaps": 0,
            "by_depth": summary, "public_sha256": _digest(tasks())}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
