"""Search asymmetric weighted holders with two independent exterior attachments."""

import argparse
from collections import Counter
from itertools import combinations, product
import json

import numpy as np

from weighted_core import INF


def connected(neighbors, side):
    pending = side & -side
    seen = pending
    while pending:
        first = pending & -pending
        pending ^= first
        new = neighbors[first.bit_length()-1] & side & ~seen
        seen |= new
        pending |= new
    return seen == side


def cut_names(sites, edges):
    number = {name: i for i, name in enumerate(sites)}
    endpoints = [(1 << number[a], 1 << number[b]) for _, a, b in edges]
    adjacent = [0] * len(sites)
    for a,b in endpoints:
        adjacent[a.bit_length()-1] |= b
        adjacent[b.bit_length()-1] |= a
    all_sites = (1 << len(sites))-1
    if any(not connected(adjacent, all_sites ^ (1 << i)) for i in range(len(sites)-1)):
        return None
    return [sum(1 << j for j, (a,b) in enumerate(endpoints) if bool(side & a) != bool(side & b))
            for side in range(1, 1 << (len(sites)-1))
            if connected(adjacent, side) and connected(adjacent, all_sites ^ side)]


class Deck:
    def __init__(self, sites, edges, supports):
        self.sites = sites
        self.edges = edges
        self.names = [name for name, _, _ in edges]
        self.index = {name: i for i, name in enumerate(self.names)}
        pairs = (('ha', 'hc'), ('va', 'vc'), ('ra', 'rc'))
        self.swapped = {a: b for pair in pairs if pair[0] in self.index for a,b in (pair, pair[::-1])}
        self.supports = np.array(supports, dtype=np.int64)
        self.cut_matrix = ((self.supports[:, None] >> np.arange(len(edges))) & 1).astype(np.int16)
        self.select = {}

    def marks(self, query):
        mask = sum(1 << self.index[name] for name in query)
        if mask not in self.select:
            self.select[mask] = np.flatnonzero(self.supports & mask == mask)
        return self.select[mask]

    def minimum(self, cuts, query):
        return cuts[:, self.marks(query)].min(axis=1, initial=INF)

    def targets(self):
        for group in ('v', 'h'):
            yield (group + 'a', group + 'b'), (group + 'c', group + 'b')

    def comparisons(self, order):
        for query in combinations(self.names, order):
            moved = tuple(self.swapped.get(name, name) for name in query)
            if sorted(query) < sorted(moved):
                yield query, moved

    def applicable(self, highest=3):
        return all(bool(len(self.marks(a))) == bool(len(self.marks(b)))
                   for order in range(1, highest+1) for a,b in self.comparisons(order))


def layout(has_d, shield_neighbors, relay):
    arms = 'abcd' if has_d else 'abc'
    sites = ['h0', 'h1', 'v', *arms, 'u', 'w'] + (['r'] if relay else []) + ['o']
    edges = [(prefix + arm, origin, arm) for arm in arms
             for prefix, origin in [('h', 'h0' if arm in 'ab' else 'h1'), ('v', 'v')]]
    edges += [('hu', 'h0', 'u'), ('hw', 'h1', 'w'), ('ou', 'o', 'u'), ('ow', 'o', 'w')]
    edges += [('v' + arm, 'v', arm) for arm in shield_neighbors]
    edges += [('r' + arm, 'r', arm) for arm in relay]
    supports = cut_names(sites, edges)
    return None if supports is None else Deck(sites, edges, supports)


def shapes():
    for has_d in (False, True):
        arms = 'abduw' if has_d else 'abuw'
        for mask in range(1 << len(arms)):
            connections = ''.join(arm for i,arm in enumerate(arms) if mask & (1 << i))
            if 'a' in connections:
                connections += 'c'
            if 0 < len(connections) < 3:
                continue
            for via_v in ('', 'u', 'w', 'uw'):
                yield has_d, via_v, connections


def weights(deck, maximum_hub, maximum_test, prices):
    has_d = 'd' in deck.sites
    tests = 'abd' if has_d else 'ab'
    arms = [tuple((a,b) for a,b in product(range(1, maximum_test+1), repeat=2)
                  if a+b+int('r'+arm in deck.index) >= 3) for arm in tests]
    hub_weights = range(1, maximum_hub+1)
    vectors = []
    for test_weights in product(*arms):
        initial = dict(zip((prefix+arm for arm in tests for prefix in ('h','v')),
                           (w for pair in test_weights for w in pair), strict=True))
        initial['hc'], initial['vc'] = initial['ha'], initial['va']
        for hu, hw, ou, ow in product(hub_weights, hub_weights, prices, prices):
            # The all-symmetric and fully present layouts are assigned to the
            # separate uniform search.
            if has_d and len(set(test_weights)) == 1 and hu == hw and ou == ow:
                if ('vu' in deck.index) == ('vw' in deck.index) and ('ru' in deck.index) == ('rw' in deck.index):
                    if len({('r'+x in deck.index) for x in 'abcd'}) == 1:
                        continue
            trial = {**initial, 'hu': hu, 'hw': hw, 'ou': ou, 'ow': ow}
            vectors.append([trial.get(name, 1) for name in deck.names])
    return np.array(vectors, dtype=np.int16).reshape((-1, len(deck.names)))


def describe(deck, weights, future, target, values):
    costs = weights[None, :] @ deck.cut_matrix.T
    candidates = []
    for left, right in deck.comparisons(4):
        a,b = int(deck.minimum(costs,left)[0]), int(deck.minimum(costs,right)[0])
        if a != b:
            candidates.append({'query': left, 'image': right, 'K': [a,b]})
    weight_deck = [[name, a, b, int(w)] for (name,a,b),w in zip(deck.edges, weights, strict=True)]
    return {'sites': deck.sites, 'weighted_meetings': weight_deck, 'map': deck.swapped,
            'future_exterior_costs': future, 'target': target, 'successor_K': values,
            'old_four_reading_differences': len(candidates), 'first_four_reading_difference': candidates[0] if candidates else None}


def search(maximum_hub, maximum_test, prices):
    counts = Counter()
    output = []
    price_indices = ('ou', 'ow')
    for has_d, via_v, relay in shapes():
        counts['layouts'] += 1
        deck = layout(has_d, via_v, relay)
        if deck is None or not deck.applicable():
            counts['structural_rejections'] += 1
            continue
        present = weights(deck, maximum_hub, maximum_test, prices)
        counts['weighted_decks'] += len(present)
        if not len(present):
            continue
        old = present @ deck.cut_matrix.T
        sides = np.array([deck.index[name] for name in price_indices])
        old_two = np.arange(len(present))
        for order in (1,2):
            for left,right in deck.comparisons(order):
                active = old[old_two]
                old_two = old_two[deck.minimum(active,left) == deck.minimum(active,right)]
                if not len(old_two):
                    break
            if not len(old_two):
                break
        counts['pair_and_lower_survivors'] += len(old_two)
        if not len(old_two):
            continue
        for shrink in ((0,), (1,), (0,1)):
            after = old[old_two].copy()
            after -= (present[old_two][:, sides[list(shrink)]] - 1) @ deck.cut_matrix[:, sides[list(shrink)]].T
            hitting = np.zeros(len(old_two), dtype=bool)
            for left,right in deck.targets():
                before, following = deck.minimum(after,left), deck.minimum(after,right)
                hitting |= before < following
            promising = old_two[hitting]
            counts['pair_breaks_with_old_pairs_carried'] += len(promising)
            for left,right in deck.comparisons(3):
                active = old[promising]
                promising = promising[deck.minimum(active,left) == deck.minimum(active,right)]
                if not len(promising):
                    break
            counts['full_current_survivors'] += len(promising)
            for index in promising:
                now = present[index]
                future = [1 if i in shrink else int(now[side]) for i,side in enumerate(sides)]
                next_weights = now.copy()
                next_weights[sides] = future
                next_cuts = next_weights[None,:] @ deck.cut_matrix.T
                for left,right in deck.targets():
                    a,b = int(deck.minimum(next_cuts,left)[0]), int(deck.minimum(next_cuts,right)[0])
                    if a < b:
                        output.append(describe(deck, now, future, [left,right], [a,b]))
                        break
    return {'parameters': {'maximum_hub': maximum_hub, 'maximum_test':maximum_test, 'prices':prices},
            'counts': dict(counts), 'examples': output}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hub', type=int, default=6)
    parser.add_argument('--test', type=int, default=2)
    parser.add_argument('--prices', type=int, nargs='+', default=[2,3,4])
    args = parser.parse_args()
    print(json.dumps(search(args.hub,args.test,args.prices), indent=2))


if __name__ == '__main__':
    main()
