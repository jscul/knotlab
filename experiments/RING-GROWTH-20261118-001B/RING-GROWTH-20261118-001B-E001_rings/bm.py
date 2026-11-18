from fractions import Fraction
import sys
def berlekamp_massey(s):
    s=[Fraction(x) for x in s]
    C=[Fraction(1)]; B=[Fraction(1)]; L=0; m=1; b=Fraction(1)
    for n in range(len(s)):
        d=s[n]+sum(C[i]*s[n-i] for i in range(1,L+1))
        if d==0: m+=1; continue
        T=C[:]; coef=d/b
        C=C+[Fraction(0)]*(len(B)+m-len(C))
        for i in range(len(B)): C[i+m]-=coef*B[i]
        if 2*L<=n: L=n+1-L; B=T; b=d; m=1
        else: m+=1
    return L, C[:L+1]
