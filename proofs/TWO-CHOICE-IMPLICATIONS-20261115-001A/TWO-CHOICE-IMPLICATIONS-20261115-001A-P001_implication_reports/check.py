"""Project actual guarded clauses and check the minimal two-port reports."""

from collections import Counter
from contextlib import ExitStack
import hashlib
import importlib.util
from itertools import permutations, product
import json
import os
from pathlib import Path
from random import Random
import sys

from solver import ImplicationBlock, common_values


ROOT = Path(__file__).resolve().parents[3]
RAW = (ROOT / "proofs/TWO-RELAY-PADDING-20261115-001D"
       / "TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/check.py")
COMPLETION = (ROOT / "proofs/GUARD-CHOICE-SEPARATION-20261115-001A"
              / "GUARD-CHOICE-SEPARATION-20261115-001A-P001_boundary_supports/solver.py")
BITS = (0, 1)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load(name, path, digest):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "immutable predecessor changed")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signed(variables, values):
    require(len(variables) == len(values), "incomplete pin vector")
    return [v if bit else -v for v, bit in zip(variables, values)]


class Oracle:
    def __init__(self, source, stack, mids, pads):
        from pysat.solvers import Solver
        reader, base, self.completion = source
        self.mids = mids
        self.pads = pads
        self.clauses, self.guards, self.hidden = reader.raw_layout(mids, pads, base)
        self.bounds = list(range(1, len(mids)//2+2))
        self.oracle = stack.enter_context(Solver(name="g3", bootstrap_with=self.clauses))

    def port_vars(self, ports):
        return [self.hidden[3*self.mids.index(port)] for port in ports]

    def model(self, raw, witness):
        bounds, bits = witness
        all_pins = signed(self.guards, raw) + signed(self.bounds, bounds) + signed(self.hidden, bits)
        require(self.oracle.solve(assumptions=all_pins), "all returned occurrence pins conflict")
        model = self.completion(self.clauses, self.guards, self.hidden, raw, witness)
        true = set(model)
        require(all(pin in true for pin in all_pins)
                and all(any(lit in true for lit in clause) for clause in self.clauses),
                "completed signed model fails a raw clause or pin")


def minimum_costs():
    """Independently enumerate every unary report and both possible proper arrows."""
    result = {0: (0, 1)}  # explicit infeasibility
    for forced in product((-1, 0, 1), repeat=2):
        for directions in product(BITS, repeat=2):
            mask = 0
            for i, (h, k) in enumerate(product(BITS, repeat=2)):
                unary = all(x == -1 or x == bit for x, bit in zip(forced, (h, k)))
                if unary and (not directions[0] or h <= k) and (not directions[1] or k <= h):
                    mask |= 1 << i
            arrows, total = result.get(mask, (3, 5))
            cost = sum(directions) + sum(x != -1 for x in forced)
            result[mask] = min(arrows, sum(directions)), min(total, cost)
    return result


def test_block(oracle, raw, ports, tally, costs, replay_models=True, catalog=None):
    block = ImplicationBlock(oracle.mids, oracle.pads, raw, ports)
    guard_pins = signed(oracle.guards, raw)
    pvars = oracle.port_vars(ports)
    masks = {}
    for a, b in product(BITS, repeat=2):
        pinned = guard_pins + signed((oracle.bounds[0], oracle.bounds[-1]), (a, b))
        report = block.report(a, b)
        mask = 0
        for i, bits in enumerate(product(BITS, repeat=len(ports))):
            actual = oracle.oracle.solve(assumptions=pinned+signed(pvars, bits))
            require(report.accepts(bits) == actual, "reported support differs from original clauses")
            mask |= int(actual) << i
            if replay_models:
                witness = block.witness(a, b, bits)
                require((witness is not None) == actual, "witness existence differs")
                if witness is not None:
                    require((witness[0][0], witness[0][-1]) == (a, b)
                            and tuple(witness[1][3*oracle.mids.index(p)] for p in ports) == bits,
                            "witness changed a supplied bit")
                    oracle.model(raw, witness)
                    tally["full_raw_witnesses_checked"] += 1
            tally["raw_port_assignment_queries"] += 1
        if len(ports) == 2:
            total = (sum(x != -1 for x in report.forced) + len(report.arrows)) if report.possible else 1
            require(costs.get(mask) == (len(report.arrows), total), "report exceeds the exact minimum")
            if catalog is not None and (a, b, mask) not in catalog:
                catalog[a, b, mask] = oracle.mids, oracle.pads, raw
        masks[a, b] = mask
        tally["reports_compared_with_raw"] += 1
    return block, masks


def merge_witness(left, right):
    require(left[0][-1] == right[0][0], "different cut boundaries")
    return left[0][:-1]+right[0], left[1]+right[1]


def catalog_joins(source, catalog, spectra, tally):
    """Construct two actual blocks for every support pair at matching cut pins."""
    distinct_bad = set()
    for a, y, b in product(BITS, repeat=3):
        for lm, rm in product(sorted(spectra[a, y]), sorted(spectra[y, b])):
            lms, lps, lr = catalog[a, y, lm]
            rms, rps, rr = catalog[y, b, rm]
            L = ImplicationBlock(lms, lps, lr, (0, 1))
            R = ImplicationBlock(rms, rps, rr, (0, 1))
            # Preserve the two ports, rename every other right-side name apart.
            ms_offset = max(lms)+1
            ps_offset = max(lps)+1
            joined_ms = list(lms) + [x if x in (0, 1) else x+ms_offset for x in rms]
            joined_ps = list(lps) + [p+ps_offset for p in rps]
            raw = bytes(24) + lr[24:] + rr[24:]
            with ExitStack() as stack:
                graph = Oracle(source, stack, joined_ms, joined_ps)
                coords = (graph.bounds[0], graph.bounds[len(lms)//2], graph.bounds[-1])
                pins = signed(graph.guards, raw) + signed(coords, (a, y, b))
                whole_mask = 0
                for i, bits in enumerate(product(BITS, repeat=2)):
                    if graph.oracle.solve(assumptions=pins+signed(graph.port_vars((0, 1)), bits)):
                        whole_mask |= 1<<i
                lreport, rreport = L.report(a, y), R.report(y, b)
                common = common_values(lreport, rreport)
                require(whole_mask == lm & rm and (common is not None) == bool(whole_mask),
                        "projected merge failed on the joined guarded clauses")
                if common is not None:
                    graph.model(raw, merge_witness(L.witness(a, y, common), R.witness(y, b, common)))
                    tally["joined_complete_witnesses_checked"] += 1
            coords_overlap = (lreport.possible and rreport.possible and
                              all(l < 0 or r < 0 or l == r for l, r in zip(lreport.forced, rreport.forced)))
            if coords_overlap and not whole_mask:
                tally["joint_cases_with_false_positive_marginals"] += 1
                distinct_bad.add((lm, rm))
            tally["boundary_triples_with_ordered_report_pairs_replayed"] += 1
    four = {(2, 9), (2, 13), (4, 9), (4, 11)}
    require(distinct_bad == four | {(r, l) for l, r in four}, "unclassified marginal error")
    require(tally["boundary_triples_with_ordered_report_pairs_replayed"] == 440
            and tally["joint_cases_with_false_positive_marginals"] == 16, "incomplete serial join census")


def three_stage(source, tally, minimum):
    reader = source[0]
    mids, pads = [0, 1, 0, 2, 1, 3], list(range(12))
    flags = [3, 0, 0, 3, 0, 3, 0, 0, 3, 0, 0, 0]
    with ExitStack() as stack:
        left = Oracle(source, stack, mids[:2], list(range(4)))
        # Padding is private, so fresh dense local labels preserve its identity.
        right = Oracle(source, stack, mids[2:], list(range(8)))
        L, left_masks = test_block(left, reader.packed(flags[:4], False, False), (0, 1), tally, minimum)
        R, right_masks = test_block(right, reader.packed(flags[4:], False, False), (0, 1), tally, minimum)
        require(left_masks[1, 0] == 4 and right_masks[0, 0] == 11, "original three-stage supports")
        lr, rr = L.report(1, 0), R.report(0, 0)
        require(common_values(lr, rr) is None
                and all(l == -1 or r == -1 or l == r for l, r in zip(lr.forced, rr.forced)),
                "individual marginals should agree while jointly inconsistent")
        for remove in product(BITS, repeat=2):
            split_ms = list(mids)
            for i, name in enumerate(mids[2:], 2):
                if name in (0, 1) and remove[name]:
                    split_ms[i] = 4 + name
            whole = Oracle(source, stack, split_ms, pads)
            raw = reader.packed(flags, True, True)
            pins = signed(whole.guards, raw) + [-whole.bounds[1]]
            require(whole.oracle.solve(assumptions=pins) == any(remove), "raw partial split differs")
            tally["three_stage_split_patterns_checked"] += 1
        tally["three_stage_left_mask"] = left_masks[1, 0]
        tally["three_stage_right_mask"] = right_masks[0, 0]


def run():
    reader = load("route_raw", RAW, "1aee23c9aa74c04ede148bf94dd5134b68b3f62f5bc29b1361b4e83f4ed3ffc7")
    base = load("route_base", reader.BASE, "54d7a006b78c876aa28901a8f06951cb9ef67ceb5325ad4c64adee7867bf78c6")
    completion = load("route_completion", COMPLETION, "bd3d184bed7f1bf150670e7cac543ff7ca3e0cb31542505cdd3fadc38bc2b0ae")
    source = reader, base, completion.complete_raw_witness
    tally = Counter()
    minimum = minimum_costs()
    require(set(range(16))-set(minimum) == {6, 7, 14}, "report-language census")
    three_stage(source, tally, minimum)

    def empty_spectra():
        return {pins: set() for pins in product(BITS, repeat=2)}

    one, two, catalog = empty_spectra(), empty_spectra(), {}
    with ExitStack() as stack:
        oracle = Oracle(source, stack, [0, 1], list(range(4)))
        for flags in product(range(4), repeat=4):
            _, masks = test_block(oracle, reader.packed(flags, False, False), (0, 1), tally, minimum,
                                  catalog=catalog)
            for pins, mask in masks.items():
                one[pins].add(mask)
    # Every private/releasable guard vector has exactly a subset of eight
    # compulsory arcs. Enumerate all subsets and all placements of two ports.
    for hpos, kpos in permutations(range(4), 2):
        others = [i for i in range(4) if i not in (hpos, kpos)]
        for repeated in BITS:
            mids = [2]*4
            mids[hpos], mids[kpos] = 0, 1
            mids[others[1]] = 2 if repeated else 3
            with ExitStack() as stack:
                oracle = Oracle(source, stack, mids, list(range(8)))
                for active in range(256):
                    flags = [3*int(bool(active & (1<<i))) for i in range(8)]
                    _, masks = test_block(oracle, reader.packed(flags, False, False), (0, 1),
                                          tally, minimum, replay_models=active in (0, 53, 255),
                                          catalog=catalog)
                    for pins, mask in masks.items():
                        two[pins].add(mask)
                    tally["two_stage_skeletons_with_arc_settings"] += 1
    require(len(one[1, 0]) == 10 and len(two[1, 0]) == 12
            and all(9 not in masks for masks in two.values()), "one/two-stage threshold")

    mids = [2, 3, 0, 1, 2, 4]
    flags = [0, 3, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0]
    pads = list(range(12))
    with ExitStack() as stack:
        oracle = Oracle(source, stack, mids, pads)
        raw = reader.packed(flags, False, False)
        _, equality = test_block(oracle, raw, (0, 1), tally, minimum, catalog=catalog)
        require(all(mask == 9 for mask in equality.values()), "three-stage full-marginal equality")
        changed = raw.copy()
        changed[24+6*8] = 0
        _, after = test_block(oracle, changed, (0, 1), tally, minimum)
        require(all(mask == 15 for mask in after.values()), "one raw switch should release the cycle")
    all_spectra = {pins: two[pins] | one[pins] | {equality[pins]} for pins in two}
    expected = {(0, 0): {1, 3, 5, 9, 11, 13, 15}, (0, 1): {9, 11, 13, 15},
                (1, 0): set(minimum), (1, 1): {8, 9, 10, 11, 12, 13, 15}}
    require(all_spectra == expected, "pinned-endpoint spectra")
    catalog_joins(source, catalog, all_spectra, tally)

    # A shared pad with a common release needs that same value in both raw models.
    first, second = reader.packed([3, 0, 0, 0], False, False), reader.packed([1, 0, 0, 0], False, False)
    left = ImplicationBlock([0, 1], [0, 1, 2, 3], first, (0, 1), pad_release={0: 1})
    right = ImplicationBlock([0, 1], [0, 1, 2, 3], second, (0, 1), pad_release={0: 1})
    ports = common_values(left.report(0, 0), right.report(0, 0))
    with ExitStack() as stack:
        whole = Oracle(source, stack, [0, 1, 0, 1], [0, 1, 2, 3, 0, 4, 5, 6])
        raw = bytes(24) + first[24:] + second[24:]
        model = merge_witness(left.witness(0, 0, ports), right.witness(0, 0, ports))
        whole.model(raw, model)
        require(model[1][1] == model[1][7] == 1, "common pad release lost in raw witness")
    tally["joined_witness_with_common_pad_release"] = 1

    # Two separately acyclic reports, giving opposite implications, can join to equality.
    dflags = [0, 3, 0, 0, 3, 0, 0, 0]
    local_raw = reader.packed(dflags, False, False)
    lmid, rmid = [0, 2, 1, 3], [1, 4, 0, 5]
    left = ImplicationBlock(lmid, list(range(8)), local_raw, (0, 1))
    right = ImplicationBlock(rmid, list(range(8)), local_raw, (0, 1))
    joint_mask = 0
    with ExitStack() as stack:
        whole = Oracle(source, stack, lmid+rmid, list(range(16)))
        raw = reader.packed(dflags+dflags, False, False)
        for i, assignment in enumerate(product(BITS, repeat=2)):
            L, R = left.report(0, 1), right.report(1, 0)
            possible = L.accepts(assignment) and R.accepts(assignment)
            pins = (signed(whole.guards, raw) + signed([1, 3, 5], (0, 1, 0))
                    + signed(whole.port_vars((0, 1)), assignment))
            require(whole.oracle.solve(assumptions=pins) == possible, "opposite reports on a real join")
            if possible:
                model = merge_witness(left.witness(0, 1, assignment), right.witness(1, 0, assignment))
                whole.model(raw, model)
            joint_mask |= int(possible) << i
        common = common_values(L, R)
        require(joint_mask == 9 and common is not None and L.accepts(common) and R.accepts(common),
                "opposite reports should jointly force equality")

    rng = Random(20261115)
    for stages, port_count in ((3, 3), (5, 4), (6, 5)):
        mids, pads = list(range(2*stages)), list(range(4*stages))
        ports = tuple(mids[:port_count])
        for i in range(port_count, len(mids)-1, 2):
            mids[i+1] = mids[i]
        for i in range(0, len(pads), 2):
            pads[i+1] = pads[i]
        with ExitStack() as stack:
            oracle = Oracle(source, stack, mids, pads)
            for n in range(10):
                signs = [rng.choice((1, 2)) for _ in pads]
                flags = [rng.choice((0, 3, signs[p])) for p in pads]
                flags[0] = flags[1] = signs[pads[0]]
                raw = reader.packed(flags, n % 4 == 0, n % 5 == 0)
                for j in range(0, len(raw), 3):
                    if not raw[j]:
                        mask = rng.randrange(7)
                        raw[j:j+3] = bytes((mask>>k)&1 for k in range(3))
                test_block(oracle, raw, ports, tally, minimum)
    # One contested pad already falls outside the positive-report premise.
    with ExitStack() as stack:
        raw = reader.packed([1, 0, 2, 0], False, False)
        oracle = Oracle(source, stack, [0, 1], [0, 1, 0, 2])
        pins = signed(oracle.guards, raw) + signed((1, 2), (1, 0))
        mixed_mask = sum(1<<i for i, bits in enumerate(product(BITS, repeat=2))
                         if oracle.oracle.solve(assumptions=pins+signed(oracle.port_vars((0, 1)), bits)))
        require(mixed_mask == 14, "mixed-sign control should realize OR")
        try:
            ImplicationBlock([0, 1], [0, 1, 0, 2], raw, (0, 1))
        except ValueError as e:
            require("simultaneous pad release" in str(e), "misidentified mixed-pad control")
        else:
            raise AssertionError("treated a mixed pad as releasable")
    return {"status": "passed", **tally, "one_stage_types_at_10": len(one[1, 0]),
            "two_stage_types_at_10": len(two[1, 0]), "three_stage_types_at_10": len(all_spectra[1, 0]),
            "pinned_spectra": {f"{a}{b}": sorted(masks) for (a, b), masks in all_spectra.items()},
            "equality_mask_after_one_guard_off": after[1, 0], "two_acyclic_blocks_joint_mask": joint_mask,
            "mixed_padding_control_mask": mixed_mask, "largest_tested_interface": 5}


if __name__ == "__main__":
    if importlib.util.find_spec("pysat") is None:
        local = ROOT / ".venv/bin/python"
        if not local.exists() or os.path.abspath(sys.executable) == os.path.abspath(local):
            raise RuntimeError("raw clause replay requires python-sat")
        os.execv(local, [str(local), "-B", __file__])
    print(json.dumps(run(), indent=2, sort_keys=True))
