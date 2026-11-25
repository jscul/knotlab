"""Rewrite a run's record file as one clean gzip member (rows of a run stopped and resumed: complete rows only, each
growth once), and record a run's wall times in run_times.json.

  python -B tidy.py rewrite R1b
  python -B tidy.py time R1b --starts 1000 --registered 2000 --parts "02:24:48-02:32:06,02:32:25-03:27:10" --note ...
"""
import argparse
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study  # noqa: E402


def rewrite(run):
    name = '%s.jsonl.gz' % run
    rows = study.read_jsonl(name)
    seen = {}
    for r in rows:
        k = (r.get('index'), r.get('law'), r.get('renaming'), r.get('run'))
        if k not in seen or ('error' in seen[k] and 'error' not in r):
            seen[k] = r
    tmp = name + '.tmp.gz'
    w = study.JsonLines(tmp)
    for r in seen.values():
        w.write(r)
    w.close()
    os.replace(study.out_path(tmp), study.out_path(name))
    back = study.read_jsonl(name)
    study.log(run, 'rows read', len(rows), 'kept', len(seen), 'read back', len(back))
    return len(back)


def record_time(run, starts, registered, parts, note):
    p = study.out_path('run_times.json')
    d = json.load(open(p)) if os.path.exists(p) else {}
    day = '2026-11-25 '
    mins = 0.0
    spans = []
    for x in parts.split(','):
        a, b = x.split('-')
        ta = datetime.strptime(day + a, '%Y-%m-%d %H:%M:%S')
        tb = datetime.strptime(day + b, '%Y-%m-%d %H:%M:%S')
        mins += (tb - ta).total_seconds() / 60
        spans.append([a, b])
    d[run] = {'starts': starts, 'registered starts': registered, 'wall minutes': round(mins, 1),
              'spans (Pacific time, 2026-11-25)': spans, 'worker processes': 6, 'note': note}
    with open(p, 'w') as f:
        json.dump(d, f, indent=1, sort_keys=True)
    study.log('run_times', run, d[run])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('rewrite', 'time'))
    ap.add_argument('run')
    ap.add_argument('--starts', type=int)
    ap.add_argument('--registered', type=int)
    ap.add_argument('--parts', default='')
    ap.add_argument('--note', default='')
    a = ap.parse_args()
    if a.what == 'rewrite':
        rewrite(a.run)
    else:
        record_time(a.run, a.starts, a.registered, a.parts, a.note)


if __name__ == '__main__':
    main()
