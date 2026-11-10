"""The frozen census of WEAK-APER-20261110-001B: level laws on three values under Leibniz's rule.

A level law on Z/3 is a set S of triples (a, b, c), a + b + c = 4: a place of value k is allowed when a of its four neighbours have
value k - 1, b have value k and c have value k + 1 (mod 3). There are 15 triples, so 2^15 = 32,768 laws. The horofunction law of
LEIBNIZ-BOARDS-20261110-001 is S = {(1, 0, 3)}.

For each law, on the tree of names (patterns = a place's value and its x-, X-, y-, Y-neighbours' values):
  E    no solution (the pruned pattern set is empty);
  D    deterministic: no pattern has two compatible neighbour patterns in one direction (finitely many solutions);
  A    a periodic solution (a finite board) uses a branching pattern: the balance linear program, maximizing the weight on
       branching patterns, has a positive optimum (LEIBNIZ-BOARDS-20261110-001A's Lemma A gives a free solution);
  WA   weakly aperiodic: solutions exist but no finite board (the balance program is infeasible); then
         L1  a doubly recurrent branching type: a vertex type (pattern, parent direction), able to reach a branching choice, recurs
             in two different child directions of itself (ticket A's Lemma A'' gives a free solution), or
         L2  horofunction certificate: (1, 0, 3) is in S (Busemann functions of generic ends are free solutions), or
         U   neither certificate: undecided by the census;
  P    periodic but no periodic solution uses a branching pattern (branching only off the periodic solutions): also checked for L1
       and L2, else U.

Usage: census.py [--out FILE] [--controls-only]
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SLUG = 'WEAK-APER-20261110-001B-E001_level_laws_on_three_values'
DEFAULT_OUT = os.path.join(ROOT, 'artifacts', 'WEAK-APER-20261110-001B', SLUG, 'census.json')

Q = 3
INV = (1, 0, 3, 2)          # letters x, X, y, Y
PATTERNS = list(itertools.product(range(Q), repeat=5))    # (centre, x, X, y, Y)
TRIPLES = [(a, b, 4 - a - b) for a in range(5) for b in range(5 - a)]
assert len(TRIPLES) == 15


def triple(p):
    c = p[0]
    a = sum(1 for v in p[1:] if v == (c - 1) % Q)
    b = sum(1 for v in p[1:] if v == c)
    return (a, b, 4 - a - b)


TRIPLE_OF = [triple(p) for p in PATTERNS]


def compat(p, g, q):
    """q can be the pattern of p's g-neighbour."""
    return q[0] == p[1 + g] and q[1 + INV[g]] == p[0]


def allowed(S):
    return [p for p, t in zip(PATTERNS, TRIPLE_OF) if t in S]


def prune(allowed_pats):
    """The tree patterns: the greatest set in which every pattern has a compatible pattern in every direction."""
    P = set(allowed_pats)
    by_key = {}
    changed = True
    while changed:
        changed = False
        for p in list(P):
            for g in range(4):
                if not any(compat(p, g, q) for q in P):
                    P.discard(p)
                    changed = True
                    break
    return sorted(P)


def neighbours_index(P):
    """For each pattern and direction, the compatible patterns in P."""
    key_in = {}
    for q in P:
        for g in range(4):
            key_in.setdefault((g, q[0], q[1 + INV[g]]), []).append(q)
    nb = {}
    for p in P:
        for g in range(4):
            nb[(p, g)] = key_in.get((g, p[1 + g], p[0]), [])
    return nb


def balance_lp(P, weight_on=None):
    """Feasibility of the balance equations over P (a finite board exists), or, with weight_on, the maximal total weight a
    normalized balanced solution puts on those patterns."""
    idx = {p: i for i, p in enumerate(P)}
    n = len(P)
    rows = []
    for g in (0, 2):
        for a in range(Q):
            for b in range(Q):
                r = np.zeros(n)
                for p in P:
                    if (p[0], p[1 + g]) == (a, b):
                        r[idx[p]] += 1
                    if (p[1 + INV[g]], p[0]) == (a, b):
                        r[idx[p]] -= 1
                if r.any():
                    rows.append(r)
    A_eq = np.array(rows + [np.ones(n)]) if rows else np.ones((1, n))
    b_eq = np.zeros(len(A_eq))
    b_eq[-1] = 1.0
    if weight_on is None:
        c = np.zeros(n)
    else:
        c = np.array([-1.0 if p in weight_on else 0.0 for p in P])
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * n, method='highs')
    if res.status != 0:
        return None
    return -res.fun if weight_on is not None else 1.0


def types_graph(P, nb):
    """Vertex types (pattern, parent direction) and their child types; locally branching types; the types that can reach one."""
    types = [(p, d) for p in P for d in range(4)]
    children = {}
    loc_branch = set()
    for (p, d) in types:
        ch = {}
        for h in range(4):
            if h == d:
                continue
            opts = [(q, INV[h]) for q in nb[(p, h)]]
            ch[h] = opts
            if len(opts) >= 2:
                loc_branch.add((p, d))
        children[(p, d)] = ch
    # reverse reachability to locally branching types
    rev = {t: [] for t in types}
    for t, ch in children.items():
        for h, opts in ch.items():
            for c in opts:
                rev[c].append(t)
    branch = set(loc_branch)
    stack = list(loc_branch)
    while stack:
        t = stack.pop()
        for s in rev[t]:
            if s not in branch:
                branch.add(s)
                stack.append(s)
    return types, children, branch


def scc_ids(types, children):
    """Strongly connected components of the type graph (iterative Kosaraju)."""
    succ = {t: [c for opts in children[t].values() for c in opts] for t in types}
    pred = {t: [] for t in types}
    for t, cs in succ.items():
        for c in cs:
            pred[c].append(t)
    seen, order = set(), []
    for t0 in types:
        if t0 in seen:
            continue
        stack = [(t0, iter(succ[t0]))]
        seen.add(t0)
        while stack:
            u, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                order.append(u)
                stack.pop()
            elif nxt not in seen:
                seen.add(nxt)
                stack.append((nxt, iter(succ[nxt])))
    comp = {}
    cid = 0
    for t0 in reversed(order):
        if t0 in comp:
            continue
        stack = [t0]
        comp[t0] = cid
        while stack:
            u = stack.pop()
            for v in pred[u]:
                if v not in comp:
                    comp[v] = cid
                    stack.append(v)
        cid += 1
    return comp


def l1_certificate(types, children, branch, comp):
    """A doubly recurrent branching type: tau in branch with two child directions h1 != h2, each with a child type in tau's
    strongly connected component (so a configuration recurs to tau through both)."""
    for t in branch:
        dirs = [h for h, opts in children[t].items() if any(comp[c] == comp[t] for c in opts)]
        if len(dirs) >= 2:
            return [list(t[0]), t[1]]
    return None


def classify(S):
    r = {'law': sorted(S)}
    P = prune(allowed(S))
    r['tree_patterns'] = len(P)
    if not P:
        r['class'] = 'E'
        return r
    nb = neighbours_index(P)
    branching = {p for p in P if any(len(nb[(p, g)]) >= 2 for g in range(4))}
    r['branching_patterns'] = len(branching)
    if not branching:
        r['class'] = 'D'
        return r
    feas = balance_lp(P)
    if feas is not None:
        w = balance_lp(P, weight_on=branching)
        if w is not None and w > 1e-9:
            r['class'] = 'A'
            r['periodic_branching_weight'] = round(w, 6)
            return r
        r['periodic'] = True
    else:
        r['periodic'] = False
    types, children, branch = types_graph(P, nb)
    comp = scc_ids(types, children)
    l1 = l1_certificate(types, children, branch, comp)
    l2 = (1, 0, 3) in S
    base = 'WA' if not r['periodic'] else 'P'
    if l1 is not None:
        r['class'] = base + '-L1'
        r['l1_type'] = l1
    elif l2:
        r['class'] = base + '-L2'
    else:
        r['class'] = base + '-U'
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--controls-only', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    controls = {'horofunction': classify({(1, 0, 3)}), 'empty': classify(set()),
                'full': classify(set(TRIPLES))}
    print('controls', json.dumps({k: v['class'] for k, v in controls.items()}), flush=True)
    out = {'controls': controls}
    if not args.controls_only:
        laws = {}
        counts = {}
        for m in range(1 << 15):
            S = {TRIPLES[i] for i in range(15) if (m >> i) & 1}
            r = classify(S)
            laws[m] = r
            counts[r['class']] = counts.get(r['class'], 0) + 1
            if m % 4096 == 4095:
                print(m + 1, counts, round(time.time() - t0, 1), flush=True)
        out['laws'] = laws
        out['counts'] = counts
        out['undecided'] = sorted(m for m, r in laws.items() if r['class'].endswith('-U'))
    out['seconds'] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, 'w'), indent=1, sort_keys=True, default=list)
    print(json.dumps(out.get('counts', {})), 'undecided', len(out.get('undecided', [])), out['seconds'], flush=True)


if __name__ == '__main__':
    main()
