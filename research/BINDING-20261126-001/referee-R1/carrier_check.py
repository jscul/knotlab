"""Look for ternary parity on separately enumerated supports, then test its origin."""
import argparse
from collections import defaultdict, deque
from itertools import combinations, product
from functools import reduce
from operator import xor
import json
from pathlib import Path
import resource
import time

HERE = Path(__file__).resolve().parent
LIMIT = 2 * 1024 ** 3
resource.setrlimit(resource.RLIMIT_AS, (LIMIT, LIMIT))


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def rem(pivots, value):
    for i in sorted(pivots, reverse=True):
        if value >> i & 1:
            value ^= pivots[i]
    return value


def basis(rows):
    result = {}
    for row in rows:
        while row:
            i = row.bit_length() - 1
            if i not in result:
                result[i] = row
                break
            row ^= result[i]
    return result


def mask(names):
    return sum(1 << i for i in names)


def moves_of(supports):
    # Complete a loose distinction at one extra holder. Every shortest
    # nonempty allowed change through d is a shortest cycle containing d.
    holders = defaultdict(list)
    for k, support in enumerate(supports):
        for d in support:
            holders[d].append(k)
    ends = {d: who if len(who) == 2 else who + [len(supports)] for d, who in holders.items()}
    links = defaultdict(list)
    for d, (u, v) in ends.items():
        links[u].append((v, d))
        links[v].append((u, d))
    moves = set()
    for d, (u, v) in ends.items():
        dist = {v: 0}
        queue = deque([v])
        while queue:
            a = queue.popleft()
            if a == u:
                break
            for b, e in links[a]:
                if e != d and b not in dist:
                    dist[b] = dist[a] + 1
                    queue.append(b)
        if u not in dist:
            continue
        todo = [(u, 1 << d)]
        while todo:
            a, changed = todo.pop()
            if a == v:
                moves.add(changed)
            else:
                todo.extend((b, changed | (1 << e)) for b, e in links[a]
                            if e != d and dist.get(b) == dist[a] - 1)
    return holders, moves


def refinement(supports, holders, size_by_round, history):
    def partition(keys):
        codes = {key: j for j, key in enumerate(sorted(set(keys)))}
        return [codes[key] for key in keys]
    ktypes = [sum(k >= count for count in size_by_round[:-1]) if history else 0 for k in range(len(supports))]
    dtypes = [0] * len(holders)
    seen = set()
    while True:
        dnext = partition([(old, tuple(sorted(ktypes[k] for k in holders[i]))) for i, old in enumerate(dtypes)])
        by_type = defaultdict(list)
        for i, key in enumerate(dnext):
            by_type[key].append(i)
        seen.update(mask(group) for group in by_type.values())
        knext = partition([(old, tuple(sorted(dnext[i] for i in support))) for old, support in zip(ktypes, supports)])
        if len(set(knext)) == len(set(ktypes)) and len(set(dnext)) == len(set(dtypes)):
            return seen
        ktypes, dtypes = knext, dnext


def small_supports(signatures):
    # Complete through weight four. Equal move signatures of two disjoint
    # halves mean their union has even parity on every shortest change.
    halves = defaultdict(list)
    for i, x in enumerate(signatures):
        halves[x].append(1 << i)
    for a, b in combinations(range(len(signatures)), 2):
        halves[signatures[a] ^ signatures[b]].append((1 << a) | (1 << b))
    result = set(halves[0])
    for group in halves.values():
        for a, b in combinations(group, 2):
            if a & b == 0:
                result.add(a | b)
    return result


def simple_cycles(holders, limit=10, budget=200000):
    links = defaultdict(list)
    for d, knots in holders.items():
        if len(knots) == 2:
            a, b = knots
            links[a].append((b, 1 << d))
            links[b].append((a, 1 << d))
    cycles = set()
    work = 0
    for first in sorted(links):
        todo = [(first, 1 << first, 0, 0)]
        while todo:
            if work >= budget:
                return cycles, True
            work += 1
            last, visited, used, length = todo.pop()
            for other, bit in links[last]:
                if used & bit or other < first:
                    continue
                if other == first:
                    cycles.add(used | bit)
                elif length + 1 < limit and not visited >> other & 1:
                    todo.append((other, visited | (1 << other), used | bit, length + 1))
    return cycles, False


def stage(supports, history, b_possible):
    names = sorted(set().union(*supports))
    assert names == list(range(len(names)))
    holders, moves = moves_of(supports)
    rows = [mask(s) for s in supports]
    old = basis(rows[:history[0]])
    prior = basis(rows[:history[-2]]) if len(history) > 1 else old
    laws = basis(rows)
    locals_ = [basis([rem(laws, 1 << i) for i in s]) for s in supports]
    mbasis = list(basis(moves).values())
    sig = [sum(((m >> i) & 1) << j for j, m in enumerate(mbasis)) for i in names]
    free = len(names) - len(laws)
    out = dict(knots=len(rows), distinctions=len(names), shortest_moves=len(moves), allowed_rank=free,
               class_bits=free-len(mbasis))
    def read_family(members, *, minimal=False, disjoint=True):
        by_value = defaultdict(list)
        for v in sorted(members, key=lambda x: (x.bit_count(), x)):
            if reduce(xor, (sig[i] for i in bits(v)), 0):
                continue
            value = rem(laws, v)
            if not value or any(rem(local, value) == 0 for local in locals_):
                continue
            if minimal and by_value[value] and v.bit_count() > by_value[value][0].bit_count():
                continue
            by_value[value].append(v)
        best = None
        best_grade = -1
        eligible = 0
        for a, b in combinations(sorted(by_value), 2):
            c = a ^ b
            if c <= b or c not in by_value:
                continue
            for va, vb, vc in product(by_value[a], by_value[b], by_value[c]):
                if disjoint and ((va & vb) or (vb & vc) or (va & vc)):
                    continue
                forced = va ^ vb ^ vc
                if not forced:
                    continue
                eligible += 1
                source_rank = len(basis(rem(old, x) for x in (va, vb, vc)))
                prev_rank = len(basis(rem(prior, x) for x in (va, vb, vc)))
                grade = source_rank + prev_rank
                if best_grade < grade:
                    best_grade = grade
                    best = dict(supports=[list(bits(x)) for x in (va, vb, vc)], nonzero_sum=list(bits(forced)),
                                values_rank=2, rank_old_laws_only=source_rank, rank_previous_laws_only=prev_rank)
        return dict(supports_tested=len(members), unread_values=len(by_value), unread_supports=sum(map(len, by_value.values())),
                    forced_triples=eligible, example=best)
    out['holder_types'] = read_family(refinement(supports, holders, history, False))
    out['holder_types_with_birth_round'] = read_family(refinement(supports, holders, history, True))
    if len(names) <= 145:
        out['minimum_support_through_four'] = read_family(small_supports(sig), minimal=True)
    if b_possible:
        cyc, capped = simple_cycles(holders)
        out['possibly_overlapping_cycles'] = dict(read_family(cyc, disjoint=False), visited_prefix=capped)
    return out


def main():
    from replay_growth import start_items, grow
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    args = ap.parse_args()
    start = time.monotonic()
    result = []
    for index, (name, supports) in enumerate(start_items('witnesses')):
        history = []
        for t in range(4):
            history.append(len(supports))
            row = stage(supports, history, index >= 3)
            result.append(dict(sample=name, round=t, **row))
            if args.pilot or t == 3:
                break
            supports, status = grow(supports)
            if status != 'funded':
                break
        if args.pilot and index == 0:
            break
    (HERE / ('carrier_pilot.json' if args.pilot else 'carriers.json')).write_text(
        json.dumps(dict(seconds=round(time.monotonic() - start, 3), stages=result), indent=2) + '\n')
    for item in result:
        print(item['sample'], item['round'], item['class_bits'], [(k, v['forced_triples']) for k, v in item.items()
                                                                  if isinstance(v, dict)])


if __name__ == '__main__':
    main()
