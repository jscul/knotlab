"""Derive and compose four guarded endpoint equations in the unnamed degree-two kernel."""

from collections import Counter
from dataclasses import dataclass
from itertools import product
from pathlib import Path
import runpy


def _load_source():
    ticket = "SHARED-REPORT-CANCELLATION-20261115-001A"
    file = Path("proofs") / ticket / (ticket + "-P001_strict_checks") / "solver.py"
    # The current repository also supports a read-only replay from private scratch.
    for anchor in (Path(__file__).resolve().parent, Path.cwd().resolve()):
        for root in (anchor, *anchor.parents):
            if (root / file).is_file():
                return runpy.run_path(str(root / file))
    raise FileNotFoundError(file)


SOURCE = _load_source()
KERNEL = SOURCE["Q"]
cut = SOURCE["cut"]
ZERO, ONE = KERNEL.ZERO, KERNEL.ONE
add, mul, var = KERNEL.add, KERNEL.mul, KERNEL.var
PAIRS = tuple(product((0, 1), repeat=2))


@dataclass(frozen=True)
class GuardedEndpoints:
    """Four proof row IDs in lexicographic order of the endpoint selector bits."""

    start: int
    end: int
    charge: int
    rows: tuple[int, ...]

    def at(self, left_bit, right_bit):
        return self.rows[2 * left_bit + right_bit]

    def reversed(self):
        return GuardedEndpoints(self.end, self.start, self.charge,
                                tuple(self.at(b, a) for a, b in PAIRS))


def _failure(variable, bit):
    return KERNEL.literal(-variable if bit else variable)


def _evaluated_equation(dag, equation, assignment):
    """Derive the equation with assignment failures, using two literal choices per product."""
    node = dag.true()
    current = ZERO
    side = []
    for term in equation:
        if not term:
            continue
        x, y = term
        xbit, ybit = assignment[x], assignment[y]
        fx = add(var(x), ONE) if xbit else var(x)
        fy = add(var(y), ONE) if ybit else var(y)
        node_xy = dag.multiply(dag.boolean(x), fx, var(y))
        xy = mul(fx, var(y))
        side.append(_failure(x, xbit))
        if xbit:
            node_xy = dag.combine(node_xy, dag.boolean(y), xy, fy)
            xy = add(xy, fy)
            side.append(_failure(y, ybit))
        node = dag.combine(node, node_xy, current, xy)
        current = add(current, xy)
    if current != equation:
        raise ValueError("the requested equation is false at this assignment")
    for atom, copies in Counter(side).items():
        for _ in range(copies - 1):
            node = dag.contract(node, atom)
    return node


class GuardedProof:
    """Build one shared DAG from the exact strict CNF produced by encode_checks."""

    def __init__(self, instance):
        self.instance = instance
        self.dag = KERNEL.Dag(instance["cnf"])
        a, b = instance["a"], instance["b"]
        shared = mul(var(a), var(b))
        self.quadratics = [add(mul(var(x), var(y)), shared)
                           for x, y, _ in instance["triples"]]
        self.selectors = [z for _, _, z in instance["triples"]]
        self._edges = {}
        self.source_examples = {}

    def fail(self, endpoint, bit):
        return _failure(self.selectors[endpoint], bit)

    def equation(self, i, j, charge, u, w):
        result = ONE if charge else ZERO
        if u:
            result = add(result, self.quadratics[i])
        if w:
            result = add(result, self.quadratics[j])
        return result

    def edge(self, block_index):
        """Derive the four rows once. Reversing the result emits no proof nodes."""
        if type(block_index) is not int or not 0 <= block_index < len(self.instance["blocks"]):
            raise ValueError("invalid source block index")
        if block_index in self._edges:
            return self._edges[block_index]
        block = self.instance["blocks"][block_index]
        i, j, charge = block["i"], block["j"], block["charge"]
        xs = self.instance["triples"]
        free = (self.instance["a"], self.instance["b"], *xs[i][:2], *xs[j][:2])
        rows = {tuple(row["bits"]): row for row in block["rows"]}
        output = []
        for u, w in PAIRS:
            equation = self.equation(i, j, charge, u, w)
            target = (self.fail(i, u), self.fail(j, w), equation)
            if equation == ZERO:
                output.append(self.dag.weaken(self.dag.true(), target))
                continue
            leaves = []
            for bits in product((0, 1), repeat=len(free)):
                failures = tuple(_failure(v, b) for v, b in zip(free, bits))
                # The source encodes the two selectors alongside their own local pair.
                a, b, x, y, xx, yy = bits
                row = rows.get((a, b, x, y, u, xx, yy, w))
                if row is None:
                    node = _evaluated_equation(self.dag, equation, dict(zip(free, bits)))
                else:
                    node = SOURCE["lift_row"](self.dag, row)
                    if block_index not in self.source_examples:
                        original = list(range(row["start"], row["start"] + 6))
                        self.source_examples[block_index] = {
                            "forbidden_bits": list(row["bits"]),
                            "strict_cnf_indices": original,
                            "axiom_proof_indices": [self.dag.axiom(i) for i in original],
                            "recovered_width_eight_proof_index": node,
                        }
                node = self.dag.weaken(node, (*failures, *target))
                leaves.append((node, failures))
            while len(leaves) > 1:
                level = []
                for (left, first), (right, _) in zip(leaves[::2], leaves[1::2]):
                    context = (*first[:-1], *target)
                    root = cut(self.dag, left, right, first[-1], context)
                    level.append((root, first[:-1]))
                leaves = level
            output.append(leaves[0][0])
        record = GuardedEndpoints(i, j, charge, tuple(output))
        self._edges[block_index] = record
        return record

    def join(self, left, right):
        """Compose two oriented paths by canceling the shared quadratic under each bit value."""
        if left.end != right.start:
            raise ValueError("the path endpoints do not match")
        i, j, k = left.start, left.end, right.end
        joined_charge = left.charge ^ right.charge
        output = []
        for u, w in PAIRS:
            inner = []
            for v in (0, 1):
                a = self.equation(i, j, left.charge, u, v)
                b = self.equation(j, k, right.charge, v, w)
                node = self.dag.combine(left.at(u, v), right.at(v, w), a, b)
                inner.append(self.dag.contract(node, self.fail(j, v)))
            context = (self.fail(i, u), self.fail(k, w),
                       self.equation(i, k, joined_charge, u, w))
            output.append(cut(self.dag, *inner, self.fail(j, 0), context))
        return GuardedEndpoints(i, k, joined_charge, tuple(output))

    def close(self, loop):
        """Discharge the two remaining selector values of an odd closed path."""
        if loop.start != loop.end or loop.charge != 1:
            raise ValueError("contradiction requires an odd closed path")
        sides = []
        for u in (0, 1):
            node = self.dag.contract(loop.at(u, u), self.fail(loop.start, u))
            sides.append(self.dag.delete_false(node))
        return cut(self.dag, *sides, self.fail(loop.start, 0), ())

    def verify(self):
        return KERNEL.verify(self.instance["n"], self.instance["cnf"], self.dag.proof)

