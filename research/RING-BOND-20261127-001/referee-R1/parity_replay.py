"""Rebuild parity agreement bonds by exact ranks and finite differences of counts."""

import argparse
import json
import random
import resource
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
from math import comb
from pathlib import Path
from time import perf_counter

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/NAE-LAYER-20261127-001/referee-R1"))
from growth_rule import advance, supports_of


def bitmask(items):
    return sum(1 << i for i in items)


def indices(bits):
    return tuple(i for i in range(bits.bit_length()) if bits >> i & 1)


@lru_cache(maxsize=8192)
def basis(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p not in pivots:
                pivots[p] = x
                break
            x ^= pivots[p]
    return tuple(sorted(pivots.values(), reverse=True))


def reduce_form(value, rows):
    for vector in rows:
        if value & (1 << (vector.bit_length() - 1)):
            value ^= vector
    return value


def law_sums(rows):
    out = [0]
    for row in rows:
        out += [v ^ row for v in out]
    return set(out)


def parity_advance(source):
    """Use the ordinary parent and demand rule, then evaluate parity implication."""
    grown = advance(source)
    if grown.status != "funded":
        return None
    span = basis(tuple(map(bitmask, source)))
    result = list(source)
    next_id = 1 + max(d for row in source for d in row)
    for birth in grown.births:
        forced = reduce_form(bitmask(birth.inputs), span) == 0
        needed = birth.demand if forced else max(birth.demand, 3 - len(birth.inputs), 1)
        result.append(birth.inputs + tuple(range(next_id, next_id + needed)))
        next_id += needed
    return tuple(result)


@lru_cache(maxsize=1)
def starts():
    return json.loads((ROOT / "research/FORBID-EDITS-20261126-001/starts.json").read_text())


def stages_for_start(index):
    source = supports_of(starts()[index])
    grown = parity_advance(source)
    return (source, grown) if grown is not None else (source,)


def pairings(six):
    if not six:
        yield ()
        return
    for j in range(1, len(six)):
        rem = six[1:j] + six[j + 1:]
        for rest in pairings(rem):
            yield ((six[0], six[j]),) + rest


@lru_cache(maxsize=32)
def extra_choices(size):
    """Extra indices for three disjoint carriers, zero denotes no extra."""
    return np.array([a for a in product(range(size + 1), repeat=3)
                     if len({x for x in a if x}) == sum(x != 0 for x in a)], dtype=np.intp)


class Carriers:
    def __init__(self, n):
        self.n = n
        self.tuples = tuple(row for size in (2, 3) for row in combinations(range(n), size))
        self.masks = np.array([bitmask(t) for t in self.tuples], dtype=np.int32)
        self.left = np.array([t[0] for t in self.tuples])
        self.middle = np.array([t[1] for t in self.tuples])
        self.right = np.array([t[-1] for t in self.tuples])
        self.by_mask = np.full(1 << n, -1, dtype=np.int32)
        self.by_mask[self.masks] = np.arange(len(self.tuples))

    def candidates(self, six_masks):
        pieces = []
        for s in sorted(six_masks):
            six = indices(s)
            extras = [0] + [1 << k for k in range(self.n) if not (s >> k & 1)]
            extra = np.asarray(extras, dtype=np.int32)[extra_choices(len(extras) - 1)]
            for pairs in pairings(six):
                fixed = np.array([bitmask(p) for p in pairs], dtype=np.int32)
                chosen = self.by_mask[extra | fixed]
                chosen.sort(axis=1)
                pieces.append(chosen)
        if not pieces:
            return np.empty((0, 3), dtype=np.int32)
        all_choices = np.concatenate(pieces)
        count = len(self.tuples)
        keys = all_choices[:, 0].astype(np.int64) * count**2 + all_choices[:, 1] * count + all_choices[:, 2]
        keys = np.unique(keys)
        return np.column_stack((keys // count**2, keys // count % count, keys % count)).astype(np.int32)

    def differences(self, units):
        a = units[self.left] ^ units[self.middle]
        b = units[self.left] ^ units[self.right]
        return np.column_stack((np.zeros_like(a), a, b, a ^ b))


@lru_cache(maxsize=24)
def carriers(n):
    return Carriers(n)


def qr_units(names, rows):
    rr = basis(tuple(rows))
    return np.array([reduce_form(1 << x, rr) for x in names], dtype=np.int64)


def unread_flags(family, names, rows):
    visible = np.zeros(len(family.tuples), dtype=bool)
    for row in rows:
        units = qr_units(names, rows + tuple(1 << x for x in indices(row)))
        visible |= (units[family.left] == units[family.middle]) & (units[family.left] == units[family.right])
    return ~visible


def fourier_weights(diff, cand):
    """Return 64 times the uniform mass of each agreement intersection."""
    a, b, c = (diff[cand[:, i], 1:] for i in range(3))
    az, bz, cz = ((side == 0).sum(axis=1, dtype=np.int16) for side in (a, b, c))

    def intersect(left, right, lz, rz):
        total = 1 + lz + rz
        for j in range(3):
            total += (left[:, j, None] == right).sum(axis=1, dtype=np.int16)
        return total

    ab, ac, bc = (intersect(a, b, az, bz), intersect(a, c, az, cz), intersect(b, c, bz, cz))
    # Exactly zero, one or two nonzero coefficient blocks account for this many.
    abc = ab + ac + bc - az - bz - cz - 2
    for ai in range(3):
        for bi in range(3):
            combined = a[:, ai] ^ b[:, bi]
            abc += (combined[:, None] == c).sum(axis=1, dtype=np.int16)
    return 16 * (az + 1), 16 * (bz + 1), 16 * (cz + 1), 4 * ab, 4 * ac, 4 * bc, abc


def missing_words(diff, cand):
    a, b, c, ab, ac, bc, abc = fourier_weights(diff, cand)
    cells = (64-a-b-c+ab+ac+bc-abc, c-ac-bc+abc, b-ab-bc+abc, bc-abc,
             a-ab-ac+abc, ac-abc, ab-abc, abc)
    mask = np.zeros(len(cand), dtype=np.uint8)
    for i, cell in enumerate(cells):
        mask |= (cell == 0).astype(np.uint8) << i
    return mask


def is_bond_missing(mask):
    return bool(mask) and all((mask & (1 << w | 1 << (w ^ (1 << j)))) !=
                              (1 << w | 1 << (w ^ (1 << j)))
                              for w in range(8) for j in range(3))


BOND_MASK = np.array([is_bond_missing(m) for m in range(256)], dtype=bool)


def connected_holders(rows):
    for size in range(1, min(len(rows), 4) + 1):
        for ix in combinations(range(len(rows)), size):
            active = rows[ix[0]]
            previous = -1
            while previous != active:
                previous = active
                for k in ix:
                    if rows[k] & active:
                        active |= rows[k]
            if all(rows[k] & active for k in ix):
                yield ix


def disjoint_count(n):
    total = 0
    for sizes in ((2, 2, 2), (2, 2, 3), (2, 3, 3), (3, 3, 3)):
        if sum(sizes) <= n:
            count = 1
            left = n
            for size in sizes:
                count *= comb(left, size)
                left -= size
            total += count // (6 if sizes[0] == sizes[2] else 2)
    return total


def to_local(mask, names):
    return bitmask(i for i, d in enumerate(names) if mask >> d & 1)


def holder_rows(stage_rows, h, observations):
    rows = tuple(stage_rows[i] for i in h)
    names = tuple(sorted(set(x for r in rows for x in indices(r))))
    observations["connected holder sets"] += 1
    observations["disjoint carrier triples on holder sets"] += disjoint_count(len(names))
    if len(names) < 6 or len(basis(rows)) < len(rows):
        return
    sums = {to_local(v, names) for v in law_sums(rows) if v.bit_count() == 6}
    if not sums:
        return
    f = carriers(len(names))
    candidates = f.candidates(sums)
    observations["carrier triples with a six-sum on independent holders"] += len(candidates)
    mask = np.all(unread_flags(f, names, rows)[candidates], axis=1)
    candidates = candidates[mask]
    observations["six-sum and individually unread on holders"] += len(candidates)
    if not len(candidates):
        return
    words = missing_words(f.differences(qr_units(names, rows)), candidates)
    observations["six-sum, unread, full triple on holders"] += int(np.count_nonzero(words == 0))
    keep = BOND_MASK[words]
    candidates, words = candidates[keep], words[keep]
    observations["local bonds before deletions"] += len(candidates)
    for j in range(len(rows)):
        if not len(candidates):
            return
        smaller = rows[:j] + rows[j + 1:]
        other = missing_words(f.differences(qr_units(names, smaller)), candidates)
        keep = words != other
        candidates, words = candidates[keep], words[keep]
    if not len(candidates):
        return
    stage_words = missing_words(f.differences(qr_units(names, stage_rows)), candidates)
    stage_unread = np.all(unread_flags(f, names, stage_rows)[candidates], axis=1)
    named = [tuple(names[p] for p in t) for t in f.tuples]
    for triple, local_mask, full_mask, unread in zip(candidates.tolist(), words.tolist(),
                                                      stage_words.tolist(), stage_unread.tolist(), strict=True):
        yield tuple(named[p] for p in triple), local_mask, full_mask, unread


def enumerate_stage(supports, born=0, evidence=None):
    """Return {three carriers: (missing word mask, chosen holders)}, raw counts, diagnostics."""
    rows = tuple(map(bitmask, supports))
    all_h = defaultdict(list)
    obs = Counter()
    for h in connected_holders(rows):
        for key, local, whole, unread in holder_rows(rows, h, obs):
            all_h[key].append((h, local, whole, unread))
    bonds = {}
    summary = {"distinctions": len(set(x for r in supports for x in r)), "knots": len(rows)}
    shape, sizes, nmissing, share = (Counter() for _ in range(4))
    with_birth = 0
    rr = basis(rows)

    @lru_cache(maxsize=None)
    def effective_rank(carrier):
        diffs = tuple(reduce_form(1 << carrier[0] | 1 << x, rr) for x in carrier[1:])
        return len(basis(diffs))

    @lru_cache(maxsize=None)
    def holder_loose(h):
        odd = 0
        for idx in h:
            odd ^= rows[idx]
        return odd.bit_count()

    def witness(name, chosen, entries):
        if evidence is not None and name not in evidence:
            evidence[name] = {
                "knots": supports, "first newborn knot": born if born else None, "carriers": chosen,
                "holder records in visit order": [
                    {"holders": hs, "local missing": [format(i, "03b") for i in indices(lo)],
                     "stage missing": [format(i, "03b") for i in indices(st)], "stage unread": u}
                    for hs, lo, st, u in entries]}

    for key, entries in all_h.items():
        h, local, whole, unread = entries[0]
        good = [g for g, l, w, u in entries if l == w and u]
        if len(entries) > 1:
            obs["carrier triples with multiple locally essential holder sets"] += 1
            obs["carrier triples with tied shortest locally essential holder sets"] += sum(len(s[0]) == len(h) for s in entries) > 1
        fits = local == whole and unread
        if good:
            obs["carrier triples accepted by at least one holder set"] += 1
            if born:
                flags = {max(g) >= born for g in good if len(g) == len(good[0])}
                obs["accepted triples with tied shortest holders differing in birth membership"] += len(flags) > 1
                if len(flags) > 1:
                    witness("shortest holders disagree on a birth", key, entries)
                obs["stage bonds having any qualifying holder set containing a birth"] += any(max(g) >= born for g in good)
        if not fits:
            obs["lost by first-shortest choice"] += bool(good)
            if good:
                obs["lost despite qualifying holder of same smallest size"] += len(h) == len(good[0])
                witness("stage bond lost by first-shortest choice", key, entries)
            continue
        bonds[key] = (local, h)
        sizes[str(len(h))] += 1
        missing = local.bit_count()
        nmissing[str(missing)] += 1
        shape_name = "".join(str(len(c)) for c in key)
        shape[shape_name + " missing " + str(missing)] += 1
        share.update(key)
        with_birth += bool(born and max(h) >= born)
        obs["all agree missing"] += bool(local >> 7)
        if shape_name in ("223", "233", "333") and missing in (2, 4):
            if (shape_name, missing) in (("223", 4), ("233", 2), ("333", 4)):
                ranks = "".join(str(effective_rank(c)) for c in key)
                obs[f"{shape_name} missing {missing}, effective ranks {ranks}"] += 1
                witness(f"{shape_name} missing {missing}, effective ranks {ranks}", key, entries)
        if len(h) == len(rows):
            loose = holder_loose(h)
            obs[f"entire-stage essential with {loose} loose distinctions"] += 1
            if loose != 6:
                witness("entire-stage essential with other than six loose distinctions", key, entries)
    summary.update({"bonds": len(bonds), "by shape and missing count": dict(shape),
                    "all agree missing": obs["all agree missing"], "six-sum fails": 0,
                    "with a birth among the holders": with_birth, "missing counts": dict(nmissing),
                    "holder sizes": dict(sizes), "readings in two or more bonds": sum(v > 1 for v in share.values()),
                    "found on the holders but not a bond of the stage": len(all_h) - len(bonds)})
    return bonds, summary, dict(obs)


def archived():
    raw = {}
    shards = {}
    for p in sorted((HERE.parent / "out").glob("census_parity_[0-9].jsonl")):
        ids = []
        for line in p.read_text().splitlines():
            row = json.loads(line)
            i = int(row["start"].split()[1])
            if i in raw:
                raise ValueError(f"Duplicate archived start {i}")
            raw[i] = row
            ids.append(i)
        shards[p.stem[-1]] = ids
    return raw, shards


def example_matches(example, bonds):
    key = tuple(tuple(c) for c, label in example["readings"] if label == "=")
    missing = bitmask(int(w, 2) for w in example["missing"])
    return (bonds.get(key) == (missing, tuple(example["holders"])) and
            example["stage missing"] == example["missing"] and example["same relation on the stage"] and
            not example["read at a knot of the stage"])


def run(which, selection):
    raw, shards = archived()
    all_ids = list(range(len(starts())))
    pilot_ten = set(random.Random(1).sample(all_ids, 10))
    held_out = sorted(random.Random(20261127).sample([i for i in all_ids if i not in pilot_ten], 1000))
    ok_shards = {i: ids == held_out[int(i)::8][:len(ids)] for i, ids in shards.items()}
    available = {"completed": sorted(raw), "unrun": sorted(set(held_out) - set(raw)), "all": held_out}
    ids = list(which if which is not None else available[selection])
    counts, agg, stages, timings, source_sizes = Counter(), defaultdict(Counter), [], [], Counter()
    special = {}
    bad, examples = [], []
    for i in ids:
        t = perf_counter()
        stage_list = stages_for_start(i)
        counts["starts"] += 1
        counts["funded"] += len(stage_list) == 2
        source_sizes[len(stage_list[0])] += 1
        if i in raw and (len(stage_list) == 1) != isinstance(raw[i]["round 1"], str):
            bad.append([i, "funding"])
        for rd, supports in enumerate(stage_list):
            before = set(special)
            bonds, summary, obs = enumerate_stage(supports, len(stage_list[0]) if rd else 0, special)
            for name in set(special) - before:
                special[name].update({"index": i, "round": rd})
            if i in raw:
                archived_stage = raw[i][f"round {rd}"]
                diffs = {k: [v, archived_stage[k]] for k, v in summary.items() if v != archived_stage[k]}
                if diffs:
                    bad.append([i, rd, diffs])
                for e in archived_stage["examples"]:
                    if not example_matches(e, bonds):
                        examples.append([i, rd, e])
                counts["archived examples checked"] += len(archived_stage["examples"])
                counts["raw stages checked"] += 1
            counts["rebuilt stages"] += 1
            counts[f"round {rd} bonds"] += len(bonds)
            counts[f"round {rd} has a bond"] += bool(bonds)
            counts[f"round {rd} existential holder bonds"] += obs.get("carrier triples accepted by at least one holder set", 0)
            counts[f"round {rd} has an existential holder bond"] += bool(obs.get("carrier triples accepted by at least one holder set"))
            counts[f"round {rd} all qualifying holders with a birth"] += obs.get("stage bonds having any qualifying holder set containing a birth", 0)
            counts[f"round {rd} has a birth among any qualifying holders"] += bool(obs.get("stage bonds having any qualifying holder set containing a birth"))
            counts[f"round {rd} with a birth"] += summary["with a birth among the holders"]
            counts[f"round {rd} has a birth among holders"] += bool(summary["with a birth among the holders"])
            counts[f"round {rd} has shared readings"] += bool(summary["readings in two or more bonds"])
            for k in ("by shape and missing count", "missing counts", "holder sizes"):
                agg[k].update(summary[k])
            agg["opportunities and holder distinctions"].update(obs)
            stages.append({"index": i, "round": rd, "source knots": len(stage_list[0]), "bonds": len(bonds),
                           "existential holder bonds": obs.get("carrier triples accepted by at least one holder set", 0),
                           "lost by first-shortest choice": obs.get("lost by first-shortest choice", 0)})
        timings.append([i, round(perf_counter() - t, 5)])
    return {"starts": ids, "complete shard lengths": {k: len(v) for k, v in shards.items()},
            "each completed shard is its ordered prefix": ok_shards,
            "archived start range": [min(raw), max(raw)], "replayed source knot counts": source_sizes,
            "requested 1000 source knot counts": dict(Counter(len(starts()[i][2]) for i in held_out)),
            "counts": counts, "tables": agg, "stage summary differences": bad,
            "archived example differences": examples, "witnesses": special, "per-stage counts": stages, "seconds per start": timings}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--indices", type=int, nargs="+", help="archive indices for timed exact-configuration pilots")
    p.add_argument("--selection", choices=("completed", "unrun", "all"), default="completed")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    start = perf_counter()
    output = run(args.indices, args.selection)
    output["wall seconds"] = round(perf_counter() - start, 5)
    output["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.out.write_text(json.dumps(output, indent=1) + "\n")
    print(json.dumps({k: output[k] for k in ("counts", "stage summary differences",
                                             "archived example differences", "wall seconds", "peak KiB")}))


if __name__ == "__main__":
    main()
