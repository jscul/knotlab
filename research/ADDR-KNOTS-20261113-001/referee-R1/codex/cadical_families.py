"""Fresh level-by-level CaDiCaL trajectories for initially hard alive levels.

Only directly checked models are promoted. Solver refutations without a logged,
checked certificate are retained diagnostically and never promoted here.
"""
import json
import resource
import tempfile
import time
from pathlib import Path

from pysat.solvers import Solver
from fresh_patterns import cnf, fate, pattern, verify_assignment

HERE = Path(__file__).resolve().parent
tempfile.tempdir = str(HERE)


def main():
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    selected = sorted({row['file'] for row in json.loads((HERE / 'refinement_selection.json').read_text())
                       if row['recorded_verdict'] == 1})
    results = []
    for name in selected:
        path = HERE / name
        rec = json.loads(path.read_text())
        previous = None
        family = {'key_id': rec['key_id'], 'file': name, 'conflict_budget': 200000,
                  'solver': 'Cadical195, fresh trajectory, no proof logging', 'levels': []}
        for n in range(1, 13):
            start = time.monotonic()
            triples = pattern(rec['key'], n)
            clauses = cnf(triples)
            values = [False] * (1 << n)
            if not clauses:
                verdict, stats = True, {}
            else:
                symmetry = min(x for triple in triples for x in triple) + 1
                with Solver(name='cd19', bootstrap_with=clauses + [[symmetry]]) as solver:
                    if previous is not None:
                        solver.set_phases([(x + 1) * (1 if previous[x >> 1] else -1) for x in range(1 << n)])
                    solver.conf_budget(200000)
                    verdict = solver.solve_limited()
                    stats = solver.accum_stats()
                    if verdict is True:
                        for lit in solver.get_model():
                            values[abs(lit) - 1] = lit > 0
            item = {'level': n, 'verdict': int(verdict) if verdict is not None else None,
                    'stats': stats, 'seconds': time.monotonic() - start}
            old = rec['levels'][n - 1]
            if verdict is True:
                assert verify_assignment(triples, values)
                assignment = ''.join('1' if v else '0' for v in values)
                item['assignment'] = assignment
                item['witness_checked_knots'] = len(triples)
                assert old['recorded_verdict'] != 0, ('CERTIFIED CONTRADICTION', rec['key_id'], n, assignment)
                if old['verdict'] is None:
                    old.update(verdict=1, certified=True, assignment=assignment,
                               witness_checked_knots=len(triples), solver=family['solver'], agrees=True)
                    old.pop('reason', None)
                    old.setdefault('refinements', []).append({k: v for k, v in item.items() if k != 'assignment'})
            family['levels'].append(item)
            previous = values if verdict is True else None
            print(json.dumps({'key': rec['key_id'][:12], 'n': n, 'v': item['verdict'],
                              'seconds': item['seconds']}), flush=True)
        verdicts = [level['verdict'] for level in rec['levels']]
        rec['fresh_fate'] = fate(verdicts, rec['counts'])
        rec['fate_agrees'] = rec['fresh_fate'] == rec['recorded_fate']
        rec['all_levels_certified'] = all(level['certified'] for level in rec['levels'])
        path.write_text(json.dumps(rec, sort_keys=True, indent=2) + '\n')
        results.append(family)
        (HERE / 'cadical_families.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
