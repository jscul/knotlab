"""Print row blocks (tag r0 r1) of roughly equal numbers of unordered class pairs for pairs.py --sym --rows, from a sides file.
usage: blocks.py TAG NBLOCKS"""
import sys
import numpy as np
import common as c
tag = sys.argv[1]; nb = int(sys.argv[2])
d = np.load(f'{c.ART}/sides_{tag}.npz')
T = d['T'].astype(np.int64)[d['nonempty']]
g = np.gcd.reduce(T.reshape(len(T), -1), axis=1); Tp = T // g[:, None, None]
U = np.unique(Tp.reshape(len(Tp), -1), axis=0).reshape(len(set(map(bytes, Tp.reshape(len(Tp), -1)))) if False else -1, 8, T.shape[2])
imgs = np.stack([U[:, p, :] for p in c.ROW_PERMS], 1).reshape(len(U), 4, -1)
N = len({min(imgs[t, k].tobytes() for k in range(4)) for t in range(len(U))})
bs = [0] + [int(round(N - np.sqrt(N * N * (1 - k / nb)))) for k in range(1, nb)] + [N]
for a, b in zip(bs[:-1], bs[1:]):
    print(tag, a, b)
