"""Relation-free exact small bonds and allocation locations for TOP referee.

Reuses the permitted CARRY referee's exact usual-limit CNF unfolding and
READ referee's independent MiniSat projection checker. No TOP study Python
is opened. Exact-global minima 2/3 are distinguished from finite-universe
minima >=4. All endpoint pairs have a finite exhaustive roster even in the
infinite pattern, so a verified 3-bond with no 2-bond is globally least.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import resource
import time
from pathlib import Path

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/TOP-INFO-20261114-001/referee-R1/codex'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


core = module('top_referee_carry_grow', Path('research/CARRY-BOUND-20261114-001/referee-R1/codex/grow_core.py'))
verify_core = module('top_referee_read_grow', Path('research/READ-RULE-20261114-001/referee-R1/codex/growth_core.py'))


def location(v, origin, target, roots):
    if v in roots:
        return {'id':v, 'kind':'main_port', 'allocation_depth':0,
                'from_root':0, 'from_target_level':target['depth'], 'address':[]}
    o = origin[v]
    a, b = o['address'], target['address']
    common = 0
    while common < min(len(a),len(b)) and a[common] == b[common]:
        common += 1
    on_word = len(a)<=len(b) and a==b[:len(a)]
    below_target = len(a)>len(b) and a[:len(b)]==b
    kind = ('main_own' if o['depth']==0 else 'target_own' if a==b else
            'on_target_word' if on_word else 'in_target_subtree' if below_target else 'side_subtree')
    return {'id':v, 'kind':kind, 'allocation_depth':o['depth'],
            'from_root':o['depth'], 'from_target_level':target['depth']-o['depth'],
            'address':a, 'target_word_attachment_level':common,
            'side_descent':len(a)-common if kind=='side_subtree' else 0}


def shape(support, copies, origin, roots, S, depth):
    found = []
    for c in copies:
        if c['definition']!=S or c['depth']!=depth or not set(support)&set(c['own']):
            continue
        loc = [location(v,origin,c,roots) for v in support]
        found.append({'target_address':c['address'], 'target_own':c['own'],
                      'members':loc,
                      'strict_middle_allocations':[x['id'] for x in loc if 0<x['allocation_depth']<depth],
                      'side_members':[x['id'] for x in loc if x['kind']=='side_subtree'],
                      'endpoint_allocations_only':all(x['allocation_depth'] in (0,depth) and x['kind']!='side_subtree' for x in loc)})
    return found


def endpoint_only(search, copies, roots, S, depth, maximum=4):
    """Find a least-size witness using main block and target's own members.

    This search may return no small witness; that is never an infinite-system
    negative verdict. Positive 3-bonds refute any need for strict-middle
    allocation in the indicated cell when size-2 exclusions are complete.
    """
    root_block = set(roots)|set(copies[0]['own'])
    checked = set()
    for size in range(2,maximum+1):
        for c in copies:
            if c['definition']!=S or c['depth']!=depth:
                continue
            own = set(c['own'])
            for a in sorted(roots):
                for x in sorted(own):
                    for extra in itertools.combinations(sorted((root_block|own)-{a,x}),size-2):
                        support = tuple(sorted((a,x)+extra))
                        if support in checked:
                            continue
                        checked.add(support)
                        if not search.shatters(support) and all(search.shatters(set(support)-{v}) for v in support):
                            return list(support),len(checked)
    return None,len(checked)


def estimate(calls, depth):
    return sum(calls**j for j in range(depth+1))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cases',default='0,1,2,3')
    p.add_argument('--depths',default='2,3,4,6')
    p.add_argument('--halo',type=int,default=1)
    p.add_argument('--seconds',type=float,default=15)
    p.add_argument('--out',default='middle_results.jsonl')
    p.add_argument('--max-size',type=int,default=6)
    p.add_argument('--endpoint-max-size',type=int,default=4)
    p.add_argument('--controls',action='store_true')
    args=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    if args.controls:
        (HERE/'middle_controls.json').write_text(json.dumps(verify_core.controls(),indent=2)+'\n')
        return
    inputs=json.loads((HERE/'middle_inputs.json').read_text())
    output=HERE/args.out
    if output.exists():
        raise RuntimeError('Refusing to overwrite previous run '+str(output))
    for index in map(int,args.cases.split(',')):
        family=inputs[index]
        defs=core.usual(json.loads(family['key']))
        G,history=core.limits(defs)
        for depth in map(int,args.depths.split(',')):
            cutoff=depth+args.halo
            begin=time.monotonic()
            rec={k:family[k] for k in ('key','key_sha256','stratum','S','wrapper','calls','preperiod','period')}
            rec.update(case=index,depth=depth,cutoff=cutoff,halo=args.halo,
                endpoint_max_size=args.endpoint_max_size,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
            if estimate(family['calls'],cutoff)>12000:
                rec.update(status='skipped_exponential_copy_estimate',estimate=estimate(family['calls'],cutoff))
            else:
                cnf,n,roots,targets,copies,origin,boundary=core.unfold(defs,G,family['S'],cutoff,depth)
                rec.update(variables=n,clauses=len(cnf),copies=len(copies),targets=len(targets),
                           boundary=len(boundary),usual_limits=[sorted(g) for g in G])
                pools=core.preferred_pools(copies,roots,family['S'],depth)
                search=core.DirectSearch(cnf,n,roots,targets,args.seconds,pools)
                try:
                    rec.update(search.run(max_size=min(n,args.max_size),seeds=min(30,10+n//5)))
                    rec['status']='exact_prefix' if rec['minimum'] else 'lower_bound_only'
                    if rec.get('witness'):
                        rec['verification']=verify_core.verify(cnf,rec['witness'],roots,targets)
                        rec['allocation_locations']=shape(rec['witness'],copies,origin,roots,family['S'],depth)
                        rec['global_minimum']=rec['minimum'] if rec['minimum']<=3 else None
                    # Endpoint-only search has its own cheap bounded budget.
                    search.deadline=time.monotonic()+min(args.seconds,8)
                    try:
                        ep,checks=endpoint_only(search,copies,roots,family['S'],depth,args.endpoint_max_size)
                        rec['endpoint_only_bond']=ep
                        rec['endpoint_only_supports_checked']=checks
                        rec['endpoint_only_status']='completed'
                        if ep:
                            rec['endpoint_only_verification']=verify_core.verify(cnf,ep,roots,targets)
                            rec['endpoint_only_locations']=shape(ep,copies,origin,roots,family['S'],depth)
                    except core.SearchTimeout:
                        rec['endpoint_only_status']='timeout'
                except core.SearchTimeout:
                    rec.update(status='timeout',by_size=search.by_size,
                        proved_prefix_lower_bound=max([x['size']+1 for x in search.by_size if x['exhausted']]+[2]))
                finally:
                    rec.update(queries=search.queries,seconds=round(time.monotonic()-begin,4),
                        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                    search.close()
            with output.open('a') as f:
                f.write(json.dumps(rec,sort_keys=True)+'\n')
            print(json.dumps({k:rec.get(k) for k in ('case','key_sha256','depth','variables','status','minimum','global_minimum','endpoint_only_bond','seconds')}),flush=True)
    (HERE/(output.stem+'_inputs.json')).write_text(json.dumps({**core.READS,**verify_core.sources()},indent=2)+'\n')


if __name__=='__main__':
    main()
