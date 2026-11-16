"""Independent learned-library extraction, physical, and paid-cost replay.

Default execution uses hand fixtures only. Sealed replay imports no producer
fitter or evaluator and consumes neither held data nor measured results until
the new library has been written and lead authorization has been given.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import gzip
import hashlib
import importlib.util
from itertools import permutations, product, combinations, accumulate
import json
from pathlib import Path
import random
import statistics
import struct
import sys
import time


TICKET="FOLD-DISCOVERY-20261115-001"
FAMILY=TICKET+"-E001_learned_library"
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_OUT=ROOT/"artifacts"/TICKET/FAMILY
OPS=("AND","OR","XOR")
ARMS=("primitive","learned","flat","given")
PRIOR_AUDIT_SHA="36c5480105869c3e77434b19adf25d09d293e0a9fa364052810df5f946837dcf"


class AuditError(ValueError):pass


def require(condition,message):
    if not condition:raise AuditError(message)


def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def normalized(value):return json.loads(json.dumps(value))
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def file_digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def get(path):return json.loads(Path(path).read_bytes())
def freeze(value):return tuple(map(freeze,value)) if isinstance(value,(list,tuple)) else value


def physical_dependencies(circuit):
    """Pin-preserving NAND expressions and multiplicities, independent of order."""
    n=circuit["inputs"]
    nodes=[digest(["input",j]) for j in range(n)]+[digest(["const",b]) for b in (0,1)]
    counts=Counter()
    for a,b in circuit["gates"]:
        node=digest(["NAND",*sorted((nodes[a],nodes[b]))]);counts[node]+=1;nodes.append(node)
    return nodes[circuit["output"]],counts


@lru_cache(maxsize=1)
def prior():
    path=ROOT/"research/FOLD-DEPTH-20261115-001/audit.py"
    require(file_digest(path)==PRIOR_AUDIT_SHA,"Immutable independent predecessor interpreter changed")
    spec=importlib.util.spec_from_file_location("independent_library_base",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def expression_bit(expr,raw,n,dag=None):
    if type(expr) is int:
        require(0<=expr<n,"Invalid raw source input")
        return raw>>expr&1
    op=expr[0]
    if op=="input":
        require(len(expr)==2 and type(expr[1]) is int and 0<=expr[1]<n,"Input outside raw domain")
        return raw>>expr[1]&1
    if op=="const":
        require(len(expr)==2 and type(expr[1]) is int and expr[1] in (0,1),"Bad constant")
        return expr[1]
    if op=="NOT":return 1-expression_bit(expr[1],raw,n,dag)
    if op=="FOLD":
        require(dag is not None and len(expr)==4,"Unbound or malformed learned call")
        return prior().nand(dag,[expression_bit(x,raw,n,dag) for x in expr[1:]])
    require(op in OPS and len(expr)==3,"Unknown Boolean instruction")
    a,b=(expression_bit(child,raw,n,dag) for child in expr[1:])
    return a&b if op=="AND" else a|b if op=="OR" else a^b


def truth(expr,n,dag=None):return sum(expression_bit(expr,x,n,dag)<<x for x in range(1<<n))


def rename(expr,order):
    if expr[0]=="input":return ("input",order[expr[1]])
    return (expr[0],*(rename(child,order) for child in expr[1:]))


def parse_primitive(expr,work):
    if isinstance(expr,str):
        try:expr=json.loads(expr)
        except json.JSONDecodeError:expr=ast.literal_eval(expr)
    require(isinstance(expr,(list,tuple)) and expr,"Malformed primitive AST")
    work["source_AST_nodes_parsed"]+=1
    op=expr[0]
    if op=="input":
        require(len(expr)==2 and type(expr[1]) is int and expr[1]>=0,"Bad primitive input")
        return (op,expr[1])
    if op=="const":
        require(len(expr)==2 and type(expr[1]) in (bool,int) and expr[1] in (0,1),"Bad primitive constant")
        return (op,int(expr[1]))
    require(op in OPS and len(expr)==3,"Discovery received a nonprimitive operation")
    return (op,parse_primitive(expr[1],work),parse_primitive(expr[2],work))


def fragment_truth(expr,work):
    work["semantic_truth_evaluations"]+=1
    work["semantic_binary_ops"]+=2
    return truth(expr,3)


def representative_catalogue(work):
    found={}
    for outer,inner,order,side in product(OPS,OPS,permutations(range(3)),(0,1)):
        x,y,z=(("input",i) for i in order)
        expr=(outer,(inner,x,y),z) if side==0 else (outer,x,(inner,y,z))
        value=fragment_truth(expr,work)
        if value not in found or canonical(expr)<canonical(found[value]):found[value]=expr
        work["generic_representative_programs"]+=1
    work["generic_raw_truth_values"]=len(found)
    return found


def anonymous_pairs(expr,work):
    if expr[0] not in OPS:return
    work["source_binary_gates"]+=1
    x,y,z=(("input",i) for i in range(3))
    for side in (1,2):
        if expr[side][0] in OPS:
            inner=expr[side][0]
            work["adjacent_gate_pairs"]+=1
            yield (expr[0],(inner,x,y),z) if side==1 else (expr[0],x,(inner,y,z))
    yield from anonymous_pairs(expr[1],work)
    yield from anonymous_pairs(expr[2],work)


def extract(programs):
    """Rebuild the complete blind ranking and every recorded acquisition unit."""
    work=Counter();representatives=representative_catalogue(work)
    accepted=[];seen=set();program_keys=set();task_ids={}
    for index,row in enumerate(programs):
        work["input_records"]+=1
        task_id=row.get("task_id",row.get("id",index)) if isinstance(row,dict) else index
        expr=row.get("expr") if isinstance(row,dict) else row
        status=row.get("status","exact") if isinstance(row,dict) else "exact"
        require(type(task_id) in (str,int),"Task support ID is not opaque scalar data")
        if status!="exact" or expr is None:
            work["rejected_input_records"]+=1;continue
        expr=parse_primitive(expr,work);tk=canonical(task_id).decode();pk=canonical(expr).decode()
        if (tk,pk) in seen:
            work["duplicate_task_program_records"]+=1;continue
        seen.add((tk,pk));accepted.append((tk,pk,task_id,expr));program_keys.add(pk);task_ids[tk]=task_id
    work.update(successful_program_records=len(accepted),distinct_successful_programs=len(program_keys),training_tasks=len(task_ids))
    classes={};trace=[]
    for tk,_,ident,expr in sorted(accepted):
        counts=Counter()
        for pair in anonymous_pairs(expr,work):
            orbit=[]
            for order in permutations(range(3)):
                orbit.append(fragment_truth(rename(pair,order),work));work["fragment_permutation_evaluations"]+=1
            key=min(orbit);counts[key]+=1
            entry=classes.setdefault(key,{"tasks":set(),"occurrences":0})
            work["task_support_membership_checks"]+=1
            if tk not in entry["tasks"]:entry["tasks"].add(tk);work["new_task_supports"]+=1
            entry["occurrences"]+=1;work["occurrence_updates"]+=1
        trace.append(dict(task_id=ident,pairs=sum(counts.values()),class_counts=[[k,counts[k]] for k in sorted(counts)]))
    proposals=[]
    for key in sorted(classes):
        record=classes[key];expr=representatives[key]
        compiled,calls,_=prior().expand(expr,3)
        require(calls==0,"Generic candidate unexpectedly contains a macro")
        dag={"gates":compiled["gates"],"output":compiled["output"]}
        require(truth(expr,3)==sum(prior().nand(dag,[x>>j&1 for j in range(3)])<<x for x in range(8))==key,
                "Candidate's literal NAND realization is wrong")
        work.update(physical_programs_compiled=1,physical_NANDs_compiled=len(dag["gates"]),physical_input_bits_read=24,
                    physical_scalar_NANDs_verified=8*len(dag["gates"]),essentiality_variable_checks=3)
        essential=all((key^(key>>(1<<j)))&(255^prior().columns(3)[j]) for j in range(3))
        support=sorted(record["tasks"])
        proposals.append(dict(truth=key,expr=normalized(expr),dag=dag,nand_gates=len(dag["gates"]),input_arity=3,
                              distinct_tasks=len(support),occurrences=record["occurrences"],supporting_task_ids=[task_ids[k] for k in support],
                              nontrivial=essential,eligible=essential and len(support)>=2))
    eligible=[p for p in proposals if p["eligible"]]
    selected=min(eligible,key=lambda p:(-p["distinct_tasks"],-p["occurrences"],p["truth"])) if eligible else None
    for p in proposals:
        p["selected"]=p is selected
        p["disposition"]="selected" if p is selected else "trivial" if not p["nontrivial"] else "one_off" if p["distinct_tasks"]<2 else "eligible_not_selected"
    work.update(proposal_classes=len(proposals),eligible_classes=len(eligible),rejected_classes=len(proposals)-len(eligible),
                one_off_classes=sum(p["disposition"]=="one_off" for p in proposals),unselected_eligible_classes=sum(p["disposition"]=="eligible_not_selected" for p in proposals),
                matched_occurrences=0 if selected is None else selected["occurrences"],
                matched_training_tasks=0 if selected is None else selected["distinct_tasks"],
                matched_program_records=0 if selected is None else sum(any(k==selected["truth"] for k,_ in row["class_counts"]) for row in trace))
    work["discarded_occurrences"]=work["adjacent_gate_pairs"]-work["matched_occurrences"]
    return normalized(dict(schema_version=1,selected=selected,proposals=proposals,accounting=dict(work),training_trace=trace))


def variable_support(expr):
    if expr[0]=="input":return Counter({expr[1]:1})
    if expr[0]=="const":return Counter()
    result=Counter()
    for child in expr[1:]:result.update(variable_support(child))
    return result


def validate_fragment_boundaries(expr):
    """Hole identity is justified by actual disjoint nonconstant operands."""
    if expr[0] not in OPS:return 0
    count=0
    for side in (1,2):
        child=expr[side]
        if child[0] in OPS:
            frontier=(child[1],child[2],expr[3-side])
            supports=[set(variable_support(node)) for node in frontier]
            require(all(supports) and all(supports[i].isdisjoint(supports[j]) for i in range(3) for j in range(i)),
                    "Anonymous fragment holes overlap or have empty support")
            count+=1
    return count+sum(validate_fragment_boundaries(child) for child in expr[1:])


def compile_roles(entry):
    if entry is None:return ()
    table=entry["truth"];roles={}
    for xpin,ypin,hpin in permutations(range(3)):
        signature=[]
        for a in range(4):
            low=((a&1)<<xpin)|((a>>1)<<ypin)
            signature.append((table>>low&1)|((table>>(low|(1<<hpin))&1)<<1))
        signature=tuple(signature)
        if signature in roles:continue
        pivot=signature.index(2) if 2 in signature else signature.index(1)
        witness=sum((signature[j]&1)<<(j-1) for j in (1,2,3))
        physical=(xpin,ypin,hpin)
        roles[signature]=dict(signature=signature,witness=witness,pivot=pivot,
                              argument_order=tuple(physical.index(i) for i in range(3)),
                              checks=tuple((i,code) for i,code in enumerate(signature) if i!=pivot))
    return tuple(roles[key] for key in sorted(roles,key=lambda s:(-sum(code in (1,2) for code in s),s)))


def inline(expr,args):
    if expr[0]=="input":return args[expr[1]]
    return (expr[0],inline(expr[1],args),inline(expr[2],args))


class ReplayLibrary(prior().ReplayPeel):
    def __init__(self,n,arm,entry=None,dag=None):
        super().__init__(n,arm);self.entry=entry;self.dag=dag if arm=="named" and entry is not None else None
        self.roles=compile_roles(entry);self.setup=Counter();self.calls=0
        if arm!="primitive" and entry is not None:
            compiled,uses,_=prior().expand(entry["expr"],3)
            gates=len(compiled["gates"])
            require(uses==0 and truth(entry["expr"],3)==entry["truth"],"Bad primitive library spelling")
            if arm=="named":
                if self.dag is None:self.dag={"gates":compiled["gates"],"output":compiled["output"]}
                else:self.setup["library_binding_validation_packed_NANDs"]+=len(self.dag["gates"])
                require(sum(prior().nand(self.dag,[x>>j&1 for j in range(3)])<<x for x in range(8))==entry["truth"],"Wrong supplied learned binding")
            self.setup.update(library_AST_NANDs_compiled=gates,library_AST_validation_packed_NANDs=gates,
                              library_permutations_compiled=6,library_entry_bits_read=48,library_distinct_roles=len(self.roles))

    def joint(self,n,table,singletons):
        if not self.roles:return None
        all_bits=prior().full(n-2)
        for x,y in combinations(range(n),2):
            self.paid["peel_pair_probes"]+=1
            at_both=table>>((1<<x)|(1<<y))&1
            self.paid["peel_witness_bit_reads"]+=1;self.paid["factor_truth_bit_reads"]+=1
            witness=singletons[x]|(singletons[y]<<1)|(at_both<<2);sections=None
            for index,role in enumerate(self.roles):
                self.paid["peel_role_probes"]+=1;self.paid["ternary_placement_tests"]+=1
                if witness!=role["witness"]:
                    self.paid["peel_role_witness_rejections"]+=1;self.paid["ternary_placement_failures"]+=1;continue
                self.paid["peel_role_column_checks"]+=1
                if sections is None:
                    x0,x1=self.pair_sections_at(n,table,x)
                    c00,c01=self.pair_sections_at(n-1,x0,y-1);c10,c11=self.pair_sections_at(n-1,x1,y-1)
                    sections=(c00,c10,c01,c11)
                residual=sections[role["pivot"]]
                if role["signature"][role["pivot"]]==1:residual^=all_bits
                unary=(0,all_bits^residual,residual,all_bits)
                ok=True
                for k,code in role["checks"]:
                    self.paid["library_column_comparisons"]+=1
                    if sections[k]!=unary[code]:ok=False;break
                if not ok:self.paid["ternary_placement_failures"]+=1;continue
                self.paid["ternary_placement_passes"]+=1;self.event("library_pair",inputs=n,x=x,y=y,role=index)
                child=self.search(n-2,residual)
                if child is None:self.paid["peel_child_failures"]+=1;continue
                positions=tuple(j for j in range(n) if j not in (x,y))
                operands=(("input",x),("input",y),self.remap(child[0],positions));args=tuple(operands[j] for j in role["argument_order"])
                expr=("FOLD",*args) if self.arm=="named" else inline(self.entry["expr"],args)
                self.paid["AST_nodes_built"]+=3 if self.arm=="named" else 4
                return freeze(expr),child[1]+1
        return None

    def run(self,table):
        # Reuse the independently checked public input/selection machinery,
        # but compile FOLD with this learned binding, never the old F constant.
        before=self.paid.copy();cache_before=self.cache_sizes();self.events=[];self.dropped=0;n=self.n
        self.paid["input_rows_received"]+=1<<n;positions=[]
        for j in range(n):
            self.layout(n,1<<j)
            if any((table>>x&1)!=(table>>(x^(1<<j))&1) for x in range(1<<n)):positions.append(j)
            self.paid["support_variable_probes"]+=1;self.paid["support_packed_bit_ops"]+=3
        positions=tuple(positions);mask=sum(1<<j for j in positions)
        _,assignments,_=self.layout(n,mask);compact=sum((table>>x&1)<<i for i,x in enumerate(assignments))
        self.paid["support_remap_calls"]+=1;self.paid["support_remap_truth_bit_reads"]+=len(assignments)
        result=self.search(len(positions),compact);expr=None if result is None else self.remap(result[0],positions)
        compiled=None;hit=False
        if expr is not None:
            self.paid["physical_compile_requests"]+=1;hit=expr in self.programs
            if hit:self.paid["physical_compile_cache_hits"]+=1;compiled=self.programs[expr]
            else:
                compiled,calls,ops=prior().expand(expr,n,self.dag)
                compiled.update(constants={"zero":n,"one":n+1},nand_gates=len(compiled["gates"]),macro_uses=calls,
                                underlying_ops={op:ops[op] for op in OPS})
                self.programs[expr]=compiled
                self.paid.update(physical_programs_compiled=1,physical_NANDs_compiled=len(compiled["gates"]),physical_macro_calls_compiled=calls)
            self.paid.update(verification_packed_NANDs=len(compiled["gates"]),verification_scalar_equivalent_NANDs=len(compiled["gates"])*(1<<n),
                             verification_rows=1<<n,verification_comparisons=1,verification_input_bit_reads=n*(1<<n))
        self.calls+=1
        return dict(expr=expr,circuit=compiled,work={key:self.paid[key]-before[key] for key in set(self.paid)|set(before)},
                    input_support=list(positions),template_uses=0 if result is None else result[1],cache_before=cache_before,cache_after=self.cache_sizes(),
                    physical_compile_cache_hit=hit,trace=list(self.events),trace_dropped=self.dropped)


def self_test():
    x=tuple(("input",i) for i in range(8))
    a=("OR",("OR",x[0],x[1]),x[2]);b=("OR",x[5],("OR",x[3],x[4]));c=("AND",("XOR",x[0],x[1]),x[2])
    rows=[dict(task_id="a",expr=a),dict(task_id="b",expr=b),dict(task_id="c",expr=c)]
    fit=extract(rows)
    require(fit["selected"]["distinct_tasks"]==2 and fit["selected"]["truth"]!=106,"Support fixture selected the old fold by default")
    require(extract(list(reversed(rows)))==fit,"Record order changed support ranking")
    duplicate=extract([rows[0],rows[0]])
    require(duplicate["selected"] is None and duplicate["accounting"]["duplicate_task_program_records"]==1,"Duplicate support manufactured recurrence")
    catalogue=representative_catalogue(Counter())
    require(len(catalogue)==21 and len({min(truth(rename(expr,p),3) for p in permutations(range(3))) for expr in catalogue.values()})==9,"Generic grammar enumeration failed")
    original=dict(truth=120,expr=["XOR",["AND",["input",0],["input",1]],["input",2]])
    signatures=lambda entry:[r["signature"] for r in compile_roles(entry)]
    for order in permutations(range(3)):
        expr=rename(freeze(original["expr"]),order);other=dict(truth=truth(expr,3),expr=expr)
        require(signatures(other)==signatures(original),"Entry input renaming changed public role order")
    shared=("XOR",("AND",x[0],x[1]),x[0])
    try:validate_fragment_boundaries(shared)
    except AuditError:pass
    else:raise AuditError("Overlapping frontier supports were accepted")
    return dict(status="pass",generic_programs=108,raw_truths=21,classes=9,distinct_support_order_duplicates=True,
                role_order_invariant_under_all_six_renamings=True,overlapping_anonymous_operands_rejected=True)


def shape(expr):
    if type(expr) is int or expr[0]=="input":return ("leaf",)
    op=expr[0];children=[]
    for child in expr[1:]:
        value=shape(child)
        children.extend(value[1:] if op in OPS and value[0]==op else (value,))
    return (op,*sorted(children)) if op in OPS else (op,*children)


def subshapes(node):
    out={node};children=node[1:]
    for child in children:out.update(subshapes(child))
    if node[0] in OPS:
        for size in range(2,len(children)):
            out.update((node[0],*selected) for selected in combinations(children,size))
    return out


def previous_targets():
    out=set();old="FOLD-REUSE-20261115-001"
    for row in get(ROOT/"artifacts"/old/(old+"-E001_second_learner")/"panel.json"):
        if row["n"]==4:out.add((4,row["truth"]))
    old="FOLD-GATE-20261115-001"
    folder=ROOT/"artifacts"/old/(old+"-E001_gated_stream")
    for split in ("train","held"):
        with (folder/(split+".bin")).open("rb") as source:
            header=json.loads(source.readline());payload=source.read()
        require(hashlib.sha256(payload).hexdigest()==header["ordered_truths_sha256"],"Archived target source changed")
        out.update((6,t) for t, in struct.iter_unpack("<Q",payload))
    return out


def rebuild_training():
    """Independent construction of the predeclared 24 training specifications."""
    A,B,C,D,E,F,G,H=range(8)
    binary=lambda op:lambda a,b:(op,a,b)
    both,either,xor=(binary(op) for op in OPS)
    f=lambda a,b,c:("F",a,b,c)
    r=lambda a,b,c:("R",a,b,c)
    q=lambda a,b,c:("Q",a,b,c)
    templates={
        4:(both(f(A,B,C),D),either(f(A,B,C),D),f(either(A,B),C,D),f(A,B,either(C,D)),
           xor(f(A,B,C),D),f(xor(A,B),C,D),both(q(A,B,C),D),either(r(A,B,C),D)),
        6:(either(f(f(A,B,C),D,E),F),f(A,both(f(B,C,D),E),F),either(f(A,B,C),f(D,E,F)),f(either(A,B),f(C,D,E),F),
           f(A,B,both(r(C,D,E),F)),f(q(A,B,C),D,either(E,F)),either(r(A,B,C),r(D,E,F)),both(q(A,B,C),q(D,E,F))),
        8:(f(either(f(f(A,B,C),D,E),F),G,H),f(f(A,B,C),f(D,E,F),either(G,H)),f(either(f(A,B,C),D),f(E,F,G),H),
           both(f(A,either(B,C),D),f(E,either(F,G),H)),f(r(A,B,C),either(D,E),f(F,G,H)),
           f(q(A,B,C),f(D,E,both(F,G)),H),either(r(A,B,C),both(r(D,E,F),either(G,H))),
           both(q(A,B,C),either(q(D,E,F),xor(G,H))))}
    def remap(tree,order):return order[tree] if type(tree) is int else (tree[0],*(remap(t,order) for t in tree[1:]))
    def primitive(tree):
        if type(tree) is int:return tree
        op=tree[0];args=[primitive(x) for x in tree[1:]]
        if op in OPS:return (op,*args)
        a,b,c=args
        return xor(both(a,b),c) if op=="F" else both(a,xor(b,c)) if op=="R" else xor(either(a,b),c)
    def count(tree,op):return 0 if type(tree) is int else int(tree[0]==op)+sum(count(c,op) for c in tree[1:])
    used=previous_targets();ids=random.Random(11390519);rows=[];metadata={}
    for n,local in templates.items():
        for index,template in enumerate(local):
            rng=random.Random(11390217+127*n+index)
            for attempt in range(1024):
                private=remap(template,rng.sample(range(n),n));source=primitive(private);value=truth(source,n)
                if (n,value) not in used:break
            else:raise AuditError("No fresh label assignment for frozen training mechanism")
            used.add((n,value));ident=f"{ids.getrandbits(96):024x}"
            rows.append(dict(id=ident,n=n,truth=value))
            metadata[ident]=dict(source=source,shape=shape(source),planted_calls=count(template,"F"),
                                 explicit_R=count(template,"R"),explicit_Q=count(template,"Q"),label_draws=attempt+1)
    random.Random(11390341).shuffle(rows)
    return rows,metadata


def check_result(actual,expected,target,n,role,dag):
    require(actual["arm"]==role and actual["n"]==n,"Method/domain mismatch")
    require(freeze(actual["expr"])==expected["expr"],"Visible-table schedule chose a different expression")
    for key in ("cache_before","cache_after","trace","trace_dropped","physical_compile_cache_hit","template_uses","input_support"):
        require(actual[key]==expected[key],f"Library search/cache replay differs: {key}")
    for key,value in actual["work"].items():
        require(type(value) is int and value>=0 and value==expected["work"].get(key,0),
                f"Executed work differs: {key}: {value} vs {expected['work'].get(key,0)}")
    require(all(value==actual["work"].get(key,0) for key,value in expected["work"].items()),"A paid operation category is missing")
    if expected["expr"] is None:
        require(actual["status"]=="unsupported" and actual["circuit"] is None and actual["truth"] is None,"Failed synthesis was silently repaired")
        return False
    require(actual["status"]=="exact" and actual["truth"]==target,"Wrong reported target truth")
    require(actual["circuit"]==expected["circuit"],"Physical NAND operands/metadata differ from independently compiled AST")
    require(prior().circuit_truth(actual["circuit"],n)==truth(actual["expr"],n,dag)==target,"Exhaustive scalar physical/AST replay fails")
    require(actual["fold_dag"]==dag and actual["macro_uses"]==expected["circuit"]["macro_uses"] and
            actual["expanded_NANDs"]==len(actual["circuit"]["gates"]),"Bound physical entry/gate count differs")
    return True


def metrics(row,target):
    r=row["result"];w=r["work"];t=r.get("timing",{})
    return dict(exact=int(r["status"]=="exact" and r["truth"]==target and r["circuit"] is not None),
                tests=w["binary_placement_trials"]+w["ternary_placement_tests"],
                failed_trials=w["binary_placement_failures"]+w["ternary_placement_failures"],cofactor_bit_reads=w["factor_truth_bit_reads"],
                template_uses=r.get("template_uses",0),physical_nands=r.get("expanded_NANDs") or 0,verified_rows=w["verification_rows"],
                search_cpu_ns=t.get("search_cpu_ns",0),search_wall_ns=round(t.get("search_seconds",0)*1e9),
                build_ns=round(t.get("build_seconds",0)*1e9),verify_ns=round(t.get("verification_seconds",0)*1e9),
                wall_ns=row.get("wall_ns",row.get("elapsed_ns",0)))


def total(rows):
    out=Counter()
    for row in rows:out.update(row)
    return dict(out)


def median_records(rows):return {key:statistics.median(r[key] for r in rows) for key in rows[0]}


def crossing(a,b):
    delta=[x-y for x,y in zip(a,b,strict=True)]
    first=next((k for k in range(1,len(delta)) if delta[k]<=0),None)
    best=min(range(1,len(delta)),key=delta.__getitem__)
    return dict(first_break_even=first,end_gap_ns=delta[-1],minimum_gap_ns=delta[best],closest_prefix=best,
                reversals=[k for k in range(2,len(delta)) if delta[k-1]<=0<delta[k]])


def records(path):
    with gzip.open(path,"rt") as source:return [json.loads(line) for line in source]


def aggregate(streams,startups,held,grade,acquisition,trainlog,train,entry,fit):
    curves={};values={};by_arm={};depths={};prefix_audit={}
    for key,rows in streams.items():
        cache,arm,repeat=key
        data=[metrics(row,target["truth"]) for row,target in zip(rows,held,strict=True)]
        upfront=acquisition["wall_ns"] if arm in ("learned","flat") else 0
        curves[key]=list(accumulate((v["wall_ns"] for v in data),initial=upfront+startups[key]));values[key]=data
    for cache in ("warm","cold"):
        by_arm[cache]={};depths[cache]={};prefix_audit[cache]={}
        base=[statistics.median(items) for items in zip(*(curves[cache,"primitive",r] for r in range(5)),strict=True)]
        for arm in ARMS:
            prefix=[statistics.median(items) for items in zip(*(curves[cache,arm,r] for r in range(5)),strict=True)]
            upfront=acquisition["wall_ns"] if arm in ("learned","flat") else 0
            result=median_records([total(values[cache,arm,r]) for r in range(5)])
            result.update(acquisition_ns=upfront,total_paid_ns=prefix[-1],downstream_ns=prefix[-1]-upfront,
                          run_paid_ns=[curves[cache,arm,r][-1] for r in range(5)],startup_ns=statistics.median(startups[cache,arm,r] for r in range(5)),
                          vs_primitive=crossing(prefix,base),paired_repeat_crossings=[crossing(curves[cache,arm,r],curves[cache,"primitive",r]) for r in range(5)])
            by_arm[cache][arm]=result
            prefix_audit[cache][arm]=dict(paid=crossing(prefix,base),marginal=crossing([x-upfront for x in prefix],base),
                                         initial_paid_gap_ns=prefix[0]-base[0],positive_prefixes_checked=len(held))
            for depth in (2,3,4):
                for kind in ("positive","negative"):
                    ids=[i for i,target in enumerate(held) if grade[target["id"]]["depth"]==depth and grade[target["id"]]["kind"]==kind]
                    cell=depths[cache].setdefault(f"{depth}-{kind}",dict(tasks=len(ids)))
                    cell[arm]=median_records([total(values[cache,arm,r][i] for i in ids) for r in range(5)])
    expected=dict(entry=entry,selected_proposal=fit["selected"],acquisition=acquisition,
                  training_counts=total(metrics(row,train[row["id"]]["truth"]) for row in trainlog),training_tasks=len(train),held_tasks=len(held),
                  failed_held_runs=sum(1-v["exact"] for rows in values.values() for v in rows),held_runs=len(streams)*len(held),
                  held_rule_input_pairs_per_run=sum(1<<r["n"] for r in held),totals=by_arm,depths=depths)
    return normalized(expected),prefix_audit


def audit(out):
    start=time.perf_counter();design=get(out/"design.json");acquisition=get(out/"gate-freeze.json")
    require(file_digest(out/"design.json")==acquisition["design_sha256"],"Acquisition is not bound to the design")
    require(datetime.fromisoformat(design["bound_utc"].replace("Z","+00:00"))<=datetime.fromisoformat(acquisition["frozen_utc"].replace("Z","+00:00")),"Training predates source/data binding")
    for category in ("training_sources","evaluation_sources"):
        for name,sha in design[category].items():require(file_digest(ROOT/name)==sha,f"Changed bound source: {name}")
    for name,sha in design["inputs"].items():require(file_digest(out/name)==sha,f"Changed frozen input: {name}")
    for name,key in (("entry.json","entry_sha256"),("candidates.json","candidates_sha256"),("training.jsonl.gz","training_log_sha256")):
        require(file_digest(out/name)==acquisition[key],"Frozen checkpoint/training receipt changed")
    require(acquisition["wall_ns"]==sum(acquisition[k] for k in ("training_solve_and_setup_ns","fit_ns","certificate_and_export_ns")),"Upfront acquisition phases do not sum")
    train_rows=get(out/"train.json");held=get(out/"held.json");grade=get(out/"grading.json");entry=get(out/"entry.json");fit=get(out/"candidates.json")
    rebuilt,source_meta=rebuild_training();require(rebuilt==train_rows,"Independent predeclared training construction differs")
    require(len(train_rows)==len(held)==24 and len({(r["n"],r["truth"]) for r in train_rows+held})==48,"Wrong training/held denominator or duplicate table")
    require({r["n"] for r in train_rows}=={4,6,8} and {r["n"] for r in held}=={5,7,9},"Train/test arity separation failed")
    require(all(set(row)=={"id","n","truth"} for row in train_rows+held),"Scientific inputs disclose labels beyond the public truth specification")
    train={r["id"]:r for r in train_rows};held_by_id={r["id"]:r for r in held}
    require(set(grade)==set(held_by_id),"Held metadata coverage differs")
    log=records(out/"training.jsonl.gz")
    require([r["id"] for r in log]==list(train),"Training execution order changed")
    engines={};programs=[];training_shapes=set();fragments=0;training_physical_rows=0
    for row in log:
        target=train[row["id"]];n=target["n"]
        if n not in engines:engines[n]=prior().ReplayPeel(n,"primitive")
        expected=engines[n].run(target["truth"])
        require(check_result(row["result"],expected,target["truth"],n,"primitive",None),"Training program failed")
        require(variable_support(row["result"]["expr"])==Counter({j:1 for j in range(n)}),"Training source is not read-once/full-support")
        fragments+=validate_fragment_boundaries(row["result"]["expr"])
        training_shapes.add(shape(row["result"]["expr"]))
        require(shape(row["result"]["expr"])==source_meta[row["id"]]["shape"],"Primitive synthesis changed the training mechanism")
        require(row["elapsed_ns"]>=row["result"]["timing"]["elapsed_seconds"]*1e9,"Acquisition time omits a training solve")
        programs.append(dict(task_id=row["id"],expr=row["result"]["expr"]));training_physical_rows+=1<<n
    require(sum(r["elapsed_ns"] for r in log)<=acquisition["training_solve_and_setup_ns"],"Acquisition omitted paid training work")
    require(acquisition["training_tasks"]==acquisition["accepted_training_programs"]==24 and acquisition["failed_training_tasks"]==0,"Training receipt success count differs")
    independent_fit=extract(programs)
    for key in ("selected","proposals","training_trace"):require(independent_fit[key]==fit[key],f"Blind training ranking differs: {key}")
    require(all(value==independent_fit["accounting"].get(key,0) for key,value in fit["accounting"].items()) and
            all(value==fit["accounting"].get(key,0) for key,value in independent_fit["accounting"].items()),"Full discarded-candidate acquisition accounting differs")
    require(fragments==fit["accounting"]["adjacent_gate_pairs"],"Recorded anonymous fragments lack disjoint support")
    require(entry==({k:fit["selected"][k] for k in ("expr","truth","dag")} if fit["selected"] else None),"Exported entry differs from the selected proposal")
    require(acquisition["export_validation_scalar_nands"]==(0 if entry is None else 8*len(entry["dag"]["gates"])),"Checkpoint certification omitted physical work")
    if entry is not None:
        require(sum(prior().nand(entry["dag"],[x>>j&1 for j in range(3)])<<x for x in range(8))==truth(entry["expr"],3)==entry["truth"],"Chosen physical entry fails an input row")
    closures=set().union(*(subshapes(s) for s in training_shapes));held_shapes=set();F_tree_exceptions=[]
    stage1=ROOT/"artifacts/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold"
    prior_grade=get(stage1/"grading.json");old_shapes={freeze(m["primitive_shape"]) for g in prior_grade.values() for m in g.values()}
    for target in held:
        meta=grade[target["id"]];n=target["n"];value=target["truth"]
        require(n==2*meta["depth"]+1 and meta["kind"] in ("positive","negative"),"Wrong held condition")
        require(all(truth(source,n)==value for source in meta["sources"]),"Held equivalent spellings disagree")
        local=shape(meta["sources"][0]);require(local==freeze(meta["primitive_shape"]),"Held source shape metadata differs")
        require(local not in old_shapes and local not in closures,"Reserved complete structure occurred in prior panel or training subtrees")
        held_shapes.add(local)
        require(value.bit_count()==1<<(n-1) and all((value^(value>>(1<<j)))&(prior().full(n)^prior().columns(n)[j]) for j in range(n)),"Held balance/full support differs")
        classes=prior().chain_classes(value,n)
        require(sorted(classes)==meta["full_gate_classes_with_or_leaves"] and bool(classes)==(meta["kind"]=="positive"),"Held arbitrary-chain certificate differs")
        if meta["kind"]=="negative" and prior().f_tree_cover(value,n):F_tree_exceptions.append(target["id"])
    print("Independent acquisition ranking, physical entry, and structural separation passed; replaying held programs.",flush=True)
    raw=[json.loads(line) for line in (out/"results.jsonl").read_text().splitlines()]
    cases=[]
    for rep in range(5):
        for cache in (("warm","cold") if rep%2==0 else ("cold","warm")):
            offset=(rep+int(cache=="cold"))%4
            cases.extend(f"{cache}-{rep}-{arm}" for arm in ARMS[offset:]+ARMS[:offset])
    require(len(raw)==40 and [row["case"] for row in raw]==cases,"Missing, duplicate, or reordered held streams")
    require(all(row["status"]=="ok" and row["attempt"]==1 for row in raw) and len({row["worker"] for row in raw})==40,"Paid held runs failed/retried or reused worker processes")
    supplied=dict(truth=120,expr=["XOR",["AND",["input",0],["input",1]],["input",2]])
    streams={};startups={};cached_expected={};stream_hashes={};physical_rows=0;scalar_nands=0
    for runner in raw:
        data=runner["result"];cache,arm,rep=(data[k] for k in ("cache","arm","repeat"));key=(cache,arm,rep)
        require(data["tasks"]==24 and data["file"]==runner["case"]+".jsonl.gz","Held stream identity differs")
        require(runner["job_sha"]==design["evaluation_sources"][str((ROOT/"experiments"/TICKET/FAMILY/"job.py").relative_to(ROOT))],"Unbound evaluation job executed")
        require(datetime.fromisoformat(runner["finished_at"])>=datetime.fromisoformat(acquisition["frozen_utc"].replace("Z","+00:00")),"Held execution predates learned checkpoint")
        path=out/data["file"];require(file_digest(path)==data["sha256"],"Held stream bytes changed")
        rows=records(path);require([r["id"] for r in rows]==list(held_by_id),"Held row order/coverage differs")
        engines={};stream_hashes[data["file"]]=data["sha256"]
        for row,target in zip(rows,held,strict=True):
            n=target["n"];require(row["n"]==n,"Held raw input width changed")
            fresh=cache=="cold" or n not in engines
            if fresh:
                if arm=="primitive":engines[n]=prior().ReplayPeel(n,"primitive")
                else:
                    e=supplied if arm=="given" else entry;role="flat" if arm=="flat" else "named"
                    dag=prior().SAVED_FOLD if arm=="given" else entry["dag"] if arm=="learned" and entry is not None else None
                    engines[n]=ReplayLibrary(n,role,e,dag)
            model=engines[n]
            if rep==0:
                expected=model.run(target["truth"]);cached_expected[cache,arm,target["id"]]=expected
            else:expected=cached_expected[cache,arm,target["id"]]
            role="primitive" if arm=="primitive" else "flat" if arm=="flat" else "named"
            dag=None if arm in ("primitive","flat") or entry is None and arm=="learned" else prior().SAVED_FOLD if arm=="given" else entry["dag"]
            actual=row["result"]
            require(actual["status"]!="error","A runtime failure remains paid but exact independent replay is inconclusive")
            check_result(actual,expected,target["truth"],n,role,dag)
            if fresh:
                setup=getattr(model,"setup",Counter())
                require(all(value==setup.get(name,0) for name,value in row["setup_work"].items()),"Entry installation/setup logical work differs")
            else:require(row["setup_work"]=={},"A retained backend is charged as a fresh installation")
            if arm!="primitive":
                install=actual["library_setup"]
                require((install is not None)==fresh,"Library installation receipt is missing or repeated")
                if install is not None:
                    require(install["truth"]==(supplied if arm=="given" else entry)["truth"] and install["expr"]==(supplied if arm=="given" else entry)["expr"],"Installed entry identity differs")
                    require(all(value==model.setup.get(name,0) for name,value in install["work"].items()),"Compiled public role/entry setup work differs")
                    require(install["seconds"]*1e9<=row["init_ns"],"Constructor cost omitted from outer held time")
            require(row["return_bytes"]==len(canonical(actual["circuit"])),"Output emission bytes differ")
            t=actual["timing"]
            require(sum(t[k] for k in ("input_seconds","search_seconds","build_seconds","verification_seconds"))<=t["elapsed_seconds"]+1e-8 and
                    t["elapsed_seconds"]*1e9<=row["wall_ns"] and t["search_cpu_ns"]<=row["cpu_ns"],"Paid time omits a synthesis/verification phase")
            physical_rows+=1<<n;scalar_nands+=(1<<n)*actual["expanded_NANDs"]
        require(data["startup_ns"]+sum(row["wall_ns"] for row in rows)<=runner["seconds"]*1e9,"Held startup/task bill exceeds entire worker time")
        streams[key]=rows;startups[key]=data["startup_ns"]
    semantic=("binary_placement_trials","ternary_placement_tests","factor_truth_bit_reads","peel_pair_probes","peel_role_probes",
              "library_column_comparisons","subproblem_requests","successful_subproblem_cache_hits","failed_subproblem_cache_hits")
    matched=0;different_emission_orders=0
    for cache in ("warm","cold"):
        for rep in range(5):
            for named,flat in zip(streams[cache,"learned",rep],streams[cache,"flat",rep],strict=True):
                a,b=named["result"],flat["result"]
                require(all(a["work"].get(k,0)==b["work"].get(k,0) for k in semantic) and a["trace"]==b["trace"],"Inlined entry changes semantic search")
                require(a["template_uses"]==a["macro_uses"]==b["template_uses"] and b["macro_uses"]==0,"Printed length replaced physically executed repeated calls")
                require(len(a["circuit"]["gates"])==len(b["circuit"]["gates"]),"Inlined library changes physical gate count")
                require(physical_dependencies(a["circuit"])==physical_dependencies(b["circuit"]),"Inlined library changes NAND dependencies or gate multiplicities")
                different_emission_orders+=a["circuit"]["gates"]!=b["circuit"]["gates"]
                matched+=1
    expected,prefixes=aggregate(streams,startups,held,grade,acquisition,log,train,entry,fit)
    require(expected==get(out/"result.json"),"Independent paid prefix/group aggregation differs from final assessor")
    ranking=sorted(fit["proposals"],key=lambda p:(-p["distinct_tasks"],-p["occurrences"],p["truth"]))
    summary=[{k:p[k] for k in ("truth","distinct_tasks","occurrences","nand_gates","selected")} for p in ranking]
    acquired=acquisition["wall_ns"];warm=expected["totals"]["warm"]
    return dict(study=TICKET,verdict="PASS",independence="Training ranking, scalar AST/NAND programs, generic role schedule, all work counters and paid costs replayed independently; no producer fitter or evaluator called.",
        input_hashes={name:file_digest(out/name) for name in ("design.json","gate-freeze.json","entry.json","candidates.json","training.jsonl.gz","results.jsonl","result.json")},
        audit_source_sha256=file_digest(Path(__file__)),stream_hashes=stream_hashes,ranking=summary,
        extraction=dict(anonymous_pairs=fragments,all_frontiers_disjoint_and_nonempty=True,all_candidate_circuits_and_accounting_match=True,
                        explicit_source_F_tasks=sum(m["planted_calls"]>0 for m in source_meta.values()),explicit_source_R_tasks=sum(m["explicit_R"]>0 for m in source_meta.values()),
                        simplest_equivalent_description="Count each ordered adjacent primitive-operator pair across distinct programs; the nine pairs have nine different three-hole semantic classes."),
        separation=dict(training_arity=[4,6,8],held_arity=[5,7,9],distinct_training_structures=len(training_shapes),distinct_held_structures=len(held_shapes),
                        complete_reserved_subtrees_in_training=0,complete_reserved_shapes_in_prior_panel=0,negative_given_F_tree_exceptions=F_tree_exceptions),
        physical=dict(training_programs=24,held_programs=960,training_scalar_input_rows=training_physical_rows,held_scalar_input_rows=physical_rows,
                      held_scalar_NAND_evaluations=scalar_nands,chosen_entry_rows=8,learned_inline_equal_NAND_dependency_pairs=matched,
                      learned_inline_different_emission_orders=different_emission_orders),
        acquisition=acquisition,totals=expected["totals"],depth_groups=expected["depths"],all_prefix_comparisons=prefixes,
        even_free_learned_deployment_shortfall_ns=acquired-warm["primitive"]["total_paid_ns"],fixture_tests=self_test(),
        interpretation=["The winning acquired class is AND of XOR (truth40), not supplied XOR of AND (class106). Distinct-task support outranks occurrence count.",
            "Abstract boundary roles were selected from actual primitive solutions, without old fold state, task locations, held outcomes or private syntax entering the fitter.",
            "This is frequency-based two-operator library induction under a designed training distribution; semantic canonicalization is equivalent here to counting adjacent operator pairs.",
            "Held positive/negative labels refer to preservation/breaking of supplied F; they do not define whether the different acquired operator is usable locally.",
            "Learned and flat share semantic search, NAND dependency expressions and gate counts. Independent argument programs can be emitted in different topological orders; naming adds no gate-count efficiency.",
            "Full new acquisition, discarded candidates, entry validation/export, each deployment load, failed trials, build, all-row verification and return emission are charged.",
            "Original ancestral fold acquisition is not operational input to this fresh primitive-to-library acquisition; the free-given arm is a separately labeled reference.",
            "Paid and marginal timing, all depths/groups and both cache regimes are distinct. The finite workload gives no general learning or complexity result."],
        audit_elapsed_s=time.perf_counter()-start,completed_utc=datetime.now(timezone.utc).isoformat())


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--self-test",action="store_true");p.add_argument("--audit",action="store_true")
    p.add_argument("--artifacts",type=Path,default=DEFAULT_OUT);args=p.parse_args()
    if args.audit:
        result=audit(args.artifacts)
        (args.artifacts/"audit.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps({"verdict":result["verdict"],"winner":result["ranking"][0],"physical":result["physical"],
                          "warm_paid":result["totals"]["warm"]["learned"]["vs_primitive"],"audit":str(args.artifacts/"audit.json")},indent=2))
    else:print(json.dumps(self_test(),sort_keys=True))
