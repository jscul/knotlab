"""Independent fixed-input fold-placement audit.

Source F-tree height, minimum complete-F-cover height and primitive circuit
depth are distinct quantities.  The finite census uses only read-once F
trees on positive raw leaves.  All physical returns must still execute on
nine original input bits, including computation of any hinted operand.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from itertools import combinations
from pathlib import Path
import statistics
import time


TICKET="FOLD-PLACEMENT-20261115-001"
FAMILY=TICKET+"-E001_fixed_inputs"
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_OUT=ROOT/"artifacts"/TICKET/FAMILY
PRIOR_SHA="36c5480105869c3e77434b19adf25d09d293e0a9fa364052810df5f946837dcf"
LIBRARY_AUDIT_SHA="6d1cc9d1bea5b89321cf3ff90348350caf251c7461d086617cdc476026dfffe8"


class AuditError(ValueError):pass


def require(condition,message):
    if not condition:raise AuditError(message)


def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def file_digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def get(path):return json.loads(Path(path).read_bytes())
def frozen(value):return tuple(map(frozen,value)) if isinstance(value,(list,tuple)) else value
def normalized(value):return json.loads(json.dumps(value))


@lru_cache(maxsize=1)
def prior():
    path=ROOT/"research/FOLD-DEPTH-20261115-001/audit.py"
    require(file_digest(path)==PRIOR_SHA,"Immutable independent scalar/cofactor interpreter changed")
    spec=importlib.util.spec_from_file_location("independent_placement_base",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.factor_witness=lru_cache(maxsize=None)(module.factor_witness)
    return module


@lru_cache(maxsize=1)
def library_base():
    path=ROOT/"research/FOLD-DISCOVERY-20261115-001/audit.py"
    require(file_digest(path)==LIBRARY_AUDIT_SHA,"Immutable independent generic-library interpreter changed")
    spec=importlib.util.spec_from_file_location("independent_placement_library",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    base=module.prior()
    base.factor_witness=lru_cache(maxsize=None)(base.factor_witness)
    return module


def program_truth(expr,n,dag=None):
    """Exact bit-parallel AST check; physical circuits still run scalar below."""
    binding=None if dag is None else (tuple(tuple(g) for g in dag["gates"]),dag["output"])
    return _program_truth(frozen(expr),n,binding)


@lru_cache(maxsize=None)
def _program_truth(expr,n,binding):
    mask=prior().full(n)
    def visit(node):
        op=node[0]
        if op=="input":
            require(len(node)==2 and type(node[1]) is int and 0<=node[1]<n,"Bad submitted AST leaf")
            return prior().columns(n)[node[1]]
        if op=="const":return mask if node[1] else 0
        values=[visit(child) for child in node[1:]]
        if op=="FOLD":
            require(binding is not None and len(values)==3,"Unbound submitted call")
            values += [0,mask]
            for a,b in binding[0]:
                require(0<=a<len(values) and 0<=b<len(values),"Bad local physical address")
                values.append(mask^(values[a]&values[b]))
            return values[binding[1]]
        require(op in ("AND","OR","XOR") and len(values)==2,"Unknown submitted AST operation")
        return values[0]&values[1] if op=="AND" else values[0]|values[1] if op=="OR" else values[0]^values[1]
    return visit(expr)


def f(a,b,c):return (a&b)^c


@lru_cache(maxsize=None)
def ordered_trees(nodes):
    if nodes==0:return (("leaf",),)
    result=[]
    for a in range(nodes):
        for b in range(nodes-a):
            c=nodes-1-a-b
            for left in ordered_trees(a):
                for right in ordered_trees(b):
                    for last in ordered_trees(c):result.append(("F",left,right,last))
    return tuple(result)


def source_height(tree):
    return 0 if tree[0]=="leaf" else 1+max(source_height(child) for child in tree[1:])


def tree_truth(tree,n=9):
    variables=iter(prior().columns(n))
    def visit(node):
        if node[0]=="leaf":return next(variables)
        return f(*(visit(child) for child in node[1:]))
    result=visit(tree)
    try:next(variables)
    except StopIteration:pass
    else:raise AuditError("Source did not use all raw inputs")
    return result


def join_shape(op,a,b):
    children=[]
    for child in (a,b):children.extend(child[1:] if child[0]==op else (child,))
    return (op,*sorted(children))


def primitive_shape(tree):
    if tree[0]=="leaf":return tree
    a,b,c=(primitive_shape(child) for child in tree[1:])
    return join_shape("XOR",join_shape("AND",a,b),c)


@lru_cache(maxsize=None)
def minimum_F_height(table,n):
    """Minimum over complete read-once F-only covers, not mixed programs."""
    if n==1:return 0 if table==2 else None
    if n<3 or not n%2 or table&1:return None
    if n==3:return 1 if prior().gate_class(table)==prior().F_CLASS else None
    best=None
    for groups in prior().ternary_partitions(n):
        sections=[prior().one_bit_section(table,n,group) for group in groups]
        if any(section is None for section in sections):continue
        outer=sum((table>>sum(sections[j][1][raw>>j&1] for j in range(3))&1)<<raw for raw in range(8))
        if prior().gate_class(outer)!=prior().F_CLASS:continue
        heights=[minimum_F_height(section[0],len(group)) for section,group in zip(sections,groups)]
        if any(height is None for height in heights):continue
        height=1+max(heights)
        if best is None or height<best:best=height
    return best


@lru_cache(maxsize=None)
def minimum_mixed_height(table,n,rotations=1):
    """Minimum full-cover height with exactly one rotated AND-of-XOR site."""
    if rotations==0:return minimum_F_height(table,n)
    if n<3 or not n%2 or table&1:return None
    rotated=prior().gate_class(40)
    if n==3:return 1 if prior().gate_class(table)==rotated else None
    best=None
    for groups in prior().ternary_partitions(n):
        sections=[prior().one_bit_section(table,n,group) for group in groups]
        if any(section is None for section in sections):continue
        outer=sum((table>>sum(sections[j][1][raw>>j&1] for j in range(3))&1)<<raw for raw in range(8))
        operation=prior().gate_class(outer)
        if operation==rotated:budgets=((0,0,0),)
        elif operation==prior().F_CLASS:budgets=((1,0,0),(0,1,0),(0,0,1))
        else:continue
        for budget in budgets:
            heights=[minimum_mixed_height(section[0],len(group),count) for section,group,count in zip(sections,groups,budget)]
            if any(height is None for height in heights):continue
            height=1+max(heights)
            if best is None or height<best:best=height
    return best


class QuietPeel(prior().ReplayPeel):
    def event(self,kind,**data):self.dropped+=1


class ReplayPlacement(library_base().ReplayLibrary):
    """Independent exact cofactor grouping, contraction and substitution replay."""
    def __init__(self,n,arm,entry=None,dag=None,strategy="placement",trace_limit=0):
        super().__init__(n,arm,entry,dag)
        self.reported_arm=arm;self.strategy=strategy;self.limit=trace_limit
        if arm=="flat" and entry is not None:self.arm="named"
        self.group_layouts={};self.decompositions={};self.hinted_solutions={}
        self.top_pending=False;self.direct_primitive=False;self.compact_hint=None
        self.hint_status="absent";self.call_tree=None;self.hist=[0,0,0,0]

    def event(self,kind,**data):
        if len(self.events)<self.limit:self.events.append(dict(kind=kind,**data))
        else:self.dropped+=1

    def group_layout(self,n,group):
        key=(n,group)
        if key in self.group_layouts:return self.group_layouts[key]
        outside=tuple(j for j in range(n) if j not in group)
        inside=tuple(prior().scatter(x,group) for x in range(8))
        external=tuple(prior().scatter(x,outside) for x in range(1<<len(outside)))
        operands=tuple(-1 if j==group[0] else j for j in range(n) if j==group[0] or j not in group)
        slot=operands.index(-1)
        positions=tuple(j for j in range(n-2) if j!=slot)
        low=tuple(prior().scatter(x,positions) for x in range(1<<len(positions)))
        result=(inside,external,operands,slot,low);self.group_layouts[key]=result
        self.paid["placement_layouts_built"]+=1;self.paid["placement_layout_entries"]+=len(inside)+2*len(external)
        self.paid["placement_layout_mask_terms"]+=len(external)
        return result

    def decompose(self,n,table,group):
        self.paid["placement_group_requests"]+=1;key=(n,table,group)
        if key in self.decompositions:
            self.paid["placement_group_cache_hits"]+=1;return self.decompositions[key]
        self.paid["placement_group_trials"]+=1
        inside,outside,operands,slot,low=self.group_layout(n,group)
        zero=sum((table>>suffix&1)<<j for j,suffix in enumerate(outside))
        one=None;inner=0;probes=1;comparisons=0;complete=True
        for assignment,base in enumerate(inside[1:],1):
            column=sum((table>>(base|suffix)&1)<<j for j,suffix in enumerate(outside))
            probes+=1;comparisons+=1
            if column!=zero:
                if one is None:one=column
                else:
                    comparisons+=1
                    if column!=one:complete=False;break
                inner |= 1<<assignment
        result=None
        if complete and one is not None:
            quotient=sum(((zero>>j&1)<<raw)|((one>>j&1)<<(raw|(1<<slot))) for j,raw in enumerate(low))
            self.paid["placement_quotient_bit_reads"]+=2*len(low)
            result=(inner,quotient,operands);self.paid["placement_group_passes"]+=1
            # Check the factorization on every original assignment, not only
            # the two class representatives used for the quotient table.
            for raw in range(1<<n):
                index=sum((raw>>j&1)<<i for i,j in enumerate(group))
                args=[inner>>index&1 if j==-1 else raw>>j&1 for j in operands]
                q=sum(value<<i for i,value in enumerate(args))
                require((table>>raw&1)==(quotient>>q&1),"Two-column contraction is not exact on original inputs")
        else:self.paid["placement_group_failures"]+=1
        self.paid["placement_packed_shifts"]+=probes-1;self.paid["placement_packed_masks"]+=probes
        self.paid["placement_packed_column_comparisons"]+=comparisons
        self.paid["placement_cofactor_rows_equivalent"]+=probes*len(outside)
        self.decompositions[key]=result;return result

    def substitute(self,expr,operands):
        self.paid["placement_substitution_nodes"]+=1
        if expr[0]=="input":return operands[expr[1]]
        if expr[0]=="const":return expr
        return (expr[0],*(self.substitute(child,operands) for child in expr[1:]))

    def contract(self,n,table,group):
        value=self.decompose(n,table,group)
        if value is None:return None
        inner,quotient,operand_ids=value
        local=self.search(3,inner)
        if local is None:self.paid["placement_inner_failures"]+=1;return None
        outer=self.search(n-2,quotient)
        if outer is None:self.paid["placement_quotient_failures"]+=1;return None
        local_expr=self.remap(local[0],group)
        operands=tuple(local_expr if j==-1 else ("input",j) for j in operand_ids)
        expr=self.substitute(outer[0],operands)
        self.paid["placement_contractions"]+=1;self.event("group",inputs=n,group=group,inner=inner,quotient=quotient)
        return expr,local[1]+outer[1]

    def search_grouped(self,n,table,hint):
        if hint is not None:
            key=(n,table,hint)
            if key in self.hinted_solutions:
                self.paid["placement_hint_solution_hits"]+=1;result=self.hinted_solutions[key]
            else:result=self.contract(n,table,hint);self.hinted_solutions[key]=result
            self.hint_status="accepted" if result is not None else "rejected"
            if result is not None:self.paid["subproblem_requests"]+=1;return result
        key=(n,table)
        if self.strategy=="direct" or n<=3 or table&1 or key in self.solutions or key in self.failures:
            return super().search(n,table)
        for group in combinations(range(n),3):
            if group==hint:continue
            result=self.contract(n,table,group)
            if result is not None:
                self.paid["subproblem_requests"]+=1;self.paid["successful_subproblems_cached"]+=1;self.solutions[key]=result
                return result
        self.paid["placement_scan_fallbacks"]+=1
        return super().search(n,table)

    def lower(self,node):
        if node[0] in ("input","const"):return node
        children=tuple(self.lower(child) for child in node[1:])
        if node[0]=="FOLD":
            count=sum(child[0] not in ("input","const") for child in children);self.hist[count]+=1
            if self.reported_arm=="flat":
                self.paid["placement_inline_nodes"]+=2;return library_base().inline(self.entry["expr"],children)
        return (node[0],*children)

    def search(self,n,table):
        if self.direct_primitive:return super().search(n,table)
        root=self.top_pending;self.top_pending=False
        result=self.search_grouped(n,table,self.compact_hint if root else None)
        if root and result is not None and result[1]:
            self.call_tree=result[0];expr=self.lower(result[0])
            require(sum(self.hist)==result[1],"Contraction changed actual call multiplicity")
            return frozen(expr),result[1]
        return result

    def cache_sizes(self):
        return {**super().cache_sizes(),"placement_layouts":len(self.group_layouts),
                "placement_group_certificates":len(self.decompositions),"placement_hinted_roots":len(self.hinted_solutions)}

    def run(self,table,hint=None):
        if hint is not None:
            require(len(hint)==3 and len(set(hint))==3 and all(type(j) is int and 0<=j<self.n for j in hint),"Invalid anonymous hint")
            hint=tuple(sorted(hint))
        self.compact_hint=None;self.hint_status="absent" if hint is None else "pending"
        if hint is not None:
            positions=tuple(j for j in range(self.n) if any((table>>x&1)!=(table>>(x^(1<<j))&1) for x in range(1<<self.n)))
            if all(j in positions for j in hint):self.compact_hint=tuple(positions.index(j) for j in hint)
            else:self.hint_status="contains_irrelevant_input"
        self.top_pending=True;self.direct_primitive=self.strategy=="direct" and hint is None and self.arm=="primitive"
        self.call_tree=None;self.hist=[0,0,0,0]
        try:result=super().run(table)
        finally:self.top_pending=False;self.direct_primitive=False
        result.update(hint=normalized(hint),hint_status=self.hint_status,template_computed_arg_histogram=self.hist,
                      library_call_tree=normalized(self.call_tree),strategy=self.strategy)
        return result


def permutation_orbit(table,n):
    """Raw truth-word relabeling by adjacent transpositions, not source syntax."""
    all_bits=prior().full(n);cols=prior().columns(n)
    swaps=[(a&(all_bits^b),b&(all_bits^a),all_bits^(a^b),1<<j) for j,(a,b) in enumerate(zip(cols,cols[1:]))]
    found={table};pending=[table]
    for value in pending:
        for low,high,equal,shift in swaps:
            other=(value&equal)|((value&low)<<shift)|((value&high)>>shift)
            if other not in found:found.add(other);pending.append(other)
    return found


def census():
    """Exhaust 55 shapes and their literal Boolean permutation classes."""
    trees=ordered_trees(4)
    require(len(trees)==55,"Wrong ordered four-F tree inventory")
    groups={}
    for tree in trees:groups.setdefault(primitive_shape(tree),[]).append((tree_truth(tree),source_height(tree)))
    seen=set();heights=Counter();records=[]
    for normal,items in sorted(groups.items()):
        table=items[0][0];orbit=permutation_orbit(table,9)
        require(seen.isdisjoint(orbit),"Two normalized source classes have equivalent raw truth tables")
        require(all(t in orbit for t,_ in items),"An associative spelling left its raw semantic orbit")
        seen.update(orbit)
        actual=minimum_F_height(table,9);enumerated=min(height for _,height in items)
        require(actual==enumerated,"Truth-only minimum height differs from exhaustive source-tree inventory")
        require(all((table^(table>>(1<<j)))&(prior().full(9)^prior().columns(9)[j]) for j in range(9)),"A census function omits a raw input")
        heights[actual]+=1
        records.append(dict(normalized_shape=normal,minimum_height=actual,source_heights=sorted({h for _,h in items}),
                            labeled_functions=len(orbit),representative_truth=table))
    require(len(groups)==13 and dict(heights)=={2:1,3:8,4:4},"Claimed four-F minimum-height census differs")
    return dict(ordered_shapes=55,semantic_classes=13,minimum_height_classes=dict(sorted(heights.items())),
                labeled_functions=len(seen),class_records=records,
                scope="Complete F-only read-once trees on nine independent positive raw leaves; no constants or other primitives")


def self_test():
    cols=prior().columns(9);a,b,c,d,e,ff,g,h,i=cols
    A,B=f(a,b,c),f(d,e,ff)
    shallow=f(A,B,f(g,h,i));reassociated=f(g,h,f(A,B,i))
    require(shallow==reassociated,"Hand source-height alias identity fails")
    require(minimum_F_height(shallow,9)==2,"Height-two semantic alias minimum differs")
    U=f(a,b,f(c,d,e))
    three=f(U,ff,f(g,h,i));four=f(g,h,f(U,ff,i))
    require(three==four and minimum_F_height(three,9)==3,"Height-three/four semantic alias identity fails")
    dag=prior().SAVED_FOLD
    expr=["FOLD",["FOLD",0,1,2],["FOLD",3,4,5],["FOLD",6,7,8]]
    compiled,calls,_=prior().expand(expr,9,dag)
    compiled.update(constants={"zero":9,"one":10})
    require(calls==4 and len(compiled["gates"])==28 and prior().circuit_truth(compiled,9)==shallow,"Original nine-input expanded physical fixture fails")
    return dict(status="pass",source_height_aliases="2=3 and 3=4 under identical raw truth",physical_original_inputs=9,
                physical_raw_rows=512,physical_F_calls=4,physical_NANDs=28)


def check_result(actual,expected,target,model,entry,reference=False):
    arm="primitive" if reference else model.reported_arm
    dag=entry["dag"] if arm=="named" else None
    require(actual["arm"]==arm and actual["n"]==model.n,"Method or physical input width differs")
    require(frozen(actual["expr"])==expected["expr"] and actual["circuit"]==expected["circuit"],"Independent schedule/physical expansion differs")
    for key in ("cache_before","cache_after","trace","trace_dropped","input_support","physical_compile_cache_hit","template_uses"):
        require(actual[key]==expected[key],f"Semantic/cache receipt differs: {key}")
    for key,value in actual["work"].items():
        require(type(value) is int and value>=0 and value==expected["work"].get(key,0),f"Actual executed work differs: {key}: {value} vs {expected['work'].get(key,0)}")
    require(all(value==actual["work"].get(key,0) for key,value in expected["work"].items()),"Expected operation category missing")
    require(actual["status"]=="exact" and actual["truth"]==target,"Incorrect/failed physical return")
    require(actual["fold_dag"]==dag,"Physical library binding differs")
    require(prior().circuit_truth(actual["circuit"],model.n)==program_truth(actual["expr"],model.n,dag)==target,
            "Raw scalar circuit/AST evaluation differs")
    require(actual["macro_uses"]==expected["circuit"]["macro_uses"] and actual["expanded_NANDs"]==len(actual["circuit"]["gates"]),"Macro/gate count differs")
    if not reference:
        for key in ("hint","hint_status","strategy","template_computed_arg_histogram","library_call_tree"):
            require(normalized(actual[key])==normalized(expected[key]),f"Group/computed-operand metadata differs: {key}")
        require(sum(actual["template_computed_arg_histogram"])==actual["template_uses"],"Reported computed-argument bins omit a real call")
        if actual["library_call_tree"] is not None:
            require(program_truth(actual["library_call_tree"],model.n,entry["dag"])==target,"Annotated call tree changes original input semantics")


def producer_fixtures():
    """Generate known hand inputs only; no selected nine-input panel is read."""
    path=ROOT/"experiments"/TICKET/FAMILY/"placement.py"
    spec=importlib.util.spec_from_file_location("placement_hand_producer",path)
    producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)
    expr=library_base().representative_catalogue(Counter())[106]
    compiled,_,_=prior().expand(expr,3)
    entry=dict(truth=106,expr=normalized(expr),dag=dict(gates=compiled["gates"],output=compiled["output"]))
    x=[("input",j) for j in range(5)]
    nested=("FOLD",("FOLD",*x[:3]),x[3],x[4])
    changed=("FOLD",("AND",x[0],("XOR",x[1],x[2])),x[3],x[4])
    comparisons=0;seen_rejection=False;seen_computed=False
    for ast in (nested,changed):
        target=library_base().truth(ast,5,entry["dag"])
        for strategy in ("direct","placement"):
            for arm in ("primitive","named","flat"):
                for hint in (None,(0,1,2),(0,2,4)):
                    actual_engine=producer.PlacementSolver(5,arm,entry if arm!="primitive" else None,entry["dag"] if arm=="named" else None,strategy,trace_limit=0)
                    independent=ReplayPlacement(5,arm,entry if arm!="primitive" else None,entry["dag"] if arm=="named" else None,strategy)
                    for _ in range(2):
                        actual=actual_engine.solve(target,hint=hint);expected=independent.run(target,hint)
                        check_result(actual,expected,target,independent,entry);comparisons+=1
                        seen_rejection |= actual["hint_status"]=="rejected"
                        seen_computed |= sum(actual["template_computed_arg_histogram"][1:])>0
    require(seen_rejection and seen_computed,"Hand fixtures missed rejected grouping or true computed operands")
    return dict(status="pass",hand_comparisons=comparisons,held_solver_runs=0,rejected_hint_checked=True,computed_operands_checked=True,
                producer_sha256=file_digest(path))


METHODS=("reference-primitive-blind",)+tuple(f"{s}-{a}-{h}" for s in ("direct","placement") for a in ("primitive","named","flat") for h in ("blind","hint"))


def primitive_source(tree):
    if type(tree) is int:return tree
    a,b,c=(primitive_source(child) for child in tree[1:])
    if tree[0]=="F":return ("XOR",("AND",a,b),c)
    if tree[0]=="R-a":return ("AND",a,("XOR",b,c))
    require(tree[0]=="R-b","Unknown source local operation")
    return ("AND",b,("XOR",a,c))


def at(tree,path):
    for j in path:tree=tree[j+1]
    return tree


def replace(tree,path,op):
    if not path:return (op,*tree[1:])
    children=list(tree[1:]);children[path[0]]=replace(children[path[0]],path[1:],op)
    return (tree[0],*children)


def tagged_height(tree):return 0 if type(tree) is int else 1+max(tagged_height(c) for c in tree[1:])


def sites(tree,path=()):
    if type(tree) is int:return
    yield path
    for j,child in enumerate(tree[1:]):yield from sites(child,path+(j,))


def complete_shape_inventory():
    positives=defaultdict(set);negatives=defaultdict(set)
    for skeleton in ordered_trees(4):
        names=iter(range(9))
        def label(node):return next(names) if node[0]=="leaf" else ("F",*(label(c) for c in node[1:]))
        tree=label(skeleton);height=tagged_height(tree)
        positives[library_base().shape(primitive_source(tree))].add(height)
        for path in sites(tree):
            for op in ("R-a","R-b"):
                changed=replace(tree,path,op)
                negatives[library_base().shape(primitive_source(changed))].add(height)
    require(len(positives)==13 and set(positives).isdisjoint(negatives),"Positive/one-edit complete grammar overlaps")
    return positives,negatives


def validate_panel(folder):
    design=get(folder/"design.json")
    for relative,sha in design["sources"].items():require(file_digest(ROOT/relative)==sha,f"Changed bound source: {relative}")
    for name,sha in design["data"].items():require(file_digest(folder/name)==sha,f"Changed bound input: {name}")
    panel=get(folder/"panel.json");grades=get(folder/"grades.json");entry=get(folder/"given.json")
    require(len(panel)==len(grades)==48 and len({r["truth"] for r in panel})==48 and len({r["id"] for r in panel})==48,"Wrong unique 48-case panel")
    require({r["id"] for r in panel}==set(grades),"Grading IDs differ")
    require(entry["truth"]==106 and len(entry["dag"]["gates"])==6 and library_base().truth(entry["expr"],3)==106,
            "Supplied canonical six-NAND entry changed")
    require(sum(prior().nand(entry["dag"],[x>>j&1 for j in range(3)])<<x for x in range(8))==106,"Given circuit has a wrong row")
    positives,negatives=complete_shape_inventory()
    archive_tables=set();archive_structures=defaultdict(set)
    for ticket,family,public_name in (("FOLD-DEPTH-20261115-001","-E001_supplied_fold","public.json"),("FOLD-DISCOVERY-20261115-001","-E001_learned_library","held.json")):
        old=ROOT/"artifacts"/ticket/(ticket+family)
        public=get(old/public_name);grade=get(old/"grading.json")
        if "primary" in grade:grade={**grade["primary"],**grade["fixed9"]}
        for row in public:
            if row["n"]==9:
                archive_tables.add(row["truth"]);archive_structures[frozen(grade[row["id"]]["primitive_shape"])].add(ticket)
    case_by_id={row["id"]:row for row in panel};cells=defaultdict(list);negative_min_mismatches=[];one_bit_groups=defaultdict(list)
    for row in panel:
        ident=row["id"];g=grades[ident];table=row["truth"];hint=tuple(row["hint"])
        require(set(row)=={"id","n","truth","hint"} and row["n"]==9 and len(hint)==len(set(hint))==3 and hint==tuple(sorted(hint)) and all(type(j) is int and 0<=j<9 for j in hint),"Public input/hint leaks fields or has invalid arity")
        require(all((table^(table>>(1<<j)))&(prior().full(9)^prior().columns(9)[j]) for j in range(9)),"Inessential original raw input")
        source=frozen(g["source"]);primitive=primitive_source(source);normal=library_base().shape(primitive)
        require(library_base().truth(primitive,9)==table and frozen(g["primitive_source"])==primitive and frozen(g["normalized_structure"])==normal,
                "Source/primitive spelling and raw truth disagree")
        require(tagged_height(source)==g["depth"] and len(list(sites(source)))==4,"Wrong four-site source height")
        inventory=prior().source_inventory(primitive)
        require(inventory["AND"]==inventory["XOR"]==4 and all(inventory["input",j]==1 for j in range(9)),"Raw support or primitive gate inventory differs")
        require(g["four_F_depths"]==sorted(positives.get(normal,())) and g["one_rotation_depths"]==sorted(negatives.get(normal,())),"Complete grammar height metadata differs")
        if g["kind"]=="positive":
            require(minimum_F_height(table,9)==g["depth"]==min(positives[normal]),"Positive stratum is not the truth-only minimum F-cover height")
            require(all(at(source,p)[0]=="F" for p in sites(source)),"Positive contains a rotated site")
        else:
            require(g["kind"]=="negative" and minimum_F_height(table,9) is None,"Negative has an alternate complete F cover")
            height=minimum_mixed_height(table,9,1)
            require(height==min(negatives[normal]),"Truth-only one-rotation minimum differs")
            if height!=g["depth"]:negative_min_mismatches.append(ident)
        require(g["max_gate_disjoint_F"]==(4 if g["kind"]=="positive" else 3) and g["output_ones"]==table.bit_count(),"Primitive-library inventory or output density metadata differs")
        require(not g["prior_exact_match"] and table not in archive_tables and g["prior_structure_tickets"]==sorted(archive_structures.get(normal,())),"Prior overlap disclosure differs")
        local=at(source,g["hint_site"])
        require(all(type(j) is int for j in local[1:]) and tuple(sorted(local[1:]))==hint,"Hint supplies more than one genuine innermost group")
        inner=prior().one_bit_section(table,9,hint)
        require(inner is not None,"Hinted group is not a genuine one-bit interface")
        local_table=sum(library_base().expression_bit(primitive_source(local),prior().scatter(a,hint),9)<<a for a in range(8))
        require(inner[0]==local_table,"Derived local truth is a supplied assumption rather than its actual cofactor class")
        twin=case_by_id[g["partner"]];other=grades[g["partner"]]
        require(twin["hint"]==row["hint"] and other["partner"]==ident and other["pair"]==g["pair"],"Matched pair/hint differs")
        require(g["edit_at_hint"]==(g["edit_site"]==g["hint_site"]),"Hint-site mutation condition differs")
        if g["kind"]=="positive":require(replace(source,g["edit_site"],g["paired_rotation"])==frozen(other["source"]),"Negative changes more than the one matched local gate")
        cells[g["depth"],g["kind"]].append((row,g))
        count=sum(prior().one_bit_section(table,9,group) is not None for group in combinations(range(9),3))
        one_bit_groups[f"{g['depth']}-{g['kind']}"].append(count)
    summary={}
    for depth in (2,3,4):
        pos=cells[depth,"positive"];neg=cells[depth,"negative"]
        require(len(pos)==len(neg)==8 and sum(g["edit_at_hint"] for _,g in neg)==4,"Wrong matched-pair/edit strata")
        summary[depth]=dict(pairs=8,positive_mechanisms=len({frozen(g["normalized_structure"]) for _,g in pos}),
                            negative_mechanisms=len({frozen(g["normalized_structure"]) for _,g in neg}),negative_ones=sorted(r["truth"].bit_count() for r,_ in neg),
                            positive_prior_cases=sum(bool(g["prior_structure_tickets"]) for _,g in pos),negative_prior_cases=sum(bool(g["prior_structure_tickets"]) for _,g in neg))
    opportunities=dict(eligible_per_task=84,total_one_bit_groups=sum(map(sum,one_bit_groups.values())),total_triples=48*84,valid_per_case_by_cell=one_bit_groups)
    return design,panel,grades,entry,dict(positive_classes=13,minimum_F_classes={2:1,3:8,4:4},one_rotation_classes=len(negatives),
                by_depth=summary,negative_minimum_rotation_height_differs_from_paired_positive=negative_min_mismatches),normalized(opportunities)


def row_metrics(row,table):
    r=row["result"];w=r["work"];t=r.get("timing",{});h=r.get("template_computed_arg_histogram",[0]*4)
    return dict(tasks=1,exact=int(r.get("truth")==table and r["status"]=="exact" and r.get("circuit") is not None),
        wall_ns=row["wall_ns"],cpu_ns=row["cpu_ns"],init_ns=row["init_ns"],search_ns=round(t.get("search_seconds",0)*1e9),
        verify_ns=round(t.get("verification_seconds",0)*1e9),build_ns=round(t.get("build_seconds",0)*1e9),
        tests=w.get("binary_placement_trials",0)+w.get("ternary_placement_tests",0)+w.get("placement_group_trials",0),
        rejections=w.get("binary_placement_failures",0)+w.get("ternary_placement_failures",0)+w.get("placement_group_failures",0),
        group_trials=w.get("placement_group_trials",0),group_failures=w.get("placement_group_failures",0),group_source_reads=w.get("placement_source_bit_reads",0),
        quotient_reads=w.get("placement_quotient_bit_reads",0),packed_group_shifts=w.get("placement_packed_shifts",0),packed_group_masks=w.get("placement_packed_masks",0),
        packed_group_comparisons=w.get("placement_packed_column_comparisons",0),group_rows_equivalent=w.get("placement_cofactor_rows_equivalent",0),
        factor_bit_reads=w.get("factor_truth_bit_reads",0),uses=r.get("template_uses",0),uses_0_computed=h[0],uses_1_computed=h[1],uses_2_computed=h[2],uses_3_computed=h[3],
        physical_nands=r.get("expanded_NANDs") or 0,verified_rows=w.get("verification_rows",0))


def total(rows):
    result=Counter()
    for row in rows:result.update(row)
    return result


def middle(rows):return {key:statistics.median(row[key] for row in rows) for key in rows[0]}


def aggregate(runs,panel,grades,opportunities,design_hash):
    streams=defaultdict(dict);partials=defaultdict(list);failures=[]
    for (cache,method,repeat),(meta,rows) in runs.items():
        whole=Counter();group=defaultdict(Counter)
        for task,row in zip(panel,rows,strict=True):
            values=row_metrics(row,task["truth"]);whole.update(values);g=grades[task["id"]]
            if not values["exact"]:failures.append((cache,method,repeat,task["id"]))
            for label in (str(g["depth"]),f"{g['depth']}-{g['kind']}",g["kind"]):group[label].update(values)
            signature=json.dumps(g["normalized_structure"],separators=(",",":"))
            group[f"shape/{g['depth']}/{g['kind']}/{signature}"].update(values)
            if g["kind"]=="negative":group["edit-at-hint" if g["edit_at_hint"] else "edit-away"].update(values)
        whole.update(startup_ns=meta["startup_ns"],paid_ns=meta["startup_ns"]+whole["wall_ns"],paid_cpu_ns=meta["startup_cpu_ns"]+whole["cpu_ns"])
        streams[cache,method][repeat]=whole
        for label,values in group.items():partials[cache,method,label].append(values)
    methods={"warm":{},"cold":{}};cells={"warm":{},"cold":{}}
    for cache,n in (("warm",5),("cold",3)):
        for method in METHODS:
            series=streams[cache,method];require(set(series)==set(range(n)),"Incomplete timing repeat set")
            methods[cache][method]=middle(list(series.values()))
            methods[cache][method].update(paid_repeats_ns=[series[r]["paid_ns"] for r in range(n)],cpu_repeats_ns=[series[r]["paid_cpu_ns"] for r in range(n)])
            cells[cache][method]={label:middle(rows) for (c,m,label),rows in partials.items() if (c,m)==(cache,method)}
    warm=methods["warm"]
    benchmark=min((m for m in METHODS if "primitive-blind" in m),key=lambda m:warm[m]["paid_ns"])
    def compare(method,reference):
        a,b=warm[method],warm[reference];saved=100*(b["paid_ns"]-a["paid_ns"])/b["paid_ns"]
        wins=sum(x<y for x,y in zip(a["paid_repeats_ns"],b["paid_repeats_ns"],strict=True));cpu=a["paid_cpu_ns"]<b["paid_cpu_ns"]
        return dict(reference=reference,percent_saved=saved,paired_wins=wins,lower_cpu=cpu,passes=not failures and saved>=10 and wins>=4 and cpu)
    comparisons={}
    for method in METHODS:
        trials=[compare(method,benchmark)]
        if method.endswith("-hint"):trials.append(compare(method,method.removesuffix("-hint")+"-blind"))
        comparisons[method]=dict(comparisons=trials,qualifies=all(t["passes"] for t in trials))
    blind=[m for m in METHODS if m.endswith("-named-blind") and comparisons[m]["qualifies"]]
    hinted=[m for m in METHODS if m.endswith("-hint") and comparisons[m]["qualifies"]]
    return normalized(dict(tasks=48,assignments=512,measured_returns=104*48,failures=failures,benchmark=benchmark,decision="blind" if blind else "hint-only" if hinted else "stop",
        qualifying_blind=blind,qualifying_hinted=hinted,comparisons=comparisons,methods=methods,cells=cells,group_opportunities=opportunities,design_sha256=design_hash))


def call_histogram(tree):
    if tree is None or tree[0] in ("input","const"):return [0,0,0,0]
    total=[0,0,0,0]
    for child in tree[1:]:
        values=call_histogram(child);total=[a+b for a,b in zip(total,values)]
    if tree[0]=="FOLD":total[sum(child[0] not in ("input","const") for child in tree[1:])]+=1
    return total


def submitted_F_height(tree):
    if tree[0] in ("input","const"):return 0
    return int(tree[0]=="FOLD")+max(submitted_F_height(child) for child in tree[1:])


def timing_sensitivity(summary,runs):
    warm=summary["methods"]["warm"];base=summary["benchmark"];result={}
    primitives=[m for m in METHODS if "primitive-blind" in m]
    for method in ("placement-named-hint","placement-flat-hint","placement-primitive-hint","placement-named-blind"):
        drops=[]
        for dropped in range(5):
            ids=[i for i in range(5) if i!=dropped]
            alternative=min(primitives,key=lambda m:statistics.median(warm[m]["paid_repeats_ns"][i] for i in ids))
            value=statistics.median(warm[method]["paid_repeats_ns"][i] for i in ids)
            fixed=statistics.median(warm[base]["paid_repeats_ns"][i] for i in ids)
            stronger=statistics.median(warm[alternative]["paid_repeats_ns"][i] for i in ids)
            drops.append(dict(dropped_repeat=dropped,percent_saved_fixed_benchmark=100*(fixed-value)/fixed,
                              reselected_benchmark=alternative,percent_saved_reselected=100*(stronger-value)/stronger,
                              paired_wins_out_of_four=sum(warm[method]["paid_repeats_ns"][i]<warm[base]["paid_repeats_ns"][i] for i in ids),
                              lower_CPU_fixed_benchmark=statistics.median(warm[method]["cpu_repeats_ns"][i] for i in ids)<statistics.median(warm[base]["cpu_repeats_ns"][i] for i in ids)))
        result[method]=drops
    phases={}
    for method in (base,"placement-named-hint","placement-flat-hint","placement-primitive-hint"):
        values=[]
        for rep in range(5):
            metadata,rows=runs["warm",method,rep]
            values.append(dict(startup_ns=metadata["startup_ns"],initialization_ns=sum(r["init_ns"] for r in rows),
                               search_CPU_ns=sum(r["result"]["timing"]["search_cpu_ns"] for r in rows),
                               search_wall_ns=sum(round(r["result"]["timing"]["search_seconds"]*1e9) for r in rows),
                               build_ns=sum(round(r["result"]["timing"]["build_seconds"]*1e9) for r in rows),
                               verification_ns=sum(round(r["result"]["timing"]["verification_seconds"]*1e9) for r in rows),
                               wall_minus_CPU_ns=warm[method]["paid_repeats_ns"][rep]-warm[method]["cpu_repeats_ns"][rep]))
        phases[method]=dict(medians=middle(values),individual_repeats=values)
    return dict(leave_one_repeat_out=result,phase_profiles=phases,
                rule="Sensitivity only; original five-repeat median, four paired wins and CPU rule remains the sole decision gate")


def audit(folder):
    started=time.perf_counter()
    design,panel,grades,entry,panel_checks,opportunities=validate_panel(folder)
    print("Independent fixed-input grading, minimum heights, paired hints and source contracts passed.",flush=True)
    raw=[json.loads(line) for line in (folder/"results.jsonl").read_text().splitlines()]
    expected_order=[]
    for rep in range(5):
        for cache in (("warm","cold") if rep%2==0 else ("cold","warm")):
            if cache=="cold" and rep>=3:continue
            seq=METHODS if rep%2==0 else METHODS[::-1];offset=(3*rep+5*int(cache=="cold"))%13
            expected_order.extend(f"{cache}-{rep}-{method}" for method in seq[offset:]+seq[:offset])
    require(len(raw)==104 and [r["case"] for r in raw]==expected_order,"Missing, duplicated or reordered official method stream")
    require(all(r["status"]=="ok" and r["attempt"]==1 for r in raw) and len({r["worker"] for r in raw})==104,"Official failures/retries or reused timing processes")
    runs={};saved_expected={};expected_models={};total_raw=0;total_NANDs=0;stream_hashes={};stage_heights=defaultdict(Counter)
    for runner in raw:
        meta=runner["result"];cache,method,rep=(meta[k] for k in ("cache","method","repeat"));strategy,arm,hint_mode=method.split("-")
        require(meta["tasks"]==48 and meta["file"]==runner["case"]+".jsonl.gz","Method stream identity differs")
        require(runner["job_sha"]==design["sources"][str((ROOT/"experiments"/TICKET/FAMILY/"job.py").relative_to(ROOT))],"Different job source executed")
        require(datetime.fromisoformat(runner["finished_at"])>=datetime.fromisoformat(design["frozen_utc"]),"Execution predates design binding")
        path=folder/meta["file"];require(file_digest(path)==meta["sha256"],"Raw receipt hash differs")
        stream_hashes[meta["file"]]=meta["sha256"]
        with gzip.open(path,"rt") as source:rows=[json.loads(line) for line in source]
        require([r["id"] for r in rows]==[p["id"] for p in panel],"Paid task sequence/coverage differs")
        model=None
        for task,row in zip(panel,rows,strict=True):
            fresh=model is None or cache=="cold"
            if fresh:
                model=QuietPeel(9,"primitive") if strategy=="reference" else ReplayPlacement(9,arm,entry if arm!="primitive" else None,entry["dag"] if arm=="named" else None,strategy)
            key=(cache,method,task["id"])
            hint=task["hint"] if hint_mode=="hint" else None
            if rep==0:
                expected=model.run(task["truth"]) if strategy=="reference" else model.run(task["truth"],hint)
                saved_expected[key]=expected
            else:expected=saved_expected[key]
            actual=row["result"]
            require(actual["status"]!="error","Runtime failure remains paid, but exact program replay is inconclusive")
            check_result(actual,expected,task["truth"],model,entry,strategy=="reference")
            require(actual["input_support"]==list(range(9)) and actual["circuit"]["inputs"]==9 and actual["work"]["verification_rows"]==512,
                    "Contracted operands replaced original raw inputs in the physical channel/check")
            require(actual["expanded_NANDs"]==24,"Four AND/four XOR physical inventory was not preserved")
            require(row["return_bytes"]==len(canonical(actual["circuit"])),"Return serialization work differs")
            require(row["init_ns"]>=0 and row["wall_ns"]>row["init_ns"] and row["cpu_ns"]>0,"Invalid paid timing fields")
            timing=actual["timing"]
            require(sum(timing[k] for k in ("input_seconds","search_seconds","build_seconds","verification_seconds"))<=timing["elapsed_seconds"]+1e-8 and
                    timing["elapsed_seconds"]*1e9<=row["wall_ns"] and timing["search_cpu_ns"]<=row["cpu_ns"],"Outer time omits a search/check/return phase")
            if strategy!="reference":
                setup=actual["library_setup"]
                require((setup is not None)==fresh,"Library installation repeated or omitted")
                if setup is not None:
                    require(all(value==model.setup.get(name,0) for name,value in setup["work"].items()),"Paid entry/role setup differs")
                    require(setup["seconds"]*1e9<=row["init_ns"],"Installation omitted from paid initialization")
                    require(setup["truth"]==(106 if arm!="primitive" else None) and setup["expr"]==(entry["expr"] if arm!="primitive" else None),"Wrong installed free entry")
                call_tree=actual["library_call_tree"]
                require(call_histogram(call_tree)==actual["template_computed_arg_histogram"],"Computed operands were counted from printed length")
                if call_tree is not None:
                    require(library_base().variable_support(call_tree)==Counter({j:1 for j in range(9)}),"Computed call operands overlap or hide raw variables")
                    if rep==0:stage_heights[cache,method,grades[task["id"]]["depth"],grades[task["id"]]["kind"]][submitted_F_height(call_tree)]+=1
            total_raw+=512;total_NANDs+=512*24
        require(meta["startup_ns"]+sum(row["wall_ns"] for row in rows)<=runner["seconds"]*1e9,"Paid full-stream cost exceeds entire runner time")
        runs[cache,method,rep]=(meta,rows)
    print("All 4,992 physical programs, original raw inputs, exact work counters and computed operands passed.",flush=True)
    matched=0;emission_order_differences=0
    for cache,repeats in (("warm",5),("cold",3)):
        for rep in range(repeats):
            for strategy in ("direct","placement"):
                for hint in ("blind","hint"):
                    _,named=runs[cache,f"{strategy}-named-{hint}",rep];_,flat=runs[cache,f"{strategy}-flat-{hint}",rep]
                    for a,b in zip(named,flat,strict=True):
                        one,two=a["result"],b["result"]
                        require(one["library_call_tree"]==two["library_call_tree"] and one["template_computed_arg_histogram"]==two["template_computed_arg_histogram"],"Named/flat used different abstract application sites")
                        require(library_base().physical_dependencies(one["circuit"])==library_base().physical_dependencies(two["circuit"]),"Matched inline NAND dependency/count differs")
                        emission_order_differences+=one["circuit"]["gates"]!=two["circuit"]["gates"];matched+=1
    expected=aggregate(runs,panel,grades,opportunities,file_digest(folder/"design.json"))
    require(expected==get(folder/"result.json"),"Independent method/cell/gate aggregation differs from the final assessor")
    sensitivity=timing_sensitivity(expected,runs)
    methods=expected["methods"]["warm"];named=methods["placement-named-hint"];flat=methods["placement-flat-hint"];base=methods[expected["benchmark"]]
    return dict(study=TICKET,verdict="PASS",independence="Independent scalar cofactor classification, exact public-schedule/counter replay, raw NAND circuits, minimum-cover grading, and complete cost/gate aggregation. No held producer solver called.",
        input_hashes={name:file_digest(folder/name) for name in ("design.json","panel.json","grades.json","given.json","results.jsonl","result.json")},
        source_sha256=file_digest(Path(__file__)),stream_hashes=stream_hashes,panel_checks=panel_checks,
        physical=dict(programs=4992,raw_input_rows=total_raw,scalar_NAND_evaluations=total_NANDs,original_inputs=9,rows_per_program=512,NANDs_each=24,
                      matched_named_inline_pairs=matched,different_emission_orders=emission_order_differences),
        all_work_counters_match=True,benchmark=expected["benchmark"],decision=expected["decision"],qualifying_blind=expected["qualifying_blind"],
        qualifying_hinted=expected["qualifying_hinted"],comparisons=expected["comparisons"],methods=expected["methods"],
        group_opportunities=opportunities,timing_sensitivity=sensitivity,
        submitted_complete_call_heights={"/".join(map(str,key)):dict(value) for key,value in stage_heights.items()},
        named_hint_CPU_saved_percent=100*(base["paid_cpu_ns"]-named["paid_cpu_ns"])/base["paid_cpu_ns"],
        named_inline_CPU_difference_ns=flat["paid_cpu_ns"]-named["paid_cpu_ns"],
        interpretation=["The registered gate and every raw input/counter were reproduced; the primary decision must remain distinct from sensitivity summaries.",
            "Minimum depth refers to complete read-once F-only covers; equivalent source trees have different heights, and unrestricted Boolean/NAND depth is not established.",
            "Height2 has one positive semantic mechanism represented by eight paired recodings; prior structural overlap and output-density differences remain disclosed.",
            "All informed arms infer a local truth byte and quotient from the same unordered triple. Computed operands are permitted in subsequent ordinary primitive operations.",
            "Computed proxy inputs were substituted by actual programs, and every return was executed on all512 original raw assignments.",
            "Named and inlined arms use the same abstract application tree and six-NAND dependencies; naming cannot explain a different semantic placement decision.",
            "A positive alternative for a modest named/inline CPU difference is less AST lowering/materialization work in the retained-call representation. This does not explain large wall/CPU gaps by itself.",
            "The observed wall gate is host-specific; full per-repeat wall/CPU and leave-one-repeat sensitivity expose descheduling/variation rather than attributing all elapsed saving to logical work.",
            "A hint-only result supports a bounded test of locating groups at fixed width. It does not earn increased depth or a claimed blind library-learning improvement."],
        fixture_tests=self_test(),audit_elapsed_s=time.perf_counter()-started,completed_utc=datetime.now(timezone.utc).isoformat())


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test",action="store_true");parser.add_argument("--census",action="store_true")
    parser.add_argument("--producer-fixtures",action="store_true")
    parser.add_argument("--audit",action="store_true");parser.add_argument("--artifacts",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args()
    if args.audit:
        result=audit(args.artifacts)
        (args.artifacts/"audit.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps({"verdict":result["verdict"],"decision":result["decision"],"benchmark":result["benchmark"],"hinted":result["qualifying_hinted"],
                          "physical":result["physical"],"audit":str(args.artifacts/"audit.json")},indent=2))
    else:print(json.dumps(producer_fixtures() if args.producer_fixtures else census() if args.census else self_test(),sort_keys=True))
