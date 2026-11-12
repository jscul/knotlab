"""A native grade for rigidity (research/NATIVE-GRADE-20261112-001/preregistration.md).

LAW-RIGIDITY-20261112-001B's shortest cyclic sequences and the law's sum around each. Rule GE, value-free and graded: the learner rests
where all shortest sums are equal, whatever the value, and is charged 2 for each shortest sequence it would have to change to get there,
W = 2 x violated knots + 2 x min(#sums 0, #sums 1). A sign change is proposed at a violated knot or at a place on a sequence of the
smaller kind (both kinds at a tie). The repair after each stop is the learner's own M1, free to re-sign (A68 is not used). Nothing reads a
drawing, a face, an order, the target, the examples, or a value chosen for the sums."""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LAW-RIGIDITY-20261112-001B/LAW-RIGIDITY-20261112-001B-P001_a_native_rest_set"))
import native_lib as N  # noqa: E402

UL, J, F, W, C, I = N.UL, N.J, N.F, N.W, N.C, N.I


class GradeEngine(N.NativeEngine):
    def __init__(self, K, S, s, x):
        super().__init__(K, S, s, x, 0)
        self.W -= 2 * (self.nwrong > 0)
        self.nseq = len(self.seqs)
        self.n1 = sum(self.par)
        self.W += 2 * min(self.n1, self.nseq - self.n1)

    def _cost(self, n1):
        return 2 * min(n1, self.nseq - n1)

    def delta(self, sites):
        d, nv, dag = UL.KnotEngine.delta(self, sites)
        dn = sum(1 - 2 * self.par[c] for c in self._toggled(sites))
        return d + self._cost(self.n1 + dn) - self._cost(self.n1), nv, dag

    def apply(self, sites, d, nv, dag):
        for c in self._toggled(sites):
            self.n1 += 1 - 2 * self.par[c]
            self.par[c] ^= 1
        W.Engine.apply(self, sites, d, nv, dag)

    def learn_sites(self):
        out = set(UL.KnotEngine.learn_sites(self))
        n0 = self.nseq - self.n1
        for c, seq in enumerate(self.seqs):
            if (self.par[c] == 1 and self.n1 <= n0 and self.n1 > 0) or (self.par[c] == 0 and n0 <= self.n1 and n0 > 0):
                out |= {(k, self.pt[k].index(d)) for (k, d) in seq}
        return sorted(out)

    def snapshot(self):
        return W.Engine.snapshot(self) + (list(self.par), self.n1)

    def restore(self, snap):
        W.Engine.restore(self, snap[:-2])
        self.par, self.n1 = snap[-2], snap[-1]


def run(name, targets, seed, budget=8_000_000):
    """UNDRAWN-LEARN-20261111-001's run with GradeEngine and the free repair (W.m1)"""
    sp = N.space(name)
    I.probe = F.sturdy_probe_k
    params = dict(C.PARAMS, budget=budget)
    rng = random.Random(seed)
    s, x = sp.start()
    E = GradeEngine(sp.K, sp.S, s, x)
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
            w = W.m1(E, 0, rng)
            after = F.read_map_k(sp.K, E.s, sp.ports) if w == 0 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows
