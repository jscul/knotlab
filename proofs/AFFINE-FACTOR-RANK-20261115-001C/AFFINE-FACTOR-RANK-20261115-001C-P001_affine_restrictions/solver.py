"""Eliminate reusable product names when every name is affine on each supplied case."""
from itertools import product
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[3]
EPIC="AFFINE-FACTOR-RANK-20261115-001"
OLD="PRODUCT-NAME-TRANSFER-20261115-001"


def component(ticket,slug):
    return runpy.run_path(str(ROOT/"proofs"/ticket/(ticket+"-P001_"+slug)/"solver.py"))


ranked=component(EPIC+"A","ranked_elimination")
named=component(OLD+"A","named_substitution")
bounded=component(OLD+"B","bounded_elimination")
q=bounded["BASE"]
ZERO,ONE,add,mul,var,polynomial=(bounded[s] for s in ("ZERO","ONE","add","mul","var","poly"))
opposite=bounded["opposite"]


def model(n,forms,values):
    """Use the same linear section for all right-hand sides; free coordinates are zero."""
    pivots={}
    for form,value in zip(forms,values):
        row=sum(1 << (term[0]-1) for term in form if term)
        rhs=value ^ (() in form)
        while row:
            p=row.bit_length()-1
            if p not in pivots:
                pivots[p]=(row,rhs)
                break
            earlier,bit=pivots[p]
            row ^= earlier
            rhs ^= bit
        if row==0 and rhs:
            raise ValueError("inconsistent test equations")
    result=0
    for pivot,(row,rhs) in sorted(pivots.items()):
        if ((row & result).bit_count() & 1) != rhs:
            result |= 1 << pivot
    return tuple((result >> i) & 1 for i in range(n))


class NonAffineProduct(ValueError):
    def __init__(self,variable,bits,corners,refinements):
        self.variable=variable
        self.case=tuple(bits)
        self.corners=tuple(corners)
        self.refinements=tuple(refinements)
        super().__init__(f"product name {variable} is nonaffine on basis case {self.case}")


def classify(basis,bits,variable,f,g,n):
    """Find a constant factor or sum on this case, or exhibit a nonlinear Boolean square."""
    for kind,control,other in (("left",f,g),("right",g,f),("sum",add(f,g),f)):
        coords=basis.coordinates(control)
        if coords is None:
            continue
        offset,mask=coords
        value=offset ^ (sum(bit for i,bit in enumerate(bits) if (mask>>i)&1) & 1)
        representative=(ZERO if value else f) if kind=="sum" else (other if value else ZERO)
        return kind,mask,opposite(control) if value else control,other,representative
    corners=[model(n,(*basis.forms,f,g),(*bits,i,j)) for i,j in product((0,1),repeat=2)]
    choices=[tuple(t for t in h if t) for h in (f,g,add(f,g))]
    raise NonAffineProduct(variable,bits,corners,choices)


def product_image(dag,basis,bits,derive,boolean,variable,f,g,source_n):
    """Derive the formal equation including the possible Boolean square repair."""
    kind,mask,expected,other,image=classify(basis,bits,variable,f,g,source_n)
    selected,equation=derive(mask)
    if selected != expected:
        raise ValueError("branch equation does not match the factor")
    node=dag.multiply(equation,selected,other)
    if kind=="sum":
        fp=opposite(f)
        square=mul(f,fp)
        first=dag.multiply(boolean(f),f,fp)
        both=dag.multiply(first,fp,f)
        identity=dag.contract(both,square)
        node=dag.combine(node,identity,mul(selected,f),square)
    return image,node,kind


def first_failure(n,definitions,basis):
    """Test all names on the full original cube, independent of the input CNF."""
    for bits in product((0,1),repeat=basis.rank):
        images={i:var(i) for i in range(1,n+1)}
        for variable,raw_f,raw_g in definitions:
            f=bounded["affine_image"](raw_f,images)
            g=bounded["affine_image"](raw_g,images)
            try:
                images[variable]=classify(basis,bits,variable,f,g,n)[-1]
            except NonAffineProduct as exc:
                return exc
    return None


def find_controls(n,cnf,proof,budget):
    """Return a minimum-rank valid observation within budget, or None."""
    if type(budget) is not int or budget<0:
        raise ValueError("rank budget must be a nonnegative integer")
    named["verify"](n,cnf,proof)
    definitions=bounded["declarations"](n,proof)
    for limit in range(min(n,budget)+1):
        stack=[()]
        while stack:
            generators=stack.pop()
            basis=ranked["AffineBasis"](n,generators)
            failure=first_failure(n,definitions,basis)
            if failure is None:
                return basis.forms
            if basis.rank<limit:
                stack.extend((*generators,h) for h in reversed(failure.refinements))
    return None


def eliminate(n,cnf,proof,generators):
    """All declared names are tested on the base cube, including declarations with no later use."""
    named["verify"](n,cnf,proof)
    basis=ranked["AffineBasis"](n,generators)
    out=q["Dag"](cnf)
    boolean=bounded["affine_boolean_builder"](out)
    leaves=[]
    kinds={"left":0,"right":0,"sum":0}
    gate_count=sum(node["rule"]=="define" for node in proof)
    for bits in product((0,1),repeat=basis.rank):
        failures,derive=ranked["guard_equation_builder"](out,basis.forms,bits,boolean)
        images={i:var(i) for i in range(1,n+1)}
        refs=[]
        def image(raw):
            return bounded["affine_image"](raw,images)
        for step in proof:
            rule=step["rule"]
            if rule=="define":
                v=step["variable"]
                f,g=map(image,step["factors"])
                images[v],node,kind=product_image(out,basis,bits,derive,boolean,v,f,g,n)
                kinds[kind]+=1
            elif rule=="boolean":
                node=boolean(images[step["variable"]])
            elif rule=="true":
                node=out.true()
            elif rule=="axiom":
                node=out.axiom(step["axiom"])
            else:
                target=[image(raw) for raw in step["clause"]]
                node=bounded["guarded_step"](out,step,refs,image,failures,target)
            required=tuple(sorted((*failures,*(image(raw) for raw in step["clause"]))))
            if out.clauses[node]!=required:
                if rule not in ("boolean","true","axiom"):
                    raise ValueError("translated inference has a different formal result")
                node=out.weaken(node,required)
            refs.append(node)
        leaves.append((refs[-1],tuple(failures)))
    while len(leaves)>1:
        merged=[]
        for (left,a),(right,b) in zip(leaves[::2],leaves[1::2]):
            if a[:-1]!=b[:-1] or a[-1]!=opposite(b[-1]):
                raise ValueError("case siblings have different parents")
            merged.append((bounded["cut"](out,left,right,a[-1],a[:-1]),a[:-1]))
        leaves=merged
    if leaves[0][0]!=len(out.proof)-1:
        out.weaken(leaves[0][0],())
    q["verify"](n,cnf,out.proof)
    return out.proof,{"rank":basis.rank,"cases":2**basis.rank,"declarations":gate_count,
                      "nodes":len(out.proof),"factor_cases":kinds}
