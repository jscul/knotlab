"""Actual named refutations with simultaneous AND and XOR boundary values."""

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import solver as S


A, Q, B = S.A, S.Q, S.B
var, add, mul, ZERO, ONE = S.var, S.add, S.mul, S.ZERO, S.ONE


def shifted(f, bit):
    return add(f, ONE) if bit else f


def strict_source(m):
    """Supply genuine input units for the shared literals and two distinct switch contexts."""
    xs = list(range(1,m+1))
    ys = list(range(m+1,2*m+1))
    switch, spare = 2*m+1,2*m+2
    n,cnf,recipes = spare,[],{}
    for v in xs[1:]+ys:
        p,q = n+1,n+2
        n += 2
        refs = list(range(len(cnf),len(cnf)+4))
        recipes[(v,)] = (refs,p,q)
        cnf.extend([[v,s*p,t*q] for s,t in product((1,-1),repeat=2)])
    for h,lit in product((switch,-switch),(xs[0],-xs[0])):
        n += 1
        refs = [len(cnf),len(cnf)+1]
        recipes[(h,lit)] = (refs,n)
        cnf.extend([[h,lit,n],[h,lit,-n]])
    return n,cnf,recipes,xs,ys,switch,spare


def derive_inputs(dag, recipes):
    result = {}
    for key,(refs,*pads) in recipes.items():
        nodes = [dag.axiom(i) for i in refs]
        if len(pads)==2:
            a,b = pads
            first,second = dag.resolve(nodes[0],nodes[1],b),dag.resolve(nodes[2],nodes[3],b)
            result[key] = dag.resolve(first,second,a)
        else:
            result[key] = dag.resolve(*nodes,pads[0])
    return result


def multiply_values(dag, first, second, definition=None):
    """Consume [f+i] and [g+j] with their actual side disjuncts."""
    f,i,ef = first
    g,j,eg = second
    val,p = i*j,mul(f,g)
    mult = dag.multiply(ef,shifted(f,i),g)
    node = dag.combine(mult,eg,mul(shifted(f,i),g),shifted(g,j),1,i)
    if definition is None:
        return p,val,node
    name,ref = definition
    out = var(name)
    return out,val,dag.combine(node,ref,shifted(p,val),add(out,p))


def sum_values(dag, terms, definition=None):
    value,bit,ref = terms[0]
    for f,j,node in terms[1:]:
        ref = dag.combine(ref,node,shifted(value,bit),shifted(f,j))
        value,bit = add(value,f),bit^j
    if definition is None:
        return value,bit,ref
    name,decl = definition
    out = var(name)
    return out,bit,dag.combine(ref,decl,shifted(value,bit),add(out,value))


def chain_definitions(dag, numbers):
    nodes = []
    current = numbers[0]
    for v in numbers[1:]:
        item = dag.define(var(current),var(v))
        nodes.append(item)
        current = item[0]
    return nodes


def make_prefix(n,cnf,recipes,xs,ys,switch,*,original):
    dag = A.Dag(n,cnf)
    pair_names, and_gates, ud = [], [], None
    if original:
        pair_names = [dag.define(var(x),var(y)) for x,y in zip(xs,ys)]
        and_gates = chain_definitions(dag,[name for name,_ in pair_names])
        total = Q.polynomial([(v,) for v,_ in pair_names])
        ud = dag.define(ONE,total)
    else:
        # Even the first fresh name is a cross-pair product when m>=2.
        and_gates = chain_definitions(dag,xs+ys)
    inputs = derive_inputs(dag,recipes)
    facts = {}
    for h in (switch,-switch):
        for first_bit in (0,1):
            values = {v:(var(v),1,inputs[(v,)]) for v in xs[1:]+ys}
            sign = xs[0] if first_bit else -xs[0]
            values[xs[0]] = var(xs[0]),first_bit,inputs[(h,sign)]
            pair_outputs = []
            if original or h < 0:
                for i,(x,y) in enumerate(zip(xs,ys)):
                    definition = pair_names[i] if original else None
                    pair_outputs.append(multiply_values(dag,values[x],values[y],definition))
            if h > 0:
                factors = pair_outputs if original else [values[v] for v in xs+ys]
                result = factors[0]
                for term,definition in zip(factors[1:],and_gates):
                    result = multiply_values(dag,result,term,definition)
            else:
                result = sum_values(dag,pair_outputs,ud)
            value,bit,node = result
            assert dag.clauses[node] == tuple(sorted((Q.literal(h),shifted(value,bit))))
            facts[(h,bit)] = node
    return dag, pair_names, and_gates[-1][0], ud, facts, inputs


def fixture(m=2, *, control=None):
    """Return the complete old refutation and certified pair-free output prefix for replay_suffix.

    'live_cubic' includes a genuine used U-times-variable deduction. The other
    negative controls insert separate malformed-for-the-image, valid-old-domain uses.
    """
    if m < 2:
        raise ValueError("the simultaneous crossed-chain fixture uses at least two pairs")
    n,cnf,recipes,xs,ys,switch,spare = strict_source(m)
    old, pair_names, old_and, ud, before, inputs = make_prefix(n,cnf,recipes,xs,ys,switch,original=True)
    new, _, new_and, _, after, _ = make_prefix(n,cnf,recipes,xs,ys,switch,original=False)
    u = ud[0]
    q = S.quadratic_xor(n,zip(xs,ys))
    cut = len(old.proof)
    imports = {node:after[key] for key,node in before.items()}
    # Force the primitive Boolean-default replay and its two true alternatives.
    # Resolving it against the first supplied parity condition returns that
    # condition with precisely its original occurrence context.
    eb = old.boolean(u)
    fact = before[(-switch,0)]
    passthrough = old.resolve(fact,eb,-u)
    assert old.clauses[passthrough] == old.clauses[fact]
    if control == "live_cubic":
        positive_y = inputs[(ys[0],)]
        imports[positive_y] = next(i for i,row in enumerate(new.clauses) if row == (shifted(var(ys[0]),1),))
        y = var(ys[0])
        a = old.multiply(passthrough,var(u),y)
        b = old.multiply(before[(-switch,1)],shifted(var(u),1),y)
        node = old.combine(a,b,mul(var(u),y),mul(shifted(var(u),1),y))
        node = old.resolve(positive_y,node,ys[0])
        xor_case = old.contract_all(node)
    else:
        if control == "retain_quadratic_factor":
            old.define(var(u),ZERO)
        elif control == "hidden_multiplier":
            zero = old.true()
            old.multiply(zero,ZERO,mul(var(u),var(spare)))
        elif control == "formal_square":
            old.multiply(eb,var(u),var(u))
        elif control == "aggregate_product":
            old.multiply(eb,var(u),var(old_and))
        elif control == "leaked_and_definition":
            ref = next(i for i,row in enumerate(old.proof) if row["rule"]=="define" and row["variable"]==old_and)
            atom = old.clauses[ref][0]
            used = old.combine(passthrough,ref,var(u),atom)
            passthrough = old.combine(used,ref,add(var(u),atom),atom)
        elif control is not None:
            raise ValueError("unknown fixture control")
        # Multiplication of another atom under a disjunct containing U.
        y,z = map(var,ys[:2])
        enlarged = old.weaken(passthrough,(*old.clauses[passthrough],y))
        mult = old.multiply(enlarged,y,z)
        f = multiply_values(old,(y,1,inputs[(ys[0],)]),(z,1,inputs[(ys[1],)]))[2]
        for v in ys[:2]:
            imports[inputs[(v,)]] = next(i for i,row in enumerate(new.clauses) if row == (shifted(var(v),1),))
        controlled = old.delete_false(old.combine(mult,f,mul(y,z),shifted(mul(y,z),1)))
        xor_case = old.resolve(controlled,before[(-switch,1)],-u)
    and_case = old.resolve(before[(switch,1)],before[(switch,0)],old_and)
    old.resolve(and_case,xor_case,switch)
    assert A.verify(n,cnf,old.proof)["declarations"] == 2*m + int(control == "retain_quadratic_factor")
    details = {"pairs":tuple(zip(xs,ys)), "pair_names":tuple(k for k,_ in pair_names),
               "xor_name":u, "old_and":old_and, "new_and":new_and, "switch":switch, "spare":spare}
    args = {"output_prefix":new.proof, "images":{old_and:var(new_and),u:q}, "imports":imports}
    return n,cnf,old.proof,cut,args,details


def truth_replay(n,cnf,rows):
    """Check each actual deduction on every input, interpreting every fresh name."""
    width = 1 << n
    universe = (1 << width)-1
    values = {}
    for v in range(1,n+1):
        stride = 1 << (v-1)
        column = ((1 << stride)-1) << stride
        length = 2*stride
        while length < width:
            column |= column << length
            length *= 2
        values[v] = column
    def polynomial(raw):
        total = 0
        for term in raw:
            m = universe
            for v in term:
                m &= values[v]
            total ^= m
        return total
    def disjunction(terms):
        out = 0
        for t in terms:
            out |= t
        return out
    meanings = []
    for row in rows:
        rule = row["rule"]
        if rule == "define":
            f,g = row["factors"]
            values[row["variable"]] = polynomial(f) & polynomial(g)
        result = disjunction(universe ^ polynomial(a) for a in row["clause"])
        if rule == "axiom":
            expected = disjunction(values[abs(lit)] ^ (universe if lit < 0 else 0) for lit in cnf[row["axiom"]])
            assert result == expected
        elif rule in ("boolean","true","define"):
            assert result == universe
        else:
            both = universe
            for j in row["parents"]:
                both &= meanings[j]
            assert not (both & ~result)
        meanings.append(result)
    return width


def boundary_check(m,meta,old,new):
    pairs = meta["pairs"]
    seen = set()
    def name_values(rows,assignment):
        values = {j+1:(assignment >> j)&1 for j in range(2*m)}
        for row in rows:
            if row["rule"] == "define":
                def affine(raw):
                    return sum(values[t[0]] if t else 1 for t in raw)%2
                f,g = row["factors"]
                values[row["variable"]] = affine(f)*affine(g)
        return values
    for assignment in range(1 << (2*m)):
        before,after = name_values(old,assignment),name_values(new,assignment)
        products = [before[x]*before[y] for x,y in pairs]
        bit = sum(products) % 2
        assert [before[v] for v in meta["pair_names"]] == products
        assert before[meta["xor_name"]]==bit and before[meta["old_and"]]==after[meta["new_and"]]==all(products)
        seen.add((int(all(products)),bit))
    assert seen == {(0,0),(0,1),(1,m%2)}
    # Every output product in the crossed chain contains x_1 and x_2.
    # A single original pair cannot be such a function on independent inputs.
    originals = {frozenset((x,y)) for x,y in pairs}
    supports = {}
    for row in new:
        if row["rule"] == "define":
            ls = [Q.polynomial(f) for f in row["factors"]]
            assert all(len(f)==len(f[0])==1 for f in ls)
            x,y = (f[0][0] for f in ls)
            support = supports.get(x,frozenset([x])) | supports.get(y,frozenset([y]))
            assert support not in originals
            supports[row["variable"]] = support
    assert len(supports) == 2*m-1
    return len(seen)


def alias_bridge(tally):
    n,pairs = 5,((1,3),(2,4))
    cnf = [[5],[-5]]
    old = A.Dag(n,cnf)
    pr = [old.define(var(x),var(y)) for x,y in pairs]
    names = [v for v,_ in pr]
    total = add(var(names[0]),var(names[1]))
    u,ur = old.define(total,ONE)
    alias = add(var(u),total)
    cancel = old.multiply(ur,alias,var(5))
    zero = old.true()
    old.multiply(zero,ZERO,var(u))  # A quadratic image is a legal displayed multiplier.
    eb = old.boolean(u)
    wider = old.weaken(eb,(*old.clauses[eb],ONE))
    scaled = old.multiply(wider,ONE,var(u))
    old.contract(scaled,var(u))
    # The factors of this retained gate become the affine pair (0,z).
    keep,kr = old.define(alias,var(5))
    p = mul(alias,var(5))
    net = old.combine(cancel,kr,p,add(var(keep),p))
    unit = old.combine(old.axiom(0),net,Q.literal(5),var(keep))
    restore = old.combine(unit,net,add(Q.literal(5),var(keep)),var(keep))
    old.resolve(restore,old.axiom(1),5)
    encoded,info = S.carry_xor(n,cnf,old.proof,pairs,names,u)
    assert A.verify(n,cnf,encoded)["declarations"]==1
    assert next(r for r in encoded if r["rule"]=="define")["factors"] == [[],[[5]]]
    assert any(r["rule"]=="multiply" and Q.polynomial(r["chosen"])==ONE and
               Q.polynomial(r["multiplier"])==S.quadratic_xor(n,pairs) for r in encoded)
    truth_replay(n,cnf,encoded)
    tally["alias_cancellation_retained_gate_nodes"] = info["nodes_added"]
    return n,cnf,old.proof,pairs,names,u


def reject(fn, target):
    try:
        fn()
    except ValueError as error:
        assert target in str(error),str(error)
        return 1
    raise AssertionError("accepted control expected to fail: "+target)


def rewrite_record():
    n,cnf,old,cut,args,meta = fixture()
    new,info = S.replay_suffix(n,cnf,old,cut,**args)
    return {"base_variables":n,"cnf":cnf,**meta,
            "cut":cut,"output_prefix_length":len(args["output_prefix"]),
            "name_images":[[name,Q.encode(value)] for name,value in args["images"].items()],
            "boundary_imports":list(map(list,args["imports"].items())),
            "suffix_row_map":info["row_map"],"before":old,"after":new}


def single_port_polynomials():
    # Q=x*y. Expand by replacing each occurrence of U by the two formal
    # variables; coefficient cancellations are independent of the solver.
    terms = ((),(1,),(2,),(3,),(1,1),(1,2),(1,3),(2,2),(2,3),(3,3))
    allowed = 0
    for mask in range(1 << len(terms)):
        before = [t for i,t in enumerate(terms) if mask >> i & 1]
        coefficients = Counter(tuple(sorted(v for identifier in t
                                          for v in ((1,2) if identifier==3 else (identifier,))))
                               for t in before)
        degree = max((len(t) for t,count in coefficients.items() if count%2),default=0)
        only_additive = all(3 not in t or t==(3,) for t in before)
        assert (degree<=2)==only_additive
        allowed += (degree<=2)
    return allowed


def main():
    for path,digest in ((S._named,"d81e4f0e8dfc8b8260587d0b7f19672bfaef87827665c8689167b72100806929"),
                        (S._source("PRODUCT-NAME-TRANSFER-20261115-001B","bounded_elimination"),
                         "7a381b7606d03304391fc1fc5e1bab52e53b55637187aaa1ced3b5aeae939312"),
                        (Path(Q.__file__),"84a7cdc149c8945061e8c46daaf9b3686cbcf4cee26f73b4e79c663bda25b71e")):
        assert sha256(Path(path).read_bytes()).hexdigest()==digest
    tally = Counter()
    for m in (0,1,2,3,4,8,16):
        n=2*m
        pairs=[(i,i+m) for i in range(1,m+1)]
        q = S.quadratic_xor(n,pairs)
        dag = A.Dag(n,[])
        end = S.boolean_quadratic(dag,q)
        S._checked_prefix(n,[],dag.proof)
        assert dag.clauses[end] == tuple(sorted((q,add(q,ONE))))
        assert len(dag.proof) == (50*m-22 if m else 2)
        tally["largest_checked_boolean_xor_nodes"] = max(tally["largest_checked_boolean_xor_nodes"],len(dag.proof))
    terms = ((),(1,),(2,),(1,1),(1,2),(2,2))
    for mask in range(64):
        f = Q.polynomial(t for i,t in enumerate(terms) if mask >> i & 1)
        dag = A.Dag(2,[])
        end = S.boolean_quadratic(dag,f)
        assert dag.clauses[end] == tuple(sorted((f,add(f,ONE))))
        S._checked_prefix(2,[],dag.proof)
        truth_replay(2,[],dag.proof)
        tally["two_variable_formal_quadratic_defaults"] += 1
    for m in (2,3,4,5):
        n,cnf,old,cut,args,meta = fixture(m)
        assert all(len(r)==len({abs(v) for v in r})==3 for r in cnf)
        new,stats = S.replay_suffix(n,cnf,old,cut,**args)
        assert A.verify(n,cnf,new)["declarations"] == 2*m-1
        assert len(new)==100*m-6 and stats["replayed"]==17
        assert boundary_check(m,meta,old,new) == 3
        tally["joint_report_assignments_checked"] += 1 << (2*m)
        tally["largest_checked_simultaneous_refutation"] = max(tally["largest_checked_simultaneous_refutation"],len(new))
        if m==2:
            assert truth_replay(n,cnf,old)==truth_replay(n,cnf,new)==(1<<n)
            tally["all_original_assignments_per_strict_proof"] = 1 << n
            tally["two_pair_old_nodes"],tally["two_pair_new_nodes"] = len(old),len(new)
    # A quadratic guard coincides with some replayed atoms. Merge complementary
    # guards by an ordinary selected quadratic pivot in the same checked proof.
    n,cnf,old,cut,args,meta = fixture()
    q = args["images"][meta["xor_name"]]
    before,one = S.replay_suffix(n,cnf,old,cut,guard=[q],**args)
    after,two = S.replay_suffix(n,cnf,old,cut,guard=[add(q,ONE)],**{**args,"output_prefix":before})
    dag = S._resume(n,cnf,after)
    dag.delete_false(dag.combine(one["root"],two["root"],q,add(q,ONE)))
    assert A.verify(n,cnf,dag.proof)["declarations"]==3
    tally["complementary_quadratic_guard_refutation_nodes"] = len(dag.proof)
    duplicated,info = S.replay_suffix(n,cnf,old,cut,guard=(q,q),**args)
    assert list(map(Q.polynomial,duplicated[info["root"]]["clause"])) == [q,q]
    tally["same_guard_occurrences_preserved"] = info["guard_size"]
    absent = dict(args["imports"])
    absent.pop(next(iter(absent)))
    tally["rejected_missing_boundary_derivation"] = reject(
        lambda: S.replay_suffix(n,cnf,old,cut,**{**args,"imports":absent}),"derived import")
    wrong = dict(args["imports"])
    first,second = tuple(wrong)[:2]
    wrong[first] = wrong[second]
    tally["rejected_wrong_boundary_derivation"] = reject(
        lambda: S.replay_suffix(n,cnf,old,cut,**{**args,"imports":wrong}),"mapped multiset")
    corrupt = deepcopy(args["output_prefix"])
    next(row for row in corrupt if row["rule"]=="axiom")["axiom"] = len(cnf)
    tally["rejected_forged_prefix_axiom"] = reject(
        lambda: S.replay_suffix(n,cnf,old,cut,**{**args,"output_prefix":corrupt}),"genuine input")
    for control in ("live_cubic","formal_square","hidden_multiplier","aggregate_product",
                    "retain_quadratic_factor","leaked_and_definition"):
        n,cnf,old,cut,args,meta = fixture(control=control)
        expected = {"retain_quadratic_factor":"must be affine","leaked_and_definition":"missing image"}.get(control,"degree above two")
        tally["rejected_"+control] = reject(lambda: S.replay_suffix(n,cnf,old,cut,**args),expected)
        if control=="live_cubic":
            live = set(A.ancestors(n,cnf,old,include_declarations=False))
            selected = var(meta["xor_name"])
            assert any(i in live and row["rule"]=="multiply" and Q.polynomial(row["chosen"])==selected
                       and Q.polynomial(row["multiplier"])==var(meta["pairs"][0][1])
                       for i,row in enumerate(old) if i>=cut)
        if control=="leaked_and_definition":
            for name,(x,y) in zip(meta["pair_names"],meta["pairs"]):
                args["images"][name] = mul(var(x),var(y))
            tally["rejected_exposed_quartic_AND_definition"] = reject(
                lambda: S.replay_suffix(n,cnf,old,cut,**args),"degree above two")
    n,cnf,old,pairs,names,u = alias_bridge(tally)
    tally["rejected_wrong_pair_binding"] = reject(
        lambda: S.carry_xor(n,cnf,old,pairs,names[::-1],u),"promised aggregate")
    tally["rejected_wrong_XOR_binding"] = reject(
        lambda: S.carry_xor(n,cnf,old,pairs,names,u+1),"promised aggregate")
    tally["rejected_reused_coordinate"] = reject(lambda: S.quadratic_xor(4,[(1,2),(2,3)]),"disjoint")
    tally["single_pair_degree_two_images_among_1024_formal_atoms"] = single_port_polynomials()
    assert tally["single_pair_degree_two_images_among_1024_formal_atoms"]==128
    generated = json.loads(json.dumps(rewrite_record()))
    saved = json.loads(Path(__file__).with_name("rewrite.json").read_text())
    assert saved == generated
    for key in ("before","after"):
        A.verify(saved["base_variables"],saved["cnf"],saved[key])
    tally["saved_replayed_refutations"] = 2
    assert tally["two_variable_formal_quadratic_defaults"]==64
    return {"status":"passed",**dict(sorted(tally.items()))}


if __name__ == "__main__":
    print(json.dumps(main(),indent=2,sort_keys=True))

