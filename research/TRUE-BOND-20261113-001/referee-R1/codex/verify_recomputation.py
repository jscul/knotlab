"""Cold SAT replay with a second solver and separately written depth-first CNF.

Does not import recompute_sat or any study implementation. Replays all retained
bond projections, raw-assumption lower searches on small cells, and combinatorial
coverage checks on every exact result.
"""
import itertools as it
import json
from math import comb
from pathlib import Path
import resource
import time
from pysat.solvers import Solver

OUT = Path(__file__).resolve().parent


def read_rows():
    latest = {}
    for name in ('recomputed.jsonl', 'recomputed_retries.jsonl'):
        for line in (OUT / name).read_text().splitlines():
            r = json.loads(line)
            latest[r['idx'], r['s'], r['h']] = r
    return latest


def fresh_depth_first(definition, D, G):
    constraints, names = [], {}

    def variable(name):
        if name not in names:
            names[name] = len(names) + 1
        return names[name]

    top = tuple(variable(((), 'top_port', p)) for p in range(3))
    local_count = definition[1]

    def visit(path, ports):
        own = tuple(variable((path, 'own', j)) for j in range(local_count))
        env = ports + own
        child = 0
        for kind, indices in definition[2]:
            variables = tuple(env[j] for j in indices)
            if kind == 'K':
                constraints.extend((list(variables), [-a for a in variables]))
            else:
                assert kind == 'SELF'
                if len(path) == D:
                    for bits in it.product((0, 1), repeat=3):
                        state = bits[0] + 2 * bits[1] + 4 * bits[2]
                        if state not in G:
                            constraints.append([v if b == 0 else -v for v, b in zip(variables, bits)])
                else:
                    visit(path + (child,), variables)
                child += 1
    visit((), top)
    constraints.append([len(names), -len(names)])
    return constraints, names


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def anchored_count(n, k):
    return choose(n, k) - choose(n-3, k) - choose(n-2, k) + choose(n-5, k)


def main():
    started = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    rows = read_rows()
    families = {r['idx']: r for r in json.loads((OUT / 'selected_families.json').read_text())['families']}
    checks = []
    for key, r in sorted(rows.items()):
        assert r['status'] == 'exact', key
        f = families[r['idx']]
        clauses, names = fresh_depth_first(f['defs'][0], r['D'], set(f['G']))
        assert len(names) == r['n']
        coverage = {str(k): r['checked_by_size'][str(k)] == anchored_count(r['n'], k)
                    for k in range(2, r['L_trunc'])}
        assert all(coverage.values()), key
        W = tuple(names[(tuple(o['copy']), o['role'], o['slot'])] for o in r['witness']['origins'])
        with Solver(name='g4', bootstrap_with=clauses) as S:
            calls = [0]
            def sat(variables, bits):
                calls[0] += 1
                return S.solve(assumptions=[v if b else -v for v, b in zip(variables, bits)])
            def free(variables):
                return all(sat(variables, bits) for bits in it.product((0, 1), repeat=len(variables)))
            forbidden = [list(bits) for bits in it.product((0, 1), repeat=len(W)) if not sat(W, bits)]
            deletions = [free(tuple(w for j, w in enumerate(W) if j != i)) for i in range(len(W))]
            assert forbidden == r['witness']['forbidden'] and all(deletions), key
            raw_lower = None
            # Raw SAT search on each small h=1 case; no model cache or complement shortcut.
            if r['h'] == 1 and r['s'] <= 2:
                top = {names[((), 'top_port', i)] for i in range(3)}
                target = {names[((0,) * r['s'], 'own', i)] for i in range(2)}
                counts = {}
                for k in range(2, r['L_trunc']):
                    counts[k] = 0
                    for variables in it.combinations(range(1, len(names) + 1), k):
                        if not set(variables).intersection(top) or not set(variables).intersection(target):
                            continue
                        counts[k] += 1
                        if not free(variables):
                            assert not all(free(tuple(w for w in variables if w != v)) for v in variables), (key, variables)
                    assert counts[k] == anchored_count(len(names), k)
                raw_lower = counts
        checks.append(dict(idx=r['idx'], s=r['s'], h=r['h'], pass_result=True,
                           projection_matches=True, all_deletions_free=True,
                           support_enumeration_counts_match=coverage,
                           independent_raw_lower_search=raw_lower, cold_solver_calls=calls[0]))
    monotonic = []
    for idx in families:
        for s in (1, 2, 3):
            seq = [rows[idx, s, h]['L_trunc'] for h in (1, 2, 3)]
            assert seq[0] >= seq[1] >= seq[2]
            monotonic.append(dict(idx=idx, s=s, L_by_h=seq))
    result = dict(cases=len(checks), passed=len(checks), second_solver='Glucose 4 (g4)',
                  independent_CNF='depth first allocation keyed by origin',
                  raw_lower_search_cases=sum(x['independent_raw_lower_search'] is not None for x in checks),
                  all_monotone_in_h=True, monotonic=monotonic, checks=checks,
                  seconds=round(time.monotonic() - started, 6),
                  peak_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 3))
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('monotonic', 'checks')}))


if __name__ == '__main__':
    main()
