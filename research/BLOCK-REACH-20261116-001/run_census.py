"""Theorem F over the LEVEL-REACH census (BLOCK-REACH-20261116-001, the thread's own code, 2026-11-16): for every alive description
whose orbits have at most four addresses, the least forgetting length r at every remaining depth (forget.py), the census profile at
depth 9, and whether its depth-9 knots form a cycle (RULER-LEVEL-20261114-001's test). Writes census_forget.json; run only after
predictions.md is frozen."""
import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from forget import least_forget  # noqa: E402
from pattern import pattern, level  # noqa: E402

CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'
N, NV = 9, (1 << 10) - 1


def cyclic(key):
    """True when the depth-9 knots form a cycle (a knot and a distinction joined twice), as in RULER-LEVEL's census_forest.py."""
    P = [tuple(int(x) for x in k) for k in pattern(key, N)]
    parent = list(range(NV + len(P)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for j, k in enumerate(P):
        for x in k:
            a, b = find(x), find(NV + j)
            if a == b:
                return True
            parent[a] = b
    return False


def profile_name(prof):
    if prof == (3, 4, 5, 6):
        return 'ruler'
    if prof == (3, 3, 4, 4):
        return 'half-rate'
    if all(isinstance(x, int) for x in prof) and len(set(prof)) == 1:
        return 'direct'
    if 'undecided' in prof:
        return 'undecided'
    if 'none' in prof:
        return 'no bond'
    return 'other'


if __name__ == '__main__':
    rows = {}
    for line in gzip.open(CENSUS, 'rt'):
        rec = json.loads(line)
        if rec.get('union') != 'alive' or 'key' not in rec:
            continue
        f = least_forget(rec['key'])
        if not f['small_orbits']:
            continue
        prof = tuple(x['L_N'] for x in rec['levels'])
        # upper bounds at every depth N >= 9: a depth-9 least bond whose members all lie at level <= 9 - r0 has the same projection,
        # hence stays a bond, at every N >= 9 (the projection onto addresses at level <= m depends on the rest only through F_(N - m))
        upper = {lv['s']: lv['L_N'] for lv in rec['levels']
                 if isinstance(lv['L_N'], int) and lv.get('bond') and max(level(v) for v in lv['bond']) <= N - f['r0']}
        rows[rec['case']] = dict(profile=list(prof), name=profile_name(prof), r=f['r'], r_stable=f['r_stable'], r_all=f['r_all'],
                                 r0=f['r0'], types=f['types'], empty_windows=f['empty_windows'], upper_every_depth=upper,
                                 cyclic=cyclic(rec['key']), relative_class=rec['classes']['relative']['class'],
                                 rises=all(isinstance(x, int) for x in prof) and prof[-1] > prof[0])
    tally = collections.Counter((r['name'], r['cyclic'], r['r_stable'], r['r_all']) for r in rows.values())
    json.dump(dict(rows=rows, tally={str(k): v for k, v in sorted(tally.items(), key=str)}), open(HERE / 'census_forget.json', 'w'), indent=1)
    for k, v in sorted(tally.items(), key=str):
        print(k, v)
