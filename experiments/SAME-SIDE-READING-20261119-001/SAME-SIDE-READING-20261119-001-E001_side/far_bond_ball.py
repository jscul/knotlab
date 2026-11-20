"""Independent satisfiability enumeration of actual small bonds touching a fixed old mark."""
from collections import Counter
from pathlib import Path
import json

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from moving_count import adjacency
from side_sources import cases, generate, loads

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def anchored(stars, origin, limit, conflict_cap=250_000, model_cap=4000):
    holders, _ = adjacency(stars)
    outside = len(stars)
    ends = {m:tuple(vs) if len(vs)==2 else (vs[0],outside) for m,vs in holders.items()}
    edge_var = {m:i+outside+2 for i,m in enumerate(sorted(holders))}
    clauses=[[-(outside+1)], [edge_var[origin]]]
    for m,(u,v) in ends.items():
        a,b,c=u+1,v+1,edge_var[m]
        clauses.extend(([a,b,-c],[-a,-b,-c],[a,-b,c],[-a,b,c]))
    clauses.extend(CardEnc.atmost(lits=list(edge_var.values()),bound=limit,
                                  top_id=max(edge_var.values()),encoding=EncType.seqcounter).clauses)
    bonds=[]; visited=0
    with Solver(name="g4",bootstrap_with=clauses) as solver:
        while visited < model_cap:
            left=conflict_cap-solver.accum_stats()["conflicts"]
            if left <= 0:
                return {"complete":False,"models":visited,"bonds":bonds}
            solver.conf_budget(left)
            solvable=solver.solve_limited()
            if solvable is None or not solvable:
                return {"complete":solvable is False,"models":visited,
                        "conflicts":solver.accum_stats()["conflicts"],"bonds":bonds}
            model=set(solver.get_model())
            cut={m for m,x in edge_var.items() if x in model}
            assert origin in cut and len(cut)<=limit
            keep=nx.Graph()
            keep.add_nodes_from(range(outside+1))
            keep.add_edges_from(uv for m,uv in ends.items() if m not in cut)
            parts=list(nx.connected_components(keep))
            colors={v:i for i,part in enumerate(parts) for v in part}
            assert len(parts)>=2
            quotient=nx.Graph()
            quotient.add_nodes_from(range(len(parts)))
            quotient.add_edges_from((colors[ends[m][0]], colors[ends[m][1]]) for m in cut)
            removable=set(quotient)-set(nx.articulation_points(quotient))
            p,q=ends[origin]
            chosen=min(removable,key=lambda u:(u not in (colors[p],colors[q]),len(parts[u]),min(parts[u])))
            shore=parts[chosen]
            support=sorted(m for m,(u,v) in ends.items() if (u in shore)!=(v in shore))
            assert set(support)<=cut and support
            if origin in support:
                bonds.append(support)
            # No other minimal parity bond can strictly contain this verified
            # bond, regardless of whether this component contains the anchor.
            solver.add_clause([-edge_var[m] for m in support])
            visited+=1
    return {"complete":False,"models":visited,"bonds":bonds}


def check_frame(stars, marks=(8,12), limit=8):
    holders,_=adjacency(stars)
    bank={m:anchored(stars,m,limit) for m in marks}
    balls=[]
    for size in range(1,limit+1):
        members=set(marks)
        for rec in bank.values():
            for bond in rec["bonds"]:
                if len(bond)<=size:
                    members.update(bond)
        balls.append(len({v for m in members for v in holders[m]}))
    return {"complete":all(r["complete"] for r in bank.values()),"roots":bank,"knots_by_bond_radius":balls}


def literal_control():
    # Four pairwise meetings on a ring with one loose distinction at each holder.
    stars=[(0,3,4),(0,1,5),(1,2,6),(2,3,7)]
    cuts=set()
    for shore in range(1,1<<len(stars)):
        active=set()
        for v,star in enumerate(stars):
            if (shore>>v)&1:
                active.symmetric_difference_update(star)
        cuts.add(frozenset(active))
    minimal={b for b in cuts if b and not any(c and c<b for c in cuts)}
    for anchor in range(8):
        result=anchored(stars,anchor,6)
        assert result["complete"]
        assert set(map(frozenset,result["bonds"]))=={b for b in minimal if len(b)<=6 and anchor in b}
    return {"all_anchors":8,"literal_minimal_bonds":len(minimal)}


def main():
    spec=cases()["J1"]
    out={"literal_control":literal_control(),"marks":[8,12],"age":3,"arms":{}}
    for arm,state in loads(spec).items():
        for age,frame in generate(spec,state,max_age=3):
            if age==3:
                r=check_frame(frame["stars"])
                out["arms"][arm]=r
                print(arm, r["complete"],r["knots_by_bond_radius"],
                      [(len(x["bonds"]),x["models"]) for x in r["roots"].values()], flush=True)
    (DATA/"far_bond_ball.json").write_text(json.dumps(out,separators=(",",":"))+"\n")


if __name__=="__main__":
    main()

