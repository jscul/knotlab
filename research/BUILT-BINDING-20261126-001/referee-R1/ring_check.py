"""Rebuild the 32 ring preparations and test their measured parity functions.

The groups and fresh counts follow the complete-round definitions in the
fresh-count proof, section 0, and the ordinary end operator. The only study
outputs read here are comparison targets. Distinction numbers are local to
this reconstruction. One process, two GiB, from the repository root:

    .venv/bin/python -B research/BUILT-BINDING-20261126-001/referee-R1/ring_check.py --pilot
    .venv/bin/python -B research/BUILT-BINDING-20261126-001/referee-R1/ring_check.py --run
"""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from functools import reduce
from itertools import combinations, product
import json
from operator import xor
from pathlib import Path
import resource
from time import perf_counter


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
LIMIT = 2 * 1024 ** 3


def total(words):
    return reduce(xor, words, 0)


def bits(word):
    while word:
        small = word & -word
        yield small.bit_length() - 1
        word ^= small


def mask(values):
    return total(1 << x for x in values)


def basis(words):
    out = {}
    for word in words:
        while word:
            place = word.bit_length()
            if place not in out:
                out[place] = word
                break
            word ^= out[place]
    return out


def remainder(word, pivots):
    for place in sorted(pivots, reverse=True):
        if word & (1 << (place - 1)):
            word ^= pivots[place]
    return word


def possible_values(reads):
    # Exact allowed tuples from the restrictions to a basis of all allowed changes.
    equations = [q for q in range(1, 1 << len(reads))
                 if total(reads[j] for j in bits(q)) == 0]
    return [state for state in range(1 << len(reads))
            if all((state & q).bit_count() % 2 == 0 for q in equations)]


def even_table(values, places):
    return values == [v for v in range(1 << places) if v.bit_count() % 2 == 0]


def ring_start(count, length, attachment, link):
    rows = [[] for _ in range(count * length)]
    rings = [list(range(i * length, (i + 1) * length)) for i in range(count)]
    loose = [[] for _ in rings]
    joins = [[] for _ in rings]
    attachments = [[] for _ in rings]
    next_bit = 0

    def add(*holders):
        nonlocal next_bit
        for k in holders:
            rows[k].append(next_bit)
        next_bit += 1
        return next_bit - 1

    def knot():
        rows.append([])
        return len(rows) - 1

    for i, ring in enumerate(rings):
        for j, k in enumerate(ring):
            loose[i].extend([add(k), add(k)])
            add(k, ring[(j + 1) % length])
    for r, s in combinations(range(count), 2):
        ends = [knot(), knot()]
        for i, end in zip((r, s), ends):
            p = len(joins[i])
            places = (p, p + 2) if attachment == 'split' else (2 * p, 2 * p)
            for place in places:
                attachments[i].append(add(end, rings[i][place % length]))
            joins[i].append(end)
        a, b = ends
        add(a, b)
        if link == 'double':
            add(a, b)
        else:
            chain = [a, knot(), knot(), knot(), b]
            for left, right in zip(chain, chain[1:]):
                add(left, right)
                add(left, right)
    return rows, rings, loose, joins, attachments


def locations(rows):
    holds = defaultdict(list)
    for k, row in enumerate(rows):
        for x in row:
            holds[x].append(k)
    assert all(1 <= len(v) <= 2 and len(v) == len(set(v)) for v in holds.values())
    return holds


def groups(neighbours):
    # A maximal valid set is a maximal clique of candidates without a
    # common witness. A pair covered by no such set gets its own birth.
    seen_by = defaultdict(set)
    for k, others in neighbours.items():
        for other in others:
            seen_by[other].add(k)
    candidates = {k: set() for k in neighbours}
    for members in seen_by.values():
        for k in members:
            candidates[k].update(members - {k})
    large = []

    def maximal(chosen, remaining, excluded):
        if not remaining and not excluded:
            if len(chosen) >= 3 and not set.intersection(*(neighbours[k] for k in chosen)):
                large.append(tuple(sorted(chosen)))
            return
        pivot = max(remaining | excluded, key=lambda k: len(remaining & candidates[k]))
        for k in sorted(remaining - candidates[pivot]):
            maximal(chosen | {k}, remaining & candidates[k], excluded & candidates[k])
            remaining.remove(k)
            excluded.add(k)

    if candidates:
        maximal(set(), set(candidates), set())
    covered = {pair for group in large for pair in combinations(group, 2)}
    pairs = [(k, j) for k, others in candidates.items() for j in others
             if k < j and (k, j) not in covered]
    return sorted(large + pairs)


def grow(rows):
    holds = locations(rows)
    loose = defaultdict(list)
    meet = [set() for _ in rows]
    for x, ks in holds.items():
        if len(ks) == 1:
            loose[ks[0]].append(x)
        else:
            a, b = ks
            meet[a].add(b)
            meet[b].add(a)
    if not loose:
        return rows, 'closed', []
    proposals = groups({k: meet[k] for k in loose})
    demand = Counter(k for p in proposals for k in p)
    if any(demand[k] > len(items) for k, items in loose.items()):
        return rows, 'stalled', []
    for k, items in sorted(loose.items()):
        proposals.extend([(k,)] * (len(items) - demand[k]))
    proposals.sort()
    next_groups = groups({i: set(p) for i, p in enumerate(proposals)})
    future = Counter(i for g in next_groups for i in g)
    laws = basis(mask(r) for r in rows)
    new_rows = list(rows)
    births = []
    unused = {k: iter(sorted(xs)) for k, xs in loose.items()}
    next_bit = max(holds) + 1
    for i, parents in enumerate(proposals):
        inputs = [next(unused[k]) for k in parents]
        closing = remainder(mask(inputs), laws) == 0
        count = 0 if closing else max(future[i], 3 - len(parents), 1)
        fresh = list(range(next_bit, next_bit + count))
        births.append((len(new_rows), parents, inputs, fresh))
        new_rows.append(inputs + fresh)
        next_bit += count
    return new_rows, 'funded', births


class Reading:
    """Allowed changes are exactly the even subsets at each holder.

    Putting each loose distinction between its holder and U adds a redundant
    parity check at U. Closing each non-tree distinction along a spanning
    forest gives independent allowed changes with every allowed change in
    their span. A read's values on these changes identify its function.
    """

    def __init__(self, rows):
        self.rows = rows
        self.outside = len(rows)
        self.ends = {x: tuple(ks) if len(ks) == 2 else (ks[0], self.outside)
                     for x, ks in locations(rows).items()}
        self.by_pair = defaultdict(list)
        self.neighbours = [set() for _ in range(self.outside + 1)]
        for x, (a, b) in self.ends.items():
            self.by_pair[tuple(sorted((a, b)))].append(x)
            self.neighbours[a].add(b)
            self.neighbours[b].add(a)
        path = {}
        for k in range(self.outside + 1):
            if k in path:
                continue
            path[k] = 0
            todo = [k]
            while todo:
                a = todo.pop()
                for b in sorted(self.neighbours[a]):
                    if b not in path:
                        x = self.by_pair[tuple(sorted((a, b)))][0]
                        path[b] = path[a] ^ (1 << x)
                        todo.append(b)
        self.value = dict.fromkeys(self.ends, 0)
        dim = 0
        for x, (a, b) in self.ends.items():
            cycle = (1 << x) ^ path[a] ^ path[b]
            if cycle:
                for y in bits(cycle):
                    self.value[y] |= 1 << dim
                dim += 1
        self.dimension = dim
        self.local = [basis(self.value[x] for x in row) for row in rows]
        self.laws = {}
        for k, row in enumerate(rows):
            v, ks = mask(row), 1 << k
            while v and v.bit_length() in self.laws:
                w, js = self.laws[v.bit_length()]
                v, ks = v ^ w, ks ^ js
            if v:
                self.laws[v.bit_length()] = (v, ks)
        assert len(self.laws) + dim == len(self.ends)
        self.short, self.small = self.find_moves()

    def law_sum(self, support):
        used = 0
        while support and support.bit_length() in self.laws:
            v, k = self.laws[support.bit_length()]
            support, used = support ^ v, used ^ k
        return None if support else used

    def function(self, support):
        return total(self.value[x] for x in bits(support))

    def find_moves(self):
        short, small = set(), set()
        for (start, end), entries in self.by_pair.items():
            tied = len(entries) > 1
            if tied:
                for a, b in combinations(entries, 2):
                    pair = (1 << a) | (1 << b)
                    short.add(pair)
                    small.add(pair)
            # Distances to end, ignoring the direct meeting. Each shortest
            # return path gives one shortest change through the selected
            # distinction, unless that distinction already has a two-change.
            dist = {end: 0}
            queue = deque([end])
            while queue:
                a = queue.popleft()
                for b in self.neighbours[a]:
                    if (a == end and b == start) or (a == start and b == end):
                        continue
                    if b not in dist:
                        dist[b] = dist[a] + 1
                        queue.append(b)
            if start not in dist:
                continue
            shortest_return = dist[start]
            limit = max(4, shortest_return) if not tied else 4
            if shortest_return > limit:
                continue

            def returns(a, visited, route):
                if a == end:
                    sizes = len(route) + 1
                    for chosen in product(entries, *route):
                        move = mask(chosen)
                        if sizes <= 5:
                            small.add(move)
                        if not tied and len(route) == shortest_return:
                            short.add(move)
                    return
                for b in self.neighbours[a] - visited:
                    if (a == start and b == end) or len(route) + 1 + dist[b] > limit:
                        continue
                    hop = self.by_pair[tuple(sorted((a, b)))]
                    returns(b, visited | {b}, route + [hop])

            returns(start, {start}, [])
        # Every allowed change of size <=5 splits into simple cycles of
        # size <=5. Their span tests invariance on all such changes exactly.
        return short, small

    def least_change(self, support):
        # A shortest change reversing a parity is a simple cycle with odd
        # overlap. In the parity double cover it has an ordinary shortest
        # path from (k,0) to (k,1) at one holder of an intersected bit.
        signed = defaultdict(set)
        for x, (a, b) in self.ends.items():
            sign = int(bool(support & (1 << x)))
            signed[a].add((b, sign))
            signed[b].add((a, sign))
        best = None
        for k in {self.ends[x][0] for x in bits(support)}:
            q = deque([(k, 0, 0)])
            seen = {(k, 0)}
            while q:
                a, sign, length = q.popleft()
                if (a, sign) == (k, 1):
                    best = length
                    break
                if best is not None and length + 1 >= best:
                    continue
                for b, delta in signed[a]:
                    state = (b, sign ^ delta)
                    if state not in seen:
                        seen.add(state)
                        q.append((*state, length + 1))
        return best

    def flags(self, support):
        f = self.function(support)
        return [bool(f) and all(not ((m & support).bit_count() % 2) for m in moves)
                for moves in (self.short, self.small)]

    def pieces(self, support):
        by_knot = defaultdict(set)
        for x in bits(support):
            for k in self.ends[x]:
                by_knot[k].add(x)
        todo = set(by_knot)
        parts = []
        while todo:
            root = min(todo)
            todo.remove(root)
            pending, knots, ds = [root], {root}, set()
            while pending:
                for x in by_knot[pending.pop()]:
                    ds.add(x)
                    for k in self.ends[x]:
                        if k not in knots:
                            pending.append(k)
                            knots.add(k)
                            todo.remove(k)
            support_part = mask(ds)
            parts.append({'size': len(ds), 'distinctions': sorted(ds), 'holders': len(knots),
                          'counts per holder': dict(sorted(Counter(len(by_knot[k]) for k in knots).items())),
                          'single cycle': self.outside not in knots and all(len(by_knot[k]) == 2 for k in knots),
                          'class fact shortest and up to five': self.flags(support_part),
                          'knots reading parity': self.reading_knots(support_part)})
        return parts

    def reading_knots(self, support):
        f = self.function(support)
        return [k for k, sub in enumerate(self.local) if remainder(f, sub) == 0]

    def partial(self, support):
        size = support.bit_count()
        rank = len(basis(self.value[x] for x in bits(support)))
        omittable = []
        if size != rank:
            for x in bits(support):
                others = basis(self.value[j] for j in bits(support ^ (1 << x)))
                if remainder(self.function(support), others) == 0:
                    omittable.append(x)
        return {'size': size, 'independent distinction values': rank,
                'distinctions omittable when reading this parity': omittable,
                'independent class facts on this support, shortest and up to five':
                    [rank - len(basis(m & support for m in moves)) for moves in (self.short, self.small)],
                'components': self.pieces(support)}


def describe(read, supports, start, loose, attachments, old_count):
    fs = [read.function(s) for s in supports]
    values = possible_values(fs)
    assert even_table(values, len(fs))
    eq = read.law_sum(total(supports))
    assert eq is not None and len(read.laws) == len(read.rows)
    splits = mask(range(old_count))
    oldbasis = basis(read.value[x] for x in start.ends)
    return {'sizes': [s.bit_count() for s in supports], 'tuples': values,
            'free after any one fact is forgotten': all(len(possible_values(fs[:i] + fs[i+1:])) == 2 ** (len(fs)-1) for i in range(len(fs))),
            'smallest number of tuples with one knot fixed': min(len(possible_values([remainder(f, sub) for f in fs])) for sub in read.local),
            'class facts shortest and up to five': [read.flags(s) for s in supports],
            'knots reading each parity': [read.reading_knots(s) for s in supports],
            'has a start representative': [remainder(f, oldbasis) == 0 for f in fs],
            'matches ring loose representative': [f == read.function(s) for f, s in zip(fs, loose)],
            'matches attachment representative': [f == read.function(s) for f, s in zip(fs, attachments)],
            'the start representatives take these same tuples': possible_values([start.function(s) for s in loose]) == values,
            'law deletions freeing all tuples, start and later': [(eq & splits).bit_count(), (eq & ~splits).bit_count()],
            'law deletions considered, start and later': [old_count, len(read.rows) - old_count]}


def archive_comparison(record, data, stage0):
    misses = []
    def check(name, got, want):
        if got != want:
            misses.append({'field': name, 'reconstructed': got, 'recorded': want})
    check('carrier sizes', data['sizes'], record['carriers'])
    check('tuples', len(data['tuples']), record['tuples'])
    check('one rule', even_table(data['tuples'], len(data['sizes'])), record['one rule'])
    check('tuple denominator', 2 ** len(data['sizes']), record['of'])
    for j, name in enumerate(('SHORT', 'UPTO5')):
        check(name, [[row[j], not loc] for row, loc in zip(data['class facts shortest and up to five'], data['knots reading each parity'])], record[name])
        check('start ' + name, [[row[j], not loc] for row, loc in zip(stage0['class facts shortest and up to five'], stage0['knots reading each parity'])], record['origin']['facts at the start, ' + name])
    orig = record['origin']
    check('start representative exists', data['has a start representative'], orig['each carrier a function of the start values'])
    check('representative sizes', stage0['sizes'], orig['start representatives (sizes)'])
    check('one rule at start', even_table(stage0['tuples'], len(stage0['sizes'])), orig["relation on the start's allowed states"])
    check('start laws force the sum', all(v.bit_count() % 2 == 0 for v in stage0['tuples']), orig['sum of the representatives a sum of start laws'])
    if 'the same joint values at the start' in orig:
        check('same values at start', data['the start representatives take these same tuples'], orig['the same joint values at the start'])
        check('count at start', len(stage0['tuples']), orig['tuples at the start'])
    deletion = record['laws whose removal frees every tuple']
    check('release by deletion', data['law deletions freeing all tuples, start and later'], [deletion['start knots'], deletion['born knots']])
    check('deletions considered', data['law deletions considered, start and later'], deletion['of start / born'])
    return misses


def retain(rows, knots):
    return [rows[k] for k in sorted(knots)]


def peel_rings(read):
    """Infer the rings on these preparations without source or round labels.

    The latest knots are exactly the loose-holding ones until distinct live
    knots meet directly. At that first such stage the directly meeting live
    knots give the source rings. Follow parents forward in the removed stages.
    The input to this reader is just the supports of the final stage.
    """
    kept = set(range(len(read.rows)))
    layers = []
    while kept:
        who = defaultdict(set)
        for k in kept:
            for x in read.rows[k]:
                who[x].add(k)
        live = set.union(*(ks for ks in who.values() if len(ks) == 1))
        meet = {k: set() for k in live}
        for ks in who.values():
            if len(ks) == 2 and ks <= live:
                a, b = ks
                meet[a].add(b)
                meet[b].add(a)
        if any(meet.values()):
            break
        layers.append({child: set.union(*(who[x] for x in read.rows[child])) - {child} for child in live})
        kept -= live
    ring_of = {}
    for k in sorted(live):
        if k in ring_of:
            continue
        tag = k
        ring_of[k] = tag
        todo = [k]
        while todo:
            for other in meet[todo.pop()]:
                if other not in ring_of:
                    ring_of[other] = tag
                    todo.append(other)
    for parents in reversed(layers):
        for child, older in parents.items():
            tags = {ring_of[k] for k in older}
            assert len(tags) == 1
            ring_of[child] = tags.pop()
    latest = {k for k, b in read.ends.values() if b == read.outside}
    supports = defaultdict(int)
    for x, ks in read.ends.items():
        touching = set(ks) & latest
        if touching and read.outside not in ks:
            assert len(touching) == 1
            supports[ring_of[touching.pop()]] |= 1 << x
    return sorted(supports.values()), len(layers)


def component_relation(read, source, components, starts):
    qs = [mask(part['distinctions']) for part in components]
    functions = [read.function(q) for q in qs]
    distinct = [(i, j) for i, f in enumerate(functions) for j, s in enumerate(starts) if read.function(s) == f]
    assert len(distinct) == len(starts) == len({j for _,j in distinct}) == len(qs)
    image = possible_values(functions)
    fixed = min(2 ** len(basis(remainder(f, row) for f in functions)) for row in read.local)
    assert even_table(image, len(qs))
    ordered_starts = [starts[j] for _,j in sorted(distinct)]
    assert image == possible_values([source.function(s) for s in ordered_starts])
    return {'component sizes': [q.bit_count() for q in qs], 'tuples': image,
            'every proper subfamily free': all(2 ** len(basis(functions[:i] + functions[i+1:])) == 2 ** (len(qs)-1) for i in range(len(qs))),
            'smallest number of tuples with one knot fixed': fixed,
            'start representatives': [list(bits(s)) for s in ordered_starts],
            'each component is a class fact, shortest and up to five': [read.flags(q) for q in qs],
            'knots reading each component': [read.reading_knots(q) for q in qs],
            'each representative a class fact before growth, shortest and up to five': [source.flags(s) for s in ordered_starts]}


def isolated(rows, source, ring, joins, descent, s):
    # Keep the ring, its attachment knots and its descendants in the given
    # grown stage. Each isolated copy gets its own newly loose distinctions.
    subset = set(ring) | set(joins) | set(descent)
    sliced = Reading(retain(rows, subset))
    assert all(x in sliced.value for x in bits(s))
    isolated_source = retain(source, set(ring) | set(joins))
    fresh_rows, status, _ = grow(isolated_source)
    different = None
    if status == 'funded':
        different = len(fresh_rows) - len(isolated_source)
    return {'knots in retained stage': len(subset), 'values': possible_values([sliced.function(s)]),
            'class fact shortest and up to five': sliced.flags(s),
            'least change flipping the retained parity': sliced.least_change(s),
            'knots reading parity': sliced.reading_knots(s),
            'growing the isolated start itself, first round': status,
            'births on growing the isolated start itself': different}


def audit_member(params, archive, earlier):
    count, length, attachment, link = params
    label = f'{count} rings of {length}, {attachment}, {link}'
    source, rings, loose_list, joins, attach_list = ring_start(*params)
    loose = [mask(xs) for xs in loose_list]
    attachments = [mask(xs) for xs in attach_list]
    rows = source
    start = Reading(source)
    # A move changing a start representative changes every equivalent
    # representative. This test also allows arbitrary reads at one knot.
    start_summary = describe(start, loose, start, loose, attachments, len(source))
    start_sums = [start.law_sum(l ^ a) for l, a in zip(loose, attachments)]
    assert all(value == mask(r) for value, r in zip(start_sums, rings))
    assert start.law_sum(total(loose)) == mask(range(len(source)))
    out = {'family': label, 'start knots': len(source), 'start distinctions': len(start.ends),
           'attachment distinctions per ring': [q.bit_count() for q in attachments],
           'connecting knots holding each attachment representative': joins,
           'all start laws give the sum of the loose representatives': True,
           'ring laws give the attachment representative': True,
           'attachment representatives distinct from each other and the loose groups':
               not any(a & b for a, b in combinations(attachments, 2)) and not (total(attachments) & total(loose)),
           'rounds': [], 'record differences': [], 'pre-freeze record differences': []}
    ar = archive[label]
    assert ar['new carriers']['knots'] == len(source) and ar['new carriers']['distinctions'] == len(start.ends)
    old_roster = {k: i for i, r in enumerate(rings) for k in r}
    last = None
    for t in range(4):
        ar_start = ar['start groups']['rounds'][t]
        if not t:
            reading = start
            spent, born = None, []
        else:
            rows, status, born = grow(rows)
            assert status == 'funded'
            reading = Reading(rows)
            ar_next = ar['new carriers']['rounds'][t-1]
            assert ar_next['distinctions'] == len(reading.ends)
            collected = [[] for _ in rings]
            for child, parents, _, fresh in born:
                parent_rings = {old_roster.get(k) for k in parents}
                if len(parent_rings) == 1 and None not in parent_rings:
                    ring = parent_rings.pop()
                    collected[ring].extend(fresh)
                    old_roster[child] = ring
            spent, last = last, [mask(group) for group in collected]
        old = describe(reading, loose, start, loose, attachments, len(source))
        under_cap = len(reading.ends) <= 500
        if under_cap:
            for diff in archive_comparison(ar_start, old, start_summary):
                out['record differences'].append({'round': t, 'reader': 'start groups', **diff})
        else:
            assert ar_start['end'] == 'not read'
        row = {'round': t, 'knots': len(rows), 'distinctions': len(reading.ends),
               'within original cap': under_cap, 'allowed state dimension': reading.dimension,
               'number of shortest changes': len(reading.short),
               'number of simple cycles of at most five distinctions': len(reading.small),
               'least change flipping the parity of each ring': [reading.least_change(a) for a in attachments],
               'shortest changes using an attachment of each ring': [sum(bool(m & a) for m in reading.short) for a in attachments],
               'simple cycles of at most five using an attachment of each ring': [sum(bool(m & a) for m in reading.small) for a in attachments],
               'start groups': old}
        if t and attachment == 'split':
            a, middle, b = rings[0][:3]
            connector = joins[0][0]
            tour = [a, middle, b, connector, a]
            chosen = [reading.by_pair[tuple(sorted((u, v)))][0] for u,v in zip(tour, tour[1:])]
            crossing = mask(chosen)
            assert crossing in reading.small and (crossing & attachments[0]).bit_count() == 2
            row['four-distinction change leaving and returning to the first ring'] = {
                    'successive holders': tour, 'distinctions': chosen, 'one of the shortest changes': crossing in reading.short,
                    'changes made to the attachment parity': (crossing & attachments[0]).bit_count() % 2}
        if t == 1:
            control = next(b for b in born if len(b[3]) >= 2)
            k, _, inputs, fresh = control
            fs = [mask(fresh[:1]), mask(fresh[1:]), mask(inputs)]
            functions = [reading.function(f) for f in fs]
            oldbasis = basis(reading.value[x] for x in start.ends)
            origin = [remainder(f, oldbasis) == 0 for f in functions]
            actual_reads = [reading.reading_knots(f) for f in fs]
            archive_control = ar['origin control']
            measured = possible_values(functions)
            row['origin control'] = {'birth': k, 'numbers of inputs and fresh distinctions': [len(inputs), len(fresh)],
                    'values': measured, 'has a start representative': origin,
                    'class facts shortest and up to five': [reading.flags(f) for f in fs],
                    'knots reading each parity': actual_reads,
                    'recorded unread flags': [pair[1] for pair in archive_control['facts SHORT']]}
            assert origin == archive_control['origin'] and even_table(measured, 3) == archive_control['one rule']
            assert len(measured) == archive_control['tuples'] and all(k in r for r in actual_reads)
            flip = mask(fresh[:2])
            assert flip in reading.short and flip in reading.small and not set(bits(flip)) & set(start.ends)
            row['origin control']['two fresh distinctions flipped with all start values fixed'] = fresh[:2]
        if t >= 2:
            new = describe(reading, spent, start, loose, attachments, len(source))
            assert all(new['matches ring loose representative']) and all(new['matches attachment representative'])
            assert not any(a & b for a, b in combinations(spent, 2))
            assert all(not (a & b) for a, b in zip(spent, attachments))
            assert all(c < q for c, q in zip(out['attachment distinctions per ring'], new['sizes']))
            new['within each selected carrier'] = [reading.partial(s) for s in spent]
            recovered, peeled = peel_rings(reading)
            assert recovered == sorted(spent) and peeled == t
            new['source rings recovered from the grown supports alone'] = True
            live = {k for k, b in reading.ends.values() if b == reading.outside}
            made = mask(x for x, ks in reading.ends.items() if reading.outside not in ks and live.intersection(ks))
            assert made == total(spent)
            components = reading.pieces(made)
            if length % 2:
                starts = loose
            else:
                starts = [mask(loose_list[i][2*j + k] for j in range(h, length, 2) for k in (0, 1))
                          for i in range(count) for h in range(2)]
            new['components found without source ring labels'] = component_relation(reading, start, components, starts)
            row['new carriers'] = new
            key = f'carriers born in round {t-1}'
            if under_cap:
                for diff in archive_comparison(ar_next[key], new, start_summary):
                    out['record differences'].append({'round': t, 'reader': 'new carriers', **diff})
            else:
                assert key not in ar_next
            if label in earlier:
                original = earlier[label]
                assert original['knots'] == len(source) and original['distinctions'] == len(start.ends)
                original_round = original['rounds'][t-1]
                assert original_round['distinctions'] == len(reading.ends)
                for diff in archive_comparison(original_round[key], new, start_summary):
                    out['pre-freeze record differences'].append({'round': t, **diff})
                if t == 2:
                    row['independently kept preparations'] = [
                        isolated(rows, source, rings[i], joins[i],
                                 [k for k, r in old_roster.items() if r == i and k >= len(source)], s)
                        for i, s in enumerate(spent)]
                    row['tuples on separately prepared copies'] = reduce(lambda a, b: a*b,
                            [len(x['values']) for x in row['independently kept preparations']], 1)
        out['rounds'].append(row)
    return out


def archived():
    data = defaultdict(dict)
    for line in (STUDY / 'frozen_built.jsonl').read_text().splitlines():
        rec = json.loads(line)
        if rec['part'] == 'origin control':
            data[rec['family']]['origin control'] = rec
        else:
            key = next(k for k in ('new carriers', 'start groups') if k in rec)
            assert key not in data[rec[key]['family']]
            data[rec[key]['family']][key] = rec[key]
    labels = {"three rings of five, detour (the referee's 30 knots)": '3 rings of 5, split, detour',
              'three rings of five, two direct links': '3 rings of 5, split, double',
              'three rings of five, paired attachments': '3 rings of 5, paired, double'}
    old = {labels[r['family']]: r for r in map(json.loads, (STUDY / 'repro_explore.jsonl').read_text().splitlines())}
    return data, old


def totals(cases):
    rows = [row for c in cases for row in c['rounds'] if row['within original cap']]
    new = [row for row in rows if 'new carriers' in row]
    carriers = [s for row in new for s in row['new carriers']['within each selected carrier']]
    component_rows = [r['new carriers']['components found without source ring labels'] for r in new]
    finer = [r for r in component_rows if len(r['component sizes']) > 4]
    isolation = [part for r in rows for part in r.get('independently kept preparations', [])]
    controls = [r['origin control'] for r in rows if 'origin control' in r]
    sizes = defaultdict(Counter)
    for c in cases:
        length = c['family'].split()[3].strip(',')
        for row in c['rounds']:
            if 'new carriers' not in row or not row['within original cap']:
                continue
            for s in row['new carriers']['within each selected carrier']:
                pattern = tuple((p['size'], p['single cycle']) for p in s['components'])
                dims = tuple(s['independent class facts on this support, shortest and up to five'])
                sizes[f'{length} knots per ring, round {row["round"]}'][(pattern, dims)] += 1
    return {'families': len(cases), 'start-group stages read in original scope': len(rows),
            'new-carrier stages in original scope': len(new), 'new carriers in original scope': len(carriers),
            'new-carrier stages additionally read beyond original size cap': sum(1 for c in cases for r in c['rounds'] if not r['within original cap']),
            'archived new and start-group comparison differences': sum(len(c['record differences']) for c in cases),
            'pre-freeze comparison differences': sum(len(c['pre-freeze record differences']) for c in cases),
            'simple-cycle carriers': sum(len(s['components']) == 1 and s['components'][0]['single cycle'] for s in carriers),
            'freely assigned designated supports': sum(s['size'] == s['independent distinction values'] for s in carriers),
            'new-carrier stages with author grouping recovered from final stage supports alone':
                sum(r['new carriers']['source rings recovered from the grown supports alone'] for r in new),
            'six-part stages yielding all 32 even tuples after fixing any one knot':
                sum(len(r['component sizes']) == 6 and len(r['tuples']) == r['smallest number of tuples with one knot fixed'] == 32 for r in finer),
            'eight-part stages yielding all 128 even tuples after fixing any one knot':
                sum(len(r['component sizes']) == 8 and len(r['tuples']) == r['smallest number of tuples with one knot fixed'] == 128 for r in finer),
            'component facts on the even-length families': sum(len(r['component sizes']) for r in finer),
            'origin-control quantities read by their own birth despite a recorded unread flag':
                sum(r['birth'] in readers and unread for r in controls for readers, unread in zip(r['knots reading each parity'], r['recorded unread flags'])),
            'rings separately retained at round two across the three earlier preparations': len(isolation),
            'retained rings contributing a nonconstant fact, shortest and up to five':
                [sum(p['class fact shortest and up to five'][j] for p in isolation) for j in range(2)],
            'independently regrown isolated sources stopping on round one':
                sum(p['growing the isolated start itself, first round'] == 'stalled' for p in isolation),
            'designated supports with omittable distinctions': sum(bool(s['distinctions omittable when reading this parity']) for s in carriers),
            'carriers supporting multiple independent class facts, shortest and up to five':
                [sum(s['independent class facts on this support, shortest and up to five'][j] > 1 for s in carriers) for j in range(2)],
            'new-carrier stages with full measured tuple set after fixing any single knot':
                sum(r['new carriers']['smallest number of tuples with one knot fixed'] == len(r['new carriers']['tuples']) for r in new),
            'new-carrier stages whose six-or-four attachment representatives all use fewer distinctions':
                sum(all(a < b for a,b in zip(c['attachment distinctions per ring'], r['new carriers']['sizes']))
                    for c in cases for r in c['rounds'] if 'new carriers' in r and r['within original cap']),
            'component sizes, cycles and class counts': {s:[{'size and single-cycle status of each component': pattern,
                    'independent class facts, shortest and up to five': dims, 'number of carriers': n}
                    for (pattern,dims),n in counts.items()] for s,counts in sizes.items()}}


def main():
    parser = ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--pilot', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (LIMIT, LIMIT))
    all_params = list(product((3, 4), (4, 5, 6, 7), ('split', 'paired'), ('double','detour')))
    # Timings use identical code, including a five-knot isolation and the
    # largest (six-knot, four-ring) stage, before the full roster is read.
    pilots = [(3, 5, 'split', 'detour'), (4, 6, 'split', 'detour')]
    comparison, earlier = archived()
    cases = []
    for params in (pilots if args.pilot else all_params):
        then = perf_counter()
        case = audit_member(params, comparison, earlier)
        case['elapsed seconds'] = round(perf_counter() - then, 4)
        cases.append(case)
        if args.pilot:
            print(case['family'], case['elapsed seconds'], 'seconds', flush=True)
    out = {'scope': 'All 32 constructed families, both move rules; the two published size omissions are read separately.',
           'shortest rule': 'All shortest allowed changes through each distinction, ties included.',
           'up-to-five rule': 'Every simple cycle of at most five. Every allowed change of at most five splits into such cycles.',
           'independent reconstructions': ['ring starts', 'ordinary groups and fresh count', 'class facts',
                 'direct single-knot reads', 'projected joint values', 'law-deletion counts', 'start and attachment representatives'],
           'processes': 1, 'address limit in bytes': LIMIT, 'maximum resident KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           'totals': totals(cases), 'families': cases}
    if args.pilot:
        print(json.dumps(out['totals'], indent=2))
    else:
        (HERE / 'ring_counts.json').write_text(json.dumps(out, indent=1) + '\n')
        print(json.dumps({k:v for k,v in out['totals'].items() if not isinstance(v,dict)}))


if __name__ == '__main__':
    main()
