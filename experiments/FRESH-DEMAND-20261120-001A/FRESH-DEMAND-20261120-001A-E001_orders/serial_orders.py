"""Exact marked event trees for the seven-knot present-state and archived rules."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations
import json
from math import factorial
from pathlib import Path
import sys

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "serial_orders.json"
SERIAL_PATH = ROOT / "experiments/ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/serial.py"
serial_spec = spec_from_file_location("round_free_serial", SERIAL_PATH)
archived = module_from_spec(serial_spec)
serial_spec.loader.exec_module(archived)
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import Relation, check_knot

U, V, S, W, A, B, Z = range(7)
ORIGINAL_NAMES = ("U", "V", "S", "W", "A", "B", "Z")
TARGET = (U, V)
TARGET_SET = set(TARGET)
DEPTH = 4


def source(multiplicity, b, w_live):
    meetings = [(U, S), (V, S), (W, S), (S, A), (A, B), (B, W), (A, Z)]
    rows = [[] for _ in ORIGINAL_NAMES]
    for i, (a, c) in enumerate(meetings):
        ds = list(range(i * multiplicity, (i + 1) * multiplicity))
        rows[a].extend(ds)
        rows[c].extend(ds)
    d = len(meetings) * multiplicity
    rows[U].extend((d, d + 1))
    rows[V].extend((d + 2, d + 3))
    rows[Z].extend(range(d + 4, d + 4 + b))
    rows[W if w_live else Z].extend((d + 4 + b, d + 5 + b))
    return tuple(map(tuple, rows))


def literal_groups(neighbours, live):
    live = tuple(sorted(live))
    pairs = {frozenset((a, b)) for a, b in combinations(live, 2) if neighbours[a] & neighbours[b]}
    big = []
    for size in range(len(live), 2, -1):
        for row in combinations(live, size):
            members = frozenset(row)
            if all(frozenset(q) in pairs for q in combinations(row, 2)) and not set.intersection(
                    *(neighbours[j] for j in row)) and not any(members < g for g in big):
                big.append(members)
    return sorted(tuple(sorted(g)) for g in big) + sorted(tuple(sorted(g)) for g in pairs if not any(g < h for h in big))


def naive_live(P):
    return {q: tuple(P.loose(q)) for q in range(len(P.bits_of)) if P.loose(q)}


def prior_children(P):
    children = defaultdict(set)
    for j in range(len(ORIGINAL_NAMES), len(P.bits_of)):
        for p in {p for d in P.bits_of[j] for p in P.owner[d] if p < j}:
            children[p].add(j)
    return children


def verify_separate_live_parts(P, live):
    parts = {U: 0, V: 0, W: 0, Z: 1}
    for j in range(len(ORIGINAL_NAMES), len(P.bits_of)):
        inherited, = {parts[p] for d in P.bits_of[j] for p in P.owner[d] if p < j}
        parts[j] = inherited
    assert {parts[j] for j in live} == {0, 1}
    for a, b in combinations(live, 2):
        if parts[a] != parts[b]:
            assert a not in P.nbr[b] and not (P.nbr[a] & P.nbr[b])


@cache
def present_moves(stars):
    P = archived.S.from_junctions(stars)
    live = naive_live(P)
    verify_separate_live_parts(P, live)
    children = prior_children(P)
    actual, offshoots, before = archived.moves(P, children)
    expected = [g for g in literal_groups(P.nbr, live) if not set.intersection(*(children[j] for j in g))]
    uses = Counter(j for g in expected for j in g)
    unary = [(j,) for j, ds in live.items() if len(ds) > uses[j]]
    assert expected == actual and unary == offshoots and list(live) == before
    return tuple(actual), tuple(offshoots)


def all_choices(stars, joins_first):
    multi, unary = present_moves(stars)
    return multi if joins_first and multi else multi + unary


def nae_solver(stars):
    clauses = [[sign * (d + 1) for d in row] for row in stars for sign in (-1, 1)]
    return Minisat22(bootstrap_with=clauses)


def input_relation(stars, P, spent, law):
    """Count actual old input assignments, including constant NAE controls."""
    if law == "parity":
        holds = [P._reduce(P._mask(tuple(spent[i] for i in range(len(spent)) if select & (1 << i)))) == 0
                 for select in range(1, 1 << len(spent))]
        assert sum(holds) == 0  # Every visited serial event is nonclosing, with open distinctions in the other part.
        return 1 << len(spent), False
    with nae_solver(stars) as solver:
        rows = [i for i in range(1 << len(spent))
                if solver.solve(assumptions=[(d + 1) if i & (1 << j) else -(d + 1) for j, d in enumerate(spent)])]
    implied = 0 not in rows and (1 << len(spent)) - 1 not in rows
    return len(rows), implied


@cache
def canonical_relation(arity, law):
    names = tuple(str(j) for j in range(arity))
    def allowed(row):
        count = sum(row.values())
        return count % 2 == 0 if law == "parity" else 0 < count < arity
    relation = Relation.from_predicate(names, allowed)
    return check_knot(relation, names[:-1], names[-1]).is_knot


@cache
def apply_move(stars, parents, law):
    """The exact ROUND-FREE present-state demand, including already joined groups at readout."""
    P = archived.S.from_junctions(stars)
    loose = naive_live(P)
    spent = tuple(loose[j][0] for j in parents)
    state_count, implied = input_relation(stars, P, spent, law)
    assert state_count == 1 << len(spent) and not implied
    assert set(spent) < {d for ds in loose.values() for d in ds}
    newborn = archived.new_junction(P, spent)
    current = set(naive_live(P)) | {newborn}
    observed = [tuple(sorted(g)) for g in P.groups_among(current)]
    assert observed == literal_groups(P.nbr, current)
    groups = [g for g in observed if newborn in g]
    demand = len(groups)
    count = archived.F.fewest(P, [{"d": demand, "p": len(parents), "implied": implied}], None)[0]
    assert count == max(demand, 3 - len(parents), 1)
    fresh = tuple(range(P.nbits, P.nbits + count))
    after = stars + ((*spent, *fresh),)
    if len(after[-1]) <= 8:
        assert canonical_relation(len(after[-1]), law)
    record = {"new_knot": newborn, "parents": parents, "consumed": spent, "demand_groups": groups,
              "fresh_count": count, "allowed_input_assignments": state_count, "implied": implied}
    return after, record


def terminal_loss(stars):
    P = archived.S.from_junctions(stars)
    exhausted = [j for j in TARGET if not P.loose(j)]
    children = prior_children(P)
    blocked = sorted(set.intersection(*(children[j] for j in TARGET)))
    if exhausted or blocked:
        return {"exhausted_parents": exhausted, "earlier_common_children": blocked}
    return None


def grade_prefixes(stars, law, joins_first, fixed_ports):
    counts = [Counter() for _ in range(DEPTH + 1)]
    witnesses = {}
    def keep(outcome, history, extra):
        if outcome not in witnesses or len(history) < len(witnesses[outcome]["history"]):
            witnesses[outcome] = {"history": history, **extra}

    def visit(stage, history):
        depth = len(history)
        checks = counts[depth]
        checks["visited"] += 1
        if history and history[-1]["parents"] == TARGET:
            birth = history[-1]
            outcome = f"exact_birth_{birth['fresh_count']}"
            checks[outcome] += 1
            same_ports = birth["consumed"] == fixed_ports
            if same_ports:
                checks[f"{outcome}_on_fixed_ports"] += 1
            keep(outcome, history, {"uses_archive_ports": same_ports})
            return
        loss = terminal_loss(stage)
        if loss:
            checks["permanently_lost"] += 1
            keep("permanently_lost", history, loss)
            if TARGET_SET < set(history[-1]["parents"]):
                checks["lost_via_larger_birth"] += 1
                keep("lost_via_larger_birth", history, loss)
            return
        moves = all_choices(stage, joins_first)
        if not moves:
            raise AssertionError("the two independent live parts do not close or stall")
        if depth == DEPTH:
            outcome = "unresolved_target_listed" if TARGET in moves else "unresolved_target_unlisted"
            checks[outcome] += 1
            keep(outcome, history, {"currently_listed_moves": moves})
            return
        checks["expanded"] += 1
        checks["moves_tried"] += len(moves)
        checks["moves_using_new_parent"] += sum(max(g) >= len(ORIGINAL_NAMES) for g in moves)
        for move in moves:
            next_stage, event = apply_move(stage, move, law)
            visit(next_stage, (*history, event))

    visit(stars, ())
    for depth in range(1, len(counts)):
        assert counts[depth]["visited"] == counts[depth - 1]["moves_tried"]
    return {"prefix_counts_by_depth": [dict(sorted(c.items())) for c in counts], "first_witnesses": witnesses}


def plan_whole_layer(stars, law):
    P = archived.S.from_junctions(stars)
    previous = archived.S.from_junctions(stars)
    old = len(stars)
    if law == "parity":
        rule = archived.S.gf2(archived.F.fewest)
    else:
        def rule(P, info, unused):
            for i in info:
                inputs = P.bits_of[i["j"]][:i["p"]]
                with nae_solver(stars) as solver:
                    i["implied"] = not any(solver.solve(assumptions=[sign * (d + 1) for d in inputs]) for sign in (-1, 1))
            return archived.F.fewest(P, info, unused)
    assert P.step(rule, None) is not None
    roster = []
    for j in range(old, len(P.bits_of)):
        old_inputs, fresh = tuple(P.bits_of[j][:P.parents[j]]), tuple(P.bits_of[j][P.parents[j]:])
        states, implied = input_relation(stars, previous, old_inputs, law)
        assert states == 1 << len(old_inputs) and not implied and fresh
        assert canonical_relation(len(P.bits_of[j]), law)
        parents = tuple(next(previous for previous in P.owner[d] if previous < old) for d in old_inputs)
        roster.append({"parents": parents, "consumed": old_inputs, "fresh": fresh, "demand": P.demand_at_birth[j]})
    return roster


def all_preplanned_permutations(stars, plan):
    stage = archived.S.from_junctions(stars)
    openings = {d for ds in naive_live(stage).values() for d in ds}
    final = {frozenset(row["consumed"] + row["fresh"]) for row in plan}
    assert all(row["fresh"] for row in plan)
    count = 0
    for order in permutations(range(len(plan))):
        left = openings.copy()
        new = set()
        made = set()
        for i in order:
            spent, fresh = (set(plan[i][field]) for field in ("consumed", "fresh"))
            assert spent <= left and not fresh & (new | stage.owner.keys())
            left -= spent
            new |= fresh
            made.add(frozenset(spent | fresh))
        assert not left and final == made
        count += 1
    assert count == factorial(len(plan))
    return count


def hybrid_snapshot_orders(stars, law, plan):
    orders = set(permutations(tuple(row["parents"] for row in plan)))
    expected = Counter((row["parents"], len(row["fresh"])) for row in plan)
    receipts = {}
    for joins_first in (False, True):
        grade = Counter()
        for order in sorted(orders):
            current = stars
            events = []
            for parents in order:
                if parents not in all_choices(current, joins_first):
                    grade["guard_prevented_completion"] += 1
                    break
                current, event = apply_move(current, parents, law)
                events.append(event)
            else:
                grade["complete"] += 1
                target = next(e for e in events if e["parents"] == TARGET)
                grade[f"target_fresh_{target['fresh_count']}"] += 1
                if expected == Counter((e["parents"], e["fresh_count"]) for e in events):
                    grade["full_fresh_count_roster_matches"] += 1
        receipts["joins_first" if joins_first else "all_moves"] = dict(sorted(grade.items()))
    return {"distinct_orders_of_original_parent_sets": len(orders), "counts": receipts}


def supports_verified(stars, multiplicity):
    P = archived.S.from_junctions(stars)
    seen, todo = {S}, [S]
    while todo:
        new = P.nbr[todo.pop()] - seen
        seen.update(new)
        todo.extend(new)
    assert len(seen) == len(stars)
    rank = len(P.basis)
    parity = 0
    for row in stars:
        unseen = {b: w & ~P._mask(row) for b, w in P.basis.items()}
        pivots = {}
        for word in unseen.values():
            while word:
                high = word.bit_length()
                if high not in pivots:
                    pivots[high] = word
                    break
                word ^= pivots[high]
        assert len(row) >= 3 and rank - len(pivots) == 1
        parity += 1
    # A partly pinned shared bundle can be completed with both values. With
    # incomparable stars any other knot has an unpinned value when one star is pinned.
    assert all(not (set(x) <= set(y)) for i, x in enumerate(stars) for j, y in enumerate(stars) if i != j)
    assert all(sum(len(P.owner[d]) == 2 and b in P.owner[d] for d in stars[a]) == multiplicity
               for a, nodes in enumerate(P.nbr) for b in nodes)
    small_states = 0
    if multiplicity == 2:
        with nae_solver(stars) as solver:
            for row in stars:
                assert canonical_relation(len(row), "nae")
                for i in range(1, (1 << len(row)) - 1):
                    assert solver.solve(assumptions=[(d + 1) if i & (1 << j) else -(d + 1) for j, d in enumerate(row)])
                    small_states += 1
    return {"source_size_knots_distinctions": (len(P.bits_of), P.nbits), "parity_projection_ranks_verified": parity,
            "nae_doubled_bundle_extension": True, "literal_nae_allowed_local_states_checked": small_states}


def specific_traces(stars, law, w_live, marks):
    events = []
    if not w_live:
        swapped = [list(row) for row in stars]
        P = archived.S.from_junctions(stars)
        for j in TARGET:
            a, b = P.loose(j)
            i, k = swapped[j].index(a), swapped[j].index(b)
            swapped[j][i], swapped[j][k] = b, a
        v = tuple(map(tuple, swapped))
        assert [set(row) for row in v] == [set(row) for row in stars]
        for g in ((U,), (V,), TARGET):
            assert g in all_choices(v, False)
            v, record = apply_move(v, g, law)
            events.append(record)
        assert events[-1]["consumed"] == marks and events[-1]["fresh_count"] == 2
        return {"two_fresh_using_the_fixed_archive_ports_after_slot_reordering": events}

    v = stars
    for g in ((U, W), (V, W), (7, 8), (U, V, 9)):
        assert g in all_choices(v, True)
        if len(events) == 3:
            assert TARGET not in all_choices(v, False)
        v, record = apply_move(v, g, law)
        events.append(record)
    assert terminal_loss(v) and all(e["parents"] != TARGET for e in events)
    return {"joins_first_larger_event_masks_and_replaces_the_exact_pair": events}


def controls():
    # All supports have three places but the sum constrains distinction 2 to zero.
    bad = ((0, 1, 2), (0, 3, 4), (1, 3, 4))
    P = archived.S.from_junctions(bad)
    assert P._reduce(P._mask((2,))) == 0
    try:
        supports_verified(bad, 2)
    except AssertionError:
        pass
    else:
        raise AssertionError("the restricted proper projection must reject the supplied source")
    # The first leaf owes both pair births while holding only one loose distinction.
    poor = ((0, 1, 2, 4), (0, 3, 4), (1, 5, 6), (2, 7, 8))
    P = archived.S.from_junctions(poor)
    assert P.step(archived.F.fewest, None) is None
    return {"false_parity_source": bad, "forced_distinction": 2, "false_source_rejected": True,
            "underfunded_complete_step": poor, "whole_layer_refused": True}


def run_fixture(multiplicity, b, w_live, full):
    stars = source(multiplicity, b, w_live)
    result = {"source": stars, "admissibility": supports_verified(stars, multiplicity), "knot_laws": {}}
    for law in ("parity", "nae"):
        plan = plan_whole_layer(stars, law)
        target = next(e for e in plan if e["parents"] == TARGET)
        assert len(target["fresh"]) == (1 if w_live else 2)
        _, immediate = apply_move(stars, TARGET, law)
        assert immediate["allowed_input_assignments"] == 4 and immediate["fresh_count"] == 1
        counts = [x.bit_count() for x in range(immediate["allowed_input_assignments"])]
        kept = counts.count(0) + counts.count(2) if law == "parity" else counts.count(1)
        assert kept < len(counts)
        report = {"whole_layer_plan": plan, "target_ports": target["consumed"],
                  "target_preplanned_fresh_count": len(target["fresh"]),
                  "premature_close_control": {"full_input_assignments": immediate["allowed_input_assignments"],
                                              "input_assignments_kept_by_zero_fresh": kept}}
        if full:
            report["archive_preserving_permutations"] = all_preplanned_permutations(stars, plan)
            report["snapshot_only_hybrid"] = hybrid_snapshot_orders(stars, law, plan)
            report["present_state"] = {"all_moves": grade_prefixes(stars, law, False, target["consumed"]),
                                       "joins_first": grade_prefixes(stars, law, True, target["consumed"])}
        report["explicit_traces"] = specific_traces(stars, law, w_live, target["consumed"])
        result["knot_laws"][law] = report
        present_moves.cache_clear()
        apply_move.cache_clear()
    assert result["knot_laws"]["parity"] == result["knot_laws"]["nae"]
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    results = {"original_knot_names": ORIGINAL_NAMES, "target_parent_indices": TARGET, "prefix_depth": DEPTH,
               "primary_multiplicity": 9, "smaller_control_multiplicity": 2, "remote_balance_parameter": 2,
               "primary": {"W_spent": run_fixture(9, 2, False, True), "W_live": run_fixture(9, 2, True, True)},
               "small_physical_control": {"W_spent": run_fixture(2, 2, False, False), "W_live": run_fixture(2, 2, True, False)},
               "negative_controls": controls()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
