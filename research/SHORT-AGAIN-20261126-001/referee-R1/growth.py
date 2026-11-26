"""Complete rounds from the written definitions, under not-all-equal with no taking of shared distinctions.

The round follows RING-IN-BALANCE definitions, with PARTS-MEET-AGAIN's
birth order and WHAT-A-BIRTH-CARRIES's SHORT-BY treatment. The two joins
and the bench starts are those of TWO-PATTERNS. The ration names and own
birth readings are as in SHORT-AGAIN. This file uses no study modules.
"""

from collections import Counter, defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha1
from itertools import combinations, permutations, product


@dataclass(frozen=True, slots=True)
class Pattern:
    knots: tuple[tuple[int, ...], ...]
    site: int = 0


# The four connected patterns in the census on at most three knots.
CENSUS_SHARINGS = {
    1: (1, ()),
    3: (2, ((0, 1),)),
    6: (3, ((0, 1), (0, 2))),
    7: (3, ((0, 1), (0, 2), (1, 2))),
}


def census_starts():
    starts = {}
    for label, (size, sharings) in CENSUS_SHARINGS.items():
        symmetries = [
            p for p in permutations(range(size))
            if {tuple(sorted((p[u], p[v]))) for u, v in sharings} == set(sharings)
        ]
        degrees = Counter(k for pair in sharings for k in pair)
        for loose in product(range(4), repeat=size):
            if any(degrees[k] + loose[k] < 3 for k in range(size)) or not any(loose):
                continue
            if any(tuple(loose[k] for k in p) < loose for p in symmetries):
                continue
            knots = [[] for _ in loose]
            for distinction, (u, v) in enumerate(sharings):
                knots[u].append(distinction)
                knots[v].append(distinction)
            next_distinction = len(sharings)
            for knot, count in zip(knots, loose):
                knot.extend(range(next_distinction, next_distinction + count))
                next_distinction += count
            base = 'g' + str(label) + ':' + ''.join(map(str, loose))
            for site in range(size):
                if any(p[site] < site and tuple(loose[k] for k in p) == loose for p in symmetries):
                    continue
                starts[f'{base}@{site}'] = Pattern(tuple(map(tuple, knots)), site)
    return starts


STARTS = census_starts()
STARTS.update({
    'ring': Pattern(tuple(((k - 1) % 5, k, *(range(5 + 3 * k, 8 + 3 * k))) for k in range(5))),
    'copier': Pattern(((0, 1, 2), (0, 3, 4))),
    'source': Pattern(((0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14),
                       (6, 7, 15, 16, 17), (2, 3, 4, 6, 18, 19, 20),
                       (7, 8, 21, 22), (5, 8, 23, 24))),
})


def start(name):
    if isinstance(name, Pattern):
        return name
    if name in STARTS:
        return STARTS[name]
    base, site = name.rsplit('@', 1)
    return Pattern(STARTS[base + '@0'].knots, int(site))


@dataclass(frozen=True, slots=True)
class Setup:
    knots: tuple[tuple[int, ...], ...]
    roles: tuple[str, ...]
    barred: frozenset[int] = frozenset()


def build(a, b, d, join='meeting', *, site_a=None, site_b=None, change=None, remove=False):
    """Join the sites d steps apart and optionally change one starting knot.

    A change is (role, index, signed loose count). The link index starts at 1
    from A. The A and B indices start at 0. A negative change bars by default.
    Early records' physical removal is requested with remove=True.
    """
    if d < 1 or join not in {'meeting', 'share'}:
        raise ValueError((d, join))
    knots, roles = [], []
    next_distinction = 0

    def add_knot(role, places=()):
        roles.append(role)
        knots.append(list(places))
        return len(knots) - 1

    def add_distinction(*holders):
        nonlocal next_distinction
        for knot in holders:
            knots[knot].append(next_distinction)
        next_distinction += 1

    def add_pattern(specification, role, site):
        nonlocal next_distinction
        if specification is None or specification == 'stub':
            return None
        pattern = start(specification)
        location = len(knots) + (pattern.site if site is None else site)
        offset = next_distinction
        for places in pattern.knots:
            add_knot(role, (offset + x for x in places))
        next_distinction += 1 + max(x for places in pattern.knots for x in places)
        return location

    def connect(left, right):
        if join == 'share':
            add_distinction(left, right)
        else:
            spent = add_knot('spent')
            add_distinction(left, spent)
            add_distinction(right, spent)
            add_distinction(right, spent)
            add_distinction(left)
            add_distinction(right)

    left = add_pattern(a, 'A', site_a)
    right = add_pattern(b, 'B', site_b)
    if b is not None:
        if a == 'stub':
            left = add_knot('A')
        ends = [left]
        for _ in range(d - 1):
            link = add_knot('link')
            connect(ends[-1], link)
            ends.append(link)
        if b == 'stub':
            right = add_knot('B')
        connect(ends[-1], right)
        ends.append(right)
        for k in ends:
            while len(knots[k]) < 3:
                add_distinction(k)

    barred = set()
    if change:
        role, index, delta = change
        candidates = [k for k, tag in enumerate(roles) if tag == role]
        target = candidates[index - (role == 'link')]
        if delta > 0:
            for _ in range(delta):
                add_distinction(target)
        else:
            holds = Counter(x for places in knots for x in places)
            loose = sorted(x for x in knots[target] if holds[x] == 1)
            if len(loose) < -delta:
                raise ValueError('no usable distinction to bar')
            chosen = loose[delta:] if delta else ()
            if remove:
                if len(knots[target]) + delta < 3 or len(loose) + delta < 1:
                    raise ValueError('removal would leave fewer than three places or no loose distinction')
                knots[target] = [x for x in knots[target] if x not in chosen]
            else:
                barred.update(chosen)
    return Setup(tuple(map(tuple, knots)), tuple(roles), frozenset(barred))


def distance_from(meets, seeds):
    distances = dict.fromkeys(seeds, 0)
    queue = deque(distances)
    while queue:
        knot = queue.popleft()
        for neighbor in meets[knot]:
            if neighbor not in distances:
                distances[neighbor] = distances[knot] + 1
                queue.append(neighbor)
    return distances


def changes(b, d):
    """Give the jam and switch records' change labels, distances and instructions."""
    pattern = Pattern(((0, 1, 2),)) if b == 'stub' else start(b)
    meets = [set() for _ in pattern.knots]
    for (u, a), (v, bs) in combinations(enumerate(pattern.knots), 2):
        if set(a).intersection(bs):
            meets[u].add(v)
            meets[v].add(u)
    from_site = distance_from(meets, (pattern.site,))
    for label, role, indices in (('B', 'B', range(len(meets))), ('L', 'link', range(1, d))):
        for prefix, delta in (('', 1), ('b', -1)):
            for i in indices:
                yield f'{prefix}{label}{i}', d + from_site[i] if label == 'B' else i, (role, i, delta)


class GuardStop(Exception):
    pass


def guard(kind, size, limit):
    if size > limit:
        raise GuardStop(f'{kind}: {size} > {limit}')


def maximal_sets(sets):
    kept = []
    by_member = defaultdict(list)
    for members in sorted(sets, key=lambda group: (-len(group), tuple(sorted(group)))):
        first = min(members, key=lambda u: len(by_member[u]))
        if any(members <= other for other in by_member[first]):
            continue
        kept.append(members)
        for u in members:
            by_member[u].append(members)
    return kept, by_member


def maximal_joinable_sets(adjacency):
    """Enumerate maximal pairwise-joinable sets by pivoted backtracking."""
    def branch(chosen, remaining, excluded):
        pivot = max(remaining | excluded, key=lambda u: len(remaining & adjacency[u]))
        return chosen, remaining, excluded, remaining - adjacency[pivot]

    unseen = set(adjacency)
    for seed in adjacency:
        if seed not in unseen:
            continue
        component = {seed}
        todo = [seed]
        while todo:
            unseen_neighbors = adjacency[todo.pop()] - component
            todo.extend(unseen_neighbors)
            component.update(unseen_neighbors)
        unseen.difference_update(component)
        if len(component) < 3:
            yield component
            continue
        if all(len(adjacency[u]) == len(component) - 1 for u in component):
            yield component
            continue
        stack = [branch((), component, set())]
        while stack:
            chosen, remaining, excluded, choices = stack[-1]
            if not choices:
                stack.pop()
                continue
            u = choices.pop()
            remaining.remove(u)
            candidates = remaining & adjacency[u]
            earlier = excluded & adjacency[u]
            excluded.add(u)
            if not candidates and not earlier:
                yield {*chosen, u}
            elif candidates:
                stack.append(branch((*chosen, u), candidates, earlier))


def met_sets(members, meets):
    by_common = defaultdict(set)
    for u in members:
        for common in meets(u):
            by_common[common].add(u)
    guard('incidences', sum(map(len, by_common.values())), 200_000_000)
    sets = {frozenset(m) for m in by_common.values() if len(m) >= 2}
    return maximal_sets(sets)


def joinable(members, met):
    adjacency = {u: set() for u in members}
    n_pairs = 0
    for group in met:
        guard('pairs', len(group) * (len(group) - 1) // 2, 2_000_000)
        for u, v in combinations(sorted(group), 2):
            if v not in adjacency[u]:
                adjacency[u].add(v)
                adjacency[v].add(u)
                n_pairs += 1
        guard('pairs', n_pairs, 2_000_000)
    return adjacency


def groups_for(members, meets):
    met, met_at = met_sets(members, meets)
    adjacency = joinable(members, met)
    big, covered = [], set()
    for count, group in enumerate(maximal_joinable_sets(adjacency), 1):
        guard('maximal joinable sets', count, 20_000_000)
        if len(group) < 3:
            continue
        first = min(group, key=lambda u: len(met_at[u]))
        if any(group <= other for other in met_at[first]):
            continue
        ordered = tuple(sorted(group))
        big.append(ordered)
        covered.update(combinations(ordered, 2))
        guard('groups', len(big), 2_000_000)
    pairs = sorted((u, v) for u in members for v in adjacency[u] if u < v and (u, v) not in covered)
    guard('groups', len(big) + len(pairs), 2_000_000)
    return tuple(sorted(big) + pairs)


def fresh_count(ration, parents, demand):
    floor = max(3 - parents, 1)
    ordinary = max(demand, floor)
    if ration == 'ORD':
        return ordinary
    if ration.startswith('CAP-'):
        cap = int(ration[4:])
        if cap < 2:
            raise ValueError('the cap must fund an offshoot of three places')
        return min(ordinary, cap)
    if ration == 'FLOOR1':
        return floor
    if ration == 'REC-ONE-FEWER':
        return max(3 - parents, 0, ordinary - 1)
    fewer = {
        'ONE-FEWER': True,
        'JOIN-FEWER': parents > 1,
        'BUSY-FEWER': parents > 1 and demand > parents,
        'ODD-FEWER': demand % 2 == 1,
        'THIRD-FEWER': demand % 3 == 2,
    }
    return max(floor, ordinary - fewer[ration])


def digest(value, length):
    return sha1(repr(value).encode()).hexdigest()[:length]


A_ONLY = frozenset({'A'})
B_ONLY = frozenset({'B'})
AB = frozenset({'A', 'B'})


def descent(roles):
    if roles == A_ONLY:
        return 'A'
    if roles == B_ONLY:
        return 'B'
    return 'joint' if AB <= roles else 'link'


@dataclass(frozen=True, slots=True)
class Birth:
    id: int
    parents: tuple[int, ...]
    kind: str
    inputs: tuple[int, ...]
    demand: int
    fresh: int
    places: int


@dataclass(slots=True)
class Round:
    round: int
    knots: int
    births: int
    a_members: int
    a_short: int
    own_births: tuple
    b_births: tuple
    joint_births: tuple
    a_joined: int
    a_kept: int
    b_kept: int
    a_cancelled: tuple
    a_shortfall: dict
    shortfall: dict
    short_by: dict
    births_by: dict
    groups: tuple = ()
    kept: tuple = ()
    owed: dict = field(default_factory=dict)
    available: dict = field(default_factory=dict)
    short: frozenset = frozenset()
    birth_records: tuple = ()


class Growth:
    def __init__(self, setup, ration, treatment, trace=False):
        self.ration, self.treatment, self.trace = ration, treatment, trace
        self.places = [list(knot) for knot in setup.knots]
        self.parents = [()] * len(self.places)
        self.born = [0] * len(self.places)
        self.meets = [set() for _ in self.places]
        holders = defaultdict(list)
        for u, places in enumerate(self.places):
            for x in places:
                holders[x].append(u)
        if any(len(k) > 2 for k in holders.values()):
            raise ValueError('only one or two holders are used in these starts')
        self.usable = {}
        self.barred = Counter()
        for x, us in sorted(holders.items()):
            if len(us) == 1:
                if x in setup.barred:
                    self.barred[us[0]] += 1
                else:
                    self.usable.setdefault(us[0], []).append(x)
            else:
                u, v = us
                self.meets[u].add(v)
                self.meets[v].add(u)
        self.next_distinction = max(holders, default=-1) + 1
        self.roles = [frozenset({role}) for role in setup.roles]
        self.names = []
        seen = Counter()
        for role in setup.roles:
            self.names.append(f'{role}{seen[role]}')
            seen[role] += 1
        self.rows = []
        self.stop = None
        self.stop_detail = None

    def fork(self):
        """Copy current holdings and retain the completed round readings."""
        other = deepcopy(self, {id(row): row for row in self.rows})
        return other

    def mark(self, knot):
        self.places[knot].append(self.next_distinction)
        self.usable.setdefault(knot, []).append(self.next_distinction)
        self.next_distinction += 1

    def bar(self, knot):
        loose = self.usable.get(knot)
        if not loose:
            raise ValueError('no usable distinction to bar')
        loose.pop()
        if not loose:
            del self.usable[knot]
        self.barred[knot] += 1

    def step(self):
        try:
            return self._step()
        except GuardStop as exc:
            self.stop, self.stop_detail = 'guard', str(exc)
            return False

    def _step(self):
        round_number = len(self.rows) + 1
        members = sorted(self.usable)
        groups = groups_for(members, self.meets.__getitem__)
        owed = Counter(u for group in groups for u in group)
        available = {u: len(self.usable[u]) for u in members}
        short = frozenset(u for u in members if owed[u] > available[u])
        if short and self.treatment == 'STALL':
            self.stop = 'stalled'
            return False
        kept = tuple(group for group in groups if short.isdisjoint(group))
        paid = Counter(u for group in kept for u in group)
        parents = list(kept)
        retire = set()
        for u in members:
            if u not in short or self.treatment == 'CANCEL-OFFSHOOT':
                offshoots = available[u] - paid[u]
            elif self.treatment == 'SHORT-BY':
                offshoots = min(available[u], owed[u] - available[u])
            else:
                offshoots = 0
                if self.treatment == 'CANCEL-RETIRE':
                    retire.add(u)
            parents.extend([(u,)] * offshoots)
        guard('births', len(parents), 2_000_000)

        # Steps 4–6. Allocate the loose distinctions in the written birth order.
        # In the demand roster a new knot meets exactly its parents. A parent
        # that is still a member also meets every new knot that took from it.
        first_birth = len(self.places)
        taken = Counter()
        children = defaultdict(set)
        inputs = []
        for u, group in enumerate(parents, first_birth):
            inputs.append(tuple(self.usable[p][taken[p]] for p in group))
            taken.update(group)
            for p in group:
                children[p].add(u)
        remaining = {u: self.usable[u][taken[u]:] for u in members if u not in retire and taken[u] < available[u]}

        demand = Counter()
        if parents:
            def demand_meets(knot):
                if knot >= first_birth:
                    return parents[knot - first_birth]
                return self.meets[knot] | children[knot]

            demand_members = [*remaining, *range(first_birth, first_birth + len(parents))]
            demand.update(u for group in groups_for(demand_members, demand_meets) for u in group)
        fresh_counts = [fresh_count(self.ration, len(group), demand[u]) for u, group in enumerate(parents, first_birth)]
        guard('distinctions', self.next_distinction + sum(fresh_counts), 40_000_000)

        # Commit the round only after both rosters and all allotments are known.
        own = {key: [] for key in ('A', 'B', 'joint', 'link')}
        birth_records = []
        seen = Counter()
        short_by = Counter(descent(self.roles[u]) for u in short)
        shortfall = Counter(str(owed[u] - available[u]) for u in short)
        a_shortfall = Counter(str(owed[u] - available[u]) for u in short if self.roles[u] == A_ONLY)
        a_members = sum(self.roles[u] == A_ONLY for u in members)
        a_joined = sum(any(self.roles[u] == A_ONLY for u in group) and
                       any(self.roles[u] != A_ONLY for u in group) for group in groups)
        a_kept = sum(any(self.roles[u] == A_ONLY for u in group) and
                     any(self.roles[u] != A_ONLY for u in group) for group in kept)
        b_kept = sum(any(self.roles[u] == B_ONLY for u in group) and
                     any(self.roles[u] != B_ONLY for u in group) for group in kept)
        a_cancelled = tuple(sorted(tuple(sorted(self.names[u] for u in group)) for group in groups
                                   if not short.isdisjoint(group) and any(self.roles[u] == A_ONLY for u in group)))
        for u in retire:
            self.barred[u] += available[u]
        self.usable = remaining
        for offset, (group, supplied, f) in enumerate(zip(parents, inputs, fresh_counts)):
            u = first_birth + offset
            kind = 'offshoot' if len(group) == 1 else 'join'
            roles = frozenset().union(*(self.roles[p] for p in group))
            named_parents = tuple(sorted(self.names[p] for p in group))
            key = kind, named_parents
            name = digest((*key, seen[key]), 16)
            seen[key] += 1
            self.roles.append(roles)
            self.names.append(name)
            loose = list(range(self.next_distinction, self.next_distinction + f))
            self.next_distinction += f
            self.places.append([*supplied, *loose])
            if loose:
                self.usable[u] = loose
            self.meets.append(set(group))
            self.parents.append(group)
            self.born.append(round_number)
            places = len(supplied) + f
            own[descent(roles)].append((name, f, places))
            if self.trace:
                birth_records.append(Birth(u, group, kind, supplied, demand[u], f, places))
        for u, new in children.items():
            self.meets[u].update(new)
        self.rows.append(Round(
            round_number, len(self.places), len(parents), a_members, short_by['A'],
            tuple(sorted(own['A'])), tuple(sorted(own['B'])), tuple(sorted(own['joint'])),
            a_joined, a_kept, b_kept, a_cancelled, dict(a_shortfall), dict(shortfall), dict(short_by),
            {role: len(values) for role, values in own.items() if values},
            groups if self.trace else (), kept if self.trace else (),
            {u: owed[u] for u in members} if self.trace else {}, available if self.trace else {},
            short if self.trace else frozenset(), tuple(birth_records),
        ))
        return True

    def run(self, rounds, bound):
        while not self.stop and len(self.rows) < rounds:
            if not self.step():
                break
            if len(self.places) > bound:
                self.stop = 'knots'
        return self


def grow(case, ration='ORD', treatment='CANCEL-WAIT', rounds=16, bound=3000, *, trace=False):
    if treatment not in {'STALL', 'CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'SHORT-BY'}:
        raise ValueError(treatment)
    return Growth(case, ration, treatment, trace).run(rounds, bound)


def first_difference(whole, changed, field_name='own_births', after=0):
    return next((a.round for a, b in zip(whole.rows[after:], changed.rows[after:])
                 if getattr(a, field_name) != getattr(b, field_name)), None)
