"""Exact four-knot probabilities and checked rational common-table certificates."""
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

from erasure import characters, fraction


HOLDINGS = ((0,1,2),(0,3,6),(1,4,7),(2,5,8))


def u_matrix(mask):
    return np.array([[0 if (a^p)&(7^mask) else (-1)**((a&p&mask).bit_count())
                      for p in range(8)] for a in range(8)], dtype=np.int64)


def tables(gram):
    mass = int(np.trace(gram))
    if mass == 0:
        return None
    answers = []
    for m in range(8):
        u = u_matrix(m)
        weight = np.diag(u @ gram @ u.T)
        den = mass*(1<<m.bit_count())
        assert min(weight)>=0 and sum(weight)==den
        answers.append([fraction(v,den) for v in weight])
    correlations = [sum((-1)**a.bit_count()*Fraction(w) for a,w in enumerate(row)) for row in answers]
    score = max(abs(correlations[7]+s*sum(correlations[m] for m in (1,2,4))) for s in (1,-1))
    return dict(settings_by_change_mask=answers,three_sign_moments=list(map(str,correlations)),score=str(score))


def deterministic_matrix():
    return np.asarray([[all(((a>>i)&1)==((word>>(2*i+((mask>>i)&1)))&1) for i in range(3))
                        for word in range(64)] for mask in range(8) for a in range(8)], dtype=np.int64)


def certificate(table):
    """HiGHS proposes a support only; every resulting inequality or marginal is checked exactly."""
    from sympy import Matrix, Rational
    A = deterministic_matrix()
    b = [Fraction(q) for row in table["settings_by_change_mask"] for q in row]
    rhs = [float(x) for x in b]
    res = linprog(np.zeros(64),A_eq=A,b_eq=rhs,bounds=(0,None),method="highs")
    if res.success:
        positions = [j for j,x in enumerate(res.x) if x>1e-8]
        basis = Matrix(A[:,positions].tolist())
        exact = basis.gauss_jordan_solve(Matrix([Rational(x.numerator,x.denominator) for x in b]))[0]
        assert all(q.is_Rational and q>0 for q in exact)
        weights = [Fraction(0)]*64
        for j,q in zip(positions,exact): weights[j] = Fraction(int(q.p),int(q.q))
        assert sum(weights)==1 and all(sum(int(a)*v for a,v in zip(row,weights))==q for row,q in zip(A,b))
        return dict(common=True,list_weights={str(j):str(v) for j,v in enumerate(weights) if v},checked_marginals=64)
    assert res.status==2
    # Farkas' alternative: for all deterministic columns A.T y >= 0 while b.T y < 0.
    dual = linprog(rhs,A_ub=-A.T,b_ub=np.zeros(64),bounds=(-1,1),method="highs")
    assert dual.success
    values = [Fraction(float(z)).limit_denominator(1000000) for z in dual.x]
    minimum = min(sum(int(a)*v for a,v in zip(col,values)) for col in A.T)
    measured = sum(q*v for q,v in zip(b,values))
    assert minimum>=0 and measured<0
    return dict(common=False,separating_coefficients=list(map(str,values)),class_minimum=str(minimum),measured=str(measured))


def one_law(law):
    # x are old marks, p are read, and q are unread, each encoded as a separate three-bit word.
    signal = np.zeros((8,8,8),dtype=np.int64)
    for w in range(512):
        for holder in HOLDINGS:
            total=sum((w>>i)&1 for i in holder)
            if (total%2 if law=="parity" else total in (0,3)):
                break
        else:
            signal[w&7,(w>>3)&7,w>>6]=1
    N=int(signal.sum())
    unread=sum((m @ m.T for m in signal),np.zeros((8,8),dtype=np.int64))
    gram_sum=np.zeros((8,8),dtype=np.int64)
    branches=[]
    for a in range(8):
        amplitudes=np.einsum("z,zpq->pq",characters(8)[a],signal)
        gram=amplitudes @ amplitudes.T
        gram_sum+=gram
        trace=int(np.trace(gram))
        panel=tables(gram)
        if panel and a==0: panel["common_table"]=certificate(panel)
        branches.append(dict(character=a,probability=fraction(trace,8*N),amplitudes_on_p_q=amplitudes.tolist(),
                             squared_state_normalizer=trace or None,reduced_p_gram_numerators=gram.tolist(),panel=panel))
    assert np.array_equal(gram_sum,8*unread)
    assert sum(Fraction(b["probability"]) for b in branches)==1
    original=tables(unread)
    original["common_table"]=certificate(original)
    pooled=tables(gram_sum)
    assert pooled["settings_by_change_mask"]==original["settings_by_change_mask"]
    for m in range(8):
        for a in range(8):
            expect=sum(Fraction(br["probability"])*Fraction(br["panel"]["settings_by_change_mask"][m][a])
                       for br in branches if br["panel"])
            assert expect==Fraction(pooled["settings_by_change_mask"][m][a])
    return dict(N=N,all_physical_words=[w for w in range(512) if signal[w&7,(w>>3)&7,w>>6]],
                unread_gram=unread.tolist(),unread=original,characters=branches,pooled=pooled)


def run():
    return dict(holding_names=HOLDINGS,word_encoding="x_i bits 0-2, p_i bits 3-5, q_i bits 6-8; low bit is first reader",
                settings="One mask bit per change choice; one result bit per minus or occupied ordinary read. Bits 2i and 2i+1 in a deterministic list give the two settings of reader i.",
                laws={law:one_law(law) for law in ("parity","nae")})
