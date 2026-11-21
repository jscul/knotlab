"""Count registered receiver ticks with simultaneous, paid, overlapping first groups."""
from importlib.util import module_from_spec, spec_from_file_location
from itertools import pairwise, product
from pathlib import Path
import gzip
import hashlib
import json

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
OLD = "JOINT-PARENTS-AND-ERASURE-20261120-001A"
SPEC = spec_from_file_location("settled_clock", ROOT / "experiments" / OLD / (OLD + "-E001_joint_parents") / "clock.py")
prior = module_from_spec(SPEC)
SPEC.loader.exec_module(prior)
old = prior.old
SITES = (20, 21, 23, 25)
MODES = tuple("".join(m) for m in product("CS", repeat=4))
SIZES = (32, 48, 64, 80)
PRICE_FIELDS = ("send","send_other_end_deletion","send_outside_end_deletion","receiver_launch",
                "receiver_internal_parent","receiver_incoming_parent","receipt")


def build(lifetime, mode):
    g = old.layout("active" if lifetime == "active" else "rewired", 32)
    cells = {}
    for site, kind in zip(SITES, mode):
        a, b, w = f"c{site}", f"c{site+1}", f"w{site}"
        triple = frozenset((a, b, w))
        g.add_edges_from(((a, w), (b, w)))
        for edge in ((a, b), (a, w), (b, w)):
            cells[frozenset(edge)] = (triple, kind)
    blocks = {x:set() for x in g}
    for a,b in g.edges:
        pair = frozenset((a,b))
        block = cells.get(pair,(pair,"ordinary"))
        blocks[a].add(block)
        blocks[b].add(block)
    return g,cells,blocks


def actual_price(word,blocks,supply):
    """List every admissible one-rank extension slot in the unrolled occupied support."""
    def delta(a,b):
        choices = blocks[a] & blocks[b]
        assert len(choices)==1
        return next(iter(choices))
    def slots(role,used):
        single = {b:2 if b[1]=="C" else 1 for b in blocks[role]}
        spare = supply[role]-sum(single.values())
        assert spare>=0 and used<=blocks[role]
        return spare+sum(n for b,n in single.items() if b not in used)
    visits=[delta(a,b) for a,b in pairwise(word)]
    assert all(a!=b for a,b in pairwise(visits))
    total=0
    for i,role in enumerate(word):
        used=set(visits[max(0,i-1):i+1])
        total+=slots(role,used)
    for i,(block,kind) in enumerate(visits):
        if kind=="C":
            total+=1
        elif kind=="S":
            extra,=block-{word[i],word[i+1]}
            total+=slots(extra,{(block,kind)})
    return total


def third_ceiling(lifetime,mode,no_extra):
    cuts={48} if lifetime=="finite" else set()
    if no_extra:
        cuts.update(i for i,ch in zip(SITES,mode) if ch=="S")
    if not cuts:
        return "unbounded"
    ordered=sorted(cuts)
    return max(b-a for a,b in pairwise([*ordered,ordered[0]+65]))


def ancestor_windows(word,m,cells,no_extra):
    """Maximal c runs in the actual incoming interval. Non-spine S extras cannot add c positions."""
    windows=[]
    for a,b in old.c_blocks(word):
        for begin in range(a,b-m+1):
            segment=word[begin:begin+m]
            indices=[int(role[1:]) for role in segment]
            differences={(j-i)%65 for i,j in pairwise(indices)}
            if not (differences=={1} or differences=={64}):
                continue
            if no_extra and any(len(t)>2 for t in prior.units(segment,cells)):
                continue
            windows.append([begin,begin+m])
    return windows


def case(lifetime,mode):
    g,cells,blocks=build(lifetime,mode)
    supply=dict(g.degree())
    out={"lifetime":lifetime,"gates":mode or "archive",
         "gate_sites":dict(zip(SITES,mode)),"source_groups_charged_to_shared_donor":
         (sum(2 if mode[i]=="C" else 1 for i in (0,1)) if mode else None),
         "shared_donor_unary_charges":mode[:2].count("S") if mode else None,
         "source_shared_donor_private":supply["c21"],
         "third_max_size":third_ceiling(lifetime,mode,False),
         "strict_third_max_size":third_ceiling(lifetime,mode,True),
         "pure_R_registers_S":False,"readers":{}}
    pair_groups=[]
    for site in SITES[:2]:
        a,b=f"c{site}",f"c{site+1}"
        pair_groups.append(prior.tile(a,b,cells))
    assert pair_groups[0]&pair_groups[1]=={"c21"}
    join_price=actual_price(("c20","c21","c22"),blocks,supply)
    out["local_common_child"]={"first_groups":[sorted(t) for t in pair_groups],
                                "shared_original":["c21"],"parents":2,"grant":join_price}
    for reader in ("extended","hereditary"):
        passage=g.subgraph([x for x in g if not x.startswith(("S","R"))]).copy()
        if reader=="hereditary":
            for edge,(block,kind) in cells.items():
                if kind=="S": passage.remove_edge(*edge)
        routes=sorted(nx.all_shortest_paths(passage,"a","b")) if nx.has_path(passage,"a","b") else []
        rows=[]
        for m in SIZES:
            candidates=[]
            for path in routes:
                signal=old.send(m//16)
                right=("Rt","Rb2",*path,"Sb2",*signal)
                n=2*len(right)+1
                word=old.left(n//2)+("Rb1",)+right
                assert all(g.has_edge(a,b) for a,b in pairwise(word))
                history=prior.proof_tree(word,cells,reader=="hereditary")
                reading=prior.trace_receiver(word,m,cells,supply,g)
                lo,hi=reading["launch_slice"]
                inputs={"send":signal,"send_other_end_deletion":signal[:-1],"send_outside_end_deletion":signal[1:],
                        "receiver_launch":word[lo:hi],"receiver_internal_parent":word[:-1],
                        "receiver_incoming_parent":word[1:],"receipt":word}
                prices={name:actual_price(w,blocks,supply) for name,w in inputs.items()}
                assert prices==reading["price_vector"]
                sham=tuple("Sb0" if x=="Sb1" else x for x in word)
                assert all(actual_price(x,blocks,supply)==actual_price(y,blocks,supply)
                           for x,y in ((word,sham),(word[:-1],sham[:-1]),(word[1:],sham[1:])))
                sham_readings=prior.frame_orientations(prior.units(sham,cells))
                assert sham_readings and not any(old.factors(w[len(w)//2+1:],signal) for w in sham_readings)
                inc=word[1:]
                tiles=prior.units(inc,cells)
                local=[i for i in range(len(tiles)-1) if tiles[i:i+2]==tuple(pair_groups)]
                if mode.startswith("SS") and reader=="extended":
                    assert len(local)==1 and len(pair_groups[0])==len(pair_groups[1])==3
                actual_cc=ancestor_windows(inc,m,cells,False)
                strict_cc=ancestor_windows(inc,m,cells,True)
                c_runs=old.c_blocks(inc)
                reading.update(history)
                reading.update({"endpoint_prices_direct_extension_count":prices,"route":path,"raw_delay":n-m,
                                "oldest_group_donors":[sorted(a) for a in prior.units(word,cells)],
                                "mixed_local_rank_three_ancestor_in_incoming":[[i,i+3] for i in local],
                                "third_rank_m_ancestors_in_incoming":actual_cc,
                                "no_extra_third_rank_m_ancestors_in_incoming":strict_cc,
                                "largest_c_run_in_incoming":max((b-a for a,b in c_runs),default=0),
                                "incoming_word":inc,"neutral_sham_accepted":False})
                candidates.append(reading)
            rows.append({"send":m,"finite":bool(routes),"minimizers":candidates})
        out["readers"][reader]=rows
    return out


def four(values):
    return {"four_values":values,"all_four_equal":None if None in values else all(x==values[0] for x in values),
            "interaction":None if None in values else values[3]-values[2]-values[1]+values[0]}


def contrasts(cases):
    by_case={(a["lifetime"],a["gates"]):a for a in cases}
    results=[]
    for chamber,fixed,reader,idx in product(("shared","disjoint"),("CC","CS","SC","SS"),("extended","hereditary"),range(4)):
        sides={}
        for lifetime in ("active","finite"):
            local=[]
            for moving in ("CC","CS","SC","SS"):
                mode=moving+fixed if chamber=="shared" else fixed+moving
                a=by_case[lifetime,mode]
                entry=a["readers"][reader][idx]["minimizers"]
                w=entry[0] if entry else {}
                val={"raw_delay":w.get("raw_delay"),"ticks_after_send":w.get("ticks_after_send"),"own_from_origin":w.get("ticks_from_origin"),
                     "local_join_grant":a["local_common_child"]["grant"],
                     "shared_donor_nonunary_charges":a["source_groups_charged_to_shared_donor"],"shared_donor_unaries":a["shared_donor_unary_charges"]}
                val.update({key:w.get("price_vector",{}).get(key) for key in PRICE_FIELDS})
                # Each non-shared outer donor pays two local pair groups in C or a triple and a unary in S.
                for i,gatemode in enumerate(mode,1):
                    val[f"gate_{i}_group_charges_per_donor"]=2 if gatemode=="C" else 1
                    val[f"gate_{i}_unary_charges_per_local_slot"]=int(gatemode=="S")
                local.append(val)
            sides[lifetime]={key:four([v[key] for v in local]) for key in local[0]}
        differences={}
        for key in sides["active"]:
            a=sides["active"][key]["interaction"];b=sides["finite"][key]["interaction"]
            differences[key]=None if a is None or b is None else a-b
        results.append({"varied":chamber,"fixed":fixed,"reader":reader,"send":SIZES[idx],
                        "order":["CC","CS","SC","SS"],"comparisons":sides,"active_minus_finite_interactions":differences})
    return results


def main():
    cases=[case(life,mode) for life,mode in product(("active","finite"),("",*MODES))]
    bycase={(r["lifetime"],r["gates"]):r for r in cases}
    matched=[]
    for life in ("active","finite"):
        for i in range(4):
            weight_two={mode:bycase[life,mode]["readers"]["extended"][i]["minimizers"][0]["price_vector"]
                        for mode in MODES if mode.count("S")==2}
            assert len({tuple(v[k] for k in PRICE_FIELDS) for v in weight_two.values()})==1
            matched.append({"lifetime":life,"send":SIZES[i],"price_vectors":weight_two})
    opportunities=[]
    for mode,i,reader in product(("archive",*MODES), range(4), ("extended","hereditary")):
        aa=bycase["active",mode]["readers"][reader][i]["minimizers"]
        bb=bycase["finite",mode]["readers"][reader][i]["minimizers"]
        assert len(aa)==1 and len(bb)<=1
        for key in ("third_rank_m_ancestors_in_incoming","no_extra_third_rank_m_ancestors_in_incoming"):
            ac=len(aa[0][key]); bc=len(bb[0][key]) if bb else None
            opportunities.append({"mode":mode,"send":SIZES[i],"reader":reader,"eligible_family":key,
                                  "active_ancestors":ac,"finite_ancestors":bc,
                                  "matched_finite_receipt":bool(bb),
                                  "active_only":bool(ac and not bc) if bb else None})
    raw={"sampling":"complete named panel without prevalence inference","cases":cases,"four_arm_contrasts":contrasts(cases),
         "weight_two_price_matches":matched,"matched_shortest_opportunity":opportunities}
    OUTPUT.mkdir(exist_ok=True,parents=True)
    p=OUTPUT/"clock.json.gz"
    p.write_bytes(gzip.compress((json.dumps(raw,sort_keys=True,separators=(",",":"))+"\n").encode(),compresslevel=9,mtime=0))
    print("clock starts",len(cases),"sends per reader",len(cases)*4,"factorial comparisons",len(raw["four_arm_contrasts"]))
    print(p.name,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
