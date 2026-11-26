"""Enumerate each support on its own, before checking which triples obey a rule."""
import argparse
from collections import defaultdict, deque, Counter
from functools import reduce
from itertools import combinations
from operator import xor
import json
from pathlib import Path
import time

from carrier_check import basis, bits, mask, moves_of, rem
from replay_growth import grow, start_items

HERE = Path(__file__).resolve().parent


def read(stage, earlier, initial, max_length=8, visit_limit=200000):
    holders, moves = moves_of(stage)
    rows = list(map(mask, stage))
    laws = basis(rows)
    names = sorted(holders)
    mbasis = list(basis(moves).values())
    k = len(names) - len(laws) - len(mbasis)
    if k < 2:
        return {'class_bits': k}
    n = len(stage)
    sig = {i: sum(((m >> i) & 1) << j for j, m in enumerate(mbasis)) for i in names}
    single = {i: rem(laws, 1 << i) for i in names}
    # Each loose distinction gets a separate endpoint used only to enumerate
    # a path's support. There is no additional knot law at these endpoints.
    links = defaultdict(list)
    for d, who in holders.items():
        a, b = who if len(who) == 2 else [who[0], n+d]
        links[a].append((b, d))
        links[b].append((a, d))
    locals_ = [basis(single[d] for d in s) for s in stage]
    cache = {}
    def unread(value):
        if value not in cache:
            cache[value] = value and all(rem(local, value) for local in locals_)
        return cache[value]

    families = [defaultdict(set) for _ in range(2)]
    work = 0
    for start in sorted(links):
        dist = {start: 0}
        queue = deque([start])
        while queue:
            v = queue.popleft()
            if dist[v] < max_length:
                for w, d in links[v]:
                    if w not in dist:
                        dist[w] = dist[v]+1
                        queue.append(w)
        todo = [(start, 1 << start, 0, 0, 0, 0)]
        while todo and work < visit_limit:
            v, seen, support, size, signature, value = todo.pop()
            work += 1
            if v > start and not signature and unread(value):
                families[1][value].add(support)
                if size == dist[v]:
                    families[0][value].add(support)
            if size < max_length:
                for w, d in links[v]:
                    if not (seen >> w & 1):
                        todo.append((w, seen | (1 << w), support | (1 << d), size+1, signature ^ sig[d], value ^ single[d]))
        if work >= visit_limit:
            break
    output = dict(class_bits=k, partial=work>=visit_limit)
    old_laws = basis(map(mask, initial))
    prev_laws = basis(map(mask, earlier))
    for title, by_value in zip(['shortest_paths', 'all_paths'], families):
        found = Counter()
        best = None
        best_grade = (-1, -1, -9999)
        for a, b in combinations(sorted(by_value), 2):
            c = a ^ b
            if c <= b or c not in by_value:
                continue
            prices = sorted((len(by_value[x]), x) for x in (a,b,c))
            lists = [sorted(by_value[v]) for _,v in prices]
            for p in lists[0]:
                for q in lists[1]:
                    if p & q:
                        continue
                    for r in lists[2]:
                        if (p | q) & r:
                            continue
                        total = p ^ q ^ r
                        assert rem(laws, total) == 0
                        new = int(rem(prev_laws, total) != 0)
                        newer_than_source = int(rem(old_laws, total) != 0)
                        found['triples'] += 1
                        found['require_this_round'] += new
                        grade = (new, newer_than_source, -total.bit_count())
                        if grade > best_grade:
                            best_grade = grade
                            best = {'supports':[list(bits(m)) for m in (p,q,r)], 'requires_this_round':bool(new),
                                    'requires_post_source_law':bool(newer_than_source)}
        output[title] = dict(unread_values=len(by_value), unread_supports=sum(map(len, by_value.values())),
                             counts=dict(found), example=best)
    return output


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--archive', action='store_true')
    args = ap.parse_args()
    start = time.monotonic()
    rows = []
    all_stages = Counter()
    groups = ['census','heldout'] if args.archive else ['witnesses']
    for group in groups:
        for j, (name, initial) in enumerate(start_items(group)):
            if args.pilot and j >= (32 if args.archive else 1):
                break
            state = previous = initial
            for t in range(3 if args.archive else 4):
                result = read(state, previous, initial)
                all_stages[group,t] += 1
                if result['class_bits'] >= 2:
                    rows.append(dict(group=group, start=name, round=t, **result))
                if t == (2 if args.archive else 3):
                    break
                previous = state
                state, status = grow(state)
                if status != 'funded':
                    break
    stem = ('paths_archive' if args.archive else 'paths_witness')+('_pilot' if args.pilot else '')
    (HERE / (stem+'.json')).write_text(json.dumps({'seconds':round(time.monotonic()-start,3),
                    'stages':{str(key):n for key,n in all_stages.items()},'eligible_stages':rows},indent=2)+'\n')
    print(stem, len(rows), {key:sum(bool(r[key]['example']) for r in rows) for key in ['shortest_paths','all_paths']})
    for r in rows:
        if any(r[key]['example'] for key in ['shortest_paths','all_paths']):
            print(r['start'], r['round'], r['shortest_paths']['example'], r['all_paths']['example'])


if __name__ == '__main__':
    main()
