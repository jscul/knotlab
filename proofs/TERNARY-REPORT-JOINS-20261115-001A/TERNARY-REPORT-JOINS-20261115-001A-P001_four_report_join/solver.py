"""Derive and join selector cases for strict three-report checks with no proof names."""

from functools import cache
from collections import Counter
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
scope = "QUADRATIC-ROUTE-TRANSFER-20261115-001A"
kernel_path = ROOT/"proofs"/scope/(scope+"-P001_quadratic_substitution")/"solver.py"
spec = spec_from_file_location("ternary_report_kernel",kernel_path)
Q = module_from_spec(spec)
spec.loader.exec_module(Q)
ZERO,ONE,add,mul,var = Q.ZERO,Q.ONE,Q.add,Q.mul,Q.var
SUPPORTS = ((0,1,2),(0,3,4),(1,3,5),(2,4,5))


def shifted(f, bit):
    return add(f,ONE) if bit else f


def chain(lits, aux):
    if len(lits)!=11 or len(aux)!=8:
        raise ValueError("expected eleven original literals and eight private variables")
    return [[lits[0],lits[1],aux[0]],
            *[[-aux[j-1],lits[j+1],aux[j]] for j in range(1,8)],
            [-aux[-1],lits[-2],lits[-1]]]


def encode_checks(h, checks):
    if type(h) is not int or h<3:
        raise ValueError("at least three distinct report positions are needed")
    triples=[tuple(range(3+3*i,6+3*i)) for i in range(h)]
    public_n=2+3*h
    n=public_n
    cnf,blocks=[],[]
    for i,j,k,c in checks:
        ids=(i,j,k)
        if (len(set(ids))!=3 or any(type(v) is not int or not 0<=v<h for v in ids)
                or type(c) not in (bool,int) or c not in (0,1)):
            raise ValueError("expected three distinct report indices and a Boolean charge")
        variables=(1,2,*(v for pos in ids for v in triples[pos]))
        rows=[]
        for bits in product((0,1),repeat=11):
            key=bits[0]&bits[1]
            value=0
            for p in (2,5,8):
                value ^= bits[p+2] & ((bits[p]&bits[p+1]) ^ key)
            if value==c:
                continue
            lits=tuple(-v if bit else v for v,bit in zip(variables,bits))
            aux=tuple(range(n+1,n+9))
            rows.append({"bits":bits,"clause":lits,"start":len(cnf),"aux":aux})
            cnf.extend(chain(lits,aux))
            n+=8
        blocks.append({"indices":ids,"charge":int(c),"variables":variables,"rows":rows})
    return {"n":n,"public_n":public_n,"a":1,"b":2,"triples":triples,"cnf":cnf,"blocks":blocks}


def four_check_source(charges=(0,0,0,1)):
    if len(charges)!=4:
        raise ValueError("expected one charge for each of the four specified checks")
    return encode_checks(6,[(*triple,c) for triple,c in zip(SUPPORTS,charges)])


class CompactDag(Q.Dag):
    """Intern polynomials and store primitive instructions without a second full wire copy."""
    def __init__(self, source):
        super().__init__(source["cnf"])
        self.n=source["n"]
        self._polys={}
        self.records=[]
        self.source_use=[]
        self._owner=[1<<i for i,b in enumerate(source["blocks"]) for _ in range(9*len(b["rows"]))]

    def intern(self,f):
        return self._polys.setdefault(f,f)

    def emit(self, rule, atoms, **fields):
        row=tuple(sorted(self.intern(f) for f in atoms))
        if rule=="axiom":
            record=(rule,fields["axiom"])
            used=self._owner[fields["axiom"]]
        elif rule=="boolean":
            record=(rule,fields["variable"])
            used=0
        elif rule=="true":
            record=(rule,)
            used=0
        else:
            parents=fields["parents"]
            used=self.source_use[parents[0]]
            if rule=="combine":
                used |= self.source_use[parents[1]]
                f,g=(self.intern(Q.polynomial(raw)) for raw in fields["chosen"])
                record=(rule,*parents,f,g,*fields["coefficients"])
            elif rule=="multiply":
                record=(rule,*parents,self.intern(Q.polynomial(fields["chosen"])),
                        self.intern(Q.polynomial(fields["multiplier"])))
            elif rule=="contract":
                record=(rule,*parents,self.intern(Q.polynomial(fields["chosen"])))
            elif rule in ("weaken","delete_false"):
                record=(rule,*parents)
            else:
                raise ValueError("unknown unnamed rule")
        ref=len(self.clauses)
        self.clauses.append(row)
        self.records.append(record)
        self.source_use.append(used)
        return ref

    def wire_row(self, i):
        record=self.records[i]
        rule=record[0]
        row={"rule":rule,"clause":[Q.encode(f) for f in self.clauses[i]]}
        if rule=="axiom":
            row["axiom"]=record[1]
        elif rule=="boolean":
            row["variable"]=record[1]
        elif rule=="combine":
            row.update(parents=list(record[1:3]),chosen=[Q.encode(f) for f in record[3:5]],coefficients=list(record[5:7]))
        elif rule in ("multiply","contract","weaken","delete_false"):
            row["parents"]=[record[1]]
            if rule in ("multiply","contract"):
                row["chosen"]=Q.encode(record[2])
            if rule=="multiply":
                row["multiplier"]=Q.encode(record[3])
        return row

    def wire(self):
        return (self.wire_row(i) for i in range(len(self.records)))


def _cut(dag,left,right,pivot,context):
    node=dag.combine(left,right,pivot,add(pivot,ONE))
    node=dag.delete_false(node)
    for f in context:
        node=dag.contract(node,f)
    if dag.clauses[node]!=tuple(sorted(context)):
        raise ValueError("case cut changed the common multiset")
    return node


def _discharge(dag, leaves, variables, common):
    for level in reversed(range(len(variables))):
        out=[]
        for i,bits in enumerate(product((0,1),repeat=level)):
            ctx=(*common,*(shifted(var(v),bit^1) for v,bit in zip(variables,bits)))
            out.append(_cut(dag,leaves[2*i],leaves[2*i+1],shifted(var(variables[level]),1),ctx))
        leaves=out
    if len(leaves)!=1:
        raise ValueError("incomplete binary case tree")
    return leaves[0]


def lift_row(dag,row):
    start,aux,lits=row["start"],row["aux"],row["clause"]
    if type(start) is not int or start<0 or dag.cnf[start:start+9]!=chain(lits,aux):
        raise ValueError("forbidden row does not cite its actual strict clauses")
    ref=dag.axiom(start)
    for j,pivot in enumerate(aux,1):
        ref=dag.resolve(ref,dag.axiom(start+j),pivot)
    if dag.clauses[ref]!=Q.signed_clause(lits):
        raise ValueError("incorrect length-eleven resolvent")
    return ref


def quadratic(source, indices, bits, charge):
    pairs=[tuple(source["triples"][p][:2]) for p,bit in zip(indices,bits) if bit]
    if sum(bits)%2:
        pairs.append((source["a"],source["b"]))
    return Q.polynomial([*pairs,*([()] if charge else [])])


def guards(source, indices, bits):
    return tuple(shifted(var(source["triples"][p][2]),bit^1) for p,bit in zip(indices,bits))


def _check_family(dag,source,block):
    ids,charge=block["indices"],block["charge"]
    all_vars=block["variables"]
    rows={row["bits"]:row for row in block["rows"]}
    selectors=[source["triples"][i][2] for i in ids]
    data=[v for v in all_vars if v not in selectors]
    @cache
    def product_value(x,y,xb,yb):
        f,g=var(x),var(y)
        leaf=dag.multiply(dag.boolean(x),shifted(f,xb),g)
        ref=dag.combine(leaf,dag.boolean(y),mul(shifted(f,xb),g),shifted(g,yb),1,xb)
        return mul(f,g),xb*yb,ref
    outputs={}
    for sigma in product((0,1),repeat=3):
        eq=quadratic(source,ids,sigma,charge)
        zg=guards(source,ids,sigma)
        terms=[t for t in eq if t]
        active=[v for v in data if any(v in t for t in terms)]
        unused=[v for v in data if v not in active]
        leaves=[]
        for alpha in product((0,1),repeat=len(active)):
            values=dict(zip(selectors,sigma))
            values.update(zip(active,alpha))
            ag=tuple(shifted(var(v),b^1) for v,b in zip(active,alpha))
            if sum(values[x]*values[y] for x,y in terms)%2==charge:
                if terms:
                    values_proved=[product_value(x,y,values[x],values[y]) for x,y in terms]
                    val,bit,ref=values_proved[0]
                    for g,j,other in values_proved[1:]:
                        ref=dag.combine(ref,other,shifted(val,bit),shifted(g,j))
                        val,bit=add(val,g),bit^j
                else:
                    ref=dag.true()
            else:
                exclusions=[]
                for beta in product((0,1),repeat=len(unused)):
                    values.update(zip(unused,beta))
                    exclusions.append(lift_row(dag,rows[tuple(values[v] for v in all_vars)]))
                ref=_discharge(dag,exclusions,unused,(*zg,*ag))
            leaves.append(dag.weaken(ref,(*zg,*ag,eq)))
        outputs[sigma]=_discharge(dag,leaves,active,(*zg,eq))
    return outputs


def join(dag,source,left,right,left_roots,right_roots):
    l,r=source["blocks"][left],source["blocks"][right]
    middle=set(l["indices"]) & set(r["indices"])
    if len(middle)!=1:
        raise ValueError("the joined checks must have exactly one common report")
    m=middle.pop()
    ids=tuple(sorted(set(l["indices"]) ^ set(r["indices"])))
    charge=l["charge"] ^ r["charge"]
    outputs,events={},{}
    for sigma in product((0,1),repeat=4):
        values=dict(zip(ids,sigma))
        terms=quadratic(source,ids,sigma,charge)
        ctx=(*guards(source,ids,sigma),terms)
        two=[]
        steps=[]
        for b in (0,1):
            values[m]=b
            ls=tuple(values[i] for i in l["indices"])
            rs=tuple(values[i] for i in r["indices"])
            lf=quadratic(source,l["indices"],ls,l["charge"])
            rf=quadratic(source,r["indices"],rs,r["charge"])
            if add(lf,rf)!=terms:
                raise ValueError("the shared report contribution did not cancel")
            used=dag.combine(left_roots[ls],right_roots[rs],lf,rf)
            shared_guard=guards(source,(m,),(b,))[0]
            merged=dag.contract(used,shared_guard)
            if dag.clauses[merged]!=tuple(sorted((*ctx,shared_guard))):
                raise ValueError("a joined conditional lost the selector or retained hidden data")
            two.append(merged)
            steps.append((used,merged))
        root=_cut(dag,*two,guards(source,(m,),(0,))[0],ctx)
        if dag.source_use[root] & ~((1<<left)|(1<<right)):
            raise ValueError("the joined check used a source outside its two blocks")
        outputs[sigma],events[sigma]=root,(*steps,root)
    return ids,charge,outputs,events


def refute(source):
    if tuple(b["indices"] for b in source["blocks"])!=SUPPORTS:
        raise ValueError("expected the four specified ternary check supports")
    if not sum(b["charge"] for b in source["blocks"])%2:
        raise ValueError("closing the two summaries requires opposite total charges")
    dag=CompactDag(source)
    families=[_check_family(dag,source,b) for b in source["blocks"]]
    left=join(dag,source,0,1,families[0],families[1])
    right=join(dag,source,2,3,families[2],families[3])
    ids,c,lr,_=left
    if left[0]!=right[0] or c==right[1]:
        raise ValueError("intermediate summaries do not oppose at the same four positions")
    final=[]
    for sigma in product((0,1),repeat=4):
        f=quadratic(source,ids,sigma,c)
        final.append(_cut(dag,lr[sigma],right[2][sigma],f,guards(source,ids,sigma)))
    end=_discharge(dag,final,[source["triples"][i][2] for i in ids],())
    if dag.clauses[end] or end!=len(dag.records)-1:
        raise ValueError("missing final empty clause")
    return dag,{"families":families,"left":left,"right":right,"selector_exclusions":final,"empty":end}


def save_certificate(path, source, dag):
    with open(path,"wb") as stream, gzip.GzipFile(fileobj=stream,mode="wb",compresslevel=5,mtime=0,filename="") as out:
        def line(obj):
            out.write((json.dumps(obj,separators=(",",":"))+"\n").encode())
        line({"n":source["n"],"cnf":source["cnf"]})
        for row in dag.wire():
            line(row)


def verify_certificate(path,source):
    with gzip.open(path,"rt",encoding="utf-8") as body:
        header=json.loads(next(body))
        if header!={"n":source["n"],"cnf":source["cnf"]}:
            raise ValueError("the saved refutation uses a different strict input")
        return Q.verify(header["n"],header["cnf"],(json.loads(line) for line in body))


def trace_record(source,dag,audit):
    def mask(bits):
        return "".join(map(str,bits))
    def parents(record):
        if record[0] in ("axiom","true","boolean"):
            return ()
        return record[1:3] if record[0]=="combine" else record[1:2]
    def ancestry(root):
        seen,axioms=set(),set()
        stack=[root]
        while stack:
            i=stack.pop()
            if i in seen:
                continue
            seen.add(i)
            r=dag.records[i]
            if r[0]=="axiom":
                axioms.add(r[1])
            stack.extend(parents(r))
        return seen,axioms
    def root_map(roots):
        return {mask(bits):r for bits,r in roots.items()}
    examples=[]
    for which in ("left","right"):
        ids,charge,outputs,events=audit[which]
        for sigma in ((1,0,1,0),(1,0,0,0)):
            root=outputs[sigma]
            _,axioms=ancestry(root)
            ids_by_block=[[j for j in block["rows"] if j["start"] in axioms] for block in source["blocks"]]
            sample=next(rs[0] for rs in ids_by_block if rs)
            traced=[]
            for beta,(used,contracted) in enumerate(events[sigma][:2]):
                p,q=dag.records[used][1:3]
                traced.append({"shared_selector":beta,"children":[[p,dag.wire_row(p)],[q,dag.wire_row(q)]],
                                "sum":[used,dag.wire_row(used)],"contract":[contracted,dag.wire_row(contracted)]})
            examples.append({"side":which,"mask":mask(sigma),"charge":charge,
                             "equation":Q.encode(quadratic(source,ids,sigma,charge)),
                             "branches":traced,"summary":[root,dag.wire_row(root)],
                             "ancestral_strict_clauses":len(axioms),
                             "ancestral_forbidden_rows_by_block":[len(rs) for rs in ids_by_block],
                             "sample_ancestral_input":{"row":sample,"strict_clauses":source["cnf"][sample["start"]:sample["start"]+9]}})
    live,axioms=ancestry(audit["empty"])
    return {"strict_input_variables":source["n"],"public_variables":source["public_n"],
            "strict_clauses":len(source["cnf"]),"supports":SUPPORTS,
            "charges":[b["charge"] for b in source["blocks"]],
            "source_sha256":sha256(json.dumps(source["cnf"],separators=(",",":")).encode()).hexdigest(),
            "proof_nodes":len(dag.records),"rule_counts":dict(sorted(Counter(r[0] for r in dag.records).items())),
            "max_width":max(map(len,dag.clauses)),"live_nodes":len(live),"live_source_axioms":len(axioms),
            "child_roots":[root_map(rs) for rs in audit["families"]],
            "summary_roots":{which:root_map(audit[which][2]) for which in ("left","right")},
            "examples":examples,"selector_exclusions":audit["selector_exclusions"],
            "empty":[audit["empty"],dag.wire_row(audit["empty"])]}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path, help="destination for the primitive proof and trace")
    destination = parser.parse_args().output_directory
    destination.mkdir(parents=True, exist_ok=True)
    raw = four_check_source()
    derivation, indices = refute(raw)
    save_certificate(destination / "four-check-proof.jsonl.gz", raw, derivation)
    (destination / "trace.json").write_text(json.dumps(trace_record(raw, derivation, indices), indent=2) + "\n")
