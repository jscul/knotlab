# A parity knot among stitched copies

Epic `PARITY-MIX-20261112-001` (`LINE-LOCK-20261112-001` direction 2, chosen by the coordinator; G17 with G8; program mathematics,
group arithmetic), 2026-11-12. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `a29eb99c8`. Proof family:
`proofs/PARITY-MIX-20261112-001A/`. **Refereed: confirmed with fixes, headline narrowed** ([referee R1](referee-R1/report.md); fixes folded
in below and logged in `docs/CORRECTIONS.md`).

## The question

Stitched harmonies alone carry no additive law in their stitch (`LINE-LOCK-20261112-001`, refereed). What is the smallest change that
lets influence pass through whole counts of copies (the copies at one count along a copy shift), and is it typical or rare? The change
tried: make some of the mixed knots flip-blind parity knots (placewise sum all 0s or all 1s), which our knots can build (A78).

## The answer

**For the census's kind set of each harmony, parity knots and not-all-equal stitches almost never coexist, so the change is rare
there; under other kind sets that present the same harmonies it is not rare (the referee). Where they coexist, the whole passes
influence further than any knot does, mostly through both kinds of knot together.**

- **Settled by definition (stated before the run).** A parity knot forbids its copies from being all equal; with parity everywhere,
  the arrangement is Ledrappier's law on the differences of places, with states only at Ledrappier's sizes; a parity knot with two known
  copies makes the third known up to a flip.
- **Which harmonies can hold one (exact).** 8 of the 45 harmonies have a flip-blind triple; the other 37 end at their first parity knot.
  All 8 are made with the orbit of 0011 or 00101101 and another orbit, and in each the largest subspace of its classes has dimension 2.
- **Survival (exact on 3 × 3 and 4 × 4; sampled on 6 × 6 and 8 × 8).** With some but not all knots parity, a state survives in 2.8% of
  the placements on 3 × 3, 0.16% on 4 × 4, 0.34% of the samples on 6 × 6 and none of the samples on 8 × 8 (survivors exist on 8 × 8:
  every 4 × 4 survivor repeated twice each way is one; and the 6 × 6 samples weight every k equally, unlike the exhaustive 3 × 3 and
  4 × 4, so the rates are not a decay with size). A scattering of parity knots ends the
  arrangement. After the run: no flip-blind triple is a triple of the not-all-equal stitch, in all 8 harmonies, **for the census's
  kind sets**; for 12 of the 96 kind sets of span at most 8 that present the 8 harmonies it fails (0011 + 01 with kinds (1, 3) and
  (5, 6): the triple 1100, 1001, 0101), and under those survival is 21.8% on 3 × 3, and 12.6% on 4 × 4 at every k from 1 to 12 for the
  example, one parity knot surviving (the referee). Rarity is a property of a presentation, not of the harmony.
- **Beyond definition, where it survives (exact; recounted on every placement by the referee).** In 69 of the 114 surviving
  placements on 3 × 3 and 832 of the 850 on 4 × 4, count 0 fixes a count that the frozen propagation does not reach; full fixing in 39
  and 632. That propagation never passes a stitch for these harmonies, so against a fair baseline (the referee): the fixing needs both
  kinds of knot in 33 of 114 and 744 of 850 survivors (parity's own linear algebra in 15 and 48, parity with the harmony's states in 21
  and 40, stitches alone in none), and stays beyond arc consistency on classes in 15 and 454, all in the joint tier. So the frozen
  failure criterion is not met, on fewer survivors than the first count said.
- **Not typical at any mixed density.** Full fixing reaches at most 5.8% of the placements at any mixed k (the referee; 3.6% by the
  class representatives), and none in the larger
  samples; only parity everywhere gives it as a rule, and there it is definitional.
- **What survives (after the run).** On 3 × 3, three parity knots keep a state exactly when they are the three knots of one copy; over
  3 × 3 and 4 × 4, 606 of the 964 survivors are such sets of a copy's three knots joined, the parity knots surrounding whole copies.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Parity forbids all-equal copies; all-parity arrangements are Ledrappier's; propagation is local | proved by hand (definitional; with the advisor model) |
| 8 of 45 harmonies have a flip-blind triple, all of subspace dimension 2 | exact (frozen) |
| Mixed placements: survival 2.8% (3 × 3), 0.16% (4 × 4), 0.34% (6 × 6 samples), 0 (8 × 8 samples), for one kind set per harmony; counts fixed but unreached in 69 and 832 survivors (every placement) | exact on 3 × 3 and 4 × 4, sampled beyond (frozen; refereed) |
| Fixing against arc consistency: joint tier 33 and 744, beyond arc consistency 15 and 454 | computed by the referee |
| No flip-blind triple is a stitch triple (census kind sets only; false for 12 of 96 kind sets); copies' three knots as the usual survivors | after the run, descriptive; refereed |

## Against the pre-registration

Harnesses held (95%); every harmony with a flip-blind triple has subspace dimension 2 (60%: met); a count fixed but unreached with
k < nm (85%: met); full fixing typical only between half density and all parity (50%: not met, it is not typical at any mixed density);
states die out before all parity at 4 × 4 and 8 × 8 (60%: met); fewer than half the harmonies have a flip-blind triple (mine, 60%:
met, 8 of 45). All five parts finished inside their caps (the 6 × 6 samples in 44 minutes). The frozen failure criterion counted
placements with k below nm, which also includes k = 0, where counts fixed but unreached come from the not-all-equal locks of
`SHIFT-LOCK-20261112-001`; the numbers above count only 1 ≤ k < nm, so the parity-made ones.

## The coordinator's question on the 3 × 3 surprise

One parity knot among eight not-all-equal stitches on 3 × 3 leaves no state for any of the 8 harmonies. The referee's product lemma
(`LINE-LOCK-R1`) does not explain it by itself, since one triple is not a permutive set. My after-run partial explanation (no
flip-blind triple is a stitch triple, and in 3 harmonies the eight stitches force the ninth) is **not the reason**: one parity knot
empties 3 × 3 under all 96 kind sets, including those whose stitch holds flip-blind triples (the referee). The emptiness stays
computed, not explained.

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
  So globally influential folding of this kind is rare, not typical, for the kind set the census used; under some other kind sets
  presenting the same harmonies, parity mixes far more often (the referee), so the rarity is not the harmony's.
- **Next.** Whether a region of parity-bound copies inside a not-all-equal arrangement survives at every size and carries count 0's
  influence through it, the shape the survivors suggest.

## Assumptions

A70, A75, A77 used; A78 added (a parity knot among copies read as flip-blind parity, built from our knots).

## Corrections

After the referee (R1), logged in `docs/CORRECTIONS.md` and knotlab's HISTORY.md: rarity holds for one kind set per harmony
(Narrowing); "beyond local propagation" restated against a fair baseline (Narrowing); and, in one entry, the fixing counts on every
placement, the 3 × 3 explanation not the reason, A78's route replaced by the referee's gadget (57 knots, 53 hidden distinctions per
place, bare not-all-equal knots on single distinctions), the 8 × 8 samples as a bound on average survival only, and the failure
criterion read at 1 ≤ k < nm (Not a block). Earlier: None at the close. Later (logged in `docs/CORRECTIONS.md`, Not a block): the proof's "on 8 × 8 never" means none in the samples, since
every 4 × 4 survivor repeated is an 8 × 8 one; and the 6 × 6 and 8 × 8 rates come from samples with equal numbers at each k, a weighting
different from the exhaustive 3 × 3 and 4 × 4, so the four rates are not a decay with size. And (Not a block) "stars of copies"
named a copy's three knots with the literature's word for a vertex's neighbourhood; it now reads "a copy's three knots". (A progress message said 4 of 220 placements survived on 6 × 6; it is 6 of 1,760 across the 8 harmonies, edited in place.)

## In the owner's words

Mixing a parity tie, the kind where any two copies decide the third, into a pattern of copies tied the not-all-equal way almost
always breaks it: there is no state left. In the rare mixtures that survive, the parity ties wrap around whole copies, and then one
line of copies decides lines that no single tie reaches. So that kind of global influence exists, but with the knot kinds used here
it is rare; written with other knot kinds, the same patterns mix far more often.

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

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 13:35 UTC, verbatim:

> Done: a parity knot among stitched copies. The write-up is research/PARITY-MIX-20261112-001/parity_mix.md. The referee is pending.
>
> • **What our knots can build.** A plain three-member parity knot needs a zero, which the not-all-equal law can't make. The flip-blind kind (sum all 0s or all 1s) can be built from our own knots. That's what I used, recorded as assumption A78.
> • **Settled by definition.** A parity knot forbids all-equal copies. With parity everywhere, the arrangement is just Ledrappier's law.
> • **Who can hold one (exact).** Only 8 of the 45 harmonies have a flip-blind triple. The other 37 end at their first parity knot.
> • **Rare, not typical (exact on small repeats, sampled beyond).** With some knots parity and the rest not-all-equal, a state survives in 2.8% of placements on 3 × 3, 0.16% on 4 × 4, 0.34% of the 6 × 6 samples, and none of the 8 × 8 samples. A scattering of parity knots ends the pattern. After the run, I found that no parity triple is ever a not-all-equal stitch triple.
> • **Beyond any single knot, where it survives.** In most surviving placements, one count of copies fixes counts that no local propagation reaches. So the whole does reach further than its knots one at a time. The survivors mostly have parity knots wrapped around whole copies.
> • **The 3 × 3 surprise.** The referee's product lemma doesn't explain it by itself. In 3 of the 8 harmonies, the other eight knots force the ninth into a not-all-equal triple, which can't also be parity. For the other 5, the emptiness is computed, not explained.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — a parity knot among stitched copies | **Status:** Successful, referee pending | survival rare; influence beyond propagation where it survives |
> | Local direction — mixed laws on stitched copies | Continue | the survivors' shape (parity around whole copies) not yet grown |
> | Broader exploration — G17's census | Known alternatives | lagged free pairs (found by the referee); the travelling bases |
> | Long-term goal — G17 Typical and rare meeting patterns | Capability gained | additive influence among copies is rare, not typical |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Parity regions inside a not-all-equal arrangement | 2/3 — Substantial | 2/3 — Testable | blocks of b × b copies whose knots are all parity, b = 1 to 4, on repeats to 12 × 12 → survives at every size and one count fixes through it, or not | Selected · awaiting go-ahead |
> | 2 | Why parity triples are never stitch triples | 1/3 — Incremental | 3/3 — Ready | a proof for every harmony, or one where they meet | Alternative · deferred |
>
> **Corrections:** none this epic. One progress-message slip (I wrote "4 of 220" where it is 6 of 1,760) is edited in place. Separately, I folded in both referee verdicts that came back: locks across two shifts (one Narrowing: the 78 cells hold at my step cut, 17 at any cut) and lines in the increments (one Narrowing: the theorem is about the stitch itself; influence in arrangements stays open). **Goals:** G17 checkpoint, no goal change. **Assumptions:** A78 added. **Basket:** #1 and #2 recorded, plus the lagged free pairs. **Advisor:** consulted twice. It found most of my first design was settled by definition and proposed the reach test; then it checked the new words.
