# The knot is the only three-place law with mutual selection

Status: Proved

Ticket `PINNING-20261031-001C`, 2026-10-31.

## Dependencies

- **`PINNING-20261031-001A`.** Five classes, plain systems, no preferred value, the pinning theorem, Schaefer status, and the clause.
- **`PINNING-20261031-001B`.** x ∨ (y ≠ z) is NP-complete on cubic systems.
- **`KNOT-COUPLING-20261031-001`.** On the knot's spaces the dimer law is (−2)ⁿ |det|, and counting is easy exactly at the knot's law, the
  dimer law and the affine couplings.
- **`MUTUAL-SELECTION-20261031-001`.** The Fibonacci law is NP-complete on cubic systems (lane C). Parity's family is affine, and the clause
  never fails (lane B).
- **External, not replayed.**
  - Seymour (1974) and Robertson–Seymour–Thomas (1999): a cubic system fails not-all-equal iff its signing is Pfaffian, and Pfaffian
    signings can be found in polynomial time.
  - Kasteleyn's theorem.
  - Fan and Cai (2020): counting 2-colourings of cubic triple systems is #P-complete.
  - Dagum and Luby (1992): perfect matchings of cubic bipartite graphs are #P-complete to count.
  - Schaefer (1978) and Tovey (1984).

## Definition

A three-place knot R is *mutually selecting* on cubic systems (plain or signed) when:
- **(M1)** the connected cubic systems on which R fails form a non-empty class, recognisable in polynomial time; and
- **(M2)** counting R-solutions is #P-hard on general cubic systems.

So the failing class makes easy what is hard elsewhere. On the class R's own count is 0.

## Theorem

**Statement.**
1. On plain cubic systems, not-all-equal is the only three-place knot that can fail. This is unconditional.
2. Assume P ≠ NP. Among all 34 three-place knot relations, in five classes, exactly the not-all-equal class is mutually selecting on signed
   cubic systems. Its failing systems also make a second law easy that is #P-hard in general: the dimer law, whose count there is
   (−2)ⁿ |det|.

**Proof.** Part 1 is Lemma 2 of ticket A. For part 2, take the five classes of ticket A, Lemma 1:

| Class | Fails on signed cubic systems | (M1) | (M2) | Mutually selecting |
| --- | --- | --- | --- | --- |
| parity | yes (inconsistent linear systems) | yes (linear algebra) | no: affine, its counts are 2^{nullity} or 0 | no |
| clause | never (Tovey) | no: empty class | yes | no |
| Fibonacci (no-lone) | yes | no unless P = NP: recognising its failures is coNP-complete (pinning theorem; MUTUAL-SELECTION C) | yes | no |
| x ∨ (y ≠ z) | yes (e.g. a 25-line system) | no unless P = NP (ticket B) | yes | no |
| not-all-equal | yes (exactly the Pfaffian signings) | yes (Robertson–Seymour–Thomas) | yes (Fan–Cai; the counting arc) | **yes** |

- **Why coNP-completeness rules out (M1).** If a coNP-complete class were recognisable in polynomial time, then P = coNP and hence P = NP.
- **The knot's (M1) on plain systems.** Plain knot's spaces are the non-2-colourable cubic systems, recognisable through sign-nonsingularity
  of the incidence matrix (Seymour; Robertson–Seymour–Thomas).
- **The second law.** The dimer law is #P-hard in general: it is (−2)ⁿ times the permanent of a cubic incidence matrix, which is
  Dagum–Luby. On the knot's spaces it is a determinant (KNOT-COUPLING A, Proposition 8). ∎

## Checks

- **Upstream (check 1).** Every upstream proof is Proved and every upstream check passed.
- **The knot's recognition mechanism (check 2).** Every signing of every cubic system with n ≤ 6: 1,380,864 signings, 2,176 of them failing.
  The signed not-all-equal system fails exactly when |det| of the signed incidence matrix equals the number of perfect matchings, i.e.
  exactly when the signing is Pfaffian.
- **The table (check 3).** It is assembled and checked against tickets A and B.

## Reading

- **The knot is singled out.** Among three-place laws it is the only one whose impossibilities can be recognised and that selects itself
  back.
- **The reason is native.** The knot is the only three-place knot with no preferred value (ticket A, Lemma 3), so it cannot pin. Every other
  knot that can fail does pin, and pinning makes its failures as hard as satisfiability. The clause prefers a value but never fails. Parity
  fails recognisably but is affine.
- **In the owner's terms.** Everything is relational: the one law that never fixes a value is the one whose failures are visible. On
  regular systems it fails only at three places (Alon–Bregman, Thomassen).

## What this does not establish

- **Laws on more places.** For not-all-equal on k places, k-regular systems never fail when k ≥ 4, but other k-place knots are not
  classified here.
- **Unconditional statements on signed systems.** These need P ≠ NP.
- **Rigidity of the knot's pieces at every size.** This was observed up to five internal points (MUTUAL-SELECTION C) and is not proved.

## Novelty

- **Classical ingredients.** Schaefer, Tovey, Seymour, Robertson–Seymour–Thomas, Kasteleyn, Fan–Cai, Dagum–Luby.
- **No overlap found yet.** The notion of mutual selection, the five-class census, and the uniqueness statement. The literature check
  comes at closure.
