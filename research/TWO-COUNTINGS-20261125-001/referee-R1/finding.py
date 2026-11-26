"""Recount allowed states and every rule's relation for the finding and part 8."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
import gzip
from itertools import combinations, product
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
TICKET = "TWO-COUNTINGS-20261125-001A"
RAW = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_two_countings"
REGISTERED = ROOT / "research" / TICKET / "structures.json"
HERE = Path(__file__).parent
SETTINGS = tuple(product(range(2), repeat=2))


@dataclass(frozen=True)
class Rule:
    law: str
    places: tuple[str, ...]

    def __str__(self):
        return f"{self.law}({','.join(self.places)})"


@dataclass(frozen=True)
class Factor:
    places: tuple[str, ...]
    values: np.ndarray


@dataclass(frozen=True)
class Verdict:
    allowed: tuple[str, ...]
    own: tuple[str, ...]
    gates: tuple[bool, bool, bool]

    @property
    def knot(self):
        return all(self.gates)


@cache
def parse_rule(text):
    law, group = text.removesuffix(")").split("(")
    places = tuple(group.split(","))
    assert law in ("even", "odd", "nae") and len(set(places)) == len(places), text
    return Rule(law, places)


def load(path):
    return json.loads(path.read_text())


def rules(texts):
    return tuple(map(parse_rule, texts))


def structure_key(structure):
    # Parity and not-all-equal are symmetric in their places. Names are kept.
    return frozenset((rule.law, tuple(sorted(rule.places))) for rule in structure)


def namespaces(structure):
    return tuple(sorted(set().union(*(rule.places for rule in structure))))


@cache
def own_relation(law, width):
    allowed = []
    for row in product((0, 1), repeat=width):
        count = sum(row)
        holds = 0 < count < width if law == "nae" else count % 2 == (law == "odd")
        if holds:
            allowed.append("".join(map(str, row)))
    return tuple(allowed)


def gates(relation, width):
    return (
        len(relation) < 2**width,
        all(
            len({state[:j] + state[j + 1:] for state in relation}) == 2 ** (width - 1)
            for j in range(width)
        ),
        bool(relation),
    )


@cache
def rule_factor(rule):
    width = len(rule.places)
    table = np.zeros((2,) * width, dtype=np.int64)
    for row in own_relation(rule.law, width):
        table[tuple(map(int, row))] = 1
    return Factor(tuple(sorted(rule.places)), table)


def factor_product(factors, domain):
    value = np.ones((2,) * len(domain), dtype=np.int64)
    for factor in factors:
        value *= factor.values.reshape(tuple(2 if v in factor.places else 1 for v in domain))
    return Factor(domain, value)


def retain(factor, places):
    removed = tuple(j for j, v in enumerate(factor.places) if v not in places)
    return Factor(tuple(v for v in factor.places if v in places), factor.values.sum(axis=removed))


def supported(factor, places):
    axis_order = tuple(factor.places.index(v) for v in places)
    return tuple(
        "".join(map(str, row))
        for row in zip(*np.nonzero(factor.values.transpose(axis_order)))
    )


def elimination_order(factors):
    active = {frozenset(f.places) for f in factors}
    while active:
        merged = defaultdict(set)
        for group in active:
            for place in group:
                merged[place].update(group)
        place = min(merged, key=lambda v: (len(merged[v]), v))
        yield place
        active = {group for group in active if place not in group}
        if len(merged[place]) > 1:
            active.add(frozenset(merged[place] - {place}))


def analyze(structure, queries=()):
    """Count and marginalize using exact integer products and sums."""
    factors = [rule_factor(rule) for rule in structure]
    factors.extend(
        Factor(tuple(sorted(query)), np.ones((2,) * len(query), dtype=np.int64))
        for query in queries
    )
    order = tuple(elimination_order(factors))
    assert len(order) < 63, "The counts must fit in signed 64-bit integers"
    position = {v: j for j, v in enumerate(order)}
    inputs = defaultdict(list)
    for index, factor in enumerate(factors):
        inputs[min(factor.places, key=position.__getitem__)].append(index)

    children = defaultdict(list)
    upward = {}
    bucket = {}
    roots = []
    for place in order:
        terms = [factors[j] for j in inputs[place]]
        terms.extend(upward[child] for child in children[place])
        domain = tuple(sorted(set().union(*(factor.places for factor in terms))))
        joint = factor_product(terms, domain)
        remaining = tuple(v for v in domain if v != place)
        message = retain(joint, remaining)
        bucket[place] = joint
        upward[place] = message
        if remaining:
            children[min(remaining, key=position.__getitem__)].append(place)
        else:
            roots.append(place)

    root_count = {root: int(upward[root].values) for root in roots}
    total = math.prod(root_count.values())
    downward = {
        root: Factor((), np.array(math.prod(value for v, value in root_count.items() if v != root)))
        for root in roots
    }
    result = {}
    for place in reversed(order):
        joint = bucket[place]
        if inputs[place]:
            full = factor_product((joint, downward[place]), joint.places)
            for index in inputs[place]:
                factor = retain(full, factors[index].places)
                assert int(factor.values.sum()) == total
                result[index] = factor
        if children[place]:
            local = [downward[place], *(factors[index] for index in inputs[place])]
            for child in children[place]:
                others = [upward[sibling] for sibling in children[place] if sibling != child]
                without_child = factor_product([*local, *others], joint.places)
                downward[child] = retain(without_child, upward[child].places)

    verdicts = {}
    for j, rule in enumerate(structure):
        allowed = supported(result[j], rule.places)
        own = own_relation(rule.law, len(rule.places))
        assert set(allowed) <= set(own)
        verdicts[rule] = Verdict(allowed, own, gates(allowed, len(rule.places)))
    query_relations = {
        query: supported(result[len(structure) + j], query)
        for j, query in enumerate(queries)
    }
    return total, verdicts, query_relations


def exhaustive(structure):
    """Finite control on supplied small examples by direct substitution."""
    names = namespaces(structure)
    scoped = {rule: [names.index(v) for v in rule.places] for rule in structure}
    own = {rule: set(own_relation(rule.law, len(rule.places))) for rule in structure}
    observed = {rule: set() for rule in structure}
    count = 0
    for row in product("01", repeat=len(names)):
        projections = {rule: "".join(row[j] for j in scoped[rule]) for rule in structure}
        if all(marginal in own[rule] for rule, marginal in projections.items()):
            count += 1
            for rule, marginal in projections.items():
                observed[rule].add(marginal)
    return count, {rule: tuple(sorted(allowed)) for rule, allowed in observed.items()}


def failure_rows(verdicts):
    return [
        {"rule": str(rule), "induced": verdict.allowed, "K1/K2/K3": verdict.gates,
         "isolated rule passes": all(gates(verdict.own, len(rule.places)))}
        for rule, verdict in verdicts.items()
        if not verdict.knot
    ]


def setting_rules(a, b):
    return (
        Rule("nae", ("x1", ("x2", "x3")[a], "za")),
        Rule("nae", ("y1", ("y2", "y3")[b], "zb")),
    )


def saved_verdicts(row, structure, count, verdicts):
    assert row["n_states"] == count, row["labels"]
    assert row["n_knots"] == len(structure) == len(row["knots"])
    assert row["n_distinctions"] == len(namespaces(structure))
    for entry, rule in zip(row["knots"], structure, strict=True):
        assert entry["knot"] == str(rule)
        verdict = verdicts[rule]
        own_gates = gates(verdict.own, len(rule.places))
        assert tuple(entry["induced"]) == verdict.allowed, (row["labels"], rule)
        assert tuple(entry[f"K{j}"] for j in range(1, 4)) == verdict.gates
        assert entry["whole"] == verdict.knot and entry["own"] == all(own_gates)
        canonical = entry.get("canonical")
        if isinstance(canonical, dict):
            assert tuple(canonical[f"K{j}"] for j in range(1, 4)) == verdict.gates
            assert canonical["knot"] == verdict.knot and canonical["agrees with projection"]


def archived_rows(ticket, pattern):
    paths = sorted((ROOT / "artifacts" / ticket).glob(pattern))
    assert paths
    for path in paths:
        with gzip.open(path, "rt") as stream:
            for line in stream:
                row = json.loads(line)
                if row["t"] == 1:
                    yield row


def start_and_round(row):
    assert row["t"] == len(row["births"]) == 1 and row["births"][0]
    after_round = rules(row["knots"])
    return after_round[:-len(row["births"][0])], after_round


def input_roster(registered):
    """Reconstruct part 8's rule-set roster and build-ordered canonical candidates."""
    part2 = load(RAW / "part2_lemma.json")
    part4 = load(RAW / "part4_examples.json")
    references = defaultdict(list)
    candidates = {}

    def add(label, structure, candidate=False):
        key = structure_key(structure)
        references[key].append(label)
        if candidate:
            candidates.setdefault(key, label)

    for label, structure in registered.items():
        add(f"structures.json: {label}", structure, True)

    items_by_name = {item["result"]["name"]: item["result"] for item in part2["items"]}
    ten_finish = []
    eleven_finish = []
    for name, item in items_by_name.items():
        for variant in item["variants"]:
            for setting, texts in variant["finished"].items():
                structure = rules(texts)
                add(f"part 2: {name} | {variant['label']} | {setting}", structure, True)
                if name.startswith("ten "):
                    ten_finish.append(structure)
                if name.startswith("eleven "):
                    eleven_finish.append(structure)

    q_rows = list(archived_rows(
        "ONE-PARENT-REREAD-20261123-001A", "*/census_gains_c_*.jsonl.gz"
    ))
    r_rows = list(archived_rows(
        "REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C", "*/arm1_gains_three_*.jsonl.gz"
    ))
    histories = []
    roster_seen = set()
    for item in part2["records"]:
        info = item["record"]
        source = info["source"]
        index = info["index"]
        archive = r_rows if source.startswith("REREAD-BIRTHS") else q_rows
        family = "rule R" if archive is r_rows else source.rsplit(" ", 1)[-1]
        row = archive[index]
        assert all(info[key] == row[key] for key in ("tid", "si", "t", "kind", "eval"))
        assert archive is r_rows or row["arm"] == family
        assert (family, index) not in roster_seen
        roster_seen.add((family, index))
        start, after_round = start_and_round(row)
        name = item["name"]
        assert len(item["variants"]) == 1
        variant = item["variants"][0]
        finishes = []
        for a, b in SETTINGS:
            actual = rules(variant["finished"][str((a, b))])
            expected = after_round + setting_rules(a, b)
            assert structure_key(actual) == structure_key(expected), (family, index, a, b)
            add(f"part 2: {name} | {(a, b)}", expected, True)
            finishes.append(expected)
        add(f"part 2 (the start): {name}", start)
        add(f"part 2 (the stage after the round): {name}", after_round)
        histories.append((family, index, row, start, after_round, tuple(finishes)))

    assert roster_seen == (
        {(row["arm"], j) for j, row in enumerate(q_rows)}
        | {("rule R", j) for j in range(len(r_rows))}
    )
    eight_thirds = rules([
        "odd(x1,x3,s1)", "odd(h1,h2,h3)", "even(x2,h1,h2,h3)",
        "even(y1,y3,s1)", "odd(k1,k2,k3)", "even(y2,k1,k2,k3)",
    ])
    eight_thirds_finish = tuple(eight_thirds + setting_rules(a, b) for a, b in SETTINGS)
    assert {
        structure_key(rules(finish))
        for finish in items_by_name["eight-thirds case"]["variants"][0]["finished"].values()
    } == set(map(structure_key, eight_thirds_finish))
    add("part 2 (the start): the 8/3 case", eight_thirds)

    eleven_start = registered["eleven (start)"]
    for row in part4["examples"]:
        example = row["example"]
        for a, b in SETTINGS:
            left, right = setting_rules(a, b)
            if example == "E3":
                left = Rule(left.law, (*left.places[:-1], "s1"))
            elif example == "E4":
                left = Rule(left.law, (*left.places[:-1], "z"))
                right = Rule(right.law, (*right.places[:-1], "z"))
            later = {
                "E5": (Rule("even", ("za", "zb", "x1")),),
                "E7": (Rule("even", ("zb", "w", "x1")),),
            }.get(example, ())
            setting = str((a, b))
            finish = eleven_start + (left, right) + later
            if example == "E2":
                assert structure_key(finish) in references
            else:
                raw_finish = row["all rows"]["variants"][0]["finished"][setting]
                assert structure_key(finish) == structure_key(rules(raw_finish))
                add(f"part 4: {example} | {setting}", finish)

    return references, candidates, histories, ten_finish, eleven_finish


def independently_make_ten_finishes(registered):
    for label, start in registered.items():
        if not label.startswith("ten "):
            continue
        holders = Counter(v for rule in start for v in rule.places)
        y_parent = next(rule for rule in start if "y1" in rule.places)
        third = next(v for v in y_parent.places if v != "y1" and holders[v] == 1)
        x_parent = next(rule for rule in start if "x1" in rule.places)
        x_options = tuple(v for v in x_parent.places if holders[v] > 1)
        y_options = tuple(v for v in y_parent.places if holders[v] > 1)
        for option_x, option_y, option_third in product(x_options, y_options, y_options):
            yield start + (
                Rule("nae", ("x1", option_x, "za")),
                Rule("nae", ("y1", option_y, "zb")),
                Rule("nae", (third, option_third, "f3")),
            )


def canonical_status(row):
    kinds = {
        "checked" if isinstance(entry["canonical"], dict) else entry["canonical"]
        for entry in row["knots"]
    }
    assert len(kinds) == 1
    (status,) = kinds
    return {
        "canonical check not run (cut)": "cut",
        "not run (more than 20 distinctions; projection only, as registered)": "over width",
        "not registered for the canonical command (projection only)": "not registered",
        "checked": "checked",
    }[status]


def check_history(records, statuses, computed):
    grouped = defaultdict(lambda: {
        "histories": 0, "histories with failures": 0, "histories all pass": 0,
        "failing parts": Counter(), "failing rules": Counter(),
        "histories all pass by archived finish score": Counter(),
        "all-pass histories with canonical finishes": Counter(),
    })
    witnesses = []
    by_size_and_score = defaultdict(Counter)
    first_at_size = {}
    starts = defaultdict(dict)
    rounds = defaultdict(dict)
    for family, index, row, start, after_round, finishes in records:
        label = grouped[family]
        label["histories"] += 1
        starts[family][structure_key(start)] = len(namespaces(start))
        rounds[family][structure_key(after_round)] = len(namespaces(after_round))
        all_structures = (start, after_round, *finishes)
        recounted = [computed[structure_key(structure)] for structure in all_structures]
        failures = [failure_rows(verdicts) for _, verdicts in recounted]
        if any(failures):
            label["histories with failures"] += 1
            label["failing parts"][str(row["tid"])] += 1
            label["failing rules"].update(
                failure["rule"] for group in failures for failure in group
            )
            if family == "rule R":
                assert all(len(group) == 3 and group == failures[0] for group in failures)
            else:
                assert [len(group) for group in failures] == [0, 0, 1, 1, 0, 0]
                assert all(group[0]["rule"] == "nae(x1,x2,za)" for group in failures if group)
        else:
            label["histories all pass"] += 1
            label["histories all pass by archived finish score"][row["eval"][3]] += 1
            rank = len(after_round), len(namespaces(after_round)), Fraction(row["eval"][3])
            by_size_and_score[family][rank] += 1
            first_at_size.setdefault((family, rank), {
                "part": row["tid"], "archive index": index,
                "round-1 choice": row["choice"], "laws": row.get("laws", row.get("newborn_laws")),
            })
            checked = sum(statuses[structure_key(finish)] == "checked" for finish in finishes)
            label["all-pass histories with canonical finishes"][checked] += 1

        if family == "uniform" and row["tid"] in (113, 143):
            assert not any(failures)
            queries = tuple(combinations(("x1", "x2", "x3"), 2))
            _, _, pair_relations = analyze(start, queries)
            assert all(len(relation) == 4 for relation in pair_relations.values())
            witnesses.append({
                "part": row["tid"], "round-1 choice": row["choice"], "archive index": index,
                "archived finish score": row["eval"][3],
                "rule counts": [len(ruleset) for ruleset in all_structures],
                "distinction counts": [len(namespaces(ruleset)) for ruleset in all_structures],
                "allowed state counts": [count for count, _ in recounted],
                "first observer's pair relations at the start": {
                    " ".join(pair): relation for pair, relation in pair_relations.items()
                },
                "rule relations at the start": {
                    str(rule): verdict.allowed for rule, verdict in recounted[0][1].items()
                },
                "rule relations after the round": {
                    str(rule): verdict.allowed for rule, verdict in recounted[1][1].items()
                },
                "rule relations in the four finishes": {
                    str(setting): {str(rule): verdict.allowed for rule, verdict in verdicts.items()}
                    for setting, (_, verdicts) in zip(SETTINGS, recounted[2:], strict=True)
                },
            })
    for family, history_counts in grouped.items():
        rank = min(by_size_and_score[family])
        history_counts["minimum passing history in archived round-1 population"] = {
            "rules after round": rank[0], "distinctions after round": rank[1],
            "archived finish score": str(rank[2]), "histories": by_size_and_score[family][rank],
            "example": first_at_size[family, rank],
        }
        history_counts["distinct named starts by width"] = Counter(starts[family].values())
        history_counts["distinct named stages after the round by width"] = Counter(rounds[family].values())
    return grouped, witnesses


def aggregate_finishes(finishes, computed):
    fails = Counter()
    present = Counter()
    distinct_fails = defaultdict(set)
    distinct_present = defaultdict(set)
    for structure in finishes:
        key = structure_key(structure)
        _, verdicts = computed[key]
        for rule, verdict in verdicts.items():
            present[str(rule)] += 1
            distinct_present[str(rule)].add(key)
            if not verdict.knot:
                fails[str(rule)] += 1
                distinct_fails[str(rule)].add(key)
    return {
        "finish occurrences": len(finishes),
        "distinct named rule sets": len({structure_key(s) for s in finishes}),
        "rules": {
            rule: {"occurrences": present[rule], "failures": fails[rule],
                   "distinct structures": len(distinct_present[rule]),
                   "failing distinct structures": len(distinct_fails[rule])}
            for rule in sorted(present)
        },
    }


def part8_recount(registered, raw, cases):
    references, candidates, histories, ten_finish, eleven_finish = input_roster(registered)
    rows = {}
    statuses = {}
    computed = {}
    counts = Counter()
    status_counts = defaultdict(Counter)
    failure_classes = Counter()
    for raw_row in raw["structures"]:
        structure = rules(raw_row["structure"])
        key = structure_key(structure)
        assert key not in rows and Counter(raw_row["labels"]) == Counter(references[key])
        rows[key] = raw_row
        status = canonical_status(raw_row)
        statuses[key] = status
        count, verdicts, _ = analyze(structure)
        saved_verdicts(raw_row, structure, count, verdicts)
        computed[key] = (count, verdicts)
        failures = failure_rows(verdicts)
        counts.update({
            "structures": 1, "rule verdicts": len(verdicts),
            "failing structures": int(bool(failures)), "failures": len(failures),
            "isolated rule failures": sum(
                not all(gates(verdict.own, len(rule.places))) for rule, verdict in verdicts.items()
            ),
            "passing rules with stricter induced relation": sum(
                verdict.knot and verdict.allowed != verdict.own for verdict in verdicts.values()
            ),
        })
        status_counts[status].update({
            "structures": 1, "rule verdicts": len(verdicts), "candidates": int(key in candidates),
            "failing structures": int(bool(failures)), "failures": len(failures),
        })
        for failure in failures:
            failure_classes[(
                failure["rule"], " ".join(failure["induced"]), failure["K1/K2/K3"]
            )] += 1

    assert set(rows) == set(references)
    eligible = [key for key in candidates if rows[key]["n_distinctions"] <= 20]
    eligible_done = sum(statuses[key] == "checked" for key in eligible)
    assert all(statuses[key] == "checked" for key in eligible[:eligible_done])
    assert all(statuses[key] == "cut" for key in eligible[eligible_done:])
    assert len(candidates) == raw["canonical candidates (registered order)"]
    assert status_counts["cut"]["structures"] == raw["canonical structures cut"]
    assert status_counts["checked"]["rule verdicts"] == raw["canonical knots checked (this run)"]
    assert counts["structures"] == raw["unique structures"]

    early = load(RAW / "part8_early_knots.json")
    early_keys = set()
    for early_row in early["structures"]:
        structure = rules(early_row["structure"])
        key = structure_key(structure)
        early_row["labels"] = [early_row["label"]]
        saved_verdicts(early_row, structure, *computed[key])
        assert statuses[key] == "checked"
        early_keys.add(key)
    early_count = sum(len(rows[key]["knots"]) for key in early_keys)
    assert early_count == early["knots checked"] == raw["canonical knots checked early"]

    registered_rows = []
    for label, structure in registered.items():
        key = structure_key(structure)
        count, verdicts = computed[key]
        registered_rows.append({
            "structure": label, "rules": len(structure), "distinctions": len(namespaces(structure)),
            "allowed states": count, "canonical status in the run": statuses[key],
            "failures": failure_rows(verdicts),
        })
    finding = load(RAW / "part8_finding_check.json")
    for original, recount in zip(finding["per structure"], registered_rows, strict=True):
        assert original["structure"] == recount["structure"]
        assert original["knots"] == recount["rules"] and original["distinctions"] == recount["distinctions"]
        assert original["fail in the whole (projection)"] == [v["rule"] for v in recount["failures"]]
    registered_summary = defaultdict(Counter)
    for entry in registered_rows:
        registered_summary[entry["canonical status in the run"]].update({
            "structures": 1, "rule verdicts": entry["rules"], "failures": len(entry["failures"]),
        })
    assert registered_summary["checked"]["rule verdicts"] == finding["canonical knots of the 33 (at most 20 distinctions)"]
    assert registered_summary["over width"]["rule verdicts"] == finding["knots of the 33 by projection only"]

    reconstructed_ten = set(map(structure_key, independently_make_ten_finishes(registered)))
    assert reconstructed_ten == set(map(structure_key, ten_finish))
    history_counts, witnesses = check_history(histories, statuses, computed)
    redundancy = []
    for label, structure in registered.items():
        if label in ("smallest gain finished 00", "smallest gain finished 01"):
            setting = Rule("nae", ("x1", "x2", "za"))
            without_setting = tuple(rule for rule in structure if rule != setting)
            count, _, free_setting = analyze(without_setting, (setting.places,))
            original_count, verdicts = computed[structure_key(structure)]
            assert count == original_count and free_setting[setting.places] == verdicts[setting].allowed
            redundancy.append({"structure": label, "with rule": original_count,
                               "without rule with za kept": count, "relation": verdicts[setting].allowed})

    for label, structure in cases:
        count, relations = exhaustive(structure)
        exact_count, exact_verdicts = computed[structure_key(structure)]
        assert count == exact_count and all(
            relations[rule] == exact_verdicts[rule].allowed for rule in structure
        ), label

    return {
        "registered structures": registered_rows,
        "registered totals by canonical status": registered_summary,
        "totals": counts,
        "canonical candidates": len(candidates),
        "canonical eligible at width 20 or less": len(eligible),
        "canonical limits by status": status_counts,
        "canonical rules checked early, included in total": early_count,
        "last checked eligible candidate": candidates[eligible[eligible_done - 1]],
        "first cut eligible candidate": candidates[eligible[eligible_done]],
        "failures by rule, induced relation, and verdict": [
            {"rule": rule, "induced": states.split(), "K1/K2/K3": checks, "occurrences": value}
            for (rule, states, checks), value in sorted(failure_classes.items())
        ],
        "ten-rule finishes independently rebuilt from rule-Q choices": len(reconstructed_ten),
        "ten-rule finish recount": aggregate_finishes(ten_finish, computed),
        "eleven-rule option pair finish recount": aggregate_finishes(eleven_finish, computed),
        "archive history counts": history_counts,
        "61/30 all-knot cases": witnesses,
        "smallest-gain setting-rule redundancy": redundancy,
        "direct substitution controls": [label for label, _ in cases],
    }


def sign_structure(base, index):
    parity_index = 0
    result = []
    signs = []
    for rule in base:
        if rule.law == "nae":
            result.append(rule)
        else:
            law = "odd" if index & (1 << parity_index) else "even"
            result.append(Rule(law, rule.places))
            signs.append(law)
            parity_index += 1
    assert parity_index == 9
    return tuple(result), signs


def recount_signs(base, rows):
    ties = Counter()
    score_class_from_saved_scores = Counter()
    failures = Counter()
    relation_classes = defaultdict(Counter)
    tested = 0
    for index, raw in enumerate(rows):
        start, signs = sign_structure(base, index)
        assert raw["index"] == index and raw["signs"] == signs
        tested += 1
        start_count, start_verdicts, _ = analyze(start)
        actual_ties = []
        for rule, verdict in start_verdicts.items():
            if len(rule.places) == 4:
                classes = {"inequality" if state[1] != state[2] else "equality"
                           for state in verdict.allowed}
                (tie,) = classes
                actual_ties.append(tie)
                relation_classes[f"{rule}: {tie}"][" ".join(verdict.allowed)] += 1
        tie_x, tie_y = actual_ties
        assert raw["tie x2,x3"] == tie_x and raw["tie y2,y3"] == tie_y
        ties[f"{tie_x} / {tie_y}"] += 1
        score = raw["from the finish"]["score_all"], raw["from the finish"]["hidden"]
        assert (score == ("20/9", True)) == (tie_x == tie_y == "inequality")
        score_class_from_saved_scores[f"{score[0]} / hidden={score[1]}"] += 1

        for setting in (None, *SETTINGS):
            if setting is None:
                count, verdicts = start_count, start_verdicts
                key = "start"
                assert count == raw["start allowed"]
            else:
                count, verdicts, _ = analyze(start + setting_rules(*setting))
                key = f"finished {setting[0]}{setting[1]}"
                assert count == raw["allowed at the finish"][str(setting)]
            actual = failure_rows(verdicts)
            assert len(actual) == 2 and all(
                entry["K1/K2/K3"] == (True, False, True) for entry in actual
            )
            saved = raw["knot test"][key]
            assert all(gates(verdict.own, len(rule.places)) == (True, True, True)
                       for rule, verdict in verdicts.items())
            assert len(saved["fail"]) == 2
            for old, new in zip(saved["fail"], actual, strict=True):
                assert old["knot"] == new["rule"] and tuple(old["induced"]) == new["induced"]
                assert tuple(old[f"K{j}"] for j in range(1, 4)) == new["K1/K2/K3"]
            failures[key] += len(actual)
    return {
        "sign assignments": tested, "structure occurrences": 5 * tested,
        "rule verdicts": 63 * tested,
        "failures by stage": failures, "isolated rule failures": 0,
        "ties": ties, "four-place start relations": relation_classes,
        "score classes from saved scores, related to independently recounted ties": score_class_from_saved_scores,
    }


def canonical(structure, rule, verdict, status):
    clauses = []
    for constraint in structure:
        allowed = own_relation(constraint.law, len(constraint.places))
        for levels in product("01", repeat=len(constraint.places)):
            if "".join(levels) not in allowed:
                clauses.append(" ".join(
                    name if value == "0" else f"-{name}"
                    for name, value in zip(constraint.places, levels, strict=True)
                ))
    names = rule.places
    words = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "; ".join(clauses),
             "--loops", *names[:-1], "--contact", names[-1]]
    witnesses = tuple(v for v in namespaces(structure) if v not in names)
    if witnesses:
        words.extend(("--witnesses", *witnesses))
    words.append("--json")
    result = subprocess.run(
        words, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
        check=False, capture_output=True, text=True,
    )
    assert result.returncode in (0, 1) and result.stdout, (result.returncode, result.stderr)
    recorded = json.loads(result.stdout)
    actual_gates = tuple(recorded[name] for name in ("binding", "loss_on_erasure", "coexistence"))
    assert tuple(recorded["allowed"]) == verdict.allowed
    assert actual_gates == verdict.gates and recorded["is_knot"] == verdict.knot
    return {"rule": str(rule), "allowed": verdict.allowed, "K1/K2/K3": actual_gates,
            "distinctions": len(namespaces(structure)), "canonical status in the run": status}


def canonical_sample(raw, pilot):
    targets = []
    for row in raw["structures"]:
        status = canonical_status(row)
        labels = row["labels"]
        if status == "over width" or not (
            labels[0].startswith("structures.json:")
            or any(label.startswith("part 2: ten ") for label in labels)
            or any("ONE-PARENT-REREAD uniform" in label and re.search(r"tid (113|143),", label)
                   for label in labels)
            or any(label.startswith("part 2: eight-thirds case") for label in labels)
            or status == "cut"
        ):
            continue
        structure = rules(row["structure"])
        _, verdicts, _ = analyze(structure)
        if status == "cut":
            if any(x[0].startswith("cut ") for x in targets):
                continue
            chosen = list(verdicts)[:1] + [rule for rule, verdict in verdicts.items() if not verdict.knot]
            if not any(not verdicts[rule].knot for rule in chosen):
                continue
            target_label = f"cut {labels[0]}"
        elif labels[0].startswith("structures.json:"):
            chosen = [rule for rule, verdict in verdicts.items() if not verdict.knot]
            if labels[0].endswith(("seven + settings 00", "nine + settings 11", "smallest gain finished 10")):
                chosen.append(structure[0])
            target_label = labels[0]
        elif any("ONE-PARENT-REREAD uniform" in label and re.search(r"tid (113|143),", label)
                 for label in labels):
            chosen = [structure[0], *structure[-2:]]
            target_label = labels[0]
        elif any("part 2: ten " in label for label in labels):
            chosen = [structure[0], structure[-3]] if labels[0].endswith("| (1, 1)") and any(
                rule == Rule("nae", ("x1", "c", "za")) for rule in structure
            ) else []
            target_label = labels[0]
        else:
            chosen = [rule for rule, verdict in verdicts.items() if not verdict.knot]
            target_label = labels[0]
        targets.extend((target_label, structure, rule, verdicts[rule], status) for rule in chosen)

    if pilot:
        target_by_width = {}
        for target in targets:
            width = len(namespaces(target[1]))
            target_by_width.setdefault(width, target)
        targets = [target_by_width[width] for width in sorted(target_by_width)]
    return [
        {"structure": label, **canonical(structure, rule, verdict, status)}
        for label, structure, rule, verdict, status in targets
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("projection", "canonical"))
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()

    frozen = {label: tuple(Rule(law, tuple(places)) for law, places in texts)
              for label, texts in load(REGISTERED).items()}
    raw = load(RAW / "part8_knots.json")
    if args.mode == "canonical":
        checked = canonical_sample(raw, args.pilot)
        result = {"checks": len(checked), "structures": len({c["structure"] for c in checked}),
                  "failing rules": sum(not all(c["K1/K2/K3"]) for c in checked),
                  "details": checked}
        output = HERE / "finding_canonical.json"
    else:
        signs = load(RAW / "part3_signs.json")["rows"]
        if args.pilot:
            rows = raw["structures"]
            widest = sorted(rows, key=lambda row: row["n_distinctions"], reverse=True)[:16]
            mini = [*rows[:16], *widest, *rows[1300:1316], *rows[-16:]]
            for row in mini:
                structure = rules(row["structure"])
                count, verdicts, _ = analyze(structure)
                saved_verdicts(row, structure, count, verdicts)
            result = {"part 8 pilot structures": len(mini),
                      "part 3 pilot": recount_signs(frozen["eleven (start)"], signs[:8])}
        else:
            controls = [(label, frozen[label]) for label in (
                "smallest gain: part", "eight + settings 00", "eleven + settings 00",
            )]
            result = {
                "part 8": part8_recount(frozen, raw, controls),
                "part 3": recount_signs(frozen["eleven (start)"], signs),
            }
        output = HERE / "finding.json"
    if args.pilot:
        print(json.dumps(result, indent=2))
    else:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
