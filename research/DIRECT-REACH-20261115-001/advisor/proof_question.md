Advisor: soundness check of three every-depth arguments before I implement and state them (under 600 words; say what you checked; point out any gap).

Setting. A description is a finite invertible automaton (states q, output flip sw[q], transitions d0, d1) and placements: triples of
slots (word w of length <= 2 over states, e in {none, 0, 1}). The depth-N pattern P_N: for each address v of length n <= N and each
placement, the NAE knot on the members w_i(v) (e = none) or w_i(v)·e (an address one level down; such slots are skipped at n = N);
knots with repeated members are dropped. P_N is a sub-pattern of P_{N+1}. Complement symmetry: if P_N allows a state it allows its
complement, so every single address is free. A bond is a constrained set all of whose proper subsets are free; L_N(k, s) is the least
size of a bond meeting level k and level k + s. A tie (forced equal or forced unequal pair) is a bond of size 2.

(1) Already done, bounded orbits. When the orbits of the maps stay of size <= 4, windows O ∪ O·{0,1} form a tree, exact message passing
gives every projection, feasible sets stabilise and pair states are eventually periodic, so ties and two-orbit 3-bonds are decided at
every depth by a finite computation (validated against SAT). I treat this as settled unless you see a flaw.

(2) Tie chains when orbits grow (orbits are whole levels). Pick S_k0 (a few addresses at level k0) and an eventually periodic letter
sequence c_k; set S_(k+1) = S_k·c_k. The window W_k is the set of knots placed at x in S_k whose maps all send x into S_k (so every
member lies in S_k ∪ S_k·{0,1}). The "type" of S_k (for each element and map: target index in S_k or outside, and the section) evolves
deterministically with c_k, so it is eventually periodic. The forward message m_k (assignments of S_k allowed by W_k0..W_(k-1)) and
the set T_k of elements of S_k tied to the class of the top element (computed in the projection of W_k0..W_k onto S_k ∪ S_(k+1)) also
evolve deterministically from finite data, hence eventually periodic, so "T_k nonempty for all k" is a finite check. Claim: then the
chain W_k0 ∪ ... is a sub-pattern of every P_N, ties forced in a sub-pattern are forced in P_N, and with life at every depth (an
automatic state: a Moore machine whose values satisfy every knot at every level, checked by a product automaton) one tie class meets
level k0 and every deeper level, so L_N(k0, s) = 2 for every s >= 1 and every N >= k0 + s.

(3) Lower bound L >= 3 for every s when orbits grow. Take a few automatic states M_1..M_r (each passes the all-level check, so each gives
a state of P_N for every N, as does its complement). For each address x at the top level k, run the product of the machines over all
deeper addresses y; if at every reachable product configuration the parities M_i(x) xor M_i(y) are not all equal, then no deep y is
tied to x at any depth. Claim: then no bond of size 2 meets level k and any level k + s, at every depth, so L >= 3 there.

(3') Upper bound L <= 3 for every s when orbits grow: a triple {x at level k, y, z at level k + s} constrained in a sub-window chain is
constrained in P_N; if each of its three pairs is shown free by two automatic states with different parities, the triple is a bond.
Along a chain the machines' values are eventually periodic, so again a finite check.

Questions: Is each claim sound as stated? In (2), is it right that a sub-pattern's forced tie stays forced in P_N only when P_N is
alive, and that nothing else is needed? In (3), is "parities not all equal" the right separation condition with complements (a tie
of either sign)? In (3'), does "constrained in a sub-pattern + every pair free in P_N" make it a bond of P_N? Any known names
(transfer matrices along a ray; automatic sequences; self-similar groups' Schreier graphs)?
