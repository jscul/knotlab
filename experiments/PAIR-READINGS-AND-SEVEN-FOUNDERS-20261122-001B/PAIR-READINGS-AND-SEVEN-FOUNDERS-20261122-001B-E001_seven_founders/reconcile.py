"""Compare each native payment with the end-law census and publish exact endpoints."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from census import LAWS, OUT, load, save
from end_operator import maximal_blocks


def normalized(end,offset):
    loose=[[k-offset,len(names)] for k,names in end["loose_names"]]
    blocks=maximal_blocks(tuple(k-offset for k in row) for _,row in end["witnessed_live_subsets"])
    comp=[[i-offset for i in part] for part in end["components"]]
    return {"h":loose,"blocks":[list(x) for x in blocks],"components":comp}


def weighted(cases,den):
    totals={"orbit":len(cases),"labelled_decorated":sum(c["labelled"] for c in cases)}
    totals.update({k:sum(c[k] for c in cases) for k in ("distinct_mass","tree_edit_mass")})
    return {"counts":totals,"fractions":{k:str(Fraction(v,den[k])) for k,v in totals.items()}}


def main():
    population=load("population.json.gz"); ends=load("census.json.gz")
    physical=load("physical_events.json.gz"); physical_summary=load("physical_summary.json")
    checked=Counter();states={}
    for case,line,native in zip(population,ends,physical,strict=True):
        uid=case["id"]; assert line["id"]==native["id"]==uid
        assert all(case[k]==native[k] for k in ("edges","flags","labelled","tau","distinct_mass","tree_edit_mass"))
        for law in LAWS:
            actual=native["laws"][law]; projected=line[law]
            assert (actual["termination"],actual["last_paid_age"],actual["first_split_age"])==(
                projected["status"],projected["paid_cuts"],projected["first_separation"])
            assert (actual["final_holders"],actual["final_distinctions"])==(projected["total_holders"],projected["total_names"])
            cur=projected["initial"];oldoffset=0;newoffset=7
            for i,t in enumerate(actual["cuts"]):
                assert normalized(t["begin"],oldoffset)==cur
                if t["status"]=="stall":
                    assert not t["births"] and t["multiple_groups"]==projected["stall"]["groups"]
                    assert t["shortages"]==[[h,b-a] for h,a,b in projected["stall"]["shortages"]]
                    checked["refused"]+=1
                    break
                c=projected["cuts"][i];kids=t["births"]
                assert [[h-oldoffset for h in v["parents"]] for v in kids]==c["parents"]
                assert [v["grant"] for v in kids]==c["grants"]
                assert [v["lookahead_demand"] for v in kids]==c["lookahead"]
                paid=[k for b in kids for k in b["paid_names"]]
                oldloose=[k for h,names in t["begin"]["loose_names"] for k in names]
                assert len(paid)==len(set(paid)) and set(paid)==set(oldloose)
                assert normalized(t["end"],newoffset)==c["next"]
                assert t["paid_targets_actually_checked_by_GF2"]==len(kids)
                cur=c["next"];oldoffset=newoffset;newoffset+=len(kids)
                checked["paid_cuts"]+=1;checked["named_births"]+=len(kids)
            checked["orbit_laws"]+=1
        states[uid]=line["parity"]
    den=load("census_totals.json")["denominators"]
    survivors=load("surviving_ends.json")["seven_survivors"]
    hits=[c for c in population if states[c["id"]]["status"]=="closed"]
    canonical=[c for c in hits if states[c["id"]]["terminal_arity"]>=3]
    later=[c for c in population if survivors.get(c["id"],{}).get("structural_certificate")]
    proved=canonical+later
    assert all(r["verdict"]!="later fate unresolved" for r in survivors.values())
    counts={key:weighted(v,den) for key,v in (("four_paid_cuts_ordinary_parity",hits),
            ("four_paid_cuts_canonical_last_knot_parity",canonical),("four_paid_cuts_NAE",[]),
            ("later_structural_only",later),("any_age_ordinary_parity_from_deduction",hits+later),
            ("any_age_canonical_last_knot_parity_from_deduction",proved),("any_age_NAE",[]))}
    out={"coverage":dict(checked),"denominators":den,"unresolved_four_cut_mass":0,"four_cut_physical_law_counts":physical_summary["laws"],
         "funnel":load("physical_controls.json")["funnel"],"endpoint_events":counts,
         "connected_parity_survivors":{k:v["verdict"] for k,v in survivors.items()},
         "supporting_sha256":{f:sha256((OUT/f).read_bytes()).hexdigest() for f in (
             "population.json.gz","catalogue_checks.json","census.json.gz","census_totals.json","physical_events.json.gz",
             "physical_summary.json","physical_controls.json","surviving_ends.json")}}
    save("result.json",out)
    print(checked,flush=True)


if __name__=="__main__":
    main()
