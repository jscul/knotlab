You are an independent referee. Check two claims from scratch and do not trust the author. Work only in this directory
((the referee's scratch directory)); do not modify
anything under /home/jscul/p-vs-np-contact-first. Python with numpy and python-sat: /home/jscul/p-vs-np-contact-first/.venv/bin/python3.
Write your own code; do not import the author's modules. Keep each computation under about 20 minutes.

Setting. One Boolean variable x_i at every integer i. A "knot kind" (0, a, b) with 0 < a < b imposes NAE(x_i, x_{i+a}, x_{i+b})
(not all equal) at every i. A finite set of kinds is a "harmony" when every bi-infinite assignment satisfying all its constraints is
periodic. For an odd n and a set S of nonzero residues mod n closed under negation, let K_S be the set of all kinds (0, a, b) with
0 < a < b < n whose residue set {0, a, b} mod n is a translate of {0, s, 2s} mod n for some s in S.

The author's lemma (window argument): if no two n-periodic words compatible with K_S (non-constant on every progression
{x, x+s, x+2s} mod n, s in S) differ in exactly one position, then K_S is a harmony and every allowed assignment has period dividing
n. (Proof: if some allowed x had x_j != x_{j+n}, the length-n windows starting at j and j+1, read cyclically, would be two compatible
periodic words differing in exactly one residue, since every residue triple meets a window in three positions of span < n.)

Claim A. n = 73, S = {±1, ±2, ±27, ±54} mod 73 (27^2 = -1 mod 73; S = H u 2H with H = {±1, ±27}). Then K_S has 12 kinds; exactly
730 compatible 73-periodic words (5 classes under rotation and flipping every value); no two differ in one position (least
distance 8); every allowed assignment has minimal period 73; offsets have gcd 1.

Claim B. n = 193, S = H u 2H u (54 H) with H = {±1, ±81} (81^2 = -1 mod 193), i.e. S = {1, 2, 31, 54, 65, 81, 112, 128, 139, 162,
191, 192}. Then K_S has 18 kinds; exactly 386 compatible 193-periodic words (one class); none differ in one position (least
distance 19); every allowed assignment has minimal period 193; offsets have gcd 1.

Claim C (negative, sample it). H u 2H, H the fourth roots of 1, does NOT make a harmony at 89 or 97 (some compatible word has a
position whose flip is again compatible), and no set of the form {±1, ±2, ±t} makes one at 67 or 71 for any t.

Please verify: (1) the kinds; (2) the counts and classes; (3) no two compatible words at Hamming distance 1, and the least
distances; (4) the window lemma (any gap?); (5) a direct check: a SAT search on a long finite window (e.g. 4n) for an assignment
satisfying every constraint inside it with x_j != x_{j+n} somewhere in the middle (should be impossible); (6) the gcd; (7) claim C.
Report each point and an overall verdict. Be concise.
