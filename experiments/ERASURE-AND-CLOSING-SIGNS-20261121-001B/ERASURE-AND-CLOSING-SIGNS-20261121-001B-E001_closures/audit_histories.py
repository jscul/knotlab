"""Recount outcomes from persisted physical rows, independent of stored event flags."""

from collections import Counter, defaultdict
from functools import lru_cache, reduce
from itertools import product
import gzip
import json

from internal_receipts import OUTPUT, affine_count, named_masks, pauli_solution, verify_paulis, write_json


def inspect(rows):
    incidence = defaultdict(list)
    for h,row in enumerate(rows):
        assert len(row) == len(set(row))
        for name in row:
            incidence[name].append(h)
    parent = list(range(len(rows)))
    def root(h):
        while h != parent[h]:
            parent[h] = parent[parent[h]]
            h = parent[h]
        return h
    for owners in incidence.values():
        assert 1 <= len(owners) <= 2
        if len(owners) == 2:
            a,b = owners
            parent[root(a)] = root(b)
    connected = defaultdict(list)
    for holder in range(len(rows)):
        connected[root(holder)].append(holder)
    comp_loose = {}
    for holders in connected.values():
        comp_loose[tuple(holders)] = frozenset(name for h in holders for name in rows[h] if len(incidence[name]) == 1)
    return incidence, comp_loose


@lru_cache(None)
def exact_operator(ends, closed_at):
    # Solving the table of commutators on loop generators is polynomial in this width.
    positive = pauli_solution(ends, {closed_at})
    if positive is not None:
        verify_paulis(ends, positive, {closed_at})
    return positive is not None


def audit(records):
    totals = defaultdict(Counter)
    global_counts = Counter()
    simultaneous_counts = Counter()
    cuts_counts = defaultdict(Counter)
    for draw in records:
        panel = draw["panel"]
        for kind, trajectory in draw["laws"].items():
            stats = totals[panel,kind]
            before = draw["source_rows"]
            state = inspect(before)
            stats["draws"] += 1
            stats["lawful"] += int(trajectory["founder"]["lawful"])
            stats[trajectory["termination"]] += 1
            seen, yes, wholly = 0, 0, False
            known_closed_terminals = {}
            for cut in trajectory["cuts"]:
                after = cut["after_rows"]
                assert before == after[:len(before)]
                incidence, components = state
                next_incidence, next_components = inspect(after)
                assert [c["holders"] for c in cut["components"]] == sorted(map(list,next_components))
                old_loose = {x for x,hs in incidence.items() if len(hs)==1}
                assert all(len(next_incidence[x]) == 2 for x in old_loose)
                old_closed = {hs for hs,loose in components.items() if not loose}
                new_closed = {hs for hs,loose in next_components.items() if not loose} - old_closed
                assert old_closed <= set(next_components)
                assert bool(cut["whole_closed"]) == all(not x for x in next_components.values())
                component_of = {h:hs for hs in components for h in hs}
                used = []
                observed = {}
                positive = 0
                for h,row in enumerate(after[len(before):],start=len(before)):
                    actual = cut["births"][h-len(before)]
                    old = frozenset(row) & incidence.keys()
                    born = frozenset(row) - incidence.keys()
                    assert old and list(row) == actual["support"] and set(actual["inputs"]) == old
                    assert len(born) == actual["fresh"] and set(actual["new_names"]) == born
                    parents = {incidence[x][0] for x in old}
                    assert len(parents) == len(old) and parents == set(actual["parents"])
                    ancestors = {component_of[h0] for h0 in parents}
                    assert len(ancestors)==1
                    ancestor = ancestors.pop()
                    if kind=="parity":
                        assert (not born) == (old == components[ancestor])
                    else:
                        assert born
                    if not born:
                        hs = next(part for part in new_closed if h in part)
                        assert set(hs) == set(ancestor) | {h}
                        assert reduce(int.__xor__, (sum(1 << x for x in before[q]) for q in ancestor),0) == sum(1<<x for x in old)
                        link_order = tuple(sorted(tuple(hs.index(q) for q in owners)
                                for owners in next_incidence.values() if owners[0] in hs))
                        verdict = exact_operator(link_order,hs.index(h))
                        observed[h] = verdict
                        positive += verdict
                        stats[f"arity_{len(old)}"] += 1
                    used.extend(old)
                assert len(used)==len(old_loose) and set(used)==old_loose
                assert len(new_closed)==len(observed)
                assert {r["holder"]:r["operator_positive"] for r in cut["new_closing_components"]}==observed
                known_closed_terminals.update(observed)
                if "union_signs" in cut:
                    terminals = cut["union_signs"]["ordered_terminal_holders"]
                    assert set(terminals) == set(known_closed_terminals)
                    scenario_list = cut["union_signs"]["scenarios"]
                    assert {tuple(x["signs_by_closing_holder"]) for x in scenario_list}==set(product((0,1),repeat=len(terminals)))
                    even_count = 1 << (len(next_incidence) - len(after) + sum(not v for v in next_components.values()))
                    names,masks = named_masks(after)
                    for scenario in scenario_list:
                        odds = set(scenario["odd_holders"])
                        expected_op = all(known_closed_terminals[h] for h in odds)
                        words = affine_count(masks,[h in odds for h in range(len(after))],len(names))
                        assert scenario["scalar"]["words"] == words == (0 if odds else even_count)
                        assert scenario["operator_admits"] == expected_op
                        if len(observed)==2:
                            simultaneous_counts[len(odds),expected_op,bool(words)] += 1
                        global_counts["complete_signed_union_scenarios"] += 1
                    global_counts["paired_cuts_with_four_signed_checks"]+=int(len(observed)==2)
                else:
                    assert len(observed)<2
                number = len(observed)
                seen += number
                yes += positive
                wholly |= cut["whole_closed"]
                stats["births"]+=len(cut["births"])
                stats["cuts"]+=1
                stats["closures"]+=number
                stats["positive_closures"]+=positive
                stats["cuts_with_closure"]+=bool(number)
                stats["births_in_closing_cuts"]+=len(cut["births"]) if number else 0
                stats["continuing_births_in_closing_cuts"]+=len(cut["births"])-number if number else 0
                cuts_counts[panel,kind][str(number)] += 1
                before = after
                state = next_incidence,next_components
            stats["draws_with_closure"] += bool(seen)
            stats["draws_with_positive_closure"] += bool(yes)
            stats["draws_wholly_closed"] += wholly
    return {"by_panel_law":{f"{p} {law}":v for (p,law),v in totals.items()},
            "new_component_counts_per_funded_cut":{f"{p} {law}":v for (p,law),v in cuts_counts.items()},
            "literal_closed_pattern_solver_cache":dict(exact_operator.cache_info()._asdict()),
            "four_sign_control":dict(global_counts),
            "all_simultaneous_scenarios_by_number_odd_operator_admits_scalar_admits":
                {f"{n} {o} {s}":k for (n,o,s),k in simultaneous_counts.items()}}


if __name__ == "__main__":
    with gzip.open(OUTPUT/"panels_histories.json.gz","rt") as f:
        data = json.load(f)
    result = audit(data)
    write_json("history_audit.json",result)
    print("independently recounted",len(data),"paired sources",result["four_sign_control"],
          result["literal_closed_pattern_solver_cache"])
