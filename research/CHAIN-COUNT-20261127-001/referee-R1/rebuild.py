"""Independent finite node core, extended nodes, and checks against ordinary growth."""
import argparse
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path
import random
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'LOOK-ALIKE-20261126-001'))
import alike


def cliques(neighbors):
    def visit(group, pool, seen):
        if not pool and not seen:
            yield frozenset(group)
        else:
            pivot = max(pool | seen, key=lambda x: len(pool & neighbors[x]))
            for x in sorted(pool - neighbors[pivot]):
                yield from visit(group | {x}, pool & neighbors[x], seen & neighbors[x])
                pool.remove(x)
                seen.add(x)
    return visit(set(), set(neighbors), set())


def families(parents):
    neighbors = {x: set() for x in parents}
    for x, y in combinations(parents, 2):
        if parents[x] & parents[y]:
            neighbors[x].add(y)
            neighbors[y].add(x)
    big = [g for g in cliques(neighbors) if len(g) >= 3 and
           not set.intersection(*(set(parents[x]) for x in g))]
    pairs = [frozenset((x, y)) for x in parents for y in neighbors[x] if x < y
             and not any(x in g and y in g for g in big)]
    return sorted(big + pairs, key=lambda g: tuple(sorted(g)))


def realize(n, blocks, opens):
    # Each witness sees exactly the specified live knots. Additional spent knots
    # keep the presentation connected and every start knot at three places or more.
    holdings = [set() for _ in range(n)]
    def share(a, b):
        key = (min(a, b), max(a, b))
        holdings[a].add(key)
        holdings[b].add(key)
    def witness(block):
        w = len(holdings)
        holdings.append(set())
        for x in block:
            share(x, w)
    for block in blocks:
        witness(block)
    for x in range(n):
        while len(holdings[x]) + opens[x] < 3 or not holdings[x]:
            witness([x])
        for i in range(opens[x]):
            holdings[x].add((-i-1, x))
    spent = len(holdings)
    for _ in range(4):
        holdings.append(set())
    for x in range(n, spent):
        for y in range(spent, spent+3):
            share(x, y)
    for x, y in combinations(range(spent, spent+4), 2):
        share(x, y)
    return [sorted(k) for k in holdings]


def draw(n, blocks, extra):
    memberships = {i: {j for j, b in enumerate(blocks) if i in b} for i in range(n)}
    degree = Counter(i for g in families(memberships) for i in g)
    opens = [max(1, degree[i]) + extra.get(i, 0) for i in range(n)]
    return realize(n, blocks, opens)


class TooLarge(Exception):
    pass


class Core:
    def __init__(self, stars):
        holders = defaultdict(set)
        for i, knot in enumerate(stars):
            for d in knot:
                holders[d].add(i)
        assert all(len(h) <= 2 for h in holders.values())
        nb = [set().union(*(holders[d] for d in knot)) - {i} for i, knot in enumerate(stars)]
        opens = [sum(len(holders[d]) == 1 for d in knot) for knot in stars]
        live = [i for i, count in enumerate(opens) if count]
        self.live = live
        self.parent = {i: frozenset() for i in live}
        self.points = {i: frozenset((i,)) for i in live}
        self.chain = {}  # chain label -> base
        self.level = [live, []]
        self.children = defaultdict(set)
        self.pieces = []
        def add(g, pts, level):
            idx = len(stars) + len(self.parent)
            self.parent[idx] = frozenset(g)
            self.points[idx] = frozenset(pts)
            level.append(idx)
            for x in g:
                self.children[x].add(idx)
        groups = families({i: nb[i] for i in live})
        self.cell_count = sum(len(g) >= 3 for g in groups)
        degree = Counter(i for g in groups for i in g)
        assert all(opens[i] >= degree[i] for i in live)
        q = -1
        for g in groups:
            add(g, g, self.level[1])
        for i in live:
            for _ in range(opens[i] - degree[i]):
                add({i}, {i, q}, self.level[1])
                for _ in range(max(0, 3 - opens[i])):
                    self.chain[len(self.chain)] = q
                q -= 1
        while self.level[-1]:
            last = self.level[-1]
            if len(last) > 32 or len(self.level) > 18:
                raise TooLarge
            nxt = []
            for g in families({i: self.parent[i] for i in last}):
                add(g, set.union(*(set(self.points[x]) for x in g)), nxt)
            self.level.append(nxt)
        self.tops = [x for row in self.level[1:] for x in row if not self.children[x]]
        self.bases = {x: frozenset(self.chain.values()) & pts for x, pts in self.points.items()}

    def failures(self):
        bad = set()
        for row in self.level[1:]:
            for x,y in combinations(row, 2):
                for c,d in combinations(self.parent[x] & self.parent[y], 2):
                    if any(self.bases[k] for k in self.parent[c] & self.parent[d]):
                        bad.add('N1')
            for x in row:
                for t,u in combinations(self.parent[x], 2):
                    b = self.bases[t] & self.bases[u]
                    if b and not any(b <= self.bases[k] for k in self.parent[t] & self.parent[u]):
                        bad.add('N2')
            universe = sorted(set(self.chain.values()))
            for j in range(1, len(universe)+1):
                for b in combinations(universe, j):
                    candidates = {x: {k for k in self.parent[x] if set(b) <= self.bases[k]}
                                  for x in row if set(b) <= self.bases[x]}
                    for g in families(candidates):
                        if len(g) >= 3 and not set.intersection(*(self.children[x] for x in g)):
                            bad.add('N3')
        return ''.join(sorted(bad)) or 'pass'

    def predictions(self, stars, law, horizon):
        # ids are (core node, multiset of chain labels); rank zero uses empty multiset.
        births = defaultdict(dict)
        starts = {(i, ()): ('start', 0, 0, len(stars[i])) for i in self.live}
        for rank, level in enumerate(self.level[1:], 1):
            for c in level:
                labels = sorted(e for e,q in self.chain.items() if q in self.points[c])
                relay = c in self.tops and not labels and (law == 'nae' or len(self.tops) > 1)
                f = len(self.children[c]) + len(labels) + int(relay)
                for round_ in range(rank, horizon+1):
                    for vec in combinations_with_replacement(labels, round_ - rank):
                        needed = {self.chain[e] for e in vec}
                        parents = {(p, vec) for p in self.parent[c] if needed <= self.points[p]}
                        for e in set(vec):
                            i = vec.index(e)
                            parents.add((c, vec[:i]+vec[i+1:]))
                        births[round_][c, vec] = (parents, f)
                if relay:
                    for age in range(horizon - rank):
                        for a in range(age+1):
                            b = age-a
                            k = ('relay', c, a, b)
                            parents = set()
                            if a:
                                parents.add(('relay', c, a-1, b))
                            if b:
                                parents.add(('relay', c, a, b-1))
                            births[rank+age+1][k] = (parents or {(c, ())}, 2)
        return starts, births


def check_growth(stars, core, law, horizon):
    sig, levels = core.predictions(stars, law, horizon)
    rows = []
    for r in range(1,horizon+1):
        a, b = Counter(), Counter()
        for x, (ps, f) in levels[r].items():
            p = len(ps)
            s = ('offshoot' if p == 1 else 'join', p, f, p+f)
            a[s] += 1
            b[s + (tuple(sorted(sig[k] for k in ps)),)] += 1
            sig[x] = s
        if a:
            rows.append({'n': sum(a.values()), 'sig0': sorted([list(k),v] for k,v in a.items()),
                         'sig1': sorted([[list(k[:4]), [list(t) for t in k[4]]], v] for k,v in b.items())})
    real = alike.grow(stars, horizon, knot_law=law)
    if rows != real['rows'] or real['end'] not in ('rounds', f'closes at round {len(rows)+1}'):
        return ('views', next((i+1 for i,(x,y) in enumerate(zip(rows,real['rows'])) if x != y),
                              min(len(rows),len(real['rows']))+1), real['end'])
    # The public two readings discard identities. Compare incidence using the same
    # black-box round API as grow. Equally parented offshoots have interchangeable names.
    state = alike.eng.from_stars(stars)
    rule = alike.eng.Law('ORD','CANCEL-WAIT',None,law)
    guard = alike.eng.Guard(100)
    ids = {(i, ()): i for i in core.live}
    for r in range(1,len(rows)+1):
        actual = defaultdict(list)
        for b in alike.eng.play_round(state, rule, guard)['births']:
            actual[frozenset(b['parents']),b['f']].append(b['id'])
        for x,(ps,f) in levels[r].items():
            key = frozenset(ids[p] for p in ps), f
            if not actual[key]:
                return ('incidence', r)
            ids[x] = actual[key].pop(0)
        assert not any(actual.values())
    return len(rows), sum(v['n'] for v in rows)


def examples():
    for m in (3,7):
        groups = [(2*j,2*j+1,2*j+2) for j in range(m)]
        blocks = sorted(set(pair for g in groups for pair in combinations(g,2)))
        yield f'{m}-groups-two-ends', draw(2*m+1, blocks, {0:1,2*m:1})
    yield 'one-base-two-chains', realize(1, [], [1])
    yield 'one-knot-two-bases', realize(1, [], [2])
    yield 'one-knot-three-offshoots', realize(1, [], [3])
    yield 'whole-group', draw(4, list(combinations(range(4),2)), {})
    yield 'two-finished-pieces', draw(4, [(0,1),(2,3)], {})
    yield 'finished-plus-chain', draw(4, [(0,1),(2,3)], {0:1})
    yield 'two-overlapping-groups', draw(4, [(0,1),(0,2),(0,3),(1,2),(1,3)], {2:1,3:1})
    yield 'spent-common-witness', draw(4, [(0,1,2),(0,3),(1,3)], {2:1,3:1})


def sample(seed):
    rng = random.Random(seed)
    n = rng.choice([4,5,6,7,8])
    pairs = list(combinations(range(n),2))
    density = rng.choice([.25,.45,.65,.8])
    blocks = [p for p in pairs if rng.random() < density]
    for _ in range(rng.randrange(4)):
        blocks.append(tuple(sorted(rng.sample(range(n),rng.choice([3,4])))))
    if not blocks:
        blocks = [(0,1)]
    # Hanging a pair on a live knot lets a chain reach a family of groups.
    if rng.randrange(2):
        blocks.append((rng.randrange(n), n))
        n += 1
    marks = rng.sample(range(n), rng.randint(1, min(3,n)))
    return draw(n, blocks, {i:1 for i in marks})


def main():
    p = argparse.ArgumentParser()
    p.add_argument('family', choices=['built','sample'])
    p.add_argument('size', type=int)
    p.add_argument('--seed', type=int, default=271126)
    p.add_argument('--rounds', type=int, default=7)
    p.add_argument('--grow', type=int, default=1000000)
    args = p.parse_args()
    cases = examples() if args.family=='built' else (
        (str(s),sample(s)) for s in range(args.seed,args.seed+args.size))
    counts = Counter()
    witnesses = {}
    details = []
    started = time.perf_counter()
    for i,(name,stars) in enumerate(cases):
        if i>=args.size:
            break
        counts['starts'] += 1
        try:
            c = Core(stars)
        except TooLarge:
            counts['core_cut'] += 1
            continue
        verdict = c.failures()
        counts[verdict] += 1
        counts['with_chains'] += bool(c.chain)
        counts['max_cells'] = max(counts['max_cells'],c.cell_count)
        counts['max_nonempty_rank'] = max(counts['max_nonempty_rank'],len(c.level)-2)
        if verdict != 'pass':
            witnesses.setdefault(verdict, name)
        if i >= args.grow:
            continue
        for law in ['nae','parity']:
            if law=='parity' and sum(len(c.children[v]) for v in c.live)==1:
                counts['parity_one_loose_excluded'] += 1
                continue
            result = check_growth(stars,c,law,args.rounds)
            if isinstance(result[0], str):
                counts['mismatch_'+verdict] += 1
                witnesses.setdefault('mismatch_'+verdict, [name,law,result])
            else:
                counts['matched_'+verdict] += 1
                counts['rounds_'+verdict] += result[0]
                counts['births_'+verdict] += result[1]
            if args.family=='built':
                details.append([name, law, c.cell_count, len(c.chain), verdict, result])
    print(json.dumps({'settings':vars(args),'counts':counts,'first':witnesses,'built':details,
                      'seconds':round(time.perf_counter()-started,3)}, indent=2))


if __name__ == '__main__':
    main()
