"""Independent search for a qualifying four-clause step on finite census stages."""

import argparse
import json
import random
import resource
import sys
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
sys.path.insert(0, str(RESEARCH / "NAE-LAYER-20261127-001/referee-R1"))
from growth_rule import advance, supports_of


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def make_mask(xs):
    return sum(1 << x for x in xs)


@cache
def partitions(n, groups=3):
    # The first member belongs to the first group in exactly one way.
    if not groups:
        return ((),) if n == 0 else ()
    out = []
    for size in (2, 3):
        if 2 * (groups - 1) <= n - size <= 3 * (groups - 1):
            for rest in combinations(range(1, n), size - 1):
                first = (0, *rest)
                remaining = [i for i in range(1, n) if i not in rest]
                for subseq in partitions(n - size, groups - 1):
                    out.append((first,) + tuple(tuple(remaining[i] for i in g) for g in subseq))
    return tuple(out)


@cache
def local_certificates(owners):
    """Restricted carriers and signs whose required word needs exactly these source laws."""
    n = len(owners)
    h = max(k.bit_length() for k in owners)
    private = tuple(i for i, k in enumerate(owners) if k.bit_count() == 1)
    shared = tuple(i for i in range(n) if i not in private)
    laws = [tuple(i for i, k in enumerate(owners) if (k >> j) & 1) for j in range(h)]

    # Global complement preserves all the agreements. Fix the last raw bit to zero.
    total = 1 << (n - 1)
    universe = (1 << total) - 1
    columns = []
    for j in range(n - 1):
        run = 1 << j
        columns.append((universe // ((1 << run) + 1)) << run)
    columns.append(0)

    def equal(group):
        ones, zeros = universe, universe
        for i in group:
            ones &= columns[i]
            zeros &= ~columns[i]
        return ones | zeros

    violations = [equal(law) for law in laws]
    full = universe
    for v in violations:
        full &= ~v
    exactly = []
    for j, v in enumerate(violations):
        for i, w in enumerate(violations):
            if i != j:
                v &= ~w
        if not v:
            return ()
        exactly.append(v)
    readings = {}
    result = []
    for k in range(max(6, len(private), n - h + 3), min(9, n) + 1):
        for extras in combinations(shared, k - len(private)):
            selected = private + extras
            for partition in partitions(k):
                groups = tuple(tuple(sorted(selected[i] for i in g)) for g in partition)
                for group in groups:
                    if group not in readings:
                        yes = equal(group)
                        readings[group] = (universe ^ yes, yes)
                for signs in product(range(2), repeat=3):
                    # Positive identifications save |group|-1 raw bits. A negative
                    # reading adds just one law to the minimal unsatisfiable system.
                    if n - h > sum(len(g)-1 if s else 1 for g, s in zip(groups, signs)):
                        continue
                    a, b, c = (readings[g][s] for g, s in zip(groups, signs))
                    combined = a & b & c
                    if full & combined or not all(combined & e for e in exactly):
                        continue
                    if full & a & b and full & a & c and full & b & c:
                        result.append(tuple(zip(groups, signs)))
    return tuple(result)


def candidate_clauses(supports):
    """All eligible signed lower triples, plus possible extras removed later."""
    laws = [make_mask(k) for k in supports]
    h = len(laws)
    covered = [0] * (1 << h)
    twice = [0] * (1 << h)
    partial = set()
    subsets = 0
    for s in range(1, 1 << h):
        j = (s & -s).bit_length() - 1
        shorter = s & (s - 1)
        covered[s] = covered[shorter] | laws[j]
        twice[s] = twice[shorter] | (covered[shorter] & laws[j])
        n = covered[s].bit_count()
        if n < 6 or n > s.bit_count() + 6 or (covered[s] ^ twice[s]).bit_count() > 9:
            continue
        subsets += 1
        chosen = sorted(bits(s), key=lambda i: (len(supports[i]), (laws[i] & twice[s]).bit_count(), i))
        owners = defaultdict(int)
        for i, j in enumerate(chosen):
            for d in supports[j]:
                owners[d] |= 1 << i
        ordered = sorted(owners, key=lambda d: (owners[d], d))
        template = tuple(owners[d] for d in ordered)
        local_groups = {}
        for clauses in local_certificates(template):
            signed = []
            for group, v in clauses:
                if group not in local_groups:
                    local_groups[group] = make_mask(ordered[i] for i in group)
                mask = local_groups[group]
                signed.append((mask << 1) | v)
            partial.add(tuple(sorted(signed)))

    names = covered[-1]
    @cache
    def extensions(literal):
        m, positive = literal >> 1, literal & 1
        masks = [m]
        if positive and m.bit_count() == 2:
            masks.extend(m | 1 << i for i in bits(names & ~m))
        return [(mask << 1) | positive for mask in masks if not any(mask & law == mask for law in laws)]

    triples = set()
    for x, y, z in partial:
        for a in extensions(x):
            for b in extensions(y):
                if (a & b) >> 1:
                    continue
                occupied = (a | b) >> 1
                for c in extensions(z):
                    if not (c >> 1 & occupied):
                        triples.add(tuple(sorted((a, b, c))))
    return triples, {"source_subsets_inspected": subsets, "partial_certificates": len(partial)}


def compatible_neighbours(pairs, label_masks):
    """For each pair of signed readings at x, all pairs disjoint from its two carriers."""
    containing = defaultdict(int)
    union = []
    for j, (b, c) in enumerate(pairs):
        mask = label_masks[b] | label_masks[c]
        union.append(mask)
        for d in bits(mask):
            containing[d] |= 1 << j
    full = (1 << len(pairs)) - 1
    for mask in union:
        choices = full
        for d in bits(mask):
            choices &= ~containing[d]
            if not choices:
                break
        yield choices


def links_of(clauses):
    by_reading = defaultdict(list)
    for a, b, c in clauses:
        by_reading[a].append((b, c))
        by_reading[b].append((a, c))
        by_reading[c].append((a, b))
    return by_reading


def peel(clauses, label_masks):
    counts = [len(clauses)]
    while clauses:
        discard = set()
        for a, pairs in links_of(clauses).items():
            if len(pairs) == 1:
                discard.add(tuple(sorted((a, *pairs[0]))))
                continue
            for pair, choices in zip(pairs, compatible_neighbours(pairs, label_masks)):
                if not choices:
                    discard.add(tuple(sorted((a, *pair))))
        if not discard:
            break
        clauses.difference_update(discard)
        counts.append(len(clauses))
    return counts


def choices(clauses, label_masks):
    """Join two clauses sharing the smallest reading and both cross completions."""
    by_reading = links_of(clauses)
    completers = defaultdict(set)
    for a, b, c in clauses:
        completers[a, b].add(c)
        completers[a, c].add(b)
        completers[b, c].add(a)
    for a in sorted(by_reading):
        # a is the smallest of the six signed readings. Order the two clauses
        # containing it; both ways to pair the four other readings are tested.
        pairs = sorted(pair for pair in by_reading[a] if a < pair[0])
        for i, partners in enumerate(compatible_neighbours(pairs, label_masks)):
            b, c = pairs[i]
            for j in bits(partners & ~((1 << (i+1)) - 1)):
                f, g = pairs[j]
                occupied = label_masks[a] | label_masks[b] | label_masks[c] | label_masks[f] | label_masks[g]
                for d, e in ((f, g), (g, f)):
                    left, right = tuple(sorted((b, e))), tuple(sorted((c, d)))
                    for x in completers.get(left, set()) & completers.get(right, set()):
                        if a < x and not occupied & label_masks[x]:
                            yield ((a, x), (b, d), (c, e))


def roster():
    starts = json.loads((RESEARCH / "FORBID-EDITS-20261126-001/starts.json").read_text())
    stages = {}
    for path in sorted((HERE.parent / "out").glob("four_*.jsonl")):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            idx = int(record["start"].split()[-1])
            supports = supports_of(starts[idx])
            n_start = len(supports)
            for row in record["rounds"]:
                t = row["round"]
                if t:
                    growth = advance(supports)
                    assert growth.status == "funded"
                    supports = growth.supports
                n = len(set().union(*map(set, supports)))
                assert (n, len(supports)) == (row["distinctions"], row["knots"])
                assert (n > 19) == row.get("not read", False)
                stages[idx, t] = (supports, n_start)
            if record["rounds"][-1]["round"] < 2:
                assert advance(supports).status != "funded"
    return starts, stages


def solve(idx, t, supports, n_start, structural_only=False, all_patterns=False):
    tick = perf_counter()
    signed, stats = candidate_clauses(supports)
    labels = sorted({v for clause in signed for v in clause})
    number = {v: i for i, v in enumerate(labels)}
    clauses = {tuple(number[v] for v in clause) for clause in signed}
    del signed
    masks = [v >> 1 for v in labels]
    result = {"start": idx, "round": t, "source_knots": n_start, "knots": len(supports),
              "distinctions": len(set().union(*map(set, supports))), **stats}
    result["peel_counts"] = peel(clauses, masks)
    result["seconds_to_join"] = round(perf_counter() - tick, 4)
    result["structural_patterns_tested"] = 0
    result["first_step"] = None
    result["first_step_needing_a_birth"] = None
    if all_patterns:
        result["patterns"] = []
    stagechecks = None
    try:
        for pattern in choices(clauses, masks):
            result["structural_patterns_tested"] += 1
            if structural_only:
                break
            if stagechecks is None:
                from omitted_semantics import StageChecks
                stagechecks = StageChecks(supports, n_start)
            readable = [[(masks[v], labels[v] & 1) for v in pair] for pair in pattern]
            raw_pairs = [[(list(bits(m)), s) for m, s in pair] for pair in readable]
            roles = stagechecks.check(readable, stop_first=False)
            if all_patterns:
                genuine = all(stagechecks.is_lower_bond((readable[0][i], readable[1][j], readable[2][i ^ j]))
                              for i, j in product(range(2), repeat=2))
                result["patterns"].append({"signed_pairs": raw_pairs, "four_genuine_lower_bonds": genuine,
                                           "qualifying_roles": roles})
            for rec in roles:
                proof = {"signed_pairs": raw_pairs, **rec}
                if result["first_step"] is None:
                    result["first_step"] = proof
                if rec["birth_law_deletions"] and result["first_step_needing_a_birth"] is None:
                    result["first_step_needing_a_birth"] = proof
            if not all_patterns and result["first_step_needing_a_birth"] is not None:
                break
    finally:
        if stagechecks is not None:
            stagechecks.close()
    result["completed_all_or_found_birth_step"] = not structural_only or not result["structural_patterns_tested"]
    if result["structural_patterns_tested"] and not structural_only:
        result["source_supports"] = supports
    result["elapsed_seconds"] = round(perf_counter() - tick, 4)
    result["process_peak_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", nargs=2, action="append", type=int, metavar=("ENTRY", "ROUND"))
    p.add_argument("--count", type=int, help="Prefix of the seeded permutation of all 211 omitted stages")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--seed", type=int, default=826135)
    p.add_argument("--output", type=Path)
    p.add_argument("--structural-only", action="store_true", help="Stop at first structural candidate before semantics")
    p.add_argument("--all-patterns", action="store_true",
                   help="Validate every structural pattern and save every qualifying role")
    args = p.parse_args()
    if args.structural_only and args.all_patterns:
        p.error("Choose structural-only or all-patterns.")
    starts, stages = roster()
    omitted = sorted(k for k, (supports, _) in stages.items() if len(set().union(*map(set, supports))) > 19)
    assert len(omitted) == 211 and len({k[0] for k in omitted}) == 193
    if args.stage:
        selected = list(map(tuple, args.stage))
    else:
        random.Random(args.seed).shuffle(omitted)
        selected = omitted[args.offset:args.offset + args.count if args.count is not None else None]
    with (args.output.open("w") if args.output else sys.stdout) as handle:
        for idx, t in selected:
            row = solve(idx, t, *stages[idx, t], structural_only=args.structural_only,
                        all_patterns=args.all_patterns)
            print(json.dumps(row, separators=(",", ":")), file=handle, flush=True)


if __name__ == "__main__":
    main()
