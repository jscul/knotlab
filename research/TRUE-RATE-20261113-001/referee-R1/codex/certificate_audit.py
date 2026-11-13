"""Fresh TRUE-RATE referee calculation, from the relation described in the notes.

No study implementation is read or imported.  The permitted BOND-DEPTH family
enumerator is represented by mapping_audit's family_inventory.json.  G is
rederived by existential enumeration and descending greatest-fixed-point
iteration.  All bond projections below are direct SAT queries on an explicitly
unfolded finite subtree with exact G relations on its outgoing calls.

Usage: /home/jscul/p-vs-np-contact-first/.venv/bin/python -B <this file>
"""
from __future__ import annotations

import hashlib
import itertools
import json
import resource
import time
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TEN = (262, 269, 302, 363, 579, 642, 662, 908, 975, 1144)
resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))


def pack(assignment: int, args) -> int:
    return sum(((assignment >> a) & 1) << j for j, a in enumerate(args))


def cycles(args):
    """Return cycle positions of the partial function j -> args[j] < 3.

    A tail leading into a cycle is not itself a carried original top port.
    """
    answer = set()
    for start in range(3):
        seq = []
        cur = start
        while cur < 3 and cur not in seq:
            seq.append(cur)
            cur = args[cur]
        if cur < 3:
            answer.update(seq[seq.index(cur):])
    return sorted(answer)


class Rule:
    def __init__(self, defs):
        assert len(defs) == 1
        ports, self.locals, calls = defs[0]
        assert ports == 3
        self.calls = [(name, tuple(args)) for name, args in calls]
        assert all(name in ("K", "SELF") for name, _ in self.calls)
        self.children = [a for n, a in self.calls if n == "SELF"]
        self.ray = self.children[0]
        self.nenv = 3 + self.locals
        self.knot_ok = [x for x in range(1 << self.nenv)
                        if all(pack(x, a) not in (0, 7)
                               for n, a in self.calls if n == "K")]

    def environment(self, g, outside=255, omit_ray=False):
        children = self.children[1:] if omit_ray else self.children
        return [x for x in self.knot_ok if (outside >> (x & 7)) & 1
                and all((g >> pack(x, a)) & 1 for a in children)]

    def bottomless(self):
        trace = [255]
        while True:
            allowed = self.environment(trace[-1])
            new = sum(1 << p for p in {x & 7 for x in allowed})
            assert new & ~trace[-1] == 0
            if new == trace[-1]:
                return new, trace
            trace.append(new)

    def outside_step(self, r, g):
        return sum(1 << p for p in
                   {pack(x, self.ray) for x in self.environment(g, r, True)})


def relation_clauses(variables, mask):
    return [[-v if (state >> j) & 1 else v
             for j, v in enumerate(variables)]
            for state in range(8) if not (mask >> state) & 1]


def one_copy_clauses(rule, g, omit_ray=False):
    clauses = []
    first = True
    for name, args in rule.calls:
        variables = [a + 1 for a in args]
        if name == "K":
            clauses += [variables, [-v for v in variables]]
        else:
            if not (first and omit_ray):
                clauses += relation_clauses(variables, g)
            first = False
    return clauses


def projection(solver, variables):
    return [a for a in range(1 << len(variables))
            if solver.solve(assumptions=[v if (a >> j) & 1 else -v
                                         for j, v in enumerate(variables)])]


def is_bond(solver, variables):
    states = projection(solver, variables)
    if len(states) == 1 << len(variables):
        return None
    pairs = [projection(solver, variables[:j] + variables[j + 1:])
             for j in range(len(variables))]
    if all(len(p) == 1 << (len(variables) - 1) for p in pairs):
        return {"variables": variables, "states": states,
                "states_bits_in_member_order":
                    [[(a >> j) & 1 for j in range(3)] for a in states],
                "pairs_after_forgetting_each_member": pairs,
                "K1": True, "K2": True, "K3": bool(states)}
    return None


def subtree(rule, g, depth):
    clauses = []
    introduced = {}
    envs = {}
    next_var = 4

    def visit(ports, path):
        nonlocal next_var
        own = list(range(next_var, next_var + rule.locals))
        next_var += rule.locals
        for j, v in enumerate(own, 3):
            introduced[v] = {"path": list(path), "slot": j}
        env = list(ports) + own
        envs[path] = env
        child_index = 0
        for name, args in rule.calls:
            variables = [env[a] for a in args]
            if name == "K":
                clauses.extend((variables, [-v for v in variables]))
            else:
                if len(path) < depth:
                    visit(variables, path + (child_index,))
                else:
                    clauses.extend(relation_clauses(variables, g))
                child_index += 1

    visit((1, 2, 3), ())
    return clauses, introduced, envs, next_var - 1


def audit_family(idx, defs):
    started = time.monotonic()
    rule = Rule(defs)
    g, trace = rule.bottomless()
    positions = cycles(rule.ray)
    rseq = [255]
    for _ in range(12):
        rseq.append(rule.outside_step(rseq[-1], g))
    record = {"idx": idx, "defs": defs, "ray_arguments": rule.ray,
              "carried_positions": positions,
              "G_mask": g, "G_states": [s for s in range(8) if g >> s & 1],
              "G_descending_masks": trace, "R_masks_depth_0_to_12": rseq,
              "R1_all_eight": rseq[1] == 255}
    with Solver(name="cadical153", bootstrap_with=one_copy_clauses(rule, g)) as s:
        record["G_checked_with_SAT"] = projection(s, [1, 2, 3]) == record["G_states"]
    with Solver(name="cadical153", bootstrap_with=one_copy_clauses(rule, g, True)) as s:
        record["R1_checked_with_SAT"] = projection(s, [a + 1 for a in rule.ray]) == list(range(8))
    assert record["G_checked_with_SAT"]
    assert record["R1_checked_with_SAT"] == record["R1_all_eight"]
    if idx not in TEN:
        return record

    clauses, introduced, envs, nvars = subtree(rule, g, 3)
    side = [v for v, where in introduced.items()
            if 1 <= len(where["path"]) <= 2
            and any(j != 0 for j in where["path"])]
    witnesses = []
    attempted = 0
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        assert solver.solve()
        for p in positions:
            found = None
            for v, w in itertools.product(envs[()][3:], side):
                attempted += 1
                answer = is_bond(solver, [p + 1, v, w])
                if answer:
                    found = {**answer, "port_position": p,
                             "own_member": introduced[v],
                             "side_member": introduced[w]}
                    break
            if found:
                witnesses.append(found)
    record.update({"truncation_max_copy_depth": 3, "copies": len(envs),
                   "SAT_variables": nvars, "SAT_clauses": len(clauses),
                   "side_candidate_count": len(side), "triples_attempted": attempted,
                   "bonds": witnesses})
    assert witnesses, (idx, positions)
    # A shallower/deeper truncation has identical projection when the same
    # member identities exist, since every cut call has the exact relation G.
    rechecks = []
    for depth in (2, 4):
        cl, intro, env, nv = subtree(rule, g, depth)
        reverse = {(tuple(where["path"]), where["slot"]): var
                   for var, where in intro.items()}
        with Solver(name="cadical153", bootstrap_with=cl) as solver:
            for witness in witnesses:
                members = [witness["port_position"] + 1]
                for name in ("own_member", "side_member"):
                    where = witness[name]
                    members.append(reverse[tuple(where["path"]), where["slot"]])
                states = projection(solver, members)
                assert states == witness["states"]
                assert is_bond(solver, members)
                rechecks.append({"depth": depth, "port_position": witness["port_position"],
                                 "states": states, "variables": nv, "copies": len(env)})
    record["other_truncation_checks"] = rechecks
    record["seconds"] = time.monotonic() - started
    return record


def controls():
    assert cycles((1, 0, 3)) == [0, 1]
    assert cycles((1, 3, 4)) == []
    assert cycles((1, 1, 3)) == [1]  # tail 0 must not be included
    assert cycles((1, 2, 0)) == [0, 1, 2]
    tests = {}
    for name, clauses in {"NAE_positive": [[1, 2, 3], [-1, -2, -3]],
                          "free_negative": [],
                          "pair_tie_negative": [[-1, 2], [1, -2]],
                          "inconsistent_negative": [[1], [-1]]}.items():
        with Solver(name="cadical153", bootstrap_with=clauses) as s:
            tests[name] = is_bond(s, [1, 2, 3]) is not None
    assert tests == {"NAE_positive": True, "free_negative": False,
                     "pair_tie_negative": False, "inconsistent_negative": False}
    return {"SAT_bond_controls": tests, "cycle_controls_passed": True}


def main():
    t0 = time.monotonic()
    inventory = HERE / "family_inventory.json"
    families = {r["idx"]: r["defs"] for r in json.loads(inventory.read_text())}
    rates_file = ROOT / "artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl"
    growing = [json.loads(line) for line in rates_file.open()]
    growing = [r["idx"] for r in growing if r.get("complete") and (r.get("lambda_float") or 0) > 0]
    carried = [idx for idx in growing if cycles(Rule(families[idx]).ray)]
    result = {"method": __doc__, "controls": controls(), "rows": []}
    for idx in carried:
        row = audit_family(idx, families[idx])
        result["rows"].append(row)
        print(json.dumps({"idx": idx, "G": row["G_mask"], "R1": row["R_masks_depth_0_to_12"][1],
                          "carried_positions": row["carried_positions"],
                          "bond_count": len(row.get("bonds", []))}), flush=True)
    result.update({"carried_growing_count": len(carried), "certified_ten": list(TEN),
                   "all_twenty_R1_full": all(r["R1_all_eight"] for r in result["rows"]),
                   "seconds": time.monotonic() - t0,
                   "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                   "inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in (inventory, rates_file)}})
    (HERE / "certificate_audit.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
