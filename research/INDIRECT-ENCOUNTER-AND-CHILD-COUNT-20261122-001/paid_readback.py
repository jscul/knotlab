"""Read the enrolled member and all its children from actual holdings alone.

Only old founder roles are supplied. Reconstruct all positive-age parent sets
using physical distinctions, without the experiment's birth log or family tags.
"""
from collections import defaultdict
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = next((ROOT/'artifacts'/(HERE.name+'B')).glob('*/physical_replay.json.gz'))


def bit(word, mark):
    return word[str(mark)]


def read(arm, wanted_count):
    levels = arm['levels']
    births = []
    parents = {}
    for old, new in zip(levels, levels[1:]):
        holders = defaultdict(list)
        for i,holding in enumerate(old['holdings']):
            for m in holding:
                holders[m].append(i)
        cohort = range(len(old['holdings']), len(new['holdings']))
        births.append(cohort)
        assert new['holdings'][:len(old['holdings'])] == old['holdings']
        for c in cohort:
            paid = [m for m in new['holdings'][c] if m in holders]
            assert all(len(holders[m]) == 1 for m in paid)
            payers = [holders[m][0] for m in paid]
            assert len(payers) == len(set(payers)) >= 1
            parents[c] = frozenset(payers)
    named = {name:i for i,name in enumerate(levels[0]['roles'])}
    def by_parents(cut, names):
        pset = {named[n] for n in names}
        choices = [c for c in births[cut-1] if parents[c]==pset]
        assert len(choices)==1, (names,choices)
        return choices[0]
    for name in ('W','P1','P2','P3','D1','D2','Da'):
        anchor = named['anchor-'+name]
        cs = [v for v in births[0] if anchor in parents[v]]
        assert len(cs) == 1
        named[name] = cs[0]
    for label,payer in (('Z','p5'),('D3','p6'),('Zs','p7')):
        named[label]=by_parents(1,[payer])
    for label,roles in {'A':['P1','P2','W'],'B':['W','Z'],'T':['Z'],
                        'X':['D1','D2','W'],'V1':['P1','D1']}.items():
        named[label]=by_parents(2,roles)
    v2s = [c for c in births[1] if parents[c] in
           ({named['P2'],named['D2']},{named['P2'],named['Da']})]
    assert len(v2s)==1
    named['V2']=v2s[0]
    receiver = {named[k] for k in ('A','B','T')}
    donor = {named[k] for k in ('D2','D3')}
    g=by_parents(3,['A','B'])
    income = parents[named['X']] & parents[named['V2']]
    assert income == ({named['D2']} if wanted_count==2 else set())
    holdings = levels[3]['holdings']
    result = []
    for c in births[3]:
        if g not in parents[c]:
            continue
        marks=set(holdings[g]) & set(levels[4]['holdings'][c])
        assert len(marks)==1
        result.append([len(parents[c]),next(iter(marks))])
    assert len(result)==len({m for _,m in result})==wanted_count
    def pure(cohort, family): return {c for c in cohort if parents[c] <= family}
    # Record the actual ancestry into the known pure family, including the focal
    # member itself to preclude a separate, unrelated surviving branch.
    certificates=[]
    gline=set()
    for age in range(2,len(births)+1):
        cohort=births[age-1]
        donor=pure(cohort,donor)
        if age>2:
            receiver=pure(cohort,receiver)
        if age==3: gline={g}
        elif age>3: gline={c for c in receiver if parents[c]&gline}
        certificates.append([age,len(receiver),len(donor),len(gline)])
        assert donor and receiver and (age<3 or gline)
    valued_launch = {k:[(m,bit(levels[t]['word'],m)) for m in sorted(levels[t]['holdings'][named[k]])]
                     for k,t in [('A',2),('B',2),('T',2),('D2',1),('D3',1)]}
    return dict(child_arities_and_G_payments=sorted(result), shared_older_payers_of_X_and_V2=int(bool(income)),
                family_counts_age_receiver_donor_focal=certificates, valued_launch=valued_launch)


def main():
    with gzip.open(RAW,'rt') as f: raw=json.load(f)
    checks={}
    for law, histories in raw['preparations'].items():
        checks[law]={}
        for label, history in histories.items():
            if label not in ('present','diverted','restored','swapped_D2'):
                continue
            checks[law][label]=read(history,3 if label=='diverted' else 2)
        baseline=checks[law]['present']['valued_launch']
        assert all(v['valued_launch']==baseline for v in checks[law].values())
    path=HERE/'paid_readback.json'
    path.write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
    print('Enrolled by physical payments and re-read',sum(map(len,checks.values())),'matched histories.')


if __name__ == '__main__':
    main()
