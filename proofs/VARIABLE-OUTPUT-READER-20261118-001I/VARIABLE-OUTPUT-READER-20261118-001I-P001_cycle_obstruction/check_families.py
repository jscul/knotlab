"""Replay the sharp cutoff and repeated intersecting four-place cycles."""

from collections import Counter
from importlib import util
from itertools import combinations
import json
from pathlib import Path
from random import Random

import networkx as nx

PROOFS = Path(__file__).resolve().parents[2]
PREVIOUS = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001H"


def from_previous(module):
    path, = PREVIOUS.glob(f"*/{module}.py")
    spec = util.spec_from_file_location(module, path)
    loaded = util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


box = from_previous("check_horizon")
reader = from_previous("check_reader")
audit = box.audit


def append(rows, inputs, count=3):
    start = max(max(row) for row in rows) + 1
    new = tuple(range(start, start + count))
    rows.append((*inputs, *new))
    return new


def central_cycle(rows, input_bit, surrounding_outputs):
    t = append(rows, [input_bit])
    p = append(rows, [t[0]])
    q = append(rows, [t[1]])
    w = append(rows, [p[0], q[0]], 2)
    b = append(rows, [p[1], q[1]], surrounding_outputs)
    c = append(rows, [t[2], w[0]], surrounding_outputs)
    return p, q, b, c


def measured(rows):
    audit.replay_history(rows, tuple(range(len(rows))))
    width = 1 + max(max(row) for row in rows)
    pairs, _, shores = reader.measured_short_bonds(rows, width, 6)
    assert set(shores) <= {1, 2}
    truth = set(map(frozenset, rows))
    assert reader.anonymous_reader(width, pairs) == truth
    perm = list(range(width))
    Random(235641 + width).shuffle(perm)
    changed = {tuple(sorted((perm[a], perm[b]))): value for (a,b), value in pairs.items()}
    decoded = reader.anonymous_reader(width, changed)
    assert decoded == {frozenset(perm[i] for i in row) for row in rows}
    menu = audit.permissions(rows)
    assert audit.permissions(list(decoded)) == {tuple(sorted(perm[i] for i in tri)) for tri in menu}
    return pairs, menu, {
        "width": width, "sites": len(rows), "named_pairs": width*(width-1)//2,
        "arities": dict(sorted(Counter(map(len, rows)).items())),
        "short_bonds_by_ordinary_shore_size": shores, "legal_triples": len(menu),
        "all_stars_and_triples_recovered_after_renaming": True,
    }


def sharp():
    rows, parents, marks, spare_at_b = box.open_box((2,2,1))
    owners = {i: site for site, row in enumerate(rows) for i in row}
    a, b, c = [owners[bit] for bit in marks]
    assert len({a,b,c}) == 3
    spare_at_a = [bit for bit in rows[a] if bit not in marks and sum(bit in row for row in rows)==1]
    assert len(spare_at_a) == 2
    t_site = len(rows)
    p, _, _, _ = central_cycle(rows, spare_at_a[0], 3)
    append(rows, [spare_at_a[1], p[2]])  # Witness at t.
    pairs, menu, report = measured(rows)
    width = report["width"]
    permutation = list(range(width))
    permutation[marks[0]], permutation[spare_at_b] = spare_at_b, marks[0]
    before = tuple(sorted(marks))
    after = tuple(sorted(permutation[i] for i in before))
    assert before in menu and after not in menu
    def bond_size(a, b):
        return pairs.get(tuple(sorted((a,b))), 7)  # 7 stands for every size greater than six.
    mismatches = {cutoff: sum(min(bond_size(i,j),cutoff+1) !=
                              min(bond_size(permutation[i],permutation[j]),cutoff+1)
                              for i,j in combinations(range(width),2)) for cutoff in (5,6)}
    assert mismatches[5] == 0 and mismatches[6] > 0
    assert bond_size(spare_at_b, marks[1]) == 6 < bond_size(marks[0], marks[1])
    graph = nx.Graph()
    graph.add_nodes_from(range(len(rows)))
    held = {}
    for k,row in enumerate(rows):
        for bit in row:
            if bit in held:
                graph.add_edge(held[bit], k)
            else:
                held[bit] = k
    graph.remove_edges_from(list(nx.bridges(graph)))
    component = nx.node_connected_component(graph,a)
    assert {a,b,c,*range(t_site, len(rows))} <= component
    report.update(history=rows, legal_mark=before, forbidden_image=after,
                  swapped_bits=[marks[0],spare_at_b],
                  changed_entries_by_K_cutoff=mismatches,
                  marked_holders_and_added_sites_in_one_bridgeless_component=True,
                  coordinate_witness_for_three_original_holders=parents)
    return report


def intersecting(repeats):
    rows = [(0,1,2)]
    input_bit = 0
    gates = []
    for stage in range(repeats):
        start = len(rows)
        p,q,b,c = central_cycle(rows,input_bit,2)
        r = append(rows,[c[0],q[2]])
        y = append(rows,[b[0],r[0]])
        gates.append(tuple(sorted((p[2],c[1],y[0]))))
        input_bit = y[1]
        low = rows[start:start+6]
        meeting_count = sum(bool(set(a)&set(b)) for a,b in combinations(low,2))
        assert all(len(row)==4 for row in low) and meeting_count == 8
    _, menu, report = measured(rows)
    assert set(gates) <= menu
    report.update(blocks=repeats,marked_legal_triples=gates,history=rows)
    return report


def shrinking_control():
    rows = [(0,1,2)]
    children = [append(rows,[site]) for site in (0,1,2)]
    a,b,c = children
    joins = [append(rows,pair,2) for pair in ((a[0],b[0]),(a[1],c[0]),(b[1],c[1]))]
    active = set().union(*map(set,rows))
    mark = tuple(x[0] for x in joins)
    assert tuple(sorted(mark)) in audit.permissions(rows)
    frontier = {x for x in active if sum(x in row for row in rows)==1}
    made = append(rows,mark,2)
    audit.replay_history(rows,tuple(range(len(rows))))
    later = {x for x in set().union(*map(set,rows)) if sum(x in row for row in rows)==1}
    assert len(frontier)==9 and len(later)==8 and later==(frontier-set(mark))|set(made)
    assert sum(len(row)==3 for row in rows)==1
    return {"history":rows, "legal_inputs":mark, "boundary_before":len(frontier),"boundary_after":len(later)}


def short_control():
    rows = [(0,1,2)]
    child = append(rows,[0],2)
    append(rows,[child[0]],2)
    audit.replay_history(rows,(0,1,2))
    width = 1 + max(max(row) for row in rows)
    _,_,shores = reader.measured_short_bonds(rows,width,6)
    assert shores.get(3) == 1
    size = (audit.mask(rows[0]) ^ audit.mask(rows[1]) ^ audit.mask(rows[2])).bit_count()
    assert size == 5
    return {"history":rows,"cut_size_on_all_three_sites":size,"short_bonds_by_ordinary_shore_size":shores}


if __name__ == "__main__":
    print(json.dumps({"sharp_one_binary": sharp(),
                      "nonshrinking_intersecting_cycles": [intersecting(n) for n in (1,2,4)],
                      "nearby_ternary_control": short_control(),
                      "single_ternary_shrinking_control": shrinking_control()}, indent=2))
