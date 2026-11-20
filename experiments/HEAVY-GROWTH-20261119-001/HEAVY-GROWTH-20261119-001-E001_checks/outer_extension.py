"""Check whether the round-nine outermost groups of 14 have a wholly outer successor."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path

from mixed_turns import Stage, members
from outer_layer import radial_layers


def run(cache, evidence):
    data = evidence.read_bytes()
    record = json.loads(gzip.decompress(data) if evidence.suffix == ".gz" else data)
    families = record["new_outer_supports_if_increased"]
    stage = Stage(cache / "start-14-age08.txt")
    outer = radial_layers(stage, stage.n - 1)[-1]
    assert outer.bit_count() == record["old_layer_sizes"][-1]
    common_anchor, _ = Counter(v for row in families for v in row).most_common(1)[0]
    parts = [[frozenset(row) for row in families if (common_anchor in row) == contains]
             for contains in (True, False)]
    unions = [set.union(*map(set, part)) for part in parts]
    assert not unions[0].intersection(unions[1])
    records = []
    for part in parts:
        common = set.intersection(*map(set, part))
        assert len(common) <= 1
        sites = sorted(set.union(*map(set,part)) - common)
        full = (1 << len(part)) - 1
        mask_for_site = {v: sum(1 << i for i,g in enumerate(part) if v in g)
                         for v in sites}
        holding = {}
        rank = sorted(sites,key=lambda v:-mask_for_site[v].bit_count())
        bit = {v:1 << i for i,v in enumerate(rank)}
        for v in rank:
            for h in stage.at[v]:
                holding[h] = holding.get(h,0) | bit[v]
        local_near = []
        for v in rank:
            allowed = 0
            for h in stage.at[v]:
                allowed |= holding.get(h,0)
            local_near.append(allowed)
        named = defaultdict(list)
        for x in range(stage.n):
            if outer >> x & 1:
                continue
            if common and any(stage.hood(stage.at[v]) >> x & 1 for v in common):
                continue
            allowed=0
            for h in stage.at[x]:
                allowed |= holding.get(h,0)
            if allowed and len(named[allowed]) < 12:
                named[allowed].append(x)
        target = None
        clique_hitters = None
        if len(part) <= 8:
            import networkx as nx
            induced = nx.Graph()
            induced.add_nodes_from(sites)
            for i, v in enumerate(rank):
                induced.add_edges_from((v, rank[j]) for j in members(local_near[i]) if j > i)
            clique_hitters = [set(k) for k in nx.find_cliques(induced)
                              if all(set(k) & g for g in part)]
        for allowed, outside_sites in sorted(named.items(),key=lambda pair:-pair[0].bit_count()):
            def hit(avail, missing, chosen):
                if not missing:
                    return chosen
                total=0
                for i in members(avail):
                    total |= mask_for_site[rank[i]]
                if missing & ~total:
                    return None
                first = (missing & -missing).bit_length()-1
                opts=[i for i in members(avail) if rank[i] in part[first]]
                opts.sort(key=lambda i:-(mask_for_site[rank[i]] & missing).bit_count())
                for i in opts:
                    got=hit(avail & local_near[i] & ~(1<<i),
                            missing & ~mask_for_site[rank[i]],chosen+[rank[i]])
                    if got is not None:
                        return got
                return None
            chosen=hit(allowed,full,[])
            if chosen is None:
                continue
            for x in outside_sites:
                group=set([x]+chosen)
                poss=stage.full
                for v in group:
                    poss &= stage.hood(stage.at[v])
                    poss &= ~(1<<v)
                while poss:
                    v=(poss & -poss).bit_length()-1
                    group.add(v)
                    poss &= stage.hood(stage.at[v]) & ~(1<<v)
                am=set(stage.at[x])
                for v in group:
                    am.intersection_update(stage.at[v])
                if len(group) >= 3 and not am:
                    assert not common.intersection(group) and all(g & group for g in part)
                    ck=stage.full
                    for v in group:
                        ck &= stage.hood(stage.at[v])
                    assert ck == sum(1<<v for v in group)
                    target=dict(old_parent_roster=sorted(group),outside_old_parent=x,
                                touching_old_parents=chosen,old_parent_count=len(group))
                    break
            if target is not None:
                break
        # Within each class all groups are mutual candidates, checked even
        # when the full intersection is empty. Distinct classes use disjoint sites.
        if not common:
            assert all(g & h for g in part for h in part)
        unique = False
        if target is None and clique_hitters is not None and not common:
            # The six maximal candidate subsets meeting all six are the six
            # stars themselves. Every one needs all five sites to hit all six
            # (each other star shares its own distinct site). Each star was
            # checked globally maximal in the preceding stage. Therefore only
            # these six real children can meet the entire family.
            unique = (set(map(frozenset,clique_hitters)) == set(part) and
                      all(any(g & h == {v} for h in part) for g in part for v in g))
            assert unique
        records.append(dict(count=len(part),common_old_parents=sorted(common),
                            exterior_child=target,
                            exact_hitting_maxima=None if clique_hitters is None else
                                sorted(sorted(g) for g in clique_hitters),
                            one_unextendible_unheld_group=unique))
    assert records[0]["exterior_child"] and records[1]["one_unextendible_unheld_group"]
    return dict(start=14,age=9,classes=records,
                exact_radius_by_age={"8":8,"9":9,"10":10,"11":10},
                pure_grandchildren=1,pure_great_grandchildren=0)


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    for name in ("cache","evidence","output"):
        p.add_argument(name,type=Path)
    args=p.parse_args()
    result=run(args.cache,args.evidence)
    args.output.write_text(json.dumps(result,separators=(",",":"))+"\n")
    print([(r["count"],r["common_old_parents"],None if r["exterior_child"] is None else
            r["exterior_child"]["old_parent_count"]) for r in result["classes"]])
