"""Independent bounded L_path check from the mathematical specification.

No EVERY-RAY or REACH producer module is imported or read.  A copy is inlined
from the description itself, its side calls use an independently iterated
greatest fixed point, and all Boolean assignments are enumerated.  Minimal
non-shattered member sets are enumerated in increasing size (at most seven).
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import resource
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
DATA = ROOT / "experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex"
INF = 10**9
MAX_N = 22
MAX_MEMBERS = 7
PANEL_POSITIONS = [0, 1, 3, 4, 5, 8, 9, 11, 13, 14, 16, 17, 20, 23, 24, 27, 30, 44]


def selfholding(defs, i):
    return any(c == "SELF" for c, a in defs[i][2])


def usual(defs):
    out = json.loads(json.dumps(defs))
    for k, own, calls in out:
        if any(c == "SELF" and sorted(a) == [0, 1, 2] for c, a in calls):
            calls.append(["K", [0, 1, 2]])
    return out


def relation(defs, i, prior, earlier):
    """Existential port relation, using complete local truth tables."""
    k, own, calls = defs[i]
    values = np.arange(1 << (k + own), dtype=np.uint32)
    ok = np.ones(len(values), dtype=bool)
    for callee, args in calls:
        idx = np.zeros(len(values), dtype=np.uint32)
        for j, v in enumerate(args):
            idx |= ((values >> v) & 1) << j
        if callee == "K":
            ok &= (idx != 0) & (idx != 7)
        else:
            allowed = prior[i] if callee == "SELF" else earlier[callee]
            lookup = np.array([(allowed >> s) & 1 for s in range(1 << len(args))], dtype=bool)
            ok &= lookup[idx]
    ans = 0
    for s in np.unique(values[ok] & ((1 << k) - 1)):
        ans |= 1 << int(s)
    return ans


def greatest_fixed_point(defs):
    sh = [i for i in range(len(defs)) if selfholding(defs, i)]
    prior = {i: (1 << (1 << defs[i][0])) - 1 for i in sh}
    history = [dict(prior)]
    for _ in range(100):
        allrels = []
        for i in range(len(defs)):
            allrels.append(relation(defs, i, prior, allrels))
        nxt = {i: allrels[i] for i in sh}
        assert all((nxt[i] | prior[i]) == prior[i] for i in sh)
        history.append(dict(nxt))
        if nxt == prior:
            return allrels, history
        prior = nxt
    raise AssertionError("greatest fixed point did not settle")


def choose_ray(defs):
    """First selfholding definition reached by main's nonself expansion."""
    def descend(i):
        if selfholding(defs, i):
            return i
        for c, args in defs[i][2]:
            if isinstance(c, int):
                got = descend(c)
                if got is not None:
                    return got
        return None
    return descend(len(defs) - 1)


def block(defs, relations, ray, top):
    """Inline nonself macros; preserve distinct occurrences and local identity."""
    k = defs[top][0]
    n = k
    constraints, choices, trace = [], [], []

    def expand(i, actual, at):
        nonlocal n
        arity, own, calls = defs[i]
        env = list(actual) + list(range(n, n + own))
        n += own
        trace.append(dict(definition=i, occurrence=at, env=env))
        for j, (callee, args) in enumerate(calls):
            aa = tuple(env[x] for x in args)
            if callee == "K":
                constraints.append(("NAE", aa, 126))
            elif callee == "SELF":
                assert i == ray
                choices.append(dict(arguments=aa, source_definition=i, occurrence=at + [j], source_call=j))
            elif selfholding(defs, callee):
                if callee == ray:
                    choices.append(dict(arguments=aa, source_definition=i, occurrence=at + [j], source_call=j))
                else:
                    constraints.append(("SIDE", aa, relations[callee]))
            else:
                expand(callee, aa, at + [j])

    expand(top, tuple(range(k)), [])
    return dict(ports=k, n=n, own=n-k, constraints=constraints, choices=choices, expansion_trace=trace)


def flatten(main, recurring, path, side_relation):
    constraints = []
    n = main["n"]
    copies = []
    target_own = []
    incoming = list(range(main["ports"]))
    for level in range(len(path) + 1):
        b = main if level == 0 else recurring
        if level == 0:
            env = list(range(b["n"]))
        else:
            env = list(incoming) + list(range(n, n + b["own"]))
            n += b["own"]
        target_own = env[b["ports"]:]
        for kind, aa, rel in b["constraints"]:
            constraints.append((kind, tuple(env[v] for v in aa), rel))
        chosen = path[level] if level < len(path) else None
        for j, item in enumerate(b["choices"]):
            aa = tuple(env[v] for v in item["arguments"])
            if j == chosen:
                incoming = aa
            else:
                constraints.append(("SIDE-RAY", aa, side_relation))
        copies.append(dict(level=level, env=env, own=target_own, chosen_call=chosen,
                           outgoing_arguments=list(incoming) if chosen is not None else None))
    return n, constraints, list(range(main["ports"])), target_own, copies


def satisfying_assignments(n, constraints):
    """Literal complete truth-table enumeration, without a solver or DP."""
    values = np.arange(1 << n, dtype=np.uint32)
    ok = np.ones(len(values), dtype=bool)
    for kind, args, relation_mask in constraints:
        ix = np.zeros(len(values), dtype=np.uint32)
        for j, v in enumerate(args):
            ix |= ((values >> v) & 1) << j
        lookup = np.array([(relation_mask >> s) & 1 for s in range(1 << len(args))], dtype=bool)
        ok &= lookup[ix]
    return values[ok]


def projection(values, members):
    projected = np.zeros(len(values), dtype=np.uint32)
    for j, v in enumerate(members):
        projected |= ((values >> v) & 1) << j
    present = np.zeros(1 << len(members), dtype=bool)
    present[projected] = True
    return present


def minimum_bond(values, n, top_ports, target_own, cap=MAX_MEMBERS):
    """Enumerate all sets by size; prune only supersets of proved failures."""
    if not len(values):
        return None, dict(reason="no allowed state (K3 fails)", subsets_evaluated=0)
    if len(values) == 1 << n:
        return None, dict(reason="whole relation full", subsets_evaluated=0)
    top_mask = sum(1 << v for v in top_ports)
    target_mask = sum(1 << v for v in target_own)
    minimal_nonshattered = []
    subsets_evaluated = 0
    skipped_supersets = 0
    for size in range(1, min(cap, n) + 1):
        for members in itertools.combinations(range(n), size):
            mask = sum(1 << v for v in members)
            if any(mask & bad == bad for bad in minimal_nonshattered):
                skipped_supersets += 1
                continue
            present = projection(values, members)
            subsets_evaluated += 1
            if present.all():
                continue
            # Every smaller non-shattered set was encountered already, so this
            # set is minimal. Explicitly verify every single deletion anyway.
            deletion_counts = [int(projection(values, members[:j]+members[j+1:]).sum()) for j in range(size)]
            assert all(c == 1 << (size - 1) for c in deletion_counts)
            minimal_nonshattered.append(mask)
            if mask & top_mask and mask & target_mask:
                return size, dict(members=members, allowed_projection=np.flatnonzero(present).tolist(),
                                  forbidden_projection=np.flatnonzero(~present).tolist(),
                                  deletion_projection_counts=deletion_counts,
                                  subsets_evaluated=subsets_evaluated,
                                  skipped_supersets=skipped_supersets,
                                  prior_minimal_nonshattered_masks=minimal_nonshattered[:-1])
    return None, dict(reason=f"no endpoint bond up to {cap}", subsets_evaluated=subsets_evaluated,
                      skipped_supersets=skipped_supersets,
                      minimal_nonshattered_masks=minimal_nonshattered)


def compare(value, reference):
    if value is None:
        return reference > MAX_MEMBERS
    return value == reference


def controls():
    def check_case(name, n, cs, endpoints, wanted):
        vals = satisfying_assignments(n, cs)
        value, witness = minimum_bond(vals, n, *endpoints)
        assert value == wanted, (name, value, wanted)
        wrong = (wanted + 1) if wanted is not None else 3
        assert not compare(value, wrong)
        return dict(name=name, n=n, constraints=cs, top_ports=endpoints[0], target_own=endpoints[1],
                    satisfying_assignments=vals.tolist(), value=value, wanted=wanted,
                    wrong_value=wrong, wrong_rejected=True, witness=witness)
    out = []
    out.append(check_case("NAE with shared port", 3, [("NAE",(0,1,2),126)], ([0],[2]), 3))
    out.append(check_case("duplicate SELF-side relation preserves identity", 3,
                          [("SIDE",(0,1,2),126),("SIDE",(0,1,2),126)], ([0],[2]),3))
    out.append(check_case("repeated argument creates two-member bond",2,
                          [("SIDE",(0,0,1),126)],([0],[1]),2))
    out.append(check_case("free endpoint is not made dependent by local NAE",4,
                          [("NAE",(0,1,2),126)],([0],[3]),None))
    # Duplicated continuing calls are separate choices; the nonchosen one is
    # still a side condition, including when both have identical arguments.
    ds=usual([[3,1,[["K",[0,1,3]],["SELF",[0,2,3]],["SELF",[0,2,3]]]]])
    rr, hist=greatest_fixed_point(ds)
    b=block(ds,rr,0,0)
    flattened=[flatten(b,b,(j,),rr[0]) for j in range(2)]
    assert flattened[0][1] == flattened[1][1]
    assert sum(k == "SIDE-RAY" for k,a,r in flattened[0][1]) == 3
    out.append(dict(name="duplicate continuing call keeps nonchosen constraint", passed=True,
                    definitions=ds, fixed_point=rr, constraints=flattened[0][1]))
    return out


def selected_families():
    panel=json.loads((DATA/"gates_full/brute_panel.json").read_text())
    old_keys=set()
    def keys(obj):
        if isinstance(obj,dict):
            if "key" in obj:
                old_keys.add(obj["key"])
            for v in obj.values():
                keys(v)
        elif isinstance(obj,list):
            for v in obj:
                keys(v)
    keys(panel)
    rows={}
    for name in ["G","N","B","B_resume","phase2"]:
        for line in (DATA/f"sample/{name}.jsonl").read_text().splitlines():
            row=json.loads(line)
            if "key" in row:
                row["independent_source_file"]=name+".jsonl"
                rows[row["key"]]=row
    candidates=[r for r in rows.values() if r.get("n_defs",1)>1 and r["key"] not in old_keys and "L_path" in r]
    candidates.sort(key=lambda r:(max(r.get("main_block_size",99),r.get("s_block_size",99)),
                                  r.get("main_own",99)+3*r.get("s_own",99),r.get("c",99),r["key"]))
    return [(i,candidates[i]) for i in PANEL_POSITIONS], len(old_keys),len(candidates)


def run(depth, limit):
    started=time.time()
    control_rows=controls()
    selected,excluded_count,candidate_count=selected_families()
    if limit:
        selected=selected[:limit]
    result=dict(interface=dict(question="Independent direct least endpoint minimal non-shattered sets along all paths",
                               evidence_stage="bounded independent referee recomputation",max_distinctions=MAX_N,
                               max_members=MAX_MEMBERS,depths=list(range(1,depth+1)),
                               forbidden_inputs="EVERY-RAY and REACH producer Python; no imports of any project module",
                               selection="fixed positions in all new several-definition sample families ordered max block, main_own+3*s_own, call count, key",
                               panel_positions=PANEL_POSITIONS,old_panel_keys_excluded=excluded_count,
                               new_several_definition_candidates=candidate_count),
                controls=control_rows,families=[],started_unix=started)
    output=HERE/"direct_brute_results.json"
    def save():
        result["seconds"]=round(time.time()-started,6)
        result["peak_rss_kib"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        output.write_text(json.dumps(result,indent=2)+"\n")
    for position,row in selected:
        key=row["key"]
        original=json.loads(key)
        ds=usual(original)
        ray=choose_ray(ds)
        rr,hist=greatest_fixed_point(ds)
        main=block(ds,rr,ray,len(ds)-1)
        recurring=block(ds,rr,ray,ray)
        expected=dict(S=ray,main_block_size=main["n"],main_own=main["own"],
                      s_block_size=recurring["n"],s_own=recurring["own"],c=len(recurring["choices"]))
        metadata_matches={k:row.get(k)==v for k,v in expected.items()}
        assert all(metadata_matches.values()),(key,expected,{k:row.get(k)for k in expected})
        f=dict(panel_position=position,key=key,definitions=original,usual_definitions=ds,
               sample_source=row["independent_source_file"],sample_class=row.get("class"),
               sample_status=row.get("status"),sample_L_path=row["L_path"][:depth],
               sample_L_path_uncarried=row.get("L_path_uncarried",[])[:depth],
               metadata=expected,metadata_matches=metadata_matches,
               independent_fixed_point=rr,fixed_point_iterations=hist,
               main_block=main,recurring_block=recurring,depths=[])
        result["families"].append(f)
        for s in range(1,depth+1):
            d=dict(depth=s,expected_paths=len(main["choices"])*len(recurring["choices"])**(s-1),paths=[],skipped=[])
            f["depths"].append(d)
            for entry in range(len(main["choices"])):
                for choices in itertools.product(range(len(recurring["choices"])),repeat=s-1):
                    path=(entry,)+choices
                    n,cs,top,target,copies=flatten(main,recurring,path,rr[ray])
                    if n>MAX_N:
                        d["skipped"].append(dict(path=path,n=n,reason="over 22 distinctions"))
                        continue
                    vals=satisfying_assignments(n,cs)
                    value,witness=minimum_bond(vals,n,top,target)
                    carried=bool(set(copies[-1]["env"][:3])&set(top))
                    d["paths"].append(dict(path=path,n=n,total_assignments=1<<n,
                                            allowed_assignment_count=len(vals),
                                            allowed_assignment_sha256=hashlib.sha256(vals.astype("<u4").tobytes()).hexdigest(),
                                            allowed_assignments=vals.tolist() if len(vals)<=128 else None,
                                            first_assignments=vals[:16].tolist(),last_assignments=vals[-16:].tolist(),
                                            constraints=cs,copies=copies,carried=carried,
                                            minimum=value,witness=witness))
            finite=[p["minimum"] for p in d["paths"] if p["minimum"] is not None]
            finite_unc=[p["minimum"] for p in d["paths"] if p["minimum"] is not None and not p["carried"]]
            d["minimum"]=min(finite) if finite else None
            d["minimum_uncarried"]=min(finite_unc) if finite_unc else None
            d["complete"]=len(d["paths"])==d["expected_paths"] and not d["skipped"]
            d["row_value"]=row["L_path"][s-1]
            d["match"]=compare(d["minimum"],d["row_value"]) if d["complete"] else None
            u=row.get("L_path_uncarried",[])
            d["uncarried_row_value"]=u[s-1] if len(u)>=s else None
            d["uncarried_match"]=compare(d["minimum_uncarried"],u[s-1]) if d["complete"] and len(u)>=s else None
            print(json.dumps(dict(panel_position=position,depth=s,paths=len(d["paths"]),complete=d["complete"],
                                  minimum=d["minimum"],row=d["row_value"],match=d["match"],
                                  uncarried_match=d["uncarried_match"])),flush=True)
            save()
    cells=[d for f in result["families"] for d in f["depths"]]
    result["summary"]=dict(families=len(result["families"]),complete_depth_cells=sum(d["complete"]for d in cells),
                           paths=sum(len(d["paths"])for d in cells),skipped_paths=sum(len(d["skipped"])for d in cells),
                           mismatches=sum(d["match"] is False for d in cells),
                           uncarried_mismatches=sum(d["uncarried_match"] is False for d in cells),
                           direct_constraints_evaluated=sum(len(p["constraints"])for d in cells for p in d["paths"]),
                           assignment_rows_enumerated=sum(p["total_assignments"]for d in cells for p in d["paths"]),
                           sample_classes=dict(Counter(f["sample_class"]for f in result["families"])))
    save()
    print(json.dumps(result["summary"],sort_keys=True),flush=True)


def moving_suffix_fixture(depth):
    """Check the quantifier issue on the small fixture named by the lead."""
    started=time.time()
    original=[[3,2,[["K",[1,3,4]],["SELF",[2,0,4]],["SELF",[0,3,4]]]]]
    ds=usual(original)
    rr,hist=greatest_fixed_point(ds)
    b=block(ds,rr,0,0)
    f=dict(definitions=original,usual_definitions=ds,independent_fixed_point=rr,
           fixed_point_iterations=hist,block=b,depths=[])
    for s in range(1,depth+1):
        d=dict(depth=s,paths=[],expected_paths=2**s)
        for path in itertools.product(range(2),repeat=s):
            n,cs,top,target,copies=flatten(b,b,path,rr[0])
            if n>MAX_N:
                raise AssertionError("fixture depth exceeds assignment ceiling")
            vals=satisfying_assignments(n,cs)
            value,witness=minimum_bond(vals,n,top,target)
            carried=bool(set(copies[-1]["env"][:3])&set(top))
            heights={0:0,1:0,2:0}
            for kind,aa,rel in cs:
                if kind == "NAE":
                    anchor,x,y=aa
                    assert anchor in heights and x not in heights and y not in heights
                    heights[x]=heights[y]=heights[anchor]+1
                else:
                    assert rel == 255
            assert len({heights[v] for v in target}) == 1
            ancestry_height=heights[target[0]]
            predicted_minimum=ancestry_height+2
            formula_match=compare(value,predicted_minimum)
            assert formula_match,(path,value,predicted_minimum)
            d["paths"].append(dict(path=path,n=n,total_assignments=1<<n,
                                    allowed_assignment_count=len(vals),
                                    allowed_assignment_sha256=hashlib.sha256(vals.astype("<u4").tobytes()).hexdigest(),
                                    constraints=cs,copies=copies,carried=carried,minimum=value,witness=witness,
                                    ancestry_height=ancestry_height,predicted_minimum=predicted_minimum,
                                    height_formula_matches=formula_match))
        finite=[p["minimum"]for p in d["paths"]if p["minimum"]is not None]
        unc=[p["minimum"]for p in d["paths"]if p["minimum"]is not None and not p["carried"]]
        d["minimum"]=min(finite)if finite else None
        d["minimum_uncarried"]=min(unc)if unc else None
        d["optimal_uncarried_paths"]=[p["path"]for p in d["paths"]if not p["carried"] and p["minimum"]==d["minimum_uncarried"]]
        f["depths"].append(d)
        f["seconds"]=round(time.time()-started,6)
        output=HERE/"direct_brute_results.json"
        result=json.loads(output.read_text())
        result["moving_suffix_fixture"]=f
        output.write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps({k:v for k,v in d.items()if k!="paths"}),flush=True)
    return f


def synthetic_repeated_self():
    original=[[3,2,[["K",[0,1,3]],["K",[0,3,4]],["SELF",[3,3,0]],["SELF",[3,4,1]]]]]
    ds=usual(original)
    rr,hist=greatest_fixed_point(ds)
    b=block(ds,rr,0,0)
    f=dict(definitions=original,independent_fixed_point=rr,fixed_point_iterations=hist,block=b,depths=[])
    for s in range(1,4):
        d=dict(depth=s,paths=[])
        for path in itertools.product(range(2),repeat=s):
            n,cs,top,target,copies=flatten(b,b,path,rr[0])
            vals=satisfying_assignments(n,cs)
            value,witness=minimum_bond(vals,n,top,target)
            assert len(vals)>0
            d["paths"].append(dict(path=path,n=n,total_assignments=1<<n,
                                    allowed_assignment_count=len(vals),constraints=cs,copies=copies,
                                    carried=bool(set(copies[-1]["env"][:3])&set(top)),
                                    minimum=value,witness=witness))
        finite=[p["minimum"]for p in d["paths"]if p["minimum"]is not None]
        d["minimum"]=min(finite)if finite else None
        f["depths"].append(d)
    return f


def audit_lassos(depth):
    started=time.time()
    source=HERE/"lasso_results.jsonl"
    raw=source.read_bytes()
    candidates=[]
    for line in raw.decode().splitlines():
        row=json.loads(line)
        if not row.get("certified"):
            continue
        original=json.loads(row["key"])
        ds=usual(original)
        ray=choose_ray(ds)
        rr,hist=greatest_fixed_point(ds)
        main=block(ds,rr,ray,len(ds)-1)
        recurring=block(ds,rr,ray,ray)
        n=main["n"]+depth*recurring["own"]
        if n<=MAX_N:
            candidates.append((n,row,original,ds,ray,rr,main,recurring))
    candidates.sort(key=lambda q:(not q[1].get("mixed_path_needed",False),q[0],q[1].get("row_order",999999),q[1]["key"]))
    f=dict(source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(raw).hexdigest(),
           selection="ten certified rows prioritizing mixed_path_needed, then smallest depth-bound distinction count,row_order,key",
           candidate_count=len(candidates),families=[])
    for nmax,row,original,ds,ray,rr,main,recurring in candidates[:10]:
        assert ray==row["independent_S"]
        assert [list(c["arguments"])for c in main["choices"]]==row["main_calls"]
        assert [list(c["arguments"])for c in recurring["choices"]]==row["self_calls"]
        one=dict(key=row["key"],definitions=original,row_order=row.get("row_order"),
                 mixed_path_needed=row.get("mixed_path_needed"),
                 entry=row["entry"],prefix=row["prefix"],period=row["period"],
                 independent_fixed_point=rr,main_block=main,recurring_block=recurring,depths=[])
        f["families"].append(one)
        for s in range(1,depth+1):
            middle=list(row["prefix"])
            while len(middle)<s-1:
                middle.extend(row["period"])
            path=(row["entry"],)+tuple(middle[:s-1])
            n,cs,top,target,copies=flatten(main,recurring,path,rr[ray])
            vals=satisfying_assignments(n,cs)
            value,witness=minimum_bond(vals,n,top,target)
            mask=sum(1<<j for j,v in enumerate(copies[-1]["env"][:3])if v in top)
            match=compare(value,row["values"][s-1])
            mask_match=mask==row["top_port_masks"][s-1]
            assert match and mask_match,(row["key"],s,value,row["values"][s-1],mask,row["top_port_masks"][s-1])
            one["depths"].append(dict(depth=s,path=path,n=n,total_assignments=1<<n,
                                      allowed_assignment_count=len(vals),
                                      allowed_assignment_sha256=hashlib.sha256(vals.astype("<u4").tobytes()).hexdigest(),
                                      constraints=cs,copies=copies,minimum=value,witness=witness,
                                      lasso_row_value=row["values"][s-1],match=match,
                                      top_port_mask=mask,lasso_row_port_mask=row["top_port_masks"][s-1],
                                      top_port_mask_match=mask_match))
        print(json.dumps(dict(lasso_row_order=one["row_order"],depths=depth,all_matches=True)),flush=True)
    f["synthetic_repeated_self"]=synthetic_repeated_self()
    f["seconds"]=round(time.time()-started,6)
    result=json.loads((HERE/"direct_brute_results.json").read_text())
    result["lasso_crosscheck"]=f
    (HERE/"direct_brute_results.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(dict(lasso_families=len(f["families"]),depth_cells=sum(len(a["depths"])for a in f["families"]),
                          synthetic_minima=[d["minimum"]for d in f["synthetic_repeated_self"]["depths"]],seconds=f["seconds"])),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--depth",type=int,default=3)
    parser.add_argument("--limit",type=int,default=0)
    parser.add_argument("--fixtures",action="store_true")
    parser.add_argument("--lassos",action="store_true")
    args=parser.parse_args()
    if args.fixtures:
        moving_suffix_fixture(args.depth)
    elif args.lassos:
        audit_lassos(args.depth)
    else:
        run(args.depth,args.limit)
