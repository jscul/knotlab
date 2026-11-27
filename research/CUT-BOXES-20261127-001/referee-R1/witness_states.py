"""Check a connected open box by literal assignment and single-law deletion."""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations, product
import json
from pathlib import Path
import sys
from time import perf_counter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "research/NAE-LAYER-20261127-001/referee-R1"))
from growth_rule import advance
from knotlab.cli import main as knotlab


# Candidate supports and carriers are transcribed from the predecessor's
# open_witness.json. No word counts, tests or verdicts are used as inputs.
START = [(4, 5, 6), (4, 7, 8), (0, 9, 10), (9, 11, 12), (1, 5, 12),
         (13, 14, 15), (7, 10, 11), (3, 14, 16), (2, 13, 16), (6, 8, 15)]
BORN = [(0, 1, 17), (2, 3, 18)]
LAWS = START + BORN
CARRIERS = [(0, 9, 17), (2, 3, 16), (1, 5, 18), (7, 10, 13), (4, 6, 8), (11, 12, 14)]
NAMES = ["A0", "A1", "B0", "B1", "C0", "C1"]
UPPER = ["P", "Q", "R"]
CHOICES = list(product((0, 1), (2, 3), (4, 5)))


def gather(raw, support):
    return sum((raw >> x & 1) << i for i, x in enumerate(support))


def support_mask(support):
    return sum(1 << x for x in support)


def word(raw, n):
    return "".join(str(raw >> i & 1) for i in range(n))


def counts(table, n):
    return dict(sorted((word(raw, n), count) for raw, count in table.items() if count))


def upper_word(six):
    return gather(six ^ (six >> 1), (0, 2, 4))


def projected(source, read):
    table = Counter()
    for six, count in source.items():
        table[read(six)] += count
    return table


def owners(knots):
    result = defaultdict(list)
    for i, knot in enumerate(knots):
        for x in knot:
            result[x].append(i)
    return result


def meet(knots):
    groups = [set(k) for k in knots]
    return [set(j for j, other in enumerate(groups) if i != j and group & other)
            for i, group in enumerate(groups)]


def same_part(neighbors):
    reached = {0}
    while True:
        extend = reached | set().union(*(neighbors[i] for i in reached))
        if extend == reached:
            return len(reached) == len(neighbors)
        reached = extend


def growth_checks():
    initial = owners(START)
    live = {v[0] for v in initial.values() if len(v) == 1}
    neighbors = meet(START)
    pairs = [(i, j, sorted(neighbors[i] & neighbors[j])) for i, j in combinations(sorted(live), 2)
             if neighbors[i] & neighbors[j]]
    assert pairs == [(2, 4, [3]), (7, 8, [5])] and same_part(neighbors)
    first = advance(START)
    assert first.status == "funded" and list(first.supports) == LAWS
    second = advance(LAWS)
    after = owners(LAWS)
    loose = sorted(x for x, v in after.items() if len(v) == 1)
    assert max(map(len, after.values())) == 2 and loose == [17, 18] and same_part(meet(LAWS))
    assert len(set().union(*map(set, CARRIERS))) == sum(map(len, CARRIERS))
    assert set(loose) <= set().union(*map(set, CARRIERS))
    return {
        "start_connected": True,
        "start_loose": sorted(x for x, v in initial.items() if len(v) == 1),
        "only_eligible_parent_pairs_with_common_older_holder": pairs,
        "funded_first_round": [vars(b) for b in first.births],
        "grown_connected": True, "grown_loose": loose,
        "grown_holders_per_distinction": {x: after[x] for x in sorted(after)},
        "following_round": {"status": second.status, "births": [vars(b) for b in second.births]},
    }


def clause(names, forbidden):
    return " ".join(("~" if value else "") + name for name, value in zip(names, forbidden, strict=True))


def describe_image(names, table):
    return [clause(names, tuple(int(c) for c in word(i, len(names))))
            for i in range(1 << len(names)) if i not in table]


def canonical(clauses, names, hidden=()):
    checks = {}
    for contact in names:
        loops = [name for name in names if name != contact]
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = knotlab(["check", "--cnf", "; ".join(clauses), "--loops", *loops,
                            "--contact", contact, "--witnesses", *hidden, "--json"])
        report = json.loads(buffer.getvalue())
        assert code == 0 and report["is_knot"] and len(report["allowed"]) == 7
        checks[contact] = {key: report[key] for key in
                           ("variables", "allowed", "binding", "loss_on_erasure", "coexistence")}
    return checks


def mixed_fixes(images, index):
    return sum({(value >> index) & 1 for value in values} == {0, 1} for values in images)


def allowed_holders(fail_counts):
    """Counts remaining after exactly the listed source laws are kept."""
    n = len(LAWS)
    totals = [fail_counts.get(mask, 0) for mask in range(1 << n)]
    for i in range(n):
        bit = 1 << i
        for mask in range(1 << n):
            if mask & bit:
                totals[mask] += totals[mask ^ bit]
    full = (1 << n) - 1
    return [totals[full ^ keep] for keep in range(1 << n)]


def minimal_holders(violation_counts):
    totals = allowed_holders(violation_counts)
    return [[i for i in range(len(LAWS)) if keep >> i & 1]
            for keep, n in enumerate(totals) if n == 0
            and all(totals[keep ^ (1 << i)] for i in range(len(LAWS)) if keep >> i & 1)]


def investigate(limit):
    physical = tuple(support_mask(k) for k in LAWS)
    carrier = tuple(support_mask(c) for c in CARRIERS)
    buckets = defaultdict(Counter)
    lowest_omission_example = {}
    mixed_by_raw_holder = [[set() for _ in range(8)] for _ in LAWS]
    by_loose = defaultdict(Counter)
    ok = {}
    for raw in range(limit):
        failed = sum(1 << i for i, mask in enumerate(physical) if (raw & mask) in (0, mask))
        six = sum(1 << i for i, mask in enumerate(carrier) if (raw & mask) in (0, mask))
        buckets[failed][six] += 1
        if failed == 0:
            ok[raw] = six
            by_loose[gather(raw, (17, 18))][six] += 1
            for k, support in enumerate(LAWS):
                mixed_by_raw_holder[k][gather(raw, support)].add(six)
        elif failed.bit_count() == 1 and upper_word(six) == 7:
            lowest_omission_example.setdefault(failed, raw)

    if limit != 1 << 19:
        return {"assignments": limit, "allowed": len(ok), "partial": True}
    source = buckets[0]
    stage_upper = projected(source, upper_word)
    assert set(stage_upper) == set(range(7))
    raw_unread = [[mixed_fixes(fixes, i) for i in range(6)] for fixes in mixed_by_raw_holder]
    assert min(min(row) for row in raw_unread) > 0

    flips = [[sum(not (raw >> x & 1) and raw ^ (1 << x) in ok and
                  ((ok[raw ^ (1 << x)] ^ six) >> i & 1) for raw, six in ok.items())
              for x in places] for i, places in enumerate(CARRIERS)]
    assert min(min(row) for row in flips) > 0
    loose_values = {word(fix, 2): [counts(projected(table, lambda x: x >> i & 1), 1)
                                    for i in range(6)] for fix, table in by_loose.items()}
    assert len(loose_values) == 4 and all(len(t) == 2 for row in loose_values.values() for t in row)

    abstract = {six: 1 for six in range(64) if all(gather(six, pick) != 7 for pick in CHOICES)}
    abstract_upper = projected(abstract, upper_word)
    assert set(abstract_upper) == set(stage_upper)
    clauses = [clause([NAMES[i] for i in pick], (1, 1, 1)) for pick in CHOICES]
    defs = []
    for j, name in enumerate(UPPER):
        names = [NAMES[2*j], NAMES[2*j+1], name]
        for a, b in product((0, 1), repeat=2):
            defs.append(clause(names, (a, b, int(a == b))))
    lower = []
    for pick in CHOICES:
        names = [NAMES[i] for i in pick]
        table = projected(source, lambda six: gather(six, pick))
        assert set(table) == set(range(7))
        failures = {mask: sum(n for six, n in hist.items() if gather(six, pick) == 7)
                    for mask, hist in buckets.items()}
        minimal = minimal_holders(failures)
        relevant = set().union(*(CARRIERS[j] for j in pick))
        missing = [sorted(relevant - set().union(*(LAWS[i] for i in holders))) for holders in minimal]
        assert len(minimal) == 1 and all(missing)
        upper_fixes = {}
        for kind, space in (("source", source), ("eight_clauses", abstract)):
            image_sets = [{upper_word(six) for six in space if gather(six, pick) == t} for t in range(8)]
            upper_fixes[kind] = [mixed_fixes(image_sets, j) for j in range(3)]
            assert min(upper_fixes[kind]) > 0
        restored_six = [six for six in range(64) if upper_word(six) == 7
                        and all(gather(six, c) != 7 for c in CHOICES if c != pick)]
        assert len(restored_six) == 1 and gather(restored_six[0], pick) == 7
        lower.append({"readings": names, "raw_states_by_triple": counts(table, 3),
                      "minimal_source_holder_sets_to_exclude_111": minimal,
                      "carrier_distinctions_missing_from_each_minimal_set": missing,
                      "upper_fixes_with_both_values": upper_fixes,
                      "restored_six_word_on_single_abstract_law_deletion": word(restored_six[0], 6),
                      "canonical": canonical(describe_image(names, table), names)})

    deletes = []
    all_loose_checks = []
    for i, law in enumerate(LAWS):
        mask = 1 << i
        extra = buckets[mask]
        upper = projected(extra, upper_word)
        assert upper[7] > 0 and set(stage_upper + upper) == set(range(8))
        added = [sum(count for six, count in extra.items() if gather(six, pick) == 7)
                 for pick in CHOICES]
        sample = lowest_omission_example[mask]
        deletes.append({"source_law": i, "remaining_source_states": len(ok) + sum(extra.values()),
                        "restored_upper_111": upper[7], "restored_upper_111_witness_raw_LSB_first": word(sample, 19),
                        "lower_111_counts_added_in_product_order": added})
        private = set(law) & {17, 18}
        if private:
            for six, n in extra.items():
                if upper_word(six) != 7 or n == 0:
                    continue
                picks = [pick for pick in CHOICES if gather(six, pick) == 7]
                assert len(picks) == 1 and private <= set().union(*(CARRIERS[j] for j in picks[0]))
            all_loose_checks.append({"source_law": i, "private_distinctions": sorted(private),
                                     "restored_upper_111_assignments_checked": upper[7]})

    return {
        "candidate_from": "research/UPPER-GROWN-20261127-001/referee-R1/open_witness.json",
        "growth_rule_from": "research/NAE-LAYER-20261127-001/referee-R1/growth_rule.py",
        "ten_start_laws_then_two_birth_laws": LAWS, "carrier_order": NAMES, "carriers": CARRIERS,
        "ordinary_growth": growth_checks(), "assignments": limit, "allowed": len(ok),
        "six_reading_state_counts": counts(source, 6), "lower": lower,
        "source_holder_fixes_with_both_values_by_lower_reading": raw_unread,
        "single_member_flips": flips, "all_loose_values_fixed_then_lower_value_counts": loose_values,
        "eight_abstract_clauses_permit_six_words": len(abstract), "upper_as_pairwise_disagreement": {
            "raw_assignments_per_word": counts(stage_upper, 3), "abstract_six_words_per_word": counts(abstract_upper, 3),
            "canonical_from_actual_six_image": canonical(describe_image(NAMES, source) + defs, UPPER, NAMES),
            "canonical_from_eight_lower_laws": canonical(clauses + defs, UPPER, NAMES)},
        "source_law_deletions": deletes, "necessary_carriers_of_loose_distinctions_checked": all_loose_checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1 << 19)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if not 1 <= args.limit <= 1 << 19:
        parser.error("--limit must be from 1 to 524288")
    start = perf_counter()
    answer = investigate(args.limit)
    answer["wall_seconds"] = round(perf_counter() - start, 6)
    if args.out:
        args.out.write_text(json.dumps(answer, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: answer[k] for k in ("assignments", "allowed", "wall_seconds")}))


if __name__ == "__main__":
    main()
