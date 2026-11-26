"""Read second seeds as loose distinctions, a held knot, and partnered knots."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, permutations, product


@dataclass(frozen=True)
class Seed:
    loose: tuple
    held: int
    partners: tuple

    @classmethod
    def from_knots(cls, record):
        knots = [frozenset(knot) for knot in record['knots']]
        counts = Counter(d for knot in knots for d in knot)
        assert max(counts.values()) <= 2
        assert all(len(a & b) <= 1 for a, b in combinations(knots, 2))
        loose = tuple(sum(counts[d] == 1 for d in knot) for knot in knots)
        partners = tuple(frozenset(j for j, other in enumerate(knots)
                                   if i != j and knot & other)
                         for i, knot in enumerate(knots))
        return cls(loose, record['at'], partners)

    @classmethod
    def from_kind(cls, kind, loose, held):
        size = len(loose)
        if kind == 'star3':
            pairs = [(0, j) for j in range(1, size)]
        else:
            pairs = [(j, j + 1) for j in range(size - 1)]
            if kind in ('ring', 'ring3'):
                pairs.append((0, size - 1))
        partners = [set() for _ in loose]
        for a, b in pairs:
            partners[a].add(b)
            partners[b].add(a)
        return cls(tuple(loose), held, tuple(map(frozenset, partners)))

    @classmethod
    def from_name(cls, name):
        kind, raw = name.split(':')
        counts, _, holder = raw.partition('@')
        values = counts.replace('[', '').replace(']', '').replace(';', ',')
        loose = tuple(map(int, values.split(',')))
        if kind == 'row5':
            held = counts.split(',').index(next(item for item in counts.split(',') if '[' in item))
        elif holder in ('', 'centre', 'hub', 'end'):
            held = 0
        elif holder in ('arm', 'mid'):
            held = 1
        else:
            held = int(holder)
        return cls.from_kind(kind, loose, held)

    def steps(self):
        known = {self.held: 0}
        todo = [self.held]
        for knot in todo:
            for other in self.partners[knot]:
                if other not in known:
                    known[other] = known[knot] + 1
                    todo.append(other)
        assert len(known) == len(self.loose)
        return tuple(known[i] for i in range(len(known)))

    def held_triple(self):
        loose = self.loose[self.held]
        partners = len(self.partners[self.held])
        return (1 + loose + partners, loose, partners)

    def signature(self, radius=None, *, ignore_loose_after=None):
        """Compare the selected knots up to renaming, keeping full partner counts."""
        steps = self.steps()
        others = [i for i, step in enumerate(steps) if i != self.held
                  and (radius is None or step <= radius)]
        descriptions = []
        for ordered in permutations(others):
            order = (self.held, *ordered)
            attrs = tuple((self.loose[i] if ignore_loose_after is None
                           or steps[i] <= ignore_loose_after else -1, len(self.partners[i]))
                          for i in order)
            links = tuple(j in self.partners[i] for i, j in combinations(order, 2))
            descriptions.append((attrs, links))
        return min(descriptions)

    def by_steps(self, radius=None):
        return tuple(sorted((step, self.loose[i], len(self.partners[i]))
                            for i, step in enumerate(self.steps())
                            if radius is None or step <= radius))

    def profiles(self):
        held = self.held_triple()
        return {'counts 0': held, 'knots': (held, tuple(sorted(zip(self.loose, map(len, self.partners))))),
                'reach 0': held, **{f'reach {r}': self.signature(r) for r in (1, 2, 3)},
                'reach all': self.signature(), 'layers 1': self.by_steps(1),
                'layers 2': self.by_steps(2), 'layers all': self.by_steps()}


def candidate_forms():
    """Generate the whole FF 3 list before removal of the already seen forms."""
    forms = set()
    for kind, sizes in [('chain', range(1, 5)), ('ring', (3, 4)), ('star3', (4,))]:
        for size in sizes:
            for loose in product(range(4), repeat=size):
                for held in range(size):
                    seed = Seed.from_kind(kind, loose, held)
                    if all(l + len(p) + (i == held) >= 3
                           for i, (l, p) in enumerate(zip(loose, seed.partners))):
                        forms.add(seed.signature())
    return forms


def group_ids(values):
    groups = defaultdict(list)
    for i, value in enumerate(values):
        groups[value].append(i)
    return list(groups.values())


def pairs_within(groups):
    return [pair for group in groups for pair in combinations(group, 2)]
