"""Read the finite core from a start using Lemma R, items 1 and 3.

Rank 1 contains the live start knots. Rank 2 contains one birth per group
and one per leftover distinction. From rank 3 on, each group of the previous
rank gives a distinct birth, even when two births hold the same map points.
The birth limit counts all non-start births of one piece. A limited read
retains complete ranks only. ``finished`` requires that no further group
can form. It can be decided even at the last permitted rank.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field


@dataclass(slots=True)
class MapPiece:
    points: frozenset
    live: tuple
    groups: tuple
    attachments: dict
    chains: dict
    cycle: bool


@dataclass(slots=True)
class StartMap:
    status: str
    sizes: tuple
    pieces: tuple


@dataclass(slots=True)
class Birth:
    rank: int
    parents: tuple
    points: frozenset
    children: tuple = ()


@dataclass(slots=True)
class Twin:
    rank: int
    births: tuple
    parents: tuple
    grandparent: int
    chain_base: int


@dataclass(slots=True)
class Piece:
    points: frozenset
    chains: dict
    cycle: bool
    nodes: dict = field(default_factory=dict)
    ranks: dict = field(default_factory=dict)
    birth_count: int = 0
    stop: str = ''
    twin: Twin | None = None
    relay: bool = False

    @property
    def finished(self):
        return self.stop == 'finished'

    @property
    def twin_rank(self):
        return self.twin.rank if self.twin else None


@dataclass(slots=True)
class Core:
    status: str
    sizes: tuple
    pieces: tuple


class _Limited(Exception):
    pass


def _indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def _group_masks(count, rosters, limit, work_limit):
    """Maximal pairwise candidates without a common holder, then uncovered pairs.

    The masks index the knots in this round. A common holder's entire roster
    is a clique, so a maximal clique has a common holder precisely when it
    equals a roster. Incidence and uncovered-pair counts stay in bit sets.
    A dense common roster can exceed the limit without listing its pairs.
    """
    blocks = {roster for roster in rosters if roster.bit_count() >= 2}
    neighbours = [0] * count
    containing = [[] for _ in range(count)]
    for block in blocks:
        for i in _indices(block):
            neighbours[i] |= block
            containing[i].append(block)
    eligible = 0
    for i, mask in enumerate(neighbours):
        neighbours[i] = mask & ~(1 << i)
        if neighbours[i].bit_count() >= 2:
            eligible |= 1 << i

    groups = []
    covered = [0] * count
    pending = [(0, eligible, 0)]
    work = 0
    while pending:
        chosen, possible, excluded = pending.pop()
        whole = chosen | possible
        if whole.bit_count() < 3:
            continue
        first = (whole & -whole).bit_length() - 1
        work += 1 + len(containing[first])
        if work > work_limit:
            raise _Limited('group search cap')
        if any(whole & ~block == 0 for block in containing[first]):
            continue
        # If the possible additions all go together, only their whole can
        # be maximal. This also avoids a recursion per knot in a dense group.
        for i in _indices(possible):
            work += 1
            if possible & ~(neighbours[i] | (1 << i)):
                break
        else:
            if any(possible & ~neighbours[i] == 0 for i in _indices(excluded)):
                continue
            if len(groups) >= limit:
                raise _Limited('birth cap')
            groups.append(whole)
            for i in _indices(whole):
                covered[i] |= whole
            continue

        # Bron–Kerbosch with a pivot. Excluded additions have already had
        # their branch visited. An explicit stack also covers large ranks.
        branches = possible
        for i in _indices(possible | excluded):
            work += 1
            others = possible & ~neighbours[i]
            if others.bit_count() < branches.bit_count():
                branches = others
                if not branches:
                    break
        for i in _indices(branches):
            bit = 1 << i
            pending.append((chosen | bit, possible & neighbours[i], excluded & neighbours[i]))
            possible ^= bit
            excluded |= bit

    for i, adjacent in enumerate(neighbours):
        later = adjacent & ~covered[i] & ~((1 << (i + 1)) - 1)
        if len(groups) + later.bit_count() > limit:
            raise _Limited('birth cap')
        groups.extend((1 << i) | (1 << j) for j in _indices(later))
    return groups


def read_map(stars, knot_law='nae', *, max_groups=100_000, group_work=2_000_000):
    """Read round 1, connected pieces, chain bases and the late-map cycle test."""
    if knot_law not in ('nae', 'parity'):
        raise ValueError('knot_law must be nae or parity')
    stars = tuple(tuple(star) for star in stars)
    sizes = tuple(map(len, stars))
    owners = defaultdict(list)
    for i, star in enumerate(stars):
        if len(set(star)) != len(star):
            raise ValueError('a distinction occurs twice in one start knot')
        for distinction in star:
            owners[distinction].append(i)

    loose = [0] * len(stars)
    neighbours = [set() for _ in stars]
    for holders in owners.values():
        if len(holders) == 1:
            loose[holders[0]] += 1
        elif len(holders) == 2:
            a, b = holders
            neighbours[a].add(b)
            neighbours[b].add(a)
        else:
            raise ValueError('Lemma R requires at most two holders per distinction')
    live = tuple(i for i, number in enumerate(loose) if number)
    live_set = set(live)
    local = {k: i for i, k in enumerate(live)}
    raw = {frozenset(holders & live_set) for holders in neighbours}
    raw = {block for block in raw if len(block) >= 2}
    roster_masks = [sum(1 << local[k] for k in block) for block in raw]
    try:
        masks = _group_masks(len(live), roster_masks, max_groups, group_work)
    except _Limited as exc:
        reason = 'map group cap' if str(exc) == 'birth cap' else str(exc)
        return StartMap(reason, sizes, ())
    groups = [tuple(live[i] for i in _indices(mask)) for mask in masks]
    demand = Counter(k for group in groups for k in group)
    if any(demand[k] > loose[k] for k in live):
        status = 'stall'
    elif not live:
        status = 'none'
    elif sum(loose) == 1 and knot_law == 'parity':
        status = 'one loose'
    else:
        status = 'in'

    cells = [frozenset(group) for group in groups if len(group) >= 3]
    blocks = [b for b in raw if not any(b < bigger for bigger in raw)
              and not any(b <= cell for cell in cells)]
    attachments = {}
    chains = {}
    for k in live:
        for _ in range(loose[k] - demand[k]):
            pendant = len(stars) + len(attachments)
            attachments[pendant] = k
            if loose[k] < 3:
                chains[pendant] = 3 - loose[k]

    families = [*blocks, *cells, *((p, k) for p, k in attachments.items())]
    connection = {p: set() for p in (*live, *attachments)}
    for family in families:
        representative = next(iter(family))
        for p in family:
            if p != representative:
                connection[p].add(representative)
                connection[representative].add(p)
    pieces = []
    visited = set()
    for first in connection:
        if first in visited:
            continue
        points = {first}
        pending = [first]
        while pending:
            additions = connection[pending.pop()] - points
            points.update(additions)
            pending.extend(additions)
        visited.update(points)
        # Family incidence cycles, with the cycles where a block and a group
        # cell meet twice or more filled under the late-map reading.
        incidence = 1 - len(points) + sum(len(family) - 1 for family in families
                                         if next(iter(family)) in points)
        filled = sum(max(0, len(block & cell) - 1) for block in blocks if block <= points
                     for cell in cells if cell <= points)
        pieces.append(MapPiece(frozenset(points), tuple(sorted(points & live_set)),
                               tuple(group for group in groups if group[0] in points),
                               {p: k for p, k in attachments.items() if p in points},
                               {p: n for p, n in chains.items() if p in points}, incidence != filled))
    return StartMap(status, sizes, tuple(pieces))


def _first_twins(piece, rank):
    """Find two births sharing distinct parents with a common chain-bearing parent."""
    if not piece.chains or rank < 3:
        return None
    # Pairs left uncovered by the larger groups cannot share two parents with
    # a different birth. Only two larger groups can witness the test.
    larger = [i for i in piece.ranks[rank] if len(piece.nodes[i].parents) >= 3]
    if len(larger) < 2:
        return None
    children = defaultdict(list)
    for birth in larger:
        for p in piece.nodes[birth].parents:
            children[p].append(birth)
    earlier_parents = []
    earlier_by_child = defaultdict(int)
    earlier_by_grandparent = defaultdict(int)
    bases = piece.chains.keys()
    base_in = {}
    for p, offspring in children.items():
        if len(offspring) < 2:
            continue
        grandparents = []
        for g in piece.nodes[p].parents:
            if g not in base_in:
                base_in[g] = min(piece.nodes[g].points & bases, default=None)
            if base_in[g] is not None:
                grandparents.append(g)
        if not grandparents:
            continue
        # Which earlier parents occur at least twice among p's children?
        # Bit sets avoid expanding a dense family into all pairs of births.
        once = twice = 0
        for child in offspring:
            seen = earlier_by_child[child]
            twice |= once & seen
            once |= seen
        for g in grandparents:
            matches = twice & earlier_by_grandparent[g]
            if matches:
                other = matches & -matches
                q = earlier_parents[other.bit_length() - 1]
                twins = tuple(child for child in offspring if earlier_by_child[child] & other)[:2]
                return Twin(rank, twins, (q, p), g, base_in[g])
        bit = 1 << len(earlier_parents)
        earlier_parents.append(p)
        for child in offspring:
            earlier_by_child[child] |= bit
        for g in grandparents:
            earlier_by_grandparent[g] |= bit
    return None


def _add_rank(piece, rank, first, births):
    ids = tuple(range(first, first + len(births)))
    children = defaultdict(list)
    for i, (parents, points) in zip(ids, births):
        piece.nodes[i] = Birth(rank, parents, points)
        for p in parents:
            children[p].append(i)
    for p, ids_here in children.items():
        piece.nodes[p].children = tuple(ids_here)
    piece.ranks[rank] = ids
    piece.birth_count += len(ids)
    if piece.twin is None:
        piece.twin = _first_twins(piece, rank)
    return first + len(ids)


def _build_piece(start, n, many, knot_law, max_rank, max_births, group_work):
    piece = Piece(start.points, start.chains, start.cycle)
    piece.ranks[1] = start.live
    piece.nodes = {k: Birth(1, (), frozenset((k,))) for k in start.live}
    if max_rank == 1:
        piece.stop = 'rank cap'
        return piece
    if len(start.groups) + len(start.attachments) > max_births:
        piece.stop = 'birth cap'
        return piece
    initial = [(group, frozenset(group)) for group in start.groups]
    initial.extend(((k,), frozenset((k, p))) for p, k in start.attachments.items())
    next_id = _add_rank(piece, 2, n, initial)
    rank = 2
    while True:
        current = piece.ranks[rank]
        rosters = defaultdict(int)
        for local, node in enumerate(current):
            for parent in piece.nodes[node].parents:
                rosters[parent] |= 1 << local
        if all(roster.bit_count() <= 1 for roster in rosters.values()):
            piece.stop = 'finished'
            piece.relay = (not piece.chains and len(current) == 1
                           and piece.nodes[current[0]].points == piece.points
                           and (knot_law == 'nae' or many))
            return piece
        if rank == max_rank:
            piece.stop = 'rank cap'
            return piece
        try:
            groups = _group_masks(len(current), rosters.values(), max_births - piece.birth_count, group_work)
        except _Limited as exc:
            piece.stop = str(exc)
            return piece
        births = []
        for group in groups:
            parents = tuple(current[i] for i in _indices(group))
            points = frozenset().union(*(piece.nodes[p].points for p in parents))
            births.append((parents, points))
        rank += 1
        next_id = _add_rank(piece, rank, next_id, births)


def build_core(stars, knot_law='nae', *, max_rank=25, max_births=5000, group_work=2_000_000):
    """Read cores under explicit per-piece limits. A rank limit alone proves no infinity."""
    if max_rank < 1 or max_births < 0 or group_work < 1:
        raise ValueError('rank and group work must be positive and births nonnegative')
    mapped = read_map(stars, knot_law, group_work=group_work)
    if mapped.status != 'in':
        return Core(mapped.status, mapped.sizes, ())
    pieces = tuple(_build_piece(piece, len(mapped.sizes), len(mapped.pieces) > 1, knot_law,
                                max_rank, max_births, group_work) for piece in mapped.pieces)
    return Core(mapped.status, mapped.sizes, pieces)
