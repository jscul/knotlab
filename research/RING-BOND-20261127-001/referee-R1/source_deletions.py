"""Delete each original source law of the twelve-knot witness and read both levels."""
import argparse
import json
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent


def check(limit):
    data = json.loads((HERE / 'layer_witness.json').read_text())
    knots = [sum(1 << x for x in k) for k in data['source_knots_not_all_equal']]
    groups = [sum(1 << x for x in c) for c in data['lower_carriers_in_A0_A1_B0_B1_C0_C1_order']]
    normal, deletions = set(), [set() for _ in knots]
    counts = [0] * len(knots)
    for s in range(limit):
        failed = -1
        for i, m in enumerate(knots):
            if s & m in (0, m):
                if failed != -1:
                    break
                failed = i
        else:
            lower = [(s & group) in (0, group) for group in groups]
            word = ''.join(str(int(lower[j] == lower[j+1])) for j in (0, 2, 4))
            if failed == -1:
                normal.add(word)
            else:
                deletions[failed].add(word)
                counts[failed] += word == '000'
    return {'raw assignments tested': limit, 'upper source image': sorted(normal),
            'number of source assignments restoring 000 by one specified deletion': counts,
            'sizes of upper image after each original source deletion': [len(normal | d) for d in deletions]}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('limit', type=int)
    p.add_argument('--out', type=Path)
    args = p.parse_args()
    t = perf_counter()
    r = check(args.limit)
    r['seconds'] = round(perf_counter() - t, 4)
    print(json.dumps(r))
    if args.out:
        args.out.write_text(json.dumps(r, indent=2) + '\n')
