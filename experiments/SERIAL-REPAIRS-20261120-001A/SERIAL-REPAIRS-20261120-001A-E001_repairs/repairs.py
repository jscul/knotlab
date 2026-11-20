"""Compare explicit choices for three archived serial repairs on the two built starts."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "repairs.json"
PREVIOUS = ROOT / "experiments/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders"


def load(name):
    spec = spec_from_file_location(name, PREVIOUS / (name + ".py"))
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


serial = load("serial_orders")
fixed = load("fixed_map")
ORIGINAL = tuple(frozenset((x,)) for x in serial.ORIGINAL_NAMES)
TARGET = frozenset(("U", "V"))
MASKS = ("", "F", "U", "G", "FU", "FG", "UG", "FUG")
DEPTH = 3


def label(cluster):
    return ",".join(sorted(cluster))


def display(move, tags):
    return tuple(label(tags[j]) for j in move)


class FixedOracle:
    def __init__(self, shifted):
        self.source = serial.source(9, 2, shifted)
        self.stars, self.parents, self.successors, self.ports = fixed.literal_map(shifted, fixed.pieces(shifted))
        assert self.source == tuple(tuple(self.stars[root]) for root in ORIGINAL)

    def ready(self, tags):
        numbers = {cluster: i for i, cluster in enumerate(tags)}
        by_inputs = defaultdict(list)
        for child in sorted(self.parents, key=fixed.order):
            parents = self.parents[child]
            if len(child) > 1 and child not in numbers and all(p in numbers for p in parents):
                move = tuple(sorted(numbers[p] for p in parents))
                by_inputs[move].append(child)
        return dict(by_inputs)

    def prefunded_fragment(self, built):
        tags = ORIGINAL + tuple(sorted(built, key=fixed.order))
        stars = tuple(tuple(self.stars[c]) for c in tags)
        ordered_counts = Counter(d for row in stars for d in row)
        assert all(count <= 2 for count in ordered_counts.values())
        for move, children in self.ready(tags).items():
            for c in children:
                assert all(ordered_counts[self.ports[tags[j], c]] == 1 for j in move)
        return tags, stars


def repair_choices(stars, tags, oracle, mask, joins_first=False):
    ready = oracle.ready(tags)
    P = serial.archived.S.from_junctions(stars)
    live = serial.naive_live(P)
    old_multi, old_unary = serial.present_moves(stars)
    if "G" in mask:
        multi = tuple(sorted(g for g in ready if len(g) > 1 and all(j in live for j in g)))
    else:
        multi = old_multi
    if "U" in mask:
        unary = tuple(sorted(g for g in ready if len(g) == 1 and g[0] in live))
    else:
        owed = Counter(j for g in multi for j in g)
        unary = tuple((j,) for j, ports in live.items() if len(ports) > owed[j])
        if "G" not in mask:
            assert unary == old_unary
    menu = multi if joins_first and multi else multi + unary
    return menu, multi + unary, ready


def primary(oracle, law, mask, joins_first):
    menu, _, ready = repair_choices(oracle.source, ORIGINAL, oracle, mask, joins_first)
    target = serial.TARGET
    assert target in menu and ready[target] == [TARGET]
    outcomes = []
    for move in menu:
        _, birth = serial.apply_move(oracle.source, move, law)
        demand = len(birth["demand_groups"])
        # F pays the knot floor at birth. We also test the stronger option
        # that pays every demand already witnessed in the physical stage.
        floor = max(1, 3 - len(move))
        at_birth = floor if "F" in mask else birth["fresh_count"]
        budgets = sorted(len(oracle.successors[c]) for c in ready.get(move, ()))
        outcomes.append({"parents": display(move, ORIGINAL), "immediate_demand": demand,
                         "fresh_at_birth": at_birth, "with_immediate_demand": max(floor, demand),
                         "full_map_fresh_counts_if_supplied": budgets})
    marked = next(row for row in outcomes if row["parents"] == ("U", "V"))
    assert marked["immediate_demand"] == 0 and marked["fresh_at_birth"] == 1
    return {"at_birth_matches_completed_roster": marked["full_map_fresh_counts_if_supplied"] == [1],
            "F_may_affect_only_later_counts_on_this_move": "F" in mask, "all_first_choices": outcomes}


def roster_audit(oracle, mask, joins_first):
    """Use preallocated completed-map supports for every compatible birth."""
    parents = {frozenset(): ()}
    levels = [0] * (DEPTH + 1)
    first = {}
    frontier = [frozenset()]
    for depth in range(DEPTH + 1):
        following = []
        levels[depth] = len(frontier)
        for built in frontier:
            tags, stars = oracle.prefunded_fragment(built)
            menu, all_moves, ready = repair_choices(stars, tags, oracle, mask, joins_first)
            for move in sorted(set(menu) - ready.keys()):
                kind = "false_unary" if len(move) == 1 else "false_multi"
                if kind not in first:
                    parity = serial.apply_move(stars, move, "parity")
                    nae = serial.apply_move(stars, move, "nae")
                    assert parity == nae
                    first[kind] = {"built_order": parents[built], "extra_move_parents": display(move, tags),
                                   "ready_map_parent_sets": [display(g, tags) for g in ready],
                                   "literal_rejected_by_map_but_possible_move": parity[1]}
            for move in sorted(ready.keys() - set(all_moves)):
                first.setdefault("missing_map_parent_set", {"built_order": parents[built],
                                                            "omitted_move_parents": display(move, tags),
                                                            "ready_clusters": [label(c) for c in ready[move]]})
            if depth < DEPTH:
                for move in menu:
                    for child in ready.get(move, ()):
                        after = built | {child}
                        if after not in parents:
                            parents[after] = (*parents[built], label(child))
                            following.append(after)
        frontier = following
    return {"compatible_parent_closed_fragments_per_depth": levels, "first_discrepancies": first}


def explicit_roster_witness(oracle, shifted, joins_first):
    if shifted:
        prefix = tuple(map(frozenset, (("U", "W"), ("V", "W"))))
        incorrect_parents = prefix
        mask = "U"
    else:
        prefix = (TARGET,)
        incorrect_parents = prefix
        mask = "G"
    built = frozenset()
    for child in prefix:
        tags, stars = oracle.prefunded_fragment(built)
        menu, _, ready = repair_choices(stars, tags, oracle, mask, joins_first)
        move = next(g for g, children in ready.items() if child in children)
        assert move in menu
        built |= {child}
    tags, stars = oracle.prefunded_fragment(built)
    menu, _, ready = repair_choices(stars, tags, oracle, mask, joins_first)
    incorrect = tuple(sorted(tags.index(c) for c in incorrect_parents))
    assert incorrect in menu and incorrect not in ready
    parity = serial.apply_move(stars, incorrect, "parity")
    nae = serial.apply_move(stars, incorrect, "nae")
    assert parity == nae
    return {"preplanned_prefix": [label(c) for c in prefix], "implemented_roster_gate": mask,
            "extra_move_parents": display(incorrect, tags), "extra_move_replayed_both_laws": parity[1]}


def local_assignments(stars, marks, law):
    P = serial.archived.S.from_junctions(stars)
    if law == "parity":
        imposed = [q for q in range(1, 1 << len(marks))
                   if P._reduce(P._mask(d for i, d in enumerate(marks) if q & (1 << i))) == 0]
        return [r for r in range(1 << len(marks)) if all((r & q).bit_count() % 2 == 0 for q in imposed)]
    with serial.nae_solver(stars) as solver:
        return [r for r in range(1 << len(marks))
                if solver.solve(assumptions=[(d + 1) if r & (1 << i) else -(d + 1) for i, d in enumerate(marks)])]


def capacity_control(oracle, law, joins_first):
    """Let both roster gates read the map but leave the at-birth count current."""
    assert len(oracle.successors[TARGET]) == 2
    p, u, v, first, second = map(frozenset, (("U", "V"), ("U", "a1"), ("V", "b1"),
                                             ("U", "V", "a1"), ("U", "V", "b1")))
    sequence = (p, u, first, v) if joins_first else (p, u, v, first)
    stars, tags = oracle.source, ORIGINAL
    events = []
    for child in sequence:
        menu, _, ready = repair_choices(stars, tags, oracle, "UG", joins_first)
        move = next(g for g, jobs in ready.items() if child in jobs)
        assert move in menu
        stars, event = serial.apply_move(stars, move, law)
        tags = (*tags, child)
        events.append({"cluster": label(child), "fresh_count": event["fresh_count"], "consumed": event["consumed"]})
    menu, _, ready = repair_choices(stars, tags, oracle, "UG", joins_first)
    move = next(g for g, jobs in ready.items() if second in jobs)
    assert move not in menu
    marked_knot = tags.index(p)
    P = serial.archived.S.from_junctions(stars)
    assert not P.loose(marked_knot) and all(P.loose(j) for j in move if j != marked_knot)
    saved_support = stars[marked_knot]
    added = P.nbits
    grown = tuple((*row, added) if j == marked_knot else row for j, row in enumerate(stars))
    allowed_before = local_assignments(stars, saved_support, law)
    allowed_after = local_assignments(grown, saved_support, law)
    added_rows = sorted(set(allowed_after) - set(allowed_before))
    assert set(allowed_before) < set(allowed_after)
    assert len(allowed_after) == 8
    assert move in repair_choices(grown, tags, oracle, "UG", joins_first)[0]
    after, birth = serial.apply_move(grown, move, law)
    assert added in birth["consumed"] and local_assignments(after, saved_support, law) == allowed_after
    return {"actual_shortfall_trace": events, "failed_successor": label(second), "failed_move": display(move, tags),
            "old_UV_support": saved_support, "late_extension_distinction": added, "repaired_by_allowing_replacement": True,
            "allowed_rows_before": allowed_before, "allowed_rows_after_late_extension": allowed_after,
            "new_old_rows": added_rows, "conservative_on_old_support": False}


def results():
    records = {}
    for shifted in (False, True):
        oracle = FixedOracle(shifted)
        proof = serial.supports_verified(oracle.source, 9)
        scaffold = serial.supports_verified(serial.source(2, 2, shifted), 2)
        by_rule = {}
        for law in ("parity", "nae"):
            by_rule[law] = {}
            for priority in (False, True):
                s = "joins_first" if priority else "all_moves"
                by_rule[law][s] = {m or "baseline": primary(oracle, law, m, priority) for m in MASKS}
        assert by_rule["parity"] == by_rule["nae"]
        pre = {s: {m or "baseline": roster_audit(oracle, m, priority) for m in ("", "U", "G", "UG")}
               for s, priority in (("all_moves", False), ("joins_first", True))}
        for s, arm in pre.items():
            assert not arm["UG"]["first_discrepancies"]
            if shifted:
                assert "false_multi" in arm["U"]["first_discrepancies"]
            else:
                assert "false_unary" in arm["G"]["first_discrepancies"]
        detail = {"literal_source": oracle.source, "lawfulness": proof, "small_bundle_lawfulness": scaffold,
                  "primary_births": by_rule, "prefunded_F_oracle_roster": pre,
                  "explicit_roster_witnesses": {s: explicit_roster_witness(oracle, shifted, priority)
                                                for s, priority in (("all_moves", False), ("joins_first", True))}}
        if not shifted:
            detail["shortfall_with_correct_roster_and_late_F"] = {
                law: {s: capacity_control(oracle, law, priority)
                      for s, priority in (("all_moves", False), ("joins_first", True))} for law in ("parity", "nae")}
        control = fixed.measure(shifted)
        detail["complete_map_positive_control"] = {"target_fresh_on_supplied_complete_map": control["common_fresh"],
                                                   "orders_through_size4": control["finite_linear_extension_counts"][-1]}
        records["W_live" if shifted else "W_spent"] = detail
        serial.apply_move.cache_clear()
        serial.present_moves.cache_clear()
    return {"subsets_including_baseline": [m or "baseline" for m in MASKS], "roster_prefix_depth": DEPTH,
            "laws": ["parity", "not-all-equal"], "oracle_note": "Counts with the prefunded F oracle use entire completed-map holdings, while U/G admit only obligations with all parents already present.",
            "arms": records}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    data = results()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
