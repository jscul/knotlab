"""Independent, size-by-size recount of the connected pair of four-knot rings."""
import argparse
import itertools
import json
import resource
import time
from collections import defaultdict
from pathlib import Path

from frozen_recount_core import grow
from periodic import kernel, mask, pivots, restrictions
from witness import check_projection

HERE = Path(__file__).resolve().parent


def make_start():
    # Two four-knot rings. One further knot meets opposite members of the first
    # and one member of the second. The additional knot has no loose distinction.
    meetings = [(base+j, base+(j+1)%4) for base in (0,4) for j in range(4)]
    meetings.extend([(8,0),(8,2),(8,4)])
    rows = [[] for _ in range(9)]
    for x, (i,j) in enumerate(meetings):
        rows[i].append(x)
        rows[j].append(x)
    x = len(meetings)
    for r, count in zip(rows, (2,2,2,2,3,2,2,2,0)):
        r.extend(range(x,x+count))
        x += count
    return rows


def by_size(rows):
    width = max(x for r in rows for x in r)+1
    cols = [mask(i for i,r in enumerate(rows) if x in r) for x in range(width)]
    z = kernel(rows,width)
    mobile = set(x for x in range(width) if any(s >> x & 1 for s in z))
    reached = set()
    moves = set()
    by_width = {}
    for size in range(1,width+1):
        # An allowed support has equal syndromes on its two halves. Split each
        # sorted support in the middle to visit it exactly once.
        left = defaultdict(list)
        for prefix in itertools.combinations(range(width),size//2):
            syndrome = 0
            for x in prefix:
                syndrome ^= cols[x]
            left[syndrome].append(prefix)
        first_this_size = set()
        count = 0
        for suffix in itertools.combinations(range(width),size-size//2):
            syndrome = 0
            for x in suffix:
                syndrome ^= cols[x]
            for prefix in left.get(syndrome, ()):
                if prefix and prefix[-1] >= suffix[0]:
                    continue
                named = prefix + suffix
                count += 1
                if any(x not in reached for x in named):
                    moves.add(mask(named))
                    first_this_size.update(named)
        by_width[size] = {"allowed":count,"newly_reached":len(first_this_size - reached)}
        reached.update(first_this_size)
        if reached == mobile:
            break
    return moves,z,by_width


def verify(rows):
    moves, z, sizes = by_size(rows)
    proj = [restrictions(z,r) for r in rows]
    move_proj = [restrictions(moves,r) for r in rows]
    f, g = mask(range(4)), mask(range(4,8))
    def values(word):
        return ((word & f).bit_count()%2) + 2*((word & g).bit_count()%2)
    return {"supports":rows,"allowed_rank":len(z),"move_rank":len(pivots(moves)),
            "distinct_moves":len(moves),"allowed_changes_by_size":sizes,
            "class_count":2**(len(z)-len(pivots(moves))),
            "ring_pair_values_rank":len(pivots(values(s) for s in z)),
            "ring_pair_values_move_rank":len(pivots(values(s) for s in moves)),
            "single_knot_read_ranks":[a-h for a,h in zip(proj,move_proj)],
            "all_supports_pass_canonical_check": all(check_projection(rows))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    pilot = parser.parse_args().pilot
    resource.setrlimit(resource.RLIMIT_AS, (1<<30,1<<30))
    t = time.monotonic()
    rows = make_start()
    built = grow(rows)
    assert built.status == "funded"
    result = {"source":verify(rows),"grown":verify(built.stage),
              "births_with_parents_in_both_rings": sum(bool(set(b.parents)&set(range(4))) and
                                                        bool(set(b.parents)&set(range(4,8))) for b in built.births)}
    if not pilot:
        # Supplement the size search with an independently numbered replay.
        n = 1+max(x for r in rows for x in r)
        renamed = [tuple(n-1-x for x in r) for r in rows]
        again = grow(renamed)
        mm, zz, _ = by_size(again.stage)
        assert len(zz)-len(pivots(mm)) == 2
        assert all(restrictions(zz,r)==restrictions(mm,r) for r in again.stage)
        result["reversed_names_and_replayed_round"] = True
    result["seconds"] = round(time.monotonic()-t,5)
    (HERE/("joint_pilot.json" if pilot else "joint_check.json")).write_text(json.dumps(result,indent=2)+"\n")
    print([(result[k]["class_count"],result[k]["ring_pair_values_move_rank"]) for k in ("source","grown")])
