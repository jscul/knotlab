"""Check which renamings were counted and check where a whole cycle gives a class read."""
import argparse
from collections import Counter
from itertools import permutations
import json
import time

from census_check import ROOT, archived, basis, input_rows, grow, mask, naelib
from ring_check import minimum_changes


def symmetries(record):
    n, pairs, loose = record
    old = {(a, b): m for a, b, m in pairs}
    holder_count = 0
    for perm in permutations(range(n)):
        if all(loose[i] == loose[perm[i]] for i in range(n)) and all(
            old.get(tuple(sorted((perm[a], perm[b])))) == m for a, b, m in pairs
        ):
            holder_count += 1
    identical = any(m > 1 for _, _, m in pairs) or any(m > 1 for m in loose)
    return holder_count, identical


def simple_cycles(rows):
    owners = {}
    for i, row in enumerate(rows):
        for name in row:
            owners.setdefault(name, []).append(i)
    neighbours = [[] for _ in rows]
    for name, hs in owners.items():
        if len(hs) == 2:
            a, b = hs
            neighbours[a].append((b, name))
            neighbours[b].append((a, name))
    cycles = set()
    for start in range(len(rows)):
        def visit(current, seen, word):
            for nxt, name in neighbours[current]:
                bit = 1 << name
                if nxt < start or word & bit:
                    continue
                if nxt == start and word:
                    cycles.add(word | bit)
                elif nxt not in seen:
                    visit(nxt, seen | {nxt}, word | bit)
        visit(start, {start}, 0)
    return cycles


def inspect_cycle(record):
    old = input_rows(record)
    stage, _ = grow(old, "parity", "ordinary", naelib)
    moves, allowed, _ = minimum_changes(stage)
    cycles = simple_cycles(stage)
    labels = [z for z in cycles if all(not (z & w).bit_count() % 2 for w in moves) and
              any((z & w).bit_count() % 2 for w in allowed)]
    local_bits = [len(basis(w & mask(row) for w in allowed)) - len(basis(w & mask(row) for w in moves))
                  for row in stage]
    n, pairs, _ = record
    simple_ring = len(pairs) == n and all(m == 1 for a, b, m in pairs) and all(
        sum(k in (a, b) for a, b, m in pairs) == 2 for k in range(n))
    return {"holdings": old, "grown_holdings": stage, "cycles": len(cycles),
            "source_has_simple_ring_meetings": simple_ring, "most_local_bits": max(local_bits),
            "cycle_labels": [[i for i in range(z.bit_length()) if z >> i & 1] for z in sorted(labels)]}


def run(pilot):
    records = json.loads((ROOT / "research/FORBID-EDITS-20261126-001/starts.json").read_text())
    rows = archived("census_canonical")
    indices = [i for i in rows if rows[i]["start"]["loose free"]["classes"] > 1]
    if pilot:
        indices = indices[:12]
    counts = Counter()
    examples = {}
    for i in indices:
        n, pairs, loose = records[i]
        hold, indistinguishable = symmetries(records[i])
        counters = {"class_bearing": True, "only_identity_on_holders": hold == 1,
                    "only_identity_including_distinctions": hold == 1 and not indistinguishable,
                    "double_meeting_no_simple_cycle_length_three_or_more": len(pairs) == n-1 and any(m == 2 for a,b,m in pairs),
                    "simple_cycle_or_double": len(pairs) >= n or any(m == 2 for a,b,m in pairs)}
        for key, value in counters.items():
            counts[key] += value
            if value:
                examples.setdefault(key, [i, records[i]])
    # Select on the archive, then reconstruct both full-cycle and one-knot reads.
    indices = [i for i, row in rows.items()
               if isinstance(row["after one round"], dict) and
               row["after one round"]["loose free"].get("classes", 0) > 1]
    if pilot:
        indices = indices[:12]
    stage_counts = Counter()
    witnesses = {}
    for i in indices:
        found = inspect_cycle(records[i])
        typ = (found["most_local_bits"] > 0, bool(found["cycle_labels"]), found["source_has_simple_ring_meetings"])
        key = str(typ)
        stage_counts[key] += 1
        witnesses.setdefault(key, {"index": i, **found})
    return {"symmetry_and_cycles": counts, "examples": examples,
            "grown_key": ["a local class bit", "a class bit on a simple cycle of shared distinctions",
                          "source meetings form a simple ring"],
            "grown_counts": stage_counts, "grown_examples": witnesses}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    tic = time.monotonic()
    out = run(args.pilot)
    out["seconds_after_imports"] = time.monotonic() - tic
    print(json.dumps(out))
