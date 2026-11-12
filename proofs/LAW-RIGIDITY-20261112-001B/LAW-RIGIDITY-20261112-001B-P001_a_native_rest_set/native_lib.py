"""A native rest set (research/LAW-RIGIDITY-20261112-001/preregistration.md, addendum, stage 2).

The shortest cyclic sequences of a base: distinct knots k1..kn and distinct distinctions d1..dn, each ki holding di and d(i+1), of the least
n the base has (the literature's shortest Berge cycles). A law's sum around one is the sum of its signs at those 2n places, mod 2; it does
not change when a distinction is flipped or a knot complemented, and it equals the parity of the disagreements between the two places of
each knot around the sequence, so it can be kept from the literals alone. Rule N0: every shortest sum is 0. Rule N1: every shortest sum is
1. The dissonance is W = 2 x violated knots + 2 x [some shortest sum is wrong]; a sign change is proposed at a violated knot or at a place
on a wrong sequence; the credit rule reads distinctions (UNDRAWN-LEARN-20261111-001's KnotEngine); after each stop the repair flips
distinctions only (A68). Nothing reads a drawing, a face, an order, the target or the examples."""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LAW-RIGIDITY-20261112-001A/LAW-RIGIDITY-20261112-001A-P001_the_two_jobs_apart"))
import jobs_lib as JL  # noqa: E402

UL, J, F, W, C, I = JL.UL, JL.J, JL.F, JL.W, JL.C, JL.I


def shortest_sequences(pt):
    """every shortest cyclic sequence, as a frozenset of its 2n places (knot, distinction)"""
    m = len(pt)
    for n in range(2, m + 1):
        out = set()

        def rec(ks, ds):
            k, d = ks[-1], ds[-1]
            for d2 in pt[k]:
                if d2 == d:
                    continue
                if d2 == ds[0] and len(ks) == n:
                    out.add(frozenset([(ks[i], ds[i]) for i in range(n)] + [(ks[i], ds[i + 1] if i + 1 < n else d2) for i in range(n)]))
                    continue
                if d2 in ds or len(ks) >= n:
                    continue
                for k2 in range(m):
                    if k2 not in ks and d2 in pt[k2]:
                        rec(ks + [k2], ds + [d2])
        for k in range(m):
            for d in pt[k]:
                rec([k], [d])
        if out:
            return n, sorted(out, key=sorted)
    return None, []


class NativeEngine(UL.KnotEngine):
    def __init__(self, K, S, s, x, want):
        super().__init__(K, S, s, x)
        self.want = want
        self.length, seqs = shortest_sequences([list(t) for t in K.pt[:getattr(K, "nl", K.n)]])
        self.seqs = seqs
        self.on = {}
        for c, seq in enumerate(seqs):
            for (k, d) in seq:
                self.on.setdefault((k, self.pt[k].index(d)), []).append(c)
        self.par = [sum(self.L[k][self.pt[k].index(d)] for (k, d) in seq) % 2 for seq in seqs]
        self.nwrong = sum(p != want for p in self.par)
        self.W += 2 * (self.nwrong > 0)

    def _toggled(self, sites):
        t = {}
        for st in sites:
            for c in self.on.get(st, ()):
                t[c] = t.get(c, 0) ^ 1
        return [c for c, b in t.items() if b]

    def delta(self, sites):
        d, nv, dag = UL.KnotEngine.delta(self, sites)
        tg = self._toggled(sites)
        dw = sum((1 - self.par[c] != self.want) - (self.par[c] != self.want) for c in tg)
        return d + 2 * ((self.nwrong + dw > 0) - (self.nwrong > 0)), nv, dag

    def apply(self, sites, d, nv, dag):
        for c in self._toggled(sites):
            self.nwrong += (1 - self.par[c] != self.want) - (self.par[c] != self.want)
            self.par[c] ^= 1
        W.Engine.apply(self, sites, d, nv, dag)

    def learn_sites(self):
        out = set(UL.KnotEngine.learn_sites(self))
        for c, seq in enumerate(self.seqs):
            if self.par[c] != self.want:
                out |= {(k, self.pt[k].index(d)) for (k, d) in seq}
        return sorted(out)

    def snapshot(self):
        return W.Engine.snapshot(self) + (list(self.par), self.nwrong)

    def restore(self, snap):
        W.Engine.restore(self, snap[:-2])
        self.par, self.nwrong = snap[-2], snap[-1]


def space(name):
    if name == "J1":
        return J.Space(1)
    B, T, _ = UL.chosen_undrawn()
    return UL.UndrawnSpace(B, T)


def run(name, want, targets, seed, budget=8_000_000):
    """UNDRAWN-LEARN-20261111-001's run with NativeEngine (rule N0 or N1) and the repair that flips distinctions only"""
    sp = space(name)
    I.probe = F.sturdy_probe_k
    params = dict(C.PARAMS, budget=budget)
    rng = random.Random(seed)
    s, x = sp.start()
    E = NativeEngine(sp.K, sp.S, s, x, want)
    W.m1(E, 0, rng)
    rows = []
    for tg in targets:
        steps, probes, r, stalls, credit = C.learn(E, sp.K, sp.ports, tg, 0, rng, params)
        m = F.read_map_k(sp.K, E.s, sp.ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "map at the stop": m}
        if steps is None:
            row["outcome"] = "not stopped"
        else:
            E.flip(rng.choice(sp.movable))
            w = JL.m1_states(E, 0, rng)
            after = F.read_map_k(sp.K, E.s, sp.ports) if w == 0 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows
