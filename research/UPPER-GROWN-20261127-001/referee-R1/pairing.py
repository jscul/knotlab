"""Test an explicit construction on the archived twelve-knot systems."""
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import json
import time

HERE = Path(__file__).resolve().parent


def pairings(remaining, neighbours):
    if not remaining:
        yield ()
        return
    first = min(remaining)
    for second in sorted(remaining & neighbours[first]):
        for rest in pairings(remaining - {first, second}, neighbours):
            yield ((first, second),) + rest


def candidates(links):
    neighbours = [set() for _ in range(12)]
    for x, y in links:
        neighbours[x].add(y)
        neighbours[y].add(x)
    for matching in pairings(set(range(12)), neighbours):
        groups = {x: i for i, pair in enumerate(matching) for x in pair}
        leftover = [(x, y) for x, y in links if groups[x] != groups[y]]
        relations = {tuple(sorted([groups[x], groups[y]])) for x, y in leftover}
        if len(relations) != 12:
            continue
        adj = [set() for _ in neighbours]
        for x, y in leftover:
            adj[x].add(y)
            adj[y].add(x)
        cycles = []
        remaining = set(range(12))
        while remaining:
            x = min(remaining)
            cycle = []
            while x in remaining:
                remaining.remove(x)
                cycle.append(x)
                x = next((y for y in sorted(adj[x]) if y in remaining), x)
            cycles.append(tuple(cycle))
        yield matching, relations, cycles


def count_constructions(links):
    designs = set()
    matchings = 0
    for matching, relations, cycles in candidates(links):
        matchings += 1
        groups = {x: i for i, pair in enumerate(matching) for x in pair}
        pairs = [(i,j) for i in range(6) for j in range(i) if (j,i) not in relations]
        for signs in product((1, -1), repeat=len(cycles)):
            carriers = [[tuple(sorted(pair))] for pair in matching]
            for cycle, sign in zip(cycles, signs):
                for k, x in enumerate(cycle):
                    y = cycle[(k + sign) % len(cycle)]
                    carriers[groups[x]].append(tuple(sorted([x, y])))
            key = tuple(sorted(tuple(sorted((tuple(sorted(carriers[i])), tuple(sorted(carriers[j]))))) for i,j in pairs))
            designs.add(key)
    return matchings, designs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    begin = time.perf_counter()
    records = []
    known_path=HERE/'closed_boxes.jsonl'
    known={(r['file'],r['line']):r for line in known_path.open() for r in [json.loads(line)] if r['knots']==12}

    for path in sorted((HERE.parent / 'out').glob('cubic_12_*.jsonl')):
        for line, content in enumerate(path.read_text().splitlines(), 1):
            raw = json.loads(content)
            matches, designs = count_constructions(raw['links'])
            row=known[path.name,line]
            labels=row['distinction_links']
            real=set()
            for found in row['all_upper']:
                box=found['carriers_and_missing_values']
                if all(v==1 for pair in box for carrier,v in pair):
                    key=tuple(sorted(tuple(sorted(tuple(sorted(tuple(sorted(labels[x])) for x in carrier))
                                                  for carrier,v in pair)) for pair in box))
                    real.add(key)
            assert designs <= real
            constructions=len(designs)
            records.append(dict(file=path.name, line=line, matchings=matches,
                                constructions=constructions, raw_boxes=raw['boxes']))
            if args.pilot and len(records) == 2:
                break
        if args.pilot:
            break
    result = dict(graphs=records, class_agreements=sum(bool(r['constructions'])==bool(r['raw_boxes']) for r in records),
                  exact_counts=sum(r['constructions']==r['raw_boxes'] for r in records),
                  positive_classes=sum(bool(r["constructions"]) for r in records),
                  generated=sum(r['constructions'] for r in records),
                  seconds=time.perf_counter()-begin)
    print({k:v for k,v in result.items() if k != 'graphs'})
    if not args.pilot:
        (HERE/'pairing.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
