"""R3n, version 2 (Amendment 5): jointly dependent accepted cliques are all kept and flagged (version 1 dropped them all, which
loses every junction when the loose set is as small as a junction).  Otherwise as reader3n.py:

R3n: RING-READ-20261118-001B's incremental reader R3 with a tie rule that does not use names (Amendment 2).

R3 adds the cliques of a stage one by one in the order of their sorted distinction names, refusing a clique that meets an
accepted junction in two or more distinctions or lies in the span of the accepted ones; when two candidates of one stage
conflict, the names decide (VARIABLE-OUTPUT-READER-20261118-001J's 27-distinction example).  R3n treats the stage's candidates
together:
- eligible: maximal cliques of at most s distinctions, not known, not in the GF(2) span of the known junctions, meeting each known
  junction in at most one distinction (as R3);
- conflict: two eligible cliques sharing two or more distinctions;
- in each connected part of the conflict graph, the cliques lying in every maximum set of pairwise non-conflicting cliques are
  accepted (a part of more than 18 cliques accepts nothing and is flagged);
- if the accepted cliques together with the known ones are dependent, they are all kept (flagged): which of them the table
  cannot choose between is left to the law, as with the outside swap.
Everything else (the set-aside step, the closure, the span test) is R3's, imported unchanged.
"""
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental'))
import reader3 as R3  # noqa: E402
R = R3.R
B = R.B
MAXPART = 18


def word(c):
    return sum(1 << b for b in c)


def max_independent_sets(nodes, edges):
    """All maximum independent sets of a small graph (nodes: list; edges: set of frozensets)."""
    best, sets = 0, []
    n = len(nodes)
    for mask in range(1 << n):
        chosen = [nodes[i] for i in range(n) if mask >> i & 1]
        if len(chosen) < best:
            continue
        if any(frozenset((a, b)) in edges for a, b in combinations(chosen, 2)):
            continue
        if len(chosen) > best:
            best, sets = len(chosen), []
        sets.append(frozenset(chosen))
    return sets


def r3n(table, top, flags=None):
    table = B.normalize_distance_pairs(table)
    labels = B.table_labels(table)
    known, known_set, basis = [], set(), {}
    flags = flags if flags is not None else Counter()
    for s in range(3, top + 1):
        raw = {p for p, d in table.items() if d < s}
        holders = {}
        for i, st in enumerate(known):
            for b in st:
                holders.setdefault(b, set()).add(i)
        crossed = set()
        for sup in R3.groups(known, s):
            for x, y in combinations(R3.bits_of(sup), 2):
                if not (holders.get(x, set()) & holders.get(y, set())):
                    crossed.add((x, y))
        found = B.clique_stars(labels, raw - crossed)
        eligible = [c for c in found if c not in known_set and len(c) <= s
                    and not any(len(c & k) > 1 for k in known) and not R.in_span(word(c), basis)]
        edges = {frozenset((a, b)) for a, b in combinations(eligible, 2) if len(a & b) > 1}
        if edges:
            flags['conflict_stages'] += 1
        # connected parts of the conflict graph
        adj = {c: set() for c in eligible}
        for e in edges:
            a, b = tuple(e)
            adj[a].add(b)
            adj[b].add(a)
        accepted, seen = [], set()
        for c in eligible:
            if c in seen:
                continue
            part, stack = [], [c]
            seen.add(c)
            while stack:
                x = stack.pop()
                part.append(x)
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            if len(part) == 1:
                accepted.append(part[0])
                continue
            if len(part) > MAXPART:
                flags['large_conflict'] += 1
                continue
            mis = max_independent_sets(part, edges)
            common = frozenset.intersection(*mis)
            if len(mis) > 1:
                flags['tie'] += 1
            accepted.extend(common)
        # joint independence, decided without names
        drop = set()
        for c in accepted:
            b2 = dict(basis)
            for d in accepted:
                if d != c:
                    R.add_row(word(d), b2)
            if R.in_span(word(c), b2):
                drop.add(c)
        if drop:
            flags['dependent_kept'] += 1
        for c in accepted:
            known.append(c)
            known_set.add(c)
            R.add_row(word(c), basis)
    return set(known)
