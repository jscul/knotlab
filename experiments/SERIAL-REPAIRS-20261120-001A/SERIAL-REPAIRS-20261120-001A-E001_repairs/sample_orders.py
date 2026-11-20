"""Compare serial repair readouts with an independently funded first source step."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import random

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "sample_orders.json"
DESIGN = ROOT / "research/SERIAL-REPAIRS-20261120-001/preregistration.md"
SEEDS = {"tree": 20261120521, "unicyclic": 20261120522, "order": 20261120523, "mark": 20261120524}
PER_SIZE = 64
SERIAL_CAP = 12
LAWS = ("parity", "nae")
POLICIES = ("uniform", "joins-first")
REPAIRS = ("A0", "F", "U", "G", "FU", "FG", "UG", "FUG")


@cache
def archive():
    path = ROOT / ("experiments/FRESH-DEMAND-20261120-001A/"
                   "FRESH-DEMAND-20261120-001A-E001_orders/sample_starts.py")
    spec = spec_from_file_location("serial_repairs_source_archive", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_draws():
    for stratum in ("tree", "unicyclic"):
        rng = random.Random(SEEDS[stratum])
        for n in range(4, 9):
            for draw in range(PER_SIZE):
                prufer = [rng.randrange(n) for _ in range(n - 2)]
                holders = nx.from_prufer_sequence(prufer)
                added = None
                if stratum == "unicyclic":
                    missing = [pair for pair in combinations(range(n), 2) if not holders.has_edge(*pair)]
                    added = rng.choice(missing)
                    holders.add_edge(*added)
                meetings = sorted(tuple(sorted(pair)) for pair in holders.edges)
                extra = [int(rng.randrange(4) == 0) for _ in range(n)]
                sizes = [max(3, holders.degree(v)) + extra[v] for v in range(n)]
                yield {"draw": f"{stratum}/{n}/{draw:02d}", "stratum": stratum, "old_knots": n,
                       "prufer": prufer, "extra_meeting": added, "loose_bonus": extra,
                       "meetings": meetings, "arities": sizes}


def admission(p):
    """Read the physical live witnesses before applying either law."""
    live = tuple(v for v in range(len(p.bits_of)) if p.loose(v))
    witnesses = {(u, v): tuple(sorted(p.nbr[u] & p.nbr[v])) for u, v in combinations(live, 2)}
    groups = [tuple(sorted(g)) for g in p.groups_among(live)]
    obligations = Counter(v for g in groups for v in g)
    loose_counts = [len(p.loose(v)) for v in range(len(p.bits_of))]
    shortages = {v: obligations[v] - loose_counts[v] for v in live if obligations[v] > loose_counts[v]}
    shared = [(pair, witnesses[pair]) for pair in witnesses if witnesses[pair]]
    return {"live": live, "loose_counts": loose_counts, "witnesses": shared, "multi_groups": groups,
            "shortages": shortages, "S0": not shortages, "S3": all(len(g) < 3 for g in groups),
            "S4": all(len(w) <= 1 for w in witnesses.values()), "S6_prime": sum(loose_counts) >= 2}


def demand_read(witnesses, live, marked):
    """Count the maximal unheld groups and uncovered pairs through a mark."""
    marked_witnesses = witnesses[marked]
    traces = {v: marked_witnesses & witnesses[v] for v in live if v != marked}
    traces = {v: row for v, row in traces.items() if row}
    siblings = sorted(traces)
    adjacent = {v: {w for w in siblings if w != v and witnesses[v] & witnesses[w]} for v in siblings}
    groups = []
    for size in range(len(siblings), 1, -1):
        for row in combinations(siblings, size):
            chosen = set(row)
            if any(chosen <= g for g in groups) or set.intersection(*(traces[v] for v in chosen)):
                continue
            if all(w in adjacent[v] for v, w in combinations(row, 2)):
                groups.append(chosen)
    covered = set().union(*groups)
    return {"sibling_count": len(siblings), "sibling_occurrences": sum(map(len, traces.values())),
            "unheld_groups": len(groups), "covered_siblings": len(covered),
            "raw_demand": len(groups) + len(siblings) - len(covered)}


def independent_roster(stars, law, physical):
    layer = archive().first_layer(stars, law)
    if layer["status"] != "formed":
        return layer
    births = layer["births"]
    planned = Counter(tuple(b["parents"]) for b in births)
    expected = Counter(physical["multi_groups"])
    use = Counter(v for group in physical["multi_groups"] for v in group)
    expected.update({(v,): o - use[v] for v, o in enumerate(physical["loose_counts"]) if o > use[v]})
    assert planned == expected
    witnesses = [set(b["parents"]) for b in births]
    for i, birth in enumerate(births):
        expected_h = sum(physical["loose_counts"][v] - 1 for v in birth["parents"])
        birth["overlap"] = demand_read(witnesses, range(len(births)), i)
        assert birth["demand"] == birth["overlap"]["raw_demand"]
        assert expected_h == birth["overlap"]["sibling_occurrences"]
    return layer


def actual_implication(p, consumed, law):
    nae, _, _ = archive().libraries()
    if law == "parity":
        implied = p._reduce(p._mask(consumed)) == 0
        assert implied == (set(consumed) == {d for d, owners in p.owner.items() if len(owners) == 1})
        return implied, (1 << len(consumed)) >> implied
    with nae._solver(p, len(p.bits_of)) as solver:
        allowed = [word for word in range(1 << len(consumed))
                   if solver.solve(assumptions=[(d + 1) if word >> j & 1 else -(d + 1)
                                                for j, d in enumerate(consumed)])]
    implied = 0 not in allowed and (1 << len(consumed)) - 1 not in allowed
    return implied, len(allowed)


def begun_event(p, law, parents, *, independently_check=False):
    """Use the real archived physical mutation and its provisional live pool."""
    nae, serial, _ = archive().libraries()
    inputs = [p.loose(v)[0] for v in parents]
    implied, states = actual_implication(p, inputs, law)
    child = serial.new_junction(p, inputs)
    live_next = [v for v in range(len(p.bits_of)) if p.loose(v) or v == child]
    groups = [tuple(sorted(g)) for g in p.groups_among(live_next) if child in g]
    demand = len(groups)
    fresh = nae.F.fewest(p, [{"p": len(parents), "d": demand, "implied": implied}], None)[0]
    floor = 0 if implied else max(1, 3 - len(parents))
    event = {"child": child, "parents": parents, "inputs": inputs, "input_states": states, "implied": implied,
             "current_groups": groups, "raw_current_demand": demand, "current_fresh": fresh, "floor_fresh": floor}
    if independently_check:
        observed = demand_read(p.nbr, live_next, child)
        assert observed["raw_demand"] == demand
        event["current_overlap"] = observed
    return event


def full_target_counts(roster):
    counts, fresh = Counter(), {}
    for birth in roster:
        group = tuple(birth["parents"])
        counts[group] += 1
        assert group not in fresh or fresh[group] == birth["fresh"]
        fresh[group] = birth["fresh"]
    return counts, fresh


def first_decisions(stars, law, layer):
    nae, serial, _ = archive().libraries()
    p = nae.S.from_junctions(stars)
    roster = layer["births"]
    reference, fresh = full_target_counts(roster)
    reference_birth = {tuple(birth["parents"]): birth for birth in roster}
    multi, unary, _ = serial.moves(p, defaultdict(set))
    granted_multi = [g for g in reference if len(g) > 1]
    granted_unary = [g for g in reference if len(g) == 1]
    assert set(multi) == set(granted_multi) and set(unary) == set(granted_unary)
    observations = {}
    for parents in sorted(set(multi + unary + granted_multi + granted_unary)):
        probe = nae.S.from_junctions(stars)
        event = begun_event(probe, law, parents, independently_check=True)
        assert event["input_states"] == 1 << len(parents) and not event["implied"]
        observations[parents] = {
            **event, "roster_multiplicity": reference[parents], "complete_fresh": fresh.get(parents),
            "complete_overlap": reference_birth[parents]["overlap"],
        }
    indices = {g: i for i, g in enumerate(observations)}
    by_policy = {}
    for policy in POLICIES:
        by_policy[policy] = {}
        for arm in REPAIRS:
            joins = granted_multi if "G" in arm else multi
            singles = granted_unary if "U" in arm else unary
            picked = joins if policy == "joins-first" and joins else joins + singles
            by_policy[policy][arm] = [indices[g] for g in sorted(picked)]
    return {"events": list(observations.values()), "menus": by_policy}


def accept_event(p, children, event, law):
    count, group = event["current_fresh"], event["parents"]
    if len(group) + count < 3:
        return "subarity_stop"
    expected = 1 << len(group)
    if count == 0:
        expected = expected // 2 if law == "parity" else expected - 2
    if event["input_states"] != expected:
        return "non_knot_stop"
    child = event["child"]
    for v in group:
        children[v].add(child)
    fresh = list(range(p.nbits, p.nbits + count))
    p.nbits += count
    p.bits_of[child].extend(fresh)
    for d in fresh:
        p.owner[d] = [child]
    p.fresh[child] = count
    p._add_row(child)
    event["introduced"] = fresh
    return None


def roster_receipt(p, counts, first_outputs, mixed, children, reference, fresh, source_width):
    def rows(collection):
        return [(g, k) for g, k in sorted(collection.items()) if k]

    missing = reference - counts
    extra = counts - reference
    needs = Counter(v for g, count in missing.items() for v in g for _ in range(count))
    shortages = {v: n - len(p.loose(v)) for v, n in needs.items() if n > len(p.loose(v))}
    blocked = [(group, sorted(set.intersection(*(children[v] for v in group))))
               for group in missing if len(group) > 1 and set.intersection(*(children[v] for v in group))]
    wrong_fresh = [e for e in first_outputs if fresh[e["parents"]] != e["current_fresh"]]
    return {"missing": rows(missing), "extra": rows(extra), "missing_shortages": shortages,
            "prior_children_blocking_missing_multis": blocked,
            "matched_source_births": len(first_outputs), "wrong_matched_fresh": len(wrong_fresh),
            "marked_fresh_comparisons": [(e["child"], e["parents"], e["current_fresh"], fresh[e["parents"]])
                                         for e in wrong_fresh],
            "mixed_events": mixed, "remaining_source_loose": [len(p.loose(v)) for v in range(source_width)]}


def present_prefix(stars, law, policy, layer, target, seed):
    nae, serial, _ = archive().libraries()
    p = nae.S.from_junctions(stars)
    rng = random.Random(seed)
    children = defaultdict(set)
    reference, fresh = full_target_counts(layer["births"])
    source_width = len(stars)
    events, first, mixed = [], [], []
    seen = Counter()
    mark = None
    status = "right_censored"
    rejected = None
    for turn in range(SERIAL_CAP + 1):
        joins, unary, _ = serial.moves(p, children)
        pool = joins if policy == "joins-first" and joins else joins + unary
        if target is not None and mark is None:
            exhausted = [v for v in target if not p.loose(v)]
            previous = sorted(set.intersection(*(children[v] for v in target)))
            if exhausted or previous:
                mark = {"status": "permanently_lost", "after": turn, "exhausted_parents": exhausted,
                        "prior_common_children": previous}
        if not pool:
            status = "no_move"
            break
        if turn == SERIAL_CAP:
            if mark is None and target is not None:
                mark = {"status": "unmade_at_cap", "currently_eligible": target in pool}
            break
        group = rng.choice(pool)
        candidate = begun_event(p, law, group)
        candidate["pool_count"] = len(pool)
        candidate["target_listed"] = target in pool
        rejection = accept_event(p, children, candidate, law)
        if rejection:
            if rejection == "subarity_stop" and law == "parity":
                # Exhausting one or two remaining loose distinctions makes this the sole archival move.
                assert len(pool) == 1 and candidate["implied"] and not candidate["current_fresh"]
            status, rejected = rejection, candidate
            # The archived proposal was provisional and contributes no accepted event.
            p = nae.S.from_junctions(stars + [e["inputs"] + e["introduced"] for e in events])
            break
        events.append(candidate)
        if not any(v >= source_width for v in group):
            seen[group] += 1
            candidate["source_roster_comparison"] = "matched" if seen[group] <= reference[group] else "extra"
            if seen[group] <= reference[group]:
                first.append(candidate)
        elif any(v < source_width for v in group):
            mixed.append(candidate["child"])
            candidate["source_roster_comparison"] = "mixed"
        else:
            candidate["source_roster_comparison"] = "later_only"
        if target is not None and group == target:
            assert mark is None
            mark = {"status": "made", "at": turn + 1, "fresh": candidate["current_fresh"],
                    "demand": candidate["raw_current_demand"]}
    if target is not None and mark is None:
        mark = {"status": "unmade_at_stop"}
    return {"status": status, "events": events, "rejected_event": rejected, "marked": mark,
            "source_roster": roster_receipt(p, seen, first, mixed, children, reference, fresh, source_width)}


def witnessed_source_read(p, parents):
    """Independent local witness reading for a marked birth on a funded source."""
    parent_set = set(parents)
    center = parent_set | {v for u in parents for w in p.nbr[u] for v in p.nbr[w] if p.loose(v)}
    witnessed = {u: {w for w in p.nbr[u] if len(p.nbr[w] & center) > 1} for u in center}
    adjacent = {u: {v for v in center - {u} if witnessed[u] & witnessed[v]} for u in center}
    groups = []
    for k in range(len(center), 2, -1):
        for row in combinations(sorted(center), k):
            members = set(row)
            if members.isdisjoint(parent_set) or any(members < c for c in groups):
                continue
            if all(v in adjacent[u] for u, v in combinations(row, 2)) and not set.intersection(*(witnessed[v] for v in row)):
                groups.append(members)
    for u, v in combinations(sorted(center), 2):
        pair = {u, v}
        if not pair.isdisjoint(parent_set) and v in adjacent[u] and not any(pair <= c for c in groups):
            groups.append(pair)
    uses = Counter(v for g in groups for v in g)
    groups.extend({v} for v in parents for _ in range(len(p.loose(v)) - uses[v]))
    try:
        selected = groups.index(parent_set)
    except ValueError:
        raise AssertionError("a funded reference action should appear in its local witness reading") from None
    return demand_read(groups, range(len(groups)), selected)


def score_source(spec, order_rng, mark_rng):
    nae, serial, _ = archive().libraries()
    stars = nae.J.stars_from(spec["arities"], spec["meetings"])
    p = nae.S.from_junctions(stars)
    lawfulness = archive().source_lawfulness(p)
    physical = admission(p)
    arms = {}
    # The one common mark is chosen by structural parent set, not by slot labelling.
    opportunities = physical["multi_groups"] if physical["S0"] and any(v["lawful"] for v in lawfulness.values()) else []
    target = mark_rng.choice(opportunities) if opportunities else None
    seeds = {policy: order_rng.getrandbits(64) for policy in POLICIES}
    for law in LAWS:
        if not lawfulness[law]["lawful"]:
            arms[law] = {"status": "unlawful"}
            continue
        layer = independent_roster(stars, law, physical)
        arms[law] = layer
        if not physical["S0"]:
            assert layer["status"] == "stall"
            continue
        if layer["status"] != "formed":
            continue
        local = {}
        for birth in layer["births"]:
            group = tuple(birth["parents"])
            if group not in local:
                read = witnessed_source_read(p, group)
                implied, states = actual_implication(p, birth["inputs"], law)
                d = read["raw_demand"]
                f = 0 if implied and not d else max(1, 3 - len(group), d)
                local[group] = {**read, "implied_inputs": implied, "allowed_input_states": states, "fresh": f}
            birth["witnessed_source_read"] = local[group]
            assert birth["overlap"] == {k: v for k, v in local[group].items() if k in birth["overlap"]}
            assert birth["fresh"] == local[group]["fresh"]
        layer["first"] = first_decisions(stars, law, layer)
        layer["prefixes"] = {policy: present_prefix(stars, law, policy, layer, target, seeds[policy]) for policy in POLICIES}
        if law == "parity":
            for policy, trace in layer["prefixes"].items():
                replay, _, _ = serial.grow_serial(spec["arities"], spec["meetings"], len(trace["events"]),
                                                  seeds[policy], policy=policy)
                actual_stars = stars + [e["inputs"] + e["introduced"] for e in trace["events"]]
                assert replay.bits_of == actual_stars
    return {**spec, "source_stars": stars, "lawfulness": lawfulness, "physical": physical,
            "target": target, "target_opportunities": len(opportunities), "schedule_seeds": seeds, "arms": arms}


def fixed_controls(order_rng, mark_rng):
    controls = []
    for n in (4, 6):
        spec = {"draw": f"cycle/{n}", "stratum": "control", "old_knots": n, "arities": [3] * n,
                "meetings": sorted(tuple(sorted((v, (v + 1) % n))) for v in range(n))}
        result = score_source(spec, order_rng, mark_rng)
        ph = result["physical"]
        assert ph["S0"] and ph["S6_prime"]
        assert ph["S3"] == (n == 4) and ph["S4"] == (n == 6)
        assert all(result["arms"][law]["status"] == "formed" for law in LAWS)
        controls.append(result)
    return controls


def first_readout(rows, policy, arm):
    counts = Counter()
    arities = defaultdict(Counter)
    wrong_draws = 0
    for row in rows:
        first = row["first"]
        choices = [first["events"][i] for i in first["menus"][policy][arm]]
        wrong = False
        for event in choices:
            by_arity = arities[len(event["parents"])]
            count = event["floor_fresh"] if "F" in arm else event["current_fresh"]
            for tally in (counts, by_arity):
                tally["choices"] += 1
                tally["off_reference_roster"] += event["roster_multiplicity"] == 0
                tally["wrong_fresh"] += count != event["complete_fresh"]
                tally["known_current_demand_differs"] += event["raw_current_demand"] != event["complete_overlap"]["raw_demand"]
            wrong |= count != event["complete_fresh"]
        wrong_draws += wrong
    return {"draws": len(rows), "draws_with_wrong_fresh": wrong_draws, "totals": dict(counts),
            "by_parent_count": {arity: dict(c) for arity, c in arities.items()}}


def prefix_readout(rows, policy):
    selected = [r["prefixes"][policy] for r in rows]
    counts = Counter()
    for trace in selected:
        receipt = trace["source_roster"]
        counts["events"] += len(trace["events"])
        counts["prefixes_with_extra_source_group"] += bool(receipt["extra"])
        counts["prefixes_with_mixed_groups"] += bool(receipt["mixed_events"])
        counts["prefixes_with_any_wrong_fresh"] += bool(receipt["wrong_matched_fresh"])
        counts["matched_source_births"] += receipt["matched_source_births"]
        counts["wrong_fresh_at_matched_source_births"] += receipt["wrong_matched_fresh"]
        complete = not receipt["missing"] and not receipt["extra"]
        counts["source_roster_complete_without_extras"] += complete
        counts["source_roster_and_fresh_complete"] += complete and not receipt["wrong_matched_fresh"]
        counts["source_roster_completion_permanently_impossible"] += bool(receipt["missing_shortages"] or receipt["prior_children_blocking_missing_multis"])
    outcomes = Counter(t["status"] for t in selected)
    marked = Counter(t["marked"]["status"] for t in selected if t["marked"] is not None)
    return {"prefixes": len(selected), "outcomes": dict(outcomes), "marked_outcomes": dict(marked), **counts}


def describe(draws):
    summary = {"draws": len(draws), "identification": dict(Counter(
        "identified_hypotheses_hold" if all(d["physical"][k] for k in ("S0", "S3", "S4", "S6_prime"))
        else "fails_S3_or_S4" if not d["physical"]["S3"] or not d["physical"]["S4"]
        else "other_hypothesis_fails" for d in draws)), "laws": {}}
    for law in LAWS:
        rows = [d["arms"][law] for d in draws if d["arms"][law]["status"] == "formed"]
        outside = [d["arms"][law] for d in draws if d["arms"][law]["status"] == "formed"
                   and not (d["physical"]["S3"] and d["physical"]["S4"])]
        complete = Counter(len(b["parents"]) for row in rows for b in row["births"])
        summary["laws"][law] = {
            "sources_by_status": dict(Counter(d["arms"][law]["status"] for d in draws)),
            "complete_births_by_parent_count": dict(complete), "funded_outside_S3_or_S4": len(outside),
            "witnessed_source_exact_raw_demand": sum(b["demand"] == b["witnessed_source_read"]["raw_demand"]
                                                     for row in rows for b in row["births"]),
            "witnessed_source_exact_fresh": sum(b["fresh"] == b["witnessed_source_read"]["fresh"]
                                                for row in rows for b in row["births"]),
            "first_choices": {policy: {arm: first_readout(rows, policy, arm) for arm in REPAIRS} for policy in POLICIES},
            "first_choices_outside_S3_or_S4": {policy: {arm: first_readout(outside, policy, arm) for arm in ("A0", "F")}
                                              for policy in POLICIES},
            "A0_random_prefixes": {policy: prefix_readout(rows, policy) for policy in POLICIES},
        }
    return summary


def metadata_summary(draws):
    diagnosed = defaultdict(list)
    for d in draws:
        p, n = (d["arms"][law] for law in LAWS)
        if "prefixes" not in p or "prefixes" not in n:
            continue
        for policy in POLICIES:
            pt, nt = p["prefixes"][policy], n["prefixes"][policy]
            if pt == nt:
                continue
            p_events = pt["events"] + ([pt["rejected_event"]] if pt["rejected_event"] else [])
            n_events = nt["events"] + ([nt["rejected_event"]] if nt["rejected_event"] else [])
            at = next((i for i, (a, b) in enumerate(zip(p_events, n_events), 1) if a != b),
                      min(len(p_events), len(n_events)) + 1)
            diagnosed[policy].append({"draw": d["draw"], "parity_status": pt["status"], "nae_status": nt["status"],
                                      "first_differing_decision": at, "same_marked_outcome": pt["marked"] == nt["marked"]})
    return {"overall": describe(draws),
            "cross_law_prefix_disagreements": dict(diagnosed),
            "by_weighting": {kind: describe([d for d in draws if d["stratum"] == kind]) for kind in ("tree", "unicyclic")},
            "by_weighting_and_size": {kind: {n: {law: dict(Counter(d["arms"][law]["status"] for d in draws
                  if d["stratum"] == kind and d["old_knots"] == n)) for law in LAWS} for n in range(4, 9)}
                                      for kind in ("tree", "unicyclic")}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, help="Disposable replay of this many leading draws")
    args = parser.parse_args()
    if args.limit is not None and args.output == OUT:
        parser.error("use a scratch output with --limit")
    order_rng, mark_rng = random.Random(SEEDS["order"]), random.Random(SEEDS["mark"])
    draws = []
    for i, spec in enumerate(source_draws()):
        if args.limit is not None and i >= args.limit:
            break
        draws.append(score_source(spec, order_rng, mark_rng))
    controls = fixed_controls(order_rng, mark_rng)
    data = {"schema_version": 1, "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(), "draws_per_size": PER_SIZE,
            "maximum_serial_decisions": SERIAL_CAP, "seeds": SEEDS, "draws": draws,
            "controls": controls, "summary": metadata_summary(draws)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as stream:
        json.dump(data, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")


if __name__ == "__main__":
    main()
