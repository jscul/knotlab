"""Read the round-three upper witness under each choice of retained source laws."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent


def check(limit):
    archive = json.loads((HERE / 'layer_ring_search.json').read_text())
    previous_knots = len(archive['round_2_disjoint']['stage'])
    result = archive['round_3_overlap']
    stage = result['stage']
    pairs = result['witness']['six_lower_carriers_grouped_into_upper_pairs']
    knots = [sum(1 << x for x in support) for support in stage]
    groups = [sum(1 << x for x in c) for pair in pairs for c in pair]
    counts = {}
    new_laws = sum(1 << k for k in range(previous_knots, len(knots)))
    local = {k: Counter() for k in range(1 << len(knots))}
    for s in range(limit):
        failed = sum(1 << k for k, m in enumerate(knots) if (s & m) in (0, m))
        values = [(s & c) in (0, c) for c in groups]
        word = ''.join(str(int(values[i] == values[i + 1])) for i in (0, 2, 4))
        local[failed][word] += 1
    for omitted in local:
        counts[omitted] = sum((table for mask, table in local.items() if mask & ~omitted == 0), Counter())
    def minimal_for_exclusion(omitted):
        return counts[omitted]['000'] == 0 and all(
            counts[omitted | (1 << i)]['000'] > 0 for i in range(len(knots)) if not (omitted >> i) & 1)
    return {'assignments tested': limit, 'stage': stage, 'carrier pairs': pairs,
            'upper counts': dict(sorted(counts[0].items())),
            'upper counts with both new laws absent': counts[new_laws],
            'restored 000 after deleting each source law': [counts[1 << i]['000'] for i in range(len(knots))],
            'minimal sufficient sets of underlying laws': [
                [i for i in range(len(knots)) if not (omit >> i) & 1] for omit in local if minimal_for_exclusion(omit)]}


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
