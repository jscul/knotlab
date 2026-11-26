"""Rebuild one round from the edited supports and the two fresh-count cuts."""

from collections import Counter, defaultdict, deque
from itertools import combinations


def _groups(meetings):
    pairs = {
        (a, b) for a, b in combinations(sorted(meetings), 2)
        if meetings[a] & meetings[b]
    }

    # Every group omits one member of any incompatible pair. Repeatedly
    # branch on such a pair, then keep the maximal groups with no common meeting.
    seen = set()
    admissible = set()

    def split(members):
        if len(members) < 3 or members in seen:
            return
        seen.add(members)
        for a, b in combinations(sorted(members), 2):
            if (a, b) not in pairs:
                split(members - {a})
                split(members - {b})
                return
        first, *rest = sorted(members)
        if not meetings[first].intersection(*(meetings[h] for h in rest)):
            admissible.add(members)

    split(frozenset(h for pair in pairs for h in pair))
    bigger = sorted(tuple(sorted(g)) for g in admissible if not any(g < other for other in admissible))
    covered = {pair for group in bigger for pair in combinations(group, 2)}
    return bigger + sorted(pairs - covered)


def _mask(distinctions):
    return sum(1 << d for d in distinctions)


def _reduce(word, parity_rows):
    while word:
        pivot = word.bit_length() - 1
        if pivot not in parity_rows:
            break
        word ^= parity_rows[pivot]
    return word


def _nae_completion(rows, fixed_zero):
    def search(zero, one):
        # Pick the missing value in a knot with the fewest remaining choices.
        # Any completion must assign that value to at least one choice.
        best = None
        for row in rows:
            free = row & ~(zero | one)
            for value, present in enumerate((zero, one)):
                if row & present:
                    continue
                size = free.bit_count()
                if not size:
                    return False
                if best is None or size < best[0]:
                    best = size, free, value
        if best is None:
            return True
        _, choices, value = best
        while choices:
            bit = choices & -choices
            choices ^= bit
            if value == 0 and search(zero | bit, one):
                return True
            if value == 1 and search(zero, one | bit):
                return True
        return False

    return search(fixed_zero, 0)


def grow(edited, law, arm):
    """Return (status, births), using only edited supports to choose the births.

    Every birth carries sorted tuples of ``parents``, ``inputs`` and ``fresh``,
    and the number ``f`` of fresh distinctions. The ordinary allotment sets
    their IDs even when a cut keeps only its first few distinctions.
    """
    if law not in ("parity", "nae") or arm not in ("ordinary", "one_fewer", "arity_floor"):
        raise ValueError((law, arm))

    owners = defaultdict(list)
    for holder, support in enumerate(edited):
        for distinction in support:
            owners[distinction].append(holder)
    meetings = [set() for _ in edited]
    for holding in owners.values():
        if len(holding) == 2 and holding[0] != holding[1]:
            a, b = holding
            meetings[a].add(b)
            meetings[b].add(a)
        elif len(holding) != 1:
            raise ValueError("each distinction must occur once at one or two holders")

    loose = {
        holder: deque(d for d in support if len(owners[d]) == 1)
        for holder, support in enumerate(edited)
    }
    live_meetings = {h: meetings[h] for h, values in loose.items() if values}
    if not live_meetings:
        return "closed", []
    parents = _groups(live_meetings)
    need = Counter(h for group in parents for h in group)
    if any(need[h] > len(loose[h]) for h in need):
        return "stalled", []

    inputs = [tuple(sorted(loose[h].popleft() for h in group)) for group in parents]
    for holder, values in loose.items():
        parents.extend((holder,) for _ in values)
        inputs.extend((d,) for d in values)

    # Provisional births meet exactly their parents. All take part in the
    # lookahead, before any fresh distinction is granted or cut.
    lookahead = _groups({i: set(group) for i, group in enumerate(parents)})
    demand = Counter(i for group in lookahead for i in group)
    rows = tuple(_mask(support) for support in edited)
    parity_rows = {}
    if law == "parity":
        for row in rows:
            residual = _reduce(row, parity_rows)
            if residual:
                parity_rows[residual.bit_length() - 1] = residual

    births = []
    next_id = max(owners) + 1
    for i, (group, taken) in enumerate(zip(parents, inputs, strict=True)):
        floor = max(0, 3 - len(group))
        ordinary = max(demand[i], floor, 1)
        if demand[i] < ordinary:
            mask = _mask(taken)
            if law == "parity":
                implied = _reduce(mask, parity_rows) == 0
            else:
                # Complement exchanges an all-zero witness and an all-one witness.
                implied = not _nae_completion(rows, mask)
            if implied:
                ordinary = demand[i]

        fresh_count = ordinary
        if arm == "one_fewer":
            fresh_count = min(ordinary, max(floor, ordinary - 1))
        elif arm == "arity_floor":
            fresh_count = min(ordinary, floor)
        births.append({
            "parents": group,
            "inputs": taken,
            "fresh": tuple(range(next_id, next_id + fresh_count)),
            "f": fresh_count,
        })
        next_id += ordinary
    return "funded", births
