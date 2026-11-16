"""Independent parent-edit truth, minimum, physical provenance and cost audit.

Only the immutable independent two-output oracle is imported.  Source targets
are reconstructed from the actual public NAND pin edit, never from the private
grade.  The exact minimum universe is jointly-essential STAGE-frontier triples;
the original raw inputs define the end-to-end functional verification domain.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
TICKET = "PARENT-FOLD-20261115-001"
DEFAULT = ROOT / "artifacts" / TICKET / (TICKET + "-E001_consumer_edits")
ORACLE_PATH = ROOT / "research/FOLD-TWO-OUTPUT-20261115-001/audit.py"
ORACLE_SHA256 = "adbe5f223102b41091ee0a13367288a1e13929fbed6d8a05564bec25c568db1d"
PRIOR_PATH = ROOT / "research/TRIPLE-ORDER-20261115-001/audit.py"
PRIOR_SHA256 = "504a6c0ff92a2a70a37b3691d2425ee3d9fab1c080b0cd8078b3444e1b182b89"


@lru_cache(maxsize=1)
def oracle():
    if hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest()!=ORACLE_SHA256:
        raise ValueError("terminal independent oracle changed")
    spec=importlib.util.spec_from_file_location("parent_fold_independent_oracle",ORACLE_PATH)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def prior():
    if hashlib.sha256(PRIOR_PATH.read_bytes()).hexdigest()!=PRIOR_SHA256:
        raise ValueError("terminal independent split oracle changed")
    spec=importlib.util.spec_from_file_location("parent_fold_independent_split",PRIOR_PATH)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def columns(n):
    return tuple(sum(((raw>>j)&1)<<raw for raw in range(1<<n)) for j in range(n))


def checked_gates(n,gates):
    result=[]
    for i,pair in enumerate(gates):
        oracle().require(isinstance(pair,(tuple,list)) and len(pair)==2,"NAND arity")
        a,b=pair
        oracle().integer(a,"NAND lhs",0,n+1+i);oracle().integer(b,"NAND rhs",0,n+1+i)
        result.append((a,b))
    return tuple(result)


def edited_gates(case,edit=None):
    n=case["n"];gates=list(checked_gates(n,case["gates"]))
    if edit is not None:
        gate,pin,to=edit["gate"],edit["pin"],edit["to"]
        oracle().integer(gate,"edited gate",n+2+case["upstream_count"],n+1+len(gates))
        oracle().integer(pin,"edited pin",0,1);oracle().integer(to,"replacement wire",0,gate-1)
        index=gate-n-2;pair=list(gates[index])
        oracle().require(pair[pin]!=to,"edit leaves the original pin unchanged")
        pair[pin]=to;gates[index]=tuple(pair)
        differences=[(i,p) for i,(old,new) in enumerate(zip(case["gates"],gates,strict=True)) for p in range(2) if old[p]!=new[p]]
        oracle().require(differences==[(index,pin)],"edit changes more than one consumer pin")
    return tuple(gates)


def raw_words(case,edit=None):
    n=case["n"];full=(1<<(1<<n))-1
    values=[*columns(n),0,full]
    for a,b in edited_gates(case,edit):values.append(full^(values[a]&values[b]))
    return tuple(values)


def stage_words(case,edit=None,dims=None,frontier_columns=None,overrides=None):
    """Interpret the declared consumer stage on its independent Boolean cube."""
    n=case["n"];m=len(case["frontier"]);dims=m if dims is None else dims
    full=(1<<(1<<dims))-1
    start=n+2+case["upstream_count"]
    values=[0]*start;values[n+1]=full
    available={n,n+1,*case["frontier"]}
    supplied=columns(dims) if frontier_columns is None else frontier_columns
    oracle().require(len(supplied)==m,"frontier column arity")
    for wire,word in zip(case["frontier"],supplied,strict=True):values[wire]=word
    for wire,(a,b) in enumerate(edited_gates(case,edit)[case["upstream_count"]:],start):
        oracle().require(a in available and b in available,"source consumer bypasses declared frontier")
        value=full^(values[a]&values[b]);values.append((overrides or {}).get(wire,value));available.add(wire)
    oracle().require(set(case["outputs"])<=available,"source output bypasses stage")
    return tuple(values)


def frontier_domain(case,words):
    n=case["n"];frontier=case["frontier"];m=len(frontier)
    oracle().require(3<=m<=n and len(set(frontier))==m,"invalid independent frontier")
    for wire in frontier:oracle().integer(wire,"frontier wire",0,n+1+case["upstream_count"])
    assignments=tuple(sum(((words[w]>>raw)&1)<<j for j,w in enumerate(frontier)) for raw in range(1<<n))
    histogram=Counter(assignments)
    oracle().require(set(histogram)==set(range(1<<m)),"frontier is not jointly surjective")
    return assignments,dict(Counter(histogram.values()))


def project_source(case,raw,stage,assignments):
    for end in case["outputs"]:
        oracle().require(all(((raw[end]>>x)&1)==((stage[end]>>assignments[x])&1) for x in range(1<<case["n"])),
                         "edited raw circuit is not the declared stage function")


def old_bit_retention(m,targets,group,bit_word):
    group=tuple(sorted(group));outside=tuple(i for i in range(m) if i not in group)
    code=[];parts=[set(),set()]
    for local in range(8):
        base=oracle().scatter(local,group);bit=(bit_word>>base)&1
        oracle().require(all(((bit_word>>(base|oracle().scatter(v,outside)))&1)==bit for v in range(1<<len(outside))),
                         "old summary is not local to its historical triple")
        signature=tuple(tuple((t>>(base|oracle().scatter(v,outside)))&1 for t in targets) for v in range(1<<len(outside)))
        parts[bit].add(signature);code.append(bit)
    sizes=[len(p) for p in parts]
    oracle().require(all(sizes),"old historical bit must be nonconstant")
    return dict(old_bit_sufficient=max(sizes)==1,old_bit_residual_counts=sizes,
                minimum_width_with_old_bit=1+(max(sizes)-1).bit_length(),local_code=code)


def changed_cone(case,edit,before,after):
    """Exact original-value snapshot, never a previous sibling's state."""
    n=case["n"];changed=set();recomputed=different=0
    for wire,pair in enumerate(edited_gates(case,edit)[case["upstream_count"]:],n+2+case["upstream_count"]):
        if wire==edit["gate"] or any(p in changed for p in pair):
            recomputed+=1
            if before[wire]!=after[wire]:changed.add(wire);different+=1
    count=len(case["gates"])-case["upstream_count"]
    return dict(examined=count,recomputed=recomputed,changed=different,reused=count-recomputed,
                recomputed_unchanged=recomputed-different)


def support_filter(case,edit,before_stage):
    """Public dependency-only locator, stopping at the declared frontier."""
    n,m=case["n"],len(case["frontier"])
    deps={wire:1<<axis for axis,wire in enumerate(case["frontier"])}
    deps.update({n:0,n+1:0})
    for wire,(a,b) in enumerate(case["gates"][case["upstream_count"]:],n+2+case["upstream_count"]):
        oracle().require(a in deps and b in deps,"dependency walk bypasses frontier")
        deps[wire]=deps[a]|deps[b]
    structural=tuple(i for i in range(m) if deps[edit["to"]]&(1<<i))
    semantic=oracle().support(m,before_stage[edit["to"]])
    history=sorted({tuple(p["inputs"]) for p in case["pieces"]})
    return dict(structural_support=structural,semantic_support=semantic,
                structural_groups=[g for g in history if set(g)<=set(structural)],
                semantic_groups=[g for g in history if set(g)<=set(semantic)])


def physical_words(physical):
    n=physical["n"];full=(1<<(1<<n))-1
    values=[*columns(n),0,full]
    for a,b in checked_gates(n,physical["gates"]):values.append(full^(values[a]&values[b]))
    for wire in (*physical["outputs"],*physical["summary_wires"]):oracle().integer(wire,"physical endpoint",0,len(values)-1)
    return tuple(values)


def check_lift(case,answer):
    n,m=case["n"],len(case["frontier"]);circuit=answer["circuit"]
    oracle().require(answer["n"]==m and circuit.get("n",m)==m,"stage arity mismatch")
    gates=list(case["gates"][:case["upstream_count"]]);mapping=[*case["frontier"],n,n+1]
    for a,b in checked_gates(m,circuit["gates"]):
        gates.append([mapping[a],mapping[b]]);mapping.append(n+1+len(gates))
    expected=dict(n=n,gates=gates,outputs=[mapping[w] for w in circuit["outputs"]],
                  summary_wires=[mapping[w] for w in answer["summary_wires"]],frontier=case["frontier"])
    oracle().require(oracle().canonical(answer["physical"])==oracle().canonical(expected),"physical return is not the exact prefix/stage lift")
    return expected


def reuse_counts(case,answer,original_words,anchor_bit,anchor,origin=None,current_raw=None):
    """Distinguish an equal truth column from preserved source-wire ancestry."""
    words=physical_words(answer["physical"]);n=case["n"];full=(1<<(1<<n))-1
    old=original_words[anchor_bit];wanted={old,full^old}
    taps=answer["physical"]["summary_wires"]
    matching=[wire for wire in taps if words[wire] in wanted]
    original=case["gates"];returned=answer["physical"]["gates"]
    same=[True]*(n+2)
    for i,pair in enumerate(returned):
        same.append(i<len(original) and tuple(pair)==tuple(original[i]) and all(same[w] for w in pair))
    preserved=[wire for wire in matching if wire<len(original_words) and same[wire] and original_words[wire] in wanted]
    is_anchor=tuple(sorted(answer["triple"]))==tuple(sorted(anchor))
    imported=[]
    refs=(origin or {}).get("retained_source_wires")
    if refs is not None:
        oracle().require(len(refs)==len(taps),"source provenance tap count")
        current_raw=original_words if current_raw is None else current_raw
        for tap,source in zip(taps,refs,strict=True):
            if source is None:continue
            oracle().integer(source,"imported source wire",0,len(original_words)-1)
            oracle().require(words[tap]==current_raw[source],"imported source annotation disagrees with actual tap")
            if original_words[source] in wanted and current_raw[source]==original_words[source]:imported.append(source)
    return dict(queries=1,chooses_anchor=int(is_anchor),semantic_old_bit_tap=int(bool(matching)),
                anchor_and_semantic_old_bit=int(is_anchor and bool(matching)),
                source_id_old_bit_tap=int(bool(preserved)),anchor_and_source_id_old_bit=int(is_anchor and bool(preserved)),
                exact_anchor_source_id=int(anchor_bit in preserved),
                declared_imported_old_source=int(bool(imported)),declared_imported_old_source_taps=len(imported),
                semantic_matching_taps=len(matching),source_id_preserved_taps=len(preserved))


def check_snapshot(m,targets,bit_word,group,grade):
    facts=oracle().characterize(m,tuple(targets))
    require=oracle().require
    require(facts["common_essential"]==tuple(range(m)),"fixture output drops a stage input")
    ranks=[count for _,count in facts["ranks"]]
    require(list(targets)==grade["outputs"] and ranks==grade["candidate_classes"] and
            min(ranks)==grade["min_classes"] and facts["minimum_bits"]==grade["width"] and
            oracle().canonical(facts["minimum_width_triples"])==oracle().canonical(grade["minimizers"]),"snapshot/global stage grade")
    retention=old_bit_retention(m,tuple(targets),group,bit_word)
    for name in ("old_bit_sufficient","old_bit_residual_counts","minimum_width_with_old_bit"):
        require(retention[name]==grade[name],"old-bit retention grade "+name)
    witness=grade["old_bit_counterexample"]
    require(bool(witness)!=retention["old_bit_sufficient"],"old-bit counterexample presence")
    if witness:
        x,y=witness["inputs"];port=witness["port"];mask=sum(1<<j for j in group)
        require(0<=x<1<<m and 0<=y<1<<m and 0<=port<2 and not (x^y)&~mask and
                ((bit_word>>x)&1)==((bit_word>>y)&1)==witness["old_bit"] and
                ((targets[port]>>x)^(targets[port]>>y))&1,"false old-bit counterexample")
    return facts,retention


def context_family(case,grade):
    m=grade["m"];dims=m-1;independent=columns(dims);front=[0]*m
    for axis,column in zip(grade["outside"],independent[2:],strict=True):front[axis]=column
    values=stage_words(case,dims=dims,frontier_columns=front,
                       overrides={grade["anchor_bit"]:independent[0],grade["gate"]:independent[1]})
    family=prior().raw_family(dims,tuple(values[w] for w in case["outputs"]))
    return hashlib.sha256(oracle().canonical(("parent outside v1",m,family))).hexdigest()


def inspect_parent(case,grade,hint):
    require=oracle().require
    require(set(case)=={"id","n","gates","upstream_count","frontier","outputs","pieces","edits"},"public/private fields mixed")
    n,m=case["n"],len(case["frontier"])
    require(n==m+2 and m==grade["m"] and m in (7,8,9),"raw/frontier fixture dimensions")
    before_raw=raw_words(case);before_stage=stage_words(case)
    assignment,multiplicity=frontier_domain(case,before_raw)
    require(multiplicity=={4:1<<m},"frontier does not have four preimages at every stage point")
    project_source(case,before_raw,before_stage,assignment)
    group=tuple(grade["anchor"]);bit=grade["anchor_bit"]
    require(tuple(hint)==group==tuple(grade["base"]["anchor"]),"supplied triple binding")
    require(grade["base"]["anchor_bit"]==bit and case["pieces"][grade["anchor_piece"]]["bit"]==bit,"historical bit binding")
    for piece in case["pieces"]:
        piece_group=tuple(piece["inputs"])
        require(piece_group==tuple(sorted(set(piece_group))) and len(piece_group)==3,"history triple")
        require(oracle().support(m,before_stage[piece["bit"]])==piece_group,"history local bit support")
        retained=old_bit_retention(m,tuple(before_stage[w] for w in piece["ports"]),piece_group,before_stage[piece["bit"]])
        require(retained["old_bit_sufficient"],"history ports do not factor through the stated bit")
    targets=tuple(before_stage[w] for w in case["outputs"])
    original,old=check_snapshot(m,targets,before_stage[bit],group,grade["base"])
    require(original["minimum_classes"]==2 and original["minimum_width_triples"]==(group,) and
            old["local_code"]==grade["base"]["old_bit_local_values"],"original unique global optimum")
    structure=context_family(case,grade)
    require(structure==grade["structure"] and int(structure[:8],16)%3==0,"parent consumer-family domain")
    family_keys=[prior().raw_family(m,targets)]
    snapshots={None:dict(raw=before_raw,stage=before_stage,targets=targets,facts=original,retention=old)}
    edits={e["id"]:e for e in case["edits"]}
    require(len(edits)==2 and set(edits)==set(grade["edits"])==set(grade["edit_ids"]),"matched child identities")
    require(len({(e["gate"],e["pin"]) for e in edits.values()})==1,"siblings change different consumer pins")
    for eid in grade["edit_ids"]:
        edit=edits[eid];g=grade["edits"][eid]
        raw=raw_words(case,edit);stage=stage_words(case,edit);project_source(case,raw,stage,assignment)
        child=tuple(stage[w] for w in case["outputs"])
        facts,retained=check_snapshot(m,child,before_stage[bit],group,g)
        expected=2 if g["kind"]=="surviving" else 4
        require(facts["minimum_classes"]==expected and group in facts["minimum_width_triples"],"matched edited width condition")
        require(stage[bit]==before_stage[bit] and raw[bit]==before_raw[bit],"consumer edit changed the old bit itself")
        changes=[(a^b).bit_count() for a,b in zip(targets,child,strict=True)]
        require(changes==g["output_change_counts"] and all(changes) and g["changed_outputs"]==[0,1],"edited-output change grade")
        changed_gate=(before_stage[edit["gate"]]^stage[edit["gate"]]).bit_count()
        require(changed_gate==g["target_change_count"]==1<<(m-2),"matched one-pin edit strength")
        standalone=old_bit_retention(m,(before_stage[edit["to"]],),group,before_stage[bit])
        require(standalone["old_bit_sufficient"]==g["replacement_alone_old_bit_sufficient"],"contextual masking grade")
        family_keys.append(prior().raw_family(m,child))
        snapshots[eid]=dict(raw=raw,stage=stage,targets=child,facts=facts,retention=retained,
                            cone_raw=changed_cone(case,edit,before_raw,raw),cone_stage=changed_cone(case,edit,before_stage,stage),
                            public_support_filter=support_filter(case,edit,before_stage))
        require(snapshots[eid]["cone_raw"]==snapshots[eid]["cone_stage"],"raw/stage changed-cone disagreement")
    require(family_keys==grade["truth_families"] and len(set(family_keys))==3 and
            all(int(k[:8],16)%3==0 for k in family_keys),"snapshot-family split")
    return dict(before_raw=before_raw,before_stage=before_stage,raw_to_stage=assignment,snapshots=snapshots,
                structure=structure,family_keys=family_keys,prefix_multiplicity=multiplicity)


def pin_away_from_timing():
    if not hasattr(os,"sched_getaffinity"):return None
    excluded={0};path=Path("/sys/devices/system/cpu/cpu0/topology/thread_siblings_list")
    if path.is_file():
        for field in path.read_text().strip().split(','):
            edges=field.split('-');excluded.update(range(int(edges[0]),int(edges[-1])+1))
    choices=sorted(set(os.sched_getaffinity(0))-excluded)
    if choices:os.sched_setaffinity(0,{choices[-1]});return choices[-1]
    return None


def _source_fingerprints(case):
    return oracle().circuit_shape(dict(n=case["n"],gates=case["gates"],outputs=case["outputs"]),case["n"])[3]


class CheckerReplay:
    """Independent original-only expression-cache and semantic checker ledger."""

    def __init__(self,case,evidence):
        self.case,self.evidence=case,evidence
        self.layouts={tuple(p["inputs"]) for p in case["pieces"]}
        self.original_bought=False
        self.ids=_source_fingerprints(case)
        n=case["n"]
        self.history={key:evidence["before_raw"][w] for w,key in enumerate(self.ids) if w>=n+2}

    def check(self,eid,answer,receipt,base,raw_values):
        c=self.case;e=self.evidence;w=receipt;n,m=c["n"],len(c["frontier"]);prefix=c["upstream_count"]
        count=len(answer["circuit"]["gates"]);raw_rows,stage_rows=1<<n,1<<m
        expected=dict(verification_calls=1,physical_prefix_gates_compared=prefix,physical_stage_gates_linked=count,
                      returned_stage_NAND_evaluations=count,returned_stage_output_bits_compared=2*stage_rows,
                      global_minimum_alternative_groups_checked=base["alternatives_checked"],
                      raw_return_prefix_NANDs_reused=prefix,raw_return_output_bits_compared=2*raw_rows,
                      stage_support_axis_tests=2*m,stage_class_calls=1+base["alternatives_checked"],
                      original_verification_cache_hits=0)
        if eid is None:
            expected.update(original_source_target_reuses=1,original_verifications_retained=1)
        else:
            cone=e["snapshots"][eid]["cone_stage"]
            for tag in ("raw_source","source_stage"):
                expected.update({tag+"_gates_examined":cone["examined"],tag+"_NAND_evaluations":cone["recomputed"],
                                 tag+("_unchanged_NANDs_reused" if tag=="raw_source" else "_NANDs_reused"):cone["reused"],
                                 tag+"_changed_values":cone["changed"],tag+"_recomputed_unchanged_values":cone["recomputed_unchanged"]})
            expected.update(raw_source_prefix_NANDs_reused=prefix,raw_source_NAND_row_equivalents=cone["recomputed"]*raw_rows,
                            raw_stage_projection_tests=2*stage_rows,raw_stage_output_bits_covered=2*raw_rows)
        groups=[tuple(sorted(answer["triple"]))]
        if answer["width"]>1:
            groups += [g for g,_ in e["snapshots"][eid]["facts"]["ranks"] if g!=groups[0]]
        builds=hits=0
        for g in groups:
            if g in self.layouts:hits+=1
            else:builds+=1;self.layouts.add(g)
        expected.update(stage_layout_builds=builds,stage_layout_hits=hits)
        raw_ids=oracle().circuit_shape(answer["physical"],n)[3]
        start=n+2+prefix
        historical_hits=0;fresh=set()
        for wire in range(start,len(raw_ids)):
            key=raw_ids[wire]
            if key in self.history:
                historical_hits+=1
                oracle().require(raw_values[wire]==self.history[key],"stale original expression value")
            else:fresh.add(key)
        expected.update(raw_return_history_expression_lookups=count,raw_return_new_expression_identities=len(fresh),
                        raw_return_history_expression_hits=historical_hits,raw_return_history_expression_misses=count-historical_hits,
                        raw_return_NANDs_reused=prefix+historical_hits,raw_return_NAND_evaluations=count-historical_hits,
                        raw_return_NAND_row_equivalents=(count-historical_hits)*raw_rows)
        if eid is None or self.original_bought:expected["original_cache_key_bytes"]=len(oracle().canonical(answer))
        for name,value in expected.items():oracle().require(w.get(name,0)==value,"paid checker counter "+name)
        assertions=dict(exact=True,width=base["width"],classes=base["classes"],minimum_universe="jointly-essential stage-frontier triples",
                        structural_locality=True,raw_assignments=raw_rows,stage_assignments=stage_rows,raw_outputs=2,
                        raw_gates_returned=len(answer["physical"]["gates"]),stage_gates_returned=count,
                        active_stage_gates=base["active_gates"],shared_stage_gates=base["shared_gates"],
                        shared_summary_wires=base["shared_summary_wires"],raw_return_replay="history",
                        source_sha256=hashlib.sha256(oracle().canonical(c)).hexdigest(),
                        historical_checker_sha256="19b66a34415d14f73264eb2188cc984da28df250317f8aae9fa66c48438efdb0")
        for name,value in assertions.items():oracle().require(w[name]==value,"paid checker assertion "+name)
        if eid is None:self.original_bought=True


def check_history(case,evidence,row,first_parent):
    n,m=case["n"],len(case["frontier"]);g=len(case["gates"]);s=g-case["upstream_count"];p=len(case["pieces"])
    ids=_source_fingerprints(case);unique=len(set(ids[n+2:]));groups=len({tuple(x["inputs"]) for x in case["pieces"]})
    producer=dict(history_raw_NANDs=g,history_fanout_edges=2*g,history_structural_lookups=g,history_structural_aliases=g-unique,
                  history_stage_NANDs=s,history_support_unions=s,history_piece_support_tests=p*m,
                  history_group_layouts_built=groups,history_piece_residual_columns=16*p,history_piece_partition_comparisons=8*p,
                  history_pieces_validated=p,history_source_gates=g,history_frontier_inputs=m)
    oracle().require(row["history"]["producer"]==producer,"before-state producer history differs")
    checker=dict(raw_columns_built=n,stage_columns_built=m,raw_setup_NAND_evaluations=g,raw_setup_NAND_row_equivalents=g*(1<<n),
                 frontier_cell_intersections=2*((1<<m)-1),frontier_assignments_verified=1<<m,raw_frontier_assignments_covered=1<<n,
                 historical_raw_source_identities=n+2,historical_raw_expression_gates_indexed=g,
                 historical_raw_expression_duplicates=g-unique,historical_raw_expressions_retained=unique,
                 source_stage_NAND_evaluations=s,raw_stage_projection_tests=2<<m,raw_stage_output_bits_covered=2<<n,
                 historical_piece_residual_pair_checks=8*p,historical_pieces_verified=p,
                 stage_support_axis_tests=p*m,stage_layout_builds=groups,stage_layout_hits=p-groups)
    checker["historical_checker_class_loads" if first_parent else "historical_checker_class_reuses"]=1
    if first_parent:checker["historical_source_bytes_hashed"]=(ROOT/"experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables/checker.py").stat().st_size
    for name,value in checker.items():oracle().require(row["history"]["checker"].get(name,0)==value,"before checker history "+name)
    oracle().require(row["history"]["checker"]["checker_setup_cpu_ns"]<=row["history"]["checker_ns"] and
                     row["history"]["producer_ns"]+row["history"]["checker_ns"]<=row["setup_ns"],"history clock containment")


def check_edit_work(case,snapshot,edit,work):
    n,m=case["n"],len(case["frontier"]);s=len(case["gates"])-case["upstream_count"]
    expected=dict(edit_stage_entries_copied=2*(m+2+s),edit_output_table_comparisons=2,
                  edit_changed_outputs=0 if edit is None else 2)
    affected=set();edges=0
    if edit is not None:
        fanout=defaultdict(list)
        for wire,pair in enumerate(case["gates"],n+2):
            for pin in pair:fanout[pin].append(wire)
        todo=[edit["gate"]]
        while todo:
            wire=todo.pop()
            if wire in affected:continue
            affected.add(wire);edges+=len(fanout[wire]);todo.extend(fanout[wire])
        cone=snapshot["cone_stage"]
        expected.update(edit_gate_refs_copied=len(case["gates"]),edit_pin_writes=1,edit_fanout_edges=edges,
                        edit_support_unions=len(affected),edit_unchanged_descendants_skipped=len(affected)-cone["recomputed"],
                        edit_packed_NANDs=cone["recomputed"],edit_unchanged_recomputations=cone["recomputed_unchanged"],
                        edit_changed_tables=cone["changed"])
    else:expected["edit_changed_tables"]=0
    expected["edit_fanout_vertices"]=len(affected)
    for name,value in expected.items():oracle().require(work.get(name,0)==value,"fresh-parent edit work "+name)


def numeric(values):return {k:v for k,v in values.items() if type(v)in(int,float)}


def read(path):return json.loads(Path(path).read_bytes())


ARMS=("ordinary","ordinary-prior","ordinary-hint","fold","ordinary-exact","ordinary-exact-hint")


def check_bound(out):
    design=read(out/"design.json");bound=read(out/"data-bound.json")
    for name,value in design["sources"].items():oracle().require(oracle().digest(ROOT/name)==value,"changed bound source "+name)
    for name,value in bound.items():oracle().require(oracle().digest(out/name)==value,"changed bound data "+name)
    return design,bound


def public_reordering(original,rendered):
    require=oracle().require
    require(len(original)==len(rendered),"rendering parent count")
    for old,new in zip(original,rendered,strict=True):
        require({k:v for k,v in old.items() if k!="pieces"}=={k:v for k,v in new.items() if k!="pieces"},"rendering changed gates, edits or identities")
        require([p["inputs"] for p in old["pieces"]]==[p["inputs"] for p in new["pieces"]],"rendering moved a group slot")
        by=defaultdict(list)
        for p in old["pieces"]:by[tuple(p["inputs"])].append(p)
        expected={g:iter(sorted(parts,key=lambda p:p["bit"])) for g,parts in by.items()}
        require(new["pieces"]==[next(expected[tuple(p["inputs"])]) for p in old["pieces"]],"rendering is not public monotone bit-ID order")
    return dict(parents=len(original),only_complementary_record_order_changed=True)


def audit_directory(out):
    require,digest,canonical=oracle().require,oracle().digest,oracle().canonical
    design,bound=check_bound(out)
    cases=read(out/"public.json");grades=read(out/"grades.json");hints=read(out/"hints.json")
    by_id={c["id"]:c for c in cases}
    require(len(cases)==len(by_id)==len(grades)==len(hints)==36 and set(by_id)==set(grades)==set(hints),"parent panel identities")
    evidence={pid:inspect_parent(c,grades[pid],hints[pid]) for pid,c in by_id.items()}
    all_families=[k for e in evidence.values() for k in e["family_keys"]]
    structures=[e["structure"] for e in evidence.values()]
    require(len(set(all_families))==108 and len(set(structures))==36,"repeated parent family")
    prior_keys=set()
    for name in ("FOLD-TWO-OUTPUT-20261115-001","TRIPLE-ORDER-20261115-001","PROBE-WITNESS-20261115-001"):
        family={"FOLD-TWO-OUTPUT-20261115-001":"E001_joint_tables","TRIPLE-ORDER-20261115-001":"E001_rank_triples",
                "PROBE-WITNESS-20261115-001":"E001_fixed_probes"}[name]
        old=ROOT/"artifacts"/name/(name+"-"+family)
        files={"FOLD-TWO-OUTPUT-20261115-001":("primary","sensitivity"),"TRIPLE-ORDER-20261115-001":("train","held"),
               "PROBE-WITNESS-20261115-001":("calibration","held")}[name]
        for file in files:
            for row in read(old/(file+".json")):prior_keys.add(prior().raw_family(row["n"],tuple(row["outputs"])))
    require(not set(all_families)&prior_keys,"a prior public Boolean family was reused")
    support_counts=Counter();presentation=Counter();ties=Counter()
    for pid,c in by_id.items():
        g=grades[pid];first=next(p for p in c["pieces"] if p["inputs"]==hints[pid])
        presentation["parents"]+=1;presentation["first_is_anchor_source_id"]+=first["bit"]==g["anchor_bit"]
        for eid in g["edits"]:
            e=evidence[pid]["snapshots"][eid];p=e["public_support_filter"]
            support_counts["edits"]+=1
            for label in ("structural","semantic"):
                support_counts[label+"_unique"]+=len(p[label+"_groups"])==1
                support_counts[label+"_matches_anchor"]+=p[label+"_groups"]==[tuple(hints[pid])]
            ties[len(e["facts"]["minimum_width_triples"])]+=g["edits"][eid]["kind"]=="broken"
    events=[json.loads(l) for l in (out/"results.jsonl").read_text().splitlines()]
    records={};stream_hashes={}
    for event in events:
        require(event["status"]=="ok","retained worker failure")
        rec=event["result"];key=rec["arm"],rec["repeat"]
        require(key[0] in ARMS and key not in records,"unknown or duplicate stream")
        require(rec["sha256"]==digest(out/rec["file"]) and rec["cpu"]==design["cpu"],"stream hash or CPU")
        records[key]=rec;stream_hashes[rec["file"]]=rec["sha256"]
    blocks=sorted({b for _,b in records})
    require(blocks==list(range(8)) and len(records)==48,"primary timing matrix is not six by eight")
    performance={a:defaultdict(list) for a in ARMS};work={a:defaultdict(Counter) for a in ARMS}
    correct={a:Counter() for a in ARMS};produced={a:Counter() for a in ARMS}
    reuse={a:defaultdict(Counter) for a in ARMS};rebuild={a:defaultdict(Counter) for a in ARMS}
    base_answers={};physical_cache={};totals=Counter();failures=[]

    def query(pid,q,arm,block,checker,prior_query=False):
        require(q["failure"] is None and q["answer"] is not None,"failed edited query")
        c=by_id[pid];g=grades[pid];eid=None if prior_query else q["id"]
        require((q["id"] is None)==prior_query,"query original/edit identity")
        snap=evidence[pid]["snapshots"][eid];answer=q["answer"]
        physical=check_lift(c,answer)
        pkey=canonical([c["n"],snap["targets"],tuple(snap["raw"][w] for w in c["outputs"]),answer])
        if pkey not in physical_cache:
            cert,info=oracle().verify_result(len(c["frontier"]),snap["targets"],answer)
            raw=physical_words(physical)
            require(tuple(raw[w] for w in physical["outputs"])==tuple(snap["raw"][w] for w in c["outputs"]),"wrong actual raw edited program")
            physical_cache[pkey]=cert,info,raw
            totals.update(unique_stage_programs=1,executed_scalar_stage_rows=1<<len(c["frontier"]),
                          executed_scalar_stage_NANDs=info["scalar_NAND_evaluations"],
                          unique_raw_table_rows_checked=1<<c["n"],packed_raw_NANDs=len(physical["gates"]))
        cert,info,raw=physical_cache[pkey]
        checker.check(eid,answer,q["check"],cert,raw)
        require(len(canonical(answer))==q["return_bytes"],"serialized return bytes")
        require(q["cpu_ns"]>=sum(q["phases"].values()) and q["check"]["verification_cpu_ns"]<=q["phases"]["verify"],"query phase clock containment")
        require(set(q["phases"])=={"update","solve","link","verify","serialize"},"missing paid query phase")
        edit=None if prior_query else next(e for e in c["edits"] if e["id"]==eid)
        check_edit_work(c,snap,edit,q["edit_work"])
        w=q["work"]
        require(all(type(v)in(int,float) and v>=0 for v in w.values()),"negative/nonnumeric solve work")
        require(w.get("group_requests",0)==w.get("group_cache_hits",0)+w.get("group_lower_bound_cache_hits",0)+w.get("group_trials",0),"exact partition requests/cache work")
        require(w.get("group_trials",0)==w.get("group_exact_partitions",0)+w.get("group_bound_rejections",0),"failed partition work omitted")
        require(w.get("returned_table_comparisons",0)>=2,"both output table comparisons")
        origin=q.get("origin",{})
        if origin.get("summary_truths") is not None:require(origin["summary_truths"]==info["code_truths"],"tap truth provenance")
        identities=canonical(answer)
        key=arm,pid,eid
        if key in base_answers:require(base_answers[key]==identities,"reversed branches/repeats changed physical result")
        else:base_answers[key]=identities
        totals.update(covered_queries=1,covered_raw_assignments=1<<c["n"],covered_raw_output_bits=2<<c["n"],
                      covered_stage_assignments=1<<len(c["frontier"]))
        if not prior_query and block==0:
            role=g["edits"][eid]["kind"]
            retained=reuse_counts(c,answer,evidence[pid]["before_raw"],g["anchor_bit"],g["anchor"],origin,snap["raw"])
            reuse[arm][role].update(retained)
            flags=origin.get("output_reuse") or []
            require(not flags or len(flags)==2 and set(flags)<={"source","semantic_alias","synthesized"},"output reuse provenance")
            synthesised=sum(f=="synthesized" for f in flags)
            require(w.get("consumer_functions_repaired",0)>=synthesised,"unpaid final consumer repair")
            cls=f"{role}/{g['stratum']}"
            rebuild[arm][cls].update(queries=1,queries_repaired=int(w.get("consumer_functions_repaired",0)>0),
                                    final_repaired_outputs=synthesised,all_consumer_repairs=w.get("consumer_functions_repaired",0),
                                    source_old_bit_selected=int(first_piece(c,hints[pid])["bit"]==g["anchor_bit"]))
        return cert

    for (arm,block),rec in sorted(records.items(),key=lambda kv:(kv[0][1],ARMS.index(kv[0][0]))):
        with gzip.open(out/rec["file"],"rt") as f:rows=[json.loads(l) for l in f]
        expected_order=list(by_id)
        if block%2:expected_order.reverse()
        require([r["id"] for r in rows]==expected_order and rec["parents"]==36,"parent order/coverage")
        costs=Counter(startup=rec["startup_ns"],total=rec["cpu_ns"],wall=rec["wall_ns"])
        require(rec["cpu_ns"]>=rec["startup_ns"]+sum(r["cpu_ns"] for r in rows),"whole-stream paid CPU")
        for pos,row in enumerate(rows):
            pid=row["id"];case=by_id[pid];g=grades[pid]
            require(row["failure"] is None,"parent initialization failure")
            check_history(case,evidence[pid],row,pos==0)
            checker=CheckerReplay(case,evidence[pid])
            costs["history"]+=row["setup_ns"];costs["producer history"]+=row["history"]["producer_ns"]
            costs["checker history"]+=row["history"]["checker_ns"]
            costs[f"seed {g['seed']}"]+=row["cpu_ns"];costs[f"m={len(case['frontier'])}"]+=row["cpu_ns"]
            if block==0:
                work[arm]["history.solver"].update(numeric(row["history"]["producer"]))
                work[arm]["history.checker"].update(numeric(row["history"]["checker"]))
            prior_cost=0
            if row["prior"] is not None:
                require(arm=="ordinary-prior","unearned original global certificate")
                query(pid,row["prior"],arm,block,checker,True)
                prior_cost=row["prior"]["cpu_ns"];costs["prior purchase"]+=prior_cost
            else:require(arm!="ordinary-prior","missing paid original optimization")
            order=[e["id"] for e in case["edits"]]
            if block%2:order.reverse()
            require([q["id"] for q in row["edits"]]==order,"sibling call order")
            require(row["cpu_ns"]>=row["setup_ns"]+prior_cost+sum(q["cpu_ns"] for q in row["edits"]),"parent total omits work")
            for q in row["edits"]:
                query(pid,q,arm,block,checker)
                target=g["edits"][q["id"]];role=target["kind"]
                costs[role]+=q["cpu_ns"]
                for name,elapsed in q["phases"].items():costs[role+"."+name]+=elapsed;costs["edits."+name]+=elapsed
                if block==0:
                    correct[arm][role]+=1;produced[arm][role+".physical gates"]+=len(q["answer"]["physical"]["gates"])
                    produced[arm][role+".bytes"]+=q["return_bytes"]
                    for label,field in (("solver","work"),("edit","edit_work"),("checker","check")):work[arm][role+"."+label].update(numeric(q[field]))
        for key,value in costs.items():performance[arm][key].append((block,value))
    series={a:{k:[v for _,v in sorted(rows)] for k,rows in per.items()} for a,per in performance.items()}
    ms={a:{k:median(vals)/1e6 for k,vals in per.items()} for a,per in series.items()}
    best=min(("ordinary","ordinary-prior","ordinary-exact"),key=lambda a:ms[a]["total"])
    savings=[a-b for a,b in zip(series[best]["total"],series["fold"]["total"],strict=True)]
    wins=sum(v>0 for v in savings);lower=ms["fold"]["total"]<ms[best]["total"]
    decision="train" if lower and wins>=7 else "repeat timing" if lower else "stop"
    computed=dict(ticket=TICKET,bounded=True,parents=36,edits=72,timing_blocks=8,failures=failures,
                  correct_unique=correct,best_unhinted=best,median_ms=ms,series_ns=series,work_first_block=work,
                  program_totals_first_block=produced,paid_saving_ms=ms[best]["total"]-ms["fold"]["total"],
                  paired_savings_ms=[v/1e6 for v in savings],fold_wins=wins,decision=decision)
    official=read(out/("result.json" if (out/"result.json").is_file() else "timing-first-eight.json"))
    for name,value in computed.items():require(canonical(official[name])==canonical(value),"assessor arithmetic "+name)
    return dict(verdict="PASS",artifact_directory=str(out),source_binding_sha256=digest(out/"design.json"),
                data_binding_sha256=digest(out/"data-bound.json"),streams=stream_hashes,all_returns_stable=True,
                replay=dict(totals),unique_query_reuse={a:{k:dict(v) for k,v in r.items()} for a,r in reuse.items()},
                unique_query_repairs={a:{k:dict(v) for k,v in r.items()} for a,r in rebuild.items()},
                public_support_filter=dict(support_counts),first_history_piece=dict(presentation),broken_minimum_tie_histogram=dict(ties),
                timing={**computed,"median_paired_saving_ms":median(savings)/1e6,
                        "threshold":"lower whole-stream median AND at least7/8 paired wins"})


def first_piece(case,hint):return next(p for p in case["pieces"] if p["inputs"]==list(hint))


def precision_replay(out,primary):
    path=out/"sensitivity/results.jsonl"
    if not path.is_file():return dict(available=False)
    events=[json.loads(l) for l in path.read_text().splitlines()]
    if len(events)!=48:return dict(available=True,complete=False,streams=len(events))
    originals={};totals={a:{} for a in ARMS};digests={}
    def operations(values):return {k:v for k,v in values.items() if not k.endswith("_ns") and not k.endswith("_seconds")}
    for arm in ARMS:
        with gzip.open(out/f"0-{arm}.jsonl.gz","rt") as f:
            originals[arm]={r["id"]:r for r in (json.loads(l) for l in f)}
    for event in events:
        oracle().require(event["status"]=="ok","precision process failure")
        s=event["result"];arm,block=s["arm"],s["repeat"]
        oracle().require(arm in ARMS and 8<=block<16 and block not in totals[arm],"precision matrix")
        oracle().require(oracle().digest(out/s["file"])==s["sha256"],"precision digest")
        digests[s["file"]]=s["sha256"]
        with gzip.open(out/s["file"],"rt") as f:rows=[json.loads(l) for l in f]
        oracle().require(len(rows)==36 and {r["id"] for r in rows}==set(originals[arm]),"precision parent set")
        oracle().require(s["cpu_ns"]>=s["startup_ns"]+sum(r["cpu_ns"] for r in rows),"precision paid CPU")
        for row in rows:
            old=originals[arm][row["id"]]
            oracle().require(row["failure"] is None,"precision parent failure")
            original_queries={q["id"]:q for q in old["edits"]}
            if old["prior"]:original_queries[None]=old["prior"]
            queries=list(row["edits"])+([row["prior"]] if row["prior"] else [])
            oracle().require({q["id"] for q in queries}==set(original_queries),"precision query set")
            for q in queries:
                p=original_queries[q["id"]]
                oracle().require(q["failure"] is None and q["answer"]==p["answer"] and q.get("origin")==p.get("origin") and
                                 q["edit_work"]==p["edit_work"] and operations(q["check"])==operations(p["check"]) and
                                 operations(q["work"])==operations(p["work"]),"precision changed logical work or answer")
                oracle().require(q["cpu_ns"]>=sum(q["phases"].values()),"precision phase total")
        totals[arm][block]=s["cpu_ns"]
    oracle().require(all(set(v)==set(range(8,16)) for v in totals.values()),"incomplete precision arms")
    med={a:median(v.values())/1e6 for a,v in totals.items()}
    best=primary["timing"]["best_unhinted"]
    deltas=[totals[best][b]-totals["fold"][b] for b in range(8,16)]
    combined={a:primary["timing"]["series_ns"][a]["total"]+[totals[a][b] for b in range(8,16)] for a in ARMS}
    joined=[a-b for a,b in zip(combined[best],combined["fold"],strict=True)]
    return dict(available=True,complete=True,streams=digests,all_programs_and_operation_counts_identical=True,
                primary_benchmark=best,median_total_ms=med,
                saving_difference_of_medians_ms=med[best]-med["fold"],median_paired_saving_ms=median(deltas)/1e6,
                paired_wins=sum(v>0 for v in deltas),paired_savings_ms=[v/1e6 for v in deltas],
                combined_16=dict(saving_difference_of_medians_ms=(median(combined[best])-median(combined["fold"]))/1e6,
                                 median_paired_saving_ms=median(joined)/1e6,paired_wins=sum(v>0 for v in joined)),
                nonclaim="Post-primary timing precision only; the registered primary decision is unchanged.")


def audit_all(out,rendering=None):
    audit_cpu=pin_away_from_timing()
    primary=audit_directory(out)
    report=dict(schema_version=1,ticket=TICKET,verdict="PASS",auditor_sha256=oracle().digest(__file__),
                terminal_oracle_sha256=ORACLE_SHA256,terminal_split_oracle_sha256=PRIOR_SHA256,audit_cpu=audit_cpu,
                self_test=self_test(),primary=primary,precision=precision_replay(out,primary),
                independence="No producer/checker imports. Actual single-pin raw and stage targets, literal residual minima, scalar stage circuits, full packed raw-domain circuits, original-only expression identities and all paid clocks are independently replayed.",
                factoring="Only identical asserted programs bound to identical actual targets reuse an earlier truth-table execution; all returns and counter ledgers are checked.",
                nonclaims=["Minimum width is global only over jointly-essential stage-frontier triples, not arbitrary raw triples.",
                           "Semantic old-bit equality, imported source provenance, preserved numeric source identity and avoided runtime work are distinct.",
                           "Hints locate a historical triple; public support containment already identifies it on this fixture family.",
                           "Timing repetitions and equivalent history renderings reuse the same36 parents and72 edits."])
    if rendering is not None:
        equivalent=public_reordering(read(out/"public.json"),read(rendering/"public.json"))
        previous=read(out/"grades.json");current=read(rendering/"grades.json")
        for pid,old in previous.items():
            revised=deepcopy(old)
            revised["anchor_piece"]=current[pid]["anchor_piece"]
            revised["base"]["anchor_piece"]=current[pid]["base"]["anchor_piece"]
            oracle().require(revised==current[pid],"rendering changed private facts beyond public-list index")
        rd=read(rendering/"design.json")
        oracle().require(rd["previous_binding"]==oracle().digest(out/"data-bound.json"),"rendering previous binding")
        report["explicit_piece"]=audit_directory(rendering)
        report["explicit_piece"]["equivalence"]=equivalent
        report["explicit_piece"]["interpretation"]="Favorable public ordering bound after the primary result; dependent timing on identical circuits, not fresh held tasks."
        report["explicit_piece"]["precision"]=precision_replay(rendering,report["explicit_piece"])
    return report


def self_test():
    n=5;gates=[]
    def nand(a,b):gates.append([a,b]);return n+1+len(gates)
    def xor(a,b):
        q=nand(a,b);return nand(nand(a,q),nand(b,q))
    q=nand(0,1);ab=nand(q,q);h=xor(ab,2);inv=nand(h,h)
    left=nand(h,3);right=nand(h,4)
    case=dict(id="hand",n=n,gates=gates,upstream_count=0,frontier=list(range(n)),outputs=[left,right],
              pieces=[dict(inputs=[0,1,2],bit=h,ports=[h,inv])],edits=[dict(id="child",gate=left,pin=1,to=0)])
    before=raw_words(case);st=stage_words(case);assignments,_=frontier_domain(case,before);project_source(case,before,st,assignments)
    edit=case["edits"][0];after=raw_words(case,edit);ast=stage_words(case,edit);project_source(case,after,ast,assignments)
    targets=tuple(ast[w] for w in case["outputs"])
    facts=oracle().characterize(n,targets)
    oracle().require(facts["minimum_bits"]==2 and facts["minimum_classes"]==3,"one-pin child has three, not four, classes")
    retention=old_bit_retention(n,targets,(0,1,2),st[h])
    oracle().require(not retention["old_bit_sufficient"] and retention["minimum_width_with_old_bit"]==2,"old bit may survive as part of a refinement")
    altered=[list(p) for p in edited_gates(case,edit)]
    answer=dict(status="exact",n=n,triple=[0,1,2],width=2,class_count=3,summary_wires=[h,0],
                circuit=dict(n=n,gates=altered,outputs=case["outputs"]))
    answer["physical"]=dict(n=n,gates=altered,outputs=case["outputs"],summary_wires=[h,0],frontier=list(range(n)))
    check_lift(case,answer);oracle().verify_result(n,targets,answer)
    reuse=reuse_counts(case,answer,before,h,(0,1,2))
    oracle().require(reuse["semantic_old_bit_tap"]==reuse["source_id_old_bit_tap"]==1,"old bit source retention")
    def moved(w):return w+1 if w>=n+2 else w
    rebuilt=deepcopy(answer)
    rebuilt["circuit"]={"n":n,"gates":[[0,0]]+[[moved(a),moved(b)] for a,b in altered],
                        "outputs":[moved(w) for w in case["outputs"]]}
    rebuilt["summary_wires"]=[moved(h),0]
    rebuilt["physical"]={"n":n,"gates":rebuilt["circuit"]["gates"],"outputs":rebuilt["circuit"]["outputs"],
                          "summary_wires":rebuilt["summary_wires"],"frontier":list(range(n))}
    check_lift(case,rebuilt);oracle().verify_result(n,targets,rebuilt)
    again=reuse_counts(case,rebuilt,before,h,(0,1,2))
    oracle().require(again["semantic_old_bit_tap"]==1 and again["source_id_old_bit_tap"]==0,
                     "recomputed equal bit was mistaken for source-ID retention")
    # Distinct, balanced frontier columns are still not jointly independent.
    a,b=columns(3)[:2];bad=dict(n=3,frontier=[0,1,5],upstream_count=1)
    try:frontier_domain(bad,(a,b,columns(3)[2],0,255,a^b))
    except ValueError:pass
    else:raise AssertionError("dependent frontier admitted")
    wrong=deepcopy(answer);wrong["physical"]["outputs"]=list(reversed(wrong["physical"]["outputs"]))
    try:check_lift(case,wrong)
    except ValueError:pass
    else:raise AssertionError("wrong physical endpoint admitted")
    return dict(one_pin_edit_classes=3,old_bit_refinement_width=2,semantic_and_source_id_reuse_distinct=True,
                dependent_frontier_rejected=True,wrong_physical_binding_rejected=True,
                terminal_cut_fixtures=oracle().self_test())


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--artifacts",type=Path,default=DEFAULT)
    parser.add_argument("--include-rendering",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=self_test() if args.self_test else audit_all(args.artifacts.resolve(),args.include_rendering.resolve() if args.include_rendering else None)
    if args.output:
        oracle().require(args.output.resolve()==DEFAULT/"audit.json","output outside owned receipt")
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    summary=result if args.self_test else {"verdict":result["verdict"],"primary":{k:result["primary"]["timing"][k] for k in
             ("best_unhinted","paid_saving_ms","median_paired_saving_ms","fold_wins","decision")},"replay":result["primary"]["replay"]}
    if not args.self_test and "explicit_piece"in result:summary["explicit_piece"]={k:result["explicit_piece"]["timing"][k] for k in
             ("best_unhinted","paid_saving_ms","median_paired_saving_ms","fold_wins","decision")}
    print(json.dumps(summary,indent=2,sort_keys=True))
