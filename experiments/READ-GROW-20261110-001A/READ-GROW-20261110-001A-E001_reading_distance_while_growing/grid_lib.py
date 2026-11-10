"""A second, independent code for doubling schedules (READ-GROW-20261110-001A-E001), written without choose_lib, net_lib or
territory_lib, for checking their positives.

Geometry, written out directly. Rings sit at (i, r) on a side x side torus; each has 4g cells at positions 0 .. 4g - 1, read left to
right (position p reads p - 1). Position 0 of ring (i, r) is the contact h(i, r), shared with position 2g of ring (i + 1, r); position g
is the contact v(i, r), shared with position 3g of ring (i, r + 1). Every other position is an own cell. Rule 60: an own cell becomes
itself plus its left neighbour on its ring. Law (12, 12): a contact becomes the sum of its left neighbours on its two rings.
Doubling: ring (i, r) becomes ring (2i, 2r) keeping its own cells; rings (2i + 1, 2r), (2i, 2r + 1), (2i + 1, 2r + 1), and every contact,
are born open. Only born cells of rings with i, r < side / n are tracked (the translations of the original n x n lattice are symmetries),
one bit each, the state one python integer per cell."""


class Grid:
    def __init__(self, n, g):
        self.n, self.g, self.side = n, g, n
        self.nvar, self.vring = 0, []
        self._build()
        self.val = [0] * self.ncell
        self._birth(set())

    # cell numbering: own cells ring by ring, then the contacts h and v of each ring
    def _build(self):
        s, g = self.side, self.g
        L = 4 * g
        self.own_pos = [p for p in range(L) if p % g != 0]
        self.own_index = {}
        k = 0
        for i in range(s):
            for r in range(s):
                for p in self.own_pos:
                    self.own_index[(i, r, p)] = k
                    k += 1
        self.h = {}
        self.v = {}
        for i in range(s):
            for r in range(s):
                self.h[(i, r)] = k
                k += 1
                self.v[(i, r)] = k
                k += 1
        self.ncell = k

    def cell(self, i, r, p):
        """the cell at position p of ring (i, r)"""
        s, g = self.side, self.g
        i, r, p = i % s, r % s, p % (4 * g)
        if p == 0:
            return self.h[(i, r)]
        if p == g:
            return self.v[(i, r)]
        if p == 2 * g:
            return self.h[((i - 1) % s, r)]
        if p == 3 * g:
            return self.v[(i, (r - 1) % s)]
        return self.own_index[(i, r, p)]

    def _birth(self, old):
        d = self.side // self.n
        for i in range(d):
            for r in range(d):
                if (i, r) in old:
                    continue
                for p in self.own_pos:
                    self.val[self.own_index[(i, r, p)]] = 1 << self.nvar
                    self.vring.append((i, r))
                    self.nvar += 1

    def step(self):
        s, g, v = self.side, self.g, self.val
        new = [0] * self.ncell
        for (i, r, p), b in self.own_index.items():
            new[b] = v[b] ^ v[self.cell(i, r, p - 1)]
        for (i, r), c in self.h.items():
            new[c] = v[self.cell(i, r, -1)] ^ v[self.cell(i + 1, r, 2 * g - 1)]
        for (i, r), c in self.v.items():
            new[c] = v[self.cell(i, r, g - 1)] ^ v[self.cell(i, r + 1, 3 * g - 1)]
        self.val = new

    def double(self):
        old_val, old_index = self.val, self.own_index
        old_rings = set()
        self.side *= 2
        self._build()
        self.val = [0] * self.ncell
        for (i, r, p), b in old_index.items():
            self.val[self.own_index[(2 * i, 2 * r, p)]] = old_val[b]
            old_rings.add((2 * i, 2 * r))
        # renumber tracked variables' rings: ring (i, r) is now (2i, 2r)
        self.vring = [(2 * i, 2 * r) for (i, r) in self.vring]
        self._birth(old_rings)

    def ring_mask(self, R):
        m = 0
        for k, o in enumerate(self.vring):
            if o == R:
                m |= 1 << k
        return m

    def contacts_of(self, i, r):
        g = self.g
        return [self.cell(i, r, p) for p in (0, g, 2 * g, 3 * g)]

    def read(self, cap=1000000):
        """{(contact cell, ring): first lag at which it does not bind the ring} over the domain's rings, and the period read"""
        d = self.side // self.n
        pairs = []
        for i in range(d):
            for r in range(d):
                m = self.ring_mask((i, r))
                for c in self.contacts_of(i, r):
                    pairs.append((c, (i, r), m))
        saved = list(self.val)
        cur = list(self.val)
        fails = {}
        power, lam = 1, 0
        keep = self.val
        for t in range(1, cap + 1):
            self.val = cur
            self.step()
            cur = self.val
            for c, R, m in pairs:
                if (c, R) not in fails and not (cur[c] & m):
                    fails[(c, R)] = t
            if cur == saved:
                self.val = keep
                return fails, t
            lam += 1
            if lam == power:
                saved, power, lam = list(cur), power * 2, 0
        self.val = keep
        return fails, None

    def hearers(self):
        """original rings (a, b) != (0, 0), in original coordinates, one of whose own cells depends on ring (0, 0)'s first row"""
        k = self.side // self.n
        m = self.ring_mask((0, 0))
        out = set()
        for a in range(self.n):
            for b in range(self.n):
                if (a, b) == (0, 0):
                    continue
                if any(self.val[self.own_index[(a * k, b * k, p)]] & m for p in self.own_pos):
                    out.add((a, b))
        return out


def play(n, g, runs):
    """the schedule from the open n x n tube; each stage read at its doubling; first hearing lag of every original ring"""
    G = Grid(n, g)
    G.double()
    f, per = G.read()
    stages = [{"lag": 0, "side": G.side, "balanced": not f, "period": per}]
    first, t = {}, 0
    for P in runs:
        for _ in range(P):
            G.step()
            t += 1
            for Y in G.hearers():
                first.setdefault(Y, t)
        G.double()
        f, per = G.read()
        stages.append({"lag": t, "side": G.side, "balanced": not f, "period": per,
                       "first failure": min(f.values()) if f else None})
        if f:
            break
    return {"n": n, "g": g, "runs": list(runs), "stages": stages,
            "every stage balanced": all(s["balanced"] for s in stages) and len(stages) == len(runs) + 1,
            "first hearing lag": {"%d,%d" % Y: lag for Y, lag in sorted(first.items())}}
