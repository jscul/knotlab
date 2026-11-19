"""PARENT-RULE-20261119-001B, exploratory (after S1a and S1b failed).  Self-grown (self_grown.py) for every arrangement of part S;
then, among the self-grown ones only, table groups (sorted-rows hash, then VF2) and state groups.  A sanity check first: open
census stages of round 1 to 3 with at most 12 junctions must all be self-grown.
Run: .venv/bin/python -B self_grown_all.py runs/parent-static -> self_grown_all.json."""
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import census_job as C  # noqa: E402
import plib as L  # noqa: E402
import static_pairs as SP  # noqa: E402
from self_grown import self_grown  # noqa: E402
DEST = ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'


def flag(row):
    return self_grown(SP.stars_of(row))


def sanity(lo_hi):
    lo, hi = lo_hi
    data = C.CJ.load()
    c = Counter()
    for i in range(lo, hi):
        P = C.S.from_junctions(C.A.stars_of(data[i]))
        for r in range(1, 4):
            res = P.step(C.S.gf2(C.F.fewest), None)
            if res is None or res['new'] == 0:
                break
            stars = [frozenset(b) for b in P.bits_of]
            if len(stars) > 12:
                break
            if L.live_set(stars):
                c['open_stages'] += 1
                c['self_grown'] += self_grown(stars)
    return dict(c)


def main(out_dir):
    recs = SP.load_results(out_dir)
    rows = [dict(zip(SP.F, r)) for c, rr in sorted(recs.items()) if rr['status'] == 'ok' for r in rr['result']['rows']]
    with Pool(8) as pool:
        san = Counter()
        for r in pool.map(sanity, [(k, k + 50) for k in range(0, 26441, 2645)]):
            san.update(r)
        flags = pool.map(flag, rows, chunksize=500)
        sg = [r for r, f in zip(rows, flags) if f]
        by = defaultdict(list)
        for r in sg:
            by[(r['key'], r['distinctions'])].append(r)
        work = [v for v in by.values() if len(v) >= 2]
        res = [g for b in pool.imap_unordered(SP.bucket, work, chunksize=2) for g in b]
    s = {'sanity_census': dict(san), 'arrangements': len(rows), 'self_grown': len(sg),
         'self_grown_by_n': dict(sorted(Counter(r['n'] for r in sg).items())),
         'self_grown_by_depth': dict(sorted(Counter(r['depth'] for r in sg).items())),
         'self_grown_P1': sum(r['P1'] == 0 for r in sg),
         'table_groups_among_self_grown': len(res),
         'same_states_groups': sum(1 for g in res if g['state_groups'] == 1),
         'other_states_groups': sum(1 for g in res if g['state_groups'] >= 2),
         'undecided_tests': sum(g['undecided_tests'] for g in res)}
    (DEST / 'self_grown_all.json').write_text(json.dumps({'summary': s, 'other_states_groups': [g for g in res if g['state_groups'] >= 2]}, indent=1, default=str))
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
