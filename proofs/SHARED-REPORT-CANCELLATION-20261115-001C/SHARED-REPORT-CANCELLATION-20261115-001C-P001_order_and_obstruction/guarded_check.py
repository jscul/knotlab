"""Replay guarded paths from genuine clauses and inspect their original-variable meaning."""

from dataclasses import asdict
from itertools import product
import json

import guarded as G


def check_meanings(builder, records):
    tested = 0
    for rec in records:
        triples = builder.instance["triples"]
        keys = tuple(dict.fromkeys((builder.instance["a"], builder.instance["b"],
                                    *triples[rec.start], *triples[rec.end])))
        for values in product((0, 1), repeat=len(keys)):
            assignment = dict(zip(keys, values))
            shared = assignment[keys[0]] & assignment[keys[1]]

            def report(index):
                x, y, z = (assignment[v] for v in triples[index])
                return z & ((x & y) ^ shared)

            def value(polynomial):
                return sum(all(assignment[v] for v in monomial)
                           for monomial in polynomial) % 2

            allowed = all(any(value(f) == 0 for f in builder.dag.clauses[root])
                          for root in rec.rows)
            assert allowed == (report(rec.start) ^ report(rec.end) == rec.charge)
            tested += 1
    return tested


def _expect_rejected(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("invalid proof operation was accepted")


def triangle():
    instance = G.SOURCE["encode_cycle"]((0, 0, 1))
    p = G.GuardedProof(instance)
    edges = [p.edge(i) for i in range(3)]
    prefix = len(p.dag.proof)
    assert p.edge(0).rows == edges[0].rows
    assert edges[2].reversed().reversed() == edges[2]
    assert prefix == len(p.dag.proof)
    _expect_rejected(lambda: p.join(edges[0], edges[2]))
    path = p.join(edges[2].reversed(), edges[1].reversed())
    loop = p.join(path, edges[0].reversed())
    empty = p.close(loop)
    p.verify()
    assert (prefix, len(p.dag.proof), empty) == (13165, 13243, 13242)
    checked = check_meanings(p, [*edges, path, loop])
    # For endpoints 00, the second addition selects the true inner selector.
    # The middle pair's quadratic occurs in both selected equations and cancels.
    cancellation = prefix + 2
    step = p.dag.proof[cancellation]
    chosen = [G.KERNEL.polynomial(raw) for raw in step["chosen"]]
    inner_vertex = edges[2].start
    inner_pair = tuple(instance["triples"][inner_vertex][:2])
    assert step["rule"] == "combine"
    assert all(inner_pair in poly for poly in chosen)
    assert all(inner_pair not in poly for poly in p.dag.clauses[cancellation])
    corrupted = list(p.dag.proof)
    fake = G.KERNEL.encode(G.mul(G.var(instance["a"]), G.var(instance["a"])))
    corrupted[cancellation] = {**step, "chosen": [fake, step["chosen"][1]]}
    _expect_rejected(lambda: G.KERNEL.verify(instance["n"], instance["cnf"], corrupted))
    assert not any(row["rule"] == "define" for row in p.dag.proof)
    return {
        "strict_clauses": len(instance["cnf"]),
        "input_variables_including_private_padding": instance["n"],
        "source_rows_by_block": p.source_examples,
        "edge_roots_00_01_10_11": [list(ed.rows) for ed in edges],
        "prefix_nodes": prefix,
        "first_join": asdict(path),
        "inner_quadratic_addition": {"row": cancellation, "parents": step["parents"],
                                     "chosen": step["chosen"]},
        "closed_path": asdict(loop),
        "empty": empty,
        "nodes": len(p.dag.proof),
        "original_assignment_comparisons": checked,
        "mutated_quadratic_pivot_rejected": True,
    }


def graph_subset():
    # A directed mix of six cycle edges and an unused seventh-vertex check.
    checks = [(0, 6, 1), (1, 0, 0), (1, 2, 1), (3, 2, 0),
              (3, 4, 1), (5, 4, 0), (5, 0, 1)]
    arrivals = [(1, False), (3, True), (5, False),
                (2, True), (4, False), (6, True)]
    instance = G.SOURCE["encode_checks"](7, checks)
    p = G.GuardedProof(instance)
    opened = {}
    trace = []
    compositions = 0
    closed = None

    def remove(endpoint):
        path = opened.get(endpoint)
        if path is not None:
            del opened[path.start]
            del opened[path.end]
        return path

    for index, reverse in arrivals:
        path = p.edge(index)
        if reverse:
            path = path.reversed()
        left = remove(path.start)
        if left is not None:
            if left.end != path.start:
                left = left.reversed()
            path = p.join(left, path)
            compositions += 1
        if path.start != path.end:
            right = remove(path.end)
            if right is not None:
                if right.start != path.end:
                    right = right.reversed()
                path = p.join(path, right)
                compositions += 1
        if path.start == path.end:
            closed = path
        else:
            opened[path.start] = opened[path.end] = path
        trace.append(len(opened) // 2)
    assert trace == [1, 2, 3, 2, 1, 0] and compositions == 5
    assert closed is not None and closed.charge == 1
    empty = p.close(closed)
    p.verify()
    unused = {j for row in instance["blocks"][0]["rows"]
              for j in range(row["start"], row["start"] + 6)}
    cited = {row["axiom"] for row in p.dag.proof if row["rule"] == "axiom"}
    assert not unused & cited
    assert len(cited) == len(instance["cnf"]) - len(unused)
    return {"arrivals": arrivals, "open_components": trace,
            "joins": compositions, "original_checks_used": len(arrivals),
            "unused_original_blocks": 1, "cited_strict_clauses": len(cited),
            "empty": empty, "nodes": len(p.dag.proof)}


def run_checks():
    even = G.GuardedProof(G.SOURCE["encode_checks"](2, [(1, 0, 1)]))
    edge = even.edge(0)
    retraced = even.join(edge, edge.reversed())
    assert retraced.start == retraced.end and retraced.charge == 0
    assert check_meanings(even, [retraced]) == 32
    _expect_rejected(lambda: even.close(retraced))
    return {"status": "passed", "triangle": triangle(), "graph_subset": graph_subset(),
            "even_closed_path_rejected": True}


if __name__ == "__main__":
    print(json.dumps(run_checks(), sort_keys=True))

