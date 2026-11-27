"""Complete source-stage search under the strengthened single-knot readings, with no holder cap."""

import argparse
from collections import Counter
from itertools import combinations
import json
from time import perf_counter

from census_replay import HERE, Truth, VALID, inputs, labels, read_rows


def strict_bonds(supports):
    truth = Truth(supports)
    places = tuple(map(set, supports))
    carriers = []
    for width in (2, 3):
        for c in combinations(truth.names, width):
            strict = all(len(p.intersection(c)) <= 1 for p in places)
            semantic = truth.profile(c)
            if not semantic[0] and (strict or semantic[1] == 0):
                carriers.append((c, sum(1 << x for x in c), strict, semantic[1] == 0,
                                 truth.agreement(c) & truth.allowed))
    counts = Counter()
    witnesses = {}
    for i, (a, ma, attr_a, sem_a, ya) in enumerate(carriers):
        for j in range(i+1, len(carriers)):
            b, mb, attr_b, sem_b, yb = carriers[j]
            if ma & mb:
                continue
            physical = attr_a and attr_b
            semantic = sem_a and sem_b
            if not physical and not semantic:
                continue
            p0, p1 = truth.allowed & ~ya & ~yb, yb & ~ya
            p2, p3 = ya & ~yb, ya & yb
            free_pair = bool(p0 and p1 and p2 and p3)
            for k in range(j+1, len(carriers)):
                c, mc, attr_c, sem_c, yc = carriers[k]
                if (ma | mb) & mc:
                    continue
                physical3 = physical and attr_c
                semantic3 = semantic and sem_c
                if not physical3 and not semantic3:
                    continue
                counts["three disjoint readings under the one-place rule"] += physical3
                counts["three disjoint readings individually open after every knot fixing"] += semantic3
                if not free_pair:
                    continue
                if p0 & yc and p1 & yc and p2 & yc and p3 & yc and p0 & ~yc and p1 & ~yc and p2 & ~yc and p3 & ~yc:
                    continue
                missing = sum((1 << (2*h)) * (not p & ~yc) + (2 << (2*h)) * (not p & yc)
                              for h, p in enumerate((p0,p1,p2,p3)))
                if not VALID[missing]:
                    continue
                C = (a,b,c)
                full_fiber = all(all(not (cell & truth.allowed) or (cell & F) for cell in truth.cells(C))
                                 for fix in truth.fixings for F in fix) if semantic3 else False
                for tag, ok in (("one-place bond", physical3), ("individually open bond", semantic3),
                                ("same joint image under every knot fixing", full_fiber)):
                    counts[tag] += ok
                    if ok and tag not in witnesses:
                        witnesses[tag] = {"supports": supports, "carriers": C, "missing": labels(missing)}
    return counts, witnesses


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ranks", type=int, nargs="+")
    p.add_argument("--out", required=True)
    opts = p.parse_args()
    start = perf_counter()
    archive = inputs()
    sample = set(read_rows("census_nae_[0-9].jsonl"))
    counts, counts_starts, heldout, heldout_starts = Counter(), Counter(), Counter(), Counter()
    positive_starts, witnesses = [], {}
    ranks = opts.ranks or range(len(archive))
    for rank in ranks:
        counted, examples = strict_bonds(archive[rank])
        counts.update(counted)
        counts_starts.update(k for k, n in counted.items() if n)
        if rank in sample:
            heldout.update(counted)
            heldout_starts.update(k for k, n in counted.items() if n)
        if counted["one-place bond"] or counted["individually open bond"]:
            positive_starts.append([rank, counted["one-place bond"], counted["individually open bond"],
                                    counted["same joint image under every knot fixing"]])
        for tag, row in examples.items():
            witnesses.setdefault(tag, dict(archive_rank=rank, **row))
    result = {"source_stages": len(ranks), "heldout_stages": len(set(ranks) & sample),
              "counts": counts, "starts": counts_starts, "sample_counts": heldout, "sample_starts": heldout_starts,
              "positive_starts": positive_starts, "witnesses": witnesses,
              "elapsed_seconds": round(perf_counter() - start, 4)}
    (HERE / opts.out).write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("positive_starts", "witnesses")}, indent=1))


if __name__ == "__main__":
    main()
