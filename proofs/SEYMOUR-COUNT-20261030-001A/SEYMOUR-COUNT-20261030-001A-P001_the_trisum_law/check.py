"""Checks for SEYMOUR-COUNT-20261030-001A-P001 (the trisum law).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 leaning splits of prisms (4- to 10-prism) and the truncated octahedron in both orientations; seen from c3 the split is swapped;
    reversing the orientation swaps it
  2 the trisum law A(T) = rho1 rho2 rho3 - alpha1 alpha2 alpha3 - beta1 beta2 beta3 on all 44 trisums of prisms (11 triples x 4
    orientations) and on 20 random trisums including truncated octahedra
  3 the support lemma: inside a trisum every piece's boundary tensor has 8 nonzero entries, 2 values per case, matching its split
  4 the weights lemma on nested trisums, by exact colouring counts of the host piece
  5 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, python-sat, numpy; about fifteen seconds)"""
import collections, hashlib, itertools, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"),
          P("THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles"),
          P("THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"),
          P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import trisum_lib as TL  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 splits
LIB = {}
for k in (2, 3, 4, 5):
    for f in (False, True):
        LIB[(f"{2 * k}-prism", f)] = TL.prism_piece(k, f)
for f in (False, True):
    LIB[("truncated octahedron", f)] = TL.truncated_octahedron_piece(f)
SPLIT = {key: TL.leaning(g) for key, g in LIB.items()}
d1, ok1 = {}, True
for key, g in LIB.items():
    other = TL.leaning(g, side='c3')
    d1[str(key)] = {"split (c1 removed)": SPLIT[key], "split (c3 removed)": other, "amplitude": sum(SPLIT[key])}
    ok1 &= other == SPLIT[key][::-1]
for k in (2, 3, 4, 5):
    a, b = SPLIT[(f"{2 * k}-prism", False)]
    ok1 &= (a, b) == (k - 1, 1) and SPLIT[(f"{2 * k}-prism", True)] == (1, k - 1)
ok1 &= SPLIT[("truncated octahedron", False)] == (8, 8)
report("1 splits: prisms (k - 1, 1), truncated octahedron (8, 8); the c3 view and the reversed orientation swap them", ok1, d1)

# ---------------------------------------------------------------- 2 the trisum law
d2, ok2 = {"prism triples": {}, "random": collections.Counter()}, True
for ks in [(2, 2, 2), (2, 2, 3), (2, 3, 3), (3, 3, 3), (2, 2, 4), (2, 3, 4), (3, 3, 4), (2, 4, 4), (4, 4, 4), (2, 2, 5), (2, 3, 5)]:
    row = {}
    for fl in [(False, False, False), (False, False, True), (False, True, False), (False, True, True)]:
        keys = [(f"{2 * k}-prism", f) for k, f in zip(ks, fl)]
        a = TL.amplitude(TL.trisum_of([LIB[key] for key in keys]))
        pred = TL.law([SPLIT[key] for key in keys])
        row["".join("1" if f else "0" for f in fl)] = (a, pred)
        ok2 &= a == pred
    d2["prism triples"][str(ks)] = row
rng = random.Random(20261030)
keys = list(LIB)
for _ in range(20):
    trip = [rng.choice(keys) for _ in range(3)]
    if sum(int(key[0].split('-')[0]) if key[0][0].isdigit() else 24 for key in trip) > 60:
        continue
    a = TL.amplitude(TL.trisum_of([LIB[key] for key in trip]))
    good = a == TL.law([SPLIT[key] for key in trip])
    d2["random"]["holds" if good else "fails"] += 1
    ok2 &= good
d2["random"] = dict(d2["random"])
report("2 the trisum law on all prism triples and orientations and on random trisums", ok2, d2)

# ---------------------------------------------------------------- 3 the support lemma
d3, ok3 = {}, True
for ks, fl in [((2, 2, 2), (False, False, False)), ((2, 3, 3), (False, False, True)), ((3, 3, 4), (False, True, False)), ((2, 3, 4), (True, False, False))]:
    keys = [(f"{2 * k}-prism", f) for k, f in zip(ks, fl)]
    G = TL.trisum_of([LIB[key] for key in keys])
    tens = TL.boundary_tensors(G)
    rows = {}
    for t, key in zip("xyz", keys):
        vals = sorted(tens[t].values())
        rows[t] = {"nonzero entries": len(tens[t]), "values": vals, "split": SPLIT[key]}
        ok3 &= len(tens[t]) == 8 and vals == sorted(list(SPLIT[key]) * 4)
    d3[str((ks, fl))] = rows
report("3 support lemma: 8 nonzero boundary entries per piece, carrying exactly its split", ok3, d3)

# ---------------------------------------------------------------- 4 the weights lemma on nested trisums
d4, ok4 = {}, True
for kA, kQ, kR, fl in [(2, 2, 2, (0, 0, 0)), (3, 3, 2, (0, 0, 0)), (3, 3, 3, (0, 0, 1)), (2, 3, 3, (0, 1, 0)), (3, 2, 3, (1, 0, 0)),
                       (4, 3, 2, (0, 1, 0)), (4, 4, 3, (1, 0, 1))]:
    host = TL.two_square_prism(kA, flipD=bool(fl[0]))
    Q = TL.prism_piece(kQ, bool(fl[1]), sq=TL.D4, tag='q')
    R = TL.prism_piece(kR, bool(fl[2]), sq=TL.D4, tag='r')
    T1 = TL.trisum_of([host, Q, R], sq=TL.D4)
    direct = TL.leaning(T1)
    sQ, sR = TL.leaning(TL.prism_piece(kQ, bool(fl[1]))), TL.leaning(TL.prism_piece(kR, bool(fl[2])))
    via = tuple(TL.weighted_host_count(host, TL.C4, TL.D4, (sQ, sR), lean) for lean in ('alpha', 'beta'))
    d4[str((kA, kQ, kR, fl))] = {"direct split of the nested trisum": direct, "weighted host count": via}
    ok4 &= direct == via
report("4 weights lemma: a nested trisum's split is its host's weighted colouring count", ok4, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
keys = [("6-prism", False), ("6-prism", False), ("6-prism", True)]
a = TL.amplitude(TL.trisum_of([LIB[k] for k in keys]))
ctrl["the product of amplitudes alone is not the trisum's amplitude"] = a != 27
ctrl["ignoring orientation (using the unswapped split) breaks the law"] = a != TL.law([SPLIT[("6-prism", False)]] * 3)
ctrl["the plain sum of pieces' amplitudes is not it either"] = a != 9
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SEYMOUR-COUNT-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
