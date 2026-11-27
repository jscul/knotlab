"""Independent eight-knot samples, inclusion covers, growth comparison and witnesses."""
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import random
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent.parent
sys.path[:0] = [str(RESEARCH / "LATE-VIEWS-20261126-001"), str(RESEARCH / "LOOK-ALIKE-20261126-001")]
import alike
import late

SEED = 41182619
ROUNDS = 9
BOUND = 2200


def connected(s, adj):
    seen = set()
    waiting = [next(iter(s))]
    while waiting:
        v = waiting.pop()
        if v not in seen:
            seen.add(v)
            waiting.extend((adj[v] & s) - seen)
    return seen == s


def sample(rng):
    """Choose labelled pairs, then live knots. Favor just enough loose distinctions to grow."""
    knots = set(range(8))
    adj = {a: set() for a in knots}
    prob = rng.choice([.27, .42, .57, .72])
    stars = [[] for _ in knots]
    for a, b in combinations(sorted(knots), 2):
        if rng.random() < prob:
            adj[a].add(b)
            adj[b].add(a)
            stars[a].append(8*a+b)
            stars[b].append(8*a+b)
    if not connected(knots, adj):
        return
    live = set(rng.sample(sorted(knots), rng.choice([3, 4, 5, 6, 7, 8])))
    if any(len(adj[a]) < 3 for a in knots-live):
        return
    blocks = [neighbours & live for neighbours in adj.values()]
    pairs = {p for block in blocks for p in combinations(sorted(block), 2)}
    groups = []
    for n in range(len(live), 2, -1):
        for members in combinations(sorted(live), n):
            s = set(members)
            if any(s <= t for t in blocks+groups):
                continue
            if all(p in pairs for p in combinations(members, 2)):
                groups.append(s)
    groups.extend(set(p) for p in sorted(pairs) if not any(set(p) <= g for g in groups))
    for a in sorted(live):
        least = max(1, 3-len(adj[a]), sum(a in g for g in groups))
        loose = least + rng.choice([0, 0, 0, 1, 2])
        if loose > 3:
            return
        stars[a].extend(100+4*a+i for i in range(loose))
    return stars


def inspect_map(m):
    overlap = [list(map(sorted, (g, h))) for g, h in combinations(m.cells, 2) if len(g & h) >= 2]
    missing, cover_errors, sizes = [], [], []
    for ids, _, _ in m.pieces:
        sets = {}
        for r in range(1, len(ids)+1):
            for members in combinations(ids, r):
                s = frozenset(members)
                if not s & m.live or not connected(s, m.adj):
                    continue
                if any(1 < len(s & g) < len(g) for g in m.cells):
                    continue
                sets[s] = len(s)-1-sum(len(g)-2 for g in m.cells if g <= s)
        sizes.append(len(sets))
        parents = {}
        for s in sets:  # the dictionary is in increasing cardinality
            maximal = []
            for t in reversed(sets):
                if t < s and not any(t < u for u in maximal):
                    maximal.append(t)
            parents[s] = set(maximal)
            rank_parents = {t for t in sets if t < s and sets[t] == sets[s]-1}
            if rank_parents != parents[s]:
                cover_errors.append([sorted(s), [sorted(t) for t in maximal], [sorted(t) for t in rank_parents]])
            if sets[s] >= 2:
                for a, b in combinations(maximal, 2):
                    if not parents[a] & parents[b]:
                        missing.append([sets[s], sorted(s), sorted(a), sorted(b)])
    return dict(overlap=overlap, missing=missing, cover_errors=cover_errors, valid_counts=sizes)


def view(row, name):
    out = Counter()
    for k, count in row[name]:
        out[json.dumps(k, separators=(',', ':'))] += count
    return out


def checked(stars, law, rounds=ROUNDS, bound=BOUND):
    pred, why = late.predict(stars, rounds, law, general=True)
    if pred is None:
        return {"refusal": why}
    grown = alike.grow(stars, rounds=rounds, bound=bound, knot_law=law)
    rows = list(grown['rows'])
    if grown['end'].startswith('closes'):
        rows.extend([{'n': 0, 'sig0': [], 'sig1': []}] * (rounds-len(rows)))
    misses = {}
    for name in ('sig0', 'sig1'):
        for t, (p, g) in enumerate(zip(pred, rows), 1):
            pcounts, gcounts = view(p, name), view(g, name)
            if pcounts != gcounts:
                misses[name] = dict(round=t, only_predicted=pcounts-gcounts, only_grown=gcounts-pcounts)
                break
    return dict(end=grown['end'], observed=len(grown['rows']), compared=len(rows), misses=misses)


def run(attempts, quota):
    rng = random.Random(SEED)
    counts, used = Counter(), Counter()
    seen = set()
    for i in range(attempts):
        counts['attempted'] += 1
        stars = sample(rng)
        if stars is None:
            continue
        counts['generated'] += 1
        key = tuple(map(tuple, stars))
        if key in seen:
            counts['labelled duplicate'] += 1
            continue
        seen.add(key)
        m = late.Map(stars)
        if m.cls != 'in' or not all(tree for _, tree, _ in m.pieces):
            counts['map declined'] += 1
            continue
        if any(len(ids)>10 or chains>3 for ids, _, chains in m.pieces):
            counts['outside size cut'] += 1
            continue
        flags = inspect_map(m)
        bucket = (m.stratum, bool(flags['overlap']), bool(flags['missing']))
        counts[str(bucket)] += 1
        if used[bucket] >= quota:
            continue
        used[bucket] += 1
        record = dict(attempt=i, stars=stars, stratum=m.stratum, flags=flags)
        for law in ('nae', 'parity'):
            record[law] = checked(stars, law)
        print(json.dumps(record, sort_keys=True), flush=True)
    print(json.dumps(dict(counts), sort_keys=True), file=sys.stderr)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('attempts', type=int)
    p.add_argument('quota', type=int)
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 << 30, 3 << 30))
    start = time.monotonic()
    run(args.attempts, args.quota)
    print(f'{time.monotonic()-start:.3f} seconds', file=sys.stderr)
