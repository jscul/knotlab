"""Check the tree and positive-age pendant proofs on small, specified histories."""

from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
from math import inf
from pathlib import Path
import sys

from structural_features import cherry_start, degree_two_free_start, pair_certificate, pendant_join_start, tree_certificate


ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = spec_from_file_location(name, ROOT / path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CHECK = load("weight_struct_verify", "experiments/GROWN-END-SWAP-20261119-001/"
             "GROWN-END-SWAP-20261119-001-E001_reached/verify.py")
LAW = load("weight_struct_law", "experiments/FIRST-KNOT-20261118-001B/"
           "FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py")


def make_stars(n, links, loose):
    stars = [[] for _ in range(n)]
    name = 0
    for u, v, h in links:
        for _ in range(h):
            stars[u].append(name)
            stars[v].append(name)
            name += 1
    for v, count in enumerate(loose):
        stars[v].extend(range(name, name + count))
        name += count
    return stars


def stages(raw):
    stage = CHECK.Arrangement.parse(raw)
    assert CHECK.start_audit(stage)["census_open_legal"]
    yield stage
    production = LAW.from_junctions(raw)
    for _ in range(2):
        result = production.step(LAW.gf2(LAW.F.fewest), None)
        assert result and result["new"]
        following = CHECK.Arrangement.parse([list(row) for row in production.bits_of])
        CHECK.round_replay(stage, following)
        yield following
        stage = following


def literal_table(stage):
    entries, _, _ = CHECK.exact_table(stage, 1 << 19)

    def pair(x, y):
        distance = entries[tuple(sorted((x, y)))]
        return inf if distance is None else distance + 1

    singles = {x: min(pair(x, y) for y in stage.labels if x != y) for x in stage.labels}
    return singles.__getitem__, pair


def check_path(weights):
    raw = make_stars(4, [(i, i + 1, h) for i, h in enumerate(weights)], [2, 0, 0, 2])
    before, current, _ = stages(raw)
    assert tree_certificate(before.stars)["pair_sufficient"] is True
    expected = weights == [3, 2, 3]
    result = tree_certificate(current.stars)
    assert result["pair_sufficient"] == expected
    single, pair = literal_table(current)
    general = pair_certificate(current.stars, single, pair, max_candidates=200)
    fixed = set().union(*(current.stars[v] for v in current.live))
    groups = {}
    for x in current.labels:
        if x not in fixed:
            profile = (single(x), *(pair(x, z) for z in sorted(fixed)))
            groups.setdefault(profile, []).append(x)
    cells = list(groups.values())
    movable = [x for cell in cells for x in cell]
    basis = CHECK.linear_basis(current.masks)
    isometries = unsafe = 0
    for parts in product(*(permutations(cell) for cell in cells)):
        phi = {x: y for cell, images in zip(cells, parts) for x, y in zip(cell, images)}
        if any(pair(x, y) != pair(phi[x], phi[y]) for x, y in combinations(movable, 2)):
            continue
        isometries += 1
        images = (sum(current.label_bits[phi.get(x, x)] for x in row) for row in current.stars)
        if any(CHECK.reduce_word(word, basis) for word in images):
            unsafe += 1
    assert (unsafe == 0) == expected and isometries > 0
    if expected:
        assert result["harmful_swap"] is None
    else:
        x, y = result["harmful_swap"]
        assert x not in set().union(*(current.stars[v] for v in current.live))
        assert single(x) == single(y)
        assert all(pair(x, k) == pair(y, k) for k in current.labels if k not in (x, y))
        assert general["harmful_pair_swap"] and general["pair_sufficient"] is False
    return result, {"all_marked_pair_maps": isometries, "equation_changing": unsafe}


def check_pendants(counts):
    n = 2 + sum(counts)
    leaves = [list(range(2, 2 + counts[0])), list(range(2 + counts[0], n))]
    links = [(0, 1, 1)] + [(h, a, 1) for h in (0, 1) for a in leaves[h]]
    raw = make_stars(n, links, [0, 0] + [2] * (n - 2))
    assert cherry_start(raw) and degree_two_free_start(raw) and not cherry_start(raw + [[]])
    before, current, following = stages(raw)
    assert not tree_certificate(current.stars)["ordinary_tree"]
    single, pair = literal_table(current)
    cert = pair_certificate(current.stars, single, pair, max_candidates=200)
    assert cert["pair_sufficient"] and not cert["one_sufficient"]
    for h in (0, 1):
        a, b = leaves[h][:2]
        ha, = before.stars[h] & before.stars[a]
        hb, = before.stars[h] & before.stars[b]
        probe = None
        for name in before.stars[a] - {ha}:
            child, = set(current.owners[name]) - {a}
            if counts[h] == 3 or len(current.stars[child] & set(before.labels)) == 1:
                probe = name
                break
        assert probe is not None and single(ha) == single(hb)
        assert pair(ha, probe) == 3 < pair(hb, probe)
        basis = CHECK.linear_basis(following.masks)
        marked = following.label_bits[hb] | following.label_bits[probe]
        extras = [0] + [following.label_bits[z] for z in following.labels if z not in (hb, probe)]
        assert all(CHECK.reduce_word(marked | bit, basis) for bit in extras)
        assert before.stars[a] in following.stars
    return tuple((len(stage.stars), len(stage.labels)) for stage in (before, current, following))


def check_broader_tree(links, degree_two_free=True):
    n = 1 + max(max(edge) for edge in links)
    degree = [0] * n
    for u, v in links:
        degree[u] += 1
        degree[v] += 1
    raw = make_stars(n, [(u, v, 1) for u, v in links], [max(0, 3 - d) for d in degree])
    assert degree_two_free_start(raw) == degree_two_free
    assert pendant_join_start(raw) and not cherry_start(raw)
    before, current, following = stages(raw)
    single, pair = literal_table(current)
    result = pair_certificate(current.stars, single, pair)
    assert result["pair_sufficient"] and not result["one_sufficient"]
    return tuple((len(stage.stars), len(stage.labels)) for stage in (before, current, following))


if __name__ == "__main__":
    for weights in ([2, 2, 2], [3, 2, 3]):
        print("bundle weights", weights, check_path(weights))
    for counts in ((2, 2), (2, 3), (3, 3)):
        print("pendant counts", counts, check_pendants(counts))
    print("three-leaf star", check_broader_tree([(0, 1), (0, 2), (0, 3)]))
    print("single and double pendants", check_broader_tree(
        [(0, 1), (1, 2), (0, 3), (0, 4), (1, 5), (2, 6), (2, 7)]))
    print("degree-two unary parent", check_broader_tree(
        [(0, 1), (0, 2), (0, 3), (3, 4), (1, 5), (1, 6), (2, 7), (2, 8)], False))
