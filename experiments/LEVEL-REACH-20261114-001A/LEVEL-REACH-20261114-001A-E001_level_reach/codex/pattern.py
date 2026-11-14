"""Specified addressed terms and their finite union of NAE knots."""
from functools import lru_cache
import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ADDR_PATH = HERE / 'input_addr.py'
_spec = importlib.util.spec_from_file_location('level_reach_addr_input', ADDR_PATH)
addr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(addr)


def level_ids(n):
    return list(range((1 << n) - 1, (1 << (n + 1)) - 1))


def level(v):
    return (int(v) + 1).bit_length() - 1


def pattern(key, N):
    s, sw, d0, d1, placements = key
    W = addr.words(s)
    aut = tuple(tuple(row) for row in (sw, d0, d1))
    placements = sorted(set(tuple(sorted(t)) for t in placements))
    pieces = []
    for n in range(N + 1):
        images = {}
        for t in {t for triple in placements for t in triple}:
            wi, slot = divmod(t, 3)
            if slot and n == N:
                continue
            y = addr.action(aut, W[wi], n)
            images[t] = y + (1 << n) - 1 if not slot else 2 * y + slot - 1 + (1 << (n + 1)) - 1
        for triple in placements:
            if not all(t in images for t in triple):
                continue
            rows = np.sort(np.stack([images[t] for t in triple], axis=1), axis=1)
            keep = (rows[:, 0] != rows[:, 1]) & (rows[:, 1] != rows[:, 2])
            if np.any(keep):
                pieces.append(rows[keep])
    if not pieces:
        return np.empty((0, 3), dtype=np.int64)
    return np.unique(np.concatenate(pieces), axis=0)


def clauses(K):
    out = []
    for row in K:
        positive = [int(v) + 1 for v in row]
        out.extend((positive, [-x for x in positive]))
    return out


def flags(key):
    return {
        'no_join': all(len({int(t) % 3 == 0 for t in triple}) == 1 for triple in key[4]),
        'tree_only': all(tuple(sorted(t)) == (0, 1, 2) for t in key[4]),
        's1': int(key[0]) == 1,
    }


def classes(key):
    s, sw, d0, d1, placements = key
    aut = tuple(tuple(row) for row in (sw, d0, d1))
    W = addr.words(s)
    used = {t // 3 for p in placements for t in p}
    starts = tuple(sorted({q for wi in used for q in W[wi]}))
    letter = addr._letter_activity(aut, starts)
    relative = ('finitary', None)
    products = {addr.relative_product(W[ti // 3], W[tj // 3])
                for p in placements for ti in p for tj in p if ti != tj}
    for product in sorted(products):
        candidate = addr._relative_activity(aut, product)
        if addr._class_rank(candidate) > addr._class_rank(relative):
            relative = candidate
        if relative[0] == 'exponential':
            break
    return {'letter': {'class': letter[0], 'degree': letter[1]},
            'relative': {'class': relative[0], 'degree': relative[1]}}


def components(K, nvars):
    parent = list(range(nvars))

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for row in K:
        a, b, c = map(int, row)
        for v in (b, c):
            ra, rv = find(a), find(v)
            parent[rv] = ra
    return [find(v) for v in range(nvars)]
