"""Exact search over disjoint reader sets. Knot order is the supplied list order.

A partial partition fixes the sets of distinctions for some readers and leaves
others unassigned. A word may use only pairs within a fixed reader or among
unassigned distinctions. Binary elimination decides whether this relaxation can
commute and close odd. For an unassigned distinction, exhaust leaving it unused
or grouping it with every eligible set of other unassigned distinctions. Each
group has pairwise disjoint holders. At most half the distinctions can be active
readers because every reader contains a failing pair. The search uses this
structural bound, subsequently lowering it to prove the minimum.
"""

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def reduce_by(vector, representative, basis):
    """Return the coset representative and update the pair word in parallel."""
    residual = 0
    while vector:
        top = vector.bit_length() - 1
        pivot = basis.get(top)
        if pivot is None:
            bit = 1 << top
            residual |= bit
            vector ^= bit
        else:
            vector ^= pivot[0]
            representative ^= pivot[1]
    return residual, representative


def add_to(basis, vector, representative):
    while vector:
        top = vector.bit_length() - 1
        pivot = basis.get(top)
        if pivot is None:
            basis[top] = vector, representative
            return
        vector ^= pivot[0]
        representative ^= pivot[1]


class ReaderSearch:
    def __init__(self, supports, pairs, required=()):
        self.supports = tuple(tuple(s) for s in supports)
        self.labels = sorted({d for s in supports for d in s})
        self.pairs = tuple(tuple(sorted(pair)) for pair in pairs)
        if len(set(self.pairs)) != len(self.pairs):
            raise ValueError("duplicate pairs")
        label_index = {d: i for i, d in enumerate(self.labels)}
        holders = [tuple(k for k, s in enumerate(supports) if d in s) for d in self.labels]
        if any(len(h) != 2 for h in holders):
            raise ValueError("each distinction must have two different holders")
        self.holders = [sum(1 << k for k in h) for h in holders]
        self.endpoints = [(label_index[a], label_index[b]) for a, b in self.pairs]
        self.incident = [0] * len(self.labels)
        self.columns = []
        self.checks = [0] * (len(supports) * (len(supports) - 1) // 2)
        check_index = {p: i for i, p in enumerate(combinations(range(len(supports)), 2))}
        self.cost = 0
        for i, (a, b) in enumerate(self.endpoints):
            if self.holders[a] & self.holders[b]:
                raise ValueError("a decidable failure cannot have a common holder")
            p, q = holders[a]
            u, v = holders[b]
            alternating = (p < u < q) != (p < v < q)
            self.cost |= alternating << i
            column = int(alternating)
            for left, right in product((p, q), (u, v)):
                j = check_index[tuple(sorted((left, right)))]
                self.checks[j] |= 1 << i
                column |= 1 << (1 + j)
            self.columns.append(column)
            self.incident[a] |= 1 << i
            self.incident[b] |= 1 << i
        pair_index = {pair: i for i, pair in enumerate(self.pairs)}
        self.required = sum(1 << pair_index[p] for p in {tuple(sorted(p)) for p in required})
        self.target = 1
        for i in bits(self.required):
            self.target ^= self.columns[i]
        self.all_distinctions = (1 << len(self.labels)) - 1
        self.groups = [[] for _ in self.labels]
        self.group_pairs = {}

        def grow(start, group, used_holders, inside):
            if inside and all(self.incident[d] & inside for d in bits(group)):
                self.group_pairs[group] = inside
                for d in bits(group):
                    self.groups[d].append((group, inside))
            for d in range(start, len(self.labels)):
                if not self.holders[d] & used_holders:
                    extra = 0
                    for member in bits(group):
                        extra |= self.incident[d] & self.incident[member]
                    grow(d + 1, group | 1 << d, used_holders | self.holders[d], inside | extra)

        grow(0, 0, 0, 0)
        for groups in self.groups:
            groups.sort(key=lambda item: (item[0].bit_count(), item[0]))
        self.pair_groups = [[g for g in choices if g[0].bit_count() == 2] for choices in self.groups]
        self.nodes = 0

        @lru_cache(maxsize=8192)
        def free_data(free):
            allowed = 0
            basis = {}
            for i, (a, b) in enumerate(self.endpoints):
                bit = 1 << i
                if free & (1 << a) and free & (1 << b):
                    allowed |= bit
                    if not self.required & bit:
                        add_to(basis, self.columns[i], bit)
            return allowed, basis

        self.free_data = free_data

    def complete(self, free, inside):
        """Find any odd word, respecting required pairs and the partial partition."""
        allowed, base = self.free_data(free)
        if self.required & ~(allowed | inside):
            return None
        target, word = reduce_by(self.target, self.required, base)
        if not target:
            return word
        extra = {}
        for i in bits(inside & ~self.required):
            residue, term = reduce_by(self.columns[i], 1 << i, base)
            add_to(extra, residue, term)
        target, word = reduce_by(target, word, extra)
        return None if target else word

    def pack(self, word, strict, limit):
        """Partition forced groups, combining compatible groups to meet the bound."""
        components = []
        members = 0
        for i in bits(word):
            a, b = self.endpoints[i]
            joint = (1 << a) | (1 << b)
            if strict and members & joint:
                return None
            members |= joint
            merged = joint
            separate = []
            for comp in components:
                if joint & comp:
                    merged |= comp
                else:
                    separate.append(comp)
            components = [*separate, merged]
        if strict:
            return components if len(components) <= limit else None
        holdings = []
        for comp in components:
            mask = 0
            for d in bits(comp):
                if mask & self.holders[d]:
                    return None
                mask |= self.holders[d]
            holdings.append((mask, comp))
        if len(components) <= limit:
            return components
        holdings.sort(key=lambda x: -x[0].bit_count())
        bins = []

        def assign(i):
            if i == len(holdings):
                return [group for _, group in bins]
            hold, group = holdings[i]
            tested = set()
            for j, (existing, group_so_far) in enumerate(bins):
                if not existing & hold and existing not in tested:
                    tested.add(existing)
                    bins[j] = existing | hold, group_so_far | group
                    found = assign(i + 1)
                    if found is not None:
                        return found
                    bins[j] = existing, group_so_far
            if len(bins) < limit:
                bins.append((hold, group))
                found = assign(i + 1)
                bins.pop()
                return found
            return None

        return assign(0)

    def search(self, strict, limit):
        groups = self.pair_groups if strict else self.groups

        def visit(free, inside, assigned):
            self.nodes += 1
            word = self.complete(free, inside)
            if word is None:
                return None
            packed = self.pack(word, strict, limit)
            if packed is not None:
                return word, packed
            if assigned == limit:
                final = self.complete(0, inside)
                return None if final is None else (final, self.pack(final, strict, limit))
            active = []
            for d in bits(free):
                if self.incident[d] & word:
                    active.append(d)
            if not active:
                raise AssertionError("a word supported entirely on the fixed readers must fit")
            pivot = min(active, key=lambda d: len(groups[d]))
            # All actual readers are included: inactive distinctions have been
            # removed, so every member must touch an eligible internal pair.
            options = [(g, p) for g, p in groups[pivot] if g & free == g]
            options.sort(key=lambda item: -(item[1] & word).bit_count())
            for group, within in options:
                answer = visit(free ^ group, inside | within, assigned + 1)
                if answer is not None:
                    return answer
            return visit(free ^ (1 << pivot), inside, assigned)

        return visit(self.all_distinctions, 0, 0)

    def minimum(self, strict, upper=None):
        best = upper
        limit = len(self.labels) // 2 if upper is None else len(upper[1]) - 1
        while limit > 0:
            found = self.search(strict, limit)
            if found is None:
                break
            if found[1] is None:
                raise AssertionError("word on selected readers did not fit")
            best = found
            limit = len(found[1]) - 1
        return best

    def render(self, result):
        if result is None:
            return None
        word, reader_masks = result
        groups = sorted(sorted(self.labels[d] for d in bits(group)) for group in reader_masks)
        return {"readers": groups, "failing_pairs": sorted([*self.pairs[i]] for i in bits(word))}


def solve(supports, pairs, *, required=(), all_choices=False):
    search = ReaderSearch(supports, pairs, required)
    try:
        strict = search.minimum(True)
        general = search.minimum(False, strict)
        answer = {
            "strict_min": None if strict is None else len(strict[1]),
            "general_min": None if general is None else len(general[1]),
            "strict_witness": search.render(strict),
            "general_witness": search.render(general),
        }
        if all_choices:
            answer["choices"] = split_choices(search)
        return answer
    finally:
        search.free_data.cache_clear()


def any_split(supports, pairs, *, required=(), strict=False):
    """Return a witness or None, optionally requiring particular pairs to fail."""
    search = ReaderSearch(supports, pairs, required)
    try:
        result = search.search(strict, len(search.labels) // 2)
        return search.render(result)
    finally:
        search.free_data.cache_clear()


def split_choices(search):
    """Enumerate only split-compatible supports of failures, on small fixtures.

    Traverse the allowed reader sets in increasing order of their first active
    distinction. Internal pairs vary independently in each set. Completed words
    are deduplicated because compatible disconnected groups can share a reader.
    """
    accepted = {}
    patterns = {}
    for group, internal in search.group_pairs.items():
        entries = []
        sub = internal
        while sub:
            if all(search.incident[d] & sub for d in bits(group)):
                sign_checks = 0
                for i in bits(sub):
                    sign_checks ^= search.columns[i]
                entries.append((sub, sign_checks))
            sub = (sub - 1) & internal
        patterns[group] = entries

    def visit(free, word, need, readers):
        if not need and search.required & word == search.required:
            previous = accepted.get(word)
            if previous is None or len(readers) < len(previous):
                accepted[word] = readers
        if not free:
            return
        _, base = search.free_data(free)
        if not search.required and reduce_by(need, 0, base)[0]:
            return
        bit = free & -free
        pivot = bit.bit_length() - 1
        visit(free ^ bit, word, need, readers)
        for group, internal in search.groups[pivot]:
            if group & free != group:
                continue
            for sub, syndrome in patterns[group]:
                visit(free ^ group, word | sub, need ^ syndrome, (*readers, group))

    visit(search.all_distinctions, 0, 1, ())
    strict_counts = defaultdict(int)
    component_sizes = set()
    reader_sizes = set()
    for word, readers in accepted.items():
        strict = search.pack(word, True, len(search.labels) // 2)
        if strict is not None:
            strict_counts[len(strict)] += 1
        components = search.pack(word, False, len(search.labels))
        component_sizes.add(tuple(sorted(group.bit_count() for group in components)))
        reader_sizes.add(tuple(sorted(group.bit_count() for group in readers)))
    return {
        "strict_odd_choices": sum(strict_counts.values()),
        "strict_sizes": sorted(strict_counts),
        "odd_choices_with_a_split": len(accepted),
        "word_counts_by_minimum_readers": dict(sorted(Counter(map(len, accepted.values())).items())),
        "failing_group_sizes": sorted(map(list, component_sizes)),
        "one_minimum_layout_per_word_sizes": sorted(map(list, reader_sizes)),
    }
