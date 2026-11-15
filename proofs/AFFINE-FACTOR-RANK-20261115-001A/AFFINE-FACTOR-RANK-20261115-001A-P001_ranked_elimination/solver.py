"""Eliminate named quadratic products using a supplied span of original affine factors."""
from functools import cache
from itertools import product
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
OLD = "PRODUCT-NAME-TRANSFER-20261115-001C"
prior = runpy.run_path(str(ROOT / "proofs" / OLD / (OLD + "-P001_depth_and_unrestricted") / "solver.py"))
A, B, Q = (prior[key] for key in ("A", "B", "Q"))
ZERO, ONE, add, var, opposite = (B[key] for key in ("ZERO", "ONE", "add", "var", "opposite"))


class AffineBasis:
    """A basis of linear parts over F2. Its coordinates also retain an affine constant."""

    def __init__(self, n, generators):
        Q["validate_cnf"](n, [])
        self.n = n
        self._pivots = {}
        forms = []
        for raw in generators:
            form = A["affine"](raw, n)
            linear = tuple(term for term in form if term)
            residual, used = self._reduce(self._bits(linear))
            if residual:
                coordinate = 1 << len(forms)
                self._pivots[residual.bit_length()] = (residual, used ^ coordinate)
                forms.append(linear)
        self.forms = tuple(forms)
        self.rank = len(forms)

    @staticmethod
    def _bits(linear):
        return sum(1 << (term[0] - 1) for term in linear if term)

    def _reduce(self, vector):
        used = 0
        while vector:
            entry = self._pivots.get(vector.bit_length())
            if entry is None:
                break
            pivot, coordinates = entry
            vector ^= pivot
            used ^= coordinates
        return vector, used

    def coordinates(self, raw):
        """Return (constant, basis bit mask), or None for a factor outside the span."""
        form = A["affine"](raw, None)
        if any(term and term[0] > self.n for term in form):
            return None
        residual, used = self._reduce(self._bits(form))
        return None if residual else (int(() in form), used)


def gate_cover(basis, definitions):
    """Pick an available original factor from either side of every formal definition."""
    covered = {}
    for name, left, right in definitions:
        for factor, other in ((left, right), (right, left)):
            coordinates = basis.coordinates(factor)
            if coordinates is not None:
                covered[name] = (*coordinates, other)
                break
        else:
            raise ValueError(f"neither factor of declaration {name} belongs to the supplied original span")
    return covered


def guard_equation_builder(dag, forms, bits, boolean):
    """Derive [sum of selected basis equations] with every branch failure as context."""
    if len(forms) != len(bits) or any(type(bit) not in (bool, int) or bit not in (0, 1) for bit in bits):
        raise ValueError("a branch must assign one bit to every basis form")
    selected = tuple(opposite(f) if bit else f for f, bit in zip(forms, bits))
    failures = tuple(opposite(f) for f in selected)

    @cache
    def derive(mask):
        if type(mask) is not int or mask < 0 or mask.bit_length() > len(forms):
            raise ValueError("invalid subset of the basis")
        total, node = ZERO, None
        for i, equation in enumerate(selected):
            if not mask & (1 << i):
                continue
            premise = boolean(forms[i])
            node = premise if node is None else dag.combine(node, premise, total, equation)
            total = add(total, equation)
        if node is None:
            node = dag.true()
        target = tuple(sorted((*failures, total)))
        if dag.clauses[node] != target:
            node = dag.weaken(node, target)
        return total, node

    return failures, derive


def eliminate(n, cnf, proof, generators):
    """Return an unnamed quadratic refutation of cnf and its rank and node counts."""
    named = A["verify"](n, cnf, proof)
    basis = AffineBasis(n, generators)
    cover = gate_cover(basis, B["declarations"](n, proof))
    dag = Q["Dag"](cnf)
    boolean = B["affine_boolean_builder"](dag)
    leaves = []

    for bits in product((0, 1), repeat=basis.rank):
        values = sum(bit << i for i, bit in enumerate(bits))
        context, guard_equation = guard_equation_builder(dag, basis.forms, bits, boolean)
        images = {i: var(i) for i in range(1, n + 1)}
        refs = []

        def image(raw):
            return B["affine_image"](raw, images)

        for row in proof:
            kind = row["rule"]
            if kind == "define":
                name = row["variable"]
                constant, mask, other = cover[name]
                value = constant ^ ((mask & values).bit_count() % 2)
                multiplier = image(other)
                images[name] = multiplier if value else ZERO
                selected, premise = guard_equation(mask)
                node = dag.multiply(premise, selected, multiplier)
            elif kind == "boolean":
                node = boolean(images[row["variable"]])
            elif kind == "axiom":
                node = dag.axiom(row["axiom"])
            elif kind == "true":
                node = dag.true()
            else:
                node = None
            target = tuple(image(atom) for atom in row["clause"])
            if node is None:
                node = B["guarded_step"](dag, row, refs, image, context, target)
            full = tuple(sorted((*context, *target)))
            if dag.clauses[node] != full:
                if kind not in ("boolean", "axiom", "true"):
                    raise ValueError("replayed deduction has a different image")
                node = dag.weaken(node, full)
            refs.append(node)
        leaves.append((refs[-1], context))

    while len(leaves) > 1:
        merged = []
        for (left, failures), (right, other_failures) in zip(leaves[::2], leaves[1::2]):
            prefix, pivot = failures[:-1], failures[-1]
            if other_failures != (*prefix, opposite(pivot)):
                raise ValueError("incompatible adjacent branch contexts")
            merged.append((B["cut"](dag, left, right, pivot, prefix), prefix))
        leaves = merged

    if leaves[0][0] != len(dag.proof) - 1:
        dag.weaken(leaves[0][0], ())
    Q["verify"](n, cnf, dag.proof)
    branches = 1 << basis.rank
    bound = 128 * branches * (n + basis.rank + 1) * (len(proof) + 1)
    if len(dag.proof) > bound:
        raise ValueError("the stated proof-node bound was exceeded")
    return dag.proof, {
        "basis": [Q["encode"](f) for f in basis.forms],
        "rank": basis.rank,
        "branches": branches,
        "declarations": len(cover),
        "maximum_definition_depth": named["maximum_definition_depth"],
        "chosen_factor_coordinates": [[constant, mask] for constant, mask, _ in cover.values()],
        "nodes": len(dag.proof),
        "verified_node_bound": bound,
    }
