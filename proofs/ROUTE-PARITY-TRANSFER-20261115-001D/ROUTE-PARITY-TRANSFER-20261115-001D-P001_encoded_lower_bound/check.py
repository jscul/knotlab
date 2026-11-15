"""Expand a raw solver trace into parity-resolution nodes and independently check its projection."""
from collections import defaultdict, deque
from itertools import chain
import json
from math import comb
from pathlib import Path
import runpy
import sys


def modules(root):
    epic = "ROUTE-PARITY-TRANSFER-20261115-001"
    def read(suffix, slug):
        leaf = epic + suffix
        return runpy.run_path(str(root / "proofs" / leaf / (leaf + "-P001_" + slug) / "check.py"))
    return read("A", "literal_projection"), read("B", "dag_transport")


def add_reasons(cnf, additions, calculus):
    """For each reverse-unit-propagation step, resolve its implication trail backwards."""
    equations = calculus["signed_clause"]
    sources = [frozenset(row) for row in cnf]
    appearances = defaultdict(list)
    units = []
    node_of = {}
    proof = []
    for index, row in enumerate(sources):
        for lit in row:
            appearances[lit].append(index)
        if len(row) == 1:
            units.append((next(iter(row)), index))

    def reference(index):
        if index not in node_of:
            assert index < len(cnf)
            node_of[index] = len(proof)
            proof.append({"rule": "axiom", "axiom": index, "clause": equations(sources[index])})
        return node_of[index]

    for added in additions:
        goal = frozenset(added)
        assert all(-lit not in goal for lit in goal)
        reasons = {}
        trail = []
        # All assumptions have priority, including when they contradict an input unit.
        for lit in goal:
            reasons[-lit] = None
        queue = deque([(-lit, None) for lit in goal] + units)
        conflict = None
        while queue and conflict is None:
            lit, origin = queue.popleft()
            if origin is not None:
                if -lit in reasons:
                    conflict = origin
                    break
                if lit in reasons:
                    continue
                reasons[lit] = origin
                trail.append(lit)
            for index in appearances[-lit]:
                row = sources[index]
                if any(term in reasons for term in row):
                    continue
                open_lits = [term for term in row if -term not in reasons]
                if not open_lits:
                    conflict = index
                    break
                if len(open_lits) == 1:
                    queue.append((open_lits[0], index))
        if conflict is None:
            raise ValueError("the learned clause failed reverse unit propagation")
        current = sources[conflict]
        parent = reference(conflict)
        for lit in reversed(trail):
            if -lit not in current:
                continue
            reason = reasons[lit]
            other = reference(reason)
            current = (current - {-lit}) | (sources[reason] - {lit})
            proof.append({"rule": "resolve", "parents": [parent, other],
                          "pivot": list(calculus["atom"](-lit)), "clause": equations(current)})
            parent = len(proof) - 1
        assert current <= goal
        if current != goal:
            proof.append({"rule": "weaken", "parents": [parent], "clause": equations(goal)})
            parent = len(proof) - 1
        index = len(sources)
        sources.append(goal)
        node_of[index] = parent
        for lit in goal:
            appearances[lit].append(index)
        if len(goal) == 1:
            units.append((next(iter(goal)), index))
    assert sources[-1] == frozenset()
    return proof, node_of[len(sources) - 1]


def live_parity_proof(proof, end, images, raw, a, n):
    """Keep ancestors and use a two-variable cut where both parity values survive projection."""
    needed = set()
    pending = [end]
    while pending:
        i = pending.pop()
        if i not in needed:
            needed.add(i)
            pending.extend(proof[i].get("parents", []))
    mapping = {}
    live = []
    inserted = False
    for i in sorted(needed):
        node = dict(proof[i])
        if "parents" in node:
            node["parents"] = [mapping[p] for p in node["parents"]]
        mapping[i] = len(live)
        live.append(node)
        if not inserted:
            literals = [mask.bit_length() * (1 if rhs else -1) for mask, rhs in node["clause"]]
            clause = a["clause_image"](literals, images, n + 1)
            if not clause:
                continue
            missing = next((x for x in range(1, n+1) if all(abs(lit) != x for lit in clause)), None)
            if missing is None:
                continue
            second = 2 if missing == 1 else 1
            pivot = [(1 << (raw.signals[missing] - 1)) | (1 << (raw.signals[second] - 1)), 0]
            parent = mapping[i]
            opposite = [pivot[0], 1]
            for atom in (pivot, opposite):
                live.append({"rule": "weaken", "parents": [parent], "clause": node["clause"] + [atom]})
            live.append({"rule": "resolve", "parents": [parent+1, parent+2], "pivot": pivot,
                         "clause": node["clause"]})
            mapping[i] = parent + 3
            inserted = True
    assert inserted
    return live


def replay(n, roster, selected, a, calculus, solver_type):
    source = [roster[i] for i in selected]
    raw, pins, images = a["build_projection"](n, roster, selected)
    cnf = raw.cnf + [[pin] for pin in pins]
    target_n = max(images)
    stages = len(raw.stages)
    assert stages == 4*len(roster) + 12*n + 8
    assert len(raw.cnf) == 32*(stages+1) and len(pins) == 24*(stages+1)
    with solver_type(name="g3", bootstrap_with=cnf, with_proof=True) as solver:
        assert not solver.solve()
        additions = [list(map(int, line.split()[:-1])) for line in solver.get_proof()
                     if not line.startswith("d ")]
    if not additions or additions[-1]:
        additions.append([])
    proof, end = add_reasons(cnf, additions, calculus)
    target = live_parity_proof(proof, end, images, raw, a, n)
    source_proof, stats = calculus["translated"](n, source, target_n, cnf, images, target)
    after = calculus["verify"](n, source, source_proof)
    # Different verifier for every source inference, by evaluating every source assignment.
    meanings = []
    for node in source_proof:
        truth = {x for x in range(1 << n) if any((x & mask).bit_count() % 2 == rhs
                                                   for mask, rhs in node["clause"])}
        if node["rule"] == "axiom":
            row = source[node["axiom"]]
            assert truth == {x for x in range(1 << n) if any(bool(x & (1 << (abs(i)-1))) == (i>0) for i in row)}
        else:
            intersection = set.intersection(*(meanings[p] for p in node["parents"]))
            assert intersection <= truth
        meanings.append(truth)
    assert not meanings[-1]
    assert after["shared_parents"] > 0 and any(
        x["rule"] == "resolve" and x["pivot"][0].bit_count() == 2 for x in source_proof)
    assert after["lines"] <= len(target)
    return {"stages": stages, "strict_clauses": len(raw.cnf), "guard_units": len(pins),
            "learned_clauses_including_empty": len(additions), "raw_proof": stats["target"],
            "projected_proof": after, "source_assignments_checked_per_line": 1 << n}


def main(root):
    from pysat.solvers import Solver
    a, calculus = modules(root)
    all3 = a["compiler"]().clauses_on(3)
    all4 = a["compiler"]().clauses_on(4)
    sample = list(chain(all3, (all3[2],), (all4[13],)))
    selected = [i for i, row in enumerate(all4) if row in sample]
    sparse = replay(3, all3, range(len(all3)), a, calculus, Solver)
    fixed = replay(4, all4, selected, a, calculus, Solver)
    # Same occurrence menu with an exact duplicate. Its missing eighth sign admits a model.
    raw, pins, _ = a["build_projection"](4, sample, [i for i in range(len(sample)) if i != 0])
    with Solver(name="g3", bootstrap_with=raw.cnf) as solver:
        assert solver.solve(assumptions=pins)
    assert len(all4) == 8*comb(4, 3)
    from random import Random
    rng = Random(54)
    population = a["compiler"]().clauses_on(5)
    sample40 = rng.choices(population, k=40)
    density_layout = a["ProjectionTemplate"](5, sample40).raw
    assert len(density_layout.stages) == 44*5 + 8
    return {"status":"passed", "sparse_three":sparse, "fixed_four":fixed,
            "duplicate_and_disabled_control_satisfiable":True, "density_eight_five_stages":228}


if __name__ == "__main__":
    import os
    root = Path(__file__).resolve().parents[3]
    python = root / ".venv/bin/python"
    if python.exists() and Path(sys.prefix).resolve() != python.parent.parent.resolve():
        os.execv(str(python), [str(python), "-B", str(Path(__file__).resolve())])
    print(json.dumps(main(root), sort_keys=True))
