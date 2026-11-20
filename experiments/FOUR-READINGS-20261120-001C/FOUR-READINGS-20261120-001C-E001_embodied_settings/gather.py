"""Collect completed census shards, independently score every leading example."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import json
from pathlib import Path
from observables import OUTPUT, WORDS, freeze, measure, prior_score_check, put


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('run_dir',type=Path)
    args=parser.parse_args()
    freeze()
    rows=[json.loads(line) for line in (args.run_dir/'results.jsonl').read_text().splitlines()]
    assert all(row['status']=='ok' for row in rows)
    shards={row['case']:row['result'] for row in rows}
    expected={f'{n:02d}-{k}' for n in range(3,11) for k in range(1,2*n//3+1)}
    assert set(shards)==expected
    summary={"structural":{},"by_size":{},"laws":{},"validated_peak_examples":0}
    body={}
    for key,s in sorted(shards.items()):
        structural=(s['presentations'],s['multiple_meetings'],s['duplicate_displays'])
        for target in (summary['structural'],summary['by_size'].setdefault(s['n'],{}).setdefault('structural',{})):
            for i,field in enumerate(('presentations','multiple_meetings','duplicate_displays')):
                target[field]=target.get(field,0)+structural[i]
        for law,e in s['laws'].items():
            raw=e.pop('raw')
            body[key,law]=raw
            for t in (summary['laws'].setdefault(law,{}),summary['by_size'][s['n']].setdefault(law,{})):
                for field,v in e.items():
                    if field not in ('peaks','bands'): t[field]=t.get(field,0)+v
                for band, br in e['bands'].items():
                    b=t.setdefault('bands',{}).setdefault(band,{'orders':0,'hidden':0,'complete':0,'peaks':{}})
                    for f in ('orders','hidden','complete'): b[f]+=br[f]
                    for level,value in br['peaks'].items():
                        if level not in b['peaks'] or Fraction(value)>Fraction(b['peaks'][level]):
                            b['peaks'][level]=value
                peaks=t.setdefault('peaks',{})
                for level,p in e['peaks'].items():
                    v=Fraction(p['score'])
                    if level in peaks and v<Fraction(peaks[level]['score']): continue
                    if level in peaks and v==Fraction(peaks[level]['score']):
                        peaks[level]['tied_orders']+=p['tied_orders']
                        continue
                    data=raw[p['histogram']]
                    old=data['marks']; l,r=p['orders']
                    marks=[old[i] for i in l]+[old[3+i] for i in r]
                    peaks[level]={**p,'shard':key,'marks':marks,'supports':data['supports'],'reader_holders':data['holders']}
            for level,p in e['peaks'].items():
                counts=list(map(int,p['histogram'].split(',')))
                l,r=p['orders']
                old=dict(zip(WORDS,counts))
                hist={tuple([w[i] for i in l]+[w[3+i] for i in r]):v for w,v in old.items()}
                h=[hist[w] for w in WORDS]
                arm,read=level.split('_')
                stats=measure(h,embodied=arm!='external')
                assert stats[read]['maximum']==p['score']
                assert arm!='hidden' or stats['full_hidden']
                summary['validated_peak_examples']+=1
    # Independently re-run the inherited scorer on the global leading placements.
    for law,e in summary['laws'].items():
        for key,p in e['peaks'].items():
            supp,marks=p['supports'],p['marks']
            n=1+max(max(x) for x in supp)
            hist=Counter()
            for i in range(1<<n):
                w=tuple((i>>j)&1 for j in range(n))
                vals=[sum(w[j] for j in row) for row in supp]
                if any((s%2 if law=='parity' else (s==0 or s==len(row))) for s,row in zip(vals,supp)):
                    continue
                hist[tuple(w[j] for j in marks)]+=1
            h=[hist[w] for w in WORDS]
            obs={"external":measure(h,False),"embodied":measure(h)}
            assert prior_score_check(h,obs)
            arm,read=key.split('_')
            assert obs['external' if arm=='external' else 'embodied'][read]['maximum']==p['score']
            p['mark_histogram']=h
            p.pop('histogram')
    raw={f'{key}-{law}':hist for (key,law),hist in body.items()}
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'census_tables.json.gz').write_bytes(gzip.compress(json.dumps(raw,separators=(',',':')).encode(),mtime=0))
    put('census_summary.json',summary)
    for law,e in summary['laws'].items():
        print(law,{key:v['score'] for key,v in e['peaks'].items()})
if __name__=='__main__':
    main()
