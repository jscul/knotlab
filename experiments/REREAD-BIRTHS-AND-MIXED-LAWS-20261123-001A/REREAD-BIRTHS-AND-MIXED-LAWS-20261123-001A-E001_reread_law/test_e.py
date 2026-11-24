"""Test (e): pace.  The first 200 draws of test (c) (in the order of p3_draws) whose first round funds under ordinary
growth; one loose distinction is added at one knot drawn by random.Random(2026112330).randrange(n), in that order.
Unedited and edited starts are grown 12 rounds or 5,000 knots under one law and one rule (ordinary growth, or R with
convention O or N).

Distance: steps in the start's sharing graph (two knots adjacent when they share a distinction) from the edited knot;
a later knot takes the least distance of its founder ancestors (ancestry through parents), which is the least distance of
its parents.  Births are matched as in the influence-cone study (INFLUENCE-CONE-20261120-001A sample.py, `index_history`
terms and the priced roster of `reading`): an original knot r is (0, r), a birth is (1, sorted identities of its
parents) and, under R, the payments (per parent: loose, or the identities of the round-start holders of the shared
distinction it paid); at each round the multisets of (identity, number of fresh distinctions) are compared and the
births in the difference, in both directions, are the changed births, each with its distance in its own history.
Identities are interned to integers shared by the two histories.  Rounds from a cap (or a round whose fresh counts are
only lower bounds) in either history on are not compared.

Run from the repo root:
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --law L --rule ordinary|R [--conv O|N]
"""
import argparse
import json
import random
import sys
import time
from collections import Counter, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402

HORIZON, CAP = 12, 5000
N_DRAWS, EDIT_SEED = 200, 2026112330


def selected_draws():
    out = []
    for dr in rlaw.lib.p3_draws():
        h = rlaw.ordinary_reference(dr["stars"], "parity", 1, CAP)
        h2 = rlaw.ordinary_reference(dr["stars"], "nae", 1, CAP)
        assert (h["steps"] >= 1) == (h2["steps"] >= 1)
        if h["steps"] >= 1:
            out.append(dr)
        if len(out) == N_DRAWS:
            break
    rng = random.Random(EDIT_SEED)
    edits = [rng.randrange(dr["n"]) for dr in out]
    return out, edits


def start_distances(stars, source):
    holders = {}
    for k, s in enumerate(stars):
        for d in s:
            holders.setdefault(d, []).append(k)
    nbr = [set() for _ in stars]
    for hs in holders.values():
        for a in hs:
            nbr[a].update(x for x in hs if x != a)
    dist = [None] * len(stars)
    dist[source] = 0
    q = deque([source])
    while q:
        v = q.popleft()
        for w in nbr[v]:
            if dist[w] is None:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


class Interner:
    def __init__(self):
        self.ids = {}

    def __call__(self, key):
        i = self.ids.get(key)
        if i is None:
            i = self.ids[key] = len(self.ids)
        return i


def index(g, n0, dist0, intern):
    """Per knot: identity (interned) and distance; per round: Counter of (identity, fresh) and the births' distances."""
    term = [intern(("f", r)) for r in range(n0)]
    dist = list(dist0)
    rounds = []
    base = n0
    for t, rd in enumerate(g.rounds):
        pay = rd.get("pay_holders")
        roster = Counter()
        bd = {}
        for i, (ps, f) in enumerate(zip(rd["parents"], rd["fresh"], strict=True)):
            pt = tuple(sorted(term[p] for p in ps))
            if pay is not None:
                ptag = tuple(sorted((term[p], None if h is None else tuple(sorted(term[x] for x in h)))
                                    for p, h in zip(ps, pay[i], strict=True)))
            else:
                ptag = ()
            tid = intern(("b", pt, ptag))
            term.append(tid)
            dist.append(min(dist[p] for p in ps))
            key = (tid, f)
            roster[key] += 1
            bd.setdefault(key, []).append(dist[-1])
        rounds.append({"roster": roster, "dist": bd, "lower": rd["fresh_lower_bound"]})
        base += len(rd["parents"])
    return rounds


def compare(ga, gb, n0, dist0):
    intern = Interner()
    ra, rb = index(ga, n0, dist0, intern), index(gb, n0, dist0, intern)
    out = []
    for t in range(HORIZON):
        a = ra[t] if t < len(ra) else None
        b = rb[t] if t < len(rb) else None
        stop_a = a is None and ga.outcome in ("cap",)
        stop_b = b is None and gb.outcome in ("cap",)
        if stop_a or stop_b or (a is not None and a["lower"]) or (b is not None and b["lower"]):
            out.append({"t": t + 1, "status": "not compared (cap or lower-bound fresh counts)"})
            break
        if a is None and b is None:
            break
        rA = a["roster"] if a else Counter()
        rB = b["roster"] if b else Counter()
        onlyA, onlyB = rA - rB, rB - rA
        ds = []
        for key, c in onlyA.items():
            ds.extend(sorted(a["dist"][key], reverse=True)[:c])
        for key, c in onlyB.items():
            ds.extend(sorted(b["dist"][key], reverse=True)[:c])
        out.append({"t": t + 1, "births_unedited": sum(rA.values()), "births_edited": sum(rB.values()),
                    "changed": len(ds), "max_distance": max(ds) if ds else None,
                    "none_in_unedited": a is None, "none_in_edited": b is None})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True, choices=rlaw.LAWS)
    ap.add_argument("--rule", required=True, choices=("ordinary", "R"))
    ap.add_argument("--conv", default="O", choices=("O", "N"))
    args = ap.parse_args()
    t0 = time.time()
    draws, edits = selected_draws()
    rows, prefixes = [], []
    for dr, k in zip(draws, edits, strict=True):
        stars = [tuple(s) for s in dr["stars"]]
        top = max(d for s in stars for d in s) + 1
        edited = list(stars)
        edited[k] = stars[k] + (top,)
        dist0 = start_distances(stars, k)
        hist = {}
        for name, st in (("unedited", stars), ("edited", edited)):
            g = rlaw.Growth(st, args.law, args.rule, args.conv)
            g.run(HORIZON, CAP, keep_payments=(args.rule == "R"))
            hist[name] = g
            if args.rule == "R":
                pre = rlaw.small_prefix(g.stars, g.n_at, args.law)
                if pre is not None and not any(g.rounds[t]["fresh_lower_bound"] for t in range(len(pre["n_at"]) - 1)):
                    pre.update({"test": "e", "arm": dr["arm"], "draw": dr["draw"], "conv": args.conv, "which": name,
                                "paid_births": [g.rounds[t]["paid_births"] for t in range(len(pre["n_at"]) - 1)]})
                    prefixes.append(pre)
        gu, ge = hist["unedited"], hist["edited"]
        rows.append({"arm": dr["arm"], "draw": dr["draw"], "n": dr["n"], "edited_knot": k, "law": args.law,
                     "rule": args.rule, "conv": args.conv if args.rule == "R" else None,
                     "start_distances": dist0,
                     "unedited": {"outcome": gu.outcome, "n_at": gu.n_at, "births": gu.births_per_round(),
                                  "paid_births": [r["paid_births"] for r in gu.rounds]},
                     "edited": {"outcome": ge.outcome, "n_at": ge.n_at, "births": ge.births_per_round(),
                                "paid_births": [r["paid_births"] for r in ge.rounds]},
                     "residual_stall": gu.outcome == "residual_stall" or ge.outcome == "residual_stall",
                     "stall": gu.outcome == "stall" or ge.outcome == "stall",
                     "rounds": compare(gu, ge, dr["n"], dist0)})
    tag = f"{args.law}_{args.rule}{args.conv if args.rule == 'R' else ''}"
    rlaw.dump(rlaw.OUT / f"e_{tag}.jsonl", rows)
    if prefixes:
        rlaw.dump(rlaw.OUT / "prefixes" / f"e_{tag}.jsonl.gz", prefixes)
    print(json.dumps({"run": tag, "draws": len(rows), "seconds": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
