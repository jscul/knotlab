"""Recognize a nested reading after independently swapping whole branches of each stage."""

from itertools import groupby
from operator import itemgetter


def _layout(middles, pads):
    if len(middles) % 2 or len(pads) != 2 * len(middles):
        raise ValueError("each stage requires two middle names and four pad names")
    positions = len(middles) + len(pads)
    first = [-1] * (2 * positions)
    second = [-1] * (2 * positions)
    word = []
    for branch, middle in enumerate(middles):
        for name, role in ((middle, 0), (pads[2 * branch], 1), (pads[2 * branch + 1], 1)):
            if type(name) is not int or not 0 <= name < positions:
                raise ValueError("use indexed integer names from 0 through the word length minus one")
            typed = 2 * name + role
            if first[typed] < 0:
                first[typed] = len(word)
            elif second[typed] < 0:
                second[typed] = len(word)
            else:
                raise ValueError("a name can occur at most twice in the same role")
            word.append(typed)
    return word, first, second


def _stable_pass(records, column, alphabet):
    """Counting sort on one dense name, preserving the other keys' current order."""
    offsets = [0] * alphabet
    for record in records:
        offsets[record[column]] += 1
    start = 0
    for name, count in enumerate(offsets):
        offsets[name] = start
        start += count
    ordered = [None] * len(records)
    for record in records:
        key = record[column]
        ordered[offsets[key]] = record
        offsets[key] += 1
    return ordered


def _swap_constraints(word, first, second):
    stages = len(word) // 6
    records = []
    for stage in range(stages):
        offset = 6 * stage
        for x in word[offset:offset + 3]:
            if second[x] < 0:
                continue
            for y in word[offset + 3:offset + 6]:
                if x != y and second[y] >= 0:
                    records.append((min(x, y), max(x, y), stage))
    # Stage is already the least significant key. Two stable passes retain that order.
    records = _stable_pass(records, 1, len(first))
    records = _stable_pass(records, 0, len(first))
    graph = [[] for _ in range(stages + 1)]
    for (x, y), occurrences in groupby(records, key=itemgetter(0, 1)):
        active = []
        for stage, same_stage in groupby(occurrences, key=itemgetter(2)):
            if sum(1 for _ in same_stage) % 2:
                active.append(stage)
        if active:
            # Both names appear in each contributing stage, so there are at most two.
            left = active[0]
            right = active[1] if len(active) == 2 else stages
            alternating = (first[x] < first[y] < second[x] < second[y] or
                           first[y] < first[x] < second[y] < second[x])
            graph[left].append((right, int(alternating)))
            graph[right].append((left, int(alternating)))
    return graph


def _satisfying_bits(graph):
    # The final node is a zero constant. Seeding it first enforces every unary pin.
    constant = len(graph) - 1
    bits = [-1] * len(graph)
    for start in range(constant, -1, -1):
        if bits[start] >= 0:
            continue
        bits[start] = 0
        pending = [start]
        while pending:
            stage = pending.pop()
            for neighbor, parity in graph[stage]:
                expected = bits[stage] ^ parity
                if bits[neighbor] < 0:
                    bits[neighbor] = expected
                    pending.append(neighbor)
                elif bits[neighbor] != expected:
                    return None
    return tuple(bits[:constant])


def _nested(word, second, bits):
    seen = bytearray(len(second))
    stack = []
    for stage, flip in enumerate(bits):
        base = 6 * stage
        for branch in (flip, 1 - flip):
            start = base + 3 * branch
            for name in word[start:start + 3]:
                if second[name] < 0:
                    continue
                if not seen[name]:
                    seen[name] = 1
                    stack.append(name)
                elif stack.pop() != name:
                    return False
    return True


def zero_order(middles, pads) -> tuple[int, ...] | None:
    """Return 0/1 branch-swap bits giving nested pairs, or None if no order works.

    The input has two middle IDs and four pad IDs per stage. Pad IDs are in
    upper-in, upper-out, lower-in, lower-out order. IDs in each separate role
    lie in range(6*r) and occur at most twice. A 1 reads the lower branch first.
    Malformed layouts raise ValueError. Both time and space are O(r+1) indexed.
    """
    word, first, second = _layout(middles, pads)
    bits = _satisfying_bits(_swap_constraints(word, first, second))
    if bits is None or not _nested(word, second, bits):
        return None
    return bits

