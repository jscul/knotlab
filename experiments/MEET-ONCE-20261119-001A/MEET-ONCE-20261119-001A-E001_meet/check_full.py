"""MEET-ONCE-20261119-001A control: on the collision groups of at most 34 distinctions, compute both full tables and test their
isomorphism directly (VF2), and re-test the states carrier by an independent check (the mapped stars span exactly the other
arrangement's equations).  Run: .venv/bin/python -B check_full.py -> check_full.json beside the artifacts."""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pairs_meet2 as P  # noqa: E402
PM = P.PM
DEST = ROOT / 'artifacts/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet'
MAXN = 34


def one(r):
    out = []
    for (i, j, v, n) in r['tests']:
        a = [frozenset(s) for s in r['members'][i]['stars']]
        b = [frozenset(s) for s in r['members'][j]['stars']]
        fa, fb = PM.table_at(a, r['distinctions']), PM.table_at(b, r['distinctions'])
        out.append({'distinctions': r['distinctions'], 'junctions': [len(a), len(b)], 'verdict': v,
                    'full_tables_isomorphic': PM.iso(PM.coloured(*fa), PM.coloured(*fb))})
    return out


def main():
    d = json.loads((DEST / 'meet_pairs2.json').read_text())
    work = [r for r in d['groups'] if r['distinctions'] <= MAXN]
    with Pool(8) as pool:
        rows = [x for res in pool.map(one, work, chunksize=1) for x in res]
    s = {'pairs_checked': len(rows), 'full_tables_isomorphic': sum(1 for x in rows if x['full_tables_isomorphic'])}
    (DEST / 'check_full.json').write_text(json.dumps({'summary': s, 'rows': rows}, indent=1))
    print(json.dumps(s))


if __name__ == '__main__':
    main()
