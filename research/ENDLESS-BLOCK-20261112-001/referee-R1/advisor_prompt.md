A short question for a colleague; be concise and name sources you are confident of (say when unsure).

Setting: a binary constraint relation A on a finite set W (A contains the diagonal: every element relates to itself). A "closed
chain of k" is a cycle x_0 - x_1 - ... - x_(k-1) - x_0 with (x_i, x_(i+1)) in A for all i (indices mod k); an "open chain" is a path.
On a path, since A contains the diagonal, the pair (x_0, x_d) ranges over A^d (relational composition), which grows with d, so any
relation forced between x_0 and x_d on a path is already forced at d = 1. On a cycle of length k, (x_0, x_j) ranges over pairs
(u, w) with A^j(u, w) and A^(k-j)(w, u); all x_i are forced equal ("the loop locks") exactly when k is less than the length of the
shortest closed walk that uses at least one non-diagonal step (the girth of A's digraph without loops). In our case W is a set of
periodic binary words of period P closed under shift, A is shift-equivariant, and the girth is at most P because a non-diagonal
step u -> shift^d(u) repeated P/gcd(d, P) times returns.

Questions: (1) Is this known under standard names (periodic points / closed walks of a finite-type shift and trace of A^k; path
consistency or cycle constraints in CSP; tree duality and the universal cover in Feder-Vardi; holonomy or winding in Z_P clock
models; voltage graphs)? Give the closest standard statement. (2) Is "a tie forced on cycles of length < girth but on no path of any
length" a fair description, and is there any subtlety I miss (for instance pendant copies, or direction of A)?
