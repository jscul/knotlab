"""Referee R1 for FIRST-KNOT-20261118-001 (own code; the study's startlib.py, job.py and FRESH-COUNT's freelib.py are not imported).

  ../../../.venv/bin/python -B referee_first.py <part> > referee_first_<part>.json      (from this directory)

Built on the referee's FRESH-COUNT-R1 simulator (`referee_fresh.Growth`: the complete-round joining policy from its statement,
GF(2) implied parity, lookahead demand), extended to a start of several junctions (round 0, shared distinctions allowed).  The fewest
rule: 0 fresh where the demand is 0 and the parity is implied, else max(d, 3 - p, 1); one count c >= 2.

Parts:
  pairs     two knots of a, b = 3..7 places (study 3..6), apart and sharing 1 or 2 distinctions: one count c = 2..9 (study 2..8) against
            Theorem 2 (runs exactly when every start knot has 0, 1 or c open distinctions; stall round as the table); the fewest rule
            against Theorem 3 (apart: both close; sharing one: per piece t + 1, or C(l, t) / 1 / t - l), with the relay u = h checked
            by GF(2) (u + h in the span of the equations).
  present   Corollary 2.1: the four-place relation as one knot, as A, B through a hidden h, and as A, A + B.
  mutual    Proposition 4 (post hoc): m knots of m + 1 places touching pairwise, m = 3..6 (study 3..5), the fewest rule, 16 rounds,
            against the crossed start of a = m (FRESH-COUNT T4(c)) from round 2, and the growth exponent from cumulative counts; the
            closing controls (three knots of five places, four of four).
"""
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/FRESH-COUNT-20261118-001/referee-R1"))
import referee_fresh as RF  # noqa: E402


class Start(RF.Growth):
    def __init__(self, junctions):
        self.bits = [list(j) for j in junctions]
        self.owner = {}
        for k, J in enumerate(junctions):
            for b in J:
                self.owner.setdefault(b, []).append(k)
        assert max(len(v) for v in self.owner.values()) <= 2
        self.nb = max(self.owner) + 1
        self.nbr = [set() for _ in junctions]
        for b, js in self.owner.items():
            if len(js) == 2:
                self.nbr[js[0]].add(js[1])
                self.nbr[js[1]].add(js[0])
        self.parents = [set() for _ in junctions]
        self.round = [0] * len(junctions)
        self.fresh = [len(J) for J in junctions]
        self.dem = [None] * len(junctions)
        self.live = list(range(len(junctions)))
        self.rounds = 0
        self.basis = {}
        for k in range(len(junctions)):
            self._add(k)
        self.forced = 0


def fewest(G, info, rng):
    return [0 if (i["implied"] and i["d"] == 0) else max(i["d"], 3 - i["p"], 1) for i in info]


def uniform(c):
    return lambda G, info, rng: [c for _ in info]


def grow(junctions, rule, rounds, max_junctions=6000):
    G = Start(junctions)
    outcome = "alive"
    for _ in range(rounds):
        r = G.step(rule, None, None)
        if r != "ok":
            outcome = r
            break
        if len(G.bits) > max_junctions:
            outcome = "big"
            break
    return G, outcome


def pair(a, b, s):
    A = list(range(a))
    return [A, A[a - s:] + list(range(a, a + b - s))]


def open_counts(junctions):
    c = Counter(x for J in junctions for x in J)
    return [sum(1 for x in J if c[x] == 1) for J in junctions]


def predicted_stall(ls, c):
    rounds = []
    for l in ls:
        if l <= 1 or c == l:
            continue
        rounds.append(2 if c <= l - 2 else 4 if c == l - 1 else 3)
    return min(rounds) if rounds else None


def part_pairs():
    out = {"uniform cells": 0, "uniform disagreements": [], "fewest": {}}
    for a in range(3, 8):
        for b in range(a, 8):
            for s in (0, 1, 2):
                st = pair(a, b, s)
                ls = open_counts(st)
                for c in range(2, 10):
                    G, outcome = grow(st, uniform(c), 9, max_junctions=20000)
                    stall = G.rounds + 1 if outcome == "stall" else None
                    pred = predicted_stall(ls, c)
                    out["uniform cells"] += 1
                    if stall != pred:
                        out["uniform disagreements"].append({"a": a, "b": b, "shared": s, "c": c, "stall": stall, "predicted": pred})
                if s in (0, 1):
                    G, outcome = grow(st, fewest, 30)
                    counts = G.counts()
                    rec = {"outcome": outcome, "rounds": G.rounds, "forced": G.forced}
                    if s == 0:
                        rec["closed as two Boolean patterns"] = outcome == "closed"
                    else:
                        pred = []
                        for t in range(1, G.rounds + 1):
                            n = 0
                            for l in ls:
                                n += (t + 1) if l == 2 else (math.comb(l, t) if t <= l else (1 if t == l + 1 else t - l))
                            pred.append(n)
                        rec["per-round counts as Theorem 3"] = counts[1:] == pred
                        # the relay: each top's single fresh bit u satisfies u + h in the span (u = h in every allowed state)
                        h = a - 1
                        relays = 0
                        for j in range(2, len(G.bits)):
                            if G.dem[j] == 0 and G.fresh[j] == 1 and len(G.parents[j]) >= 3:
                                u = G.bits[j][-1]
                                relays += G._reduce((1 << u) | (1 << h)) == 0
                                rec.setdefault("tops with one fresh bit", 0)
                                rec["tops with one fresh bit"] += 1
                        rec["relays u = h"] = relays
                    out["fewest"][f"{a}-{b} shared {s}"] = rec
    return out


def part_present():
    x1, x2, x3, x4, h = 0, 1, 2, 3, 4
    shapes = {"one knot": [[x1, x2, x3, x4]], "A, B through hidden h": [[x1, x2, h], [h, x3, x4]],
              "A, A + B": [[x1, x2, h], [x1, x2, x3, x4]]}
    out = {}
    for name, st in shapes.items():
        rec = {"open counts": open_counts(st)}
        for c in range(2, 7):
            G, outcome = grow(st, uniform(c), 8)
            rec[f"c={c}"] = outcome if outcome != "stall" else f"stall at round {G.rounds + 1}"
        G, outcome = grow(st, fewest, 20)
        rec["fewest"] = {"outcome": outcome, "counts": G.counts()}
        out[name] = rec
    # the projection: allowed states of A, B forgetting h equal the one knot's
    import itertools as it
    proj = {(v[0], v[1], v[2], v[3]) for v in it.product((0, 1), repeat=5) if (v[0] ^ v[1] ^ v[4]) == 0 and (v[4] ^ v[2] ^ v[3]) == 0}
    one = {v for v in it.product((0, 1), repeat=4) if (v[0] ^ v[1] ^ v[2] ^ v[3]) == 0}
    out["A, B with h forgotten = the four-place knot"] = proj == one
    return out


def mutual(m, places_extra=0):
    """m knots, each pair sharing one distinction of its own; each knot has m - 1 shared and 2 + places_extra open."""
    nxt = 0
    shared = {}
    for i, j in itertools.combinations(range(m), 2):
        shared[(i, j)] = nxt
        nxt += 1
    knots = []
    for i in range(m):
        J = [shared[tuple(sorted((i, j)))] for j in range(m) if j != i]
        for _ in range(2 + places_extra):
            J.append(nxt)
            nxt += 1
        knots.append(J)
    return knots


def crossed(a, rounds):
    G = RF.Growth(a)
    rule = lambda G_, info, rng: [k + (1 if G_.rounds == a - 1 else 0) for k in RF.fewest(G_, info, rng)]
    for _ in range(rounds):
        if G.step(rule, None, None) != "ok" or len(G.bits) > 40000:
            break
    return G.counts()


def exponent(counts):
    """log-log slope of the cumulative junction count over the last third of the rounds."""
    cum = list(itertools.accumulate(counts))
    T = len(cum)
    i, j = max(2, (2 * T) // 3), T - 1
    return round(math.log(cum[j] / cum[i]) / math.log((j + 1) / (i + 1)), 2)


def part_mutual():
    out = {}
    for m in range(3, 7):
        R = 16 if m <= 4 else 13 if m == 5 else 11
        st = mutual(m)
        G, outcome = grow(st, fewest, R, max_junctions=60000)
        mc = G.counts()
        cc = crossed(m, R + m)
        # Proposition 4: from round 2 on the growth is the crossed start's from its round a = m + 1 on
        k = min(len(mc) - 2, len(cc) - (m + 1))
        same = mc[2:2 + k] == cc[m + 1:m + 1 + k]
        out[f"m={m}"] = {"knots of": m + 1, "open counts": open_counts(st), "outcome": outcome, "rounds": G.rounds,
                         "junctions per round": mc, "offshoots per round": G.offshoots(), "forced": G.forced,
                         "crossed start a = m, junctions per round": cc,
                         "rounds compared": k, "equal to the crossed start (shifted)": same,
                         "cumulative-count exponent (last third)": exponent(mc)}
        print(m, outcome, same, out[f"m={m}"]["cumulative-count exponent (last third)"], file=sys.stderr, flush=True)
    for name, st in (("three knots of five places, mutually touching", mutual(3, 1)),):
        G, outcome = grow(st, fewest, 16)
        out[name] = {"outcome": outcome, "junctions per round": G.counts(), "offshoots per round": G.offshoots()}
    # four knots of four places each touching the other three: three shared + one open each
    four = []
    nxt = 0
    sh = {}
    for i, j in itertools.combinations(range(4), 2):
        sh[(i, j)] = nxt
        nxt += 1
    for i in range(4):
        four.append([sh[tuple(sorted((i, j)))] for j in range(4) if j != i] + [nxt])
        nxt += 1
    G, outcome = grow(four, fewest, 16)
    out["four knots of four places, mutually touching"] = {"open counts": open_counts(four), "outcome": outcome,
                                                           "junctions per round": G.counts()}
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"pairs": part_pairs, "present": part_present, "mutual": part_mutual}[part](), indent=1, default=str))
