"""Seam reports of not-all-equal patterns, and one record-carrying count.

S1  complement-closed relations on s = 1..4 distinctions: 2^(2^(s-1)).
S2  how many are determined by their two-place shadows (s = 1, 2, 3); the
    failures at s = 3, and whether each is a knot (K1-K3).
S3  at s = 4, relations not determined by their three-place shadows.
S4  not-all-equal colourings of the tetrahedron, octahedron and icosahedron
    counted by a record-carrying run (bucket elimination along an order, the
    w-record law without combining), against brute force.
    python3 -B seam.py
"""

import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def states(s):
    return list(itertools.product((0, 1), repeat=s))


def complement_closed(s):
    pairs = []
    seen = set()
    for x in states(s):
        if x in seen:
            continue
        c = tuple(1 - v for v in x)
        seen |= {x, c}
        pairs.append((x, c))
    for mask in range(1 << len(pairs)):
        rel = set()
        for i, (x, c) in enumerate(pairs):
            if mask >> i & 1:
                rel |= {x, c}
        yield frozenset(rel)


def determined_by(rel, s, k):
    """Is rel equal to the set of states whose every k-place shadow lies in
    rel's k-place shadow?"""
    shadows = {}
    for idx in itertools.combinations(range(s), k):
        shadows[idx] = {tuple(x[i] for i in idx) for x in rel}
    rebuilt = {x for x in states(s) if all(tuple(x[i] for i in idx) in sh for idx, sh in shadows.items())}
    return rebuilt == set(rel)


def is_knot(rel, s):
    if not rel or len(rel) == 2 ** s:
        return False
    for drop in range(s):
        keep = [i for i in range(s) if i != drop]
        if len({tuple(x[i] for i in keep) for x in rel}) != 2 ** (s - 1):
            return False
    return True


def nae_ok(x, face):
    vals = {x[v] for v in face}
    return len(vals) == 2


def brute_count(n, faces):
    return sum(1 for x in states(n) if all(nae_ok(x, f) for f in faces))


def record_count(n, faces, order=None):
    """Bucket elimination: carry a record (dict from the carried distinctions'
    joint state to a count); absorb every face once all its distinctions have
    been brought in; sum out a distinction once no unabsorbed face uses it.
    Returns the count and the largest number of distinctions carried."""
    order = order or list(range(n))
    carried = []          # tuple of carried distinctions
    record = {(): 1}
    absorbed = [False] * len(faces)
    widest = 0
    for v in order:
        # bring v in
        carried.append(v)
        record = {k + (b,): c for k, c in record.items() for b in (0, 1)}
        widest = max(widest, len(carried))
        # absorb faces now fully carried
        pos = {u: i for i, u in enumerate(carried)}
        for fi, f in enumerate(faces):
            if not absorbed[fi] and all(u in pos for u in f):
                absorbed[fi] = True
                record = {k: c for k, c in record.items() if len({k[pos[u]] for u in f}) == 2}
        # forget distinctions no unabsorbed face uses
        for u in list(carried):
            if all(absorbed[fi] or u not in f for fi, f in enumerate(faces)):
                i = carried.index(u)
                new = {}
                for k, c in record.items():
                    kk = k[:i] + k[i + 1:]
                    new[kk] = new.get(kk, 0) + c
                record = new
                carried.pop(i)
    assert all(absorbed)
    return sum(record.values()), widest


TETRA = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
OCTA = [(a, b, c) for a in (0, 1) for b in (2, 3) for c in (4, 5)]
ICOSA = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5), (0, 5, 1), (1, 2, 6), (2, 3, 7), (3, 4, 8), (4, 5, 9), (5, 1, 10),
         (1, 6, 10), (2, 7, 6), (3, 8, 7), (4, 9, 8), (5, 10, 9), (6, 7, 11), (7, 8, 11), (8, 9, 11), (9, 10, 11), (10, 6, 11)]


def main():
    out = {}
    for s in (1, 2, 3, 4):
        rels = list(complement_closed(s))
        row = {"complement_closed": len(rels),
               "determined_by_2_place_shadows": sum(determined_by(r, s, 2) for r in rels) if s >= 2 else len(rels)}
        if s == 3:
            fails = [r for r in rels if not determined_by(r, s, 2)]
            row["failures"] = [sorted("".join(map(str, x)) for x in set(states(3)) - r) for r in fails]
            row["failures_are_knots"] = [is_knot(r, 3) for r in fails]
        if s == 4:
            row["determined_by_3_place_shadows"] = sum(determined_by(r, s, 3) for r in rels)
            nae4 = frozenset(x for x in states(4) if len(set(x)) == 2)
            row["nae4_determined_by_3_place_shadows"] = determined_by(nae4, 4, 3)
        out[f"s={s}"] = row
    counts = {}
    for name, n, faces in (("tetrahedron", 4, TETRA), ("octahedron", 6, OCTA), ("icosahedron", 12, ICOSA)):
        # every face appears; each distinction in some face
        assert sorted({u for f in faces for u in f}) == list(range(n))
        bf = brute_count(n, faces)
        rc, widest = record_count(n, faces)
        counts[name] = {"brute_force": bf, "record_run": rc, "largest_carried": widest}
    out["S4_counts"] = counts
    expected = {"s=1": 2, "s=2": 4, "s=3": 16, "s=4": 256}
    out["S1"] = all(out[k]["complement_closed"] == v for k, v in expected.items())
    out["S2"] = ([out[f"s={s}"]["determined_by_2_place_shadows"] for s in (1, 2, 3)] == [2, 4, 12]
                 and all(out["s=3"]["failures_are_knots"]))
    out["S3"] = out["s=4"]["nae4_determined_by_3_place_shadows"] is False
    out["S4"] = all(c["brute_force"] == c["record_run"] for c in counts.values()) and \
        [counts[k]["brute_force"] for k in ("tetrahedron", "octahedron", "icosahedron")] == [6, 18, 72]
    with open(os.path.join(HERE, "seam.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
