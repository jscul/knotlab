"""Listing of a census class in parts (for sides of 5 knots), merged into one table list in the format of sides.py.

usage: sides_parts.py CLASS CUT KMAX IMAX HMAX NPARTS P0 P1
  runs sides_enum for the parts P0 .. P1-1 of NPARTS (structures whose first knot index is the part modulo NPARTS) and saves
  them as sides_<tag>_part<P0>_<P1>.npz; with P0 = P1 = NPARTS the saved part files are merged into sides_<tag>.npz (tables
  deduplicated, keeping for each the structure with the fewest knots, then the fewest extra holders).
"""
import sys, json, subprocess, time, struct, glob, os
import numpy as np
import common as c

cls = sys.argv[1]; cut = int(sys.argv[2]); kmax = int(sys.argv[3]); imax = int(sys.argv[4]); hmax = int(sys.argv[5])
nparts = int(sys.argv[6]); p0 = int(sys.argv[7]); p1 = int(sys.argv[8])
obsmax = {'L': 1, 'S': 2}[cls]
tag = f'{cls}_c{cut}_k{kmax}_i{imax}_h{hmax}'
t0 = time.time()

def parse(binf):
    raw = open(binf, 'rb').read()
    N, K = struct.unpack_from('<ii', raw, 0); off = 8
    T = np.frombuffer(raw, dtype=np.uint8, count=N * 8 * K, offset=off).reshape(N, 8, K).astype(np.int16); off += N * 8 * K
    raw_i = np.frombuffer(raw, dtype=np.int32, offset=off)
    I_arr = np.zeros(N, np.int8); nk = np.zeros(N, np.int8); ex = np.zeros(N, np.int8); KN = np.full((N, kmax, 6), -1, np.int8)
    q = 0
    for t in range(N):
        I_arr[t], nk[t], ex[t] = raw_i[q], raw_i[q + 1], raw_i[q + 2]; q += 3
        n_ = int(nk[t]); KN[t, :n_] = raw_i[q:q + 6 * n_].reshape(n_, 6); q += 6 * n_
    return T, I_arr, nk, ex, KN

if p0 < nparts:
    allstats = []
    for part in range(p0, p1):
        binf = f'{c.ART}/sides_{tag}_p{part}.bin'
        p = subprocess.run([f'{c.ART}/sides_enum', str(cut), str(kmax), str(imax), str(obsmax), str(hmax), binf, str(part), str(nparts)],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        st = [json.loads(l) for l in p.stdout.strip().splitlines()]
        T, I_arr, nk, ex, KN = parse(binf); os.remove(binf)
        np.savez_compressed(f'{c.ART}/sides_{tag}_part{part}.npz', T=T, internal=I_arr, knots=nk, extra=ex, structs=KN)
        json.dump(st, open(f'{c.ART}/sides_{tag}_part{part}.json', 'w'))
        print(f'part {part}: structures {st[-1]["structures"]}, tables {st[-1]["tables"]}, {time.time() - t0:.0f}s', flush=True)
else:
    Ts = []; Is = []; nks = []; exs = []; KNs = []; total = 0; stats = []
    for part in range(nparts):
        d = np.load(f'{c.ART}/sides_{tag}_part{part}.npz')
        st = json.load(open(f'{c.ART}/sides_{tag}_part{part}.json')); stats.append(st); total += st[-1]['structures']
        Ts.append(d['T']); Is.append(d['internal']); nks.append(d['knots']); exs.append(d['extra']); KNs.append(d['structs'])
    T = np.concatenate(Ts); I_arr = np.concatenate(Is); nk = np.concatenate(nks); ex = np.concatenate(exs); KN = np.concatenate(KNs)
    flat = T.reshape(len(T), -1)
    U, inv = np.unique(flat, axis=0, return_inverse=True); inv = inv.reshape(-1)
    order = np.lexsort((ex, nk, inv))
    first = np.ones(len(order), bool); first[1:] = inv[order][1:] != inv[order][:-1]
    sel = order[first]
    N = len(U)
    T = T[sel]; I_arr = I_arr[sel]; nk = nk[sel]; ex = ex[sel]; KN = KN[sel]
    nonempty = T.reshape(N, -1).sum(1) > 0
    np.savez_compressed(f'{c.ART}/sides_{tag}.npz', T=T, alloc=np.zeros(N, bool), nonempty=nonempty, internal=I_arr, knots=nk, extra=ex, structs=KN)
    by_k = {}
    for st in stats:
        for row in st[:-1]: by_k[(row['internal'], row['knots'])] = by_k.get((row['internal'], row['knots']), 0) + row['structures']
    json.dump(dict(cls=cls, cut=cut, kmax=kmax, imax=imax, hmax=hmax, nparts=nparts, structures=total, tables=N,
                   structures_by_internal_and_knots={f'{i},{k}': v for (i, k), v in sorted(by_k.items())},
                   stats=[dict(tables=N, structures=total)]), open(f'{c.ART}/sides_{tag}.json', 'w'), indent=1)
    for part in range(nparts):
        os.remove(f'{c.ART}/sides_{tag}_part{part}.npz'); os.remove(f'{c.ART}/sides_{tag}_part{part}.json')
    print(f'{tag}: labelled structures {total}; distinct tables {N} (nonempty {int(nonempty.sum())}); {time.time() - t0:.0f}s')
