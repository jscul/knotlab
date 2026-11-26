"""Finite-map forecasts for the late-view referee check, from the start only.

A chain is unused, has length one, or has length at least two. The last
choice contributes x²/(1-x). Collect these generating functions exactly by
birth description. The scope of this computation is the finite map's two
proposed readings.
"""

from collections import Counter, defaultdict
from itertools import combinations
from math import comb


def elements(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def subsets(mask):
    current = mask
    while True:
        yield current
        if not current:
            return
        current = (current - 1) & mask


def contained(part, whole):
    return (part & whole) == part


def union(masks):
    out = 0
    for mask in masks:
        out |= mask
    return out


def component(start, allowed, neighbours):
    seen = 0
    new = start
    while new:
        seen |= new
        new = union(neighbours[bit] for bit in elements(new)) & allowed & ~seen
    return seen


class Start:
    def __init__(self, stars, law):
        knots = {1 << index: set(star) for index, star in enumerate(stars)}
        self.start_descriptions = {bit: ('start', 0, 0, len(star)) for bit, star in knots.items()}
        multiplicities = Counter(d for star in knots.values() for d in star)
        loose = {bit: sum(multiplicities[d] == 1 for d in star) for bit, star in knots.items()}
        self.live = sum(bit for bit in knots if loose[bit])
        neighbours = {bit: sum(b for b in knots if b != bit and knot & knots[b])
                      for bit, knot in knots.items()}
        blocks = {mask & self.live for mask in neighbours.values() if (mask & self.live).bit_count() >= 2}
        pairs = {a | b for block in blocks for a, b in combinations(elements(block), 2)}
        cliques = [mask for mask in subsets(self.live) if mask.bit_count() >= 3 and
                   all((a | b) in pairs for a, b in combinations(elements(mask), 2))]
        self.cells = [s for s in cliques if not any(s != t and contained(s, t) for t in cliques)
                      and not any(contained(s, t) for t in blocks)]
        groups = self.cells + [p for p in pairs if not any(contained(p, c) for c in self.cells)]
        demand = {bit: sum(bool(bit & g) for g in groups) for bit in knots}
        self.stall = any(demand[bit] > loose[bit] for bit in knots)
        self.total_loose = sum(loose.values())
        self.reason = ('stall' if self.stall else 'none' if not self.total_loose else
                       'one loose' if self.total_loose == 1 and law == 'parity' else 'predicted')
        self.blocks = [b for b in blocks if not any(b != t and contained(b, t) for t in blocks)
                       and not any(contained(b, c) for c in self.cells)]
        repeated = any((neighbours[a] & neighbours[b]).bit_count() >= 2
                       for a, b in combinations(elements(self.live), 2))
        original_class = not (self.stall or self.cells or repeated)
        overlaps = [(a & b).bit_count() for a, b in combinations(self.cells, 2)]
        if original_class and self.total_loose >= 2:
            self.stratum = 'proved class'
        elif original_class and self.total_loose == 1:
            self.stratum = 'one loose distinction'
        elif not self.cells:
            self.stratum = 'repeated blocks only'
        elif any(k >= 2 for k in overlaps):
            self.stratum = 'group cells sharing two knots'
        elif any((b & c).bit_count() >= 2 for b in self.blocks for c in self.cells):
            self.stratum = 'a block meeting a group cell in two knots'
        elif any(overlaps):
            self.stratum = 'group cells sharing a knot'
        else:
            self.stratum = 'group cells'
        self.pieces = []
        if self.reason != 'predicted':
            return
        self.pendants = {}
        self.rays = {}
        self.neighbours = defaultdict(int)
        for h in self.blocks + self.cells:
            for v in elements(h):
                self.neighbours[v] |= h ^ v
        next_bit = 1 << len(stars)
        next_ray = 1
        for v in elements(self.live):
            pending = 0
            for _ in range(loose[v] - demand[v]):
                pending |= next_bit
                for _ in range(max(3 - loose[v], 0)):
                    self.rays[next_ray] = next_bit
                    next_ray <<= 1
                next_bit <<= 1
            self.pendants[v] = pending
        unseen = self.live
        while unseen:
            live_part = component(unseen & -unseen, unseen, self.neighbours)
            unseen ^= live_part
            hs = [h for h in self.blocks + self.cells if h & live_part]
            excess = sum(h.bit_count() - 1 for h in hs) - live_part.bit_count() + 1
            filled = sum(max((b & c).bit_count() - 1, 0) for b in self.blocks
                         for c in self.cells if c & live_part)
            if excess != filled:
                self.reason = 'a piece with a cycle'
                return
            self.pieces.append(live_part)


class Piece:
    def __init__(self, rank, cells, ray_owner, start_descriptions, mode):
        self.rank = rank
        self.whole = union(rank)
        self.ray_owner = ray_owner
        self.starts = start_descriptions
        self.lower = {}
        self.fresh = {}
        self.active = {s: sum(ray for ray, p in ray_owner.items() if s & p) for s in rank}
        self.signatures = {}
        self.ray_bases = {e: union(ray_owner[ray] for ray in elements(e)) for e in subsets(sum(ray_owner))}
        if mode == 'graded':
            by_rank = defaultdict(list)
            for s, r in rank.items():
                by_rank[r].append(s)
            above = Counter()
            for s, r in rank.items():
                # Compare all valid sets at the preceding rank, by inclusion.
                self.lower[s] = {p for p in by_rank[r-1] if contained(p, s)}
                above.update(self.lower[s])
            self.fresh = {s: above[s] + self.active[s].bit_count() for s in rank}
        elif mode == 'frozen':
            for s, r in rank.items():
                proposals = {s ^ v for v in elements(s)}
                reserved = 0
                cell_ways = 0
                for c in cells:
                    if contained(c, s):
                        proposals.update((s ^ c) | v for v in elements(c))
                    elif (s & c).bit_count() == 1:
                        reserved |= c
                        cell_ways += (s | c) in rank
                self.lower[s] = {p for p in proposals if rank.get(p) == r-1}
                loose_ways = sum((s | v) in rank for v in elements(self.whole & ~(s | reserved)))
                self.fresh[s] = loose_ways + cell_ways + self.active[s].bit_count()
        else:
            raise ValueError(mode)

    def parents(self, core, rays):
        return (p for p in self.lower[core] if contained(self.ray_bases[rays], p))

    def sig(self, core, rays):
        key = core, rays
        if key not in self.signatures:
            if not rays and core in self.starts:
                sig = self.starts[core]
            else:
                parents = rays.bit_count() + sum(1 for _ in self.parents(core, rays))
                fresh = self.fresh[core]
                sig = ('offshoot' if parents == 1 else 'join', parents, fresh, parents + fresh)
            self.signatures[key] = sig
        return self.signatures[key]

    def collect(self, terms, relay=False, skip=0):
        dimension = 0
        for core, rank in self.rank.items():
            if core == skip:
                continue
            dimension = max(dimension, self.active[core].bit_count())
            for active in subsets(self.active[core]):
                k = active.bit_count()
                sig = self.sig(core, active)
                if relay and core == self.whole:
                    sig = with_extra_loose(sig)
                core_parents = tuple(self.sig(p, active) for p in self.parents(core, active))
                for short in subsets(active):
                    long_count = k - short.bit_count()
                    shorter = tuple(self.sig(core, active ^ a) for a in elements(short))
                    parent_kinds = tuple(sorted(core_parents + shorter + (sig,) * long_count))
                    first_round = rank - 1 + k + long_count
                    terms[(sig, parent_kinds), first_round, long_count] += 1
        return dimension


def with_extra_loose(sig):
    kind, parents, fresh, places = sig
    return kind, parents, fresh + 1, places + 1


def make_piece(start, live_part, mode, control):
    cells = [] if control == 'cells' else [c for c in start.cells if c & live_part]
    pendants = union(start.pendants[v] for v in elements(live_part))
    ray_owner = {a: v for a, v in start.rays.items() if pendants & v}
    ranks = {}
    # A pendant can occur precisely when its live knot occurs. First choose the
    # live subset, then any subset of the available pendants.
    for live in subsets(live_part):
        if not live or any(1 < (c & live).bit_count() < c.bit_count() for c in cells):
            continue
        if component(live & -live, live, start.neighbours) != live:
            continue
        r = live.bit_count() - sum(c.bit_count()-2 for c in cells if contained(c, live))
        available = union(start.pendants[v] for v in elements(live))
        for selected in subsets(available):
            ranks[live | selected] = r + selected.bit_count()
    return Piece(ranks, cells, ray_owner, start.start_descriptions, mode)


def expand(terms, dimension, rounds):
    # Give all the rational sums a common denominator (1-x)^D. If the
    # numerator has degree m >= D, the last disagreement with the eventual
    # polynomial is the coefficient of x^(m-D) in the polynomial quotient.
    # The remainder has degree < D, so its coefficients are polynomial for
    # every nonnegative index. Thus the interpolation cut is max(3,D,m).
    numerators = [defaultdict(Counter), defaultdict(Counter)]
    for (sig, parents), first, long_count in terms:
        count = terms[(sig, parents), first, long_count]
        power = dimension - long_count
        short, detailed = numerators[0][sig], numerators[1][sig, parents]
        for i in range(power + 1):
            coefficient = count * comb(power, i) * (-1 if i % 2 else 1)
            short[first + i] += coefficient
            detailed[first + i] += coefficient
    rows = [{'n': 0, 'sig0': [], 'sig1': []} for _ in range(rounds)]
    cuts = []
    for reading, polys in enumerate(numerators):
        last = max((i for poly in polys.values() for i, c in poly.items() if c), default=0)
        cuts.append(max(3, dimension, last))
        for key, poly in sorted(polys.items()):
            counts = [poly.get(t, 0) for t in range(rounds+1)]
            for _ in range(dimension):
                for t in range(1, rounds+1):
                    counts[t] += counts[t-1]
            label = list(key) if not reading else [list(key[0]), [list(p) for p in key[1]]]
            for t, c in enumerate(counts[1:]):
                if c:
                    if c < 0:
                        raise ValueError('negative coefficient in a birth series')
                    if not reading:
                        rows[t]['n'] += c
                    rows[t]['sig1' if reading else 'sig0'].append([label, c])
    return rows, cuts


def evaluate(stars, rounds, law='nae', mode='frozen', control=None):
    if control not in (None, 'relay', 'cells') or law not in ('nae', 'parity'):
        raise ValueError((control, law))
    start = Start(stars, law)
    result = {'read': start.reason, 'stratum': start.stratum, 'D': None, 'K0': None, 'K1': None, 'rows': None}
    if start.reason != 'predicted':
        return result
    terms = Counter()
    dimension = 0
    for live_part in start.pieces:
        piece = make_piece(start, live_part, mode, control)
        relay = not piece.ray_owner and control != 'relay' and (law == 'nae' or len(start.pieces) > 1)
        dimension = max(dimension, piece.collect(terms, relay=relay))
        if relay:
            w = piece.rank[piece.whole]
            root_desc = with_extra_loose(piece.sig(piece.whole, 0))
            after = Piece({1: w, 3: w+1}, [], {1: 2, 2: 2}, {1: root_desc}, mode)
            dimension = max(dimension, after.collect(terms, skip=1))
    rows, cuts = expand(terms, dimension, rounds)
    result.update(D=dimension, K0=cuts[0], K1=cuts[1], rows=rows)
    return result
