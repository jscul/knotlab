"""Literal parity controls and exhaustive classification of three agreement carriers."""

import argparse
import json
import resource
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

from parity_replay import HERE, bitmask, enumerate_stage, indices, law_sums, parity_advance, stages_for_start


def subspaces(width):
    """Each reduced binary basis once, with the highest occupied place as pivot."""
    for rank in range(width + 1):
        for pivots in combinations(range(width), rank):
            tails = [tuple(i for i in range(p) if i not in pivots) for p in pivots]
            choices = [[(1 << p) | bitmask(t[j] for j in range(len(t)) if s >> j & 1)
                        for s in range(1 << len(t))] for p, t in zip(pivots, tails, strict=True)]
            for rows in product(*choices):
                yield rows


def scan_image(shape):
    widths = [k - 1 for k in shape]
    groups = [((1 << k) - 1) << sum(widths[:i]) for i, k in enumerate(widths)]
    width = sum(widths)
    counts, shape_bonds, ranks_bonds, linked_duals = Counter(), Counter(), Counter(), Counter()
    failures, controls = [], {}
    for rows in subspaces(width):
        states = law_sums(rows)
        observed = {sum((not (s & g)) << (2 - i) for i, g in enumerate(groups)) for s in states}
        every_pair = all(len({w & (7 ^ (1 << j)) for w in observed}) == 4 for j in range(3))
        dual = {p for p in range(1 << width) if all((p & x).bit_count() % 2 == 0 for x in rows)}
        six = sorted(p for p in dual if all(p & g for g in groups))
        counts["all subspaces"] += 1
        counts["all agree missing"] += 7 not in observed
        counts["six-sum"] += bool(six)
        counts["six-sum and eight words"] += bool(six) and len(observed) == 8
        counts["every pair free"] += every_pair
        counts["every pair free and a missing word"] += every_pair and len(observed) < 8
        counts["every pair free, a missing word and no six-sum"] += every_pair and len(observed) < 8 and not six
        counts["a missing word, some restricted pair and no six-sum"] += not every_pair and len(observed) < 8 and not six
        if every_pair and len(observed) < 8:
            nmiss = 8-len(observed)
            shape_bonds[str(nmiss)] += 1
            ranks = tuple(len({p & g for p in states}).bit_length() - 1 for g in groups)
            ranks_bonds[f"{nmiss} missing; effective ranks " + "".join(map(str, ranks))] += 1
            linked_duals[str(len(six))] += 1
            if not six:
                failures.append(sorted(states))
        if six and len(observed) == 8 and "six-sum with eight words" not in controls:
            controls["six-sum with eight words"] = {"syndrome basis": rows, "six-sum characters": six,
                                                   "observed": sorted(observed)}
    return {"counts": dict(counts), "number missing on bonds": dict(shape_bonds),
            "missing by rank, ordered carriers": dict(ranks_bonds),
            "number of distinct six-sums on each bond": dict(linked_duals),
            "counterexamples to necessity": failures, "controls": controls}


class TruthTable:
    """One integer bit per assignment, retaining even sums only."""
    def __init__(self, supports):
        self.supports = tuple(map(tuple, supports))
        self.names = tuple(sorted({d for s in supports for d in s}))
        nassignments = 1 << len(self.names)
        self.all = (1 << nassignments) - 1
        bits = self.bits = {}
        for k, d in enumerate(self.names):
            block_length = 1 << k
            bits[d] = (self.all // ((1 << block_length) + 1)) << block_length
        self.laws = []
        for support in supports:
            odd = 0
            for d in support:
                odd ^= bits[d]
            self.laws.append(self.all ^ odd)
        self.stage = self.allowed(range(len(self.laws)))

    def allowed(self, rows):
        states = self.all
        for k in rows:
            states &= self.laws[k]
        return states

    @lru_cache(maxsize=1024)
    def yes(self, c):
        same = self.all
        for d in c[1:]:
            same &= self.all ^ (self.bits[c[0]] ^ self.bits[d])
        return same

    def words(self, carriers, allowed=None):
        states = self.stage if allowed is None else allowed
        parts = [states]
        for carrier in carriers:
            yes = self.yes(tuple(carrier))
            parts = [item for part in parts for item in (part & ~yes, part & yes)]
        return tuple(format(i, "03b") for i, part in enumerate(parts) if part)

    def read_at(self, c, rows, allowed):
        yes = self.yes(tuple(c))
        determined = []
        for k in rows:
            parts = [allowed]
            for d in self.supports[k]:
                parts = [v for p in parts for v in (p & self.bits[d], p & ~self.bits[d]) if v]
            if all(not (p & yes) or not (p & ~yes) for p in parts):
                determined.append(k)
        return determined


def is_pair_free(words):
    return all(len({w[:d] + w[d + 1:] for w in words}) == 4 for d in range(3))


def literal_candidates(supports):
    t = TruthTable(supports)
    cs = [c for s in (2, 3) for c in combinations(t.names, s)]
    disjoint, whole = 0, Counter()
    six_source = law_sums(tuple(map(bitmask, supports)))
    example = None
    for a, b, c in combinations(cs, 3):
        if len(set(a+b+c)) != len(a+b+c):
            continue
        disjoint += 1
        reads = tuple((a, b, c))
        if any(t.read_at(k, range(len(supports)), t.stage) for k in reads):
            continue
        whole["individually unread"] += 1
        words = t.words(reads)
        whole["pairwise free"] += is_pair_free(words)
        dual = [tuple(pair for pair in pairs) for pairs in product(*(combinations(k, 2) for k in reads))
                if bitmask(sum(pairs, ())) in six_source]
        whole["unread, eight words, a six-sum"] += bool(dual) and len(words) == 8
        if dual and len(words) == 8 and example is None:
            example = {"knots": supports, "carriers": reads, "six-sum pair choices": dual, "words": words}
        whole["bonds"] += is_pair_free(words) and len(words) < 8
        whole["bonds without a six-sum"] += is_pair_free(words) and len(words) < 8 and not dual
    return {"knots": supports, "disjoint triples": disjoint, "after unread test": whole,
            "six-sum insufficient example": example}


def verify_holder_witness(witness):
    t = TruthTable(witness["knots"])
    cs = tuple(tuple(c) for c in witness["carriers"])
    wins = []
    for record in witness["holder records in visit order"]:
        h = record["holders"]
        allowed = t.allowed(h)
        words = t.words(cs, allowed)
        full = t.words(cs)
        assert set(record["local missing"]) == {format(i, "03b") for i in range(8)} - set(words)
        assert set(record["stage missing"]) == {format(i, "03b") for i in range(8)} - set(full)
        assert is_pair_free(words) and len(words) != 8
        stage_readers = [t.read_at(c, range(len(t.laws)), t.stage) for c in cs]
        holder_readers = [t.read_at(c, h, allowed) for c in cs]
        assert bool(record["stage unread"]) == (not any(stage_readers)) and not any(holder_readers)
        deletions = {str(k): t.words(cs, t.allowed([j for j in h if k != j])) for k in h}
        assert all(set(v) > set(words) for v in deletions.values())
        wins.append({"holders": h, "local words": words, "stage words": full, "deletion words": deletions,
                     "readers on holders": holder_readers, "readers on stage": stage_readers})
    return {"knots": t.supports, "carriers": cs, "start index": witness["index"], "round": witness["round"],
            "first newborn knot": witness["first newborn knot"], "holder comparisons": wins}


def parity_agreement_cnf(supports, carriers):
    clauses = []

    def exclude(names, values):
        clauses.append(" ".join(("~" if bit else "") + name for name, bit in zip(names, values, strict=True)))

    for law in supports:
        names = [f"x{d}" for d in law]
        for values in product((0, 1), repeat=len(law)):
            if sum(values) % 2:
                exclude(names, values)
    for symbol, carrier in zip(("a", "b", "c"), carriers, strict=True):
        for values in product((0, 1), repeat=len(carrier)):
            bad_reading = int(len(set(values)) != 1)
            exclude([f"x{d}" for d in carrier] + [symbol], values + (bad_reading,))
    return "; ".join(clauses)


def fresh_law_witness():
    start, grown = stages_for_start(1)
    t = TruthTable(grown)
    src = t.allowed(range(len(start)))
    src_sums = law_sums(tuple(map(bitmask, start)))
    bonds, _, _ = enumerate_stage(grown, len(start))
    for carriers, (_, holders) in sorted(bonds.items(), key=lambda kv: (sum(map(len, kv[0])), kv[0])):
        if max(holders) < len(start):
            continue
        choices = [bitmask(sum(pairs, ())) for pairs in product(*(combinations(k, 2) for k in carriers))]
        if any(p in src_sums for p in choices):
            continue
        before = t.words(carriers, src)
        if len(before) < 8:
            continue
        after = t.words(carriers)
        assert len(after) < 8 and is_pair_free(after)
        return {"source": start, "grown": grown, "carriers": carriers, "local holders": holders,
                "holder CNF": parity_agreement_cnf([grown[h] for h in holders], carriers),
                "source words with new distinctions left free": before, "grown words": after,
                "six-distinction law sums among source laws": [],
                "six-distinction sums among holder laws":
                    [indices(p) for p in choices if p in law_sums(tuple(bitmask(grown[h]) for h in holders))]}
    raise RuntimeError("No witness")


def six_sum_with_all_words():
    source, grown = stages_for_start(1)
    holders = tuple(range(len(source) + 1))
    local = TruthTable(tuple(grown[k] for k in holders))
    full = TruthTable(grown)
    sums = law_sums(tuple(map(bitmask, local.supports)))
    carriers = list(combinations(local.names, 3))
    for triple in combinations(carriers, 3):
        if len(set(sum(triple, ()))) != 9:
            continue
        six = [p for p in sums if p.bit_count() == 6 and
               all((p & bitmask(c)).bit_count() == 2 for c in triple)]
        if not six or len(local.words(triple)) != 8 or len(full.words(triple)) != 8:
            continue
        if any(full.read_at(c, range(len(grown)), full.stage) for c in triple):
            continue
        return {"grown knots": grown, "holders": holders, "carriers": triple,
                "six-distinction sums on holders": [indices(p) for p in sorted(six)],
                "eight words on holders": local.words(triple), "eight words on stage": full.words(triple)}
    raise RuntimeError("No six-sum control")


def combined_sample(old, new):
    assert not set(old["starts"]) & set(new["starts"]) and len(old["starts"]) + len(new["starts"]) == 1000
    by_source_size = {}
    for population, record in (("original completed prefixes", old), ("original unfinished starts", new)):
        rows = [s for s in record["per-stage counts"] if s["round"] == 0]
        by_source_size[population] = {
            str(n): {"start count": sum(s["source knots"] == n for s in rows),
                     "had a bond": sum(s["source knots"] == n and bool(s["bonds"]) for s in rows)}
            for n in (3, 4, 5)}
    counts = Counter(old["counts"]) + Counter(new["counts"])
    tables = {k: Counter(old["tables"][k]) + Counter(new["tables"][k]) for k in old["tables"]}
    return {"counts": counts, "tables": tables, "source weighting": by_source_size}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    t0 = perf_counter()
    shapes = ((2,2,2), (2,2,3), (2,3,3), (3,3,3)) if not args.pilot else ((2,3,3),)
    sub = {"".join(map(str, s)): scan_image(s) for s in shapes}
    ring = ((0,1,3), (1,2,4), (2,0,5))
    grown = parity_advance(ring)
    assert grown is not None and parity_advance(grown) is None
    result = {"linear image classifications": sub, "ring": [literal_candidates(r) for r in (ring, grown)],
              "next ring round funded": False}
    result["three unread carriers with a six-sum and all eight words"] = six_sum_with_all_words()
    if not args.pilot:
        source = stages_for_start(1)[0]
        result["complete eight-distinction source literal control"] = literal_candidates(source)
        result["a grown parity relation needs a born law"] = fresh_law_witness()
        saved = json.loads((HERE / "parity_replay_results.json").read_text())
        extension = json.loads((HERE / "parity_extension.json").read_text())
        result["entire preselected sample"] = combined_sample(saved, extension)
        result["literal holder and shape witnesses"] = {
            name: verify_holder_witness(w) for name, w in saved["witnesses"].items()}
    result["wall seconds"] = round(perf_counter() - t0, 5)
    result["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({"subspaces": {s: r["counts"]["all subspaces"] for s, r in sub.items()},
                      "wall seconds": result["wall seconds"], "peak KiB": result["peak KiB"]}))


if __name__ == "__main__":
    main()
