"""Look for the necessary carrier patterns even after forgetting every clause's signs."""
import argparse
import json
import resource
from collections import defaultdict
from functools import cache
from itertools import permutations
from time import perf_counter

import closed_forms as scan


def support_patterns(n, unread, signed):
    lower = {tuple(sorted(x >> 1 for x in clause)) for clause in signed}
    assert len(lower) == len(signed)
    by_pair = defaultdict(set)
    for a, b, c in lower:
        by_pair[a, b].add(c)
        by_pair[b, c].add(a)
        by_pair[a, c].add(b)
    available = (1 << n) - 1
    unread_set = set(unread)
    @cache
    def contained(room):
        return [s for s in scan.subset_masks(room, (2, 3)) if s in unread_set]
    @cache
    def completions(room):
        # Every triple of new mutually disjoint carriers in the remaining
        # distinctions. Count even the choices with no chance to be a clause.
        count = 0
        clause_count = 0
        partial = []
        for d in contained(room):
            for e in contained(room ^ d):
                if e <= d:
                    continue
                for f in contained(room ^ d ^ e):
                    if f <= e:
                        continue
                    count += 1
                    clause_count += (d, e, f) in lower
                    choices = by_pair.get((d, e)), by_pair.get((d, f)), by_pair.get((e, f))
                    if all(choices):
                        partial.append(choices)
        return count, clause_count, partial
    total_completions = 0
    disjoint = 0
    alternating = 0
    extendible = 0
    for anchor in lower:
        a, b, c = anchor
        count, other, partial = completions(available ^ (a | b | c))
        total_completions += count
        disjoint += other
        if count:
            extendible += 1
        # In an alternating form, each of the other three clauses contains
        # one different original reading and a different pair of new ones.
        # Try all six assignments of original readings to pairs of new ones.
        for p, q, r in partial:
            for x, y, z in permutations(anchor):
                if x in p and y in q and z in r:
                    alternating += 1
    assert disjoint % 2 == 0 and alternating % 4 == 0
    return dict(extendible_unsigned_single_clauses=extendible,
                choices_of_three_further_carriers_summed_over_anchor_clauses=total_completions,
                pairs_of_clauses_on_six_disjoint_carriers=disjoint // 2,
                alternating_four_clause_sets_with_all_signs_disregarded=alternating // 4)


def run(cases):
    start = perf_counter()
    stages = json.loads((scan.HERE / "growth_stages.json").read_text())
    prior = {r["census_id"]: r for r in json.loads((scan.HERE / "closed_counts.json").read_text())["rows"]}
    chosen = set(cases) if cases else set(prior)
    lib = scan.kernel()
    rows = []
    for s in stages:
        cid = s["census_id"]
        if s["law"] != "one_fewer" or cid not in chosen:
            continue
        names = sorted({x for knot in s["supports"] for x in knot})
        idx = {x: i for i, x in enumerate(names)}
        knots = [[idx[x] for x in k] for k in s["supports"]]
        _, unread, _, _, signed = scan.lower_bonds(lib, knots, len(names), None)
        row = support_patterns(len(names), unread, signed)
        assert row["extendible_unsigned_single_clauses"] == prior[cid]["extendible_single_clauses"]
        row["census_id"] = cid
        rows.append(row)
    assert {r["census_id"] for r in rows} == chosen
    # All 8 possible clauses on 6 paired, disjoint readings: four disjoint
    # pairs of clauses and two alternating four-clause choices. Swapping the
    # sign on one occurrence leaves the carrier-only answer the same.
    raw = [3 << (2*i) for i in range(6)]
    cs = {tuple(2*raw[t]+1 for t in (i,j,k)) for i in (0,1) for j in (2,3) for k in (4,5)}
    a, b, c = min(cs)
    cs.remove((a, b, c))
    cs.add((a^1, b, c))
    ctrl = support_patterns(12, raw, cs)
    assert ctrl["pairs_of_clauses_on_six_disjoint_carriers"] == 4
    assert ctrl["alternating_four_clause_sets_with_all_signs_disregarded"] == 2
    return dict(identical_replays_under_both_laws=len(rows), rows=rows, mixed_sign_control=ctrl,
                totals={key: sum(row[key] for row in rows) for key in ctrl},
                elapsed_seconds=round(perf_counter()-start, 4),
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=int, nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run(args.cases)
    scan.write_json(scan.HERE / args.output, result)
    print(result["totals"], "seconds", result["elapsed_seconds"], "peak KiB", result["peak_rss_kib"])
