"""Try a larger finite cap on the thirteen uncarried cases without lassos."""
import json,resource,signal
from lasso_certify import OUT,read_rows
from lasso_automaton import search,alarm,StopSearch
resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
rows=read_rows();signal.signal(signal.SIGALRM,alarm)
todo=[r for line in (OUT/'lasso_results.jsonl').open() if not (r:=json.loads(line))['certified'] and rows[r['key']]['class_path_uncarried']=='bounded']
answers=[]
for old in todo:
    signal.alarm(20)
    try:r=search(rows[old['key']],9,12000)
    except (StopSearch,MemoryError) as ex:r=dict(key=old['key'],complete=False,reason=str(ex),cap=9)
    finally:signal.alarm(0)
    r.pop('graph',None);answers.append(r)
    print(json.dumps({k:v for k,v in r.items() if k not in ['key','certificate']}),flush=True)
    (OUT/'lasso_higher_cap.json').write_text(json.dumps(answers,indent=2)+'\n')
