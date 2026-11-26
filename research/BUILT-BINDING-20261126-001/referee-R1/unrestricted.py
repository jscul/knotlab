"""Read every linear class fact on a bounded roster, and test disjoint representatives."""
import argparse
from collections import Counter, deque
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
import time

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
DATA = STUDY.parent / "FORBID-EDITS-20261126-001"
resource.setrlimit(resource.RLIMIT_AS, (1400 << 20, 1400 << 20))


def mask(names):
    return sum(1 << x for x in names)


def indices(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def basis(rows):
    b = {}
    for v in rows:
        while v:
            p = v.bit_length() - 1
            if p not in b:
                b[p] = v
                break
            v ^= b[p]
    return b


def reduce_by(v, b):
    for p in sorted(b, reverse=True):
        if v >> p & 1:
            v ^= b[p]
    return v


def perpendicular(b, n):
    for free in set(range(n)) - b.keys():
        x = 1 << free
        for p in sorted(b):
            if (b[p] & x).bit_count() % 2:
                x |= 1 << p
        yield x


def supports(n, shared, loose):
    knots = [[] for _ in range(n)]
    name = 0
    for a, b, count in shared:
        for t in range(count):
            knots[a].append(name)
            knots[b].append(name)
            name += 1
    for knot, count in zip(knots, loose):
        knot.extend(range(name, name + count))
        name += count
    return tuple(tuple(k) for k in knots)


def sampled(n, count, seed, limit):
    rng = random.Random(seed)
    pairs = list(combinations(range(n), 2))
    kept = 0
    while kept < count:
        meetings = [p for p in pairs if rng.random() < 1 / 3]
        shared = [(a, b, rng.choice((1, 2))) for a, b in meetings]
        loose = [rng.choice((0, 1, 2)) for _ in range(n)]
        if sum(loose) + sum(k for _, _, k in shared) > limit:
            continue
        rows = supports(n, shared, loose)
        if min(map(len, rows)) < 3:
            continue
        reached = {0}
        for _ in range(n):
            for a, b in meetings:
                if a in reached or b in reached:
                    reached.update((a, b))
        if len(reached) == n:
            yield rows
            kept += 1


def owners(rows):
    held = [[] for _ in range(1 + max(max(r) for r in rows))]
    for k, row in enumerate(rows):
        for d in row:
            held[d].append(k)
    return held


def groups(neighbours, live):
    # Each possible parent pair shares a neighbour. Valid larger groups
    # are maximal mutually eligible sets with no neighbour shared by all.
    live = set(live)
    cand = {x: set() for x in live}
    for neighbours_of_one in neighbours:
        for x, y in combinations(sorted(neighbours_of_one & live), 2):
            cand[x].add(y)
            cand[y].add(x)
    large = []
    def visit(chosen, available, visited):
        if not available and not visited:
            if len(chosen) >= 3 and not set.intersection(*(neighbours[i] for i in chosen)):
                large.append(tuple(sorted(chosen)))
            return
        pivot = max(available | visited, key=lambda x: len(available & cand[x]))
        for x in sorted(available - cand[pivot]):
            visit(chosen | {x}, available & cand[x], visited & cand[x])
            available.remove(x)
            visited.add(x)
    if live:
        visit(set(), live.copy(), set())
    covered = {p for g in large for p in combinations(g, 2)}
    return sorted(large) + [(a, b) for a in sorted(live) for b in sorted(cand[a]) if a < b and (a, b) not in covered]


def grow(rows):
    who = owners(rows)
    loose = [[] for _ in rows]
    nbr = [set() for _ in rows]
    for x, holders in enumerate(who):
        if len(holders) == 1:
            loose[holders[0]].append(x)
        else:
            a, b = holders
            nbr[a].add(b)
            nbr[b].add(a)
    live = [k for k, names in enumerate(loose) if names]
    if not live:
        return None
    plan = groups(nbr, live)
    demand = Counter(k for g in plan for k in g)
    if any(demand[k] > len(loose[k]) for k in live):
        return None
    plan += [(k,) for k in live for _ in range(len(loose[k]) - demand[k])]
    incoming = [iter(names) for names in loose]
    children = [set() for _ in rows]
    for j, g in enumerate(plan):
        for k in g:
            children[k].add(len(rows) + j)
    following = groups(children + [set(g) for g in plan], range(len(rows), len(rows) + len(plan)))
    need = Counter(k for g in following for k in g)
    laws = basis(map(mask, rows))
    born = []
    fresh = len(who)
    for j, g in enumerate(plan):
        paid = tuple(next(incoming[k]) for k in g)
        q = need[len(rows) + j]
        if reduce_by(mask(paid), laws):
            q = max(q, 1, 3 - len(g))
        born.append(tuple(sorted(paid)) + tuple(range(fresh, fresh + q)))
        fresh += q
    return rows + tuple(born)


def small_changes(who, nknots):
    # Shortest per distinction, with all ties. Every change of size <=5
    # is a sum of simple loops of size <=5, so their spans suffice.
    neighbours = [[] for _ in range(nknots + 1)]
    ends = []
    for i, hs in enumerate(who):
        a, b = hs if len(hs) == 2 else (hs[0], nknots)
        ends.append((a, b))
        neighbours[a].append((b, i))
        neighbours[b].append((a, i))
    shortest, bounded = set(), set()
    for i, (a, b) in enumerate(ends):
        dist = {a: 0}
        queue = deque([a])
        while queue:
            v = queue.popleft()
            for w, j in neighbours[v]:
                if i != j and w not in dist:
                    dist[w] = dist[v] + 1
                    queue.append(w)
        if b not in dist:
            continue
        def paths(v, remaining, seen, value):
            if v == a:
                if remaining == 0:
                    yield value
                return
            if dist[v] > remaining:
                return
            for w, j in neighbours[v]:
                if j != i and w not in seen and remaining >= 1:
                    yield from paths(w, remaining - 1, seen | {w}, value | (1 << j))
        for length in sorted({dist[b]} | set(range(dist[b], 5))):
            for v in paths(b, length, {b}, 1 << i):
                if length == dist[b]:
                    shortest.add(v)
                if length <= 4:
                    bounded.add(v)
    return [basis(shortest), basis(bounded)]


def disjoint(values, who, row_count, allowed=None):
    width = len(who)
    stride = row_count + width
    # Independent sums of knot laws change the support of each representative.
    # Each distinction has only one or two holders, so the local truth table is small.
    with Solver() as solver:
        for a, val in enumerate(values):
            start = a * stride
            for d, held in enumerate(who):
                coeff = [start + k + 1 for k in held]
                term = start + row_count + d + 1
                if allowed is not None and d not in allowed:
                    solver.add_clause([-term])
                for bits in product((0, 1), repeat=len(coeff)):
                    result = (sum(bits) + (val >> d & 1)) % 2
                    solver.add_clause([(-k if bit else k) for k, bit in zip(coeff, bits)] + [term if result else -term])
        for d in range(width):
            picks = [a * stride + row_count + d + 1 for a in range(len(values))]
            for x, y in combinations(picks, 2):
                solver.add_clause([-x, -y])
        if solver.solve():
            positive = set(solver.get_model())
            return [[d for d in range(width) if a * stride + row_count + d + 1 in positive] for a in range(len(values))]


def read(rows, count, examples, name, t, n0, previous_layer):
    who = owners(rows)
    n = len(who)
    laws = basis(map(mask, rows))
    for tag, moves in zip(('shortest', 'at most five'), small_changes(who, len(rows))):
        c = count[tag]
        c['stages'] += 1
        dim = n - len(laws) - len(moves)
        if dim < 2:
            continue
        c['two or more independent facts'] += 1
        directions = basis(reduce_by(x, laws) for x in perpendicular(moves, n))
        assert len(directions) == dim
        labels = {0}
        for x in directions.values():
            labels |= {v ^ x for v in labels}
        labels.remove(0)
        for row in rows:
            # A general Boolean function of this knot can determine a linear
            # fact only if the fact is linear on the knot's allowed values.
            b = basis([*laws.values(), *(1 << j for j in row)])
            labels = {v for v in labels if reduce_by(v, b)}
            if not labels:
                break
        c['three or more unread functions'] += len(labels) >= 3
        triples = [(x, y, x ^ y) for x, y in combinations(sorted(labels), 2) if y < (x ^ y) and (x ^ y) in labels]
        c['stages with an unread even triple'] += bool(triples)
        c['unread even triples'] += len(triples)
        found = set()
        for values in triples:
            reads = disjoint(values, who, len(rows))
            if reads:
                assert all(reduce_by(mask(r) ^ f, laws) == 0 for r, f in zip(reads, values))
                assert not any(set(a) & set(b) for a, b in combinations(reads, 2))
                if 'all' not in found:
                    c['stages with disjoint reads'] += 1
                    witness = dict(start=name, round=t, knots=rows, supports=reads)
                    examples[tag].append(witness)
                    found.add('all')
                for title, allowed in [('new distinctions only',range(n0,n)),
                                       ('preceding birth round only',previous_layer)]:
                    if title not in found and allowed:
                        restricted = disjoint(values, who, len(rows), allowed)
                        if restricted:
                            c[title] += 1
                            found.add(title)
                            witness[title] = restricted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--group', choices=['census','heldout','sampled'], required=True)
    args = ap.parse_args()
    start = time.monotonic()
    group = args.group
    if group == 'census':
        roster = ((str(j), supports(*s)) for j, s in enumerate(json.loads((DATA/'starts.json').read_text())))
        maxround = 2
    else:
        sizes = range(6, 9) if group == 'heldout' else range(9, 13)
        size_count, seed, limit = (300, 20261206, 18) if group == 'heldout' else (100, 20261212, 30)
        if args.pilot:
            size_count = 2
        roster = ((f'{n}-{j}', s) for n in sizes for j,s in enumerate(sampled(n,size_count,seed+n,limit)))
        maxround = 3
    archived = {r['start']: r['rounds'] for r in map(json.loads,(STUDY/f'frozen_premises_{group}.jsonl').read_text().splitlines()) if 'start' in r}
    counts, examples, coverage = {}, {'shortest':[], 'at most five':[]}, Counter()
    for j, (name, initial) in enumerate(roster):
        if args.pilot and group == 'census' and j >= 40:
            break
        label = {'heldout':'held out','census':'census','sampled':'sampled'}[group] + ' ' + name
        archived_rounds = {r['round']:r for r in archived[label] if 'premises broken' in r}
        stage = initial
        sizes = [len(owners(initial))]
        coverage['starts'] += 1
        for t in range(maxround+1):
            if t:
                stage = grow(stage)
                assert (stage is not None) == (t in archived_rounds), (label,t)
                coverage['transition statuses compared'] += 1
                if stage is None:
                    break
            n = len(owners(stage))
            if n > 150:
                coverage['trajectories cut past 150 distinctions'] += 1
                break
            if t:
                b = basis(v & ~((1 << len(owners(initial)))-1) for v in map(mask, stage))
                assert n-len(owners(initial))-len(b) == archived_rounds[t]['span']['dim Z_new'], (name,t,n,initial,stage,archived_rounds[t])
                coverage['fixed-start dimensions compared'] += 1
                sizes.append(n)
            c = counts.setdefault(t, {'shortest':Counter(),'at most five':Counter()})
            previous_layer = range(sizes[t-2], sizes[t-1]) if t >= 2 else ()
            read(stage, c, examples, label, t, sizes[0], previous_layer)
    result = dict(roster=group, maxround=maxround, counts=counts, examples=examples, coverage=coverage,
                  seconds=round(time.monotonic()-start,3))
    if not args.pilot:
        (HERE/f'unrestricted_{group}.json').write_text(json.dumps(result, indent=2)+'\n')
    print(group, 'pilot' if args.pilot else 'full', coverage, 'seconds', result['seconds'],
          'witnesses', {k:len(v) for k,v in examples.items()}, flush=True)

if __name__ == '__main__':
    main()
