"""Check whether any lower bond on an omitted positive stage determines an upper reading."""

import argparse
from collections import Counter
from functools import cache
from itertools import combinations
import json
from time import perf_counter

import numpy as np

from omitted_search import HERE, bits, candidate_clauses, make_mask


def agreement(states, mask):
    fixed = states & mask
    return (fixed == 0) | (fixed == mask)


def upper(states, pair, both):
    (a, p), (b, q) = pair
    left, right = agreement(states, a) == p, agreement(states, b) == q
    return left & right if both else left | right


def pack(col):
    return int.from_bytes(np.packbits(col, bitorder="little").tobytes(), "little")


def cells(cols, mask):
    regions = [mask]
    for c in cols:
        regions = [region for old in regions for region in (old & ~c, old & c)]
    return regions


def replay(record, pilot=False):
    tick = perf_counter()
    supports = record["source_supports"]
    laws = tuple(map(make_mask, supports))
    n = record["distinctions"]
    assert set().union(*map(set, supports)) == set(range(n))
    raw = np.arange(1 << n, dtype=np.uint32)
    allowed = np.ones(len(raw), dtype=bool)
    for law in laws:
        allowed &= ~agreement(raw, law)
    states = raw[allowed]
    del raw
    # A sampled pair of opposite values proves non-determination. Every
    # calculation still unresolved by this finite set uses the full relation.
    sample = states[np.random.default_rng(739116).choice(len(states), min(4096, len(states)), replace=False)]
    sample_mask = (1 << len(sample)) - 1
    candidates, _ = candidate_clauses(supports)
    triples = {tuple(sorted(x >> 1 for x in s)) for s in candidates}
    unions = [(a | b | c, (a, b, c)) for a, b, c in sorted(triples)]

    @cache
    def sampled_column(mask):
        return pack(agreement(sample, mask))

    @cache
    def determined_at_one_source(mask):
        eq = agreement(states, mask).astype(np.uint8)
        for law in laws:
            places = tuple(bits(law))
            rawfix = np.zeros(len(states), dtype=np.uint16)
            for j, x in enumerate(places):
                rawfix |= ((states >> x) & 1).astype(np.uint16) << j
            counts = np.bincount(2 * rawfix + eq, minlength=2 ** (len(places) + 1))
            if not (counts[::2].astype(bool) & counts[1::2].astype(bool)).any():
                return True
        return False

    @cache
    def check_query(pair, both):
        u = upper(sample, pair, both)
        sample_u = pack(u)
        domain = pair[0][0] | pair[1][0]
        changes = {}
        for d in bits(domain):
            y = sample ^ (1 << d)
            pick = np.flatnonzero(allowed[y] & (u != upper(y, pair, both)))
            if len(pick):
                changes[d] = int(sample[pick[0]])
                continue
            y = states ^ (1 << d)
            pick = np.flatnonzero(allowed[y] & (upper(states, pair, both) != upper(y, pair, both)))
            if len(pick):
                changes[d] = int(states[pick[0]])
        necessary = make_mask(changes)
        cover = remaining = 0
        determining = []
        full_u = None
        for union, triple in unions:
            if union & necessary != necessary:
                continue
            cover += 1
            slices = cells((sampled_column(m) for m in triple), sample_mask)
            if any(region & sample_u and region & ~sample_u for region in slices):
                continue
            remaining += 1
            if full_u is None:
                full_u = upper(states, pair, both).astype(np.uint8)
            key = np.zeros(len(states), dtype=np.uint8)
            for m in triple:
                key = (key << 1) | agreement(states, m)
            counts = np.bincount(2 * key + full_u, minlength=16).reshape(8, 2)
            if (counts > 0).all(axis=1).any():
                continue
            words = np.flatnonzero(counts.sum(axis=1))
            if len(words) == 8 or not all(len(set(words & keep)) == 4 for keep in (3, 5, 6)):
                continue
            if not any(determined_at_one_source(m) for m in triple):
                determining.append([list(bits(m)) for m in triple])
        return {"pair": [[list(bits(m)), s] for m, s in pair], "both": bool(both),
                "changing_raw_bit_to_source_state": changes,
                "candidate_unions_covering_essential_distinctions": cover,
                "full_projection_tests_after_sample": remaining,
                "determining_stage_bonds": determining}

    readings = set()
    for pattern in record["patterns"]:
        pairs = tuple(tuple(sorted((make_mask(c), s) for c, s in pair)) for pair in pattern["signed_pairs"])
        for role in pattern["qualifying_roles"]:
            readings.update((pair, j == role["both_pair"]) for j, pair in enumerate(pairs))
    # This pair lies together in one of the certified lower triples, so that
    # triple necessarily determines either Boolean function of the pair.
    control_readings = [record["patterns"][0]["signed_pairs"][j][0] for j in (0, 1)]
    control = tuple(sorted((make_mask(c), s) for c, s in control_readings)), True
    query = sorted(readings)
    if pilot:
        query = query[:1]
    out = [check_query(*q) for q in query]
    planted = check_query(*control)
    assert planted["determining_stage_bonds"]
    return {"start": record["start"], "round": record["round"], "source_states": len(states),
            "candidate_signed_words": len(candidates), "unique_candidate_carrier_triples": len(triples),
            "different_upper_functions_by_recipe": len(readings), "functions_tested": len(query),
            "functions_determined_at_a_stage_bond": sum(bool(x["determining_stage_bonds"]) for x in out),
            "function_results": out, "positive_control": planted,
            "elapsed_seconds": round(perf_counter() - tick, 4)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    rows = [json.loads(s) for s in (HERE / "omitted_stages.jsonl").read_text().splitlines()]
    positives = sorted((r for r in rows if r["first_step"]), key=lambda r: r["start"])
    if args.pilot:
        positives = positives[:1]
    out = [replay(r, pilot=args.pilot) for r in positives]
    path = HERE / ("omitted_global_pilot.json" if args.pilot else "omitted_global.json")
    path.write_text(json.dumps(out, indent=2) + "\n")
    for r in out:
        print(r["start"], r["functions_tested"], r["functions_determined_at_a_stage_bond"], r["elapsed_seconds"])


if __name__ == "__main__":
    main()
