"""Check a last-slot fork directly against its physical writes and the prior clock."""
from collections import Counter, defaultdict
from copy import deepcopy
from itertools import combinations, product
from pathlib import Path
import json

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher
from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ID = HERE.parent.name
PRIOR = "TICK-BIRTHS-AND-SCARCITY-20261121-001B"
ARCHIVE = ROOT / "artifacts" / PRIOR / (PRIOR + "-E001_serial")
THIS = ROOT / "artifacts" / ID / (ID + "-E001_last_slot")


def physical(stars, nsource):
    owners = defaultdict(list)
    for k, row in enumerate(stars):
        assert len(row) == len(set(row))
        for d in row:
            owners[d].append(k)
    loose = [set() for _ in stars]
    neighbours = [set() for _ in stars]
    for d, at in owners.items():
        if len(at) == 1:
            loose[at[0]].add(d)
        else:
            a, b = at
            neighbours[a].add(b)
            neighbours[b].add(a)
    parents = {c: tuple(sorted(k for k in neighbours[c] if k < c)) for c in range(nsource, len(stars))}
    return owners, loose, neighbours, parents


def groups(nb, live):
    graph = nx.Graph()
    for row in nb:
        graph.add_edges_from(combinations(row & live, 2))
    large = [set(s) for s in nx.find_cliques(graph)
             if len(s) >= 3 and not set.intersection(*(nb[q] for q in s))]
    pairs = [set(p) for p in graph.edges if not any(set(p) <= s for s in large)]
    return {tuple(sorted(group)) for group in large + pairs}


def admissible(nb, loose, parents):
    live = {p for p, ds in enumerate(loose) if ds}
    old = [set(group) for group in parents.values()]
    joins = {g for g in groups(nb, live) if not any(set(g) <= h for h in old)}
    count = Counter(p for g in joins for p in g)
    unary = {(p,) for p in live if len(loose[p]) > count[p]}
    return joins | unary, joins if joins else unary


def parity_reduce(row, basis):
    while row and row.bit_length() in basis:
        row ^= basis[row.bit_length()]
    return row


def admits_each_input(stars, spent, law):
    if law == "parity":
        basis = {}
        for row in stars:
            reduced = parity_reduce(sum(1 << d for d in row), basis)
            if reduced:
                basis[reduced.bit_length()] = reduced
        return all(parity_reduce(sum(1 << d for d in part), basis) for k in range(1, len(spent)+1)
                   for part in combinations(spent, k))
    with Minisat22() as solver:
        for row in stars:
            solver.add_clause([d+1 for d in row])
            solver.add_clause([-d-1 for d in row])
        return all(solver.solve(assumptions=[(d+1)*v for d,v in zip(spent, signs, strict=True)])
                   for signs in product((-1,1), repeat=len(spent)))


def source_law(stars, law):
    owners, _, nb, _ = physical(stars, len(stars))
    graph = nx.Graph((i,j) for i,row in enumerate(nb) for j in row)
    assert nx.is_connected(graph)
    assert all(len(row) >= 3 for row in stars) and len(set(owners)) > 0
    if law == "parity":
        # Each source row is its only local equation if constraints vanish
        # on every codimension-one subset of its support.
        for row in stars:
            assert all(admits_each_input(stars, row[:k]+row[k+1:],law) for k in range(len(row)))
    else:
        with Minisat22() as solver:
            for row in stars:
                solver.add_clause([d+1 for d in row])
                solver.add_clause([-d-1 for d in row])
            for row in stars:
                for signs in product((-1,1), repeat=len(row)):
                    projected = solver.solve(assumptions=[v*(x+1) for v,x in zip(signs,row)])
                    assert projected == (len(set(signs)) == 2)


def write(stars, nsource, event, law):
    owners, loose, nb, earlier = physical(stars, nsource)
    raw, priority = admissible(nb, loose, earlier)
    ps = tuple(event["parents"])
    ds = event["consumed_slots"]
    assert ps in raw and event["child"] == len(stars)
    assert len(ds) == len(ps) and all(owners[d] == [p] for p,d in zip(ps,ds))
    assert len(ds) < sum(map(len, loose)) and admits_each_input(stars, ds, law)
    child = len(stars)
    provisional = stars + [ds]
    _, remaining, tmp_nb, _ = physical(provisional, nsource)
    live = {j for j,l in enumerate(remaining) if l} | {child}
    demand = {g for g in groups(tmp_nb,live) if child in g}
    assert demand == set(map(tuple,event["current_demand"]))
    fresh = event["fresh"]
    assert len(fresh) == max(1, 3-len(ps), len(demand))
    assert not set(owners).intersection(fresh) and len(fresh) == len(set(fresh))
    return stars + [ds+fresh], ps in priority


def history(stars, nsource, events, law):
    priorities = []
    for event in events:
        stars, scored = write(stars, nsource, event, law)
        priorities.append(scored)
    return stars, priorities


def rooted(parents, root, nsource):
    graph = nx.DiGraph()
    todo = [root]
    while todo:
        k = todo.pop()
        if k in graph and "name" in graph.nodes[k]:
            continue
        role = ("source",k) if k < nsource else ("born",k == root)
        graph.add_node(k, name=role)
        for p in parents.get(k, ()):
            graph.add_edge(p,k)
            todo.append(p)
    return graph


def clock():
    guard = json.loads((ARCHIVE/"receipt.json").read_bytes())["laws"]["parity"]["bare"]
    later = guard["complete_cuts"]["6"]["supports"]
    target = guard["tick_windows"]["6"]["tick"]
    _, _, _, parents = physical(later, 8)
    shape = rooted(parents, target, 8)
    required = {k:parents[k] for k in shape if k>=8}
    assert len(required) == 20 and set(shape)-set(required) == {0,2,4,6}
    return shape, required


def matches(stars, ns, target_shape):
    _,_,_, parents = physical(stars, ns)
    found = {}
    for k in parents:
        graph = rooted(parents,k,ns)
        if len(graph) == len(target_shape):
            matcher = DiGraphMatcher(target_shape,graph,node_match=lambda x,y: x["name"]==y["name"])
            count = sum(1 for _ in matcher.isomorphisms_iter())
            if count:
                found[k] = count
    return found


def fixed_role_parents(common, source_size, template):
    """Find required roles whose actual parent set all future complete turns must use."""
    _, loose, _, actual = physical(common, source_size)
    children = defaultdict(list)
    for k, ps in actual.items():
        children[ps].append(k)
    fixed = {i:i for i in (0,2,4,6)}
    outputs = {}
    for role in sorted(template):
        if not all(i in fixed for i in template[role]):
            continue
        ps = tuple(sorted(fixed[i] for i in template[role]))
        outputs[role] = ps
        current = children.get(ps, [])
        if len(current) != 1:
            continue
        if len(ps) >= 2:
            # Common-child veto rules out a second child on these exact parents.
            fixed[role] = current[0]
        elif not loose[ps[0]]:
            fixed[role] = current[0]
        elif ps == (0,):
            # Every complete target also needs these two original pairs.
            # If all remaining slots are needed for them, any further unary
            # can never occur on a complete-target continuation.
            pair_needs = {(0,2),(0,6)}
            assert pair_needs <= set(template.values())
            debts = sum(not children.get(p) for p in pair_needs)
            if len(loose[0]) <= debts:
                fixed[role] = current[0]
    return outputs, children


def paid_first_spend_boundary(shape, needed):
    archive = json.loads((ARCHIVE/"raw.json").read_bytes())["sources"]["same_continuation"]
    out = {}
    for law, old in archive.items():
        stars = old["source"]
        source_law(stars, law)
        _, loose, nb, parents = physical(stars,9)
        raw, priority = admissible(nb,loose,parents)
        outside = sorted(g for g in raw if 8 in g)
        assert nb[8] == {3} and nb[3] == {2,4,8}
        assert outside == [(2,8),(4,8)]
        true_pairs = {ps for ps in needed.values() if max(ps) < 8 and len(ps) == 2}
        assert {q for q in true_pairs if 2 in q} == {(0,2),(2,4)}
        assert {q for q in true_pairs if 4 in q} == {(2,4),(4,6)}
        assert len(loose[2]) == len(loose[4]) == 3
        assert all(g in priority for g in outside)
        trace = old["cold"]["unrestricted"]["ascending"]["trace"]
        completed, eligible = history(stars,9,trace,law)
        assert matches(completed,9,shape) == {len(completed)-1:1}
        out[law] = {"initial_eligible_outside_payments":outside,"pure_role_control_writes":len(trace)}
    return out


def make_event(stars, ns, ps, force_slots=None):
    owners, loose, nb, prior = physical(stars,ns)
    offered, _ = admissible(nb,loose,prior)
    if ps not in offered:
        return None
    force_slots = force_slots or {}
    spent = [force_slots.get(p,min(loose[p])) for p in ps]
    assert all(d in loose[p] for p,d in zip(ps,spent))
    born = len(stars)
    _, current, after_nb, _ = physical(stars+[spent],ns)
    live = {j for j,slots in enumerate(current) if slots} | {born}
    demand = sorted(g for g in groups(after_nb,live) if born in g)
    count = max(1,3-len(ps),len(demand))
    first = max(owners)+1
    return {"parents":list(ps),"consumed_slots":spent,"child":born,"current_demand":[list(g) for g in demand],
            "fresh":list(range(first,first+count))}


def fork_certificate(stars, ns, required, control, outside, law):
    owners, loose, nb, actual = physical(stars,ns)
    offered, priority = admissible(nb,loose,actual)
    rp, op = tuple(control["parents"]), tuple(outside["parents"])
    assert rp in offered and op in offered
    assert len(rp)>1 and not set(rp).issubset(op), "the treatment includes the required parent set"
    fixed,children = fixed_role_parents(stars,ns,required)
    unpaid = [role for role,ps in fixed.items() if ps == rp and not children.get(ps)]
    assert unpaid, "needed fixed-parent obligation is missing"
    target_donors = [d for d in set(rp).intersection(op) if len(loose[d])==1]
    assert len(target_donors)==1, "a unique shared last-slot donor is required"
    donor, = target_donors
    last, = loose[donor]
    assert control["consumed_slots"][rp.index(donor)] == outside["consumed_slots"][op.index(donor)] == last
    outsider = ns-1
    assert outsider not in rooted(actual,donor,ns)
    paths = []
    for j in op:
        a = rooted(actual,j,ns)
        if j != donor and outsider in a:
            paths.append(nx.shortest_path(a,outsider,j))
    assert paths, "outside birth has no distinct outside-paying parent"
    earlier = {k:list(ps) for k,ps in actual.items() if donor in ps}
    assert not any(set(rp).issubset(ps) for ps in earlier.values())
    spent,_ = write(stars,ns,outside,law)
    _, remainder, _, past = physical(spent,ns)
    assert not remainder[donor]
    assert not any(set(rp).issubset(ps) for ps in past.values())
    return {"required_actual_parents":rp, "permanently_mandatory_bare_template_roles":unpaid,
            "outside_actual_parents":op, "outside_payment_paths_from_H":paths, "donor":donor,
            "actual_last_slot":last, "prior_children_of_donor":earlier,
            "both_joins_first_at_fork":rp in priority and op in priority,
            "physical_old_slots_of_outside_after":sorted(remainder[outsider]),
            "physical_old_slots_of_other_required_parent_after":
                {p:sorted(remainder[p]) for p in rp if p!=donor}}


def validate_equal_index(common_state, ns, lost_step, count, shape, law):
    current,_ = write(common_state,ns,lost_step,law)
    trace=[]
    for _ in range(count-1):
        _,loose,nb,prior=physical(current,ns)
        offered,_=admissible(nb,loose,prior)
        assert offered
        selected=min(offered,key=lambda g:sum(1<<p for p in g))
        event=make_event(current,ns,selected)
        current,_=write(current,ns,event,law)
        trace.append(event)
    assert not matches(current,ns,shape)
    return trace


def omit_ninth(w, shape, law):
    source = w["source"]
    ns = len(source)
    before,_=history(source,ns,w["common"][:-1],law)
    outside=tuple(w["treatment"][0]["parents"])
    donor=w["fork"]["donor"]
    last=w["fork"]["slot"]
    _,loose,_,_=physical(before,ns)
    assert len(loose[donor])==2 and last in loose[donor]
    prepare=make_event(before,ns,outside,{donor:last})
    if prepare is None:
        return {"outside_was_admitted":False,"slots_before":sorted(loose[donor])}
    after,_=write(before,ns,prepare,law)
    _,remain,_,_=physical(after,ns)
    assert len(remain[donor])==1
    prefix=after
    follow=[]
    for scored in w["control"]:
        event=make_event(prefix,ns,tuple(scored["parents"]))
        if not event:
            break
        prefix,_=write(prefix,ns,event,law)
        follow.append(event)
    return {"outside_was_admitted":True,"slots_before":sorted(loose[donor]),"slots_after":sorted(remain[donor]),
            "consumed_same_name":last,"next_required_birth_replayed":bool(follow),
            "followed_events":len(follow),"proposed_control_events":len(w["control"]),
            "marked_children":list(matches(prefix,ns,shape)), "outside":prepare, "follow":follow}


def main():
    saved=json.loads((THIS/"witness.json").read_text())
    shape,needed=clock()
    summary={"first_outside_class":paid_first_spend_boundary(shape,needed),"laws":{}}
    for law,w in saved["witnesses"].items():
        source=w["source"]
        ns=len(source)
        source_law(source,law)
        common,cp=history(source,ns,w["common"],law)
        assert matches(common,ns,shape)=={}
        c,cc=history(common,ns,w["control"],law)
        hits=matches(c,ns,shape)
        assert hits == {len(c)-1:1}
        treatment,lp=history(common,ns,w["treatment"],law)
        assert not matches(treatment,ns,shape)
        cert=fork_certificate(common,ns,needed,w["control"][0],w["treatment"][0],law)
        through=validate_equal_index(common,ns,w["treatment"][0],len(w["control"]),shape,law)
        no_ninth=omit_ninth(w,shape,law)
        try:
            fork_certificate(common,ns,needed,w["control"][0],w["control"][0],law)
        except AssertionError as e:
            assert str(e)=="the treatment includes the required parent set"
        else:
            raise AssertionError("obsolete prior-common-child substitute passed")
        assert no_ninth["slots_after"] and no_ninth["next_required_birth_replayed"]
        assert no_ninth["marked_children"] == [len(c)-1]
        pre8,_ = history(source,ns,w["common"][:-1],law)
        same_old = no_ninth["outside"]
        possible = make_event(pre8,ns,tuple(w["control"][0]["parents"]),
                              {cert["donor"]:cert["actual_last_slot"]})
        try:
            fork_certificate(pre8,ns,needed,possible,same_old,law)
        except AssertionError as err:
            assert str(err)=="a unique shared last-slot donor is required"
        else:
            raise AssertionError("two available slots incorrectly counted as one")
        renamed=saved["reversed_source_names"][law]
        rs=renamed["source"]
        source_law(rs,law)
        rc,_ = history(rs,len(rs),renamed["common"],law)
        rw,_ = history(rc,len(rs),renamed["control"],law)
        assert matches(rw,len(rs),shape) == {len(rw)-1:1}
        renumbered = fork_certificate(rc,len(rs),needed,renamed["control"][0],renamed["treatment"][0],law)
        summary["laws"][law]={"fork":cert,"target_source_pair_incidence":
                        sorted(ps for ps in needed.values() if len(ps)==2 and max(ps)<8),
                        "common_count":len(cp),"first_joins_first_violation":
                        next((i for i,v in enumerate(cp,1) if not v),None),
                        "all_control_suffix_is_joins_first":all(cc),"all_loss_suffix_is_joins_first":all(lp),
                        "clock_birth_at_global_event":len(c)-ns,
                        "irreversible_loss_at_global_event":len(common)-ns+1,
                        "matched_event_budget":{"control_marked_holder":max(hits),
                        "loss_arm_marked_holders":[],"additional_physical_loss_arm_writes":through},
                        "one_fewer_shared_preparatory_write":no_ninth,
                        "wrong_parent_control_rejected":True,"two_slots_rejected_as_last":True,
                        "reversed_naming_fork":renumbered}
    assert summary["laws"]["parity"]==summary["laws"]["nae"]
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
