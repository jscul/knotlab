"""Check the records and completions of the registered setting births."""

import gzip
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import lcm
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STRUCTURES = ROOT / "research/TWO-COUNTINGS-20261125-001A/structures.json"
A, B = ("x1", "x2", "x3"), ("y1", "y2", "y3")
OPTIONS_A, OPTIONS_B = ("x2", "x3", "c"), ("y2", "y3", "t")
BITS = (0, 1)
CONTEXTS = tuple(product(BITS, repeat=2))


def allowed_states(rules):
    names = sorted({name for _, places in rules for name in places})
    indices = {name: 1 << i for i, name in enumerate(names)}
    masks = [(law, sum(indices[name] for name in places)) for law, places in rules]
    states = []
    for code in range(1 << len(names)):
        for law, mask in masks:
            ones = (mask & code).bit_count()
            if law == "nae":
                if ones in (0, mask.bit_count()):
                    break
            elif ones % 2 != (law == "odd"):
                break
        else:
            states.append({name: int(bool(code & indices[name])) for name in names})
    return states


def read(state, names):
    return tuple(state[n] for n in names)


def fresh_values(state, loose, shared):
    return [z for z in BITS if not state[loose] == state[shared] == z]


def same_information(states, left, right):
    pairs = {(read(state, left), read(state, right)) for state in states}
    return len(pairs) == len({l for l, _ in pairs}) == len({r for _, r in pairs})


def visible_response(states, old_record, loose, shared, extra=None):
    response = {}
    for state in states:
        label = read(state, old_record)
        multiplier = 1 if extra is None else len(fresh_values(state, *extra))
        g = tuple(multiplier * (z in fresh_values(state, loose, shared)) for z in BITS)
        if response.setdefault(label, g) != g:
            return False
    return True


def setting_stage(state, x, y, example, extra, bob_fresh=1):
    az = fresh_values(state, "x1", x)
    bz = fresh_values(state, "y1", y)
    if example == "E3":
        if state["x1"] == state[x] == state["s1"]:
            return []
        return [{"zb": v} for v in bz]
    if example == "E4":
        return [{"z": z} for z in az if z in bz]
    if bob_fresh == 1:
        second_records = [{"zb": z} for z in bz]
    else:
        second_records = [
            {"zb": z, "zb2": w}
            for z, w in product(BITS, repeat=2)
            if not state["y1"] == state[y] == z == w
        ]
    stage = [{"za": u} | v for u, v in product(az, second_records)]
    if extra is not None:
        stage = [row | {"f3": w} for row in stage for w in fresh_values(state, *extra)]
    return stage


def joint_tables(states, opts_a, opts_b, rec_a, rec_b, mode,
                 example=None, extra=None, bob_fresh=1, prior=None):
    tables = {}
    for a, b in CONTEXTS:
        table = Counter()
        for state in states:
            stage = setting_stage(state, opts_a[a], opts_b[b], example, extra, bob_fresh)
            if not stage:
                continue
            weight = 1 if mode == "finish" else Fraction(1, len(stage))
            if prior is not None:
                weight *= prior(state)
            for births in stage:
                if example == "E5" and births["za"] ^ births["zb"] != state["x1"]:
                    continue
                if example == "E7":
                    births["w"] = births["zb"] ^ state["x1"]
                final = state | births
                table[read(final, rec_a), read(final, rec_b)] += weight
        tables[a, b] = table
    return tables


def distributions(tables, side):
    result = {}
    for context, table in tables.items():
        mass = sum(table.values())
        dist = Counter()
        for pair, v in table.items():
            dist[pair[side]] += Fraction(v, mass)
        result[context] = dist
    return result


def total_variation(left, right):
    return sum(abs(left[k] - right[k]) for k in left.keys() | right.keys()) / 2


def changes(tables):
    alice, bob = (distributions(tables, i) for i in BITS)
    return (
        max(total_variation(alice[a, 0], alice[a, 1]) for a in BITS),
        max(total_variation(bob[0, b], bob[1, b]) for b in BITS),
    )


def score(tables):
    counts = tuple(
        sum(len({pair[side] for ab, table in tables.items() if ab[side] == setting for pair in table})
            for setting in BITS)
        for side in BITS
    )
    if counts[0] < counts[1]:
        tables = {(b, a): {(y, x): v for (x, y), v in row.items()} for (a, b), row in tables.items()}
    assert min(counts) <= 16, counts
    totals = {ab: sum(table.values()) for ab, table in tables.items()}
    probabilities = {
        ab: {k: Fraction(v, totals[ab]) for k, v in table.items()}
        for ab, table in tables.items()
    }
    scale = lcm(*(p.denominator for row in probabilities.values() for p in row.values()))
    left = [sorted({x for b in BITS for x, _ in probabilities[a, b]}) for a in BITS]
    right = [sorted({y for a in BITS for _, y in probabilities[a, b]}) for b in BITS]
    contributions = []
    for b in BITS:
        columns = []
        for y in right[b]:
            columns.append(
                tuple(
                    (1 - 2 * a * b) * int(scale * probabilities[a, b].get((x, y), 0))
                    for a in BITS
                    for x in left[a]
                )
            )
        contributions.append(
            [
                tuple(sum(s * v for s, v in zip(signs, row)) for row in zip(*columns))
                for signs in product((-1, 1), repeat=len(columns))
            ]
        )
    # One placement of the negative CHSH sign suffices over all outcome functions.
    # The first reader maximizes each row independently after the second answers.
    best = max(sum(abs(x + y) for x, y in zip(u, v)) for u, v in product(*contributions))
    return Fraction(best, scale)


def round_options(rules):
    holders = Counter(name for _, places in rules for name in places)
    holdings = [set(places) for _, places in rules]
    live = [i for i, places in enumerate(holdings) if any(holders[n] == 1 for n in places)]
    for i, places in enumerate(holdings):
        assert sum(bool(holdings[j] & places) for j in live if i != j) < 2
    parents = {
        loose: i
        for i in live
        for loose in holdings[i]
        if holders[loose] == 1
    }
    options = {loose: frozenset(n for n in holdings[i] if holders[n] > 1) for loose, i in parents.items()}
    for loose, other in combinations(options, 2):
        if parents[loose] == parents[other]:
            continue
        for shared, other_shared in product(options[loose], options[other]):
            inputs, other_inputs = {loose, shared}, {other, other_shared}
            assert not inputs & other_inputs
            assert not any(hold & inputs and hold & other_inputs for hold in holdings)
    assert max(Counter(parents.values()).values()) <= 2
    # Each parent makes at most two births, and no birth from a different
    # parent takes an input with the same holder. Each birth needs one fresh distinction.
    return options


def inspect_settings(structures, pilot):
    starts = [name for name in structures if "(start)" in name and name.startswith(("eleven", "ten"))]
    if pilot:
        starts = starts[:1]
    for name in starts:
        rules = structures[name]
        states = allowed_states(rules)
        options = round_options(rules)
        assert options["x1"] == set(OPTIONS_A)
        if name.startswith("eleven"):
            assert options == {"x1": set(OPTIONS_A), "y1": set(OPTIONS_B)}
            assert all(s["x1"] != s["c"] and s["y1"] != s["t"] for s in states)
            assert all(len(setting_stage(s, x, y, None, None)) > 0
                       for s in states for x, y in product(OPTIONS_A, OPTIONS_B))
        else:
            assert len(options) == 3
            assert all(s["t"] == s["y1"] ^ s["y2"] ^ s["y3"] for s in states)
            assert {s["t"] == s["y1"] for s in states} == {False, True}
        print(name, len(states), "old states", {k: sorted(v) for k, v in sorted(options.items())})
        third = next((n for n in options if n not in ("x1", "y1")), None)
        extras = [(third, n) for n in sorted(options[third])] if third else [None]
        pairs = product(combinations(OPTIONS_A, 2), combinations([n for n in OPTIONS_B if n in options["y1"]], 2), extras)
        for index, (xs, ys, extra) in enumerate(pairs):
            if pilot and index:
                break
            assert same_information(states, A, ("x1", *xs))
            assert same_information(states, B, ("y1", *ys))
            assert all(visible_response(states, A, "x1", x) for x in xs)
            assert all(visible_response(states, B, "y1", y, extra) for y in ys)
            missing = sorted((set(xs) - set(A)) | (set(ys) - set(B))
                             | (set(extra or ()) - set(B)))
            finish = joint_tables(states, xs, ys, (*A, "za"), (*B, "zb"), "finish", extra=extra)
            start = joint_tables(states, xs, ys, (*A, "za"), (*B, "zb"), "start", extra=extra)
            value = score(finish)
            expected = {"eleven": "20/9" if not missing else "19/9" if len(missing) == 1 else "37/18",
                        "ten": "109/54" if "c" in xs else "55/27"}[name.split()[0]]
            assert value == Fraction(expected) and changes(finish) == (0, 0)
            assert score(start) == 2 and changes(start) == (0, 0)
            print(xs, ys, extra, "outside fixed record", missing, "finish", value, "start 2, hidden both")
        if name.startswith("eleven"):
            return_states = states
            old_a = tuple(sorted({n for _, ps in rules[:5] for n in ps}))
            old_b = tuple(sorted({n for _, ps in rules[5:] for n in ps}))
            full = joint_tables(states, OPTIONS_A[:2], OPTIONS_B[:2], (*old_a, "za"), (*old_b, "zb"), "finish")
            assert changes(full) == (Fraction(1, 3), 0)
            print("All distinctions held by each reader, finish change", *(str(t) for t in changes(full)))
    return return_states


def inspect_examples(states, pilot):
    records = {
        "E3": ((*A, "s1"), (*B, "zb"), "7/3", ("0", "1/6")),
        "E4": ((*A, "z"), (*B, "z"), "17/6", ("1/3", "1/3")),
        "E5": ((*A, "za"), (*B, "zb"), "11/4", ("1/4", "0")),
        "E6": ((*A, "zb"), (*B, "zb"), "5/2", ("1/4", "0")),
        "E7": ((*A, "w"), (*B, "zb"), "5/2", ("1/4", "0")),
    }
    example_names = ("E5",) if pilot else records
    for name in example_names:
        ra, rb, expected, tv = records[name]
        tables = joint_tables(states, OPTIONS_A[:2], OPTIONS_B[:2], ra, rb, "start", example=name)
        value = score(tables)
        signal = tuple(str(t) for t in changes(tables))
        assert (str(value), signal) == (expected, tv)
        print(name, "score", value, "record changes", *signal)
    witness = next(s for s in states if read(s, A + B) == (0, 1, 0, 1, 0, 1))
    offered = setting_stage(witness, "x2", "y2", "E5", None)
    accepted = [(r["za"], r["zb"]) for r in offered if r["za"] ^ r["zb"] == witness["x1"]]
    assert len(offered) == 4 and accepted == [(0, 0), (1, 1)]
    print("E5 at old records 010 and 101, context 00, surviving fresh pairs", accepted)


def inspect_deletions(rules, pilot):
    reference_path = next((ROOT / "artifacts/SETTING-AS-REREAD-20261123-001A").glob("*/e.json"))
    reference = json.loads(reference_path.read_text())
    tested = [row for row in reference["rows"] if "b" in row]
    assert len(reference["rows"]) == 66 and len(tested) == 10
    assert sum(len(row["b"]) for row in tested) == 57
    above = [t for row in tested for t in row["b"] if Fraction(t["score_i"]) > 2]
    assert len(above) == 30 and sum(t["hidden"]["both"] for t in above) == 12
    print("Deletion archive: 66 starts, 10 scored, 57 comparisons, 12 hidden excesses and 18 exposed")
    for row in tested:
        removed = row["removed"]
        if removed not in ([3, 4], [1, 7]):
            continue
        states = allowed_states([rule for i, rule in enumerate(rules) if i not in removed])
        if removed == [1, 7]:
            def mass(state):
                return (4 - (state["m1"] == state["t"])) * (4 - (state["m2"] == state["t"]))

            fresh = ("zb", "zb2")
        else:
            mass = None
            fresh = ("zb",)
        answers = Counter()
        for test in (row["b"][:1] if pilot else row["b"]):
            xs, ys = test["pair_A"], test["pair_B"]
            tables = joint_tables(states, xs, ys, ("x1", *xs, "za"), ("y1", *ys, *fresh),
                                  "finish", bob_fresh=len(fresh), prior=mass)
            value = score(tables)
            tv = tuple(str(t) for t in changes(tables))
            assert str(value) == test["score_i"]
            assert tv == (test["hidden"]["A"]["largest_change"], test["hidden"]["B"]["largest_change"])
            assert all(sum(tables[a, b].values()) == test["words"][f"{a}{b}"] for a, b in CONTEXTS)
            answers[value] += 1
        print("Removing", row["removed_knots"], "finish scores",
              {str(v): n for v, n in sorted(answers.items())}, "largest", max(answers))


def archive_rows(ticket, pattern):
    for path in sorted((ROOT / "artifacts" / ticket).glob(f"*/{pattern}")):
        with gzip.open(path, "rt") as stream:
            yield from map(json.loads, stream)


def inspect_archives(pilot):
    populations = [
        ("ordinary growth", "REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B", "t1_hits_c2_*.jsonl.gz"),
        ("rule R", "REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C", "arm1_gains_three_*.jsonl.gz"),
        ("rule Q", "ONE-PARENT-REREAD-20261123-001A", "census_gains_c_*.jsonl.gz"),
    ]
    for label, ticket, pattern in populations:
        by_stage_arm = Counter()
        starts = set()
        for row in archive_rows(ticket, pattern):
            if label == "ordinary growth" and (row["stage0_excess"] or not row["excess"] or row["t"] == 0):
                continue
            assert len(row["table"]) == 64 and row["eval"][:2] == [True, True]
            by_stage_arm[row["t"], row.get("arm", "-")] += 1
            starts.add(row["si"])
            if pilot:
                break
        print(label, "gain starts", len(starts), "gain rows by round and arm", dict(sorted(by_stage_arm.items())))


if __name__ == "__main__":
    is_pilot = "--pilot" in sys.argv
    structures = json.loads(STRUCTURES.read_text())
    starting_states = inspect_settings(structures, is_pilot)
    inspect_examples(starting_states, is_pilot)
    inspect_deletions(structures["eleven (start)"], is_pilot)
    inspect_archives(is_pilot)
