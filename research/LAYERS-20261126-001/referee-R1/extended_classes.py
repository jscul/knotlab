"""Rank frozen shortest changes and their class readings without a tie cap."""

from collections import defaultdict, deque


class BinarySpan:
    def __init__(self, words=()):
        self.rows = {}
        for word in words:
            self.add(word)

    def __len__(self):
        return len(self.rows)

    def reduce(self, word):
        while word:
            row = self.rows.get(word.bit_length() - 1)
            if row is None:
                break
            word ^= row
        return word

    def add(self, word):
        word = self.reduce(word)
        if word:
            self.rows[word.bit_length() - 1] = word
        return bool(word)

    def kernel(self, coordinates):
        pivots = sorted(self.rows.items())
        for i in coordinates:
            if i in self.rows:
                continue
            word = 1 << i
            for pivot, equation in pivots:
                if (equation & word).bit_count() % 2:
                    word |= 1 << pivot
            yield word


def bit_sum(indices):
    return sum(1 << i for i in indices)


def incidence(rows):
    owners = defaultdict(list)
    for knot, row in enumerate(rows):
        assert len(row) == len(set(row))
        for distinction in row:
            owners[distinction].append(knot)
    assert all(len(values) in (1, 2) for values in owners.values())
    return owners


def shortest_change_span(places, count, allowed_rank):
    # Give every loose distinction one additional holder for this calculation.
    # Its parity is implied. In the resulting incidence graph, an even change
    # is a sum of cycles. The shortest change through a named distinction is
    # that distinction plus a shortest return between its holders without it.
    pairs = [(values[0], values[1] if len(values) == 2 else count) for values in places]
    adjacency = [[] for _ in range(count + 1)]
    words = [1 << i for i in range(len(pairs))]
    for (left, right), word in zip(pairs, words, strict=True):
        adjacency[left].append((right, word))
        adjacency[right].append((left, word))
    moves = BinarySpan()
    for (start, finish), omitted in zip(pairs, words, strict=True):
        if len(moves) == allowed_rank:
            break
        levels = {start: 0}
        prefix = {start: 0}
        todo = deque([start])
        while todo and finish not in levels:
            here = todo.popleft()
            for there, used in adjacency[here]:
                if used != omitted and there not in levels:
                    levels[there] = levels[here] + 1
                    prefix[there] = prefix[here] ^ used
                    todo.append(there)
        if finish not in levels:
            continue
        moves.add(prefix[finish] ^ omitted)

        # Trace only transitions on a shortest return. Replacing the prefix
        # of a return at one transition gives the difference below between two
        # allowed shortest changes. Along any return these differences sum to
        # its difference from the chosen return. They span all ties exactly.
        seen = {finish}
        todo = deque([finish])
        while todo:
            here = todo.popleft()
            for there, used in adjacency[here]:
                if used == omitted or levels.get(there, -2) != levels[here] - 1:
                    continue
                moves.add(prefix[here] ^ used ^ prefix[there])
                if there not in seen:
                    seen.add(there)
                    todo.append(there)
    return moves


def inspect(rows, old_rows=None, old_shared=()):
    owners = incidence(rows)
    names = sorted(owners)
    coordinate = {name: i for i, name in enumerate(names)}
    knots = [[coordinate[name] for name in row] for row in rows]
    checks = [bit_sum(row) for row in knots]
    laws = BinarySpan(checks)
    allowed_rank = len(names) - len(laws)
    moves = shortest_change_span([owners[name] for name in names], len(rows), allowed_rank)
    label_rank = allowed_rank - len(moves)
    result = {
        "knots": len(rows),
        "distinctions": len(names),
        "allowed rank": allowed_rank,
        "move rank": len(moves),
        "label rank": label_rank,
        "listed reader rank": 0,
        "knot reader rank": 0,
    }
    if old_rows is not None:
        old = incidence(old_rows)
        assert tuple(rows[:len(old_rows)]) == tuple(old_rows)
        fresh_mask = bit_sum(coordinate[name] for name in owners.keys() - old.keys())
        fresh_rank = len(BinarySpan(check & fresh_mask for check in checks))
        result["old projection kept"] = len(laws) - fresh_rank == len(BinarySpan(checks[:len(old_rows)]))
    if old_shared:
        shared = bit_sum(coordinate[name] for name in old_shared)
        result["old shared parity is a label"] = bool(laws.reduce(shared)) and all(
            not ((shared & move).bit_count() % 2) for move in moves.rows.values()
        )
    if label_rank == 0:
        return result

    allowed = tuple(laws.kernel(range(len(names))))
    listed_readers = BinarySpan(checks)
    knot_readers = BinarySpan(checks)
    for row, support in zip(knots, checks, strict=True):
        local_moves = BinarySpan(move & support for move in moves.rows.values())
        projection_rank = len(BinarySpan(word & support for word in allowed))
        assert len(local_moves) <= projection_rank < len(row)
        if projection_rank == len(local_moves):
            continue
        is_knot = len(row) >= 3 and projection_rank == len(row) - 1
        for word in local_moves.kernel(row):
            listed_readers.add(word)
            if is_knot:
                knot_readers.add(word)
    result['listed reader rank'] = len(listed_readers) - len(laws)
    result['knot reader rank'] = len(knot_readers) - len(laws)
    assert 0 <= result['knot reader rank'] <= result['listed reader rank'] <= label_rank
    if label_rank - result['listed reader rank'] >= 2:
        # Retain independent representative parities outside the span of the
        # listed readings. In each extension of that span, independence is
        # modulo both the listed readings and all law equations.
        result['parities independent of listed readings'] = [
            [name for i, name in enumerate(names) if word & (1 << i)]
            for word in moves.kernel(range(len(names))) if listed_readers.add(word)
        ]
        assert len(listed_readers) - len(laws) == label_rank
    return result
