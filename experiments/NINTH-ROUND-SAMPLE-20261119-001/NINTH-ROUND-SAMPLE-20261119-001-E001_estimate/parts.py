"""Exact block, adjacency, twin and correction counts for a sampled stage."""
from collections import Counter
import json
from pathlib import Path
import sys


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def read_stage(path):
    with path.open() as stream:
        n, b = map(int, next(stream).split())
        blocks = [list(map(int, line.split())) for line in stream]
    assert len(blocks) == b
    masks = [sum(1 << i for i in block) for block in blocks]
    adjacency = [0] * n
    for block, blockmask in zip(blocks, masks):
        for v in block:
            adjacency[v] |= blockmask
    for v in range(n):
        adjacency[v] &= ~(1 << v)
    return n, blocks, masks, adjacency


def connected_parts(available, nbr, complement=False):
    parts = []
    while available:
        frontier = available & -available
        available ^= frontier
        part = 0
        while frontier:
            part |= frontier
            hit = 0
            for v in members(frontier):
                hit |= ((~nbr[v]) if complement else nbr[v]) & available
                if hit == available:
                    break
            available ^= hit
            frontier = hit
        parts.append(part)
    return parts


def main():
    stage = Path(sys.argv[1])
    age = int(stage.stem.removeprefix("age"))
    n, blocks, masks, adj = read_stage(stage)
    allpts = (1 << n) - 1
    held = []
    for block, mask in zip(blocks, masks):
        common = allpts ^ mask
        for v in block:
            common &= adj[v]
            if not common:
                held.append(block)
                break
    false_twins=Counter(adj)
    true_twins=Counter(word | 1 << v for v,word in enumerate(adj))
    edges=sum(w.bit_count() for w in adj)//2
    parents=json.loads((stage.parent/f"parents{age}.json").read_text())
    isolated=sum(w==0 for w in adj)
    # Every candidate pair without an unheld extension lies in at least one held maximal block.
    # For p>=2 only isolation can leave one unused fresh distinction. For p=1 allow two.
    possible_offshoots=isolated+2*sum(len(p)==1 for p in parents)
    cover=[0]*n
    for b in held:
        mask=sum(1<<v for v in b)
        for v in b:
            cover[v] |= mask
    covered_pairs=sum((xs & ~(1<<v)).bit_count() for v,xs in enumerate(cover))//2
    summary=dict(age=age,junctions=n,blocks=len(blocks),candidate_pairs=edges,isolated=isolated,
                 held_maximal_blocks=len(held),held_sizes=sorted(map(len,held)),
                 residual_pairs_upper=covered_pairs,offshoots_upper=possible_offshoots,
                 true_twin_class_sizes=dict(Counter(true_twins.values())),false_twin_class_sizes=dict(Counter(false_twins.values())),
                 joined_component_sizes=sorted((p.bit_count() for p in connected_parts(allpts,adj,True)),reverse=True),
                 component_sizes=sorted((p.bit_count() for p in connected_parts(allpts,adj)),reverse=True))
    here=Path(__file__).resolve().parent
    out=here.parents[2]/"artifacts"/here.parent.name/here.name/f"parts{age}.json"
    out.write_text(json.dumps(summary,indent=1)+"\n")
    print({k:(str(v)[:210] if isinstance(v,(list,dict)) else v) for k,v in summary.items()},flush=True)


if __name__ == "__main__":
    main()

