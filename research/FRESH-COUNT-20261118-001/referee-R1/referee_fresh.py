"""Referee R1 for FRESH-COUNT-20261118-001 (own code; the study's freelib.py, ideals.py, bonds.py, job.py are not imported).

  ../../../.venv/bin/python -B referee_fresh.py <part> > referee_fresh_<part>.json      (from this directory)

The complete-round joining policy of CUBIC-FROM-A-KNOT-20261117-001 on even-parity junctions, written from its statement: live
junctions hold loose bits; two live junctions are candidates when they have a common neighbour; a valid set is a clique of at least
three candidates with no neighbour common to all; groups are the maximal valid sets (capped: every valid triple) and every candidate
pair in no valid set (capped: in no valid triple); each live junction gives one loose bit to each of its groups, every other loose bit
gets an offshoot; a junction in more groups than it has loose bits stalls the round.  The count rule gives each new junction k fresh
bits; the demand is the number of next-round groups containing it, computed with every new junction counted live (lookahead).
Implied parity is tested by GF(2) elimination (not by Lemma 0).  The descent-order check (T1) recomputes the ideals from parents.

Parts:
  uniform   one count c, uncapped and capped at three, a = 3..9 (study 3..7), c = 1..a + 3, ten rounds for a <= 4, nine for a = 5,
            eight for a >= 6 (study eight).
  fewest    the fewest rule, a = 3..8 (study 3..6).
  blind     blind counts uniform on 1..K, a = 3, 4, K = 2..6, 200 runs each, to round 14 (study 10), the referee's own seeds.
  handover  1 to 4 surplus rounds then the fewest rule for 25 rounds, 300 runs: offshoots per round constant (T4b); and the crossed
            start, a = 3..7 (study 3..6).
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from math import comb

import networkx as nx


class Growth:
    def __init__(self, a):
        self.bits = [list(range(a))]
        self.owner = {b: [0] for b in range(a)}
        self.nb = a
        self.nbr = [set()]
        self.parents = [set()]
        self.round = [0]
        self.fresh = [a]
        self.dem = [None]
        self.live = [0]
        self.rounds = 0
        self.rows = []          # GF(2) basis {pivot: row}
        self.basis = {}
        self._add(0)
        self.forced = 0

    def _mask(self, bits):
        return sum(1 << b for b in bits)

    def _reduce(self, x):
        while x:
            p = x.bit_length() - 1
            if p not in self.basis:
                return x
            x ^= self.basis[p]
        return 0

    def _add(self, j):
        x = self._reduce(self._mask(self.bits[j]))
        if x:
            self.basis[x.bit_length() - 1] = x

    def loose(self, j):
        return [b for b in self.bits[j] if len(self.owner[b]) == 1]

    def groups(self, live, cap):
        lv = set(live)
        G = nx.Graph()
        G.add_nodes_from(lv)
        for w in range(len(self.bits)):
            ln = sorted(u for u in self.nbr[w] if u in lv)
            G.add_edges_from(itertools.combinations(ln, 2))
        valid = []
        cand = {u: set(G[u]) for u in G}

        def ext(S, common, P):
            # a clique S that keeps a common neighbour w, with every possible extension inside w's neighbours, contains no valid set
            if common and any(P <= self.nbr[w] for w in common):
                return
            if len(S) >= 3 and not common:
                valid.append(frozenset(S))
            if cap is not None and len(S) >= cap:
                return
            for v in sorted(P):
                ext(S + [v], common & self.nbr[v], {w for w in P if w > v and w in cand[v]})

        for u in sorted(lv):
            ext([u], set(self.nbr[u]), {w for w in cand[u] if w > u})
        if cap is None:
            vs = set(valid)
            by_elem = defaultdict(list)
            for T in vs:
                for x in T:
                    by_elem[x].append(T)
            groups = [S for S in vs if not any(len(T) > len(S) and S < T for T in by_elem[min(S)])]
        else:
            groups = [S for S in valid if len(S) == 3]
        covered = {frozenset(p) for S in (valid if cap is None else groups) for p in itertools.combinations(S, 2)}
        pairs = [frozenset(e) for e in G.edges() if frozenset(e) not in covered]
        return groups + pairs

    def step(self, rule, cap=None, rng=None):
        live = [j for j in self.live if self.loose(j)]
        if not live:
            return "closed"
        gs = self.groups(live, cap)
        use = Counter(j for g in gs for j in g)
        lo = {j: self.loose(j) for j in live}
        if any(use[j] > len(lo[j]) for j in live):
            return "stall"
        plan, taken = [], Counter()
        for g in gs:
            bits = []
            for j in sorted(g):
                bits.append(lo[j][taken[j]])
                taken[j] += 1
            plan.append(bits)
        for j in live:
            for b in lo[j][taken[j]:]:
                plan.append([b])
        self.rounds += 1
        new = []
        for bits in plan:
            jid = len(self.bits)
            self.bits.append(list(bits))
            self.nbr.append(set())
            self.parents.append(set())
            for b in bits:
                for o in self.owner[b]:
                    self.nbr[o].add(jid)
                    self.nbr[jid].add(o)
                    self.parents[jid].add(o)
                self.owner[b].append(jid)
            self.round.append(self.rounds)
            self.fresh.append(0)
            self.dem.append(None)
            new.append(jid)
        nxt = self.groups(new, cap)
        demand = Counter(j for g in nxt for j in g)
        info = []
        for jid in new:
            implied = self._reduce(self._mask(self.bits[jid])) == 0
            pf = [self.fresh[o] for o in self.parents[jid]]
            info.append({"j": jid, "p": len(self.parents[jid]), "d": demand[jid], "implied": implied, "parent_fresh": pf})
        ks = rule(self, info, rng)
        for jid, k, inf in zip(new, ks, info):
            if k == 0 and not inf["implied"]:
                raise ValueError("zero fresh bits on a junction whose parity is not implied")
            if k > 0 and inf["implied"]:
                self.forced += 1          # fresh bits under an implied parity: a distinction with one value
            for _ in range(k):
                b = self.nb
                self.nb += 1
                self.bits[jid].append(b)
                self.owner[b] = [jid]
            self.fresh[jid] = k
            self.dem[jid] = inf["d"]
            self._add(jid)
        self.live = [j for j in new if self.fresh[j] > 0]
        return "ok"

    def counts(self):
        c = Counter(self.round)
        return [c[r] for r in range(self.rounds + 1)]

    def offshoots(self):
        c = Counter(self.round[j] for j in range(len(self.bits)) if len(self.parents[j]) == 1)
        return [c[r] for r in range(self.rounds + 1)]

    def check_ideals(self, limit=60000):
        """T1: junction -> its set of offshoots below or equal; a bijection onto the ideals of size <= rounds, rank = size,
        parents = lower covers."""
        n = len(self.bits)
        offs = [v for v in range(n) if len(self.parents[v]) == 1]
        ix = {q: i for i, q in enumerate(offs)}
        I = [0] * n
        for v in range(n):
            m = 0
            for u in self.parents[v]:
                m |= I[u]
            if v in ix:
                m |= 1 << ix[v]
            I[v] = m
        err = Counter()
        seen = set()
        for v in range(n):
            err["rank != size"] += bin(I[v]).count("1") != self.round[v]
            err["built twice"] += I[v] in seen
            seen.add(I[v])
            for u in self.parents[v]:
                err["parent not a lower cover"] += not (I[u] & ~I[v] == 0 and bin(I[v] & ~I[u]).count("1") == 1)
        below = [I[q] & ~(1 << ix[q]) for q in offs]
        frontier, total, missing = {0}, 1, 0
        for size in range(1, self.rounds):          # the last round may be cut short only by a stall, so check below it
            nxt = set()
            for J in frontier:
                for i in range(len(offs)):
                    if not (J >> i) & 1 and (below[i] & ~J) == 0:
                        nxt.add(J | (1 << i))
            total += len(nxt)
            missing += sum(1 for J in nxt if J not in seen)
            frontier = nxt
            if total > limit:
                break
        err["missing ideals"] = missing
        return dict(err), total


def uniform(c):
    return lambda G, info, rng: [c for _ in info]


def floored(inf, k):
    return k if inf["implied"] else max(k, 3 - inf["p"], 1)


def fewest(G, info, rng):
    return [0 if i["implied"] else floored(i, i["d"]) for i in info]


def blind(K):
    return lambda G, info, rng: [floored(i, rng.randint(1, K)) for i in info]


def surplus(q):
    return lambda G, info, rng: [0 if i["implied"] else floored(i, i["d"] + (1 if (i["d"] > 0 and rng.random() < q) else 0))
                                 for i in info]


def run(a, rule, rounds, cap=None, seed=0, max_junctions=8000):
    G = Growth(a)
    rng = random.Random(seed)
    outcome = "alive"
    for _ in range(rounds):
        r = G.step(rule, cap, rng)
        if r != "ok":
            outcome = r
            break
        if len(G.bits) > max_junctions:
            outcome = "big"
            break
    return G, outcome


def part_uniform():
    out = {}
    for cap in (None, 3):
        for a in range(3, 10):
            R = 10 if a <= 4 else 9 if a == 5 else 8
            for c in range(1, a + 4):
                G, outcome = run(a, uniform(c), R, cap, max_junctions=60000)
                stall = G.rounds + 1 if outcome == "stall" else None
                if cap is None:
                    predicted = None if c == a else (2 if c <= a - 2 else 4 if c == a - 1 else 3)
                else:
                    predicted = None if c == a == 3 else (4 if c == a else (2 if c <= a - 2 else 4 if c == a - 1 else 3))
                rec = {"outcome": outcome, "stall round": stall, "predicted stall": predicted, "agrees": stall == predicted,
                       "rounds run": G.rounds}
                if outcome == "alive":
                    rec["counts = C(t + a - 1, a - 1)"] = all(G.counts()[t] == comb(t + a - 1, a - 1) for t in range(G.rounds + 1))
                    if a <= 6:
                        rec["T1 errors"], rec["ideals checked"] = G.check_ideals()
                out[f"cap={cap} a={a} c={c}"] = rec
                print(f"cap={cap} a={a} c={c}", rec["outcome"], rec["rounds run"], file=sys.stderr, flush=True)
    bad = [k for k, v in out.items() if not v["agrees"] or v.get("counts = C(t + a - 1, a - 1)") is False
           or any(v.get("T1 errors", {}).values())]
    return {"cells": len(out), "cells disagreeing with T2 / T3": bad, "detail": out}


def part_fewest():
    out = {}
    for a in range(3, 9):
        G, outcome = run(a, fewest, a + 3)
        out[f"a={a}"] = {"outcome": outcome, "rounds": G.rounds, "counts": G.counts(),
                         "counts = C(a, j)": G.counts() == [comb(a, j) for j in range(a + 1)],
                         "junction sizes": sorted({len(b) for b in G.bits}), "GF(2) rank": len(G.basis),
                         "rank = 2^a - 1": len(G.basis) == 2 ** a - 1, "forced": G.forced,
                         "T1 errors": G.check_ideals()[0]}
    return out


def part_blind():
    out = {}
    for a in (3, 4):
        for K in range(2, 7):
            hist = Counter()
            alive = 0
            forced = 0
            for s in range(200):
                G, outcome = run(a, blind(K), 14, seed=f"referee-blind-{a}-{K}-{s}", max_junctions=2500)
                if outcome == "stall":
                    hist[G.rounds + 1] += 1
                else:
                    alive += 1
                    hist[outcome] += 1
                forced += G.forced > 0
            out[f"a={a} K={K}"] = {"not stalled by round 14": alive, "stall rounds / outcomes": dict(sorted(hist.items(), key=str)),
                                   "runs with fresh bits under an implied parity": forced}
    return out


def part_handover():
    res = Counter()
    fails = []
    for s in range(300):
        rng = random.Random(f"referee-handover-{s}")
        a = rng.choice([3, 4, 5])
        h = rng.randint(1, 4)
        q = rng.choice([0.2, 0.4])
        G = Growth(a)
        ok = True
        for _ in range(h):
            r = G.step(surplus(q), None, rng)
            if r != "ok" or len(G.bits) > 2500:
                ok = False
                break
        if not ok:
            res["ended before the hand-over"] += 1
            continue
        start = G.rounds
        outcome = "alive"
        for _ in range(25):
            r = G.step(fewest, None, rng)
            if r != "ok":
                outcome = r
                break
            if len(G.bits) > 2500:
                outcome = "big"
                break
        offs = G.offshoots()[start + 1:]
        # T4(b): from the second fewest round on, offshoots per round = offshoots of the first fewest round with demand 1
        first = [j for j in range(len(G.bits)) if G.round[j] == start + 1 and len(G.parents[j]) == 1]
        d1 = sum(1 for j in first if G.dem[j] == 1)
        later = offs[1:]
        constant = len(set(later)) <= 1
        res[f"{outcome}, chains {later[0] if later else 0}"] += 1
        if not constant or (later and later[0] != d1):
            fails.append({"seed": s, "a": a, "h": h, "q": q, "offshoots per fewest round": offs, "first-round offshoots with demand 1": d1})
        res["runs checked"] += 1
        res["forced distinctions"] += G.forced
    crossed = {}
    for a in range(3, 8):
        G = Growth(a)
        rule = lambda G_, info, rng, a=a: [k + (1 if G_.rounds == a - 1 else 0) for k in fewest(G_, info, rng)]
        outcome = "alive"
        for _ in range(12):
            r = G.step(rule, None, None)
            if r != "ok":
                outcome = r
                break
            if len(G.bits) > 8000:
                outcome = "big"
                break
        crossed[f"a={a}"] = {"outcome": outcome, "offshoots per round": G.offshoots(), "junctions per round": G.counts()}
    return {"hand-overs": dict(res), "T4b failures": fails, "crossed starts": crossed}


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"uniform": part_uniform, "fewest": part_fewest, "blind": part_blind, "handover": part_handover}[part](),
                     indent=1, default=str))
