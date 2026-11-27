"""Check the frozen parity clauses and bound interface without importing the reader."""
import argparse
import ast
from itertools import product
import json
from pathlib import Path
import resource
from time import perf_counter
from pysat.card import CardEnc, EncType
from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent


def gate():
    source = ast.parse((HERE.parent / 'minflip.py').read_text())
    helper, = [node for node in ast.walk(source)
               if isinstance(node, ast.FunctionDef) and node.name == 'xor']
    call, = [node for node in ast.walk(helper) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr == 'extend']
    clauses = []
    names = {'acc': 1, 'y': 2, 'z': 3}
    for row in call.args[0].elts:
        literals = []
        for v in row.elts:
            if isinstance(v, ast.Name):
                literals.append(names[v.id])
            else:
                assert isinstance(v.op, ast.USub) and isinstance(v.operand, ast.Name)
                literals.append(-names[v.operand.id])
        clauses.append(literals)
    for a, b, y in product((0, 1), repeat=3):
        bits = (a, b, y)
        satisfied = all(any(bits[abs(lit)-1] == (lit > 0) for lit in row) for row in clauses)
        assert satisfied == (a ^ b == y)
    return clauses


def trial(size, fixed):
    # Equality around one ordinary cycle forces all distinctions to agree.
    # The target is one distinction or the parity of two equal distinctions.
    names = list(range(1, size+1))
    base = []
    for i in range(1, size+1):
        j = i % size + 1
        base.extend(([i, -j], [-i, j]))
    base.extend([[1, 2], [-1, -2]] if fixed else [[1]])
    with Minisat22(bootstrap_with=base) as unconstrained:
        if not unconstrained.solve():
            assert fixed
            return None
    def at_most(k):
        card = CardEnc.atmost(names, k, top_id=size, encoding=EncType.seqcounter)
        with Minisat22(bootstrap_with=base + card.clauses) as solver:
            if solver.solve():
                model = solver.get_model()
                assert all(abs(model[i-1]) == i for i in names)
                weight = sum(model[i-1] > 0 for i in names)
                assert weight <= k
                return weight
        return None
    high = at_most(40)
    if high is None:
        return 'more than 40'
    low = 0
    while high - low > 1:
        k = (low + high) // 2
        result = at_most(k)
        if result is None:
            low = k
        else:
            high = result
    return high


def main():
    resource.setrlimit(resource.RLIMIT_AS, (1536 << 20, 1536 << 20))
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    t = perf_counter()
    xor = gate()
    sizes = [39] if args.pilot else [1, 3, 15, 39, 40, 41]
    checks = {}
    for size in sizes:
        finite = trial(size, False)
        assert finite == (size if size <= 40 else 'more than 40')
        fixed = trial(size, True) if size >= 2 else 'not applicable'
        checks[size] = {'one distinction':finite, 'two equal distinctions':fixed}
    if not args.pilot:
        (HERE / 'solver_gate_counts.json').write_text(json.dumps(
            {'frozen gate in order accumulator, next, output':xor,
             'gate truth assignments checked':8,'known minima with cap 40':checks}, indent=2) + '\n')
    print('Checked sizes', sizes, 'elapsed seconds', round(perf_counter() - t, 3))


if __name__ == '__main__':
    main()
