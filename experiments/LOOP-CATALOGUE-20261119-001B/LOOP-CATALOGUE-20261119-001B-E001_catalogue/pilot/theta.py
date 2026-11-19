import sys, time; sys.path.insert(0, '.')
import eddy as E
sz = [5, 5, 5, 5, 5, 5]; e = [(0, 1), (0, 4), (0, 5), (1, 2), (2, 3), (3, 4), (3, 5)]
t = time.time(); g = E.J.grow(sz, e, rounds=24, maxj=400000, tmax=2400)
print(g['counts'], g['outcome'], round(time.time() - t, 1), flush=True)
