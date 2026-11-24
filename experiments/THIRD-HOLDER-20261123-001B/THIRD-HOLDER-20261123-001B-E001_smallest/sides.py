"""List every side table of a census class (THIRD-HOLDER-20261123-001B pre-registration, "Census") with the compiled
enumerator sides_enum.c, and write them in the format of REVIEW-LEADS-20261123-001C's sides.py (npz of tables + json of one
structure per table).

usage: sides.py CLASS CUT KMAX IMAX HMAX
  CLASS L: each observer distinction exactly one old holder; CLASS S: one or two old holders.
  HMAX: largest number of holders of an internal distinction (3 in the study; 2 reproduces ticket C's census).
"""
import sys, json, subprocess, time, struct
import numpy as np
import common as c

cls = sys.argv[1]; cut = int(sys.argv[2]); kmax = int(sys.argv[3]); imax = int(sys.argv[4]); hmax = int(sys.argv[5])
obsmax = {'L': 1, 'S': 2}[cls]
tag = f'{cls}_c{cut}_k{kmax}_i{imax}_h{hmax}'
t0 = time.time()
binf = f'{c.ART}/sides_{tag}.bin'
p = subprocess.run([f'{c.ART}/sides_enum', str(cut), str(kmax), str(imax), str(obsmax), str(hmax), binf], capture_output=True, text=True)
if p.returncode != 0:
    print(p.stdout, p.stderr); sys.exit(1)
stats = [json.loads(l) for l in p.stdout.strip().splitlines()]
for s in stats: print(s)
raw = open(binf, 'rb').read()
N, K = struct.unpack_from('<ii', raw, 0)
off = 8
T = np.frombuffer(raw, dtype=np.uint8, count=N * 8 * K, offset=off).reshape(N, 8, K).astype(np.int16)
off += N * 8 * K
# per table: internal count, knots, extra holders, and the knots (arity, law, members[4]) as small integers
raw_i = np.frombuffer(raw, dtype=np.int32, offset=off)
I_arr = np.zeros(N, dtype=np.int8); nk_arr = np.zeros(N, dtype=np.int8); ex_arr = np.zeros(N, dtype=np.int8)
KN = np.full((N, kmax, 6), -1, dtype=np.int8)
q = 0
for t in range(N):
    I_arr[t], nk_arr[t], ex_arr[t] = raw_i[q], raw_i[q + 1], raw_i[q + 2]; q += 3
    nk = int(nk_arr[t])
    KN[t, :nk] = raw_i[q:q + 6 * nk].reshape(nk, 6); q += 6 * nk
assert q * 4 + off == len(raw)
import os; os.remove(binf)
nonempty = T.reshape(N, -1).sum(1) > 0
np.savez_compressed(f'{c.ART}/sides_{tag}.npz', T=T, alloc=np.zeros(N, dtype=bool), nonempty=nonempty, internal=I_arr, knots=nk_arr,
                    extra=ex_arr, structs=KN)
json.dump(dict(cls=cls, cut=cut, kmax=kmax, imax=imax, hmax=hmax, stats=stats,
               note='one structure per table in the npz: structs[t, k] = (arity, law 0 even 1 odd 2 nae, members; 0..2 x1..x3, '
                    '3.. s1.., then h1..); see side_struct() in common.py'), open(f'{c.ART}/sides_{tag}.json', 'w'), indent=1)
tot = stats[-1]
print(f'{tag}: labelled structures {tot["structures"]}; distinct tables {N} (nonempty {int(nonempty.sum())}); '
      f'tables whose kept structure (fewest knots, then fewest extra holders) has an extra holder: {int((ex_arr > 0).sum())}; {time.time() - t0:.1f}s')
