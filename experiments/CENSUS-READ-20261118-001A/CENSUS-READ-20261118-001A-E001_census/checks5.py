"""Checks after the pass-5 readout (not predictions): (i) what R3n returns at the 3-connected stages classed "same states";
(ii) the stages where R3n's verdict changed under renaming: does the closure step's enumeration change with the names?
(iii) C7: R3's verdict on the side-limited table (pass 1) against the exact table (pass 5), stage by stage.
Run: .venv/bin/python -B checks5.py runs/census-exact5 runs/census-read  -> checks5.json beside the artifacts."""
import json
import random
import sys
import zlib
from collections import Counter
from pathlib import Path

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import job  # noqa: E402
import job_exact3 as J  # noqa: E402
import exact_table_v2 as X  # noqa: E402
import reader3n_v2 as N  # noqa: E402
from longrun import load_results  # noqa: E402
R, R3, S, F, A = job.R, job.R3, job.S, job.F, job.A


def stars_at(key, r):
    P = S.from_junctions(A.stars_of((tuple(key[0]), tuple(key[1]))))
    for _ in range(r):
        P.step(S.gf2(F.fewest), None)
    return [frozenset(b) for b in P.bits_of]


def main(p5, p1):
    arrs = [a for cid, r in sorted(load_results(p5).items()) if cid.startswith('census') for a in r['result']['arrangements']]
    stages = [(a, st) for a in arrs for st in a['stages']]
    out = {}
    # (i)
    kinds = Counter()
    for a, st in stages:
        if st['connectivity'] == 'three' and st['r3n'] == 'same_states':
            stars = stars_at(a['key'], st['round'])
            truth = set(stars)
            own = R.owners(stars)
            loose = frozenset(b for b, js in own.items() if len(js) == 1)
            K = max(map(len, stars))
            got = N.r3n(X.exact_table(stars, K + 2), K + 3)
            kinds['truth_plus_loose_set' if got == truth | {loose} else
                  ('subset_of_truth_plus_loose' if got <= truth | {loose} else 'other')] += 1
    out['r3n_same_states_at_three_connected'] = dict(kinds)
    # (ii)
    changed = [(a, st) for a, st in stages if any(v != st['r3n'] for v in st['r3n_renamed'])]
    rows = []
    for a, st in changed[:12]:
        stars = stars_at(a['key'], st['round'])
        K = max(map(len, stars))
        H = K + 2
        tab = X.exact_table(stars, H)
        labels = sorted(R.owners(stars))
        rng = random.Random(zlib.crc32(f'{json.dumps(a["key"])}/{st["round"]}'.encode()))
        img = list(labels)
        rng.shuffle(img)
        perm = dict(zip(labels, img))
        fl0, fl1 = Counter(), Counter()
        g0 = N.r3n(tab, H + 1, fl0)
        g1 = J.renamed(lambda t, top: N.r3n(t, top, fl1), tab, perm, H + 1)
        rows.append({'key': a['key'], 'round': st['round'], 'junctions': len(stars), 'same_output': g0 == g1,
                     'flags_identity': dict(fl0), 'flags_renamed': dict(fl1)})
    out['r3n_renaming_changes'] = {'stages': len(changed), 'replayed': rows,
                                   'replayed_large_conflict_involved': sum(1 for r in rows if r['flags_identity'].get('large_conflict') or r['flags_renamed'].get('large_conflict'))}
    # (iii)
    side = {(json.dumps(a['key']), st['round']): st['r3'] for cid, r in sorted(load_results(p1).items())
            if cid.startswith('census') and r['status'] == 'ok' for a in r['result']['arrangements'] for st in a['stages']}
    c7 = Counter()
    for a, st in stages:
        v = side.get((json.dumps(a['key']), st['round']))
        if v is None:
            continue
        big = 'over_14' if st['junctions'] > 14 else 'at_most_14'
        closed = st['connectivity'] == 'zero'
        c7[f'{big}{"_closed" if closed else ""}_{"same" if v == st["r3"] else "changed"}'] += 1
    out['C7_r3_side_limited_vs_exact'] = dict(c7)
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    (dest / 'checks5.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:4000])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
