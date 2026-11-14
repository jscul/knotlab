# What the rigidity certificates imply

Let F_n be #2's full NAE pattern, D_n its two parity-violating knots, and
H_n = F_n minus D_n. Write p_n(x) = popcount(x) mod 2. For every even n >= 4,
the independent all-level check identifies D_n and establishes that p_n is a
state of H_n. Complement symmetry gives the other state 1-p_n.

If H_n is rigid, it therefore has exactly these two states. Every state of
F_n would be a state of H_n, but p_n and 1-p_n both violate both knots of
D_n. Thus F_n is dead. This is a uniform implication, not a proof of its
rigidity premise at all levels. Rigidity by itself, without identifying the
unique state and its failure on the deleted knots, would not suffice.

The fresh SAT test fixes X_0=0. This selects parity rather than its
complement. It adds the full blocking clause

    OR_x (X_x != p_n(x)).

A refutation proves there is no other state with X_0=0. Any additional state
with X_0=1 would have an additional complementary state with X_0=0. Therefore
the test includes every possible additional state, including changes at
addresses absent from knots. The retained DRUP refutations for n=6,8,10,12
all pass the earlier independent RUP checker; no SAT solver is trusted for
these UNSAT verdicts. A second checked state exists at n=4.

## What a finite all-level rigidity argument would still need

There is a precise reformulation. For any state s of H_n, define
t_x = s_x XOR p_n(x). In a remaining knot let a,b be its two addresses with
the same parity and c its address of the other parity. NAE on s is exactly

    t_a = t_b  implies  t_c = t_a.

Consequently rigidity means that every assignment satisfying all these
implications is constant. Equivalently, there is no nonempty proper set S
of addresses such that both S and its complement are closed under every
rule "if a,b belong, c belongs" arising this way. A finite induction showing
this property survives the explicitly derived passage from n to n+2 would
prove all-even rigidity. So could an independently justified finite
description of all forced equalities, with completeness for arbitrary
states and a checked induction.

Neither the finite certificates nor a product automaton that follows a
prescribed parity state proves that property. The latter reads three mapped
addresses and checks one proposed state; rigidity quantifies over every
assignment on 2^n addresses. No reduction of that quantifier to a fixed
finite automaton, nor the needed induction, is supplied here. All-even
rigidity and hence all-even death remain open in this audit. In particular,
n=4 shows why a starting-level qualification is necessary.
