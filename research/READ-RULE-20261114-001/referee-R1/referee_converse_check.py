# Referee's own brute force of Codex's converse counterexample (wrapper with own e,f,g forcing p!=q; S(a,b,c) own x,w:
# NAE(a,x,b), NAE(c,x,w), SELF(a,b,x)); finite truncation, members anywhere in it.
import numpy as np, itertools, sys
def run(d, D):
    names=['p','q','r','e','f','g']+[f'x{i}' for i in range(D)]+[f'w{i}' for i in range(D)]
    ix={n:i for i,n in enumerate(names)}; n=len(names)
    cons=[('p','q','e'),('p','q','f'),('p','q','g'),('e','f','g')]
    for i in range(D):
        cons.append(('p',f'x{i}','q'))
        cons.append(('r' if i==0 else f'x{i-1}', f'x{i}', f'w{i}'))
    S=np.arange(1<<n,dtype=np.int64)
    ok=np.ones(1<<n,bool)
    bit=lambda v:(S>>ix[v])&1
    for a,b,c in cons:
        A,B,C=bit(a),bit(b),bit(c); ok&=~((A==B)&(B==C))
    Om=S[ok]
    def proj(idx):
        k=np.zeros(len(Om),np.int64)
        for j,v in enumerate(idx): k|=((Om>>v)&1)<<j
        return len(np.unique(k))
    def shattered(idx): return proj(idx)==1<<len(idx)
    def bond(idx):
        if shattered(idx): return False
        return all(shattered(sub) for sub in itertools.combinations(idx,len(idx)-1))  # downward closed: subsets of shattered are shattered
    roots=[ix['p'],ix['q'],ix['r']]; tg=[ix[f'x{d-1}'],ix[f'w{d-1}']]
    others=list(range(n))
    for size in range(2,n+1):
        for rt in roots:
            for t in tg:
                rest=[v for v in others if v not in (rt,t)]
                for extra in itertools.combinations(rest,size-2):
                    idx=(rt,t)+extra
                    if bond(idx): return size,[names[v] for v in idx]
    return None
for d in range(1,int(sys.argv[1])+1):
    print(d, run(d, d+1), flush=True)
