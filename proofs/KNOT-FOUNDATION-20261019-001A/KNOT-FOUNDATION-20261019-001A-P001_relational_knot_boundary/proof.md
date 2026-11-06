# Relational knot boundary: the K1–K3 test and the width threshold

Status: Proved

Ticket `KNOT-FOUNDATION-20261019-001A`. This proof replaces Proof 0009
(`CONTACT-001I-P001`) and the kernel `CONTACT-FORMAL-KERNEL-001A-P001` as the
evidence for the protected arity thesis. Both predecessors stay unchanged.

## Standard statement

Take Boolean relations on variables L1, …, Ln, c with n ≥ 2, read as "loop i
is present" and "the contact is made". Call a relation a *knot* when:
- **(K1)** with every Li true, some value of c is excluded;
- **(K2)** with any Li false, every assignment of the other variables is allowed;
- **(K3)** some assignment with every Li true is allowed.

Then:
1. For two loops, the only knots are ¬L1 ∨ ¬L2 ∨ c and ¬L1 ∨ ¬L2 ∨ ¬c.
2. No knot can be defined by a 2-CNF formula, even with existentially
   quantified auxiliary variables.
3. Every knot can be defined by three-literal clauses with n − 2 auxiliary
   variables. Without auxiliary variables, it needs a clause of width n + 1.

## Nearest known result

Claim 2 follows directly from two classical results:
- relations definable by 2-CNF with existential quantification are exactly
  the relations closed under Boolean majority (Schaefer 1978);
- such relations are determined by their two-variable projections (Baker and
  Pixley 1975).

Claim 3 is the standard splitting of a wide Horn clause into three-literal
clauses. Novelty: `known-overlap-found`. The new material is the K1–K3
definition, plus two diagnoses of earlier project artifacts (Theorems 6 and
7). The mathematics itself is not new.

## Setting

The semantics is relational. A system of clauses defines the joint states it
allows. Auxiliary variables are witnesses, quantified away. No executor,
scheduler or checker may supply an input: if a constraint should hold only
while a loop runs, the loop's presence appears in it as a literal. A verdict
depends only on the allowed states, so it does not change when the same
relation is written differently.

Loop presence is taken as given. Whether a loop's presence can be formed from
the logic itself is ticket `KNOT-FOUNDATION-20261019-001B`.

## Results

Let R be a relation on L1, …, Ln, c that passes K1–K3.

**Theorem 1 (uniqueness).** R excludes exactly one state: every loop present
with c equal to one fixed value. So R is ¬L1 ∨ … ∨ ¬Ln ∨ c, or the same
clause with ¬c.

*Proof.* K2 allows every state in which some loop is absent. That leaves two
states, both with every loop present. K1 excludes at least one of them and K3
allows at least one. ∎

**Theorem 2 (invisible in its parts).** Every projection of R onto a proper
subset S of its variables allows every assignment of S.

*Proof.* Take an assignment of S.
- If some loop is absent in it, or missing from S, extend it with that loop
  absent; K2 allows the result.
- Otherwise every loop is in S and present, so S omits c. Extend with the
  value of c that K3 allows. ∎

**Theorem 3 (no pairwise definition).** R is not closed under majority, so no
2-CNF with any witnesses defines it.

*Proof.* Let c* be the excluded contact value. Take three states:
- x: L1 absent, every other loop present, c = c*;
- y: L2 absent, every other loop present, c = c*;
- z: every loop present, c = ¬c*.

K2 allows x and y, and Theorem 1 allows z. Taking the majority in each place
gives every loop present with c = c*, which R excludes.

Each 2-clause is closed under majority. Conjunction and existential
projection preserve that closure, so every relation that a 2-CNF with
witnesses defines is closed under majority. ∎

**Theorem 4 (width three suffices).** Introduce witnesses w1, …, w(n−2) and
take these clauses:
- ¬L1 ∨ ¬L2 ∨ w1;
- ¬w(i−1) ∨ ¬L(i+1) ∨ wi, for 2 ≤ i ≤ n − 2;
- ¬w(n−2) ∨ ¬Ln ∨ c.

For n = 2 the single clause is ¬L1 ∨ ¬L2 ∨ c. Every clause has exactly three
literals, and projecting the witnesses away gives the knot ¬L1 ∨ … ∨ ¬Ln ∨ c.

Without witnesses, a clause of width w excludes 2^(n+1−w) states. Every
clause that R implies may exclude only R's one excluded state, so the
definition needs a clause of width n + 1.

*Proof.* If every loop is present, the clauses force w1, …, w(n−2) in turn and
then c. Otherwise, set each wi to "L1, …, L(i+1) are all present". Every
clause then holds whatever the value of c. ∎

**Theorem 5 (no affine knot).** No relation defined by linear equations over
GF(2) is a knot. In particular, parity A ⊕ B ⊕ c = 0 is invisible in pairs
but fails K2: with A absent, B and c must still be equal.

*Proof.* A nonempty affine relation has 2^d states. By Theorem 1 a knot has
2^(n+1) − 1 states, which is odd and greater than one. ∎

**Theorem 6 (checking a guard only while its loop runs adds a literal).**
Proof 0009's clause-transition executor checks a loop's guard only while that
loop runs. As a constraint, "guard g holds while loop L is present" is
¬L ∨ g. Consider the cross-wired 2-clause guards: ¬B ∨ c for loop A, and
¬A ∨ c for loop B.
- Under that rule, both guards become the three-literal clause ¬A ∨ ¬B ∨ c,
  which is the knot.
- Read relationally, they are the common hub (¬A ∨ c) ∧ (¬B ∨ c). The hub
  fails K2: with B absent, a present A still forces c.

So a 2-clause system that acts like a knot under that executor does so
because the executor supplies the third literal. Proof 0009 also tests
jointness syntactically: its `irreducibly_joint_contact` requires one clause
that names both loops and the contact. Its verdicts are correct. Its
semantics would accept or reject for reasons other than the allowed states.

**Theorem 7 (the earlier kernel's erasure condition is weaker than K2).**
`CONTACT-FORMAL-KERNEL-001A` states erasure as "once a loop is erased, the
relation ignores the contact". The relation (A ↔ B) ∧ (A → c) is defined by
the 2-CNF clauses ¬A ∨ B, A ∨ ¬B and ¬A ∨ c. It:
- has the enabled and disabled joint values that the kernel's
  `CompleteWitness` requires;
- does not factor into one-loop parts;
- is unchanged when the two roles are swapped;
- satisfies that erasure condition.

So it passes every condition of `CompleteWitness` that depends on the
relation. It fails K2: with A absent, B must be absent. Under K2, Theorem 3
excludes every 2-CNF relation.

## Machine checks

`KnotKernel.lean` is checked by Lean 4.32.2. `check.py` pins that version
with `lean +leanprover/lean4:v4.32.2`. The kernel proves the following, and
every theorem depends only on the axioms `propext` and `Quot.sound`:
- `knot_unique`: Theorem 1 for two loops, in both directions;
- `knot_shadow_ab`, `knot_shadow_ak`, `knot_shadow_bk`: Theorem 2 for two
  loops;
- `knot_not_majority_closed` and `no_two_cnf_defines_knot`: Theorem 3 for two
  loops, with witnesses of any type;
- `chain_defines_knot`: Theorem 4 for every list of loops, using clauses of
  exactly three literals;
- `cross_relational_not_knot`, `cross_gated_eq_atom` and `cross_gated_isKnot`:
  Theorem 6;
- `tied_passes_old_conditions`, `tied_role_swap`, `tied_is_two_cnf` and
  `tied_not_knot`: Theorem 7.

`check.py` re-derives the finite claims with its own enumeration, independently
of `tools/knotlab` and of the Lean source:
- all 256 relations on three variables (two knots);
- knots of 2 to 6 loops (K1–K3, invisible in every smaller projection, and
  the three-literal chain);
- for knots of 2 to 4 loops, failure of majority and affine closure;
- for knots of up to 5 loops, the width n + 1 needed without witnesses;
- all 262,144 sets of unit and 2-literal clauses on three variables;
- 3,000 sampled 2-CNF systems with one to three witnesses;
- the hub, parity, the earlier kernel's accepted relation, and the gated and
  relational readings of the cross-wired guards.

It then compiles the kernel, lists the axioms each theorem uses, and confirms
that Lean rejects a mutated atom.

Each control runs on a deliberately wrong input, and each rejects it:
- dropping half of K2 admits more than two relations;
- a broken witness chain fails to define the knot;
- the majority test rejects the atom;
- the knot test rejects the hub;
- Lean rejects the kernel with `atom` replaced by `¬a ∨ k`.

The checker binds both predecessor manifests by SHA-256.

## Safe conclusion

In relational semantics with loop presence given:
- the two-loop knot is the atom ¬A ∨ ¬B ∨ c, up to which contact value
  counts as made;
- no 2-CNF with witnesses defines any knot;
- three-literal clauses with witnesses define the knot of any number of
  loops.

Proof 0009's verdicts stand on this evidence. Its executor gating and
syntactic jointness test are not inherited, and neither is the earlier
kernel's erasure condition.

## Nonclaims

- Nothing here forms a loop's presence natively. The native-formation flags
  stay false until ticket B decides that question.
- These results are about definability. The width threshold is not a
  complexity bound.
- One knot is the first atomic logical topology. It is not composed topology,
  a path or a metric.
