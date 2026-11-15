"""Check guard-dependent splitting against the original guarded clauses with PySAT."""
import json
import os
import sys
from collections import Counter
from functools import lru_cache
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[3]
if __name__ == "__main__" and find_spec("pysat") is None and Path(sys.prefix) != ROOT / ".venv":
    python = ROOT / ".venv/bin/python"
    if python.is_file():
        os.execv(python, [str(python), "-B", str(Path(__file__).resolve()), *sys.argv[1:]])

from pysat.solvers import Solver

BITS = (0, 1)
TRIPLES = tuple(product(BITS, repeat=3))


def predecessor(ticket):
    file = next((ROOT / "proofs" / ticket).glob("*-P001_*/check.py"))
    spec = spec_from_file_location(ticket, file)
    result = module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ORIGINAL = predecessor("SIGNED-KNOT-OVERLAP-20261114-001C")
ROUTE = predecessor("TWO-RELAY-PADDING-20261115-001D")


def guards(flags, positive=False, negative=False):
    """Bit i of an edge flag enforces that implication at pad value i."""
    return tuple(ROUTE.packed(flags, positive, negative))


def number(triple):
    return "".join(str(x) for x in triple)


class Raw:
    """Use the existing emitter, giving both solvers the same indexed guard assumptions."""

    def __init__(self, mids, pads):
        self.r = len(mids) // 2
        self.cnf, self.switches, self.hidden = ROUTE.raw_layout(mids, pads, ORIGINAL)
        assert all(len(clause) == 3 for clause in self.cnf)
        assert len(self.cnf) == 32 * (self.r + 1) and len(self.switches) == 24 * (self.r + 1)
        self.solver = Solver(name="g3", bootstrap_with=self.cnf)
        self.checked_models = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.solver.delete()

    def with_guards(self, values):
        assert len(values) == len(self.switches)
        return [v if bit else -v for v, bit in zip(self.switches, values)]

    def accepts(self, fixed, pins=(), verify_model=False):
        assumptions = fixed + [var if val else -var for var, val in pins]
        answer = self.solver.solve(assumptions=assumptions)
        if answer and verify_model:
            model = set(self.solver.get_model())
            assert all(lit in model for lit in assumptions)
            assert all(any(lit in model for lit in clause) for clause in self.cnf)
            self.checked_models += 1
        return answer

    def triples(self, cut, values, verify_models=False):
        fixed = self.with_guards(values)
        boundary = (1, 1 + cut, 1 + self.r)
        return {t for t in TRIPLES if self.accepts(fixed, zip(boundary, t), verify_models)}

    def fibres(self, controls, variable):
        fixed = self.with_guards(controls)
        return {(a, b): {h for h in BITS if self.accepts(fixed, ((1, a), (2, b), (variable, h)), True)}
                for a, b in product(BITS, repeat=2)}


def featured_middle():
    mids, split = [0, 1, 0, 2], [0, 1, 3, 2]
    pads = list(range(8))
    flags = [3, 3, 0, 0, 3, 3, 0, 0]
    safe = guards(flags)
    unsafe_list = list(safe)
    unsafe_list[30] = 0  # First raw switch of the [-pad] slot of the left upper outgoing edge.
    unsafe = tuple(unsafe_list)
    assert sum(x != y for x, y in zip(safe, unsafe)) == 1
    expected = {t for t in TRIPLES if t[0] <= t[1] <= t[2]}
    relaxed = {t for t in TRIPLES if t[1] <= t[2]}
    with Raw(mids, pads) as joined, Raw(split, pads) as separate, Raw([0, 1], list(range(4))) as local:
        table = local.fibres(guards(flags[:4]), local.hidden[0])
        assert table == {(a, b): {j for j in BITS if a <= j <= b} for a, b in product(BITS, repeat=2)}
        assert joined.triples(1, safe, True) == separate.triples(1, safe, True) == expected
        assert separate.triples(1, unsafe, True) == relaxed
        assert joined.triples(1, unsafe, True) == relaxed - {(1, 0, 0)}
        assert joined.accepts(joined.with_guards(unsafe)) and separate.accepts(separate.with_guards(unsafe))
        with_endpoints = (1,) * 24 + unsafe[24:]
        assert not joined.accepts(joined.with_guards(with_endpoints))
        assert separate.accepts(separate.with_guards(with_endpoints), verify_model=True)
        # This other one-bit neighbor has a positive model with BOTH local copies forced to 1.
        pinned_safe = list(unsafe)
        pinned_safe[54] = 0
        assert sum(x != y for x, y in zip(pinned_safe, unsafe)) == 1
        assert joined.triples(1, pinned_safe, True) == separate.triples(1, pinned_safe, True) == set(TRIPLES)
        with_endpoints = [1] * 24 + pinned_safe[24:]
        assert joined.accepts(joined.with_guards(with_endpoints), ((2, 1),), True)
        assert separate.accepts(separate.with_guards(with_endpoints), ((2, 1),), True)
        left = local.fibres([0] * 24 + pinned_safe[24:48], local.hidden[0])
        right = local.fibres([0] * 24 + pinned_safe[48:72], local.hidden[0])
        assert left[1, 1] == right[1, 0] == {1}
        return {"guard_bits": len(safe), "raw_ternary_clauses": len(joined.cnf),
                "changed_guard_index_zero_based": 30, "guard_hamming_distance": 1,
                "safe_triples": sorted(map(number, expected)), "unsafe_split_triples": sorted(map(number, relaxed)),
                "unsafe_joined_triples": sorted(map(number, relaxed - {(1, 0, 0)})),
                "shared_middle_values_at_00_01_10_11": [sorted(table[t]) for t in product(BITS, repeat=2)],
                "opposite_endpoint_guard_decisions_joined_split": [False, True],
                "second_safe_neighbor": {"changed_guard_index_zero_based": 54, "safe_triples": 8,
                                         "active_endpoints_forced_both_fibres_at_110": [1, 1],
                                         "safe_to_unsafe_joined_decisions": [True, False],
                                         "safe_to_unsafe_split_decisions": [True, True]},
                "strict_positive_models_rechecked": joined.checked_models + separate.checked_models + local.checked_models}


@lru_cache(maxsize=None)
def middle_support(int_flags, a, b):
    return {j for j, other in product(BITS, repeat=2)
            if all(not on or tail <= head for on, (tail, head) in
                   zip(int_flags, ((a, j), (j, b), (a, other), (other, b))))}


def one_middle_census():
    counts = Counter()
    with Raw([0, 1, 0, 2], range(8)) as joined, Raw(range(4), range(8)) as split:
        for edges in product(BITS, repeat=8):
            raw = guards([3 * bit for bit in edges])
            together = joined.triples(1, raw)
            apart = split.triples(1, raw)
            local_together, local_apart = set(), set()
            for x, b, z in TRIPLES:
                left = middle_support(edges[:4], x, b)
                right = middle_support(edges[4:], b, z)
                if left and right:
                    local_apart.add((x, b, z))
                if left & right:
                    local_together.add((x, b, z))
            assert local_together == together and local_apart == apart
            lost = apart - together
            assert lost <= {(1, 0, 0), (1, 1, 0)}
            endpoints = (1,) * 24 + raw[24:]
            joined_unsat = not joined.accepts(joined.with_guards(endpoints))
            split_sat = split.accepts(split.with_guards(endpoints))
            assert bool(lost) == (joined_unsat and split_sat)
            counts[",".join(sorted(map(number, lost))) or "none"] += 1
    assert counts == {"none": 217, "100": 15, "110": 15, "100,110": 9}
    return {"all_two_stage_private_pad_masks": sum(counts.values()), "lost_triples": dict(counts),
            "ordinary_endpoint_decision_changes": sum(counts.values()) - counts["none"]}


def all_pad_inputs():
    """Exhaust all four-state guard flags at both ends of four shared positive-pad names."""
    # Each position pairs across the cut, while all middles are private. Eliminate each
    # local middle by enumerating its two values independently at a fixed pad vector.
    local = {}
    for flags in product(range(4), repeat=4):
        rows = {}
        for a, b in product(BITS, repeat=2):
            mask = 0
            for assignment in range(16):
                on = [(flags[j] >> ((assignment >> j) & 1)) & 1 for j in range(4)]
                if all(any((not on[j] or a <= m) and (not on[j + 1] or m <= b) for m in BITS)
                       for j in (0, 2)):
                    mask |= 1 << assignment
            if a <= b:
                assert mask == (1 << 16) - 1
            rows[a, b] = mask
        local[flags] = rows
    pairs_checked = 0
    for left, right in product(local.values(), repeat=2):
        for a, b, c in TRIPLES:
            l, r = left[a, b], right[b, c]
            assert bool(l & r) == bool(l and r)
        pairs_checked += 1
    return {"four_pad_names_joint_across_cut": 4, "all_two_stage_four_state_edge_masks": pairs_checked,
            "exposed_triple_comparisons": 8 * pairs_checked}


def one_pad_raw_census():
    # Exactly one pad spans the cut. Six private pads give binary effective edge choices.
    joined_pads = [0, 1, 2, 3, 0, 4, 5, 6]
    counts = 0
    with Raw(range(4), joined_pads) as joined, Raw(range(4), range(8)) as split:
        choices = [(0, 1, 2, 3) if j in (0, 4) else (0, 3) for j in range(8)]
        for flags in product(*choices):
            values = guards(flags)
            assert joined.triples(1, values) == split.triples(1, values)
            counts += 1
        # For a descent each half of this specimen forces its own incoming pad to
        # turn off the only live route. The left requires 1, the right requires 0.
        with Raw(range(2), range(4)) as block:
            left = block.fibres(guards([1, 3, 0, 0]), block.hidden[1])
            right = block.fibres(guards([2, 3, 0, 0]), block.hidden[1])
            assert left[1, 0] == {1} and right[1, 0] == {0}
            assert all(left[t] == right[t] == {0, 1} for t in ((0, 0), (0, 1), (1, 1)))
    return {"all_effective_masks": counts, "raw_joined_and_split_boundary_queries": 16 * counts,
            "left_and_right_pad_values_on_their_respective_descents": [1, 0]}


def random_local_mids(positions, rng):
    names = list(range(positions))
    places = list(range(positions))
    rng.shuffle(places)
    for a, b in zip(places[::2], places[1::2]):
        if rng.randrange(2):
            names[b] = names[a]
    return names


def split_at(names, index):
    offset = max(names, default=-1) + 1
    return [*names[:index], *(offset + x for x in names[index:])]


def larger_raw():
    rng = Random(27182818)
    total = middle_cases = middle_losses = 0
    recovered = 0
    for r in range(3, 11):
        for case in range(18):
            cut = rng.randrange(1, r)
            mid = split_at(random_local_mids(2 * r, rng), 2 * cut)
            # Pair some pad positions across the cut, while retaining other internal identities.
            pad = random_local_mids(4 * r, rng)
            left, right = rng.randrange(4 * cut), rng.randrange(4 * cut, 4 * r)
            # Swapping labels at fixed positions can move an existing local pair across a cut.
            pad[left], pad[right] = pad[right], pad[left]
            if not (set(pad[:4*cut]) & set(pad[4*cut:])):
                unused = 4 * r
                pad[left] = pad[right] = unused
            apart_pad = split_at(pad, 4 * cut)
            flags = [rng.randrange(4) for _ in range(4*r)]
            vector = list(guards(flags))
            # Correlated partial guard triplets exercise the raw clauses beyond all-on/all-off.
            for j in range(24, len(vector), 3):
                if not vector[j]:
                    vector[j + rng.randrange(3)] = 1
            if case % 3 == 0:
                for j in range(24):
                    vector[j] = rng.randrange(2)
            with Raw(mid, pad) as whole, Raw(mid, apart_pad) as apart:
                assert whole.triples(cut, vector, True) == apart.triples(cut, vector, True)
                recovered += whole.checked_models + apart.checked_models
            assert not (set(mid[:2*cut]) & set(mid[2*cut:]))
            total += 1
            # Now keep every pad private across the cut and make just one positive middle common.
            bridge = max(mid) + 1
            if case == 0:
                li, ri = 0, 2 * r - 2
                flags = [0] * (4 * r)
                flags[0], flags[4 * (r - 1) + 1] = 3, 3
                vector = guards(flags)
            else:
                li, ri = rng.randrange(2 * cut), rng.randrange(2 * cut, 2 * r)
            mid[li] = mid[ri] = bridge
            split_mid = mid.copy()
            split_mid[ri] = bridge + 1
            assert set(mid[:2*cut]) & set(mid[2*cut:]) == {bridge}
            with Raw(mid, apart_pad) as whole, Raw(split_mid, apart_pad) as apart:
                joint = whole.triples(cut, vector, True)
                independent = apart.triples(cut, vector, True)
                assert joint <= independent
                loss = independent - joint
                assert loss <= {(1, 0, 0), (1, 1, 0)}
                if case == 0:
                    assert len(loss) == 2
                middle_cases += 1
                middle_losses += bool(loss)
                recovered += whole.checked_models + apart.checked_models
    return {"padding_layouts_and_guard_vectors": total,
            "single_middle_layouts_and_guard_vectors": middle_cases,
            "single_middle_layouts_with_loss": middle_losses, "largest_stages": 10,
            "original_ternary_models_rechecked": recovered, "seed": 27182818}


def mixed_middle_pad_control():
    # Positive x forces J. Its left/right outgoing halves need opposite pad values
    # to fail. A second-stage private branch transmits b to z unconditionally.
    mids = [0, 1, 0, 2]
    p = [0, 1, 2, 3, 4, 1, 5, 6]
    flags = [3, 1, 0, 0, 0, 2, 3, 3]
    on = guards(flags, True, True)
    with Raw(mids, p) as joined, Raw(mids, range(8)) as split_pad:
        assert not joined.accepts(joined.with_guards(on))
        assert split_pad.accepts(split_pad.with_guards(on), verify_model=True)
    return {"one_middle_still_shared": True, "joined_sat": False, "only_pad_split_sat": True}


if __name__ == "__main__":
    results = {"live_switch": featured_middle(), "middle_mask_census": one_middle_census(),
               "only_pads_symbolic": all_pad_inputs(), "one_pad_raw": one_pad_raw_census(),
               "larger_pad_cases": larger_raw(), "mixed_middle_control": mixed_middle_pad_control()}
    results["status"] = "passed"
    print(json.dumps(results, indent=2, sort_keys=True))

