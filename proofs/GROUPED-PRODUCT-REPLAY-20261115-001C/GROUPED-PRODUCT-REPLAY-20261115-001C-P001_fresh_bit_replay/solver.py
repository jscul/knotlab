"""Replay a proof on a common AND chain after splitting on a fresh bit or its quadratic report."""
from collections import Counter
from functools import cache
from itertools import chain
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[3]
EPIC = "GROUPED-PRODUCT-REPLAY-20261115-001"
OLD = "PRODUCT-NAME-TRANSFER-20261115-001"


def component(ticket, slug):
    return runpy.run_path(str(ROOT/"proofs"/ticket/(ticket+"-P001_"+slug)/"solver.py"))


named = component(OLD+"A", "named_substitution")
bounded = component(OLD+"B", "bounded_elimination")
group = component(EPIC+"A", "regroup_final")
parity = component(EPIC+"B", "carry_quadratic_xor")
q = named["q"]
ZERO, ONE, var, add, mul = q.ZERO, q.ONE, q.var, q.add, q.mul


def bit(value):
    return ONE if value else ZERO


def complement(f):
    return add(f, ONE)


def xor(forms):
    return q.polynomial(chain.from_iterable(forms))


def degree(f):
    return max(map(len, f), default=0)


def fail_atoms(inputs, values):
    return tuple(complement(add(var(v), bit(b))) for v,b in zip(inputs,values))


def assignment_report(dag, pairs, values, *, pair_defs=(), alias=None):
    """Derive the value of the whole pair XOR from one input assignment, as an implication."""
    inputs = tuple(chain.from_iterable(pairs))
    if len(values)!=len(inputs) or any(type(b) is not int or b not in (0,1) for b in values):
        raise ValueError("pair assignment must supply one bit per input")
    accumulated, total = None, ZERO
    for k,(i,j) in enumerate(pairs):
        a,b = values[2*k:2*k+2]
        x,y = var(i),var(j)
        xeq,yeq = add(x,bit(a)),add(y,bit(b))
        xy = mul(x,y)
        product = dag.multiply(dag.boolean(i),xeq,y)
        term = add(xy,bit(a*b))
        node = dag.combine(product,dag.boolean(j),mul(xeq,y),yeq,1,a)
        if pair_defs:
            p,definition = pair_defs[k]
            node = dag.combine(node,definition,term,add(var(p),xy))
            term = add(var(p),bit(a*b))
        if accumulated is None:
            accumulated=node
        else:
            accumulated=dag.combine(accumulated,node,total,term)
        total=add(total,term)
    if alias is not None:
        u,definition=alias
        selected=add(var(u),xor(var(p) for p,_ in pair_defs))
        accumulated=dag.combine(accumulated,definition,total,selected)
        total=add(total,selected)
    expected=tuple(sorted((*fail_atoms(inputs,values),total)))
    if dag.clauses[accumulated]!=expected:
        raise ValueError("wrong assignment report")
    return accumulated


class ReplayError(ValueError):
    def __init__(self, line, rule, field, case, detail, monomial=None):
        super().__init__(f"source line {line} ({rule}), {field}, case {case}: {detail}")
        self.line,self.rule,self.field,self.case=line,rule,field,case
        self.monomial=monomial


class Images(dict):
    """Unmentioned original variables map to themselves without allocating the declared roster."""
    def __init__(self,n):
        super().__init__()
        self.originals=n

    def __missing__(self,v):
        if 1<=v<=self.originals:
            return var(v)
        raise KeyError(v)


def parse_prefix(n, proof, cut, pairs, z):
    """Identify the read-once tree and s=z*(sum of pairs), with an optional explicit XOR alias."""
    leaves=tuple(chain.from_iterable(pairs))
    if (len(pairs)<2 or any(len(p)!=2 for p in pairs) or len(set(leaves))!=len(leaves)
        or any(type(v) is not int or not 1<=v<=n for v in (*leaves,z)) or z in leaves):
        raise ValueError("need disjoint positive input pairs and a distinct original bit")
    if type(cut) is not int or not 0<cut<len(proof):
        raise ValueError("invalid source cut")
    defs=[step for step in proof[:cut] if step["rule"]=="define"]
    count=len(leaves)-1
    if len(defs) not in (count+1,count+2):
        raise ValueError("prefix must declare the tree, optional XOR alias and gated XOR")
    supports={v:frozenset([v]) for v in leaves}
    form_names={var(v):v for v in leaves}
    pair_names={}
    for step in defs[:count]:
        factors=[q.polynomial(g) for g in step["factors"]]
        if any(f not in form_names for f in factors):
            raise ValueError("AND operands must be leaves or earlier tree names")
        a,b=(form_names[f] for f in factors)
        if supports[a]&supports[b]:
            raise ValueError("an AND subtree reuses a leaf")
        v=step["variable"]
        supports[v]=supports[a]|supports[b]
        form_names[var(v)]=v
        if len(supports[v])==2:
            pair_names[supports[v]]=v
    root=defs[count-1]["variable"]
    if supports[root]!=set(leaves) or any(frozenset(pair) not in pair_names for pair in pairs):
        raise ValueError("old AND does not cover the requested disjoint pairs")
    names=tuple(pair_names[frozenset(pair)] for pair in pairs)
    sum_names=xor(var(i) for i in names)
    u=None
    choices=[sum_names]
    if len(defs)==count+2:
        alias=defs[count]
        if Counter(map(q.polynomial,alias["factors"]))!=Counter((ONE,sum_names)):
            raise ValueError("aggregate alias has a different meaning")
        u=alias["variable"]
        choices.append(var(u))
    s=defs[-1]["variable"]
    gated=Counter(map(q.polynomial,defs[-1]["factors"]))
    if not any(gated==Counter((var(z),choice)) for choice in choices):
        raise ValueError("gated aggregate has a different meaning")
    return leaves,names,root,u,s


def guarded(dag,node,guard):
    if not guard:
        return node
    return dag.weaken(node,(*dag.clauses[node],*guard))


def restrict_known(dag, node, z, b):
    """Obtain H or L[z:=b] from the already derived L, preserving repeated disjuncts."""
    old=dag.clauses[node]
    selected=add(var(z),bit(b))
    guard=complement(selected)
    first=True
    for f in old:
        quot=[]
        for term in f:
            power=term.count(z)
            if power:
                tail=tuple(v for v in term if v!=z)
                for j in range(power):
                    if b or j==0:
                        quot.append(tuple(sorted(tail+(z,)*(power-1-j))))
        derivative=q.polynomial(quot)
        if derivative:
            diff=mul(selected,derivative)
            delta=dag.multiply(dag.boolean(z),selected,derivative)
            node=dag.combine(node,delta,f,diff)
            if not first:
                node=dag.contract(node,guard)
            first=False
    return guarded(dag,node,(guard,)) if first else node


def replay(n,cnf,proof,cut,pairs,z,*,reports=(),mode="fresh"):
    """Return a checked proof, a trace and cost data; the original certificate is always verified.

    reports is a sequence of (old prefix line, pair assignment) for old conditional
    U-reports used by the suffix. Ordinary input and standard AND ports are recognized.
    Report values and the target derivations are calculated here; no new premises enter.
    """
    named["verify"](n,cnf,proof)
    pairs=tuple(tuple(p) for p in pairs)
    inputs,names,root,u,s=parse_prefix(n,proof,cut,pairs,z)
    if mode not in ("fresh","parity","direct"):
        raise ValueError("unknown replay mode")
    Q=parity["quadratic_xor"](n,pairs)
    target=named["Dag"](n,cnf)
    order=tuple(i for i,j in pairs)+tuple(j for i,j in pairs)
    new_root,implies,all_imply=group["chain_portals"](target,order)
    old_ports={q.signed_clause([-root,i]):j for i,j in implies.items()}
    old_ports[q.signed_clause([root,*(-i for i in inputs)])]=all_imply
    reports=tuple((idx,tuple(vals)) for idx,vals in reports)
    exported={}
    for idx,vals in reports:
        if type(idx) is not int or not 0<=idx<cut or idx in exported:
            raise ValueError("invalid assignment report index")
        node=assignment_report(target,pairs,vals)
        value=sum(a*b for a,b in zip(vals[::2],vals[1::2]))%2
        forms=[xor(var(p) for p in names)]
        if u is not None:
            forms.append(var(u))
        wanted=[tuple(sorted((*fail_atoms(inputs,vals),add(f,bit(value))))) for f in forms]
        if tuple(sorted(map(q.polynomial,proof[idx]["clause"]))) not in wanted:
            raise ValueError("old assignment report has a different clause")
        exported[idx]=(node,value)

    @cache
    def boolean(f):
        return parity["boolean_quadratic"](target,f)

    all_bits=(None,) if mode=="direct" else (0,1)
    conclusions=[]
    traces=[]
    for b in all_bits:
        guard=() if b is None else (complement(add(var(z) if mode=="fresh" else Q,bit(b))),)
        images=Images(n)
        images.update({p:mul(var(x),var(y)) for p,(x,y) in zip(names,pairs)})
        images[root]=var(new_root)
        if mode=="parity":
            # One pair absorbs the branch equation. The written sum of pair names now equals b formally.
            images[names[-1]]=add(bit(b),xor(images[p] for p in names[:-1]))
            if u is not None:
                images[u]=bit(b)
            images[s]=mul(bit(b),var(z))
        else:
            if u is not None:
                images[u]=Q
            if mode=="fresh":
                images[z]=bit(b)
            images[s]=mul(images[z],Q)
        refs={}
        activity=[]
        def image(raw):
            return bounded["affine_image"](raw,images)

        def limited(f,line,field):
            if degree(f)>2:
                offender=next(t for t in f if len(t)>2)
                raise ReplayError(line,proof[line]["rule"],field,b,"degree exceeds two",offender)
            return f

        def premise(idx):
            if idx in refs:
                return refs[idx]
            step=proof[idx]
            rule=step["rule"]
            old=tuple(sorted(map(q.polynomial,step["clause"])))
            if idx in exported:
                node,value=exported[idx]
                if mode=="parity":
                    node=target.combine(node,boolean(Q),add(Q,bit(value)),add(Q,bit(b)))
                else:
                    node=guarded(target,node,guard)
            elif rule=="axiom":
                node=target.axiom(step["axiom"])
                node=(restrict_known(target,node,z,b) if mode=="fresh"
                      else guarded(target,node,guard))
            elif rule=="boolean" and (step["variable"]<=n or step["variable"] in images):
                node=guarded(target,boolean(limited(images[step["variable"]],idx,"Boolean default")),guard)
            elif rule=="true" or old==(ZERO,):
                node=guarded(target,target.true(),guard)
            elif old in old_ports:
                node=guarded(target,old_ports[old],guard)
            elif rule=="define" and step["variable"] in (*names,u,s):
                val=limited(image(old[0]),idx,"defining equation")
                if not val:
                    node=guarded(target,target.true(),guard)
                elif mode=="parity" and val==add(Q,bit(b)):
                    node=boolean(Q)
                else:
                    raise ReplayError(idx,rule,"crossing equation",b,"missing derivation")
            else:
                raise ReplayError(idx,rule,"crossing parent",b,"no derived replacement for this old premise")
            expected=tuple(sorted((*guard,*(image(f) for f in old))))
            if target.clauses[node]!=expected:
                raise ReplayError(idx,rule,"crossing parent",b,"replacement has a different multiset")
            refs[idx]=node
            return node

        for i in range(cut,len(proof)):
            step=proof[i]
            rule=step["rule"]
            for j in step.get("parents",()):
                try:
                    premise(j)
                except KeyError as exc:
                    raise ReplayError(j,proof[j]["rule"],"crossing parent",b,
                                      f"old interior variable {exc.args[0]} is missing") from exc
            try:
                if rule in ("boolean","axiom","true"):
                    node=premise(i)
                elif rule=="define":
                    f,g=(image(raw) for raw in step["factors"])
                    if f in (ZERO,ONE) or g in (ZERO,ONE):
                        images[step["variable"]]=limited(mul(f,g),i,"product value")
                        node=guarded(target,target.true(),guard)
                    elif max(degree(f),degree(g))<=1:
                        v,node=target.define(f,g)
                        images[step["variable"]]=var(v)
                        node=guarded(target,node,guard)
                    else:
                        raise ReplayError(i,rule,"defining factor",b,"new names require affine factors")
                else:
                    if rule=="multiply":
                        f,g=(limited(image(step[key]),i,key) for key in ("chosen","multiplier"))
                        limited(mul(f,g),i,"product")
                    elif rule=="combine":
                        for raw in step["chosen"]:
                            limited(image(raw),i,"chosen")
                    elif rule=="contract":
                        limited(image(step["chosen"]),i,"chosen")
                    values=[limited(image(raw),i,"clause") for raw in step["clause"]]
                    node=bounded["guarded_step"](target,step,refs,image,guard,values)
                expected=tuple(sorted((*guard,*(image(f) for f in step["clause"]))))
            except KeyError as exc:
                raise ReplayError(i,rule,"private name",b,f"old interior variable {exc.args[0]} is missing") from exc
            if target.clauses[node]!=expected:
                raise ReplayError(i,rule,"conclusion",b,"different formal multiset")
            refs[i]=node
            activity.append(node)
        conclusions.append(refs[len(proof)-1])
        traces.append(activity)
    if len(conclusions)==2:
        pivot=var(z) if mode=="fresh" else Q
        end=bounded["cut"](target,*conclusions,complement(pivot),())
    else:
        end=conclusions[0]
    if end!=len(target.proof)-1:
        target.weaken(end,())
    checked=named["verify"](n,cnf,target.proof)
    return target.proof,{"mode":mode,"cases":len(all_bits),"source_nodes":len(proof),
                         "output_nodes":len(target.proof),"output_names":checked["declarations"],
                         "root":new_root,"cut":cut,"source_to_target":traces}
