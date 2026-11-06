# Pinning: decision at closure

Epic `PINNING-20261031-001`, closed 2026-10-31. Program: foundations.

## The request

The mutual-selection scan found that among the symmetric three-place laws only the knot (not-all-equal) has failing cubic systems that
can be recognised and that select it back. The owner approved extending this to every three-place knot, asymmetric ones included
("Continue"). The plan was to prove that pinning a value makes a law hard on cubic systems, and to find a pinning piece for every knot that
prefers a value.

## What was found

| # | Result | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Under flips and permutations, the 34 three-place knot relations form exactly five classes: parity, Fibonacci (no-lone), not-all-equal, x ∨ (y ≠ z), clause. | proved (enumeration) | A, Lemma 1 |
| 2 | Only not-all-equal excludes both constant colourings, so on plain cubic systems it is the only knot that can fail, asymmetric knots included. | proved | A, Lemma 2 |
| 3 | Only the four signed not-all-equal relations are unchanged by flipping every colour. Such a law cannot pin. | proved | A, Lemma 3 |
| 4 | **Pinning theorem.** A pinning piece, a relation that becomes an equality or disequality once one point is pinned, and a full piece make a law as hard on simple cubic systems as with unbounded occurrences. | proved; checked on 60 + 80 instances | A, Theorem 4; B |
| 5 | One skeleton pins every knot that pins: four internal points, the lines (0,1,2), (0,1,3), (0,2,3), and the tails (1,2,a) and (3,b,c). It pins the Fibonacci law, x ∨ (y ≠ z) and parity. | observed | A, B |
| 6 | The clause cannot pin (a pinning piece would contradict Tovey). Not-all-equal cannot pin (no preferred value). | proved | A |
| 7 | x ∨ (y ≠ z) is NP-complete on cubic systems. Its failures are absent on small systems (exhaustive for n ≤ 5) but exist: an explicit system has 25 lines. | proved | B |
| 8 | **Uniqueness.** Assuming P ≠ NP, not-all-equal is the only three-place knot whose failing cubic systems are non-empty and recognisable while its count is hard in general. On plain systems this holds unconditionally. Its failing systems also make the dimer law easy. | proved | C |
| 9 | The knot's recognition test, checked directly: on all 1,380,864 signings with n ≤ 6, a system fails exactly when its signing is Pfaffian (|det| = #PM). | checked | C |

**The stop condition.** It asked whether some knot that prefers a value provably cannot pin. The clause is such a knot, but it never
fails, so it is not a candidate for mutual selection. No other knot is.

## Reading

- **The knot is singled out natively.**
  - It is the only three-place knot with no preferred value.
  - It is the only knot that can fail on plain systems.
  - It is the only knot whose failures can be recognised and make hard counts easy.
- **The mechanism is pinning.**
  - A law that prefers a value can build that value out of relations alone.
  - A built value turns one line into an equality, and equalities give fan-out. Fan-out makes the cubic case as hard as the general one.
  - The knot can never build a value. Its pieces reach only nothing, everything and itself (checked up to five internal points).
- **In the owner's terms.** Everything is relational: the one three-place law that never fixes a value is the one whose impossibilities
  are visible, and three is the one arity at which such a law fails on regular systems (Alon–Bregman, Thomassen).

## Literature (brief check, 2026-10-31)

- **Dalmau and Ford (2003).** With the constant relations available, three occurrences per variable already make Boolean constraint
  satisfaction as hard as the unrestricted problem.
- **Our theorem.** The pinning theorem is the exactly-three version in which the law must manufacture its constants. It is close to
  Dalmau–Ford in spirit, so folklore risk is moderate to high.
- **Other ingredients.** The counting analogues for at most three occurrences appear in recent Holant work (arXiv 2201.03375).
  Exactly-three not-all-equal is polynomial by Seymour and Robertson–Seymour–Thomas.
- **What appears new.** The five-class census of three-place knots, the no-preferred-value lemma, the shared pinning skeleton and the
  uniqueness statement. No overlap was found.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — pinning across all three-place knots | **Status:** Successful | Every three-place knot is classified, and the uniqueness theorem is proved (conditional on P ≠ NP for signed systems, unconditional for plain ones). |
| Local direction — native selection among three-place laws | Complete | The three-place picture is settled. Open: rigidity of the knot's pieces at every size. |
| Broader exploration — the two/three boundary | Known alternatives | (a) arity four (below); (b) rigidity at every size; (c) a short note on native selection, gathering the coupling dichotomy, mutual selection and uniqueness. |
| Long-term goal — the two/three boundary as emergence | Capability gained | The knot is the unique three-place law that selects itself, and the reason is that it has no preferred value. Missing bridge: whether three is the only arity with a mutually selecting law. |
| Next recommendation — value-free laws on four places | **Next step:** Research directions. A bounded scan of the four-place knots with no preferred value, such as not-exactly-two (weights 0, 1, 3, 4), on 4-regular systems. Do any fail, can their failures be recognised, and do they select anything back? | Not-all-equal on four places never fails on 4-regular systems (Thomassen). A value-free four-place knot with recognisable failures would show that mutual selection is not special to three. If none exists, three is special. First discriminator: a census of failures on small 4-regular systems, and a search for equality-building pieces. |
| Interest — that recommendation | **2/3 — Promising** | It bears directly on the two/three thesis. The main uncertainty is the size of the four-place catalogue, and value-free laws that are hard by other routes. |
| Execution — that action | Planned; awaits the owner | Alternatives (2/3 each): rigidity of the knot's pieces at every size; a short note on native selection. |
