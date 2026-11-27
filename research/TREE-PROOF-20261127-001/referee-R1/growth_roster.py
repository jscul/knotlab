"""Reconstruct the frozen roster from its raw census and declared weightings."""

import json
from itertools import combinations, count, pairwise, product
from pathlib import Path
from random import Random


RESEARCH = Path(__file__).resolve().parents[2]
ARCHIVE = RESEARCH / "SELECTED-KNOTS-20261127-001"
SETS = ("census", "heldout", "sampled", "built")


def _describe_start(size, shared, loose):
    rows = [[] for _ in range(size)]
    names = count()
    for a, b, multiplicity in shared:
        for _ in range(multiplicity):
            name = next(names)
            rows[a].append(name)
            rows[b].append(name)
    for row, amount in zip(rows, loose, strict=True):
        row.extend(next(names) for _ in range(amount))
    return tuple(map(tuple, rows))


def _labelled_sample(size, amount, seed, cap):
    rng = Random(seed)
    all_pairs = tuple(combinations(range(size), 2))
    accepted = 0
    while accepted < amount:
        selected = [pair for pair in all_pairs if rng.random() < 1 / 3]
        shared = [(a, b, rng.choice((1, 2))) for a, b in selected]
        loose = [rng.choice((0, 1, 2)) for _ in range(size)]
        if sum(loose) + sum(multiplicity for _, _, multiplicity in shared) > cap:
            continue
        candidate = _describe_start(size, shared, loose)
        if min(map(len, candidate)) < 3:
            continue

        reached = {0}
        while True:
            extended = set(reached)
            for a, b in selected:
                if a in reached or b in reached:
                    extended.update((a, b))
            if reached == extended:
                break
            reached = extended
        if len(reached) == size:
            yield candidate
            accepted += 1


def ring_start(number, size, attachment, link):
    """Form the declared rings with their connecting knots and two loose names per ring knot."""
    rows = [[] for _ in range(number * size)]
    names = count()

    def share(*knots):
        name = next(names)
        for knot in knots:
            rows[knot].append(name)

    rings = [list(range(i * size, (i + 1) * size)) for i in range(number)]
    for ring in rings:
        for a, b in pairwise(ring + ring[:1]):
            share(a, b)
    for ring in rings:
        for knot in ring:
            share(knot)
            share(knot)

    attachments = [0] * number
    for a, b in combinations(range(number), 2):
        left = len(rows)
        right = left + 1
        rows.extend(([], []))
        for ring, connector in ((a, left), (b, right)):
            place = attachments[ring]
            attachments[ring] += 1
            places = (2 * place, 2 * place) if attachment == "paired" else (place, place + 2)
            for place in places:
                share(rings[ring][place % size], connector)
        share(left, right)
        if link == "double":
            share(left, right)
        else:
            via = list(range(len(rows), len(rows) + 3))
            rows.extend([] for _ in via)
            for source, target in pairwise([left, *via, right]):
                share(source, target)
                share(source, target)
    return tuple(map(tuple, rows))


def _fourteen_knot_start():
    rows = [[] for _ in range(14)]
    names = count()

    def share(*knots):
        name = next(names)
        for knot in knots:
            rows[knot].append(name)

    for i in range(0, 12, 4):
        for a, b in pairwise((i, i + 1, i + 2, i + 3, i)):
            share(a, b)
        for knot in (i + 1, i + 3):
            share(knot)
            share(knot)
        share(i, 12)
        share(i + 2, 13)
    share(12, 13)
    return tuple(map(tuple, rows))


def load_starts(which):
    """Yield start names and numbered supports in the frozen order."""
    if which == "census":
        raw = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
        population = json.loads(raw.read_text())
        for index in Random(20261215).sample(range(len(population)), 1000):
            yield f"census {index}", _describe_start(*population[index])
    elif which == "heldout":
        for size in range(6, 9):
            for index, rows in enumerate(_labelled_sample(size, 300, 20261206 + size, 18)):
                yield f"held out {size}-{index}", rows
    elif which == "sampled":
        for size in range(9, 13):
            for index, rows in enumerate(_labelled_sample(size, 100, 20261212 + size, 30)):
                yield f"sampled {size}-{index}", rows
    elif which == "built":
        for number, size, attach, link in product(
            (3, 4), range(4, 8), ("split", "paired"), ("double", "detour")
        ):
            yield f"{number} rings of {size}, {attach}, {link}", ring_start(number, size, attach, link)
        yield "the 14-knot start", _fourteen_knot_start()
    else:
        raise ValueError(f"Unknown frozen roster {which!r}")
