"""Census for DISTANCE-INFO-20261117-001A-E001.

Relations of not-all-equal bases on n labelled distinctions: every one for
n = 4, 5, 6; for n = 7, those of random knot sets (1 to 12 distinct knots, the
count uniform, knots uniform; seeds sha256 DI:7:<shard>; 8 shards of 50,000
draws).  Readings (a) unsigned pairwise bond-distance table, (b) signed table,
(c) bond set, (c-s) bond set with signed ties, (c') every bond with its missing
joint states, (d) prime implicates (control, n <= 5 all and 5,000 at n = 6).
For each reading: distinct readings, colliding groups, relations in them, and
up to 10 smallest collisions, each tagged isomorphic or not.
python3 -B census.py      (writes artifacts/.../census.json)
"""
import hashlib
import json
import os
import random
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tables as T  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "DISTANCE-INFO-20261117-001A", "DISTANCE-INFO-20261117-001A-E001_tables")
READINGS = ("a", "b", "c", "c-s", "c'")


def read_all(args):
    n, rels, with_bonds = args
    out = []
    for r in rels:
        row = {"rel": r, "a": T.bond_table(n, r), "b": T.bond_table(n, r, signed=True)}
        if with_bonds:
            row["c"], row["c-s"], row["c'"] = T.bond_signatures(n, r)
        out.append(row)
    return out


def bonds_for(args):
    n, rels = args
    return [(r,) + T.bond_signatures(n, r) for r in rels]


def pi_for(args):
    n, rels = args
    return [(r, T.prime_implicates(n, r)) for r in rels]


def sample7(shard):
    rng = random.Random(int.from_bytes(hashlib.sha256(f"DI:7:{shard}".encode()).digest()[:8], "little"))
    masks = [T.knot_mask(7, k) for k in T.all_knots(7)]
    full = (1 << 128) - 1
    out = set()
    for _ in range(50000):
        r = full
        for k in rng.sample(range(35), rng.randint(1, 12)):
            r &= masks[k]
        if r:
            out.add(r)
    return out


def summarize(n, rows, key, iso_check=True):
    groups = {}
    for row in rows:
        groups.setdefault(row[key], []).append(row["rel"])
    coll = sorted((v for v in groups.values() if len(v) > 1),
                  key=lambda v: (min(bin(r).count("1") for r in v), len(v)))
    ex = []
    for v in coll[:10]:
        a, b = v[0], v[1]
        ex.append({"size": len(v), "allowed": [bin(r).count("1") for r in v[:4]], "hex": [hex(r) for r in v[:4]],
                   "first_two_isomorphic": T.isomorphic(n, a, b) if iso_check and n <= 7 else None})
    return {"distinct": len(groups), "colliding_groups": len(coll),
            "relations_in_collisions": sum(len(v) for v in coll), "examples": ex}


def main():
    res = {}
    with Pool(4) as pool:
        for n in (4, 5, 6, 7):
            if n < 7:
                rels = sorted(T.distinct_relations(n))
            else:
                rels = sorted(set().union(*pool.map(sample7, range(8))))
            full_bonds = n <= 6
            rows = [x for part in pool.map(read_all, [(n, rels[i::16], full_bonds) for i in range(16)]) for x in part]
            if not full_bonds:  # bond readings only inside (a)-collisions, which they refine
                groups = {}
                for row in rows:
                    groups.setdefault(row["a"], []).append(row)
                inside = [row for g in groups.values() if len(g) > 1 for row in g]
                got = {r: (c, cs, cp) for part in pool.map(bonds_for, [(n, [x["rel"] for x in inside[i::16]]) for i in range(16)])
                       for (r, c, cs, cp) in part}
                for row in rows:
                    if row["rel"] in got:
                        row["c"], row["c-s"], row["c'"] = got[row["rel"]]
                    else:
                        row["c"] = row["c-s"] = row["c'"] = ("unique table", row["rel"])
            rec = {"relations": len(rels), "sampled": n == 7}
            for key in READINGS:
                rec[key] = summarize(n, rows, key)
            pis = rels if n <= 5 else random.Random(6).sample(rels, 5000)
            pi_rows = [{"rel": r, "d": p} for part in pool.map(pi_for, [(n, pis[i::16]) for i in range(16)]) for r, p in part]
            rec["d"] = summarize(n, pi_rows, "d")
            rec["d"]["checked"] = len(pis)
            res[n] = rec
            print(n, rec["relations"], {k: (rec[k]["distinct"], rec[k]["colliding_groups"]) for k in READINGS + ("d",)}, flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "census.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
