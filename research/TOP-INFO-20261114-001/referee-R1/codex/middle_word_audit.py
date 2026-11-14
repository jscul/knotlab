"""Exact selected-word SAT at larger depths, with top-only member sets.

Reuses only word_cnf's AST from the allowed earlier READ referee. Other
subtrees have their exact usual limits, not free boundary assumptions. No
per-call transfer or window relation is used to establish any displayed bond.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import itertools
import json
import resource
import time
from pathlib import Path

import middle_bonds as audit
ROOT, HERE, core, independent = audit.ROOT, audit.HERE, audit.core, audit.verify_core
OLDER = ROOT/'research/READ-RULE-20261114-001/referee-R1/codex/coverage_direct.py'
tree=ast.parse(OLDER.read_text())
tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='word_cnf']
namespace={'core':core}
exec(compile(tree,str(OLDER),'exec'),namespace)
word_cnf=namespace['word_cnf']


def words(calls,n,seed):
    """A fixed small hypothesis roster, not an exhaustive word search."""
    out=[]
    def add(w):
        if w not in out:
            out.append(w)
    if seed:
        add(tuple(seed[i%len(seed)] for i in range(n)))
    for size in range(1, min(4,n)+1):
        for cycle in itertools.product(range(calls),repeat=size):
            add(tuple(cycle[i%size] for i in range(n)))
    for tail in range(calls):
        for prefix in itertools.product(range(calls),repeat=min(3,n)):
            add(prefix+(tail,)*(n-len(prefix)))
    return out


def endpoint_bond(cnf,maximum=4):
    rootblock=set(cnf['roots'])|set(cnf['copies'][0]['own'])
    target=set(cnf['targets'])
    universe=rootblock|target
    with core.Solver(name='cadical195',bootstrap_with=cnf['clauses']) as solver:
        cache={}
        def full(support):
            key=tuple(sorted(support))
            if key not in cache:
                cache[key]=all(solver.solve(assumptions=[v+1 if mask>>j&1 else -(v+1)
                    for j,v in enumerate(key)]) for mask in range(1<<len(key)))
            return cache[key]
        assert solver.solve()
        pairs=all(full({r,x}) for r in cnf['roots'] for x in target)
        for size in range(2, min(maximum,len(universe))+1):
            for support in itertools.combinations(sorted(universe),size):
                if not set(support)&cnf['roots'] or not set(support)&target:
                    continue
                if not full(support) and all(full(set(support)-{v}) for v in support):
                    return {'witness':list(support),'size':size,'all_root_target_pairs_full':pairs,
                            'global_least_through_this_target_copy':size if size<=3 and (size==2 or pairs) else None,
                            'verification':independent.verify(cnf['clauses'],support,cnf['roots'],target),
                            'member_allocation_depths':[cnf['origin'].get(v,{'depth':0})['depth'] for v in support],
                            'all_allocated_at_root_or_target':True}
    return None


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cases',default='18,44,57')
    parser.add_argument('--depths',default='8,9,10,11,12,13,20,50')
    parser.add_argument('--out',default='middle_word_results.jsonl')
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    inputs=json.loads((HERE/'middle_inputs.json').read_text())
    output=HERE/args.out
    if output.exists():
        raise RuntimeError('Refusing overwrite '+str(output))
    for case in map(int,args.cases.split(',')):
        r=inputs[case]
        raw=json.loads(r['key'])
        defs=core.usual(raw)
        main=len(defs)-1
        flat=core.flatten(defs,main)
        entries=[j for j,(c,a) in enumerate(flat[1]) if c==r['S']] if r['wrapper'] else [None]
        for depth in map(int,args.depths.split(',')):
            start=time.monotonic()
            n=depth-int(r['wrapper'])
            found=None
            tries=0
            for entry in entries:
                for word in words(r['calls'],n,(1,1,0) if case==18 else (1,)):
                    cnf=word_cnf(raw,r['S'],entry,word)
                    tries+=1
                    bond=endpoint_bond(cnf,maximum=4)
                    if bond:
                        found={**bond,'entry':entry,'word':list(word),'variables':cnf['n'],
                               'clauses':len(cnf['clauses'])}
                        break
                if found:
                    break
            rec={'case':case,'key':r['key'],'key_sha256':r['key_sha256'],
                 'stratum':r['stratum'],'depth':depth,'wrapper':r['wrapper'],
                 'known_one_block_word_mu':r['preperiod'],'known_one_block_period':r['period'],
                 'status':'positive' if found else 'no_small_bond_in_fixed_word_roster',
                 'bond':found,'word_roster_tries':tries,'seconds':round(time.monotonic()-start,5),
                 'scope':'positive exact bond; no claim that sampled words exhaust the infinite family',
                 'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            with output.open('a') as f:
                f.write(json.dumps(rec,sort_keys=True)+'\n')
            print(json.dumps({'case':case,'depth':depth,'status':rec['status'],
                    'size':found['size'] if found else None,'tries':tries,'seconds':rec['seconds']}),flush=True)
    (HERE/(output.stem+'_inputs.json')).write_text(json.dumps({
        str(OLDER.relative_to(ROOT)):hashlib.sha256(OLDER.read_bytes()).hexdigest(),
        'helpers':independent.sources()},indent=2)+'\n')


if __name__=='__main__':
    main()
