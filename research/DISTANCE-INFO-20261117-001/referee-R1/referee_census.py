"""Referee R1 for DISTANCE-INFO-20261117-001 (own code; nothing imported from the study).

  .venv/bin/python -B referee_census.py > referee_census.json

1. Knot sets against relations: at n = 4, 5, 6 every set of not-all-equal knots (2^C(n,3) of them) is mapped to its allowed
   states; the satisfiable sets and the distinct relations are counted, and two distinct satisfiable sets with one relation are
   exhibited if they exist.
2. Readings of every distinct relation, by bit masks over the 2^n states (a projection onto B misses pattern p exactly when the
   relation shares no state with the states showing p on B). A bond is a set B on which the projection is a knot: not every
   joint state occurs, and forgetting any one member leaves the rest free. Two bond definitions:
     bonds >= 2: the study's (a two-place tie is a bond, distance 1);
     bonds >= 3: the glossary's ("a chain of two-place ties has no knot, and so no bond distance"; the canonical knot has two
                 loops and a contact).
   Readings: (a) unsigned pairwise bond distance; (b) ties signed; (c) the bond set; (c-s) with tie signs; (c') every bond with
   its missing joint states. Two other readings of "how far two distinctions are", from the allowed states:
     (e) for every pair, the number of allowed states in which the two differ;
     (e+) the same with the number of allowed states (the full pair counts, since the relations are closed under flipping).
3. n = 7: the referee's own sample of random knot sets (1 to 12 knots), readings (a) and (c').
"""
from __future__ import annotations

import itertools
import json

import numpy as np


def knots(n):
    return list(itertools.combinations(range(n), 3))


def state_bits(n):
    s = np.arange(1 << n)
    return [(s >> i) & 1 for i in range(n)]


def to_words(boolvec):
    """A boolean vector over the 2^n states as uint64 words."""
    b = np.asarray(boolvec, bool)
    W = (len(b) + 63) // 64
    out = np.zeros(W, np.uint64)
    for i in np.nonzero(b)[0]:
        out[i // 64] |= np.uint64(1) << np.uint64(i % 64)
    return out


def knot_words(n):
    bits = state_bits(n)
    return [to_words(~((bits[a] == bits[b]) & (bits[b] == bits[c]))) for a, b, c in knots(n)]


def all_relations(n):
    """Relations (as uint64 word rows) of every knot set, by a subset recursion; returns the rows and the knot-set ids."""
    kw = np.array(knot_words(n))                     # m x W
    m, W = kw.shape
    full = np.array([np.iinfo(np.uint64).max] * W, np.uint64)
    if (1 << n) % 64:
        full[-1] = (np.uint64(1) << np.uint64((1 << n) % 64)) - np.uint64(1)
    rel = np.zeros((1 << m, W), np.uint64)
    rel[0] = full
    for j in range(m):
        lo, hi = 1 << j, 1 << (j + 1)
        rel[lo:hi] = rel[0:lo] & kw[j]
    return rel


def readings(n, rel):
    """rel: R x W uint64 rows. Returns a dict of reading name -> R x k array (rows compared for equality)."""
    R, W = rel.shape
    bits = state_bits(n)
    subsets = [B for k in range(2, n + 1) for B in itertools.combinations(range(n), k)]
    sub_all = [B for k in range(1, n + 1) for B in itertools.combinations(range(n), k)]
    pres = {}
    full_rel = np.array([np.iinfo(np.uint64).max] * W, np.uint64)
    if (1 << n) % 64:
        full_rel[-1] = (np.uint64(1) << np.uint64((1 << n) % 64)) - np.uint64(1)
    big = {}  # the one set with more than 64 joint states (all 7 distinctions): its presence is the relation itself
    for B in sub_all:
        k = len(B)
        if (1 << k) > 64:
            big[B] = rel
            continue
        pr = np.zeros(R, np.uint64)
        for p in range(1 << k):
            sel = np.ones(1 << n, bool)
            for t, v in enumerate(B):
                sel &= bits[v] == ((p >> t) & 1)
            mw = to_words(sel)
            hit = np.zeros(R, bool)
            for w in range(W):
                hit |= (rel[:, w] & mw[w]) != 0
            pr |= hit.astype(np.uint64) << np.uint64(p)
        pres[B] = pr
    allones = lambda k: np.uint64(0xFFFFFFFFFFFFFFFF) if (1 << k) == 64 else np.uint64((1 << (1 << k)) - 1)
    fullp = {B: pres[B] == allones(len(B)) for B in sub_all if B not in big}
    for B in big:
        fullp[B] = np.all(rel == full_rel, axis=1)
    bond = {}
    for B in subsets:
        ok = ~fullp[B]
        for j in range(len(B)):
            ok &= fullp[B[:j] + B[j + 1:]]
        bond[B] = ok
    pairs = list(itertools.combinations(range(n), 2))
    out = {}
    for lo_size, tag in ((2, ">=2"), (3, ">=3")):
        dist = np.full((R, len(pairs)), 99, np.int64)
        for B in subsets:
            if len(B) < lo_size:
                continue
            for pi, (u, v) in enumerate(pairs):
                if u in B and v in B:
                    upd = bond[B] & (dist[:, pi] == 99)
                    dist[upd, pi] = len(B) - 1
        out[f"a {tag}"] = dist
        signed = dist.copy()
        if lo_size == 2:
            for pi, (u, v) in enumerate(pairs):
                eq = (pres[(u, v)] & np.uint64(1)) != 0          # pattern 00 present: the tie is "equal"
                signed[(dist[:, pi] == 1) & eq, pi] = 101
                signed[(dist[:, pi] == 1) & ~eq, pi] = 102
            out["b >=2"] = signed
        bs = np.stack([bond[B] for B in subsets if len(B) >= lo_size], 1).astype(np.int64)
        out[f"c {tag}"] = bs
        if lo_size == 2:
            sg = np.stack([np.where(bond[(u, v)], np.where((pres[(u, v)] & np.uint64(1)) != 0, 1, 2), 0)
                           for (u, v) in pairs], 1)
            out["c-s >=2"] = np.concatenate([bs, sg], 1)
        cols = []
        for B in subsets:
            if len(B) < lo_size:
                continue
            if B in big:
                for w in range(W):
                    cols.append(np.where(bond[B], (~rel[:, w]) & full_rel[w], np.uint64(0)))
            else:
                cols.append(np.where(bond[B], (~pres[B]) & allones(len(B)), np.uint64(0)).astype(np.uint64))
        out[f"c' {tag}"] = np.stack(cols, 1).view(np.int64)
    # (e): pairwise disagreement counts; (e+): with the number of allowed states
    cnt = np.zeros((R, len(pairs)), np.int64)
    for pi, (u, v) in enumerate(pairs):
        mw = to_words(bits[u] != bits[v])
        for w in range(W):
            cnt[:, pi] += np.bitwise_count(rel[:, w] & mw[w]).astype(np.int64)
    size = sum(np.bitwise_count(rel[:, w]).astype(np.int64) for w in range(W))
    out["e"] = cnt
    out["e+"] = np.concatenate([cnt, size[:, None]], 1)
    return out


def distinct(arr):
    return int(len(np.unique(arr, axis=0)))


def main():
    res = {}
    for n in (4, 5, 6):
        rel = all_relations(n)
        nz = np.any(rel != 0, axis=1)
        sat = rel[nz]
        uniq, inv, cnts = np.unique(sat, axis=0, return_inverse=True, return_counts=True)
        row = {"knot_sets": int(len(rel)), "satisfiable_sets": int(nz.sum()), "distinct_relations": int(len(uniq)),
               "relations_with_several_knot_sets": int((cnts > 1).sum())}
        if (cnts > 1).any():
            ids = np.nonzero(nz)[0]
            g = int(np.argmax(cnts > 1))
            members = ids[inv.ravel() == g][:2]
            ks = knots(n)
            row["example_same_relation"] = [[list(ks[j]) for j in range(len(ks)) if (int(s) >> j) & 1] for s in members]
        rd = readings(n, uniq)
        row["readings"] = {k: distinct(v) for k, v in rd.items()}
        res[n] = row
    # n = 7: the referee's own sample
    n = 7
    rng = np.random.default_rng(97)
    kw = np.array(knot_words(n))
    rows = set()
    for _ in range(60000):
        sel = rng.choice(len(kw), int(rng.integers(1, 13)), replace=False)
        r = np.bitwise_and.reduce(kw[sel], axis=0)
        if np.any(r != 0):
            rows.add(tuple(int(x) for x in r))
    sat7 = np.array(sorted(rows), dtype=np.uint64)
    rd7 = readings(n, sat7)
    res[7] = {"sampled_relations": int(len(sat7)), "readings": {k: distinct(v) for k, v in rd7.items()}}
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
