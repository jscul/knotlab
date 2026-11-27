"""Direct truth-table audit of the alternative split named in the earlier record."""

from argparse import ArgumentParser
from collections import Counter
from itertools import product
import json
from pathlib import Path
from random import Random
import time

import networkx as nx
import numpy as np


HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "UPPER-GROWN-20261127-001" / "out"
PARENT_FILE = "cubic_12_3.jsonl"
PARENT_LINE = 1
GENERATION_SEED = 1015
NEW_CARRIERS = ((0, 1, 10), (3, 4, 17), (2, 6, 18),
                (8, 11, 14), (5, 7, 9), (12, 13, 15))
TRIPLES = list(product((0, 1), (2, 3), (4, 5)))


def raw_system():
    rows = [json.loads(line) for path in sorted(RAW.glob("cubic_12_*.jsonl"))
            for line in path.read_text().splitlines()]
    row = json.loads((RAW / PARENT_FILE).read_text().splitlines()[PARENT_LINE - 1])
    position = sorted((r for r in rows if r["boxes"]), key=lambda r: r["links"]).index(row)
    archive = next(r for f in (HERE.parent / "out").glob("cut_*.jsonl")
                   for line in f.read_text().splitlines() if (r := json.loads(line))["graph"] == position)
    graph = nx.random_regular_graph(3, 12, seed=GENERATION_SEED)
    numbered_links = list(graph.edges())
    assert sorted(map(list, numbered_links)) == row["links"]
    supports = tuple(tuple(i for i, ends in enumerate(numbered_links) if k in ends)
                     for k in range(12))
    assert all(len(k) == 3 for k in supports)
    old = tuple(tuple(c) for pair in row["example"][0]["box"] for c, sign in pair if sign == 1)
    assert len(old) == 6
    seeded = archive["cut distinction"]
    assert seeded == Random(20261129 + position).choice(range(18))
    assert archive["knots at its ends"] == sorted(numbered_links[seeded])
    return supports, old, position, seeded


def split_source(supports, cuts):
    opened = [list(k) for k in supports]
    for new_x, split_at in enumerate(cuts, len({x for k in supports for x in k})):
        ends = [i for i, k in enumerate(supports) if split_at in k]
        assert len(ends) == 2
        k = opened[ends[-1]]
        k[k.index(split_at)] = new_x
    return tuple(map(tuple, opened))


def read_word(states, carrier):
    # A fixed bit from the same carrier is copied to each other place.
    base, *rest = carrier
    return np.logical_and.reduce([((states >> base) ^ (states >> x)) & 1 == 0 for x in rest])


def failures(states, supports):
    broken = np.zeros(len(states), dtype=np.uint16)
    for i, carrier in enumerate(supports):
        broken |= read_word(states, carrier).astype(np.uint16) << i
    return broken


def joint(values):
    word = values[0].astype(np.uint8)
    for next_value in values[1:]:
        word = (word << 1) + next_value
    return word


def counts(codes, width):
    return np.bincount(codes, minlength=1 << width).tolist()


def evaluate(supports, carriers, limit=None):
    places = list(x for c in carriers for x in c)
    assert len(set(places)) == len(places)
    n = 1 + max(x for k in supports for x in k)
    full = 1 << n
    states = np.arange(full if limit is None else min(full, limit), dtype=np.uint32)
    broken = failures(states, supports)
    accepted = broken == 0
    allowed = states[accepted]
    readings = [read_word(states, c) for c in carriers]
    triples = [joint([readings[i][accepted] for i in t]) for t in TRIPLES]
    lower = [counts(w, 3) for w in triples]
    upper = joint([a != b for a, b in zip(readings[::2], readings[1::2])])
    upper_counts = counts(upper[accepted], 3)
    restored = [int(np.count_nonzero((broken == (1 << i)) & (upper == 7)))
                for i in range(len(supports))]
    mixed = []
    for c in supports:
        bits = joint([(allowed >> x) & 1 for x in c])
        mixed.append([sum(np.any(bits[read[accepted]] == w) and np.any(bits[~read[accepted]] == w)
                          for w in range(8)) for read in readings])
    flips = []
    if len(states) == full:
        for c, value in zip(carriers, readings):
            flips.append([int(np.count_nonzero(accepted[allowed ^ (1 << x)]
                                              & (value[allowed ^ (1 << x)] != value[allowed]))) // 2
                          for x in c])
        assert sum(upper_counts) == len(allowed)
    multiplicities = Counter(x for c in supports for x in c)
    return {
        "supports": supports, "carriers": carriers, "assignments_checked": len(states),
        "allowed_assignments": len(allowed),
        "loose_distinctions": sorted(x for x, count in multiplicities.items() if count == 1),
        "lower_counts_000_through_111": lower,
        "upper_disagreement_counts_000_through_111": upper_counts,
        "upper_111_restored_assignments_by_deleted_law": restored,
        "source_knot_fixings_leaving_each_reading_free": [[int(v) for v in row] for row in mixed],
        "undirected_allowed_single_flips_changing_each_carrier_place": flips,
        "lower_clauses_missing_only_111": sum(all(c > 0 for c in row[:7]) and row[7] == 0
                                             for row in lower),
        "unread_at_every_knot": all(min(row) > 0 for row in mixed),
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    supports, old, position, seeded = raw_system()
    opened = split_source(supports, (0,))
    old_on_new_end = tuple(tuple(18 if x == 0 else x for x in c) for c in old)
    checks = dict(closed_archived=evaluate(supports, old, args.prefix),
                  opened_new_box=evaluate(opened, NEW_CARRIERS, args.prefix),
                  old_on_retained_end=evaluate(opened, old, args.prefix),
                  old_on_new_end=evaluate(opened, old_on_new_end, args.prefix))
    out = {"closed_row": [PARENT_FILE, PARENT_LINE], "generator_seed_for_labels": GENERATION_SEED,
           "cut_study_sorted_position": position, "seeded_split_at": seeded, "alternative_split_at": 0,
           "split_law_index_receiving_fresh_distinction": 1,
           "lower_triples_as_reading_indices": TRIPLES,
           "checked": checks, "seconds": round(time.perf_counter() - start, 6)}
    if args.prefix is None:
        assert seeded != 0 and opened[1] == (18, 3, 4)
        for tag in ("closed_archived", "opened_new_box"):
            check = checks[tag]
            assert check["lower_clauses_missing_only_111"] == 8 and check["unread_at_every_knot"]
            assert all(check["upper_disagreement_counts_000_through_111"][:7])
            assert check["upper_disagreement_counts_000_through_111"][7] == 0
            assert all(check["upper_111_restored_assignments_by_deleted_law"])
            assert min(map(min, check["undirected_allowed_single_flips_changing_each_carrier_place"])) > 0
        assert all(checks[tag]["upper_disagreement_counts_000_through_111"][7] > 0
                   for tag in ("old_on_new_end", "old_on_retained_end"))
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(out["cut_study_sorted_position"], out["seeded_split_at"], out["seconds"],
          {k: [v["allowed_assignments"], v["lower_clauses_missing_only_111"],
               v["upper_disagreement_counts_000_through_111"][-1]] for k, v in checks.items()})


if __name__ == "__main__":
    main()
