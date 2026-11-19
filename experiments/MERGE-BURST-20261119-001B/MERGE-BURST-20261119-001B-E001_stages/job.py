"""Shared-runner job for MERGE-BURST-20261119-001B-E001 (frozen with the pre-registration).

One case per start: EXPLOSIVE's explosive starts within seven places (the 15 stopped at its per-start limits, and the one that
closed, as the control), read from runs/explosive. Each is followed by mblib.follow: a forked child (6 GB, 15 minutes, to round 60)
reports every round's count, largest group, stage class and reduced-stage verdict. At the first reduced stage in the class it
reports the reading and the branch system's next 40 rounds, then grows 8 more rounds to check them."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import mblib  # noqa: E402

sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def population():
    R = load_results(str(ROOT / 'runs/explosive'))
    out = []
    for cid, r in sorted(R.items()):
        if not cid.startswith('cap-7'):
            continue
        for x in r['result']['starts']:
            if x['measured'] == 'explosive':
                out.append({'sizes': x['sizes'], 'edges': [tuple(y) for y in x['edges']], 'n': x['n'], 'outcome_then': x['outcome'],
                            'counts_then': x['counts'], 'groups_then': x['groups']})
    out.sort(key=lambda x: (x['n'], sum(x['sizes']), x['sizes'], x['edges']))
    return out


def cases():
    for i, x in enumerate(population()):
        yield f'start-{i:02d}', {'i': i}


def run(case_id, payload):
    x = population()[payload['i']]
    r = mblib.follow(x['sizes'], x['edges'], T=60, H=40, V=8, mem=6_000_000_000, seconds=900)
    return {'start': x, 'follow': r}
