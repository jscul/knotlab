"""Growth while running (GROW-RUN-20261109-001A), on SEPARATE-20261108-001A's net_lib.

A tube is the n x m square torus of equally spaced rule-60 rings with law (12, 12) contacts (GROW-NET-20261108-001A): ring (i, r) for i in
Z_n round the loop and r in a cyclic list of row labels, listing E, N, W, S at cells 0, g, 2g, 3g of its 4g cells; h(i, r) joins (i, r)
E to (i + 1, r) W, and v(i, r) joins (i, r) N to (i, next r) S. Cells are named by keys (('o', ring, cell) for own cells, ('c', kind,
i, r) for contacts), so that a network and the one a band turns it into can be compared cell by cell.

A Run reads the whole history as one space-time law (TIME-KNOTS-20261107-001A): every cell holds the set, mod 2, of born cells its
value depends on. The first row is born at lag 0; a band inserted at lag t0 is born there, its rings' cells new open distinctions. A
contact binds ring X at a lag when its value depends on one of X's own born cells (A32). Inserting a band after row r turns v(i, r)
into the contact of (i, r) with the new ring (i, r*) and adds v(i, r*) joining (i, r*) to (i, next r); the split says what the two
contacts hold at t0: "lower" (v(i, r) keeps the old value, v(i, r*) is new), "upper" (the reverse), "fresh" (both new) or "copy"
(both the old value)."""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import net_lib as N  # noqa: E402
LAW = (12, 12)

class Tube:
    """rows: cyclic list of row labels; ring (i, r); contacts named ('h', i, r), ('v', i, r): v(i, r) joins (i, r) N to (i, next r) S"""
    def __init__(self, n, rows, g):
        self.n, self.rows, self.g = n, list(rows), g
    def build(self):
        n, rows, g = self.n, self.rows, self.g
        rings = [(i, r) for r in rows for i in range(n)]
        idx = {R: k for k, R in enumerate(rings)}
        nxt = {r: rows[(k + 1) % len(rows)] for k, r in enumerate(rows)}
        prv = {r: rows[(k - 1) % len(rows)] for k, r in enumerate(rows)}
        names, contacts = [], []
        for r in rows:
            for i in range(n):
                # h(i, r): (i, r) E (pos 0) -- (i+1, r) W (pos 2g)
                names.append(('h', i, r)); contacts.append((idx[(i, r)], 0, idx[((i + 1) % n, r)], 2 * g, LAW))
                # v(i, r): (i, r) N (pos g) -- (i, nxt r) S (pos 3g)
                names.append(('v', i, r)); contacts.append((idx[(i, r)], g, idx[(i, nxt[r])], 3 * g, LAW))
        sizes = tuple(4 * g for _ in rings)
        rows_m, Nb, blocks = N.matrix(sizes, (60,) * len(rings), contacts)
        lay, _, _ = N.layout(sizes, contacts)
        keys = [None] * Nb
        for c, nm in enumerate(names):
            keys[c] = ('c',) + nm
        for k, R in enumerate(rings):
            for p, b in enumerate(lay[k]):
                if b >= len(contacts):
                    keys[b] = ('o', R, p)
        self.rings, self.idx, self.names, self.contacts, self.sizes = rings, idx, names, contacts, sizes
        self.M, self.Nb, self.blocks, self.keys = rows_m, Nb, blocks, keys
        self.pos = {kk: b for b, kk in enumerate(keys)}
        return self

class Run:
    """forward exact dependence: state[b] = bitset of variables; variables are born cells"""
    def __init__(self, tube):
        self.t = 0
        self.tube = tube.build()
        self.nvar = 0
        self.vkey = []
        self.owner = []   # variable -> ('own', ring) or ('con', name)
        self.state = [self.fresh(k) for k in self.tube.keys]
    def fresh(self, key):
        v = 1 << self.nvar
        self.nvar += 1
        self.owner.append(('own', key[1]) if key[0] == 'o' else ('con', key[1:]))
        self.vkey.append(key)
        return v
    def step(self):
        M, s = self.tube.M, self.state
        new = []
        for row in M:
            v, x = 0, row
            while x:
                low = x & -x
                v ^= s[low.bit_length() - 1]
                x ^= low
            new.append(v)
        self.state = new
        self.t += 1
    def insert_band(self, after, label, split="lower"):
        """insert row `label` after row `after`; split: which contact keeps the old v cell's value
        lower: v(i, after) (now (i, after)-(i, label)) keeps it, v(i, label) fresh; upper: v(i, label) takes it, v(i, after) fresh;
        fresh: both fresh; copy: both take it"""
        old = self.tube
        old_val = {k: self.state[b] for b, k in enumerate(old.keys)}
        rows = list(old.rows)
        rows.insert(rows.index(after) + 1, label)
        new = Tube(old.n, rows, old.g).build()
        st = []
        for k in new.keys:
            if k[0] == 'o':
                st.append(old_val[k] if k in old_val else self.fresh(k))
            else:
                kind, i, r = k[1], k[2], k[3]
                if kind == 'h':
                    st.append(old_val[k] if k in old_val else self.fresh(k))
                elif r == after:
                    st.append(old_val[k] if split in ('lower', 'copy') else self.fresh(k))
                elif r == label:
                    st.append(old_val[('c', 'v', i, after)] if split in ('upper', 'copy') else self.fresh(k))
                else:
                    st.append(old_val[k])
        self.tube, self.state = new, st
    def ringmask(self, R):
        m = 0
        for v, o in enumerate(self.owner):
            if o == ('own', R):
                m |= 1 << v
        return m

def orbit_rows(M, start, cap=200000):
    return N.orbit(M, start, cap)

def binds_forever(run, c_key):
    """does contact c bind both of its rings at every lag from now on (network fixed from now): exact via the row orbit"""
    tb = run.tube
    c = tb.pos[c_key]
    ra, pa, rb, pb, law = tb.contacts[c]
    masks = [run.ringmask(tb.rings[ra]), run.ringmask(tb.rings[rb])]
    o = orbit_rows(tb.M, 1 << c)
    if o is None:
        return None
    seq, T1, p = o
    first_fail = [None, None]
    for k, row in enumerate(seq):
        v, x = 0, row
        while x:
            low = x & -x
            v ^= run.state[low.bit_length() - 1]
            x ^= low
        for j in (0, 1):
            if first_fail[j] is None and not (v & masks[j]):
                first_fail[j] = k + 1
    return first_fail, T1, p


def footprint(run, R):
    """{own-cell key of ring R: the cell keys whose value depends on it now}"""
    out = {}
    for v, k in enumerate(run.vkey):
        if k[0] == 'o' and k[1] == R:
            out[k] = frozenset(run.tube.keys[b] for b, s in enumerate(run.state) if s >> v & 1)
    return out


def brute_values(n, m, g, T0, split, horizon, flips, seed):
    """an independent check of the dependence sets: run actual bit values from a random first row (and random bits for the band
    at T0), once as drawn and once with one born cell flipped, and return for each flipped cell the (lag, cell key) pairs whose values
    differ; by linearity these are exactly the cells whose dependence set holds the flipped cell"""
    rng = random.Random(seed)

    def simulate(flip):
        tube = Tube(n, list(range(m)), g).build()
        bits = {k: rng_first[k] for k in tube.keys}
        if flip[0] == 0:
            bits[flip[1]] ^= 1
        out = {}
        for t in range(1, horizon + 1):
            if t - 1 == T0:
                rows = list(tube.rows)
                rows.insert(rows.index(0) + 1, 0.5)
                new = Tube(n, rows, g).build()
                nb = {}
                for k in new.keys:
                    if k in bits and not (k[0] == 'c' and k[1] == 'v' and k[3] == 0 and split in ('upper', 'fresh')):
                        nb[k] = bits[k]
                    elif k[0] == 'c' and k[1] == 'v' and k[3] == 0.5 and split in ('upper', 'copy'):
                        nb[k] = bits[('c', 'v', k[2], 0)]
                    else:
                        nb[k] = rng_band[k] ^ (1 if flip[0] == 1 and flip[1] == k else 0)
                tube, bits = new, nb
            vec = [bits[k] for k in tube.keys]
            nxt = []
            for row in tube.M:
                v, x = 0, row
                while x:
                    low = x & -x
                    v ^= vec[low.bit_length() - 1]
                    x ^= low
                nxt.append(v)
            bits = {k: nxt[b] for b, k in enumerate(tube.keys)}
            out[t] = dict(bits)
        return out
    tube0 = Tube(n, list(range(m)), g).build()
    rng_first = {k: rng.randrange(2) for k in tube0.keys}
    rows = list(tube0.rows)
    rows.insert(1, 0.5)
    tube1 = Tube(n, rows, g).build()
    rng_band = {k: rng.randrange(2) for k in tube1.keys}
    base = simulate((None, None))
    res = {}
    for flip in flips:
        other = simulate(flip)
        res[flip] = {(t, k) for t in base for k in base[t] if base[t][k] != other[t][k]}
    return res
