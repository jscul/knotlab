"""Lift signed patterns of actual parent sets to certified incompatible pairs."""

import argparse
import hashlib
import json
import random
from pathlib import Path


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def adjacency(blocks, n):
    rows = [0] * n
    for block in blocks:
        mask = sum(1 << v for v in block)
        for v in block:
            rows[v] |= mask
    return rows


def read_blocks(path):
    with path.open() as f:
        n, k = map(int, next(f).split())
        blocks = [list(map(int, line.split())) for line in f]
    assert len(blocks) == k
    return n, blocks


def lift(bins, next_rows):
    size = len(bins)
    out = []
    for i in range(size // 2):
        a, b = bins[i], bins[size - 1 - i]
        if a.bit_count() > b.bit_count():
            a, b = b, a
        if not b:
            continue
        for v in indices(a):
            disjoint = b & ~next_rows[v]
            if disjoint:
                out.append([v, (disjoint & -disjoint).bit_length() - 1])
                break
    return out


def search(folder, trials, seed):
    old_n, old_blocks = read_blocks(folder / "age7.txt")
    n, blocks = read_blocks(folder / "age8.txt")
    parent_sets = json.loads((folder / "parents8.json").read_text())
    parent_ids = sorted({x for row in parent_sets for x in row})
    assert len(parent_ids) == old_n and len(parent_sets) == n
    position = {x: i for i, x in enumerate(parent_ids)}
    owners = [[] for _ in parent_ids]
    for v, row in enumerate(parent_sets):
        for p in row:
            owners[position[p]].append(v)
    sets = [sum(1 << v for v in group) for group in owners]
    old_adj = adjacency(old_blocks, old_n)
    new_adj = adjacency(blocks, n)
    rng = random.Random(seed)
    best = []
    best_old = []
    for trial in range(trials):
        available = (1 << old_n) - 1
        bins = [(1 << n) - 1]
        old_pairs = []
        while available:
            vertices = list(indices(available))
            poss = [(u, available & ~old_adj[u] & ~(1 << u)) for u in vertices]
            poss = [(u, missing) for u, missing in poss if missing]
            if not poss:
                break
            choices = []
            for u, missing in rng.sample(poss, min(len(poss), 22)):
                partners = list(indices(missing))
                for v in rng.sample(partners, min(len(partners), 7)):
                    rest = available & old_adj[u] & old_adj[v]
                    choices.append((rest.bit_count(), rng.random(), u, v, rest))
            choices.sort(reverse=True)
            _, _, u, v, available = rng.choice(choices[:1 + trial % 8])
            old_pairs.append([u, v])
            bins = [cell & sets[j] for cell in bins for j in (u, v)]
            if len(bins) > len(best) * 2:
                witness = lift(bins, new_adj)
                if len(witness) > len(best):
                    best, best_old = witness, old_pairs.copy()
    verify(n, blocks, best)
    return {"old_n": old_n, "n": n, "old_parent_index_pairs": best_old,
            "pairs": best, "k": len(best), "trials": trials, "seed": seed,
            "stage_sha256": hashlib.sha256((folder / "age8.txt").read_bytes()).hexdigest()}


def verify(n, blocks, pairs):
    holders = [set() for _ in range(n)]
    for i, b in enumerate(blocks):
        for x in b:
            holders[x].add(i)
    flat = [x for pair in pairs for x in pair]
    assert len(flat) == len(set(flat))
    for i, x in enumerate(flat):
        for j, y in enumerate(flat[:i]):
            assert bool(holders[x] & holders[y]) == (i // 2 != j // 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--trials", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20261119094)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = search(args.folder, args.trials, args.seed)
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    print({k: v for k, v in result.items() if k != "pairs"})
