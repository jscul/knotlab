"""Price announcements for each disclosed subset of four actual erasure records."""
from fractions import Fraction
import numpy as np
from independent_rates import exact, proportions, read_names, rows, signed_sum, source, witness


def ordinary_questions(words):
    characters = np.array([[signed_sum(h & s) for s in range(16)] for h in range(16)])
    vec = np.einsum("hs,sri->hri", characters, words)
    return np.einsum("hri,hrj->hrij", vec, vec)


def merge_records(ports, subset):
    # The writer sees the literal values of just these paid-sign coordinates.
    groups = sorted({h & subset for h in range(16)})
    return np.array([ports[[h for h in range(16) if h & subset == g]].sum(axis=0)
                     for g in groups])


def all_rates(ports, score, denominator):
    return {subset: proportions(rows(merge_records(ports, subset),score),denominator)
            for subset in range(16)}


def any_randomized_use_of_a_record_is_bounded(cells):
    # Independent fractional upper bound from minimization over all breakpoints.
    from collections import Counter
    m = Counter(cells)
    candidates = {Fraction(0)} | {Fraction(w,-s) for w,s in m if s<0}
    best = min(sum(k*max(0,w+l*s) for (w,s),k in m.items()) for l in candidates)
    assert exact(cells)[1] == best


def fractional_mask(cells):
    accepted = {i: Fraction(1) for i,(w,s) in enumerate(cells) if w and s >= 0}
    credit = sum(cells[i][1] for i in accepted)
    rejected = sorted((i for i,(w,s) in enumerate(cells) if w and s < 0),
                      key=lambda i: Fraction(cells[i][0], -cells[i][1]), reverse=True)
    for i in rejected:
        if not credit:
            break
        cost = -cells[i][1]
        fraction = min(Fraction(1), Fraction(credit,cost))
        accepted[i] = fraction
        credit -= fraction*cost
    return accepted


def matched_dummy(cells,mask,denominator):
    # Preserve the entire h,k frequency table and sever its conditional focal correlation.
    # Grouping by record index modulo 512 leaves the same sibling observation k.
    mass_at_k = [sum(cells[512*h+k][0] for h in range(16)) for k in range(512)]
    surplus_at_k = [sum(cells[512*h+k][1] for h in range(16)) for k in range(512)]
    w = sum(cells[i][0]*p for i,p in mask.items())
    if not w:
        return Fraction(0),None,None
    actual = sum(cells[i][1]*p for i,p in mask.items())
    dummy = sum(p*cells[i][0]*Fraction(surplus_at_k[i%512],mass_at_k[i%512])
                for i,p in mask.items() if cells[i][0])
    return Fraction(w,denominator), Fraction(actual+2*w,56*w), Fraction(dummy+2*w,56*w)


def main():
    for law in ("nae","parity"):
        words = source(law)
        n = int(words.sum())
        retained, ports = read_names(words,8)
        ordinary = ordinary_questions(words)
        assert np.trace(ports,axis1=-2,axis2=-1).sum() == 32*n
        assert np.trace(ordinary,axis1=-2,axis2=-1).sum() == 16*n
        for c in (0,1):
            score = witness(c)
            prices = all_rates(ports,score,32*n)
            print(law,"orientation",c)
            for subset, rates in prices.items():
                print("  known signs",f"{subset:04b}",*rates)
            full = prices[15]
            print("  least accessible subsets attaining each full optimum",
                  [[f"{k:04b}" for k,v in prices.items() if v[i]==full[i]
                    and not any(h!=k and h&k==h and prices[h][i]==full[i] for h in prices)]
                   for i in (0,1)])
            for small in range(16):
                for big in range(16):
                    if small & big == small:
                        assert all(a<=b for a,b in zip(prices[small],prices[big]))
            assert prices[0]==proportions(rows(retained,score),2*n)
            each = [proportions(rows(port,score),32*n) for port in ports]
            local = tuple(sum(p[i] for p in each) for i in (0,1))
            assert all(a<=b for a,b in zip(local,full))
            print("  separately by erasure character",local)
            print("  nine ordinary with same access",proportions(rows(ordinary,score),16*n))
            fully_tagged = np.broadcast_to(retained,ports.shape)
            print("  full orthogonal copy of spent values",proportions(rows(fully_tagged,score),32*n))
            cells = rows(ports,score)
            any_randomized_use_of_a_record_is_bounded(cells)
            mask = fractional_mask(cells)
            price, real_score, dummy_score = matched_dummy(cells,mask,32*n)
            assert price == full[1]
            print("  independently chosen full randomized flag:",len(mask),
                  "accepted whole or fractionally; rate",price,"real excess",real_score,
                  "frequency-matched dummy excess",dummy_score)
        reference = None
        for bit in range(9):
            payer = 1 + bit//3
            unused, moved_ports = read_names(words,bit)
            for c in (0,1):
                prices = all_rates(moved_ports,witness(c),32*n)
                signature = (prices[0],prices[15],prices[14],prices[15^(1<<payer)],
                             sorted(prices.values()))
                if reference is None:
                    reference = signature
                assert signature == reference
        print("  288 named placements, orientations and erasure disclosures checked")


if __name__ == "__main__":
    main()
