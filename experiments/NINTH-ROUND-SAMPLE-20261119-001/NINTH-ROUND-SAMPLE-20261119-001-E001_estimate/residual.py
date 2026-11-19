"""Probability sample of candidate pairs using an exact test for a covering group."""
from collections import Counter
import json
from pathlib import Path
import random
import sys
from scipy.stats import beta
from parts import read_stage, members


def covering_test(n, blocks, masks, adjacency):
    owner = [0]*n
    for h, b in enumerate(blocks):
        for v in b:
            owner[v] |= 1<<h

    def extends(candidates, held):
        if not held:
            return True
        candidates_left = candidates
        shortest = None
        for h in members(held):
            outside = candidates & ~masks[h]
            if not outside:
                return False
            candidates_left &= ~masks[h]
            if shortest is None or outside.bit_count() < shortest.bit_count():
                shortest = outside
        if candidates_left:
            return True
        return any(extends(candidates & adjacency[z], held & owner[z]) for z in members(shortest))

    def covered(u,v):
        return extends(adjacency[u] & adjacency[v], owner[u] & owner[v])
    return covered


def main():
    age = int(sys.argv[1])
    sample_size = int(sys.argv[2])
    base = Path(sys.argv[3])
    n, blocks, masks, adjacency = read_stage(base / f"age{age}.txt")
    covered = covering_test(n, blocks, masks, adjacency)
    total = sum(x.bit_count() for x in adjacency)//2
    if sample_size:
        rng = random.Random(f"20261119094-residual-{age}")
        hits = 0
        for _ in range(sample_size):
            while True:
                u,v=rng.randrange(n),rng.randrange(n)
                if u!=v and (adjacency[u]>>v)&1:
                    break
            hits += not covered(u,v)
        # Exact two-sided binomial interval conditional on this one fixed stage.
        alpha = .001
        lo = float(beta.ppf(alpha/2, hits, sample_size-hits+1)) if hits else 0.
        hi = float(beta.ppf(1-alpha/2, hits+1, sample_size-hits)) if hits<sample_size else 1.
        info=dict(age=age,weighting="Independent uniform candidate pairs of the specified stage; with replacement",
                  samples=sample_size,hits=hits,candidate_pairs=total,estimated_residual=total*hits/sample_size,
                  confidence=.999,interval=[int(total*lo),int(total*hi)+1])
    else:
        residual=sum(not covered(u,v) for u in range(n) for v in members(adjacency[u]) if u<v)
        info=dict(age=age,candidate_pairs=total,exact_residual=residual)
    print(info,flush=True)
    here=Path(__file__).resolve().parent
    out=here.parents[2]/"artifacts"/here.parent.name/here.name/f"residual{age}.json"
    out.write_text(json.dumps(info,indent=2)+"\n")

if __name__ == "__main__":
    main()

