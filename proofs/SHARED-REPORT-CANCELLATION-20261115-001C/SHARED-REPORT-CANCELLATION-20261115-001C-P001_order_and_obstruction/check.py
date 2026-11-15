"""Replay chronological proofs and challenge their claimed representation bounds."""
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
EPIC = "SHARED-REPORT-CANCELLATION-20261115-001"


def module(path):
    return SimpleNamespace(**runpy.run_path(str(path)))


def source(letter, slug):
    ticket = EPIC + letter
    return HERE.parents[2] / "proofs" / ticket / (ticket+"-P001_"+slug) / "solver.py"


O = module(HERE / "solver.py")
A = module(source("A", "strict_checks"))
B = module(source("B", "regroup_paths"))
G = module(HERE / "guarded.py")


def digest(obj):
    data = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return sha256(data).hexdigest()


class Endpoints:
    """Independent small control: a path stores just its oriented ends and its required parity."""
    def __init__(self, charges):
        self.charges = charges

    def edge(self, e):
        return e, (e+1) % len(self.charges), self.charges[e]

    def join(self, left, right):
        assert left[1] == right[0] and left[0] != right[1]
        return left[0], right[1], left[2] ^ right[2]

    def close(self, path, incoming):
        assert path[:2] == incoming[:2][::-1] and (path[2] ^ incoming[2]) == 1
        return True


class GuardedBuilder:
    def __init__(self, instance):
        self.proof = G.GuardedProof(instance)
        self.reports = []
        self.compositions = []
        self.local_nodes = 0

    def edge(self, e, reverse=False):
        before = len(self.proof.dag.proof)
        t = self.proof.edge(e)
        self.local_nodes += len(self.proof.dag.proof)-before
        record = t.reversed() if reverse else t
        self.reports.append({"edge": e, "from": record.start, "to": record.end,
                             "charge": record.charge, "rows": list(record.rows)})
        return record

    def join(self, left, right):
        before = len(self.proof.dag.proof)
        record = self.proof.join(left, right)
        self.compositions.append({"through": left.end, "from": record.start, "to": record.end,
                                  "charge": record.charge, "rows": list(record.rows),
                                  "nodes": len(self.proof.dag.proof)-before})
        return record

    def close(self, path, edge):
        loop = self.join(path, edge)
        empty = self.proof.close(loop)
        self.proof.verify()
        assert self.proof.dag.proof[empty]["clause"] == []
        return empty


def proof_blocks(instance, rows):
    """Read source-block chronology from kernel axioms, without consulting the planner."""
    by_clause = {}
    for e, block in enumerate(instance["blocks"]):
        for forbid in block["rows"]:
            for slot in range(forbid["start"], forbid["start"]+6):
                by_clause[slot] = e
    block_order, used = [], set()
    for row in rows:
        if row["rule"] != "axiom":
            continue
        slot = row["axiom"]
        used.add(slot)
        e = by_clause[slot]
        if not block_order or block_order[-1] != e:
            block_order.append(e)
    return block_order, used


def guarded_cycle(charges, arrivals):
    instance = A.encode_cycle(charges)
    builder = GuardedBuilder(instance)
    empty, schedule = O.walk_cycle(len(charges), iter(arrivals), builder)
    dag = builder.proof.dag
    block_order, used = proof_blocks(instance, dag.proof)
    assert block_order == list(arrivals) and used == set(range(len(instance["cnf"])))
    assert all(row["rule"] != "define" for row in dag.proof)
    return {"charges": list(charges), "order": list(arrivals), "cnf_sha256": digest(instance["cnf"]),
            "strict_clauses": len(instance["cnf"]), "nodes": len(dag.proof), "empty": empty,
            "source_nodes": builder.local_nodes, "schedule": schedule,
            "check_rows": builder.reports, "path_rows": builder.compositions,
            "last_step": dag.proof[empty], "proof_sha256": digest(dag.proof)}


def check_orders():
    counts = {}
    for h in range(3, 9):
        c = [0]*(h-1) + [1]
        count = 0
        for order in permutations(range(h)):
            done, plan = O.walk_cycle(h, iter(order), Endpoints(c))
            assert done
            seen = set()
            for p in plan["events"]:
                seen.add(p["arrival"])
                runs = sum((i-1) % h not in seen for i in seen)
                assert p["components"] == runs
            assert plan["peak_components"] <= h//2
            count += 1
        counts[str(h)] = count
    for bad in ([0, 1], [0, 0, 2], [0, 1, 3], [0, 1, 2, 0]):
        try:
            O.walk_cycle(3, bad, Endpoints((0, 0, 1)))
        except ValueError:
            continue
        raise AssertionError("invalid arrival order accepted")
    return counts


def check_graphs():
    possible = list(combinations(range(4), 2))
    sat, unsat = 0, 0
    for signs in product((-1, 0, 1), repeat=len(possible)):
        checks = [(*(p if i%2 else p[::-1]), c) for i, (p, c) in enumerate(zip(possible, signs)) if c >= 0]
        feasible = [values for values in product((0, 1), repeat=4)
                    if all(values[u] ^ values[v] == c for u, v, c in checks)]
        result = O.pair_graph(4, checks)
        if feasible:
            assert tuple(result["values"]) in feasible
            sat += 1
        else:
            cycle = result["cycle"]
            vertices = [(checks[e][1], checks[e][0]) if rev else tuple(checks[e][:2]) for e, rev in cycle]
            assert len(set(u for u,v in vertices)) == len(cycle)
            assert all(v == vertices[(i+1)%len(vertices)][0] for i,(u,v) in enumerate(vertices))
            assert sum(checks[e][2] for e,rev in cycle) % 2 == 1
            unsat += 1
    return {"satisfiable": sat, "inconsistent": unsat}


def check_counts():
    # A second signed-count calculation enumerates one triple at a time and convolves the two parities.
    counts = []
    for k in range(17):
        bad = [0, 0]
        for a, b in product((0, 1), repeat=2):
            local = [0, 0]
            for x, y, z in product((0, 1), repeat=3):
                local[z*((x*y)^(a*b))] += 1
            even, odd = 1, 0
            for _ in range(k):
                even, odd = even*local[0]+odd*local[1], even*local[1]+odd*local[0]
            bad[0] += odd
            bad[1] += even
        assert bad == [O.forbidden_count(k, c) for c in (0, 1)]
        counts.append(bad)
    return counts


def sample_graph():
    checks = [(0,2,0),(1,3,0),(3,2,1),(4,3,0),(1,2,0),(0,4,1),(1,4,0)]
    encoded = A.encode_checks(5, checks)
    cycle = O.pair_graph(5, checks)["cycle"]
    path = B.PathBuilder(encoded, cycle_edges=cycle)
    dag, _ = O.graph_proof(cycle, path)
    B.verify_resolution(dag)
    gb = GuardedBuilder(encoded)
    empty = O.graph_proof(cycle, gb)
    block_order, used = proof_blocks(encoded, gb.proof.dag.proof)
    assert block_order == [e for e, rev in cycle] and 0 < len(used) < len(encoded["cnf"])
    assert digest(encoded["cnf"]) == digest(dag.cnf)
    good = [(u, v, (u%2)^(v%2)) for u,v,c in checks]
    good_instance = A.encode_checks(5, good)
    model = O.signed_model(good_instance, O.pair_graph(5, good)["values"])
    return {"input_checks": checks, "cycle": cycle, "strict_clauses": len(encoded["cnf"]),
            "used_clauses": len(used), "ordinary_nodes": len(dag.steps),
            "guarded_nodes": len(gb.proof.dag.proof), "empty_guarded": empty,
            "strict_model_bits_for_consistent_signs": len(model)-1}


def grouping_depth():
    charges = (0,)*8 + (1,)
    result = {}
    for grouping in ("left", "balanced"):
        dag, stats = B.path_refutation(charges, grouping)
        depths = []
        for row in dag.steps:
            if row[0] == "axiom":
                depths.append(0)
            else:
                _, left, right, pivot = row
                depths.append(1 + max(depths[left], depths[right]))
        assert stats["all_nodes_live"] and depths[-1] >= (len(dag.cnf)-1).bit_length()
        result[grouping] = {"nodes": len(dag.steps), "depth": depths[-1], "cnf_sha256": digest(dag.cnf)}
    assert result["left"]["nodes"] == result["balanced"]["nodes"]
    assert result["left"]["cnf_sha256"] == result["balanced"]["cnf_sha256"]
    assert result["left"]["depth"] > result["balanced"]["depth"]
    return result


def header_controls():
    for h in range(3, 8):
        for k in range(h+1):
            charges = [1]*k + [0]*(h-k)
            instance = A.encode_cycle(charges)
            rows = len(instance["cnf"]) // 6
            counted_h = (instance["n"]-2-5*rows) // 3
            assert counted_h == h and (rows-72*counted_h) == 112*k
    wires = [(0,1), (1,2), (2,0), (3,4), (4,5), (5,3), (2,3)]
    headers, feasible = [], []
    for signs in [(1,1,0,0,0,0,0), (1,0,0,0,1,0,0)]:
        checks = [(*wire, c) for wire, c in zip(wires, signs)]
        instance = A.encode_checks(6, checks)
        headers.append([instance["n"], len(instance["cnf"])])
        result = O.pair_graph(6, checks)
        feasible.append("values" in result)
        if "values" in result:
            O.signed_model(instance, result["values"])
    assert headers[0] == headers[1] and feasible == [True, False]
    return {"two_connected_networks_with_identical_header": headers[0], "satisfiable": feasible}


def main():
    fixed = (0,0,1)
    triangle = guarded_cycle(fixed, (0,1,2))
    disordered = guarded_cycle(fixed, (1,0,2))
    assert triangle["cnf_sha256"] == disordered["cnf_sha256"]
    A_trace = json.loads(source("A", "strict_checks").with_name("trace.json").read_text())
    assert A_trace["cnf_sha256"] == triangle["cnf_sha256"]
    c = (0,0,0,0,0,1)
    orders = [tuple(range(6)), (0,2,4,1,3,5)]
    six, ordinary = [], []
    for order in orders:
        six.append(guarded_cycle(c, order))
        encoded = A.encode_cycle(c)
        (dag, _), plan = O.walk_cycle(6, iter(order), B.PathBuilder(encoded))
        B.verify_resolution(dag)
        assert digest(dag.cnf) == six[-1]["cnf_sha256"]
        axioms = ({"rule": "axiom", "axiom": step[1]} for step in dag.steps if step[0] == "axiom")
        actual_order, used = proof_blocks(encoded, axioms)
        assert actual_order == list(order) and len(used) == len(encoded["cnf"])
        ordinary.append({"nodes": len(dag.steps), "schedule": plan})
    assert six[0]["cnf_sha256"] == six[1]["cnf_sha256"]
    event = O.prefix_costs(c, orders[1])[2]
    assert event == {"edge":4, "boundary":[0,1,2,3,4,5], "charge":0, "forbidden_rows":454272}
    fibers = O.pair_fibers()
    assert [(q["assignments"], q["quadratic_rank"]) for q in fibers] == [(184,37),(72,36)]
    counts = check_counts()
    triple_control = O.three_report_control()
    assert triple_control["solutions"] == 0
    assert triple_control["models_after_single_deletion"] == [8]*4
    assert triple_control["pair_sum_supports"] == [4]*6
    sample = {"source_named_first_inlining_failure": A_trace["first_over_degree_after_removing_all_names"],
              "triangle_consecutive": triangle, "triangle_second_arrival": disordered, "six": six,
              "ordinary_six": ordinary, "separate_vs_flat_after_three_even_checks":
              {"separate_components": 3, "separate_full_rows": 216, "combined_full_rows": event["forbidden_rows"]},
              "graph": sample_graph(), "grouping_depth": grouping_depth(), "three_report_control": triple_control}
    independent = module(HERE / "guarded_check.py").run_checks()
    assert independent["status"] == "passed" and independent["triangle"]["mutated_quadratic_pivot_rejected"]
    sample["reverse_guarded_triangle"] = independent["triangle"]
    snapshot = HERE / "comparison.json"
    if sys.argv[1:] == ["--emit-comparison"]:
        snapshot.write_text(json.dumps(sample, indent=2)+"\n")
    else:
        if sys.argv[1:]:
            raise ValueError("unknown arguments")
        assert json.loads(json.dumps(sample)) == json.loads(snapshot.read_text())
    summary = {"status":"passed", "triangle_nodes": triangle["nodes"], "proper_sum_first_cubic_row":
               A_trace["first_over_degree_after_removing_all_names"]["index"], "two_boundary_fibers": fibers,
               "matching_six_rows": counts[6][0], "matching_eight_rows": counts[8][0],
               "arrival_permutations": check_orders(), "signed_graphs": check_graphs(),
               "six_consecutive_guarded_nodes": six[0]["nodes"], "six_interleaved_guarded_nodes": six[1]["nodes"],
               "six_ordinary_nodes": [r["nodes"] for r in ordinary], "more_general_pair_graph": sample["graph"],
               "grouping_depth": sample["grouping_depth"],
               "guarded_independent_check": independent, "encoding_header_control": header_controls(),
               "next_three_report_control": triple_control}
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
