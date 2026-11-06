"""Closed braids, their Wirtinger data, and evaluation in the group G.

Conventions
-----------
* A braid on n strands is a list of nonzero integers read from the top
  (index 0) down.  Generator i > 0: the strand at position i-1 crosses OVER the
  strand at position i (the two swap); i < 0: it crosses UNDER.  Positions are
  0-based.
* Arcs: top arc at position q has id q; each crossing starts a new arc on its
  under-strand (ids n, n+1, ...).  The closure identifies the bottom arc at
  position q with top arc q.
* Wirtinger relations (paths composed left to right, basepoint above the
  diagram, each meridian linking the knot +1).  At a crossing of sign +1
      out = over^-1 * in * over,
  at a crossing of sign -1
      out = over * in * over^-1.
  The sign of a crossing is chirality * sign(generator).  chirality = +1 reads
  positive generators as positive crossings; chirality = -1 is the mirror.  The
  counts replayed here are checked not to depend on this choice.
* Seifert longitude based on top arc 0 (start at the top of position 0 and
  follow the knot downwards):
      lambda = x_0^(-writhe) * prod_{undercrossings, in order} over_arc^(sign).
* p-surgery relator: x_0^p * lambda.  The presentation of pi1(S^3_p(K)) used
  everywhere is   < x_0..x_{n-1} | bottom_q * x_q^-1 (q < n), x_0^p lambda >,
  the bottom arcs being words in the top arcs through the crossings.

Independent replay code: written from scratch, standard library only.
"""
from group import MULT, INV, IDENTITY, power


class ClosedBraid:
    def __init__(self, n, word, chirality=1):
        self.n = n
        self.word = list(word)
        self.chirality = chirality
        pos_arc = list(range(n))
        n_arcs = n
        self.crossings = []        # (over_arc, in_arc, out_arc, sign)
        self.level_arcs = []       # arc ids at each position just before word[L]
        last_touch = [-1] * n
        for idx, g in enumerate(self.word):
            i = abs(g)
            assert 1 <= i <= n - 1, (g, n)
            self.level_arcs.append(tuple(pos_arc))
            p, q = i - 1, i
            over_pos, under_pos = (p, q) if g > 0 else (q, p)
            sign = chirality * (1 if g > 0 else -1)
            over, inn, out = pos_arc[over_pos], pos_arc[under_pos], n_arcs
            n_arcs += 1
            self.crossings.append((over, inn, out, sign))
            pos_arc[under_pos] = over      # the over-strand moves across
            pos_arc[over_pos] = out        # the under-strand moves across, new arc
            last_touch[p] = last_touch[q] = idx
        self.level_arcs.append(tuple(pos_arc))
        self.bottom = tuple(pos_arc)
        self.n_arcs = n_arcs
        self.last_touch = last_touch
        self.max_pos = [abs(g) for g in self.word]
        self.writhe = sum(c[3] for c in self.crossings)
        self._build_longitude()

    def _build_longitude(self):
        events, cur, passes = [], 0, 0
        while True:
            for idx, g in enumerate(self.word):
                i = abs(g)
                p, q = i - 1, i
                if cur != p and cur != q:
                    continue
                over_pos, under_pos = (p, q) if g > 0 else (q, p)
                over, _, _, sign = self.crossings[idx]
                if cur == under_pos:
                    events.append((over, sign))
                    cur = over_pos
                else:
                    cur = under_pos
            passes += 1
            if cur == 0:
                break
        if passes != self.n:
            raise ValueError("closure is not a knot (strand permutation not an n-cycle)")
        assert len(events) == len(self.word)
        self.longitude = events

    # ------------------------------------------------------------ evaluation
    def propagate(self, top):
        """Images of all arcs, given the images of the top arcs (codes in G)."""
        img = list(top) + [IDENTITY] * len(self.crossings)
        for over, inn, out, sign in self.crossings:
            o = img[over]
            if sign > 0:
                img[out] = MULT[MULT[INV[o]][img[inn]]][o]
            else:
                img[out] = MULT[MULT[o][img[inn]]][INV[o]]
        return img

    def longitude_value(self, img):
        g = power(img[0], -self.writhe)
        for over, sign in self.longitude:
            g = MULT[g][img[over] if sign > 0 else INV[img[over]]]
        return g

    def surgery_value(self, img, p):
        return MULT[power(img[0], p)][self.longitude_value(img)]

    def relator_values(self, img, p):
        """Values of the n closure relators and of the surgery relator."""
        vals = [MULT[img[self.bottom[q]]][INV[img[q]]] for q in range(self.n)]
        vals.append(self.surgery_value(img, p))
        return vals


# ------------------------------------------------------------- braid words
def trefoil():
    return 2, [1, 1, 1]


def figure_eight_sum(k):
    """(4_1)^#k on 2k+1 strands."""
    word = []
    for i in range(k):
        word += [2 * i + 1, -(2 * i + 2), 2 * i + 1, -(2 * i + 2)]
    return 2 * k + 1, word


BORROMEAN3 = [1, -2, 1, -2, 1, -2]


def fat_crossing(g, size=3):
    """Thin word of a fat crossing of fat strands i, i+1 (bundles of `size`)."""
    i = abs(g)
    b = size * (i - 1)
    word = [b + size + r - 1 - t for r in range(1, size + 1) for t in range(size)]
    if g < 0:
        word = [-x for x in reversed(word)]
    return word


def cabled(word3, offset, size=3):
    thin = [x for g in word3 for x in fat_crossing(g, size)]
    return [(abs(x) + offset) * (1 if x > 0 else -1) for x in thin]


def insert_blocks(base, insertions):
    """Insert blocks into `base`; insertions = [(level, block_word), ...] with
    levels referring to the base word (block goes just before base[level]).
    Returns (new_word, start index of each block in the new word)."""
    order = sorted(range(len(insertions)), key=lambda t: insertions[t][0])
    starts = [None] * len(insertions)
    out, pos = [], 0
    for L in range(len(base) + 1):
        for t in order:
            if insertions[t][0] == L:
                starts[t] = len(out)
                out.extend(insertions[t][1])
        if L < len(base):
            out.append(base[L])
    assert all(s is not None for s in starts)
    return out, starts


def borromean_insertions(base, specs):
    """specs = [(level, thin offset), ...]: insert the 3-cabled Borromean braid."""
    return insert_blocks(base, [(L, cabled(BORROMEAN3, o)) for L, o in specs])
