#!/usr/bin/env python3
"""Fresh JSONL recount and descriptive diameter analysis, no producer imports.

The census denominator is outcome == 'base'; travelling is the certified
COMMON-FOLD class 'travels', excluding 'travels, uncertified'. Prefixes end
only after a whole sample, whose r=3,4,5 readings are dependent.
"""
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from statistics import NormalDist
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
DATA=ROOT/"artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts"


def read(path):
    return [json.loads(x)for x in path.read_text().splitlines() if x.strip()]


def canonical(kind):
    pts=sorted(map(tuple,kind))
    a,b=pts[0]
    return tuple((x-a,y-b)for x,y in pts)


def universe(box):
    return {canonical(k)for k in itertools.combinations(box,3)}


def diameter(k):
    return max(max(c[j]for c in k)-min(c[j]for c in k)for j in (0,1))


def wilson(k,n):
    if not n:
        return None
    z=NormalDist().inv_cdf(0.975)
    den=1+z*z/n
    mid=(k/n+z*z/(2*n))/den
    half=z*math.sqrt((k/n*(1-k/n)+z*z/(4*n))/n)/den
    return [max(0,mid-half),min(1,mid+half)]


def rate(k,n):
    return {"k":k,"n":n,"rate":k/n if n else None,"wilson95_nominal":wilson(k,n)}


def rank(dirs):
    if not dirs:
        return 0
    a,b=dirs[0]
    return 2 if any(a*y-b*x for x,y in dirs[1:]) else 1


def summary(bs,completed):
    bases=[b for b in bs if b["outcome"]=="base"]
    travel=[b for b in bases if b["class"]=="travels"]
    main2=[b for b in travel if rank(b["main"]["certified directions"])==2]
    after=[b for b in travel if rank(b["main"]["certified directions"])==2 or b["id"]in completed]
    uncert=[b for b in travel if rank(b["main"]["certified directions"]+b["main"]["forced, uncertified"])==2
            and rank(b["main"]["certified directions"])<2]
    w=rate(len(after),len(travel))
    if len(travel)<40:
        verdict="inconclusive by size"
    elif w["wilson95_nominal"][0]>=0.5 and w["rate"]>=0.7:
        verdict="pass"
    elif w["wilson95_nominal"][1]<0.7:
        verdict="fail"
    else:
        verdict="inconclusive"
    return {"raw_readings":len(bs),"outcomes":dict(Counter(b["outcome"]for b in bs)),
            "classes":dict(Counter(b["class"]for b in bs)),"bases":len(bases),
            "travelling":rate(len(travel),len(bases)),
            "main_two_certified":rate(len(main2),len(travel)),
            "forced_second_uncertified_before_completion":len(uncert),
            "after_completion":w,"one_direction_unresolved_after_completion":len(travel)-len(after),
            "W1_numeric_rule":verdict}


def metric_rows(bs,keys):
    groups=defaultdict(list)
    for b in bs:
        if b["outcome"]=="base":
            groups[tuple(b[k]for k in keys)].append(b)
    out=[]
    ordered=sorted(groups.items(),key=lambda pair:tuple(Fraction(v) if name=="mean_diameter"else v
                   for name,v in zip(keys,pair[0])))
    for key,gg in ordered:
        row=dict(zip(keys,key))
        row.update(rate(sum(b["class"]=="travels"for b in gg),len(gg)))
        row["class_counts"]=dict(Counter(b["class"]for b in gg))
        row["sample_count"]=len({b["sample"]for b in gg})
        out.append(row)
    return out


def pct(x):
    return f"{100*x:.1f}%" if x is not None else "—"


def main():
    start=time.monotonic()
    original=read(DATA/"census.jsonl")
    resumed=read(DATA/"resume_census/results.jsonl")
    calibration=read(DATA/"calibration.jsonl")
    samples={}
    for row in original:
        if "by r"in row:
            key=(row["beta"],row["sample"])
            assert key not in samples
            samples[key]=(row,"before pause")
    for wrapper in resumed:
        if wrapper["status"]=="ok":
            row=wrapper["result"]
            key=(row["beta"],row["sample"])
            assert key not in samples
            samples[key]=(row,"resumed")
    old=universe([(x,y)for x in range(3)for y in range(-2,3)])
    large=universe([(x,y)for x in range(4)for y in range(-3,4)])
    assert (len(old),len(large))==(171,738)
    completed_checks=json.loads((HERE/"completion_checks.json").read_text())
    completed=set()
    for row in completed_checks:
        assert row["check"]["certified"] and row["independent_of_main"]
        assert row["both_directions_independently_certified"]
        completed.add((row["beta"],row["sample"],row["r"]))
    bases=[]
    for (beta,i),(row,source) in sorted(samples.items()):
        assert set(row["by r"])=={"3","4","5"}
        prev=[]
        for r in (3,4,5):
            b=dict(row["by r"][str(r)])
            kinds=[canonical(k)for k in b["kinds"]]
            assert len(kinds)==r and len(set(kinds))==r
            assert all(k in large for k in kinds)
            assert not prev or prev==kinds[:len(prev)]
            prev=kinds
            ds=[diameter(k)for k in kinds]
            assert ds==b["diameters"]
            assert b["stratum"]==("old box" if all(k in old for k in kinds)else "new kinds")
            if "main"in b:
                m=b["main"]
                assert rank(m["certified directions"])==m["rank certified"]
                assert rank(m["certified directions"]+m["forced, uncertified"])==m["rank forced"]
            b.update(beta=beta,sample=i,r=r,source=source,id=(beta,i,r),max_diameter=max(ds),
                     mean_diameter=str(Fraction(sum(ds),r)),mean_diameter_numeric=sum(ds)/r)
            m=sum(ds)/r
            b["mean_bin"]=("[1,2)" if m<2 else "[2,3)" if m<3 else "[3,4)" if m<4 else "[4,5)" if m<5 else "[5,6]")
            bases.append(b)
    stops={}
    for beta in range(3):
        total=0
        for key in sorted(k for k in samples if k[0]==beta):
            i=key[1]
            total+=sum(b["class"]=="travels" and b["outcome"]=="base" and b["stratum"]=="new kinds"
                       for b in samples[key][0]["by r"].values())
            if total>=40:
                stops[beta]=i
                break
        assert all((beta,i)in samples for i in range(stops[beta]+1))
    prefix=[b for b in bases if b["sample"]<=stops[b["beta"]]]
    recount={"denominator":"outcome=base; numerator class=travels; 'travels, uncertified' excluded from numerator",
             "uncertainty":"Nominal Wilson 95% formula; dependent nested r-prefixes and outcome-dependent sample stopping prevent a guaranteed 95% binomial coverage interpretation.",
             "kinds":{ "old":len(old),"large":len(large)},"samples":len(samples),"base_readings":len(bases),
             "stopping_indices":stops,"prefix":{},"all_completed":{}}
    for mode,selection in (("prefix",prefix),("all_completed",bases)):
        for beta in range(3):
            indices=sorted(i for w,i in samples if w==beta and (mode=="all_completed"or i<=stops[beta]))
            entry={"sample_count":len(indices),"last_index":max(indices),
                   "missing_indices":[i for i in range(max(indices)+1)if i not in indices]}
            for st in ("new kinds","old box"):
                entry[st]=summary([b for b in selection if b["beta"]==beta and b["stratum"]==st],completed)
            recount[mode][str(beta)]=entry
    capped=[tuple(row["item"])for row in original if "dropped at the cap"in row]
    observed={tuple(x["item"])for x in original}
    holes=[]
    for beta in (0,1):
        last=max(i for w,i in observed if w==beta)
        holes.extend((beta,i)for i in range(last+1)if (beta,i)not in observed)
    reruns=[]
    for beta,i in sorted(set(capped+holes)):
        bb=[b for b in bases if (b["beta"],b["sample"])==(beta,i)]
        reruns.append({"beta":beta,"sample":i,"before_pause":"logged capped" if (beta,i)in capped else "no row before pause",
                       "readings":[{"r":b["r"],"outcome":b["outcome"],"class":b["class"],"stratum":b["stratum"],
                                    "rank_certified":b.get("main",{}).get("rank certified"),
                                    "rank_forced":b.get("main",{}).get("rank forced"),
                                    "completed_rank_two":b["id"]in completed or b.get("main",{}).get("rank certified",0)==2}
                                   for b in bb]})
    recount["before_pause_missing"]={"logged_capped":len(capped),"unlogged_holes":len(holes),
                                      "warning":"An unlogged hole within the observed index range does not establish whether a sample started before the pause.",
                                      "reruns":reruns}
    recount["calibration"]={"attempted":len(calibration),"logged_capped":sum("dropped at the cap"in row for row in calibration),
                             "completed":sum("dropped at the cap"not in row for row in calibration),
                             "planned":23,"items":calibration,"W3":"undecided"}
    # Independent comparisons with permitted summaries, never input to counts.
    claimed=json.loads((ROOT/"research/WEIGHTS-20261112-001/summary.json").read_text())
    checks=[]
    for beta in range(3):
        x=recount["prefix"][str(beta)]
        assert stops[beta]==claimed[str(beta)]["stopping index"]
        for st in ("new kinds","old box"):
            c=claimed[str(beta)][st];a=x[st]
            assert a["bases"]==c["bases"]
            assert a["travelling"]["k"]==c["travelling"]
            assert [a["after_completion"]["k"],a["after_completion"]["n"]]==c["after completion"]["two certified"][:2]
        checks.append({"beta":beta,"stopping_and_counts_match":True})
    recount["comparison_to_provided_summary"]=checks
    tables={}
    specs={"by_r":["beta","stratum","r"],
           "by_max_diameter":["beta","stratum","max_diameter"],
           "by_mean_diameter_exact":["beta","stratum","mean_diameter"],
           "by_mean_diameter_bin":["beta","stratum","mean_bin"],
           "by_r_and_max_diameter":["beta","stratum","r","max_diameter"],
           "by_r_and_mean_diameter_exact":["beta","stratum","r","mean_diameter"],
           "by_r_and_mean_diameter_bin":["beta","stratum","r","mean_bin"]}
    for mode,selection in (("prefix",prefix),("all_completed",bases)):
        tables[mode]={name:metric_rows(selection,keys)for name,keys in specs.items()}
    def trend(gg,field):
        if not gg:return None
        xs=[b[field]for b in gg];ys=[int(b["class"]=="travels")for b in gg]
        mx=sum(xs)/len(xs);my=sum(ys)/len(ys)
        cov=sum((x-mx)*(y-my)for x,y in zip(xs,ys))/len(xs)
        return {"n":len(gg),"mean_size":mx,"travel_rate":my,"covariance_size_travelling":cov,
                "mean_size_travelling":sum(x*y for x,y in zip(xs,ys))/sum(ys) if sum(ys)else None,
                "mean_size_other":sum(x*(1-y)for x,y in zip(xs,ys))/(len(xs)-sum(ys)) if sum(ys)<len(xs)else None}
    tables["within_group_descriptive_trends"]=[]
    for beta in range(3):
        for st in ("new kinds","old box"):
            for r in (None,3,4,5):
                gg=[b for b in prefix if b["outcome"]=="base" and b["beta"]==beta and b["stratum"]==st and (r is None or b["r"]==r)]
                tables["within_group_descriptive_trends"].append({"beta":beta,"stratum":st,"r":r,
                  "largest":trend(gg,"max_diameter"),"mean":trend(gg,"mean_diameter_numeric")})
    # Equal r weights illustrate the composition issue; descriptive only.
    recount["equal_r_standardized_travelling"]={}
    for beta in range(3):
        out={}
        for st in ("new kinds","old box"):
            rr=[x for x in tables["prefix"]["by_r"]if x["beta"]==beta and x["stratum"]==st]
            out[st]=sum(x["rate"]for x in rr)/3 if len(rr)==3 else None
        recount["equal_r_standardized_travelling"][str(beta)]=out
    provenance={"scope_kind":"epic","scope_id":"WEIGHTS-20261112-001","task":"Independent referee recomputation",
                "writes":"research/WEIGHTS-20261112-001/referee-R1/codex only",
                "no_producer_imports":True,"processes":1,"python":".venv/bin/python -B",
                "inputs_sha256":{},"scripts_sha256":{},"seconds_data_analysis":time.monotonic()-start}
    paths=[DATA/"census.jsonl",DATA/"calibration.jsonl",DATA/"resume_census/results.jsonl"]
    paths += [ROOT/"research/WEIGHTS-20261112-001"/name for name in ("completion.json","summary.json","partial_summary.json","two_shifts.md","preregistration.md","paused.md")]
    paths += [ROOT/"research/SHIFT-COUNT-20261112-001/referee-R1"/name for name in ("ref_shiftcount.py","ref_137.py")]
    paths += [ROOT/"research/COMMON-FOLD-20261112-001/referee-R1/ref_fold.py"]
    paths += [ROOT/"research"/family/name for family,name in (
        ("SHIFT-COUNT-20261112-001","preregistration.md"),
        ("SHIFT-COUNT-20261112-001","shift_count.md"),
        ("FAR-BOUND-20261112-001","far_bound.md"),
        ("COMMON-FOLD-20261112-001","common_fold.md"))]
    for path in paths:
        provenance["inputs_sha256"][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    for name in ("audit_data.py","audit_certificates.py","write_report.py"):
        if not (HERE/name).exists():
            continue
        provenance["scripts_sha256"][name]=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    for name,obj in (("recount.json",recount),("diameter_tables.json",tables),("provenance.json",provenance)):
        (HERE/name).write_text(json.dumps(obj,indent=2)+"\n")
    md=["# Diameter tables", "", "Descriptive rates of the certified travelling class among records with outcome `base`. Both prefix and all-completed selections are shown. Wilson intervals are nominal: nested r-readings share a sample, and the prefix stopping rule depends on observed travel. Exact mean diameter is a rational number; mean bins are an additional descriptive display.", ""]
    for mode in ("prefix","all_completed"):
        for name,keys in specs.items():
            md += [f"## {mode}: {name}","","| "+" | ".join(keys+["travelling / bases","rate","Wilson 95% (nominal)"])+" |",
                   "| "+" | ".join(["---"]*(len(keys)+3))+" |"]
            for row in tables[mode][name]:
                lo,hi=row["wilson95_nominal"]
                md.append("| "+" | ".join([str(row[k])for k in keys]+[f'{row["k"]}/{row["n"]}',pct(row["rate"]),f'{pct(lo)}–{pct(hi)}'])+" |")
            md.append("")
    (HERE/"diameter_tables.md").write_text("\n".join(md)+"\n")
    print(json.dumps({"stops":stops,"prefix":{beta:{st:x[st]["after_completion"]for st in ("new kinds","old box")}
                     for beta,x in recount["prefix"].items()},"all_completed":{beta:{st:x[st]["after_completion"]for st in ("new kinds","old box")}
                     for beta,x in recount["all_completed"].items()},"calibration":recount["calibration"]},indent=2))


if __name__=="__main__":
    main()
