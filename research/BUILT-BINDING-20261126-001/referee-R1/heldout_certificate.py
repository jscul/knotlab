"""Check a held-out triple literally. Search for disjoint simple paths on the same stage."""
import argparse
from collections import defaultdict
from functools import reduce
from itertools import combinations, product
import json
import operator
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

from pysat.solvers import Solver
import unrestricted as U

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
resource.setrlimit(resource.RLIMIT_AS, (1000 << 20, 1000 << 20))


def clauses(names, bit):
    for bs in product((0, 1),repeat=len(names)):
        if sum(bs) % 2 != bit:
            yield [(-i-1 if b else i+1) for i,b in zip(names,bs)]


def changes(rows, parts):
    n = 1 + max(max(r) for r in rows)
    syndromes = [sum(1 << k for k,r in enumerate(rows) if d in r) for d in range(n)]
    carrier = [sum(1 << k for k,p in enumerate(parts) if d in p) for d in range(n)]
    counts = [[0]*8 for _ in range(5)]
    for size in range(1, 6):
        for c in combinations(range(n), size):
            if not reduce(operator.xor,(syndromes[d] for d in c)):
                counts[size-1][reduce(operator.xor,(carrier[d] for d in c))] += 1
    return counts


def path_search(rows, parts):
    who = U.owners(rows)
    outer = len(rows)
    adj = [[] for _ in range(outer+1)]
    for d, h in enumerate(who):
        a, b = h if len(h)==2 else (h[0],outer)
        adj[a].append((b,d))
        adj[b].append((a,d))
    laws = U.basis(U.mask(r) for r in rows)
    targets = [U.reduce_by(U.mask(p),laws) for p in parts]
    by_value = {v:set() for v in targets}
    for root in range(outer+1):
        def visit(k, seen, m):
            if m and k > root:
                v = U.reduce_by(m,laws)
                if v in by_value:
                    by_value[v].add(m)
            if len(seen) == 9:
                return
            for w, d in adj[k]:
                if w not in seen:
                    visit(w,seen|{w},m|(1<<d))
        visit(root,{root},0)
    best = None
    supports = [sorted(by_value[v],key=lambda m:(m.bit_count(),m)) for v in targets]
    for a in supports[0]:
        for b in supports[1]:
            if a&b:
                continue
            for c in supports[2]:
                if c&(a|b):
                    continue
                new = (a.bit_count()+b.bit_count()+c.bit_count(),a,b,c)
                if best is None or new < best:
                    best = new
                break
    return dict(limit=8, counts=list(map(len,supports)),
                example=None if best is None else [list(U.indices(x)) for x in best[1:]])


def inspect(rows, parts, search_paths=False):
    even = []
    with_zero = [[] for _ in rows]
    solutions = {}
    for v in product((0,1),repeat=3):
        with Solver(bootstrap_with=[c for r in rows for c in clauses(r,0)]) as solver:
            for p, b in zip(parts,v):
                for c in clauses(p,b):
                    solver.add_clause(c)
            if solver.solve():
                key=''.join(map(str,v))
                even.append(key)
                solutions[key]=[x-1 for x in solver.get_model() if x>0]
                for k,r in enumerate(rows):
                    if solver.solve(assumptions=[-x-1 for x in r]):
                        with_zero[k].append(key)
    raw = changes(rows,parts)
    answer=dict(knots=len(rows),distinctions=1+max(max(r) for r in rows), image=even,
                attained_by=solutions, images_with_one_knot_zero=with_zero,
                allowed_change_counts_by_size_and_carrier_flips=raw)
    if search_paths:
        answer['simple_paths']=path_search(rows,parts)
    return answer


def canonical(image):
    names = ['a','b','c']
    cnf = '; '.join(' '.join(('~' if b=='1' else '')+n for n,b in zip(names,f'{v:03b}'))
                    for v in range(8) if f'{v:03b}' not in image)
    out = {}
    for c in names:
        call = subprocess.run([sys.executable,'-B','-m','knotlab','check','--cnf',cnf,'--contact',c,
                               '--loops',*[v for v in names if v!=c],'--json'],
                              capture_output=True,text=True,check=True,cwd=ROOT,
                              env=dict(os.environ, PYTHONPATH=str(ROOT/'tools')))
        out[c] = json.loads(call.stdout)
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pilot',action='store_true')
    args=ap.parse_args()
    start=time.monotonic()
    cert=json.loads((HERE/'unrestricted_heldout.json').read_text())['examples']['at most five'][0]
    rows, parts = cert['knots'], cert['supports']
    assert len(rows)==20
    result=dict(start='Nineteenth accepted labelled eight-knot sample, seed 20261214.', carriers=parts)
    # Only a comparison: the start and independent stages come from the
    # rejection process and fresh-count implementation in unrestricted.py.
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    sys.path.insert(0,str(U.DATA))
    from forbid import grown
    shared_stage=independent=tuple(tuple(r) for r in rows[:8])
    compared=[]
    for t in range(1, 2 if args.pilot else 4):
        shared_stage,status,_=grown(shared_stage,'parity','ordinary')
        independent=U.grow(independent)
        assert status=='funded' and shared_stage==independent
        compared.append(dict(round=t,matching_ordered_knot_laws=len(independent)))
        if t==2:
            assert shared_stage==tuple(tuple(r) for r in rows)
    result['comparison_only_with_shared_growth']=compared
    result['rounds']={}
    stages = [(0,rows[:8])] if args.pilot else [(0,rows[:8]),(1,rows[:13]),(2,rows)]
    for t, stage in stages:
        now=inspect(stage,parts,search_paths=True)
        assert now['image']==['000','011','101','110']
        if t==2:
            assert all(v == now['image'] for v in now['images_with_one_knot_zero'])
            assert not any(sum(by_word[1:]) for by_word in now['allowed_change_counts_by_size_and_carrier_flips'])
        result['rounds'][t]=now
    result['checker']=canonical(now['image'])
    if not args.pilot:
        new_parts=cert['new distinctions only']
        assert all(x >= 18 for p in new_parts for x in p)
        result['new_distinction_carriers']=new_parts
        result['round_two_new_distinctions']=inspect(rows,new_parts)
        mismatch=[]
        for old,new in zip(parts,new_parts):
            # Seek a state where the two named parities disagree.
            with Solver(bootstrap_with=[c for r in rows for c in clauses(r,0)]) as solver:
                for c in clauses(sorted(set(old)^set(new)),1):
                    solver.add_clause(c)
                mismatch.append(solver.solve())
        assert not any(mismatch)
        result['allowed_state_distinguishing_old_and_new_reads']=mismatch
        paths=now['simple_paths']['example']
        if paths:
            result['path_alternative']=inspect(rows,paths)
            assert result['path_alternative']['image']==now['image']
        (HERE/'heldout_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print('pilot' if args.pilot else 'full', round(time.monotonic()-start,3), 'seconds', now['simple_paths'])
if __name__=='__main__':
    main()
