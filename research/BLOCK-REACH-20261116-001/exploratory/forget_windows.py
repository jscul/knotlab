"""Exploratory (BLOCK-REACH-20261116-001, the thread's own, 2026-11-16): for small-orbit descriptions, the one-step relations of the
blocks along every descending path (an orbit's assignment to one child orbit's assignment, the block's knots holding and every other
child's subtree feasible, at stabilised depth), and the least r such that every composition of r consecutive steps is a product of its
two projections (forgets). BRANCH-DEPTH-20261112-001A then gives a lower bound 1 + ceil(s/r) at every depth along each path."""
import gzip
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import WindowTree  # noqa: E402


def step_relations(tree):
    F = tree.feasible(12)
    r0 = next(r for r in range(12) if F[r] == F[r + 1])
    Fc = F[r0]
    rel = {}
    for t in range(len(tree.types)):
        for ci, (c, pos) in enumerate(tree.children[t]):
            pairs = tree.step(t, Fc, ci, frozenset((x, x) for x in range(1 << tree.m[t])))
            rel[(t, ci)] = (c, frozenset(pairs))
    return rel, Fc


def compose(R, S):
    by = {}
    for a, b in S:
        by.setdefault(a, set()).add(b)
    return frozenset((a, c) for a, b in R for c in by.get(b, ()))


def rectangular(R):
    if not R:
        return True
    A = {a for a, _ in R}
    B = {b for _, b in R}
    return len(R) == len(A) * len(B)


def least_forget(tree, rmax=6):
    rel, Fc = step_relations(tree)
    # relations along paths: state = (type, composed relation from the start of the window)
    for r in range(1, rmax + 1):
        ok = True
        for t0 in range(len(tree.types)):
            frontier = {(t0, frozenset((x, x) for x in range(1 << tree.m[t0])))}
            for _ in range(r):
                nxt = set()
                for t, R in frontier:
                    for ci in range(len(tree.children[t])):
                        c, S = rel[(t, ci)]
                        nxt.add((c, compose(R, S)))
                frontier = nxt
            if not all(rectangular(R) for _, R in frontier):
                ok = False
                break
        if ok:
            return r
    return None


if __name__ == '__main__':
    recs = [json.loads(l) for l in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')]
    tally = Counter()
    for r in recs:
        if r.get('union') != 'alive' or 'key' not in r:
            continue
        prof = tuple(x['L_N'] for x in r['levels'])
        name = ('ruler' if prof == (3, 4, 5, 6) else 'half' if prof == (3, 3, 4, 4) else
                'direct' if len(set(prof)) == 1 and all(isinstance(x, int) for x in prof) else
                'undecided' if 'undecided' in prof else 'other')
        try:
            tree = WindowTree(r['key'])
        except ValueError:
            continue
        tally[(name, least_forget(tree))] += 1
    for k, v in sorted(tally.items(), key=str):
        print(k, v)
