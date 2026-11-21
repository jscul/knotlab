"""Compare all actual parent rosters and grants to connected rank extensions through rank ten."""
from collections import Counter, defaultdict
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
from pathlib import Path
import json
import networkx as nx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TARGET=ROOT/"artifacts"/HERE.parent.name/HERE.name
PRIOR="JOINT-PARENTS-AND-ERASURE-20261120-001A"
SPEC=spec_from_file_location("native_groups", ROOT/"experiments"/PRIOR/(PRIOR+"-E001_joint_parents")/"check_cells.py")
old=module_from_spec(SPEC)
SPEC.loader.exec_module(old)
MAX_RANK=10
GATES=(frozenset((0,1,2)),frozenset((1,3,4)))
P=1


def prepare(modes):
    real=set(range(6))
    graph=nx.Graph()
    for cell in (*GATES,(0,5)):
        graph.add_edges_from(combinations(cell,2))
    supply={p:max(2,graph.degree(p)) for p in real}
    witnesses=[frozenset((0,5))]
    separate=[]
    for cell,mode in zip(GATES,modes):
        if mode=="S":
            separate.append(cell)
            witnesses.extend(frozenset(pair) for pair in combinations(cell,2))
        else:
            witnesses.append(cell)
    demand=Counter(p for group in old.groups(real,witnesses) for p in group)
    next_id=6
    for p in sorted(real):
        for _ in range(supply[p]-demand[p]):
            pendant=next_id;next_id+=1
            graph.add_edge(p,pendant)
            for _ in range(max(0,3-supply[p])):
                last=pendant
                for _ in range(MAX_RANK+1):
                    graph.add_edge(last,next_id);last=next_id;next_id+=1
    return real,graph,supply,witnesses,separate


def rank(s,separate):
    return len(s)-sum(cell<=s for cell in separate)


def extensions(s,graph,separate):
    found=set()
    for x in s:
        for y in graph[x]:
            if y in s: continue
            t=s|{y}
            while True:
                closed=t.union(*(block for block in separate if len(t&block)>=2))
                if closed==t: break
                t=closed
            if rank(t,separate)==rank(s,separate)+1:
                found.add(frozenset(t))
    return found


def ambient(points):
    code={0:2,1:1,2:3,3:4,4:5}
    values={0}
    for p in points:
        values|={x^code[p] for x in values}
    return values


def ss_restrictions():
    graph=nx.Graph()
    for block in GATES: graph.add_edges_from(combinations(block,2))
    valid=[]
    for n in range(6):
        for tup in combinations(range(5),n):
            s=frozenset(tup)
            if s and not nx.is_connected(graph.subgraph(s)): continue
            if any(len(s&b)==2 for b in GATES):continue
            assert len(ambient(s))==2**rank(s,GATES)
            valid.append(s)
    for a,b in product(valid,repeat=2):
        assert ambient(a)&ambient(b)==ambient(a&b)
        if not (a&b) and a and b:
            continue
        c=a|b
        while True:
            d=c.union(*(cell for cell in GATES if len(c&cell)>=2))
            if c==d:break
            c=d
        assert c in valid and ambient(c)=={i^j for i in ambient(a) for j in ambient(b)}
    full=frozenset(range(5))
    facets=[sorted(x) for x in valid if rank(x,GATES)==2 and x<=full]
    assert {tuple(x) for x in facets}=={tuple(sorted(x)) for x in GATES}
    return {"restrictions":[sorted(s) for s in valid],"missing_nonzero_vectors":[6,7],
            "full_five_originals_rank":rank(full,GATES),"full_actual_predecessors":facets}


def check(modes):
    real,g,supply,witnesses,separate=prepare(modes)
    roster=[frozenset({x}) for x in sorted(real)]
    h=[supply[x] for x in sorted(real)]
    rows=[]
    for current_rank in range(1,MAX_RANK):
        native=old.groups(range(len(roster)),witnesses)
        debit=Counter(p for group in native for p in group)
        assert all(h[i]>=debit[i] for i in range(len(h)))
        native.extend(frozenset({i}) for i in range(len(h)) for _ in range(h[i]-debit[i]))
        next_witnesses=[{j for j,group in enumerate(native) if i in group} for i in range(len(roster))]
        proposals=old.groups(range(len(native)),next_witnesses)
        next_demand=Counter(p for group in proposals for p in group)
        next_grants=[max(1,3-len(group),next_demand[i]) for i,group in enumerate(native)]
        by_support=defaultdict(set)
        for i,s in enumerate(roster):
            for t in extensions(s,g,separate):
                by_support[t].add(i)
        by_parents=defaultdict(list)
        for t,parents in sorted(by_support.items(),key=lambda z:tuple(sorted(z[0]))):
            by_parents[frozenset(parents)].append(t)
        roots=[]
        for i,group in enumerate(native):
            assert by_parents[group],(modes,current_rank,group)
            s=by_parents[group].pop()
            assert next_grants[i]==len(extensions(s,g,separate)),(modes,current_rank,group,s,next_grants[i])
            roots.append(s)
        assert not any(by_parents.values())
        rows.append({"rank":current_rank+1,"new_knots":len(native),"parent_arity":dict(sorted(Counter(map(len,native)).items())),
                     "actual_fresh":dict(sorted(Counter(next_grants).items()))})
        roster,h,witnesses=roots,next_grants,next_witnesses
    return rows


def main():
    cases={"".join(m):check(m) for m in product("CS",repeat=2)}
    result={"cases":cases,"witness":"two marked triples sharing p with separately funded original and unary control",
            "ss_adjacent_block":ss_restrictions(),"both_laws":"nonclosing funded end",
            "total_new_births":sum(r["new_knots"] for rows in cases.values() for r in rows)}
    TARGET.mkdir(parents=True,exist_ok=True)
    p=TARGET/"rank_check.json"
    p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(result["total_new_births"],"complete native births",sha256(p.read_bytes()).hexdigest())


if __name__=="__main__":main()
