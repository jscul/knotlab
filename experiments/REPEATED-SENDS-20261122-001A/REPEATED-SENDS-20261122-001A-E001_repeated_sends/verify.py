"""Recompute the joint masses and verify full physical witnesses independently."""

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations_with_replacement, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
PRIOR_SCOPE = "HIDDEN-SENDER-MARKS-20261122-001A"
PRIOR = ROOT / "artifacts" / PRIOR_SCOPE / (PRIOR_SCOPE + "-E001_hidden_sends")
JOINT = DATA / "joint.json.gz"
WITNESSES = DATA / "witnesses.json.gz"
SOURCE = DATA / "source.json.gz"
PINNED = {
    JOINT: "dff18fbd9135729003b0a026da41cc44f337d355c9de1a5d3c0552b8ceb98135",
    WITNESSES: "446aa2aada51b7160e42e613758258fb5a7cfecddca4ca69248816dff3cfdc58",
    SOURCE: "441598562ae392169f3ee51f9faf0857d0e9314da186ca849b8ec37cc20c4041",
    PRIOR / "growth.json.gz": "f89de84f884b323e40f81a59dc7afa0e734bf4dc974e26eb5c7be9c5f775ce9a",
    PRIOR / "supports.json.gz": "35d55ff7594316542c0ee003ea4c0de1c82eda207c66b82a54961b1befccbf80",
    PRIOR / "whole_words.json.gz": "d652b46212ed4fdd3ad344596ce9a6c1b2cc2be3327cb8fbac6a765226c2f290",
}
LAWS = ("parity", "nae")
ROUTES = ("intact", "interrupted", "sham")
SIDES = ("00", "01", "10", "11")
BANDS = tuple(map("".join, combinations_with_replacement("EPBF", 2)))
REQUESTS = ("II", "IT", "TI", "TT")
CLASSES = ("structural", "pointwise")
DELTA = (1 << 510) | (1 << 563)
WORDS = {"".join(bits) for bits in product("01", repeat=3)}
CLOCK = ((None, None, None), (0, 1, 2))


def mask(names):
    return sum(1 << name for name in names)


def bits(word, names):
    return "".join(str((word >> name) & 1) for name in names)


def lawful(law, width, count):
    return count % 2 == 0 if law == "parity" else count not in (0, width)


def fresh(law, inherited, width):
    count = inherited.count("1")
    return tuple("".join(row) for row in product("01", repeat=width)
                 if lawful(law, width + len(inherited), count + row.count("1")))


def exact(table):
    return {key: Fraction(value) for key, value in table.items()}


def as_mass(table):
    return {key: str(value) for key, value in table.items() if value}


def physical(growth, law, route):
    case = growth["cases"][route][law]
    rows = list(growth["original_stars"])
    original = mask(set().union(*map(set, rows)))
    births = {}
    last_by_age = [len(rows)]
    for cut in case["cuts"]:
        for row in cut["births"]:
            assert row["holder"] == len(rows)
            births[row["holder"]] = row
            rows.append(row["consumed_names"] + row["fresh_names"])
        last_by_age.append(len(rows))
    assert len(rows) == 647
    r = births[294]
    assert (r["parents"], r["consumed_names"], r["fresh_names"]) == ([162, 165], [949, 957], [1754, 1755, 1756])
    assert case["receivers"]["R"]["holding"] == rows[294]
    assert tuple(map(tuple, case["receivers"]["R"]["local_clock"])) == CLOCK
    owned_at_birth = [{h for h, names in enumerate(rows[:last_by_age[2]]) if d in names}
                      for d in r["fresh_names"]]
    assert owned_at_birth == [{294}, {294}, {294}]
    owned_after_finish = [{h for h, names in enumerate(rows) if d in names} for d in r["fresh_names"]]
    assert owned_after_finish == [{294, 631}, {294, 633}, {294, 634}]
    return {"births": births, "constraints": [(mask(row), len(row)) for row in rows],
            "domain": mask(set().union(*map(set, rows))), "old_domain": original, "last": last_by_age}


def independent_factor(source, state, old):
    law = source["law"]
    births = state["births"]
    r = births[294]
    active = [row["holder"] for row in source["carriers_in_a_b_order"]]
    assert active == ([164, 163] if source["route"] == "interrupted" else [162, 163])
    choices = {}
    for h in set(active) | set(r["parents"]):
        child = births[h]
        choices[h] = fresh(law, bits(old, child["consumed_names"]), len(child["fresh_names"]))
    seen = {}
    accepted_at_c = Counter()
    local_allocations = source["allocations"]
    for row in local_allocations:
        banks = tuple(row["carrier_fresh_words"])
        assert banks not in seen
        blockers = []
        for h, bank in zip(active, banks, strict=True):
            birth = births[h]
            assert bank in choices[h]
            if not lawful(law, len(bank) + len(birth["consumed_names"]),
                          bank.count("1") + bits(old ^ DELTA, birth["consumed_names"]).count("1")):
                blockers.append(h)
        passed = not blockers
        assert passed == row["swap_admitted"] and sorted(blockers) == row["blocking_holders"]
        seen[banks] = passed
        if 162 in active:
            paid = births[162]["fresh_names"].index(949)
            accepted_at_c[passed, banks[active.index(162)][paid]] += Fraction(1, len(local_allocations))
        else:
            paid = births[162]["fresh_names"].index(949)
            for c in choices[162]:
                accepted_at_c[passed, c[paid]] += Fraction(1, len(local_allocations) * len(choices[162]))
    assert seen.keys() == set(product(*(choices[h] for h in active)))
    assert sum(accepted_at_c.values()) == 1
    assert sum(v for (ok, _), v in accepted_at_c.items() if ok) == Fraction(source["pointwise_admission_probability"])
    p_index = births[165]["fresh_names"].index(957)
    p_probability = Counter(row[p_index] for row in choices[165])
    result = Counter()
    for (yes, c), weight in accepted_at_c.items():
        for paid_p, count in p_probability.items():
            compatible = fresh(law, c + paid_p, len(r["fresh_names"]))
            for word in compatible:
                result[yes, word] += weight * Fraction(count, len(choices[165]) * len(compatible))
    assert sum(result.values()) == 1 and all(weight > 0 for weight in result.values())
    return result


def check_witness(law, route, state, old, factor_key, entry):
    enabled, z = factor_key
    full = int(entry["before_late_checks"], 16)
    candidate = int(entry["would_be_after_one_late"], 16)
    assert full >= 0 and full & ~state["domain"] == 0
    assert full & state["old_domain"] == old and full ^ candidate == DELTA
    focused = {162, 163, 165, 294} | ({164} if route == "interrupted" else set())
    assert {int(h) for h in entry["chosen_foreground"]} == focused
    for h, selected in entry["chosen_foreground"].items():
        assert bits(full, state["births"][int(h)]["fresh_names"]) == selected
    masks = state["constraints"]
    assert all(lawful(law, width, (full & m).bit_count()) for m, width in masks)
    bad = {h for h, (m, width) in enumerate(masks) if not lawful(law, width, (candidate & m).bit_count())}
    assert bad <= ({164, 163} if route == "interrupted" else {162, 163})
    assert not {h for h in bad if h < state["last"][0]}
    assert all({h for h in bad if h < stop} == bad for stop in state["last"][1:])
    assert enabled == entry["late_lawful"] == (not bad)
    assert bits(full, (949, 957, 1754, 1755, 1756)) == bits(candidate, (949, 957, 1754, 1755, 1756))
    assert bits(full, (1754, 1755, 1756)) == bits(candidate, (1754, 1755, 1756)) == entry["R_fresh"] == z
    assert candidate ^ DELTA == full


def local_history(z):
    assert z in WORDS
    return (z, CLOCK[0]), (z, CLOCK[1])


def check_observation(observation):
    assert type(observation) is tuple and len(observation) == 2
    assert all(type(row) is tuple and len(row) == 2 for row in observation)
    assert observation == local_history(observation[0][0])


def check_counterfeit_history():
    # Independent reads have the same marginals, but put mass on 56 impossible histories.
    counterfeit = [((first, CLOCK[0]), (second, CLOCK[1]))
                   for first, second in product(sorted(WORDS), repeat=2) if first != second]
    counterfeit.append((("000", CLOCK[0], "S0"), ("000", CLOCK[1])))
    for row in counterfeit:
        try:
            check_observation(row)
        except AssertionError:
            continue
        raise AssertionError("An independent second read or source label was accepted")
    return len(counterfeit) - 1


def realized(request, bands, admission_class, eligible):
    result = []
    for q, band in zip(request, bands, strict=True):
        if q == "I":
            result.append("I")
        elif band == "E":
            result.append("M")
        else:
            result.append("M" if admission_class == "pointwise" and eligible else "U")
    return "".join(result)


def push(factor, request, bands, admission_class):
    table = Counter()
    references = defaultdict(list)
    for (ok, word), weight in factor.items():
        status = realized(request, bands, admission_class, ok)
        key = f"{status}|{word}"
        check_observation(local_history(word))
        table[key] += weight
        references[key].append(f"{int(ok)}|{word}")
    assert sum(table.values()) == 1
    return table, {key: sorted(refs) for key, refs in references.items()}


def marginal(table):
    result = Counter()
    for key, weight in table.items():
        _, word = key.split("|")
        result[word] += weight
    assert sum(result.values()) == 1
    return result


def comparison(a, b):
    assert set(a) == set(b) == WORDS
    tv = sum(abs(a[w] - b[w]) for w in WORDS) / 2
    accuracy = sum(max(a[w], b[w]) for w in WORDS) / 2
    return {"total_variation": str(tv), "accuracy": str(accuracy),
            "histories_certifying_left": [], "histories_certifying_right": []}


def scored_events(table):
    statuses, total = Counter(), defaultdict(dict)
    two, fewer = Counter(), Counter()
    for key, weight in table.items():
        actual, word = key.split("|")
        statuses[actual] += weight
        total[word][actual] = weight
        (two if actual == "MM" else fewer)[word] += weight
    mass_two, mass_fewer = sum(two.values()), sum(fewer.values())
    assert mass_two + mass_fewer == 1 and set(total) == WORDS
    assert all(set(row) == set(statuses) for row in total.values())
    return {
        "actual_status_mass": as_mass(statuses),
        "two_realized": str(mass_two), "fewer_realized": str(mass_fewer),
        "best_two_vs_fewer_prior": str(max(mass_two, mass_fewer)),
        "best_two_vs_fewer_given_R": str(sum(max(two[w], fewer[w]) for w in WORDS)),
        "best_exact_status_given_R": str(sum(max(table.values()) for table in total.values())),
        "posterior_two_at_each_history": {w: str(Fraction(two[w], two[w] + fewer[w])) for w in WORDS},
        "status_at_each_word": {w: sorted(table) for w, table in total.items()},
        "any_record_excludes_globally_attainable_status": False,
        "R_given_two_realized": as_mass({w: v / mass_two for w, v in two.items()}) if mass_two else None,
        "R_given_fewer_realized": as_mass({w: v / mass_fewer for w, v in fewer.items()}) if mass_fewer else None,
    }


def compare_all(data, support, independent):
    prior = {f"{x['law']}-{x['route']}-{x['side']}": x["weighted"]
             for x in support["projections"] if x["target"] == "R"}
    launches = {(r["basis"], r["bands"], r["class"], r["request"]): r for r in data["launches"]}
    comparisons = {(r["basis"], r["bands"], r["class"]): r["summary"] for r in data["comparisons"]}
    assert len(launches) == len(data["launches"]) == 1920
    assert len(comparisons) == len(data["comparisons"]) == 480
    referenced_laws, referenced_summaries = set(), set()
    after_finish = 0
    headline = {}
    for basis, bands, admission in product(prior, BANDS, CLASSES):
        outcomes = {}
        summaries = {}
        for choice in REQUESTS:
            early = next((i for i, band in enumerate(bands) if band != "E"), len(bands))
            fate = choice[:early].count("T") % 2
            factor = f"{basis}-{fate}"
            row = launches[basis, bands, admission, choice]
            assert row["factor"] == factor
            submitted = data["joint_laws"][row["joint"]]
            recomputed, references = push(independent[factor], choice, bands, admission)
            assert exact(submitted["joint_P_actual_and_local"]) == recomputed
            assert submitted["eligible_witness_references"] == references
            referenced_laws.add(row["joint"])
            outcomes[choice] = recomputed
            summaries[choice] = marginal(recomputed)
            statuses = {key.split("|")[0] for key in recomputed}
            assert all({key.split("|")[0] for key in recomputed if key.endswith("|" + word)} == statuses
                       for word in WORDS)
            if any(any(s == "M" and b == "F" for s, b in zip(status, bands, strict=True)) for status in statuses):
                after_finish += 1
        score = comparison(summaries["II"], summaries["TT"])
        mix = Counter({key: weight / 2 for key, weight in outcomes["II"].items()})
        mix.update({key: weight / 2 for key, weight in outcomes["TT"].items()})
        first = prior[basis]["equal_prior_optimal_accuracy"]
        summary = {
            "II_vs_TT": score, "TI_vs_TT": comparison(summaries["TI"], summaries["TT"]),
            "II_vs_IT": comparison(summaries["II"], summaries["IT"]),
            "single_B307_accuracy": first, "birth_alone": score["accuracy"], "birth_plus_finish": score["accuracy"],
            "gain_from_second_local_sample": "0", "full_vs_single_B307": str(Fraction(score["accuracy"]) - Fraction(first)),
            "TT_actual_population": scored_events(outcomes["TT"]),
            "II_TT_mixture_actual_population": scored_events(mix),
        }
        key = comparisons[basis, bands, admission]
        assert data["summaries"][key] == summary
        referenced_summaries.add(key)
        if basis.endswith("-00"):
            contains_early = bands[0] == "E" and bands[1] != "E"
            bias = basis in ("nae-intact-00", "nae-sham-00") and contains_early
            assert score["accuracy"] == ("789/1568" if bias else "1/2")
            if bands in ("EE", "EP", "PP"):
                headline[f"{basis}-{bands}-{admission}"] = {
                    "II_vs_TT_accuracy": score["accuracy"],
                    "TT_status_masses": summary["TT_actual_population"]["actual_status_mass"],
                }
    assert referenced_laws == data["joint_laws"].keys() and referenced_summaries == data["summaries"].keys()
    return after_finish, headline


def audit():
    raw = {path: path.read_bytes() for path in PINNED}
    assert {path: sha256(blob).hexdigest() for path, blob in raw.items()} == PINNED
    joint, witness, source, growth, support, earlier = (json.loads(gzip.decompress(raw[path])) for path in PINNED)
    assert joint["baseline_hashes"] == {path.name: digest for path, digest in PINNED.items() if path.parent == PRIOR}
    assert witness["common_old"] == earlier["old_words"]
    frozen_source = {(cell["law"], cell["route"], cell["side"], cell["first_action"]): cell
                     for cell in source["cells"]}
    boards = {(law, route): physical(growth, law, route) for law, route in product(LAWS, ROUTES)}
    assert joint["observer"].keys() == {f"{law}-{route}" for law, route in boards}
    assert all(tuple(map(tuple, row["local_intro_and_finish"])) == CLOCK and row["further_positive_finishes"] == 0
               for row in joint["observer"].values())
    prior = {(x["law"], x["route"], x["side"]): x["weighted"]
             for x in support["projections"] if x["target"] == "R"}
    computed = {}
    checked = 0
    for law, route, side, first in product(LAWS, ROUTES, SIDES, ("idle", "swap")):
        net = int(first == "swap")
        k = f"{law}-{route}-{side}-{net}"
        old = int(earlier["old_words"][f"{law}-{side}"]["sender_idle_and_swap"][net], 16)
        cell = frozen_source[law, route, side, first]
        assert old == int(cell["first_action_net_old_word"], 16)
        truth = independent_factor(cell, boards[law, route], old)
        spec = joint["factors"][k]
        assert spec["actual_first_payment_a_b"] == bits(old, (510, 563))
        assert exact(spec["after_payment_eligible_and_R_word"]) == {f"{int(ok)}|{w}": v for (ok, w), v in truth.items()}
        z = Counter()
        for (eligible, word), weight in truth.items():
            z[word] += weight
            ref = witness["full_examples"][k][f"{int(eligible)}|{word}"]
            check_witness(law, route, boards[law, route], old, (eligible, word), ref)
            checked += 1
        assert witness["full_examples"][k].keys() == {f"{int(ok)}|{w}" for ok, w in truth}
        assert z == exact(prior[law, route, side][first])
        computed[k] = truth
    assert len(computed) == 48 and computed.keys() == joint["factors"].keys() == witness["full_examples"].keys()
    after_finish, headline = compare_all(joint, support, computed)
    counterfeit = check_counterfeit_history()
    return {
        "passed": True,
        "audit_class": "V1 independently authored replay on frozen inputs",
        "input_sha256": {str(path.relative_to(ROOT)): value for path, value in PINNED.items()},
        "source_factors": len(computed),
        "factor_witnesses_checked_on_full_holdings": checked,
        "scheduled_request_cells": 1920,
        "intent_and_actual_status_cases": 480,
        "cells_with_a_possible_move_after_R_FINISH": after_finish,
        "complete_histories_excluding_a_globally_attainable_status": 0,
        "fabricated_off_diagonal_histories_rejected": counterfeit,
        "fabricated_source_label_rejected": True,
        "primary_00_timing_checks": headline,
    }


if __name__ == "__main__":
    target = DATA / "verification.json"
    target.write_text(json.dumps(audit(), sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(sha256(target.read_bytes()).hexdigest(), target)
