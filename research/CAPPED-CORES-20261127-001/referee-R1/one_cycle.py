"""Count finite connected sets up to translation for the seven-knot draw with a five-knot cycle and two leaves."""
from itertools import combinations
from math import comb
import argparse
import json
import time

from certificates import parity_certificate, step

OWNER_PAIRS = [(0,1),(2,4),(0,3),(4,5),(0,5),(0,6),(2,6)]
SIZES = [6,4,4,4,4,6,6]
# One period in the unrolling of the common-neighbour blocks.
PERIOD = (0,2,5,6,4)


def count(size):
    answer = {1:2, 2:1}.get(size, 0)  # Sets using only knots 1 and 3 in one block.
    for first in range(5):
        for length in range(1, size+1):
            # Each decorated block has consecutive positions 2,3 modulo 5.
            blocks = (first+length-1-2)//5 - (first-1-3)//5
            answer += comb(2*blocks, size-length)
    return answer


def verify(rounds):
    neighbours = [set() for _ in SIZES]
    for a,b in OWNER_PAIRS:
        neighbours[a].add(b)
        neighbours[b].add(a)
    rank = sorted(step(neighbours), key=sorted)
    assert all(len(g)==2 for g in rank)
    assert all(len(neighbours[i]) + sum(i in g for g in rank)==s for i,s in enumerate(SIZES))
    assert all(len(a&b)<=1 for a,b in combinations(neighbours,2))
    marks = parity_certificate(rank)
    assert marks["independent_marks"] == 1
    widths = [len(SIZES)]
    for r in range(1,rounds+1):
        widths.append(len(rank))
        if r < rounds:
            rank = step(rank)
    assert widths == [count(s) for s in range(1,len(widths)+1)]
    predicted = [count(s) for s in range(1, 51)]
    for size in range(11,51):
        assert count(size)==count(size-5)+2*count(size-6)+count(size-7)
    return {"owner_pairs":OWNER_PAIRS, "sizes":SIZES, "rank1":sorted(map(sorted,step(neighbours))),
            "checked_core_widths":widths, "cluster_counts_sizes_1_to_50":predicted,
            "marks_on_sorted_rank1":marks, "rank1_numbering":list(map(sorted,sorted(step(neighbours),key=sorted)))}


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("rounds",type=int)
    args=parser.parse_args()
    start=time.monotonic()
    result=verify(args.rounds)
    result["seconds"]=time.monotonic()-start
    print(json.dumps(result,indent=2))
