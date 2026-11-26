"""Check early ordinary growth on meeting patterns from the older explosive-growth record."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
from pathlib import Path
import resource
from time import perf_counter

import networkx as nx
from pysat.solvers import Minisat22


ROOT = Path(__file__).resolve().parents[3]
GROWTH = Path("research/FORBID-EDITS-20261126-001/forbid.py")
EXPLOSIVE = "EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled"
SMALLEST = Path("experiments") / EXPLOSIVE / "posthoc_smallest.json"
EXPLOSIVE_RESULTS = Path("artifacts") / EXPLOSIVE / "results.json"
REFERENCE = Path(
    "experiments/BREAK-EDDIES-20261119-001B/"
    "BREAK-EDDIES-20261119-001B-E001_breaks/population_ref.json"
)
OUT = Path(__file__).with_suffix(".json")
NAMED = OUT.parents[1]
MEMORY_LIMIT = 2_000_000_000
CASE_IDS = (
    "smallest_archived_blowup",
    "archived_two_triples_blowup",
    "archived_three_regular_blowup",
    "archived_three_regular_symmetric_control",
    "equalized_two_triples_control",
    "two_knots_one_shared_control",
)


def read(path):
    return json.loads((ROOT / path).read_text())


def cases():
    smallest = read(SMALLEST)[0]
    yield CASE_IDS[0], smallest, smallest["counts"], f"{SMALLEST} row 0"

    starts = read(REFERENCE)
    historical = read(EXPLOSIVE_RESULTS)["ref"]
    for case, index in zip(CASE_IDS[1:4], (4, 7, 6), strict=True):
        yield case, starts[index], historical[index]["counts"], f"{REFERENCE} row {index}"

    equalized = {"sizes": [6] * 6, "edges": starts[4]["edges"]}
    yield CASE_IDS[4], equalized, None, f"{REFERENCE} row 4 with all knots given six places"
    yield CASE_IDS[5], {"sizes": [3, 3], "edges": [[0, 1]]}, None, "small exhaustive control"


def supports_from_record(record):
    supports = [[] for _ in record["sizes"]]
    for distinction, (left, right) in enumerate(record["edges"]):
        supports[left].append(distinction)
        supports[right].append(distinction)
    next_distinction = len(record["edges"])
    for support, size in zip(supports, record["sizes"], strict=True):
        loose = size - len(support)
        assert loose >= 0
        support.extend(range(next_distinction, next_distinction + loose))
        next_distinction += loose
    return tuple(map(tuple, supports))


def fibres_of(supports):
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        for distinction in support:
            holders[distinction].append(knot)
    fibres = defaultdict(list)
    for distinction, knots in sorted(holders.items()):
        assert len(knots) in (1, 2) and len(set(knots)) == len(knots)
        fibres[tuple(knots)].append(distinction)
    assert list(sorted(holders)) == list(range(len(holders)))
    return fibres, len(holders)


def image_of_holders(holders, knot_map):
    return tuple(sorted(knot_map[knot] for knot in holders))


def knot_automorphisms(knot_count, fibres):
    meeting = nx.Graph()
    meeting.add_nodes_from((knot, {"loose": len(fibres.get((knot,), ()))}) for knot in range(knot_count))
    for holders, distinctions in fibres.items():
        if len(holders) == 2:
            meeting.add_edge(*holders, shared=len(distinctions))
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        meeting, meeting, node_match=lambda left, right: left == right,
        edge_match=lambda left, right: left == right,
    )
    maps = sorted(tuple(mapping[knot] for knot in range(knot_count)) for mapping in matcher.isomorphisms_iter())
    if knot_count <= 6:
        brute = [candidate for candidate in permutations(range(knot_count)) if all(
            len(fibres.get(image_of_holders(holders, candidate), ())) == len(distinctions)
            for holders, distinctions in fibres.items()
        )]
        assert maps == brute
    return maps


def transpositions(mapping):
    return [(left, right) for left, right in enumerate(mapping) if left < right]


def distinction_lift(fibres, width, knot_map, exchange_within_fixed_fibres):
    mapping = list(range(width))
    for holders, distinctions in fibres.items():
        target = image_of_holders(holders, knot_map)
        if target != holders:
            for left, right in zip(distinctions, fibres[target], strict=True):
                mapping[left] = right
        elif exchange_within_fixed_fibres:
            for left, right in zip(distinctions[::2], distinctions[1::2]):
                mapping[left], mapping[right] = right, left
    assert all(mapping[mapping[distinction]] == distinction for distinction in range(width))
    return tuple(mapping)


def chain_check(knot_map, distinction_map, fibres):
    pairs = transpositions(knot_map)
    partners = {knot for pair in pairs for knot in pair}
    moved = nx.Graph()
    moved.add_nodes_from(sorted(partners))
    cross_orbit = moved.copy()
    fixed_shared = []
    shared_between_partners = []
    for holders, distinctions in fibres.items():
        if len(holders) != 2 or not partners.issuperset(holders):
            continue
        left, right = holders
        for distinction in distinctions:
            if distinction == distinction_map[distinction]:
                fixed_shared.append(distinction)
                continue
            moved.add_edge(left, right, distinction=distinction)
            if knot_map[left] == right:
                shared_between_partners.append(distinction)
            else:
                cross_orbit.add_edge(left, right, distinction=distinction)

    chains = []
    for left, right in pairs:
        if nx.has_path(cross_orbit, left, right):
            chains.append(nx.shortest_path(cross_orbit, left, right))
    witness = None
    if chains:
        knots = min(chains, key=lambda chain: (len(chain), chain))
        distinction_chain = [cross_orbit[left][right]["distinction"] for left, right in zip(knots, knots[1:])]
        quotient_knots = [min(knot, knot_map[knot]) for knot in knots]
        twists = [(left != rep_left) ^ (right != rep_right)
                  for (left, right), (rep_left, rep_right)
                  in zip(zip(knots, knots[1:]), zip(quotient_knots, quotient_knots[1:]), strict=True)]
        assert quotient_knots[0] == quotient_knots[-1] and sum(twists) % 2 == 1
        assert len(quotient_knots[:-1]) == len(set(quotient_knots[:-1]))
        witness = {"lifted_knots": knots, "knots_in_quotient": quotient_knots,
                   "distinctions": distinction_chain,
                   "distinction_pairs": [sorted((d, distinction_map[d])) for d in distinction_chain],
                   "changes_representative_side": twists}

    components = sorted(sorted(component) for component in nx.connected_components(moved))
    component_index = {knot: i for i, component in enumerate(components) for knot in component}
    return {
        "moved_knot_component_sizes": [len(component) for component in components],
        "component_permutation": [component_index[knot_map[component[0]]] for component in components],
        "partner_pairs_connected_via_other_orbits": len(chains),
        "shortest_side_exchanging_chain": witness,
        "fixed_shared_distinctions_between_partners": fixed_shared,
        "moved_shared_distinctions_within_one_pair": shared_between_partners,
    }


def state_string(state, width):
    return None if state is None else "".join(str((state >> distinction) & 1) for distinction in range(width))


def parity_solution(rows, width):
    basis = {}
    for mask, rhs in rows:
        while mask:
            pivot = mask.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (mask, rhs)
                break
            retained_mask, retained_rhs = basis[pivot]
            mask ^= retained_mask
            rhs ^= retained_rhs
        if not mask and rhs:
            return 0, None
    state = 0
    for pivot, (mask, rhs) in sorted(basis.items()):
        state |= (rhs ^ ((state & mask).bit_count() % 2)) << pivot
    return 1 << (width - len(basis)), state


class StateCheck:
    def __init__(self, supports, width, law):
        self.supports = supports
        self.masks = [sum(1 << distinction for distinction in support) for support in supports]
        self.width = width
        self.law = law
        self.nae_clauses = [
            [sign * (distinction + 1) for distinction in support]
            for support in supports for sign in (1, -1)
        ]
        self.exact_control_states = None
        if width <= 10:
            self.exact_control_states = [state for state in range(1 << width) if self.allowed(state)]

    def allowed(self, state):
        if self.law == "parity":
            return all((state & mask).bit_count() % 2 == 0 for mask in self.masks)
        return all(0 < (state & mask) < mask for mask in self.masks)

    def preserves_flip(self, flip):
        original, violating_knot = None, None
        if self.law == "parity":
            for knot, mask in enumerate(self.masks):
                if (flip & mask).bit_count() % 2:
                    original, violating_knot = 0, knot
                    break
        else:
            with Minisat22(bootstrap_with=self.nae_clauses) as solver:
                # It suffices to test a first violation of all zeros because global complement preserves NAE.
                for knot, support in enumerate(self.supports):
                    assumptions = [distinction + 1 if flip & (1 << distinction) else -(distinction + 1)
                                   for distinction in support]
                    if solver.solve(assumptions=assumptions):
                        original = sum(1 << (lit - 1) for lit in solver.get_model() if lit > 0)
                        violating_knot = knot
                        break
        if self.exact_control_states is not None:
            assert (original is None) == all(self.allowed(state ^ flip) for state in self.exact_control_states)
        if original is not None:
            assert self.allowed(original) and not self.allowed(original ^ flip)
        return {"preserved": original is None, "violating_knot": violating_knot,
                "allowed_preimage": state_string(original, self.width)}

    def fixed_by_swap_and_flip(self, mapping, flip):
        if any(((flip >> left) ^ (flip >> right)) & 1 for left, right in enumerate(mapping)):
            raise ValueError("the flip must be constant on each swap pair")
        if any(left == right and flip & (1 << left) for left, right in enumerate(mapping)):
            return {"has_allowed_state": False, "state_count": 0, "allowed_witness": None}
        pairs = transpositions(mapping)
        if self.law == "parity":
            equations = [(mask, 0) for mask in self.masks]
            equations.extend(((1 << left) | (1 << right), (flip >> left) & 1) for left, right in pairs)
            count, witness = parity_solution(equations, self.width)
        else:
            clauses = self.nae_clauses.copy()
            for left, right in pairs:
                a, b = left + 1, right + 1
                clauses.extend(((a, b), (-a, -b)) if flip & (1 << left) else ((a, -b), (-a, b)))
            with Minisat22(bootstrap_with=clauses) as solver:
                model = solver.get_model() if solver.solve() else None
            witness = None if model is None else sum(1 << (lit - 1) for lit in model if lit > 0)
            count = 0 if witness is None else None
        if self.exact_control_states is not None:
            exact = sum(self.matches(state, mapping, flip) for state in self.exact_control_states)
            assert (witness is not None) == (exact > 0) and (count is None or count == exact)
            count = exact
        if witness is not None:
            assert self.allowed(witness) and self.matches(witness, mapping, flip)
        return {"has_allowed_state": witness is not None, "state_count": count,
                "allowed_witness": state_string(witness, self.width)}

    @staticmethod
    def matches(state, mapping, flip):
        flipped = state ^ flip
        return all((((state >> right) ^ (flipped >> left)) & 1) == 0 for left, right in enumerate(mapping))


def measure_stage(supports, law):
    fibres, width = fibres_of(supports)
    state_check = StateCheck(supports, width, law)
    maps = knot_automorphisms(len(supports), fibres)
    all_flip = (1 << width) - 1
    lift_records = []
    nontrivial_involutions = 0
    for knot_map in maps:
        if not transpositions(knot_map) or any(knot_map[target] != knot for knot, target in enumerate(knot_map)):
            continue
        nontrivial_involutions += 1
        lifts = defaultdict(list)
        for exchange in (False, True):
            lift = distinction_lift(fibres, width, knot_map, exchange)
            lifts[lift].append("exchange_within_fixed_fibres" if exchange else "keep_within_fixed_fibres")
        for distinction_map, lift_kinds in lifts.items():
            assert all({distinction_map[d] for d in support} == set(supports[knot_map[knot]])
                       for knot, support in enumerate(supports))
            moved_flip = sum(1 << d for d, target in enumerate(distinction_map) if d != target)
            lift_records.append({
                "knot_pairs": transpositions(knot_map),
                "fixed_knots": [knot for knot, target in enumerate(knot_map) if knot == target],
                "distinction_pairs": transpositions(distinction_map),
                "fixed_distinctions": width - moved_flip.bit_count(),
                "lift_kinds": lift_kinds,
                "chain": chain_check(knot_map, distinction_map, fibres),
                "moved_only_flip": state_check.preserves_flip(moved_flip),
                "swap_fixed": state_check.fixed_by_swap_and_flip(distinction_map, 0),
                "swap_equals_global_complement": state_check.fixed_by_swap_and_flip(distinction_map, all_flip),
                "swap_equals_moved_only_complement": state_check.fixed_by_swap_and_flip(distinction_map, moved_flip),
            })
    return {"supports": supports, "knots": len(supports), "distinctions": width,
            "knot_automorphisms": len(maps), "knot_moving_involutions": nontrivial_involutions,
            "global_flip": state_check.preserves_flip(all_flip), "lifts": lift_records}


def run_case(record, historical, provenance, rounds, engine):
    start_supports = supports_from_record(record)
    panels = {}
    for law in ("parity", "nae"):
        current = start_supports
        stages = []
        births = len(current)
        for age in range(rounds + 1):
            if historical is not None:
                assert births == historical[age]
            stages.append({"round": age, "births": births, **measure_stage(current, law)})
            if age < rounds:
                current, info = engine.grow(current, law, "ordinary", engine.ENGINE)
                assert current is not None and info["status"] == "funded"
                births = len(info["births"])
        panels[law] = stages
    return {"source": provenance, "sizes": record["sizes"], "shared_pairs": record["edges"],
            "archived_birth_counts": historical, "panels": panels,
            "same_supports_under_both_laws": [parity["supports"] == nae["supports"]
                                             for parity, nae in zip(panels["parity"], panels["nae"], strict=True)]}


def partnered_supports():
    block_holders = {frozenset(pair): index for index, pair in enumerate(
        (pair for pair in combinations(range(6), 2) if pair[0] // 2 != pair[1] // 2), 6,
    )}
    overlaps = [(knot, block) for holders, block in block_holders.items() for knot in sorted(holders)]
    for holders, block in block_holders.items():
        partner_block = block_holders[frozenset(knot ^ 1 for knot in holders)]
        if block < partner_block:
            overlaps.append((block, partner_block))
    return supports_from_record({"sizes": [8] * 6 + [3] * 12, "edges": overlaps})


def parity_kernel(supports, width):
    rows = {}
    for support in supports:
        equation = sum(1 << d for d in support)
        for pivot, row in sorted(rows.items(), reverse=True):
            if equation & (1 << pivot):
                equation ^= row
        if equation:
            rows[equation.bit_length() - 1] = equation
    vectors = []
    for free in sorted(set(range(width)) - rows.keys()):
        state = 1 << free
        for pivot, row in sorted(rows.items()):
            if (state & row).bit_count() & 1:
                state |= 1 << pivot
        vectors.append(state)
    return vectors


def signed_character(kernel, pairs, convention):
    """Return exact signed sums against linear characters via an orthogonal basis."""
    if convention not in ("U", "W1", "W1c"):
        raise ValueError(f"unknown weighting {convention}")
    if convention == "U":
        pairs = []
    if convention == "W1c":
        ones = sum((1 << a) | (1 << b) for a, b in pairs)
    else:
        ones = 0

    def q(state):
        state ^= ones
        return sum((state >> a) & (state >> b) & 1 for a, b in pairs) % 2

    def companion(state):
        return sum(((state >> a) & 1) << b | ((state >> b) & 1) << a for a, b in pairs)

    def odd_dot(left, right):
        return (left & right).bit_count() & 1

    remaining = [(vector, companion(vector)) for vector in kernel]
    radical, paired = [], []
    while remaining:
        u, mate_u = remaining.pop()
        match = next((index for index, (v, _) in enumerate(remaining) if odd_dot(v, mate_u)), None)
        if match is None:
            radical.append(u)
            continue
        v, mate_v = remaining.pop(match)
        paired.append((u, v))
        for index, (w, mate_w) in enumerate(remaining):
            if odd_dot(w, mate_v):
                w, mate_w = w ^ u, mate_w ^ mate_u
            if odd_dot(w, mate_u):
                w, mate_w = w ^ v, mate_w ^ mate_v
            remaining[index] = (w, mate_w)

    constant = q(0)

    def with_phase(vectors):
        return [(vector, q(vector) ^ constant) for vector in vectors]

    left_basis = with_phase([u for u, _ in paired])
    right_basis = with_phase([v for _, v in paired])
    radical_basis = with_phase(radical)
    base_factor = 1 << (len(radical) + len(paired))

    def character(observed):
        if any(phase ^ odd_dot(vector, observed) for vector, phase in radical_basis):
            return 0
        exponent = constant ^ (sum(
            (a ^ odd_dot(u, observed)) & (b ^ odd_dot(v, observed))
            for (u, a), (v, b) in zip(left_basis, right_basis, strict=True)
        ) % 2)
        return -base_factor if exponent else base_factor

    return character


def projection_counts(character, reads):
    width = len(reads)
    terms = [character(sum(1 << d for i, d in enumerate(reads) if (selected >> i) & 1))
             for selected in range(1 << width)]
    values = list(product((0, 1), repeat=width))
    masks = [sum(v << i for i, v in enumerate(word)) for word in values]
    counts = [sum(value if (selected & mask).bit_count() % 2 == 0 else -value
                  for selected, value in enumerate(terms)) for mask in masks]
    assert all(count % (1 << width) == 0 for count in counts)
    return [count >> width for count in counts]


def marginal_cell(z, scan_left, scan_right, scan_both):
    values = [z + scan_left + scan_right + scan_both, z + scan_left - scan_right - scan_both,
              z - scan_left + scan_right - scan_both, z - scan_left - scan_right + scan_both]
    assert all(value % 4 == 0 for value in values)
    return [value // 4 for value in values]


def choose_two(n):
    return n * (n - 1) // 2


def score_group(columns, denominator, readers, output):
    signatures = defaultdict(list)
    for column, ea, eb in columns:
        signatures[(abs(ea + eb), abs(ea - eb))].append(column)
    for i, ((plus_a, minus_a), same) in enumerate(signatures.items()):
        for j, ((plus_b, minus_b), other) in enumerate(signatures.items()):
            if j < i or (i == j and len(same) < 2):
                continue
            numerator = max(plus_a + minus_b, minus_a + plus_b)
            best = output["best"]
            if best is None or numerator * best.denominator > best.numerator * denominator:
                output["best"] = Fraction(numerator, denominator)
            if numerator > 2 * denominator:
                column_pairs = combinations(same, 2) if i == j else product(same, other)
                output["hits"].update((readers, tuple(sorted(pair))) for pair in column_pairs)


def exact_gates(character, holder_sets, candidates):
    """Count placements by the columns that agree at each gate, using integer tables."""
    denomin = character(0)
    first = {d: character(1 << d) for d in candidates}
    cells = defaultdict(dict)
    sign = 1 if denomin >= 0 else -1
    for left in candidates:
        for right in candidates:
            if not holder_sets[left].isdisjoint(holder_sets[right]):
                continue
            sums = marginal_cell(denomin, first[left], first[right], character((1 << left) | (1 << right)))
            a, b, c, d = sums
            squares = [value ** 2 for value in sums]
            a_sq, b_sq, c_sq, d_sq = squares
            cells[left][right] = (
                denomin != 0 and all(value * sign >= 0 for value in sums), (a + d - b - c) * sign,
                sum(squares), c_sq + d_sq, b_sq + d_sq, a_sq + d_sq - b_sq - c_sq,
            )

    r1 = dict.fromkeys(("placements", "G0", "G1", "G2", "G3"), 0)
    r2 = r1.copy()
    for output in (r1, r2):
        output.update(best=None, hits=set())
    for left, right in combinations(candidates, 2):
        pair = (left, right)
        common = cells[left].keys() & cells[right].keys()
        n_eligible = choose_two(len(common))
        r1["placements"] += n_eligible
        r2["placements"] += n_eligible
        if denomin:
            r1["G0"] += n_eligible
        r1_columns = []
        r2_live = 0
        normalizers = Counter()
        r2_groups = defaultdict(list)
        for t in common:
            hold_a, e_a, norm_a, alice_a, bob_a, e_sq_a = cells[left][t]
            hold_b, e_b, norm_b, alice_b, bob_b, e_sq_b = cells[right][t]
            if hold_a and hold_b:
                r1_columns.append((t, e_a, e_b))
            if norm_a and norm_b:
                r2_live += 1
                if norm_a == norm_b:
                    normalizers[norm_a] += 1
                    if bob_a == bob_b:
                        r2_groups[norm_a, alice_a, alice_b].append((t, e_sq_a, e_sq_b))
        r1["G1"] += choose_two(len(r1_columns))
        score_group(r1_columns, abs(denomin), pair, r1)
        r2["G0"] += choose_two(r2_live)
        r2["G2"] += sum(choose_two(count) for count in normalizers.values())
        for (norm, _, _), columns in r2_groups.items():
            r2["G3"] += choose_two(len(columns))
            score_group(columns, norm, pair, r2)
    r1["G2"] = r1["G3"] = r1["G1"]
    r2["G1"] = r2["G0"]
    for result in (r1, r2):
        if result["best"] is not None:
            result["best"] = str(result["best"])
    return {"Z": denomin, "R1": r1, "R2": r2}


def named_rows(name):
    return [json.loads(line) for line in (NAMED / f"named_{name}.jsonl").read_text().splitlines()]


def conjugacy_keys(supports, lifts):
    fibres, _ = fibres_of(supports)
    renamings = knot_automorphisms(len(supports), fibres)
    return {tuple(lift["knot_pairs"]): min(
        tuple(sorted(image_of_holders(pair, perm) for pair in lift["knot_pairs"])) for perm in renamings
    ) for lift in lifts}


def named_partners(engine, gate_rounds):
    stages, current = [], partnered_supports()
    recorded = named_rows("partnered")
    births = len(current)
    for age in range(3):
        structural = measure_stage(current, "parity")
        kernel = parity_kernel(current, structural["distinctions"])
        lifts = structural["lifts"]
        conjugate = conjugacy_keys(current, lifts)
        rebuilt = {"round": age, "births": births, "knots": structural["knots"],
                   "distinctions": structural["distinctions"], "parity_dimension": len(kernel),
                   "automorphisms": structural["knot_automorphisms"], "knot_involutions": structural["knot_moving_involutions"],
                   "involution_conjugacy_classes": len(set(conjugate.values())),
                   "lifts_before_conjugacy_quotient": len(lifts), "lifts_exchanging_sides": sum(
                       row["chain"]["shortest_side_exchanging_chain"] is not None for row in lifts),
                   "global_flip_preserves_parity": structural["global_flip"]["preserved"],
                   "signed_readings": "not run"}
        if age < len(recorded):
            old = recorded[age]
            assert (old["K"], old["D"], old["parity_dim"], old["swaps"]) == (
                rebuilt["knots"], rebuilt["distinctions"], rebuilt["parity_dimension"], rebuilt["knot_involutions"],
            )
            representatives = {tuple(transpositions(row["perm"])) for row in old["classes"]}
            assert len(representatives) == len(set(conjugate.values()))
            assert {conjugate[rep] for rep in representatives} == set(conjugate.values())
            assert len(old["classes"]) == sum(tuple(lift["knot_pairs"]) in representatives for lift in lifts)
        if age in gate_rounds:
            rebuilt.update(compare_named_gates(current, kernel, lifts, recorded[age]))
        stages.append(rebuilt)
        if age < 2:
            current, info = engine.grow(current, "parity", "ordinary", engine.ENGINE)
            assert current is not None and info["status"] == "funded"
            births = len(info["births"])
    return stages


def compare_named_gates(supports, kernel, lifts, recorded):
    fibres, width = fibres_of(supports)
    holder_sets = [frozenset() for _ in range(width)]
    for holders, distinctions in fibres.items():
        for distinction in distinctions:
            holder_sets[distinction] = frozenset(holders)
    rebuilt = []
    all_hits = Counter()
    witness = None
    for index, old in enumerate(recorded["classes"]):
        knot_pairs = transpositions(old["perm"])
        lift_kind = "keep_within_fixed_fibres" if old["lift"] == "min" else "exchange_within_fixed_fibres"
        lift, = (lift for lift in lifts if lift["knot_pairs"] == knot_pairs and lift_kind in lift["lift_kinds"])
        assert old["kind"] == "one" and lift["chain"]["shortest_side_exchanging_chain"]
        candidates = sorted(d for pair in lift["distinction_pairs"] for d in pair)
        assert len(candidates) == len(set(candidates)) == old["readers"][0] == old["readers"][1]
        row = {"row": index, "knot_pairs": knot_pairs, "lift": old["lift"], "candidates_per_reader": len(candidates),
               "side_exchanging_chain": lift["chain"]["shortest_side_exchanging_chain"], "weightings": {}}
        for weighting, old_weight in old["weightings"].items():
            character = signed_character(kernel, lift["distinction_pairs"], weighting)
            fresh = exact_gates(character, holder_sets, candidates)
            assert fresh["Z"] == old_weight["Z"]
            for reading in ("R1", "R2"):
                current = fresh[reading]
                hits = current.pop("hits")
                earlier = old_weight[reading]
                assert all(earlier[key] == current[key] for key in current)
                assert hits == {(tuple(a), tuple(b)) for a, b, *_ in earlier["hits"]}
                assert len(hits) == len(earlier["hits"])
                current["hits"] = len(hits)
                if reading == "R1" and weighting == "W1":
                    assert hits == {(right, left) for left, right in hits}
                    all_hits.update(hits)
                    if witness is None and hits:
                        reader_a, reader_b = min(hits)
                        reads = reader_a + reader_b
                        cells = [projection_counts(character, (a, b)) for a, b in product(reader_a, reader_b)]
                        signed = projection_counts(character, reads)
                        unsigned = projection_counts(signed_character(kernel, (), "U"), reads)
                        signed_support = [word for word, count in zip(product((0, 1), repeat=4), signed, strict=True) if count]
                        cross_reader_ties = [(reads[i], reads[j], next(iter(differences)))
                                             for i, j in product(range(2), range(2, 4))
                                             if len(differences := {word[i] ^ word[j] for word in signed_support}) == 1]
                        holders_a = holder_sets[reader_a[0]] | holder_sets[reader_a[1]]
                        holders_b = holder_sets[reader_b[0]] | holder_sets[reader_b[1]]
                        witness = {"swap_row": index, "reads": [reader_a, reader_b], "signed_total": fresh["Z"],
                                   "table_cells_00_01_10_11": cells,
                                   "reader_holders": [sorted(holders_a), sorted(holders_b)],
                                   "holders_share_distinction": any(holders_a.intersection(holders) and holders_b.intersection(holders)
                                                                    for holders in fibres),
                                   "four_read_nonempty_words": sum(count > 0 for count in unsigned),
                                   "four_read_words_with_both_signs": sum(u > abs(s) for u, s in zip(unsigned, signed, strict=True)),
                                   "four_read_signed_counts": signed, "four_read_unsigned_counts": unsigned,
                                   "signed_support_cross_reader_xor": cross_reader_ties}
            row["weightings"][weighting] = fresh
        rebuilt.append(row)
    return {"signed_readings": "independently matched all recorded gates and hit identities", "readings": rebuilt,
            "W1_R1_counts": {"placements_across_lifts": sum(all_hits.values()),
                             "placements_unlabelled_readers_across_lifts": sum(all_hits.values()) // 2,
                             "placements_without_lift_identity": len(all_hits),
                             "placements_without_lift_identity_or_reader_order": len(all_hits) // 2},
            "W1_R1_witness": witness}


def named_lone(engine):
    rows = []
    for recorded in named_rows("lone"):
        law = recorded["law"]
        current = ((0, 1, 2, 3),)
        births = [1]
        status = "alive"
        for _ in range(6):
            stage, info = engine.grow(current, law, "ordinary", engine.ENGINE)
            if stage is None:
                status = info["status"]
                break
            current = stage
            births.append(len(info["births"]))
        stage = measure_stage(current, law)
        assert (status, len(births) - 1, stage["knots"], stage["distinctions"], stage["knot_moving_involutions"]) == (
            recorded["status"], recorded["round"], recorded["K"], recorded["D"], recorded["swaps"],
        )
        reader_duplicates = []
        if isinstance(recorded["classes"], list):
            fibres, _ = fibres_of(current)
            for index, swap in enumerate(recorded["classes"]):
                if swap["kind"] != "two":
                    continue
                knot_map = swap["perm"]
                maximal = swap["lift"] == "max"
                distinction_map = distinction_lift(fibres, stage["distinctions"], knot_map, maximal)
                meeting = nx.Graph()
                meeting.add_nodes_from(knot for knot, target in enumerate(knot_map) if knot != target)
                meeting.add_edges_from(holders for holders, distinctions in fibres.items()
                                       if len(holders) == 2 and all(k in meeting for k in holders)
                                       and any(d != distinction_map[d] for d in distinctions))
                sides = list(nx.connected_components(meeting))
                candidates = [[(d, len(holders)) for holders, group in fibres.items()
                               if side.issuperset(holders) for d in group] for side in sides]
                raw = [sum(count for _, count in part) for part in candidates]
                assert raw == swap["readers"]
                reader_duplicates.append({"row": index, "candidates_as_logged": raw,
                                          "distinct_candidates": [len(part) for part in candidates],
                                          "placements_as_logged": choose_two(raw[0]) * choose_two(raw[1]),
                                          "placements_with_distinct_choices": choose_two(len(candidates[0])) * choose_two(len(candidates[1]))})
            questions = [reading for swap in recorded["classes"] for w in swap["weightings"].values()
                         for key, reading in w.items() if key in ("R1", "R2")]
            analysed = {"logged_rows": len(recorded["classes"]), "logged_reading_weight_rows": len(questions),
                        "logged_hits": sum(len(q["hits"]) for q in questions),
                        "logged_best": str(max(Fraction(q["best"]) for q in questions if q["best"] is not None))}
        else:
            analysed = recorded["classes"]
        rows.append({"law": law, "births": births, "status": status, "knots": stage["knots"],
                     "distinctions": stage["distinctions"], "knot_involutions": stage["knot_moving_involutions"],
                     "readings": analysed, "two_sided_candidate_multiplicity": reader_duplicates})
    return rows


def even_flip_counterexample():
    supports = ((0, 1, 2, 3, 4, 5), (0, 1, 6, 7), (2, 3, 8, 9), (4, 6, 7, 10), (5, 8, 9, 11))
    knot_map = (0, 2, 1, 4, 3)
    fibres, width = fibres_of(supports)
    lift = distinction_lift(fibres, width, knot_map, False)
    assert len(transpositions(lift)) * 2 == width
    mask = (1 << width) - 1
    panels = {}
    for law in ("parity", "nae"):
        census = defaultdict(int)
        check = StateCheck(supports, width, law)
        for state in product((0, 1), repeat=width):
            parts = [sum(state[d] for d in support) for support in supports]
            allowed = all(total % 2 == 0 if law == "parity" else 0 < total < len(support)
                          for total, support in zip(parts, supports, strict=True))
            if allowed:
                census["allowed"] += 1
                census["swap_fixed"] += all(state[d] == state[target] for d, target in enumerate(lift))
                census["swap_to_complement"] += all(state[d] != state[target] for d, target in enumerate(lift))
        observed = check.fixed_by_swap_and_flip(lift, mask)
        assert observed["has_allowed_state"] == (census["swap_to_complement"] > 0)
        assert check.preserves_flip(mask)["preserved"]
        panels[law] = dict(census)
    return {"supports": supports, "knot_pairs": transpositions(knot_map), "distinction_pairs": transpositions(lift),
            "global_complement_preservation": True, "exact_state_counts": panels}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASE_IDS)
    parser.add_argument("--rounds", type=int, choices=(0, 1, 2), default=2)
    parser.add_argument("--benchmark", action="store_true", help="run measurements and print only resource use")
    parser.add_argument("--benchmark-named-round", type=int, choices=(0, 1), help="time one partnered round's gates only")
    args = parser.parse_args()
    if args.case and not args.benchmark:
        parser.error("--case is for benchmarking")

    start_time = perf_counter()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
    spec = spec_from_file_location("blowup_growth", ROOT / GROWTH)
    engine = module_from_spec(spec)
    spec.loader.exec_module(engine)
    if args.benchmark_named_round is not None:
        named_partners(engine, {args.benchmark_named_round})
        print(json.dumps({"partnered_round": args.benchmark_named_round,
                          "wall_seconds": round(perf_counter() - start_time, 6),
                          "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
        return
    results = {case: run_case(record, historical, source, args.rounds, engine)
               for case, record, historical, source in cases() if args.case is None or case == args.case}
    named = None if args.benchmark else {"partnered": named_partners(engine, {0, 1}), "lone": named_lone(engine),
                                          "even_flip_counterexample": even_flip_counterexample()}
    resources = {"wall_seconds": round(perf_counter() - start_time, 6),
                 "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 "address_space_limit_bytes": MEMORY_LIMIT}
    if args.benchmark:
        print(json.dumps({"cases": list(results), "rounds": args.rounds, **resources}))
        return
    result = {"growth": str(GROWTH), "archive_for_reference_birth_counts": str(EXPLOSIVE_RESULTS),
              "rounds": args.rounds, "cases": results, "named_comparison": named, "resources": resources,
              "scope": {
                  "chains": "Use distinct moved knot pairs and moved shared distinctions. Their lift starts at one knot and ends at its mate. Distinctions within a single pair are recorded separately.",
                  "lifts": "Exhaustive knot involutions. For each, test the two extreme lifts within fixed owner sets, with one ordered bijection between distinct owner sets.",
                  "states": "Exact parity counts and not-all-equal existence. Small cases with up to ten distinctions are checked exhaustively under both laws. A null count means existence without a count.",
                  "sampling": "Archived cases and controls were chosen by construction. No weighting over starts was used.",
                  "source_visibility": "The archived rebuild preceded direct access to the study. An earlier terminology search surfaced summary lines from the assumptions register. The named comparison used the recorded rows and a separate implementation.",
                  "late_rounds": "Stages after round 2 were outside the state and swap analysis. A wider feasibility check reached the memory limit during the older engine's next-round group cross-check."
              }}
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"case_count": len(results), "law_round_rows": sum(
        len(stages) for row in results.values() for stages in row["panels"].values()), **resources}))


if __name__ == "__main__":
    main()
