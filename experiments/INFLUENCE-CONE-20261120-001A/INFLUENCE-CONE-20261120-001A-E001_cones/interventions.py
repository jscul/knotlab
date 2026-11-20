"""Physical intervention, terminal observation and serial delivery controls."""
from argparse import ArgumentParser
from collections import Counter
import json
from pathlib import Path
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "interventions.json"
for ticket, tag in [("READ-ORIGIN-20261120-001A", "origins"),
                    ("FRESH-DEMAND-20261120-001A", "orders")]:
    sys.path.insert(0, str(ROOT / "experiments" / ticket / (ticket + "-E001_" + tag)))
from boundaries import law_gate, ownership, recode, source, stage_size, write_layer
from end_operator import from_stars, neighbors, proposals, step
import serial_orders


def private(rows, holder):
    result = rows.copy()
    result[holder] += (max(ownership(rows)) + 1,)
    return result


def end_of(rows):
    return from_stars([rows[i] for i in range(len(rows))])


def distances(rows, sender, receiver):
    end = end_of(rows)
    full = nx.Graph(neighbors(end))
    two = nx.Graph()
    two.add_nodes_from(end.opens)
    two.add_edges_from(group for group in proposals(end) if len(group) == 2)
    physical = nx.Graph()
    physical.add_nodes_from(rows)
    physical.add_edges_from(tuple(h) for h in ownership(rows).values() if len(h) == 2)

    def distance(graph):
        if sender not in graph or receiver not in graph:
            return "inactive"
        if not nx.has_path(graph, sender, receiver):
            return "infinite"
        return nx.shortest_path_length(graph, sender, receiver)
    return {label: distance(graph) for label, graph in
            [("witness", full), ("exact_two", two), ("physical", physical)]}


def literal_layer(rows, law):
    end = end_of(rows)
    plan = step(end, law)
    assert plan.status == "extend"
    grown = write_layer(rows, law)
    old = ownership(rows)
    actual = []
    for k in sorted(set(grown) - set(rows)):
        inputs = [v for v in grown[k] if v in old]
        parents = tuple(sorted(old[v][0] for v in inputs))
        assert all(len(old[v]) == 1 for v in inputs)
        actual.append((k, parents, len(grown[k]) - len(parents)))
    assert Counter((p, h) for k, p, h in actual) == Counter(zip(plan.parents, plan.fresh))
    return grown, actual


def invariant(rows, r, law):
    def roster(frame, target, inverse):
        _, births = literal_layer(frame, law)
        return sorted((sorted(inverse[p] for p in ps), h)
                      for _, ps, h in births if target in ps)
    renamed, bijection = recode(rows, 20261120854)
    a = roster(rows, r, {k:k for k in rows})
    b = roster(renamed, bijection[r], {v:k for k,v in bijection.items()})
    assert a == b
    return a


def owner_edit(law):
    rows = source(6, [(i, (i+1) % 6) for i in range(6)], [3]*6)
    shared, = set(rows[0]) & set(rows[5])
    edited = rows.copy()
    edited[0] = tuple(v for v in rows[0] if v != shared)
    plus_at_five = private(rows, 5)
    assert all(rows[k] == edited[k] for k in range(1,6))
    assert ownership(edited)[shared] == [5]
    arms = {}
    for name, form in [("intact", rows), ("changed_holder_zero", edited),
                       ("same_extra_open_at_five", plus_at_five)]:
        assert law_gate(form, law, {})
        e = end_of(form)
        unmarked = invariant(form, 1, law)
        r, s = {1}, {0}
        exposure = []
        for _ in range(2):
            form, records = literal_layer(form, law)
            r = {k for k, ps, h in records if r.intersection(ps)}
            s = {k for k, ps, h in records if s.intersection(ps)}
            assert not r & s
            exposure.append(dict(total=len(records), receiver=len(r),
                                 fresh=sum(h for k, ps, h in records if k in r),
                                 common=len(r&s)))
        start = {"intact":rows,"changed_holder_zero":edited,"same_extra_open_at_five":plus_at_five}[name]
        arms[name] = dict(holdings=stage_size(start), root_opens=e.opens[1], openings=e.opens,
                          blocks=e.blocks, distance_owner=distances(start,0,1),
                          distance_other_holder=distances(start,5,1), local=unmarked, trace=exposure)
        assert arms[name]["distance_owner"]=={"witness":"infinite","exact_two":"infinite","physical":1}
    assert end_of(edited).opens==end_of(plus_at_five).opens
    arity = lambda arm: sorted(len(p) for p,_ in arms[arm]["local"])
    assert arity("intact")==arity("same_extra_open_at_five")==[1,1,3]
    assert arity("changed_holder_zero")==[1,1,2]
    return arms


def closure_source(length, enabled):
    # Three live roots and three pair witnesses. A spent alternate route joins two
    # witnesses. Its middle alone optionally carries one previously absent loose bit.
    joins = [(0,3),(1,3),(1,4),(2,4),(0,5),(2,5)]
    interior = list(range(6,6+2*length-1))
    route = [3,*interior,4]
    joins.extend(zip(route,route[1:]))
    sender=route[length]
    rows=source(6+len(interior), [pair for pair in joins for _ in range(2)],
                [1]*3+[0]*(3+len(interior)))
    return (private(rows,sender) if enabled else rows),sender


def terminal(length,law):
    result={}
    for mode in (False,True):
        rows,sender=closure_source(length,mode)
        assert law_gate(rows,law,{})
        compare=invariant(rows,0,law)
        grown,births=literal_layer(rows,law)
        child,=[k for k,ps,h in births if ps==(0,1,2)]
        openings=end_of(grown).opens
        accepted=set()
        bits=[next(v for v in rows[k] if len(ownership(rows)[v])==1) for k in range(3)]
        if law=="parity":
            from outside import rank_of
            masks=[sum(1<<v for v in support) for support in rows.values()]
            for row in range(8):
                # Augmented equations, with RHS held above every physical bit.
                fixed=[1<<v for v in bits]
                column=1<<(max(ownership(rows))+1)
                aug=[g | (column if row>>j&1 else 0) for j,g in enumerate(fixed)]
                if rank_of(masks+fixed)==rank_of(masks+aug):
                    accepted.add(row)
        else:
            from pysat.solvers import Minisat22
            clauses=[[sign*(v+1) for v in support] for support in rows.values() for sign in (1,-1)]
            with Minisat22(bootstrap_with=clauses) as sat:
                for row in range(8):
                    if sat.solve(assumptions=[(v+1)*(1 if row>>j&1 else -1) for j,v in enumerate(bits)]):
                        accepted.add(row)
        expected=0 if law=="parity" and not mode else 1
        assert compare==[([0,1,2],expected)]
        assert len(grown[child])==3+expected and openings.get(child,0)==expected
        assert len(accepted)==(4 if law=="parity" and not mode else 8)
        result["remote_on" if mode else "remote_off"]=dict(
            old_size=stage_size(rows), separation=distances(rows,sender,0), roster=compare,
            observed_child_size=len(grown[child]), formed=len(births), new_size=stage_size(grown),
            still_live=bool(openings), projected_rows=sorted(accepted))
    return result


def structural_source(length, enabled):
    names=["r","a","b","x","y"]+["r"+str(i) for i in range(1,length+1)]
    tail=["r"]+names[5:]
    core=[("r","a"),("r","b"),("a","b"),("a","x"),("a","y"),("b","x"),("b","y")]
    bonds=[]
    for u,v in core+list(zip(tail,tail[1:])):
        w="w_"+u+"_"+v
        names.append(w)
        for point in (u,v):
            bonds.extend([(point,w)]*2)
    names.append("switch")
    bonds.extend([("switch","x")]*2+[("switch","w_a_x")]*2)
    supplies={"r":2,"a":3,"b":3,"x":1,"y":1,"w_r_a":2,**dict.fromkeys(tail,2)}
    ids={k:i for i,k in enumerate(names)}
    rows=source(len(names),[(ids[u],ids[v]) for u,v in bonds],[supplies.get(k,0) for k in names])
    if enabled:
        bit=max(ownership(rows))+1
        for s in ["switch","y"]:
            rows[ids[s]]+=(bit,)
    return rows,ids,ids[tail[-1]]


def charged(length,law):
    d=length+2
    cases={}
    for mode in (False,True):
        rows,ids,r=structural_source(length,mode)
        assert law_gate(rows,law,{})
        raw=rows
        s={ids["x"],ids["y"]}
        assert all(distances(rows,x,r)["witness"]==d for x in s)
        inc={r}
        trace=[]
        for i in range(1,d+1):
            end=end_of(rows)
            limited=step(end,law,max_births=840)
            if limited.status=="cap":
                trace.append(dict(depth=i,status="cap",min_births=limited.planned_births_lower))
                break
            assert limited.status=="extend"
            rows,actual=literal_layer(rows,law)
            inc={k for k,ps,h in actual if inc.intersection(ps)}
            s={k for k,ps,h in actual if s.intersection(ps)}
            fs=sorted(h for k,ps,h in actual if k in inc)
            assert bool(inc&s)==(i>=d)
            if i<=d-2:
                assert set(fs)=={2}
            if i==d-1:
                assert fs==[2]*(len(fs)-1)+[4 if mode else 3]
            trace.append(dict(depth=i,roster=len(inc),common=len(inc&s),
                              local_fresh=dict(sorted(Counter(fs).items())),
                              total_births=len(actual),accumulated=stage_size(rows)))
        cases["on" if mode else "off"]=dict(root_profile=invariant(raw,r,law),
              witness_distance=d,exact_two_distance=distances(raw,ids["x"],r)["exact_two"],
              cohort=trace)
    off,on=cases["off"]["cohort"],cases["on"]["cohort"]
    for i,(o,a) in enumerate(zip(off,on),1):
        if "cap" in [o.get("status"),a.get("status")]:
            break
        assert a["roster"]-o["roster"]==(i==d)
    return cases


def serial():
    result={}
    for live in (False,True):
        rows=serial_orders.source(9,2,live)
        arms={}
        for law in ("parity","nae"):
            plan=serial_orders.plan_whole_layer(rows,law)
            target=next(e for e in plan if e["parents"]==serial_orders.TARGET)
            marks=target["consumed"]
            orders=serial_orders.all_preplanned_permutations(rows,plan)
            prefix=serial_orders.grade_prefixes(rows,law,True,marks)
            prefix_all=serial_orders.grade_prefixes(rows,law,False,marks)
            arms[law]=dict(fixed=orders,fixed_target_fresh=len(target["fresh"]),
                           joins_first=prefix,any_move=prefix_all)
        result["live" if live else "spent"]=arms
    return result


def main():
    parser=ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUT)
    target=parser.parse_args().out
    both={}
    for law in ("parity","nae"):
        both[law]=dict(owner_edit=owner_edit(law),
                       first_step_closure={str(i):terminal(i,law) for i in [2,4,8]},
                       charged={str(i+2):charged(i,law) for i in [0,1,2,3]})
    output=dict(laws=both,serial=serial())
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":
    main()
