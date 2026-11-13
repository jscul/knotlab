"""Fresh direct satisfiability referee computation; no TRUE-BOND implementation imports.

Only allowed BD census supplies family definitions. Everything after that (greatest
fixed point G, copy expansion, CNF, support enumeration, minimality) is fresh code.
No subtree summary or ray DP is used. All supports below the first bond size are
exhausted; at the first successful size one witness suffices.
"""
from __future__ import annotations
import argparse
from collections import Counter, deque
import hashlib
import importlib.util
import itertools as it
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BD_PATH = ROOT / 'experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py'
REF_PATH = ROOT / 'artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl'
PRIOR_PATH = ROOT / 'artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl'


def load_bd():
    spec = importlib.util.spec_from_file_location('permitted_bond_depth', BD_PATH)
    bd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bd)
    return bd


def greatest_port_relation(definition):
    """Descend from all 8 states using explicit local assignments, not study code."""
    _, local_count, calls = definition
    current = set(range(8))
    rounds = 0
    while True:
        nxt = set()
        for values in it.product((0, 1), repeat=3 + local_count):
            valid = True
            for kind, args in calls:
                triple = tuple(values[a] for a in args)
                if kind == 'K':
                    valid = len(set(triple)) > 1
                elif kind == 'SELF':
                    valid = sum(v << i for i, v in enumerate(triple)) in current
                else:
                    raise ValueError(kind)
                if not valid:
                    break
            if valid:
                nxt.add(sum(values[i] << i for i in range(3)))
        rounds += 1
        assert nxt <= current
        if nxt == current:
            return current, rounds
        current = nxt


def select_families():
    prior = [json.loads(t) for t in PRIOR_PATH.read_text().splitlines()]
    ids = {r['idx'] for r in prior if r.get('complete') and (r.get('lambda_float') or 0) > 0}
    bd = load_bd()
    fs = [(idx, ds) for idx, ds in bd.families_one_def() if idx in ids]
    fs.sort(key=lambda p: (p[1][0][1], sum(k == 'SELF' for k, _ in p[1][0][2]), p[0]))
    chosen = fs[:7]
    chosen += [p for p in fs if p[0] == 911 and p[0] not in {i for i, _ in chosen}]
    if len(chosen) < 8:
        chosen = fs[:8]
    rows = []
    for idx, ds in chosen:
        G, rounds = greatest_port_relation(ds[0])
        _, _, bd_g = bd.L.depth_sequence(ds, bd.L.TOP)
        assert G == {i for i, a in enumerate(bd_g[0]) if a}
        rows.append(dict(idx=idx, defs=ds, locals=ds[0][1],
                         self_calls=sum(k == 'SELF' for k, _ in ds[0][2]),
                         G=sorted(G), G_rounds=rounds))
    result = dict(ordering='(own distinctions, SELF calls, idx); seven smallest plus mandatory 911',
                  study_size=len(ids), families=rows)
    (OUT / 'selected_families.json').write_text(json.dumps(result, indent=2) + '\n')
    return rows


def expand(definition, G, s, h):
    """Copies at levels 0..D inclusive, D=s+h. Bottom SELF arguments lie in G."""
    D = s + h
    _, local_count, calls = definition
    clauses, origins, copies = [], {}, []
    for p in range(1, 4):
        origins[p] = dict(copy=[], role='top_port', slot=p - 1, depth=0)
    next_var = 4
    pending = deque([((), (1, 2, 3))])
    target = None
    while pending:
        path, ports = pending.popleft()
        own = tuple(range(next_var, next_var + local_count))
        next_var += local_count
        env = ports + own
        for slot, v in enumerate(own):
            origins[v] = dict(copy=list(path), role='own', slot=slot, depth=len(path))
        if path == (0,) * s:
            target = own
        copies.append(dict(path=path, ports=ports, own=own))
        child_number = 0
        for kind, args in calls:
            actual = tuple(env[a] for a in args)
            if kind == 'K':
                clauses.append(list(actual))
                clauses.append([-v for v in actual])
            elif kind == 'SELF':
                if len(path) < D:
                    pending.append((path + (child_number,), actual))
                else:
                    for state in range(8):
                        if state not in G:
                            clauses.append([-v if (state >> i) & 1 else v for i, v in enumerate(actual)])
                child_number += 1
            else:
                raise ValueError(kind)
    n = next_var - 1
    # Declare unconstrained variables as well, including spare own distinctions.
    clauses.append([n, -n])
    assert target is not None
    return clauses, n, (1, 2, 3), target, origins, len(copies)


class DirectSAT:
    """All decisions are SAT assumptions; full satisfying models only skip queries.

    If cached genuine solutions realize every assignment on W, W is proved free.
    If an assignment is absent, ask SAT. A false answer proves constrained.
    Global complement symmetry halves assignments (checked on G by the caller).
    """
    def __init__(self, clauses, n):
        self.solver = Solver(name='cadical153', bootstrap_with=clauses)
        self.n = n
        self.calls = 0
        self.cache = {(): True}
        self.pattern = [0] * (n + 1)
        self.all_models = 0
        self.models = 0
        self.support_checks = 0
        self.query_satisfied = 0
        self.query_unsatisfied = 0
        self.cache_hits = 0
        self.model_coverage_hits = 0
        self.initial_satisfiable = self.ask([])

    def close(self):
        self.solver.delete()

    def ask(self, assumptions):
        self.calls += 1
        answer = self.solver.solve(assumptions=assumptions)
        if answer:
            self.query_satisfied += 1
            model = self.solver.get_model()
            assert len(model) >= self.n
            b, bc = 1 << self.models, 1 << (self.models + 1)
            for lit in model:
                if abs(lit) <= self.n:
                    self.pattern[abs(lit)] |= b if lit > 0 else bc
            self.models += 2
            self.all_models = (1 << self.models) - 1
        else:
            self.query_unsatisfied += 1
        return answer

    def free(self, support):
        W = tuple(sorted(support))
        if W in self.cache:
            self.cache_hits += 1
            return self.cache[W]
        self.support_checks += 1
        assert len(set(W)) == len(W)
        # Self-duality permits fixing the first variable to zero.
        for values in it.product((0, 1), repeat=len(W) - 1):
            assignment = (0,) + values
            seen = self.all_models
            for v, bit in zip(W, assignment):
                seen &= self.pattern[v] if bit else (self.all_models ^ self.pattern[v])
                if not seen:
                    break
            if seen:
                self.model_coverage_hits += 1
                continue
            assumptions = [v if bit else -v for v, bit in zip(W, assignment)]
            if not self.ask(assumptions):
                self.cache[W] = False
                return False
        self.cache[W] = True
        return True

    def witness(self, W):
        allowed, forbidden = [], []
        for values in it.product((0, 1), repeat=len(W)):
            assumptions = [v if bit else -v for v, bit in zip(W, values)]
            (allowed if self.ask(assumptions) else forbidden).append(list(values))
        deletions = []
        for v in W:
            remaining = tuple(w for w in W if w != v)
            # Independent full assumptions check; do not rely on the model cache.
            tests = [self.ask([w if bit else -w for w, bit in zip(remaining, values)])
                     for values in it.product((0, 1), repeat=len(remaining))]
            deletions.append(dict(forgotten=v, all_assignments_satisfiable=all(tests), tests=len(tests)))
        assert forbidden and allowed and all(d['all_assignments_satisfiable'] for d in deletions)
        return dict(variables=list(W), allowed=allowed, forbidden=forbidden, deletions=deletions)


def candidates(pool, top, target, size):
    """Enumerate every anchored support, once, including members anywhere."""
    top, target = set(top), set(target)
    for p in sorted(top):
        for q in sorted(target):
            rest = [v for v in pool if v not in (p, q)]
            for helpers in it.combinations(rest, size - 2):
                W = tuple(sorted((p, q) + helpers))
                if min(top.intersection(W)) != p or min(target.intersection(W)) != q:
                    continue
                yield W


class CaseTimeout(Exception):
    pass


def alarm_handler(signum, frame):
    raise CaseTimeout('per-case foreground time budget')


def run_case(family, s, h, seconds=90, maxsize=5, warm_support=None):
    started = time.monotonic()
    G = set(family['G'])
    assert all((7 ^ a) in G for a in G)
    clauses, n, top, target, origins, copy_count = expand(family['defs'][0], G, s, h)
    row = dict(idx=family['idx'], s=s, h=h, D=s+h, n=n, copies=copy_count,
               clauses=len(clauses), status='running', exhaustive_through=1,
               checked_by_size={}, method='direct SAT with exhaustive support search below minimum')
    S = DirectSAT(clauses, n)
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(seconds)
    try:
        assert S.initial_satisfiable
        warm_valid = (warm_support is not None and set(warm_support) <= set(range(1, n+1))
                      and set(warm_support).intersection(top) and set(warm_support).intersection(target)
                      and not S.free(warm_support)
                      and all(S.free(tuple(w for w in warm_support if w != v)) for v in warm_support))
        if warm_valid:
            row['warm_witness'] = list(warm_support)
            maxsize = min(maxsize, len(warm_support) - 1)
        for size in range(2, maxsize + 1):
            row['active_size'] = size
            count = 0
            for W in candidates(list(range(1, n + 1)), top, target, size):
                count += 1
                row['checked_by_size'][str(size)] = count
                if S.free(W):
                    continue
                if all(S.free(tuple(w for w in W if w != v)) for v in W):
                    row.update(status='exact', L_trunc=size, witness=S.witness(W))
                    row['witness']['origins'] = [origins[v] for v in W]
                    return row
            row['exhaustive_through'] = size
        if warm_valid:
            row.update(status='exact', L_trunc=len(warm_support), witness=S.witness(warm_support))
            row['witness']['origins'] = [origins[v] for v in warm_support]
            return row
        row.update(status='not_found_within_size_cap', L_trunc=None)
    except CaseTimeout as e:
        row.update(status='timeout', L_trunc=None, error=str(e))
    finally:
        signal.alarm(0)
        row.update(seconds=round(time.monotonic() - started, 6),
                   peak_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 3),
                   sat_calls=S.calls, cached_models=S.models, support_checks=S.support_checks,
                   sat_satisfied=S.query_satisfied, sat_unsatisfied=S.query_unsatisfied,
                   free_cache_hits=S.cache_hits, model_coverage_hits=S.model_coverage_hits)
        S.close()
    return row


def controls():
    results = []
    # This NAE chain on three fresh own distinctions per copy has L=s+3.
    d = (3, 3, [('K', (0, 1, 3)), ('SELF', (3, 4, 5))])
    G, rounds = greatest_port_relation(d)
    f = dict(idx='chain_control', defs=[d], G=sorted(G))
    for s in (1, 2):
        r = run_case(f, s, 1, seconds=30, maxsize=s+3)
        # The expected values are independently checked by the direct projection.
        r['expected'] = s + 3
        r['pass'] = r.get('L_trunc') == r['expected']
        results.append(r)
    # A wholly free recursive definition has no bonds up to the exhausted cap.
    f = dict(idx='free_control', defs=[(3, 1, [('SELF', (0, 1, 2))])], G=list(range(8)))
    r = run_case(f, 1, 1, seconds=30, maxsize=4)
    r['pass'] = r['status'] == 'not_found_within_size_cap' and r['exhaustive_through'] == 4
    results.append(r)
    # Great fixed point is NAE when NAE is explicitly imposed on the ports.
    G, rounds = greatest_port_relation((3, 0, [('K', (0, 1, 2)), ('SELF', (0, 1, 2))]))
    results.append(dict(control='greatest_fixed_point_NAE', G=sorted(G), pass_result=G == set(range(1, 7))))
    (OUT / 'controls.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(dict(controls=[r.get('pass',r.get('pass_result')) for r in results])), flush=True)
    assert all(r.get('pass', r.get('pass_result')) for r in results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', type=int, nargs='*')
    parser.add_argument('--h', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--s', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--seconds', type=int, default=90)
    parser.add_argument('--output', default='recomputed.jsonl')
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--warm-witnesses', help='Own earlier direct-SAT output, for retested upper witnesses only')
    args = parser.parse_args()
    # User budget is 6 GB total. This lane has a conservative 4 GB address cap.
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    if args.controls:
        controls()
        return
    families = select_families()
    if args.only:
        families = [f for f in families if f['idx'] in args.only]
    refs = {r['idx']: r for r in map(json.loads, REF_PATH.read_text().splitlines())}
    dest = OUT / args.output
    done = set()
    if dest.exists():
        done = {(r['idx'], r['s'], r['h']) for r in map(json.loads, dest.read_text().splitlines())}
    warm_rows = []
    if args.warm_witnesses:
        warm_rows = [r for r in map(json.loads, (OUT / args.warm_witnesses).read_text().splitlines()) if r['status'] == 'exact']
    with dest.open('a') as stream:
        for h in args.h:
            for s in args.s:
                for family in families:
                    if (family['idx'], s, h) in done:
                        continue
                    matches = [r for r in warm_rows if r['idx'] == family['idx'] and r['s'] == s and r['h'] <= h]
                    warm = min(matches, key=lambda r: (r['L_trunc'], r['h']))['witness']['variables'] if matches else None
                    row = run_case(family, s, h, seconds=args.seconds, maxsize=5, warm_support=warm)
                    if warm is not None:
                        row['warm_source'] = args.warm_witnesses
                    row['study_L'] = refs[family['idx']]['L'][s-1]
                    row['study_L_ray'] = refs[family['idx']]['L_ray'][s-1]
                    row['agrees_with_study'] = (row.get('L_trunc') == row['study_L']) if row['status'] == 'exact' else None
                    stream.write(json.dumps(row, sort_keys=True) + '\n')
                    stream.flush()
                    print(json.dumps({k: row.get(k) for k in ['idx','s','h','n','status','L_trunc','study_L','seconds','sat_calls']}), flush=True)


if __name__ == '__main__':
    main()
