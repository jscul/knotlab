You are an independent referee. Recheck a small proof and a computation; do not trust the author. Work only in this directory
((the referee's scratch directory)); you may READ files
under /home/jscul/p-vs-np-contact-first but must not modify anything there. Python 3 with numpy and python-sat is at
/home/jscul/p-vs-np-contact-first/.venv/bin/python3. Write your own code; do not import the author's modules.

Setting. Bases of the not-all-equal law (NAE) along one shift: one Boolean variable x_i at every integer i, and for each of finitely
many kinds (0, a, b) with 0 < a < b, the constraint NAE(x_i, x_{i+a}, x_{i+b}) at every i. A "harmony" is such a base whose allowed
bi-infinite states all repeat (are periodic). Claim under test: no harmony has a state of odd period p <= 29.

Definitions. For a binary word u of minimal period p (x_i = u[i mod p]): G(u) = set of pairs (alpha, beta) mod p such that u is not
constant on (r, r+alpha, r+beta) for every r. A word c of period p is compatible with u if it is not constant on any such triple.
A residue r0 of c is flippable if no triple (r, r+alpha, r+beta) with (alpha, beta) in G(u) that contains r0 (in any of the three
places) has its other two values in c equal to each other and different from c[r0]. A certificate for u is a compatible c with a
flippable residue.

Author's lemmas, to check by hand:
 L1. NAE is invariant under flipping all values; an orbit of odd period is never mapped onto itself by this flip.
 L2. u satisfies kind (0,a,b) iff (a mod p, b mod p) is in G(u); for odd p no good pair has alpha = 0, beta = 0 or alpha = beta.
 L3. If u has a certificate (c, r0), every base allowing u also allows c with one value flipped at a position of residue r0, which
     does not repeat; so no harmony allows u.
 L4. If p is odd and u has no certificate, then the base B_u of all kinds (0,a,b) with b < p that u satisfies is a harmony (every
     allowed state has period p). Hence "no harmony has a state of odd period p" iff "every word of period p has a certificate".
Computational claim: every Lyndon word of odd length 3..29 has a certificate (for 25,328,938 words); for the words of period >= 17
that are not their own certificate, the author lists the certificate in
/home/jscul/p-vs-np-contact-first/proofs/EVEN-PERIOD-20261112-001A/EVEN-PERIOD-20261112-001A-P001_flip_certificates/result_census.json
(rows[*]["certified by another word"], fields u, c, residue). Control: words that occur in actual harmonies (01, 0011, 000111,
00001111, 00101101) should have NO certificate.

Please: (1) check L1-L4 carefully, especially L3 (positions in the same residue class as the flipped one) and L4 (does the window
argument really yield compatibility and flippability?); (2) with your own code, verify every listed certificate, recompute the full
claim for odd p <= 21 (all words), and test a random sample of at least 200 words at each of p = 23, 25, 27, 29; (3) check the
control words; (4) for one word of period 17 that is not its own certificate, build its listed certificate with one flip and verify
directly, on a finite window, that it satisfies every kind of span <= 40 that u satisfies; (5) also test L4's converse direction on
one even-period control word: for u = 0011, is B_u (kinds of span < 4... or a few spans) a harmony? Report: each lemma correct or
not (with the flaw if any), each computation's outcome with counts, and your overall verdict. Be concise.
