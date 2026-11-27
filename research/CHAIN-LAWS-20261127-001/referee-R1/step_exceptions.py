"""Compare two explicit extra-law explanations with each local gate exception."""

import argparse
import json
import resource
import time
from collections import Counter
from itertools import combinations

from step_readings import DEFINING, HERE, StageCheck, chain_carriers, open_rows


def law_patterns(knots, chain):
    local = [knots[k] for k in chain]
    first = local[0] - local[1]
    third = local[2] - local[1] - local[3]
    second = local[1] - local[0] - local[2]
    additions = [s for i, s in enumerate(knots) if i not in chain]
    direct = (first | third) in additions
    # The helper is the sole third distinction at the attachment of the first
    # two free places. It must also be the sole third at the other attachment.
    pair_first = {next(iter(s - first)) for s in additions if first < s and len(s) == 3}
    other = second | third
    pair_other = {next(iter(s - other)) for s in additions if other < s and len(s) == 3}
    return direct, bool(pair_first & pair_other)


def minimum_extra(check, chain, omit, wants):
    base = set(chain) - {omit}
    outside = sorted(set(range(len(check.supports))) - set(chain))
    for size in range(len(outside) + 1):
        for extra in combinations(outside, size):
            kept = base.union(extra)
            active = [s if i in kept else -s for i, s in enumerate(check.law_selectors)]
            if not check.deletion.allows(active + wants):
                return list(extra)
    raise ValueError("full stage allowed the stated exclusion")


def obstruction(stage, chain, lower, restore):
    check = StageCheck(stage)
    try:
        raw = chain_carriers(stage, chain)
        bits = [check.deletion.agree(tuple(check.var[x] for x in group)) for group in raw]
        causes = []
        for j, mask in enumerate(lower):
            if mask == 127:
                continue
            # In both observed masks a pair has lost 11. State its two
            # true readings directly and find one smallest extra set.
            assert mask in (63, 95)
            group = DEFINING[j]
            pair = [group[0], group[1 if mask == 63 else 2]]
            extra = minimum_extra(check, chain, None, [bits[p] for p in pair])
            causes.append({"defining_triple": j, "pair_impossible_at_11": pair,
                           "pair_raw_carriers": [raw[p] for p in pair], "outside_laws": extra})
        if not causes:
            for position, mask in enumerate(restore):
                for both in range(3):
                    if mask & (1 << both):
                        continue
                    wants = bits[2 * both:2 * both + 2] + [check.deletion.either(bits[2*j], bits[2*j+1])
                                                            for j in range(3) if j != both]
                    extra = minimum_extra(check, chain, chain[position], wants)
                    causes.append({"chain_position_removed": position, "pair_reading_both": both, "outside_laws": extra})
        return causes
    finally:
        check.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    timer = time.perf_counter()
    stages = {row["id"]: row for row in open_rows(HERE / "step_stages.jsonl.gz")
              if not args.pilot or row["id"] < 8}
    labels = {row["stage"]: (row["start"], row["round"]) for row in open_rows(HERE / "step_incidence.jsonl.gz")
              if row["arm"] == "one_fewer" and row["stage"] in stages}
    lawsets = {sid: list(map(frozenset, row["supports"])) for sid, row in stages.items()}
    counts = Counter()
    minimal_sizes = Counter()
    examples = {}
    for row in open_rows(HERE / "step_reading_rows.jsonl.gz"):
        sid = row["stage"]
        if sid not in stages:
            continue
        rank = row["chain_index"]
        chain = stages[sid]["chains"][rank]
        direct, paired = law_patterns(lawsets[sid], chain)
        lower_fails = row["lower"] != [127] * 4
        removal_only = row["frozen"] and not row["every_law"]
        name = f"lower_fails={int(lower_fails)};removal_only={int(removal_only)};direct_law={int(direct)};paired_laws={int(paired)}"
        counts[name] += 1
        if lower_fails or removal_only:
            causes = obstruction(stages[sid]["supports"], chain, row["lower"], row["restore"])
            for cause in causes:
                minimal_sizes[f"{'lower' if lower_fails else 'removal_only'}_size_{len(cause['outside_laws'])}"] += 1
            examples.setdefault(name, []).append({"start": labels[sid][0], "round": labels[sid][1], "stage": sid,
                                                   "chain_index": rank, "lower_masks": row["lower"],
                                                   "restored_roles_after_removing_each_law": row["restore"],
                                                   "smallest_outside_sets_with_the_chain": causes})
    output = {"direct_law": "An extra law on the free places of knot 0 and the free place of knot 2.",
              "paired_laws": "A common third distinction in extra laws on the free places of knot 0 and on the free places of knots 1 and 2.",
              "counts": counts, "minimum_extra_law_counts": minimal_sizes,
              "exceptions": examples, "wall_seconds": time.perf_counter() - timer,
              "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    suffix = "_pilot" if args.pilot else ""
    (HERE / f"step_exceptions{suffix}.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["counts"]), output["wall_seconds"], output["peak_kib"])


if __name__ == "__main__":
    main()
