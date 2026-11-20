"""Determine which groups can increase the eccentricity of the recurring tip."""
import argparse
import gzip
import json
import sys
from functools import lru_cache
from pathlib import Path

import networkx as nx
from mixed_turns import Stage, members


def radial_layers(stage, tip):
    here, seen = 1 << tip, 0
    result = []
    while here:
        result.append(here)
        seen |= here
        hset = {h for v in members(here) for h in stage.at[v]}
        here = 0
        for h in hset:
            here |= stage.blocks[h]
        here &= ~seen
    assert seen == stage.full
    return result


def future_sets(stage, parents, domain):
    full = stage.full
    physical = list(members(domain))
    def hood(v):
        return stage.hood(stage.at[v])
    graph = nx.Graph()
    graph.add_nodes_from(physical)
    for v in physical:
        graph.add_edges_from((v, w) for w in members(hood(v) & domain) if w > v)
    groups = []
    maxima = 0
    for clique in nx.find_cliques(graph):
        maxima += 1
        if len(clique) < 3:
            continue
        mask = sum(1 << v for v in clique)
        if any(mask & ~stage.blocks[h] == 0 for h in stage.at[clique[0]]):
            continue
        outside = full ^ domain
        for v in clique:
            outside &= hood(v)
            if not outside:
                groups.append(mask)
                break
    # A large legal group through a,b exists precisely when their common
    # closed neighborhood contains a clique that escapes every block holding a,b.
    @lru_cache(maxsize=50000)
    def escapes(available, held):
        if not held:
            return True
        if not available:
            return False
        choices = min((available & ~stage.blocks[h] for h in held), key=int.bit_count)
        if not choices:
            return False
        union = 0
        for h in held:
            union |= stage.blocks[h]
        if available & ~union:
            return True
        for v in members(choices):
            following = tuple(h for h in held if stage.blocks[h] >> v & 1)
            if escapes(available & hood(v), following):
                return True
        return False
    residual = []
    for a, b in graph.edges():
        held = tuple(sorted(set(stage.at[a]).intersection(stage.at[b])))
        assert held
        if not escapes(hood(a) & hood(b), held):
            residual.append((1 << a) | (1 << b))
    unary = []
    for v in physical:
        degree = (hood(v) | (1 << v)).bit_count() - 1
        if len(parents[v]) == 1 and degree <= 1:
            unary.extend([1 << v] * (2-degree))
        if len(parents[v]) > 1 and degree == 0:
            unary.append(1 << v)
    return groups + residual + unary, dict(candidate_pairs=graph.number_of_edges(),
            induced_maximal_cliques=maxima, full_unheld_maxima=len(groups),
            literal_residual_pairs=len(residual), unary=len(unary))


def run(cache, start, age):
    pref = cache / f"start-{start:02}-age{age:02}"
    stage = Stage(pref.with_suffix(".txt"))
    parents = json.load(gzip.open(pref.with_suffix(".parents.json.gz"), "rt"))
    tip, = [i for i, p in enumerate(parents) if len(p) == 1]
    layers = radial_layers(stage, tip)
    old_r = len(layers)-1
    groups, stats = future_sets(stage, parents, layers[-1])
    old_union = set(v for g in groups for v in members(g))
    return dict(start=start, old_age=age, old_radius=old_r,
                old_layer_sizes=[b.bit_count() for b in layers],
                new_radius=old_r+int(bool(groups)), extreme_group_count=len(groups),
                old_sites_used=len(old_union), breakdown=stats,
                new_outer_supports_if_increased=[list(members(g)) for g in groups])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cache",type=Path)
    p.add_argument("start",type=int)
    p.add_argument("age",type=int)
    p.add_argument("output",type=Path)
    opts=p.parse_args()
    ans=run(opts.cache,opts.start,opts.age)
    payload=(json.dumps(ans, separators=(",", ":"))+"\n").encode()
    opts.output.write_bytes(gzip.compress(payload, mtime=0) if opts.output.suffix==".gz" else payload)
    print({k:v for k,v in ans.items() if k!="new_outer_supports_if_increased"})
