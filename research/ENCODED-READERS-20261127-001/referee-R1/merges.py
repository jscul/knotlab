"""Exact reductions of the active distinctions of a strict reader choice.

A term is a reader and lists the two holders of each of its two settings.
Each occurrence is a separate setting, even if two occurrences have identical
holders. Knot labels are fixed. See merge_arguments.md for the proofs.
"""
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from random import Random


def normalized(terms):
    return tuple(sorted(tuple(sorted(tuple(sorted(h)) for h in t)) for t in terms))


def active_counts(game):
    return Counter(u for term in game for meeting in term for u in meeting)


def checks(game):
    """Return the Pauli X and Z masks of each knot, assigning one bit per term."""
    at = defaultdict(lambda: [0, 0])
    for j, term in enumerate(game):
        if len(term) != 2 or any(len(h) != 2 for h in term) or len(set(term[0] + term[1])) != 4:
            raise ValueError(f"each reader needs four distinct holders: {term}")
        for setting, meeting in enumerate(term):
            for u in meeting:
                at[u][setting] |= 1 << j
    return dict(at)


def product_sign(at, order):
    x = z = sign = 0
    for u in order:
        next_x, next_z = at[u]
        sign ^= (z & next_x).bit_count() % 2
        x ^= next_x
        z ^= next_z
    assert x == z == 0
    return sign


@lru_cache(maxsize=8192)
def signed_checks(game):
    at = checks(game)
    commuting = all(((x & b) ^ (z & a)).bit_count() % 2 == 0
                    for (x, z), (a, b) in combinations(at.values(), 2))
    order = sorted(at)
    second = order.copy()
    Random(97 * len(at) + len(game)).shuffle(second)
    if len(second) > 1 and second == order:
        second = second[1:] + second[:1]
    return commuting, product_sign(at, order), product_sign(at, second)


def met_mask(term):
    """Bit v(v-1)/2+u is the pair of knots u<v met by this reader."""
    result = 0
    for a in term[0]:
        for b in term[1]:
            u, v = sorted((a, b))
            result |= 1 << (v * (v - 1) // 2 + u)
    return result


@lru_cache(maxsize=8192)
def proper_commuting_part(game):
    """An explicit proper nonempty commuting subset, or None after exhausting them."""
    columns = [met_mask(term) for term in game]
    sums = [0]
    for bits in range(1, (1 << len(game)) - 1):
        bit = bits & -bits
        value = sums[bits ^ bit] ^ columns[bit.bit_length() - 1]
        if value == 0:
            return tuple(j for j in range(len(game)) if (bits >> j) & 1)
        sums.append(value)
    return None


@lru_cache(maxsize=8192)
def base_kind(game):
    n = len(game)
    counts = active_counts(game)
    if n == 3 and len(counts) == 4 and len({h for term in game for h in term}) == 6:
        return "three-reader game"
    if n < 5 or n % 2 == 0 or len(counts) != n + 1 or sorted(counts.values()) != [3] * n + [n]:
        return None
    common = next(u for u, d in counts.items() if d == n)
    opposite = {}
    neighbours = defaultdict(set)
    for term in game:
        if not any(common in h for h in term):
            return None
        shared, other = term if common in term[0] else term[::-1]
        j = next(v for v in shared if v != common)
        opposite[j] = other
        a, b = other
        neighbours[a].add(b)
        neighbours[b].add(a)
    if len(opposite) != n or set(opposite) != set(neighbours) or any(len(s) != 2 for s in neighbours.values()):
        return None
    # From each j, both holders of the paired meeting must be the two knots
    # furthest from j in the connected ring. This test uses no orientation.
    for j, pair in opposite.items():
        distance = {j: 0}
        todo = deque([j])
        while todo:
            v = todo.popleft()
            for u in neighbours[v]:
                if u not in distance:
                    distance[u] = 1 + distance[v]
                    todo.append(u)
        if len(distance) != n or any(distance[u] != n // 2 for u in pair):
            return None
    return f"ring game of {n}"


@dataclass(frozen=True)
class Move:
    left: int
    right: int
    repeated: tuple
    knot: int
    forced: bool
    doubled: bool
    child: tuple


@lru_cache(maxsize=8192)
def moves(game):
    counts = active_counts(game)
    result = []
    for i, j in combinations(range(len(game)), 2):
        a, b = game[i], game[j]
        for common in set(a).intersection(b):
            left = a[1] if a[0] == common else a[0]
            right = b[1] if b[0] == common else b[0]
            through = set(left).intersection(right)
            if not through:
                continue
            replacement = tuple(sorted(set(left).symmetric_difference(right)))
            remaining = [term for k, term in enumerate(game) if k != i and k != j]
            if replacement:
                remaining.append((common, replacement))
            child = normalized(remaining)
            for w in sorted(through):
                result.append(Move(i, j, common, w, counts[w] == 2, not replacement, child))
    return tuple(result)


def move_key(move):
    return move.knot, move.forced, move.doubled, move.child


class Search:
    """The whole decreasing search for one roster. States can be shared by words."""

    def __init__(self):
        self.steps = {}
        self.outcomes = {}
        self.forced_ends = {}
        self.path_count = {}
        self.reached = {}

    def explore(self, game):
        if game in self.steps:
            return
        assert signed_checks(game) == (True, 1, 1), game
        minimal = proper_commuting_part(game) is None
        c = len(active_counts(game)) - len(game)
        steps = tuple(sorted(set(move_key(m) for m in moves(game))))
        self.steps[game] = steps
        answers, forced_ends, reached = set(), set(), {game}
        n_paths = 0
        if not steps:
            answers.add((game, ()))
            n_paths = 1
        if not any(forced for _, forced, _, _ in steps):
            forced_ends.add(game)
        for w, forced, doubled, child in steps:
            self.explore(child)
            assert len(child) == len(game) - 1 - doubled
            if not doubled:
                assert len(active_counts(child)) - len(child) == c + (not forced)
            if minimal:
                assert not doubled and proper_commuting_part(child) is None
            reached.update(self.reached[child])
            n_paths += self.path_count[child]
            if forced:
                forced_ends.update(self.forced_ends[child])
            for end, signature in self.outcomes[child]:
                answers.add((end, tuple(sorted((*signature, (w, forced, doubled))))))
        assert len(forced_ends) == 1
        if base_kind(game):
            assert not steps
        self.reached[game] = reached
        self.outcomes[game] = answers
        self.forced_ends[game] = forced_ends
        self.path_count[game] = n_paths

    def route(self, game, end, signature):
        """Recover a chronological legal sequence for a recorded multiset of steps."""
        if not signature:
            assert game == end
            return []
        for w, forced, doubled, child in self.steps[game]:
            item = w, forced, doubled
            if item not in signature:
                continue
            rest = list(signature)
            rest.remove(item)
            if (end, tuple(rest)) in self.outcomes[child]:
                return [item, *self.route(child, end, tuple(rest))]
        raise ValueError("no route has the requested ending and steps")


def label_word(supports, pairs, indices):
    owners = defaultdict(list)
    for u, support in enumerate(supports):
        for d in support:
            owners[d].append(u)
    if any(len(holder) != 2 or holder[0] == holder[1] for holder in owners.values()):
        raise ValueError("the input holding must be closed")
    selected = [pairs[i] for i in indices]
    if len({d for term in selected for d in term}) != 2 * len(selected):
        raise ValueError("a distinction occurs in more than one reader setting")
    terms = [tuple(sorted((tuple(owners[d]), d) for d in term)) for term in selected]
    return sort_labelled(terms)


def sort_labelled(terms):
    return tuple(sorted(terms, key=lambda t: (tuple(h for h, _ in t), tuple(d for _, d in t))))


def unlabel(labelled):
    return normalized(tuple(h for h, _ in term) for term in labelled)


def first_decoding(labelled, search):
    """Pick the successful route selected by sorted knot and active setting labels.

    The independently obtained reachable endings determine which children can
    succeed. A fresh setting trails all live labels. Its magnitude is immaterial.
    """
    route = []
    while True:
        game = unlabel(labelled)
        if base_kind(game):
            return game, route
        ranked = []
        for move in moves(game):
            if not any(base_kind(end) for end, _ in search.outcomes[move.child]):
                continue
            travelling, partners = [], []
            for i in (move.left, move.right):
                term = labelled[i]
                mate, moving = term if term[0][0] == move.repeated else term[::-1]
                travelling.append(moving)
                partners.append(mate)
            ranked.append(((move.knot, *sorted(d for _, d in travelling)), move, travelling, partners))
        if not ranked:
            return None, route
        _, move, travelling, partners = min(ranked, key=lambda item: item[0])
        next_label = 1 + max(d for term in labelled for _, d in term)
        keep = [term for k, term in enumerate(labelled) if k not in (move.left, move.right)]
        if not move.doubled:
            other = tuple(sorted(set(travelling[0][0]).symmetric_difference(travelling[1][0])))
            earlier = 0 if travelling[0][1] < travelling[1][1] else 1
            keep.append(tuple(sorted((partners[earlier], (other, next_label)))))
        labelled = sort_labelled(keep)
        assert unlabel(labelled) == move.child
        route.append((move.knot, move.forced, move.doubled))
