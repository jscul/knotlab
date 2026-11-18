"""RING-READ-20261118-001B: the incremental reader R3, frozen before it runs.

R3 reads the bond-distance table stage by stage, s = 3 .. top:
- every junction read at an earlier stage is kept;
- a short pair (distance < s) is removed when both its distinctions lie in the support of the sum of a connected set of known
  junctions (connected through shared distinctions; at most s of them, grown only while the running support stays at most
  s + 2, the advisor's closure) whose support has at most s distinctions, unless one known junction holds both;
- the new junctions of stage s are the maximal cliques of what remains, of at most s distinctions, that are not known, not in
  the GF(2) span of the known ones, and share at most one distinction with every known junction (frozen fact F2 used as a
  filter); they are added in order of size, then of their sorted distinctions; larger cliques wait for their own stage.
R3+ is R3 followed by ticket A's legality repair and own-table check.  The table, the growth and the step are ticket A's
(`ringread.py`, commit a90132fcc, hash checked on import).
"""
import hashlib
import sys
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / 'experiments/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables'
assert hashlib.sha256((A / 'ringread.py').read_bytes()).hexdigest() == \
    'f38d0b7406a181ec0273df9baa2445fb1b820c0e60a36a06b3664956702d9c43'
sys.path.insert(0, str(A))
import ringread as R  # noqa: E402
B = R.B


def groups(known, s, slack=2):
    """Connected sets of at most s known junctions with support at most s, grown (ESU) only while the running support stays
    at most s + slack.  Yields supports as sorted lists."""
    holders = {}
    for i, st in enumerate(known):
        for b in st:
            holders.setdefault(b, []).append(i)
    adj = {i: set() for i in range(len(known))}
    for js in holders.values():
        for a, c in combinations(js, 2):
            adj[a].add(c)
            adj[c].add(a)
    masks = [sum(1 << b for b in st) for st in known]
    out = []

    def extend(U, sup, ext, v):
        if len(U) > 1 and sup.bit_count() <= s:
            out.append(sup)
        if len(U) == s:
            return
        ext = set(ext)
        while ext:
            w = ext.pop()
            nsup = sup ^ masks[w]
            if nsup.bit_count() > s + slack:
                continue
            nb = {x for x in adj[w] if x > v and x not in U and all(x not in adj[u] for u in U)}
            extend(U | {w}, nsup, ext | nb, v)

    for v in range(len(known)):
        if masks[v].bit_count() <= s + slack:
            extend(frozenset([v]), masks[v], {x for x in adj[v] if x > v}, v)
    return out


def bits_of(mask):
    out = []
    while mask:
        low = mask & -mask
        out.append(low.bit_length() - 1)
        mask ^= low
    return out


def r3(table, top):
    table = B.normalize_distance_pairs(table)
    labels = B.table_labels(table)
    known, known_set, basis = [], set(), {}
    for s in range(3, top + 1):
        raw = {p for p, d in table.items() if d < s}
        holders = {}
        for i, st in enumerate(known):
            for b in st:
                holders.setdefault(b, set()).add(i)
        crossed = set()
        for sup in groups(known, s):
            for x, y in combinations(bits_of(sup), 2):
                if not (holders.get(x, set()) & holders.get(y, set())):
                    crossed.add((x, y))
        found = B.clique_stars(labels, raw - crossed)
        for c in sorted(found, key=lambda c: (len(c), sorted(c))):
            if c in known_set or len(c) > s:
                continue
            if any(len(c & k) > 1 for k in known):
                continue
            w = sum(1 << b for b in c)
            if R.in_span(w, basis):
                continue
            known.append(c)
            known_set.add(c)
            R.add_row(w, basis)
    return set(known)


def repair(cand, table, m, K, max_remove=6):
    """Ticket A's R2 step on given candidates: inclusion-minimal removals to a legal incidence, kept when the own table
    equals the given one."""
    labels = B.table_labels(table)
    cand = sorted(cand, key=lambda s: (len(s), sorted(s)))
    cover = Counter(b for s in cand for b in s)
    over = {b for b, c in cover.items() if c > 2}
    involved = [i for i, s in enumerate(cand) if s & over]
    report = {'candidates': len(cand), 'over_covered_distinctions': len(over), 'candidates_in_conflict': len(involved),
              'uncovered_distinctions': sum(1 for b in labels if cover[b] == 0), 'removal_sizes_tried': 0}
    repairs = []
    if not over:
        repairs = [frozenset()] if R.legal(cand, labels) else []
    else:
        for k in range(1, max_remove + 1):
            if comb(len(involved), k) > 200000:
                report['removals_truncated_at'] = k
                break
            report['removal_sizes_tried'] = k
            for drop in combinations(involved, k):
                d = frozenset(drop)
                if any(prev <= d for prev in repairs):
                    continue
                kept = [s for i, s in enumerate(cand) if i not in d]
                if R.legal(kept, labels):
                    repairs.append(d)
    report['legal_repairs'] = len(repairs)
    survivors = []
    for d in repairs:
        kept = [s for i, s in enumerate(cand) if i not in d]
        own, _ = R.bond_table(kept, m, K)
        if R.pooled(own, K) == R.pooled(table, K):
            survivors.append(frozenset(kept))
    report['repairs_reproducing_the_table'] = len(survivors)
    return survivors, report
