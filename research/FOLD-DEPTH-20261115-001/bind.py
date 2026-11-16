"""Create pre-solver fixtures and freeze the study sources and all input commitments."""
import argparse
import hashlib
import json
from pathlib import Path
import time

NOTES = Path(__file__).resolve().parent
ROOT = NOTES.parents[1]
TICKET = NOTES.name
EXP = ROOT/'experiments'/TICKET/(TICKET+'-E001_supplied_fold')
OUT = ROOT/'artifacts'/TICKET/EXP.name
SOURCE = ROOT/'artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner'
FOLD_SHA = '271dbaaab837a5ad91962c12ec421385adf44cb82358698a6bd1bd7576dab907'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, data):
    with path.open('xb') as file:
        file.write(data)


def json_bytes(obj):
    return json.dumps(obj,separators=(',',':'),sort_keys=True,allow_nan=False).encode()+b'\n'


def bind(directory):
    import tasks
    out = Path(directory).resolve()
    out.mkdir(exist_ok=True,parents=True)
    if (out/'freeze.json').exists():
        raise ValueError('study already frozen in this directory')
    original = SOURCE/'fold.json'
    if sha(original) != FOLD_SHA:
        raise ValueError('original two-operation program fingerprint changed')
    records, grade = {}, {}
    for split, get_tasks in [('primary',tasks.tasks),('fixed9',tasks.fixed_width_tasks)]:
        panel = list(get_tasks())
        metadata = tasks.grading(split)
        if len(panel) != len(metadata):
            raise ValueError(f'{split} metadata size differs')
        grade[split] = metadata
        for public in panel:
            key = public['id']
            if key not in metadata or set(public) != {'id','n','truth'}:
                raise ValueError(f'unexpected task format for {split}')
            if key in records and records[key] != public:
                raise ValueError('a fixed-width alias changed function')
            records[key] = public
    if len({(t['n'],t['truth']) for t in records.values()}) != len(records):
        raise ValueError('repeated actual targets in measured cases')
    ordered = sorted(records.values(),key=lambda t:hashlib.sha256(('depth-schedule-v1/'+t['id']).encode()).digest())
    write_new(out/'public.json',json_bytes(ordered))
    write_new(out/'grading.json',json_bytes(grade))
    write_new(out/'fold.json',original.read_bytes())
    sources = [EXP/'contract.json',EXP/'identity.json',EXP/'job.py',EXP/'solver.py',EXP/'peel.py',
               NOTES/'tasks.py',NOTES/'bind.py',NOTES/'assess.py',NOTES/'preregistration.md',original,SOURCE/'panel.json']
    # The scientific instrument declares any extra local runtime dependencies.
    import sys
    sys.path.insert(0,str(EXP))
    import solver
    sources += [ROOT/p for p in getattr(solver,'SOURCE_DEPENDENCIES',())]
    bound = {'sources':{str(p.relative_to(ROOT)):sha(p) for p in sources},
             'inputs':{n:sha(out/n) for n in ('public.json','grading.json','fold.json')},
             'frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'tasks':len(ordered)}
    write_new(out/'freeze.json',json_bytes(bound))
    print(json.dumps(bound,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=OUT)
    bind(p.parse_args().out)
