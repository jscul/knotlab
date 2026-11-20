"""Frozen sample of component transfer, physical witnesses and unary lineages."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache, lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import random
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "sample.json"
DESIGN = ROOT / "research/GENERATORS-20261120-001/preregistration.md"
SEEDS = {"tree": 20261120701, "augmented_tree": 20261120702}
LAWS = ("parity", "nae")
PER_SIZE = 48
LAYERS = 3
CAP = 128


def load(name, source):
    spec = spec_from_file_location(name, ROOT / "experiments" / source)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@cache
def libraries():
    prior = load("generator_sample_source", "FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/sample_starts.py")
    end = load("generator_sample_end", "ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py")
    nae, _, _ = prior.libraries()
    return prior, end, nae


def source_draws():
    for name, seed in SEEDS.items():
        rng = random.Random(seed)
        for n in range(4, 9):
            for i in range(PER_SIZE):
                word = [rng.randrange(n) for _ in range(n - 2)]
                graph = nx.from_prufer_sequence(word)
                added = None
                if name == "augmented_tree":
                    added = rng.choice([g for g in combinations(range(n), 2) if not graph.has_edge(*g)])
                    graph.add_edge(*added)
                meetings = sorted(tuple(sorted(g)) for g in graph.edges)
                spare = [int(rng.randrange(4) == 0) for _ in range(n)]
                sizes = [max(3, graph.degree(v)) + spare[v] for v in range(n)]
                yield {"draw": f"{name}/{n}/{i:02d}", "weighting": name, "source_knots": n,
                       "prufer": word, "added_meeting": added, "extra_loose": spare,
                       "meetings": meetings, "arities": sizes}


def graph_from_witnesses(opens, rows):
    pairs = Counter(pair for block in rows.values() for pair in combinations(block, 2))
    graph = {v: set() for v in opens}
    for v, w in pairs:
        graph[v].add(w)
        graph[w].add(v)
    return graph, pairs


def components(graph):
    remaining = set(graph)
    partition = []
    while remaining:
        root = min(remaining)
        work = [root]
        remaining.remove(root)
        for v in work:
            unseen = graph[v] & remaining
            work.extend(unseen)
            remaining.difference_update(unseen)
        partition.append(tuple(sorted(work)))
    return tuple(partition)


def cycle_word(part, graph, opens, multiplicities):
    start = min(part)
    words = []
    for first in sorted(graph[start]):
        walk = [start, first]
        while len(walk) < len(part):
            following, = graph[walk[-1]] - {walk[-2]}
            walk.append(following)
        word = tuple((opens[v], multiplicities[tuple(sorted((v, w)))])
                     for v, w in zip(walk, walk[1:] + [start], strict=True))
        words.extend(word[i:] + word[:i] for i in range(len(word)))
    return min(words)


def recognized(opens, graph, multiplicities, witness_rows):
    comp = components(graph)
    cycles, endpoints = [], []
    for part in comp:
        degrees = [len(graph[v]) for v in part]
        if len(part) >= 3 and set(degrees) == {2}:
            cycles.append({"members": part, "loose_and_witness_word": cycle_word(part, graph, opens, multiplicities),
                           "has_higher_witness": any(len(set(row).intersection(part)) >= 3 for row in witness_rows.values())})
        if degrees.count(1) == 2 and max(degrees) <= 2:
            endpoints.extend(v for v in part if len(graph[v]) == 1 and opens[v] == 2)
    return {"components": comp, "cycles": cycles, "two_loose_path_ends": endpoints}


def readings(p, prior_births):
    _, end, _ = libraries()
    physical = end.from_stars(p.bits_of)
    opens = physical.opens
    assert opens == {v: len(p.loose(v)) for v in p.live if p.loose(v)}

    # The holdings reader counts common holders directly, including spent holders.
    literal_pairs = Counter({(v, w): len(p.nbr[v] & p.nbr[w]) for v, w in combinations(opens, 2)
                             if p.nbr[v] & p.nbr[w]})
    full_graph = {v: set() for v in opens}
    for v, w in literal_pairs:
        full_graph[v].add(w)
        full_graph[w].add(v)
    witness_rows = {i: tuple(sorted(adj & opens.keys())) for i, adj in enumerate(p.nbr) if len(adj & opens.keys()) >= 2}
    full = recognized(opens, full_graph, literal_pairs, witness_rows)

    # The end reader receives just live holders, loose counts and witnessed sets.
    observed_graph, observed_pairs = graph_from_witnesses(opens, witness_rows)
    witnessed = recognized(opens, observed_graph, observed_pairs, witness_rows)
    assert literal_pairs == observed_pairs and full == witnessed and full_graph == end.neighbors(physical)
    if prior_births is not None:
        from_parentage = defaultdict(list)
        for birth in prior_births:
            if birth["fresh"]:
                for v in birth["parents"]:
                    from_parentage[v].append(birth["knot"])
        actual_parent_rows = {v: tuple(sorted(row)) for v, row in from_parentage.items() if len(row) >= 2}
        assert witness_rows == actual_parent_rows
        assert all(v not in opens for v in witness_rows)

    erased_rows = {v: row for v, row in witness_rows.items() if v in opens}
    erased_graph, erased_pairs = graph_from_witnesses(opens, erased_rows)
    erased = recognized(opens, erased_graph, erased_pairs, erased_rows)
    return physical, {"loose": opens, "witnesses": witness_rows,
                      "full_holdings": full, "witnessed_end": witnessed, "erase_spent_witnesses": erased,
                      "candidate_pairs": len(literal_pairs), "pairs_after_erasing_spent": len(erased_pairs)}


def literal_step(p, law, plan):
    _, _, nae = libraries()
    old = len(p.bits_of)
    rule = nae.parity_rule(nae.F.fewest) if law == "parity" else nae.nae_rule(nae.F.fewest)
    fresh_receipts = {}

    def record(pres, info, rng):
        counts = rule(pres, info, rng)
        solver = nae._solver(pres, old) if law == "nae" else None
        try:
            for row, count in zip(info, counts, strict=True):
                width = row["p"]
                allowed = (1 << width) >> row["implied"] if law == "parity" else None
                if solver is not None and width <= 10:
                    marks = pres.bits_of[row["j"]][:width]
                    allowed = sum(solver.solve(assumptions=[d + 1 if word >> i & 1 else -(d + 1)
                                                           for i, d in enumerate(marks)]) for word in range(1 << width))
                    assert allowed == (1 << width) - (0 if count else 2)
                fresh_receipts[row["j"]] = (width, row["d"], count, row["implied"], allowed)
        finally:
            if solver is not None:
                solver.delete()
        return counts

    result = p.step(record)
    if plan.status == "stall":
        assert result is None and not fresh_receipts and len(p.bits_of) == old
        return []
    assert result["new"] == len(plan.parents) == len(fresh_receipts)
    births = []
    for v, (arity, demand, fresh, implied, allowed) in fresh_receipts.items():
        inputs, introduced = p.bits_of[v][:arity], p.bits_of[v][arity:]
        parents = tuple(sorted(next(holder for holder in p.owner[d] if holder != v) for d in inputs))
        assert len(set(parents)) == arity and all(holder < old for holder in parents)
        assert fresh == len(introduced) and set(introduced) == set(p.loose(v))
        births.append({"knot": v, "parents": parents, "inputs": inputs, "fresh": fresh, "introduced": introduced,
                       "demand": demand, "implied": implied, "input_projection_size": allowed})
    assert Counter((b["parents"], b["fresh"], b["demand"]) for b in births) == Counter(
        zip(plan.parents, plan.fresh, plan.demand, strict=True))
    assert all(b["implied"] == plan.implied for b in births)
    return births


@lru_cache(maxsize=1024)
def reduced_lawfulness(stars):
    prior, _, nae = libraries()
    return prior.source_lawfulness(nae.S.from_junctions(stars))


def physical_isolation(stars, omitted, law, part_end, solo):
    """Retain every shared distinction, erasing only loose slots outside this part."""
    _, end, nae = libraries()
    trimmed = tuple(tuple(d for d in support if d not in omitted) for support in stars)
    too_small = [v for v, support in enumerate(trimmed) if len(support) < 3]
    if too_small:
        return {"status": "arity_rejected", "short_supports": too_small}
    if not reduced_lawfulness(trimmed)[law]["lawful"]:
        return {"status": "projection_rejected"}
    restricted = end.from_stars(trimmed)
    assert restricted == part_end
    p = nae.S.from_junctions(trimmed)
    turns = literal_step(p, law, solo)
    if any(len(b["parents"]) + b["fresh"] < 3 for b in turns):
        assert law == "parity" and solo.implied and len(turns) == 1
        return {"status": "legacy_subarity_stop", "rejected_birth": turns[0]}
    return {"status": "physically_replayed", "births": turns}


def compare_parts(stars, old_end, old_comp, following, births, law):
    _, end, _ = libraries()
    old_pairs = {(v, w) for v, seen in end.neighbors(old_end).items() for w in seen if v < w}
    covered_pairs = {pair for b in births for pair in combinations(b["parents"], 2)}
    assert covered_pairs == old_pairs
    owner = {v: i for i, part in enumerate(old_comp) for v in part}
    new_comp = following["witnessed_end"]["components"]
    new_members = {v: i for i, part in enumerate(new_comp) for v in part}
    to_new = defaultdict(set)
    from_old = defaultdict(set)
    by_origin = defaultdict(list)
    cross = []
    incidence_count = Counter(d for support in stars for d in support)
    loose_by_holder = {v: {d for d in stars[v] if incidence_count[d] == 1} for v in old_end.opens}
    for b in births:
        parents_from = {owner[v] for v in b["parents"]}
        if len(parents_from) != 1:
            cross.append(b["knot"])
        for i in parents_from:
            by_origin[i].append(b)
            if b["fresh"]:
                dest = new_members[b["knot"]]
                from_old[dest].add(i)
                to_new[i].add(dest)
    records = []
    for i, group in enumerate(old_comp):
        part_end = end.restricted(old_end, group)
        solo = end.step(part_end, law, max_births=CAP)
        assert solo.status == "extend"
        realized = by_origin[i]
        actual = Counter((b["parents"], b["demand"], b["fresh"]) for b in realized)
        solo_budget = Counter(zip(solo.parents, solo.demand, solo.fresh, strict=True))
        same_parents_and_demands = Counter((b["parents"], b["demand"]) for b in realized) == Counter(
            zip(solo.parents, solo.demand, strict=True))
        assert same_parents_and_demands
        if solo_budget != actual:
            assert law == "parity" and solo.implied and len(old_comp) > 1 and len(realized) == 1 and realized[0]["fresh"] > 0
        omitted = set().union(*(row for v, row in loose_by_holder.items() if owner[v] != i))
        stripped = physical_isolation(stars, omitted, law, part_end, solo) if omitted else {"status": "whole_part"}
        stripped["erased_loose"] = sorted(omitted)
        closing_arity = len(solo.parents[0]) if solo.implied else None
        records.append({"old_part": group, "successor_parts": [new_comp[j] for j in sorted(to_new[i])],
                        "actual_births": [b["knot"] for b in realized], "isolated_parentage_and_demand_agree": same_parents_and_demands,
                        "part_alone_fresh_agree": solo_budget == actual, "part_alone_fresh": solo.fresh,
                        "part_alone_implied": solo.implied, "part_alone_closing_arity": closing_arity,
                        "physical_reduction": stripped})
    return {"parts": records, "cross_part_births": cross,
            "old_pairs_covered_by_a_birth": len(covered_pairs),
            "split_old_parts": sum(len(to_new[i]) > 1 for i in range(len(old_comp))),
            "merged_new_parts": sum(len(from_old[j]) > 1 for j in range(len(new_comp))),
            "vanished_old_parts": sum(not to_new[i] for i in range(len(old_comp))),
            "new_parts_without_old": sum(not from_old[j] for j in range(len(new_comp)))}


def unary_receipt(old_end, before, after, births, chain_lengths, earlier_parents):
    occurrences = Counter(v for b in births for v in b["parents"])
    assert occurrences == Counter(old_end.opens)
    reused = sorted(earlier_parents & occurrences.keys())
    earlier_parents.update(occurrences)
    unary = defaultdict(list)
    newborns_without_siblings = []
    positive_chain = {}
    for b in births:
        is_alone = all(occurrences[v] == 1 for v in b["parents"])
        if is_alone:
            newborns_without_siblings.append(b["knot"])
        if len(b["parents"]) == 1:
            parent, = b["parents"]
            unary[parent].append(b["knot"])
            positive_chain[b["knot"]] = chain_lengths.get(parent, 0) + 1
    positive_lones = {b["knot"] for b in births if b["fresh"] and b["knot"] in newborns_without_siblings}
    assert positive_lones == {part[0] for part in after["witnessed_end"]["components"] if len(part) == 1}
    old_lones = [g[0] for g in before["witnessed_end"]["components"] if len(g) == 1]
    assert all(len(unary[v]) == old_end.opens[v] for v in old_lones)
    return positive_chain, {"unary_births_by_parent": dict(unary), "old_singleton_parents": old_lones,
                            "newborns_without_siblings": newborns_without_siblings,
                            "actual_parents_reused_at_later_sizes": reused, "unary_chain_length": positive_chain}


def plan_receipt(plan):
    return {"status": plan.status, "proposed_parents": plan.parents, "proposed_fresh": plan.fresh,
            "provisional_demand": plan.demand, "shortages": plan.shortages,
            "planned_births_lower": plan.planned_births_lower, "implied_sole_birth": plan.implied}


def verify_following(plan, births, observed_end):
    _, end, _ = libraries()
    available = defaultdict(list)
    for b in births:
        available[b["parents"], b["fresh"], b["demand"]].append(b["knot"])
    translate = {i: available[attrs].pop() for i, attrs in enumerate(zip(plan.parents, plan.fresh, plan.demand, strict=True))}
    projected = end.End({translate[i]: loose for i, loose in plan.end.opens.items()},
                        tuple(tuple(translate[i] for i in block) for block in plan.end.blocks))
    assert projected == observed_end


def history(stars, law, lawful):
    _, end, nae = libraries()
    if not lawful:
        return {"terminal": "unlawful_source", "frames": [], "transitions": []}
    p = nae.S.from_junctions(stars)
    old_end, before = readings(p, None)
    frames = [before]
    transitions = []
    reused_parents = set()
    chains = {}
    terminal = "formation_limit"
    for age in range(LAYERS):
        assert len(old_end.opens) <= CAP
        old_comp = before["witnessed_end"]["components"]
        plan = end.step(old_end, law, max_births=CAP)
        attempt = {"source_age": age, "plan": plan_receipt(plan), "births": []}
        transitions.append(attempt)
        if plan.status == "closed":
            terminal = "closed"
            break
        if plan.status == "cap":
            terminal = "birth_cap"
            break
        old_stars = tuple(map(tuple, p.bits_of))
        births = literal_step(p, law, plan)
        if plan.status == "stall":
            terminal = "stall"
            attempt["part_alone_plans"] = [plan_receipt(end.step(end.restricted(old_end, part), law, max_births=CAP))
                                           for part in old_comp]
            break

        if any(len(b["parents"]) + b["fresh"] < 3 for b in births):
            assert law == "parity" and plan.implied and len(births) == 1
            terminal = "legacy_subarity_stop"
            attempt["rejected_legacy_closing_birth"] = births[0]
            break
        new_end, after = readings(p, births)
        verify_following(plan, births, new_end)
        part_reads = compare_parts(old_stars, old_end, old_comp, after, births, law)
        chains, unary = unary_receipt(old_end, before, after, births, chains, reused_parents)
        attempt.update(births=births, component_correspondence=part_reads, unary=unary)
        frames.append(after)
        if not new_end.opens:
            terminal = "closed"
            break
        old_end, before = new_end, after
    return {"terminal": terminal, "frames": frames, "transitions": transitions}


def score_source(spec):
    prior, _, nae = libraries()
    stars = nae.J.stars_from(spec["arities"], spec["meetings"])
    lawful = prior.source_lawfulness(nae.S.from_junctions(stars))
    return {**spec, "source_stars": stars, "lawfulness": lawful,
            "laws": {law: history(stars, law, lawful[law]["lawful"]) for law in LAWS}}


def check_recoding(draws):
    _, _, nae = libraries()
    certificates = []
    for kind in SEEDS:
        chosen = next((d for d in draws if d["weighting"] == kind and len(d["laws"]["parity"]["frames"]) >= 2), None)
        if chosen is None:
            continue
        births = chosen["laws"]["parity"]["transitions"][0]["births"]
        stars = chosen["source_stars"] + [b["inputs"] + b["introduced"] for b in births]
        hi = max(d for star in stars for d in star)
        n = len(stars)
        renamed = [sorted(hi - d for d in star) for star in reversed(stars)]
        _, observation = readings(nae.S.from_junctions(renamed), None)
        prior = chosen["laws"]["parity"]["frames"][1]

        def permute(ids):
            return tuple(sorted(n - 1 - v for v in ids))

        for reader in ("full_holdings", "witnessed_end", "erase_spent_witnesses"):
            old, new = prior[reader], observation[reader]
            assert sorted(permute(comp) for comp in old["components"]) == sorted(new["components"])
            assert permute(old["two_loose_path_ends"]) == tuple(sorted(new["two_loose_path_ends"]))
            assert sorted((permute(c["members"]), c["loose_and_witness_word"], c["has_higher_witness"]) for c in old["cycles"]) == sorted(
                (c["members"], c["loose_and_witness_word"], c["has_higher_witness"]) for c in new["cycles"])
        certificates.append({"draw": chosen["draw"], "age": 1, "renamed_holders": n, "renamed_distinctions": hi + 1})
    return certificates


def summarize(draws, law):
    rows = [d["laws"][law] for d in draws]
    ages = {}
    for age in range(LAYERS + 1):
        frames = [r["frames"][age] for r in rows if len(r["frames"]) > age]
        plans = [r["transitions"][age] for r in rows if len(r["transitions"]) > age]
        realized = [p for p in plans if "component_correspondence" in p]
        parts = [pt for p in realized for pt in p["component_correspondence"]["parts"]]
        births = [b for p in realized for b in p["births"]]
        unary = [p["unary"] for p in realized]
        ages[age] = {
            "reached_frames": len(frames), "empty_ends": sum(not f["loose"] for f in frames),
            "max_live_in_frame": max((len(f["loose"]) for f in frames), default=0),
            "live_parts": sum(len(f["witnessed_end"]["components"]) for f in frames),
            "frames_with_separate_parts": sum(len(f["witnessed_end"]["components"]) > 1 for f in frames),
            "full_and_witnessed_agree": sum(f["full_holdings"] == f["witnessed_end"] for f in frames),
            "erased_spent_changes_component_partition": sum(f["erase_spent_witnesses"]["components"] != f["witnessed_end"]["components"] for f in frames),
            "all_candidate_pairs": sum(f["candidate_pairs"] for f in frames),
            "candidate_pairs_without_spent_witnesses": sum(f["pairs_after_erasing_spent"] for f in frames),
            "cycle_parts": sum(len(f["witnessed_end"]["cycles"]) for f in frames),
            "cycle_parts_without_higher_witness": sum(not c["has_higher_witness"] for f in frames for c in f["witnessed_end"]["cycles"]),
            "two_loose_path_ends": sum(len(f["witnessed_end"]["two_loose_path_ends"]) for f in frames),
            "path_ends_without_spent_witnesses": sum(len(f["erase_spent_witnesses"]["two_loose_path_ends"]) for f in frames),
            "attempt_statuses": dict(Counter(p["plan"]["status"] for p in plans)),
            "lawful_materialized_transitions": len(realized), "positive_transitions": sum(any(b["fresh"] for b in p["births"]) for p in realized),
            "realized_births": len(births), "birth_arity_distribution": dict(Counter(len(b["parents"]) for b in births)),
            "zero_fresh_births": sum(not b["fresh"] for b in births),
            "cross_part_births": sum(len(p["component_correspondence"]["cross_part_births"]) for p in realized),
            "old_pairs_covered_by_a_birth": sum(p["component_correspondence"]["old_pairs_covered_by_a_birth"] for p in realized),
            "split_old_parts": sum(p["component_correspondence"]["split_old_parts"] for p in realized),
            "merged_new_parts": sum(p["component_correspondence"]["merged_new_parts"] for p in realized),
            "vanished_old_parts": sum(p["component_correspondence"]["vanished_old_parts"] for p in realized),
            "new_parts_without_old": sum(p["component_correspondence"]["new_parts_without_old"] for p in realized),
            "continued_parts": sum(bool(pt["successor_parts"]) for pt in parts),
            "part_alone_comparisons": len(parts), "part_alone_parentage_demand_agrees": sum(pt["isolated_parentage_and_demand_agree"] for pt in parts),
            "part_alone_fresh_disagrees": sum(not pt["part_alone_fresh_agree"] for pt in parts),
            "part_alone_fresh_disagrees_by_closing_arity": dict(Counter(pt["part_alone_closing_arity"] for pt in parts
                                                                       if not pt["part_alone_fresh_agree"])),
            "physical_reduction_statuses": dict(Counter(pt["physical_reduction"]["status"] for pt in parts)),
            "physical_reduction_fresh_disagrees": sum(pt["physical_reduction"]["status"] == "physically_replayed"
                                                       and not pt["part_alone_fresh_agree"] for pt in parts),
            "pure_local_parts_blocked_by_whole_stall": sum(q["status"] == "extend" for p in plans for q in p.get("part_alone_plans", ())),
            "singleton_live_parents": sum(len(u["old_singleton_parents"]) for u in unary),
            "newborns_without_siblings": sum(len(u["newborns_without_siblings"]) for u in unary),
            "same_parent_multiple_unaries": sum(len(offs) > 1 for u in unary for offs in u["unary_births_by_parent"].values()),
            "parent_reused_at_later_size": sum(len(u["actual_parents_reused_at_later_sizes"]) for u in unary),
            "terminal_unary_chain_lengths": dict(Counter(k for u in unary for k in u["unary_chain_length"].values())),
        }
    physical_source_funded = sum(bool(r["transitions"]) and r["transitions"][0]["plan"]["status"] == "extend" for r in rows)
    return {"draws": len(draws), "lawful_sources": sum(d["lawfulness"][law]["lawful"] for d in draws),
            "physically_funded_source_steps": physical_source_funded, "terminal_statuses": dict(Counter(r["terminal"] for r in rows)),
            "by_age": ages}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, help="Replay only the leading draws into scratch")
    args = parser.parse_args()
    if args.limit is not None and args.output == OUT:
        parser.error("use --output for a disposable replay")
    data = []
    for i, source in enumerate(source_draws()):
        if args.limit is not None and i >= args.limit:
            break
        data.append(score_source(source))
    strata = {weighting: [d for d in data if d["weighting"] == weighting] for weighting in SEEDS}
    record = {"schema_version": 1, "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(), "seeds": SEEDS,
              "max_layers": LAYERS, "max_births": CAP, "draws_per_size": PER_SIZE, "draws": data,
              "recoding_checks": check_recoding(data), "summary": {"all": {law: summarize(data, law) for law in LAWS},
                          "by_weighting": {w: {law: summarize(draws, law) for law in LAWS} for w, draws in strata.items()},
                          "by_weighting_and_size": {w: {n: {law: dict(Counter(d["laws"][law]["terminal"] for d in draws
                                  if d["source_knots"] == n)) for law in LAWS} for n in range(4, 9)} for w, draws in strata.items()}}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(record, f, sort_keys=True, separators=(",", ":"))
        f.write("\n")


if __name__ == "__main__":
    main()
