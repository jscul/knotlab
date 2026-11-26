"""Check the existing reduced-block identification and first-round lookups on actual births."""
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
from hashlib import sha256
from itertools import combinations, islice
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
HELD = {"uniform": "held_out", "stratified": "grown_stratified", "handbuilt": "grown_handbuilt",
        "grow7": "grown_grow7", "horizon": "grown_horizon"}
FIT = {"nae": [("one to four", RESEARCH / "LOOK-ALIKE-20261126-001/phase1_grown.jsonl.gz"),
               ("five", RESEARCH / "SETTLE-BOUND-20261126-001/grown_g5_nae.jsonl.gz")],
       "parity": [("five", RESEARCH / "SETTLE-BOUND-20261126-001/grown_g5_par.jsonl.gz")]}
EARLIER = {law: [("earlier thousand", RESEARCH / f"SETTLE-BOUND-20261126-001/grown_g6_{key}.jsonl.gz"),
                 ("earlier two thousand", RESEARCH / f"LAST-MERGE-20261126-001/grown_fresh_{law}.jsonl.gz")]
           for law, key in [("nae", "nae"), ("parity", "par")]}


def read(path, limit):
    with gzip.open(path, "rb") as f:
        yield from map(json.loads, islice(f, limit))


def reduced_class(stars):
    """Test all four premises of Corollary 2 on maximal live-neighbour sets."""
    stars = list(map(frozenset, stars))
    copies = Counter(d for knot in stars for d in knot)
    loose = [sum(copies[d] == 1 for d in knot) for knot in stars]
    live = {i for i, count in enumerate(loose) if count}
    raw = [frozenset(i for i in live if i != j and stars[j] & stars[i]) for j in range(len(stars))]
    blocks = [b for b in set(raw) if len(b) >= 2 and not any(b < q for q in raw)]
    # For a linear family a cycle of three blocks has three distinct intersections.
    if sum(loose) < 2 or any(len(a & b) >= 2 for a, b in combinations(blocks, 2)):
        return False
    if any((a & b) and (b & c) and (a & c) and not (a & b & c)
           for a, b, c in combinations(blocks, 3)):
        return False
    # Under the two premises above all round-one groups are pairs within blocks.
    return all(sum(len(b) - 1 for b in blocks if i in b) <= loose[i] for i in live)


@lru_cache(maxsize=10000)
def intern(blob):
    return sha256(blob).digest()


def row_key(row, reading):
    # The combined view is determined by sig1: each described birth includes its sig0.
    return intern(json.dumps(sorted(row[reading]), separators=(",", ":")).encode())


class PrefixLookup:
    def __init__(self):
        self.by_first = defaultdict(set)
        self.by_total = defaultdict(set)

    def add(self, keys, n):
        self.by_first[keys[0]].add(keys)
        self.by_total[n].add(keys)

    def matches(self, keys, n):
        # An archive ending at its cap gives no answer about later rounds.
        def score(pool):
            eligible = {x[:len(keys)] for x in pool if len(x) >= len(keys)}
            if not eligible:
                return "unseen first round or shorter source"
            if keys not in eligible:
                return "first round seen, continuation different"
            if len(eligible) == 1:
                return "unique in source and correct"
            return "correct among multiple continuations"
        return score(self.by_first.get(keys[0], ())), score(self.by_total.get(n, ()))


def signature(x, reading):
    seq = tuple(row_key(row, reading) for row in x["rows"])
    # A closure is evidence for zero births on subsequent rounds; a cap is not.
    if x["end"].startswith("closes"):
        seq += (row_key({reading: []}, reading),) * max(24 - len(seq), 0)
    return seq


def run(limit):
    accepted = {}
    predicted_counts = {}
    for p in read(STUDY / "predictions.jsonl.gz", None):
        if p["read"] == "predicted":
            key = p["set"], p["knot law"], p["index"]
            accepted[key] = p["stratum"]
            predicted_counts[key] = tuple(r["n"] for r in p["rows"])
    out = {"known_identification": {}, "simple_lookups": {}}
    for law in ("nae", "parity"):
        dbs = {}
        for label, paths in [("fitting", FIT[law]), ("earlier_six_knot", EARLIER[law])]:
            tables = {s: PrefixLookup() for s in ("sig0", "sig1")}
            for _, path in paths:
                for x in read(path, limit):
                    if x["rows"]:
                        for s, table in tables.items():
                            table.add(signature(x, s), x["rows"][0]["n"])
            dbs[label] = tables
        for pop, filename in HELD.items():
            if law == "parity" and pop == "horizon":
                continue
            proof, checks, coarse = defaultdict(Counter), defaultdict(Counter), Counter()
            # Find actual pairs with the very same first-round description but different later readings.
            first_groups = defaultdict(list)
            for x in read(STUDY / f"{filename}_{law}.jsonl.gz", limit):
                stratum = accepted.get((pop, law, x["index"]))
                if stratum is None:
                    continue
                actual_n = [r["n"] for r in x["rows"]]
                guess_n = predicted_counts[pop, law, x["index"]]
                if x["end"].startswith("closes"):
                    actual_n += [0] * (len(guess_n) - len(actual_n))
                first_n = next((i for i,(a,b) in enumerate(zip(actual_n,guess_n), 1) if a != b), None)
                coarse["agree" if first_n is None else f"first differs at {first_n}"] += 1
                covered = reduced_class(x["stars"])
                proof[stratum]["Corollary 2" if covered else "outside Corollary 2"] += 1
                for s in ("sig0", "sig1"):
                    keys = signature(x, s)
                    n = x["rows"][0]["n"]
                    for label, tables in dbs.items():
                        typed, total = tables[s].matches(keys, n)
                        checks[f"{s}: {label}, first-round kinds"][typed] += 1
                        checks[f"{s}: {label}, first-round total"][total] += 1
                    if s == "sig1":
                        first_groups[keys[0]].append((x["index"], keys))
            witnesses = []
            pair_count = 0
            for bucket in first_groups.values():
                for (i, a), (j, b) in combinations(bucket, 2):
                    first = next((t for t, (v,w) in enumerate(zip(a,b), start=1) if v != w), None)
                    if first is not None:
                        pair_count += 1
                        if len(witnesses) < 3:
                            witnesses.append({"start_indices": [i, j], "first_later_difference": first})
            label = f"{pop} {law}"
            out["known_identification"][label] = proof
            out["simple_lookups"][label] = {"lookups": checks, "birth totals alone": coarse, "pairs_same_first_parent_view_different_later": pair_count,
                                           "example_pairs": witnesses, "distinct_first_parent_views": len(first_groups)}
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    start = time.monotonic()
    data = run(30 if args.pilot else None)
    data["elapsed_seconds"] = round(time.monotonic() - start, 3)
    file = HERE / ("alternatives_pilot.json" if args.pilot else "alternatives.json")
    file.write_text(json.dumps(data, indent=2) + "\n")
    print(file.name, data["elapsed_seconds"])
