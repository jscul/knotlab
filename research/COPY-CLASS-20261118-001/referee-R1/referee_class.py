"""Referee R1 for COPY-CLASS-20261118-001 (own code; the study's classlib.py, run.py, readout.py, posthoc.py and the pinned
keeplib/knotlib are not imported).

  ../../../.venv/bin/python -B referee_class.py > referee_class.json      (from this directory)

SEEDK as in the referee's COPY-READ-R1 (knot-local fills from MID-RULE-R1's `local_fills`, SEED's condition after the first
crossing, else a knot-local subdivision), on FRESH seeds and starts: every bracketing of 5, 6, 7, the bracketings of 8 at indices
1, 4, 7, ... (the study took 0, 3, 6, ...), 30 uniform random bracketings of the line of 12 to n = 30, and, past the study, 30 of
the line of 14 and 15 of the line of 16 to n = 34.  After the switch, for every fill making a new crossing and each of its knot sets
(one middle knot, two end knots, by MID-RULE's E1), the referee computes from the old crossing graph and r's quadrants:
  SEED       clause (a) no new crossing between two crossed splits; clause (b) every uncrossed split gaining crossings ends with the
             crossers of a crossed split (a model); cross-checked against KNOT-SWITCH-R1's `seed_ok`;
  C1         every new crossing joins a split separating one end pair to a split separating the other;
  CR         the model sought among the crossed splits separating the end pair sharing a distinction with the middle pair;
  CRSWAP     ... separating the other end pair (the far pair);
  CRNOT      ... among the crossed splits separating neither end pair (a control);
  and, beyond the study, where ALL models of every gained split lie, how large the far pair's crossed splits are among the crossed
  splits, what a random candidate set of the same size would score, how many knot sets of a copy step pass CRSWAP, and how many splits
  the check reads.  A rule accepts an extension when it accepts one of its knot sets (as in the study).
"""
import itertools
import json
import math
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for d in ("MEET-ORDERS-20261118-001", "KNOT-SWITCH-20261118-001", "MID-RULE-20261118-001", "COPY-READ-20261118-001"):
    sys.path.insert(0, str(ROOT / "research" / d / "referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_switch as RSW  # noqa: E402
import referee_mid as RMID  # noqa: E402
import referee_copy as RCOPY  # noqa: E402

COPY_CLASS = json.load(open(ROOT / "research/COPY-READ-20261118-001/referee-R1/referee_copy_examples.json"))[0]["closure class"]


def quad(a, b, full):
    return (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))


def crossing_data(S, n, a1):
    """Old splits, the old crossing graph (adjacency sets) and the new crossings made by putting r = 1 on the states of a1."""
    full = (1 << n) - 1
    sp = RSW.splits(S, n)
    idx = {s: i for i, s in enumerate(S)}
    adj = {i: set() for i in range(len(sp))}
    new = []
    for i, j in itertools.combinations(range(len(sp)), 2):
        q = quad(sp[i], sp[j], full)
        if all(q):
            adj[i].add(j)
            adj[j].add(i)
            continue
        ra, rb = (a1 >> idx[sp[i]]) & 1, (a1 >> idx[sp[j]]) & 1
        k = (0 if ra else 2) + (0 if rb else 1)
        if sum(1 for x in q if not x) == 1 and not q[k]:
            new.append((i, j))
    return sp, adj, new


def sep(sp, x, y):
    return {i for i, s in enumerate(sp) if ((s >> x) ^ (s >> y)) & 1}


def judge(S, n, a1, cert):
    """The verdicts on one crossing-making fill and its knot sets."""
    sp, adj, new = crossing_data(S, n, a1)
    active = {v for v in adj if adj[v]}
    clause_a = not any(i in active and j in active for i, j in new)
    newN = {}
    for i, j in new:
        newN.setdefault(i, set()).add(j)
        newN.setdefault(j, set()).add(i)
    gained = sorted(u for u in newN if u not in active)
    after = {v: frozenset(adj[v] | newN.get(v, set())) for v in adj}
    models = {u: {m for m in active if after[m] == after[u]} for u in gained}
    seed = clause_a and all(models[u] for u in gained)
    kind_b = None
    if clause_a and not seed:
        sub = all(any(after[u] < after[m] for m in active) for u in gained)
        sup = all(any(after[u] > after[m] for m in active) for u in gained)
        kind_b = "strict subset" if sub else ("strict superset" if sup else "mixed")
    sets = []
    for ks in cert:
        mids = [k for k in ks if k[1] == n]
        ends = [k for k in ks if k[1] != n]
        rec = {"mids": len(mids), "ends": len(ends)}
        if len(mids) != 1 or len(ends) != 2:
            rec["shape"] = "other"
            sets.append(rec)
            continue
        mp = {mids[0][0], mids[0][2]}
        pe = [tuple(x for x in k if x != n) for k in ends]
        share = [t for t in range(2) if mp & set(pe[t])]
        rec["shape"] = {1: "one end pair touches the middle pair", 2: "both touch", 0: "neither touches"}[len(share)]
        S1 = [sep(sp, *p) for p in pe]
        rec["c1"] = all((i in S1[0] and j in S1[1]) or (i in S1[1] and j in S1[0]) for i, j in new)
        if len(share) == 1:
            near, far = S1[share[0]], S1[1 - share[0]]
            cand = {"CR": near & active, "CRSWAP": far & active, "CRNOT": active - near - far, "CRBOTH": (near | far) & active}
            for name, C in cand.items():
                rec[name] = clause_a and all(models[u] & C for u in gained)
            rec["cand_far"] = len(cand["CRSWAP"])
            rec["far_all"] = cand["CRSWAP"] == active
            rec["near_crossed"] = len(cand["CR"])
            rec["near_far"] = (len(near), len(far))
            if seed:
                rec["models"] = [(len(models[u]), len(models[u] & far), len(models[u] & near), len(models[u] - near - far)) for u in gained]
                rec["gained_in"] = [("near" if u in near else "") + ("far" if u in far else "") for u in gained]
                # what the check reads: the end pairs' splits, their crossers and the models' crossers
                read = near | far
                for v in near | far:
                    read |= adj[v]
                for u in gained:
                    for m in models[u] & far:
                        read |= after[m]
                rec["read_share"] = len(read) / len(sp)
                # a random candidate set of the same size as CRSWAP's: the chance every gained split finds a model in it
                A, c = len(active), len(cand["CRSWAP"])
                p = 1.0
                for u in gained:
                    p *= 1 - math.comb(A - len(models[u]), c) / math.comb(A, c)
                rec["random_same_size"] = p
        sets.append(rec)
    return {"seed": seed, "clause_a": clause_a, "kind_b": kind_b, "gained": len(gained), "splits": len(sp), "active": len(active),
            "model_crossers": [len(after[u]) for u in gained], "sets": sets}


def run(args):
    idx, T, n0, nmax = args
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    rng = random.Random(f"referee-class:{T}")
    rows = []
    while n < nmax:
        F = RMID.local_fills(S, n, G)
        crossed = RSW.crosses(S, n)
        good = []
        if crossed:
            byext = {}
            for a0, a1, ks in F:
                byext.setdefault((a0, a1), []).append(ks)
            for (a0, a1), cert in byext.items():
                if not RCOPY.new_crossing(S, n, a1):
                    seed = RSW.seed_ok(S, n, RMID.apply(S, n, a0, a1))
                    if seed:
                        good += [(a0, a1, ks) for ks in cert]
                    continue
                v = judge(S, n, a1, cert)
                v["seed_check"] = RSW.seed_ok(S, n, RMID.apply(S, n, a0, a1))
                v["n"] = n
                v["run"] = idx
                if v["seed"]:
                    v["copy_class"] = any(RCOPY.canon0(ks, n, S) == COPY_CLASS for ks in cert)
                    good += [(a0, a1, ks) for ks in cert]
                rows.append(v)
        else:
            good = F
        if good:
            a0, a1, ks = rng.choice(good)
            S2 = RMID.apply(S, n, a0, a1)
        else:
            subs = [(u, v) for u, v in sorted(G) if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
            if not subs:
                break
            u, v = rng.choice(subs)
            ks = ((u, n, v),)
            S2 = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if RSW.ok(x, ks[0])))
        S, n = S2, n + 1
        G = G | RM.pairs_of(ks)
    return rows


def starts():
    J = []
    for n0 in (5, 6, 7):
        J += [(tuple(T), n0, 30) for T in RM.bracketings(0, n0 - 1)]
    J += [(tuple(T), 8, 30) for T in RM.bracketings(0, 7)[1::3]]
    rng = random.Random("referee-class-lines")
    J += [(RM.random_bracketing(0, 11, rng), 12, 30) for _ in range(30)]
    J += [(RM.random_bracketing(0, 13, rng), 14, 34) for _ in range(30)]
    J += [(RM.random_bracketing(0, 15, rng), 16, 34) for _ in range(15)]
    return [(i,) + j for i, j in enumerate(J)]


def summarise(rows, J):
    out = {"starts": len(J), "crossing_extensions": len(rows), "copy_steps": sum(r["seed"] for r in rows),
           "seed_vs_seed_ok_disagree": sum(r["seed"] != r["seed_check"] for r in rows)}
    sets = [s for r in rows for s in r["sets"]]
    out["knot_sets"] = len(sets)
    out["knot_set_shapes"] = dict(Counter(s["shape"] for s in sets))
    out["c1_fail"] = sum(1 for s in sets if s.get("c1") is False)
    for name in ("CR", "CRSWAP", "CRNOT", "CRBOTH"):
        t = Counter()
        for r in rows:
            acc = any(s.get(name) for s in r["sets"])
            t[f"seed={int(r['seed'])} {name}={int(acc)}"] += 1
        out[name + " vs SEED (extensions)"] = dict(sorted(t.items()))
    C = [r for r in rows if r["seed"]]
    out["copy_steps_in_copy_class"] = sum(r["copy_class"] for r in C)
    ok_sets = [sum(1 for s in r["sets"] if s.get("CRSWAP")) for r in C]
    tot_sets = [sum(1 for s in r["sets"] if "CRSWAP" in s) for r in C]
    out["copy steps: knot sets passing CRSWAP / knot sets with one touching end pair"] = dict(Counter(f"{a}/{b}" for a, b in zip(ok_sets, tot_sets)))
    out["copy steps where every such knot set passes CRSWAP"] = sum(a == b for a, b in zip(ok_sets, tot_sets))
    m = Counter()
    for r in C:
        for s in r["sets"]:
            for tot, far, near, neither in s.get("models", []):
                m["gained split readings"] += 1
                m["all models separate the far pair"] += far == tot
                m["some model separates the near pair"] += near > 0
                m["some model separates neither"] += neither > 0
                m[f"models per gained split = {tot}"] += 1
            for g in s.get("gained_in", []):
                m[f"gained split separates: {g or 'neither'}"] += 1
    out["where the models lie (copy steps, per knot set and gained split)"] = dict(sorted(m.items()))
    fr = sorted(s["cand_far"] / r["active"] for r in C for s in r["sets"] if "cand_far" in s)
    out["copy steps: far pair's crossed splits / crossed splits (median, min, max)"] = (fr[len(fr) // 2], fr[0], fr[-1]) if fr else None
    fr2 = sorted(s["cand_far"] / r["active"] for r in rows if not r["seed"] for s in r["sets"] if "cand_far" in s)
    out["refused: far pair's crossed splits / crossed splits (median)"] = fr2[len(fr2) // 2] if fr2 else None
    rnd = [max(s["random_same_size"] for s in r["sets"] if "random_same_size" in s) for r in C if any("random_same_size" in s for s in r["sets"])]
    out["random candidate set of CRSWAP's size: expected recall over copy steps (best knot set)"] = round(sum(rnd) / max(1, len(rnd)), 4)
    out["random candidate set: copy steps it would pass with probability 1"] = sum(1 for p in rnd if p > 1 - 1e-12)
    rd = sorted(s["read_share"] for r in C for s in r["sets"] if "read_share" in s)
    out["copy steps: share of all splits the CRSWAP check reads (median, min, max)"] = (round(rd[len(rd) // 2], 3), round(rd[0], 3), round(rd[-1], 3)) if rd else None
    mc = sorted(c / r["splits"] for r in C for c in r["model_crossers"])
    out["copy steps: model's crossers / splits (median)"] = round(mc[len(mc) // 2], 3) if mc else None
    out["copy steps: model crossers"] = dict(sorted(Counter(c for r in C for c in r["model_crossers"]).items()))
    t = Counter()
    for r in rows:
        if not r["seed"]:
            t["(a)" if not r["clause_a"] else "(b) " + r["kind_b"]] += 1
    out["refusals"] = dict(t)
    # the far pair separated by every crossed split, as a sign of a copy step (some knot set with one touching end pair has it)
    t = Counter()
    for r in rows:
        sign = any(s.get("far_all") for s in r["sets"])
        t[f"seed={int(r['seed'])} far pair separated by every crossed split={int(sign)}"] += 1
        if sign and not r["seed"]:
            t["refused with the sign: (a)" if not r["clause_a"] else "refused with the sign: (b)"] += 1
    out["sign: far pair separated by every crossed split"] = dict(sorted(t.items()))
    nc = Counter(s["near_crossed"] for r in C for s in r["sets"] if "near_crossed" in s)
    out["copy steps: crossed splits separating the near pair (count: copy steps)"] = dict(sorted(nc.items()))
    out["copy steps: knot sets by shape"] = dict(Counter(s["shape"] for r in C for s in r["sets"]))
    out["copy steps by n"] = dict(sorted(Counter(r["n"] for r in C).items()))
    return out


def main(workers=16):
    J = starts()
    with Pool(workers) as P:
        res = P.map(run, J, chunksize=1)
    rows = [r for rs in res for r in rs]
    out = {"all": summarise(rows, J)}
    small = {j[0] for j in J if j[2] <= 8}
    out["bracketings of 5 to 8"] = summarise([r for r in rows if r["run"] in small], [j for j in J if j[2] <= 8])
    out["lines of 12"] = summarise([r for r in rows if J[r["run"]][2] == 12], [j for j in J if j[2] == 12])
    out["lines of 14 and 16 (past the study), to n = 34"] = summarise([r for r in rows if J[r["run"]][2] >= 14], [j for j in J if j[2] >= 14])
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
