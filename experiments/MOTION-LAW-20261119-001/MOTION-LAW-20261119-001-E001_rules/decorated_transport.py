"""Commuting co-enabled physical firings on a corridor oriented by its own nearness."""

from collections import Counter
from itertools import combinations
import json
import math
import random

from sources import DATA, ReturnRule, co_knotted_pairs, source_and_stage


class Reader:
    def __init__(self, structure, stride, increasing=True):
        source = structure.source
        graph = structure.graph
        children = {w: structure.full[w] & source for w in structure.full if w not in source}
        spare = Counter(next(iter(parents)) for parents in children.values() if len(parents) == 1)
        forward = {}
        backward = {}
        self.quads = {}
        self.private = {}
        sign = 1 if increasing else -1
        for v in graph:
            if len(graph[v]) != 2 or spare[v] > 2:
                continue
            ahead = [w for w in graph[v] if spare[w] == (spare[v]+sign) % 3]
            behind = [w for w in graph[v] if spare[w] == (spare[v]-sign) % 3]
            if len(ahead) != 1 or len(behind) != 1:
                continue
            forward[v], backward[v] = ahead[0], behind[0]
            quad = structure.packet((behind[0], v, ahead[0]))
            self.quads[v] = quad
            self.private[v] = {b for b in quad if set(structure.stage.owners[b]) - source}
            assert len(self.private[v]) == 2

        def jump(v, direction, inverse):
            for _ in range(stride):
                w = direction.get(v)
                if w is None or inverse.get(w) != v:
                    return None
                v = w
            return v

        self.guards = []
        for v in self.quads:
            prev = jump(v, backward, forward)
            nxt = jump(v, forward, backward)
            last = jump(nxt, forward, backward) if nxt is not None else None
            word = (prev, v, nxt, last)
            if None not in word and len(set(word)) == 4:
                self.guards.append(word)

    def enabled(self, values):
        occupied = {}
        for v, pair in self.private.items():
            k = len(values & pair)
            occupied[v] = None if k == 1 else k // 2
        fires = set()
        for a, b, c, d in self.guards:
            word = (occupied[a], occupied[b], occupied[c], occupied[d])
            if word == (0, 1, 0, 0):
                fires.add(c)
            elif word == (0, 1, 1, 0):
                fires.add(b)
        return fires


def source(n):
    assert n % 3 == 0 and n >= 9
    return dict(id=f"decorated_ring_{n}", sizes=[4+i%3 for i in range(n)],
                meetings=[[i, (i+1)%n] for i in range(n)])


def physical_checks(n, strides, *, rename=False):
    stars, structure = source_and_stage(source(n))
    if rename:
        rng = random.Random(2601)
        names = sorted(set().union(*map(set, stars)))
        shuffled = names.copy()
        rng.shuffle(shuffled)
        rename_map = dict(zip(names, shuffled))
        stars = [[rename_map[b] for b in s] for s in stars]
        reordered = list(stars)
        rng.shuffle(reordered)
        structure = ReturnRule(co_knotted_pairs(reordered))
    ids = {frozenset(row): v for v, row in enumerate(structure.stars)}
    landmarks = [ids[frozenset(row)] for row in stars[:n]]
    rows = []
    for increasing in (True, False):
        for stride in strides:
            reader = Reader(structure, stride, increasing)
            j = 0
            start = reader.quads[landmarks[j]]
            state = start
            period = n // math.gcd(stride, n)
            for _ in range(period):
                nxt = (j + (1 if increasing else -1)*stride) % n
                for who in (nxt, j):
                    assert reader.enabled(state) == {landmarks[who]}
                    moment = reader.quads[landmarks[who]]
                    assert moment in structure.stage.minimum_response(next(iter(moment))).supports
                    state = state ^ moment
                    assert structure.stage.allowed_change(state)
                assert state == reader.quads[landmarks[nxt]]
                j = nxt
            assert state == start
            row = dict(stride=stride, increasing=increasing, shifts=period, events=2*period)
            if n == 9:
                squares = states = 0
                for mask in range(1 << n):
                    state = frozenset()
                    for j, mark in enumerate(landmarks):
                        if mask >> j & 1:
                            state = state ^ reader.quads[mark]
                    enabled = reader.enabled(state)
                    for x, y in combinations(enabled, 2):
                        assert y in reader.enabled(state ^ reader.quads[x])
                        assert x in reader.enabled(state ^ reader.quads[y])
                        squares += 1
                    states += 1
                row.update(code_states=states, coenabled_pairs=squares)
            rows.append(row)
    return dict(source_knots=n, size_two_knots=len(stars), distinctions=len(structure.stage.owners), rows=rows)


def word_check():
    checked = active = 0
    for displacement in (1, 2, 3):
        for mask in range(1 << (4 + displacement)):
            word = [(mask >> i) & 1 for i in range(4+displacement)]

            def fires(w, start):
                window = w[start:start+4]
                if window == [0, 1, 0, 0]:
                    return start+2
                if window == [0, 1, 1, 0]:
                    return start+1
                return None

            a, b = fires(word, 0), fires(word, displacement)
            checked += 1
            if a is None or b is None:
                continue
            active += 1
            assert a != b
            after_a, after_b = word.copy(), word.copy()
            after_a[a] ^= 1
            after_b[b] ^= 1
            assert fires(after_a, displacement) == b and fires(after_b, 0) == a
    return dict(overlapping_words=checked, coenabled_overlaps=active)


if __name__ == "__main__":
    results = {}
    for n, strides in ((9, (1, 2, 4)), (81, (1, 2, 4, 8, 16))):
        row = physical_checks(n, strides)
        assert row == physical_checks(n, strides, rename=True)
        results[str(n)] = row
    results["overlap_proof"] = word_check()
    (DATA / "decorated_transport.json").write_text(json.dumps(results, indent=2)+"\n")
    print("All 224 local overlap words and both orientations of the 9- and 81-knot physical controls passed.")
