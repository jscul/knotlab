"""Rebuild ring preparations and test the old shared parity on their actual moves."""
import argparse
from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import resource
import time

from census_check import ROOT, basis, mask, null_basis, remainder
import naelib


def minimum_changes(rows, pinned=False):
    # Each shared distinction has two holders. For this calculation only, give
    # all loose distinctions one extra holder. Even parity there follows from
    # even parity at the real holders. A shortest even change through a given
    # distinction consists of it and a shortest return between its holders.
    owners = defaultdict(list)
    for i, row in enumerate(rows):
        for d in row:
            owners[d].append(i)
    pairs = {}
    for d, hs in owners.items():
        if len(hs) == 2:
            pairs[d] = hs
        elif not pinned:
            first, = hs
            pairs[d] = [first, len(rows)]
    adj = defaultdict(list)
    for d, (a, b) in pairs.items():
        adj[a].append((b, d))
        adj[b].append((a, d))
    moves = set()
    for marked, (a, b) in pairs.items():
        dist = {b: 0}
        todo = deque([b])
        while todo:
            k = todo.popleft()
            if k == a:
                break
            for other, d in adj[k]:
                if d != marked and other not in dist:
                    dist[other] = 1 + dist[k]
                    todo.append(other)

        def collect(k, word):
            if k == b:
                moves.add(word)
                return
            for other, d in adj[k]:
                if d != marked and dist.get(other) == dist[k] - 1:
                    collect(other, word | (1 << d))

        if a in dist:
            collect(a, 1 << marked)
    checks = list(map(mask, rows))
    singles = [1 << d for d, hs in owners.items() if len(hs) == 1]
    allowed = null_basis(checks + (singles if pinned else []), owners)
    return moves, allowed, singles


def inspect(rows, n, pinned):
    moves, allowed, singles = minimum_changes(rows, pinned)
    motion = basis(moves)
    old_shared = (1 << n) - 1
    par = lambda w: (w & old_shared).bit_count() % 2
    pinned_changes = null_basis(list(map(mask, rows)) + singles, set().union(*rows))
    return {
        "knots": len(rows), "distinctions": len(set().union(*rows)),
        "rank_allowed": len(allowed), "rank_moves": len(motion), "classes": 1 << (len(allowed) - len(motion)),
        "shortest_ties": len(moves), "move_lengths": dict(Counter(w.bit_count() for w in moves)),
        "old_shared_parity_nonconstant": any(map(par, allowed)),
        "old_shared_parity_on_some_move": any(map(par, moves)),
        "whole_old_ring_changes_class": bool(remainder(old_shared, motion)),
        "whole_old_ring_allowed": all(not (mask(row) & old_shared).bit_count() % 2 for row in rows),
        "loose_preserving_class_bits": len(basis(motion + pinned_changes)) - len(motion),
        "bits_readable_in_one_knot": max(len(basis(w & mask(row) for w in allowed)) -
                                         len(basis(w & mask(row) for w in motion)) for row in rows),
    }


def ring(n):
    return [(i, (i + 1) % n, n + 2*i, n + 2*i + 1) for i in range(n)]


def run(sizes, rounds):
    archive_file, = (ROOT / "artifacts/READS-HOLDERS-SOURCES-20261120-001A").glob("*/motion.json")
    archive = {(r["ring"], r["age"], r["loose_pinned"]): r
               for r in json.loads(archive_file.read_text())["rings"]}
    out = []
    for n in sizes:
        stage = naelib.J.S.from_junctions(ring(n))
        step = naelib.parity_rule(naelib.J.F.fewest)
        for age in range(rounds + 1):
            if age:
                rec = stage.step(step, None)
                if rec is None or not rec["new"]:
                    out.append({"n": n, "age": age, "no_round": True})
                    break
            rows = stage.bits_of
            for pinned in (False, True):
                result = inspect(rows, n, pinned)
                prior = archive.get((n, age, pinned))
                if prior:
                    for key, other in [("rank_allowed", "allowed_change_rank"), ("rank_moves", "shortest_rank"),
                                       ("classes", "shortest_fixed_weighting_dimension"), ("shortest_ties", "shortest_generators")]:
                        assert result[key] == prior[other], (n, age, pinned, key, result[key], prior[other])
                    result["matched_motion_archive"] = True
                out.append({"n": n, "age": age, "pinned": pinned, **result})
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", required=True)
    parser.add_argument("--rounds", type=int, required=True)
    options = parser.parse_args()
    tic = time.monotonic()
    results = run(options.sizes, options.rounds)
    print(json.dumps({"rows": results, "seconds_after_imports": time.monotonic() - tic,
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
