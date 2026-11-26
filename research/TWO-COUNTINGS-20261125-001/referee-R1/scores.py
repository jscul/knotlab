"""Recount setting scores from frozen rules and archived birth records."""

import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import lru_cache
import gzip
from itertools import combinations, product
import json
from math import lcm, prod
from pathlib import Path
from random import Random
import resource
from time import perf_counter

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
TICKET = ROOT / "research" / "TWO-COUNTINGS-20261125-001A"
ARTIFACTS = ROOT / "artifacts"
STUDY = ARTIFACTS / TICKET.name / f"{TICKET.name}-E001_two_countings"
SETTINGS = tuple(product(range(2), repeat=2))
FIRST = ("x1", "x2", "x3")
SECOND = ("y1", "y2", "y3")
DEFAULT_OPTIONS = (("x2", "x3"), ("y2", "y3"))
START = "from the start"
STAGE = "from stage 1"
FINISH = "from the finish"
MIXED_FIRST = "mixed stage (the first observer first)"
MIXED_SECOND = "mixed stage (the second observer first)"
POOLED_START = "from the start, pooled (nu uniform over histories)"
POOLED_FINISH = "from the finish, pooled (each history and state once, TD 3.5)"
POOLED_UNIFORM = "from the finish, nu uniform over histories"


def read_json(path):
    return json.loads(path.read_text())


def rule(text):
    kind, names = text.rstrip(")").split("(")
    return kind, tuple(names.split(","))


def rule_names(rules):
    return sorted({name for _, names in rules for name in names})


def holds(kind, value, mask):
    taken = value & mask
    if kind == "nae":
        return taken not in (0, mask)
    return (taken.bit_count() % 2) == (kind == "odd")


@lru_cache(maxsize=160)
def allowed(rules):
    """Eliminate parity constraints, then filter their solutions by not-all-equal."""
    names = rule_names(rules)
    bits = {name: 1 << i for i, name in enumerate(names)}
    pivots = {}
    nae_masks = []
    for kind, places in rules:
        assert kind in {"even", "odd", "nae"} and len(set(places)) == len(places)
        mask = sum(bits[name] for name in places)
        if kind == "nae":
            nae_masks.append(mask)
            continue
        value = int(kind == "odd")
        while mask and (pivot := mask.bit_length() - 1) in pivots:
            previous, parity = pivots[pivot]
            mask ^= previous
            value ^= parity
        if not mask:
            if value:
                return bits, ()
        else:
            pivots[mask.bit_length() - 1] = mask, value
    free_bits = tuple(bits[name] for i, name in enumerate(names) if i not in pivots)
    candidates = [0]
    for bit in free_bits:
        candidates.extend([candidate | bit for candidate in candidates])
    equations = [(1 << pivot, *pivots[pivot]) for pivot in sorted(pivots)]
    states = []
    for candidate in candidates:
        for bit, mask, parity in equations:
            if ((candidate & mask).bit_count() % 2) != parity:
                candidate |= bit
        if all(holds("nae", candidate, mask) for mask in nae_masks):
            states.append(candidate)
    return bits, tuple(sorted(states))


def encoded(state, record, bits):
    return sum((1 << i) for i, name in enumerate(record) if state & bits[name])


@lru_cache(maxsize=None)
def fresh_options(kind, n_old, n_fresh, old_values):
    mask = (1 << (n_old + n_fresh)) - 1
    return tuple(
        fresh for fresh in range(1 << n_fresh)
        if holds(kind, old_values | (fresh << n_old), mask)
    )


def round_completion_rows(round_rules, bits):
    assigned_fresh = set()
    rows = []
    for kind, places in round_rules:
        old = tuple(name for name in places if name in bits)
        fresh = set(places) - bits.keys()
        assert fresh and assigned_fresh.isdisjoint(fresh)
        assigned_fresh.update(fresh)
        rows.append((kind, old, len(fresh)))
    return rows


def completion_count(completion_rows, bits, state):
    return prod(len(fresh_options(kind, len(old), n_fresh, encoded(state, old, bits)))
                for kind, old, n_fresh in completion_rows)


def setting_rule(own, option, fresh):
    return "nae", (own, option, fresh)


def finished_rules(source, before, options, extra=()):
    return {
        (a, b): source + before + (
            setting_rule("x1", options[0][a], "za"),
            setting_rule("y1", options[1][b], "zb"),
        ) + extra
        for a, b in SETTINGS
    }


def build_tables(source, before=(), options=DEFAULT_OPTIONS, extra=(), shared_record=False):
    """Sum over the private fresh distinctions of the pre-setting and setting births."""
    bits, states = allowed(source)
    assert states
    pre_round = round_completion_rows(before, bits)
    third_birth = round_completion_rows(extra, bits)
    fresh_before = set(rule_names(before)) - bits.keys()
    fresh_extra = set(rule_names(extra)) - bits.keys()
    assert fresh_before.isdisjoint(fresh_extra | {"za", "zb"})
    assert fresh_extra.isdisjoint({"za", "zb"})
    counts = {stage: np.zeros((2, 2, 16, 16), dtype=np.int64)
              for stage in (START, FINISH, MIXED_FIRST, MIXED_SECOND)}
    if before:
        counts[STAGE] = np.zeros((2, 2, 16, 16), dtype=np.int64)
    shared = {stage: np.zeros((2, 2, 4), dtype=np.int64) for stage in counts} if shared_record else {}
    old_counts = np.zeros((8, 8), dtype=np.int64)
    fresh_given_old = {}
    for state in states:
        grow = completion_count(pre_round, bits, state)
        third = completion_count(third_birth, bits, state)
        assert grow > 0 and third > 0
        x = encoded(state, FIRST, bits)
        y = encoded(state, SECOND, bits)
        old_counts[x, y] += grow
        shared_value = encoded(state, ("s1", "s2"), bits) if shared_record else None
        for a, b in SETTINGS:
            first_values = fresh_options("nae", 2, 1, encoded(state, ("x1", options[0][a]), bits))
            second_values = fresh_options("nae", 2, 1, encoded(state, ("y1", options[1][b]), bits))
            # The all-functions maximum can use the old record alone. This identifies precisely
            # when the two fresh bits are independent local randomizations of those old records.
            assert first_values == fresh_given_old.setdefault((0, a, x), first_values)
            assert second_values == fresh_given_old.setdefault((1, b, y), second_values)
            n_first, n_second = len(first_values), len(second_values)
            weights = {START: 4 // (n_first * n_second), FINISH: grow * third,
                       MIXED_FIRST: grow * (2 // n_second), MIXED_SECOND: grow * third * (2 // n_first)}
            if before:
                weights[STAGE] = grow * weights[START]
            for za, zb in product(first_values, second_values):
                for stage, weight in weights.items():
                    counts[stage][a, b, x + 8 * za, y + 8 * zb] += weight
                    if shared_record:
                        shared[stage][a, b, shared_value] += weight
    return counts, old_counts, len(states), shared


def normalized(tables):
    """Integer numerators on one checked common denominator."""
    tables = np.array(tables, dtype=np.int64)
    flat = tables.reshape(4, -1)
    divisors = np.gcd.reduce(flat, axis=1)
    assert np.all(divisors > 0)
    flat //= divisors[:, None]
    totals = flat.sum(axis=1)
    denominator = lcm(*map(int, totals))
    assert 4 * denominator < 2**63
    flat *= (denominator // totals)[:, None]
    return tables, denominator


def coarsen(tables):
    return tables.reshape(2, 2, 2, 8, 2, 8).sum(axis=(2, 4))


@lru_cache(maxsize=None)
def signs(n, fix_first):
    choices = np.arange(1 << (n - fix_first), dtype=np.int64) << fix_first
    return 1 - 2 * ((choices[:, None] >> np.arange(n)) & 1)


def best_all(tables):
    """Optimize the second record functions by signs of their coefficients."""
    supports = [np.flatnonzero(tables[a].sum(axis=(0, 2))) for a in range(2)]
    others = [np.flatnonzero(tables[:, b].sum(axis=(0, 1))) for b in range(2)]
    if sum(map(len, supports)) > sum(map(len, others)):
        tables = tables.transpose(1, 0, 3, 2)
        supports = others
    first = signs(len(supports[0]), True)
    second = signs(len(supports[1]), False)
    terms = [first @ tables[0, b, supports[0], :] for b in range(2)]
    other_terms = [second @ tables[1, b, supports[1], :] for b in range(2)]
    # All four minus-sign placements are equivalent by sign changes of entire outcome functions.
    # The fixed sign likewise amounts to changing the sign of all four functions together.
    return max(
        int(np.max(np.abs(terms[0] + row_0).sum(axis=1) +
                   np.abs(terms[1] - row_1).sum(axis=1)))
        for row_0, row_1 in zip(*other_terms)
    )


PARITIES = np.array([[1 - 2 * ((mask & value).bit_count() % 2) for value in range(16)]
                     for mask in range(1, 16)], dtype=np.int64)


def best_parity(tables):
    correlations = PARITIES @ tables @ PARITIES.T
    highs = []
    lows = []
    for minus_a, minus_b in SETTINGS:
        responses = []
        for b in range(2):
            first_sign = -1 if (minus_a, minus_b) == (0, b) else 1
            second_sign = -1 if (minus_a, minus_b) == (1, b) else 1
            responses.append(first_sign * correlations[0, b, :, None, :] +
                             second_sign * correlations[1, b, None, :, :])
        highs.append(int((responses[0].max(axis=2) + responses[1].max(axis=2)).max()))
        lows.append(int((responses[0].min(axis=2) + responses[1].min(axis=2)).min()))
    return max(highs), max(max(highs), -min(lows))


@lru_cache(maxsize=1024)
def score_normalized(encoded_tables, denominator):
    tables = np.frombuffer(encoded_tables, dtype=np.int64).reshape(2, 2, 16, 16)
    # A local average of a sign function is in [-1, 1]; the bilinear maximum
    # has a deterministic sign function at each of these intervals' ends.
    best = best_all(coarsen(tables))
    signed, absolute = best_parity(tables)
    change_first = int(np.abs(tables[:, 0].sum(axis=2) - tables[:, 1].sum(axis=2)).sum(axis=1).max())
    change_second = int(np.abs(tables[0].sum(axis=1) - tables[1].sum(axis=1)).sum(axis=1).max())
    return {"score_all": str(Fraction(best, denominator)),
            "score_parity": str(Fraction(signed, denominator)),
            "score_parity_abs": str(Fraction(absolute, denominator)),
            "change_first": str(Fraction(change_first, 2 * denominator)),
            "change_second": str(Fraction(change_second, 2 * denominator)),
            "hidden": change_first == change_second == 0}


def score(raw):
    tables, denominator = normalized(raw)
    return score_normalized(tables.tobytes(), denominator)


def record_change(raw):
    amounts, denominator = normalized(raw)
    first = int(np.abs(amounts[:, 0] - amounts[:, 1]).sum(axis=1).max())
    second = int(np.abs(amounts[0] - amounts[1]).sum(axis=1).max())
    return {"change under the second observer's setting": str(Fraction(first, 2 * denominator)),
            "change under the first observer's setting": str(Fraction(second, 2 * denominator))}


def history(source, before=(), options=DEFAULT_OPTIONS, extra=(), shared=False):
    raw, old_counts, n_source, shared_counts = build_tables(source, before, options, extra, shared)
    return {"rows": {stage: score(tables) for stage, tables in raw.items()},
            "source states": n_source, "states before settings": int(old_counts.sum()),
            "states at the finish": dict(zip(map(str, SETTINGS), map(int, raw[FINISH].sum(axis=(2, 3)).flat))),
            "shared record": {stage: record_change(counts) for stage, counts in shared_counts.items()}}, raw, old_counts


def pooled(raw_variants, stage, uniform):
    if not uniform:
        return sum((r[stage] for r in raw_variants), start=np.zeros_like(raw_variants[0][stage]))
    normalized_variants = [normalized(r[stage]) for r in raw_variants]
    common = lcm(*(d for _, d in normalized_variants))
    assert 4 * len(raw_variants) * common < 2**63
    return sum((table * (common // denom) for table, denom in normalized_variants),
               start=np.zeros_like(raw_variants[0][stage]))


def keyed(raw, patterns, n_functions):
    results = {}
    const = n_functions - 1
    for label in (START, FINISH):
        results[label] = {}
        for b in range(2):
            weights = np.zeros((n_functions, 16), dtype=np.int64)
            for i, pattern in enumerate(patterns):
                selection_bit = pattern if n_functions == 256 else i
                first_values = raw[label][:, b, pattern] + raw[label][:, b, 8 + pattern]
                which = (np.arange(n_functions) >> selection_bit) & 1
                weights += first_values[which]
            totals = weights.sum(axis=1)
            biggest = Fraction(0)
            against_constant = Fraction(0)
            witness = (0, 1)
            nonzero = 0
            for g in range(n_functions - 1):
                divergences = np.abs(weights[g] * totals[g + 1:, None] - weights[g + 1:] * totals[g]).sum(axis=1)
                for offset in np.flatnonzero(divergences):
                    other = g + 1 + int(offset)
                    change = Fraction(int(divergences[offset]), 2 * int(totals[g]) * int(totals[other]))
                    nonzero += 1
                    if change > biggest:
                        biggest, witness = change, (g, other)
                    if (g == 0 or other == const) and change > against_constant:
                        against_constant = change
            results[label][str(b)] = {"pairs": n_functions * (n_functions - 1) // 2,
                                      "different pairs": nonzero, "largest": str(biggest),
                                      "against a constant": str(against_constant),
                                      "witness": [format(g, f"0{(n_functions - 1).bit_length()}b") for g in witness]}
    return {"functions": n_functions, "allowed patterns": patterns, "rows": results}


def ten_choices(source, third_own):
    """The special no-join start and one-fresh-distinction births of both ten-rule cases."""
    places = [set(places) for _, places in source]
    holds_at_start = Counter(name for held in places for name in held)
    loose = {name for name, count in holds_at_start.items() if count == 1}
    assert loose == {"x1", "y1", third_own}
    members = [i for i, held in enumerate(places) if held & loose]
    assert len(members) == 2
    assert not any(all(held & places[i] for i in members) for j, held in enumerate(places) if j not in members)
    choices = [set(next(held for held in places if name in held)) - loose
               for name in ("x1", "y1", third_own)]
    assert choices[0] == {"x2", "x3", "c"}
    second_option = next(name for name in ("y2", "y3") if name != third_own)
    assert choices[1] == choices[2] == {second_option, "t"}
    combinations_checked = 0
    for takes in product(*map(sorted, choices)):
        births = [set(pair) for pair in zip(("x1", "y1", third_own), takes)]
        demand = [0, 0, 0]
        for i, j in combinations(range(3), 2):
            others = places + [held for k, held in enumerate(births) if k not in (i, j)]
            if any(held & births[i] and held & births[j] for held in others):
                demand[i] += 1
                demand[j] += 1
        assert demand == [0, 1, 1]
        assert [max(d, 3 - len(birth), 1) for d, birth in zip(demand, births)] == [1, 1, 1]
        combinations_checked += 1
    return second_option, combinations_checked


def frozen_structures():
    return {label: tuple((kind, tuple(places)) for kind, places in rules)
            for label, rules in read_json(TICKET / "structures.json").items()}


def compare_history(label, measured, reported, differences):
    values = {"allowed at the finish": measured["states at the finish"],
              "allowed at S_s": measured["states before settings"]}
    for field, value in values.items():
        if value != reported["info"][field]:
            differences.append([label, "counts", field, value, reported["info"][field]])
    if measured["rows"].keys() != reported["rows"].keys():
        differences.append([label, "weightings", list(measured["rows"]), list(reported["rows"])])
    for stage, row in measured["rows"].items():
        for field, value in row.items():
            if value != reported["rows"][stage][field]:
                differences.append([label, stage, field, value, reported["rows"][stage][field]])


def compare_finished(label, expected, recorded, differences):
    for pair, rules in expected.items():
        if rules != tuple(rule(text) for text in recorded[str(pair)]):
            differences.append([label, pair, "finished rules"])


def check_keyed(report, name, measured, differences):
    for b in range(2):
        standard = report["results"][f"second observer fixed at {b}"]
        for mode in ("from the start", "from the finish (pooled)"):
            row = measured["rows"][START if mode == "from the start" else FINISH][str(b)]
            for key, field in (("largest change of the second record between two g", "largest"),
                               ("largest change against a constant function", "against a constant")):
                if row[field] != standard[f"{mode}: {key}"]:
                    differences.append([name, b, mode, key, row[field], standard[f"{mode}: {key}"]])
        for label, actual in (("functions g", measured["functions"]),
                              ("first observer allowed patterns of (x1,x2,x3)", len(measured["allowed patterns"]))):
            if actual != standard[label]:
                differences.append([name, b, label, actual, standard[label]])


def group_items(structures, reported, limit):
    differences = []
    named_rows = {}
    options_first = list(combinations(("x2", "x3", "c"), 2))
    options_second = list(combinations(("y2", "y3", "t"), 2))
    raw_keyed = {}
    sources = {name: structures[f"{name} (start)"] for name in ("eleven", "seven", "eight", "eighteen")}
    sources["nine"] = structures["nine, the pencil (start)"]
    sources["smallest gain"] = structures["smallest gain: part"]
    growth = structures["smallest gain: part + rule-Q round 1"][len(sources["smallest gain"]):]
    sources["eight-thirds case"] = tuple(map(rule, (
        "odd(x1,x3,s1)", "odd(h1,h2,h3)", "even(x2,h1,h2,h3)",
        "even(y1,y3,s1)", "odd(k1,k2,k3)", "even(y2,k1,k2,k3)",
    )))
    items = [(f"eleven {'-'.join(a)}/{'-'.join(b)}", "eleven", (), (a, b), {"only": ()})
             for a, b in product(options_first, options_second)]
    items += [(name, name, growth if name == "smallest gain" else (), DEFAULT_OPTIONS, {"only": ()})
              for name in ("smallest gain", "seven", "eight", "nine", "eighteen")]
    round_counts = {}
    for name, third_own, source_label in (("ten A", "y2", "ten A: eleven less even(y2,k1,k2) (start)"),
                                         ("ten B", "y3", "ten B: eleven less odd(y3,k1,k2) (start)")):
        sources[name] = structures[source_label]
        second_option, round_counts[name] = ten_choices(sources[name], third_own)
        variants = {f"third birth takes {take}": (setting_rule(third_own, take, "f3"),)
                    for take in ("t", second_option)}
        items += [(f"{name} {'-'.join(a)}/{second_option}-t", name, (), (a, (second_option, "t")), variants)
                  for a in options_first]
    items.append(("eight-thirds case", "eight-thirds case", (), DEFAULT_OPTIONS, {"only": ()}))
    reported_items = {row["result"]["name"]: row["result"] for row in reported["items"]}
    assert {row[0] for row in items} == reported_items.keys()
    for label, name, before, options, variants in items[:limit]:
        selected = {}
        raw_variants = []
        target = reported_items[label]
        run_variants = {variant["label"]: variant for variant in target["variants"]}
        assert run_variants.keys() == variants.keys()
        for variant, extra in variants.items():
            measured, raw, old_counts = history(sources[name], before, options, extra, shared=name == "eleven")
            compare_history([label, variant], measured, run_variants[variant], differences)
            compare_finished([label, variant], finished_rules(sources[name], before, options, extra),
                             run_variants[variant]["finished"], differences)
            if name == "eleven":
                for stage in (START, FINISH):
                    marginal = run_variants[variant]["info"]["marginals"][f"(s1,s2) {stage}"]
                    if marginal != measured["shared record"][stage]:
                        differences.append([label, stage, "(s1,s2)", measured["shared record"][stage], marginal])
            selected[variant] = measured
            raw_variants.append(raw)
            if options == DEFAULT_OPTIONS and name in {"eleven", "eighteen"}:
                raw_keyed[name] = (raw, np.flatnonzero(old_counts.sum(axis=1)).tolist())
        named_rows[label] = {"variants": selected}
        if name.startswith("ten "):
            pooling = {POOLED_START: score(pooled(raw_variants, START, True)),
                       POOLED_FINISH: score(pooled(raw_variants, FINISH, False)),
                       POOLED_UNIFORM: score(pooled(raw_variants, FINISH, True))}
            for mode, result in pooling.items():
                if result != target["pooled"][mode]:
                    differences.append([label, mode, result, target["pooled"][mode]])
            named_rows[label]["pooled"] = pooling
    keyed_counts = {}
    for target in reported["keyed"]:
        name = target["structure"]
        if name not in raw_keyed:
            continue
        raw, patterns = raw_keyed[name]
        measured = keyed(raw, patterns, 16 if name == "eleven" else 256)
        check_keyed(target, name, measured, differences)
        keyed_counts[name] = measured
    return {"rows": named_rows, "ten rule round-one choices": round_counts,
            "keyed": keyed_counts, "differences": differences}


def archives():
    for source, epic, pattern in (
        ("rule Q", "ONE-PARENT-REREAD-20261123-001A", "*/census_gains_c_*.jsonl.gz"),
        ("rule R", "REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C", "*/arm1_gains_three_*.jsonl.gz"),
    ):
        index = 0
        for path in sorted((ARTIFACTS / epic).glob(pattern)):
            with gzip.open(path, "rt") as archive:
                for line in archive:
                    row = json.loads(line)
                    if source == "rule R" or row["t"] == 1:
                        yield source, index, path.name, row
                    index += 1


def group_archives(reported, limit):
    rows = []
    differences = []
    read = Counter()
    reported_rows = defaultdict(deque)
    for result in reported["records"]:
        meta = result["record"]
        recorded_rules = tuple(map(rule, result["variants"][0]["finished"]["(0, 0)"][:-2]))
        key = (meta["source"], meta["si"], meta["tid"], meta["kind"], recorded_rules)
        reported_rows[key].append(result)
    for line, index, path, original in archives():
        if limit is not None and read[line] >= limit:
            continue
        read[line] += 1
        source_label = (f"ONE-PARENT-REREAD {original['arm']}" if line == "rule Q" else "REREAD-BIRTHS rule R")
        source_and_round = tuple(map(rule, original["knots"]))
        assert original["t"] == len(original["births"]) == 1
        split = len(source_and_round) - len(original["births"][0])
        source, before = source_and_round[:split], source_and_round[split:]
        measured, _, old_counts = history(source, before)
        key = (source_label, original["si"], original["tid"], original["kind"], source_and_round)
        result = reported_rows[key].popleft()
        compare_history([line, index], measured, result["variants"][0], differences)
        compare_finished([line, index], finished_rules(source, before, DEFAULT_OPTIONS),
                         result["variants"][0]["finished"], differences)
        finish = measured["rows"][FINISH]
        recorded_score = original["eval"][-1]
        assert result["record"]["eval"] == original["eval"]
        if finish["score_all"] != recorded_score or finish["hidden"] != original["eval"][0]:
            differences.append([line, index, "archived finish", finish, original["eval"]])
        recorded_table = np.array(original["table"], dtype=np.int64).reshape(8, 8)
        reversed_bits = [int(f"{i:03b}"[::-1], 2) for i in range(8)]
        table_agrees = bool(np.array_equal(old_counts, recorded_table))
        agrees_bit_reversed = bool(np.array_equal(old_counts, recorded_table[np.ix_(reversed_bits, reversed_bits)]))
        if not agrees_bit_reversed:
            differences.append([line, index, "archived old six-distinction table"])
        rows.append({"line": line, "archive index": index, "archive file": path, "arm": original.get("arm"),
                     "study record index": result["record"]["index"],
                     "part": original["tid"], "source position": original["pos"], "recorded score": recorded_score,
                     "old table (low bit first) agrees": table_agrees,
                     "old table (high bit first) agrees": agrees_bit_reversed, **measured})
    if limit is None:
        assert len(rows) == len(reported["records"]) == 894 and not any(reported_rows.values())
    return {"rows": rows, "differences": differences}


def group_signs(structures, reported, limit):
    start = structures["eleven (start)"]
    rows = []
    differences = []
    for index, target in enumerate(reported["rows"][:limit]):
        assert index == target["index"]
        signs_at_index = iter("odd" if index & (1 << i) else "even" for i in range(9))
        changed = tuple((next(signs_at_index) if kind != "nae" else kind, places) for kind, places in start)
        bits, states = allowed(changed)
        ties = {}
        for p, q in (("x2", "x3"), ("y2", "y3")):
            values = {bool(state & bits[p]) != bool(state & bits[q]) for state in states}
            assert len(values) == 1
            ties[f"tie {p},{q}"] = "inequality" if values == {True} else "equality"
        measured, _, _ = history(changed)
        for label, value in {"start allowed": measured["source states"],
                             "allowed at the finish": measured["states at the finish"], **ties}.items():
            if value != target[label]:
                differences.append([index, label, value, target[label]])
        for stage in (START, FINISH):
            for field, value in measured["rows"][stage].items():
                if value != target[stage][field]:
                    differences.append([index, stage, field, value, target[stage][field]])
        rows.append({"index": index, **ties, **measured})
    both = {row["index"] for row in rows if row["tie x2,x3"] == row["tie y2,y3"] == "inequality"}
    excess = {row["index"] for row in rows if row["rows"][FINISH]["score_all"] == "20/9" and row["rows"][FINISH]["hidden"]}
    return {"rows": rows, "differences": differences, "tie indices equal hidden 20/9 indices": both == excess,
            "both inequalities": len(both), "hidden at 20/9": len(excess)}


def brute_force(rules):
    names = rule_names(rules)
    place = {name: i for i, name in enumerate(names)}
    states = np.arange(1 << len(names), dtype=np.int64)
    for kind, held in rules:
        values = sum((states >> place[name]) & 1 for name in held)
        if kind == "nae":
            states = states[(values != 0) & (values != len(held))]
        else:
            states = states[values % 2 == (kind == "odd")]
    return tuple(map(int, states))


def direct_matrices(source, before):
    # Enumerate the full state sets and recover all transition multiplicities by projection.
    # This gate uses neither the private-fresh product nor the local-record reduction.
    rows = {stage: [] for stage in (START, FINISH, MIXED_FIRST, MIXED_SECOND)}
    if before:
        rows[STAGE] = []
    for a, b in SETTINGS:
        first = setting_rule("x1", DEFAULT_OPTIONS[0][a], "za")
        second = setting_rule("y1", DEFAULT_OPTIONS[1][b], "zb")
        complete = source + before + (first, second)
        names = rule_names(complete)
        bits = {name: 1 << i for i, name in enumerate(names)}
        states = brute_force(complete)
        record_a = [encoded(state, FIRST + ("za",), bits) for state in states]
        record_b = [encoded(state, SECOND + ("zb",), bits) for state in states]
        start_mask, prior_mask = (sum(bits[n] for n in rule_names(rules)) for rules in (source, source + before))
        pre_completions = Counter(value & prior_mask for value in states)
        intermediate_completions = Counter(value & start_mask for value in pre_completions)
        start_states = brute_force(source)
        round_states = brute_force(source + before)
        assert set(intermediate_completions) == {sum(bits[n] for i, n in enumerate(rule_names(source)) if s & (1 << i))
                                                for s in start_states}
        assert set(pre_completions) == {sum(bits[n] for i, n in enumerate(rule_names(source + before)) if s & (1 << i))
                                        for s in round_states}
        first_mask = prior_mask | bits["za"]
        second_mask = prior_mask | bits["zb"]
        first_completions = Counter(value & first_mask for value in states)
        second_completions = Counter(value & second_mask for value in states)
        start_denoms = [intermediate_completions[s & start_mask] * pre_completions[s & prior_mask] for s in states]
        stage_denoms = {START: start_denoms, FINISH: [1] * len(states),
                        MIXED_FIRST: [first_completions[s & first_mask] for s in states],
                        MIXED_SECOND: [second_completions[s & second_mask] for s in states]}
        if before:
            stage_denoms[STAGE] = [pre_completions[s & prior_mask] for s in states]
        for mode, values in stage_denoms.items():
            scale = lcm(*values)
            matrix = np.zeros((16, 16), dtype=np.int64)
            for u, v, denominator in zip(record_a, record_b, values):
                matrix[u, v] += scale // denominator
            rows[mode].append(matrix)
    return {mode: np.array(tables).reshape(2, 2, 16, 16) for mode, tables in rows.items()}


def literal_parity(tables):
    corr = (PARITIES @ tables @ PARITIES.T).tolist()
    signed = -2**63
    absolute = 0
    for a0, a1, b0, b1 in product(range(15), repeat=4):
        terms = [corr[0][0][a0][b0], corr[0][1][a0][b1], corr[1][0][a1][b0], corr[1][1][a1][b1]]
        total = sum(terms)
        signed = max(signed, total - 2 * min(terms))
        absolute = max(absolute, signed, 2 * max(terms) - total)
    return signed, absolute


def literal_binary_functions(tables):
    # Directly enumerate all four functions for the small arbitrary gate tables.
    functions = list(product((-1, 1), repeat=tables.shape[2]))
    return max(sum(((-1 if (a, b) == (1, 1) else 1) * int(tables[a, b, u, v]) * fs[a][u] * fs[2 + b][v])
                   for a, b in SETTINGS for u, v in product(range(tables.shape[2]), repeat=2))
               for fs in product(functions, repeat=4))


def group_gates(structures, reported, limit):
    gates = []
    targets = [(label, rules) for label, rules in structures.items() if label.startswith(("eleven", "smallest gain"))]
    for label, rules in targets[:limit]:
        actual = allowed(rules)[1]
        expected = brute_force(rules)
        assert expected == actual
        gates.append({"allowed-set equality": label, "states": len(actual)})
    matrix_targets = (("eleven", "eleven (start)", None),
                      ("smallest gain", "smallest gain: part", "smallest gain: part + rule-Q round 1"))
    for label, start_label, before_label in matrix_targets[:limit]:
        source = structures[start_label]
        before = structures[before_label][len(source):] if before_label else ()
        direct = direct_matrices(source, before)
        raw, _, _, _ = build_tables(source, before)
        assert direct.keys() == raw.keys()
        for mode, direct_tables in direct.items():
            direct_normalized, direct_denominator = normalized(direct_tables)
            computed, computed_denominator = normalized(raw[mode])
            assert computed_denominator == direct_denominator and np.array_equal(computed, direct_normalized)
            gates.append({"exact joint table equality": label, "weighting": mode, "setting pairs": 4})
            if mode in (START, FINISH):
                assert best_all(computed) == best_all(coarsen(computed))
                assert literal_parity(computed) == best_parity(computed)
                gates.append({"complete versus old record functions and literal parity choices": label, "weighting": mode})
        for a, b in SETTINGS:
            name = f"eleven + settings {a}{b}" if not before else f"smallest gain finished {a}{b}"
            assert finished_rules(source, before, DEFAULT_OPTIONS)[a, b] == structures[name]
            gates.append({"frozen finished rules match constructed rules": name})
    random = Random(20261126)
    n_tests = 60 if limit is None else min(limit, 60)
    for test in range(n_tests):
        n = 1 if test % 5 == 0 else 2
        raw = np.array([random.randrange(5) for _ in range(4 * n * n)], dtype=np.int64).reshape(2, 2, n, n)
        raw[:, :, 0, 0] += 1  # Keep every setting distribution defined.
        tables, _ = normalized(raw)
        assert literal_binary_functions(tables) == best_all(tables)
    return {"gates": gates, "independent small arbitrary table checks": n_tests,
            "small arbitrary table seed": 20261126, "recorded gate rows": len(reported["checks"]),
            "reported failures": reported["failed"]}


def summary(group, result):
    def tally(rows):
        counts = Counter((stage, cell["score_all"], cell["hidden"]) for row in rows for stage, cell in row["rows"].items())
        return [{"counting": stage, "score": score, "hidden": hidden, "count": value}
                for (stage, score, hidden), value in sorted(counts.items())]

    if group == "items":
        variants = [variant for item in result["rows"].values() for variant in item["variants"].values()]
        pools = [{"rows": item["pooled"]} for item in result["rows"].values() if "pooled" in item]
        return {"named histories": len(variants), "rows": tally(variants + pools),
                "common-stage rows": sum(sum(stage in (START, STAGE) for stage in r["rows"]) for r in variants),
                "pooled variants": len(pools)}
    if group == "archives":
        out = {}
        for line, arm in (("rule Q", "uniform"), ("rule Q", "mixed"), ("rule R", None)):
            rows = [row for row in result["rows"] if row["line"] == line and row["arm"] == arm]
            label = line if arm is None else f"{line} {arm}"
            out[label] = {"records": len(rows), "part identifiers": len({(row["part"], row["source position"]) for row in rows}),
                          "counts": tally(rows),
                          "matches archived absolute parities": sum(row["rows"][FINISH]["score_parity_abs"] == row["recorded score"] for row in rows),
                          "matches archived signed parities": sum(row["rows"][FINISH]["score_parity"] == row["recorded score"] for row in rows),
                          "old table (low bit first) matches": sum(row["old table (low bit first) agrees"] for row in rows),
                          "old table (high bit first) matches": sum(row["old table (high bit first) agrees"] for row in rows)}
        return out
    if group == "signs":
        return tally(result["rows"])
    return {"checks listed": len(result["gates"]), "arbitrary tables": result["independent small arbitrary table checks"]}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("group", choices=("gates", "items", "archives", "signs"))
    cli.add_argument("--limit", type=int, help="rehearsal prefix per input group")
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    started = perf_counter()
    structures = frozen_structures()
    if args.group == "gates":
        result = group_gates(structures, read_json(STUDY / "part1_gates.json"), args.limit)
    elif args.group == "items":
        result = group_items(structures, read_json(STUDY / "part2_lemma.json"), args.limit)
    elif args.group == "archives":
        result = group_archives(read_json(STUDY / "part2_lemma.json"), args.limit)
    else:
        result = group_signs(structures, read_json(STUDY / "part3_signs.json"), args.limit)
    result["summary"] = summary(args.group, result)
    result["wall seconds"] = round(perf_counter() - started, 4)
    result["peak resident KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result["virtual memory ceiling bytes"] = resource.getrlimit(resource.RLIMIT_AS)[0]
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in {"gates", "rows", "keyed"}}, indent=2))


if __name__ == "__main__":
    main()
