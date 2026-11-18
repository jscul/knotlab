"""Referee R1 for COPY-READ-20261118-001 (own code; the study's copylib.py, run.py, readout.py and the pinned keeplib/knotlib are not
imported).

  ../../../.venv/bin/python -B referee_copy.py > referee_copy.json      (from this directory)

SEEDK as in the referee's KEEP-READ-R1 (knot-local moves, SEED's condition after the first crossing, else a knot-local subdivision),
with the knot-local fills enumerated in Python integers by the referee's MID-RULE-R1 `local_fills` (irredundant knot sets, no state
limit), from every bracketing of 5, 6, 7 and every third of 8, to n = 30.  After the switch every fill that makes a new crossing is
labelled absorbing (SEED accepts it) or refused, and read at:
  tier 0    the move's knots, with each distinction's role (middle or end) and the new distinction marked;
  closure   the same with every betweenness the states imply among the move's old distinctions.
Classes are exact: a canonical form, the least relabelling over every order of the move's old distinctions that keeps a
renaming-free signature (how often each is a middle or an end, in the move's knots and in the implied betweenness).  Reported: counts,
the clean-witness fraction pooled and held out (classes learnt on even start indices, scored on odd ones), and, beyond the study,
each class's lift (its share of absorbing moves over its share of all crossing-making moves), to ask whether the knots carry a
statistical sign even where no exact rule exists.
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-SWITCH-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/MID-RULE-20261118-001/referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_switch as RSW  # noqa: E402
import referee_mid as RMID  # noqa: E402


def new_crossing(S, n, a1):
    """Does the fill (new distinction 1 on the states of a1) make two old splits cross?"""
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})
    idx = {s: i for i, s in enumerate(S)}
    for a, b in itertools.combinations(sp, 2):
        q = (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))
        if all(q):
            continue
        ra, rb = (a1 >> idx[a]) & 1, (a1 >> idx[b]) & 1
        # the quadrant r lands in: (r on a's side?, r on b's side?)
        k = (0 if ra else 2) + (0 if rb else 1)
        if not q[k]:
            return True
    return False


CACHE = {}


def canon0(ks, n, S=None):
    """Exact canonical form of the move's picture (tier 0, or the closure tier when S is given): the least relabelling over every
    order of the move's old distinctions that keeps a renaming-free signature (times as middle, times as end, implied roles)."""
    old = sorted({v for k in ks for v in k if v != n})
    implied = []
    if S is not None:
        for x, z in itertools.combinations(old, 2):
            for y in old:
                if y not in (x, z) and all(RSW.ok(s, (x, y, z)) for s in S):
                    implied.append((x, y, z))
    key = (tuple(ks), tuple(implied))
    if key in CACHE:
        return CACHE[key]
    sig = {v: (sum(1 for k in ks if k[1] == v), sum(1 for k in ks if v in (k[0], k[2])),
               sum(1 for t in implied if t[1] == v), sum(1 for t in implied if v in (t[0], t[2]))) for v in old}
    groups = defaultdict(list)
    for v in old:
        groups[sig[v]].append(v)
    keys = sorted(groups)
    best = None
    for combo in itertools.product(*[itertools.permutations(groups[g]) for g in keys]):
        order = [v for part in combo for v in part]
        lab = {v: i for i, v in enumerate(order)}
        lab[n] = -1
        kk = sorted((tuple(sorted((lab[k[0]], lab[k[2]]))), lab[k[1]]) for k in ks)
        ii = sorted((tuple(sorted((lab[x], lab[z]))), lab[y]) for x, y, z in implied)
        cand = (tuple(keys), tuple(kk), tuple(ii))
        if best is None or cand < best:
            best = cand
    CACHE[key] = repr(best)
    return CACHE[key]


def run(args):
    idx, T = args
    n0 = 1 + max(max(k) for k in T)
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    rng = random.Random(f"referee-copy:{T}")
    rows = []
    while n < 30:
        F = RMID.local_fills(S, n, G)
        crossed = RSW.crosses(S, n)
        if crossed:
            acc = {}
            for a0, a1, ks in F:
                key = (a0, a1)
                if key not in acc:
                    S2 = RMID.apply(S, n, a0, a1)
                    acc[key] = (RSW.seed_ok(S, n, S2), new_crossing(S, n, a1))
                ok, nc = acc[key]
                if not nc:
                    continue
                rows.append({"run": idx, "n": n, "ext": f"{n}:{a0}:{a1}", "label": "absorb" if ok else "refuse",
                             "c0": canon0(ks, n), "cc": canon0(ks, n, S)})
            good = [f for f in F if acc[(f[0], f[1])][0]]
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
            k = (u, n, v)
            S2 = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if RSW.ok(x, k)))
            ks = (k,)
        S, n = S2, n + 1
        G = G | RM.pairs_of(ks)
    return rows


def main(workers=16):
    Ts = []
    for n0 in (5, 6, 7):
        Ts += [tuple(T) for T in RM.bracketings(0, n0 - 1)]
    Ts += [tuple(T) for T in RM.bracketings(0, 7)][::3]
    with Pool(workers) as P:
        rows = [r for rs in P.map(run, list(enumerate(Ts)), chunksize=1) for r in rs]
    out = {"runs": len(Ts), "crossing_fills": len(rows), "absorbing": sum(r["label"] == "absorb" for r in rows)}
    out["absorbing_share"] = out["absorbing"] / max(1, out["crossing_fills"])
    absn = sorted(r["n"] for r in rows if r["label"] == "absorb")
    out["absorbing_n_median"] = absn[len(absn) // 2] if absn else None
    base = out["absorbing_share"]
    for key, name in (("c0", "tier 0"), ("cc", "closure")):
        cls = defaultdict(Counter)
        for r in rows:
            cls[r[key]][r["label"]] += 1
        dirty = {c for c, v in cls.items() if v["refuse"]}
        A = [r for r in rows if r["label"] == "absorb"]
        exts = defaultdict(set)
        for r in A:
            exts[(r["run"], r["ext"])].add(r[key])
        pooled = sum(1 for e in exts.values() if any(c not in dirty for c in e)) / max(1, len(exts))
        tr = [r for r in rows if r["run"] % 2 == 0]
        te = defaultdict(set)
        for r in A:
            if r["run"] % 2 == 1:
                te[(r["run"], r["ext"])].add(r[key])
        seen_abs = {r[key] for r in tr if r["label"] == "absorb"}
        dirty_tr = {r[key] for r in tr if r["label"] == "refuse"}
        heldout_seen = sum(1 for e in te.values() if any(c in seen_abs or c in dirty_tr for c in e)) / max(1, len(te))
        heldout_clean = sum(1 for e in te.values() if any(c in seen_abs and c not in dirty_tr for c in e)) / max(1, len(te))
        lifts = sorted(((v["absorb"] / max(1, v["absorb"] + v["refuse"])) / base if base else 0, v["absorb"], v["refuse"])
                       for c, v in cls.items() if v["absorb"])
        top = lifts[-3:]
        out[name] = {"classes": len(cls), "classes_with_absorbing": sum(1 for v in cls.values() if v["absorb"]),
                     "clean_witness_pooled": round(pooled, 4), "heldout_seen": round(heldout_seen, 4),
                     "heldout_clean": round(heldout_clean, 4),
                     "largest_lifts (lift, absorbing, refused)": [(round(l, 1), a, r) for l, a, r in top],
                     "share_of_absorbing_in_classes_with_lift_above_10": round(sum(a for l, a, r in lifts if l > 10) / max(1, out["absorbing"]), 3)}
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
