"""Fresh all-copies CNF/SAT referee, independent of the study's algorithms.

Only the permitted input-language module is imported.  No port-to-port
relations, composition, semigroup, or path-DP implementation is used.

A second SAT problem chooses a signed cube of at most k distinctions. Every
allowed full model returned by the instance solver rules out all cubes
compatible with that model. Thus UNSAT of this second problem is an exact
certificate that every remaining eligible cube extends. UNSAT instance cubes
are checked for minimal *support*, over all assignments of each deletion.
Any smaller nonshattered support excludes all supersets, irrespective of signs.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
import resource
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex'
INPUT = ROOT / 'experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py'
spec = importlib.util.spec_from_file_location('referee_input_language', INPUT)
lang = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lang)
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType


def usual_and_limit(raw):
    defs = []
    for k, l, calls in raw:
        calls = [(c, tuple(a)) for c, a in calls]
        if any(c == 'SELF' and sorted(a) == [0, 1, 2] for c, a in calls):
            calls.append(('K', (0, 1, 2)))
        defs.append((k, l, calls))
    _, _, G = lang.depth_sequence(defs, lang.TOP)
    return defs, {i: [bool(x) for x in g] for i, g in G.items()}


def unfold(defs, G, cutoff, target_depth):
    """All definitions and all SELF children, fresh locals per occurrence.

    Root main is depth 0 when self-holding. Otherwise self-holding entry
    copies in its finite expansion are depth 1, per the frozen clarification.
    A numeric call is expanded at unchanged depth: only SELF increments it.
    All copies through cutoff inclusive are explicit; calls below use G.
    """
    n = defs[-1][0]
    clauses, targets, copies, origin = [], set(), [], {}
    selfholding = {i for i, d in enumerate(defs) if any(c == 'SELF' for c, _ in d[2])}

    def forbid(actual, good):
        for state, allowed in enumerate(good):
            if not allowed:
                clauses.append([-(v + 1) if state >> j & 1 else v + 1
                                for j, v in enumerate(actual)])

    def visit(i, actual, depth, address, recursive_context=False):
        nonlocal n
        k, l, calls = defs[i]
        context = recursive_context or i in selfholding
        local = list(range(n, n + l)); n += l
        env = list(actual) + local
        copies.append({'definition': i, 'depth': depth, 'address': address,
                       'ports': list(actual), 'own': local})
        for v in local:
            origin[v] = {'definition': i, 'depth': depth, 'address': address}
        # Numeric helper locals belong to the same flattened copy; they are
        # own distinctions as well. Other self-holding types use the same
        # SELF depth convention and are not silently omitted as targets.
        if depth == target_depth:
            targets.update(local)
        for callno, (callee, args) in enumerate(calls):
            a = [env[x] for x in args]
            if callee == 'K':
                clauses.extend([[v + 1 for v in a], [-(v + 1) for v in a]])
            elif callee == 'SELF':
                if depth >= cutoff:
                    forbid(a, G[i])
                else:
                    visit(i, a, depth + 1, address + [callno], True)
            else:
                # Finite inlining is not a SELF depth step. A main wrapper
                # enters a self-holding copy at depth 1.
                d = depth if context else (1 if callee in selfholding else 0)
                visit(callee, a, d, address + ['D'+str(callno)], context)

    main = len(defs) - 1
    visit(main, list(range(defs[-1][0])), 0, [])
    return clauses, n, set(range(defs[-1][0])), targets, copies, origin


class SearchTimeout(Exception):
    pass


class DirectSearch:
    def __init__(self, clauses, n, roots, targets, seconds=90, preferred_pools=None):
        self.n, self.roots, self.targets = n, roots, targets
        self.clause_supports = {tuple(sorted({abs(x)-1 for x in c})) for c in clauses}
        cs = {tuple(sorted(c)) for c in clauses}
        self.complement_closed = all(tuple(sorted(-x for x in c)) in cs for c in clauses)
        self.sat = Solver(name='cadical195', bootstrap_with=clauses)
        self.start, self.deadline = time.monotonic(), time.monotonic() + seconds
        self.models, self.model_keys, self.forbidden = [], set(), set()
        self.queries, self.iterations = 0, 0
        self.random = random.Random(318021)
        self.meta = None
        self.shatter_cache = {}
        self.by_size = []
        self.profiles = [0]*n
        self.preferred_pools = preferred_pools or []

    def tick(self):
        if time.monotonic() > self.deadline:
            raise SearchTimeout()

    def solve(self, cube):
        self.tick(); self.queries += 1
        answer = self.sat.solve(assumptions=cube)
        if answer:
            m = {abs(x)-1: x > 0 for x in self.sat.get_model() if abs(x) <= self.n}
            bits = bytes(int(m.get(v, False)) for v in range(self.n))
            variants = [bits]
            if self.complement_closed:
                variants.append(bytes(1-x for x in bits))
            for model_bits in variants:
                if model_bits not in self.model_keys:
                    bit = 1 << len(self.models)
                    for v,b in enumerate(model_bits):
                        if b: self.profiles[v] |= bit
                    self.model_keys.add(model_bits); self.models.append(model_bits)
                    if self.meta is not None:
                        self.meta.add_clause(self.model_clause(model_bits))
            return True
        return False

    @staticmethod
    def pos(v): return 3*v + 1
    @staticmethod
    def neg(v): return 3*v + 2
    @staticmethod
    def selected(v): return 3*v + 3

    def model_clause(self, model):
        return [self.neg(v) if b else self.pos(v) for v, b in enumerate(model)]

    def shatters(self, support):
        support = tuple(sorted(support))
        if support in self.shatter_cache:
            return self.shatter_cache[support]
        for state in range(1 << len(support)):
            bits = tuple(state >> j & 1 for j in range(len(support)))
            mask = (1 << len(self.models))-1
            for j,v in enumerate(support):
                mask &= self.profiles[v] if bits[j] else ~self.profiles[v]
                if not mask: break
            if mask:
                continue
            if not self.solve([(v+1) if bits[j] else -(v+1) for j, v in enumerate(support)]):
                self.shatter_cache[support] = False
                return False
        self.shatter_cache[support] = True
        return True

    def minimal_support(self, support):
        support = set(support)
        for v in sorted(support):
            smaller = support - {v}
            if not self.shatters(smaller):
                support = smaller
        return tuple(sorted(support))

    def exclude_nonface(self, support):
        support = tuple(sorted(support))
        self.forbidden.add(support)
        if self.meta is not None:
            self.meta.add_clause([-self.selected(v) for v in support])

    def result(self, found, by_size):
        assert not self.shatters(found)
        assert all(self.shatters(set(found)-{v}) for v in found)
        bad = []
        for state in range(1 << len(found)):
            cube = [(v+1) if state >> j & 1 else -(v+1) for j,v in enumerate(found)]
            if not self.solve(cube): bad.append(state)
        return {'minimum':len(found),'witness':list(found),'forbidden_states':bad,
                'by_size':by_size,'one_deleted_all_shattered':True}

    def preferred_witness(self, size):
        # This is a positive-witness heuristic only. All lower-size
        # exclusions still range over EVERY unfolded distinction.
        stop = min(self.deadline, time.monotonic()+4)
        tried = set()
        for pool in self.preferred_pools:
            for support in itertools.combinations(sorted(pool),size):
                if time.monotonic()>stop: return None
                if not set(support)&self.roots or not set(support)&self.targets: continue
                if support in tried: continue
                tried.add(support)
                if any(set(f).issubset(support) for f in self.forbidden): continue
                if self.shatters(support): continue
                minimal = self.minimal_support(support)
                if set(minimal)&self.roots and set(minimal)&self.targets:
                    return minimal
                self.exclude_nonface(minimal)
        return None

    def global_supports(self,size):
        """Exhaust every endpoint-eligible support of the requested size."""
        seen=set()
        for a in sorted(self.roots):
            for b in sorted(self.targets):
                others=[v for v in range(self.n) if v not in (a,b)]
                for extra in itertools.combinations(others,size-2):
                    self.tick()
                    support=tuple(sorted((a,b)+extra))
                    if support in seen:continue
                    seen.add(support)
                    if self.shatters(support):continue
                    minimal=self.minimal_support(support)
                    if set(minimal)&self.roots and set(minimal)&self.targets:
                        return minimal
                    self.exclude_nonface(minimal)
        return None

    def run(self, max_size=6, seeds=120):
        if not self.solve([]):
            raise ValueError('empty instance')
        # At size two the endpoint condition names every possible support;
        # enumerate them directly. This is also useful model coverage.
        q0 = self.queries
        for a in sorted(self.roots):
            for b in sorted(self.targets):
                if not self.shatters({a,b}):
                    support = self.minimal_support({a,b})
                    if set(support)&self.roots and set(support)&self.targets:
                        return {'minimum':len(support),'witness':list(support),
                                'by_size':[], 'one_deleted_all_shattered':True}
                    self.exclude_nonface(support)
        self.by_size.append({'size':2,'exhausted':True,'queries':self.queries-q0,
                             'iterations':0,'method':'all endpoint pairs'})
        # Models are aids only; all decisive UNSAT calls are exhaustive SAT.
        for _ in range(seeds):
            vs = self.random.sample(range(self.n), min(6, self.n))
            self.sat.set_phases([(v+1) if self.random.getrandbits(1) else -(v+1)
                                 for v in range(self.n)])
            self.solve([(v+1) if self.random.getrandbits(1) else -(v+1) for v in vs])
        by_size = self.by_size
        for size in range(3, max_size + 1):
            self.tick()
            preferred = self.preferred_witness(size)
            if preferred is not None:
                by_size.append({'size':size,'exhausted':False,
                                'method':'direct prefix witness after global lower exclusions'})
                return self.result(preferred,by_size)
            estimate=len(self.roots)*len(self.targets)*math.comb(self.n-2,size-2)
            enumeration_cap=2_000_000 if size==3 else 1_000_000
            if size in (3,4) and estimate<=enumeration_cap:
                q0=self.queries
                direct=self.global_supports(size)
                by_size.append({'size':size,'exhausted':direct is None,
                                'queries':self.queries-q0,'iterations':0,
                                'method':'every endpoint-eligible support, direct SAT/model coverage'})
                if direct is not None:return self.result(direct,by_size)
                continue
            base = []
            for v in range(self.n):
                p, q, t = self.pos(v), self.neg(v), self.selected(v)
                base.extend([[-p, -q], [-p, t], [-q, t], [-t, p, q]])
            base.append([self.selected(v) for v in sorted(self.roots)])
            base.append([self.selected(v) for v in sorted(self.targets)])
            enc = CardEnc.atmost([self.selected(v) for v in range(self.n)],
                                 bound=size, top_id=3*self.n, encoding=EncType.seqcounter)
            base.extend(enc.clauses)
            base.extend(self.model_clause(m) for m in self.models)
            base.extend([-self.selected(v) for v in f] for f in self.forbidden)
            # A clause support is directly known to be constrained. A bond
            # cannot strictly contain it. At equal size it can only qualify
            # if both endpoint requirements hold, so retain that possibility.
            for f in self.clause_supports:
                if len(f) < size or not (set(f)&self.roots and set(f)&self.targets):
                    base.append([-self.selected(v) for v in f])
            q0, i0 = self.queries, self.iterations
            self.meta = Solver(name='glucose42', bootstrap_with=base)
            timer = threading.Timer(max(0.001,self.deadline-time.monotonic()),self.meta.interrupt)
            timer.daemon=True;timer.start()
            found = None
            try:
                while True:
                    self.tick(); self.iterations += 1
                    self.meta.conf_budget(1000)
                    answer = self.meta.solve_limited(expect_interrupt=True)
                    if answer is None:
                        continue
                    if not answer:
                        break
                    mm = set(x for x in self.meta.get_model() if x > 0)
                    cube = [(v+1) if self.pos(v) in mm else -(v+1)
                            for v in range(self.n) if self.selected(v) in mm]
                    if self.solve(cube):
                        continue
                    support = self.minimal_support({abs(x)-1 for x in cube})
                    if set(support) & self.roots and set(support) & self.targets:
                        found = support
                        break
                    self.exclude_nonface(support)
            finally:
                timer.cancel();timer.join(timeout=1)
                self.meta.delete(); self.meta = None
            by_size.append({'size': size, 'exhausted': found is None,
                            'queries': self.queries-q0, 'iterations': self.iterations-i0})
            if found is not None:
                return self.result(found,by_size)
        return {'minimum': None, 'proved_lower_bound': max_size + 1,
                'by_size': by_size}

    def close(self): self.sat.delete()


def controls():
    cases = [
        ('one_nae', [[1,2,3],[-1,-2,-3]], 3, {0}, {2}, 3),
        ('two_independent', [[1,2,3],[-1,-2,-3],[4,5,6],[-4,-5,-6]], 6, {0}, {5}, None),
        ('two_nae_chain', [[1,2,3],[-1,-2,-3],[3,4,5],[-3,-4,-5]], 5, {0}, {4}, 4),
        ('prefix_without_endpoint_bond', [[1,2,3],[-1,-2,-3],[2,3,4],[-2,-3,-4]], 4, {0}, {3}, None),
        ('suffix_restores_endpoint_bond', [[1,2,3],[-1,-2,-3],[2,3,4],[-2,-3,-4],
                                         [3,4,5],[-3,-4,-5]], 5, {0}, {3}, 4),
        ('support_minimality_control', [[1,2],[-1,-2],[2,3,4],[-2,-3,-4]], 4, {0}, {3}, 3),
    ]
    out = []
    for name, clauses, n, root, target, expected in cases:
        # Exact exhaustive subset reference for controls, separate from CEGAR.
        with Solver(name='cadical195', bootstrap_with=clauses) as s:
            def full(vs):
                return all(s.solve(assumptions=[(v+1) if state >> j & 1 else -(v+1)
                                                for j,v in enumerate(vs)])
                           for state in range(1 << len(vs)))
            oracle = None
            for k in range(2, n+1):
                for vs in itertools.combinations(range(n), k):
                    if not set(vs)&root or not set(vs)&target: continue
                    if not full(vs) and all(full(tuple(x for x in vs if x != v)) for v in vs):
                        oracle = k; break
                if oracle: break
        search = DirectSearch(clauses,n,root,target,30)
        try: result = search.run(max_size=n,seeds=10)
        finally: search.close()
        # The oracle, not a hand-labelled expected value, is authoritative.
        assert result['minimum'] == oracle, (name, result, oracle)
        assert oracle == expected, (name, oracle, expected)
        out.append({'name': name, 'minimum': oracle, 'cegar_agrees': True,
                    'hand_expectation': expected})
    # Deliberately dropping one deletion check would accept this supersupport;
    # actual checker must reject it.
    search = DirectSearch([[1,2,3],[-1,-2,-3]],4,{0},{3},30)
    try:
        reject = not (not search.shatters({0,1,2,3}) and
                      all(search.shatters({0,1,2,3}-{v}) for v in range(4)))
    finally: search.close()
    assert reject
    return {'cases': out, 'nonminimal_mutant_rejected': reject}


def load_cases(count):
    rows = [json.loads(line)['result'] for line in (DATA/'full/results.jsonl').read_text().splitlines()]
    rows = [r for r in rows if r['verdict'] == 'grows']
    rows.sort(key=lambda r: (r['preparation']['s_block_size'],
                             r['preparation']['n_defs'], r['r'], r['key']))
    return rows[:count]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count',type=int,default=10)
    ap.add_argument('--case',type=int)
    ap.add_argument('--depths',default='1,2,3,4,5')
    ap.add_argument('--halos',default='1,2')
    ap.add_argument('--seconds',type=float,default=75)
    ap.add_argument('--max-size',type=int,default=6)
    ap.add_argument('--output',default='direct_bonds.jsonl')
    ap.add_argument('--controls',action='store_true')
    args = ap.parse_args()
    if args.controls:
        result = controls()
        (OUT/'direct_controls.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
        return
    rows = load_cases(args.count)
    for idx, row in enumerate(rows):
        if args.case is not None and args.case != idx: continue
        defs,G = usual_and_limit(json.loads(row['key']))
        for s in map(int,args.depths.split(',')):
            for h in map(int,args.halos.split(',')):
                t0 = time.monotonic()
                clauses,n,roots,targets,copies,origin = unfold(defs,G,s+h,s)
                rec = {'case': idx, 'key':row['key'], 's':s,'h':h, 'cutoff':s+h,
                       'variables':n,'clauses':len(clauses),'copies':len(copies),
                       'targets':len(targets),'r_recorded':row['r'],
                       'claimed_lower_bound':2+s//row['r'],
                       'L_path_recorded':row['L_path'][s-1],
                       'definition_count':len(defs), 'G':G}
                pools = []
                for target in copies:
                    if target['depth'] != s or not target['own']: continue
                    address=target['address']
                    pool=set(roots)
                    for ancestor in copies:
                        a=ancestor['address']
                        if len(a)<=len(address) and address[:len(a)]==a:
                            pool.update(ancestor['own']);pool.update(ancestor['ports'])
                    pools.append(pool)
                search = DirectSearch(clauses,n,roots,targets,args.seconds,pools)
                try:
                    rec.update(search.run(max_size=min(args.max_size,rec['L_path_recorded']),
                                          seeds=min(150, 30+n//3)))
                    rec['status']='exact' if rec['minimum'] is not None else 'lower_bound_only'
                    if rec.get('witness'):
                        rec['witness_origins']=[origin.get(v,{'root_port':v}) for v in rec['witness']]
                        rec['lower_bound_holds']=rec['minimum']>=rec['claimed_lower_bound']
                        rec['path_upper_bound_holds']=rec['minimum']<=rec['L_path_recorded']
                except SearchTimeout:
                    rec.update(status='timeout', minimum=None,by_size=search.by_size,
                               proved_lower_bound=max([x['size']+1 for x in search.by_size
                                                       if x['exhausted']]+[2]))
                finally:
                    rec.update(seconds=round(time.monotonic()-t0,3),queries=search.queries,
                               iterations=search.iterations,models=len(search.models),
                               excluded_nonfaces=len(search.forbidden),
                               peak_rss_kb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                    search.close()
                with (OUT/args.output).open('a') as f:f.write(json.dumps(rec,sort_keys=True)+'\n')
                print(json.dumps({k:rec[k] for k in ['case','s','h','variables','status','minimum','seconds','queries','iterations']}),flush=True)


if __name__ == '__main__':main()
