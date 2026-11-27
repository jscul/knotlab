"""Direct finite replay for a second layer under the even-parity law."""

import argparse
from itertools import combinations
import json


def agrees(state, carrier):
    values = {state >> p & 1 for p in carrier}
    return int(len(values) == 1)


def restrict_to(state, places):
    return sum((state >> p & 1) << i for i, p in enumerate(places))


def determined(states, carrier, places):
    seen = {}
    for state in states:
        key = restrict_to(state, places)
        reading = agrees(state, carrier)
        if key in seen and seen[key] != reading:
            return False
        seen[key] = reading
    return True


def image(states, carriers):
    return {tuple(agrees(s, c) for c in carriers) for s in states}


def knot_image(words, n):
    return 0 < len(words) < 2 ** n and all(
        len({w[:i] + w[i + 1:] for w in words}) == 2 ** (n - 1)
        for i in range(n)
    )


def try_cluster(supports, bound):
    size = 1 + max(max(row) for row in supports)
    masks = [sum(1 << i for i in row) for row in supports]
    all_states = list(range(2 ** size))
    violations = [{i for i, m in enumerate(masks) if (s & m).bit_count() % 2 != 1}
                  for s in all_states]
    states = [s for s, bad in zip(all_states, violations) if not bad]
    extra = [[s for s, bad in zip(all_states, violations) if bad == {i}]
             for i in range(len(supports))]
    carriers = [c for n in (2, 3) for c in combinations(range(size), n)
                if all(not determined(states, c, row) for row in supports)]
    tested = 0
    for triplet in combinations(carriers, 3):
        if sum(map(len, triplet)) != len(set().union(*triplet)):
            continue
        tested += 1
        words = image(states, triplet)
        if knot_image(words, 3) and all(image(after, triplet) - words for after in extra):
            return {'supports':supports,'upper':triplet,'image':sorted(words),
                    'tested':tested}
        if bound and tested >= bound:
            break
    return {'supports':supports,'tested':tested,'upper':None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    patterns = [
        [(0, 1, 2), (2, 3, 4), (4, 5, 6)],
        [(0, 1, 2), (2, 3, 4), (2, 5, 6)],
        [(0, 1, 2), (2, 3, 4), (0, 4, 5)],
        [(0, 1, 2), (1, 2, 3), (3, 4, 5)],
        [(0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8)],
    ]
    print(json.dumps([try_cluster(rows, 1 if args.pilot else None)
                      for rows in patterns], indent=2))
