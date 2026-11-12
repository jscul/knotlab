You are an independent referee. Check one claim from scratch and do not trust the author. Work only in this directory
((the referee's scratch directory)); do not modify anything
under /home/jscul/p-vs-np-contact-first. Python with numpy and python-sat: /home/jscul/p-vs-np-contact-first/.venv/bin/python3. Write
your own code.

Setting. One Boolean variable x_i at every integer i. A "knot kind" (0, a, b) with 0 < a < b imposes NAE(x_i, x_{i+a}, x_{i+b})
(not all equal) at every i. A finite set of kinds is a "harmony" when every bi-infinite assignment satisfying all its constraints is
periodic.

Claim. Let p = 61 and S = {1, 2, 11, 22} (closed under the multiplier 11 up to sign, since 11^2 = -1 mod 61). Let K be the set of all
kinds (0, a, b) with 0 < a < b < 61 such that the residue set {0, a, b} mod 61 is a translate of {0, s, 2s} or {0, -s, -2s} for some
s in S (12 kinds). Then K is a harmony; every allowed assignment has minimal period exactly 61 (odd); there are exactly 122 allowed
assignments of period 61 (two orbits under shifting, swapped by flipping every value); and the kinds' offsets have greatest common
divisor 1, so K does not split into independent parts.

The author's argument: a 61-periodic word c is allowed iff it is non-constant on every translate of {0, s, 2s} mod 61; if some
allowed bi-infinite x had x_j != x_{j+61}, then the length-61 windows of x starting at j and j+1, read cyclically, would be two
allowed periodic words differing in exactly one residue (every residue triple sits inside one window with span < 61, so it is a kind
of K); but the 122 allowed periodic words contain no two at Hamming distance 1. Hence every allowed x is 61-periodic.

Please verify: (1) the 12 kinds; (2) the count of allowed 61-periodic words and their orbits; (3) that no two differ in exactly one
position; (4) the window argument (is it airtight? any gap, e.g. about kinds needed inside a window, or the cyclic reading?); (5) an
independent direct check, e.g. a SAT search on a long finite window for an assignment satisfying every constraint inside the window
with x_j != x_{j+61} somewhere in the middle; (6) gcd of offsets. Report each point and an overall verdict. Be concise.
