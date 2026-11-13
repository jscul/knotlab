"""Independent address-pattern reconstruction, written from the frozen spec.

This module deliberately has no study-code imports. Integer addresses are MSB first.
"""
from __future__ import annotations

import hashlib
import itertools
import struct


def words(s):
    return [()] + [(q,) for q in range(s)] + list(itertools.product(range(s), repeat=2))


def state_actions(key, level):
    """Induct on the first letter, storing the entire suffix action at each step."""
    s, swaps, d0, d1, _ = key
    previous = [[0] for _ in range(s)]
    for depth in range(1, level + 1):
        half = 1 << (depth - 1)
        current = []
        for q in range(s):
            row = []
            for b, successor in ((0, d0[q]), (1, d1[q])):
                prefix = (b ^ swaps[q]) * half
                row.extend(prefix + y for y in previous[successor])
            current.append(row)
        previous = current
    return previous


def direct_state(key, q, x, level):
    """Separate, letter-by-letter action for controls; no array recurrence."""
    _, swaps, d0, d1, _ = key
    result = 0
    for shift in range(level - 1, -1, -1):
        bit = (x >> shift) & 1
        result = (result << 1) | (bit ^ swaps[q])
        q = d1[q] if bit else d0[q]
    return result


def pattern(key, level):
    maps = state_actions(key, level)
    catalog = words(key[0])
    needed = {w for placement in key[4] for w in placement}
    images = {}
    for index in needed:
        word = catalog[index]
        result = list(range(1 << level))
        for q in reversed(word):
            result = [maps[q][x] for x in result]
        images[index] = result
    triples = set()
    for placement in key[4]:
        for image in zip(*(images[i] for i in placement)):
            if len(set(image)) == 3:
                triples.add(tuple(sorted(image)))
    return sorted(triples)


def pattern_bytes(level, triples):
    flat = [v for row in triples for v in row]
    return struct.pack('<qq', level, len(triples)) + struct.pack(f'<{len(flat)}q', *flat)


def fingerprint(patterns):
    digest = hashlib.sha1()
    for n, triples in enumerate(patterns, 1):
        digest.update(pattern_bytes(n, triples))
    return digest.hexdigest()


def cnf(triples):
    result = []
    for triple in triples:
        positive = [v + 1 for v in triple]
        result.append(positive)
        result.append([-v for v in positive])
    # No complement-symmetry unit is added: certificates prove the original CNF.
    return result


def verify_assignment(triples, values):
    return all(len({values[v] for v in triple}) == 2 for triple in triples)


def joining(triples, k=1):
    mask = (1 << k) - 1
    return sum(len({v & mask for v in triple}) > 1 for triple in triples)


def fate(verdicts, counts):
    relevant = [v for v, c in zip(verdicts, counts) if c]
    if not relevant:
        return 'F0'
    if relevant[0] == 0:
        return 'F1'
    if any(v == 1 and 0 in relevant[i + 1:] for i, v in enumerate(relevant)):
        return 'F2'
    if all(v == 1 for v in relevant):
        return 'F3'
    return 'FU'
