"""Check recorded lower bonds by simpler exhaustive methods on small raw stages."""
import gzip
import json
import subprocess
from itertools import combinations
from pathlib import Path
from time import perf_counter

from read_recount import HERE, PROGRAM, RESEARCH, mask, stage_source


def direct(sup):
    raw = sorted(set().union(*map(set,sup)))
    knots = [mask(s) for s in sup]
    # Use all states including complements, and literal fixed knot assignments.
    states=[x for x in range(1 << len(raw)) if all(x & m not in (0,m) for m in knots)]
    universe=(1 << len(states))-1
    readings={}
    for width in (2,3):
        for carrier in combinations(raw,width):
            c=mask(carrier)
            positive=[i for i,x in enumerate(states) if x & c in (0,c)]
            if len(positive) in (0,len(states)):
                continue
            yes=set(positive)
            negative=set(range(len(states)))-yes
            if any({states[i]&k for i in yes}.isdisjoint(states[i]&k for i in negative) for k in knots):
                continue
            readings[c]=sum(1<<i for i in yes)
    result={}
    for a,b,c in combinations(sorted(readings),3):
        if a & b or a & c or b & c:
            continue
        sets=[(universe^readings[v],readings[v]) for v in (a,b,c)]
        image={4*i+2*j+k for i,first in enumerate(sets[0])
               for j,second in enumerate(sets[1]) for k,third in enumerate(sets[2]) if first & second & third}
        if len(image)<8 and all(len({w & ~(1<<d) for w in image})==4 for d in range(3)):
            result[a,b,c]=sum(1<<w for w in set(range(8))-image)
    return result


def ordered_bonds(raw):
    result={}
    for a,b,c,missing in raw:
        given=(a,b,c)
        order=sorted(range(3),key=given.__getitem__)
        permuted=0
        for w in range(8):
            if missing & (1<<w):
                new=sum(((w>>(2-p))&1)<<(2-pos) for pos,p in enumerate(order))
                permuted |= 1<<new
        key=tuple(given[p] for p in order)
        if key in result:
            raise ValueError("duplicate lower bond")
        result[key]=permuted
    return result


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--small",action="store_true")
    opt=parser.parse_args()
    starts=json.loads((RESEARCH/"FORBID-EDITS-20261126-001/starts.json").read_text())
    cases=[(206,0)] if opt.small else [(206,0),(163,0),(37,1),(1199,0),(2191,0),(420,0)]
    result=[]
    for i,t in cases:
        sup=dict(stage_source(starts,i))[t]
        before=perf_counter()
        plain=direct(sup)
        out=json.loads(subprocess.check_output([str(PROGRAM),"2",*map(str,map(mask,sup))]))
        optimized=ordered_bonds(out["all_bonds"])
        if plain!=optimized: raise ValueError(f"all-bond signed set differs at entry {i}, round {t}")
        result.append({"entry":i,"round":t,"complete_signed_bond_sets_match":True,
                       "bonds":len(plain),"multi_word":sum(k.bit_count()>1 for k in plain.values()),
                       "seconds":round(perf_counter()-before,5)})
    if not opt.small:
        earlier=json.loads((RESEARCH/"UPPER-GROWN-20261127-001/referee-R1/upper_sample.json").read_text())[0]
        ref=earlier["witness"]
        table=json.loads(gzip.decompress((HERE/"read_all_bonds_420_2.json.gz").read_bytes()))
        lits=[2*mask(raw)+val for raw,val in ref["raw_agreements_and_selected_value"]]
        fam=sorted(sorted(lits[p] for p in triple) for triple in ref["lower_clauses"])
        old_pair=sorted(lits[:2])
        rows=[r for r in table["relations"] if r["clauses"]==fam and r["pairs"][r["both"]]==old_pair]
        assert len(rows)==1 and ref["source"]==table["supports"]
        rel=rows[0]
        assert (rel["restored_111_assignments_by_individual_law_deletion"]==ref["restored_upper_111_by_dropped_law"]
                and rel["words"]==ref["actual_upper_words"] and ref["source_knots"]==len(starts[420][2])
                and earlier["signed_bonds"]==len(table["clauses"]))
        witness={"source_supports_identical":True,"named_four_clauses_identical":True,
                 "all_ten_named_role_deletions_match":True,"seven_upper_words_match":True,
                 "single_word_bonds":len(table["clauses"])}
    else:
        witness={}
    path=HERE/("read_bond_controls_timing.json" if opt.small else "read_bond_controls.json")
    path.write_text(json.dumps({"small_brute_force":result,"earlier_positive_control":witness},indent=2)+"\n")
    print(json.dumps(result))


if __name__=="__main__":
    main()
