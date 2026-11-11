# Infinite bases with periodic overlap

Epic `PERIODIC-READ-20261111-001` (`OVERLAP-READ-20261111-001` directions 1 and 2; G1, question 9; program topology, group
spacing), 2026-11-11, at the coordinator's go-ahead under the owner's standing mandate. Pre-registered in commit 8f760e476 before any
registered run. The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary (`publication/knotlab/INTUITIONS.md`) and the pre-registration: a **meeting pattern** says which knots
share which distinctions; a **periodic knot pattern** repeats it under every integer shift of Z^d (d = 1 or 2), with one distinction
of each kind and one knot of each kind at each shift, and nothing limiting how many knots lie on a pair (literature: a periodic
3-uniform hypergraph); a **finite repeat** is the pattern modulo a sublattice (literature: a periodic quotient); the **window** of
radius R is the part with shifts in [−R, R]^d; the **unit** at a shift is its distinctions. Tied pairs, frozen distinctions, unnamed
hollow triples and reading faithfully are as in `OVERLAP-READ-20261111-001`.

## The question

Which infinite bases with a periodic meeting pattern does the not-all-equal law (NAE) read faithfully, with how much overlap, and what
does an infinite base show that its finite repeats do not? Beside it: what are `OVERLAP-READ-20261111-001`'s global hollow triples?

## The question in standard terms

For periodic 3-uniform hypergraphs over Z and Z², which have proper 2-colourings under which the restricted sets of at most three
vertices near a unit are exactly the edges, and how does that compare with their periodic quotients? And are the triples that only
a whole swapped torus triangulation restricts the removed triangles, restricted by the other colour class of triangles?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Along one shift the reading is exact.** All 181 one-shift patterns settle (P1 held): 73 read faithfully, 23 of them with a pair in three or four knots. | computed, exact (the window bound is a theorem) | A |
| 2 | **Along two shifts, an infinite base can carry a pair in four knots.** Of 627 two-shift patterns, 134 are read faithfully, 331 are not and 160 stay unsettled (2 have no state). 36 of the faithful ones have a pair in three or more knots and 2 a pair in four (P2 held): one co-knotted pair in four knots and five in one each. | computed, settled by the three bounds | A |
| 3 | **The infinite base is not its finite repeats.** 25 two-shift patterns read faithfully have no finite repeat of index 9 to 30 read faithfully (P3 held), and across all faithful patterns only 7.7% of finite repeats are read faithfully. Most verdicts need repeats in one shift only, whose states can change from one repeating regime to another (literature: a domain wall), a state no finite repeat holds: without them, 128 of the 134 faithful verdicts and 26 of the 331 others would be unsettled (the referee's count). | computed | A |
| 4 | **The ruler's first step survives at infinity.** In every two-shift pattern read faithfully, each of the 4,858 pairs two steps apart lies in a bond of four whose other two distinctions are each next to one of the pair (P4 held): the unbonded pairs of the finite overlapping bases do not appear here. | computed | A |
| 5 | **Source labels.** 87 of the 134 two-shift and 68 of the 73 one-shift faithful patterns are native at their first periodic state: every kind's distinction is flipped by a change within three shifts. For the others no such flip was found there, a lower bound on nativeness, not a proof of rigidity. | computed (measured, not predicted) | A |
| 6 | **Two classes with equal pair counts read alike (proved).** If the knots of a finite pattern split into two classes meeting every co-knotted pair once each, both classes and their union have the same states. Checked on all 272 six-regular one-pair weaves (literature: flat tori) with 12 to 24 distinctions. | proved; checked | B |
| 7 | **What the global hollow triples are.** In 91 of `OVERLAP-READ-20261111-001`'s 98 global bases, every triple only the whole base holds is a knot the swaps removed (G1 failed narrowly); where the removed knots lie in one class (85), the untouched class forces each of them (G2 held, a corollary of the lemma), and in the other 13 the remaining knots of the other class with the swapped-in knots do. Of the 7 exceptions, 3 follow locally once the removed knots are put back; in the three smallest bases (25 to 27 distinctions) "only the whole base" is degenerate, since two steps already reach every knot; the clear exceptions are a triple on 25 distinctions held by an odd cycle that wraps once around the weave, and a triple of three distinctions in a row on 35. None of them has a pair-count certificate like the two classes (the referee's test). | proved (the mechanism); computed | B |

## Answer

Infinite bases with a repeating meeting pattern can carry real overlap and still be read natively: along one shift the reading is
exact and pairs lie in up to four knots; along two shifts the law reads 134 of 627 patterns faithfully, 36 with a pair in three or
more knots and two with a pair in four, and in all of them pairs two steps apart share a bond of four, the ruler's first step. The
infinite base is a different object from its finite repeats: most finite repeats of a faithfully read pattern are not read
faithfully, and some value patterns live only in states that change from one repeating regime to another. The global hollow triples
of the finite census are, in almost every case, a removed knot held by the other class of knots, which has the same pair counts.

## Reading

**Interpretation, not a theorem.**
- **Base realities.** In the owner's sense an infinite meeting pattern is a base reality. Here such bases exist with overlap the law
  still reads natively, and they are not the same as any of their finite repeats: the infinite pattern has states the finite ones
  cannot hold, and loses the short cycles that make finite repeats misread.
- **Overlap at infinity looks like a spine.** Both bases with a pair in four knots have one co-knotted pair, repeated along one shift,
  lying in four knots, and every other pair in one: many knots hang on a repeated pair, like the pages of a book along a line.
- **Two halves of one weave.** A two-fold weave whose knots split into two classes is read the same from either half. Remove a knot
  from one half and the other half still holds it, through the whole weave: that is what the global hollow triples were.
- **For question 9.** The ruler's first step holds on every faithfully read infinite base in the family, overlap included; whether
  bond distance grows like graph distance further out is the next measurement.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** The two-class lemma. **Computed.** Everything else, in the registered families
  only: one-shift patterns with shifts in {0, 1, 2}, two-shift patterns with one kind of distinction, shifts in {−1, 0, 1}², all with
  one or two knot kinds and 500 of the 2,120 with three. Two-shift verdicts are settled by the bounds; 160 are not.

## Stress test

One-shift readings are exact by the window bound. Two-shift readings: each verdict counted is settled by a finite repeat or a
one-shift repeat (extends) or a window (does not). The pilot's larger window and index (radius 9, index 48) settled nothing more on 40
patterns, so the unsettled ones need either larger windows or states that never repeat.

## Review

An independent referee (a fresh agent with code sharing nothing with the census: an exact transfer-graph reader along one shift, its
own finite repeats, one-shift repeats and window, other SAT solvers) found the bounds sound and reproduced every verdict:
- **One shift:** all 181 patterns agree with its exact reader (every verdict and every bond row). The pre-registration's window bound
  is stated with an extra span term; the sufficient bound is R ≥ M + 2^(k·span), which R = 24 meets for every set read. P1 could not
  fail as coded, since the exact window never returns unsettled; the referee's transfer-graph reader is its control.
- **Two shifts:** all 627 readings reproduced (625 verdicts with their reasons, the 2 with no state, the 160 unsettled counts). The two
  bases with a pair in four knots are faithful on all 57 distinctions near a unit, and with five P3 examples they stay faithful one size
  past, at graph distance 3. The one-shift repeats are exact and their states are states of the infinite base (4,050 random queries
  agree with its construction).
- **P4** holds as coded, with the bond's other two distinctions each next to one end of the pair; read as both next to the same end it
  would fail for 2,288 of the 4,858 pairs, so the pre-registration's wording is narrower than its code (see Corrections). The summary's
  "P5" is a measured quantity, a lower bound on nativeness.
- **Ticket B:** the lemma is correct; its statement should ask for equal pair counts (a quotient can put two lattice edges on one pair,
  giving two knots of each class), now so stated. `check.py` is correct, but its notion of "only the whole base" degenerates on the
  three smallest weaves; the four unexplained triples are described in conclusion 7.

## Literature and provenance

- **Known.** Shifts of finite type and their de Bruijn graphs (Lind and Marcus 1995); undecidability of emptiness and states that
  never repeat in two dimensions (Berger 1966; Robinson 1971); domain walls; the two-class lemma as an instance of trades (Hedayat and
  Li 1979) and of the NAE-to-maximum-cut triangle gadget.
- **Not found** (bounded search): a census of NAE on periodic hypergraphs, or of which periodic overlaps it reads faithfully.
- **Classification.** Known-with-delta: the tools are classical; the census, its comparison with finite repeats and the reading of
  the global triples are the delta.

## Workspace assumptions

- **Relied on.** A67 (a base is read on sets of at most three distinctions), A64. **Changed.** None.

## Ratio

- **Substantive.** The census (one registered run), the two-class lemma and its check, an after-run description of G1's exceptions,
  one referee pass.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**), on the published pre-registration: P4 said a bond of four "with two
distinctions next to one of them", while the code, and the verdict, take each of the two next to one end of the pair; and the one-shift
window bound carried an unneeded span term. The frozen code's summary also scores a fifth item it calls P5; it was registered as
measured, not predicted, and is reported as conclusion 5.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — infinite bases with periodic overlap | **Status:** Successful | P1 to P4 held; overlap read natively at infinity; the global triples explained but for 4 |
| Local direction — NAE on infinite overlapping bases | Continue | The ruler beyond its first step and the balls' growth are unmeasured; 160 readings unsettled |
| Broader exploration — G1 on bases of knots alone | Known alternatives | Rigid periodic states; the catalogue's growth; reading by pair counts |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | Infinite bases with overlap are read natively, and differently from their finite repeats |

**Corrections:** one, Not a block (the pre-registration's wording of P4 and of the window bound). **Goals:** a G1 checkpoint (capability gained), no goal change. **Assumptions:** none changed.
**Basket:** `OVERLAP-READ-20261111-001#3` (the catalogue's growth, 1/3, 2/3), `OVERLAP-READ-20261111-001#4` (reading by pair counts,
2/3, 1/3), `LONG-LOOP-20261111-001#3` (bond balls read dimension 2, 2/3, 2/3); taken: none yet; direction 1 below is the first.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Bond balls on infinite overlapping bases | 3/3 — Major | 2/3 — Testable | On the 134 faithful two-shift bases, count distinctions within bond distance 2, 3 and 4 of a unit and fit their growth → dimension read natively on an overlapping infinite base, or a base whose balls stop growing | Selected · awaiting go-ahead |
| 2 | Settle the unsettled | 1/3 — Modest | 2/3 — Testable | Repeats in one shift with longer periods, and windows past radius 9, on the 160 → each settled, or a pattern whose verdict needs states that never repeat | Alternative · deferred |
| 3 | Rigid periodic states | 2/3 — Substantial | 2/3 — Testable | For the 47 two-shift patterns rigid at their first periodic state, find a native state or prove every state rigid → native everywhere, or a base read faithfully with no native state | Alternative · deferred |
| 4 | The four unexplained global triples | 1/3 — Modest | 3/3 — Ready | Test for a second pair of knot classes with equal counts in those four bases → explained, or a new mechanism | Alternative · deferred |

1. **Bond balls.** Payoff 3: it is the measurement in place of the ruler that question 9 needs, on the owner's infinite bases.
   Concreteness 2: the bases and the bond test exist; bonds of five and six cost more.
2. **Unsettled.** Payoff 1, concreteness 2.
3. **Rigid states.** Payoff 2: a base read faithfully with no native state would separate the two readings the canon names.
   Concreteness 2.
4. **Four exceptions.** Payoff 1, concreteness 3.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
