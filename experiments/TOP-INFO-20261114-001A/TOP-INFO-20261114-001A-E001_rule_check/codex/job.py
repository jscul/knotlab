"""Shared-runner job for TOP checks. This file never launches a service."""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))
import top_data as data
from limits import Limits, LimitReached
CAT=None
ROWS=None


def setup(params):
    global CAT,ROWS
    if params:
        raise ValueError('no scientific parameter overrides')
    CAT=json.loads((HERE/'catalog.json').read_text())
    indexed=CAT['source_index']
    s=(data.ROOT/indexed['source']).stat()
    if (s.st_size,s.st_mtime_ns)!=(indexed['bytes'],indexed['mtime_ns']):
        raise ValueError('CARRY file changed since reused streaming index')
    frozen=HERE/'frozen_sources.json'
    if not frozen.exists():
        raise ValueError('freeze local code and dependencies first')
    for f in json.loads(frozen.read_text())['files']:
        if data.inputs.digest(data.ROOT/f['path'])!=f['sha256']:
            raise ValueError('frozen implementation/input changed: '+f['path'])
    ROWS={r['key']:r for r in CAT['rows']}


def cases():
    if CAT is None:
        setup({})
    # Interleave the three operations so --limit 20 exercises every implementation.
    flags=sorted(ROWS,key=data.top_order)
    two=CAT['selected_two_block']
    forgetting=CAT['forgetting_controls']
    for i in range(max(len(flags),len(two),len(forgetting))):
        if i<len(flags):
            k=flags[i];yield 'flags:'+data.top_order(k),dict(kind='flags',key=k)
        if i<len(two):
            k=two[i];yield 'two_block:'+data.top_order(k),dict(kind='two_block',key=k)
        if i<len(forgetting):
            f=forgetting[i];yield 'forgetting:'+data.top_order(f['key']),dict(kind='forgetting',**f)


def comparison(raw,two):
    """Compare all overlapping eventual congruences, plus available prefix depths."""
    old=raw['window'];shift=int(raw['wrapper']);violations=[];tested=0
    old_levels={x['s']:x['U'] for x in old.get('levels',[])}
    for a in two.get('levels',[]):
        u=old_levels.get(a['s']);v=a['U2']
        if isinstance(u,int) and isinstance(v,int):
            tested+=1
            if v>u:violations.append(dict(s=a['s'],U=u,U2=v))
    if old.get('complete') and two.get('complete'):
        g=math.gcd(old['period'],two['period'])
        for a in old['residues']:
            for b in two['residues']:
                if (a['s_mod_period']-b['s_mod_period'])%g:
                    continue
                u,v=a['U'],b['U2']
                if isinstance(u,int) and isinstance(v,int):
                    tested+=1
                    if v>u:violations.append(dict(old_residue=a['residue'],two_residue=b.get('residue'),U=u,U2=v))
    complete=bool(old.get('complete') and two.get('complete'))
    return dict(passed=False if violations else True if complete else None,complete=complete,
                finite_pairs_tested=tested,violations=violations)


def forgetting_gate(two,r):
    shift=int(two['wrapper']);violations=[];tested=0
    for a in two.get('levels',[]):
        if not isinstance(a['U2'],int):continue
        tested+=1
        lower=2+a['s']//r
        if a['U2']<lower:violations.append(dict(s=a['s'],U2=a['U2'],lower=lower))
    # A finite repeating upper bound must recur at arbitrarily large depth.
    if two.get('complete'):
        for a in two['residues']:
            if not isinstance(a['U2'],int):continue
            s=two['preperiod']+a['residue']
            threshold=r*(a['U2']-1)
            if s<threshold:s+=math.ceil((threshold-s)/two['period'])*two['period']
            lower=2+s//r
            if a['U2']<lower:violations.append(dict(s=s,U2=a['U2'],lower=lower,periodic=True))
    complete=bool(two.get('complete'))
    return dict(r=r,wrapper_shift=shift,finite_levels_tested=tested,complete=complete,
                passed=False if violations else True if complete else None,violations=violations,
                qualification='word s; absolute depth s+wrapper shift; upper search through size 6; >6 is not a finite bound')


def run(case_id,payload):
    kind,key=payload['kind'],payload['key']
    if case_id!=kind+':'+data.top_order(key):raise ValueError('case identity mismatch')
    budget=Limits(585,2_800_000_000)
    if kind=='flags':
        import checks
        try:
            result=checks.run_family(ROWS[key],budget.checkpoint)
        except (LimitReached,MemoryError) as exc:
            result=dict(key=key,complete=False,residues=[],caps=[str(exc)],
                        plain_pinned=dict(some_residue=None,every_residue=None),
                        bond_pinned=dict(some_residue=None,every_residue=None))
    else:
        import two_block
        raw=data.load_raw(ROWS[key]) if kind=='two_block' else None
        result=two_block.run_family(key,raw=raw,checkpoint=budget.checkpoint)
        if kind=='two_block':result['one_block_gate']=comparison(raw,result)
        else:result['forgetting_gate']=forgetting_gate(result,payload['r'])
    result.update(kind=kind,metrics=budget.metrics())
    return result
