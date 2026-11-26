"""Recover the freeze, prior work, opportunity counts and archive inventory without changing the study."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = HERE.parents[2]
SCOPE = STUDY.name
FREEZE = '233d6f3087'
CLOSE = '7fe6e10ac6'
resource.setrlimit(resource.RLIMIT_AS, (900 << 20, 900 << 20))


def run(args, check=True):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=check)


def git(*args):
    return run(['git',*args]).stdout


def query(term):
    args = ['scripts/track.py','objects',term,'--until','2026-11-26','--exclude',SCOPE,'--limit','8','--json']
    results=json.loads(run([sys.executable,'-B',*args]).stdout)
    def concise(r):
        path=r['record']
        known=run(['git','cat-file','-e',f'{FREEZE}:{path}'],False).returncode==0
        return dict(id=r['id'], record=path, record_in_freeze_tree=known)
    return dict(args=args, index=[concise(r) for r in results['index']])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pilot',action='store_true')
    args=ap.parse_args()
    start=time.monotonic()
    terms=['binding', 'class facts shortest changes', 'closing birth implied loose distinctions',
           'old states parity growth', 'forbidding cuts', 'fewest fresh distinctions']
    result=dict(searches=[query(t) for t in terms[:1 if args.pilot else None]])
    rel=STUDY.relative_to(ROOT)
    frozen=git('show',f'{FREEZE}:{rel}/README.md')
    closed=git('show',f'{CLOSE}:{rel}/README.md')
    assert closed.startswith(frozen)
    filenames=git('ls-tree','-r','--name-only',FREEZE,'--',str(rel)).splitlines()
    result['record']=dict(freeze=FREEZE, closure=CLOSE, note_appended_without_changing_prediction=closed.startswith(frozen),
                          score_script_in_freeze=any(p.endswith('/score.py') for p in filenames),
                          frozen_output_files_in_freeze_tree=sum('/frozen_' in p for p in filenames),
                          output_files_in_closure=len([p for p in git('ls-tree','-r','--name-only',CLOSE,'--',str(rel)).splitlines() if '/frozen_' in p]),
                          changed_already_frozen_code=git('diff','--name-only',FREEZE,CLOSE,'--',str(rel/'families.py'),str(rel/'repro.py'),str(rel/'premises.py'),str(rel/'origin_scan.py')).splitlines(),
                          carrier_500_limit_in_freeze_prose='500' in frozen,
                          carrier_500_limit_in_freeze_code='cap=500' in git('show',f'{FREEZE}:{rel}/repro.py'),
                          n_5_or_7_only_predicted='For n = 5 and 7' in frozen,
                          stop_rule_excludes_label_prediction='All of P1 (a, c), P2, P3 and P4' in frozen)
    gate=run([sys.executable,'-B','scripts/track.py','objects-gate',str(rel/'README.md')],False)
    result['prior_work_gate']=dict(code=gate.returncode,message=(gate.stdout+gate.stderr).strip())
    result['tables']={}
    for path in sorted(STUDY.glob('*.json*')):
        data=path.read_bytes()
        value = json.loads(data) if path.suffix=='.json' else [json.loads(s) for s in data.splitlines()]
        result['tables'][path.name]=dict(records=len(value),sha256=hashlib.sha256(data).hexdigest())
    result['seconds']=round(time.monotonic()-start,3)
    if not args.pilot:
        (HERE/'record.json').write_text(json.dumps(result,indent=2)+'\n')
    print('pilot' if args.pilot else 'full', result['seconds'], result['prior_work_gate'])
if __name__=='__main__':
    main()
