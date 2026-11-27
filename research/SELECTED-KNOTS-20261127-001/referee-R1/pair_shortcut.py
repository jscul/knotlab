"""Exact costs for three families in an alternating chain, including witnesses."""
import argparse
import json
import resource
from collections import defaultdict, deque
from itertools import combinations
from pathlib import Path
from time import perf_counter


def start(q):
    # A, C0, W0, C1, W1, ..., C(q-1), B. Each W has three shared and no loose.
    rows = [[] for _ in range(2 * q + 1)]
    x = 0
    for i in range(len(rows) - 1):
        copies = 2 if 0 < i < len(rows) - 2 and i % 2 else 1
        for _ in range(copies):
            rows[i].append(x)
            rows[i + 1].append(x)
            x += 1
    for i, row in enumerate(rows):
        if i in (0, len(rows) - 1) or i % 2:
            row.extend([x, x + 1])
            x += 2
    assert min(map(len, rows)) >= 3
    return rows


def holdings(rows):
    held = defaultdict(list)
    for i, row in enumerate(rows):
        for x in row:
            held[x].append(i)
    return held


def groups(rows):
    held = holdings(rows)
    loose = [sorted(x for x in row if len(held[x]) == 1) for row in rows]
    neighbors = [set() for _ in rows]
    for a in held.values():
        if len(a) == 2:
            i, j = a
            neighbors[i].add(j)
            neighbors[j].add(i)
    live = {i for i, xs in enumerate(loose) if xs}
    proposals = sorted({pair for ns in neighbors for pair in combinations(sorted(live & ns), 2)})
    candidates = {i: set() for i in live}
    for i, j in proposals:
        candidates[i].add(j)
        candidates[j].add(i)
    # In this construction every component is a path or a singleton. The
    # general group rule therefore proposes precisely the pairs above.
    assert all(len(ns) <= 2 for ns in candidates.values())
    assert all(not (candidates[i] & candidates[j]) for i, j in proposals)
    return loose, proposals, candidates


def grow(rows):
    loose, pairs, _ = groups(rows)
    inputs = [[loose[i].pop(0), loose[j].pop(0)] for i, j in pairs]
    inputs.extend([x] for xs in loose for x in xs)
    assert len(inputs) > 1
    # Compute provisional demand using one temporary fresh distinction per birth.
    x = max(holdings(rows)) + 1
    provisional = rows + [p + [x + j] for j, p in enumerate(inputs)]
    _, _, next_neighbors = groups(provisional)
    answer = list(rows)
    for j, p in enumerate(inputs, len(rows)):
        count = max(1, 3 - len(p), len(next_neighbors[j]))
        answer.append(p + list(range(x, x + count)))
        x += count
    return answer


def least_changes(rows, tags):
    # Add one bookkeeping holder for all current loose distinctions. Even
    # incidence there follows by summing the genuine laws. Decompose any
    # allowed change into closed walks. Record the cheapest walk of each
    # two-bit signature starting anywhere, then allow sums of walks.
    held = holdings(rows)
    book = len(rows)
    adj = [[] for _ in range(book + 1)]
    for x, hs in held.items():
        a, b = hs if len(hs) == 2 else [hs[0], book]
        tag = tags.get(x, 0)
        adj[a].append((b, x, tag))
        adj[b].append((a, x, tag))
    best = {}
    for v in range(len(adj)):
        origin = (v, 0)
        queue = deque([origin])
        prev = {origin: None}
        while queue:
            cur = queue.popleft()
            u, s = cur
            for w, x, delta in adj[u]:
                nxt = (w, s ^ delta)
                if nxt not in prev:
                    prev[nxt] = (cur, x)
                    queue.append(nxt)
        for sig in (1, 2, 3):
            node = (v, sig)
            if node not in prev:
                continue
            walk = []
            while node != origin:
                node, x = prev[node]
                walk.append(x)
            if sig not in best or len(walk) < len(best[sig]):
                best[sig] = walk
    # With two signature bits, a cheapest sum uses one or two distinct
    # nonzero signatures. Removing an equal pair preserves the target.
    certified = {}
    for sig in (1, 2, 3):
        i, j = [s for s in (1, 2, 3) if s != sig]
        walk = min([best[sig], best[i] + best[j]], key=len)
        support = set()
        for x in walk:
            support.symmetric_difference_update({x})
        assert len(support) == len(walk)
        assert all(len(support.intersection(r)) % 2 == 0 for r in rows)
        assert sum(tags[x] == 1 for x in support & tags.keys()) % 2 == sig % 2
        assert sum(tags[x] == 2 for x in support & tags.keys()) % 2 == sig // 2
        certified[sig] = sorted(support)
    return certified


def literal(rows, tags):
    xs = sorted(holdings(rows))
    laws = [sum(1 << x for x in row) for row in rows]
    a, b = [sum(1 << x for x in tags if tags[x] == color) for color in (1, 2)]
    best = {}
    for w in range(1 << len(xs)):
        if any((w & law).bit_count() % 2 for law in laws):
            continue
        sig = (w & a).bit_count() % 2 + 2 * ((w & b).bit_count() % 2)
        best[sig] = min(w.bit_count(), best.get(sig, len(xs) + 1))
    return best


def run(q, rounds):
    rows = start(q)
    loose, _, candidates = groups(rows)
    assert set(candidates) == {0, 2*q} | set(range(1, 2*q, 2))
    assert not candidates[0] and not candidates[2*q]
    assert all(i+2 in candidates[i] for i in range(1, 2*q-2, 2))
    tags = {x: 1 for x in loose[0]} | {x: 2 for x in loose[-1]}
    result = {'live middle knots': q, 'start': rows, 'outer family supports': [loose[0], loose[-1]],
              'middle family support': [x for xs in loose[1:-1] for x in xs],
              'start holder steps between outer families': 2*q, 'stages': []}
    for t in range(rounds + 1):
        cert = least_changes(rows, tags)
        costs = {k: len(v) for k, v in cert.items()}
        assert costs[1] == costs[2] == 3 + 2*t
        if q == 2 and t == 0:
            assert all(literal(rows, tags)[k] == v for k, v in costs.items())
        result['stages'].append({'round': t, 'knots': len(rows), 'distinctions': len(holdings(rows)),
                                 'measured outer pair': costs[3], 'predicted outer pair': 2*q+2+2*t,
                                 'either outer with middle': costs[1], 'outer pair witness': cert[3]})
        if t < rounds:
            rows = grow(rows)
    return result


if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (1024 << 20, 1024 << 20))
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    t0 = perf_counter()
    cases = [(2, 0), (8, 1)] if args.pilot else [(2, 0), (4, 4), (8, 6), (12, 6)]
    result = [run(q, n) for q, n in cases]
    print('Cases', len(result), 'seconds', round(perf_counter() - t0, 3))
    if not args.pilot:
        Path(__file__).with_name('pair_shortcut.json').write_text(json.dumps(result, indent=2)+'\n')
