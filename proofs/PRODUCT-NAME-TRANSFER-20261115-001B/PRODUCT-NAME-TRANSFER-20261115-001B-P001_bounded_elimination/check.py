"""Check actual multiset deductions, including branching on dense affine forms."""
from functools import cache
from itertools import product
import json
from pathlib import Path
import runpy

M = runpy.run_path(str(Path(__file__).with_name("solver.py")))
Q, add, mul, var, zero, one = (M[k] for k in ("BASE", "add", "mul", "var", "ZERO", "ONE"))
enc = Q["encode"]


def example(n, factors):
    # Two opposite input units give a small controlled contradiction. Every definition
    # contributes twice to the path that recovers the unit used by the final cut.
    cnf = [[-1], [1]]
    dag = Q["Dag"](cnf)
    current = dag.axiom(0)
    signals = []
    for j, (g, h) in enumerate(factors, n + 1):
        d = add(var(j), mul(g, h))
        definition = dag.emit("define", [d], variable=j, factors=[enc(g), enc(h)])
        current = dag.combine(current, definition, dag.clauses[current][0], d)
        signals.append((definition, d))
        dag.boolean(j)
    for definition, d in reversed(signals):
        current = dag.combine(current, definition, dag.clauses[current][0], d)
    dag.resolve(current, dag.axiom(1), -1)
    return cnf, dag.proof


def truth_check(n, cnf, rows):
    """Check the original cube for every generated base axiom and local implication."""
    universe = (1 << (1 << n)) - 1
    columns = {i: sum(1 << bit for bit in range(1 << n) if bit >> (i-1) & 1) for i in range(1, n+1)}
    @cache
    def zero_set(polynomial):
        values = 0
        for term in polynomial:
            mask = universe
            for i in term:
                mask &= columns[i]
            values ^= mask
        return universe ^ values
    meanings = []
    for row in rows:
        meaning = 0
        for raw in row["clause"]:
            meaning |= zero_set(Q["polynomial"](raw))
        if row["rule"] == "axiom":
            expected = 0
            for lit in cnf[row["axiom"]]:
                expected |= columns[lit] if lit > 0 else universe ^ columns[-lit]
            assert meaning == expected
        elif not row.get("parents"):
            assert meaning == universe
        else:
            old = universe
            for parent in row["parents"]:
                old &= meanings[parent]
            assert old & ~meaning == 0
        meanings.append(meaning)
    assert meanings and meanings[-1] == 0


def main():
    x, y, z = map(var, (1, 2, 3))
    affine = [Q["polynomial"](mon for i, mon in enumerate(((), (1,), (2,))) if mask >> i & 1)
              for mask in range(8)]
    cases = [(2, [(f, g)]) for f,g in product(affine, repeat=2)]
    cases += [(3, []), (3, [(x,y), (var(4),z)]),
              (3, [(add(x,y), add(y,z)), (add(var(4), one), add(x,z)), (add(var(5),var(4)),var(4))]),
              (3, [(x,x), (var(4),zero), (var(4),one), (var(6),add(y,var(4)))])]
    assignment_checks = largest = total_nodes = total_branches = 0
    deepest = {}
    for n, factors in cases:
        cnf, original = example(n, factors)
        out, stats = M["eliminate"](n, cnf, original)
        truth_check(n, cnf, out)
        k, size = len(factors), len(original)
        assert stats["branches"] == 2**k
        assert len(out) <= 128 * 2**k * (n+k+1) * (size+1)
        largest = max(largest, len(out))
        total_nodes += len(out)
        total_branches += stats["branches"]
        assignment_checks += len(out) * (1 << n)
        if k == 4:
            deepest = {"inferences_before":size, **stats}
    # A false declaration or use before availability is checked even on an inconsistent source.
    cnf, original = example(3, [(x,y)])
    bad = [dict(r) for r in original]
    change = next(i for i, r in enumerate(bad) if r["rule"] == "define")
    bad[change]["factors"] = [enc(var(4)), enc(y)]
    negative = 0
    for wrong in (bad, [dict(r, clause=[[]]) if i==change else r for i,r in enumerate(original)]):
        try:
            M["eliminate"](3,cnf,wrong)
        except ValueError:
            negative += 1
    assert negative == 2
    return {"status":"passed","tested_proofs":len(cases),"one_gate_affine_pairs":64,
            "largest_output_nodes":largest,"generated_proof_nodes":total_nodes,"tested_leaves":total_branches,
            "source_line_assignment_checks":assignment_checks,"four_gate_case":deepest,
            "bad_declarations_rejected":negative}


if __name__ == "__main__":
    print(json.dumps(main(),sort_keys=True))
