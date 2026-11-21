"""Replay the original funded end for the four-site shared-donor comparison.

The archived receiver supplies its source, tick and member conventions. This
audit builds the new original parent groups and next sibling groups from the
witnesses. It checks every subinterval by excluding competing ordinary groups.
Every size-m ancestor of a late binary interval is a contiguous tile window;
we enumerate all spellings of those windows on the true incoming parent.
"""
import argparse
import gzip
import importlib.util
import json
from collections import Counter, defaultdict
from itertools import combinations, pairwise, product
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "research/JOINT-PARENTS-AND-ERASURE-20261120-001/audit_clock.py"
spec = importlib.util.spec_from_file_location("disjoint_price_audit", PRIOR)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
clocks = audit.prior
GATES = (20,21,23,25)
SENDS = (32,48,64,80)


def original(lifetime, modes):
    middle = clocks.middle(lifetime,32)
    graph = nx.Graph(middle)
    for prefix in ("R","S"):
        graph.add_edges_from((prefix+a,prefix+b) for a,b in audit.FRAME)
    graph.add_edges_from([("Rr1","Sb2"),("Rb2","a"),("b","Sb2")])
    held = [frozenset(p) for p in graph.edges]
    specials = {}
    for j,mode in zip(GATES,modes):
        u,v,w = f"c{j}", f"c{j+1}", f"w{j}"
        for d in (u,v):
            clocks.meet(middle,w,d)
            graph.add_edge(w,d)
        key=frozenset((u,v))
        specials[key]=(w, mode)
        if mode=="C":
            held.remove(key)
            held.append(frozenset((u,v,w)))
        else:
            held.extend([frozenset((u,w)),frozenset((v,w))])
    first=audit.groups(held)
    dues=Counter(d for g in first for d in g)
    for d,h in graph.degree:
        assert h>=dues[d]
        first.extend([frozenset((d,))]*(h-dues[d]))
    incident=defaultdict(set)
    entries={}
    for i,g in enumerate(first):
        for d in g: incident[d].add(i)
        for pair in combinations(g,2):
            pair=frozenset(pair)
            assert pair not in entries
            entries[pair]=i
    second=set(audit.groups(incident.values()))
    covered={frozenset(p) for g in second for p in combinations(g,2)}
    return middle,first,incident,entries,second,covered,specials


def c_spells(groups, forbid_extra):
    if forbid_extra and any(len(g)!=2 for g in groups):
        return []
    joints=[p&q for p,q in pairwise(groups)]
    if any(len(g)!=1 for g in joints): return []
    middles=[next(iter(g)) for g in joints]
    spells=[]
    for a,b in product(groups[0]-{middles[0]},groups[-1]-{middles[-1]}):
        seq=[a,*middles,b]
        if all(x.startswith("c") for x in seq):
            ranks=[int(x[1:]) for x in seq]
            steps={(v-u)%65 for u,v in pairwise(ranks)}
            if steps=={1} or steps=={64}: spells.append(seq)
    return spells


def certify(lifetime,modes):
    middle,first,incident,entries,second,covered,specials=original(lifetime,modes)
    paths=list(clocks.simple_paths(middle,"a","b"))
    info={}
    shared=None
    if modes:
        t1=entries[frozenset(("c20","c21"))]; t2=entries[frozenset(("c21","c22"))]
        assert first[t1]&first[t2]=={"c21"}
        assert frozenset((t1,t2)) in second
        shared={"original_group_sizes":[len(first[t1]),len(first[t2])],
                "through_child_parents":2,
                "through_child_grant":audit.count_extensions(("c20","c21","c22"),incident,entries,specials), "shared_donor_private_names":len(incident["c21"]),
                "shared_donor_group_payments":sum(len(first[s])>1 for s in incident["c21"])}
    for reader in ("extended","hereditary"):
        eligible=[p for p in paths if reader=="extended" or
                  all(len(first[entries[frozenset(ab)]])==2 for ab in pairwise(p))]
        info[reader]={}
        for m in SENDS:
            if not eligible:
                info[reader][m]=[]
                continue
            dist=min(map(len,eligible))-1
            routes=[p for p in eligible if len(p)==dist+1]
            ends=list(clocks.sender_endings(clocks.sent_word(m)))
            end_size=min(map(len,ends))
            receipts=[]
            for path,tail in product(routes,[v for v in ends if len(v)==end_size]):
                right=("Rt","Rb2")+path+tuple("S"+v for v in tail)
                left=tuple("R"+audit.CALENDAR[j%12] for j in range(-len(right),0))
                word=left+("Rb1",)+right
                assert audit.paid_word(word,first,entries,second,covered)==len(word)-1
                prices=audit.payment_vector(word,incident,entries,specials,m)
                outer=[first[entries[frozenset(ab)]] for ab in pairwise(word[1:])]
                window_counts=[]
                for strict in (False,True):
                    windows=[i for i in range(len(outer)-m+2) if c_spells(outer[i:i+m-1],strict)]
                    window_counts.append(len(windows))
                receipts.append(dict(passage=dist, size=len(word), ticks_since_send=sum(
                    v>m for v in clocks.receiver_ticks(len(word))), prices=prices,
                    incoming_third_windows=window_counts))
            info[reader][m]=receipts
    return {"shared":shared,"readers":info}


def compute():
    return {arm+"/"+(modes or "none"):certify(arm,modes)
            for arm in ("active","matched") for modes in [""]+["".join(v) for v in product("CS",repeat=4)]}


def check_archive(result):
    location = ROOT/"artifacts"/(Path(__file__).resolve().parent.name+"A")
    with gzip.open(next(location.glob("*/clock.json.gz")),"rt") as stream:
        source=json.load(stream)
    compared=registered=grants=0
    for case in source["cases"]:
        lifetime = "matched" if case["lifetime"]=="finite" else "active"
        modes = "" if case["gates"]=="archive" else case["gates"]
        ours=result[lifetime+"/"+(modes or "none")]
        if modes:
            local, measured = ours["shared"], case["local_common_child"]
            assert measured["shared_original"]==["c21"]
            assert [len(p) for p in measured["first_groups"]]==local["original_group_sizes"]
            assert (measured["parents"],measured["grant"])==(2,local["through_child_grant"])
            assert case["source_groups_charged_to_shared_donor"]==local["shared_donor_group_payments"]
        for reader, sends in case["readers"].items():
            for send in sends:
                compared+=1
                rows=ours["readers"][reader][send["send"]]
                assert len(rows)==len(send["minimizers"])
                for mine,actual in zip(rows,send["minimizers"]):
                    assert (mine["size"],mine["ticks_since_send"],mine["passage"])==(
                        actual["size"],actual["ticks_after_send"],len(actual["route"])-1)
                    assert actual["raw_delay"]==mine["size"]-send["send"]
                    assert mine["prices"]==actual["price_vector"]==actual["endpoint_prices_direct_extension_count"]
                    assert mine["incoming_third_windows"]==[
                        len(actual["third_rank_m_ancestors_in_incoming"]),
                        len(actual["no_extra_third_rank_m_ancestors_in_incoming"])]
                    registered+=1
                    grants+=len(mine["prices"])
    print(compared,"reader/start/send cases;", registered,"actual registrations;",grants,"grants matched.")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sums",action="store_true")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    result=compute()
    if args.check:
        check_archive(result)
    elif args.sums:
        for mode in ("extended","hereditary"):
            rows=[r for case in result.values() for r in case["readers"][mode].values()]
            print(mode,len(rows),sum(map(len,rows)),Counter(
                v["passage"] for row in rows for v in row))
        for k in ("active/SSCC","active/CCSS","matched/SSCC","matched/CCSS"):
            print(k,result[k]["shared"],result[k]["readers"]["extended"][32])
    else:
        print(json.dumps(result,sort_keys=True,indent=2))
