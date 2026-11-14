"""Optional sound pruning for fresh_search; no change to its frozen source.

Resolve native clauses with native clauses, then those resolvents with native
clauses (width at most five). Every resulting clause is an implicate. A bond
cannot strictly contain its nonfull support. We exclude only supports which
do not already meet both designated levels, so every crossing superset would
be strict. Completeness still comes from the original full existence circuit.
"""
from __future__ import annotations
import copy
import hashlib
import json
import time
from collections import defaultdict
from fresh_pattern import cnf
from fresh_search import compile_existence, search


def derived_nonfull(knots, rounds=2, max_width=5, clause_limit=150000):
    originals = sorted({frozenset(c) for c in cnf(knots)},key=lambda c:tuple(sorted(c)))
    by_literal = defaultdict(list)
    for i,c in enumerate(originals):
        for x in c:
            by_literal[x].append(i)
    known = set(originals)
    frontier = list(originals)
    resolutions = 0
    stopped = False
    for _ in range(rounds):
        following = []
        for c in frontier:
            for pivot in sorted(c):
                for i in by_literal[-pivot]:
                    d = originals[i]
                    r = (c-{pivot}) | (d-{-pivot})
                    if len(r)>max_width or any(-v in r for v in r):
                        continue
                    # Independently reconstruct the resolvent, with both parents
                    # already original/proved. No solver assertion is trusted.
                    assert pivot in c and -pivot in d
                    assert r == frozenset(v for v in c|d if v not in (pivot,-pivot))
                    resolutions += 1
                    if r not in known:
                        known.add(r)
                        following.append(r)
                        if len(known)>=clause_limit:
                            stopped = True
                            break
                if stopped:
                    break
            if stopped:
                break
        frontier = following
        if stopped:
            break
    supports = sorted({tuple(sorted({abs(x)-1 for x in c})) for c in known})
    digest = hashlib.sha256(json.dumps(supports,separators=(',',':')).encode()).hexdigest()
    return supports, {'rounds':rounds,'maximum_width':max_width,'proved_clauses':len(known),
                      'resolution_steps_checked':resolutions,'nonfull_supports':len(supports),
                      'stopped_at_clause_limit':stopped,'support_sha256':digest}


def add_support_filters(compilation, supports, A, B):
    original, root, stats = compilation
    circuit = copy.copy(original)
    circuit.clauses = list(original.clauses)
    aset,bset = set(A),set(B)
    blocks = [s for s in supports if not (aset.intersection(s) and bset.intersection(s))]
    variables = sorted({v for s in blocks for v in s})
    presence = {}
    for v in variables:
        circuit.top += 1
        p = presence[v] = circuit.top
        a,b = 2*v+1,2*v+2
        circuit.clauses.extend([[-a,p],[-b,p],[-p,a,b]])
    for support in blocks:
        circuit.clauses.append([-presence[v] for v in support])
    return (circuit,root,dict(stats)), len(blocks)


def accelerated_search(knots,nvars,A,B,cap=10,seconds=120,precompiled=None,support_cache=None):
    start = time.monotonic()
    if precompiled is None:
        precompiled = compile_existence(knots,nvars,start+seconds,8)
    if support_cache is None:
        support_cache = derived_nonfull(knots)
    supports, pruning_stats = support_cache
    compilation, blocked = add_support_filters(precompiled,supports,A,B)
    remaining = max(0.01,seconds-(time.monotonic()-start))
    result = search(knots,nvars,A,B,cap=cap,seconds=remaining,precompiled=compilation)
    result['resolution_pruning'] = dict(pruning_stats,applied_blocks=blocked,
                                        preparation_seconds=time.monotonic()-start-result['stats'].get('seconds',0))
    return result
