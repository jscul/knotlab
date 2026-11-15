"""Two stages, one identified middle pair and one identified pair of edge pads."""
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import random
import sys

# An index is a vector of eight pairs of strict-clause activations. Each
# active triple has three distinct raw guards; the endpoint groups are on.
N = 1 << 16
ALL = (1 << N) - 1
HALVES = [ALL // ((1 << (1 << j)) + 1) << (1 << j) for j in range(16)]
WEIGHTS = [int.from_bytes(bytes(
    sum(1 << bit for bit in range(8) if (start + bit).bit_count() == weight)
    for start in range(0, N, 8)), "little") for weight in range(17)]


def routes(joins):
    middles = [3, 4, 5, 6]
    if joins:
        a, b = joins
        middles[b] = middles[a]
    arcs = defaultdict(list)
    for branch, middle in enumerate(middles):
        i = branch // 2
        arcs[i].append((middle, 2 * branch))
        arcs[middle].append((i + 1, 2 * branch + 1))
    def paths(node, visited):
        if node == 2:
            yield ()
        else:
            for dst, edge in arcs[node]:
                if dst not in visited:
                    for tail in paths(dst, visited | {dst}):
                        yield (edge,) + tail
    return list(paths(0, {0}))


def contradiction(paths, pair=()):
    def one_pad(value):
        edge_live = []
        for i in range(8):
            h0, h1 = HALVES[2*i:2*i+2]
            edge_live.append((h0, h1)[value] if i in pair else h0 & h1)
        any_route = 0
        for path in paths:
            live = ALL
            for i in path:
                live &= edge_live[i]
            any_route |= live
        return any_route
    return one_pad(0) & one_pad(1)


def minimal(truth):
    answer = truth
    for j, on in enumerate(HALVES):
        answer &= ~(on & (truth << (1 << j)))
    return answer


def actual_models(joins, pads, mask):
    """Try each assignment of the boundary, middle values and the shared pad.
    A private edge pad occurs nowhere else, so its two possible values can be
    tried on that edge alone. Endpoints are fixed to 1 and 0."""
    for middle_mask in range(16):
        middle = [(middle_mask >> b) & 1 for b in range(4)]
        if joins and middle[joins[0]] != middle[joins[1]]:
            continue
        for x1 in (0, 1):
            x = (1, x1, 0)
            values = []
            for b, m in enumerate(middle):
                values.extend((not x[b // 2] or m, not m or x[b // 2 + 1]))
            for z in (0, 1):
                def holds(i):
                    if values[i]:
                        return True
                    pad_values = (z,) if i in pads else (0, 1)
                    return any(not (mask & (1 << (2*i + val))) for val in pad_values)
                if all(holds(i) for i in range(8)):
                    return True
    return False


def main():
    original = routes(())
    classes = defaultdict(Counter)
    witnesses = {}
    model_checks = 0
    cross_checks = 0
    rng = random.Random(2393)
    for join in combinations(range(4), 2):
        paths = routes(join)
        j_only = contradiction(paths)
        for pads in combinations(range(8), 2):
            p_only = contradiction(original, pads)
            both = contradiction(paths, pads)
            joint_only = both & ~(j_only | p_only)
            assert (j_only | p_only) & ~both == 0
            for test in [0, N - 1] + [rng.randrange(N) for _ in range(20)]:
                for mode_j, mode_p, truth in [(join, pads, both), ((), pads, p_only), (join, (), j_only)]:
                    assert actual_models(mode_j, mode_p, test) != bool(truth >> test & 1)
                    cross_checks += 1
            essential = minimal(both) & joint_only
            label = "same stage" if join[0] // 2 == join[1] // 2 else "across stages"
            record = classes[label]
            record["wirings"] += 1
            record["wirings_with_joint_only_inputs"] += bool(joint_only)
            record["joint_only_inputs"] += joint_only.bit_count()
            for h, weight in enumerate(WEIGHTS):
                if not essential & weight:
                    continue
                count = (essential & weight).bit_count()
                raw_size = 24 + 3*h
                record["minimal_joint_only_supports_size_" + str(raw_size)] += count
                family = label, raw_size
                hit = essential & weight
                example = (hit & -hit).bit_length() - 1
                if family not in witnesses:
                    witnesses[family] = (join, pads, example)
                for mode_j, mode_p, truth in [(join, pads, both), ((), pads, p_only), (join, (), j_only)]:
                    assert actual_models(mode_j, mode_p, example) != bool(truth >> example & 1)
                    model_checks += 1
    special = (0, 2), (1, 5)
    mask = sum(3 << (2*i) for i in (0, 6, 7)) | (1 << 2) | (1 << 11)
    checked = contradiction(routes(special[0]), special[1])
    assert minimal(checked) >> mask & 1
    assert not actual_models(*special, mask)
    assert actual_models(special[0], (), mask) and actual_models((), special[1], mask)
    results = {"status":"passed", "wirings":6*28, "activation_vectors_per_wiring":N,
               "direct_model_checks_on_minima": model_checks, "other_direct_model_checks": cross_checks,
               "distinguished_raw_core":24+3*mask.bit_count(),
               "classes":dict(classes), "small_witnesses":[{"kind":a,"raw_size":s,"middle_join":j,
               "pad_join":p,"active_half_mask":m} for (a,s),(j,p,m) in sorted(witnesses.items())]}
    if sys.argv[1:] == ["--verify"]:
        saved = json.loads(Path(__file__).with_name("two_stage_census.json").read_text())
        assert json.loads(json.dumps(results)) == saved
    print(json.dumps(results, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
