"""Enumerate two-middle fibres and test every admissible table on one guarded wiring."""
import json
import os
import sys
from collections import Counter, defaultdict
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from itertools import combinations, product
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[3]
if __name__ == "__main__" and find_spec("pysat") is None and Path(sys.prefix) != ROOT / ".venv":
    python = ROOT / ".venv/bin/python"
    if python.is_file():
        os.execv(python, [str(python), "-B", str(Path(__file__).resolve()), *sys.argv[1:]])

from pysat.solvers import Solver


def predecessor(ticket):
    filename = next((ROOT / "proofs" / ticket).glob("*-P001_*/check.py"))
    spec = spec_from_file_location(ticket, filename)
    program = module_from_spec(spec)
    sys.modules[ticket] = program
    spec.loader.exec_module(program)
    return program


PHYSICAL = predecessor("TWO-RELAY-PADDING-20261115-001C")
LOCAL = predecessor("GUARD-CHOICE-SEPARATION-20261115-001B")
BITS = (0, 1)
STATES = tuple(product(BITS, repeat=4))  # start, end, displayed H, displayed K
NAND, XOR, OR = 7, 6, 14


def fibres(table):
    return tuple(table >> (4 * endpoints) & 15 for endpoints in range(4))


def admissible(table):
    if not (table & 1 and table & (1 << 15)):
        return False
    for i in range(16):
        if table & (1 << i):
            if not (table & (1 << (i & 7)) and table & (1 << (i | 4))):
                return False
    return True


def mixed_clause(terms):
    """Express a signed mixed Boolean ternary clause as an OR of two positive arcs."""
    tails = [-lit for lit in terms if lit < 0]
    heads = [lit for lit in terms if lit > 0]
    if len(tails) == 1 and len(heads) == 2:
        return [(tails[0], head) for head in heads]
    if len(tails) == 2 and len(heads) == 1:
        return [(tail, heads[0]) for tail in tails]
    raise ValueError("the ternary clause must contain both signs")


def forbidden_row(i):
    terms = [v if bit == 0 else -v for v, bit in enumerate(STATES[i], 1)]
    neg = next(t for t in terms if t < 0)
    pos = next(t for t in terms if t > 0)
    other = [t for t in terms if t not in (neg, pos)]
    w = 4 + i
    return (mixed_clause((neg, other[0], w)), mixed_clause((-w, other[1], pos)))


def universal_template(equal_pad_signs=False):
    """Use the predecessor's two-use signal blocks and its unmodified raw CNF emitter."""
    ON, OFF = PHYSICAL.ON, PHYSICAL.OFF
    ports = defaultdict(list)
    disjunction = 0
    for forbidden in range(1, 15):
        for alternatives in forbidden_row(forbidden):
            for j, (tail, head) in enumerate(alternatives):
                wire = ("wire", disjunction, j)
                sign = 1 if j == 0 or equal_pad_signs else -1
                edge = PHYSICAL.Edge("half", disjunction, sign, forbidden)
                ports[tail].append((wire, edge, OFF))
                ports[head].append((wire, OFF, ON))
            disjunction += 1
    entry, exit_wire = ("terminal", 0), ("terminal", 1)
    ports[1].append((entry, OFF, ON))
    ports[2].append((exit_wire, ON, OFF))
    stages, starts, displays = [], {}, {}

    def stage(upper, lower=None):
        if lower is None:
            lower = (("unused", len(stages)), OFF, OFF)
        stages.append((upper, lower))

    stage((entry, ON, OFF))
    for v in range(1, 19):  # A,D,H,K and one auxiliary for each of the fourteen candidate rows.
        feedback = ("feedback", v)
        stage((feedback, OFF, ON))
        starts[v] = len(stages)
        for port in ports[v]:
            middle = ("chain", len(stages))
            if v in (3, 4):
                displays.setdefault(v, middle)
            stage((middle, ON, ON), port)
        stage((feedback, ON, OFF))
    stage((exit_wire, OFF, ON))
    raw = PHYSICAL.StrictTemplate(stages, starts)
    assert disjunction == 28 and len(stages) == 152
    assert len(raw.cnf) == 4896 and len(raw.observable) == 3672
    assert set(raw.optional) == set(range(1, 15)) and all(len(v) == 12 for v in raw.optional.values())
    assert raw.middle_uses[displays[3]] == raw.middle_uses[displays[4]] == 1
    assert max(raw.middle_uses.values()) == max(raw.pad_uses.values()) == 2
    shown = (raw.var(("boundary", 0)), raw.var(("boundary", len(stages))),
             raw.var(("middle", displays[3])), raw.var(("middle", displays[4])))
    return raw, shown


def table_raw_guards(raw, requested):
    forbidden = {j for j in range(1, 15) if not requested & (1 << j)}
    endpoint = set(raw.observable[:24])
    result = [-abs(g) if abs(g) in endpoint else g for g in raw.guards(forbidden)]
    assert len(result) == len(raw.observable)
    return result


def check_forbidden_rows():
    for i in range(1, 15):
        pairs = forbidden_row(i)
        for j, state in enumerate(STATES):
            witnesses = []
            for bit in BITS:
                values = dict(enumerate(state, 1))
                values[4 + i] = bit
                if all(any(values[u] <= values[v] for u, v in arcs) for arcs in pairs):
                    witnesses.append(bit)
            assert bool(witnesses) == (i != j)
    return 14 * len(STATES)


def read_raw(solver, raw, shown, requested, check_models):
    pins = table_raw_guards(raw, requested)
    read, models = 0, 0
    for i, state in enumerate(STATES):
        fixed = pins + [v if bit else -v for v, bit in zip(shown, state)]
        if solver.solve(assumptions=fixed):
            read |= 1 << i
            if check_models:
                model = set(solver.get_model())
                assert set(fixed) <= model
                assert all(any(lit in model for lit in clause) for clause in raw.cnf)
                models += 1
    return read, models


def all_tables():
    demands = [table for table in range(1 << 16) if admissible(table)]
    raw, shown = universal_template()
    actual = set()
    models = 0
    with Solver(name="g3", bootstrap_with=raw.cnf) as solver:
        for index, requested in enumerate(demands):
            read, validated = read_raw(solver, raw, shown, requested,
                                       check_models=(index % 40 == 0 or index == len(demands) - 1))
            assert read == requested, (requested, read)
            actual.add(read)
            models += validated
    spectra = [sorted({fibres(m)[s] for m in actual}) for s in range(4)]
    assert len(actual) == 324 and [len(x) for x in spectra] == [8, 4, 16, 8]
    # This is the same literal CNF. A wrong guard sign on each second choice releases every row.
    wrong, wrong_shown = universal_template(equal_pad_signs=True)
    assert wrong.cnf == raw.cnf and wrong_shown == shown
    with Solver(name="g3", bootstrap_with=wrong.cnf) as solver:
        broken, _ = read_raw(solver, wrong, shown, demands[0], False)
        assert broken == 65535 and broken != demands[0]
    return {"four_bit_candidate_tables": 65536, "distinct_fixed_wiring_tables": len(actual),
            "stages": len(raw.stages), "strict_ternary_clauses": len(raw.cnf), "supplied_guard_bits": len(raw.observable),
            "displayed_occurrences_per_middle": [1, 1], "raw_endpoint_and_middle_assignment_queries": 16 * len(actual),
            "models_checked_against_every_clause": models, "fibres_by_endpoints_00_01_10_11": spectra,
            "all_equal_pad_signs_wrong_menu_gives_full_relation": True}


def matching_patterns(length):
    """All labelled-position partitions into pairs and singletons, up to name renaming."""
    def visit(labels, open_names, next_name):
        if len(labels) == length:
            yield tuple(labels)
            return
        yield from visit([*labels, next_name], [*open_names, next_name], next_name + 1)
        for i, name in enumerate(open_names):
            yield from visit([*labels, name], open_names[:i] + open_names[i + 1:], next_name)
    yield from visit([], [], 0)


def number_mixed(pads, flags):
    polarities = defaultdict(set)
    for pad, flag in zip(pads, flags):
        if flag in (1, 2):
            polarities[pad].add(flag)
    return sum(len(s) == 2 for s in polarities.values())


def three_stage_orders():
    # Physical middle 2 is the only repeated one. Its two arcs link x2 back to x1.
    # The displayed middles 0 and 1 occur only in the middle stage.
    directions = {11: (5, 6), 13: (4, 7), 9: (4, 5, 6, 7)}
    with LOCAL.Raw([2, 3, 0, 1, 2, 4], range(12)) as raw:
        for mask, inner_edges in directions.items():
            flags = [0] * 12
            for i in (1, 8, *inner_edges):
                flags[i] = 3
            pins = raw.with_guards(LOCAL.guards(flags))
            table = 0
            for i, (a, d, h, k) in enumerate(STATES):
                at = ((1, a), (4, d), (raw.hidden[6], h), (raw.hidden[9], k))
                if raw.accepts(pins, at, True):
                    table |= 1 << i
            assert fibres(table) == (mask,) * 4
    return set(directions)


def one_stage():
    min_pads = [dict() for _ in range(4)]
    tables = set()
    diagrams = guard_sets = model_checks = 0
    for pads in matching_patterns(4):
        diagrams += 1
        # H and K are the distinct actual middle occurrences of this stage.
        with LOCAL.Raw([0, 1], pads) as raw:
            for flags in product(range(4), repeat=4):
                fixed = raw.with_guards(LOCAL.guards(flags))
                q = number_mixed(pads, flags)
                mask = 0
                for i, (a, d, h, k) in enumerate(STATES):
                    values = ((1, a), (2, d), (raw.hidden[0], h), (raw.hidden[3], k))
                    # Evaluate witnesses of the OR-and-NAND two-pad fixture against every original clause.
                    picked = pads == (0, 1, 0, 1) and flags == (1, 1, 2, 2)
                    if raw.accepts(fixed, values, picked):
                        mask |= 1 << i
                assert admissible(mask)
                tables.add(mask)
                for t, fibre in enumerate(fibres(mask)):
                    min_pads[t][fibre] = min(q, min_pads[t].get(fibre, 3))
                guard_sets += 1
            model_checks += raw.checked_models
    assert (diagrams, guard_sets) == (10, 2560)
    assert [len(row) for row in min_pads] == [5, 1, 16, 5]
    assert min_pads[2][XOR] == 2 and min_pads[2][NAND] == min_pads[2][OR] == 1
    assert min_pads[0][NAND] == min_pads[3][OR] == 1 and model_checks > 0
    private_orders = three_stage_orders()
    without_mixed = [{mask for mask, cost in row.items() if cost == 0} | private_orders for row in min_pads]
    assert [len(row) for row in without_mixed] == [7, 4, 13, 7]
    return {"pad_layouts": diagrams, "four_state_guard_menus": guard_sets, "raw_assignment_queries": 16 * guard_sets,
            "different_complete_tables_in_one_stage": len(tables),
            "verified_zero_mixed_fibre_counts_with_three_stage_orders": [len(row) for row in without_mixed],
            "number_of_fibres_by_endpoints": [len(row) for row in min_pads],
            "minimum_mixed_pads_at_10_for_OR_NAND_XOR": [min_pads[2][m] for m in (OR, NAND, XOR)],
            "named_XOR_fixture_original_models_verified": model_checks}


def occurrence_cap_control():
    # An intentionally out-of-class pad controlling all four implications can encode XOR by itself.
    with LOCAL.Raw([0, 1], [0, 0, 0, 0]) as raw:
        fixed = raw.with_guards(LOCAL.guards([1, 2, 2, 1]))
        support = 0
        for i, (h, k) in enumerate(product(BITS, repeat=2)):
            if raw.accepts(fixed, ((1, 1), (2, 0), (raw.hidden[0], h), (raw.hidden[3], k)), True):
                support |= 1 << i
        assert support == XOR
    return {"uses_of_one_pad_outside_the_two_use_class": 4, "observed_fibre_at_10": support}


def implication_reports():
    # Intersect literal truth sets directly, independent of the order-closure criterion.
    unary_orientations = [3, 12, 5, 10]
    p, q = 11, 13  # H=>K excludes 10 (value index 2), K=>H excludes 01.
    by_directions = []
    for budget in (0, 1, 2):
        allowed = set()
        for selection in product(BITS, repeat=4):
            row = 15
            for selected, condition in zip(selection, unary_orientations):
                if selected:
                    row &= condition
            for used in range(budget + 1):
                for subset in combinations((p, q), used):
                    reduced = row
                    for implication in subset:
                        reduced &= implication
                    allowed.add(reduced)
        by_directions.append(allowed)
    assert list(map(len, by_directions)) == [10, 12, 13]
    assert by_directions[2] - by_directions[1] == {9}
    assert set(range(16)) - by_directions[2] == {NAND, XOR, OR}
    for mask in range(16):
        closure = (mask & 6) != 6 or (mask & 9) == 9
        assert closure == (mask in by_directions[2])
    return {"unary_only": 10, "at_most_one_ordered_implication": 12, "both_implications_allowed": 13,
            "only_mask_needing_both": 9, "three_masks_outside": [NAND, XOR, OR]}


def random_graph_check():
    """Project graphs with hidden vertices and one optional pair of opposite constraints directly."""
    rng = Random(409613)
    count = 0
    for n in range(4, 9):
        pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
        truth = {arc: sum(1 << u for u in range(1 << n) if (u >> arc[0] & 1) <= (u >> arc[1] & 1))
                 for arc in pairs}
        assignments = {s: sum(1 << u for u in range(1 << n) if tuple(u >> k & 1 for k in range(4)) == s)
                       for s in STATES}
        for _ in range(600):
            base = (1 << (1 << n)) - 1
            for arc in rng.sample(pairs, rng.randrange(n + 2)):
                base &= truth[arc]
            e, f = rng.sample(pairs, 2)
            possible = base & (truth[e] | truth[f])
            projected = sum(1 << i for i, state in enumerate(STATES) if assignments[state] & possible)
            assert XOR not in fibres(projected)
            count += 1
    return {"random_one_mixed_pad_graphs": count, "largest_total_vertices": 8, "seed": 409613}


if __name__ == "__main__":
    results = {"report_language": implication_reports(), "single_stage": one_stage(),
               "one_mixed_pad_stress": random_graph_check(), "occurrence_cap_control": occurrence_cap_control(),
               "four_literal_exclusion_checks": check_forbidden_rows(), "full_tables": all_tables()}
    results["status"] = "passed"
    print(json.dumps(results, indent=2, sort_keys=True))

