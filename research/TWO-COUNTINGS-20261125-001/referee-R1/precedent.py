"""Recount the three earlier settings studies from their own rule lists and gain archives."""

import argparse
import gzip
import json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache, lru_cache
from itertools import product
from math import gcd, lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FIRST = next((ROOT / "artifacts").glob("SETTING-AS-REREAD-20261123-001A/*/main.json")).parent
SECOND = next((ROOT / "artifacts").glob("ONE-PARENT-REREAD-20261123-001A/*/PRUNED.md")).parent
THIRD = next((ROOT / "artifacts").glob("THIRD-HOLDER-20261123-001B/*/structures_found.json")).parent
COPIES = next((ROOT / "artifacts").glob("THIRD-HOLDER-20261123-001A/*/structure_k2.json")).parent
OBS = (("x1", "x2", "x3"), ("y1", "y2", "y3"))
SETTINGS = (("nae(x1,x2,za)", "nae(x1,x3,za)"), ("nae(y1,y2,zb)", "nae(y1,y3,zb)"))


def read(path):
    return json.loads(path.read_text())


@cache
def rule_parts(rule):
    law, places = rule[:-1].split("(")
    return law, tuple(places.split(","))


@cache
def bit_columns(width):
    """One bit per state of this side, with its distinction values in columns."""
    n = 1 << width
    result = []
    for position in range(width):
        block = 1 << position
        bits = ((1 << block) - 1) << block
        period = 2 * block
        while period < n:
            bits |= bits << period
            period *= 2
        result.append(bits)
    return (1 << n) - 1, result


def partition(bits, names, columns):
    parts = [bits]
    for name in names:
        col = columns[name]
        parts = [group for previous in parts for group in (previous & ~col, previous & col)]
    return parts


@lru_cache(maxsize=2100)
def enumerate_side(rules, shared, record):
    all_names = sorted(set(shared).union(record, *(rule_parts(r)[1] for r in rules)))
    full, bits = bit_columns(len(all_names))
    columns = dict(zip(all_names, bits))
    allowed = full
    for r in rules:
        law, places = rule_parts(r)
        if law == "nae":
            all_one, all_zero = full, full
            for v in places:
                all_one &= columns[v]
                all_zero &= ~columns[v]
            allowed &= ~(all_zero | all_one)
        else:
            assert law in ("even", "odd")
            parity = 0
            for v in places:
                parity ^= columns[v]
            allowed &= parity if law == "odd" else ~parity
    result = []
    for group in partition(allowed, shared, columns):
        counts = [p.bit_count() for p in partition(group, record, columns)]
        relations = []
        for r in rules:
            pieces = partition(group, rule_parts(r)[1], columns)
            relations.append(sum(1 << i for i, p in enumerate(pieces) if p))
        result.append((counts, relations))
    return result


@cache
def knot(rel, width):
    n = 1 << width
    if rel == 0 or rel == (1 << n) - 1:
        return False
    for i in range(width):
        bit = 1 << i
        for w in range(n):
            if w & bit == 0 and rel >> w & 1 == 0 and rel >> (w | bit) & 1 == 0:
                return False
    return True


@lru_cache(maxsize=1800)
def combine(sides, records):
    names = [{v for r in rules for v in rule_parts(r)[1]} for rules in sides]
    shared = tuple(sorted(names[0] & names[1]))
    a, b = (enumerate_side(side, shared, record) for side, record in zip(sides, records))
    width_a, width_b = (1 << len(rec) for rec in records)
    matrix = [[0] * width_b for _ in range(width_a)]
    induced = [[0] * len(side) for side in sides]
    for (ac, ar), (bc, br) in zip(a, b):
        if sum(ac) == 0 or sum(bc) == 0:
            continue
        for i, amount in enumerate(ac):
            if amount:
                for j, other in enumerate(bc):
                    matrix[i][j] += amount * other
        for masks, merged in zip((ar, br), induced):
            for i, mask in enumerate(masks):
                merged[i] |= mask
    failures = {}
    for rules, masks in zip(sides, induced):
        for rule, mask in zip(rules, masks):
            size = len(rule_parts(rule)[1])
            if not knot(mask, size):
                failures[rule] = [format(state, f"0{size}b") for state in range(1 << size) if mask >> state & 1]
    return matrix, failures


def contrasts(values):
    out = list(values)
    step = 1
    while step < len(out):
        for begin in range(0, len(out), 2 * step):
            for i in range(begin, begin + step):
                v, w = out[i], out[i + step]
                out[i], out[i + step] = v + w, v - w
        step *= 2
    return out


def parity_score(tables):
    totals = [sum(map(sum, m)) for m in tables]
    scale = lcm(*totals)
    correlations = []
    for m, total in zip(tables, totals):
        rows = [contrasts(r) for r in m]
        both = list(zip(*(contrasts(col) for col in zip(*rows))))
        correlations.append([[v * (scale // total) for v in row] for row in both])
    c00, c01, c10, c11 = correlations
    best = 0
    masks = range(1, len(c00))
    for a0, a1 in product(masks, repeat=2):
        for orientation in (-1, 1):
            plus = max(abs(c00[a0][b] + orientation * c10[a1][b]) for b in masks)
            minus = max(abs(c01[a0][b] - orientation * c11[a1][b]) for b in masks)
            best = max(best, plus + minus)
    return str(Fraction(best, scale))


def normalized_marginal(matrix, side):
    counts = list(map(sum, matrix if side == 0 else zip(*matrix)))
    total = sum(counts)
    return [Fraction(c, total) for c in counts]


def same_archived_table(current, saved):
    """The older study identified choice swaps, flipping all three recorded old bits, and exchanging observers."""
    common = gcd(*(v for row in current for v in row))
    scaled = [[v // common for v in row] for row in current]
    maps = []
    for swap, flip in product(range(2), repeat=2):
        indices = []
        for state in range(8):
            first, second, third = (state >> bit & 1 for bit in (2, 1, 0))
            if swap:
                second, third = third, second
            value = 4 * first + 2 * second + third
            indices.append(value ^ (7 if flip else 0))
        maps.append(indices)
    for coordinates in (scaled, list(zip(*scaled))):
        for left, right in product(maps, repeat=2):
            if all(coordinates[left[i]][right[j]] == saved[i][j] for i in range(8) for j in range(8)):
                return True
    return False


def settings(sides):
    old, old_fail = combine(sides, OBS)
    tables, failures = [], []
    records = (OBS[0] + ("za",), OBS[1] + ("zb",))
    for a, b in product(range(2), repeat=2):
        done = (sides[0] + (SETTINGS[0][a],), sides[1] + (SETTINGS[1][b],))
        table, failed = combine(done, records)
        tables.append(table)
        failures.append(failed)
    hidden = [
        all(normalized_marginal(tables[i], side) == normalized_marginal(tables[j], side)
            for i, j in (((0, 1), (2, 3)) if side == 0 else ((0, 2), (1, 3))))
        for side in (0, 1)
    ]
    return {
        "old_matrix": old,
        "old_states": sum(map(sum, old)),
        "old_fail": old_fail,
        "finished_states_00_01_10_11": [sum(map(sum, table)) for table in tables],
        "finished_fail_00_01_10_11": failures,
        "hidden": hidden,
        "score": parity_score(tables),
    }


def split_old_part(rules):
    # The two sides identify their private old distinctions by x/A and y/B.
    # Every round-one birth here belongs to the y side. Later births checked
    # here also use that side's fresh distinctions.
    def on_a(rule):
        return any(v.startswith(("x", "A")) for v in rule_parts(rule)[1])
    return tuple(r for r in rules if on_a(r)), tuple(r for r in rules if not on_a(r))


def available_at_single_parent(sides):
    """A necessary condition for Q to offer both stated settings by one re-reading parent on each side."""
    rules = [set(rule_parts(r)[1]) for side in sides for r in side]
    holds = Counter(name for places in rules for name in places)
    possible = []
    for first, option0, option1 in OBS:
        parents = [places for places in rules if first in places]
        possible.append(len(parents) == 1 and {option0, option1} <= parents[0]
                        and min(holds[option0], holds[option1]) >= 2)
    return possible


def direct_setting_study():
    main = read(FIRST / "main.json")
    signs = read(FIRST / "f_000-512.json")["rows"]
    deletions = read(FIRST / "e.json")["rows"]
    sides = (tuple(main["knots"][:5]), tuple(main["knots"][5:]))
    old, failed = combine(sides, OBS)
    direct = {}
    for pa in ("x2", "x3", "c"):
        for pb in ("y2", "y3", "t"):
            finished = (sides[0] + (f"nae(x1,{pa},za)",), sides[1] + (f"nae(y1,{pb},zb)",))
            _, ff = combine(finished, (OBS[0] + ("za",), OBS[1] + ("zb",)))
            direct[pa + "/" + pb] = ff
    holders = {v: [r for side in sides for r in side if v in rule_parts(r)[1]] for v in ("x1", "y1")}
    surviving = tuple(tuple(r for r in side if r not in failed) for side in sides)
    after, _ = combine(surviving, OBS)
    return {
        "old_states": sum(map(sum, old)), "old_fail": failed,
        "only_holders_of_the_two_loose_distinctions": holders,
        "Q_has_the_required_parent_and_both_options_on_each_side": available_at_single_parent(sides),
        "loose_distinctions_held_after_omitting_failed_rules": [v for v, rules in holders.items() if set(rules) - set(failed)],
        "states_after_dropping_the_two_failing_parents_with_all_16_old_distinctions_kept": sum(map(sum, after)),
        "nine_concrete_finished_structures": direct,
        "source_classification_of_the_512_sign_assignments": dict(Counter(
            f"{row['score_i']}, {'hidden' if row['hidden'] else 'visible'}" for row in signs)),
        "source_deletion_subsets": len(deletions),
        "source_subsets_with_only_the_two_named_births": [r["removed_knots"] for r in deletions if r["strict"]],
        "source_subsets_with_a_hidden_excess_and_any_other_births": read(FIRST / "e.json")["loose_hidden_excess"],
    }


def third_study(sample):
    found = read(THIRD / "structures_found.json")
    results, groups = [], Counter()
    for index, given in enumerate(found):
        if sample and index not in (0, 99, 290, 291):
            continue
        sides = tuple(tuple(given[name]) for name in ("knots_A", "knots_B"))
        data = settings(sides)
        old = data.pop("old_matrix")
        matrix_matches = None if given.get("M") is None else same_archived_table(old, given["M"])
        assert matrix_matches is not False, index
        passing = not data["old_fail"] and not any(data["finished_fail_00_01_10_11"])
        size = sum(map(len, sides))
        groups[(given["source"], size, passing)] += 1
        assert data["score"] == given["score"] and all(data["hidden"]), (index, data["score"], given["score"])
        results.append({
            "index_in_structures_found_zero_based": index, "source": given["source"], "old_rules": size,
            "score": data["score"], "hidden": data["hidden"], "all_pass": passing,
            "archived_old_matrix_agrees_up_to_the_declared_symmetries": matrix_matches, "old_fail": list(data["old_fail"]),
            "finished_fail": [list(item) for item in data["finished_fail_00_01_10_11"]],
            "extra_old_holders": given["measures"]["extra_holders"],
            "Q_has_the_required_parent_and_both_options_on_each_side": available_at_single_parent(sides),
        })
    return {
        "scope": "One stored rule list per reported representative, including the two reduction starts. Different rule lists with the same observer table need separate knot tests.",
        "counts": [{"source": source, "old_rules": n, "all_pass": p, "count": count}
                   for (source, n, p), count in sorted(groups.items())],
        "representatives": results,
    }


def iter_gains():
    for path in sorted(SECOND.glob("census_gains_c_*.jsonl.gz")):
        with gzip.open(path, "rt") as stream:
            for line in stream:
                yield json.loads(line)


def q_study(sample):
    by_part = {}
    tested = {}
    by_arm = defaultdict(Counter)
    source_parts = Counter()
    for path in sorted(SECOND.glob("census_parts_c_*.jsonl.gz")):
        with gzip.open(path, "rt") as stream:
            for line in stream:
                row = json.loads(line)
                source_parts["included"] += 1
                mode = row["choice_record"]["mode"]
                assert mode in ("all", "drawn", "no round")
                source_parts["with_round_within_stop"] += mode != "no round"
                source_parts["complete_round_one_choices"] += mode == "all"
                source_parts["choices_sampled"] += mode == "drawn"
    for row in iter_gains():
        tid, when, arm = row["tid"], row["t"], row["arm"]
        if when > 1 and arm != "uniform":
            continue
        if sample and tid not in (104, 113):
            continue
        rules = tuple(row["knots"])
        before = rules[:7]
        if tid not in by_part:
            baseline = settings(split_old_part(before))
            baseline.pop("old_matrix")
            by_part[tid] = {"original_rules": before, "baseline": baseline, "uniform": Counter(), "mixed": Counter(),
                            "Q_has_the_required_setting_parent_and_both_options_before_growth": available_at_single_parent(split_old_part(before)),
                            "Q_has_the_required_setting_parent_and_both_options_after_growth": set()}
        assert before == by_part[tid]["original_rules"]
        if rules not in tested:
            tested[rules] = settings(split_old_part(rules))
        data = tested[rules]
        assert all(data["hidden"]) and data["score"] == row["eval"][-1], (tid, data, row["eval"])
        assert not data["old_fail"], (tid, data["old_fail"])
        failed_set = set().union(*data["finished_fail_00_01_10_11"])
        exact = all(set(fail) <= {"nae(x1,x2,za)"} for fail in data["finished_fail_00_01_10_11"])
        assert exact and all(set(fail) == failed_set for fail in data["finished_fail_00_01_10_11"][:2])
        assert not any(data["finished_fail_00_01_10_11"][2:])
        assert data["finished_fail_00_01_10_11"] == by_part[tid]["baseline"]["finished_fail_00_01_10_11"]
        label = f"round {when}, " + ("fails a supplied setting" if failed_set else "all pass")
        by_arm[arm][label] += 1
        by_part[tid][arm][f"round {when}, {data['score']}"] += 1
        if when == 1:
            parents = available_at_single_parent(split_old_part(rules))
            by_part[tid]["Q_has_the_required_setting_parent_and_both_options_after_growth"].add(tuple(parents))
    for part in by_part.values():
        key = "Q_has_the_required_setting_parent_and_both_options_after_growth"
        part[key] = sorted(part[key])
    return {
        "prior_parts_archive": source_parts,
        "counts": by_arm, "distinct_rule_lists_at_grown_stages_tested": len(tested),
        "scope": "All round-one gaining records and later uniform-law gaining records. The baseline is each old part tested with the same four supplied setting pairs before any rule-Q birth.",
        "parts": by_part,
    }


def multiple_births(sample):
    """Check the two older copied structures; their extra old distinctions have uniquely determined values."""
    reports = {}
    for k in ((2,) if sample else (2, 3)):
        example = read(COPIES / f"structure_k{k}.json")
        original = (example["alice_knots"], example["bob_knots"])
        # A copied old distinction occurs in a parity rule with the same other
        # places and same sign as its original. Subtracting the two equations
        # establishes equality. Verify that witness separately for every copy.
        copy_map = {v: v.split("_")[0] for v in example["old_distinctions"] if "_" in v}
        for copied, base in copy_map.items():
            occurrences = [(law, vs) for side in original for law, vs in side if copied in vs]
            assert len(occurrences) == 1
            law, places = occurrences[0]
            assert law in ("even", "odd")
            twin = [base if v == copied else v for v in places]
            assert any([law, twin] in side for side in original)

        def reduce_names(rules):
            result = []
            for law, places in rules:
                short = tuple(copy_map.get(v, v) for v in places)
                assert len(short) == len(set(short))
                result.append(law + "(" + ",".join(short) + ")")
            return tuple(result)

        old_sides = tuple(reduce_names(side) for side in original)
        old, old_fails = combine(old_sides, OBS)
        finish, start = [], []
        pair_reports = []
        for a, b in product(range(2), repeat=2):
            pair = (example["births_alice"][str(a)], example["births_bob"][str(b)])
            sides = tuple(side + reduce_names(new) for side, new in zip(old_sides, pair))
            records = tuple(tuple(example[name]) for name in ("record_alice", "record_bob"))
            table, fails = combine(sides, records)
            finish.append(table)
            # Each record entry names the old observer values and all k fresh
            # values. Its count in a finished table is the corresponding old
            # pair count. Counting from the start divides that count among
            # all record entries that extend that old pair.
            copies_per_value = 1 << k
            counted = [[0] * len(table[0]) for _ in table]
            blocks = Counter()
            for i, row in enumerate(table):
                for j, value in enumerate(row):
                    if value:
                        old_pair = i >> k, j >> k
                        assert value == old[old_pair[0]][old_pair[1]]
                        blocks[old_pair] += 1
            for i, row in enumerate(table):
                for j, value in enumerate(row):
                    if value:
                        divisor = blocks[i >> k, j >> k]
                        assert copies_per_value ** 2 % divisor == 0
                        counted[i][j] = value * (copies_per_value ** 2 // divisor)
            assert sum(map(sum, counted)) == sum(map(sum, old)) * copies_per_value ** 2
            start.append(counted)
            pair_reports.append({"settings": [a, b], "rules": sum(map(len, sides)),
                                 "states": sum(map(sum, table)), "failing_rules": fails})
        def hidden(tables):
            return all(normalized_marginal(tables[i], side) == normalized_marginal(tables[j], side)
                       for side, pairs in enumerate((((0, 1), (2, 3)), ((0, 2), (1, 3))))
                       for i, j in pairs)
        reports[k] = {
            "old_rules": sum(map(len, old_sides)), "old_states": sum(map(sum, old)), "old_failing_rules": old_fails,
            "copies_verified_equal_to_old_distinctions": len(copy_map), "finished": pair_reports,
            "parity_score_from_the_finish": parity_score(finish), "both_hidden_from_the_finish": hidden(finish),
            "parity_score_from_the_start": parity_score(start), "both_hidden_from_the_start": hidden(start),
        }
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="Time four representative third-holder cases and two one-parent parts.")
    args = parser.parse_args()
    output = {"direct_lawful_settings": direct_setting_study(), "third_holder": third_study(args.sample),
              "one_parent": q_study(args.sample), "multiple_birth_settings_in_the_earlier_study": multiple_births(args.sample)}
    if args.sample:
        print("Sample passed.", len(output["third_holder"]["representatives"]), len(output["one_parent"]["parts"]))
        return
    target = HERE / "precedent_counts.json"
    target.write_text(json.dumps(output, indent=1, sort_keys=True) + "\n")
    print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
