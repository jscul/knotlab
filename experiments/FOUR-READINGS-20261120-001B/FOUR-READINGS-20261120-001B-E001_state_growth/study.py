"""Exhaust small named starts, substantiate model arguments and repeat weighted controls."""
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement, permutations, product
from fractions import Fraction
import json
from pathlib import Path
from random import Random
import subprocess
import sys
import os

from model import (accepts, add, allowed, bits, build, growth, literal_counts, mask_of,
                   nae_counts, nae_lawful, ownership, parity_counts, parity_local, reduced, width)
from pair_tables import OUT

ROOT = Path(__file__).resolve().parents[3]


def connected(holdings):
    remaining = list(holdings[1:])
    visited = holdings[0]
    while True:
        rest = []
        for row in remaining:
            if row & visited:
                visited |= row
            else:
                rest.append(row)
        if len(rest) == len(remaining):
            return not rest
        remaining = rest


def census_size(n):
    labels = (1 << n)-1
    candidates = tuple(s for s in range(1,labels+1) if s.bit_count()>=3)
    perms = []
    for p in permutations(range(n)):
        perms.append(tuple(mask_of(p[i] for i in bits(s)) for s in range(labels+1)))
    relations = {}
    views = defaultdict(lambda: defaultdict(lambda: [set(),set()]))
    populations = Counter()
    raw_admitted = 0
    for k in range(1,2*n//3+1):
        for holdings in combinations_with_replacement(candidates,k):
            if any(sum(bool(x & 1<<i) for x in holdings) not in (1,2) for i in range(n)):
                continue
            if not connected(holdings):
                continue
            raw_admitted += 1
            rows = tuple(tuple(bits(x)) for x in holdings)
            for law in ('nae','parity'):
                words = allowed(rows,law)
                if any(len({s & x for s in words}) !=
                       ((1 << x.bit_count())-2 if law=='nae' else 1 << (x.bit_count()-1)) for x in holdings):
                    continue
                key = mask_of(words)
                if key not in relations:
                    recoded = tuple(mask_of(p[s] for s in words) for p in perms)
                    smallest = min(recoded)
                    relations[key] = (smallest, tuple(i for i,v in enumerate(recoded) if v == smallest))
                orbit, transports = relations[key]
                status,births = growth(rows,law)
                for family in ('all','distinct_support'):
                    if family=='distinct_support' and len(set(holdings))!=k:
                        continue
                    populations[law,family] += 1
                    def signature(p):
                        return (status, tuple(sorted((tuple(sorted(p[holdings[h]] for h in parents)),fresh)
                                                     for parents,fresh in births)))
                    viewed = views[law,family,'named'][key]
                    viewed[0].add(holdings)
                    viewed[1].add(signature(perms[0]))
                    viewed = views[law,family,'renamed'][orbit]
                    changes = [perms[i] for i in transports]
                    viewed[0].add(min(tuple(sorted(p[x] for x in holdings)) for p in changes))
                    viewed[1].add(min(signature(p) for p in changes))
    summaries = {}
    for (law,family,matching),v in sorted(views.items()):
        summaries[f'{law}_{family}_{matching}'] = {
            'presentations':sum(len(p) for p,_ in v.values()),'state_classes':len(v),
            'state_classes_with_different_holdings':sum(len(p)>1 for p,_ in v.values()),
            'state_classes_with_different_first_growth':sum(len(g)>1 for _,g in v.values()),
            'max_holdings_per_class':max(len(p) for p,_ in v.values()),
            'max_growths_per_class':max(len(g) for _,g in v.values())}
    return {'named_connected_syntactic':raw_admitted,'counts':summaries}


def duplicate_controls():
    one = ((0,1,2),)
    four = ((0,1,2),(0,3,4),(1,5,6),(2,7,8))
    result = {}
    for label,left,right in [('three',one,one*2),('extra_six',four,(*four,(3,4,5,6,7,8)))]:
        by_law = {}
        for law in ('parity','nae'):
            words = allowed(left,law)
            assert words==allowed(right,law)
            details = []
            for rows in (left,right):
                form = tuple(map(mask_of,rows))
                projections = [len({x & row for x in words}) for row in form]
                assert projections == [((1 << r.bit_count())-2 if law=='nae' else 1 << (r.bit_count()-1))
                                       for r in form]
                status,births = growth(rows,law)
                details.append({'rows':rows,'projections':projections,'terminal':status,'births':births})
            assert details[0]['terminal']=='births' and details[1]['terminal']=='closed'
            by_law[law] = {'solutions':len(words),'arms':details,
                           'disagreements':list(literal_counts(words,width(left))[1].values())}
        result[label] = by_law
    return result


def canonical_gate():
    results = []
    for n,law in product((3,6),('parity','nae')):
        names = [f'x{i}' for i in range(n)]
        rule = []
        for s in range(1 << n):
            if accepts([tuple(range(n))],s,law):
                continue
            rule.append(' '.join(('~' if s >> i & 1 else '') + name for i,name in enumerate(names)))
        cmd = [sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(rule),
               '--loops',*names[:-1],'--contact',names[-1],'--json']
        env = {**os.environ,'PYTHONPATH':str(ROOT/'tools')}
        work = subprocess.run(cmd,env=env,text=True,check=True,capture_output=True)
        j = json.loads(work.stdout)
        assert j['is_knot'] and j['coexistence'] and j['invisible_in_parts'] and j['binding']
        results.append({'width':n,'law':law,'allowed':len(j['allowed']),'K1':j['binding'],
                        'K2':j['invisible_in_parts'],'K3':j['coexistence']})
    return results


def switch_family(r):
    """Each named leaf has two disjoint possible numbers of children."""
    counts = [(r+2*i,r+2*i+1) for i in range(r)]
    # Each input leaf has its own physical names, held by S or by the bookkeeping exterior.
    base_rows, blocks = [], []
    offset = 0
    for a,b in counts:
        left = tuple(range(offset,offset+a))
        right = tuple(range(offset+a,offset+a+b))
        blocks.append((left,right))
        base_rows.append((*left,*right))
        offset += a+b
    base = None
    family = []
    for switch in product((0,1),repeat=r):
        common = tuple(v for i,idx in enumerate(switch) for v in blocks[i][idx])
        rows = (common,*base_rows)
        assert parity_local(rows)==[1]*len(rows)
        basis = reduced(map(mask_of,rows))
        if base is None:
            base = basis
        assert basis==base
        status,births = growth(rows,'parity')
        assert status=='births'
        actual = Counter(h for ps,_ in births for h in ps)
        counts_expected = tuple(len(blocks[i][1-idx]) for i,idx in enumerate(switch))
        assert tuple(actual[i+1] for i in range(r))==counts_expected
        family.append(tuple(sorted(actual.values())))
    assert len(set(family))==len(family)
    return {'leaves':r,'distinctions':offset,'presentations':len(family),
            'distinct_name_free_first_growth_histories':len(set(family)),
            'common_relation_rank':len(base),'bits_lower_bound':r}


def tree(rng,n):
    # Uniform Prüfer sequence. Draw the Bernoulli opening after choosing the tree.
    seq = [rng.randrange(n) for _ in range(n-2)]
    degree = Counter(seq)
    joins = []
    for x in seq:
        leaf = next(i for i in range(n) if degree[i]==0)
        joins.append((leaf,x))
        degree[leaf] = -1
        degree[x] -= 1
    joins.append(tuple(i for i in range(n) if degree[i]==0))
    deg = Counter(i for p in joins for i in p)
    return build(joins,[max(0,3-deg[i])+int(rng.randrange(4)==0) for i in range(n)])


def observation(rows, rng):
    raw = parity_local(rows)
    check = {'parity':all(x==1 and len(row)>=3 for x,row in zip(raw,rows)),
             'nae':all(len(row)>=3 for row in rows) and nae_lawful(rows)}
    live = sorted({v[0] for v in ownership(rows).values() if len(v)==1})
    if not any(check.values()) or len(live)<2:
        return {'lawful':check,'marked':False}
    sender,receiver = rng.sample(live,2)
    edited = add(rows,{sender})
    pairs = tuple(combinations(sorted(rows[receiver]),2))
    tests = {}
    for law,reader in [('parity',parity_counts),('nae',nae_counts)]:
        if not check[law]:
            continue
        assert all(x==1 for x in parity_local(edited)) if law=='parity' else nae_lawful(edited)
        m,d = reader(rows)
        n,e = reader(edited)
        assert all(n*d[ij]==m*e[ij] for ij in pairs)==all(
            Fraction(d[ij],m)==Fraction(e[ij],n) for ij in pairs)
        old_status,old_births = growth(rows,law)
        new_status,new_births = growth(edited,law)
        tests[law] = {'solutions':[m,n],'status':[old_status,new_status],
                      'births':[len(old_births),len(new_births)],
                      'receiver_pairs':len(pairs),'raw_changed':sum(d[ij]!=e[ij] for ij in pairs),
                      'rate_changed':sum(n*d[ij]!=m*e[ij] for ij in pairs)}
    return {'lawful':check,'marked':True,'sender':sender,'receiver':receiver,'tests':tests}


def sample_panel():
    # Draw all independent tree shapes and Bernoulli openings before drawing marks.
    rng = Random(20261120207)
    trees = [(f'{n}-{i}', tree(rng,n)) for n in [4,5,6] for i in range(32)]
    archive = ROOT/'artifacts/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/explosive.json'
    selected = json.loads(archive.read_text())['catalogue']
    panels = {'uniform_trees':{},'explosive_archive':{}}
    for label,rows in trees:
        panels['uniform_trees'][label] = observation(rows,rng)
    for label,record in selected.items():
        q = observation(tuple(map(tuple,record['source'])),rng)
        assert q['lawful'] == {law:r['lawful'] for law,r in record['source_gate'].items()}
        panels['explosive_archive'][label] = q
    summary = {}
    for panel, records in panels.items():
        for law in ('parity','nae'):
            tests = [r['tests'][law] for r in records.values() if r['marked'] and law in r['tests']]
            summary[f'{panel}_{law}'] = {'draws':len(records),'lawful':sum(r['lawful'][law] for r in records.values()),
                'marked':len(tests),'original_funded':sum(t['status'][0]=='births' for t in tests),
                'edited_funded':sum(t['status'][1]=='births' for t in tests),
                'receiver_rates_changed_starts':sum(t['rate_changed']>0 for t in tests),
                'receiver_pair_denominator':sum(t['receiver_pairs'] for t in tests),
                'receiver_rates_changed_pairs':sum(t['rate_changed'] for t in tests),
                'receiver_raw_changed_pairs':sum(t['raw_changed'] for t in tests)}
    return {'summary':summary,'records':panels}


def main():
    results = {'canonical_gate':canonical_gate(),'duplicate_and_distinct_controls':duplicate_controls(),
               'census':{n:census_size(n) for n in [3,4,5]},
               'unbounded_family':[switch_family(r) for r in [3,4,5,6]],'samples':sample_panel()}
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'study.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results['samples']['summary']))


if __name__=='__main__':
    main()
