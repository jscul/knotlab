"""RING-READ-20261118-001A: the ring's bond-distance tables and readers past six distinctions.

The ring of four four-place knots and one five-place knot grows under the cheapest counts (RING-GROWTH-20261118-001's ring.py,
closed record).  A junction is a set of distinctions; a distinction lies in one junction (loose) or two (shared).

Bond distance.  In the junction graph with one outside vertex o that ends every loose distinction, the minimal parity
consequences (circuits of the cut space) are the bonds delta(J): J and its complement both connected.  With o outside J, the
support of delta(J) is the XOR of J's junctions.  D(x, y) = (fewest distinctions in a bond containing both) - 1.

`bond_table(stars, m, K)` enumerates every connected J of at most m junctions (o excluded) whose complement, with o, is
connected, and keeps the distances up to K; every other pair is pooled at K + 1 ("larger").  Completeness for bonds whose two
sides both exceed m junctions is checked by comparing m with m + 1 (and argued in the decision note).

Readers.  R0 = BOND-NEXT-JOIN-20261117-001's `read_stages` (support sizes 3 to 6), imported from the closed proof file.
R1 = the same stages run on to support size K + 1.  R2 = R1's junctions, repaired: remove candidates until every distinction
lies in one or two, and keep only repairs whose own bond table equals the given one.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RING = ROOT / 'experiments/RING-GROWTH-20261118-001B/RING-GROWTH-20261118-001B-E001_rings'
READER = ROOT / 'proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/check_rearrangements.py'
DIGESTS = {
    RING / 'ring.py': '00a66203cfca618c22d1996e9e598e05160a06b6cac192968a09a575bbc6ab72',
    READER: '2a27ca668cef0fc3f26492789958073161a2af572cf113f60b9e849ed973143a',
    ROOT / 'experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py':
        'ba4d90274ebf36cb16626c29aba7be116437d6b694bf05f650295881da1d2074',
    ROOT / 'experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/freelib.py':
        '7f9ef5f67852b35fdd816e4a04f7fe3df2998d611e792ed9e0a44cba8f46e7a5',
}
for _path, _digest in DIGESTS.items():
    assert hashlib.sha256(_path.read_bytes()).hexdigest() == _digest, _path
sys.path.insert(0, str(RING))
import ring as _ring  # noqa: E402  (puts startlib and freelib on the path)
import startlib as S  # noqa: E402

_spec = importlib.util.spec_from_file_location('bond_next_join_reader', READER)
B = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = B
_spec.loader.exec_module(B)

SIZES = [4, 4, 4, 4, 5]


def grow(T):
    """The ring grown T complete rounds; returns the presentation."""
    return _ring.grow(_ring.ring(SIZES), T)


def stars_of(P):
    return [frozenset(b) for b in P.bits_of]


def owners(stars):
    own = {}
    for j, s in enumerate(stars):
        for b in s:
            own.setdefault(b, []).append(j)
    return own


def junction_graph(stars):
    """Adjacency of junctions; index len(stars) is the outside vertex o."""
    n = len(stars)
    adj = [set() for _ in range(n + 1)]
    for b, js in owners(stars).items():
        if len(js) > 2:
            raise ValueError('a distinction in three junctions')
        u, v = (js[0], js[1]) if len(js) == 2 else (js[0], n)
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bond_table(stars, m, K):
    """Exact bond distances up to K over bonds with a side of at most m junctions; other pairs pooled at K + 1."""
    n = len(stars)
    adj = junction_graph(stars)
    OUT = n
    mask = [sum(1 << b for b in s) for s in stars]
    best = {}
    stats = Counter()

    def complement_connected(U):
        seen = {OUT}
        stack = [OUT]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in U and y not in seen:
                    seen.add(y)
                    stack.append(y)
        return len(seen) + len(U) == n + 1

    def record(U, sup):
        size = sup.bit_count()
        if size > K + 1:
            return
        bits = []
        x = sup
        while x:
            low = x & -x
            bits.append(low.bit_length() - 1)
            x ^= low
        better = [p for p in combinations(bits, 2) if best.get(p, K + 1) > size - 1]
        if not better:
            return
        stats['complement_checks'] += 1
        if complement_connected(U):
            for p in better:
                best[p] = size - 1

    def extend(U, sup, ext, v):
        stats['sides'] += 1
        record(U, sup)
        if len(U) == m:
            return
        ext = set(ext)
        while ext:
            w = ext.pop()
            nb = {x for x in adj[w] if x != OUT and x > v and x not in U and all(x not in adj[u] for u in U)}
            extend(U | {w}, sup ^ mask[w], ext | nb, v)

    for v in range(n):
        extend(frozenset([v]), mask[v], {x for x in adj[v] if x != OUT and x > v}, v)
    bits = sorted(owners(stars))
    table = {p: best.get(p, K + 1) for p in combinations(bits, 2)}
    return table, dict(stats)


def pooled(table, H):
    """Distances above H pooled at H + 1."""
    return {p: (d if d <= H else H + 1) for p, d in table.items()}


def r0(table):
    """BOND-NEXT-JOIN's proved reader, unchanged (support sizes 3 to 6)."""
    return B.read_stages(table)[6]


def r1(table, top):
    """The same stages run on to support size `top`."""
    table = B.normalize_distance_pairs(table)
    labels = B.table_labels(table)
    stars = set()
    for support in range(3, top + 1):
        raw = {pair for pair, delta in table.items() if delta < support}
        stars = B.clique_stars(labels, B.prune(raw, stars, support))
    return stars


def in_span(word, basis):
    """GF(2) membership; basis maps leading bit to row."""
    while word:
        row = basis.get(word.bit_length() - 1)
        if row is None:
            return False
        word ^= row
    return True


def add_row(word, basis):
    while word:
        top = word.bit_length() - 1
        row = basis.get(top)
        if row is None:
            basis[top] = word
            return
        word ^= row


def r1_linear(table, top):
    """R1', the advisor's linear prune: R1's stages, discarding every clique in the span of the previous stage's junctions."""
    table = B.normalize_distance_pairs(table)
    labels = B.table_labels(table)
    stars = set()
    for support in range(3, top + 1):
        raw = {pair for pair, delta in table.items() if delta < support}
        basis = {}
        for s in stars:
            add_row(sum(1 << b for b in s), basis)
        found = B.clique_stars(labels, B.prune(raw, stars, support))
        stars = {c for c in found if c in stars or not in_span(sum(1 << b for b in c), basis)}
    return stars


def legal(stars, labels):
    """Legal for the law: every distinction in one or two junctions, junctions of at least three distinctions, two junctions
    sharing at most one distinction."""
    cover = Counter(b for s in stars for b in s)
    if not all(1 <= cover[b] <= 2 for b in labels) or any(len(s) < 3 for s in stars):
        return False
    shared = Counter()
    own = owners(stars)
    for b, js in own.items():
        if len(js) == 2:
            shared[tuple(sorted(js))] += 1
    return all(c == 1 for c in shared.values())


def r2(table, top, m, K, max_remove=6):
    """R1's junctions, repaired to a legal incidence, kept when their own table equals the given one.
    Returns (survivors, report)."""
    labels = B.table_labels(table)
    cand = sorted(r1(table, top), key=lambda s: (len(s), sorted(s)))
    cover = Counter(b for s in cand for b in s)
    over = {b for b, c in cover.items() if c > 2}
    involved = [i for i, s in enumerate(cand) if s & over]
    report = {'candidates': len(cand), 'over_covered_distinctions': len(over), 'candidates_in_conflict': len(involved),
              'uncovered_distinctions': sum(1 for b in labels if cover[b] == 0)}
    repairs = []
    report['removal_sizes_tried'] = 0
    if not over:
        repairs = [frozenset()]
    else:
        from math import comb
        for k in range(1, max_remove + 1):
            if comb(len(involved), k) > 200000:
                report['removals_truncated_at'] = k
                break
            report['removal_sizes_tried'] = k
            for drop in combinations(involved, k):
                d = frozenset(drop)
                if any(prev <= d for prev in repairs):
                    continue  # inclusion-minimal repairs only
                kept = [s for i, s in enumerate(cand) if i not in d]
                if legal(kept, labels):
                    repairs.append(d)
    report['legal_repairs'] = len(repairs)
    survivors = []
    for d in repairs:
        kept = [s for i, s in enumerate(cand) if i not in d]
        own, _ = bond_table(kept, m, K)
        if pooled(own, K) == pooled(table, K):
            survivors.append(frozenset(kept))
    report['repairs_reproducing_the_table'] = len(survivors)
    return survivors, report


def next_round(stars):
    """One round of the cheapest counts grown from these junctions alone (no rounds, no parents): the multiset of
    (parent junctions, fresh count) of the new junctions, parents named by their distinction sets."""
    stars = sorted(stars, key=lambda s: sorted(s))
    P = S.from_junctions([sorted(s) for s in stars])
    P.linalg = False
    old = len(stars)
    own = owners(stars)
    P.step(S.F.fewest, None)
    return Counter((frozenset(stars[own[b][0]] for b in P.bits_of[j] if b in own), P.fresh[j])
                   for j in range(old, len(P.bits_of)))


def true_next_round(T):
    """The true round T + 1, in the same terms."""
    P = grow(T + 1)
    stars = [frozenset(b) for b, r in zip(P.bits_of, P.round_of) if r <= T]
    # junctions of round <= T as they stood at round T: drop the bits added later? Bits are only added at birth, so a
    # junction's set is final once it is born.
    own = owners(stars)
    return Counter((frozenset(stars[own[b][0]] for b in P.bits_of[j] if b in own), P.fresh[j])
                   for j in range(len(P.bits_of)) if P.round_of[j] == T + 1)
