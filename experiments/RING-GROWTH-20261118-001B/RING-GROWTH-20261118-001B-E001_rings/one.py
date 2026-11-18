import sys, time
from ring import ring, grow
from bm import berlekamp_massey  # noqa: E402
sz=[int(x) for x in sys.argv[1].split(',')]; R=int(sys.argv[2])
t=time.time(); P=grow(ring(sz), R, maxj=15000); c=P.counts_by_round()
L,C=berlekamp_massey(c[4:])
rec=[(i,str(C[i])) for i in range(1,len(C)) if C[i]!=0]
print(sz, 'rounds', P.rounds, 'secs', round(time.time()-t), 'counts', c, 'BM order', L, 'on', len(c)-4, 'terms', rec, flush=True)
