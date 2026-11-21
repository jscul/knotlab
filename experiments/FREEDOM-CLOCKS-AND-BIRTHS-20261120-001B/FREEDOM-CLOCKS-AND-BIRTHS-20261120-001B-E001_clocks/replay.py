"""Compare the four study outputs to independent, fully regenerated files."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT/'artifacts'/HERE.parent.name/HERE.name
RESEARCH = ROOT/'research'/HERE.parent.name


def digest(file):
    return sha256(file.read_bytes()).hexdigest()


def main():
    env = dict(os.environ, PYTHONHASHSEED='7')
    with tempfile.TemporaryDirectory(dir=OUT) as temporary:
        saved = Path(temporary)
        def run(args):
            subprocess.run([sys.executable, '-B', *map(str,args)], env=env, check=True,
                           stdout=subprocess.DEVNULL)
        commands = [(HERE/'clocks.py', '--output-dir', saved),
                    (HERE/'rings.py', '--output', saved/'rings.json')]
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(run, commands))
        checks={}
        for name in ['clocks.json','draws.jsonl','rates.json','rings.json']:
            assert (saved/name).read_bytes()==(OUT/name).read_bytes(),name
            checks[name]=digest(OUT/name)
    files=[HERE/'contract.json',HERE/'clocks.py',HERE/'rings.py',HERE/'replay.py',
           RESEARCH/'advisor.json',RESEARCH/'preregistration.md']
    rec={'regeneration':'Physical inputs, exact words and true-parent checks, two laws. Independent Python hash seed 7.',
         'draw_count':sum(1 for _ in (OUT/'draws.jsonl').open()),'byte_identical_outputs':checks,
         'input_sha256':{str(p.relative_to(ROOT)):digest(p) for p in files}}
    (OUT/'replay.json').write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps(checks))


if __name__=='__main__':
    main()
