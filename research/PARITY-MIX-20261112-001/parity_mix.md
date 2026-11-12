# A parity knot among stitched copies

Epic `PARITY-MIX-20261112-001` (`LINE-LOCK-20261112-001` direction 2, chosen by the coordinator; G17 with G8; program mathematics,
group arithmetic), 2026-11-12. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `a29eb99c8`. Proof family:
`proofs/PARITY-MIX-20261112-001A/`. **Referee pending.**

## The question

Stitched harmonies alone carry no additive law in their stitch (`LINE-LOCK-20261112-001`, refereed). What is the smallest change that
lets influence pass through whole counts of copies (the copies at one count along a copy shift), and is it typical or rare? The change
tried: make some of the mixed knots flip-blind parity knots (placewise sum all 0s or all 1s), which our knots can build (A78).

## The answer

**Parity knots and not-all-equal stitches almost never coexist, so the change is rare; where they do coexist, the whole passes
influence further than any knot does.**

- **Settled by definition (stated before the run).** A parity knot forbids its copies from being all equal; with parity everywhere,
  the arrangement is Ledrappier's law on the differences of places, with states only at Ledrappier's sizes; a parity knot with two known
  copies makes the third known up to a flip.
- **Which harmonies can hold one (exact).** 8 of the 45 harmonies have a flip-blind triple; the other 37 end at their first parity knot.
  All 8 are made with the orbit of 0011 or 00101101 and another orbit, and in each the largest subspace of its classes has dimension 2.
- **Survival (exact on 3 × 3 and 4 × 4; sampled on 6 × 6 and 8 × 8).** With some but not all knots parity, a state survives in 2.8% of
  the placements on 3 × 3, 0.16% on 4 × 4, 0.34% of the samples on 6 × 6 and none on 8 × 8. A scattering of parity knots ends the
  arrangement. One reason, after the run: no flip-blind triple is ever a triple of the not-all-equal stitch, in all 8 harmonies.
- **Beyond definition, where it survives (exact).** In 69 of the 114 surviving placements on 3 × 3 and 806 of the 850 on 4 × 4, count 0
  fixes a count that local propagation from count 0 does not reach, and in 24 and 646 it fixes every count. So the frozen failure
  criterion (nothing beyond propagation) is not met: the harmony's states and the knots together reach further than the knots one by
  one.
- **Not typical at any mixed density.** Full fixing reaches at most 3.6% of the placements at any mixed k, and none in the larger
  samples; only parity everywhere gives it as a rule, and there it is definitional.
- **What survives (after the run).** On 3 × 3, three parity knots keep a state exactly when they are the three knots of one copy; over
  3 × 3 and 4 × 4, 606 of the 964 survivors are such stars of copies joined, the parity knots surrounding whole copies.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Parity forbids all-equal copies; all-parity arrangements are Ledrappier's; propagation is local | proved by hand (definitional; with the advisor model) |
| 8 of 45 harmonies have a flip-blind triple, all of subspace dimension 2 | exact (frozen) |
| Mixed placements: survival 2.8% (3 × 3), 0.16% (4 × 4), 0.34% (6 × 6 samples), 0 (8 × 8 samples); counts fixed but unreached in 69 and 806 survivors | exact on 3 × 3 and 4 × 4, sampled beyond (frozen) |
| No flip-blind triple is a stitch triple; stars of copies as the usual survivors | after the run, descriptive |

## Against the pre-registration

Harnesses held (95%); every harmony with a flip-blind triple has subspace dimension 2 (60%: met); a count fixed but unreached with
k < nm (85%: met); full fixing typical only between half density and all parity (50%: not met, it is not typical at any mixed density);
states die out before all parity at 4 × 4 and 8 × 8 (60%: met); fewer than half the harmonies have a flip-blind triple (mine, 60%:
met, 8 of 45). All five parts finished inside their caps (the 6 × 6 samples in 44 minutes). The frozen failure criterion counted
placements with k below nm, which also includes k = 0, where counts fixed but unreached come from the not-all-equal locks of
`SHIFT-LOCK-20261112-001`; the numbers above count only 1 ≤ k < nm, so the parity-made ones.

## The coordinator's question on the 3 × 3 surprise

One parity knot among eight not-all-equal stitches on 3 × 3 leaves no state for any of the 8 harmonies. The referee's product lemma
(`LINE-LOCK-R1`) does not explain it by itself, since one triple is not a permutive set. What does, in part (after the run): no
flip-blind triple is a stitch triple, and in 3 of the 8 harmonies the eight stitches already force the ninth cell's triple into the
stitch, so one parity knot is a contradiction; in the other 5 they do not, and the emptiness is computed, not explained.

## Known mathematics

Ledrappier's shift (1978) and the triangular plaquette model (Newman and Moore, 1999), whose states on 2^k sizes are trivial; closed
invariant subsets of algebraic shifts (Einsiedler, 2004); bootstrap and rigidity percolation (Aizenman and Lebowitz; Holroyd; Jacobs and
Thorpe); mixtures of linear and non-linear clauses ((2 + p)-SAT; Monasson and co-authors); locked constraint problems (Zdeborová and
Mézard); site-dependent cellular automata (Cattaneo and co-authors); for what not-all-equal can build, Schaefer and the Galois
connection. The definitional facts are folklore in this literature. The mixture on a harmony's states, its survival rates and the
counts fixed but unreached are new data; no mechanism is claimed new.

## What it changes

- **For the owner's "globally influential".** A knot of the additive kind can pass influence through whole counts of copies, but it
  does not mix with the not-all-equal stitches of repeating patterns: scattered among them it ends the pattern. Where both survive,
  the whole reaches further than the knots one at a time, but only in rare placements in which the parity knots surround whole copies.
  So globally influential folding of this kind is rare, not typical.
- **Next.** Whether a region of parity-bound copies inside a not-all-equal arrangement survives at every size and carries count 0's
  influence through it, the shape the survivors suggest.

## Assumptions

A70, A75, A77 used; A78 added (a parity knot among copies read as flip-blind parity, built from our knots).

## Corrections

None. (A progress message said 4 of 220 placements survived on 6 × 6; it is 6 of 1,760 across the 8 harmonies, edited in place.)

## In the owner's words

Mixing a parity tie, the kind where any two copies decide the third, into a pattern of copies tied the not-all-equal way almost
always breaks it: there is no state left. In the rare mixtures that survive, the parity ties wrap around whole copies, and then one
line of copies decides lines that no single tie reaches. So that kind of global influence exists, but it is rare, not typical.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a parity knot among stitched copies | **Status:** Successful, referee pending | survival rare; influence beyond propagation where it survives |
| Local direction — mixed laws on stitched copies | Continue | the survivors' shape (stars of copies) not yet grown |
| Broader exploration — G17's census | Known alternatives | lagged free pairs (`LINE-LOCK-20261112-001` #R1); the travelling bases |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | additive influence among copies is rare, not typical |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Parity regions inside a not-all-equal arrangement | 2/3 — Substantial | 2/3 — Testable | blocks of b × b copies all of whose knots are parity, inside the stitched arrangement, b = 1 to 4, on repeats to 12 × 12 → survives at every size and count 0 fixes through it, or not | Selected · awaiting go-ahead |
| 2 | Why flip-blind triples are never stitch triples | 1/3 — Incremental | 3/3 — Ready | a proof for every harmony, or one harmony where they meet | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained, with G8; no goal change). **Assumptions:** A78 added; A70, A75,
A77 used. **Basket:** #1, #2 recorded. **Advisor:** consulted twice before the freeze (it found most of the first design settled by
definition and proposed the reach test; then the words).
