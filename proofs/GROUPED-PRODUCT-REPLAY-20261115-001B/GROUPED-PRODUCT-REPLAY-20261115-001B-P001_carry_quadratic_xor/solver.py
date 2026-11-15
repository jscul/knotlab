"""Checked multiset degree-two substitution of a quadratic XOR at a proof boundary."""

from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3] / "proofs"


def _source(scope, slug):
    return ROOT / scope / (scope + "-P001_" + slug) / "solver.py"


_named = _source("PRODUCT-NAME-TRANSFER-20261115-001A", "named_substitution")
_spec = spec_from_file_location("grouped_xor_named", _named)
A = module_from_spec(_spec)
_spec.loader.exec_module(A)
Q = A.q
B = runpy.run_path(str(_source("PRODUCT-NAME-TRANSFER-20261115-001B", "bounded_elimination")))
ZERO, ONE, var, add, mul = Q.ZERO, Q.ONE, Q.var, Q.add, Q.mul


def quadratic_xor(n, pairs):
    """Return sum x_i*y_i as a formal polynomial on distinct original coordinates."""
    Q.validate_cnf(n, [])
    terms, seen = [], set()
    for pair in pairs:
        if len(pair) != 2:
            raise ValueError("each product requires two coordinates")
        x, y = pair
        if (type(x) is not int or type(y) is not int or not 1 <= x <= n or not 1 <= y <= n
                or x == y or x in seen or y in seen):
            raise ValueError("expected disjoint original coordinate pairs")
        seen.update((x, y))
        terms.append((x, y))
    return Q.polynomial(terms)


def boolean_quadratic(dag, form):
    """Derive [form] or [form+1] from Boolean axioms of the variables actually used."""
    if dag.convention != "multiset":
        raise ValueError("expected occurrence-counted multiset clauses")
    value = Q.checked_poly(form, getattr(dag, "live", None))
    terms = [term for term in value if term]
    if not terms:
        return dag.weaken(dag.true(), (ZERO, ONE))
    prefix = ZERO
    total = None
    for term in terms:
        x = term[0]
        term_row = dag.boolean(x)
        atom = (term,)
        if len(term) == 2:
            y = term[1]
            term_row = B["boolean_gate"](dag, var(x), term_row, var(y), dag.boolean(y), product_gate=True)
        if total is None:
            total = term_row
        else:
            total = B["boolean_gate"](dag, prefix, total, atom, term_row, product_gate=False)
        prefix = add(prefix, atom)
    # A constant exchanges the two atoms of the same Boolean disjunction.
    if dag.clauses[total] != tuple(sorted((value, add(value, ONE)))):
        raise ValueError("wrong derived Boolean disjunction")
    return total


def _checked_prefix(n, cnf, rows):
    """Validate every real deduction even when its last line is a guarded clause."""
    for row in rows:
        if row["rule"] == "axiom":
            index = row["axiom"]
            if type(index) is not int or not 0 <= index < len(cnf):
                raise ValueError("prefix axiom is outside the genuine input")
    # The extra axiom occurs only after every real row. It lets the complete
    # refutation checker validate the prefix without making a new premise available to it.
    terminal = {"rule": "axiom", "axiom": len(cnf), "clause": []}
    A.verify(n, [*cnf, []], [*rows, terminal])


def _resume(n, cnf, prefix):
    _checked_prefix(n, cnf, prefix)
    out = A.Dag(n, cnf)
    out.proof = list(prefix)
    out.clauses = [Q.clause((Q.polynomial(raw) for raw in row["clause"]), "multiset") for row in prefix]
    out.live += sum(row["rule"] == "define" for row in prefix)
    return out


def replay_suffix(n, cnf, proof, cut, *, output_prefix=(), images=None, imports=None, guard=()):
    """Transfer a suffix of a checked refutation. Input variables keep their IDs.

    Map used pre-cut name IDs to formal polynomials in the output prefix.
    Imports map old pre-cut node indices to already derived output-prefix nodes.
    A common list of guard atoms may be attached to every replayed conclusion.
    Return fresh raw output rows and a report identifying the final line.
    """
    A.verify(n, cnf, proof)
    if type(cut) is not int or not 0 <= cut < len(proof):
        raise ValueError("the suffix must include the final proof row")
    out = _resume(n, cnf, output_prefix)
    old_live = n + sum(row["rule"] == "define" for row in proof[:cut])
    known = {}
    for v, value in (images or {}).items():
        if type(v) is not int or not n < v <= old_live:
            raise ValueError("images may specify only old pre-cut names")
        known[v] = Q.checked_poly(value, out.live)
    context = tuple(Q.checked_poly(atom, out.live) for atom in guard)
    imported = dict(imports or {})
    if any(type(i) is not int or not 0 <= i < cut or type(j) is not int or not 0 <= j < len(output_prefix)
           for i, j in imported.items()):
        raise ValueError("boundary import is outside one of the prefixes")

    def variable_image(v):
        if v <= n:
            return var(v)
        if v not in known:
            raise ValueError(f"missing image for pre-cut name {v}")
        return known[v]

    def image(raw):
        result = ZERO
        for term in Q.polynomial(raw):
            product = ONE
            for v in term:
                product = mul(product, variable_image(v))
            result = add(result, product)
        return Q.checked_poly(result, out.live)

    @cache
    def boolean(form):
        return boolean_quadratic(out, form)

    def mapped_clause(step):
        return tuple(sorted(image(f) for f in step["clause"]))

    def with_context(ref, bare):
        guarded = tuple(sorted((*bare, *context)))
        actual = out.clauses[ref]
        if actual == guarded:
            return ref
        if actual == bare:
            return out.weaken(ref, guarded)
        raise ValueError("imported or derived line disagrees with the mapped multiset")

    def initial(step, bare):
        kind = step["rule"]
        if kind == "axiom":
            return out.axiom(step["axiom"])
        if kind == "boolean":
            return boolean(variable_image(step["variable"]))
        if kind == "true" or bare == (ZERO,):
            return out.true()
        raise ValueError("a nontrivial pre-cut parent needs an exact derived import")

    refs = {}
    def import_parent(i):
        bare = mapped_clause(proof[i])
        base = imported[i] if i in imported else initial(proof[i], bare)
        refs[i] = with_context(base, bare)

    for i in imported:
        import_parent(i)
    for i in range(cut, len(proof)):
        step = proof[i]
        kind = step["rule"]
        for parent in step.get("parents", ()):
            if parent not in refs:
                import_parent(parent)
        if kind == "define":
            # The retained declaration grammar requires two affine factors,
            # even when their product would simplify to zero.
            left, right = (A.affine(image(f), out.live) for f in step["factors"])
            name, ref = out.define(left, right)
            known[step["variable"]] = var(name)
            refs[i] = with_context(ref, mapped_clause(step))
            continue
        bare = mapped_clause(step)
        if kind in ("axiom", "true", "boolean"):
            refs[i] = with_context(initial(step, bare), bare)
            continue
        # guarded_step checks imaged selections and explicit multipliers as
        # well as the conclusion. Its binary step removes the extra guard copy.
        ref = B["guarded_step"](out, step, refs, image, context, bare)
        if out.clauses[ref] != tuple(sorted((*bare, *context))):
            raise ValueError("replayed rule changed the required side occurrences")
        refs[i] = ref
    last = refs[len(proof)-1]
    if out.clauses[last] != tuple(sorted(context)):
        raise ValueError("wrong final guarded conclusion")
    if last != len(out.proof)-1:
        last = out.weaken(last, context)
    if context:
        _checked_prefix(n, cnf, out.proof)
    else:
        A.verify(n, cnf, out.proof)
    return out.proof, {"root": last, "replayed": len(proof)-cut, "guard_size": len(context),
                       "nodes_added": len(out.proof)-len(output_prefix),
                       "row_map": [[i, refs[i]] for i in range(cut,len(proof))]}


def xor_boundary(n, proof, pairs, pair_names, xor_name):
    """Authenticate pair products and the linear name U=(sum p_i)*1."""
    pairs, pair_names = tuple(pairs), tuple(pair_names)
    form = quadratic_xor(n, pairs)
    if (len(pair_names) != len(pairs) or any(type(v) is not int or v <= n for v in (*pair_names, xor_name))
            or len(set((*pair_names, xor_name))) != len(pairs)+1):
        raise ValueError("expected one fresh name per pair and a distinct XOR name")
    defs = {row["variable"]: (i, row) for i,row in enumerate(proof) if row["rule"] == "define"}
    def checked(name, f, g):
        if name not in defs:
            raise ValueError("missing declared boundary name")
        i, row = defs[name]
        actual = tuple(Q.polynomial(factor) for factor in row["factors"])
        if actual not in ((f,g),(g,f)):
            raise ValueError("declared factors disagree with the promised aggregate")
        expected = add(var(name),mul(f,g))
        if len(row["clause"]) != 1 or Q.polynomial(row["clause"][0]) != expected:
            raise ValueError("boundary equation does not define the stated aggregate")
        return i
    images, total, positions = {}, ZERO, []
    for name, (x,y) in zip(pair_names,pairs):
        positions.append(checked(name,var(x),var(y)))
        images[name] = mul(var(x),var(y))
        total = add(total,var(name))
    last = checked(xor_name,total,ONE)
    if any(i >= last for i in positions):
        raise ValueError("the XOR declaration must follow its pair definitions")
    images[xor_name] = form
    return last+1, images


def carry_xor(n, cnf, proof, pairs, pair_names, xor_name, *, output_prefix=(), imports=None, guard=()):
    """Carry an authenticated original XOR, emitting no replacement name for it."""
    cut, images = xor_boundary(n, proof, pairs, pair_names, xor_name)
    return replay_suffix(n, cnf, proof, cut, output_prefix=output_prefix, images=images,
                         imports=imports, guard=guard)
