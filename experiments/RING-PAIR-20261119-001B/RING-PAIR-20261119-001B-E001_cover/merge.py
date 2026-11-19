"""Score RING-PAIR-20261119-001B-E001.  .venv/bin/python -B merge.py <runner out dir> <results.json>"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import covermodel as M  # noqa: E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('ring_pair_job', HERE / 'job.py')   # not JOIN-GROWTH's job.py on the path
job = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(job)
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def main():
    recs = load_results(sys.argv[1])
    for extra in sys.argv[3:]:          # the memory rerun (amendment of 01:48 UTC)
        for cid, rec in load_results(extra).items():
            if rec.get('status') == 'ok' and (recs.get(cid) or {}).get('status') != 'ok':
                recs[cid] = rec
    rows, held, scored = {}, 0, 0
    for cid, pay in job.cases():
        rec = recs.get(cid)
        if rec is None or rec.get('status') != 'ok':
            rows[cid] = {'status': None if rec is None else rec.get('status')}
            continue
        r = rec['result']
        c = r['counts']
        row = {'outcome': r['outcome'], 'rounds': r['rounds'], 'junctions': r['junctions'], 'in_scope': r['in_scope'],
               'why': r['why'], 'counts': c, 'last_ratio': c[-1] / c[-2] if len(c) > 2 and c[-2] else None}
        if pay['predicted']:
            scored += 1
            row['equal'] = r.get('equal')
            row['first_difference'] = r.get('first_difference')
            held += bool(r.get('equal'))
            nv, B = M.blocks_of(pay['n'], [tuple(x) for x in pay['edges']], pay['surplus'])
            row['lambda'] = 1 / M.rho(B)
        rows[cid] = row
    out = {'P1': {'held': held, 'scored': scored}, 'cases': rows}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out['P1']))
    for k, v in rows.items():
        print(k, v.get('outcome'), v.get('rounds'), v.get('equal'), v.get('first_difference'), round(v.get('lambda') or 0, 4),
              round(v.get('last_ratio') or 0, 4))


if __name__ == '__main__':
    main()
