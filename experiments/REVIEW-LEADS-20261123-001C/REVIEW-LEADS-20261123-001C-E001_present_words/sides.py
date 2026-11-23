"""List every side table of the census class (REVIEW-LEADS-20261123-001C pre-registration, "Census class").

usage: sides.py CUT KMAX [IMAX]      (IMAX defaults to 3)

A side has three observer distinctions x1 x2 x3 (exactly one holder each), CUT cut distinctions s1.. (exactly one holder on
this side), I internal distinctions h1.. (one or two holders on this side), 0 <= I <= IMAX, and between 1 and KMAX knots of
arity 3 or 4 with law even, odd or not-all-equal, on distinct sets of distinctions (two knots may hold the same set only with
different laws).  Side table T[x, cut value] = number of completions of the internal distinctions.  Tables are deduplicated
exactly; for each table one structure that makes it is recorded, and a second one in the allocation class if there is one
(x2 and x3 held by one knot, x1 by a different knot).
"""
import sys, json, time, itertools
import numpy as np
import common as c

cut = int(sys.argv[1]); kmax = int(sys.argv[2]); imax = int(sys.argv[3]) if len(sys.argv) > 3 else 3
tag = f'c{cut}_k{kmax}_i{imax}'
t_start = time.time()
NAMES = ['x1', 'x2', 'x3']

def dnames(cut, i):
    return NAMES + [f's{j+1}' for j in range(cut)] + [f'h{j+1}' for j in range(i)]

tables = {}          # key bytes -> dict(T, struct, alloc_struct)
stats = []
CH = 60000
total_structs = 0

for i in range(imax + 1):
    n = 3 + cut + i
    knots = [(mem, law) for ar in (3, 4) for mem in itertools.combinations(range(n), ar) for law in ('even', 'odd', 'nae')]
    nk = len(knots)
    B = np.zeros((nk, n), dtype=np.int8)
    for q, (mem, law) in enumerate(knots):
        B[q, list(mem)] = 1
    idx = np.arange(2 ** n)
    bits = [((idx >> (n - 1 - j)) & 1).astype(np.int8) for j in range(n)]
    A = np.zeros((nk, 2 ** n), dtype=bool)
    for q, (mem, law) in enumerate(knots):
        s = sum(bits[j] for j in mem)
        if law == 'nae': A[q] = (s != 0) & (s != len(mem))
        elif law == 'even': A[q] = (s % 2 == 0)
        else: A[q] = (s % 2 == 1)
    is_alloc_knot = np.array([(1 in mem) and (2 in mem) and (0 not in mem) for mem, law in knots])
    hi = np.array([1] * (3 + cut) + [2] * i, dtype=np.int8)
    names = dnames(cut, i)
    # level-wise generation of knot sets j1<j2<...
    P = np.arange(nk, dtype=np.int32)[:, None]
    cnt = B.copy()
    for m in range(1, kmax + 1):
        uncovered = (cnt == 0).sum(1)
        final = (uncovered == 0)
        S = int(final.sum())
        nt0 = len(tables)
        if S:
            Pf = P[final]
            total_structs += S
            for s0 in range(0, S, CH):
                blk = Pf[s0:s0 + CH]
                ok = A[blk[:, 0]].copy()
                for q in range(1, m): ok &= A[blk[:, q]]
                T = ok.reshape(len(blk), 8, 2 ** cut, 2 ** i).sum(-1).astype(np.int8)
                alloc = is_alloc_knot[blk].any(1)
                flat = T.reshape(len(blk), -1)
                u, first = np.unique(flat, axis=0, return_index=True)
                for fi in first:
                    key = flat[fi].tobytes()
                    e = tables.get(key)
                    if e is None:
                        e = tables[key] = dict(T=T[fi].copy(), struct=None, alloc_struct=None)
                        e['struct'] = (i, [knots[int(q)] for q in blk[fi]])
                if alloc.any():
                    fa = flat[alloc]; ba = blk[alloc]; ta = T[alloc]
                    ua, firsta = np.unique(fa, axis=0, return_index=True)
                    for fi in firsta:
                        key = fa[fi].tobytes()
                        e = tables.get(key)
                        if e is None:
                            e = tables[key] = dict(T=ta[fi].copy(), struct=(i, [knots[int(q)] for q in ba[fi]]), alloc_struct=None)
                        if e['alloc_struct'] is None:
                            e['alloc_struct'] = (i, [knots[int(q)] for q in ba[fi]])
        stats.append(dict(cut=cut, internal=i, knots=m, structures=S, new_tables=len(tables) - nt0, seconds=round(time.time() - t_start, 1)))
        print(stats[-1], flush=True)
        if m == kmax: break
        # extend prefixes (prefix-valid: counts <= hi; remaining knots must be able to cover what is missing)
        newP = []; newC = []
        left = kmax - m - 1                       # knots still to add after this extension
        last = P[:, -1]
        for j in range(nk):
            sel = np.nonzero(last < j)[0]
            if sel.size == 0: continue
            c2 = cnt[sel] + B[j]
            good = (c2 <= hi).all(1)
            if left >= 0:
                unc = (c2 == 0).sum(1)
                good &= (unc <= 4 * left)
            sel = sel[good]
            if sel.size == 0: continue
            newP.append(np.concatenate([P[sel], np.full((sel.size, 1), j, dtype=np.int32)], 1)); newC.append(c2[good])
        if not newP: break
        P = np.concatenate(newP); cnt = np.concatenate(newC)

# ---- write -------------------------------------------------------------------------------------------------------------
keys = list(tables)
def fmt(struct):
    if struct is None: return None
    i, kn = struct
    nm = dnames(cut, i)
    return dict(internal=i, knots=[dict(members=[nm[j] for j in mem], law=law) for mem, law in kn])
Tarr = np.stack([tables[k]['T'] for k in keys]).astype(np.int16)
alloc = np.array([tables[k]['alloc_struct'] is not None for k in keys])
nonempty = Tarr.reshape(len(keys), -1).sum(1) > 0
np.savez_compressed(f'{c.ART}/sides_{tag}.npz', T=Tarr, alloc=alloc, nonempty=nonempty)
json.dump(dict(cut=cut, kmax=kmax, imax=imax, stats=stats,
               structures=[dict(struct=fmt(tables[k]['struct']), alloc_struct=fmt(tables[k]['alloc_struct'])) for k in keys]),
          open(f'{c.ART}/sides_{tag}.json', 'w'))
print(f'cut {cut}, <= {kmax} knots, <= {imax} internal: valid structures {total_structs}; distinct tables {len(keys)} '
      f'(nonempty {int(nonempty.sum())}, in the allocation class {int(alloc.sum())}, nonempty and in class {int((alloc & nonempty).sum())}); '
      f'{time.time() - t_start:.1f}s')
