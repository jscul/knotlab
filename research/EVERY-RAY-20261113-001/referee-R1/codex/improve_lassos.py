"""Look for all-positive-depth witnesses for the six eventual-only lassos."""
import json,signal,time
from lasso_certify import OUT,read_rows
from lasso_automaton import search,alarm,StopSearch
rows=read_rows()
todo=[r for line in (OUT/'lasso_results.jsonl').open() if (r:=json.loads(line))['certified'] and not r['all_depths_have_bond']]
signal.signal(signal.SIGALRM,alarm)
answers=[]
for old in todo:
    signal.alarm(40)
    try:r=search(rows[old['key']],9,10000,require_all_depths=True)
    except (StopSearch,MemoryError) as ex:r=dict(key=old['key'],complete=False,reason=str(ex))
    finally:signal.alarm(0)
    r.pop('graph',None)
    answers.append(r)
    print(json.dumps({k:v for k,v in r.items() if k not in ['key','certificate']}),flush=True)
(OUT/'lasso_improvements.json').write_text(json.dumps(answers,indent=2)+'\n')
