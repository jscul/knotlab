"""Strict circuits for two product checksums and a degree-two refutation on their original clauses."""
from itertools import product
from pathlib import Path
import runpy
from types import SimpleNamespace


def _dependency(ticket, slug):
    rel = Path("proofs") / ticket / (ticket+"-P001_"+slug) / "solver.py"
    for root in (*Path(__file__).resolve().parents, Path.cwd()):
        if (root / rel).is_file():
            return runpy.run_path(str(root / rel))
    raise FileNotFoundError(rel)


Q = SimpleNamespace(**_dependency("QUADRATIC-ROUTE-TRANSFER-20261115-001A", "quadratic_substitution"))
cut = _dependency("PRODUCT-NAME-TRANSFER-20261115-001B", "bounded_elimination")["cut"]


def wires(shape, m):
    if type(m) is not int or m < 1 or shape not in ("star", "path"):
        raise ValueError("expected a nonempty path or star")
    return [(1 if shape == "star" else i, i+1) for i in range(1, m+1)]


def encode(shape, m, charge=1, *, factor_right=False):
    edges = wires(shape, m)
    if factor_right and (shape != "path" or m % 2):
        raise ValueError("neighbor sums regroup an even number of path edges")
    if type(charge) is not int or charge not in (0, 1):
        raise ValueError("invalid checksum charge")
    n = m+1
    cnf = []

    def fresh():
        nonlocal n
        n += 1
        return n

    def relation(kind, variables, bit=0):
        forbidden = {}
        for values in product((0, 1), repeat=len(variables)):
            wrong = (values[0]*values[1] != values[2] if kind == "and" else
                     sum(values) % 2 != bit)
            if not wrong:
                continue
            clause = [(-v if b else v) for v,b in zip(variables, values)]
            start = len(cnf)
            if len(clause) == 2:
                aux = fresh()
                cnf.extend([clause+[aux], clause+[-aux]])
            else:
                cnf.append(clause)
                aux = None
            forbidden[values] = (start, aux)
        return {"kind":kind, "variables":tuple(variables), "charge":bit, "forbidden":forbidden}

    def evaluator(factor):
        pairs, additions, neighbor_sums = [], [], []
        if factor:
            for i in range(0,m,2):
                left, middle = edges[i]
                right = edges[i+1][1]
                summed = relation("xor",(left,right,fresh()))
                neighbor_sums.append(summed)
                pairs.append(relation("and",(middle,summed["variables"][-1],fresh())))
        else:
            for left, right in edges:
                pairs.append(relation("and", (left, right, fresh())))
        current = pairs[0]["variables"][-1]
        for gate in pairs[1:]:
            step = relation("xor", (current, gate["variables"][-1], fresh()))
            additions.append(step)
            current = step["variables"][-1]
        return {"products":pairs,"additions":additions,"neighbor_sums":neighbor_sums,"checksum":current}

    first, second = evaluator(False), evaluator(factor_right)
    terminal = relation("xor", (first["checksum"], second["checksum"]), charge)
    return {"shape":shape, "m":m, "n":n, "cnf":cnf, "edges":edges, "sides":(first,second),
            "terminal":terminal}


def _shift(f, b):
    return Q.add(f,Q.ONE) if b else f


def _equation(gate):
    v = gate["variables"]
    if gate["kind"] == "and":
        return Q.add(Q.var(v[-1]),Q.mul(Q.var(v[0]),Q.var(v[1])))
    return Q.polynomial(([()] if gate["charge"] else [])+[(i,) for i in v])


def _conditional_value(dag, equation, bits):
    ref, acc = dag.true(), Q.ZERO
    for term in equation:
        if not term:
            continue
        x = term[0]
        selected = _shift(Q.var(x),bits[x])
        local = dag.boolean(x)
        if len(term) == 2:
            y = term[1]
            local = dag.multiply(local, selected, Q.var(y))
            selected = Q.mul(selected,Q.var(y))
            if bits[x]:
                y_value = _shift(Q.var(y),bits[y])
                local = dag.combine(local,dag.boolean(y),selected,y_value)
                selected = Q.add(selected,y_value)
        ref = dag.combine(ref,local,acc,selected)
        acc = Q.add(acc,selected)
    if acc != equation:
        raise ValueError("the gate equation failed at this assignment")
    return ref


def derive_gate(dag, gate):
    """Derive one reusable singleton from its own four strict rows, with local Boolean cases."""
    variables, equation = gate["variables"], _equation(gate)
    refs = []
    for values in product((0,1),repeat=len(variables)):
        failures = tuple(_shift(Q.var(v),1^b) for v,b in zip(variables,values))
        if values in gate["forbidden"]:
            idx, aux = gate["forbidden"][values]
            node = dag.axiom(idx)
            if aux is not None:
                node = dag.resolve(node,dag.axiom(idx+1),aux)
            if dag.clauses[node] != tuple(sorted(failures)):
                raise ValueError("wrong source for forbidden gate assignment")
        else:
            node = _conditional_value(dag,equation,dict(zip(variables,values)))
        refs.append(dag.weaken(node,(*failures,equation)))
    for level in reversed(range(len(variables))):
        next_level = []
        for j, prefix in enumerate(product((0,1),repeat=level)):
            context = [equation,*[_shift(Q.var(v),1^b) for v,b in zip(variables,prefix)]]
            next_level.append(cut(dag,refs[2*j],refs[2*j+1],_shift(Q.var(variables[level]),1),context))
        refs = next_level
    if dag.clauses[refs[0]] != (equation,):
        raise AssertionError("the closing unit lost its gate equation")
    return refs[0]


def _add_units(dag, left, right):
    a, = dag.clauses[left]
    b, = dag.clauses[right]
    return dag.combine(left,right,a,b)


def refutation(instance):
    if instance["terminal"]["charge"] != 1:
        raise ValueError("equal checksums have a common model")
    dag = Q.Dag(instance["cnf"])
    first, second = instance["sides"]
    if second["neighbor_sums"]:
        return _factored_refutation(instance,dag,first,second)
    equality = None
    equal_products, equal_sums, first_join = [], [], None
    for i,(gate, other) in enumerate(zip(first["products"],second["products"])):
        left, right = derive_gate(dag,gate), derive_gate(dag,other)
        pair = _add_units(dag,left,right)
        equal_products.append(pair)
        if i == 0:
            first_join = {"inputs":gate["variables"][:2],"parents":[left,right],
                          "row":pair,"deduction":dag.proof[pair]}
            equality = pair
        else:
            add_left = derive_gate(dag,first["additions"][i-1])
            add_right = derive_gate(dag,second["additions"][i-1])
            carry = _add_units(dag,add_left,add_right)
            carry = _add_units(dag,carry,equality)
            equality = _add_units(dag,carry,pair)
        equal_sums.append(equality)
    opposite = derive_gate(dag,instance["terminal"])
    false = _add_units(dag,opposite,equality)
    if dag.clauses[false] != (Q.ONE,):
        raise ValueError("the input did not yield a false equation")
    empty = dag.delete_false(false)
    return dag, {"first_quadratic_cancellation":first_join, "equal_products":equal_products,
                 "equal_checksums":equal_sums, "opposite":opposite, "false":false, "empty":empty}


def _factored_refutation(instance, dag, first, second):
    equality = None
    group_rows = []
    first_join = None
    for i,(summed,right_gate) in enumerate(zip(second["neighbor_sums"],second["products"])):
        j = 2*i
        left_gates = first["products"][j:j+2]
        middle = right_gate["variables"][0]
        linear = derive_gate(dag,summed)
        scaled = dag.multiply(linear,_equation(summed),Q.var(middle))
        group = scaled
        for gate in [*left_gates,right_gate]:
            group = _add_units(dag,group,derive_gate(dag,gate))
        products = [gate["variables"][-1] for gate in [*left_gates,right_gate]]
        if dag.clauses[group] != (Q.polynomial((v,) for v in products),):
            raise AssertionError("the two neighboring terms did not combine into the factored term")
        if i == 0:
            first_join = {"sum_unit":linear,"scale_row":scaled,"scale_step":dag.proof[scaled],
                          "three_product_equality":group,"equality_step":dag.proof[group]}
        group_rows.append(group)
        equality = group if equality is None else _add_units(dag,equality,group)
        for pos in range(max(1,j),j+2):
            equality = _add_units(dag,equality,derive_gate(dag,first["additions"][pos-1]))
        if i:
            equality = _add_units(dag,equality,derive_gate(dag,second["additions"][i-1]))
    opposite = derive_gate(dag,instance["terminal"])
    false = _add_units(dag,opposite,equality)
    if dag.clauses[false] != (Q.ONE,):
        raise AssertionError("lost the terminal checksum difference")
    empty = dag.delete_false(false)
    return dag, {"first_distributive_step":first_join, "group_rows":group_rows,
                 "equal_checksums":equality,"opposite":opposite,"false":false,"empty":empty}


def honest_assignment(instance, raw):
    if len(raw) != instance["m"]+1 or any(v not in (0,1) for v in raw):
        raise ValueError("one input bit is needed per vertex")
    values = [0]+list(raw)+[0]*(instance["n"]-len(raw))
    for side in instance["sides"]:
        for gate in side["neighbor_sums"]:
            a,b,out = gate["variables"]
            values[out] = values[a] ^ values[b]
        for gate in side["products"]:
            x,y,p = gate["variables"]
            values[p] = values[x] & values[y]
        for gate in side["additions"]:
            prev,p,t = gate["variables"]
            values[t] = values[prev] ^ values[p]
    return values


def locate_difference(differences):
    """Identify a mismatching product using one parity question per halving."""
    if not differences or any(v not in (0,1) for v in differences) or sum(differences)%2 != 1:
        raise ValueError("an odd total difference is required")
    lo, hi, tests = 0, len(differences), []
    while hi-lo > 1:
        middle = (lo+hi)//2
        answer = sum(differences[lo:middle]) % 2
        tests.append((lo,middle,answer))
        if answer:
            hi = middle
        else:
            lo = middle
    return lo, tests


def block_cases(m, block_size):
    """Bounds with both running checksums visible only at a fixed sequence of block boundaries."""
    if type(m) is not int or m < 1 or type(block_size) is not int or block_size < 1:
        raise ValueError("positive path and block lengths are required")
    lengths = [min(block_size,m-start) for start in range(0,m,block_size)]
    ranks = [(width+1)//2 for width in lengths]
    return {"block_lengths":lengths,"extra_prefix_bits":2*(len(lengths)-1),
            "leaf_upper":sum(1 << r for r in ranks),
            "depth_upper":(len(lengths)-1).bit_length()+max(ranks)}
