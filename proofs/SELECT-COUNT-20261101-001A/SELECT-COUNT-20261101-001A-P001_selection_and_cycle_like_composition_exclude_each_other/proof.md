# Selection and cycle-like composition exclude each other

Status: Proved

Ticket `SELECT-COUNT-20261101-001A`, 2026-11-01.

## Question

- **The missing bridge.** `NATIVE-PATHS-20261101-001` ended with this missing bridge: a law that both selects its spaces and composes
  natively.
- **What each half means.**
  - *Selecting* is mutual selection (PINNING C): (M1) the systems where the law fails form a non-empty class recognisable in polynomial
    time, and (M2) the law's own count is #P-hard in general.
  - *Composing natively* is the program's criterion for composition with routes and a bond distance (NATIVE-NETWORK): the law's knots
    compose like cycles, i.e. they satisfy circuit elimination (KNOT-CIRCUITS).
- **Where the candidates are.**
  - At three places only the knot selects.
  - At four places only five weak classes of FOUR-PREFER (13–17) could still select; none failed in any search.
- **The question here.** Do any of them compose their knots like cycles? And can any law do both?

## Dependencies

- **`KNOT-CIRCUITS-20261020-001B`.** Definitions:
  - constrained sets, circuits, and knots (circuits of at least three variables);
  - *composes like cycles* (circuit elimination);
  - hubs.

  Results:
  - Theorem 2: a Boolean law composes like cycles iff it is affine, and composes its knots like cycles iff it is affine or bijunctive.
  - Proposition 3: two knots sharing only e form a hub iff every e-fibre of one meets every e-fibre of the other.
- **`FOUR-PREFER-20261101-001`.** The twenty four-place classes (library `prefer_lib`) and D's table, which leaves 13–17 open.
- **`PINNING-20261031-001C`.**
  - The definition of mutual selection.
  - Only the knot (not-all-equal) has it at three places.
  - Parity fails (M2), because its count is 2^(n−r) or 0.

## Theorem

1. **The weak classes do not compose their knots like cycles.**
   - **A forcing-place knot in each class.** Each of the 288 relations of classes 13–17 yields a knot with a *forcing place*, a place
     where one value allows every state.
     - Classes 13, 16 and 17 have one directly.
     - Classes 14 and 15 get one by identifying two places, which turns them into three-place clauses. For 6 of the 48 relations of
       class 15, the identified places carry opposite signs.
   - **The hub.** Two copies of such a knot sharing only its forcing place form a hub: both copies are circuits of their system, and the
     union minus the shared place is unconstrained. So circuit elimination fails.
   - **Consistency with Theorem 2.** None of the 288 relations is affine or bijunctive, which is what Theorem 2 requires.
2. **No law with a knot both selects and composes its knots like cycles.**
   - **The statement.** Let a Boolean law (plain or signed, of any arity) have at least one knot. If its knots compose like cycles, it is
     affine. Then its solution count is 2^(n−r) or 0, so (M2) fails and it has no mutual selection.
   - **At three places.** The knot selects and parity composes; they are different laws.
   - **At four places.** The weak classes cannot do both, whether or not they ever fail.

**Remark (the knot is needed).** A knot-free law can satisfy (M1) and (M2) and still compose its knots like cycles, vacuously.
- **Example: signed two-clauses (2-SAT with literals).** Their failures are recognised in polynomial time, and their count is #P-complete
  (Valiant 1979).
- **The boundary.** Selection without knots exists, but only below three places. This is the program's 2-versus-3 boundary once more.

## Proof

**Item 1.**
- **The hub.** Let K be a knot with forcing place j and value v.
  - Take two copies of K with their variables disjoint except the one at place j, called e.
  - **Every e-fibre contains v.** The e-fibre of an assignment x of the other places is the set of values of e with (x, e) ∈ K. It
    contains v, by forcing.
  - **So the fibres meet.** Every e-fibre of one copy meets every e-fibre of the other (in v). By Proposition 3 the pair is a hub.
  - **Directly:** set e = v, and every assignment of the other places of both copies is allowed. So the union minus e is unconstrained.
  - **Both copies are circuits.** K is a knot, and the other copy constrains nothing on K's places beyond what K does, since it allows
    both values of e.
- **The forcing places**, found by check 2:
  - Class 13 excludes {1011, 1101, 1110}, so 0 at place 0 forces.
  - Class 16 excludes {1101, 1110}, and class 17 excludes {1011, 1100}; in both, 0 at place 0 forces.
  - Class 14 excludes {0111, 1011, 1100}. With places 0 and 1 identified, it excludes only 100, a clause.
  - Class 15 excludes {0111, 1000, 1110}. With places 0 and 1 identified, it excludes only 110, a clause.
  - Every other member of a class is the canonical relation with places permuted and values flipped. Identifying two places of a member
    corresponds to identifying, with or without opposite signs, the matching places of the canonical relation. That is why six members
    of class 15 need opposite signs.

**Item 2.**
- **Theorem 2.** It says that knots composing like cycles force the law to be affine or bijunctive.
- **Bijunctive laws have no knot.**
  - A bijunctive relation is the set of tuples whose two-place projections are allowed.
  - A knot on k ≥ 3 places has full (k − 1)-place projections, hence full two-place projections.
  - So a bijunctive knot would be the full relation, contradicting K1. A law with a knot whose knots compose like cycles is therefore
    affine.
- **Affine laws fail (M2).** The solutions of an affine system form an affine subspace, so their number is 0 or 2^(n−r), computable by
  Gaussian elimination. ∎

## Checks

`check.py` (`result.json`, about 3 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Classes 13–17 are exactly the classes FOUR-PREFER D leaves open. All 288 relations are knots; none is affine, bijunctive or complement-closed. | pass |
| 2 | For every one of the 288 relations, a forcing-place knot and its hub. | 64 + 48 + 32 direct; 96 + 42 identified; 6 identified with opposite signs |
| 3 | Exhaustive at three and four places (34 and 742 knots): no bijunctive knot, and the affine knots are exactly the two parity cosets. | pass |
| 4 | The three-place table. Only parity is affine. The clause and x ∨ (y ≠ z) have forcing places. NAE and Fibonacci have none, and Theorem 2 covers them. | pass |
| 5 | Control: parity has no forcing place, and two parity knots satisfy elimination. The hub test fires on the clause. | pass |

## Reading

- **Composition belongs to parity, selection to the knot, and no law with a knot holds both.**
  - The knot fails in a way recognisable and still hard to count, and it composes only through hubs or pairwise (NATIVE-PATHS).
  - Parity composes like cycles, with routes and a bond distance, but its count is easy, so its failures select nothing.
  - The boundary between them is the affine boundary.
- **The weak four-place classes.**
  - They compose no better than the knot does.
  - Even if one of them turned out to fail selectively, it would not supply the bridge.
- **What remains.** The bridge between selection and native composition does not exist among Boolean laws with knots. To have both, a
  program would need composition other than cycle-like, or values beyond two.

## What this does not establish

- **Whether the weak classes ever fail.** This stays open, as in FOUR-PREFER C.
- **Non-Boolean laws.** Theorem 1 of KNOT-CIRCUITS covers Mal'tsev laws on larger domains; the exclusion is not claimed there.
- **Weaker notions of composition.** The statement concerns cycle-like composition only.

## Novelty

- **Ours.** Theorem 2, Proposition 3 and the definition of mutual selection.
- **Classical background.** Post's lattice and Schaefer, together with the affine count.
- **New here.**
  - The forcing-place hubs for the weak classes.
  - The exclusion statement.
  - The remark that selection without knots exists only below three places.
- **Folklore risk.** These are elementary consequences, and the folklore risk is moderate.
