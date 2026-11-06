# Mutual selection: the decision

Epic `MUTUAL-SELECTION-20261031-001`, closed 2026-10-31. Program: foundations.

## The request

`KNOT-COUPLING-20261031-001` showed that on the knot's spaces exactly two non-trivial laws count easily: the knot's law (not-all-equal)
and the dimer law. The owner approved a bounded scan ("Yes, let's continue"): is this mutual selection special to the knot?

**Mutual selection.** A law has it when two things hold:
- its unsolvable cubic systems form a non-empty class that can be recognised in polynomial time;
- that class makes the law easy to count in return, and few others.

## What the lanes found

| Lane | Laws | Finding | Interest |
| --- | --- | --- | --- |
| A (`…001A`) | all symmetric laws, plain; exactly-one | A plain cubic system can fail only for a law that excludes both constant colourings. Among the seven symmetric knots only not-all-equal does. Exactly-one and exactly-two fail, but are NP-complete to decide (exact cover by 3-sets, every element in three sets; Gonzalez 1985). | 0/3 |
| B (`…001B`) | parity, clauses, with signs | Signed parity fails recognisably (inconsistent linear systems), but its whole coupling family is affine, so it selects nothing. Signed cubic clause systems never fail (Tovey 1984; 1,380,864 signings checked). | 0/3 |
| C (`…001C`) | the Fibonacci (no-lone) laws, with signs | They fail on many small cubic systems, globally, with irregular counts. Deciding them is NP-complete: a five-line gadget pins a port to a value, a line with a pinned point is an equality, and equality chains give fan-out, so Schaefer applies. The reduction was checked on 60 instances. | 1/3 (hardness), 2/3 (rigidity) |

**Verdict.** Among the symmetric three-place laws, only the knot has mutual selection.
- On plain systems it is the only knot that can fail.
- With signs it is the only law whose failures are both non-trivial and recognisable. Parity's failures are recognisable but select
  nothing; the Fibonacci laws' failures are coNP-complete to recognise, unless NP = coNP.

## Why: the knot has no preferred value

- **The elementary fact.** A three-place relation unchanged when every colour is flipped is a union of antipodal pairs. Among these the
  only knots (full two-place projections, not everything allowed) are the four signed not-all-equal relations. So the knot is the only
  three-place knot with no preferred value.
- **Consequences for gadgets.**
  - A law with no preferred value can never pin a value. A gadget's accepted set is closed under flipping every colour, and a pinned value
    is not.
  - The scan measured more. Not-all-equal gadgets with up to five internal points reach exactly three relations: nothing, everything, and
    not-all-equal itself. Fibonacci gadgets reach fifteen, including pinned values.
  - A pinned value turns one Fibonacci line into an equality, equalities give fan-out, and fan-out gives NP-completeness.
- **The knot cannot pin.** Its unsolvable cubic systems are exactly the Pfaffian signings (Seymour; Robertson–Seymour–Thomas), which can be
  recognised. On them, the knot's law and the dimer law count easily.
- **Arity (classical).** Every k-regular k-uniform system can be 2-coloured when k ≥ 4 (Alon–Bregman 1988 for k ≥ 8, Thomassen 1992 for
  k ≥ 4). On regular uniform systems the knot's law can fail only at three places, where the Fano plane fails.
- **In the owner's words.** Everything is relational: the knot is the one three-place law that never fixes a value, and three is the one
  arity at which such a law can fail. Laws that prefer a value can manufacture a constant out of relations alone, and that is where
  hardness enters.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — mutual selection across the symmetric three-place laws | **Status:** Successful | Every symmetric law is classified on plain and signed cubic systems. The knot is the only one with mutual selection. |
| Local direction — mutual selection | Continue, widened | Open: the asymmetric three-place knots, and whether not-all-equal gadgets are rigid at every size. |
| Broader exploration — the two/three boundary | Known alternatives | (a) pinning across all three-place knots (below); (b) rigidity of not-all-equal gadgets at every size; (c) folding the counting results into the note. |
| Long-term goal — the two/three boundary as emergence | Capability gained | The knot is singled out natively. It is the only three-place knot with no preferred value. Its failures are recognisable and select it back, while the knots that prefer a value pin it and become hard or trivial. Three is the only arity at which the knot's law can fail on regular systems. |
| Next recommendation — pinning across all three-place knots | **Next step:** Continue. Open a fresh epic over every three-place knot, symmetric and asymmetric, with signs. (1) Prove that pinning plus non-affinity makes deciding on cubic systems NP-complete (fan-out through pinned equalities, and Schaefer). (2) Find a pinning gadget for every knot that prefers a value, or an obstruction. (3) State the result: the knot is the only three-place knot whose impossibilities on cubic systems can be recognised non-trivially. | First discriminator: pinning gadgets for the asymmetric knots, such as x ∨ (y ≠ z), by the same catalogue search. Stop if some value-preferring non-affine knot provably cannot pin; that would be a second candidate for mutual selection. |
| Interest — that recommendation | **3/3 — Hot** | The evidence is concrete: the knot cannot pin and is easy, while the Fibonacci law pins and is hard. The payoff is a uniqueness theorem for the knot among all three-place laws, phrased in the owner's own terms (no preferred value). Main uncertainty: asymmetric knots may need larger gadgets, and fan-out from a pinned value may need a different equality gadget per law. |
| Execution — that action | Planned; awaits the owner | Alternatives: rigidity of not-all-equal gadgets at every size (2/3); the counting note (2/3). |
