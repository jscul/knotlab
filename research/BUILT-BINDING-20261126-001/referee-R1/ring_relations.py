"""Check the actual projected ring tables for every possible contact."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def verify(image, n):
    names=[f'x{j}' for j in range(n)]
    clauses=[' '.join(('~' if v>>j&1 else '')+x for j,x in enumerate(names))
             for v in range(1<<n) if v not in image]
    results=[]
    for c in names:
        result=subprocess.run([sys.executable,'-B','-m','knotlab','check',
                               '--cnf','; '.join(clauses),'--contact',c,'--loops',
                               *[x for x in names if x!=c],'--json'],
                              cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'tools')),
                              text=True,capture_output=True,check=True)
        check=json.loads(result.stdout)
        assert check['is_knot']
        results.append(check)
    return results


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pilot',action='store_true')
    args=ap.parse_args()
    start=time.monotonic()
    data=json.loads((HERE/'ring_counts.json').read_text())
    groups=Counter()
    for family in data['families']:
        count=len(family['rounds'][0]['start groups']['sizes'])
        for stage in family['rounds']:
            if 'new carriers' in stage:
                target=stage['new carriers']
                sub=target['components found without source ring labels']
                for label,arity,image in [('selected rings',count,target['tuples']),
                                           ('common-holding components',len(sub['component sizes']),sub['tuples'])]:
                    groups[(label,arity,tuple(image),stage['within original cap'])]+=1
        if args.pilot:
            break
    answers={}
    for label,n,image,within in groups:
        if (n,image) not in answers:
            answers[n,image]=verify(image,n)
    packed=[dict(reading=label,arity=n, image=image, within_original_cap=within,
                 stages=stages, role_checks=answers[n,image]) for (label,n,image,within),stages in groups.items()]
    if not args.pilot:
        (HERE/'ring_relations.json').write_text(json.dumps(packed,indent=2)+'\n')
    print('rounds',sum(groups.values()),'role assignments',sum(map(len,answers.values())),
          'seconds',round(time.monotonic()-start,3))
if __name__=='__main__':
    main()
