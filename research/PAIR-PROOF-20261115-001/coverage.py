"""Replay shared pair witnesses and construct offline optimal group-coverage advice.

Run .venv/bin/python -B research/PAIR-PROOF-20261115-001/coverage.py. An advice
entry [i,j,base] asks the executing solver to read four actual edited output
labels. The base is a full frontier input with i and j cleared. Only the
separate coverage artifact contains grades and post-edit coverage diagnostics.
"""

import hashlib
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SAVED = ROOT / "artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/explicit-piece"
DEST = ROOT / "artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses"
INPUTS = {
    "public.json": "7dddbcf0d2e86c18376c2f46f25150b26e50d6c6c6f5039837937077e281e150",
    "grades.json": "095518e925494ae2723858e9a70241c19cc6cea454696914d8a135bf55422bac",
}


def _read(name):
    data = (SAVED / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != INPUTS[name]:
        raise ValueError(f"Frozen fixture changed: {name}")
    return json.loads(data)


@lru_cache(maxsize=None)
def _columns(n):
    return tuple(sum(1 << x for x in range(1 << n) if x & (1 << a)) for a in range(n))


def _raw(p, edit=None):
    n = p["n"]
    full = (1 << (1 << n)) - 1
    wires = [*_columns(n), 0, full]
    for i, (a, b) in enumerate(p["gates"], n + 2):
        if edit and i == edit["gate"]:
            a, b = (edit["to"], b) if edit["pin"] == 0 else (a, edit["to"])
        wires.append(full ^ (wires[a] & wires[b]))
    return wires


def _truth(p, grade, edit=None):
    wires = _raw(p, edit)
    m = len(p["frontier"])
    labels = [-1] * (1 << m)
    fibers = Counter()
    for raw in range(1 << p["n"]):
        x = sum(((wires[w] >> raw) & 1) << i for i, w in enumerate(p["frontier"]))
        label = sum(((wires[w] >> raw) & 1) << k for k, w in enumerate(p["outputs"]))
        if labels[x] not in (-1, label):
            raise AssertionError("An output varies at fixed frontier input")
        labels[x] = label
        fibers[x] += 1
    if len(fibers) != 1 << m or set(fibers.values()) != {4}:
        raise AssertionError("Wrong frontier fibers")
    packed = [sum(((v >> k) & 1) << i for i, v in enumerate(labels)) for k in (0, 1)]
    if packed != grade["outputs"]:
        raise AssertionError("Saved tables and independent physical replay disagree")
    return labels


def _eligible_and_ranks(labels, m):
    axes = [i for i in range(m) if all(any((labels[x] ^ labels[x ^ (1 << i)]) & (1 << out)
                                           for x in range(1 << m)) for out in (0, 1))]
    triples = tuple(combinations(range(m), 3))
    eligible = [k for k, t in enumerate(triples) if set(t) <= set(axes)]
    ranks = []
    for k in eligible:
        mask = sum(1 << i for i in triples[k])
        outer = [x for x in range(1 << m) if not x & mask]
        inner = [x for x in range(1 << m) if not x & ~mask]
        ranks.append(len({bytes(labels[x | y] for y in outer) for x in inner}))
    return eligible, ranks


def _corners(labels, i, j, x):
    a, b = 1 << i, 1 << j
    return (labels[x], labels[x | a], labels[x | b], labels[x | a | b])


def _first_three(corners):
    return next(t for t in combinations(range(4), 3) if len({corners[q] for q in t}) == 3)


def _tests(labels, m):
    answers = {}
    for i, j in combinations(range(m), 2):
        mask = (1 << i) | (1 << j)
        bases = [x for x in range(1 << m) if not x & mask and len(set(_corners(labels, i, j, x))) >= 3]
        if bases:
            answers[i, j] = bases
    return answers


def _mask_set(vector):
    return sum(1 << x for x in vector)


def _union(items):
    value = 0
    for item in items:
        value |= item
    return value


def _coverage_ids(mask):
    return [i for i in range(mask.bit_length()) if mask & (1 << i)]


def _shape(m, missing):
    """Actual unavailable pattern and canonical ordered physical roles."""
    if not missing:
        return "empty", ()
    if len(missing) == 1:
        return "edge", next(iter(missing))
    triangles = [t for t in combinations(range(m), 3) if set(combinations(t, 2)) <= missing]
    if len(triangles) == 1:
        triangle = triangles[0]
        rest = missing - set(combinations(triangle, 2))
        if not rest:
            return "triangle", triangle
        if len(rest) == 1 and not set(next(iter(rest))) & set(triangle):
            return "triangle_and_edge", (*triangle, *next(iter(rest)))
    raise ValueError(f"Uncovered pattern outside this panel's exact optimizer: {missing}")


def _small_graphs(n, np):
    """Exhaustively partition all labeled graphs into relabeling orbits on <=7 vertices."""
    edges = list(combinations(range(n), 2))
    index = {p: i for i, p in enumerate(edges)}
    relabel = np.asarray([[1 << index[tuple(sorted((p[a], p[b])))] for a, b in edges]
                          for p in permutations(range(n))], dtype=np.int32).T.copy()
    seen = np.zeros(1 << len(edges), dtype=bool)
    for mask in range(len(seen)):
        if seen[mask]:
            continue
        inds = [i for i in range(len(edges)) if mask & (1 << i)]
        orbit = np.bitwise_or.reduce(relabel[inds], axis=0) if inds else np.array([0])
        seen[orbit] = True
        yield tuple(edges[i] for i in inds)
    if not seen.all():
        raise AssertionError("A labeled prefix graph was omitted")


def _shape_embeddings(h, edges):
    """Embed the required unavailable pairs in the prefix *untested*-pair graph."""
    fits = {"empty": ()}
    if edges:
        fits["edge"] = edges[0]
    eset = set(edges)
    for t in combinations(range(h), 3):
        if set(combinations(t, 2)) <= eset:
            fits.setdefault("triangle", t)
            disjoint = next((e for e in edges if not any(v in t for v in e)), None)
            if disjoint is not None:
                fits["triangle_and_edge"] = (*t, *disjoint)
                break
    return fits


@lru_cache(maxsize=3)
def _frontiers(m):
    """Exact extremal tables over every admissible subset of test pairs, for every cardinality.

    Work in the graph of untested pairs: uncovered triples are precisely its
    triangles. All forced untested edges fit in h=m-2 vertices on these fixtures.
    Enumerate the h-vertex graph H up to relabeling. Attach the last two vertices
    using all neighborhoods S,T and their mutual edge z. Their triangle increment
    is edges_H(S)+edges_H(T)+z*|S intersection T|. They are free of forced edges.
    """
    import numpy as np

    h = m - 2
    size = 1 << h
    total_pairs = m * (m - 1) // 2
    masks = np.arange(size, dtype=np.int32)
    card = np.asarray([i.bit_count() for i in range(size)], dtype=np.int32)
    extra_edges = card[:, None] + card[None, :]
    intersection = card[masks[:, None] & masks[None, :]]
    code = masks[:, None] * size + masks[None, :]
    stride = 2 * size * size
    infinity = 1 << 30
    indicators = {e: ((masks & (1 << e[0]) != 0) & (masks & (1 << e[1]) != 0)).astype(np.int32)
                  for e in combinations(range(h), 2)}
    best = {name: [None] * (total_pairs + 1) for name in ("empty", "edge", "triangle", "triangle_and_edge")}
    num_graphs = 0
    for edges in _small_graphs(h, np):
        num_graphs += 1
        fits = _shape_embeddings(h, edges)
        e = set(edges)
        triangles = sum(all(p in e for p in combinations(t, 2)) for t in combinations(range(h), 3))
        within = sum((indicators[edge] for edge in edges), start=np.zeros(size, dtype=np.int32))
        edge_counts = len(edges) + extra_edges
        triangle_counts = triangles + within[:, None] + within[None, :]
        best_here = np.full(total_pairs + 1, infinity, dtype=np.int32)
        for z in (0, 1):
            values = (triangle_counts + z * intersection) * stride + z * size * size + code
            np.minimum.at(best_here, edge_counts + z, values)
        for count in np.nonzero(best_here < infinity)[0]:
            ntri, choice = divmod(int(best_here[count]), stride)
            k = total_pairs - int(count)
            for shape, roles in fits.items():
                saved = best[shape][k]
                if saved is None or ntri < saved[0]:
                    z, st = divmod(choice, size * size)
                    s, t = divmod(st, size)
                    best[shape][k] = (ntri, edges, s, t, z, roles)
    return best, {"prefix_vertices": h, "prefix_labeled_graphs": 1 << (h * (h - 1) // 2),
                  "prefix_orbits": num_graphs, "extensions_per_orbit": 2 * size * size}


def _menu_for(record, m, physical_roles, by_pair):
    _, edges, s, t, z, local_roles = record
    h = m - 2
    mapping = dict(zip(local_roles, physical_roles))
    mapping.update(zip((v for v in range(m) if v not in local_roles),
                       (v for v in range(m) if v not in physical_roles)))
    untested = set(edges)
    untested.update((i, h) for i in range(h) if s & (1 << i))
    untested.update((i, h + 1) for i in range(h) if t & (1 << i))
    if z:
        untested.add((h, h + 1))
    select = sorted(tuple(sorted((mapping[a], mapping[b]))) for a, b in combinations(range(m), 2)
                    if (a, b) not in untested)
    if any(pair not in by_pair for pair in select):
        raise AssertionError("Constructive optimum includes an unusable pair")
    remaining = list(select)
    covered, prefix, tests = 0, [0], []
    while remaining:
        pair = max(remaining, key=lambda p: (by_pair[p]["mask"] & ~covered).bit_count())
        remaining.remove(pair)
        covered |= by_pair[pair]["mask"]
        prefix.append(covered.bit_count())
        tests.append(by_pair[pair]["test"])
    return tests, prefix


def _edit(m, original, original_tests, current, grade):
    triples = tuple(combinations(range(m), 3))
    eligible, ranks = _eligible_and_ranks(current, m)
    if eligible != list(range(len(triples))) or ranks != grade["candidate_classes"]:
        raise AssertionError("Saved grades and independent triple enumeration disagree")
    fresh = _tests(current, m)
    by_pair = {}
    for pair in combinations(range(m), 2):
        if pair in fresh:
            covers = [k for k in eligible if set(pair) <= set(triples[k])]
            corner_masks = []
            for x in fresh[pair]:
                colors = _corners(current, *pair, x)
                corner_masks.append([sum(1 << c for c in group) for group in combinations(range(4), 3)
                                     if len({colors[c] for c in group}) == 3])
            by_pair[pair] = {"mask": _mask_set(covers), "covers": covers, "bases": fresh[pair], "corner_masks": corner_masks,
                             "witness_count": len(fresh[pair]), "test": [*pair, fresh[pair][0]]}
    coverable = _union(v["mask"] for v in by_pair.values())
    reused = {"same_three": [], "any_three_of_four": []}
    for pair, tests in original_tests.items():
        base = tests[0]
        corners = _corners(current, *pair, base)
        old_corners = _first_three(_corners(original, *pair, base))
        if len(set(corners)) >= 3:
            reused["any_three_of_four"].append(pair)
        if len({corners[q] for q in old_corners}) == 3:
            reused["same_three"].append(pair)
    for name, pairs in reused.items():
        ids = _coverage_ids(_union(by_pair[p]["mask"] for p in pairs))
        reused[name] = {"pairs": pairs, "covered": ids}
    missing = set(combinations(range(m), 2)) - set(fresh)
    shape, physical = _shape(m, missing)
    optima = _frontiers(m)[0][shape]
    frontier = []
    for k, optimum in enumerate(optima):
        if optimum is None:
            break
        tests, prefix = _menu_for(optimum, m, physical, by_pair)
        coverage = len(triples) - optimum[0]
        if len(tests) != k or prefix[-1] != coverage:
            raise AssertionError("Exhaustive bound and actual menu coverage disagree")
        frontier.append({"k": k, "covered": coverage, "tests": tests})
        if coverage == coverable.bit_count():
            break
    if not frontier or frontier[-1]["covered"] != coverable.bit_count():
        raise AssertionError("Did not find a full cover")
    k = frontier[-1]["k"]
    # Independent full-cover lower bounds: no triangle permits at most floor(m²/4)
    # untested pairs (Mantel). For one forced triangle, each outside vertex has
    # at most one neighbor on it and the outside graph is triangle-free.
    forced = len(triples) - coverable.bit_count()
    maximum_untested = (m * m // 4 if forced == 0 else 3 + (m - 3) + (m - 3) ** 2 // 4)
    lower = m * (m - 1) // 2 - maximum_untested
    if forced not in (0, 1) or k != lower:
        raise AssertionError("Independent full-cover lower bound did not match")
    unr = [q for q in eligible if not coverable & (1 << q)]
    if any(ranks[q] < 3 for q in _coverage_ids(coverable)):
        raise AssertionError("Pair witness excluded a true one-bit group")
    return {
        "m": m, "kind": grade["kind"], "width": (min(ranks) - 1).bit_length(), "eligible": eligible,
        "available": [{k: v for k, v in row.items() if k != "mask"} for row in by_pair.values()],
        "unusable_pairs": sorted(missing), "unusable_shape": shape, "coverable": _coverage_ids(coverable),
        "uncovered": [{"index": q, "triple": triples[q], "exact_classes": ranks[q]} for q in unr],
        "min_full": k, "independent_full_lower_bound": lower, "prefix_coverage": prefix,
        "frontier": frontier, "original_rechecked": reused,
    }


def generate():
    parents, grades = _read("public.json"), _read("grades.json")
    details, advice, originals = {}, {}, {}
    sums = {kind: Counter() for kind in ("surviving", "broken")}
    for p in parents:
        pid = p["id"]
        g = grades[pid]
        m = len(p["frontier"])
        original = _truth(p, g["base"])
        original_tests = _tests(original, m)
        originals[pid] = [{"test": [i, j, bases[0]], "corners": _first_three(_corners(original, i, j, bases[0]))}
                          for (i, j), bases in original_tests.items()]
        details[pid], advice[pid] = {}, {}
        for edit in p["edits"]:
            eid = edit["id"]
            eg = g["edits"][eid]
            current = _truth(p, eg, edit)
            stats = _edit(m, original, original_tests, current, eg)
            details[pid][eid] = stats
            advice[pid][eid] = stats["frontier"][-1]["tests"]
            row = sums[stats["kind"]]
            row.update({"edits": 1, "eligible": len(stats["eligible"]), "fresh": len(stats["coverable"]),
                        "same_three": len(stats["original_rechecked"]["same_three"]["covered"]),
                        "any_three_of_four": len(stats["original_rechecked"]["any_three_of_four"]["covered"]),
                        "minimum_full_tests": stats["min_full"]})
    coverage = {
        "schema": 1, "inputs_sha256": INPUTS, "totals": sums, "original_witnesses": originals,
        "frontier_optimality": "Exhaustive maximum number of excluded triples for each pair-test budget. "
                               "A menu at one budget need not extend a menu at another. "
                               "Menus use the first successful full input setting for each pair. "
                               "Neither reads, overlap, gate work nor CPU are optimized.",
        "graph_enumeration": {m: _frontiers(m)[1] for m in sorted({len(p["frontier"]) for p in parents})},
        "tasks": details,
    }
    return coverage, {"schema": 1, "parents": advice}


if __name__ == "__main__":
    result, menus = generate()
    DEST.mkdir(parents=True, exist_ok=True)
    for name, data in (("coverage.json", result), ("oracle_advice.json", menus)):
        packed = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
        path = DEST / name
        if path.exists():
            if path.read_bytes() != packed:
                raise FileExistsError(f"Existing artifact differs: {path}")
        else:
            with path.open("xb") as f:
                f.write(packed)
        print(name, len(packed), hashlib.sha256(packed).hexdigest(), flush=True)
    print(json.dumps(result["totals"], sort_keys=True))
