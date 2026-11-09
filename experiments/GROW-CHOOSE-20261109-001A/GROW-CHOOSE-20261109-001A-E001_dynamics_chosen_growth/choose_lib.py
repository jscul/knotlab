"""Growth chosen by the dynamics (GROW-CHOOSE-20261109-001A-E001), on SEPARATE-20261108-001A's net_lib.

As GROW-RUN-20261109-001A's growrun_lib, with both sides of the square tube labelled: ring (i, r) for i in a cyclic list of column
labels (round the seed loop) and r in a cyclic list of row labels; h(i, r) joins (i, r) E to (next i, r) W and v(i, r) joins (i, r) N to
(i, next r) S. A band can be inserted after a row (n new rings, cutting the v contacts there) or after a column (m new rings, cutting
the h contacts), while the network runs; its cells are new open distinctions (A44) and the cut contact goes by one of four splits (lower
or upper keeps the old value on the first or the second of the two contacts, fresh gives both new cells, copy gives both the old
value). The whole history is read as one space-time law; a contact binds a ring when its value depends on one of the ring's own born
cells. persists() reads whether every contact binds both of its rings at every lag from now if the network stays as it is: the state
is iterated under the fixed map until it repeats (Brent's cycle detection), which covers every later lag."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import net_lib as N  # noqa: E402
LAW=(12,12)
class Tube2:
    def __init__(self, cols, rows, g): self.cols, self.rows, self.g = list(cols), list(rows), g
    def build(self):
        cols, rows, g = self.cols, self.rows, self.g
        rings=[(i,r) for r in rows for i in cols]; idx={R:k for k,R in enumerate(rings)}
        nr={r:rows[(k+1)%len(rows)] for k,r in enumerate(rows)}; nc={i:cols[(k+1)%len(cols)] for k,i in enumerate(cols)}
        names, contacts = [], []
        for r in rows:
            for i in cols:
                names.append(('h',i,r)); contacts.append((idx[(i,r)],0,idx[(nc[i],r)],2*g,LAW))
                names.append(('v',i,r)); contacts.append((idx[(i,r)],g,idx[(i,nr[r])],3*g,LAW))
        sizes=tuple(4*g for _ in rings)
        M,Nb,blocks=N.matrix(sizes,(60,)*len(rings),contacts); lay,_,_=N.layout(sizes,contacts)
        keys=[None]*Nb
        for c,nm in enumerate(names): keys[c]=('c',)+nm
        for k,R in enumerate(rings):
            for p,b in enumerate(lay[k]):
                if b>=len(contacts): keys[b]=('o',R,p)
        self.rings,self.contacts,self.M,self.keys=rings,contacts,M,keys
        self.pos={kk:b for b,kk in enumerate(keys)}
        return self
class Run2:
    def __init__(self, tube):
        self.tube=tube.build(); self.vkey=[]; self.nvar=0
        self.state=[self.fresh(k) for k in self.tube.keys]
    def fresh(self,key):
        v=1<<self.nvar; self.nvar+=1; self.vkey.append(key); return v
    def step(self):
        M,s=self.tube.M,self.state; new=[]
        for row in M:
            v,x=0,row
            while x:
                low=x&-x; v^=s[low.bit_length()-1]; x^=low
            new.append(v)
        self.state=new
    def insert(self, kind, after, label, split):
        old=self.tube; ov={k:self.state[b] for b,k in enumerate(old.keys)}
        cols,rows=list(old.cols),list(old.rows)
        if kind=='row': rows.insert(rows.index(after)+1,label); cut='v'
        else: cols.insert(cols.index(after)+1,label); cut='h'
        new=Tube2(cols,rows,old.g).build(); st=[]
        for k in new.keys:
            if k[0]=='o':
                st.append(ov[k] if k in ov else self.fresh(k)); continue
            kd,i,r=k[1],k[2],k[3]
            pos_lab = r if kind=='row' else i
            if kd!=cut or pos_lab not in (after,label):
                st.append(ov[k] if k in ov else self.fresh(k)); continue
            other = (('c',kd,i,after) if kind=='row' else ('c',kd,after,r))
            if pos_lab==after:
                st.append(ov[k] if split in ('lower','copy') else self.fresh(k))
            else:
                st.append(ov[other] if split in ('upper','copy') else self.fresh(k))
        self.tube,self.state=new,st
    def ringmask(self,R):
        m=0
        for v,k in enumerate(self.vkey):
            if k[0]=='o' and k[1]==R: m|=1<<v
        return m
def persists(run, cap=200000):
    """True if every contact binds both of its rings at every lag from now on with the network fixed, False if one fails at some lag,
    None if the state has not repeated within cap steps"""
    tb = run.tube
    masks = {}
    pairs = []
    for c, (ra, pa, rb, pb, law) in enumerate(tb.contacts):
        for R in (tb.rings[ra], tb.rings[rb]):
            if R not in masks:
                masks[R] = run.ringmask(R)
        pairs.append((c, masks[tb.rings[ra]], masks[tb.rings[rb]]))
    s = list(run.state)
    saved, power, lam = list(s), 1, 0   # Brent's cycle detection: exact comparisons, constant memory
    for _ in range(cap):
        new = []
        for row in tb.M:
            v, x = 0, row
            while x:
                low = x & -x
                v ^= s[low.bit_length() - 1]
                x ^= low
            new.append(v)
        s = new
        for c, ma, mb in pairs:
            if not (s[c] & ma) or not (s[c] & mb):
                return False
        if s == saved:
            return True             # every state from saved round the cycle back to it has been read
        lam += 1
        if lam == power:
            saved, power, lam = list(s), power * 2, 0
    return None
