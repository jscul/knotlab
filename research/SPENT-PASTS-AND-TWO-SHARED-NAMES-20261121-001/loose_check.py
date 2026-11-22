"""Independent exact check on the isolated source and its first funded round.

A full word assigns x0,x1,x2 and the six new loose names p0,q0,p1,q1,p2,q2.
The old triple is retained for the first reading and forgotten in the second.
Uses only the standard library.
"""

from collections import Counter
from fractions import Fraction
from itertools import product


def binary(length):
    return tuple(product((0, 1), repeat=length))


def allowed(law, bits):
    return len(set(bits)) == 2 if law == "nae" else sum(bits) % 2 == 0


def moment(matrix, changes):
    """Unnormalised tr(rho O), with changes indicated by mask in [0,8)."""
    total = 0
    for w in range(8):
        ordinary = w & (7 ^ changes)
        total += (-1)**ordinary.bit_count()*matrix[w][w ^ changes]
    normalizer = sum(matrix[i][i] for i in range(8))
    return Fraction(total, normalizer)


def matrix_for_counts(columns):
    return [[sum(c[a]*c[b] for c in columns) for b in range(8)] for a in range(8)]


def read_score(matrix):
    return moment(matrix,7) - sum(moment(matrix,k) for k in (1,2,4))


def first_round(law):
    hidden = binary(3)
    ends = binary(6)
    full = {(x,e) for x in hidden for e in ends if allowed(law,x) and
            all(allowed(law,(x[i],e[2*i],e[2*i+1])) for i in range(3))}
    past_counts = {e:sum((x,e) in full for x in hidden) for e in ends}
    n = len(full)
    w = sum(k*k for k in past_counts.values())
    # Fix the three unread q values. Interleave integer-indexed p with q.
    def p_values(q):
        return [tuple(value for pair in zip(p,q) for value in pair) for p in hidden]
    tagged = matrix_for_counts([[int((x,e) in full) for e in p_values(q)]
                                for x in hidden for q in hidden])
    clean = matrix_for_counts([[past_counts[e] for e in p_values(q)] for q in hidden])
    assert sum(tagged[i][i] for i in range(8)) == n
    assert sum(clean[i][i] for i in range(8)) == w
    if law=="parity":
        # A pure end can flip one p on each of two different children.
        x_pair = lambda g: Fraction(sum(g[i][i^6] for i in range(8)),sum(g[i][i] for i in range(8)))
        assert (x_pair(tagged),x_pair(clean))==(0,1)
    assert sum(count*count for count in Counter(e for x,e in full).values()) == w
    # Averaging all character outcomes recovers the retained density including its coherences.
    total = [[0]*8 for _ in range(8)]
    for k in hidden:
        by_q = []
        for q in hidden:
            by_q.append([sum((-1)**sum(a*b for a,b in zip(x,k))
                             for x in hidden if (x,e) in full) for e in p_values(q)])
        g = matrix_for_counts(by_q)
        total = [[total[i][j]+g[i][j] for j in range(8)] for i in range(8)]
    assert total == [[8*t for t in row] for row in tagged]
    def collision(a):
        return sum(past_counts[e]**2 for e in ends if a(e))
    assert collision(lambda e:True) == w
    isolated = matrix_for_counts([[int(allowed(law,x)) for x in hidden]])
    print(law, "first round, N, W:", n,w, "loose multiplicities:",sorted(Counter(past_counts.values()).items()))
    print("isolated score:",read_score(isolated),"three newborn readers, retained:",read_score(tagged),
          "clean:",read_score(clean),"clean fraction:",Fraction(w,8*n),"equal-copy fraction:",Fraction(w,n*n))
    for scored in (tagged, clean, isolated):
        vals = [moment(scored,k) for k in (7,4,2,1)]
        # Single-sign combinations can have different classical bounds.
        rows = [tuple(((-1)**((value>>j)&1)) for j in range(6)) for value in range(64)]
        def deterministic(row,mask):
            v=1
            for j in range(3):
                v *= row[2*j+((mask>>j)&1)]
            return v
        bounds = [max(abs(deterministic(row,7)+s*sum(deterministic(row,k) for k in (1,2,4)))
                      for row in rows) for s in (-1,1)]
        assert bounds == [2,4]
        assert abs(vals[0]+sum(vals[1:]))<=4
    return read_score(tagged), read_score(clean)


def check_extension_rows(law):
    leaves = binary(2)
    b = [[int(allowed(law,(i,)+j)) for j in leaves] for i in range(2)]
    g = [[sum(u*v for u,v in zip(b[i],b[j])) for j in range(2)] for i in range(2)]
    # At r=0 the old bit has just one possible value. At r=1 both
    # amplitudes are one. This is a supplied two-label preparation.
    before = Fraction(1,3)
    after = Fraction(g[0][0],g[0][0]+sum(sum(s) for s in g))
    assert len(set(map(sum,b)))==1
    print(law,"one-parent two-fresh extension Gram matrix:",g,"spectator:",before,"->",after)
    assert after==(Fraction(3,13) if law=="nae" else before)


def check_archived_holders():
    import gzip
    import json
    from collections import defaultdict
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    archive, = (root/'artifacts'/'FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A').glob('*/histories.json.gz')
    with gzip.open(archive,'rt') as stream:
        cases = [case for case in json.load(stream)['cases'] if case['mode']=='built']
    checked = 0
    for case in cases:
        law = case['law']
        for age,holdings in enumerate(case['stages']):
            count = Counter(x for row in holdings for x in row)
            loose = {x for x,k in count.items() if k==1}
            if age:
                assert before.isdisjoint(loose)
            before = loose
            parties = [tuple(x for x in row if x in loose)[:3] for row in holdings
                       if len(set(row)&loose)>=3]
            if not parties:
                continue
            assert len(count)<=16
            rows = [sum(1<<x for x in row) for row in holdings]
            def lawful(word):
                if law=="parity":
                    return all((word&r).bit_count()%2==0 for r in rows)
                return all(word&r not in (0,r) for r in rows)
            words = [w for w in range(1<<len(count)) if lawful(w)]
            loose_mask = sum(1<<x for x in loose)
            end_counts = Counter(w & loose_mask for w in words)
            for marks in parties:
                mask = sum(1<<x for x in marks)
                def score(weight):
                    columns = defaultdict(lambda:[0]*8)
                    for word,value in weight.items():
                        obs = sum(((word>>n)&1)<<i for i,n in enumerate(marks))
                        columns[word & ~mask][obs] = value
                    return read_score(matrix_for_counts(columns.values()))
                retained = score(dict.fromkeys(words,1))
                clean = score(end_counts)
                print(case['label'],law,"step",age,"marks",marks,"retained / clean",retained,clean)
                checked += 1
    assert checked==12


def check_three_loose_bound():
    # Six mixed three-bit words have equal exterior multiplicity. Either
    # homogeneous triple can be forbidden, but a fixed exterior with at
    # least one additional holder name cannot forbid both.
    samples = 0
    for denom in range(1,12):
        for i,j in product(range(denom+1), repeat=2):
            a,b = Fraction(i,denom),Fraction(j,denom)
            if a+b<1:
                continue
            gram = matrix_for_counts([[a,1,1,1,1,1,1,b]])
            score = read_score(gram)
            norm = 6+a*a+b*b
            assert score*norm == 2*a*b+18-6*(a+b)
            gap = 25*norm - 13*score*norm
            assert gap == 6*(a+b-1)*(a+b+14)+19*(a-b)**2
            assert abs(score)<=Fraction(25,13)
            assert (score==Fraction(25,13))==(a==b==Fraction(1,2))
            samples+=1
    print("Three loose marks: verified the exact bound identity on",samples,"rational cases.")


if __name__ == "__main__":
    for law in ("parity","nae"):
        first_round(law)
        check_extension_rows(law)
    check_archived_holders()
    check_three_loose_bound()
