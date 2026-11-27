"""Independent finite-core reading and explicit chain-length count."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'LOOK-ALIKE-20261126-001'))
import alike


def roster(families):
    """Maximal pairwise-compatible families lacking a common witness, then uncovered pairs."""
    families = [set(f) for f in families if len(f) >= 2]
    pairs = {p for f in families for p in combinations(sorted(f), 2)}
    compat = defaultdict(set)
    for a, b in pairs:
        compat[a].add(b)
        compat[b].add(a)
    big = []

    def visit(chosen, possible, used):
        if not possible and not used:
            if len(chosen) >= 3 and all(not chosen <= f for f in families):
                big.append(tuple(sorted(chosen)))
            return
        pivot = max(possible | used, key=lambda v: len(possible & compat[v]))
        for v in sorted(possible - compat[pivot]):
            visit(chosen | {v}, possible & compat[v], used & compat[v])
            possible.remove(v)
            used.add(v)

    if pairs:
        visit(set(), set(compat), set())
    covered = {p for group in big for p in combinations(group, 2)}
    return sorted(big + list(pairs - covered))


@dataclass
class Birth:
    grade: int
    support: frozenset
    parents: tuple
    base_chains: tuple
    start_size: int = 0
    fresh_core: int = 0


def map_data(stars, law):
    names = defaultdict(list)
    for i, star in enumerate(stars):
        for d in star:
            names[d].append(i)
    opens = Counter()
    neighbours = [set() for _ in stars]
    for owners in names.values():
        if len(owners) == 1:
            opens[owners[0]] += 1
        else:
            a, b = owners
            neighbours[a].add(b)
            neighbours[b].add(a)
    live = set(opens)
    families = [s & live for s in neighbours]
    groups = roster(families)
    demand = Counter(k for g in groups for k in g)
    if not live or (sum(opens.values()) == 1 and law == 'parity') or any(demand[k] > opens[k] for k in live):
        return None
    cells = [set(g) for g in groups if len(g) > 2]
    maximal = {frozenset(f) for f in families if len(f) >= 2}
    blocks = [b for b in maximal if not any(b < c for c in maximal) and not any(b <= c for c in cells)]
    parts = [{k} for k in live]
    for g in groups:
        touching = [s for s in parts if s.intersection(g)]
        parts = [s for s in parts if s not in touching] + [set.union(*touching)]
    for part in parts:
        incidence = sum(len(h)-1 for h in cells + blocks if h & part) - len(part) + 1
        allowance = sum(max(0, len(b & c) - 1) for b in blocks for c in cells if b & part)
        if incidence != allowance:
            return None
    return opens, groups, demand, parts


def core(stars, law, depth):
    data = map_data(stars, law)
    if data is None:
        return None
    opens, groups, demand, parts = data
    births, carriers = {}, {}
    chains = {}
    next_id = len(stars)
    for k in opens:
        births[k] = Birth(0, frozenset((k,)), (), (), len(stars[k]))
    layer = []
    for g in groups:
        births[next_id] = Birth(1, frozenset(g), tuple(g), ())
        layer.append(next_id)
        next_id += 1
    for k in sorted(opens):
        for _ in range(opens[k] - demand[k]):
            base = next_id
            chains[base] = tuple((base, j) for j in range(max(0, 3-opens[k])))
            carriers[base] = k
            births[next_id] = Birth(1, frozenset((k, base)), (k,), chains[base])
            layer.append(next_id)
            next_id += 1
    for grade in range(2, depth + 2):
        by_parent = defaultdict(list)
        for i in layer:
            for p in births[i].parents:
                by_parent[p].append(i)
        layer = []
        for g in roster(by_parent.values()):
            s = frozenset.union(*(births[i].support for i in g))
            ch = tuple(sorted(e for b in s for e in chains.get(b, ())))
            births[next_id] = Birth(grade, s, tuple(g), ch)
            for i in g:
                births[i].fresh_core += 1
            layer.append(next_id)
            next_id += 1
        if not layer:
            break
    for part in parts:
        bases = {b for b, k in carriers.items() if k in part}
        if any(chains[b] for b in bases) or (law == 'parity' and len(parts) == 1):
            continue
        piece = part | bases
        for i, b in list(births.items()):
            if b.grade <= depth and b.support == piece and b.fresh_core == 0:
                b.fresh_core += 1
                births[next_id] = Birth(b.grade + 1, b.support | {next_id}, (i,),
                                         ((next_id, 0), (next_id, 1)))
                next_id += 1
    return births


def allocations(chains, remaining, pos=0):
    if pos == len(chains):
        if not remaining:
            yield ()
        return
    for n in range(remaining + 1):
        for tail in allocations(chains, remaining - n, pos + 1):
            yield ((chains[pos], n),) + tail if n else tail


def kinds(births, i, lengths):
    def shallow(i, occupied):
        b = births[i]
        if b.grade == 0:
            return ('start', 0, 0, b.start_size)
        keep = [p for p in b.parents if occupied.issubset(births[p].base_chains)]
        p = len(keep) + len(occupied)
        f = b.fresh_core + len(b.base_chains)
        return ('join' if p > 1 else 'offshoot', p, f, p + f)

    b = births[i]
    occupied = {e for e, n in lengths}
    s = shallow(i, occupied)
    parent_kinds = [shallow(p, occupied) for p in b.parents if occupied.issubset(births[p].base_chains)]
    for e, n in lengths:
        parent_kinds.append(shallow(i, occupied - {e} if n == 1 else occupied))
    return s, (s, tuple(sorted(parent_kinds)))


def predict(stars, law, depth):
    births = core(stars, law, depth)
    if births is None:
        return None
    rows = [(Counter(), Counter()) for _ in range(depth)]
    for i, b in births.items():
        if not 1 <= b.grade <= depth:
            continue
        for t in range(b.grade, depth + 1 if b.base_chains else b.grade + 1):
            for lengths in allocations(b.base_chains, t - b.grade):
                a, v = kinds(births, i, lengths)
                rows[t - 1][0][a] += 1
                rows[t - 1][1][v] += 1
    return rows


def observed(row):
    return (Counter({tuple(k): n for k, n in row['sig0']}),
            Counter({(tuple(k), tuple(map(tuple, ps))): n for (k, ps), n in row['sig1']}))


def compare(stars, law, depth):
    pred = predict(stars, law, depth)
    if pred is None:
        return None
    growth = alike.grow(stars, depth, knot_law=law)
    actual = list(map(observed, growth['rows']))
    if growth['end'].startswith('closes'):
        actual.extend([(Counter(), Counter())] * (depth - len(actual)))
    first = [next((t for t, (g, p) in enumerate(zip(actual, pred), 1) if g[r] != p[r]), None) for r in (0, 1)]
    return {'end': growth['end'], 'tested': len(actual), 'first': first,
            'grown': [sum(g[0].values()) for g in actual], 'predicted': [sum(p[0].values()) for p in pred]}
