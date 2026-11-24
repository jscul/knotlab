# Thread's separate check of study A, round 1 of rule R on the 1,024 sparse draws:
# groups from the RECORDED operator (end_operator.proposals), payments by this file's own code.
import sys, json, glob, gzip, collections
sys.path.insert(0,'experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test')
import lib
EO=lib.EO
A='artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/'
def round1(stars, conv):
    holders=collections.defaultdict(list)
    for k,s in enumerate(stars):
        for d in s: holders[d].append(k)
    loose={k:[d for d in s if len(holders[d])==1] for k,s in enumerate(stars)}
    if not any(loose.values()): return dict(status='no live knot')
    end=EO.from_stars(stars)
    groups=EO.proposals(end)                     # recorded group rule
    used=collections.Counter(v for g in groups for v in g)
    short={k:used[k]-n for k,n in end.opens.items() if used[k]>n}
    left={k:len(loose[k]) for k in end.opens}    # loose distinctions not yet handed out
    paid=collections.defaultdict(set); payments=0; paid_births=0; unpaid=0
    for g in groups:
        took_shared=False
        for p in g:
            if left[p]>0: left[p]-=1; continue
            cands=sorted(d for d in stars[p] if len(holders[d])>=2 and d not in paid[p]
                         and not any(q in g and q!=p for q in holders[d]))
            if not cands: unpaid+=1; continue
            d=cands[0] if conv=='O' else cands[-1]
            paid[p].add(d); payments+=1; took_shared=True
        paid_births+=took_shared
    births=len(groups)+sum(left.values())
    return dict(status='residual' if unpaid else 'round', short=len(short), payments=payments, paid_births=paid_births, births=births, unpaid=unpaid)
if __name__=='__main__':
    # Run from the repository root: .venv/bin/python -B research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks/rule_r_round_one.py
    draws=list(lib.p3_draws())
    rec={}
    for f in sorted(glob.glob(A+'c_*_arm*.jsonl')):
        for l in open(f):
            r=json.loads(l); rec[(r['law'],r['conv'],r['arm'],r['draw'])]=r
    tot=collections.Counter()
    for conv in 'ON':
        for dr in draws:
            m=round1(dr['stars'],conv)
            for law in ('parity','nae'):
                r=rec[(law,conv,dr['arm'],dr['draw'])]
                if m['status']=='no live knot':
                    ok=r['rounds']==0 and r['outcome']=='closed'; tot[(conv,law,'no live knot')]+=1
                elif m['status']=='residual':
                    ok=r['outcome']=='residual_stall' and r['rounds']==0 and sum(n for _,n in (r['residual'] or []))==m['unpaid']
                    tot[(conv,law,'residual stall at round 1')]+=1
                else:
                    ok=(r['rounds']>=1 and r['births'][0]==m['births'] and r['short_knots'][0]==m['short']
                        and r['payments'][0]==m['payments'] and r['paid_births'][0]==m['paid_births'])
                    if r['rounds']==0: ok=r['outcome']=='cap'
                    tot[(conv,law,'round made')]+=1; tot[(conv,law,'with a short knot')]+=m['short']>0; tot[(conv,law,'payments')]+=m['payments']
                tot[(conv,law,'agree with the study')]+=bool(ok)
    for k,n in sorted(tot.items()): print(k,n)
    # the two set-ups of the whole-stage-settings study
    sys.path.insert(0, glob.glob('experiments/WHOLE-STAGE-SETTINGS-20261120-001B/*/')[0])
    import edits
    preps={p.name:p for p in edits.built_cases()}
    p=preps['S_cycle_five']
    for s in ((0,0),(0,1),(1,0),(1,1)):
        st=p.edited(s); turn=EO.step(EO.from_stars(st),'nae')
        print('two-sided stall, settings',s,'| ordinary:',turn.status,'| rule R (O, N):',[(x['status'],x['short'],x['payments'],x['births']) for x in (round1(st,c) for c in 'ON')])
    p=preps['C_binary']
    for s in ((0,0),(0,1),(1,0),(1,1)):
        st=p.edited(s); t=EO.step(EO.from_stars(st),'parity')
        print('parity closing, settings',s,'| ordinary:',t.status,'parents',t.parents,'fresh',t.fresh,'implied',t.implied,'| short knots under R:',round1(st,'O').get('short'))
