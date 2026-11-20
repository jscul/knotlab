"""Reproduce published outputs in a temporary owned directory and compare bytes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import rates
import verify
from survey import HERE, OUT, ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--omit-edits', action='store_true', help='run just the independent-start checks')
    options=parser.parse_args()
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise SystemExit('Set PYTHONHASHSEED=0, as in the reported runs.')
    source=ROOT/'research'/HERE.parent.name
    comparisons={}
    with tempfile.TemporaryDirectory(dir=OUT) as d:
        replay=Path(d)
        def run(script, output):
            subprocess.run([sys.executable,'-B',str(HERE/script),'--output',str(replay/output)],check=True)
        run('survey.py','draws.jsonl')
        verify.OUT=replay
        verify.main()
        rates.OUT=replay
        rates.main(replay/'rates.md')
        targets=['draws.jsonl','certificates.json','rates.json','rates.md']
        if not options.omit_edits:
            run('edits.py','edits.json')
            targets.append('edits.json')
        for name in targets:
            original=(source if name.endswith('.md') else OUT)/name
            assert (replay/name).read_bytes()==original.read_bytes(),name
            comparisons[name]=digest(original)
    data={'method':'Regenerated and compared every byte to the saved output. PYTHONHASHSEED=0.',
          'records':comparisons,'draw_count':sum(1 for _ in (OUT/'draws.jsonl').open()),
          'python':sys.version.split()[0], 'inputs':{p.name:digest(p) for p in
              [source/'preregistration.md',source/'advisor.json',HERE/'contract.json',HERE/'identity.json',
               HERE/'survey.py',HERE/'verify.py',HERE/'rates.py',HERE/'edits.py',HERE/'replay.py']}}
    if not options.omit_edits:
        (OUT/'replay.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(comparisons,sort_keys=True))


if __name__=='__main__':
    main()
