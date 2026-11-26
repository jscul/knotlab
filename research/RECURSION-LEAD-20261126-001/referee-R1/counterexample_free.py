"""Search the one-birth case left by counting distinctions in a free return.

The input is a connected, simple sharing pattern and a nonempty set of its
holders each bearing exactly one loose distinction. A single implied birth
uses all that stock when the whole set forms one group (or is one offshoot).
It adds no fresh distinctions. Enumerate every tied shortest change in the
grown parity relation and test a return by exact incidence isomorphism.

Why the search can be restricted to one implied birth on a connected start
---------------------------------------------------------------------------
Every distinction in the exchange is open under its exchanged parity rules.
For a distinction in a move, take the incidence row of any grown holder
containing the distinction and restrict it to the exchanged distinctions.
That row has even intersection with every allowed change, including every
move. It therefore gives an exchanged change flipping the given distinction.
If the exchange is isomorphic to the start, every distinction of the start
is open, too.

Ordinary growth extends every old allowed state. A birth with two or more
fresh distinctions can flip any one by flipping a pair. With one fresh
distinction it can flip that one when its old input parity can vary. On a
connected start, a nonempty subset of the loose distinctions has implied
even parity only when it contains them all: in any sum of old holder rows
that erases every shared distinction, the two holders of each shared
distinction must have the same coefficient. The one implied birth thus
spends all the loose stock. Its next demand is zero because there is no
second newborn and its ordinary fresh count is zero. All fresh distinctions
that actually appear in ordinary growth on such a start are therefore open.
The exchange retains every open distinction, taking a shortest change
through it. Its size in distinctions is the starting size plus the number
of fresh distinctions whenever all the starting distinctions are open.
Consequently a free return requires zero fresh distinctions, and the funded
growth consists solely of the one implied birth. Ordinary growth closes at
that point. Even before the birth the allowed states and the exchange were
the same. Counting around a finite orbit of connected starts gives the same
zero-fresh requirement at each step.

At least five loose distinctions are necessary in the remaining case.
A doubled shared distinction would yield a two-place move. In the simple
graph of the completed sharing pattern each nonempty even set of distinctions
splits into cycles of at least three. The sum of the move rows is just the
set of distinctions held once in the exchange (lawful exchanges have at most
two holders). Isomorphism gives as many of these as initially loose, one at
each of different holders: each supplied parent has paid one distinction
to the single birth. Every cycle in their sum must be strictly longer than
the unique move through any of its distinctions: a tie would have put the
cycle itself in the exchange, with several loose distinctions in one holder.
This excludes one to three loose distinctions, and with four forces each
live parent to have three places, two of which it shares with old holders.

With four parents, any parent having no other live neighbour would have
three distinct shortest four-place changes through its newborn link, one
via a shared old neighbour with each other parent. Thus each live parent
has an old live neighbour. Their four sets of two old neighbours must
intersect in pairs with empty global intersection to fund the sole birth.
Such a family consists of the three different pairs from a set of three
witnesses, with possible repetitions. At least two of those witnesses are
live so that every pair contains a live neighbour. Each live witness must
use its two old places on the other two witnesses because it cannot be its
own neighbour. A fourth live parent would lie outside the three witnesses
and could find at most one witness with a place for it. This excludes four.
"""

import argparse
from collections import Counter, defaultdict, deque
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
import time

import networkx as nx


def covered_by_one_birth(old, live):
    if len(live) == 1:
        return True
    neighbours = [set(old[a]) for a in live]
    if any(not a & b for a, b in combinations(neighbours, 2)):
        return False
    return len(live) == 2 or not set.intersection(*neighbours)


def moves_of(completed):
    """Each open distinction closes a shortest route between its two holders."""
    edges = list(completed.edges)
    neighbours = [[] for _ in completed]
    for index, (a, b) in enumerate(edges):
        neighbours[a].append((b, index))
        neighbours[b].append((a, index))
    moves = set()
    for excluded, (a, b) in enumerate(edges):
        queue = deque([a])
        depth = {a: 0}
        ways = defaultdict(list)
        while queue:
            v = queue.popleft()
            if b in depth and depth[v] >= depth[b]:
                break
            for w, other in neighbours[v]:
                if other == excluded:
                    continue
                if w not in depth:
                    depth[w] = depth[v] + 1
                    queue.append(w)
                if depth[w] == depth[v] + 1:
                    ways[w].append((v, other))
        if b not in depth:
            continue
        pending = [(b, 1 << excluded)]
        while pending:
            v, partial = pending.pop()
            if v == a:
                moves.add(partial)
            else:
                pending.extend((w, partial | (1 << e)) for w, e in ways[v])
    return edges, sorted(moves)


def incidence(rows):
    graph = nx.Graph()
    for a, places in enumerate(rows):
        graph.add_node(('holder', a), kind=0)
        for named in places:
            graph.add_node(('distinction', named), kind=1)
            graph.add_edge(('holder', a), ('distinction', named))
    return graph


def compare(old, live):
    grown = old.copy()
    born = len(old)
    grown.add_edges_from((a, born) for a in live)
    edges, moves = moves_of(grown)
    arities = [mask.bit_count() for mask in moves]
    held = [sum(mask >> e & 1 for mask in moves) for e in range(len(edges))]
    result = {
        'lawful': bool(held) and bool(moves) and min(arities) >= 3 and max(held) <= 2,
        'exchange covers every distinction': all(held),
        'number of holders agrees': len(moves) == len(old),
    }
    result['arity multiset agrees'] = sorted(arities) == sorted(grown.degree(v) for v in old)
    if not all(result.values()):
        return result, False
    original = [[e for e, ends in enumerate(edges) if v in ends] for v in old]
    exchanged = [[e for e in range(len(edges)) if mask >> e & 1] for mask in moves]
    same = nx.is_isomorphic(incidence(original), incidence(exchanged),
                            node_match=lambda a, b: a['kind'] == b['kind'])
    return result, same


def exclusion_keys(n):
    """Rebuild only the frozen input labels needed to exclude overlapping starts."""
    if n not in (6, 7):
        return []
    raw = Path(__file__).resolve().parents[1] / 'recur_heldout.jsonl'
    expected = [r for line in raw.read_text().splitlines()
                if (r := json.loads(line))['knots'] == n]
    pairs = list(combinations(range(n), 2))
    rng = random.Random(20261206 + n)
    admitted = []
    for recorded in expected:
        while True:
            edges = [pr for pr in pairs if rng.random() < 1 / 3]
            multiplicities = [rng.choice((1, 2)) for _ in edges]
            loose = [rng.choice((0, 1, 2)) for _ in range(n)]
            if sum(multiplicities) + sum(loose) > 18:
                continue
            degrees = [0] * n
            for (a, b), m in zip(edges, multiplicities, strict=True):
                degrees[a] += m
                degrees[b] += m
            if any(d + l < 3 for d, l in zip(degrees, loose, strict=True)):
                continue
            pattern = nx.empty_graph(n)
            pattern.add_edges_from(edges)
            if nx.is_connected(pattern):
                break
        assert loose == recorded['loose'] and max(degrees) == recorded['most shared distinctions at a knot']
        if all(m == 1 for m in multiplicities) and max(loose) <= 1 and sum(loose):
            nx.set_node_attributes(pattern, dict(enumerate(loose)), 'loose')
            admitted.append(pattern)
    return admitted


def atlas_cases(n, limit, audit):
    old_graphs = [g for g in nx.graph_atlas_g() if len(g) == n and nx.is_connected(g)]
    random.Random(367 + n).shuffle(old_graphs)
    excluded = exclusion_keys(n)
    audit['old connected sharing graphs in complete list'] = len(old_graphs)
    audit['frozen labelled draws with simple sharing and unit loose stocks'] = len(excluded)
    for label, old in enumerate(old_graphs[:limit]):
        audit['old sharing graphs tried'] += 1
        audit['nonempty subsets of old holders before screening'] += (1 << n) - 1
        for size in range(1, n + 1):
            if n <= 5 and old.number_of_edges() + size <= 12:
                continue
            for live in combinations(old, size):
                if any(old.degree(v) + int(v in live) < 3 for v in old):
                    continue
                audit['markings outside census bound with at least three places per holder'] += 1
                if not covered_by_one_birth(old, live):
                    continue
                audit['funded single implied birth before removing frozen draws'] += 1
                if excluded:
                    nx.set_node_attributes(old, {v: int(v in live) for v in old}, 'loose')
                    if any(nx.is_isomorphic(old, g, node_match=lambda a, b: a['loose'] == b['loose'])
                           for g in excluded):
                        audit['markings isomorphic to a frozen draw removed'] += 1
                        continue
                yield label, old, live


def colourings(p):
    """Name the three supplied sets by first appearance."""
    for tail in product(range(3), repeat=p-1):
        word = (0,) + tail
        if 1 in word and 2 in word and word.index(1) < word.index(2):
            yield word


def witness_cases(p, limit, audit):
    # Every two live parents meet a common one of the three other holders.
    # Each of the three omitted labels occurs, so none witnesses the entire set.
    live = tuple(range(p))
    donors = list(combinations(range(p, p+3), 2))
    linear = [(a, a+1) for a in range(p-1)]
    arrangements = [('chain', linear), ('ring', linear + [(p-1, 0)])]
    if not p % 2:
        arrangements.append(('pairs', linear[::2]))
    audit['all words giving all three labels in order of first appearance'] = (3**p - 3*2**p + 3) // 6
    audit['full family before live meeting and arity screens'] = (
        audit['all words giving all three labels in order of first appearance'] * len(arrangements) * 8)
    included = 0
    for colors in colourings(p):
        matching = [(name, links) for name, links in arrangements
                    if all(colors[a] != colors[b] for a, b in links)]
        if not matching:
            continue
        if limit is not None and included == limit:
            break
        included += 1
        audit['eligible words used'] += 1
        for arrangement, links in matching:
            base = nx.empty_graph(p+3)
            base.add_edges_from(links)
            base.add_edges_from((v, p+j) for v in live for j in range(3) if j != colors[v])
            for selected in range(8):
                old = base.copy()
                old.add_edges_from(pair for j, pair in enumerate(donors) if selected >> j & 1)
                if any(old.degree(w) < 3 for w in range(p, p+3)):
                    continue
                audit['designs after live meeting and arity screens'] += 1
                assert covered_by_one_birth(old, live)
                yield (arrangement, colors, selected), old, live


def evaluate(cases):
    counts = Counter()
    per_loose = defaultdict(Counter)
    positives = []
    for label, old, live in cases:
        facts, returns = compare(old, live)
        facts['funded single implied birth'] = True
        facts['lawful with matching holder count'] = facts['lawful'] and facts['number of holders agrees']
        facts['lawful with matching count and arities'] = facts['lawful'] and facts['arity multiset agrees']
        facts['returns'] = returns
        counts.update({key: int(value) for key, value in facts.items()})
        per_loose[len(live)].update({key: int(facts[key]) for key in ('funded single implied birth', 'lawful', 'returns')})
        if returns:
            positives.append({'case': label, 'holders': len(old), 'shared': list(old.edges), 'loose': live})
    return {'counts': counts, 'by loose count': per_loose, 'returns': positives}


def controls():
    result = {}
    for n in (4, 5):
        edges, moves = moves_of(nx.wheel_graph(n + 1))
        equations = [sum(1 << idx for idx, ends in enumerate(edges) if v in ends) for v in range(n+1)]
        allowed = [x for x in range(1, 1 << len(edges))
                   if all((x & row).bit_count() % 2 == 0 for row in equations)]
        direct = set()
        for j in range(len(edges)):
            options = [x for x in allowed if x >> j & 1]
            least = min(x.bit_count() for x in options)
            direct.update(x for x in options if x.bit_count() == least)
        assert direct == set(moves)
        ring = nx.cycle_graph(n)
        facts, returns = compare(ring, tuple(ring))
        assert all(facts.values()) and returns and not covered_by_one_birth(ring, tuple(ring))
        result[n] = {'directly rebuilt moves': len(moves), 'returns if sole birth supplied': returns,
                     'ordinary growth makes that sole birth': False}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('family', choices=['atlas', 'witness'])
    parser.add_argument('sizes', type=int, nargs='+')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    report = {
        'family': args.family, 'sizes': args.sizes, 'pilot prefix per size': args.limit,
        'counting': ('One old simple connected sharing graph per isomorphism type; every subset of '
                     'its displayed holders marked live. Markings can repeat up to isomorphism. '
                     'One loose distinction at each marked holder, none elsewhere. Excludes the frozen starts.'
                     if args.family == 'atlas' else
                     'One count per listed choice. Live holders are in a chain, ring, or consecutive '
                     'pairs. Each meets two of three other holders, chosen by a three-symbol word '
                     'in order of first appearance. Adjacent live holders omit different symbols. '
                     'Test all eight choices of meetings among the three other holders and require '
                     'at least three places each. Renamings can repeat. Six or more live holders '
                     'give at least nine total, disjoint from the frozen sizes.'),
        'control': controls(),
        'sizes tested': {},
    }
    for size in args.sizes:
        tick = time.perf_counter()
        audit = Counter()
        cases = (atlas_cases(size, args.limit, audit) if args.family == 'atlas'
                 else witness_cases(size, args.limit, audit))
        outcome = evaluate(cases)
        outcome['generation counts'] = audit
        outcome['elapsed seconds'] = round(time.perf_counter()-tick, 4)
        report['sizes tested'][size] = outcome
    report['elapsed seconds'] = round(time.perf_counter()-start, 4)
    report['peak resident KiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    for n, row in report['sizes tested'].items():
        print(n, row['counts'], row['elapsed seconds'])


if __name__ == '__main__':
    main()
