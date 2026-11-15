"""Minimize exceptions over all legal exchanges of the two branches at each stage."""

from typing import NamedTuple


class Arc(NamedTuple):
    start: int
    end: int
    physical: int
    swap: int


def _typed_word(middles, pads):
    if len(middles) % 2 or len(pads) != 2 * len(middles):
        raise ValueError("expected two middles and four pads per stage")
    size = len(middles) + len(pads)
    if any(not isinstance(name, int) or not 0 <= name < size
           for seq in (middles, pads) for name in seq):
        raise ValueError("names must be indexed between 0 and the word length minus one")
    word = []
    for j, middle in enumerate(middles):
        word.extend((2 * middle, 2 * pads[2*j] + 1, 2 * pads[2*j+1] + 1))
    return word


class Layout:
    def __init__(self, middles, pads):
        self.word = _typed_word(middles, pads)
        size = len(self.word)
        self.stages = size // 6
        self.mate = [-1] * size
        first = [-1] * (2 * size)
        for pos, name in enumerate(self.word):
            earlier = first[name]
            if earlier < 0:
                first[name] = pos
            elif self.mate[earlier] < 0:
                self.mate[pos] = earlier
                self.mate[earlier] = pos
            else:
                raise ValueError("a typed name occurs in more than two physical positions")

        self.outgoing = [[] for _ in range(11 * self.stages + 1)]
        self.copies = [[] for _ in self.word]
        for i in range(self.stages):
            entry = 11 * i
            for swap in (0, 1):
                first_inner = entry + 1 + 5 * swap
                vertices = [entry, *range(first_inner, first_inner + 5), entry + 11]
                for step in range(6):
                    physical = 6 * i + (step + 3 * swap) % 6
                    arc = Arc(vertices[step], vertices[step + 1], physical, swap)
                    self.outgoing[arc.start].append(arc)
                    self.copies[physical].append(arc)


def _interval_tables(layout):
    """Scores are -1 for an unreachable pair of vertices and 0 on an empty path."""
    size = len(layout.outgoing)
    score = [[-1] * size for _ in range(size)]
    choice = [bytearray(size) for _ in range(size)]
    for u in range(size - 1, -1, -1):
        row, picks = score[u], choice[u]
        row[u] = 0
        for outgoing_index, first_arc in enumerate(layout.outgoing[u]):
            # Each outgoing arc supplies one skip and at most two ways to match.
            skip_code = 1 + 3 * outgoing_index
            following = score[first_arc.end]
            for v in range(first_arc.end, size):
                if following[v] > row[v]:
                    row[v] = following[v]
                    picks[v] = skip_code

            mate = layout.mate[first_arc.physical]
            if mate < 0:
                continue
            for copy_index, closing_arc in enumerate(layout.copies[mate]):
                inside = following[closing_arc.start]
                if inside < 0:
                    continue
                after = score[closing_arc.end]
                for v in range(closing_arc.end, size):
                    if after[v] >= 0 and inside + 1 + after[v] > row[v]:
                        row[v] = inside + 1 + after[v]
                        picks[v] = skip_code + 1 + copy_index
    return score, choice


def optimal_order(middles, pads):
    """Return (swaps, removed) as tuples. 1 exchanges two intact branch triples.

    Removed names are sorted. Middle name j has ID 2*j, and pad name j has
    ID 2*j+1. The input uses the predecessor's indexed names and two-use cap.
    """
    layout = Layout(middles, pads)
    score, choice = _interval_tables(layout)
    swaps = [-1] * layout.stages
    seen = bytearray(len(layout.word))
    kept = bytearray(2 * len(layout.word))

    def take_arc(arc):
        stage = arc.physical // 6
        if seen[arc.physical] or swaps[stage] not in (-1, arc.swap):
            raise AssertionError("traceback mixed incompatible branches or repeated an occurrence")
        seen[arc.physical] = 1
        swaps[stage] = arc.swap

    jobs = [(0, len(layout.outgoing) - 1)]
    while jobs:
        u, v = jobs.pop()
        if u == v:
            continue
        code = choice[u][v]
        if not code:
            raise AssertionError("traceback reached an infeasible interval")
        outgoing_index, how = divmod(code - 1, 3)
        first_arc = layout.outgoing[u][outgoing_index]
        take_arc(first_arc)
        if how == 0:
            jobs.append((first_arc.end, v))
        else:
            mate = layout.mate[first_arc.physical]
            closing_arc = layout.copies[mate][how - 1]
            take_arc(closing_arc)
            name = layout.word[first_arc.physical]
            if kept[name]:
                raise AssertionError("traceback scored the same pair twice")
            kept[name] = 1
            jobs.extend(((closing_arc.end, v), (first_arc.end, closing_arc.start)))
    if not all(seen) or sum(kept) != score[0][-1]:
        raise AssertionError("traceback does not realize the optimal full path")
    paired = bytearray(len(kept))
    for pos, mate in enumerate(layout.mate):
        if mate > pos:
            paired[layout.word[pos]] = 1
    removed = tuple(name for name in range(len(paired)) if paired[name] and not kept[name])
    return tuple(swaps), removed
