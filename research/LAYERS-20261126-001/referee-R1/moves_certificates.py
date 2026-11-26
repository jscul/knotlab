"""Check the named joined-ring facts by enumerating supports with matching parities."""

import argparse
import itertools
import json
import os
import resource
import subprocess
import sys
import time
from collections import Counter, defaultdict
from functools import reduce
from operator import xor
from pathlib import Path

import moves as m


ROOT = m.HERE.parents[2]
GROWTH = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae"


def check_growth(supports, expected):
    # The independent growth output is the input to all moves computations.
    # This comparison alone invokes the existing ordinary growth implementation.
    sys.path.insert(0, str(GROWTH))
    import naelib
    built = naelib.S.from_junctions(supports)
    result = built.step(naelib.parity_rule(naelib.F.fewest), None)
    assert result["new"] and list(map(set, built.bits_of)) == list(map(set, expected))
    return result["new"]


def support_tables(columns, fixed, highest):
    """Collect indexed supports by the parity checks which each toggles."""
    available = [i for i in range(len(columns)) if i not in fixed]
    tables = []
    for size in range(highest + 1):
        out = defaultdict(list)
        for selected in itertools.combinations(available, size):
            syndrome = reduce(xor, (columns[i] for i in selected), 0)
            out[syndrome].append((selected[0] if selected else len(columns),
                                  selected[-1] if selected else -1, m.mask(selected)))
        tables.append(out)
    return tables


def supported_changes(tables, parity, k, fixed=0):
    """Use the first floor(k/2) places as one half so every support is counted once."""
    cut = k // 2
    words = []
    for remainder, left in tables[cut].items():
        right = tables[k - cut].get(remainder ^ parity, ())
        for _, end, first in left:
            words.extend(first | second | fixed for start, _, second in right if end < start)
    assert len(set(words)) == len(words)
    return words


def shortest_from_syndromes(supports, limit, connector=None):
    own = m.owners(supports)
    columns = [m.mask(own[i]) for i in range(len(own))]
    tables = support_tables(columns, (), (limit + 1) // 2)
    by_size = {k: supported_changes(tables, 0, k) for k in range(1, limit + 1)}
    if connector is not None:
        assert not any(w >> connector & 1 for changes in by_size.values() for w in changes)
        through_one = support_tables(columns, (connector,), 3)
        for k in range(limit + 1, 8):
            by_size[k] = supported_changes(through_one, columns[connector], k - 1, 1 << connector)
    minima = [min(k for k, words in by_size.items() if any(w >> i & 1 for w in words)) for i in range(len(columns))]
    minimum_through = {w for k, words in by_size.items() for w in words if any(minima[i] == k for i in m.bits(w))}
    via_cycles, ml = m.cycle_generators(supports)
    assert minima == ml and set(via_cycles["through"]) == minimum_through
    groups = {"through": minimum_through, **{b: {w for k, words in by_size.items() if k <= b for w in words}
                                             for b in (4, 5) if b <= limit}}
    for kind, words in groups.items():
        all_spans = m.echelon(words)
        graph_span = m.echelon(via_cycles[kind])
        assert len(all_spans) == len(graph_span)
        assert all(not m.add(graph_span.copy(), w) for w in words)
    return groups, dict(sorted(Counter(minima).items()))


def checker_projection(width, projection):
    names = [f"x{j}" for j in range(width)]
    forbidden = set(range(1 << width)) - set(projection)
    cnf = ";".join(" ".join(("~" if state & (1 << j) else "") + n for j, n in enumerate(names))
                   for state in sorted(forbidden))
    call = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
            "--loops", *names[:-1], "--contact", names[-1], "--json"]
    return json.loads(subprocess.check_output(call, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}))


def four_classes(supports, moves, labels):
    n = len(m.owners(supports))
    z = m.perp(map(m.mask, supports), n)
    h = list(m.echelon(moves).values())
    assert len(z) == len(h) + 2
    assert all(not m.dot(l, w) for l in labels for w in moves)
    assert len(m.echelon(m.values(labels, z))) == 2
    signatures = [m.mask(j for j, l in enumerate(labels) if m.dot(l, w)) for w in z]
    representatives = {0: 0}
    for w, sign in zip(z, signatures):
        for code, rep in list(representatives.items()):
            representatives.setdefault(code ^ sign, rep ^ w)
    assert set(representatives) == set(range(4))
    proj_checks = {}
    table = []
    for k, places in enumerate(supports):
        projected = m.all_words(m.echelon(m.restrict(w, places) for w in z).values())
        assert set(projected) == {x for x in range(1 << len(places)) if x.bit_count() % 2 == 0}
        class_zero = list(m.echelon(m.restrict(w, places) for w in h).values())
        images = {}
        for value, translate in representatives.items():
            images[value] = {w ^ m.restrict(translate, places) for w in m.all_words(class_zero)}
        assert all(p == set(projected) for p in images.values())
        if len(places) not in proj_checks:
            check = checker_projection(len(places), projected)
            assert check["is_knot"]
            proj_checks[len(places)] = {key: check[key] for key in
                                        ("is_knot", "binding", "invisible_in_parts", "coexistence")}
        table.append({"holder": k, "places": len(places), "projection_per_class": [len(images[v]) for v in range(4)]})
    # The study compares one holder at a time. To test the stronger reading
    # "no proper part", locate small sets of holders which can read a named bit.
    named = labels + [labels[0] ^ labels[1]]
    names = ["first", "second", "sum"]
    images = m.values(named, z)
    observed = [m.values([1 << i for i in places], z) for places in supports]
    shortest_reads = {}
    for size in (1, 2, 3):
        if len(shortest_reads) == len(names):
            break
        for picked in itertools.combinations(range(len(supports)), size):
            span = m.echelon(w for h in picked for w in observed[h])
            for name, value in zip(names, images):
                if name not in shortest_reads and not m.add(span.copy(), value):
                    shortest_reads[name] = picked
    return {"allowed_rank": len(z), "move_rank": len(h), "class_rank": 2,
            "class_population": 1 << len(h), "labels": [list(m.bits(l)) for l in labels],
            "representatives_in_label_order_00_10_01_11": [list(m.bits(representatives[v])) for v in range(4)],
            "single_holder_projections": table, "knot_check_grouped_by_projection_arity": proj_checks,
            "least_holder_sets_reading_named_bits_search_through_three": shortest_reads}


def five_rings():
    source, rings = m.joined_rings([5, 5], [(0, 5, "change", 0, 1)], "except_joins")
    connector = 10
    labels = [r ^ (1 << connector) for r in rings]
    stages = [source]
    births = []
    for _ in range(3):
        after, status = m.grow(stages[-1])
        assert status == "funded"
        births.append(check_growth(stages[-1], after))
        stages.append(after)
    g0, _ = shortest_from_syndromes(source, 5)
    g1, shortest = shortest_from_syndromes(stages[1], 5, connector)
    assert len(m.echelon(g0["through"])) == len(m.perp(map(m.mask, source), len(m.owners(source))))
    alleles = four_classes(stages[1], g1["through"], labels)
    cross = [w for w in g1["through"] if w & (1 << connector)]
    # A single frozen move exchanges the joining distinction and both raw ring
    # parities; the two combined labels persist. The connector participates.
    assert cross and all(m.dot(w, rings[0]) and m.dot(w, rings[1]) for w in cross)
    assert all(not m.dot(w, r) for w in g1["through"] - set(cross) for r in rings)
    for a, b in zip(rings, rings[::-1]):
        assert all(not m.dot(a, m.mask(s)) for s in stages[1])
        assert [m.dot(a, l) for l in (a ^ (1 << connector), b ^ (1 << connector))] == [1, 0]
    persistent = []
    for r, s in enumerate(stages[1:], start=1):
        each, _ = m.cycle_generators(s)
        assert all(not m.dot(w, l) for w in each["through"] for l in labels)
        assert all(not m.dot(a, m.mask(p)) for a in rings for p in s)
        persistent.append({"round": r, "knots": len(s), "minimum_per_distinction_keeps_both_combined_labels": True,
                           "old_ring_changes_still_exchange_them_independently": True})
    # Each birth in the first round has parents in one ring. Summing all parity
    # laws on that side identifies the connector with its loose parity.
    left = set(range(5))
    for j, s in enumerate(stages[1][len(source):], start=len(source)):
        old_places = [i for i in s if i in m.owners(source)]
        parents = {h for i in old_places for h in m.owners(source)[i]}
        if parents <= set(range(5)):
            left.add(j)
        else:
            assert not (parents & set(range(5)))
    eqs = list(map(m.mask, stages[1]))
    side_parities = [reduce(xor, (eqs[j] for j in side), 1 << connector)
                     for side in (left, set(range(len(eqs))) - left)]
    assert not (side_parities[0] & side_parities[1])
    assert all(m.dot(w, parity) == ((w >> connector) & 1)
               for w in m.perp(eqs, len(m.owners(stages[1]))) for parity in side_parities)
    return {"meaning": "two five-knot rings with one shared distinction at the two holders without any loose distinction",
            "source": source, "grown_once": stages[1], "births_replayed_by_existing_ordinary_growth": births,
            "independent_low_weight_recount": {"source_through_move_count": len(g0["through"]),
                  "grown_through_move_count": len(g1["through"]), "shortest_support_size_by_distinction_count": shortest,
                  "grown_changes_up_to_five": len(g1[5])},
            "grown_class_certificate": alleles, "joining_distinction": connector,
            "every_complete_move_through_join_flips_both_raw_ring_parities": len(cross),
            "example_cross_ring_move": list(m.bits(min(cross))),
            "side_loose_parities_equal_to_the_join": [list(m.bits(v)) for v in side_parities],
            "original_ring_exchanges": [list(m.bits(r)) for r in rings], "later_named_parity_checks": persistent}


def four_rings():
    source, rings = m.joined_rings([4, 4], [(0, 4, "change", 1, 2)], "rings")
    stages = [source]
    births = []
    for _ in range(3):
        nxt, status = m.grow(stages[-1])
        assert status == "funded"
        births.append(check_growth(stages[-1], nxt))
        stages.append(nxt)
    table = []
    for r, s in enumerate(stages):
        g, shortest = shortest_from_syndromes(s, 5)
        table.append({"round": r, "knots": len(s), "distinctions": len(m.owners(s)),
                      "all_changes_of_at_most_five": len(g[5]), "shortest_support_size_by_distinction_count": shortest,
                      "ranks": m.classify(s, m.perp(map(m.mask, s), len(m.owners(s))), g[5], rings)})
        if r >= 2:
            table[-1]["four_class_certificate"] = four_classes(s, g[5], rings)
    own = m.owners(source)
    mixed = []
    for h, s in enumerate(stages[1][len(source):], start=len(source)):
        parents = sorted(k for i in s if i in own for k in own[i])
        if any(k < 4 for k in parents) and any(4 <= k < 8 for k in parents):
            mixed.append({"new_holder": h, "parents": parents, "support": s})
    assert mixed
    return {"meaning": "two four-knot rings joined by one holder sharing two distinctions with each ring",
            "source": source, "after_one": stages[1], "after_two": stages[2],
            "births_replayed_by_existing_ordinary_growth": births, "mixed_ring_births_in_round_one": mixed,
            "at_most_five": table}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    start = time.perf_counter()
    result = {"joining_two_five_knot_rings": five_rings()}
    if not args.pilot:
        result["joining_two_four_knot_rings"] = four_rings()
    result["measured_seconds"] = round(time.perf_counter() - start, 4)
    result["peak_resident_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(result["measured_seconds"], result["peak_resident_KiB"])


if __name__ == "__main__":
    main()
