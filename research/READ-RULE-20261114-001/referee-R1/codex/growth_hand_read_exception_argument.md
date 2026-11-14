# Wrapper tie and a linearly growing bond

This is a fresh counterexample candidate to the **syntactic** converse that a
growing bond requires every carried value to be unread. It is not a
counterexample to Theorem R with its exception, or to the dichotomy. The parent
referee supplied the construction; this lane wrote the independent direct-CNF
checks and the argument below. No lifecycle or proof status is changed.

Let S(a,b,c) have own distinctions x,w and constraints
`NAE(a,x,b)`, `NAE(c,x,w)`, and `SELF(a,b,x)`. Main has ports p,q,r,
forces p opposite to q, and calls S(p,q,r). One variant forces the tie by
`NAE(p,q,q)`; the other uses three fresh main-own distinctions e,f,g and
`NAE(p,q,e)`, `NAE(p,q,f)`, `NAE(p,q,g)`, `NAE(e,f,g)`. The latter
uses distinct arguments in every constraint and call.

The main gadget enforces p opposite to q: if p=q, e=f=g must be their opposite,
contradicting the last constraint; if p differs from q, every choice of e,f,g
except the two constant triples extends. Therefore every S-copy constraint
`NAE(p,x_i,q)` is vacuous. The entire allowed system is a product of the
main tie/gadget relation and

`NAE(r,x_0,w_0), NAE(x_0,x_1,w_1), NAE(x_1,x_2,w_2), ...`.

All carried p and q positions are syntactically read with an own x in every S
copy. They are killed by exactly Theorem R's opposite-tie exception. No S-own
distinction is tied to p or q. Main root r lies in the second product factor.

Write d≥1 for absolute S-copy depth, including the main wrapper. The target
copy is index t=d−1 and its S-call length is n=d−1. Then **L(d)=d+2**.

For the lower bound, a minimal non-shattered set cannot have members in two
independent product factors: if the product projection is non-full, one factor
projection is already non-full. Thus a root-to-covered-target bond must use
root r, and all its members must belong to the displayed chain.

For each j<t, if w_j is absent, quantifying it makes its NAE constraint full on
its two other variables. The remaining relation factors into the part holding
r and the part holding the target. A bond cannot span that product, so every
w_j for j<t must be present. If x_t is the target and w_t is absent, the same
argument applies at j=t. If w_t is the target, it is present already. Every
root-to-target bond therefore contains `{r,w_0,...,w_t}`, of size d+1.
This set is shattered: for arbitrary values of its members, choose
`x_i=1−w_i` for i≤t and extend the tail. A bond consequently needs at least
one more distinction and has size at least d+2. This reasoning permits members
anywhere, including arbitrarily far below the target.

For the upper bound, take `W_d={r,w_0,...,w_t,x_t}`. Assign r=0 and
`w_i=i mod 2`. Each NAE constraint then successively forces
`x_i=(i+1) mod 2`. Assigning `x_t=t mod 2` is impossible, so W_d is
non-shattered. Every single deletion is shattered:

- Without x_t, choose each `x_i=1−w_i` forward.
- Without r, choose the intermediate values backward, setting
  `x_{i−1}=1−w_i` and finally `r=1−w_0`.
- Without w_j, satisfy the prefix forward and the suffix backward. The omitted
  w_j can satisfy its NAE constraint for either resulting pair of end values.

All tails extend. Single-deletion fullness implies fullness of every proper
subset, so W_d is a bond of d+2 members. This proves the stated value by a
direct product and pendant argument, independently of per-call relations or
pumping. The JSON evidence records direct exact-prefix minima for both
variants at d=1,...,6 and independently enumerates each witness projection and
every single deletion with MiniSat22.

The family resolves the syntactic reading. An assertion using "effectively
read" must specify whether the exception has already been excluded; with that
meaning, it is a different assertion and this family does not contradict it.
