"""Expand shallow extensions into a verified larger-degree unnamed polynomial proof."""
from collections import Counter
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[3]
P = "PRODUCT-NAME-TRANSFER-20261115-001"
def module(scope, slug):
    return runpy.run_path(str(ROOT/"proofs"/scope/(scope+"-P001_"+slug)/"solver.py"))

B = module(P+"B","bounded_elimination")
A = module(P+"A","named_substitution")
Q = B["BASE"]
ZERO,ONE,add,mul,var,poly = (B[k] for k in ("ZERO","ONE","add","mul","var","poly"))
opposite = B["opposite"]


def degree(f):
    return max((len(t) for t in f), default=0)


class DegreeDag(Q["Dag"]):
    def __init__(self, cnf, cap):
        super().__init__(cnf)
        self.cap = cap

    def emit(self, rule, atoms, **fields):
        row = tuple(sorted(poly(f) for f in atoms))
        if any(degree(f) > self.cap for f in row):
            raise ValueError("expanded equation exceeds degree cap")
        self.clauses.append(row)
        self.proof.append({"rule":rule, "clause":[Q["encode"](f) for f in row], **fields})
        return len(self.proof)-1

    def multiply(self, node, distinguished, multiplier):
        f,g = poly(distinguished),poly(multiplier)
        if degree(g) > self.cap:
            raise ValueError("expanded multiplier exceeds degree cap")
        return self.emit("multiply", (*Q["removes"](self.clauses[node],f),mul(f,g)),
                         parents=[node], chosen=Q["encode"](f), multiplier=Q["encode"](g))


def verify_unnamed(n, cnf, proof, cap):
    """Check exact occurrences and formal coefficients separately from the emitting builder."""
    Q["validate_cnf"](n,cnf)
    def checked(raw):
        result = poly(raw,n)
        if degree(result)>cap:
            raise ValueError("formal degree exceeds the proposed bound")
        return result
    arities = {"axiom":0,"true":0,"boolean":0,"weaken":1,"contract":1,"delete_false":1,"multiply":1,"combine":2}
    rows = []
    max_degree = 0
    for index, line in enumerate(proof):
        kind = line["rule"]
        parents = line.get("parents",[])
        if len(parents)!=arities.get(kind) or any(type(j) is not int or not 0<=j<index for j in parents):
            raise ValueError("invalid deduction reference")
        row = Counter(checked(f) for f in line["clause"])
        max_degree = max(max_degree,max((degree(f) for f in row),default=0))
        if kind == "axiom":
            j = line["axiom"]
            if type(j) is not int or not 0<=j<len(cnf):
                raise ValueError("invalid CNF axiom")
            expected = Counter(Q["signed_clause"](cnf[j]))
        elif kind == "true":
            expected = Counter([ZERO])
        elif kind == "boolean":
            v = line["variable"]
            if type(v) is not int or not 1<=v<=n:
                raise ValueError("Boolean default outside the source")
            expected = Counter([var(v),opposite(var(v))])
        elif kind == "weaken":
            if not rows[parents[0]]<=row:
                raise ValueError("an old occurrence was discarded")
            expected = row
        else:
            selected = ([ONE] if kind=="delete_false" else [checked(x) for x in line["chosen"]]
                        if kind=="combine" else [checked(line["chosen"])])
            if len(selected)!=len(parents):
                raise ValueError("invalid number of selected atoms")
            expected = Counter()
            for j,f in zip(parents,selected):
                old = rows[j].copy()
                if old[f] < (2 if kind=="contract" else 1):
                    raise ValueError("missing selected occurrence")
                old[f] -= 1
                expected.update(old)
            if kind=="multiply":
                g = checked(line["multiplier"])
                max_degree = max(max_degree, degree(g))
                # Collect formal monomials modulo two without Boolean reductions.
                coeff = Counter(tuple(sorted(u+v)) for u in selected[0] for v in g)
                expected[tuple(sorted(t for t,a in coeff.items() if a%2))] += 1
            if kind=="combine":
                c = line["coefficients"]
                if len(c)!=2 or any(type(a) is not int or a not in (0,1) for a in c):
                    raise ValueError("invalid field coefficients")
                coeff = Counter(t for f,a in zip(selected,c) if a for t in f)
                expected[tuple(sorted(t for t,a in coeff.items() if a%2))] += 1
        if row != +expected:
            raise ValueError("formal rule result does not match the displayed disjunction")
        rows.append(row)
    if not rows or rows[-1]:
        raise ValueError("missing empty conclusion")
    return max_degree


def expand(n,cnf,proof):
    """Inline the sequential product definitions. The output has only the original n names."""
    A["verify"](n,cnf,proof)
    definitions = B["declarations"](n,proof)
    depth = {v:0 for v in range(1,n+1)}
    for name,f,g in definitions:
        depth[name] = 1+max((depth[t[0]] for t in (*f,*g) if t),default=0)
    h = max(depth.values(),default=0)
    cap = 2**(h+1)
    dag = DegreeDag(cnf,cap)
    images = {v:var(v) for v in range(1,n+1)}
    witnesses = {}
    def boolean_for_name(v):
        if v not in witnesses:
            witnesses[v] = dag.boolean(v)
        return witnesses[v]
    def sum_with_boolean(raw):
        names=[t[0] for t in raw if t]
        if not names:
            return raw, dag.weaken(dag.true(),(ZERO,ONE))
        value=images[names[0]]
        ef=boolean_for_name(names[0])
        for v in names[1:]:
            g=images[v]
            ef=B["boolean_gate"](dag,value,ef,g,boolean_for_name(v),product_gate=False)
            value=add(value,g)
        return (opposite(value) if () in raw else value), ef
    refs=[]
    def image(raw):
        return B["affine_image"](raw,images)
    for step in proof:
        kind=step["rule"]
        if kind=="define":
            name=step["variable"]
            (f,ef),(g,eg)=[sum_with_boolean(poly(raw)) for raw in step["factors"]]
            images[name]=mul(f,g)
            witnesses[name]=B["boolean_gate"](dag,f,ef,g,eg,product_gate=True)
            node=dag.true()
        elif kind=="axiom":
            node=dag.axiom(step["axiom"])
        elif kind=="true":
            node=dag.true()
        elif kind=="boolean":
            node=boolean_for_name(step["variable"])
        else:
            target=[image(raw) for raw in step["clause"]]
            node=B["guarded_step"](dag,step,refs,image,(),target)
        if dag.clauses[node] != tuple(sorted(image(raw) for raw in step["clause"])):
            raise ValueError("incorrect expanded line")
        refs.append(node)
    # A proof might end by citing a cached, already empty CNF axiom.
    if not dag.proof or refs[-1]!=len(dag.proof)-1:
        dag.weaken(refs[-1],())
    actual=verify_unnamed(n,cnf,dag.proof,cap)
    return dag.proof,{"declarations":len(definitions),"depth":h,"permitted_degree":cap,
                      "max_displayed_degree":actual,"nodes":len(dag.proof)}


def extension_clauses(dag, t, definition, left, right):
    """Derive the three ordinary ER clauses for t = truth(left) AND truth(right)."""
    def truth(literal):
        return var(literal) if literal>0 else opposite(var(-literal))
    u,v=truth(left),truth(right)
    eu,ev=dag.boolean(abs(left)),dag.boolean(abs(right))
    uv=mul(u,v)
    d=add(var(t),uv)
    first=dag.combine(dag.multiply(eu,u,v),definition,uv,d)
    second=dag.combine(dag.multiply(ev,v,u),definition,uv,d)
    base=dag.multiply(eu,opposite(u),v)
    joined=dag.combine(base,ev,mul(opposite(u),v),opposite(v))
    third=dag.combine(joined,definition,opposite(uv),d)
    return first,second,third


def eliminate(n, cnf, proof, *, method="count"):
    """Verify the named certificate and choose a degree-two or a shallow-depth simulation."""
    A["verify"](n,cnf,proof)
    if method not in ("count", "depth"):
        raise ValueError("unknown elimination method")
    empty = next((i for i, row in enumerate(cnf) if not row), None)
    if empty is not None:
        dag = Q["Dag"](cnf)
        dag.axiom(empty)
        verify_unnamed(n,cnf,dag.proof,2)
        return dag.proof, {"nodes":1,"empty_input_axiom":empty}
    return B["eliminate"](n,cnf,proof) if method == "count" else expand(n,cnf,proof)


def eliminate_shared_factor(n, cnf, proof, factor):
    """One common original affine factor or its complement in every declaration."""
    A["verify"](n,cnf,proof)
    f=poly(factor,n)
    if degree(f)>1:
        raise ValueError("the common factor must be affine in the original variables")
    definitions=B["declarations"](n,proof)
    gates={}
    for v,g,h in definitions:
        if g in (f,opposite(f)):
            gates[v]=(g==opposite(f),h)
        elif h in (f,opposite(f)):
            gates[v]=(h==opposite(f),g)
        else:
            raise ValueError("a declaration lacks the proposed factor and its complement")
    out=Q["Dag"](cnf)
    boolean=B["affine_boolean_builder"](out)
    cases=[]
    for value in (0,1):
        images={i:var(i) for i in range(1,n+1)}
        selected=opposite(f) if value else f
        failure=opposite(selected)
        refs=[]
        def image(raw):
            return B["affine_image"](raw,images)
        for step in proof:
            kind=step["rule"]
            if kind=="define":
                v=step["variable"]
                invert,raw=gates[v]
                other=image(raw)
                images[v]=other if value^invert else ZERO
                node=out.multiply(boolean(f),selected,other)
            elif kind=="boolean":
                node=boolean(images[step["variable"]])
            elif kind=="true":
                node=out.true()
            elif kind=="axiom":
                node=out.axiom(step["axiom"])
            else:
                target=[image(a) for a in step["clause"]]
                node=B["guarded_step"](out,step,refs,image,(failure,),target)
            wanted=tuple(sorted((failure,*(image(a) for a in step["clause"]))))
            if out.clauses[node]!=wanted:
                node=out.weaken(node,wanted)
            refs.append(node)
        cases.append(refs[-1])
    B["cut"](out,*cases,opposite(f),())
    Q["verify"](n,cnf,out.proof)
    return out.proof,{"branches":2,"nodes":len(out.proof),"declarations":len(definitions)}


def prune(n,cnf,proof):
    """Serialize the retained named ancestry, normalizing before consecutive renumbering."""
    A["verify"](n,cnf,proof)
    retained=A["ancestors"](n,cnf,proof)
    variables={v:v for v in range(1,n+1)}
    refs={}
    out=[]
    def rename(raw):
        return Q["encode"](poly(tuple(variables[v] for v in m) for m in poly(raw)))
    for j in retained:
        step=proof[j].copy()
        kind=step["rule"]
        if kind=="define":
            step["factors"]=[rename(g) for g in step["factors"]]
            v=step["variable"]
            variables[v]=len(variables)+1
            step["variable"]=variables[v]
        if kind=="boolean":
            step["variable"]=variables[step["variable"]]
        if "parents" in step:
            step["parents"]=[refs[t] for t in step["parents"]]
        step["clause"]=[rename(g) for g in step["clause"]]
        if kind in ("contract","multiply"):
            step["chosen"]=rename(step["chosen"])
        if kind=="combine":
            step["chosen"]=[rename(g) for g in step["chosen"]]
        if kind=="multiply":
            step["multiplier"]=rename(step["multiplier"])
        refs[j]=len(out)
        out.append(step)
    A["verify"](n,cnf,out)
    return out
