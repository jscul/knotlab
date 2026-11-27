"""Compare saved rows with independently seeded starts, first ranks and parity witnesses."""
from collections import Counter
from itertools import combinations
import argparse
import json
import random
import resource
import time
from pathlib import Path

import networkx as nx

from certificates import parity_certificate, step, verify_transport
from redraw import canonical_input, first_ranks, grow, pieces, tree_plus


HERE = Path(__file__).resolve().parent


def piece_kind(knots, families, shares, n):
    neighbours = [set() for _ in range(n)]
    for a,b in shares:
        neighbours[a].add(b)
        neighbours[b].add(a)
    raw = {frozenset(nb.intersection(knots)) for nb in neighbours}
    cells = {frozenset(f) for f in families if len(f) >= 3}
    blocks = [g for g in raw if len(g)>=2 and not any(g < h for h in raw)
              and not any(g<=h for h in cells)]
    rank = 1-len(knots)+sum(len(f)-1 for f in [*blocks,*cells])
    filled = sum(max(0,len(f&g)-1) for f in cells for g in blocks)
    return rank, rank-filled


def check_repeat_candidates(rank, widths):
    candidates = [(i+1, j+1) for j in range(1,len(widths))
                  for i in range(j) if widths[i] == widths[j]]
    if not candidates:
        return []
    needed = {r for pair in candidates for r in pair}
    graphs = {}
    for r in range(1, max(needed)+1):
        assert len(rank) == widths[r-1]
        if r in needed:
            graph = nx.Graph()
            for i, parents in enumerate(rank):
                graph.add_node(("birth",i), role="birth")
                for x in parents:
                    graph.add_node(("parent",x), role="parent")
                    graph.add_edge(("birth",i),("parent",x))
            graphs[r] = graph
        if r < max(needed):
            rank = step(rank)
    for a, b in candidates:
        assert not nx.is_isomorphic(graphs[a], graphs[b],
                                    node_match=lambda x,y: x["role"]==y["role"])
    return candidates


def rebuild(archive, limit):
    saved = [json.loads(line) for line in archive.read_text().splitlines()]
    meta = saved.pop()
    if limit:
        saved = saved[:limit]
    wanted = {row["draw"]:row for row in saved}
    rng = random.Random(meta["seed"])
    sampler = grow if meta["weighting"] == "grow" else tree_plus
    n = meta["knots"]
    results = []
    distinct = set()
    for draw in range(max(wanted)+1):
        sizes, shares = sampler(n, rng)
        if draw not in wanted:
            continue
        source = wanted[draw]
        key = canonical_input(sizes, shares)
        assert key not in distinct
        distinct.add(key)
        loose, groups, offshoots, accepted = first_ranks(sizes, shares)
        assert accepted
        inputs = list(pieces(loose, groups, offshoots))
        assert len(inputs)==len(source["pieces"])
        result = {"draw_zero_based":draw,"pieces":[]}
        for (knots,rank1), record in zip(inputs,source["pieces"]):
            rank = list(map(frozenset,rank1))
            raw, adjusted = piece_kind(knots,rank1,shares,n)
            info = {"stored_class":record["class"], "raw_cycle_rank":raw, "adjusted_cycle_rank":adjusted,
                    "rank_1_parents":list(map(sorted,rank)), "parity_rank":1,
                    "certificate":parity_certificate(rank)}
            if record["class"] == "subset finish":
                history=[]
                for r in range(1,record["rank"]+1):
                    history.append(len(rank))
                    if r<record["rank"]:
                        rank=step(rank)
                m=len(rank)
                shared = set.intersection(*(set(f) for f in rank))
                assert m == record["m"] and shared
                total = sum(history)+(1<<m)-m-1
                assert total==record["births"]
                info.update({"rank_widths":history, "common_parents":sorted(shared),
                             "remaining_births":(1<<m)-m-1,"total_births":total,"knots":knots,
                             "shared_distinctions":shares,"knot_sizes":sizes})
            if record["class"]=="unresolved":
                history = record["births by rank"]
                info["repeat_candidates_rejected"] = check_repeat_candidates(rank, history)
                for r in range(1,min(4,len(history))+1):
                    assert history[r-1]==len(rank)
                    if (not info["certificate"]["independent_marks"]) and r>1 and len(rank)<=36:
                        cert = parity_certificate(rank)
                        if cert["independent_marks"]:
                            info.update({"parity_rank":r,"certificate":cert,"witness_parents":list(map(sorted,rank))})
                    if r<min(4,len(history)):
                        rank=step(rank)
            if info["certificate"]["independent_marks"]:
                witness = info.get("witness_parents", info["rank_1_parents"])
                info["transferred_odd_walk"] = verify_transport(list(map(frozenset,witness)), info["certificate"])
            result["pieces"].append(info)
        results.append(result)
    return {"weighting":meta["weighting"],"knots":n,"starts":results}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
    started=time.monotonic()
    rows=[rebuild(p,1 if args.pilot else None) for p in sorted((HERE.parent/"runs").glob("*.jsonl"))]
    counts=Counter()
    for group in rows:
        for r in group["starts"]:
            counts["starts"]+=1
            if any(p["certificate"]["independent_marks"] for p in r["pieces"]):
                counts["proved_nonterminating"]+=1
            for p in r["pieces"]:
                counts[p["stored_class"]+"_pieces"]+=1
                if p["stored_class"]=="unresolved":
                    counts[f'cycle_rank_{p["adjusted_cycle_rank"]}']+=1
    print(json.dumps({"totals":counts, "seconds":time.monotonic()-started, "records":rows},separators=(",",":")))


if __name__ == "__main__":
    main()
