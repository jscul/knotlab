"""Strict original-input checks, exact long-clause lifting and named F2 cancellation."""

from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import runpy


def _previous(ticket, slug):
    return Path(__file__).resolve().parents[3] / "proofs" / ticket / (ticket+"-P001_"+slug) / "solver.py"


named_path = _previous("PRODUCT-NAME-TRANSFER-20261115-001A","named_substitution")
spec = spec_from_file_location("signed_cycle_named_kernel",named_path)
A = module_from_spec(spec)
spec.loader.exec_module(A)
Q = A.q
cut_path = _previous("PRODUCT-NAME-TRANSFER-20261115-001B","bounded_elimination")
cut = runpy.run_path(str(cut_path))["cut"]
ZERO, ONE, var, add, mul = Q.ZERO, Q.ONE, Q.var, Q.add, Q.mul


def _shift(form, bit):
    return add(form,ONE) if bit else form


def _chain(clause, aux):
    if len(clause) != 8 or len(aux) != 5:
        raise ValueError("an eight-literal row has five private chain variables")
    return [[clause[0],clause[1],aux[0]],
            *[[-aux[j-1],clause[j+1],aux[j]] for j in range(1,5)],
            [-aux[-1],clause[-2],clause[-1]]]


def encode_checks(h, checks):
    """Encode ordered (i,j,charge) checks, with zero-based distinct report indices."""
    if type(h) is not int or h < 0:
        raise ValueError("invalid number of reports")
    public_n = 2+3*h
    triples = [tuple(range(3+3*i,6+3*i)) for i in range(h)]
    cnf,blocks = [],[]
    n = public_n
    for i,j,charge in checks:
        if (type(i) is not int or type(j) is not int or not 0 <= i < h or not 0 <= j < h
                or i == j or type(charge) not in (int,bool) or charge not in (0,1)):
            raise ValueError("expected two distinct report indices and one Boolean charge")
        charge = int(charge)
        variables = (1,2,*triples[i],*triples[j])
        rows = []
        for bits in product((0,1),repeat=8):
            a,b,x,y,z,xx,yy,zz = bits
            shared = a*b
            if (z*((x*y)^shared) ^ zz*((xx*yy)^shared)) == charge:
                continue
            clause = tuple(-v if bit else v for v,bit in zip(variables,bits))
            aux = tuple(range(n+1,n+6))
            rows.append({"bits":bits,"clause":clause,"start":len(cnf),"aux":aux})
            cnf.extend(_chain(clause,aux))
            n += 5
        blocks.append({"i":i,"j":j,"charge":charge,"variables":variables,"rows":rows})
    return {"n":n,"public_n":public_n,"a":1,"b":2,"triples":triples,"blocks":blocks,"cnf":cnf}


def encode_cycle(charges):
    charges = tuple(charges)
    if len(charges) < 3:
        raise ValueError("a simple cycle requires at least three reports")
    return encode_checks(len(charges),((i,(i+1)%len(charges),c) for i,c in enumerate(charges)))


def lift_row(dag, row):
    """Derive this forbidden assignment's length-eight clause from its six genuine input slots."""
    start,aux,clause = row["start"],row["aux"],row["clause"]
    if type(start) is not int or start < 0 or dag.cnf[start:start+6] != _chain(clause,aux):
        raise ValueError("row does not match the six actual source clauses")
    ref = dag.axiom(start)
    for index,pivot in enumerate(aux,1):
        ref = dag.resolve(ref,dag.axiom(start+index),pivot)
    if dag.clauses[ref] != Q.signed_clause(clause):
        raise ValueError("resolution failed to recover the original row")
    return ref


def named_prefix(instance):
    """Return the primitive proof prefix, its check-root indices and its quadratic report forms."""
    dag = A.Dag(instance["n"],instance["cnf"])
    a,b = instance["a"],instance["b"]
    triples = instance["triples"]
    shared, shared_def = dag.define(var(a),var(b))
    local = [dag.define(var(x),var(y)) for x,y,z in triples]
    reports = [mul(var(z),add(var(local[i][0]),var(shared))) for i,(x,y,z) in enumerate(triples)]

    @cache
    def value_of_product(x,y,xbit,ybit,name,definition):
        f,g = var(x),var(y)
        m = dag.multiply(dag.boolean(x),_shift(f,xbit),g)
        proved = dag.combine(m,dag.boolean(y),mul(_shift(f,xbit),g),_shift(g,ybit),1,xbit)
        p = mul(f,g)
        return dag.combine(proved,definition,_shift(p,xbit*ybit),add(var(name),p))

    @cache
    def report_value(i,abit,bbit,xbit,ybit,zbit):
        x,y,z = triples[i]
        lname,ldef = local[i]
        sa = value_of_product(a,b,abit,bbit,shared,shared_def)
        la = value_of_product(x,y,xbit,ybit,lname,ldef)
        kbit,lbit = abit*bbit,xbit*ybit
        inner = add(var(shared),var(lname))
        inside = dag.combine(sa,la,_shift(var(shared),kbit),_shift(var(lname),lbit))
        scaled = dag.multiply(dag.boolean(z),_shift(var(z),zbit),inner)
        combined = dag.combine(scaled,inside,mul(_shift(var(z),zbit),inner),_shift(inner,kbit^lbit),1,zbit)
        return zbit*(kbit^lbit),combined

    roots = []
    for block in instance["blocks"]:
        i,j,c = block["i"],block["j"],block["charge"]
        variables = block["variables"]
        equation = _shift(add(reports[i],reports[j]),c)
        forbidden = {tuple(row["bits"]):row for row in block["rows"]}
        refs = []
        for bits in product((0,1),repeat=8):
            av,bv,*tail = bits
            guards = tuple(_shift(var(v),1^value) for v,value in zip(variables,bits))
            if bits in forbidden:
                base = lift_row(dag,forbidden[bits])
                node = dag.weaken(base,(*guards,equation))
            else:
                ibit,ir = report_value(i,av,bv,*tail[:3])
                jbit,jr = report_value(j,av,bv,*tail[3:])
                if (ibit^jbit) != c:
                    raise ValueError("missing forbidden original-variable row")
                node = dag.combine(ir,jr,_shift(reports[i],ibit),_shift(reports[j],jbit))
                for shared_guard in guards[:2]:
                    node = dag.contract(node,shared_guard)
            if dag.clauses[node] != tuple(sorted((*guards,equation))):
                raise ValueError("a branch failed to derive its guarded check")
            refs.append(node)
        for level in reversed(range(8)):
            next_refs = []
            for j0,prefix in enumerate(product((0,1),repeat=level)):
                context = [equation,*[_shift(var(v),bit^1) for v,bit in zip(variables,prefix)]]
                next_refs.append(cut(dag,refs[2*j0],refs[2*j0+1],_shift(var(variables[level]),1),context))
            refs = next_refs
        if dag.clauses[refs[0]] != (equation,):
            raise ValueError("the check root is not the required singleton equation")
        roots.append(refs[0])
    return dag,roots,reports


def named_refutation(instance, order=None):
    """Combine all check equations in the supplied order; they must sum to the false constant."""
    dag,roots,reports = named_prefix(instance)
    order = list(range(len(roots))) if order is None else list(order)
    if not order or sorted(order) != list(range(len(roots))):
        raise ValueError("expected a permutation of all check roots")
    current = roots[order[0]]
    additions = []
    for j in order[1:]:
        other = roots[j]
        current = dag.combine(current,other,dag.clauses[current][0],dag.clauses[other][0])
        additions.append(current)
    if dag.clauses[current] != (ONE,):
        raise ValueError("the chosen checks do not sum to the false equation")
    end = dag.delete_false(current)
    A.verify(instance["n"],instance["cnf"],dag.proof)
    return dag, {"edge_roots":roots,"addition_nodes":additions,"false_unit":current,"empty":end,
                 "order":order,"report_forms":[Q.encode(f) for f in reports]}
