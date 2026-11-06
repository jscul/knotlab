# The forgetting reading of the knot test: census, width and the place of parity

Status: Proved

Ticket `KNOT-FOUNDATION-20261019-001E`. On 2026-10-19 the repository owner
chose the forgetting reading of erasure for the canonical knot test. This
proof supplies the evidence for that reading. It builds on
`KNOT-FOUNDATION-20261019-001A-P001`, which proved the absence reading and
stays unchanged.

## Standard statement

Take Boolean relations on n + 1 variables, with n ≥ 2. Call a relation a
*knot* when two conditions hold:
- it excludes at least one assignment;
- for each variable, the projection that forgets that variable allows every
  assignment of the others.

Then:
- **(i)** On three variables exactly 34 relations are knots. Up to permuting
  and negating variables they fall into five classes, by number of excluded
  assignments: 1, 2 (two classes), 3 and 4.
- **(ii)** A knot has at least 2^n states. Only the two parity relations have
  exactly 2^n.
- **(iii)** No knot is definable by 2-CNF, even with existentially
  quantified auxiliary variables.
- **(iv)** A knot implies no clause on fewer than all of its variables.
- **(v)** Parity on m variables is definable by 4(m − 1) + 1 clauses of at
  most three literals with m − 1 auxiliary variables, while it needs
  2^(m − 1) clauses of width m without them.

## Nearest known result

- **(iii):** relations definable by 2-CNF with existential quantification are
  the majority-closed ones (Schaefer 1978), and majority-closed relations are
  determined by their two-variable projections (Baker and Pixley 1975).
- **(ii):** binary codes with minimum distance two and 2^n words of length
  n + 1 are the parity codes.
- **(v):** the Tseitin encoding (1968).
- **(i):** a finite classification, here checked exhaustively.

Novelty: `known-overlap-found`. The new material is the choice of this
reading as the knot test and what it implies for the program's earlier
verdicts.

## Setting

A loop contributes one open distinction, a variable it leaves free, and the
contact is one more variable. The semantics is relational: allowed states
only, witnesses quantified away, no input supplied by an executor. Erasing a
loop forgets it, so its variable is no longer constrained by anything.

The knot test K1–K3 then reads:
- **K1 binding:** the relation is constrained as a whole.
- **K2 loss on erasure:** forgetting any one variable, a loop or the
  contact, leaves the others unconstrained.
- **K3 coexistence:** some state is allowed. K2 implies it.

In short: constrained as a whole, unconstrained in every part. Forgetting the
contact must also free the loops, which rules out loops tied to each other
directly. Without that condition, 48 relations on three variables would
pass, including "A ≠ B" with the contact unused.

## Results

**Theorem 1 (census).** Exactly 34 relations on two loops and a contact are
knots. Up to renaming and negation they come in five shapes:

| Excluded states | Relations | Bits the whole holds and no pair does |
| --- | --- | --- |
| 1 (a single three-literal clause, the atom) | 8 | 0.193 |
| 2 at distance three | 4 | 0.415 |
| 2 at distance two | 12 | 0.415 |
| 3 | 8 | 0.678 |
| 4 (parity, odd or even) | 2 | 1.000 |

*Proof.* A relation on three variables has every pair projection full
exactly when no two excluded states differ in one coordinate. So the
excluded states form a nonempty independent set of the 3-cube. Count those
sets and classify them under the cube's 48 symmetries. Both the count and
the classification were done exhaustively. ∎

**Theorem 2 (parity hides the most).** A knot on n + 1 variables has at least
2^n states, so it hides at most one bit. Exactly the two parity relations
reach that bound.

*Proof.* Forgetting one variable leaves all 2^n assignments of the others,
each needing at least one state, so there are at least 2^n states.

Now suppose there are exactly 2^n. Forgetting the last variable is then a
bijection, so the relation is the graph of a function f. Two states that
differ in one coordinate cannot both be allowed, since forgetting that
coordinate would then be two-to-one. So f must change whenever one input
bit changes. That makes f parity or its complement. ∎

**Theorem 3 (no pairwise definition).** No 2-CNF with any witnesses defines a
knot.

*Proof.* A 2-CNF relation with witnesses quantified away is closed under
majority. A majority-closed relation is determined by its pairs (Baker and
Pixley 1975). Every pair of a knot is unconstrained, so the relation would
allow everything, contradicting K1.

For three variables the kernel gives the direct argument. For a target
state, take allowed states that agree with it on each of the three pairs.
Their majority is the target. ∎

**Theorem 4 (no narrow clause).** A knot on m variables implies no clause on
fewer than m variables. Without witnesses, every clause in its definition has
full width.

*Proof.* A clause on fewer variables constrains a proper projection, and
every proper projection of a knot is unconstrained. ∎

**Theorem 5 (naming partial matches).** Let each witness a_i say whether a_(i−1)
and x_(i+1) differ, defined by four clauses of three literals, and fix the
last witness. These clauses define parity on any number of variables.

*Proof.* The four clauses force a_i = a_(i−1) ⊕ x_(i+1). Fixing the last
witness fixes the parity of all the variables. ∎

**Theorem 6 (the absence reading is a special case).** Every knot of the
absence reading (`KNOT-FOUNDATION-20261019-001A-P001`) is a knot here. Parity
is a knot here but not there.

*Proof.* Under absence, erasing a loop frees everything, which frees every
pair. Parity fails the absence reading because with one loop absent the
other two must still be equal. ∎

**Theorem 7 (no knot of infinitely many loops).** No set of finite clauses,
even with infinitely many witnesses, defines a knot over infinitely many
variables.

*Proof.* By compactness, an excluded state is already excluded by finitely
many clauses. Those clauses name finitely many variables. Forget one variable
they do not name: the same clauses still exclude every extension, so the
forgotten variable does not free the rest, contradicting K2. ∎

**Carried over from ticket A.**
- Checking a loop's guard only while the loop runs adds that loop's presence
  as a literal.
- Cross-wired 2-clause guards read relationally are the common hub, which
  fails K2 here as well: with one loop forgotten, the other loop still
  forces the contact.
- The earlier kernel's relation `(A ↔ B) ∧ (A → c)` fails here too, because
  A and B are tied.

## Machine checks

`ForgettingKernel.lean` is checked by Lean 4.32.2, pinned in `check.py` with
`lean +leanprover/lean4:v4.32.2`. Every theorem depends only on `propext` and
`Quot.sound`. The kernel proves:
- `atom_isKnot` and `parity_isKnot`: both are knots;
- `hub_not_knot` and `tied_not_knot`: the common hub and the earlier kernel's
  relation are not;
- `absence_knot_is_knot` and `parity_not_absence_knot`: Theorem 6;
- `no_clause_on_a_b`, `no_clause_on_a_k` and `no_clause_on_b_k`: Theorem 4
  for two loops;
- `majority_with_free_pairs_is_full` and `no_two_cnf_defines_knot`: Theorem 3
  for two loops, with witnesses of any type;
- `parity_chain_defines_parity`: Theorem 5 for every length.

`check.py` re-derives the finite claims with its own enumeration,
independently of `tools/knotlab` and of the Lean source:
- the census and shapes (Theorem 1);
- the bound and its equality case for three and four variables (Theorem 2);
- all 166 relations that unit and 2-literal clauses define on three
  variables, plus 3,000 sampled 2-CNF systems with witnesses (Theorem 3);
- minimum widths for the atom and parity on up to five variables (Theorem 4);
- the parity chain for 2 to 6 variables (Theorem 5);
- the reference cases.

Each control runs on a deliberately wrong input, and each rejects it:
- K2 without the contact condition admits more than 34 relations;
- a broken parity chain fails to define parity;
- the majority test rejects parity;
- the knot test rejects the hub;
- Lean rejects the kernel when `parity` is replaced by the hub.

## Safe conclusion

Under the forgetting reading, a knot is a relation that is constrained as a
whole and unconstrained in every part.
- On two loops and a contact there are 34 knots in five shapes, from the atom
  to parity.
- Parity hides the most possible, one bit.
- No 2-CNF with witnesses defines a knot, and three-literal clauses with
  named intermediates define every one.
- Every knot of the absence reading remains a knot.

## Nonclaims

- Which logical structures count as loops is interpretive. The test applies
  to their open distinctions, and the native-formation flags stay false.
- These results are about definability. They give no complexity bound.
- One knot is the first atomic logical topology. It is not composed topology,
  a path or a metric.
