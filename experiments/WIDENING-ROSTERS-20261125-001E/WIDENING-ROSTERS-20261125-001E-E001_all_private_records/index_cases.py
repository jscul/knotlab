"""List every actual physical candidate before calculating any allowed states."""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path


def packing(value):
    return json.dumps(value,separators=(',',':')).encode()


def read_stream(path, expected):
    with gzip.open(path,'rb') as f:
        data=f.read()
    assert sha256(data).hexdigest()==expected
    return [json.loads(line) for line in data.splitlines()]


def build(manifest,primary,output):
    systems=output/'systems'
    systems.mkdir(parents=True,exist_ok=True)
    requests={}
    cases={}
    for line in manifest.read_text().splitlines():
        trajectory=json.loads(line)
        case,law=trajectory['case'],trajectory['kl']
        stages=read_stream(primary/trajectory['support_file'],trajectory['support_sha256'])
        events=read_stream(primary/trajectory['events_file'],trajectory['events_sha256'])
        prefixes={}; tally=Counter(); marks=Counter()
        for event in events:
            t=event['t']
            for route in event['routes']:
                if not route['contacts']:
                    tally['different arms']+=1
                for c in route['contacts']:
                    if t not in prefixes:
                        supports=[row for stage in stages[:t+1] for row in stage['supports']]
                        material=packing(supports)
                        digest=sha256(material).hexdigest()
                        target=systems/(digest+'.json.gz')
                        if not target.exists(): target.write_bytes(gzip.compress(material,mtime=0))
                        prefixes[t]=digest,supports
                    digest,supports=prefixes[t]
                    u,v=route['u'],route['v']
                    origin='start-held' if c<stages[0]['distinctions'] else 'made'
                    assert c in supports[u] and c in supports[v] and c in supports[route['w']]
                    left=set(supports[u])-set(supports[v]);right=set(supports[v])-set(supports[u])
                    width=len(left)+len(right)+1
                    tally['occurrences']+=1; tally['literal rows']+=len(left)*len(right)
                    a,b=sorted((u,v))
                    key=law,digest,a,b,c
                    if key not in requests:
                        requests[key]=dict(law=law,system=digest,u=a,v=b,c=c,width=width,knots=len(supports),example=[case,event['s'],t,event['X'],event['Y'],route['route'],route['w'],u,v,c],count=0)
                    requests[key]['count']+=1
                    marks[f"{route['route']}/{origin}"]+=1
        cases[f'{case}/{law}']=dict(tallies=tally,kinds=marks)
    data=sorted(requests.values(),key=lambda r:(r['law'],r['system'],r['u'],r['v'],r['c']))
    (output/'requests.jsonl').write_bytes(b''.join(packing(r)+b'\n' for r in data))
    (output/'coverage.json').write_text(json.dumps(cases,indent=1,sort_keys=True)+'\n')
    print('resource inventory',len(data),'distinct physical problems,',dict(sorted(Counter(r['width'] for r in data).items())),'width histogram')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ('manifest','primary','output'):parser.add_argument(name,type=Path)
    build(**vars(parser.parse_args()))
