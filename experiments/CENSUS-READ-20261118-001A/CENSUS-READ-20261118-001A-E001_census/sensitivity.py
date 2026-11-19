"""CENSUS-READ-20261118-001A Amendment 1, C7: exact tables on the sampled census stages of more than 14 junctions.
Run: .venv/bin/python -B sensitivity.py runs/census-read [runs/census-read-single]  -> sensitivity.json beside the artifacts."""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import job  # noqa: E402
import exact_table as X  # noqa: E402
from longrun import load_results  # noqa: E402
R, R3, S, F, A = job.R, job.R3, job.S, job.F, job.A


def stage_stars(key, r):
    P = S.from_junctions(A.stars_of((tuple(key[0]), tuple(key[1]))))
    for _ in range(r):
        P.step(S.gf2(F.fewest), None)
    return [frozenset(b) for b in P.bits_of]


def check(item):
    key, r, before = item
    st = stage_stars(key, r)
    truth = set(st)
    own = R.owners(st)
    loose = frozenset(b for b, js in own.items() if len(js) == 1)
    K = max(map(len, st))
    H = K + 2
    side, _ = R.bond_table(st, 6, H)
    ex = X.exact_table(st, H)
    inside = [p for p in ex if ex[p] <= K - 1 or side[p] <= K - 1]
    diff_inside = sum(1 for p in inside if ex[p] != side[p])
    diff_all = sum(1 for p in ex if ex[p] != side[p])
    after = {'r3': job.verdict(R3.r3(ex, H + 1), truth, loose), 'r3m': job.verdict(job.r3m(ex, H + 1), truth, loose)}
    return {'key': key, 'round': r, 'junctions': len(st), 'largest': K, 'differing_inside_horizon': diff_inside,
            'differing_any': diff_all, 'before': before, 'after': after,
            'verdict_changed': any(before[k] != after[k] for k in after)}


def main(dirs):
    items, exact_seen = [], 0
    arrs = []
    for d in dirs:
        for cid, rec in sorted(load_results(d).items()):
            if rec['status'] == 'ok' and cid.startswith('census'):
                arrs.extend(rec['result']['arrangements'])
    arrs.sort(key=lambda a: (a['key'][0], a['key'][1]))
    seen = set()
    for a in arrs:
        k = json.dumps(a['key'])
        if k in seen:
            continue
        seen.add(k)
        for st in a['stages']:
            if st['junctions'] <= 14:
                continue
            before = {'r3': st['r3'], 'r3m': st['r3m']}
            if 'exact' not in before.values() or before['r3'] != 'exact' or before['r3m'] != 'exact':
                items.append((a['key'], st['round'], before))
            else:
                if exact_seen % 50 == 0:
                    items.append((a['key'], st['round'], before))
                exact_seen += 1
    with Pool(12) as pool:
        res = pool.map(check, items, chunksize=1)
    out = {'stages_checked': len(res), 'not_exact_before': sum(1 for x in res if 'exact' != x['before']['r3'] or 'exact' != x['before']['r3m']),
           'stages_differing_inside_horizon': sum(1 for x in res if x['differing_inside_horizon']),
           'stages_differing_anywhere': sum(1 for x in res if x['differing_any']),
           'verdicts_changed': sum(1 for x in res if x['verdict_changed']),
           'C7_holds': all(not x['differing_inside_horizon'] and not x['verdict_changed'] for x in res),
           'rows': res}
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    (dest / 'sensitivity.json').write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
