"""Replay the guarded ring preparations one physical birth at a time."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys

import networkx as nx
from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research" / HERE.parent.name / "design.md"
DESIGN_SHA256 = "afaae4ecdd0abbe14fa8a9b7dc415dff62d3b411aa6483c7d303ef848e658f1d"
RINGS = ROOT / ("experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/"
                "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B-E001_clocks/rings.py")
CUTS = (5, 6, 9, 10)
TICK_DEPTHS = (6, 10)
LAWS = ("parity", "nae")


spec = spec_from_file_location("guarded_ring_clock_reference", RINGS)
rings = module_from_spec(spec)
sys.modules[spec.name] = rings
spec.loader.exec_module(rings)
physical = rings.fixture()
from end_operator import End, step


@dataclass(frozen=True)
class Preparation:
    name: str
    source: tuple
    windings: tuple
    attachment: int | None = None
    consumer: int | None = None


def preparations():
    clean, pure = rings.attached_ring(8, (0,))
    same, same_windings = rings.attached_ring(8, (0,), 3)
    other, other_windings = rings.attached_ring(8, (0,), 2)
    added_two, = set(same[2]) - set(clean[2])
    added_four, = set(same[4]) - set(clean[4])
    supply = list(clean)
    supply[2], supply[4] = (*clean[2], added_two), (*clean[4], added_four)
    short = list(same)
    short[2] = tuple(d for d in same[2] if d != added_two)
    return (
        Preparation("bare", clean, pure),
        Preparation("attachment_3", same, same_windings, 3, 8),
        Preparation("attachment_2", other, other_windings, 2, 8),
        Preparation("supply_only", tuple(supply), tuple(rings.rings_on(tuple(range(8)), {0: 1, 2: 1, 4: 1}))),
        Preparation("shortfall", tuple(short), same_windings, 3, 8),
    )


class Holdings:
    """Read depth, actual input holders and loose distinctions from the supports."""

    def __init__(self, stars, source_count):
        self.stars = stars
        self.source_count = source_count
        self.owners, self.neighbors, self.loose = physical.incidence(stars)
        self.depth = nx.multi_source_dijkstra_path_length(self.neighbors, range(source_count))
        assert len(self.depth) == len(stars)
        self.incoming = [{} for _ in stars]
        self.shared_at_source = Counter()
        for distinction, owners in self.owners.items():
            if len(owners) == 1:
                continue
            parent, child = sorted(owners, key=self.depth.__getitem__)
            if self.depth[child] == 0:
                self.shared_at_source.update(owners)
            else:
                assert self.depth[child] == self.depth[parent] + 1
                assert parent not in self.incoming[child]
                self.incoming[child][parent] = distinction
        self.ancestry = {k: frozenset((k,)) for k in range(source_count)}
        for k in sorted(self.depth, key=self.depth.__getitem__):
            if self.depth[k] > 0:
                assert self.incoming[k]
                self.ancestry[k] = frozenset().union(*(self.ancestry[p] for p in self.incoming[k]))
        self.loose_count = sum(map(len, self.loose.values()))

    def restored_plan(self, law):
        """Read the ordinary plan at the least unfinished depth and subtract actual writes."""
        depth = min(self.depth[k] for k in self.loose)
        old = [k for k in self.depth if self.depth[k] == depth]
        supply = {
            k: len(self.stars[k]) - self.shared_at_source[k] - len(self.incoming[k])
            for k in old
        }
        witnesses = [k for k, d in self.depth.items() if d == max(0, depth - 1)]
        blocks = tuple(tuple(supply.keys() & self.neighbors[w].keys()) for w in witnesses)
        plan = step(End(supply, blocks), law)
        pending = Counter(zip(plan.parents, plan.fresh, strict=True))
        for k, d in self.depth.items():
            if d == depth + 1:
                parents = tuple(sorted(self.incoming[k]))
                item = parents, len(self.stars[k]) - len(parents)
                assert pending[item] > 0
                pending[item] -= 1
        pending = +pending
        if plan.status == "extend":
            need = Counter()
            for (parents, _), count in pending.items():
                for parent in parents:
                    need[parent] += count
            assert need == {k: len(self.loose[k]) for k in old if k in self.loose}
        return depth, plan, pending


def signature(birth):
    return birth.parents, len(birth.fresh)


def admitted(pending, joins_first):
    multi = {item for item in pending if len(item[0]) > 1}
    return multi if joins_first and multi else pending.keys()


class SerialReplay:
    """Write one birth with named physical inputs and check both sides of the write."""

    def __init__(self, case, frame, law, ticks_before=0):
        self.case = case
        self.stage = Holdings(frame, len(case.source))
        self.law = law
        self.ticks = ticks_before
        self.solver = None

    def __enter__(self):
        if self.law == "nae":
            self.solver = Minisat22()
            for star in self.stage.stars:
                physical.nae_add(self.solver, star)
        return self

    def __exit__(self, *exc):
        if self.solver is not None:
            self.solver.delete()

    def write(self, birth, joins_first, *, tick=False, chosen=None, guard=None):
        before = self.stage
        depth, plan, pending = before.restored_plan(self.law) if guard is None else guard
        assert plan.status == "extend" and not plan.implied
        parents, fresh_count = signature(birth)
        assert signature(birth) in admitted(pending, joins_first)
        eligible = tuple(tuple(before.loose[parent]) for parent in parents)
        inputs = birth.inputs if chosen is None else chosen
        assert len(inputs) == len(set(inputs)) == len(parents)
        assert all(d in loose for d, loose in zip(inputs, eligible, strict=True))
        assert all(before.owners[d] == [p] for p, d in zip(parents, inputs, strict=True))
        # Connected parity gives free inputs on each proper subset of the loose
        # distinctions. A fresh distinction extends every old allowed state.
        assert len(inputs) < before.loose_count
        assert fresh_count >= 1 and len(parents) + fresh_count >= 3
        input_words = 1 << len(inputs)
        if self.law == "nae":
            assert physical.nae_words(self.solver, inputs) == tuple(range(input_words))
        elif tick:
            assert physical.parity_words(before.stars, inputs) == tuple(range(input_words))
        first_fresh = max(before.owners) + 1
        fresh = tuple(range(first_fresh, first_fresh + fresh_count))
        assert not before.owners.keys() & set(fresh)
        support = (*inputs, *fresh)
        new = len(before.stars)
        if self.law == "nae":
            physical.nae_add(self.solver, support)
            if tick:
                assert physical.nae_words(self.solver, support) == physical.expected_words(self.law, len(support))
        elif tick:
            assert physical.parity_words(before.stars + (support,), support) == physical.expected_words(self.law, len(support))
        self.stage = Holdings(before.stars + (support,), before.source_count)
        assert self.stage.depth[new] == depth + 1
        assert self.stage.incoming[new] == dict(zip(parents, inputs, strict=True))
        assert set(self.stage.loose[new]) == set(fresh)
        assert self.stage.loose_count == before.loose_count - len(inputs) + len(fresh)
        assert all(self.stage.owners[d] == [p, new] for p, d in zip(parents, inputs, strict=True))
        self.ticks += int(tick)
        return {
            "birth": new + 1 - before.source_count,
            "depth": depth + 1,
            "knot": new,
            "ordinary_child": birth.knot,
            "parents": parents,
            "eligible_slots_at_parents": eligible,
            "consumed": inputs,
            "fresh": fresh,
            "loose_before": before.loose_count,
            "loose_after": self.stage.loose_count,
            "permitted_input_words": input_words,
            "original_ancestry": sorted(self.stage.ancestry[new]),
            "consumer": self.case.consumer in self.stage.ancestry[new],
            "strict_ticks": self.ticks - int(tick),
            "inclusive_ticks": self.ticks,
        }


def known_clusters(windings):
    return tuple(rings.collect_model_labels(winding) for winding in windings)


def match_ring(windings, old_indices, age, births, *, whole):
    by_parents = {frozenset(birth.parents): birth for birth in births}
    assert len(by_parents) == len(births)
    matches = tuple(rings.advance_indices(winding, old, by_parents, age, whole)
                    for winding, old in zip(windings, old_indices, strict=True))
    current = tuple(match[0] for match in matches)
    ticks = tuple(knot for match in matches for knot in match[2])
    return current, ticks


def consumer_birth(birth, ancestry, consumer):
    return any(consumer in ancestry[parent] for parent in birth.parents)


def marked_witness(windings, old_indices, indices, born, stage, spare):
    index, cluster = next((i, cluster) for i, labels in enumerate(indices) for cluster, knot in labels.items()
                          if knot == born.knot)
    winding = windings[index]
    assert rings.impulse(cluster)
    parent_roles = {old_indices[index][role]: role for role in rings.model_parents(winding, cluster)}
    assert set(parent_roles) == set(stage.incoming[born.knot]) == set(born.parents)
    for parent in born.parents:
        ancestors, remaining = set(), [parent]
        while remaining:
            knot = remaining.pop()
            if knot not in ancestors:
                ancestors.add(knot)
                remaining.extend(stage.incoming[knot])
        assert spare["knot"] in ancestors
    occurrences = [winding.holders[(cluster.phase + j) % len(winding.holders)]
                   for j in range(cluster.originals)]
    assert occurrences[0] == occurrences[-1] == 0
    return {"knot": born.knot, "original_occurrences": occurrences,
            "selected_leftover_offsets": [offset for _, offset, _ in cluster.selected],
            "original_spare_birth": spare["knot"],
            "parents": [{"knot": p, "depth": stage.depth[p], "spent_input": stage.incoming[born.knot][p],
                         "selected_leftover_offsets": [offset for _, offset, _ in parent_roles[p].selected]}
                        for p in born.parents]}


def ordered_prefix(case, frame, layer, tick, law, mode, joins_first, ticks_before):
    trace = []
    remaining = {b.knot: b for b in layer}
    with SerialReplay(case, frame, law, ticks_before) as replay:
        donors = frozenset(tick.parents)
        consumers = {b.knot for b in layer if consumer_birth(b, replay.stage.ancestry, case.consumer)}
        siblings = {b.knot for b in layer if b.knot != tick.knot and donors.intersection(b.parents)}
        ahead = {"tick_first": set(), "shared_consumers_first": consumers & siblings,
                 "all_consumers_first": consumers, "all_siblings_first": siblings}[mode]

        def priority(birth):
            return (0 if birth.knot in ahead else 1 if birth == tick else 2, birth.knot)

        while tick.knot in remaining:
            guard = replay.stage.restored_plan(law)
            available = admitted(guard[2], joins_first)
            assert guard[2] == Counter(signature(b) for b in remaining.values())
            choice = min((b for b in remaining.values() if signature(b) in available), key=priority)
            trace.append(replay.write(choice, joins_first, tick=choice == tick, guard=guard))
            del remaining[choice.knot]
        skipped = sorted(ahead & remaining.keys())
        assert all(len(remaining[k].parents) == 1 for k in skipped) and (joins_first or not skipped)
        assert trace[-1]["strict_ticks"] == ticks_before and trace[-1]["inclusive_ticks"] == ticks_before + 1
        if mode == "all_siblings_first" and not skipped:
            assert all(len(slots) == 1 for slots in trace[-1]["eligible_slots_at_parents"])
        withdrawals = {
            p: sum(p in event["parents"] and event["consumer"] for event in trace[:-1])
            for p in tick.parents
        }
    return {"events": trace, "ahead_but_blocked_by_priority": skipped,
            "tick_relative_birth": len(trace), "consumer_withdrawals_at_tick_parents": withdrawals}


def swapped_first_slot(case, frame, layer, tick, law, joins_first, ticks_before):
    initial = Holdings(frame, len(case.source))
    available = admitted(initial.restored_plan(law)[2], joins_first)
    alternatives = [b for b in layer if signature(b) in available and set(b.parents).intersection(tick.parents)
                    and consumer_birth(b, initial.ancestry, case.consumer)]
    if not alternatives:
        return {"status": "no admitted shared-donor consumer"}
    rival = min(alternatives, key=lambda b: b.knot)
    donor, = set(tick.parents).intersection(rival.parents)
    tick_index, rival_index = tick.parents.index(donor), rival.parents.index(donor)
    contested, other = tick.inputs[tick_index], rival.inputs[rival_index]
    assert contested != other and {contested, other} <= set(initial.loose[donor])
    planned_swaps = {tick.knot: list(tick.inputs), rival.knot: list(rival.inputs)}
    planned_swaps[tick.knot][tick_index], planned_swaps[rival.knot][rival_index] = other, contested
    with SerialReplay(case, frame, law, ticks_before) as forward:
        ab = [forward.write(b, joins_first, tick=b == tick) for b in (tick, rival)]
    with SerialReplay(case, frame, law, ticks_before) as reverse:
        ba = [reverse.write(b, joins_first, tick=b == tick, chosen=tuple(planned_swaps[b.knot]))
              for b in (rival, tick)]
    assert ab[0]["consumed"][tick_index] == ba[0]["consumed"][rival_index] == contested
    bits = {contested: other, other: contested}
    knots = {}
    for old, new in zip(ab, reversed(ba), strict=True):
        knots[old["knot"]] = new["knot"]
        bits.update(zip(old["fresh"], new["fresh"], strict=True))
    assert set(bits) == set(bits.values())
    assert all({bits.get(d, d) for d in support} == set(reverse.stage.stars[knots.get(k, k)])
               for k, support in enumerate(forward.stage.stars))
    return {"status": "paired swap", "shared_parent": donor, "same_first_consumed_slot": contested,
            "tick_first": ab, "consumer_first": ba, "exchanged_distinction_names": bits,
            "exchanged_child_names": knots}


def tick_window(case, frame, layer, tick, law, ticks_before):
    stage = Holdings(frame, len(case.source))
    assert case.consumer not in stage.ancestry[tick.parents[0]] | stage.ancestry[tick.parents[1]]
    per_parent = {
        p: {"initial_loose_slots": stage.loose[p],
            "all_sibling_children": [b.knot for b in layer if b != tick and p in b.parents],
            "consumer_sibling_children": [b.knot for b in layer if p in b.parents
                                          and consumer_birth(b, stage.ancestry, case.consumer)]}
        for p in tick.parents
    }
    modes = ("tick_first", "shared_consumers_first", "all_consumers_first", "all_siblings_first")
    orders = {
        name: {mode: ordered_prefix(case, frame, layer, tick, law, mode, joins_first, ticks_before)
               for mode in modes}
        for name, joins_first in (("unrestricted", False), ("joins_first", True))
    }
    swaps = {name: swapped_first_slot(case, frame, layer, tick, law, joins_first, ticks_before)
             for name, joins_first in (("unrestricted", False), ("joins_first", True))}
    return {"tick": tick.knot, "parents": tick.parents, "per_parent": per_parent,
            "orders": orders, "same_slot_swaps": swaps}


def interval(cuts, start, stop):
    first, last = cuts[start], cuts[stop]
    ticks = last["ticks"] - first["ticks"]
    births = last["births"] - first["births"]
    pure = last["pure_births"] - first["pure_births"]
    return {"ticks": ticks, "births": births, "parent_steps": stop - start, "pure_births": pure,
            "consumer_births": last["consumer_births"] - first["consumer_births"],
            "consumer_inputs": last["consumer_inputs"] - first["consumer_inputs"],
            "ticks_per_birth": [ticks, births], "ticks_per_parent_step": [ticks, stop - start],
            "ticks_per_pure_birth": [ticks, pure]}


def run_preparation(case, law, pure, bare_budgets):
    physical.certify_source(case.source, law)
    initial = Holdings(case.source, len(case.source))
    if case.name == "shortfall":
        depth, plan, pending = initial.restored_plan(law)
        assert depth == 0 and plan.status == "stall" and plan.shortages == ((2, 1),) and not pending
        return {"source": case.source, "source_projection_verified": True,
                "initial_loose": initial.loose_count, "guard_status": plan.status,
                "shortages": plan.shortages, "births": 0, "ticks": 0}, {}

    pure_indices, full_indices = known_clusters(pure), known_clusters(case.windings)
    budgets, depths, tick_witnesses, tick_windows, cuts = {}, {}, {}, {}, {}
    cuts[0] = {"births": 0, "pure_births": 0, "consumer_births": 0, "consumer_inputs": 0,
               "ticks": 0, "loose": initial.loose_count}
    consumer_count, consumer_inputs = 0, 0
    previous_parents = {}
    seen_ticks = []
    original_spare_birth = None
    with SerialReplay(case, case.source, law) as replay:
        for age in range(1, CUTS[-1] + 1):
            frame = replay.stage.stars
            _, layer, _ = physical.literal_turn(frame, law)
            pure_next, ticks = match_ring(pure, pure_indices, age, layer, whole=False)
            if age == 1:
                marked, = [b for b in layer if b.parents == (0,)]
                original_spare_birth = {"knot": marked.knot, "input": marked.inputs[0]}
            by_id = {b.knot: b for b in layer}
            events = []
            for birth in layer:
                event = replay.write(birth, True, tick=birth.knot in ticks)
                assert (event["knot"], event["consumed"], event["fresh"]) == (birth.knot, birth.inputs, birth.fresh)
                previous_parents[birth.knot] = frozenset(event["parents"])
                events.append(event)
            physical_layer = tuple(physical.Birth(e["knot"], e["parents"], e["consumed"], e["fresh"]) for e in events)
            assert (pure_next, ticks) == match_ring(pure, pure_indices, age, physical_layer, whole=False)
            if ticks:
                observed_tick, = ticks
                seen_ticks.append(age)
                tick = by_id[observed_tick]
                tick_witnesses[age] = marked_witness(pure, pure_indices, pure_next, tick, replay.stage, original_spare_birth)
                if case.name != "supply_only":
                    tick_windows[age] = tick_window(case, frame, layer, tick, law, replay.ticks - 1)
            pure_indices = pure_next
            full_indices, _ = match_ring(case.windings, full_indices, age, physical_layer, whole=True)
            actual_profile = Counter((len(b.parents), len(b.fresh)) for b in physical_layer)
            assert actual_profile == sum((rings.count_profile(w, age) for w in case.windings), Counter())
            assert rings.physical_end_profile(replay.stage.stars, physical_layer) == rings.observables(actual_profile)
            matched = set().union(*(set(rows.values()) for rows in full_indices))
            assert matched == by_id.keys()
            budgets[age] = [{model: len(by_id[knot].fresh) for model, knot in indices.items()}
                            for indices in pure_indices]
            deltas = Counter()
            if bare_budgets:
                for bare, actual in zip(bare_budgets[age], budgets[age], strict=True):
                    assert bare.keys() == actual.keys()
                    deltas.update(actual[cluster] - bare[cluster] for cluster in bare)
            layer_consumers = [e for e in events if e["consumer"]]
            consumer_count += len(layer_consumers)
            consumer_inputs += sum(len(e["consumed"]) for e in layer_consumers)
            assert sum(1 for rows in pure_indices for knot in rows.values()
                       if case.consumer not in replay.stage.ancestry[knot]) == sum(map(len, pure_indices))
            depths[age] = {"events": events, "births": len(events), "loose": replay.stage.loose_count,
                           "consumer_births": len(layer_consumers), "matched_pure_fresh_deltas_from_bare": dict(deltas),
                           "matched_pure_births": sum(map(len, pure_indices)), "marked_ticks": ticks}
            if age in CUTS:
                source, recovered, recovered_rings, recovered_age = physical.peel(replay.stage.stars, law)
                assert source == frozenset(range(len(case.source))) and recovered_age == age
                assert recovered == previous_parents and recovered_rings == {frozenset(range(8))}
                births = len(replay.stage.stars) - len(case.source)
                cuts[age] = {"supports": replay.stage.stars, "births": births,
                             "loose": replay.stage.loose_count, "ticks": replay.ticks,
                             "consumer_births": consumer_count, "consumer_inputs": consumer_inputs,
                             "pure_births": births - consumer_count, "parents_recovered_from_supports": True}
    assert tuple(seen_ticks) == TICK_DEPTHS
    return {"source": case.source, "source_projection_verified": True, "attachment_host": case.attachment,
            "original_spare_birth": original_spare_birth, "complete_cuts": cuts, "depths": depths,
            "intervals": {f"{a}-{b}": interval(cuts, a, b) for a, b in ((0, 6), (5, 6), (6, 10))},
            "tick_witnesses": tick_witnesses, "tick_windows": tick_windows}, budgets


def run():
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_SHA256
    cases = preparations()
    pure = cases[0].windings
    by_law = {}
    for law in LAWS:
        rows, bare = {}, {}
        for case in cases:
            row, budgets = run_preparation(case, law, pure, bare)
            rows[case.name] = row
            if case.name == "bare":
                bare = budgets
        by_law[law] = rows
    assert by_law["parity"] == by_law["nae"]
    return {"design_sha256": DESIGN_SHA256, "complete_depths": CUTS, "tick_depths": TICK_DEPTHS,
            "all_physical_ledgers_agree_under_both_laws": True, "laws": by_law}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    output = json.dumps(run(), sort_keys=True, separators=(",", ":")) + "\n"
    if args.out is None:
        print(output, end="")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output)


if __name__ == "__main__":
    main()
