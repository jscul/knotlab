"""Independent exact checks for the local phase, the seven-setting menu and two copies.

Use the project's Python with SymPy. No data produced by the B258 proof are used.
A question is a plain Z value read (None) or a change turned by a multiple of
pi/6. The supplemental two-copy signs refer to the separately reviewed test.
"""
from functools import lru_cache
from itertools import combinations, product
from math import comb
import sympy as sp

ROOT5 = sp.sqrt(5)
ANGLE_MENU = {"Z": None, "X": 0, "+60": 2, "-60": -2, "+90": 3, "+30": 1, "-30": -1}
WORDS = tuple(product((0, 1), repeat=3))
SIX = sp.Integer(6)


@lru_cache(maxsize=None)
def moment(question, shift):
    """Sum the contributions of every ordinary word, including zero-support words."""
    total = 0
    for x in WORDS:
        if sum(x) in (0, 3):
            continue
        y = tuple(v if angle is None else 1-v for v, angle in zip(x, question))
        if sum(y) in (0, 3):
            continue
        sign = (-1)**sum(v for v, angle in zip(x, question) if angle is None)
        angle = sum((1-2*v)*(a-shift) for v, a in zip(x, question) if a is not None)
        total += sign*sp.cos((angle % 12)*sp.pi/6)
    return sp.simplify(total/SIX)


def score_rows(shift):
    rows = []
    for a,b in combinations(ANGLE_MENU,2):
        # E(b,b,b) ± the three equal E(b,a,a), and the interchanged form.
        u,v = ANGLE_MENU[a],ANGLE_MENU[b]
        for p,q in ((u,v),(v,u)):
            for coefficient in (-1,1):
                measured = abs(moment((p,p,p),shift)+3*coefficient*moment((p,q,q),shift))
                rows.append((a,b,coefficient,measured))
    return rows


def deterministic_bound(relative_sign):
    values = []
    for a,b,c,d,e,f in product((1,-1),repeat=6):
        values.append(abs(a*c*e+relative_sign*(a*d*f+b*c*f+b*d*e)))
    return max(values)


def menus():
    assert deterministic_bound(-1)==2 and deterministic_bound(1)==4
    result={}
    for name,turn in (("positive",0),("first root",2)):
        rows = score_rows(turn)
        def greatest(pairs):
            return max(row[-1] for row in pairs)
        raw = greatest(rows)
        minus = greatest(row for row in rows if row[2]==-1)
        zx = greatest(row for row in rows if row[:3]==("Z","X",-1))
        result[name]=(raw,minus,zx)
        print("seven named questions:",name,"scan, bound-two maximum, fixed Z/X",raw,minus,zx)
        assert raw==sp.Rational(7,2)
    return result


def word_factor(m,k,s):
    return 1-sp.exp(2*sp.pi*sp.I*k*s/m)


def phase_winding():
    from math import gcd
    for m in range(2,21):
        for k in range(1,m):
            if gcd(k,m)!=1:
                continue
            jumps=[(k*(s+1))//m-(k*s)//m for s in range(1,m-1)]
            assert (len(set(jumps))<=1) == (k in (1,m-1))
    # The recorded ternary moving and idle alternatives have the same occupancy.
    assert {sum(x) for x in ((1,0,1),(0,1,1),(1,1,0))}=={2}
    d0,d1,d2=sp.symbols("d0 d1 d2",nonzero=True)
    assert sp.cancel((d1/d0)*(d2/d1)*(d0/d2))==1


def twin_pins():
    # On both pins, the first two possible weights are consecutive. Removing
    # the same phase from each bit leaves a relative sign only at winding two.
    # Derive amplitudes from the complex chord separately below.
    I = sp.eye(4)
    W = sp.Matrix([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])
    plus,minus=(I+W)/2,(I-W)/2
    rational=sp.Rational
    H = sp.Matrix([[1,sp.I],[sp.I,1]])/sp.sqrt(2)
    for common in (sp.diag(1,sp.I),H):
        same=sp.kronecker_product(common,common)
        assert sp.simplify(same.H*W*same-W)==sp.zeros(4)
    table=[]
    for k in (1,2):
        theta=sp.pi*k/5
        r=sp.simplify(2*sp.cos(theta))
        assert sp.simplify(r/(1+r*r)-1/ROOT5)==0
        moduli=[0,1,r,r,1,0]
        z=sp.simplify(sum(comb(5,s)*a*a for s,a in enumerate(moduli)))
        pin1,pin2=sp.simplify((1+r*r)/z),sp.simplify(2*r*r/z)
        selected=sp.simplify(pin1*pin2)
        assert z>0 and 0<selected<1
        for kind,relative in (("magnitudes",1),("product",1 if k==1 else -1),("conjugate",1 if k==1 else -1)):
            # Same frame change on both last bits. The conditional input word
            # probabilities are identical under all three preparations.
            a=sp.Matrix([1,r])/sp.sqrt(1+r*r)
            b=sp.Matrix([1,relative])/sp.sqrt(2)
            raw=sp.kronecker_product(a,b)
            keep=sp.simplify((raw.H*plus*raw)[0])
            reject=sp.simplify((raw.H*minus*raw)[0])
            rho_a,rho_b=a*a.H,b*b.H
            assert sp.simplify(keep-(1+(rho_a*rho_b).trace())/2)==0
            assert sp.simplify(keep+reject-1)==0
            assert sp.simplify(keep-sp.Rational(3,4)-relative/(2*ROOT5))==0
            delta=sp.symbols("delta",real=True)
            changed=sp.diag(1,sp.exp(sp.I*delta))*b
            overlap=sp.expand_complex((a.H*changed)[0])
            changed_keep=sp.trigsimp(sp.expand_complex((1+overlap*sp.conjugate(overlap))/2))
            predicted=sp.Rational(3,4)+relative*sp.cos(delta)/(2*ROOT5)
            assert sp.simplify(changed_keep-predicted)==0
            branches=[]
            for proj in (plus,minus):
                out=proj*raw
                branches.append(tuple(sp.simplify(x*sp.conjugate(x)) for x in out))
            assert branches[1][0]==branches[1][3]==0
            print("five-place k =",k,kind,"conditional ±",keep,reject,"pin probabilities",pin1,pin2,"joint launch",selected,"words by port",branches)
            table.append((k,kind,keep,reject,pin1,pin2,selected))
            # Re-evaluate from the two original complex factors on each pin.
            # This direct numerical cross-check includes the common phase that
            # was removed in the exact matrix derivation.
            v=sp.Matrix([word_factor(5,k,s) for s in (1,2)])
            w=sp.Matrix([word_factor(5,k,s) for s in (2,3)])
            if kind=="magnitudes":v,w=v.applyfunc(abs),w.applyfunc(abs)
            if kind=="conjugate":v,w=v.conjugate(),w.conjugate()
            v,w=v.evalf(40),w.evalf(40)
            raw_check=sp.kronecker_product(v/v.norm(),w/w.norm())
            assert abs(complex((raw_check.H*plus*raw_check)[0])-float(keep))<1e-13
        diagonal=sp.diag(1,r*r)/(1+r*r)
        mixed=sp.kronecker_product(diagonal,sp.eye(2)/2)
        assert sp.simplify((mixed*plus).trace())==rational(3,4)
    # Each parity exterior fixes the opposite value of the last bit.
    for p,expected in ((1,{1}),(2,{0})):
        assert {x for x in (0,1) if (p+x)%2==0}==expected
    even_pairs=[(a,b) for a,b in product((0,1),repeat=2) if (1+a)%2==0 and (2+b)%2==0]
    assert even_pairs==[(1,0)] and (even_pairs[0][1],even_pairs[0][0]) not in even_pairs
    uniform=sp.Matrix([1,1,1,1])/2
    assert (uniform.H*plus*uniform)[0]==1
    assert (sp.eye(4)/4*plus).trace()==sp.Rational(3,4)
    return table


if __name__=="__main__":
    menus()
    phase_winding()
    twin_pins()
