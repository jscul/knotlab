"""Compress the dominant-block roster and certify its exact birth corrections."""

import argparse
from collections import Counter, defaultdict
from functools import cached_property
import gzip
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path

import networkx as nx

from control_hybrid import indices


def mask_of(vertices, n):
    packed = bytearray((n + 7)//8)
    for u in vertices:
        packed[u >> 3] |= 1 << (u & 7)
    return int.from_bytes(packed, "little")


class NearBlock:
    def __init__(self, path):
        self.path = path
        raw = path.read_bytes()
        file_rows = raw.splitlines()
        self.n, count = map(int, file_rows[0].split())
        self.blocks = tuple(mask_of(map(int,row.split()),self.n) for row in file_rows[1:])
        assert len(self.blocks) == count == len(set(self.blocks))
        self.digest = sha256(raw).hexdigest()
        self.full = (1 << self.n)-1
        self.big = max(self.blocks, key=int.bit_count)
        self.others = tuple(indices(self.full ^ self.big))
        self.out_mask = self.full ^ self.big
        self.reverse = {v:i for i,v in enumerate(self.others)}
        self.rows = self.outside_rows()

    def outside_rows(self):
        rows = [0]*len(self.others)
        for block in self.blocks:
            for u in indices(block & self.out_mask):
                rows[self.reverse[u]] |= block
        assert all(row & (1 << x) for row,x in zip(rows,self.others,strict=True))
        return tuple(rows)

    @cached_property
    def exterior_types(self):
        types = defaultdict(list)
        for u, row in zip(self.others,self.rows,strict=True):
            types[row & self.big].append(u)
        return dict(types)

    @cached_property
    def interior_types(self):
        width = (self.n+7)//8
        profiles = [x.to_bytes(width,"little") for x in self.exterior_types]
        out = Counter()
        for u in indices(self.big):
            byte, bit = divmod(u,8)
            mask = sum(((row[byte] >> bit) & 1) << j for j,row in enumerate(profiles))
            out[mask] += 1
        return out

    def corrections(self):
        d = self.big.bit_count()
        # An outsider always has enough neighbors in the block that any
        # compatible pair meeting the exterior has a third such neighbor.
        minimum = min(x.bit_count() for x in self.exterior_types)
        assert 2*minimum-d > 0 and minimum > 1
        held = [i for i,b in enumerate(self.blocks) if not self.can_extend(b)]
        assert held == [self.blocks.index(self.big)]
        pairs = comb(self.interior_types[0],2) + sum(a*b for (u,a),(v,b) in combinations(self.interior_types.items(),2) if not u & v)
        candidate_pairs = comb(d,2) + sum((row & self.big).bit_count() for row in self.rows)
        candidate_pairs += sum((row & self.out_mask).bit_count()-1 for row in self.rows)//2
        with gzip.open(self.path.with_suffix(".parents.json.gz"),"rt") as handle:
            parents = json.load(handle)
        assert len(parents) == self.n and min(map(len,parents)) >= 2
        # Positive joint demand: every outsider lies in an unheld large
        # group; each block member lies in an unheld large group or a residual pair.
        return {"held_maximal_cliques":held, "candidate_pairs":candidate_pairs,
                "isolated":0, "offshoots":0, "residual_pairs":pairs,
                "minimum_outside_to_inside_candidate_degree":minimum,
                "minimum_parent_count":min(map(len,parents)), "next_births_minus_raw_maxima":pairs-1}

    def can_extend(self, clique):
        large = self.big
        for u in indices(clique & self.out_mask):
            large &= self.rows[self.reverse[u]]
        if large & ~clique:
            return True
        return any(not clique & (1 << u) and clique & row == clique for u,row in zip(self.others,self.rows,strict=True))

    def quotient(self):
        # Literal B vertices of one interface type are true candidate twins.
        # Include the entire class if any member is selected.
        v = [(None, sig) for sig in self.interior_types]
        repeats = list(self.interior_types.values()) + [1]*len(self.others)
        profile_ids = {u:j for j,group in enumerate(self.exterior_types.values()) for u in group}
        v.extend((u, 1 << profile_ids[u]) for u in self.others)
        pairs = []
        for i,(u,usig) in enumerate(v):
            for j in range(i+1,len(v)):
                w, wsig = v[j]
                if w is None:
                    continue
                conflict = not (usig & wsig) if u is None else not ((self.rows[self.reverse[u]] >> w) & 1)
                if conflict:
                    pairs.append((i,j))
        rows = [0]*len(v)
        for u,w in pairs:
            rows[u] |= 1 << w
            rows[w] |= 1 << u
        return tuple(rows), tuple(repeats), len(self.interior_types)


def exact_completed_outside(rows, n_inside):
    """Every maximal clique is determined by its outsider members.

    Enumerate their containing maximal outsider cliques. Within each such
    clique, enumerate the possible common interior neighborhoods and complete
    all compatible outsiders. The remaining maximality test is global.
    """
    full_b = (1 << n_inside)-1
    # Equal conflict rows are nonadjacent in the conflict graph. Selecting
    # one forces all those twins, preserving maximal sets by bijection.
    by_row = defaultdict(list)
    for u in range(n_inside,len(rows)):
        by_row[rows[u]].append(u)
    reps = tuple(group[0] for group in by_row.values())
    graph = nx.Graph()
    graph.add_nodes_from(range(len(reps)))
    graph.add_edges_from((i,j) for i,u in enumerate(reps) for j,v in enumerate(reps) if i<j and not ((rows[u] >> v) & 1))
    conflict = [sum(1 << y for y,v in enumerate(reps) if (rows[u] >> v) & 1) for u in reps]
    inside_neighbors = [full_b & ~rows[u] for u in reps]
    by_interface = defaultdict(int)
    for v, neighbors in enumerate(inside_neighbors):
        by_interface[neighbors] |= 1 << v

    valid, tested = set(), set()
    eligible_memo = {}
    profiles = Counter()
    maximal_outside_count = 0
    for outer in nx.find_cliques(graph):
        maximal_outside_count += 1
        outer_mask = sum(1 << u for u in outer)
        intersections = {full_b}
        for n_b in set(inside_neighbors[u] for u in outer):
            intersections.update(x & n_b for x in tuple(intersections))
        profiles[len(intersections)] += 1
        for t in intersections:
            eligible = eligible_memo.get(t)
            if eligible is None:
                eligible = 0
                for n_b, inside_type in by_interface.items():
                    if n_b & t == t:
                        eligible |= inside_type
                eligible_memo[t] = eligible
            s = outer_mask & eligible
            if s in tested:
                continue
            tested.add(s)
            still = eligible ^ s
            for u in indices(s):
                still &= ~conflict[u]
                if not still:
                    break
            if not still:
                valid.add(s)
    assert 0 in valid
    payload = "\n".join(hex(s) for s in sorted(valid)).encode()
    return {"raw_maximal_cliques":len(valid), "outsider_closed_profile_classes":len(reps),
            "maximal_cliques_of_outsider_quotient":maximal_outside_count,
            "candidate_intersections_by_outsider_clique":dict(profiles),
            "distinct_B_intersections":len(eligible_memo), "different_outsider_candidates_tested":len(tested),
            "outsider_sets_sha256":sha256(payload).hexdigest()}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("stage",type=Path)
    cli.add_argument("--output",type=Path,required=True)
    cli.add_argument("--count",action="store_true")
    args = cli.parse_args()
    stage = NearBlock(args.stage)
    rows, repeats, n_inside = stage.quotient()
    after = {"stage":stage.path.stem, "input_sha256":stage.digest, "live":stage.n, "block_count":len(stage.blocks),
             "dominant_block":stage.big.bit_count(), "outside_points":len(stage.others),
             "inside_types":n_inside, "outside_profiles":len(stage.exterior_types),
             "inside_type_multiplicities":dict(stage.interior_types),
             "sum_quotient_conflict_degrees":sum(row.bit_count() for row in rows),
             "literal_conflict_rows_on_quotient": [hex(r) for r in rows], "literal_names_per_quotient_node":repeats,
             "correction":stage.corrections()}
    if args.count:
        calculation = exact_completed_outside(rows,n_inside)
        after["exact_count"] = calculation | {"next_births":calculation["raw_maximal_cliques"] + after["correction"]["next_births_minus_raw_maxima"]}
    args.output.write_text(json.dumps(after,indent=2,sort_keys=True)+"\n")


if __name__ == "__main__":
    main()
