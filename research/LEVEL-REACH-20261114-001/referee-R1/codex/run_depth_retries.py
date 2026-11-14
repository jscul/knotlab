"""Retry completed forest depth timeouts with independently audited pruning."""
import json
import resource
import time
from pathlib import Path
from fresh_pattern import build
from fresh_search import compile_existence,levels
from resolution_accel import derived_nonfull,accelerated_search

HERE=Path(__file__).resolve().parent


def main():
    resource.setrlimit(resource.RLIMIT_AS,(3<<30,3<<30))
    resource.setrlimit(resource.RLIMIT_CPU,(1000,1000))
    baseline=list(map(json.loads,(HERE/'cert_audit/depth_results.jsonl').read_text().splitlines()))
    output=HERE/'depth_retries.jsonl'
    done={(r['case'],r['N'],r['s']) for r in map(json.loads,output.read_text().splitlines())} if output.exists() else set()
    todo=[r for r in baseline if r.get('incidence_forest_N9') and not r['result']['exact']
          and (r['case'],r['N'],r['s']) not in done]
    for r in todo[:3]:
        knots=build(r['key'],r['N'])
        nv=(1<<(r['N']+1))-1
        A,B=levels(3,r['s'])
        result=accelerated_search(knots,nv,A,B,seconds=120)
        row={k:r[k] for k in ['case','stratum','key','N','s','study_N9']}
        row['result']=result
        row['baseline_reason']=r['result'].get('reason')
        row['peak_rss_MiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        with output.open('a') as f:
            f.write(json.dumps(row,separators=(',',':'))+'\n')
        print(json.dumps({'case':r['case'][:16],'N':r['N'],'s':r['s'],'L':result['L'],
                          'seconds':result['stats'].get('seconds'),'pruning':result['resolution_pruning']}),flush=True)


if __name__=='__main__':
    main()
