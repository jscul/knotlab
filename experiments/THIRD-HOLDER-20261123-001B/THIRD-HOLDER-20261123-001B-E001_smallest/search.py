"""Seeded search (THIRD-HOLDER-20261123-001B pre-registration, "Seeded search"): 2,000,000 drawn sides per class of up to 9
knots, seed 2026112321, pooled as in REVIEW-LEADS-20261123-001C's targeted.py (mode "free"), pools capped at 20,000
distinct tables.  The pools are written in the format of sides.py and paired by pairs_c.py.

usage: search.py CLASS RUN [DRAWS_PER_RUN]
  CLASS L or S.  The 2,000,000 lawful sides of a class are drawn in consecutive runs (RUN = 0, 1, ...); the generator state
  is saved after each run and the next run continues the same stream.  The last run writes the pools.

A drawn side: k knots, k uniform in 2..9, each of 3 or 4 places (uniform), laws even / odd / not-all-equal (uniform); a cut
of 1 or 2 shared distinctions (uniform; each with one holder on this side); observer distinctions with one old holder
(class L) or one or two (class S, uniform for each); I internal distinctions, at most 9, each with one to three holders, the
holder counts filling exactly the remaining places (I uniform over its feasible range; the extra holders put one at a time
on a uniform internal distinction still below three); distinctions placed on uniform distinct knots with free places
(observers first, then the others in a uniform order).  A draw that leaves a free place or cannot place a distinction is
discarded and does not count.  Pools: per class and cut size, the first 20,000 distinct non-empty side tables in draw order.
"""
import sys, os, json, time, pickle
import numpy as np
import common as c

cls = sys.argv[1]; run = int(sys.argv[2]); per_run = int(sys.argv[3]) if len(sys.argv) > 3 else 500_000
SEED = 2026112321; TOTAL = 2_000_000; CAP = 20_000
t0 = time.time()
state_f = f'{c.ART}/search_{cls}_state.pkl'
LAWS = ('even', 'odd', 'nae'); LAWI = {l: i for i, l in enumerate(LAWS)}

class U:
    """Uniforms from one seeded numpy generator, drawn in blocks (the stream is fixed by the seed)."""
    def __init__(s, rng): s.rng = rng; s.buf = rng.random(1 << 16); s.i = 0
    def u(s):
        if s.i >= len(s.buf): s.buf = s.rng.random(1 << 16); s.i = 0
        v = s.buf[s.i]; s.i += 1; return v
    def integer(s, lo, hi):          # uniform in lo..hi-1
        return lo + int(s.u() * (hi - lo))
    def sample(s, pool, h):          # h distinct elements of the list pool, uniform
        pool = list(pool); out = []
        for _ in range(h):
            j = s.integer(0, len(pool)); out.append(pool.pop(j))
        return out

if run == 0:
    st = dict(rng=np.random.default_rng(SEED), drawn=0, attempts=0, pools={1: {}, 2: {}}, distinct={1: {}, 2: {}},
              order_first={1: 0, 2: 0}, empty=0)
    st['U'] = U(st['rng'])
else:
    st = pickle.load(open(state_f, 'rb'))
Ug = st['U']

def gen():
    k = Ug.integer(2, 10)
    sizes = [3 + Ug.integer(0, 2) for _ in range(k)]
    cut = 1 + Ug.integer(0, 2)
    obs = [1, 1, 1] if cls == 'L' else [1 + Ug.integer(0, 2) for _ in range(3)]
    R = sum(sizes) - sum(obs) - cut
    if R < 0: return None
    lo = (R + 2) // 3; hi = min(R, 9)
    if lo > hi: return None
    I = Ug.integer(lo, hi + 1)
    h = [1] * I
    for _ in range(R - I):
        cand = [j for j in range(I) if h[j] < 3]
        h[cand[Ug.integer(0, len(cand))]] += 1
    cap = list(sizes); mem = [[] for _ in range(k)]
    def place(dist, hh):
        free = [q for q in range(k) if cap[q] > 0]
        if len(free) < hh: return False
        for q in Ug.sample(free, hh):
            mem[q].append(dist); cap[q] -= 1
        return True
    for dist in range(3):
        if not place(dist, obs[dist]): return None
    rest = list(range(3, 3 + cut + I)); hold = [1] * cut + h
    order = Ug.sample(range(len(rest)), len(rest))
    for q in order:
        if not place(rest[q], hold[q]): return None
    if any(cap): return None
    laws = [Ug.integer(0, 3) for _ in range(k)]
    return cut, I, [(len(m), laws[q], sorted(m)) for q, m in enumerate(mem)], h, obs

# ---- tables: bitsets of allowed words per layout (cut, I); bit w of a word index: x (3 bits, x1 high), cut values, internals low
_layout = {}
def layout(cut, I):
    key = (cut, I)
    if key not in _layout:
        n = 3 + cut + I; NB = 1 << n
        w = np.arange(NB)
        def bitpos(j):
            if j < 3: return cut + I + 2 - j
            if j < 3 + cut: return I + (cut - 1 - (j - 3))
            return I - 1 - (j - 3 - cut)
        bits = [((w >> bitpos(j)) & 1) for j in range(n)]
        _layout[key] = (n, bits, {})
    return _layout[key]

def knot_bits(cut, I, ar, law, mem):
    n, bits, cache = layout(cut, I)
    key = (law, tuple(mem))
    b = cache.get(key)
    if b is None:
        s = sum(bits[j] for j in mem)
        ok = ((s != 0) & (s != ar)) if law == 2 else ((s % 2) == (0 if law == 0 else 1))
        b = np.packbits(ok.astype(np.uint8), bitorder='little')
        cache[key] = b
    return b

def table(cut, I, knots):
    ok = None
    for ar, law, mem in knots:
        b = knot_bits(cut, I, ar, law, mem)
        ok = b.copy() if ok is None else (ok & b)
    allowed = np.unpackbits(ok, bitorder='little')[:1 << (3 + cut + I)]
    return allowed.reshape(8, 1 << cut, 1 << I).sum(-1).astype(np.int32)

target = min(TOTAL, st['drawn'] + per_run)
while st['drawn'] < target:
    st['attempts'] += 1
    g = gen()
    if g is None: continue
    st['drawn'] += 1
    cut, I, knots, h, obs = g
    T = table(cut, I, knots)
    if T.sum() == 0: st['empty'] += 1; continue
    key = T.tobytes()
    if key in st['distinct'][cut]: continue
    extra = sum(max(0, v - 2) for v in h)
    st['distinct'][cut][key] = (T, I, knots, extra, st['drawn'])      # every distinct table (for the exploratory extension)
    pool = st['pools'][cut]
    if len(pool) < CAP:
        pool[key] = (T, I, knots, extra, st['drawn'])
print(f'class {cls} run {run}: lawful sides drawn {st["drawn"]} of {TOTAL} (attempts {st["attempts"]}), empty tables {st["empty"]}, '
      f'distinct non-empty tables cut 1: {len(st["distinct"][1])}, cut 2: {len(st["distinct"][2])}; pools {len(st["pools"][1])}, {len(st["pools"][2])}; '
      f'{time.time() - t0:.0f}s', flush=True)
if st['drawn'] < TOTAL:
    pickle.dump(st, open(state_f, 'wb'))
else:
    info = {}
    for cut, which in ((1, 'pool'), (2, 'pool'), (1, 'all'), (2, 'all')):
        pool = st['pools'][cut] if which == 'pool' else st['distinct'][cut]; keys = list(pool)
        N = len(keys)
        T = np.stack([pool[k][0] for k in keys]).astype(np.int32)
        KN = np.full((N, 9, 6), -1, dtype=np.int8)
        for t, k in enumerate(keys):
            for q, (ar, law, mem) in enumerate(pool[k][2]):
                KN[t, q, 0] = ar; KN[t, q, 1] = law; KN[t, q, 2:2 + ar] = mem
        tag = f'search_{cls}_c{cut}' + ('' if which == 'pool' else '_all')
        np.savez_compressed(f'{c.ART}/sides_{tag}.npz', T=T, alloc=np.zeros(N, bool), nonempty=np.ones(N, bool),
                            internal=np.array([pool[k][1] for k in keys], np.int8), knots=np.array([len(pool[k][2]) for k in keys], np.int8),
                            extra=np.array([pool[k][3] for k in keys], np.int8), structs=KN, draw_index=np.array([pool[k][4] for k in keys], np.int64))
        info[tag] = dict(tables=N, distinct_tables_all_draws=len(st['distinct'][cut]),
                         last_table_at_draw=int(max(pool[k][4] for k in keys)) if keys else None)
        json.dump(dict(cls=cls, cut=cut, seed=SEED, lawful_sides=st['drawn'], attempts=st['attempts'], empty_tables=st['empty'], cap=CAP,
                       which=('the pool: first 20,000 distinct tables in draw order' if which == 'pool' else
                              'every distinct table of the 2,000,000 draws (exploratory extension beyond the cap)'),
                       **info[tag], note='structures in the npz as in sides.py (members 0..2 x1..x3, then cut, then internal)'),
                  open(f'{c.ART}/sides_{tag}.json', 'w'), indent=1)
    if os.path.exists(state_f): os.remove(state_f)
    print('pools written', info)
