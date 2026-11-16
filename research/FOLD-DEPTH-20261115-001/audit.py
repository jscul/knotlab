"""Independent physical and accounting audit of the supplied-fold experiment.

No producer evaluator, factorizer, task generator or selector is imported.
By default only hand fixtures execute.  --audit consumes sealed receipts.
The homogeneous arbitrary-gate CHAIN certificate and the stronger particular-F
read-once TREE certificate are different finite questions.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import gzip
import hashlib
import importlib.util
from itertools import combinations, permutations, product
import json
from pathlib import Path
import statistics
import sys
import time


TICKET="FOLD-DEPTH-20261115-001"
FAMILY=TICKET+"-E001_supplied_fold"
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_OUT=ROOT/"artifacts"/TICKET/FAMILY
ROLES=("primitive","named","flat")
ARMS=ROLES+tuple("peel-"+role for role in ROLES)
SAVED_FOLD={"gates":[[0,1],[5,5],[4,2],[7,6],[4,6],[9,2],[8,10]],"output":11}


class AuditError(ValueError):
    pass


def require(condition,message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get(path):
    return json.loads(Path(path).read_bytes())


def full(n):
    return (1<<(1<<n))-1


def bit(value):
    require(type(value) is int and value in (0,1),"Expected an actual bit")
    return value


@lru_cache(maxsize=None)
def columns(n):
    return tuple(sum((raw>>j&1)<<raw for raw in range(1<<n)) for j in range(n))


def nand(dag,args):
    values=[bit(x) for x in args]+[0,1]
    require(set(dag)=={"gates","output"},"Malformed literal saved DAG")
    for gate in dag["gates"]:
        require(isinstance(gate,(list,tuple)) and len(gate)==2 and all(type(i) is int and 0<=i<len(values) for i in gate),
                "NAND reads an invalid or future operand")
        values.append(1-(values[gate[0]]&values[gate[1]]))
    require(type(dag["output"]) is int and 0<=dag["output"]<len(values),"Invalid NAND output")
    return values[dag["output"]]


def source_value(tree,raw,n):
    """Raw scalar semantics for independently spelled grader source formulas."""
    if type(tree) is int:
        require(0<=tree<n,"Source leaf outside raw input domain")
        return raw>>tree&1
    require(isinstance(tree,(tuple,list)) and tree,"Malformed source expression")
    op=tree[0]
    if op=="input":
        require(len(tree)==2 and type(tree[1]) is int and 0<=tree[1]<n,"Invalid program input")
        return raw>>tree[1]&1
    if op=="const":
        require(len(tree)==2,"Invalid constant expression")
        return bit(tree[1])
    if op=="NOT":
        require(len(tree)==2,"NOT arity differs")
        return 1-source_value(tree[1],raw,n)
    if op=="FOLD":
        require(len(tree)==4,"Saved fold requires three actual operands")
        return nand(SAVED_FOLD,[source_value(child,raw,n) for child in tree[1:]])
    require(op in ("AND","OR","XOR") and len(tree)==3,"Unknown/malformed Boolean expression")
    a,b=(source_value(child,raw,n) for child in tree[1:])
    return a&b if op=="AND" else a|b if op=="OR" else a^b


def source_truth(tree,n):
    return sum(source_value(tree,raw,n)<<raw for raw in range(1<<n))


def expand(tree,n,fold=SAVED_FOLD):
    """Literal independent NAND expansion, with no global common-subtree reuse."""
    gates=[];ops=Counter();calls=0
    def gate(a,b):
        gates.append([a,b]);return n+1+len(gates)
    def visit(node):
        nonlocal calls
        if type(node) is int:
            require(0<=node<n,"Leaf outside input domain")
            return node
        op=node[0]
        if op=="input":
            require(len(node)==2 and type(node[1]) is int and 0<=node[1]<n,"Bad input node")
            return node[1]
        if op=="const":
            require(len(node)==2,"Bad constant node")
            return n+bit(node[1])
        if op=="NOT":
            a=visit(node[1]);ops[op]+=1;return gate(a,a)
        if op=="FOLD":
            require(len(node)==4,"Bad saved-fold node")
            addresses=[visit(child) for child in node[1:]]+[n,n+1]
            for a,b in fold["gates"]:
                addresses.append(gate(addresses[a],addresses[b]))
            calls+=1
            return addresses[fold["output"]]
        require(op in ("AND","OR","XOR") and len(node)==3,"Unknown program operator")
        a,b=visit(node[1]),visit(node[2]);ops[op]+=1
        if op=="AND":
            t=gate(a,b);return gate(t,t)
        if op=="OR":
            aa,bb=gate(a,a),gate(b,b);return gate(aa,bb)
        t=gate(a,b);aa,bb=gate(a,t),gate(b,t);return gate(aa,bb)
    output=visit(tree)
    return {"inputs":n,"gates":gates,"output":output},calls,ops


def circuit_truth(circuit,n):
    require(circuit["inputs"]==n,"Physical input arity differs")
    if "constants" in circuit:
        require(circuit["constants"]=={"zero":n,"one":n+1},"Physical constant addresses differ")
    # Validate addresses once, then independently execute every scalar input.
    size=n+2
    for operands in circuit["gates"]:
        require(isinstance(operands,(list,tuple)) and len(operands)==2 and all(type(i) is int and 0<=i<size for i in operands),
                "Physical NAND references a future or invalid address")
        size+=1
    require(type(circuit["output"]) is int and 0<=circuit["output"]<size,"Physical output tap is invalid")
    answer=0
    for raw in range(1<<n):
        values=[raw>>j&1 for j in range(n)]+[0,1]
        for a,b in circuit["gates"]:
            values.append(1-(values[a]&values[b]))
        answer |= values[circuit["output"]]<<raw
    return answer


def scatter(raw,positions):
    return sum((raw>>j&1)<<old for j,old in enumerate(positions))


@lru_cache(maxsize=256)
def gate_class(table):
    require(type(table) is int and 0<=table<256,"Wrong ternary Boolean table")
    return min(sum((table>>scatter(x,order)&1)<<x for x in range(8)) for order in permutations(range(3)))


F_CLASS=gate_class(sum(nand(SAVED_FOLD,[x>>j&1 for j in range(3)])<<x for x in range(8)))


def two_pin_sections(table,n,i,j):
    other=tuple(k for k in range(n) if k not in (i,j))
    return tuple(sum((table>>(scatter(x,other)|((a&1)<<i)|((a>>1)<<j))&1)<<x for x in range(1<<(n-2)))
                 for a in range(4))


@lru_cache(maxsize=None)
def chain_classes(table,n):
    """All homogeneous arbitrary-gate read-once CHAINS, modulo port order."""
    require(n>=3 and n%2 and 0<=table<=full(n),"Wrong homogeneous-chain domain")
    if n==3:
        return frozenset((gate_class(table),))
    result=set();rest_full=full(n-2)
    for i,j in combinations(range(n),2):
        sections=two_pin_sections(table,n,i,j)
        varying=[s for s in sections if s not in (0,rest_full)]
        if not varying:
            continue
        canonical_inner=varying[0]
        if any(s not in (0,rest_full,canonical_inner,canonical_inner^rest_full) for s in sections):
            continue
        for inner in (canonical_inner,canonical_inner^rest_full):
            outer=0
            for a,section in enumerate(sections):
                for h in (0,1):
                    value=0 if section==0 else 1 if section==rest_full else h if section==inner else 1-h
                    outer |= value<<(a+4*h)
            operation=gate_class(outer)
            if operation in chain_classes(inner,n-2):
                result.add(operation)
    return frozenset(result)


@lru_cache(maxsize=None)
def chain_classes_or_leaves(table,n,logical_inputs):
    """Every OR-leaf partition, without accepting a supplied grouping hint."""
    if n==logical_inputs:
        return chain_classes(table,n)
    require(n>logical_inputs>=3,"Invalid OR-leaf quotient")
    quotients=set()
    for i,j in combinations(range(n),2):
        z,a,b,ab=two_pin_sections(table,n,i,j)
        if a==b==ab:
            quotients.add(z|(a<<(1<<(n-2))))
    return frozenset().union(*(chain_classes_or_leaves(q,n-1,logical_inputs) for q in quotients))


@lru_cache(maxsize=None)
def ternary_partitions(n):
    """Unordered nonempty odd-sized groups; operation class covers port order."""
    out=[]
    for tail in product(range(3),repeat=n-1):
        labels=(0,)+tail
        if 1 not in labels or 2 not in labels or labels.index(1)>labels.index(2):
            continue
        groups=tuple(tuple(i for i,label in enumerate(labels) if label==k) for k in range(3))
        if all(len(group)%2 for group in groups):
            out.append(groups)
    return tuple(out)


@lru_cache(maxsize=None)
def one_bit_section(table,n,group):
    other=tuple(k for k in range(n) if k not in group)
    rows=[];kinds={}
    for assignment in range(1<<len(group)):
        fixed=scatter(assignment,group)
        section=sum((table>>(fixed|scatter(x,other))&1)<<x for x in range(1<<len(other)))
        rows.append(section)
        if section not in kinds:
            kinds[section]=len(kinds)
            if len(kinds)>2:
                return None
    if len(kinds)!=2:
        return None
    # F(0,0,0)=0, so every full F subtree has zero on zero. The zero
    # assignment pins the Boolean orientation without guessing an inner label.
    word=sum((row!=rows[0])<<a for a,row in enumerate(rows))
    representative=next(a for a in range(1<<len(group)) if word>>a&1)
    return word,(0,scatter(representative,group))


@lru_cache(maxsize=None)
def f_tree_cover(table,n):
    """A complete read-once TREE of F on raw positive inputs, any grouping."""
    if n==1:
        return table==2
    if n<3 or not n%2 or table&1:
        return False
    if n==3:
        return gate_class(table)==F_CLASS
    for groups in ternary_partitions(n):
        sections=[one_bit_section(table,n,group) for group in groups]
        if any(section is None for section in sections):
            continue
        operation=sum((table>>(sum(sections[i][1][x>>i&1] for i in range(3)))&1)<<x for x in range(8))
        if gate_class(operation)!=F_CLASS:
            continue
        if all(f_tree_cover(section[0],len(group)) for group,section in zip(groups,sections)):
            return True
    return False


def factor_witness(table,n,left,op):
    """Independent exhaustive cofactor-matrix factor test for a given split."""
    require(op in ("AND","OR","XOR"),"Unknown binary factor operation")
    left=tuple(left);right=tuple(i for i in range(n) if i not in left)
    require(left and right and len(set(left))==len(left) and all(0<=i<n for i in left),"Invalid factor split")
    rows=tuple(sum((table>>(scatter(a,left)|scatter(b,right))&1)<<b for b in range(1<<len(right)))
               for a in range(1<<len(left)))
    all_right=full(len(right))
    if op=="AND":
        r=next((row for row in rows if row),None)
        if r is None or any(row not in (0,r) for row in rows):return None
        l=sum((row==r)<<a for a,row in enumerate(rows))
    elif op=="OR":
        r=next((row for row in rows if row!=all_right),None)
        if r is None or any(row not in (all_right,r) for row in rows):return None
        l=sum((row==all_right)<<a for a,row in enumerate(rows))
    else:
        r=rows[0]
        if any(row not in (r,r^all_right) for row in rows):return None
        l=sum((row!=r)<<a for a,row in enumerate(rows))
    if l in (0,full(len(left))) or r in (0,all_right):return None
    return l,r


def normalized_source(tree):
    if type(tree) is int:return ("leaf",)
    op=tree[0];children=[]
    for child in tree[1:]:
        node=normalized_source(child)
        children.extend(node[1:] if op in ("AND","OR","XOR") and node[0]==op else (node,))
    return (op,*sorted(children)) if op in ("AND","OR","XOR") else (op,*children)


def source_inventory(tree):
    if type(tree) is int:return Counter({("input",tree):1})
    total=Counter({tree[0]:1})
    for child in tree[1:]:total.update(source_inventory(child))
    return total


def audit_panel(public,grading):
    require(len(public)==60 and len({p["id"] for p in public})==60,"Wrong unique measured task count")
    require(all(set(p)=={"id","n","truth"} for p in public),"Task inputs disclose extra metadata")
    require(len({(p["n"],p["truth"]) for p in public})==60,"Duplicate function among unique tasks")
    expected=sorted(public,key=lambda p:hashlib.sha256(("depth-schedule-v1/"+p["id"]).encode()).digest())
    require(public==expected,"The public stream is not the preselected common order")
    tasks={p["id"]:p for p in public};stats={};tree_exceptions=[]
    require(set(grading)=={"primary","fixed9"},"Unexpected grading panels")
    require(len(grading["primary"])==48 and len(grading["fixed9"])==18,"Wrong grading denominators")
    require(len(set(grading["primary"])&set(grading["fixed9"]))==6,"Fixed-width aliases counted incorrectly")
    for split,metadata in grading.items():
        groups=defaultdict(list);cells=Counter()
        for ident,meta in metadata.items():
            require(ident in tasks,"Grading has an unmeasured task")
            task=tasks[ident];n=task["n"];truth=task["truth"];depth=meta["depth"];kind=meta["kind"]
            require(depth in (2,3,4) and kind in ("positive","negative"),"Unknown depth/control stratum")
            require(n==(9 if split=="fixed9" else 2*depth+1) and meta["logical_inputs"]==2*depth+1,"Wrong raw/logical width")
            require(truth.bit_count()==1<<(n-1) and truth.bit_count()==meta["balanced_ones"],"Output-balance mismatch")
            require(all((truth^(truth>>(1<<j)))&(full(n)^columns(n)[j]) for j in range(n)),"Inessential raw input")
            require(len(meta["sources"])>=3 and all(source_truth(source,n)==truth for source in meta["sources"]),"Equivalent source spellings disagree")
            if "source_styles_innermost_first" in meta:
                require(len(meta["source_styles_innermost_first"])==len(meta["sources"]),"Source-style metadata is incomplete")
            require(json.loads(json.dumps(normalized_source(meta["sources"][0])))==meta["primitive_shape"],"Normalized source mechanism metadata differs")
            inventory=source_inventory(meta["sources"][0])
            require(all(inventory["input",j]==1 for j in range(n)) and sum(inventory[op] for op in ("AND","OR","XOR"))==n-1==meta["primitive_gates"],
                    "Matched source is not read-once or has wrong primitive size")
            classes=chain_classes_or_leaves(truth,n,meta["logical_inputs"])
            require(sorted(classes)==meta["full_gate_classes_with_or_leaves"],"Arbitrary homogeneous-chain certificate differs")
            require((kind=="positive")==bool(classes),"Negative is a homogeneous arbitrary-gate chain")
            if kind=="positive":require(F_CLASS in classes,"Positive excludes supplied F chain")
            if split=="primary":
                cover=f_tree_cover(truth,n)
                if kind=="positive":require(cover,"Positive lacks the expected general F-tree cover")
                elif cover:tree_exceptions.append(ident)
            if "reference" in meta:
                require(split=="fixed9" and depth==4 and meta["reference"]==ident and ident in grading["primary"],"Unbound fixed-width alias")
            groups[meta["pair"]].append((ident,meta));cells[depth,kind]+=1
        for pair,items in groups.items():
            require(len(items)==2 and {m["kind"] for _,m in items}=={"positive","negative"},"Broken positive/negative match")
            for ident,meta in items:
                other=next(i for i,_ in items if i!=ident)
                require(meta["partner"]==other,"Matched partner changed")
                require(meta["paired_edit"][0] in range(meta["depth"]),"Out-of-range recurrence edit")
                require(meta["mutation"]==(None if meta["kind"]=="positive" else meta["paired_edit"]),"Control mutation label differs")
            pos=next(m for _,m in items if m["kind"]=="positive");neg=next(m for _,m in items if m["kind"]=="negative")
            a,b=(source_inventory(m["sources"][0]) for m in (pos,neg))
            if pos["equal_gate_inventory"]:
                require(a==b,"Rotation control changed raw inputs or gate inventory")
            else:
                require(all(b[op]-a[op]=={"AND":-1,"OR":1,"XOR":0}[op] for op in ("AND","OR","XOR")),"OR replacement control has wrong inventory change")
        stats[split]={"rows":len(metadata),"pairs":len(groups),"strata":{f"{d}-{k}":v for (d,k),v in sorted(cells.items())},
                      "distinct_normalized_mechanisms":len({canonical(m["primitive_shape"]) for m in metadata.values()}),
                      "aliases":sum("reference" in m for m in metadata.values())}
    return {"unique_tasks":60,"raw_input_rows":sum(1<<p["n"] for p in public),"panels":stats,
            "primary_negative_complete_F_tree_exceptions":tree_exceptions,
            "homogeneous_arbitrary_gate_exclusion_scope":"read-once chains, including all admissible OR-leaf partitions"}


def frozen(tree):
    return tuple(map(frozen,tree)) if isinstance(tree,(tuple,list)) else tree


class ReplaySolver:
    """Public schedule replay using independent scalar cofactor arithmetic.

    Every newly executed binary screen is cross-checked by the exhaustive
    matrix predicate above. Counters use the registered logical units, not
    the number of Python instructions executed by this audit.
    """
    def __init__(self,n,arm):
        self.n=n;self.arm=arm;self.paid=Counter();self.layouts={};self.factors={};self.probes={}
        self.roots={};self.solutions={};self.failures=set();self.remaps={};self.programs={}
        self.events=[];self.dropped=0

    def event(self,kind,**data):
        if len(self.events)<32:self.events.append(dict(kind=kind,**data))
        else:self.dropped+=1

    def layout(self,n,mask):
        self.paid["layout_requests"]+=1
        if (n,mask) in self.layouts:
            self.paid["layout_cache_hits"]+=1;return self.layouts[n,mask]
        positions=tuple(j for j in range(n) if mask>>j&1);outside=tuple(j for j in range(n) if not mask>>j&1)
        assignments=tuple(scatter(x,positions) for x in range(1<<len(positions)))
        broadcasts=tuple(sum(1<<(x|scatter(y,outside)) for y in range(1<<len(outside))) for x in assignments)
        self.paid.update(layout_tables_built=1,layout_rows_indexed=1<<n,
                         layout_embedding_entries=(1<<len(positions))+(1<<len(outside)),layout_broadcast_bit_ops=3*(1<<n))
        value=(positions,assignments,broadcasts);self.layouts[n,mask]=value;return value

    def section(self,n,truth,mask,fixed):
        self.paid["factor_requests"]+=1;key=(n,truth,mask,fixed)
        if key in self.factors:
            self.paid["factor_cache_hits"]+=1;return self.factors[key]
        positions,assignments,broadcasts=self.layout(n,mask)
        values=[truth>>(x|fixed)&1 for x in assignments]
        compact=sum(v<<i for i,v in enumerate(values));lifted=sum(column for column,v in zip(broadcasts,values) if v)
        self.paid["factor_truth_bit_reads"]+=len(values);self.paid["factor_lift_bit_ors"]+=sum(values)
        self.paid["factor_constant_sections" if compact in (0,full(len(positions))) else "factor_nonconstant_sections"]+=1
        self.paid["factor_sections_extracted"]+=1
        value=(compact,lifted,positions);self.factors[key]=value;return value

    @staticmethod
    @lru_cache(maxsize=None)
    def splits(n):
        mask=(1<<n)-1
        return tuple(sorted((m for m in range(1,mask) if (m.bit_count(),m)<=((mask^m).bit_count(),mask^m)),key=lambda m:(m.bit_count(),m)))

    def probe(self,n,truth,mask,op):
        self.paid["binary_placement_requests"]+=1;key=(n,truth,mask,op)
        if key in self.probes:
            self.paid["binary_placement_cache_hits"]+=1;return self.probes[key]
        self.paid["binary_placement_trials"]+=1;other=((1<<n)-1)^mask
        witness=(truth&-truth).bit_length()-1
        a=self.section(n,truth,mask,witness&other if op=="AND" else 0)
        b=self.section(n,truth,other,witness&mask if op=="AND" else 0)
        valid=bool(a[0] not in (0,full(len(a[2]))) and b[0] not in (0,full(len(b[2]))) and not(a[0]&1) and not(b[0]&1))
        if valid:
            composed=a[1]&b[1] if op=="AND" else a[1]|b[1] if op=="OR" else a[1]^b[1]
            self.paid["binary_recomposition_ops"]+=1;self.paid["binary_comparison_rows_equivalent"]+=1<<n
            valid=composed==truth
        else:self.paid["binary_early_rejections"]+=1
        independent=factor_witness(truth,n,a[2],op)
        independently_valid=bool(independent is not None and not(independent[0]&1) and not(independent[1]&1))
        require(valid==independently_valid,"Screen disagrees with independent exhaustive factor test")
        self.paid["binary_placement_passes" if valid else "binary_placement_failures"]+=1
        self.event("binary",inputs=n,group=mask,op=op,passed=valid)
        result={"op":op,"group":mask,"other":other,"a":a,"b":b} if valid else None
        self.probes[key]=result;return result

    def root(self,n,truth):
        self.paid["root_certificate_requests"]+=1;key=(n,truth)
        if key in self.roots:
            self.paid["root_certificate_cache_hits"]+=1;return self.roots[key]
        result=None
        for mask in self.splits(n):
            for op in ("AND","OR","XOR"):
                result=self.probe(n,truth,mask,op)
                if result is not None:break
            if result is not None:break
        self.roots[key]=result;self.paid["root_certificate_failures"]+=result is None;return result

    def remap(self,expr,positions):
        self.paid["AST_remap_requests"]+=1;key=(expr,positions)
        if key in self.remaps:
            self.paid["AST_remap_cache_hits"]+=1;return self.remaps[key]
        if expr[0]=="input":result=("input",positions[expr[1]])
        elif expr[0]=="const":result=expr
        else:result=(expr[0],*(self.remap(child,positions) for child in expr[1:]))
        self.paid["AST_remap_nodes"]+=1;self.remaps[key]=result;return result

    def join_binary(self,n,truth,cert):
        a,b=cert["a"],cert["b"];left=self.search(len(a[2]),a[0])
        if left is None:return None
        right=self.search(len(b[2]),b[0])
        if right is None:return None
        self.paid["AST_nodes_built"]+=1
        return ((cert["op"],self.remap(left[0],a[2]),self.remap(right[0],b[2])),left[1]+right[1])

    def lift(self,n,mask,compact):
        broadcasts=self.layout(n,mask)[2];self.paid["factor_lift_bit_ors"]+=compact.bit_count()
        return sum(column for i,column in enumerate(broadcasts) if compact>>i&1)

    def template(self,n,truth):
        for mask in self.splits(n):
            self.paid["outer_xor_screens"]+=1;outer=self.probe(n,truth,mask,"XOR")
            if outer is None:self.paid["outer_xor_failures"]+=1;continue
            for inner,c in ((outer["a"],outer["b"]),(outer["b"],outer["a"])):
                if len(inner[2])<2:continue
                self.paid["ternary_placements_considered"]+=1;self.paid["inner_and_screens"]+=1
                cert=self.root(len(inner[2]),inner[0])
                if cert is None or cert["op"]!="AND":
                    self.paid["inner_and_failures"]+=1;self.paid["root_kind_prunes"]+=cert is not None
                    self.event("inner_prune",inputs=n,inner_inputs=len(inner[2]),root=None if cert is None else cert["op"]);continue
                a,b=cert["a"],cert["b"]
                a_pos=tuple(inner[2][j] for j in a[2]);b_pos=tuple(inner[2][j] for j in b[2])
                a_mask=sum(1<<j for j in a_pos);b_mask=sum(1<<j for j in b_pos)
                aa,bb=self.lift(n,a_mask,a[0]),self.lift(n,b_mask,b[0])
                self.paid["ternary_placement_tests"]+=1;composed=(aa&bb)^c[1]
                if self.arm=="named":self.paid["ternary_named_packed_NANDs"]+=7
                else:self.paid.update(ternary_flat_AND_ops=1,ternary_flat_XOR_ops=1)
                self.paid["ternary_comparison_rows_equivalent"]+=1<<n
                if composed!=truth:self.paid["ternary_placement_failures"]+=1;continue
                self.paid["ternary_placement_passes"]+=1
                self.event("ternary",inputs=n,groups=[a_mask,b_mask,sum(1<<j for j in c[2])])
                children=[self.search(len(z[2]),z[0]) for z in (a,b,c)]
                if any(child is None for child in children):continue
                args=[self.remap(children[0][0],a_pos),self.remap(children[1][0],b_pos),self.remap(children[2][0],c[2])]
                expr=("FOLD",*args) if self.arm=="named" else ("XOR",("AND",args[0],args[1]),args[2])
                self.paid["AST_nodes_built"]+=1 if self.arm=="named" else 2
                return expr,1+sum(child[1] for child in children)
        return None

    def search(self,n,truth):
        self.paid["subproblem_requests"]+=1;key=(n,truth)
        if key in self.solutions:self.paid["successful_subproblem_cache_hits"]+=1;return self.solutions[key]
        if key in self.failures:self.paid["failed_subproblem_cache_hits"]+=1;return None
        result=None
        if truth in (0,full(n)):result=(("const",int(bool(truth))),0)
        elif n==1 and truth==2:result=(("input",0),0)
        elif n>=2 and not(truth&1):
            root=self.root(n,truth)
            if root is not None:
                if self.arm!="primitive":
                    if root["op"]=="XOR":result=self.template(n,truth)
                    else:self.paid["root_kind_prunes"]+=1
                if result is None:result=self.join_binary(n,truth,root)
                if result is None:
                    for mask in self.splits(n):
                        if mask==root["group"]:continue
                        cert=self.probe(n,truth,mask,root["op"])
                        if cert is not None:
                            result=self.join_binary(n,truth,cert)
                            if result is not None:break
        if result is None:self.failures.add(key);self.paid["failed_subproblems_cached"]+=1
        else:
            if truth in (0,full(n)) or (n==1 and truth==2):self.paid["AST_nodes_built"]+=1
            self.solutions[key]=result;self.paid["successful_subproblems_cached"]+=1
        return result

    def cache_sizes(self):
        return dict(layout_tables=len(self.layouts),factor_sections=len(self.factors),binary_probe_results=len(self.probes),
                    root_certificates=len(self.roots),successful_subproblems=len(self.solutions),failed_subproblems=len(self.failures),
                    AST_layouts=len(self.remaps),physical_programs=len(self.programs))

    def run(self,truth):
        before=self.paid.copy();cache_before=self.cache_sizes();self.events=[];self.dropped=0;n=self.n;positions=[]
        self.paid["input_rows_received"]+=1<<n
        for j in range(n):
            self.layout(n,1<<j)
            if any((truth>>x&1)!=(truth>>(x^(1<<j))&1) for x in range(1<<n)):positions.append(j)
            self.paid["support_variable_probes"]+=1;self.paid["support_packed_bit_ops"]+=3
        mask=sum(1<<j for j in positions);positions=tuple(positions)
        _,assignments,_=self.layout(n,mask)
        compact=sum((truth>>x&1)<<i for i,x in enumerate(assignments))
        self.paid["support_remap_calls"]+=1;self.paid["support_remap_truth_bit_reads"]+=len(assignments)
        solved=self.search(len(positions),compact);expr=None if solved is None else self.remap(solved[0],positions)
        compiled=None;hit=False
        if expr is not None:
            self.paid["physical_compile_requests"]+=1;hit=expr in self.programs
            if hit:self.paid["physical_compile_cache_hits"]+=1;compiled=self.programs[expr]
            else:
                compiled,calls,ops=expand(expr,n)
                compiled.update(constants={"zero":n,"one":n+1},nand_gates=len(compiled["gates"]),macro_uses=calls,
                                underlying_ops={op:ops[op] for op in ("AND","OR","XOR")})
                self.programs[expr]=compiled
                self.paid.update(physical_programs_compiled=1,physical_NANDs_compiled=len(compiled["gates"]),physical_macro_calls_compiled=calls)
            self.paid.update(verification_packed_NANDs=len(compiled["gates"]),verification_scalar_equivalent_NANDs=len(compiled["gates"])*(1<<n),
                             verification_rows=1<<n,verification_comparisons=1,verification_input_bit_reads=n*(1<<n))
        keys=set(before)|set(self.paid)
        return dict(expr=expr,circuit=compiled,work={k:self.paid[k]-before[k] for k in keys},input_support=list(positions),
                    template_uses=0 if solved is None else solved[1],cache_before=cache_before,cache_after=self.cache_sizes(),
                    physical_compile_cache_hit=hit,trace=list(self.events),trace_dropped=self.dropped)


class ReplayPeel(ReplaySolver):
    """Independent simultaneous four-section and singleton recognition."""
    def __init__(self,n,arm):
        super().__init__(n,arm);self.pair_layouts=set();self.pair_sections={}

    def pair_sections_at(self,n,truth,variable):
        self.paid["peel_cofactor_requests"]+=1;key=(n,truth,variable)
        if key in self.pair_sections:
            self.paid["peel_cofactor_hits"]+=1;return self.pair_sections[key]
        self.paid["peel_cofactor_misses"]+=1
        if (n,variable) not in self.pair_layouts:
            self.pair_layouts.add((n,variable));self.paid["peel_index_tables_built"]+=1
            self.paid["peel_index_row_pairs"]+=1<<(n-1)
        positions=tuple(j for j in range(n) if j!=variable)
        answers=tuple(sum((truth>>(scatter(raw,positions)|(value<<variable))&1)<<raw for raw in range(1<<(n-1))) for value in (0,1))
        self.paid["peel_cofactor_bit_reads"]+=1<<n;self.paid["factor_truth_bit_reads"]+=1<<n
        self.pair_sections[key]=answers;return answers

    def joint(self,n,truth,singletons):
        f=full(n-2)
        for x,y in combinations(range(n),2):
            self.paid["peel_pair_probes"]+=1
            at_both=truth>>((1<<x)|(1<<y))&1
            self.paid["peel_witness_bit_reads"]+=1;self.paid["factor_truth_bit_reads"]+=1
            eligible={(0,0,1):0,(0,1,1):1,(1,0,1):2}.get((singletons[x],singletons[y],at_both),-1)
            for role in range(3):
                self.paid["peel_role_probes"]+=1;self.paid["ternary_placement_tests"]+=1
                if role!=eligible:
                    self.paid["peel_role_witness_rejections"]+=1;self.paid["ternary_placement_failures"]+=1;continue
                self.paid["peel_role_column_checks"]+=1
                low,high=self.pair_sections_at(n,truth,x)
                c00,c01=self.pair_sections_at(n-1,low,y-1);c10,c11=self.pair_sections_at(n-1,high,y-1)
                if role==0:residual=c00;matches=c10==c01==c00 and c11==(f^c00)
                elif role==1:residual=c10;matches=c00==0 and c01==f and c11==(f^c10)
                else:residual=c01;matches=c00==0 and c10==f and c11==(f^c01)
                if not matches:self.paid["ternary_placement_failures"]+=1;continue
                self.paid["ternary_placement_passes"]+=1
                self.event("direct_pair",inputs=n,x=x,y=y,role=role)
                child=self.search(n-2,residual)
                if child is None:self.paid["peel_child_failures"]+=1;continue
                positions=tuple(j for j in range(n) if j not in (x,y));h=self.remap(child[0],positions)
                left,right=("input",x),("input",y)
                args=(left,right,h) if role==0 else (left,h,right) if role==1 else (right,h,left)
                expr=("FOLD",*args) if self.arm=="named" else ("XOR",("AND",args[0],args[1]),args[2])
                self.paid["AST_nodes_built"]+=3 if self.arm=="named" else 4
                return expr,child[1]+1
        return None

    def single(self,n,truth,singletons):
        f=full(n-1)
        for variable in range(n):
            sections=None
            for op in ("AND","OR","XOR"):
                self.paid["peel_single_op_probes"]+=1;self.paid["binary_placement_requests"]+=1;self.paid["binary_placement_trials"]+=1
                if singletons[variable]!=int(op!="AND"):
                    self.paid["peel_single_witness_rejections"]+=1;self.paid["binary_placement_failures"]+=1;continue
                self.paid["peel_single_column_checks"]+=1
                if sections is None:sections=self.pair_sections_at(n,truth,variable)
                low,high=sections
                if op=="AND":matches=low==0;residual=high
                elif op=="OR":matches=high==f;residual=low
                else:matches=high==(f^low);residual=low
                if not matches:self.paid["binary_placement_failures"]+=1;continue
                self.paid["binary_placement_passes"]+=1
                child=self.search(n-1,residual)
                if child is None:self.paid["peel_child_failures"]+=1;continue
                self.event("direct_single",inputs=n,variable=variable,op=op)
                positions=tuple(j for j in range(n) if j!=variable);self.paid["AST_nodes_built"]+=2
                return (op,("input",variable),self.remap(child[0],positions)),child[1]
        return None

    def search(self,n,truth):
        key=(n,truth)
        if key in self.solutions or key in self.failures or n<2 or truth in (0,full(n)) or truth&1:
            return super().search(n,truth)
        self.paid["subproblem_requests"]+=1
        singletons=tuple(truth>>(1<<j)&1 for j in range(n))
        self.paid["peel_witness_bit_reads"]+=n;self.paid["factor_truth_bit_reads"]+=n
        result=self.joint(n,truth,singletons) if self.arm!="primitive" and n>=3 else None
        if result is None:result=self.single(n,truth,singletons)
        if result is None:
            self.paid["peel_general_fallbacks"]+=1
            for mask in self.splits(n):
                if mask.bit_count()==1:continue
                for op in ("AND","OR","XOR"):
                    cert=self.probe(n,truth,mask,op)
                    if cert is not None:
                        result=self.join_binary(n,truth,cert)
                        if result is not None:break
                if result is not None:break
        if result is None:self.failures.add(key);self.paid["failed_subproblems_cached"]+=1
        else:self.solutions[key]=result;self.paid["successful_subproblems_cached"]+=1
        return result

    def cache_sizes(self):
        return {**super().cache_sizes(),"peel_cofactor_layouts":len(self.pair_layouts),"peel_cofactor_pairs":len(self.pair_sections)}


def self_test():
    f=["FOLD",["input",0],["input",1],["input",2]]
    truth=source_truth(f,3);require(truth==120,"Saved DAG raw truth differs")
    circuit,uses,_=expand(f,3)
    require(uses==1 and len(circuit["gates"])==7 and circuit_truth(circuit,3)==truth,"Literal saved-DAG fixture failed")
    inline=["XOR",["AND",["input",0],["input",1]],["input",2]]
    simple,_,_=expand(inline,3)
    require(len(simple["gates"])==6 and circuit_truth(simple,3)==truth,"Inline primitive control failed")
    branch=["FOLD",["FOLD",0,1,2],["FOLD",3,4,5],6]
    branched_truth=source_truth(branch,7)
    require(f_tree_cover(branched_truth,7) and not chain_classes(branched_truth,7),"Chain/tree distinction fixture failed")
    serial=["FOLD",["FOLD",0,1,2],3,4]
    require(F_CLASS in chain_classes(source_truth(serial,5),5),"Serial positive fixture failed")
    xor=source_truth(["XOR",0,1],2)
    require(factor_witness(xor,2,(0,),"XOR")== (2,2),"Exact XOR factor fixture failed")
    require(factor_witness(xor,2,(0,),"AND") is None,"A failing factor test was accepted")
    corrupt=json.loads(json.dumps(circuit));corrupt["gates"][0]=[900,0]
    try:circuit_truth(corrupt,3)
    except AuditError:pass
    else:raise AuditError("Future-address mutation accepted")
    changed=json.loads(json.dumps(circuit));changed["gates"][-1]=[3,3]
    require(circuit_truth(changed,3)!=truth,"Wrong-gate semantic mutation undetected")
    replay=ReplaySolver(3,"named");first=replay.run(truth);second=replay.run(truth)
    require(first["template_uses"]==1 and first["work"].get("binary_placement_failures",0)>0,"Placement/failure fixture did not exercise search")
    require(second["work"].get("binary_placement_trials",0)==0 and second["work"].get("ternary_placement_tests",0)==0,
            "Successful subproblem memo failed")
    majority=sum((raw.bit_count()>=2)<<raw for raw in range(8))
    rejected=ReplaySolver(3,"primitive");bad=rejected.run(majority);again=rejected.run(majority)
    require(bad["expr"] is None and bad["work"]["binary_placement_trials"]==9,"Failed split accounting fixture failed")
    require(again["work"].get("binary_placement_trials",0)==0 and again["work"]["failed_subproblem_cache_hits"]==1,"Failed cache reuse was charged as a new placement")
    return {"status":"pass","raw_saved_truth":120,"source_NANDs":7,"inline_NANDs":6,
            "branched_F_tree_not_chain":True,"factor_positive_and_negative":True,"physical_mutations_rejected":True,
            "successful_and_failed_cache_reuse":True,"all_nine_failed_majority_trials_charged":True}


def check_result(actual,expected,target,n,arm):
    role=arm.removeprefix("peel-")
    require(actual["arm"]==role and actual["n"]==n,"Returned method/input identity differs")
    require(actual["input_support"]==expected["input_support"],"Input-support compression differs")
    require(frozen(actual["expr"])==expected["expr"],"Public schedule returns a different physical expression")
    for key in ("cache_before","cache_after","trace","trace_dropped","physical_compile_cache_hit","template_uses"):
        require(actual[key]==expected[key],f"Cache/schedule replay differs: {key}")
    for key,value in actual["work"].items():
        require(type(value) is int and value>=0,"Work count is not a nonnegative integer")
        require(value==expected["work"].get(key,0),f"Executed logical work differs: {key}: {value} vs {expected['work'].get(key,0)}")
    require(all(value==actual["work"].get(key,0) for key,value in expected["work"].items()),"Expected work omitted from receipt")
    if expected["circuit"] is None:
        require(actual["status"]=="unsupported" and actual["circuit"] is None and actual["truth"] is None,"Unsupported target was silently repaired")
        require(actual["expanded_NANDs"] is None and actual["macro_uses"]==0,"Failed solve was given a physical return")
        return False
    require(actual["status"]=="exact" and actual["truth"]==target,"Successful solve declares wrong truth")
    require(actual["circuit"]==expected["circuit"],"Physical operands differ from independently expanded submitted expression")
    require(actual["macro_uses"]==expected["circuit"]["macro_uses"] and actual["expanded_NANDs"]==len(actual["circuit"]["gates"]),"Physical call/gate accounting differs")
    require(circuit_truth(actual["circuit"],n)==source_truth(actual["expr"],n)==target,"Literal all-input circuit/AST replay fails")
    require(actual["fold_dag"]==(SAVED_FOLD if role=="named" else None),"Named binding/inline separation differs")
    return True


def producer_fixtures():
    """Optional known-input generation; never reads the scientific panels."""
    path=ROOT/"experiments"/TICKET/FAMILY/"solver.py"
    spec=importlib.util.spec_from_file_location("solver",path)
    producer=importlib.util.module_from_spec(spec);sys.modules["solver"]=producer;spec.loader.exec_module(producer)
    spec2=importlib.util.spec_from_file_location("fold_depth_hand_peeler",path.with_name("peel.py"))
    peeler=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(peeler)
    samples=[(2,source_truth(["XOR",0,1],2)),(3,120),(3,source_truth(["FOLD",0,2,1],3)),(3,source_truth(["FOLD",1,2,0],3)),
             (4,source_truth(["OR",["FOLD",0,1,2],3],4)),(4,source_truth(["XOR",0,2],4)),
             (3,sum((raw.bit_count()>=2)<<raw for raw in range(8)))]
    comparisons=0
    for n,target in samples:
        for arm in ARMS:
            role=arm.removeprefix("peel-");paired=arm.startswith("peel-")
            actual_engine=(peeler.PeelSolver if paired else producer.Solver)(n,role,SAVED_FOLD if role=="named" else None)
            independent=(ReplayPeel if paired else ReplaySolver)(n,role)
            for repeat in range(2):
                actual=actual_engine.solve(target);expected=independent.run(target)
                check_result(actual,expected,target,n,arm);comparisons+=1
                if n==3 and target!=120 and repeat==0:
                    corrupted=json.loads(json.dumps(actual));corrupted["work"]["binary_placement_trials"]-=1
                    try:check_result(corrupted,expected,target,n,arm)
                    except AuditError:pass
                    else:raise AuditError("Omitting a failed placement escaped accounting check")
    return {"status":"pass","producer_source_sha256":file_digest(path),"hand_comparisons":comparisons,
            "panel_imports_or_runs":0,"omitted_failed_trial_rejected":True}


def metrics(receipt,target):
    r=receipt["result"];w=r["work"];t=r["timing"]
    return dict(exact=int(r.get("truth")==target and r.get("circuit") is not None),
                tests=w["binary_placement_trials"]+w["ternary_placement_tests"],binary=w["binary_placement_trials"],
                compound=w["ternary_placement_tests"],reads=w["factor_truth_bit_reads"],uses=r.get("template_uses",0),
                nands=r.get("expanded_NANDs") or 0,search_cpu_ns=t["search_cpu_ns"],
                search_wall_ns=round(t["search_seconds"]*1e9),build_ns=round(t["build_seconds"]*1e9),
                verify_ns=round(t["verification_seconds"]*1e9),reported_wall_ns=receipt["wall_ns"],
                total_cpu_ns=receipt["cpu_ns"],setup_ns=receipt["setup_wall_ns"])


def totals(mappings):
    result=Counter()
    for mapping in mappings:result.update(mapping)
    return dict(result)


def normalized(value):
    return json.loads(json.dumps(value))


def aggregate(streams,public,grading):
    measures={key:{ident:metrics(row,public[ident]["truth"]) for ident,row in rows.items()} for key,rows in streams.items()}
    tables={}
    for split,grade in grading.items():
        tables[split]={}
        for cache,repeats in (("cold",5),("warm",1)):
            cells={}
            for depth in (2,3,4):
                for kind in ("negative","positive"):
                    ids=[ident for ident,meta in grade.items() if meta["depth"]==depth and meta["kind"]==kind]
                    require(ids,"Missing depth/control stratum")
                    cell=dict(n_tasks=len(ids),depth=depth,kind=kind)
                    for arm in ARMS:
                        runs=[totals(measures[cache,arm,repeat][i] for i in ids) for repeat in range(repeats)]
                        value={key:statistics.median(row[key] for row in runs) for key in runs[0]}
                        value["search_cpu_repeats"]=[row["search_cpu_ns"] for row in runs]
                        base=streams[cache,arm,0]
                        value["work_totals"]=totals(base[i]["result"]["work"] for i in ids)
                        value["fold_use_distribution"]=dict(Counter(base[i]["result"].get("template_uses",0) for i in ids))
                        value["status_counts"]=dict(Counter(base[i]["result"]["status"] for i in ids))
                        cell[arm]=value
                    for route,prefix in (("factor",""),("pair","peel-")):
                        plain,named=prefix+"primitive",prefix+"named";saving={}
                        for metric in ("tests","reads","search_cpu_ns","reported_wall_ns"):
                            base,new=cell[plain][metric],cell[named][metric]
                            gaps=[statistics.median(measures[cache,plain,r][i][metric] for r in range(repeats))-
                                  statistics.median(measures[cache,named,r][i][metric] for r in range(repeats)) for i in ids]
                            saving[metric]=dict(per_task=(base-new)/len(ids),fraction=(base-new)/base if base else 0,
                                                n_positive=sum(x>0 for x in gaps),n_equal=sum(x==0 for x in gaps),n_negative=sum(x<0 for x in gaps))
                        cell[route+"_savings"]=saving
                    cells[f"{depth}-{kind}"]=cell
            tables[split][cache]=cells
    success=all(row["exact"] for rows in measures.values() for row in rows.values())
    gate=dict(all_exact=success,strategies={})
    for route in ("factor","pair"):
        cells=[tables["primary"]["cold"][f"{d}-positive"] for d in (2,3,4)]
        def passes(metric):
            shallow,deep=(cells[j][route+"_savings"][metric] for j in (0,2))
            return deep["per_task"]>shallow["per_task"] and deep["fraction"]>=0.10 and deep["n_positive"]>cells[2]["n_tasks"]/2
        reads=[cell[route+"_savings"]["reads"]["per_task"] for cell in cells]
        gate["strategies"][route]=dict(work_criterion=passes("tests"),time_and_row_criterion=passes("search_cpu_ns") and reads[2]>0 and reads[2]>reads[0])
    gate["discover"]=success and any(flag for entry in gate["strategies"].values() for flag in entry.values())
    whole={}
    for cache,repeats in (("cold",5),("warm",1)):
        whole[cache]={}
        for arm in ARMS:
            rows=[totals(measures[cache,arm,rep].values()) for rep in range(repeats)]
            entry={key:statistics.median(row[key] for row in rows) for key in rows[0]}
            entry["work_totals"]=totals(row["result"]["work"] for row in streams[cache,arm,0].values())
            entry["setup_work_totals"]=totals(row["setup_work"] for row in streams[cache,arm,0].values())
            whole[cache][arm]=entry
    return normalized(dict(unique_tasks=len(public),exact_possible_rule_input_pairs=sum(1<<p["n"] for p in public.values()),
                           timed_rule_runs=sum(map(len,measures.values())),failed_logical_runs=sum(1-row["exact"] for rows in measures.values() for row in rows.values()),
                           gate=gate,tables=tables,whole_panel=whole))


def audit(out):
    start=time.perf_counter();bound=get(out/"freeze.json")
    require(bound["tasks"]==60,"Wrong frozen task count")
    for relative,sha in bound["sources"].items():require(file_digest(ROOT/relative)==sha,f"Changed scientific source: {relative}")
    for name,sha in bound["inputs"].items():require(file_digest(out/name)==sha,f"Changed bound input: {name}")
    require(get(out/"fold.json")==SAVED_FOLD,"Saved original DAG was replaced")
    public_rows=get(out/"public.json");grading=get(out/"grading.json")
    panel=audit_panel(public_rows,grading);public={row["id"]:row for row in public_rows}
    previous_path=ROOT/"artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/panel.json"
    previous={(r["n"],r["truth"]) for r in get(previous_path)}
    require(not previous.intersection((r["n"],r["truth"]) for r in public_rows),"An archived target was repeated")
    print("Independent task controls passed, including arbitrary-tree F negatives; checking frozen streams.",flush=True)
    raw=[json.loads(line) for line in (out/"results.jsonl").read_text().splitlines()]
    expected_cases=[f"cold-{rep}-{arm}" for rep in range(5) for arm in ARMS[rep%6:]+ARMS[:rep%6]]+[f"warm-0-{arm}" for arm in ARMS]
    require(len(raw)==36 and [r["case"] for r in raw]==expected_cases,"Missing, duplicate, or reordered official timing case")
    require(all(r["status"]=="ok" and r["attempt"]==1 for r in raw),"Runner failure/retry is missing from paid case accounting")
    require(len({r["worker"] for r in raw})==36,"Trials share worker processes")
    streams={};expected_cold={};total_physical_rows=0;total_scalar_NANDs=0;logical_failures=[];hashes={}
    for runner in raw:
        receipt=runner["result"];cache=receipt["cache"];arm=receipt["arm"];rep=receipt["repeat"]
        require(receipt["tasks"]==60 and receipt["file"]==runner["case"]+".jsonl.gz","Stream identity mismatch")
        require(runner["job_sha"]==bound["sources"][str((ROOT/"experiments"/TICKET/FAMILY/"job.py").relative_to(ROOT))],"Unbound job source ran")
        require(datetime.fromisoformat(runner["finished_at"])>=datetime.fromisoformat(bound["frozen_utc"].replace("Z","+00:00")),"A measured stream predates the bind")
        path=out/receipt["file"];require(file_digest(path)==receipt["sha256"],"Changed measured stream")
        hashes[receipt["file"]]=receipt["sha256"]
        with gzip.open(path,"rt") as source:rows=[json.loads(line) for line in source]
        require(len(rows)==60 and [row["id"] for row in rows]==list(public),"Missing, reordered or duplicate task in stream")
        engines={};by_id={};role=arm.removeprefix("peel-");engine_type=ReplayPeel if arm.startswith("peel-") else ReplaySolver
        for row in rows:
            ident=row["id"];task=public[ident];n=task["n"];target=task["truth"];actual=row["result"]
            require(row["n"]==n,"Receipt arity changed")
            fresh=cache=="cold" or n not in engines
            if fresh:engines[n]=engine_type(n,role)
            if cache=="cold" and rep>0:expected=expected_cold[arm,ident]
            else:
                expected=engines[n].run(target)
                if cache=="cold":expected_cold[arm,ident]=expected
            if actual["status"]=="error":
                raise AuditError(f"Runtime error preserved but full replay is inconclusive: {runner['case']}/{ident}: {actual.get('error')}")
            exact=check_result(actual,expected,target,n,arm)
            if not exact:logical_failures.append([runner["case"],ident])
            before=row["setup_work"]
            require(all(type(v) is int and v>=0 for v in before.values()),"Invalid paid setup work")
            if fresh:
                require(before.get("archive_validation_scalar_NANDs",0)==(56 if role=="named" else 0) and
                        before.get("archive_validation_input_bit_reads",0)==(24 if role=="named" else 0),"Supplied-DAG validation cost missing")
                require(all(v==0 for k,v in before.items() if k not in ("archive_validation_scalar_NANDs","archive_validation_input_bit_reads")),"Fresh setup includes unexplained prior search work")
            else:require(before=={},"Warm reused backend was charged as a new setup")
            require(row["return_bytes"]==(len(canonical(actual["circuit"])) if actual["circuit"] is not None else 0),"Physical return serialization charge differs")
            require(type(row["wall_ns"]) is int and row["wall_ns"]>row["setup_wall_ns"]>=0 and row["cpu_ns"]>0,"Invalid timing receipt")
            t=actual["timing"]
            require(all(value>=0 for value in t.values()),"Negative phase duration")
            phases=sum(t[name] for name in ("input_seconds","search_seconds","build_seconds","verification_seconds"))
            require(phases<=t["elapsed_seconds"]+1e-8 and t["elapsed_seconds"]*1e9<=row["wall_ns"],"Paid elapsed time omits a solve phase")
            require(t["search_cpu_ns"]<=row["cpu_ns"],"Search CPU exceeds total paid CPU")
            if exact:
                total_physical_rows+=1<<n;total_scalar_NANDs+=(1<<n)*actual["expanded_NANDs"]
            by_id[ident]=row
        require(receipt["stream_total_ns"]==sum(row["wall_ns"] for row in rows),"Stream total omits task setup/failure costs")
        require(receipt["stream_total_ns"]<=runner["seconds"]*1e9,"Paid task time exceeds entire runner time")
        streams[cache,arm,rep]=by_id
    print("All physical expressions, exhaustive raw inputs and executed work counters passed; checking quantitative summaries.",flush=True)
    semantic_keys=("binary_placement_trials","binary_placement_requests","binary_placement_cache_hits","binary_placement_failures","binary_placement_passes",
                   "factor_truth_bit_reads","factor_requests","factor_cache_hits","factor_sections_extracted","outer_xor_screens","inner_and_screens",
                   "ternary_placement_tests","ternary_placement_passes","ternary_placement_failures","subproblem_requests",
                   "successful_subproblem_cache_hits","failed_subproblem_cache_hits","peel_pair_probes","peel_role_probes","peel_single_op_probes")
    flat_pairs=0;multiuse=Counter();physical_penalty=0
    for cache,repeats in (("cold",5),("warm",1)):
        for rep in range(repeats):
            for prefix in ("","peel-"):
                for ident in public:
                    named=streams[cache,prefix+"named",rep][ident]["result"];flat=streams[cache,prefix+"flat",rep][ident]["result"]
                    require(all(named["work"].get(k,0)==flat["work"].get(k,0) for k in semantic_keys),"Named and equally informed inline arms used different semantic searches")
                    require(named["trace"]==flat["trace"] and named["template_uses"]==flat["template_uses"],"Named/flat placement trace differs")
                    require(named["macro_uses"]==named["template_uses"] and flat["macro_uses"]==0,"Printed template length replaced actual physical calls")
                    if named["circuit"] is not None:
                        require(named["expanded_NANDs"]-flat["expanded_NANDs"]==named["template_uses"],"Seven-vs-six physical expansion was silently optimized")
                        physical_penalty+=named["expanded_NANDs"]-flat["expanded_NANDs"]
                    flat_pairs+=1
                    if cache=="cold" and rep==0:multiuse[prefix+"named",named["macro_uses"]]+=1
    independently_aggregated=aggregate(streams,public,grading)
    require(independently_aggregated==get(out/"result.json"),"Final assessor output differs from independent full aggregation")
    trends={split:{cache:{f"{d}-{kind}":{key:cell[key] for key in ("n_tasks","factor_savings","pair_savings")}
                         for d in (2,3,4) for kind in ("positive","negative") for cell in [cells[f"{d}-{kind}"]]}
                   for cache,cells in caches.items()} for split,caches in independently_aggregated["tables"].items()}
    primary=independently_aggregated["tables"]["primary"]["cold"]
    gate=independently_aggregated["gate"]
    return {"study":TICKET,"verdict":"PASS","independence":"Independent scalar raw-input/AST/NAND evaluation, cofactor-matrix tests, full public schedule/counter replay and aggregation. No producer evaluator or task generator used in sealed replay.",
            "inputs":{"freeze.json":file_digest(out/"freeze.json"),"public.json":file_digest(out/"public.json"),"grading.json":file_digest(out/"grading.json"),
                      "fold.json":file_digest(out/"fold.json"),"results.jsonl":file_digest(out/"results.jsonl"),"result.json":file_digest(out/"result.json"),
                      "audit.py":file_digest(Path(__file__)),"bound_sources":bound["sources"]},
            "streams":hashes,"panel":panel,"all_exact":not logical_failures,"logical_failures":logical_failures,
            "replayed_rule_runs":len(raw)*len(public),"scalar_physical_input_rows":total_physical_rows,"scalar_NAND_evaluations":total_scalar_NANDs,
            "all_work_counters_reproduced":True,"named_inline_matched_cases":flat_pairs,
            "named_extra_physical_NANDs_over_inline":physical_penalty,
            "cold_first_repeat_named_use_counts":{arm:{str(count):v for (a,count),v in multiuse.items() if a==arm} for arm in ("named","peel-named")},
            "preregistered_gate":gate,"depth_trends":trends,"whole_panel":independently_aggregated["whole_panel"],
            "fixture_tests":self_test(),"interpretation":[
                "The particular free template and an equally informed inline library have identical semantic placements; naming adds no search benefit.",
                "The general factor-screened strategy and direct four-cofactor strategy must be reported separately.",
                "The screen compares depth4 against depth2; a depth3-to-depth4 reversal does not fail its registered endpoint condition and must remain visible.",
                "Primary depth covaries with arity; fixed-nine sensitivity separates that confound, and its depth4 cases are aliases rather than new observations.",
                "All targets are complete public truth tables. This stage tests synthesis with supplied knowledge, not fresh-label learning or library discovery.",
                "Named invocations physically retain all seven saved NANDs; inline uses six. Search savings do not imply cheaper returned execution.",
                "Source acquisition is explicitly free here. Setup, failures, search, build, exhaustive verification and return serialization are paid; experimental logging and independent audit are outside deployment timing.",
                "Arbitrary-gate negative certificates exclude homogeneous read-once chains; the separate particular-F check excludes arbitrary complete read-once F trees on primary negatives.",
                "Finite pilot timing and its permissive two-strategy screen justify a separate frozen discovery test only; no general complexity advantage follows."],
            "audit_elapsed_s":time.perf_counter()-start,"completed_utc":datetime.now(timezone.utc).isoformat()}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--audit",action="store_true",help="consume sealed receipts only after lead authorization")
    parser.add_argument("--producer-fixtures",action="store_true",help="compare producer only on hand inputs")
    parser.add_argument("--artifacts",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args()
    if args.audit:
        result=audit(args.artifacts)
        (args.artifacts/"audit.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps({"verdict":result["verdict"],"gate":result["preregistered_gate"],"rule_runs":result["replayed_rule_runs"],
                          "raw_input_replays":result["scalar_physical_input_rows"],"audit":str(args.artifacts/"audit.json")},indent=2))
    else:
        print(json.dumps(producer_fixtures() if args.producer_fixtures else self_test(),sort_keys=True))
