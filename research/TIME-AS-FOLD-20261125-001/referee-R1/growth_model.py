"""Growth and return readings from the frozen definitions."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from time import process_time


@dataclass(frozen=True)
class Law:
    ration: str
    treatment: str
    taking: str
    choice: str
    parity: bool
    fillers: bool = False
    by_parents: bool = False
    demand_before_takes: bool = False

    @classmethod
    def from_record(cls, key):
        base, rule, choice, group = (key[k] for k in ('base', 'rule', 'choice', 'group'))
        treatment = base.partition('(')[2].partition(')')[0] or 'WAIT'
        return cls(
            'FLOOR1' if base.startswith('COPY-LAW') else 'CAP-3',
            treatment, rule or 'none', choice, key['knot_law'] == 'parity',
            '+FILLERS' in base, group == 'fbp', group == 'dbt',
        )


@dataclass(frozen=True)
class Knot:
    born: int
    parents: tuple
    places: tuple
    inputs: tuple = ()
    take: tuple = ()
    demand: int = 0
    ration_input: int = 0
    usable_fresh: int = 0
    barred_fresh: int = 0
    shared_inputs: tuple = ()


class Guard(Exception):
    pass


def bits(mask):
    while mask:
        least = mask & -mask
        yield least.bit_length() - 1
        mask ^= least


def mask_of(names):
    result = 0
    for name in names:
        result |= 1 << name
    return result


class Span:
    def __init__(self):
        self.pivots = {}

    def remainder(self, row):
        while row:
            pivot = row.bit_length() - 1
            if pivot not in self.pivots:
                break
            row ^= self.pivots[pivot]
        return row

    def add(self, row):
        row = self.remainder(row)
        if row:
            self.pivots[row.bit_length() - 1] = row


def maximal_sets(sets):
    """Filter strict subsets by indexing already kept sets by their members."""
    containing = defaultdict(list)
    maximal = []
    for members in sorted(set(sets), key=lambda s: (-s.bit_count(), s)):
        names = list(bits(members))
        pivot = min(names, key=lambda u: len(containing[u]))
        if any(members & larger == members for larger in containing[pivot]):
            continue
        maximal.append(members)
        for name in names:
            containing[name].append(members)
    return tuple(maximal)


def member_parts(adjacency):
    remaining = mask_of(adjacency)
    parts = []
    while remaining:
        part = frontier = remaining & -remaining
        while frontier:
            neighbors = 0
            for member in bits(frontier):
                neighbors |= adjacency[member]
            frontier = neighbors & ~part
            part |= frontier
        parts.append(tuple(bits(part)))
        remaining &= ~part
    return tuple(parts)


class Roster:
    def __init__(self, holders, h, k, sides=None):
        self.h = h
        self.k = k
        self.members = tuple(sorted(h))
        self.ordinal = {u: 1 << u for u in h}
        self.direct = dict.fromkeys(h, 0)
        meetings = {}
        self.incidences = 0
        for held_by in holders.values():
            if len(held_by) < 2:
                continue
            members_here = 0
            for u in held_by:
                members_here |= self.ordinal.get(u, 0)
            if not members_here:
                continue
            self.incidences += members_here.bit_count() * (len(held_by) - 1)
            for u in held_by:
                other_members = members_here & ~self.ordinal.get(u, 0)
                meetings[u] = meetings.get(u, 0) | other_members
                if u in h:
                    self.direct[u] |= other_members
        self.met_sets = {m for m in meetings.values() if m.bit_count() > 1}
        adjacency = dict.fromkeys(h, 0)
        for met_set in self.met_sets:
            for u in bits(met_set):
                adjacency[u] |= met_set ^ self.ordinal[u]
        if sides is not None:
            left = mask_of(u for u in h if sides[u] & 1)
            right = mask_of(u for u in h if sides[u] & 2)
            for u in h:
                if sides[u] & 1:
                    adjacency[u] &= ~right
                if sides[u] & 2:
                    adjacency[u] &= ~left
        self.adjacency = adjacency
        self._parts = None
        self._parts_shape = None

    @property
    def parts(self):
        if self._parts is None:
            self._parts = member_parts(self.adjacency)
        return self._parts

    @property
    def shapes(self):
        if self._parts_shape is None:
            all_met = maximal_sets(self.met_sets)
            member_part = {u: i for i, part in enumerate(self.parts) for u in part}
            by_part = defaultdict(list)
            for met_set in all_met:
                first = (met_set & -met_set).bit_length() - 1
                by_part[member_part[first]].append(met_set)
            self._parts_shape = {
                part: Shape(part, self.h, self.k, by_part[i])
                for i, part in enumerate(self.parts)
            }
        return self._parts_shape

    def past_start(self, part, through_roster):
        if through_roster:
            return not any(self.direct[u] for u in part)
        subset = mask_of(part)
        return not any(self.direct[u] & subset for u in part)

    def direct_counts(self, part):
        subset = mask_of(part)
        found = sum((self.direct[u] & subset).bit_count() for u in part) // 2
        carried = sum(
            (self.direct[u] & self.adjacency[u] & subset).bit_count() for u in part
        ) // 2
        return (found, found - carried)

    def groups(self):
        if self.incidences > 2_000_000:
            raise Guard('holder incidences')
        if sum(m.bit_count() for m in self.adjacency.values()) > 40_000:
            raise Guard('joinable pairs')
        # Pivoted maximal-clique search with an explicit stack. The search is
        # restricted to non-isolated members because singletons cannot join.
        adjacent = self.adjacency
        active = mask_of(u for u, others in adjacent.items() if others)
        stack = [(0, active, 0)]
        joins = []
        covered = defaultdict(int)
        leaves = 0
        maximal_met = maximal_sets(self.met_sets)
        met_containing = defaultdict(list)
        for met in maximal_met:
            for u in bits(met):
                met_containing[u].append(met)
        while stack:
            chosen, candidates, excluded = stack.pop()
            if not (candidates | excluded):
                leaves += 1
                if leaves > 200_000:
                    raise Guard('maximal cliques')
                if chosen.bit_count() < 3:
                    continue
                group = tuple(bits(chosen))
                pivot = min(group, key=lambda u: len(met_containing[u]))
                if any(chosen & m == chosen for m in met_containing[pivot]):
                    continue
                joins.append(group)
                if len(joins) > 20_000:
                    raise Guard('groups')
                for u in group:
                    covered[u] |= chosen
                continue
            pivot = max(bits(candidates | excluded), key=lambda u: (adjacent[u] & candidates).bit_count())
            for u in bits(candidates & ~adjacent[pivot]):
                stack.append((chosen | self.ordinal[u], candidates & adjacent[u], excluded & adjacent[u]))
                candidates ^= self.ordinal[u]
                excluded |= self.ordinal[u]
        pairs = [
            (u, v)
            for u in self.members
            for v in bits(adjacent[u] & ~covered[u])
            if u < v
        ]
        if len(joins) + len(pairs) > 20_000:
            raise Guard('groups')
        return sorted(joins) + pairs


class Shape:
    """Isomorphism of members colored by holdings and of their maximal met sets."""

    def __init__(self, members, h, k, met):
        self.members = members
        local = {u: i for i, u in enumerate(members)}
        self.colors = tuple((h[u], k.get(u, 0)) for u in members)
        self.met = tuple(sorted(tuple(local[u] for u in bits(m)) for m in met))
        self.incident = [[] for _ in members]
        for met_id, met_set in enumerate(self.met):
            for u in met_set:
                self.incident[u].append(met_id)
        degree = [
            (color, tuple(sorted(len(self.met[m]) for m in self.incident[u])))
            for u, color in enumerate(self.colors)
        ]
        self.invariant = (tuple(sorted(degree)), tuple(sorted(map(len, self.met))))

    def same(self, other):
        if self.invariant != other.invariant:
            return False
        if self.colors == other.colors and self.met == other.met:
            return True
        shapes = (self, other)

        def colors_for(items):
            palette = {label: i for i, label in enumerate(sorted({label for group in items for label in group}))}
            return tuple(tuple(palette[label] for label in group) for group in items)

        member_colors = colors_for([shape.colors for shape in shapes])
        met_colors = colors_for([tuple(map(len, shape.met)) for shape in shapes])
        while True:
            new_member = colors_for([
                [(mc[u], tuple(sorted(sc[m] for m in shape.incident[u]))) for u in range(len(mc))]
                for shape, mc, sc in zip(shapes, member_colors, met_colors)
            ])
            new_met = colors_for([
                [(sc[m], tuple(sorted(mc[u] for u in group))) for m, group in enumerate(shape.met)]
                for shape, mc, sc in zip(shapes, member_colors, met_colors)
            ])
            if Counter(new_member[0]) != Counter(new_member[1]) or Counter(new_met[0]) != Counter(new_met[1]):
                return False
            stable = (
                len(set(new_member[0])) == len(set(member_colors[0]))
                and len(set(new_met[0])) == len(set(met_colors[0]))
            )
            member_colors, met_colors = new_member, new_met
            if stable:
                break
        left, right = member_colors
        by_color = defaultdict(list)
        for v, color in enumerate(right):
            by_color[color].append(v)
        order = sorted(range(len(left)), key=lambda u: (len(by_color[left[u]]), -len(self.incident[u]), u))
        mapping = {}
        used = set()

        def signatures(shape, member, subset, met_color):
            return Counter(
                (met_color[m], tuple(sorted(subset[u] for u in shape.met[m] if u in subset)))
                for m in shape.incident[member]
            )

        # Walk partial bijections without using one stack frame per member.
        candidates = [iter(by_color[left[order[0]]])]
        guesses = []
        while candidates:
            i = len(candidates) - 1
            u = order[i]
            v = next(candidates[-1], None)
            if v is None:
                candidates.pop()
                if guesses:
                    old_u, old_v = guesses.pop()
                    del mapping[old_u]
                    used.remove(old_v)
                continue
            if v in used:
                continue
            left_met = signatures(self, u, mapping, met_colors[0])
            right_met = signatures(other, v, {name: name for name in used}, met_colors[1])
            if left_met != right_met:
                continue
            mapping[u] = v
            used.add(v)
            guesses.append((u, v))
            if len(guesses) == len(order):
                return True
            candidates.append(iter(by_color[left[order[i + 1]]]))
        return False


class Growth:
    def __init__(self, start, law, prefix=None, after=0, bar=(), mask=None):
        self.law = law
        self.barred = {}
        self.knots = []
        self.holders = defaultdict(list)
        self.lineage = []
        self.span = Span()
        self.rosters = []
        self.records = []
        self.stop = None
        self.guard = None
        self.mask = mask
        self.sides = []
        self.next_distinction = 0
        if prefix is None:
            for places in start:
                self.add(Knot(0, (), tuple(places)))
        else:
            self.records = prefix.records[:after]
            self.rosters = prefix.rosters[:after]
            self.barred = {d: t for d, t in prefix.barred.items() if t <= after}
            for knot in prefix.knots:
                if knot.born > after:
                    break
                self.add(knot)
        for knot in bar:
            for d in self.knots[knot].places:
                if len(self.holders[d]) == 1 and d not in self.barred:
                    self.barred[d] = after
        self.rosters.append(self.roster())

    def add(self, knot, update_span=True):
        name = len(self.knots)
        self.knots.append(knot)
        ancestors = 0
        side = 0
        for parent in knot.parents:
            ancestors |= self.lineage[parent] | (1 << parent)
            side |= self.sides[parent]
        if self.mask is not None:
            x, y, selected, bar_round = self.mask
            if knot.born <= selected:
                side &= ~1
                if name in x:
                    side |= 1
            if knot.born <= bar_round:
                side &= ~2
                if name in y:
                    side |= 2
        self.sides.append(side)
        self.lineage.append(ancestors)
        for d in knot.places:
            self.holders[d].append(name)
        if knot.places:
            self.next_distinction = max(self.next_distinction, max(knot.places) + 1)
        if self.law.parity and update_span:
            self.span.add(mask_of(knot.places))

    def loose(self):
        usable, barred = defaultdict(list), defaultdict(list)
        for d, owners in self.holders.items():
            if len(owners) == 1:
                target = barred if d in self.barred else usable
                target[owners[0]].append(d)
        return {u: sorted(ds) for u, ds in usable.items()}, barred

    def roster(self):
        loose, barred = self.loose()
        return Roster(self.holders, {u: len(ds) for u, ds in loose.items()}, {u: len(ds) for u, ds in barred.items()})

    def candidates(self, parents):
        rule, _, limit = self.law.taking.partition(':')
        parent = parents[0]
        if rule == 'none':
            return ()
        if rule == 'Q':
            return sorted(d for d in self.knots[parent].places if len(self.holders[d]) > 1) if len(parents) == 1 else ()
        if rule == 'MET':
            if (len(parents) == 1 and limit == 'join') or (len(parents) > 1 and limit == 'offshoot'):
                return ()
            meets = [
                {u for d in self.knots[p].places for u in self.holders[d] if u != p}
                for p in parents
            ]
            sources = set.intersection(*meets)
        else:
            if len(parents) != 1:
                return ()
            parent_count = len(self.knots[parent].parents)
            if (limit == 'join' and parent_count < 2) or (limit == 'offshoot' and parent_count != 1):
                return ()
            depth = int(rule.rsplit('-', 1)[1])
            level = {parent}
            sources = set()
            for step in range(depth):
                level = {p for u in level for p in self.knots[u].parents}
                if step == depth - 1 or rule.startswith('UP-TO'):
                    sources.update(level)
        unavailable = {d for p in parents for d in self.knots[p].places}
        return sorted({
            d for source in sources for d in self.knots[source].places
            if len(self.holders[d]) > 1 and d not in unavailable
        })

    def take(self, parents, ordinary, index):
        eligible = [d for d in self.candidates(parents) if d not in ordinary]
        if not eligible:
            return ()
        choice = self.law.choice
        if choice in ('NONE', 'OLDEST') or (choice == 'IN-TURN' and len(parents) > 1):
            return (eligible[0],)
        if choice == 'NEWEST':
            return (eligible[-1],)
        if choice == 'BY-COUNT':
            index = len(self.knots[parents[0]].places)
        return (eligible[index % len(eligible)],)

    def step(self, t):
        law = self.law
        before = self.rosters[-1]
        current = (
            before if self.mask is None
            else Roster(self.holders, before.h, before.k, self.sides)
        )
        groups = current.groups()
        owed = Counter(u for group in groups for u in group)
        short = {u for u in current.members if owed[u] > current.h[u]}
        waiting = short if law.treatment == 'WAIT' else set()
        retired = short if law.treatment == 'RETIRE' else set()
        old_usable, _ = self.loose()
        supply = {u: iter(ds) for u, ds in old_usable.items()}
        births = []
        for group in groups:
            if not short.intersection(group):
                births.append((group, tuple(next(supply[u]) for u in group), 0))
        for u in current.members:
            if u in waiting or u in retired:
                continue
            for index, d in enumerate(supply[u]):
                births.append(((u,), (d,), index))
        if len(births) > 20_000:
            raise Guard('births')
        first = len(self.knots)
        future_holders = self.holders.copy()
        altered = {}
        inputs = []
        takes = []
        for i, (parents, ordinary, index) in enumerate(births, first):
            take = self.take(parents, ordinary, index)
            takes.append(take)
            inputs.append(ordinary + take)
            for d in ordinary if law.demand_before_takes else ordinary + take:
                if d not in altered:
                    altered[d] = list(self.holders[d])
                altered[d].append(i)
        future_holders.update(altered)
        demand_h = {u: before.h[u] for u in waiting}
        demand_h.update(dict.fromkeys(range(first, first + len(births)), 1))
        future_sides = None
        if self.mask is not None:
            future_sides = self.sides + [
                (1 if any(self.sides[p] & 1 for p in parents) else 0)
                | (2 if any(self.sides[p] & 2 for p in parents) else 0)
                for parents, _, _ in births
            ]
        demand_roster = Roster(future_holders, demand_h, before.k, future_sides)
        try:
            demand = Counter(u for group in demand_roster.groups() for u in group)
        except Guard as err:
            raise Guard(f'demand {err}') from err
        fresh_start = self.next_distinction
        new_knots = []
        for i, (parents, _, _) in enumerate(births):
            used = inputs[i]
            take = takes[i]
            p = len(parents) if law.by_parents else len(set(used))
            d = demand[first + i]
            minimum = max(3 - p, 1)
            fresh = minimum if law.ration == 'FLOOR1' else min(max(d, minimum), 3)
            if law.parity and not self.span.remainder(mask_of(used)):
                fresh = 0
            usable = min(fresh, d) if law.fillers else fresh
            new_places = tuple(range(fresh_start, fresh_start + fresh))
            new_knots.append(Knot(
                t, parents, used + new_places, used, take, d, p, usable, fresh - usable,
                tuple(d for d in used if len(self.holders[d]) > 1),
            ))
            fresh_start += fresh
        if fresh_start > 400_000:
            raise Guard('distinctions')
        for u in retired:
            for d in old_usable[u]:
                self.barred[d] = t
        for knot in new_knots:
            self.add(knot, update_span=False)
            if knot.barred_fresh:
                for d in knot.places[-knot.barred_fresh:]:
                    self.barred[d] = t
        if law.parity:
            for knot in new_knots:
                self.span.add(mask_of(knot.places))
        self.records.append((before, tuple(sorted(short)), tuple(sorted(waiting)), tuple(sorted(retired)), first, tuple(new_knots)))
        self.rosters.append(self.roster())

    def grow(self, rounds=18, knot_bound=4000):
        started = process_time()
        for t in range(len(self.rosters), rounds + 1):
            if process_time() - started >= 600:
                self.stop = 'unfinished'
                break
            try:
                self.step(t)
            except Guard as err:
                self.guard = str(err)
                self.stop = 'guard'
                break
            if len(self.knots) > knot_bound:
                self.stop = 'knots'
                break
        return self

    def round_count(self):
        return len(self.rosters) - 1

    def descends(self, u, part, birth_round):
        if self.knots[u].born <= birth_round:
            return bool((1 << u) & part)
        return bool(self.lineage[u] & part)

    def start_returns(self):
        start = self.rosters[0]
        whole = Shape(start.members, start.h, start.k, maximal_sets(start.met_sets))
        return [
            t for t, roster in enumerate(self.rosters[1:], 1)
            if any(whole.same(shape) for shape in roster.shapes.values())
        ]

    def summary_rounds(self):
        first = len(self.knots) - sum(k.born != 0 for k in self.knots)
        return [[0, len(self.rosters[0].members), len(self.rosters[0].parts), 0, first]] + [
            [t, len(after.members), len(after.parts), len(births), first + len(births)]
            for t, (after, (_, _, _, _, first, births)) in enumerate(zip(self.rosters[1:], self.records), 1)
        ]

    def listing(self):
        rows = []
        # Record input holders immediately before each complete round.
        holders = defaultdict(list)
        for u, knot in enumerate(self.knots):
            if knot.born:
                break
            for d in knot.places:
                holders[d].append(u)
        for t, (roster, short, waiting, retired, first, births) in enumerate(self.records, 1):
            row = {
                'round': t,
                'members_before': list(roster.members),
                'parts_before': [list(p) for p in roster.parts],
                'short': list(short),
                'waiting': list(waiting),
                'retired': list(retired),
                'births': [
                    {
                        'id': u, 'kind': 'join' if len(k.parents) > 1 else 'offshoot',
                        'parents': list(k.parents), 'inputs': [[d, list(holders[d])] for d in k.inputs],
                        'taken_by_rule': list(k.take), 'D': k.demand, 'p': k.ration_input,
                        'f': k.usable_fresh + k.barred_fresh,
                        'usable': k.usable_fresh, 'barred': k.barred_fresh,
                    }
                    for u, k in enumerate(births, first)
                ],
            }
            rows.append(row)
            for u, knot in enumerate(births, first):
                for d in knot.places:
                    holders[d].append(u)
        return rows


@dataclass(frozen=True)
class Tick:
    round: int
    qualifies: tuple
    off: tuple
    mixed: int
    direct: int
    uncarried: int


class Returns:
    def __init__(self, growth, past=False, greatest=False, through_roster=False):
        self.growth = growth
        self.greatest = greatest
        self.from_part = {}
        self.starts = []
        frames = []
        for t, roster in enumerate(growth.rosters):
            by_invariant = defaultdict(list)
            for part, shape in roster.shapes.items():
                by_invariant[shape.invariant].append((part, shape))
            frames.append(by_invariant)
        followed = set()
        for s, roster in enumerate(growth.rosters[:-1]):
            for part, shape in roster.shapes.items():
                if past and not roster.past_start(part, through_roster):
                    continue
                self.starts.append((s, part))
                original = mask_of(part)
                for t in range(s + 1, len(frames)):
                    qualifies = tuple(
                        q for q, target in frames[t].get(shape.invariant, ())
                        if any(growth.knots[u].born > s for u in q)
                        and all(growth.descends(u, original, s) for u in q)
                        and shape.same(target)
                    )
                    if not qualifies:
                        continue
                    new_roster = growth.rosters[t]
                    next_part = self.choose(qualifies)
                    off = []
                    mixed = 0
                    for q in new_roster.parts:
                        if q in qualifies:
                            continue
                        desc = [growth.descends(u, original, s) for u in q]
                        if any(desc):
                            off.append(q)
                            mixed += not all(desc)
                    direct, uncarried = new_roster.direct_counts(next_part)
                    self.from_part[s, part] = Tick(t, qualifies, tuple(off), mixed, direct, uncarried)
                    followed.add((t, next_part))
                    break
        self.starts = [key for key in self.starts if key not in followed]

    def choose(self, qualifies):
        return qualifies[-1] if self.greatest else qualifies[0]

    def chain(self, start):
        ticks = []
        while start in self.from_part:
            tick = self.from_part[start]
            ticks.append(tick)
            start = (tick.round, self.choose(tick.qualifies))
        return ticks

    @staticmethod
    def periods(start_round, ticks):
        all_rounds = [start_round] + [tick.round for tick in ticks]
        return [b - a for a, b in zip(all_rounds, all_rounds[1:])]

    def records(self, include_single=False):
        records = []
        for start in self.starts:
            s, part = start
            ticks = self.chain(start)
            if not ticks or (len(part) == 1 and not include_single):
                continue
            periods = self.periods(s, ticks)
            stretches = [i for i in range(len(periods) - 3) if len(set(periods[i:i + 4])) == 1]
            records.append({
                't0': s, 'P0': list(part), 'size': len(part), 'periods': periods,
                'ticks': [
                    [tick.round, list(self.choose(tick.qualifies)), len(tick.off), tick.mixed,
                     len(tick.qualifies) - 1, tick.direct, tick.uncarried]
                    for tick in ticks
                ],
                'clock': len(part) > 1 and bool(stretches),
                'clock_off4': len(part) > 1 and any(all(tick.off for tick in ticks[i:i + 4]) for i in stretches),
                'ticks_off': sum(bool(tick.off) for tick in ticks),
            })
        return records

    def endless(self):
        return [
            [s, list(part), [tick.round for tick in all_ticks]]
            for s, part in self.starts
            if len(part) == 1 and (all_ticks := self.chain((s, part)))
        ]

    def metrics(self, series, endless):
        # All searched origins, including a part with no tick, contribute to n_series.
        every_chain = [self.chain(key) for key in self.starts]
        off = [sum(bool(t.off) for t in ticks) for ticks in every_chain]
        return {
            'n_series': len(self.starts),
            'n_clocks': sum(row['clock'] for row in series),
            'clock': any(row['clock'] for row in series),
            'clock_off4': any(row['clock_off4'] for row in series),
            'clock_off4_anywhere': any(row['clock'] and row['ticks_off'] >= 4 for row in series),
            'series_off2': any(n >= 2 for n in off),
            'tick_off_any': any(off),
            'max_ticks_off': max(off, default=0),
            'max_ticks_off_or_copies': max((
                sum(bool(t.off or len(t.qualifies) > 1) for t in ticks) for ticks in every_chain
            ), default=0),
            'copies': sum(len(t.qualifies) - 1 for ticks in every_chain for t in ticks),
            'direct_not_carried': sum(t.uncarried for ticks in every_chain for t in ticks),
            'mixed_parts_given_off': sum(t.mixed for ticks in every_chain for t in ticks),
            'endless_chains': len(endless),
        }
