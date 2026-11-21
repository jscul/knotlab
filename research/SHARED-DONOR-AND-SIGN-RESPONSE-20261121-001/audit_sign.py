"""Check the two signs on the complete depth-ten menu of each archived switch.

For one actually distinguished outgoing sibling, construct all 32 complete
word effects simultaneously on the sixteen input words. The matrices below
have integer entries in units of 1/24. They describe a supplied measurement
and specify no new ordinary firing. The unmarked and firing-retained cases
supply independent obstructions.
"""
import argparse
import gzip
import json
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PRIOR = "SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A"
ARCHIVE = ROOT/"artifacts"/PRIOR/(PRIOR+"-E001_sign_records")/"archived_events.json.gz"


def swap(word, a, b):
    if (a in word) == (b in word):
        return word
    return word ^ {a, b}


def analyse(data, arm):
    nodes = {n["id"]:n for n in arm["traces"]["loaded"]["nodes"]}
    words = {i:frozenset(n["word"]) for i,n in nodes.items()}
    cols = sorted(n["id"] for n in nodes.values() if n["depth"] == 10)
    assert cols == sorted(g["target"] for g in nodes[11]["enabled_events"]) and len(cols)==16
    index = {i:j for j,i in enumerate(cols)}
    antecedents = defaultdict(list)
    centers = {}
    records = {}
    for i in cols:
        for draw in nodes[i]["enabled_events"]:
            t=draw["target"]
            assert Fraction(draw["chance_given_source"]) == Fraction(1,8)
            center, = draw["at_knots"]
            if t in centers:
                assert centers[t] == center
            centers[t] = center
            antecedents[t].append(i)
            records[i,t]=draw["event_id"]
    common=sorted(t for t,row in antecedents.items() if 12 in row and 13 in row)
    assert len(antecedents)==32 and common==[32,33,34,35]
    erased_center=centers[32]
    siblings=frozenset.union(*(words[t] for t in common)) - frozenset.intersection(*(words[t] for t in common))
    assert len(siblings)==4 and all(len(words[t]&siblings)==1 for t in common)
    mark, = words[32]&siblings
    prefixes=[words[i] for i in nodes if nodes[i]["depth"]<=10]
    all_prefix_events=[frozenset(data["events"][v["event_id"]]["distinctions"])
                       for n in nodes.values() if n["depth"]<10 for v in n["enabled_events"]]
    for a,b in combinations(siblings,2):
        assert all(swap(set(w),a,b)==set(w) for w in data["holdings"])
        assert all(swap(w,a,b)==w for w in prefixes + all_prefix_events)
        assert {swap(words[x],a,b) for x in common}=={words[x] for x in common}
    assert all(records[12,t]!=records[13,t] for t in common)
    bounds={}
    for name, chosen in (("standard",False),("one_outgoing_mark",True)):
        total=np.zeros((16,16),dtype=int)
        probabilities={}
        ranks=defaultdict(set)
        for t, old in antecedents.items():
            ids=[index[v] for v in old]
            assert len(ids)==4
            if chosen and centers[t]==erased_center:
                assert len(words[t]&siblings)==1
                if mark in words[t]:
                    core=3*np.ones((4,4),dtype=int)
                    sector="marked"
                else:
                    core=4*np.eye(4,dtype=int)-np.ones((4,4),dtype=int)
                    sector="other_sibling"
            else:
                core=3*np.eye(4,dtype=int)
                sector="unmarked_holder"
            # Exact scaled projections. PSD and the ranks follow from E^2=kE, k>0.
            k={"marked":12,"other_sibling":4,"unmarked_holder":3}[sector]
            assert np.array_equal(core@core,k*core)
            rank,remainder=divmod(int(np.trace(core)),k)
            assert not remainder
            ranks[sector].add(rank)
            effect=np.zeros_like(total)
            effect[np.ix_(ids,ids)]=core
            assert all(effect[index[i],index[i]]==(3 if i in old else 0) for i in cols)
            total+=effect
            i,j=index[12],index[13]
            probabilities[t]=tuple(Fraction(int(effect[i,i]+effect[j,j]+sign*2*effect[i,j]),48)
                                   for sign in (1,-1))
        assert np.array_equal(total,24*np.eye(16,dtype=int))
        port=probabilities[32]
        complement=tuple(sum(p[i] for t,p in probabilities.items() if t!=32) for i in (0,1))
        assert all(a+b==1 for a,b in zip(port,complement))
        bounds[name]={"word32":list(map(str,port)), "complement":list(map(str,complement)),
                      "effect_ranks":{k:sorted(v) for k,v in ranks.items()}}
    return {"loaded_donor":arm["donor_knot"],"pointwise_fixed_prefix_words":len(prefixes),
            "pointwise_fixed_prefix_offers":len(all_prefix_events),"permutable_output_marks":sorted(siblings),
            "target_mark":mark,"input_words":len(cols),"output_words":len(antecedents),
            "common_words":common,"effects":bounds}


def compare_study(rows):
    folder = ROOT/"artifacts"/(Path(__file__).resolve().parent.name+"B")
    receipt = json.loads(next(folder.glob("*/receipt.json")).read_bytes())
    checks = receipt["checks"]
    assert len(checks) == len(rows) == 2
    for control, recorded in zip(rows, checks):
        assert recorded["old_words"] == control["input_words"]
        assert recorded["complete_words"] == control["output_words"]
        assert recorded["past_fixed_transpositions"] == 6
        for study_key, audit_key in (("ordinary","standard"), ("one_active_outgoing_mark","one_outgoing_mark")):
            assert recorded["target_plus_minus"][study_key] == control["effects"][audit_key]["word32"]
    print("Both physical loadings matched for 16 inputs, 32 complete outcomes and both signed preparations.")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with the later switch study receipt")
    args = parser.parse_args()
    with gzip.open(ARCHIVE,"rt") as stream:
        data=json.load(stream)["uniform_switch"]
    rows = [analyse(data,arm) for arm in data["directions"]]
    if args.check:
        compare_study(rows)
    else:
        print(json.dumps(rows,indent=2,sort_keys=True))
