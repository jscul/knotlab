"""Compare every whole-record verdict and its physical occurrence count."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys


def compare(folder):
    result={}
    for line in (folder/'primary/results.jsonl').read_text().splitlines():
        receipt=json.loads(line); assert receipt['status']=='ok'
        stage=receipt['result']
        for u,v,c,outcome,n in stage['rows']:
            key=stage['law'],stage['system'],u,v,c
            assert key not in result
            result[key]=(outcome,n)
    out=Counter();weighted=Counter();widths=Counter()
    with gzip.open(folder/'referee/records.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);key=tuple(r[k] for k in ('law','system','u','v','c'))
            assert result.pop(key)==(r['outcome'],r['count'])
            assert r['coherent'] and r['c_open']
            out[(r['law'],r['outcome'])]+=1;weighted[(r['law'],r['outcome'])]+=r['count'];widths[r['width']]+=1
    assert not result
    return dict(experiment_id='WIDENING-ROSTERS-20261125-001E-E001',status='PASS',errors=[],checked=[dict(law=law,outcome=o,unique=n,occurrences=weighted[law,o]) for (law,o),n in sorted(out.items())],width_min=min(widths),width_max=max(widths),bindings={str(p.relative_to(folder)):sha256(p.read_bytes()).hexdigest() for p in (folder/'primary/results.jsonl',folder/'referee/records.jsonl.gz',folder/'referee/population.json',folder/'requests.jsonl')})


if __name__=='__main__':
    print(json.dumps(compare(Path(sys.argv[1])),indent=2))
