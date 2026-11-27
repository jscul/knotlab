"""Search smaller named parity presentations for the three example properties."""
import argparse
import json
import time
from collections import Counter
from itertools import combinations
from census_tools import HERE, connected, roster, tree


def rank_key(rows):
    span = {0}
    for r in rows:
        span.update(v ^ r for v in tuple(span))
    return tuple(sorted(span))


def search(n, first_rows=None):
    names = (1 << n) - 1
    options = [r for r in range(1, names+1) if r.bit_count() >= 3]
    seen = {}
    presentation_counts = Counter()
    witnesses = {}
    count = 0

    def visit(at, rows, used, twice):
        nonlocal count
        if used == names and connected(rows):
            count += 1
            space = rank_key(rows)
            presentation_counts[space] += 1
            families = tree(rows)[0]
            loose = used ^ twice
            intersections = [a & b for a,b in combinations(rows,2)]
            singly = all(x.bit_count() <= 1 for x in intersections)
            signature = (families, loose, singly)
            earlier = seen.setdefault(space, {})
            states = (1 << n) // len(space)
            for (f, l, simple), p in earlier.items():
                cases = []
                if l != loose and {len(f), len(families)} == {1,2}:
                    cases.append('different marks, two families versus one')
                    if singly and simple:
                        cases.append('different marks, two versus one, at most one shared per pair')
                if l == loose and loose.bit_count() == 2 and f == families and len(f) == 1:
                    cases.append('same two marks and one family')
                for case in cases:
                    key = case + (', eight states' if states==8 else
                                  ', sixteen states' if states==16 else ', other state count')
                    witnesses.setdefault(key, dict(support_masks=[p, rows], states=states))
            earlier.setdefault(signature, rows)
        if 2*n - used.bit_count() - twice.bit_count() < 3:
            return
        for i in range(at, len(options)):
            if not rows and first_rows is not None and i >= first_rows:
                break
            r = options[i]
            if not r & twice:
                visit(i+1, (*rows,r), used|r, twice | (r & used))

    visit(0, (), 0, 0)
    results = dict(connected_presentations=count, examples=witnesses)
    if first_rows is None:
        eligible = [(i, r) for i, r in enumerate(roster()) if max(r).bit_length() == n]
        unique = [(i, r) for i, r in eligible if presentation_counts[rank_key(r)] == 1]
        results["census_sources"] = len(eligible)
        results["census_sources_unique_even_unmarked"] = len(unique)
        if unique:
            i, rows = unique[0]
            results["first_unique_unmarked"] = dict(census_index=i, source_support_masks=rows,
                                                      states=(1 << n)//len(rank_key(rows)))
    return results


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    begin=time.monotonic()
    if args.pilot:
        print('first two supports at width seven',search(7,2)['connected_presentations'],
              'seconds',round(time.monotonic()-begin,3))
    else:
        result={n:search(n) for n in range(3,8)}
        (HERE / 'pair_sizes.json').write_text(json.dumps(result,indent=2)+'\n')
        print('complete',round(time.monotonic()-begin,3),'seconds')
