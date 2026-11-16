"""Independent staged-feedback, physical-program and prefix-cost audit.

The primary causal pair shares teaching data, not necessarily terminal
equality outcomes.  A passing cached semantic column is trusted only after
binding and executing the actual NAND circuit.  Cumulative costs include
the archived source and all new gate acquisition before any held task.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
from itertools import permutations, accumulate
import json
import pickle
from pathlib import Path
from functools import lru_cache
import random
import statistics
import struct
import time


TICKET = "FOLD-GATE-20261115-001"
FAMILY = TICKET + "-E001_gated_stream"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "artifacts" / TICKET / FAMILY
STAGES = (8,12,16,24,32,48,64)
N = 6
FULL = (1 << 64) - 1
COLUMNS = tuple(sum(1 << x for x in range(64) if x >> j & 1) for j in range(N))
INITIAL = (16,47,3,29,35,40,38,63)
FEATURES = ("ones","minority_labels","closest_input_errors","decreasing_pairs","whole_parity_errors")
ARMS = ("median","gated-warm","gated-cold","always","median-warm","adaptive")
TRACE_KEYS = ("prefix_labels","teacher_mismatch_mask","teacher_rows","try_fold","used_fold",
              "proposal_stages","proposal_truths","verifier_calls","verifier_packed_checks",
              "verifier_rows","adaptive_feedback","accepted_stage","physical_sha256")
PRIOR_AUDIT_SHA = "04f5fae77505d6670d808a58acd0a720d548b9776f35d80d3b7d4ca884a7177b"


class AuditError(ValueError):
    pass


def require(condition,message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def prior_interpreter():
    """Reuse immutable independent semantics, never a producer or old run."""
    path=ROOT/"research/FOLD-REUSE-20261115-001/audit.py"
    require(file_digest(path)==PRIOR_AUDIT_SHA,"Independent prior physical interpreter changed")
    spec=importlib.util.spec_from_file_location("fold_gate_independent_NAND",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def physical_hash(circuit):
    return digest([circuit["inputs"],circuit["output"],circuit["gates"]])


def check_program(program,fold,n=6):
    interpreter=prior_interpreter()
    circuit=program["circuit"]
    expected=interpreter.expand_ast(program["expr"],n,fold)
    require(circuit["inputs"]==n and circuit["gates"]==expected["gates"] and circuit["output"]==expected["output"],
            "Physical operands/output differ from the submitted program")
    require(program["physical_sha256"]==physical_hash(circuit),"Cached verification digest does not bind actual NAND operands")
    values=[]
    for raw in range(1<<n):
        actual=interpreter.dag_value(expected,[raw>>j&1 for j in range(n)])
        semantic=interpreter.eval_ast(program["expr"],raw,n,fold)
        require(actual==semantic,"Physical NAND and AST semantics disagree")
        values.append(actual)
    truth=sum(value<<raw for raw,value in enumerate(values))
    require(program["truth"]==truth,"Public semantic cache differs from physically executed circuit")
    return truth


def check_circuit(program, cache):
    """Execute every literal NAND on all 64 inputs; trust neither table nor AST."""
    circuit=program["circuit"]
    token=program["physical_sha256"]
    require(token==physical_hash(circuit),"Physical digest does not bind NAND operands")
    require(circuit["inputs"]==N,"Wrong physical input domain")
    require(circuit.get("constants")=={"zero":6,"one":7},"Changed physical constant addresses")
    require(circuit["nand_gates"]==program["expanded_NANDs"]==len(circuit["gates"]),"Wrong physical gate charge")
    require(program["macro_uses"]==circuit["macro_uses"] in (0,1),"Wrong macro count")
    if token in cache:
        require(cache[token][1]==circuit,"Same physical token names different circuits")
        return cache[token][0]
    values=list(COLUMNS)+[0,FULL]
    for gate in circuit["gates"]:
        require(isinstance(gate,list) and len(gate)==2 and all(type(i) is int and 0<=i<len(values) for i in gate),
                "Physical NAND reads an invalid/future address")
        values.append(FULL ^ (values[gate[0]] & values[gate[1]]))
    output=circuit["output"]
    require(type(output) is int and 0<=output<len(values),"Invalid physical output")
    truth=values[output]
    # A separate scalar loop checks lane packing, and executes the actual tuple
    # of operand addresses rather than the producer's compiler or interpreter.
    scalar_truth=0
    for raw in range(64):
        bits=[raw>>j&1 for j in range(N)]+[0,1]
        for a,b in circuit["gates"]:
            bits.append(1-(bits[a]&bits[b]))
        scalar_truth |= bits[output]<<raw
    require(scalar_truth==truth,"Scalar and packed literal NAND replay disagree")
    cache[token]=(truth,circuit)
    return truth


def cumulative_crossovers(gaps,initial_gap=0,strict=False):
    """Tie-or-better is the registered primary, with strict saving optional."""
    wins=lambda gap: gap<0 if strict else gap<=0
    entries=[]
    was_win=wins(initial_gap)
    first=None
    for prefix,gap in enumerate(gaps,1):
        win=wins(gap)
        if win and first is None:
            first=prefix
        if win!=was_win:
            entries.append({"prefix":prefix,"direction":"gated_tie_or_better" if win else "gated_more_expensive","gap_ns":gap})
        was_win=win
    if not gaps:
        return {"prefixes":0,"first_crossover":None,"transitions":[],"terminal_gap":initial_gap,"minimum_gap":initial_gap}
    minimum=min(gaps)
    last_loss=next((i for i in range(len(gaps),0,-1) if not wins(gaps[i-1])),0)
    return {"prefixes":len(gaps),"first_crossover":first,"transitions":entries,"terminal_gap":gaps[-1],
            "minimum_gap":minimum,"minimum_gap_prefix":gaps.index(minimum)+1,
            "winning_prefixes":sum(map(wins,gaps)),"sustained_from":last_loss+1 if last_loss<len(gaps) else None}


def teacher_labels(truth,order):
    require(len(order)==64 and sorted(order)==list(range(64)),"Teaching schedule must expose each six-input row once")
    labels=[truth>>x&1 for x in order]
    mismatch=sum((((x&1)!=(truth>>x&1)))<<x for x in order[8:])
    return labels,mismatch


def gate_features(prefix):
    rows=list(prefix)[:8]
    require(len(rows)==8 and len({x for x,_ in rows})==8,"Gate requires eight distinct visible examples")
    require(all(type(x) is int and 0<=x<64 and type(y) in (int,bool) and y in (0,1) for x,y in rows),"Invalid visible gate inputs")
    ones=sum(y for _,y in rows)
    return {"ones":ones,"minority_labels":min(ones,8-ones),
            "closest_input_errors":min(sum((x>>j&1)!=y for x,y in rows) for j in range(6)),
            "decreasing_pairs":sum((u&v)==u for u,a in rows if a for v,b in rows if not b),
            "whole_parity_errors":sum((x.bit_count()&1)!=y for x,y in rows)}


def gate_decision(checkpoint,prefix):
    rule=checkpoint["rule"]
    if rule is None or len(prefix)<8:
        return False
    features=gate_features(prefix)
    require(rule["feature"] in features and rule["op"] in ("<=",">="),"Unknown frozen gate rule")
    value=features[rule["feature"]]
    return value<=rule["limit"] if rule["op"]=="<=" else value>=rule["limit"]


def get(path):
    return json.loads(Path(path).read_bytes())


def public_order():
    suffix=[x for x in range(64) if x not in INITIAL]
    random.Random(6202602).shuffle(suffix)
    return INITIAL+tuple(suffix)


def read_split(path, split):
    with Path(path).open("rb") as source:
        header=json.loads(source.readline())
        payload=source.read()
    count={"train":1024,"held":32768}[split]
    require(header["split"]==split and header["format"]=="fold-gate-truth-u64le-v1" and header["n"]==6,
            "Wrong split identity")
    require(header["row_order"]==list(public_order()) and header["stages"]==list(STAGES),"Changed teaching schedule")
    require(header["count"]==count and len(payload)==8*count,"Truncated target stream")
    require(hashlib.sha256(payload).hexdigest()==header["ordered_truths_sha256"],"Ordered target digest mismatch")
    values=tuple(x[0] for x in struct.iter_unpack("<Q",payload))
    require(len(set(values))==count,"Repeated target in split")
    return header,values


def join_shape(op,left,right):
    # Unrestricted leaf-count splits, then AC normalization, unlike a truth
    # lookup or the producer's adjacent-swap orbit implementation.
    children=[]
    for child in (left,right):
        children.extend(child[1:] if child[0]==op else (child,))
    return (op,*sorted(children))


@lru_cache(maxsize=None)
def shapes(leaves):
    if leaves==1:
        return ((0,),)
    found=set()
    for size in range(1,leaves):
        for left in shapes(size):
            for right in shapes(leaves-size):
                for op in (1,2,3):
                    found.add(join_shape(op,left,right))
    return tuple(sorted(found))


def shape_value(shape,columns):
    leaves=iter(columns)
    def visit(node):
        if node==(0,):
            return next(leaves)
        values=[visit(child) for child in node[1:]]
        result=values[0]
        for value in values[1:]:
            result=result&value if node[0]==1 else result|value if node[0]==2 else result^value
        return result
    return visit(shape)


def fold_shape(node):
    return bool(node[0]==3 and any(child[0]==1 for child in node[1:])) or any(map(fold_shape,node[1:]))


def word_digest(words):
    h=hashlib.sha256()
    for word in words:
        h.update(struct.pack("<Q",word))
    return h.hexdigest()


def independent_population(headers,targets):
    """Directly evaluate all 720 variable permutations of 651 public trees."""
    inventory=shapes(6)
    require(len(inventory)==651,"Wrong normalized public mechanism inventory")
    orbits=[]
    mechanism_of={}
    folded=set()
    orders=tuple(permutations(COLUMNS))
    for index,shape in enumerate(inventory):
        orbit=tuple(sorted({shape_value(shape,cols) for cols in orders}))
        require(not set(orbit).intersection(mechanism_of),"Different normalized mechanisms have the same function")
        for truth in orbit:
            require(all((truth^(truth>>(1<<j)))&(FULL^COLUMNS[j]) for j in range(6)),"Task omits an essential input")
            mechanism_of[truth]=index
        orbits.append(orbit)
        if fold_shape(shape):
            folded.update(orbit)
    require(len(mechanism_of)==81819 and len(folded)==39671,"Wrong extensional public grammar")
    # A separate semantic subset DP checks the formula/permutation generator.
    @lru_cache(maxsize=None)
    def base(mask):
        if mask.bit_count()==1:
            return frozenset((COLUMNS[mask.bit_length()-1],))
        out=set()
        for left in range(1,mask):
            if left&mask!=left or not left&(mask&-mask):
                continue
            for a in base(left):
                for b in base(mask^left):
                    out.update((a&b,a|b,a^b))
        return frozenset(out)
    require(base(63)==set(mechanism_of),"Independent subset-DP and direct-permutation grammars disagree")
    ids=list(range(651));random.Random(6202611).shuffle(ids)
    partition={"train":sorted(ids[:162]),"held":sorted(ids[162:])}
    summary={}
    for split,seed in (("train",6202612),("held",6202613)):
        pool=[(truth,index) for index in partition[split] for truth in orbits[index]]
        sampled=random.Random(seed).sample(pool,len(targets[split]))
        require(tuple(t for t,_ in sampled)==targets[split],"Frozen stream differs from preselected mechanism-partition sample")
        counts=Counter(index for _,index in sampled)
        h=headers[split]
        checks={"pool_mechanisms":len(partition[split]),"pool_labeled":len(pool),
                "pool_foldable_mechanisms":sum(fold_shape(inventory[i]) for i in partition[split]),
                "pool_foldable_labeled":sum(t in folded for t,_ in pool),"sample_mechanisms":len(counts),
                "sample_foldable_mechanisms":sum(fold_shape(inventory[i]) for i in counts),
                "sample_foldable_tasks":sum(t in folded for t,_ in sampled),
                "sample_recodings_after_first":len(sampled)-len(counts),"max_tasks_per_mechanism":max(counts.values()),
                "partition_mechanisms_sha256":word_digest(partition[split]),"sample_mechanisms_sha256":word_digest(sorted(counts)),
                "ordered_truths_sha256":word_digest(t for t,_ in sampled),"ordered_mechanisms_sha256":word_digest(i for _,i in sampled)}
        require(all(h[k]==v for k,v in checks.items()),"Frozen split statistics are wrong")
        summary[split]=checks
    require(set(partition["train"]).isdisjoint(partition["held"]),"Train/held mechanisms overlap")
    require(set(targets["train"]).isdisjoint(targets["held"]),"Train/held targets overlap")
    summary.update(mechanisms=651,foldable_mechanisms=sum(map(fold_shape,inventory)),functions=81819,fold_functions=39671,
                   verified_by="all variable permutations plus independent subset semantic DP")
    return tuple(sorted(mechanism_of)),tuple(sorted(folded)),summary,{mask:base(mask) for mask in range(1,64)}


class PublicSelector:
    """Literal sorted candidates filtered only by the provided observations."""
    def __init__(self,plain,folded):
        self.values={"default":plain,"fold":folded}
        self.positions={route:{t:i for i,t in enumerate(values)} for route,values in self.values.items()}
        self.initial={}
        for route,values in self.values.items():
            buckets=defaultdict(list)
            for truth in values:
                key=sum((truth>>x&1)<<pos for pos,x in enumerate(INITIAL))
                buckets[key].append(truth)
            self.initial[route]={key:tuple(items) for key,items in buckets.items()}

    def start(self,route,key):
        return self.initial[route].get(key,())

    @staticmethod
    def narrow(pool,visible):
        mask=sum(1<<x for x,_ in visible)
        answers=sum(label<<x for x,label in visible)
        return tuple(t for t in pool if t&mask==answers)

    @staticmethod
    def choose(pool):
        return pool[(len(pool)-1)//2] if pool else None


def replay_trace(row,target,arm,checkpoint,selector,order):
    labels,mismatch=teacher_labels(target,order)
    prefix=sum(label<<pos for pos,label in enumerate(labels[:8]))
    if row is not None:
        require(row["prefix_labels"]==prefix,"Initial labels differ from target")
    initial=tuple(zip(order[:8],labels[:8]))
    try_fold=arm=="always" or (arm.startswith("gated") and gate_decision(checkpoint,initial))
    if row is not None:
        require(row["try_fold"]==try_fold,"Gate did not use the frozen prefix-only decision")
    counters=Counter(tasks=1,try_fold=try_fold,teacher_rows=0,verifier_rows=0,verifier_packed_checks=0,
                     first_exact=0,final_fold=0,used_fold=0,verifier_calls=0,proposals=0,expanded_NANDs_returned=0)
    work=Counter(task_states_created=1)
    previous_by_route=Counter()
    def charge(route,visible):
        work["candidate_calls"]+=1
        work["fold_candidate_calls" if route=="fold" else "default_candidate_calls"]+=1
        work["example_rows_validated"]+=len(visible)
        for _,label in visible[previous_by_route[route]:]:
            work["constraint_bitset_ops"]+=1 if label else 2
        previous_by_route[route]=len(visible)
    truths=[];stages=[];feedback=[];scanned=0;seen=set();used=False;route="default"
    if arm=="adaptive":
        if row is not None:
            require(row["teacher_mismatch_mask"] is None and row["teacher_rows"]==0,"Adaptive reference received the common teaching suffix")
        visible=list(initial);known=set(order[:8]);pool=selector.start("default",prefix)
        while True:
            charge("default",visible)
            candidate=selector.choose(pool)
            require(candidate is not None,"Empty primitive version space")
            truths.append(candidate);stages.append(len(visible))
            wrong=candidate^target
            if not wrong:
                scanned+=64
                break
            x=wrong.bit_length()-1
            require(x not in known,"Adaptive correction contradicts an already visible label")
            scanned+=64-x;feedback.append([x,target>>x&1])
            for equal in range(63,x,-1):
                if equal not in known:
                    visible.append((equal,candidate>>equal&1));known.add(equal)
            visible.append((x,target>>x&1));known.add(x)
            pool=selector.narrow(pool,visible)
        counters["verifier_rows"]=scanned
    else:
        if row is not None:
            require(row["teacher_rows"]==56 and row["teacher_mismatch_mask"]==mismatch,"Common ordered teaching feedback differs")
        counters["teacher_rows"]=56
        pool=selector.start("default",prefix)
        for stage in STAGES:
            visible=tuple(zip(order[:stage],labels[:stage]))
            route="fold" if try_fold and stage==8 else "default"
            if route=="fold":
                folded=selector.start("fold",prefix)
                candidate=selector.choose(folded)
                charge("fold",visible)
                used=candidate is not None
                if not used:
                    work["empty_fold_selections"]+=1
                    route="default"
            if route=="default":
                pool=selector.narrow(pool,visible)
                candidate=selector.choose(pool)
                charge("default",visible)
            require(candidate is not None,"Empty common public version space")
            truths.append(candidate);stages.append(stage)
            if candidate not in seen:
                counters["verifier_packed_checks"]+=1
                if candidate==target:
                    break
                seen.add(candidate)
        else:
            raise AuditError("No exact candidate after all public labels")
    counters["used_fold"]=used
    counters["first_exact"]=truths[0]==target
    counters["proposals"]=len(truths)
    counters["verifier_calls"]=len(truths) if arm=="adaptive" else counters["verifier_packed_checks"]
    counters["final_fold"]=route=="fold"
    for key,value in (("proposal_truths",truths),("proposal_stages",stages),("adaptive_feedback",feedback),
                      ("accepted_stage",stages[-1]),("verifier_calls",counters["verifier_calls"]),
                      ("verifier_packed_checks",counters["verifier_packed_checks"]),("verifier_rows",scanned),("used_fold",used)):
        if row is not None:
            require(row[key]==value,f"Public-only proposal/check replay differs: {arm}/{key}")
    expected={"prefix_labels":prefix,"try_fold":try_fold,"used_fold":used,"proposal_truths":truths,"proposal_stages":stages,
              "teacher_rows":counters["teacher_rows"],"teacher_mismatch_mask":None if arm=="adaptive" else mismatch,
              "verifier_calls":counters["verifier_calls"],"verifier_packed_checks":counters["verifier_packed_checks"],
              "verifier_rows":scanned,"adaptive_feedback":feedback,"accepted_stage":stages[-1]}
    return route,counters,work,expected


def replay_gate(training,targets,order):
    require(training["warmup_count"]==64 and training["passes"]==3 and training["mode_order"]==["median","always"],"Changed training protocol")
    costs=training["cpu_ns"]
    require(len(costs)==1024 and all(len(pair)==2 and all(len(a)==3 and all(type(v) is int and v>=0 for v in a) for a in pair) for pair in costs),
            "Incomplete paired CPU training measurements")
    rows=[]
    for target,pair in zip(targets,costs):
        prefix=[(x,target>>x&1) for x in order[:8]]
        rows.append((gate_features(prefix),statistics.median(pair[0]),statistics.median(pair[1])))
    measured=rows[64:]
    best_rule=None;best_gain=0;best_attempts=0;nonnull=[]
    for name in FEATURES:
        values=sorted({feature[name] for feature,_,_ in measured})
        for op,thresholds in (("<=",values[:-1]),(">=",values[1:])):
            for limit in thresholds:
                selected=[m-f for feature,m,f in measured if (feature[name]<=limit if op=="<=" else feature[name]>=limit)]
                if min(len(selected),960-len(selected))<4:
                    continue
                gain=sum(selected);nonnull.append(gain)
                if (gain,-len(selected))>(best_gain,-best_attempts):
                    best_rule={"feature":name,"op":op,"limit":limit};best_gain=gain;best_attempts=len(selected)
    base=sum(m for _,m,_ in measured);probe=sum(f for _,_,f in measured)
    cp={"schema_version":1,"prefix_length":8,"min_training_rules_per_branch":4,"rule":best_rule,
        "training":{"rules":960,"selected_fold_attempts":best_attempts,"selected_cost":base-best_gain,
                    "savings_vs_always_median":best_gain,"always_median_cost":base,"always_try_cost":probe,
                    "per_rule_hindsight_min_cost":sum(min(m,f) for _,m,f in measured)}}
    cp["sha256"]=digest(cp)
    diagnostics={"eligible_thresholds":len(nonnull),"largest_nonnull_training_saving_ns":max(nonnull),
                 "fold_cheaper_training_rules":sum(f<m for _,m,f in measured),
                 "sum_all_recorded_training_cpu_ns":sum(sum(a) for pair in costs for a in pair)}
    return cp,diagnostics


def submitted_pairs(expected):
    return [("fold" if expected["used_fold"] and stage==8 else "default",truth)
            for stage,truth in zip(expected["proposal_stages"],expected["proposal_truths"],strict=True)]


def simulate_training(targets,checkpoint,selector,order):
    selected={};counters={}
    for arm in ("median","always"):
        programs=set();work=Counter()
        for target in targets:
            _,_,paid,expected=replay_trace(None,target,arm,checkpoint,selector,order)
            programs.update(submitted_pairs(expected));work.update(paid)
        selected[arm]=programs;counters[arm]=work
    return selected,counters


class FrozenBackend:
    """Opaque data holder: never run a producer constructor or __setstate__."""


class DataOnlyUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        if (module,name)==("search","SearchBackend"):
            return FrozenBackend
        if (module,name)==("builtins","object"):
            return object
        raise AuditError(f"Executable/unrecognized training cache object: {module}.{name}")


def inspect_snapshot(path,expected_pairs,selector,subsets,fold,physical_cache):
    with gzip.open(path,"rb") as reader:
        state=DataOnlyUnpickler(reader).load()
    allowed={"n","rows","full","mask","_work","_seconds","_owner","fold_dag","fold_sha256","_inputs",
             "_base","_fold","_partitions","_tripartitions","_broadcasts","_row_indexes","_asts","_programs","_fold_guard_done"}
    require(type(state) is FrozenBackend and set(state.__dict__)==allowed,"Training cache retains unexpected state")
    require((state.n,state.rows,state.full,state.mask,state._inputs)==(6,64,FULL,63,COLUMNS),"Cached input domain changed")
    require(set(state._programs)==expected_pairs,"Training cache contains unearned or missing public programs")
    for mask,(ordered,members) in state._base.items():
        require(members==subsets[mask] and ordered==tuple(sorted(members)),"Cached primitive class was changed")
    if state.fold_dag is not None:
        require(state.fold_dag==fold and state.fold_sha256==digest(fold),"Cached saved DAG changed")
        require(state._fold[63][0]==selector.values["fold"],"Cached fold class differs from independent public grammar")
    else:
        require(not state._fold,"Plain cache contains a hidden fold class")
    # These caches contain public syntax/functions only, with no task state or
    # target-specific labels. Validate every stored program, including failures.
    for (route,truth),program in state._programs.items():
        receipt=dict(program,physical_sha256=physical_hash(program["circuit"]))
        require(program["truth"]==truth and check_circuit(receipt,physical_cache)==truth,"Training program cache truth is stale")
        require(check_program(receipt,fold)==truth,"Training cached program differs from its literal AST")
        require(program["macro_uses"]==int(route=="fold"),"Cached route has the wrong saved-call count")
    for (route,x),membership in state._row_indexes.items():
        packed=bytearray((len(selector.values[route])+7)//8)
        for i,truth in enumerate(selector.values[route]):
            if truth>>x&1:
                packed[i>>3]|=1<<(i&7)
        require(membership==int.from_bytes(packed,"little"),"Public cached row index differs from literal candidates")
    return {"programs":len(state._programs),"physical_NANDs":sum(p["expanded_NANDs"] for p in state._programs.values()),
            "public_row_indexes":len(state._row_indexes),"task_label_state_retained":False,
            "safe_data_only_deserialization":True}


def iter_trace(path):
    with gzip.open(path,"rb") as source:
        require(json.loads(next(source))==list(TRACE_KEYS),"Trace schema changed")
        for line in source:
            values=json.loads(line)
            require(len(values)==len(TRACE_KEYS),"Truncated trace row")
            yield dict(zip(TRACE_KEYS,values,strict=True)),line


def read_manifests(out,selector,physical_cache):
    manifests={};summaries={}
    for arm in ARMS:
        programs={}
        with gzip.open(out/f"programs-{arm}.jsonl.gz","rt") as source:
            for line in source:
                program=json.loads(line);token=program["physical_sha256"]
                require(token not in programs,"Repeated manifest identity")
                truth=check_circuit(program,physical_cache)
                route=program["route"]
                require(route in selector.values and truth in selector.positions[route],"Physical program is outside its public class")
                require(program["candidate_index"]==selector.positions[route][truth],"Candidate ID does not name its physical truth")
                require(program["macro_uses"]==int(route=="fold"),"Physical macro metadata differs from route")
                programs[token]=(program,truth)
        require(len(programs)==32768,"Accepted program manifest does not cover each distinct target")
        manifests[arm]=programs
        summaries[arm]={"unique_returned_programs":len(programs),"manifest_sha256":file_digest(out/f"programs-{arm}.jsonl.gz")}
    return manifests,summaries


def check_work(actual,before,expected,programs,prior_programs):
    delta={key:actual["counters"][key]-before["counters"][key] for key in actual["counters"]}
    for key,value in expected.items():
        require(delta[key]==value,f"Backend work is inconsistent with public replay: {key}")
    require(delta["materialization_requests"]==expected["candidate_calls"]-expected["empty_fold_selections"],"Program construction requests are missing")
    builds=len(programs-prior_programs)
    require(delta["physical_programs_compiled"]==delta["physical_programs_validated"]==builds,"Physical cache build/validation count differs")
    require(delta["materialization_cache_hits"]==delta["materialization_requests"]-builds,"Physical cache hit count differs")
    require(delta["physical_NANDs_compiled"]==delta["validation_packed_NANDs"],"New physical gates were not all validated")
    require(delta["validation_scalar_equivalent_NANDs"]==64*delta["validation_packed_NANDs"],"Packed/scalar physical charge conversion differs")
    require(actual["cache"]["physical_programs"]==before["cache"]["physical_programs"]+builds,"Final physical cache conservation fails")
    require(actual["cache"]["physical_NANDs_retained"]==before["cache"]["physical_NANDs_retained"]+delta["physical_NANDs_compiled"],"Retained NAND ledger differs")
    require(actual["cache"]["physically_verified_columns"]==actual["cache"]["physical_programs"],"Unvalidated output column entered cache")
    return {"new_physical_programs":builds,"materialization_hits":delta["materialization_cache_hits"],
            "physical_packed_NANDs":delta["validation_packed_NANDs"],"candidate_calls":delta["candidate_calls"],
            "public_example_rows_validated":delta["example_rows_validated"],"constraint_bitset_ops":delta["constraint_bitset_ops"]}


def reproduce_trace_arm(out,arm,targets,checkpoint,selector,order,manifest):
    total=Counter();work=Counter();programs=set();hash_state=hashlib.sha256();used_tokens=set();length=0
    first_pairs=[];early=Counter()
    for i,(row,line) in enumerate(iter_trace(out/f"trace-{arm}.jsonl.gz")):
        require(i<len(targets),"Extra trace task")
        target=targets[i]
        route,counts,paid,expected=replay_trace(row,target,arm,checkpoint,selector,order)
        hash_state.update(line);work.update(paid);programs.update(submitted_pairs(expected))
        token=row["physical_sha256"]
        require(token in manifest,"Returned physical program is missing from manifest")
        program,truth=manifest[token]
        require(truth==target==row["proposal_truths"][-1] and program["route"]==route,"Returned circuit does not implement accepted submission/target")
        counts["expanded_NANDs_returned"]=program["expanded_NANDs"]
        total.update(counts);used_tokens.add(token);length+=1
        first_pairs.append((row["prefix_labels"],row["proposal_truths"][0]))
        early[row["accepted_stage"]]+=1
    require(length==len(targets) and used_tokens==set(manifest),"Trace/manifest coverage differs")
    return {"stats":dict(total),"work":work,"programs":programs,"trace_hash":hash_state.hexdigest(),
            "accepted_stages":dict(sorted(early.items())),"first_pairs":first_pairs}


def assessor_comparison(comparison):
    return {"first_break_even":comparison["first_crossover"],"sustained_from":comparison["sustained_from"],
            "reversals":[t["prefix"] for t in comparison["transitions"] if t["direction"]=="gated_more_expensive"],
            "closest_prefix":comparison["minimum_gap_prefix"],"lowest_gap_ns":comparison["minimum_gap"],"end_gap_ns":comparison["terminal_gap"]}


def audit(out):
    started=time.perf_counter()
    design=get(out/"design.json");freeze=get(out/"gate-freeze.json");checkpoint=get(out/"gate.json")
    require(file_digest(out/"design.json")==freeze["design_sha256"],"Design was not frozen before gate")
    require(design["bound_utc"]<=freeze["frozen_utc"],"Checkpoint precedes source binding")
    for relative,expected in design["sources"].items():
        require(file_digest(ROOT/relative)==expected,f"Changed bound scientific source: {relative}")
    for name,key in (("gate.json","gate_file_sha256"),("training.json.gz","training_log_sha256")):
        require(file_digest(out/name)==freeze[key],"Changed frozen training artifact")
    require(checkpoint["sha256"]==digest({k:v for k,v in checkpoint.items() if k!="sha256"}),"Checkpoint internal hash differs")
    require((freeze["training_targets"],freeze["training_rows_used_for_fit"])==(1024,960),"Changed training population")
    headers={};targets={}
    for split in ("train","held"):
        require(file_digest(out/f"{split}.bin")==design["splits"][split],"Changed frozen split file")
        headers[split],targets[split]=read_split(out/f"{split}.bin",split)
        require(word_digest(targets[split])==design["ordered_targets"][split],"Unbound ordered target sequence")
    with gzip.open(out/"training.json.gz","rt") as source:
        training=json.load(source)
    replayed_gate,training_diagnostic=replay_gate(training,targets["train"],public_order())
    require(replayed_gate==checkpoint,"Independent training-cost threshold sweep selects a different policy")
    require(freeze["paid_training_cpu_ns"]>=training_diagnostic["sum_all_recorded_training_cpu_ns"],"Paid training omits recorded learner CPU")
    print("Independent gate fit and bindings passed; rebuilding the public grammar.",flush=True)
    plain,folded,population,subsets=independent_population(headers,targets)
    selector=PublicSelector(plain,folded);order=public_order()
    selected_training,training_work=simulate_training(targets["train"],checkpoint,selector,order)
    physical_cache={};snapshot_report={}
    fold_path=ROOT/"artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/fold.json"
    fold=get(fold_path)
    for mode,arm in (("gated","always"),("median","median")):
        meta=freeze["snapshots"][mode];path=out/meta["name"]
        require(path.stat().st_size==meta["bytes"] and file_digest(path)==meta["sha256"],"Snapshot differs from frozen checkpoint")
        snapshot_report[mode]=inspect_snapshot(path,selected_training[arm],selector,subsets,fold,physical_cache)
        require(snapshot_report[mode]["programs"]==meta["cache"]["physical_programs"],"Snapshot program count differs")
    for pair in training["counts_per_pass"]:
        require(len(pair)==2,"Incomplete paired training pass")
        for ledger,arm in zip(pair,("median","always"),strict=True):
            for key,value in training_work[arm].items():
                require(ledger["counters"][key]==value,"Training work differs from independently replayed public proposals")
            require(ledger["cache"]["physical_programs"]==len(selected_training[arm]),"Training build count is wrong")
    print("Independent population and saved training programs passed; replaying held circuits and proposals.",flush=True)
    manifests,manifest_report=read_manifests(out,selector,physical_cache)
    traces={arm:reproduce_trace_arm(out,arm,targets["held"],checkpoint,selector,order,manifests[arm]) for arm in ARMS}
    raw=[json.loads(line) for line in (out/"results.jsonl").read_text().splitlines()]
    expected_order=[(r,a) for r in range(3) for a in (("median","gated-warm","gated-cold")[r:]+("median","gated-warm","gated-cold")[:r])]
    expected_order +=[(0,a) for a in ("always","median-warm","adaptive")]
    require(len(raw)==12 and [(r["result"]["repeat"],r["result"]["arm"]) for r in raw]==expected_order,"Missing, duplicated or reordered method trial")
    require(all(r["status"]=="ok" and r["attempt"]==1 for r in raw),"Failed/retried official run")
    require(len({r["worker"] for r in raw})==12,"Timing trials did not use separate processes")
    cost_path=ROOT/"artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/source_cost.json"
    oldcost=get(cost_path)
    source_ns=round(oldcost["original_acquisition_wall_s"]*1e9)
    require(source_ns==11057666975,"Original acquisition charge changed")
    upfront={"gated-warm":source_ns+freeze["paid_training_wall_ns"],"gated-cold":source_ns+freeze["paid_training_wall_ns"],"always":source_ns}
    assessed=get(out/"result.json")
    curves=defaultdict(dict);arms=defaultdict(list);work_report={};previous_finish=None
    for receipt in raw:
        row=receipt["result"];arm=row["arm"];repeat=row["repeat"];reference=traces[arm]
        require(receipt["job_sha"]==design["sources"][str((ROOT/"experiments"/TICKET/FAMILY/"job.py").relative_to(ROOT))],"Unbound job executed")
        finish=datetime.fromisoformat(receipt["finished_at"])
        require(finish>=datetime.fromisoformat(freeze["frozen_utc"].replace("Z","+00:00")),"Held run predates checkpoint freeze")
        estimated_start=finish.timestamp()-receipt["seconds"]
        require(previous_finish is None or estimated_start>=previous_finish-0.01,"Official timed workers overlapped")
        previous_finish=finish.timestamp()
        require(row["trace_keys"]==list(TRACE_KEYS) and row["trace_hash"]==reference["trace_hash"],"Timing repeats changed semantic trace")
        require(row["stats"]==reference["stats"],"Official statistics differ from independent trace replay")
        require(row["first_run_trace"]==(f"trace-{arm}.jsonl.gz" if repeat==0 else None),"Wrong trace identity")
        require(row["program_manifest"]==(f"programs-{arm}.jsonl.gz" if repeat==0 else None),"Wrong physical manifest identity")
        prior=selected_training["always"] if arm=="gated-warm" else selected_training["median"] if arm=="median-warm" else set()
        if arm.endswith("-warm"):
            mode=arm.split("-")[0]
            require(row["growth_before"]["cache"]==freeze["snapshots"][mode]["cache"],"Warm setup did not use the frozen public cache")
        else:
            require(row["growth_before"]["cache"]["physical_programs"]==0,"Cold arm started with a program cache")
        work_report[f"{repeat}-{arm}"]=check_work(row["growth_after"],row["growth_before"],reference["work"],reference["programs"],prior)
        timing=(out/row["times"]).read_bytes()
        require(len(timing)==32768*16 and hashlib.sha256(timing).hexdigest()==row["times_sha256"],"Truncated or changed timing file")
        wall,cpu=zip(*struct.iter_unpack("<QQ",timing))
        require(all(v>0 for v in wall+cpu),"Invalid zero duration")
        curve=list(accumulate(wall,initial=upfront.get(arm,0)+row["setup_wall_ns"]))
        curves[arm][repeat]=curve
        record={"repeat":repeat,"setup_ns":row["setup_wall_ns"],"total_ns":curve[-1],"downstream_ns":curve[-1]-upfront.get(arm,0),
                "cpu_ns":row["setup_cpu_ns"]+sum(cpu),"physical_builds":work_report[f"{repeat}-{arm}"]["new_physical_programs"],
                "physical_hits":work_report[f"{repeat}-{arm}"]["materialization_hits"],
                "physical_packed_NANDs":work_report[f"{repeat}-{arm}"]["physical_packed_NANDs"]}
        arms[arm].append(record)
        require(receipt["seconds"]*1e9>=record["downstream_ns"],"Charged inner time exceeds actual entire runner time")
        require(record in assessed["arms"][arm]["runs"],"Assessed per-run cost differs from raw times")
    midpoint={arm:[statistics.median(xs) for xs in zip(*[reps[r] for r in sorted(reps)],strict=True)] for arm,reps in curves.items()}
    comparison={}
    for arm in ("gated-warm","gated-cold"):
        difference=[a-b for a,b in zip(midpoint[arm],midpoint["median"],strict=True)]
        check=cumulative_crossovers(difference[1:],difference[0])
        require(assessed["arms"][arm]["comparison"]==assessor_comparison(check),"All-prefix median cost assessment differs")
        paired=[]
        for repeat in range(3):
            dif=[a-b for a,b in zip(curves[arm][repeat],curves["median"][repeat],strict=True)]
            item=cumulative_crossovers(dif[1:],dif[0]);paired.append(item)
            require(assessed["arms"][arm]["paired_repeats"][repeat]==assessor_comparison(item),"Per-repeat crossover arithmetic differs")
        comparison[arm]={"pointwise_median":check,"individual_repeats":paired,
                         "median_total_ns":midpoint[arm][-1],"median_downstream_ns":midpoint[arm][-1]-upfront[arm]}
    for arm,runs in arms.items():
        require(assessed["arms"][arm]["median_total_ns"]==statistics.median(r["total_ns"] for r in runs),"Endpoint median differs")
        require(assessed["arms"][arm]["upfront_ns"]==upfront.get(arm,0),"Assessor omitted acquisition")
    require(assessed["training"]["checkpoint"]==checkpoint and assessed["training"]["paid_training_ns"]==freeze["paid_training_wall_ns"] and
            assessed["training"]["source_ns"]==source_ns,"Assessor training/source bill differs")
    for split in ("train","held"):
        require(assessed[f"{split}_split"]==headers[split],"Assessed split summary differs")
    require(assessed["correct_rule_input_pairs_per_arm"]==32768*64,"Wrong physical input coverage")
    folded_members=set(folded)
    paired_choices=Counter(tasks=32768,fold_possible=sum(t in folded_members for t in targets["held"]))
    ambiguity=defaultdict(dict)
    for i,(target,base,always) in enumerate(zip(targets["held"],traces["median"]["first_pairs"],traces["always"]["first_pairs"],strict=True),1):
        key,b=base;_,f=always
        paired_choices["same_first_truth"]+=b==f
        paired_choices["both_first_exact"]+=b==f==target
        paired_choices["fold_only_first_exact"]+=b!=target and f==target
        paired_choices["median_only_first_exact"]+=b==target and f!=target
        if b!=f and target in (b,f):
            ambiguity[key]["median" if target==b else "fold"]=(i,target)
    # Full trajectory counts follow independently validated exact trace rows.
    for (base,_),(always,_),(gated,_) in zip(iter_trace(out/"trace-median.jsonl.gz"),iter_trace(out/"trace-always.jsonl.gz"),iter_trace(out/"trace-gated-warm.jsonl.gz"),strict=True):
        paired_choices["fewer_checks_with_unconditional_fold"]+=always["verifier_calls"]<base["verifier_calls"]
        paired_choices["more_checks_with_unconditional_fold"]+=always["verifier_calls"]>base["verifier_calls"]
        paired_choices["different_from_default_gate_trajectory"]+=gated["proposal_truths"]!=base["proposal_truths"]
    require(dict(paired_choices)==assessed["paired_choices"],"Reported first-proposal/control counts differ")
    ambiguous={key:group for key,group in ambiguity.items() if len(group)==2}
    require(assessed["prefix_ambiguity"]["opposite_first_winners_prefixes"]==len(ambiguous),"Ambiguous-prefix diagnostic differs")
    audit_hashes={name:file_digest(out/name) for name in ("design.json","gate-freeze.json","gate.json","training.json.gz","results.jsonl","result.json")}
    audit_hashes["audit.py"]=file_digest(Path(__file__))
    all_stats={arm:traces[arm]["stats"] for arm in ARMS}
    return {"study":TICKET,"verdict":"PASS","independence":"Independent scalar NAND interpreter, public-class generation, literal-candidate selection and gate/cost replay; no producer evaluator/fitter invoked.",
            "input_hashes":audit_hashes,"population":population,"training":{"checkpoint":checkpoint,**training_diagnostic,
            "archived_source_ns":source_ns,"paid_gate_training_wall_ns":freeze["paid_training_wall_ns"],"total_upfront_ns":upfront["gated-warm"],
            "data_only_snapshots":snapshot_report},"physical_replay":{"unique_circuits_including_training":len(physical_cache),
            "scalar_inputs_each":64,"correct_held_input_pairs_per_arm":32768*64,"manifests":manifest_report,
            "failed_held_proposal_limit":"All failed semantic submissions and accounting replayed; their literal circuit bytes were not exported. Training saved failed circuits and all returned held circuits were physically replayed."},
            "arm_stats":all_stats,"physical_work":work_report,"prefix_cost_comparison":comparison,
            "ordinary_median_total_ns":midpoint["median"][-1],
            "even_free_deployment_shortfall_ns":upfront["gated-warm"]-midpoint["median"][-1],
            "paired_choices":dict(paired_choices),"ambiguous_initial_prefixes":len(ambiguous),"self_tests":self_test(),
            "interpretation":["The learned rule is null: it never tries the fold, and its semantic trace is identical to ordinary median.",
                "No measured positive prefix repays source plus gate acquisition, even with the training cache retained.",
                "Acquisition alone exceeds ordinary median's entire stream cost; this workload could not repay even free gated deployment.",
                "The always-fold diagnostic is separate from a successfully learned conditional policy.",
                "Physical verification validates a built column once and reuses the trusted cache; terminal tests are not fresh NAND execution.",
                "The warm-default ancillary cache is gifted and excludes its acquisition; it is a favorable sensitivity check.",
                "Timings exclude referee fixture generation, experimental logging, and this independent audit as preregistered.",
                "A richer gate or different workload remains untested; ambiguous eight-label prefixes preclude always picking the first-exact route from those labels, not a perfect cost-selection impossibility."],
            "categories":{k:{"status":"pass","rationale":v} for k,v in {
                "scope_and_authority":"Owned verifier only; held audit authorized after frozen checkpoint.",
                "information_leakage":"Learner selection independently reproduced from visible prefixes only; safe snapshots retain no task-label state.",
                "split_integrity":"Direct full permutation reconstruction verifies distinct train/held mechanisms and exact sampled streams.",
                "comparator_fairness":"Common full teaching stream, common median fallback, optional one fold; cold sensitivity and adaptive ancillary explicit.",
                "artifact_and_checker":"Source hashes, freeze ancestry, twelve distinct sequential processes, physical circuits and timings match.",
                "identifiability":"Opposite first winners share eight-label prefixes; policy's available information is explicitly limited.",
                "resource_fairness":"Source plus every paid gate-training pass charged at every positive prefix; public caching counted.",
                "statistical_validity":"All preselected tasks complete; three repeats per primary arm, pointwise median and individual curves verified.",
                "representation_robustness":"Mechanism partition is invariant to all 720 input permutations; all six inputs are essential.",
                "causal_alternatives":"Null fitted gate isolates no positive fold-use effect; warm-cache and richer-gate explanations remain separated.",
                "independent_replay":"Every saved held proposal sequence and returned physical circuit replayed independently.",
                "adversarial_mutation":"Digest, gate and instruction-address corruption fixtures rejected.",
                "claim_scope":"Finite host-specific negative result; no claim of universal reuse failure or learning impossibility."}.items()},
            "audit_elapsed_s":time.perf_counter()-started,"completed_utc":datetime.now(timezone.utc).isoformat()}


def self_test():
    interpreter=prior_interpreter()
    fold={"gates":[[0,1],[5,5],[4,2],[7,6],[4,6],[9,2],[8,10]],"output":11}
    expr=["FOLD",["input",0],["input",1],["input",2]]
    raw=interpreter.expand_ast(expr,6,fold)
    circuit={"inputs":6,"gates":raw["gates"],"output":raw["output"]}
    truth=sum(interpreter.dag_value(raw,[x>>j&1 for j in range(6)])<<x for x in range(64))
    program={"expr":expr,"circuit":circuit,"truth":truth,"physical_sha256":physical_hash(circuit)}
    require(check_program(program,fold)==truth,"Independent physical verifier fixture failed")
    changed=json.loads(json.dumps(program));changed["circuit"]["gates"][-1]=[6,6]
    try:
        check_program(changed,fold)
    except AuditError:
        pass
    else:
        raise AuditError("Changed NAND operands survived the cached-program binding")
    crossed=cumulative_crossovers([3,0,2,-3],4)
    require(crossed["first_crossover"]==2 and len(crossed["transitions"])==3 and crossed["terminal_gap"]==-3,
            "A later crossover reversal was lost")
    rows=[(x,x&1) for x in range(8)]
    cp={"rule":{"feature":"ones","op":">=","limit":4}}
    require(gate_decision(cp,rows)==gate_decision(cp,rows+[(8,1),(9,0)]),"Gate read beyond the first eight labels")
    raw.update(inputs=6,constants={"zero":6,"one":7},nand_gates=len(raw["gates"]),macro_uses=1)
    physical={"circuit":raw,"physical_sha256":physical_hash(raw),"expanded_NANDs":len(raw["gates"]),"macro_uses":1}
    require(check_circuit(physical,{})==truth,"Physical-only manifest fixture failed")
    invalid=json.loads(json.dumps(physical));invalid["circuit"]["gates"][0]=[900,0]
    invalid["physical_sha256"]=physical_hash(invalid["circuit"])
    try:
        check_circuit(invalid,{})
    except AuditError:
        pass
    else:
        raise AuditError("A rehashed future-address mutation passed physical verification")
    stale=json.loads(json.dumps(physical));stale["circuit"]["output"]=0
    stale["physical_sha256"]=physical_hash(stale["circuit"])
    require(check_circuit(stale,{})!=truth,"A rehashed semantic mutation retained the expected answer")
    corrupted_cp=dict(cp,sha256="0"*64)
    require(corrupted_cp["sha256"]!=digest({k:v for k,v in corrupted_cp.items() if k!="sha256"}),"Gate corruption fixture failed")
    return {"status":"pass","actual_NAND_binding":True,"suffix_independence_fixture":True,
            "all_prefix_reversals_and_ties":True,"future_address_rejected":True,"rehashed_wrong_semantics_detected":True,
            "gate_digest_corruption_detected":True}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--artifacts",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),sort_keys=True))
    else:
        result=audit(args.artifacts)
        (args.artifacts/"audit.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps({"verdict":result["verdict"],"audit":str(args.artifacts/"audit.json"),
                          "gate":result["training"]["checkpoint"]["rule"],
                          "comparison":result["prefix_cost_comparison"]},indent=2))
