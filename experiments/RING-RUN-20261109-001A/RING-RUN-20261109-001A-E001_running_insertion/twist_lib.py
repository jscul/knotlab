"""A ring inserted while the twist tube runs (RING-RUN-20261109-001A-E001), on GROW-RUN-20261109-001A's growrun_lib.

The twist torus <(2, 1), (N, 0)> in tube coordinates (GROW-PLAIN-20261109-001B): rings labelled round a cycle, ring L listing E, N, W, S
at cells 0, g, 2g, 3g of its 4g cells; h(L) joins L's E to next(L)'s W, and v(L) joins L's N to prev(prev(L))'s S. Inserting ring R
after ring j rewires h(j) (now j to R), v(next j) (now to j) and v(next next j) (now to R), and adds h(R) and v(R): the next stage is
the twist torus of one more ring. The split says what the three rewired contacts hold at the insertion: "keep" their values, or
"fresh", born anew; the new ring's cells and its two new contacts are born, new open distinctions (A44)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROWRUN = next((ROOT / "proofs/GROW-RUN-20261109-001A").glob("*/"))
sys.path.insert(0, str(GROWRUN))
import growrun_lib as GR  # noqa: E402

N_ = GR.N
LAW = GR.LAW


class TwistTube:
    def __init__(self, labels, g):
        self.labels, self.g = list(labels), g
        self.rows = self.labels

    def build(self):
        labels, g = self.labels, self.g
        K = len(labels)
        idx = {L: k for k, L in enumerate(labels)}
        nxt = {L: labels[(k + 1) % K] for k, L in enumerate(labels)}
        prv = {L: labels[(k - 1) % K] for k, L in enumerate(labels)}
        names, contacts = [], []
        for L in labels:
            names.append(('h', L)); contacts.append((idx[L], 0, idx[nxt[L]], 2 * g, LAW))
            names.append(('v', L)); contacts.append((idx[L], g, idx[prv[prv[L]]], 3 * g, LAW))
        sizes = tuple(4 * g for _ in labels)
        rows_m, Nb, blocks = N_.matrix(sizes, (60,) * len(labels), contacts)
        lay, _, _ = N_.layout(sizes, contacts)
        keys = [None] * Nb
        for c, nm in enumerate(names):
            keys[c] = ('c',) + nm
        for k, L in enumerate(labels):
            for p, b in enumerate(lay[k]):
                if b >= len(contacts):
                    keys[b] = ('o', L, p)
        self.rings, self.idx, self.names, self.contacts, self.sizes = list(labels), idx, names, contacts, sizes
        self.M, self.Nb, self.blocks, self.keys = rows_m, Nb, blocks, keys
        self.pos = {kk: b for b, kk in enumerate(keys)}
        self.nxt, self.prv = nxt, prv
        return self


class Run(GR.Run):
    def insert_ring(self, after, label, split="keep"):
        old = self.tube
        old_val = {k: self.state[b] for b, k in enumerate(old.keys)}
        rewired = {('c', 'h', after), ('c', 'v', old.nxt[after]), ('c', 'v', old.nxt[old.nxt[after]])}
        labels = list(old.labels)
        labels.insert(labels.index(after) + 1, label)
        new = TwistTube(labels, old.g).build()
        st = []
        for k in new.keys:
            if k in rewired:
                st.append(old_val[k] if split == "keep" else self.fresh(k))
            elif k in old_val:
                st.append(old_val[k])
            else:
                st.append(self.fresh(k))
        self.tube, self.state = new, st
