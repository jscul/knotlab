# Independent referee of the period-61 harmony (a fresh session, 2026-11-12)

Model: claude-opus-5-5. Brief: brief.md. Code written by the referee: referee_check.py.

I checked every point with my own code, and the claim holds as stated. The code is `check.py` in this directory; it uses python-sat with CaDiCaL.

**(1) The 12 kinds: confirmed.** 11·{1, 2, 11, 22} ≡ {11, 22, −1, −2} mod 61, so S is closed under the multiplier 11 up to sign. There are 244 distinct residue triples, and the kinds with 0 < a < b < 61 whose residues form one of them are exactly these 12:
(0,1,2), (0,1,60), (0,2,4), (0,2,59), (0,11,22), (0,11,50), (0,17,39), (0,22,39), (0,22,44), (0,39,50), (0,57,59), (0,59,60).

**(2) Count and orbits: confirmed.** Listing every satisfying assignment of the 244 triple constraints gives exactly 122 words. They fall into 2 shift orbits of size 61 each, and flipping every value maps one orbit onto the other. All 122 also satisfy the 12 kinds checked directly as constraints on the periodic word. None is constant and 61 is prime, so each has minimal period exactly 61.

**(3) No two words at distance 1: confirmed.** No pair among the 122 words is at Hamming distance 1. The smallest distance between any two is 11.

**(4) The window argument: airtight.**
- **Kinds inside a window:** a translate T of {0, s, 2s} mod 61 has exactly one representative of each residue in the window [j, j+60]. Call them u < v < w, so w − u ≤ 60. Then {0, v−u, w−u} mod 61 = T − u is itself a translate, so (0, v−u, w−u) is in K. Its constraint applies at position u, so the window is non-constant on T. K was defined to contain every such kind, so nothing is missing.
- **Cyclic reading:** for a 61-periodic word, the K-constraints are exactly the "non-constant on every residue triple" conditions. So "allowed periodic word" means the same thing on both sides of the argument.
- **The one-position difference:** the cyclic readings of the windows at j and j+1 agree at every residue except j mod 61, where they hold x_j and x_{j+61}. By (3) these two must be equal, so every allowed x is 61-periodic. Combined with (2), the minimal period is exactly 61.

**(5) Direct SAT check: confirmed.** On finite windows of lengths 400 and 1000, I imposed every constraint that fits inside the window. With the extra requirement x_j ≠ x_{j+61} for some j in a 100-position band in the middle, both are UNSAT. Without that requirement both windows are satisfiable, so the UNSAT result is not vacuous.

**(6) gcd of the offsets: confirmed.** It is 1; the kind (0,1,2) alone guarantees this.

**Verdict:** the claim is correct. K is a harmony, every allowed assignment has minimal period exactly 61, there are exactly 122 of them in two flip-swapped orbits, and K does not split into independent parts.
