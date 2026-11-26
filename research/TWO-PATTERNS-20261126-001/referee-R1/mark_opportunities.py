"""Count mark depth and exposure from the closed record. Rebuild missing census
comparison lengths only through round seven. No study modules are imported."""
import argparse
from collections import Counter, defaultdict, deque
from functools import lru_cache
import gzip
import itertools
import json
from pathlib import Path
import random
import subprocess
from time import monotonic

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
BENCH = {
    'ring': ([3]*5, [(0,1),(1,2),(2,3),(3,4),(0,4)], 0),
    'copier': ([2,2], [(0,1)], 0),
    'source': ([3,0,3,3,3,2,2], [(0,1),(0,4),(1,4),(2,4),(2,6),(3,4),(3,5),(5,6)], 0),
}
CENSUS = {1: [], 3: [(0,1)], 6: [(0,1),(0,2)], 7: [(0,1),(0,2),(1,2)]}
RATIONS = ['ORD','CAP-3','FLOOR1']
SHORT = ['CANCEL-WAIT','CANCEL-RETIRE','CANCEL-OFFSHOOT']
SOURCES = [('bench','bench_runs'),('bench','bench_take_marks'),('bench','bench_owing'),('census','census_runs')]

@lru_cache(None)
def part(name):
    if name in BENCH:
        return BENCH[name]
    family,rest=name.split(':')
    loose,site=rest.split('@')
    return list(map(int,loose)),CENSUS[int(family[1:])],int(site)

def joined(a,b,steps,join):
    ha,ea,ia=part(a)
    hb,eb,ib=part(b)
    n=len(ha)
    loose=ha+hb
    pairs=ea+[(n+u,n+v) for u,v in eb]
    sites=[ia]
    for _ in range(steps-1):
        sites.append(len(loose))
        loose.append(0 if join=='meeting' else 1)
    sites.append(n+ib)
    for start,end in zip(sites,sites[1:]):
        if join=='meeting':
            spent=len(loose)
            loose.append(0)
            pairs.extend([(start,spent),(end,spent)])
            loose[start]+=1
            loose[end]+=1
        else:
            pairs.append((start,end))
    return loose,pairs

def distances(adj,sources):
    seen=dict.fromkeys(sources,0)
    queue=deque(seen)
    while queue:
        u=queue.popleft()
        for v in adj[u]:
            if v not in seen:
                seen[v]=seen[u]+1
                queue.append(v)
    return seen

@lru_cache(None)
def depths(a,b,steps,join,receiver,index):
    loose,pairs=joined(a,b,steps,join)
    n=len(part(a)[0])
    m=len(part(b)[0])
    mark=n+index if receiver=='A' else index
    sources=range(n) if receiver=='A' else range(n,n+m)
    live_sources=[u for u in sources if loose[u]]
    loose[mark]+=1
    meetings=[set() for _ in loose]
    for u,v in pairs:
        meetings[u].add(v)
        meetings[v].add(u)
    # One witnessed step has a common third knot, which may itself be spent.
    # Measure on the marked end; it is the union of the two ends if a mark
    # awakens a previously spent knot. Infinity is reported separately.
    witnessed=[set() for _ in loose]
    for neighbours in meetings:
        for u,v in itertools.combinations((x for x in neighbours if loose[x]),2):
            witnessed[u].add(v)
            witnessed[v].add(u)
    other=b if receiver=='A' else a
    _,es,site=part(other)
    local=[set() for _ in part(other)[0]]
    for u,v in es:
        local[u].add(v); local[v].add(u)
    nominal=steps+distances(local,[site])[index]
    return distances(witnessed,live_sources).get(mark),nominal

@lru_cache(None)
def normalize(name,mark):
    loose,edges,site=part(name)
    h=list(loose)
    if mark is not None:
        h[mark]+=1
    edge_set={tuple(sorted(e)) for e in edges}
    choices=[]
    for order in itertools.permutations(range(len(h))):
        if {tuple(sorted((order[u],order[v]))) for u,v in edges}==edge_set:
            choices.append((tuple(h[v] for v in order), order.index(site)))
    funds,s=min(choices)
    return funds,tuple(edges),s

def signature(a,b,join,ration,treat,marked=None,index=None):
    s,t=sorted([normalize(a,index if marked=='A' else None),
                normalize(b,index if marked=='B' else None)])
    # Without taking, the extra shared distinction on the second side of a
    # meeting only repeats an existing meeting with the spent knot.
    return s,t,join,ration,treat

def to_job(sig):
    (ah,ae,ia),(bh,be,ib),join,r,t=sig
    n=len(ah)
    h=list(ah+bh); pairs=list(ae)+[(u+n,v+n) for u,v in be]
    if join=='meeting':
        pairs.extend([(ia,len(h)),(ib+n,len(h))])
        h[ia]+=1; h[ib+n]+=1; h.append(0)
    else:
        pairs.append((ia,ib+n))
    return ' '.join(map(str,[RATIONS.index(r),SHORT.index(t),len(h),len(pairs),
                             *h,*itertools.chain.from_iterable(pairs)]))

def load_rows(cap=None):
    tables={}
    for family,source in SOURCES:
        with gzip.open(STUDY/family/(source+'.jsonl.gz'),'rt') as f:
            seq=(json.loads(line) for line in f)
            tables[source]=[row for row in itertools.islice(seq,cap) if 'reads' in row]
    return tables

def census_jobs(rows):
    all_jobs=set()
    for r in rows:
        a,b,j,x,t=r['A'],r['B'],r['join'],*r['law']
        all_jobs.add(signature(a,b,j,x,t))
        for receiver,other in [('A','B'),('B','A')]:
            for idx in range(len(r['reads'][receiver]['marks'])):
                all_jobs.add(signature(a,b,j,x,t,other,idx))
    return sorted(all_jobs)

def validate_sample(replay):
    with (HERE/'regrow_full.json').open() as f:
        cases=[r for r in json.load(f)['results'] if r['archive']=='census']
    comparisons=0
    for r in cases:
        a,b=r['A'],r['B']
        args=(a,b,r['join'],*r['law'])
        baseline=len(replay[signature(*args)])
        actual=Counter()
        for sender in ('A','B'):
            for mark in range(len(part(r[sender])[0])):
                actual[min(baseline,len(replay[signature(*args,sender,mark)]))]+=1
        expected=Counter()
        for n,count in r['common_rounds_by_comparison']['own mark'].items():
            expected[min(7,int(n))]+=count
        assert actual==expected, (args,actual,expected)
        comparisons+=sum(actual.values())
    return {'census archive rows':len(cases),'marked comparison lengths checked against full growth':comparisons}

def run_jobs(jobs,exe):
    start=monotonic()
    run=subprocess.run([str(exe)],input=''.join(to_job(s)+'\n' for s in jobs),
                       capture_output=True,text=True,check=True)
    data={}
    for sig,line in zip(jobs,run.stdout.splitlines(),strict=True):
        counts=list(map(int,line.split()))
        assert len(counts)==7 or counts[-1]>1500, (sig,counts)
        data[sig]=counts
    return data,round(monotonic()-start,3)

def opportunities(tables,replay):
    out={}
    for source,rows in tables.items():
        census=source=='census_runs'
        counts=Counter(); hist=defaultdict(Counter); example={}; latest=None
        for r in rows:
            a,b,j,t=r['A'],r['B'],r['join'],r.get('steps',1)
            rounds=r['rounds' if census else 'rounds read']
            flags=set()
            if census:
                common_args=(a,b,j,*r['law'])
                unmarked=replay[signature(*common_args)]
                assert len(unmarked)==min(7,rounds)
                start_size=len(part(a)[0])+len(part(b)[0])+int(j=='meeting')
                expected=list(itertools.accumulate(
                    (x+y+z for x,y,z in zip(r['reads']['A']['own births'],r['reads']['B']['own births'],r['joint'],strict=True)),
                    initial=start_size))[1:8]
                assert unmarked==expected, (r['i'],r['j'],r['law'],r['join'],unmarked,expected)
                if rounds<=7: assert unmarked[-1]==r['knots']
            for receiver,other in [('A','B'),('B','A')]:
                rd=r['reads'][receiver]
                if census:
                    marks=[(i,own,joint,len(replay[signature(*common_args,other,i)]))
                           for i,(own,joint) in enumerate(rd['marks'])]
                else:
                    marks=[(int(i),m['own making first differs'],m['joint descent first differs'],m['rounds compared'])
                           for i,m in rd.get('mark at a start knot of the other',{}).items()]
                for i,own,joint,m in marks:
                    comp=min(rounds,m)
                    hist['common comparison length capped at seven'][str(min(comp,7))]+=1
                    d,nom=depths(a,b,t,j,receiver,i)
                    group='unreachable' if d is None else str(d)
                    hist['witnessed step count'][group]+=1
                    hist['nominal joins plus internal sharings'][str(nom)]+=1
                    if own is None or own>6:
                        if comp>=7:
                            hist['unheard through six with a seventh comparison by witnessed steps'][group]+=1
                    hist['witnessed steps and own first hearing'][f'{group}, {own}']+=1
                    hist['witnessed steps and joint first hearing'][f'{group}, {joint}']+=1
                    counts['marks']+=1; flags.add('marked')
                    if rounds>=7: flags.add('unmarked through seven')
                    if comp>=7:
                        counts['mark comparisons through seven']+=1
                        flags.add('some mark through seven')
                    if own is None or own>6:
                        counts['marks not heard by six in recorded window']+=1
                        if comp>=7:
                            counts['unheard through six with a seventh comparison']+=1
                            flags.add('some unheard mark with a seventh comparison')
                            if d is not None:
                                counts['such marks initially reachable by witnessed steps']+=1
                                flags.add('such a reachable mark')
                            if d is not None and d>6:
                                counts['such marks needing over six witnessed steps']+=1
                                flags.add('such a distant mark')
                    if own is not None and (d is None or own>d):
                        counts['own first hearing later than witnessed depth or initially unreachable']+=1
                        if d is not None:
                            counts['own first hearing later than finite witnessed depth']+=1
                            if latest is None or own-d>latest:
                                latest=own-d
                                example={'a':a,'b':b,'case law':r['law'],'join':j,'steps':t,
                                         'receiver':receiver,'other mark index':i,'witnessed steps':d,'round':own}
            for flag in flags:
                counts['cases: '+flag]+=1
        out[source]={'totals':counts,'histograms':hist,'delay example':example}
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--pilot',action='store_true')
    ap.add_argument('--exe',type=Path,default=HERE/'horizon_run')
    args=ap.parse_args()
    tables=load_rows()
    jobs=census_jobs(tables['census_runs'])
    if args.pilot:
        subset=random.Random(261126).sample(jobs,128)
        _,elapsed=run_jobs(subset,args.exe)
        print(json.dumps({'seed':261126,'size':len(jobs),'pilot':len(subset),'seconds':elapsed,
                          'full estimate seconds':round(elapsed*len(jobs)/len(subset),1)}))
    else:
        replay,elapsed=run_jobs(jobs,args.exe)
        results=opportunities(tables,replay)
        results['census horizon reconstruction']={'unique inputs':len(jobs),'seconds':elapsed,
            'independent sample cross-check':validate_sample(replay),
            'checked unmarked horizons (truncated at seven)':len(tables['census_runs']),
            'unmarked knot totals checked round by round':sum(min(7,r['rounds']) for r in tables['census_runs']),
            'counts at final round checked when original ended by seven':sum(r['rounds']<=7 for r in tables['census_runs'])}
        (HERE/'mark_opportunities.json').write_text(json.dumps(results,sort_keys=True,indent=2)+'\n')
