# Value-free laws on four places: decision at closure

Epic `FOUR-PLACE-20261031-001`, closed 2026-10-31. Program: foundations.

## The request

- **The question.** At three places the knot (not-all-equal) is the only law with mutual selection: its failures can be recognised, and
  its count is hard in general (PINNING C). Is three the only arity where that happens?
- **Approval.** The owner approved a scan of four-place laws with no preferred value ("Yes, let's continue with this"). It resumed after
  the parity correction, with that correction's two guards: no one-sided transforms, and a test of whether failures are local.

## What was found

| # | Result | Status | Evidence |
| --- | --- | --- | --- |
| 1 | The value-free four-place knots are 30 relations in four classes: parity (8 states), not-exactly-two (10), twelve (12), not-all-equal (14). None can pin. Only parity is Schaefer-tractable. | proved (enumeration) | A |
| 2 | Census over every signing of every 4-regular 4-uniform system with n ≤ 7 (1, 1, 4, 14 systems): not-all-equal never fails; parity and not-exactly-two fail on every system; twelve on all but three. | checked | A |
| 3 | For every k ≥ 4, signed not-all-equal never fails on k-regular k-uniform systems. A minimal failure would be square and sign-nonsingular (signed Seymour lemma), but the digraph has in- and out-degree ≥ 3 and is even (Thomassen 1992). | proved | B |
| 4 | Not-exactly-two and twelve build equality without constants: five-point link pieces without repeated lines. A regularization makes them NP-complete on 4-regular systems, so their failures are coNP-complete. | proved; 160/160 against a SAT solver | C |
| 5 | No value-free four-place knot is mutually selecting (unless NP-complete problems are polynomial). | proved | D |

## Answer

**Yes, among laws with no preferred value.**
- **At three places** the value-free law is rigid and fails, exactly on the Pfaffian spaces, which are recognisable and make hard counts
  easy.
- **At four places**, the value-free law that is rigid (not-all-equal) never fails. The others build equality and become as hard as
  satisfiability, and parity is easy to count.
- **The reason** is Thomassen's threshold. A k-place line gives a digraph of degree k − 1. Such digraphs can avoid evenness, which is
  what failure needs, only when k − 1 = 2.

## Reading

- **Three is special for a structural reason.** "No preferred value" singles out the knot at three places. At four places it is common,
  and it no longer protects a law: value-free four-place laws build equality without constants.
- **What selection needs.** It needs a law that is rigid and still fails. These two pull against each other, and three places is the only
  arity where both hold.
- **In the owner's terms.** The two/three boundary appears one level up, through Thomassen's even cycles: degree two can avoid even
  cycles, degree three cannot.

## Literature (checked 2026-10-31)

- **Thomassen (1992), "The even cycle problem for directed graphs", J. AMS 5.** Strong digraphs with minimum in- and out-degree at least 3
  are even; the paper lists applications to colour-critical hypergraphs and sign-nonsingular matrices. A related paper is Thomassen
  (1986), "Sign-nonsingular matrices and even cycles in directed graphs", LAA 75.
- **Seymour (1974) and Alon–Bregman (1988).** Plain hypergraph 2-colouring.
- **What appears new.** The signed version (any negations) follows by Seymour's argument, but no explicit statement was found
  (moderate folklore risk). The four-class census, the constant-free link pieces and the four-place uniqueness statement were found in no
  source.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — value-free laws on four places | **Status:** Successful | No value-free four-place knot has mutual selection. Value-free not-all-equal fails on regular systems only at three places (Thomassen). |
| Local direction — mutual selection across arities | Practically complete for value-free laws | Open: four-place laws that prefer a value (expected to pin or never fail), and the other value-free k-place laws for k ≥ 5 (expected to build equality). |
| Broader exploration — the two/three boundary | Known alternatives | (a) A note on native selection: coupling dichotomy, uniqueness, local versus global failures, the Thomassen threshold. (b) Four-place laws that prefer a value. (c) Composition of the knot's selected spaces toward native networks. |
| Long-term goal — the two/three boundary as emergence | Capability gained | A structural reason why three is special: selection needs a rigid law that fails, and Thomassen's threshold allows that only at three places. Missing bridge: from selection to composed native structure. |
| Next recommendation — choosing among (a), (b), (c) | **Next step:** Research directions. A bounded comparison of the three. Lean (a) if the owner wants the selection arc made reviewable, (c) if the aim is native emergence beyond selection. | (b) is likely to confirm the expectation (1/3). (a) converts several proved results into one reviewable piece (2/3). (c) is the step back toward the thesis (2/3). |
| Interest — that recommendation | **2/3 — Promising** | The selection arc is complete. The main uncertainty is which continuation adds most toward native emergence rather than presentation. |
| Execution — that action | Awaits the owner | Nothing is started without approval. |
