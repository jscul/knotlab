"""Matched finite controls and a timed depth retry for optional pruning."""
import json
import random
import time
from pathlib import Path
from fresh_pattern import build
from fresh_search import levels, search, compile_existence
from resolution_accel import accelerated_search, derived_nonfull

HERE=Path(__file__).resolve().parent


def main():
    plan=json.loads((HERE/'sample_plan.json').read_text())
    controls=[]
    for row in plan['sample'][:12]:
        knots=build(row['key'],4)
        for s in [1,2]:
            A,B=levels(2,s)
            plain=search(knots,31,A,B,cap=7,seconds=10)
            fast=accelerated_search(knots,31,A,B,cap=7,seconds=10)
            assert plain['exact'] and fast['exact'] and plain['L']==fast['L']
            controls.append({'case':row['case'],'N':4,'s':s,'plain':plain['L'],
                             'accelerated':fast['L'],'pruning':fast['resolution_pruning']})
    (HERE/'acceleration_controls.json').write_text(json.dumps({'controls':controls},indent=2)+'\n')
    row=plan['sample'][4]
    knots=build(row['key'],11)
    A,B=levels(3,4)
    result=accelerated_search(knots,4095,A,B,seconds=120)
    output={'case':row['case'],'stratum':row['stratum'],'key':row['key'],'N':11,'s':4,
            'study_N9':6,'result':result}
    (HERE/'acceleration_benchmark.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'case':row['case'][:16],'N':11,'s':4,'L':result['L'],
                      'seconds':result['stats'].get('seconds'),'pruning':result['resolution_pruning']}),flush=True)


if __name__=='__main__':
    main()
