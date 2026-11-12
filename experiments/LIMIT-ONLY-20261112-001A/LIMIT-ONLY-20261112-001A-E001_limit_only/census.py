"""LIMIT-ONLY-20261112-001A: nested families that die at a finite depth while their bottomless limit lives.

Families of SHORT-DESC-20261112-001's language (dlang.py). For each: the finite depths (SELF at depth 1 is the holding knot) and the
limit (SELF never reaches a bottom: iterate from 'nothing' to the greatest fixed point; by compactness the infinite pattern allows a
state iff that fixed point's main relation is non-empty). Tested on every family:
  L1 (lemma; code control): a family that dies at a finite depth but lives in the limit has a self-holding definition whose limit
     relation allows its three ports to be all equal (the state the holding knot forbids).
  L2 (criterion): a family lives at every finite depth iff the main relation is non-empty at P, the largest tuple of relations
     inside the knot with P inside Phi(P) (iterate X -> knot and Phi(X) from the knot). True when the knot and its image Phi(knot)
     compare (proved); measured, with its failures split by kind, where they do not.
Classes: E, every one-definition family with three ports, 0 to 3 own distinctions and one to three calls (a multiset of knots and
SELF calls, at least one SELF); W, families drawn by the description code (main variant), fresh seeds.
Run from the repository root:  census.py --exhaustive WORKER WORKERS  |  census.py --sample WORKER TRIES  |  census.py --summary
"""
import hashlib, itertools, json, os, random, sys, time
from collections import Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census"))
import dlang as L

OUT = os.environ.get("LO_OUT") or os.path.join(HERE, "../../../artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only")
PAIRS = [(1, 6), (2, 5), (4, 3)]                       # the knot's complementary pairs of port states (bit j = port j)


def read(defs):
    """Fate over finite depths, the limit, the knot's comparability with its image, the L2 criterion and the L1 gate."""
    selfs = [i for i, d in enumerate(defs) if any(cl == "SELF" for cl, _ in d[2])]
    f = L.fate(defs)
    finite_alive = f["first_dead"] is None
    _, _, lim = L.depth_sequence(defs, L.TOP)
    _, _, orbit_end = L.depth_sequence(defs, L.NAE)
    limit_only = (not finite_alive) and f["limit_alive"]
    knot = {i: L.NAE for i in selfs}
    image = L.relations(defs, knot)
    up = all(not np.any(L.NAE & ~image[i]) for i in selfs)        # the knot inside its image
    down = all(not np.any(image[i] & ~L.NAE) for i in selfs)      # the image inside the knot
    comp = "equal" if (up and down) else ("up" if up else ("down" if down else "incomparable"))
    X = dict(knot)                                                # P: the largest X inside the knot with X inside Phi(X)
    while True:
        rels = L.relations(defs, X)
        Y = {i: L.NAE & rels[i] for i in selfs}
        if all(np.array_equal(Y[i], X[i]) for i in selfs):
            break
        X = Y
    l2_pred = bool(L.relations(defs, X)[-1].any())
    l1 = (not limit_only) or any(lim[i][0] for i in selfs)
    kind = None
    if l2_pred != finite_alive:
        kind = "period above 1" if f["period"] > 1 else ("fixed point outside the knot" if any(orbit_end[i][0] for i in selfs)
                                                         else "other")
    return dict(fate=f["fate"], first_dead=f["first_dead"], period=f["period"], after=f["after"], limit_alive=f["limit_alive"],
                limit_only=limit_only, comparability=comp, L1_ok=l1, L2_pred=l2_pred, L2_ok=(l2_pred == finite_alive),
                L2_failure=kind, limit_all_equal=[bool(lim[i][0]) for i in selfs], limit_kinds=f["limit_kinds"], nself=len(selfs))


def exhaustive(worker, workers):
    os.makedirs(OUT, exist_ok=True)
    f = open(os.path.join(OUT, f"exhaustive_{worker}.jsonl"), "w")
    idx, t0 = -1, time.time()
    for l in range(4):
        V = 3 + l
        options = [("K", c) for c in itertools.combinations(range(V), 3)] + [("SELF", p) for p in itertools.permutations(range(V), 3)]
        for c in (1, 2, 3):
            for body in itertools.combinations_with_replacement(range(len(options)), c):
                if not any(options[j][0] == "SELF" for j in body):
                    continue
                if len(set(body)) < len(body):                    # a repeated call adds nothing
                    continue
                idx += 1
                if idx % workers != worker:
                    continue
                defs = [(3, l, [options[j] for j in body])]
                r = read(defs)
                if r["limit_only"] or not r["L1_ok"] or not r["L2_ok"]:
                    r["defs"] = defs
                f.write(json.dumps(dict(l=l, c=c, **{k: v for k, v in r.items()})) + "\n")
    f.write(json.dumps(dict(kind="done", seconds=round(time.time() - t0))) + "\n")
    f.close()


def sample(worker, tries):
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(int(hashlib.sha256(f"LO:{worker}".encode()).hexdigest()[:16], 16))
    f = open(os.path.join(OUT, f"sample_{worker}.jsonl"), "w")
    for k in range(tries):
        d = L.sample(rng, **L.VARIANTS["main"])
        if "defs" in d and d.get("t") is not None:
            r = read(d["defs"])
            r["bits"] = d["bits"] - d["tbits"]
            if r["limit_only"] or not r["L1_ok"] or not r["L2_ok"]:
                r["defs"] = d["defs"]
            f.write(json.dumps(r) + "\n")
    f.write(json.dumps(dict(kind="done", tries=tries)) + "\n")
    f.close()


def summarize(prefix):
    rows = [json.loads(x) for name in sorted(os.listdir(OUT)) if name.startswith(prefix) for x in open(os.path.join(OUT, name))]
    rows = [r for r in rows if r.get("kind") != "done"]
    S = dict(families=len(rows))
    S["fate_x_limit"] = {f"{a}|{b}": v for (a, b), v in Counter((r["fate"], r["limit_alive"]) for r in rows).items()}
    S["comparability"] = dict(Counter(r["comparability"] for r in rows))
    S["L1_exceptions"] = sum(not r["L1_ok"] for r in rows)
    S["L2_failures_by_comparability"] = dict(Counter(r["comparability"] for r in rows if not r["L2_ok"]))
    S["L2_failures_by_kind"] = dict(Counter(r["L2_failure"] for r in rows if not r["L2_ok"]))
    S["L2_failures_among_incomparable"] = [sum(not r["L2_ok"] for r in rows if r["comparability"] == "incomparable"),
                                           sum(r["comparability"] == "incomparable" for r in rows)]
    lo = [r for r in rows if r["limit_only"]]
    S["limit_only"] = len(lo)
    S["limit_only_by_comparability"] = dict(Counter(r["comparability"] for r in lo))
    S["P3_limit_only_down_share"] = round(sum(r["comparability"] == "down" for r in lo) / len(lo), 4) if lo else None
    S["limit_only_first_dead"] = dict(Counter(r["first_dead"] for r in lo))
    S["limit_only_after"] = dict(Counter(r["after"] for r in lo))
    S["limit_only_limit_kinds"] = dict(Counter(k for r in lo for k in r["limit_kinds"]))
    dying = [r for r in rows if r["fate"] != "forever"]
    S["dying"] = len(dying)
    S["dying_share_alive_in_limit"] = round(sum(r["limit_alive"] for r in dying) / len(dying), 4) if dying else None
    small = sorted([r for r in lo if "defs" in r and len(r["defs"]) == 1], key=lambda r: (len(r["defs"][0][2]), r["defs"][0][1]))
    S["smallest_limit_only"] = [dict(defs=r["defs"], first_dead=r["first_dead"], comparability=r["comparability"]) for r in small[:6]]
    S["L2_counterexamples"] = [dict(defs=r["defs"], comparability=r["comparability"], kind=r["L2_failure"]) for r in rows
                               if not r["L2_ok"] and "defs" in r][:6]
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--exhaustive":
        exhaustive(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "--sample":
        sample(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "--summary":
        out = dict(exhaustive=summarize("exhaustive_"), sampled=summarize("sample_"))
        json.dump(out, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(out, indent=1))
