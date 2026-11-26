"""Check the sequence of the design, its addendum and the saved results."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent.relative_to(ROOT)
DESIGN, ADDENDUM, RESULT = '947486d0f4', 'bd7c6b57af', '89f8da21e9'


def command(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, check=False)


def snapshot(commit, file):
    result = command(['git', 'show', f'{commit}:{STUDY}/{file}'])
    return result.stdout if result.returncode == 0 else None


def freeze_record():
    records = {}
    for ref in (DESIGN, ADDENDUM, RESULT):
        records[ref] = {file: sha256(blob).hexdigest() if blob is not None else None for file in
                        ('README.md','alike.py','criterion.py','phase1_grown.jsonl.gz','phase1_pairs.jsonl.gz',
                         'phase1_rule.json','phase2.py','phase2.json','phase2_grown.jsonl.gz')
                        for blob in [snapshot(ref, file)]}
    texts = [snapshot(ref, 'README.md') for ref in (DESIGN, ADDENDUM, RESULT)]
    return {'committed_file_hashes': records,
            'design_is_byte_prefix_of_addendum': texts[1].startswith(texts[0]),
            'addendum_is_byte_prefix_of_results': texts[2].startswith(texts[1]),
            'current_note_equals_results': texts[2] == (ROOT/STUDY/'README.md').read_bytes(),
            'commits_in_order': all(command(['git','merge-base','--is-ancestor',a,b]).returncode == 0
                                    for a,b in ((DESIGN,ADDENDUM),(ADDENDUM,RESULT)))}


if __name__ == '__main__':
    t0 = monotonic()
    note = str(STUDY/'README.md')
    tracker = [sys.executable,'-B','scripts/track.py']
    gate = command(tracker+['objects-gate',note])
    result = freeze_record()
    result['gate_on_design_note'] = {'exit': gate.returncode,'message': gate.stdout.decode().strip()}
    result['gate_on_frozen_texts'] = {}
    for ref in (DESIGN, ADDENDUM):
        frozen_gate = subprocess.run(tracker+['objects-gate','/dev/stdin'], cwd=ROOT,
                                     input=snapshot(ref,'README.md'), capture_output=True)
        result['gate_on_frozen_texts'][ref] = {
            'exit': frozen_gate.returncode, 'message': frozen_gate.stdout.decode().strip()}
    result['searches'] = []
    for query in ('births read without names agreement up to the count',
                  'ring eddies rate surplus places golden ratio',
                  'largest maximal block binomial burst',
                  'live-neighbour sets down-closure',
                  'polynomial dimension counts growing trees relays',
                  'start origin complete layer zero bits'):
        args = ['objects', query,'--until','2026-11-26','--exclude',STUDY.name,'--limit','5','--json']
        found = command(tracker+args)
        found.check_returncode()
        index = json.loads(found.stdout)['index']
        result['searches'].append({'arguments':args,'top_index_rows': [row['record'] for row in index]})
    result['seconds'] = round(monotonic() - t0, 3)
    (HERE/'provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({x: result[x] for x in ('gate_on_design_note','searches','seconds')},indent=2))
