"""Doubling schedules read on one territory (CROSS-WHY-20261110-001B).

The network of GROW-CHOOSE-20261109-001A-E001's choose_lib (Tube2: a square tube of rule-60 rings of 4g cells with law (12, 12)
contacts) under the doubling law of BIRTH-RULE-20261109-001A-E001's double(run, t, "open"): at a doubling every ring splits into a
2 x 2 block, the old ring keeping its own cells, every contact and every cell of a new ring born open. A schedule is the list of run
lengths between doublings, the first doubling at lag 0 from the open n x n tube.

Exact reduction (ticket B, Lemma 1): the law, the open start and the doubling commute with the translations of the original n x n
lattice, so a contact binds a ring exactly when its translate binds the translate. Only the rings of one fundamental domain, positions
[0, side/n) x [0, side/n), are read, and only their born cells are tracked; the state is a numpy array of bit words, one row per cell,
one bit per tracked born cell. Every row of the step matrix has exactly two entries, so a step is two gathers and an XOR."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth"))
import choose_lib as CL  # noqa: E402

ONE = np.uint64(1)


class NRun:
    def __init__(self, g, n=3):
        self.g, self.n = g, n
        self.tube = CL.Tube2(list(range(n)), list(range(n)), g).build()
        self.vowner, self.W = [], 1
        self.state = np.zeros((len(self.tube.keys), 1), dtype=np.uint64)
        self._index()
        self._born(set())

    def _index(self):
        A, B = [], []
        for row in self.tube.M:
            idx, x = [], row
            while x:
                low = x & -x
                idx.append(low.bit_length() - 1)
                x ^= low
            assert len(idx) == 2
            A.append(idx[0])
            B.append(idx[1])
        self.A, self.B = np.array(A), np.array(B)
        k, m = len(self.tube.cols) // self.n, len(self.tube.rows) // self.n
        cs, rs = set(self.tube.cols[:k]), set(self.tube.rows[:m])
        self.domain = [R for R in self.tube.rings if R[0] in cs and R[1] in rs]

    def _born(self, old_rings):
        dom = set(self.domain)
        for b, k in enumerate(self.tube.keys):
            if k[0] == 'o' and k[1] not in old_rings and k[1] in dom:
                v = len(self.vowner)
                self.vowner.append(k[1])
                if v >= 64 * self.W:
                    self.state = np.concatenate([self.state, np.zeros_like(self.state)], axis=1)
                    self.W *= 2
                self.state[b, v // 64] |= ONE << np.uint64(v % 64)

    def step(self):
        self.state = self.state[self.A] ^ self.state[self.B]

    def double(self, t):
        old = self.tube
        old_rings = set(old.rings)
        cols, rows = [], []
        for x in old.cols:
            cols += [x, (t, 'c', x)]
        for x in old.rows:
            rows += [x, (t, 'r', x)]
        new = CL.Tube2(cols, rows, self.g).build()
        st = np.zeros((len(new.keys), self.W), dtype=np.uint64)
        for b, k in enumerate(new.keys):
            if k[0] == 'o' and k[1] in old_rings:
                st[b] = self.state[old.pos[k]]
        self.tube, self.state = new, st
        self._index()
        self._born(old_rings)
        return old_rings

    def mask(self, R):
        m = np.zeros(self.W, dtype=np.uint64)
        for v, o in enumerate(self.vowner):
            if o == R:
                m[v // 64] |= ONE << np.uint64(v % 64)
        return m

    def read(self, restricted=False, cap=1000000):
        """{(contact, domain ring): first lag after now at which the contact does not bind the ring}, and the period read: the stage
        fixed from now, through a full cycle of the state (Brent). restricted: each ring's parts kept on its own cells only."""
        tb = self.tube
        rl = list(self.domain)
        rpos = {R: i for i, R in enumerate(rl)}
        masks = np.stack([self.mask(R) for R in rl])
        cidx, midx, keys = [], [], []
        for c, (ra, pa, rb, pb, law) in enumerate(tb.contacts):
            for r in (ra, rb):
                R = tb.rings[r]
                if R in rpos:
                    cidx.append(c)
                    midx.append(rpos[R])
                    keys.append((c, R))
        cidx, Mp = np.array(cidx), masks[np.array(midx)]
        s = self.state.copy()
        if restricted:
            for b, k in enumerate(tb.keys):
                s[b] = s[b] & masks[rpos[k[1]]] if (k[0] == 'o' and k[1] in rpos) else 0
        fails, alive = {}, np.ones(len(keys), dtype=bool)
        saved, power, lam = s.copy(), 1, 0
        for t in range(1, cap + 1):
            s = s[self.A] ^ s[self.B]
            bound = (s[cidx] & Mp).any(axis=1)
            for i in np.nonzero(alive & ~bound)[0]:
                fails[keys[i]] = t
            alive &= bound
            if np.array_equal(s, saved):
                return fails, t
            lam += 1
            if lam == power:
                saved, power, lam = s.copy(), power * 2, 0
        return fails, None

    def own_rank(self, R):
        """rank over GF(2) of ring R's parts on its own cells, and its number of own cells"""
        m = self.mask(R)
        rows = []
        for b, k in enumerate(self.tube.keys):
            if k[0] == 'o' and k[1] == R:
                rows.append(int.from_bytes((self.state[b] & m).tobytes(), 'little'))
        piv, r = {}, 0
        for v in rows:
            while v:
                h = v.bit_length() - 1
                if h in piv:
                    v ^= piv[h]
                else:
                    piv[h] = v
                    r += 1
                    break
        return r, len(rows)

    def originals_hearing(self):
        """the original rings other than (0, 0) one of whose own cells depends now on (0, 0)'s first-row cells"""
        m = self.mask((0, 0))
        out = set()
        for b, k in enumerate(self.tube.keys):
            if k[0] == 'o' and k[1] != (0, 0) and isinstance(k[1][0], int) and isinstance(k[1][1], int) and (self.state[b] & m).any():
                out.add(k[1])
        return out


def play(g, runs, n=3, stop_at_failure=True, restricted=False):
    """the schedule from the open n x n tube: doubling at lag 0, then each run, then a doubling; each stage read at its doubling lag"""
    r = NRun(g, n)
    t, first_cross, heard = 0, None, set()
    r.double(0)
    stages = []
    f, per = r.read()
    stages.append({"lag": 0, "side": len(r.tube.cols), "balanced": not f, "period": per})
    for P in runs:
        for _ in range(P):
            r.step()
            t += 1
            h = r.originals_hearing()
            if h and first_cross is None:
                first_cross = t
            heard |= h
        old = r.double(t)
        f, per = r.read()
        st = {"lag": t, "side": len(r.tube.cols), "balanced": not f, "period": per,
              "first failure": min(f.values()) if f else None,
              "failing rings": len({R for c, R in f}), "failing rings born here": len({R for c, R in f if R not in old})}
        if restricted and f:
            fr, _ = r.read(restricted=True)
            st["kind"] = "internal" if fr else "heard"
        stages.append(st)
        if f and stop_at_failure:
            break
    return {"g": g, "n": n, "runs": list(runs), "first crossing lag": first_cross,
            "original rings hearing (0, 0)": sorted(map(str, heard)), "stages": stages,
            "every stage balanced": all(s["balanced"] for s in stages) and len(stages) == len(runs) + 1}
