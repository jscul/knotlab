"""Necessary incidence, witness and ordinary price tests for an unmarked end."""
from collections import Counter, defaultdict
from itertools import combinations
import networkx as nx
from select_target import OUT
from census_stages import End, step, proposals


def evaluate(n,options,indices,previous):
    rows=[set(options[k]['support']) for k in indices]
    fresh=[set(options[k]['fresh']) for k in indices]
    U=[set(options[k]['inputs']) for k in indices]
    old=list(map(set,previous))
    inherited=[tuple(h for h,K in enumerate(old) if K & inputs) for inputs in U]
    if any(len(s)!=len(inputs) for s,inputs in zip(inherited,U)):return 'distinct parent',None
    if any(count>1 and len(p)>1 for p,count in Counter(inherited).items()):return 'nonunary birth cannot repeat',None
    now_end=End({j:len(f) for j,f in enumerate(fresh)},tuple(tuple(i for i,p in enumerate(inherited) if h in p) for h in range(len(old))))
    planned=proposals(now_end)
    demand=Counter(j for p in planned for j in p)
    if any(len(f)!=max(1,3-len(p),demand[j]) for j,(f,p) in enumerate(zip(fresh,inherited))):return 'previous fresh allocation',None
    # Current birth roster determines its previous witnessed pair graph:
    # each witnessed pair either became a pair birth or lies in a larger one.
    graph=nx.Graph()
    graph.add_nodes_from(range(len(old)))
    for p in inherited: graph.add_edges_from(combinations(p,2))
    maxsets={frozenset(c) for c in nx.find_cliques(graph) if len(c)>=3}
    multi={frozenset(p) for p in inherited if len(p)>=3}
    if not multi<=maxsets:return 'nonmaximal named group',None
    allpairs={frozenset(p) for p in graph.edges}
    remaining_pairs={p for p in allpairs if not any(p<=q for q in multi)}
    if {frozenset(p) for p in inherited if len(p)==2}!=remaining_pairs:return 'residual pairs',None
    fixed=[frozenset(j for j,K in enumerate(old) if j!=i and K&J) for i,J in enumerate(old)]
    if any(frozenset(p) not in allpairs for B in fixed for p in combinations(B,2)):return 'sibling co-witness contradiction',None
    if any(K<=B for K in multi for B in fixed):return 'required unheld group already jointly witnessed',None
    targets=allpairs|(maxsets-multi)
    targets={x for x in targets if not any(x<=f for f in fixed)}
    # Each as-yet unknown witness touches a clique, and cannot witness in
    # full any current multi-parent birth of size at least three.
    feasible_groups=[]
    for group in nx.find_cliques(graph):
        for m in range(2,len(group)+1):
            for g in combinations(group,m):
                g=frozenset(g)
                if any(r<=g for r in multi):continue
                if any(r<=g for r in targets):feasible_groups.append(g)
    feasible_groups=set(feasible_groups)
    use=Counter(x for H in (*rows,*old) for x in H)
    allfresh=set.union(*fresh)
    residual={x:(1 if x in allfresh else 2)-use[x] for x in range(n)}
    if min(residual.values())<0:return 'overfull named distinction',None
    budgets=[sum(residual[x] for x in K) for K in old]
    # For each endpoint all required previous/earlier witness sets through
    # that endpoint need simultaneous hits by distinct available slots.
    for j,budget in enumerate(budgets):
        family={r for r in targets if j in r}
        possible={frozenset(r for r in family if r<=g) for g in feasible_groups if j in g}
        reachable={frozenset()}
        for _ in range(min(budget,len(family))):
            reachable.update({seen|added for seen in reachable for added in possible})
            if frozenset(family) in reachable:break
        if frozenset(family) not in reachable:return 'too few old shared slots for required witnesses',None
    turn=step(now_end,'nae')
    assert turn.status=='extend'
    profile=tuple(sorted((tuple(sorted(tuple(sorted(rows[j])) for j in p)),q) for p,q in zip(turn.parents,turn.fresh)))
    payload=dict(roster=profile,previous_groups=inherited,residual=[residual[x] for x in range(n)],
                 previous_witness_obligations=[sorted(s) for s in sorted(targets,key=lambda s:(len(s),tuple(sorted(s))))])
    return 'viable',payload
