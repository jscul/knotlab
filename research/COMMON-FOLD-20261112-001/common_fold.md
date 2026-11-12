# How common global influence is among random samples

Epic `COMMON-FOLD-20261112-001` (`ACROSS-FOLD-20261112-001` direction 1; G17 with G1, question 9; program topology, group spacing),
2026-11-12, at the owner's go-ahead. Pre-registered in commit 28c3a3f0d after the advisor model's critique of the design; both
censuses ran after. The canonical K1–K3 test is unchanged. **Referee pending** (handed to the referee thread).

## Words

As in the guide's glossary and the pre-registration: knot kind, tied along a shift, travels along a shift, a travelling base, global
influence along a shift, weighting W(r), sample, last base. The owner's word for what this epic counts is folding; the record's
unlengthened shift is what a travelling base has.

## The question

Base 16 is one sample nobody chose. Among random samples of meeting patterns, under a declared weighting, is global influence (a
bounded set whose values decide distinctions arbitrarily many steps away) typical or rare, and is base 16's kind of it, a pattern
that travels along a shift without ties, typical or rare? On random finite samples, how much of a base does a pair decide?

## The question in standard terms

For random periodic 3-uniform hypergraphs on ℤ² with r edge orbits drawn from a box, under proper 2-colouring: how often, among the
2-colourable ones, does a vertex force its translate (a tie along a shift), and how often does a finite pattern force its own
translate with no such tie? For random 3-uniform hypergraphs grown to non-2-colourability: the backbone of a conditioned pair, split
into the pair's own ties, unit propagation and search.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Global influence along a shift becomes typical as knots overlap more.** Under W(r) (the first r of one random order of the 171 kinds; each distinction in 3r knots), the share of bases tied or travelling along a shift is 0% at r = 1, 3.5% at 2, 18.5% at 3, 44% at 4, 68% at 5 and 81 to 87% at 6 to 8 (Wilson intervals in the table below). | computed, frozen (A1, A4 held) | A |
| 2 | **Base 16's kind is a middle-density phenomenon.** Travelling bases (tied along no listed shift) are 0% at r = 1 and 3.5% at r = 2, where base 16 sits, rise to 28% and 30% at r = 4 and 5 (the peak), and fall to 21%, 9% and 4% at r = 6, 7, 8. Most travelling sets have three distinctions, as base 16's does. | computed, frozen (A2 held) | A |
| 3 | **Near contradiction, ties take over.** Bases tied along a shift are 2% at r = 3, 16% at 4, 38% at 5 and 60%, 74%, 83% at 6, 7, 8, while contradictions rise from none at r ≤ 3 to 61% of the samples at r = 8: the bases left near the edge are rigid along a shift, one distinction deciding a whole line of others. | computed, frozen (A3, A5 held) | A |
| 4 | **The rates are lower bounds within the searched family, and stable.** A larger family on 50 samples raised the travelling rate by 0, 8 and 6 points at r = 2, 3, 4 (frozen bound 10, A6 held); travelling found but not certified by doubly periodic states is a further 0.5 to 8% of the bases per r; certificates are not monotone along prefixes (86 travelling bases lost one when a kind was added). Rates on lattice index 1 alone are the same within a point. | computed, frozen | A |
| 5 | **The lemma.** A certified travelling pattern on a free set A gives, for every k, a bond of at most \|A\| + 1 distinctions holding a + k t and a member of A, while steps apart grow linearly: an unlengthened shift. A tie along t gives bond distance 1 at every multiple of t. | proved (settled before the run) | A |
| 6 | **In finite random samples influence is local until the end, then global, and found only by search.** On uniform growth with 100 and 200 distinctions, a co-knotted pair decides about 1% of the base at half and three quarters of the way (one distinction, by propagation); at the last base it decides 85% and 82% on average, almost evenly at every number of steps (88 to 91% at one step, 72 to 75% at three), with at most 0.4% by propagation. Mostly this is the pair's own ties: 4.1% and 6.1% lie beyond them on average, so the frozen bound of 5% (B4) failed at 200, while single pairs outside the large tie class decide up to 91% beyond their ties. The tree control decides only the third of the pair's own knot (B1). | computed, frozen (exploratory; B1, B2, B3 held at 100 and 200, B4 failed at 200; 400 undecided) | B |
| 7 | **The samples with 400 distinctions did not finish.** All 20 needed more than 30 minutes each at the last base (solving at the edge of contradiction), in the registered run (stopped after 2 hours, nothing written) and in its rerun with a cap per run (all 20 dropped at the cap). B2 to B4 are undecided at 400. | deviation, recorded | B |

**Ticket A in numbers** (200 samples per r; among bases; Wilson 95% intervals):

| r | Contradictions | Bases | Unsettled | Travelling | Tied along a shift | Either |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | 200 | 0 | 0 (0–1.9%) | 0 (0–1.9%) | 0 (0–1.9%) |
| 2 | 0 | 200 | 0 | 7 (1.7–7.1%) | 0 (0–1.9%) | 7 (1.7–7.1%) |
| 3 | 0 | 200 | 0 | 33 (12.0–22.3%) | 4 (0.8–5.0%) | 37 (13.7–24.5%) |
| 4 | 3 | 197 | 0 | 55 (22.1–34.6%) | 32 (11.8–22.0%) | 87 (37.4–51.1%) |
| 5 | 20 | 179 | 1 | 53 (23.4–36.7%) | 68 (31.2–45.3%) | 121 (60.4–74.0%) |
| 6 | 62 | 131 | 7 | 28 (15.2–29.2%) | 78 (51.0–67.6%) | 106 (73.3–86.7%) |
| 7 | 97 | 98 | 5 | 9 (4.9–16.5%) | 73 (65.1–82.1%) | 82 (75.1–89.7%) |
| 8 | 122 | 75 | 3 | 3 (1.4–11.1%) | 62 (72.6–89.6%) | 65 (77.2–92.6%) |

## Answer

Typical, once knots overlap enough. Under a uniform weighting of small families of knot kinds, a random periodic base with one or two
kinds almost never lets a bounded set decide distinctions far away; with four or more it usually does, and near contradiction almost
always. Base 16's own kind of influence, a pattern that travels without ties, so that the law makes a direction of no length, is
rare where base 16 sits (two kinds, 3.5%) but common in the middle (about 30% at four and five kinds), and gives way to ties as
contradiction nears. In finite random samples a pair's value stays local until the last knots before the end; at the last base it decides four
fifths of the base at every distance, found only by search and mostly through its own ties, with a share beyond them that grew from
4% to 6% between 100 and 200 distinctions.

## Reading

**Interpretation, not a theorem.**
- **For the owner's "globally influential".** Global influence is not special to one chosen pattern: it is what overlap does. As each
  distinction joins more knots, a few values decide more and farther, first by patterns that travel (the law making its own
  unlengthened shift) and then, close to contradiction, by ties that bind whole lines. So "can be kind of globally influential" is
  the rule for dense overlap under this weighting, not the exception.
- **Three regimes.** Few kinds: free, local. Middle: travelling, a geometry of the law's own (base 16's kind). Near the edge: tied,
  rigid. The middle regime is where the law reads a dimension different from the meeting pattern's; the edge is where it reads almost
  none.
- **The same edge in finite samples.** Growing finite samples meet the edge from the other side: influence stays local until the
  last knots, then a pair decides most of the base, mostly through ties, as `RANDOM-FATES-20261112-001` found for ties alone. Near
  contradiction, periodic and finite samples alike are held by ties.
- **For G17.** These are rates under one declared weighting each (A71); a different box or a different process could move them. The
  regimes, not the numbers, are the reading.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** The lemma (conclusion 5). **Computed.** Every rate, per presentation under
  W(r), within the searched family (sets of 2 to 4 cells in a 2 × 3 box, ten shifts, a 15 × 19 window, doubly periodic certificates
  up to period 8): lower bounds on global influence.

## Stress test

The sensitivity part is the one-size-past test of the search family (A6): it moved the travelling rate by at most 8 points. Ticket B
could not go one size past (400 distinctions) within its caps.

## Review

Referee pending: handed to the referee thread on 2026-11-12.

## Literature and provenance

- **Known.** Random ℤ^d shifts of finite type (McGoff and Pavlov 2016) are studied for emptiness, entropy and periodic points;
  deterministic and expansive directions of two-dimensional shifts of finite type (Boyle and Lind; Zinoviadis; a subshift
  deterministic in every direction is finite); failures of strong irreducibility and spatial mixing; backbones and frozen variables
  in random constraint problems.
- **Not found** (bounded search): how often small random families of not-all-equal kinds travel or tie along a shift; the three
  regimes.
- **Classification.** New as stated, folklore risk moderate (directional determinism is well studied, its frequency in random
  families of this kind is not).

## Workspace assumptions

- **Relied on.** A64, A67, A71. **Added.** A76 (global influence on periodic bases read as ties or travelling along a shift; on finite
  samples as the forced fraction of a small set).

## Advisor model

Consulted before freezing (the owner's rule of 2026-11-12): it found the confound that changed the design (bases near contradiction
tied along a shift, not travelling), asked for nested prefixes, the free-set condition and complement symmetry in the lemma, lattice
and reflection strata, rates over bases and over bases plus unsettled, a sensitivity part, and for finite samples the split into
ties, propagation and search with a shell profile.

## Ratio

- **Substantive.** Two frozen censuses and a sensitivity part; the lemma.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**): the pre-registration (commit 28c3a3f0d) and this note's first version
(80d5c66a3) named the new assumption A75 before reserving the number, and A75 is `BASES-WITHIN-20261112-001`'s; it is A76. Two
deviations, recorded here and in `docs/LONG_RUNNING.md`: ticket B's registered run was stopped after 2 hours with nothing
written (it writes only at the end, and its 400-distinction samples did not finish; its runtime estimate of 15 minutes was wrong),
and was rerun unchanged with each run written as it finished and a cap of 30 minutes per run (`rerun_b.py`), which dropped every
400-distinction sample; its summary leaves out the per-distance profile, which the frozen summary code would have tried to add up
as a number (a bug that would have stopped the registered run after all its runs), and was written from the saved runs after the
rerun's own time limit stopped it at the same step. The same happened to `PARITY-FIVE-A2` on 2026-11-11 (a part that writes only at the end keeps nothing when
stopped): write each run as it finishes.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — how common global influence is | **Status:** Successful, referee pending | Every frozen prediction of ticket A held; ticket B held at 100 and 200 distinctions except the bound beyond ties, undecided at 400 |
| Local direction — the middle regime | Continue | A third of bases travel at four to five kinds: what the law reads there is the next measurement |
| Broader exploration — G17 under other weightings | Known alternatives | Bigger boxes of kinds, three shifts, other growth processes |
| Long-term goal — G17 with G1 | Capability gained | Global influence is typical under dense overlap, in three regimes; the law's own geometry is a middle-density regime, not one chosen sample |

**Corrections:** one, Not a block (the new assumption's number; two deviations recorded besides). **Goals:** a G17 checkpoint (capability gained), served with G1; no goal change.
**Assumptions:** A76 added (the pre-registration called it A75, a number another thread had taken; one correction, Not a block). **Basket:** `ACROSS-FOLD-20261112-001#2` (all bonds across, 2/3, 2/3), `ACROSS-FOLD-20261112-001#3` (the other
folding classes, 2/3, 3/3), `FOLD-20261112-001#2` (the other shortcuts, 2/3, 3/3); taken: `ACROSS-FOLD-20261112-001#1` by this epic.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What the law reads on typical travelling bases | 3/3 — Major | 2/3 — Testable | On the travelling bases of this census at r = 4 and 5, find the self-keeping sets (the flip form generalized) and measure bond distance across the unlengthened shift → the law reads one dimension across on most of them, or base 16 is special | Selected · awaiting go-ahead |
| 2 | Why ties take over near contradiction | 2/3 — Substantial | 2/3 — Testable | On the tied bases, find what forces the tie (a pattern of kinds) and whether a criterion predicts tie, travel or neither from the kinds → a rule, or none | Alternative · deferred |
| 3 | Other weightings | 2/3 — Substantial | 3/3 — Ready | Rerun ticket A with a larger box of kinds and with three shifts → the three regimes hold, or depend on the weighting | Alternative · deferred |

1. **Typical travelling bases.** Payoff 3: whether the law's own lower-dimensional geometry is typical in the middle regime decides
   whether base 16's line is a curiosity. Concreteness 2: the travelling sets are recorded; the flip form needs generalizing.
2. **Ties near contradiction.** Payoff 2, concreteness 2.
3. **Other weightings.** Payoff 2, concreteness 3: the code exists.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
