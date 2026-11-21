"""Fresh paired replays for the radius-two separating-name policy."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from functools import cache
from itertools import combinations
from pathlib import Path
from random import Random
import gzip
import io
import json
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / ("experiments/LOOSE-NAMES-AND-SPENT-JOINS-20261120-001B/"
                "LOOSE-NAMES-AND-SPENT-JOINS-20261120-001B-E001_spent_joins/samples.py")
PREREGISTRATION = ROOT / "research" / HERE.parent.name / "preregistration.md"
MODEL = HERE / "model.py"
ARMS = ("trees", "partnered", "distal")
RULES = ("ordinary", "spent", "local")
LAWS = ("parity", "nae")
N = 64
H = 4
BIRTH_CAP = 256
FORECAST_CAP = 8192
RADIUS = 2
SEEDS = {"trees": 20261120841, "partnered": 20261120842,
         "distal": 20261120843, "queries": 20261120844}


@cache
def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def prior():
    return load("local_join_previous_replay", PRIOR)


def model():
    return load("local_join_fresh_model", MODEL)


def fixture():
    return prior().fixture()


def step(stars, law, rule):
    return model().step(stars, law, rule, cap=BIRTH_CAP, forecast_cap=FORECAST_CAP)


def distal_start(rng):
    length = rng.randrange(1, 7)
    left, right = range(4, 4 + length), range(4 + length, 4 + 2 * length)
    shared = [(0, 1), (0, 2), (1, 3)]
    shared.extend(tuple(pair) for branch, root in ((left, 0), (right, 1))
                  for pair in zip((root, *branch), branch))
    return {"length": length, "side_roots": (0, 1), "central_name": 0,
            "terminal_query": (2, 3), "branch_tips": (left[-1], right[-1]),
            "shared_pairs": shared, "loose_supplies": (0, 0) + (6,) * (2 * length + 2)}


def make_sources(raw):
    open_stars = fixture().source_from(raw["shared_pairs"], raw["loose_supplies"])
    if "central_name" not in raw:
        return {"source": open_stars}
    new = 1 + max(d for row in open_stars for d in row)
    closed_stars = tuple((*row, new) if v in raw["branch_tips"] else row
                          for v, row in enumerate(open_stars))
    _, _, before = fixture().incidence(open_stars)
    _, _, after = fixture().incidence(closed_stars)
    assert before == after
    return {"open": open_stars, "edited": closed_stars}


def query_seeds():
    rng = Random(SEEDS["queries"])
    return {(arm, k): rng.getrandbits(128) for arm in ARMS for k in range(N)}


def choose_query(raw, stars, seed):
    rng = Random(seed)
    _, _, loose = fixture().incidence(stars)
    holders = raw["terminal_query"] if "terminal_query" in raw else tuple(sorted(rng.sample(sorted(loose), 2)))
    return holders, tuple(rng.choice(loose[v]) for v in holders)


def near_holders(ordinary, left, right):
    return (nx.single_source_shortest_path_length(ordinary, left, cutoff=RADIUS).keys()
            | nx.single_source_shortest_path_length(ordinary, right, cutoff=RADIUS).keys())


def rooted_snapshot(stars, bit):
    owners, ordinary, loose = fixture().incidence(stars)
    left, right = owners[bit]
    near = near_holders(ordinary, left, right)
    shared_degree = Counter(v for vs in owners.values() if len(vs) == 2 for v in vs)
    visible = [(v, len(loose.get(v, ())), shared_degree[v]) for v in sorted(near)]
    internal = [(d, *sorted(vs)) for d, vs in sorted(owners.items())
                if len(vs) == 2 and set(vs) <= near]
    recorded = model().rooted_record(model().read(stars), bit)
    assert recorded["root"] == (left, right, bit) and recorded["holders"] == visible
    assert sorted((d, a, b) for a, b, bits in recorded["shared"] for d in bits) == internal
    return {"roots": (left, right), "tested_distinction": bit,
            "visible_holders": visible, "induced_shared_distinctions": internal}


def independent_permissions(stars):
    """Delete the individual name and test the rooted and unrestricted holdings."""
    owners, ordinary, loose = fixture().incidence(stars)
    multiplicity = Counter(tuple(sorted(hs)) for hs in owners.values() if len(hs) == 2)
    grants = {"ordinary": (), "spent": [], "local": []}
    for bit, hs in sorted(owners.items()):
        if len(hs) != 2 or any(v in loose for v in hs):
            continue
        left, right = sorted(hs)
        if multiplicity[left, right] != 1:
            continue
        a, b = (tuple(sorted(set(ordinary[v]) & loose.keys())) for v in (left, right))
        if not a or not b:
            continue
        near = near_holders(ordinary, left, right)
        ordinary.remove_edge(left, right)
        local = not nx.has_path(ordinary.subgraph(near), left, right)
        global_ = not nx.has_path(ordinary, left, right)
        ordinary.add_edge(left, right)
        assert not global_ or local
        if local:
            assert not set(a) & set(b)
            row = (bit, left, right, a, b)
            grants["local"].append(row)
            if global_:
                grants["spent"].append(row)
    for rule in ("local", "spent"):
        assert len(grants[rule]) == len({tuple(sorted((*a, *b))) for _, _, _, a, b in grants[rule]})
    return grants


def after_payment(stars, rows):
    _, ordinary, _ = fixture().incidence(stars)
    for bit, a, b, _, _ in rows:
        near = near_holders(ordinary, a, b)
        ordinary.remove_edge(a, b)
        assert nx.has_path(ordinary.subgraph(near), a, b), bit
        ordinary.add_edge(a, b)


def union_children(births, left, right):
    first = {b["id"] for b in births if left & set(b["parents"])}
    second = {b["id"] for b in births if right & set(b["parents"])}
    return first, second


@cache
def replay(stars, law, rule, pair, *, partnered=False):
    base = prior()
    rows = []
    first = literal_first = None
    decided = False
    certificate = "capped_before_decision"
    left, right = ({k} for k in pair)
    for age in range(3 if partnered else H):
        move = step(stars, law, rule)
        permissions = independent_permissions(stars)
        assert tuple(sorted(move.bridges)) == tuple(sorted(permissions[rule]))
        roster_union = {tuple(sorted((*a, *b))) for _, _, _, a, b in permissions[rule]}
        assert set(move.added) == roster_union
        assert not any(permissions.values()) or age < 2
        entry = {"age": age, "status": move.status, "funded": move.funded,
                 "physical_permissions": permissions, "added": move.added,
                 "shortages": move.shortages, "forecast_added": move.next_added,
                 "planned_births_lower": move.planned_births_lower,
                 "actual_births": None}
        if rows and not rows[-1]["closed_after_step"]:
            previous = rows[-1]
            assert tuple(previous["forecast_added"]) == move.added
            if move.status != "cap" or move.funded is True:
                required = Counter(k for group in move.groups for k in group)
                assert all(required[b["id"]] == b["next_demand"] for b in previous["actual_births"])
                entry["previous_forecast_matches_actual_demand"] = True
        rows.append(entry)
        if move.status != "extend":
            assert move.stars == stars
            if move.parents:
                entry.update(planned_parents=move.parents, planned_inputs=move.inputs)
            if not decided and move.status in ("closed", "stall"):
                decided, certificate = True, move.status
            break
        continuing, _ = base.check_actual(stars, move, law)
        births = [{"id": i, "parents": parents, "inputs": inputs,
                   "fresh": base.names_and_count(fresh), "next_demand": demand}
                  for i, (parents, inputs, fresh, demand) in enumerate(
                      zip(move.parents, move.inputs, move.fresh, move.demand, strict=True), len(stars))]
        entry.update(actual_births=births, total_actual_fresh=sum(map(len, move.fresh)),
                     total_actual_births=len(births), closed_after_step=not continuing,
                     added_input_slots=sum(map(len, move.added)))
        stars = move.stars
        if move.added:
            after_payment(stars, move.bridges)
            entry["paid_name_has_radius_two_alternate_route"] = True
        left, right = union_children(births, left, right)
        entry["query_ancestry"] = [sorted(left), sorted(right)]
        if left & right and literal_first is None:
            literal_first = age + 1
            if decided:
                assert first == literal_first
            else:
                first, decided, certificate = literal_first, True, "actual_birth"
        elif not decided and not continuing:
            decided, certificate = True, "closing_cut"
        elif not decided and age == 1:
            d = base.witnessed_separation(stars, left, right)
            first = d + 2 if d is not None else None
            decided, certificate = True, "ordinary_parent_identity_after_second_cut"
    if first is not None and first <= sum(r["status"] == "extend" for r in rows):
        assert first == literal_first
    return base.History(rows, first, decided, certificate, literal_first)


def central_trial(raw, star, law, rule, history):
    row = history.rows[0]
    bit = raw["central_name"]
    witnesses = [w for w in row["physical_permissions"][rule] if w[0] == bit]
    donors = (2, 3, 4, 4 + raw["length"])
    paid_view = None
    if row["actual_births"]:
        matching = [b for b in row["actual_births"] if b["parents"] == donors]
        assert bool(matching) == bool(witnesses) and len(matching) <= 1
        if matching:
            paid_view = matching[0]
    assert all(v in fixture().incidence(star)[2] for v in donors)
    return {"permission": bool(witnesses), "rival_union": donors,
            "paid_child": paid_view,
            "literal_first_common": history.observed_first_common,
            "first_common": history.first_common,
            "first_common_decided": history.arrival_decided}


def matched_rules(histories, size):
    base = prior()
    return {f"{a}_vs_{b}": base.paired_comparison(histories[a], histories[b], size)
            for a, b in combinations(RULES, 2)}


def recode_probe(stars):
    holders = tuple(reversed(range(len(stars))))
    bits = sorted({d for row in stars for d in row})
    distinction = dict(zip(bits, reversed(bits), strict=True))
    recoded = tuple(tuple(sorted(distinction[d] for d in stars[v])) for v in holders)
    original = independent_permissions(stars)
    altered = independent_permissions(recoded)
    for rule in RULES:
        def old_record(row):
            d, w, z, a, b = row
            sides = [(holders[w], tuple(sorted(holders[i] for i in a))),
                     (holders[z], tuple(sorted(holders[i] for i in b)))]
            (x, left), (y, right) = sorted(sides)
            return (distinction[d], x, y, left, right)
        assert set(map(old_record, altered[rule])) == set(original[rule])
        for law in LAWS:
            first, second = step(stars, law, rule), step(recoded, law, rule)
            assert first.status == second.status and first.funded == second.funded
            assert set(first.added) == {tuple(sorted(holders[v] for v in g)) for g in second.added}
            assert sorted(first.shortages) == sorted((holders[v], k) for v, k in second.shortages)
            if first.status == "extend":
                a = Counter((p, len(f)) for p, f in zip(first.parents, first.fresh, strict=True))
                b = Counter((tuple(sorted(holders[v] for v in p)), len(f))
                            for p, f in zip(second.parents, second.fresh, strict=True))
                assert a == b
    return True


def trial(arm, raw, index, seed):
    sources = make_sources(raw)
    pair, marks = choose_query(raw, next(iter(sources.values())), seed)
    result = {"index": index, "raw_start": raw, "query_seed": seed, "query_holders": pair,
              "query_loose_distinctions": marks, "preparations": {}}
    for tag, stars in sources.items():
        side = {"original_stars": stars, "lawful_by_law": {}, "by_law": {}}
        if arm == "distal":
            side["original_radius_two_record"] = rooted_snapshot(stars, raw["central_name"])
        for law in LAWS:
            admitted = prior().lawful(stars, law)
            side["lawful_by_law"][law] = admitted
            if not admitted:
                continue
            histories = {rule: replay(stars, law, rule, pair, partnered=arm == "partnered") for rule in RULES}
            if arm in ("trees", "partnered"):
                # The exact same cohorts and prices also imply identical
                # eligibility/arrival even where their next width is capped.
                assert histories["spent"] == histories["local"]
            if arm == "partnered":
                assert histories["ordinary"] == histories["spent"]
                assert [r["total_actual_births"] for r in histories["local"].rows] == [8, 10, 24]
                third = histories["local"].rows[-1]["actual_births"]
                assert {b["fresh"]["count"] for b in third} == {4086 // 2}
            row = {"policies": {rule: vars(h) for rule, h in histories.items()},
                   "matched_actual_outputs": matched_rules(histories, len(stars))}
            if arm == "distal":
                row["central_distinction"] = {
                    rule: central_trial(raw, stars, law, rule, h) for rule, h in histories.items()}
                for rule, result_row in row["central_distinction"].items():
                    expect = rule != "ordinary" and (tag == "open" or (rule == "local" and raw["length"] >= 3))
                    assert result_row["permission"] == bool(result_row["paid_child"]) == expect
                    assert result_row["first_common_decided"]
                    assert result_row["first_common"] == (1 if expect else None)
            side["by_law"][law] = row
        if index == 0:
            side["relabelled_first_cut_with_paid_outputs_checked"] = recode_probe(stars)
        result["preparations"][tag] = side
    if arm == "distal":
        open_ = result["preparations"]["open"]
        edited = result["preparations"]["edited"]
        equal = open_["original_radius_two_record"] == edited["original_radius_two_record"]
        assert equal == (raw["length"] >= 3)
        result["identical_original_radius_two_records"] = equal
        result["matched_edits"] = {}
        for law in LAWS:
            a, b = (result["preparations"][tag]["by_law"][law] for tag in ("open", "edited"))
            result["matched_edits"][law] = {}
            for rule in RULES:
                left, right = (r["central_distinction"][rule]["paid_child"] for r in (a, b))
                h1, h2 = (prior().History(**v["policies"][rule]) for v in (a, b))
                result["matched_edits"][law][rule] = {
                    "central_paid_fresh_open_and_edited":
                        [c["fresh"]["count"] if c else None for c in (left, right)],
                    "matched_actual_outputs": prior().paired_comparison(h1, h2, len(sources["open"])),
                }
    return result


def distribution(values):
    return dict(sorted(Counter(values).items()))


def summarize_policy(histories, rule):
    score = prior().interval
    by_age = {}
    for age in range(H):
        rows = [p["rows"][age] for p in histories if len(p["rows"]) > age]
        eligible = [r for r in rows if r["physical_permissions"][rule]]
        paid = [r for r in rows if r["status"] == "extend"]
        by_age[age] = {
            "attempted": len(rows),
            "statuses": Counter(r["status"] for r in rows),
            "policy_qualification": score(bool(r["physical_permissions"][rule]) for r in rows),
            "funding_where_qualified": score(r["funded"] for r in eligible),
            "funding_of_nonempty_plans": score(r["funded"] for r in rows if r["status"] != "closed"),
            "actual_added_birth_given_eligible":
                score(True if r["actual_births"] else False if r["status"] == "stall" else None for r in eligible),
            "materialized": len(paid),
            "actual_total_births": distribution(r["total_actual_births"] for r in paid),
            "actual_total_fresh": distribution(r["total_actual_fresh"] for r in paid),
            "added_input_slots": distribution(r["added_input_slots"] for r in paid),
            "maximum_parent_number": distribution(max(len(b["parents"]) for b in r["actual_births"]) for r in paid),
        }
    any_paid = []
    for h in histories:
        if any(r["actual_births"] and r["added"] for r in h["rows"]):
            any_paid.append(True)
        elif any(r["status"] in ("cap", "forecast_cap") for r in h["rows"][:2]):
            any_paid.append(None)
        else:
            any_paid.append(False)
    event = prior().first_common
    funded = [h for h in histories if h["rows"][0]["funded"] is True]
    return {"lawful_starts_with_query": len(histories),
            "first_funded": score(h["rows"][0]["funded"] for h in histories),
            "actual_added_birth": score(any_paid),
            "finite_common_descendant": score(event(h) for h in histories),
            "finite_common_descendant_given_funding": score(event(h) for h in funded),
            "decided_delays": Counter(str(h["first_common"]) if h["arrival_decided"] else "unresolved"
                                      for h in histories),
            "ages": by_age}


def summarize_preparation(draws, tag, law):
    prepared = [d["preparations"][tag] for d in draws]
    eligible = [p["by_law"][law] for p in prepared if p["lawful_by_law"][law]]
    score = prior().interval
    return {"all_starts": len(draws), "lawful": score(p["lawful_by_law"][law] for p in prepared),
            "policies": {rule: summarize_policy([x["policies"][rule] for x in eligible], rule) for rule in RULES}}


def paired_distal_summary(draws, law):
    score = prior().interval
    grouped = {(f"length_{i}"): [d for d in draws if d["raw_start"]["length"] == i]
               for i in range(1, 7)}
    grouped["near"] = [d for d in draws if d["raw_start"]["length"] <= 2]
    grouped["far"] = [d for d in draws if d["raw_start"]["length"] >= 3]
    grouped["all"] = draws
    result = {}
    for name, group in grouped.items():
        row = {"draws": len(group),
               "identical_physical_radius_two_records":
                   score(d["identical_original_radius_two_records"] for d in group)}
        for rule in RULES:
            opened, edited = ([d["preparations"][side]["by_law"][law]["central_distinction"][rule]
                               for d in group if d["preparations"][side]["lawful_by_law"][law]]
                              for side in ("open", "edited"))
            price_pairs = [d["matched_edits"][law][rule]["central_paid_fresh_open_and_edited"] for d in group]
            comparable = [p for p in price_pairs if None not in p]
            row[rule] = {"open_permission": score(r["permission"] for r in opened),
                         "edited_permission": score(r["permission"] for r in edited),
                         "open_paid_central_child": score(bool(r["paid_child"]) for r in opened),
                         "edited_paid_central_child": score(bool(r["paid_child"]) for r in edited),
                         "open_marked_first_child": score(r["first_common"] == 1 for r in opened),
                         "edited_marked_first_child": score(r["first_common"] == 1 for r in edited),
                         "central_child_price_changed_given_both_paid": score(a != b for a, b in comparable),
                         "central_child_priced_open_edited": Counter(str(p) for p in price_pairs)}
        result[name] = row
    return result


def run(arm):
    base = prior()
    seeds = query_seeds()
    rng = Random(SEEDS[arm])
    generate = {"trees": base.tree_start, "partnered": base.partner_start, "distal": distal_start}[arm]
    draws = [trial(arm, generate(rng), i, seeds[arm, i]) for i in range(N)]
    tags = tuple(draws[0]["preparations"])
    contract_path = HERE / "contract.json"
    contract = json.loads(contract_path.read_text())
    advice = ROOT / contract["advisor_receipt"]
    inputs = (Path(__file__).resolve(), MODEL, PREREGISTRATION, contract_path,
              advice, PRIOR, model().PRIOR / "model.py", base.FIXTURES)
    result = {"arm": arm, "seeds": SEEDS, "draws": draws, "attempted_parent_steps": H,
              "birth_cap": BIRTH_CAP, "forecast_cap": FORECAST_CAP,
              "by_preparation": {tag: {law: summarize_preparation(draws, tag, law) for law in LAWS}
                                 for tag in tags},
              "sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in inputs}}
    if arm == "distal":
        result["distal_edit_by_length_and_law"] = {law: paired_distal_summary(draws, law) for law in LAWS}
    if arm == "partnered":
        result["after_third_literal_cut"] = {"exact_next_width": 4086, "proof": "partnered recurrence",
                                            "complete_cohorts_in_all_policies_identical_at_all_ages": True}
    return result


def write_receipt(result, stream):
    json.dump(result, stream, sort_keys=True, separators=(",", ":"), allow_nan=False)
    stream.write("\n")


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--arm", required=True, choices=ARMS)
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    receipt = run(args.arm)
    if args.output is None:
        write_receipt(receipt, sys.stdout)
    elif args.output.suffix == ".gz":
        with args.output.open("xb") as out:
            with gzip.GzipFile(filename="", fileobj=out, mode="wb", mtime=0) as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8") as text:
                    write_receipt(receipt, text)
    else:
        with args.output.open("x", encoding="utf-8") as out:
            write_receipt(receipt, out)


if __name__ == "__main__":
    main()
