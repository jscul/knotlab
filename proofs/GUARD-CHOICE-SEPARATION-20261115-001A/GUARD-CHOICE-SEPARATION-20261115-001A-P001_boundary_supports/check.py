"""Compare boundary tables and all supplied witness bits with the actual strict CNF."""

from collections import Counter
from contextlib import ExitStack
import hashlib
import importlib.util
from itertools import product
import json
import os
from pathlib import Path
from random import Random
import sys

from solver import analyze_cut, complete_raw_witness


ROOT = Path(__file__).resolve().parents[3]
RAW_READER = (ROOT / "proofs/TWO-RELAY-PADDING-20261115-001D"
              / "TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/check.py")
READER_SHA = "1aee23c9aa74c04ede148bf94dd5134b68b3f62f5bc29b1361b4e83f4ed3ffc7"
BASE_SHA = "54d7a006b78c876aa28901a8f06951cb9ef67ceb5325ad4c64adee7867bf78c6"
BITS = (0, 1)


def require(condition, text):
    if not condition:
        raise AssertionError(text)


def load(name, path, digest):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "raw encoding changed")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signed(variables, values):
    require(len(variables) == len(values), "incomplete simultaneous pin vector")
    return [var if bit else -var for var, bit in zip(variables, values)]


class RawFormula:
    def __init__(self, reader, base, stack, ms, ps):
        from pysat.solvers import Solver
        clauses, self.guards, self.hidden = reader.raw_layout(ms, ps, base)
        self.clauses = clauses
        self.sat = stack.enter_context(Solver(name="g3", bootstrap_with=clauses))
        self.boundaries = list(range(1, len(ms)//2+2))
        self.typed = [t for j, m in enumerate(ms) for t in (2*m, 2*ps[2*j]+1, 2*ps[2*j+1]+1)]

    def query(self, guard_pins, additional=(), witness=None):
        pins = list(guard_pins) + list(additional)
        if witness is not None:
            xs, values = witness
            pins.extend(signed(self.boundaries, xs))
            pins.extend(signed(self.hidden, values))
        return self.sat.solve(assumptions=pins)


def split_names(ms, ps, cut, port):
    changed_ms, changed_ps = list(ms), list(ps)
    labels, start = (changed_ps, 4*cut) if port % 2 else (changed_ms, 2*cut)
    pos = labels.index(port//2, start)
    labels[pos] = max(labels) + 1
    return changed_ms, changed_ps


def combine(left, right):
    return left[0][:-1] + right[0], left[1] + right[1]


class Audit:
    def __init__(self, reader, base, stack, ms, ps, cut, port):
        self.ms, self.ps, self.cut, self.port = ms, ps, cut, port
        self.left = RawFormula(reader, base, stack, ms[:2*cut], ps[:4*cut])
        self.right = RawFormula(reader, base, stack, ms[2*cut:], ps[4*cut:])
        self.joined = RawFormula(reader, base, stack, ms, ps)
        self.split = RawFormula(reader, base, stack, *split_names(ms, ps, cut, port))

    def coordinates(self, a, y, b):
        return signed([1, self.cut+1, len(self.ms)//2+1], [a, y, b])

    def run(self, raw, tally):
        result = analyze_cut(self.ms, self.ps, raw, self.cut)
        require(result.port == self.port, "incorrect crossing identity")
        open_raw = [0]*24 + list(raw[24:])
        cut_guard = 24*(self.cut + 1)
        halves = [(self.left, result.left, open_raw[:cut_guard]),
                  (self.right, result.right, [0]*24 + open_raw[cut_guard:])]
        for formula, table, local_raw in halves:
            guards = signed(formula.guards, local_raw)
            port_var = formula.hidden[formula.typed.index(self.port)]
            for l, r, h in product(BITS, repeat=3):
                keys = (l, r, h)
                fixed = signed([formula.boundaries[0], formula.boundaries[-1], port_var], keys)
                possible = formula.query(guards, fixed)
                require(possible == (keys in table), "local support differs from raw SAT")
                if possible:
                    require(formula.query(guards, fixed, table[keys]), "bad local complete witness")
                    tally["local_witnesses_pinned"] += 1
                tally["local_support_entries_checked"] += 1
        joint_pins = signed(self.joined.guards, open_raw)
        split_pins = signed(self.split.guards, open_raw)
        observed_lost = []
        original_outer, split_outer = set(), set()
        for a, y, b in product(BITS, repeat=3):
            fixed = self.coordinates(a, y, b)
            joined = self.joined.query(joint_pins, fixed)
            split = self.split.query(split_pins, fixed)
            left, right = result.masks(a, y, b)
            require(joined == bool(left & right) and split == bool(left and right),
                    "joined or split triple differs from raw SAT")
            if joined:
                original_outer.add((a, b))
                witness = result.witness(a, y, b)
                require(witness is not None and self.joined.query(joint_pins, fixed, witness),
                        "assembled witness fails the original raw formula")
                tally["joined_triple_witnesses_pinned"] += 1
            if split:
                split_outer.add((a, b))
                lv = next(v for v in BITS if left & (1<<v))
                rv = next(v for v in BITS if right & (1<<v))
                model = combine(result.left[a, y, lv], result.right[y, b, rv])
                require(self.split.query(split_pins, fixed, model), "bad split witness")
            if split and not joined:
                observed_lost.append((a, y, b))
            tally["triple_comparisons"] += 1
        require(tuple(observed_lost) == result.lost_triples(), "wrong displayed-triple loss")
        require(tuple(sorted(split_outer-original_outer)) == result.lost_outer_pairs(),
                "wrong outer projection")
        if observed_lost:
            tally["vectors_losing_a_triple"] += 1
        if split_outer != original_outer:
            tally["vectors_losing_an_outer_pair"] += 1
        actual_pins = signed(self.joined.guards, raw)
        answer = result.solve()
        require(self.joined.query(actual_pins) == (answer is not None), "guarded SAT differs")
        if answer is not None:
            require(self.joined.query(actual_pins, witness=answer), "bad actual guard-pinned model")
            tally["actual_guard_witnesses_pinned"] += 1
            model = complete_raw_witness(self.joined.clauses, self.joined.guards, self.joined.hidden,
                                         raw, answer)
            true = set(model)
            require(all(pin in true for pin in actual_pins) and
                    all(any(lit in true for lit in clause) for clause in self.joined.clauses) and
                    self.joined.query(actual_pins, model), "bad complete raw assignment")
            tally["full_raw_assignments_evaluated"] += 1
        tally["guard_vectors_checked"] += 1
        tally["max_local_mixed_pad_count"] = max(tally["max_local_mixed_pad_count"], *result.mixed)
        return result


def make_layout(stages, cut, role, rng):
    ms, ps = list(range(2*stages)), list(range(4*stages))
    port = None
    for kind, (labels, boundary) in enumerate(((ms, 2*cut), (ps, 4*cut))):
        left, right = list(range(boundary)), list(range(boundary, len(labels)))
        rng.shuffle(left)
        rng.shuffle(right)
        if kind == role:
            l, r = left.pop(), right.pop()
            labels[r] = labels[l]
            port = 2*labels[l] + kind
        for part in (left, right):
            for i in range(0, len(part)-1, 2):
                if rng.randrange(3):
                    labels[part[i+1]] = labels[part[i]]
    return ms, ps, port


def run():
    reader = load("nested_raw", RAW_READER, READER_SHA)
    base = load("strict_raw", reader.BASE, BASE_SHA)
    tally = Counter()
    ms, ps = [0, 1, 0, 3], [0, 1, 0, 3, 4, 5, 6, 7]
    with ExitStack() as stack:
        audit = Audit(reader, base, stack, ms, ps, 1, 0)
        # Left a -> (h OR y), right h -> b. Only y=1 glues at a=1,b=0.
        masked = reader.packed([1, 0, 2, 3, 0, 3, 0, 0])
        result = audit.run(masked, tally)
        require(result.lost_triples() == ((1, 0, 0),) and not result.lost_outer_pairs(),
                "outer-vs-displayed discriminator")
        require(result.mixed == (1, 0) and result.masks(1, 0, 0) == (2, 1)
                and result.masks(1, 1, 0) == (3, 1), "masked triple support values")
        tally["masked_external_example_lost_triples"] = len(result.lost_triples())
        tally["masked_external_example_lost_outer_pairs"] = len(result.lost_outer_pairs())
        # Both occurrences can constrain h. All triples still admit a common
        # witness, while some independently chosen side models disagree.
        same_direction = reader.packed([3, 0, 0, 0, 3, 0, 0, 0])
        safe = audit.run(same_direction, tally)
        require(not safe.lost_triples() and safe.masks(1, 0, 0) == (2, 3), "live safe cut")
        mismatch = combine(safe.left[1, 0, 1], safe.right[0, 0, 0])
        fixed = audit.coordinates(1, 0, 0)
        require(audit.split.query(signed(audit.split.guards, same_direction), fixed, mismatch)
                and not audit.joined.query(signed(audit.joined.guards, same_direction), fixed, mismatch),
                "independent mismatched witnesses silently glued")
        tally["safe_split_mismatched_witness_rejected"] = 1
        # Joining supports of h after erasing y would admit a spurious 10.
        missing_y = reader.packed([3, 0, 3, 3, 3, 0, 3, 3])
        mismatch_y = audit.run(missing_y, tally)
        opts = [mismatch_y.masks(1, y, 0) for y in BITS]
        require((opts[0][0] | opts[1][0]) & (opts[0][1] | opts[1][1])
                and not any(l & r for l, r in opts), "erased cut boundary did not create a false model")
        tally["omitted_cut_boundary_false_positive"] = 1

    shapes = [([0, 1, 0, 3], [0, 1, 0, 3, 4, 5, 4, 7], 0),
              ([0, 0, 2, 2], [0, 1, 2, 3, 0, 5, 6, 7], 1)]
    vectors = list(product(range(4), repeat=4))
    for mids, pads, port in shapes:
        with ExitStack() as stack:
            audit = Audit(reader, base, stack, mids, pads, 1, port)
            for i, left in enumerate(vectors):
                right = vectors[(71*i + 103) % 256]
                raw = reader.packed(left+right, start=bool(i % 2), end=bool(i % 3))
                audit.run(raw, tally)
    tally["one_stage_half_patterns_per_side_per_role"] = len(vectors)

    rng = Random(20261115)
    for stages in (3, 4, 5, 7):
        for role in BITS:
            cut = rng.randrange(1, stages)
            mids, pads, port = make_layout(stages, cut, role, rng)
            with ExitStack() as stack:
                audit = Audit(reader, base, stack, mids, pads, cut, port)
                for i in range(10):
                    raw = reader.packed([rng.randrange(4) for _ in range(4*stages)])
                    for j in range(0, len(raw), 3):
                        if not raw[j]:
                            mask = rng.randrange(7)
                            raw[j:j+3] = bytes((mask>>k)&1 for k in range(3))
                    if i % 3:
                        raw[rng.randrange(24)] = 0
                    audit.run(raw, tally)
    tally["largest_raw_replay_stages"] = 7
    rejected = 0
    for mids, pads, cut in [([0, 1, 2, 3], list(range(8)), 1),
                            ([0, 1, 0, 1], list(range(8)), 1),
                            ([0, 0, 0, 1], list(range(8)), 1), (ms, ps, 0)]:
        try:
            analyze_cut(mids, pads, reader.packed([0]*8), cut)
        except ValueError:
            rejected += 1
    require(rejected == 4, "invalid separator or occurrence cap accepted")
    tally["invalid_cuts_rejected"] = rejected
    return {"status": "passed", **tally}


if __name__ == "__main__":
    if importlib.util.find_spec("pysat") is None:
        local = ROOT / ".venv/bin/python"
        if not local.exists() or os.path.abspath(sys.executable) == os.path.abspath(local):
            raise RuntimeError("the raw replay requires python-sat")
        os.execv(local, [str(local), "-B", __file__])
    print(json.dumps(run(), indent=2, sort_keys=True))
