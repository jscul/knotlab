# Lemma G and the independent global minima

**No counterexample found.** The raw direct search and the support-radius
argument below establish the infinite-pattern least bond at all six requested
depths in the first eight selected growers. The support-radius argument does
not invoke Lemma G, its reported r, or any per-call relation implementation.

## Independent support-radius argument for the first eight families

The shape checks in `grow_global_exact.py` establish that each selected S
block has one own variable x, one S call, and exactly one NAE constraint on
x and two live ports (possibly supplied by a recursive helper with no own
variables and exact port mask NAE). On the live ports the S call replaces
one port by x and retains the port that occupied that replacement position.
Consequently the constraints on each infinite chain are exactly
NAE(v_i,v_{i+1},v_{i+2}) for i >= 0. The first two variables are ports of
main; own variables begin at index 2. A wrapper has no own variables and
starts several such chains, sharing only main's ports, with additional
constraints on those ports. Dead carried ports occur in no chain constraint.

Two consecutive unselected chain variables separate the projection onto the
selected variables above and below them. To see this, retain the two
boundary variables on each side of the two blanks. All 16 assignments to
these four variables extend across the blanks in the six-variable chain.
This is checked directly by SAT, without constructing any per-call relation.
Any separately allowed upper and lower states can therefore be joined,
also for infinite tails; all other chain constraints are untouched. The
matched control with only one blank fails, so the check is not vacuous.

Suppose a bond contains a main port and has k members. A nonempty selected
tail cannot be separated from the main port by two consecutive omitted own
variables: its projection would factor, and one proper side would already
be non-shattered, contrary to minimality. Thus, if the deepest selected own
variable in a chain has index M, the at most k-1 selected own variables in
that chain must cover indices 2,...,M with no two consecutive omissions and
with M selected. This implies M <= 2k-1. The deepest absolute S depth is
therefore at most 2k-3 for main=S and 2k-2 for a wrapper.

For a SAT witness of size B, every hypothetical smaller global bond is
confined to absolute depth 2B-5 (2B-4 for a wrapper). Each original SAT prefix
already reaches at least that depth. Its exhaustive exclusion of all
smaller endpoint-eligible supports consequently excludes all smaller bonds
anywhere in the infinite pattern. This closes the finite-member-universe
limitation for these eight families, at all 48 requested depth cases.
The further r=1,2,3 and branching samples retain the explicitly stated
finite-prefix interpretation; this closure is not asserted for them.

## Lemma G: constrained above, unread below

The least fixed point must be liveness, seeded by constraint occurrences and
propagated back through call arguments. Its complement marks positions
unread in the entire subtree of that copy. Induction on finite constraint
occurrences proves that a value entering such a position never occurs in
any descendant constraint. Compactness extends the statement to the usual
infinite limit.

This is a subtree-relative assertion. A value entering an unread position
may occur in a constraint above that copy, or in another branch. It must
remain in the upper/context formula. It is incorrect to delete the actual
distinction globally merely because one of its lower port occurrences is
dead. The controlled example in `grow_lemma_audit.py` retains an upper
NAE(p,a,b) while p is carried unread below: the upper NAE remains constrained,
and the independent lower constraint factors from it. A mutant that treats
p as globally free is rejected.

For a member-free stretch, keep every upper constraint, identify repeated
variables by their actual identity, and existentially remove only unread
port occurrences from the stretch's interface. No lower constraint depends
on the removed values. Any reduced stretch witness can be lifted while
keeping the values already chosen above: unread output positions impose
no new lower constraint. Repeated identities through dead positions therefore
do not obstruct this lifting. If the reduced input-output relation is
P x Q, gluing to the context F and the lower part H gives

    exists alpha,beta [F(X_upper,alpha) & P(alpha) & Q(beta) & H(X_lower,beta)]
      = exists alpha[F(X_upper,alpha) & P(alpha)]
        & exists beta[Q(beta) & H(X_lower,beta)].

An identity whose value survives only in unread positions is assigned to
its upper occurrence in this partition, not counted again as a distinct
lower member. Thus each proper side of a crossing bond is shattered by
minimality, their product is shattered, and the crossing bond is impossible.
The prior gap counting, with the wrapper's one-level shift, then applies.

**Not a block — proof clarification required.** The intended live-quotient
argument is sound, including a carried value constrained above. The opening
observation about a globally unconstrained variable alone does not prove
the subtree-relative deletion step; the factorisation/lifting argument above
should be stated explicitly. The all-family SAT certificate audit independently
matches liveness and the least rectangular length for all 632 growers:
r=1 in 318, r=2 in 163, r=3 in 55, r=4 in 96. These finite certificates support
the symbolic argument; the computation alone is not a uniform proof.
