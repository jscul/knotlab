"""Independent physical-program and charged-search audit of fold reuse.

Source acquisition, cached hypotheses, sparse-label fitting and target
verification are distinct charges. No producer evaluator or fitter is used.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from itertools import permutations
from datetime import datetime
import math
import statistics
import random


TICKET = "FOLD-REUSE-20261115-001"
FAMILY = TICKET + "-E001_second_learner"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "artifacts" / TICKET / FAMILY
METHODS = ("first_plain","first_fold","median_plain","median_fold")


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bit(value):
    require(type(value) is int and value in (0, 1), "Expected an actual Boolean bit")
    return value


def dag_value(dag, args, actions=None):
    data = [bit(value) for value in args] + [0, 1]
    constant_base = len(args)
    require(isinstance(dag, dict) and set(dag) == {"gates", "output"}, "Malformed literal NAND DAG")
    for gate in dag["gates"]:
        require(len(gate) == 2 and all(type(i) is int and 0 <= i < len(data) for i in gate),
                "NAND instruction reads a future or invalid address")
        left, right = gate
        data.append(1 - data[left] * data[right])
        if actions is not None:
            actions["NAND"] += 1
            actions["CONST" if left in (constant_base,constant_base+1) else "READ"] += 1
            if left == right:
                actions["COPY"] += 1
            else:
                actions["CONST" if right in (constant_base,constant_base+1) else "READ"] += 1
            actions["WRITE"] += 1
    require(type(dag["output"]) is int and 0 <= dag["output"] < len(data), "Invalid NAND output tap")
    if actions is not None:
        actions["CONST" if dag["output"] in (constant_base,constant_base+1) else "READ"] += 1
    return data[dag["output"]]


def eval_ast(expr, raw, n, fold):
    require(isinstance(expr, (list,tuple)) and expr, "Malformed hypothesis AST")
    op = expr[0]
    if op == "input":
        require(len(expr) == 2 and type(expr[1]) is int and 0 <= expr[1] < n, "Input outside common domain")
        return raw >> expr[1] & 1
    if op == "FOLD":
        require(len(expr) == 4, "Fold requires three actual arguments")
        return dag_value(fold, [eval_ast(child,raw,n,fold) for child in expr[1:]])
    require(op in ("AND","OR","XOR") and len(expr) == 3, "Forbidden primitive or malformed AST")
    left,right = (eval_ast(child,raw,n,fold) for child in expr[1:])
    return left & right if op == "AND" else left | right if op == "OR" else left ^ right


def primitive_expressions():
    a,b = ("input",0),("input",1)
    not_a,not_b = ("NAND",a,a),("NAND",b,b)
    ab = ("NAND",a,b)
    return {"AND":("NAND",ab,ab), "OR":("NAND",not_a,not_b)}


def expand_ast(expr, n, fold):
    """Clone each literal primitive/fold implementation, without hidden CSE."""
    gates = []
    primitives = primitive_expressions()
    def primitive(node, args):
        if node[0] == "input":
            return args[node[1]]
        if node[0] == "const":
            return n + node[1]
        left = primitive(node[1],args)
        right = left if node[1] == node[2] else primitive(node[2],args)
        gates.append([left,right])
        return n + 1 + len(gates)
    def visit(node):
        op = node[0]
        if op == "input":
            require(len(node)==2 and type(node[1]) is int and 0 <= node[1] < n,"Invalid variable in physical expansion")
            return node[1]
        if op == "XOR":
            require(len(node)==3,"XOR arity differs")
            left,right=visit(node[1]),visit(node[2])
            def gate(a,b):
                gates.append([a,b])
                return n+1+len(gates)
            shared=gate(left,right)
            first,second=gate(left,shared),gate(right,shared)
            return gate(first,second)
        if op in primitives:
            require(len(node)==3,"Binary primitive arity differs")
            return primitive(primitives[op],[visit(node[1]),visit(node[2])])
        require(op=="FOLD" and len(node)==4,"Invalid saved-fold invocation")
        addresses = [visit(child) for child in node[1:]] + [n,n+1]
        for left,right in fold["gates"]:
            require(type(left) is int and type(right) is int and 0 <= min(left,right) and max(left,right)<len(addresses),
                    "Invalid saved DAG operand")
            gates.append([addresses[left],addresses[right]])
            addresses.append(n+1+len(gates))
        return addresses[fold["output"]]
    output = visit(expr)
    return {"gates":gates,"output":output}


def program_truth(expr, n, fold):
    physical = expand_ast(expr,n,fold)
    values = []
    for raw in range(1<<n):
        high = eval_ast(expr,raw,n,fold)
        actual = dag_value(physical,[raw>>j&1 for j in range(n)])
        require(high==actual,"Serialized AST differs from fully expanded actual NAND gates")
        values.append(actual)
    return sum(value<<raw for raw,value in enumerate(values)),len(physical["gates"])


def first_mismatch(expr, n, target, fold):
    """Descending public verifier; every visited program execution is charged."""
    physical = expand_ast(expr,n,fold)
    rows = gates = 0
    for raw in range((1<<n)-1,-1,-1):
        value = dag_value(physical,[raw>>j&1 for j in range(n)])
        rows += 1
        gates += len(physical["gates"])
        label = target >> raw & 1
        if value != label:
            return {"counterexample":[raw,label],"checked_rows":rows,"NAND":gates}
    return {"counterexample":None,"checked_rows":rows,"NAND":gates}


def tuple_tree(value):
    return tuple(tuple_tree(child) for child in value) if isinstance(value,list) else value


def ast_inventory(expr):
    if expr[0]=="input":
        return [expr[1]],0,Counter()
    leaves,macros,ops=[],0,Counter()
    for child in expr[1:]:
        part,uses,counts=ast_inventory(child)
        leaves.extend(part);macros+=uses;ops.update(counts)
    if expr[0]=="FOLD":
        macros+=1
    else:
        ops[expr[0]]+=1
    return leaves,macros,ops


class Catalogues:
    """Independent cold construction of the declared common syntax/order."""

    def __init__(self,fold):
        self.fold=fold
        self.base_entries={}
        self.syntax_work=Counter(base_syntax_generated=0,fold_syntax_generated=0)

    @staticmethod
    def splits(mask):
        low=mask&-mask
        left=(mask-1)&mask
        while left:
            right=mask^left
            if right and left&low:
                yield left,right
            left=(left-1)&mask

    @staticmethod
    def binary(op,a,b):
        return (op,a,b) if a<=b else (op,b,a)

    @lru_cache(None)
    def base_syntax(self,mask):
        if mask.bit_count()==1:
            result=(("input",mask.bit_length()-1),)
        else:
            result=tuple(sorted(self.binary(op,a,b) for left,right in self.splits(mask)
                                for a in self.base_syntax(left) for b in self.base_syntax(right)
                                for op in ("AND","OR","XOR")))
        self.syntax_work["base_syntax_generated"]+=len(result)
        return result

    @lru_cache(None)
    def fold_syntax(self,mask):
        if mask.bit_count()<3:
            return ()
        expressions=[]
        first=(mask-1)&mask
        while first:
            remaining=mask^first
            second=(remaining-1)&remaining
            while second:
                third=remaining^second
                if third:
                    expressions.extend(("FOLD",a,b,c) for a in self.base_syntax(first)
                                       for b in self.base_syntax(second) for c in self.base_syntax(third))
                second=(second-1)&remaining
            first=(first-1)&mask
        for left,right in self.splits(mask):
            for a in self.fold_syntax(left):
                for b in self.base_syntax(right):
                    expressions.extend(self.binary(op,a,b) for op in ("AND","OR","XOR"))
            for a in self.base_syntax(left):
                for b in self.fold_syntax(right):
                    expressions.extend(self.binary(op,a,b) for op in ("AND","OR","XOR"))
        result=tuple(sorted(expressions))
        self.syntax_work["fold_syntax_generated"]+=len(result)
        return result

    def snapshot(self):
        return {**self.syntax_work,"base_syntax_hits":self.base_syntax.cache_info().hits,
                "base_syntax_misses":self.base_syntax.cache_info().misses,
                "fold_syntax_hits":self.fold_syntax.cache_info().hits,"fold_syntax_misses":self.fold_syntax.cache_info().misses}

    def entries(self,n,syntax,fold,work):
        work["input_columns_built"]+=n
        work["input_column_bit_reads"]+=n*(1<<n)
        result=[]
        for expr in syntax:
            truth,gates=program_truth(expr,n,fold)
            leaves,uses,ops=ast_inventory(expr)
            require(sorted(leaves)==list(range(n)),"Candidate violates the common read-once essential-input grammar")
            work.update(hypothesis_programs_compiled=1,compiled_NANDs=gates,public_packed_NANDs=gates,
                        public_scalar_equivalent_NANDs=gates*(1<<n))
            result.append({"truth":truth,"expr":expr,"macro_uses":uses,"search_operations":sum(ops.values())+uses,
                           "expanded_NANDs":gates,"underlying_ops":{op:ops[op] for op in ("AND","OR","XOR")}})
        return result

    def base(self,n,work):
        if n not in self.base_entries:
            self.base_entries[n]=self.entries(n,self.base_syntax((1<<n)-1),None,work)
            work["base_raw_cache_misses"]+=1
        else:
            work["base_raw_cache_hits"]+=1
        return self.base_entries[n]

    def build(self,n):
        before=self.snapshot()
        work=Counter({key:0 for key in ("hypothesis_programs_compiled","compiled_NANDs","public_packed_NANDs",
                     "public_scalar_equivalent_NANDs","input_columns_built","input_column_bit_reads","base_raw_cache_hits",
                     "base_raw_cache_misses","base_index_attempts","fold_index_attempts","base_duplicates_rejected",
                     "fold_duplicates_rejected","base_retained","fold_retained")})
        base=self.base(n,work)
        prefix=[]
        if self.fold is not None:
            base3=self.base(3,work)
            truth,gates=program_truth(("FOLD",("input",0),("input",1),("input",2)),3,self.fold)
            require(truth in {row["truth"] for row in base3},"Fold enlarged the primitive hypothesis class")
            work.update(input_columns_built=3,input_column_bit_reads=24,hypothesis_programs_compiled=1,
                        compiled_NANDs=gates,public_packed_NANDs=gates,public_scalar_equivalent_NANDs=8*gates)
            prefix=self.entries(n,self.fold_syntax((1<<n)-1),self.fold,work)
        retained,seen,generation=[],set(),0
        for origin,entries in (("fold",prefix),("base",base)):
            for row in entries:
                work[f"{origin}_index_attempts"]+=1
                if row["truth"] in seen:
                    work[f"{origin}_duplicates_rejected"]+=1
                else:
                    seen.add(row["truth"])
                    retained.append(row|{"origin":origin,"generation_index":generation})
                    work[f"{origin}_retained"]+=1
                generation+=1
        require(seen=={row["truth"] for row in base},"Inherited semantic hypothesis set differs")
        after=self.snapshot()
        construction={"catalogue_cache_hit":False,**work,**{k:after[k]-before[k] for k in before},
                      "return_index_entries_copied":len(retained)}
        spans={}
        def fold_span(node):
            if node[0]=="input":
                return ()
            if node[0]=="FOLD":
                return (len(ast_inventory(node)[0]),)
            return sum((fold_span(child) for child in node[1:]),())
        for row in prefix:
            spans.setdefault(row["truth"],set()).update(fold_span(row["expr"]))
        return {"n":n,"candidates":retained,"construction":construction,"fold_spans":spans}


def equality(actual,expected,label):
    require(canonical(actual)==canonical(expected),"Independent mismatch: "+label)


def proposal(candidate,index,round_index=None,consistent=None):
    keys=("expr","origin","macro_uses","expanded_NANDs")
    result={key:candidate[key] for key in keys}
    result["candidate_index"]=index
    if round_index is not None:
        result.update(round=round_index,generation_index=candidate["generation_index"],
                      search_operations=candidate["search_operations"],underlying_ops=candidate["underlying_ops"])
    if consistent is not None:
        result["consistent_before"]=consistent
    return result


def first_fit(catalog,examples,target,fold):
    n=catalog["n"]
    evidence=[list(row) for row in examples]
    proposals,attempts,feedback,added=[],[],[],[]
    inspected=tests=0
    for index,candidate in enumerate(catalog["candidates"]):
        inspected+=1
        accepted=True
        for x,label in evidence:
            tests+=1
            if candidate["truth"]>>x&1 != label:
                accepted=False
                break
        if not accepted:
            continue
        row=proposal(candidate,index,len(proposals)+1)
        proposals.append(row)
        checked=first_mismatch(candidate["expr"],n,target,fold)
        attempts.append({"expr":candidate["expr"],"physical_gates":candidate["expanded_NANDs"],
                         "rows":checked["checked_rows"],"nand_evaluations":checked["NAND"],"counterexample":checked["counterexample"]})
        if checked["counterexample"] is None:
            feedback.append({"round":len(proposals),"candidate_index":index,"exact":True})
            break
        x,label=checked["counterexample"]
        require(x not in {p[0] for p in evidence},"Verifier repeated a satisfied label")
        event={"round":len(proposals),"candidate_index":index,"x":x,"label":label}
        added.append(event);feedback.append(event|{"exact":False});evidence.append([x,label])
    else:
        raise AuditError("No exact candidate in the declared primitive class")
    final=catalog["candidates"][index]
    return {"schema_version":1,"status":"exact","n":n,"initial_proposal":proposals[0],"proposals":proposals,
            "hypotheses_inspected":inspected,"consistency_label_tests":tests,"checker_calls":len(proposals),
            "checker_failures":len(added),"checker_feedback":feedback,"added_evidence":added,
            "initial_input_example_count":len(examples),"initial_examples":examples,"final_examples":evidence,
            "final_candidate_index":index,"final_expr":final["expr"],"final_origin":final["origin"],
            "final_macro_uses":final["macro_uses"],"final_search_operations":final["search_operations"],
            "final_expanded_NANDs":final["expanded_NANDs"]},attempts


def median_fit(catalog,examples,target,fold):
    eligible=[(c["truth"],i) for i,c in enumerate(catalog["candidates"])
              if all(c["truth"]>>x&1==label for x,label in examples)]
    eligible.sort()
    values=[v for v,_ in eligible]
    lo,hi=0,len(eligible)
    proposals,attempts,evidence=[],[],[]
    comparisons=0
    def lower(start,end,key):
        nonlocal comparisons
        while start<end:
            comparisons+=1
            mid=(start+end)//2
            if values[mid]<key:
                start=mid+1
            else:
                end=mid
        return start
    while lo<hi:
        before=hi-lo
        middle=(lo+hi-1)//2
        _,index=eligible[middle]
        candidate=catalog["candidates"][index]
        proposals.append(proposal(candidate,index,consistent=before))
        checked=first_mismatch(candidate["expr"],catalog["n"],target,fold)
        attempts.append({"expr":candidate["expr"],"physical_gates":candidate["expanded_NANDs"],
                         "rows":checked["checked_rows"],"nand_evaluations":checked["NAND"],"counterexample":checked["counterexample"]})
        if checked["counterexample"] is None:
            return {"status":"exact","initial_proposal":dict(proposals[0]),"final_expr":candidate["expr"],
                    "proposals":proposals,"added_evidence":evidence,"hypotheses_inspected":len(proposals),
                    "order_comparisons":comparisons,"checker_calls":len(proposals),"checker_failures":len(evidence),
                    "final_macro_uses":candidate["macro_uses"],"final_expanded_NANDs":candidate["expanded_NANDs"]},attempts
        x,label=checked["counterexample"]
        prefix=(values[middle]>>(x+1)<<(x+1))|(label<<x)
        newlo=lower(lo,hi,prefix)
        newhi=lower(newlo,hi,prefix+(1<<x))
        require(0<newhi-newlo<before,"Median failure did not narrow the public version space")
        # Every inferred higher target bit is already checked, not an oracle query.
        for raw in range(x+1,1<<catalog["n"]):
            require((candidate["truth"]>>raw&1)==(target>>raw&1),"Median used an unverified prefix bit")
        evidence.append({"round":len(proposals),"candidate_index":index,"x":x,"label":label})
        lo,hi=newlo,newhi
    raise AuditError("Median selector lost the target")


def primitive_witness(tree):
    if type(tree) is int:
        return ("input",tree)
    require(len(tree)==3 and tree[0] in ("AND","OR","XOR"),"Invalid concealed target witness")
    return (tree[0],primitive_witness(tree[1]),primitive_witness(tree[2]))


def permutation_classes(functions,n):
    maps=[tuple(sum((raw>>new&1)<<old for old,new in enumerate(order)) for raw in range(1<<n))
          for order in permutations(range(n))]
    by_truth,classes={},{}
    for truth in sorted(functions):
        if truth in by_truth:
            continue
        members={sum((truth>>old&1)<<new for new,old in enumerate(mapping)) for mapping in maps}
        require(members<=functions,"Hypothesis class is not closed under raw-variable renaming")
        key=min(members)
        classes[key]=sorted(members)
        by_truth.update(dict.fromkeys(members,key))
    return by_truth,classes


def edits(expr,path=()):
    if expr[0]=="input":
        return
    op,left,right=expr
    for other in ("AND","OR","XOR"):
        if other!=op:
            yield "substitution",path,(other,left,right)
    if left[0]!="input":
        lower,a,b=left
        yield "rotation",path,(lower,a,(op,b,right))
    if right[0]!="input":
        lower,b,c=right
        yield "rotation",path,(lower,(op,left,b),c)
    for kind,where,node in edits(left,path+(0,)):
        yield kind,where,(op,node,right)
    for kind,where,node in edits(right,path+(1,)):
        yield kind,where,(op,left,node)


def check_panel(panel,catalogs,fold):
    require(len(panel)==32 and len({p["id"] for p in panel})==32,"Panel missing/duplicate task ID")
    index={p["id"]:p for p in panel}
    report={}
    for n in (4,5):
        rows=[p for p in panel if p["n"]==n]
        require(Counter(p["group"] for p in rows)=={"positive":4,"negative":4,"neutral":8},"Task cohort cardinalities differ")
        functions={c["truth"] for c in catalogs[False][n]["candidates"]}
        by_truth,classes=permutation_classes(functions,n)
        rng=random.Random(87019+137*n)
        initial=[]
        for weight in ((1,2,3,2,4) if n==4 else (1,4,2,3,2,3,5)):
            choices=[x for x in range(1,1<<n) if x.bit_count()==weight and x not in initial]
            initial.append(rng.choice(choices))
        neutral_rng=random.Random(41269+n)
        neutral_orbits=neutral_rng.sample(sorted(classes),8)
        neutral_truths=[neutral_rng.choice(classes[key]) for key in neutral_orbits]
        require({p["truth"] for p in rows if p["group"]=="neutral"}==set(neutral_truths),"Neutral tasks were not the independent fixed draw")
        seen=set()
        pairs=[]
        for task in rows:
            truth=task["truth"]
            require(truth in functions,"Concealed target is outside the common class")
            witness=primitive_witness(task["metadata"]["primitive_witness"])
            actual,_=program_truth(witness,n,None)
            require(actual==truth and sorted(ast_inventory(witness)[0])==list(range(n)),"Target witness/common domain differs")
            require(all(any((truth>>x&1)!=(truth>>(x^(1<<j))&1) for x in range(1<<n)) for j in range(n)),
                    "A fresh task has an inessential input")
            equality(task["initial"],initial,"task-independent initial row selection")
            meta=task["metadata"]
            orbit=by_truth[truth]
            require(orbit not in seen,"Two test tasks differ only by variable renaming")
            seen.add(orbit)
            require(meta["canonical_truth"]==orbit and meta["labeled_tables_in_class"]==len(classes[orbit]) and meta["ones"]==truth.bit_count(),
                    "Task family metadata differs from independently checked truth")
            spans=sorted(catalogs[True][n]["fold_spans"].get(truth,()))
            equality(meta["possible_fold_spans"],spans,"all equivalent fold placements")
            require(meta["fold_realizable"]==bool(spans),"Semantic fold status differs")
            if task["group"]=="positive":
                other=index[meta["partner"]]
                control=primitive_witness(other["metadata"]["primitive_witness"])
                require(other["group"]=="negative" and other["metadata"]["partner"]==task["id"] and
                        not catalogs[True][n]["fold_spans"].get(other["truth"]),"Matched control contains a fold in an equivalent tree")
                require((meta["edit"],tuple(meta["edit_path"]),control) in set(edits(witness)),"Matched control is not the declared single edit")
                if meta["edit"]=="rotation":
                    require(ast_inventory(witness)[2]==ast_inventory(control)[2],"Rotation changed primitive counts")
                pairs.append({"id":task["id"],"partner":other["id"],"edit":meta["edit"],
                              "changed_rows":(truth^other["truth"]).bit_count()})
        report[str(n)]={"tasks":len(rows),"essential_inputs":n,"distinct_mechanisms":len(seen),
                        "common_hypotheses":len(functions),"initial":initial,"pairs":pairs,
                        "neutral_fold_realizable":sum(bool(catalogs[True][n]["fold_spans"].get(p["truth"])) for p in rows if p["group"]=="neutral")}
    return report


def source_receipt(out):
    source=json.loads((out/"source_cost.json").read_bytes())
    ancestor=ROOT/"artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec"
    origin=ROOT/"artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand"
    paths={"parser_run":ancestor/"results.jsonl","parser_checkpoint":ancestor/"varied_checkpoint.json",
           "composition_run":origin/"results.jsonl","checkpoint":origin/"checkpoint.json","source_freeze":origin/"freeze.json",
           "raw_plans":origin/"raw_proposals.json","checked_plans":origin/"plans.json"}
    require(set(paths)==set(source["source_files"]),"Source ancestry receipt fields changed")
    for name,path in paths.items():
        require(file_digest(path)==source["source_files"][name],"Immutable ancestor changed: "+name)
    frozen=json.loads(paths["source_freeze"].read_bytes())
    for relative,sha in frozen["files"].items():
        require(file_digest(ROOT/relative)==sha,"Immutable source implementation changed: "+relative)
    parser=next(p for p in map(json.loads,paths["parser_run"].read_text().splitlines()) if p["case"]=="varied")
    composed=next(p for p in map(json.loads,paths["composition_run"].read_text().splitlines()) if p["case"]=="packet_nand")
    require(source["parser_training_case_wall_s"]==parser["seconds"] and source["composition_training_case_wall_s"]==composed["seconds"] and
            source["composition_training_fit_cpu_s"]==composed["result"]["fit_cpu_seconds"],"Historical source costs were replaced")
    acquisition=parser["seconds"]+composed["seconds"]+source["export_and_recertification_wall_s"]
    require(math.isclose(acquisition,source["original_acquisition_wall_s"],abs_tol=1e-12),"Source cost chain addition differs")
    fold=json.loads((out/"fold.json").read_bytes())
    require(file_digest(out/"fold.json")==source["dag_sha256"] and (out/"fold.json").stat().st_size==source["serialized_fold_bytes"],"Fold transfer byte count differs")
    key=source["source_wiring_id"]
    raw=json.loads(paths["raw_plans"].read_bytes())["plans"][key]["raw"]
    checked=json.loads(paths["checked_plans"].read_bytes())["wirings"][key]
    equality(fold,raw["dag"],"saved actual source NAND DAG")
    equality(raw,checked["sender"]["certified"],"source checker preserved the raw program")
    equality(source["source_work"],raw["public_actions"],"source public search accounting")
    equality(source["source_certificate"],checked["certificate"],"source exhaustive checker accounting")
    require(key=="d406ab6ea3ee6c83" and len(fold["gates"])==7 and
            sum(dag_value(fold,[x>>j&1 for j in range(3)])<<x for x in range(8))==120,"Wrong inherited fold truth or gate count")
    return source,fold


def stats(values):
    return {"median":statistics.median(values),"range":[min(values),max(values)]}


def outcome(task,fit,attempts,raw):
    n=task["n"]
    initial=len(raw["examples"])
    first_truth=sum(eval_ast(fit["proposals"][0]["expr"],x,n,raw["fold_binding"])<<x for x in range(1<<n))
    errors=(first_truth^task["truth"]).bit_count()
    work={"tasks":1,"initial_labels":initial,"held_rows":(1<<n)-initial,"first_correct_held_rows":(1<<n)-initial-errors,
          "first_exact":int(errors==0),"certified_tasks":1,"final_correct_rows":1<<n,"checks":len(attempts),
          "failed_checks":len(attempts)-1,"verifier_rows":sum(a["rows"] for a in attempts),
          "verifier_nands":sum(a["nand_evaluations"] for a in attempts),"hypotheses_inspected":fit["hypotheses_inspected"],
          "first_fit_label_tests":fit.get("consistency_label_tests",0),"median_order_comparisons":fit.get("order_comparisons",0),
          "final_uses_fold":int(bool(fit["final_macro_uses"])),"total_output_bytes":raw["output_bytes"],
          "final_physical_gates":attempts[-1]["physical_gates"]}
    truth_trace=[sum(eval_ast(a["expr"],x,n,raw["fold_binding"])<<x for x in range(1<<n)) for a in attempts]
    return {"work":work,"truth_trace":truth_trace,"counterexamples":[a["counterexample"] for a in attempts]}


def audit(out):
    out=Path(out)
    freeze=json.loads((out/"freeze.json").read_bytes())
    require(freeze["ticket"]==TICKET and freeze["tasks"]==32,"Wrong frozen experiment identity")
    for relative,sha in freeze["sources"].items():
        require(file_digest(ROOT/relative)==sha,"Frozen source changed: "+relative)
    for name,sha in freeze["inputs"].items():
        require(file_digest(out/name)==sha,"Frozen input changed: "+name)
    source,fold=source_receipt(out)
    panel=json.loads((out/"panel.json").read_bytes())
    by_id={task["id"]:task for task in panel}
    raw=[json.loads(line) for line in (out/"results.jsonl").read_text().splitlines()]
    require(len(raw)==12 and {r["case"] for r in raw}=={f"{i}-{m}" for i in range(3) for m in METHODS} and
            all(r["status"]=="ok" for r in raw),"Trial coverage/failures differ")
    require(len({r["worker"] for r in raw})==12,"Cross-method cache reuse: workers were not fresh")
    config=json.loads((out/"job.json").read_bytes())
    require(config["max_cases_per_worker"]==1,"Fresh-worker accounting disabled")
    job_path="experiments/"+TICKET+"/"+FAMILY+"/job.py"
    for r in raw:
        require(r["job_sha"]==freeze["sources"][job_path] and datetime.fromisoformat(r["finished_at"])>=datetime.fromisoformat(freeze["utc"]),"Wrong execution source/timing binding")
        require(r["result"]["pid"]==r["worker"],"Worker identity receipt differs")
    catalogs={}
    for inherited in (False,True):
        builder=Catalogues(fold if inherited else None)
        catalogs[inherited]={n:builder.build(n) for n in (4,5)}
    for n in (4,5):
        require({c["truth"] for c in catalogs[False][n]["candidates"]}=={c["truth"] for c in catalogs[True][n]["candidates"]},
                "Inheritance changed semantic capacity")
    panel_audit=check_panel(panel,catalogs,fold)
    official=json.loads((out/"result.json").read_bytes())
    for name,sha in official["bindings"].items():
        require(file_digest(out/name)==sha,"Result binding changed: "+name)
    generated={}
    for method in METHODS:
        inherited=method.endswith("_fold")
        binding=fold if inherited else None
        generated[method]={}
        for task in panel:
            examples=[[x,task["truth"]>>x&1] for x in task["initial"]]
            fn=median_fit if method.startswith("median_") else first_fit
            fit,attempts=fn(catalogs[inherited][task["n"]],examples,task["truth"],binding)
            generated[method][task["id"]]=(fit,attempts)
    outcomes={}
    samples={method:[] for method in METHODS}
    for record in raw:
        run=record["result"];method=run["method"];inherited=method.endswith("_fold")
        require(record["case"]==f"{run['repeat']}-{method}" and len(run["rows"])==32,"Run identity/task count differs")
        require([r["id"] for r in run["rows"]]==[t["id"] for t in panel],"Task order differs")
        for n in (4,5):
            actual=run["catalogues"][str(n)];expected=catalogs[inherited][n]
            truths=[c["truth"] for c in expected["candidates"]]
            require(actual["distinct"]==len(truths) and actual["unordered_digest"]==digest(sorted(truths)) and
                    actual["ordered_digest"]==digest(truths),"Cache truth/order fingerprint differs")
            construction={k:v for k,v in actual["construction"].items() if k!="elapsed_seconds"}
            equality(construction,expected["construction"],"every cold build/cache/duplicate charge")
            indexes=next(t["initial"] for t in panel if t["n"]==n) if method.startswith("median_") else []
            equality(actual["initial_index_rows"],indexes,"public median index inputs")
            require(actual["median_indexed_functions"]==(len(truths) if indexes else 0),"Median public index construction omitted")
        rows={};times={}
        for actual in run["rows"]:
            task=by_id[actual["id"]];n=task["n"]
            fit,attempts=generated[method][task["id"]]
            equality(actual["examples"],[[x,task["truth"]>>x&1] for x in task["initial"]],"identical sparse label acquisition")
            stripped={k:v for k,v in actual["fit"].items() if k not in ("checker_seconds","learner_seconds","elapsed_seconds")}
            equality(stripped,fit,"all proposal/selection/evidence fields")
            equality([{k:v for k,v in a.items() if k!="wall_ns"} for a in actual["attempts"]],attempts,"every accepted and rejected NAND execution")
            expected_bytes=len(json.dumps(actual["fit"]["final_expr"],separators=(",",":")).encode())
            require(actual["output_bytes"]==expected_bytes,"Executable result serialization omitted")
            require(sum(a["wall_ns"] for a in actual["attempts"])<=actual["wall_ns"],"Checker time exceeds full task cost")
            raw_with_binding=actual|{"fold_binding":fold if inherited else None}
            rows[task["id"]]=outcome(task,fit,attempts,raw_with_binding)
            times[task["id"]]={"task_wall_s":actual["wall_ns"]*1e-9,"check_wall_s":sum(a["wall_ns"] for a in actual["attempts"])*1e-9}
        require(run["setup_wall_ns"]+sum(r["wall_ns"] for r in run["rows"])<=run["downstream_wall_ns"],"Setup/task costs omitted from total")
        equality(rows,official["task_outcomes"][method],"reported deterministic outcomes")
        outcomes[method]=rows
        samples[method].append((run,times))
    groups={"all":list(by_id)}|{g:[t["id"] for t in panel if t["group"]==g] for g in ("positive","negative","neutral")}
    methods={}
    for method in METHODS:
        repeats=sorted(samples[method],key=lambda pair:pair[0]["repeat"])
        require([r["repeat"] for r,_ in repeats]==[0,1,2],"Missing timing repeat")
        work={}
        for group,ids in groups.items():
            counts=Counter()
            for key in ids:
                counts.update(outcomes[method][key]["work"])
            work[group]=dict(counts)
            for key in ("task_wall_s","check_wall_s"):
                work[group][key]=stats([sum(times[i][key] for i in ids) for _,times in repeats])
        acquisition=source["original_acquisition_wall_s"] if method.endswith("_fold") else 0
        methods[method]={"work":work,"source_wall_s":acquisition,
                         "downstream_wall_s":stats([r["downstream_wall_ns"]*1e-9 for r,_ in repeats]),
                         "downstream_cpu_s":stats([r["downstream_cpu_ns"]*1e-9 for r,_ in repeats]),
                         "setup_wall_s":stats([r["setup_wall_ns"]*1e-9 for r,_ in repeats]),
                         "full_wall_s":stats([acquisition+r["downstream_wall_ns"]*1e-9 for r,_ in repeats])}
    equality(methods,official["methods"],"all cost/work summaries and original source charge")
    changes={}
    for group,ids in groups.items():
        pairs=[(outcomes["first_fold"][i]["work"]["checks"],outcomes["first_plain"][i]["work"]["checks"]) for i in ids]
        changes[group]={"fewer":sum(a<b for a,b in pairs),"equal":sum(a==b for a,b in pairs),"more":sum(a>b for a,b in pairs)}
    equality(changes,official["primary_checks_paired"],"paired benefit/harm counts")
    null_checks=null_plain_gates=null_fold_gates=0
    for task in panel:
        key=task["id"]
        for field in ("truth_trace","counterexamples"):
            equality(outcomes["median_plain"][key][field],outcomes["median_fold"][key][field],"common-order median causal null")
        plain=catalogs[False][task["n"]]
        lookup={c["truth"]:c for c in catalogs[True][task["n"]]["candidates"]}
        common={"n":task["n"],"candidates":[lookup[c["truth"]] for c in plain["candidates"]]}
        examples=[[x,task["truth"]>>x&1] for x in task["initial"]]
        matched_fit,matched_attempts=first_fit(common,examples,task["truth"],fold)
        base_fit,base_attempts=generated["first_plain"][key]
        equality([a["counterexample"] for a in matched_attempts],[a["counterexample"] for a in base_attempts],"common-primitive-order first-fit feedback")
        equality([program_truth(p["expr"],task["n"],fold)[0] for p in matched_fit["proposals"]],outcomes["first_plain"][key]["truth_trace"],
                 "common-primitive-order first-fit hypotheses")
        require(matched_fit["hypotheses_inspected"]==base_fit["hypotheses_inspected"] and
                matched_fit["consistency_label_tests"]==base_fit["consistency_label_tests"],"Common order changed label information")
        null_checks+=len(matched_attempts)
        null_plain_gates+=sum(a["nand_evaluations"] for a in base_attempts)
        null_fold_gates+=sum(a["nand_evaluations"] for a in matched_attempts)
    projected={}
    for selector in ("first","median"):
        plain,fold_method=methods[selector+"_plain"],methods[selector+"_fold"]
        saved=plain["work"]["all"]["task_wall_s"]["median"]-fold_method["work"]["all"]["task_wall_s"]["median"]
        gap=source["original_acquisition_wall_s"]+fold_method["setup_wall_s"]["median"]-plain["setup_wall_s"]["median"]
        projected[selector]={"warm_s_saved_per_32":saved,"first_projected_32_task_batches":max(1,math.floor(gap/saved)+1) if saved>0 else None}
    equality(projected,official["projections"],"conditional comparable-workload extrapolations")
    require(official["median_semantic_traces_equal"]==32,"Median null summary differs")
    equality(official["hypothesis_counts"],{str(n):len(catalogs[False][n]["candidates"]) for n in (4,5)},"semantic class size summary")
    return {"ticket":TICKET,"schema_version":1,"status":"pass","audit_source_sha256":file_digest(__file__),
            "result_sha256":file_digest(out/"result.json"),"panel_audit":panel_audit,"source_cost":source,
            "trials_replayed":12,"task_replays":384,"hypothesis_counts":official["hypothesis_counts"],
            "catalogue_work":{str(int(mode)):{str(n):c["construction"] for n,c in catalogs[mode].items()} for mode in (False,True)},
            "methods":methods,"paired_checks":changes,"median_semantic_null_tasks":32,
            "common_primitive_order_null":{"tasks":32,"checks_each":null_checks,"plain_actual_NANDs":null_plain_gates,
                                            "fold_actual_NANDs":null_fold_gates,"semantic_feedback_identical":True},
            "projections":projected,"limits":["The inherited intervention changes a prior/order over an identical semantic class.",
             "The fold was synthesized by a frozen public planner using learned primitives; a ternary parameter was not directly fitted.",
             "The original seven-NAND source is preserved; ordinary primitive expansion implements the same fold in six NANDs.",
             "Full acquisition uses historical elapsed wall, with marginal existing-asset results reported separately; it is not CPU-equivalent.",
             "Median candidate indexing and order comparisons are charged in setup/time and separate counters; proposal counts alone are not total work.",
             "An equivalence-query checker supplies charged target information; this is not learning from the initial sparse labels alone."]}


def self_test():
    fold = {"gates":[[0,1],[5,5],[4,2],[7,6],[4,6],[9,2],[8,10]],"output":11}
    macro = ["FOLD",["input",0],["input",1],["input",2]]
    plain = ["XOR",["AND",["input",0],["input",1]],["input",2]]
    left,cost = program_truth(macro,3,fold)
    right,other_cost = program_truth(plain,3,fold)
    require(left==right==120 and cost==7 and other_cost==6,"Original fold or optimized primitive fixture differs")
    require(first_mismatch(macro,3,left,fold)=={"counterexample":None,"checked_rows":8,"NAND":56},"Exact verifier charge differs")
    require(first_mismatch(macro,3,left^(1<<6),fold)=={"counterexample":[6,0],"checked_rows":2,"NAND":14},
            "First-failure order or rejected-candidate charge differs")
    optimized={"gates":[[0,1],[5,5],[6,2],[6,7],[2,7],[8,9]],"output":10}
    require(all(dag_value(fold,[x>>j&1 for j in range(3)])==dag_value(optimized,[x>>j&1 for j in range(3)]) for x in range(8)),
            "Six-gate implementation control is not equivalent")
    return {"status":"pass","actual_NAND_vs_AST":True,"charged_first_counterexample":True,
            "source_seven_vs_six_gate_equivalence":True}


if __name__ == "__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--self-test",action="store_true")
    cli.add_argument("--out",type=Path,default=DEFAULT_OUT)
    cli.add_argument("--write",action="store_true")
    args=cli.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),sort_keys=True))
    else:
        result=audit(args.out)
        if args.write:
            (args.out/"audit.json").write_bytes(canonical(result)+b"\n")
        print(json.dumps({"status":result["status"],"trials":result["trials_replayed"],"hypothesis_counts":result["hypothesis_counts"],
                          "checks":{m:v["work"]["all"]["checks"] for m,v in result["methods"].items()},
                          "common_order_null":result["common_primitive_order_null"]},indent=2))
