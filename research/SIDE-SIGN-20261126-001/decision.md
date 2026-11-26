# A sign to the sides: what stands

> **Referee report R1, 26 November 2026: confirmed with fixes, no Block** ([the report](referee-R1/report.md)). Two exact
> tables at CHSH 4 were rebuilt independently (start 3097 with the block sign; a seven-knot not-all-equal stage grown
> once from start 1212 with the swap's sign on kept states), every structural count matched on all 7,075 starts, and
> all 8,856 sampled weighting-and-reading summaries matched. Read this record with these narrowings.
> - **Placements were counted with repeats.** A distinction shared inside a side was listed once per holder, so some
>   placements were tried more than once. Distinct placements: parity W1 923, 32,552 and 107,804 at rounds 0, 1 and 2
>   (not 1,397, 32,840 and 109,936); W2 25 (not 100); not-all-equal W1k 7,382 and 55,488 under R1, 4,310 and 3,096
>   under R2 (3,016 of the last at 4 and 80 at 12/5); W3 132, 996, 1,328; W3m 12, 1,600, 6,856. The stages with a hit
>   and every winning value are unchanged; the parity unsigned control covers 92,134,111 distinct placements.
> - **"Through the completions" was tested on four values, not on the reading.** Every R1 hit needs weights of both
>   signs; the annotation checked a full four-value word and only the first 20 hits of a row. Every parity W1 hit has a
>   four-value word with both signs; 64 and 144 not-all-equal W3m hits (rounds 1, 2) and 16 W1k hits (round 2) do not,
>   cancelling only across the readers' chosen pair. "Every hit after growth goes through the completions" is withdrawn
>   in that form; so is "every one annotated" for the round-0 W1 hits (743 of 1,397 entries were annotated).
> - **What a state reads of a swap is its mismatch x + swap(x).** Kept and flipped are two of its values; most swap rows
>   also have states of neither kind. A chain from a knot to its image establishes the exchange; the two-distinction
>   read measures only the state's mismatch on that pair. "A state sees the twist only as kept and flipped" is narrowed
>   to that.
> - **The controls show a swap is unnecessary in those examples, not that R1 and R2 reward every sign.** Random matchings
>   (94 of 200 on one stage) and products of two single-distinction signs (156 of 231 on another) were rebuilt; they say
>   nothing about a frequency over arbitrary signs, and writing W1k as single-distinction signs keeps its restriction to
>   kept states. "R1 and R2 reward any sign" is narrowed to "R1 and R2 give the excess without the swap on the stages
>   tested".
> - **The tie is on the signed support.** Parity hits have one read of each reader tied among the words with nonzero
>   signed weight, not among the allowed words (start 89: all 16 words occur, summation cancels those with x₄ ≠ x₉).
>   W2's excess needs both side parities to be functions of the four reads (the advisor's lemma holds); "only where the
>   sides are small" has no size bound behind it.
> - **A sign the table missed.** The sign of the swap on a state's own orbit (+1 if kept, −1 otherwise) needs no held
>   value or ordering; on all 23,760 parity lift rows it gives no hit, though a constructed growth with the readers' pools
>   relaxed reaches 4 with it. W1 is also the sign of the permutation the lift induces on H(x) ∩ swap(H(x)), the held
>   distinctions kept by it, on every state.
> - **Smaller fixes.** The not-all-equal cutoff was more than 22 distinctions, not more than 2^22 states (all 10 round-1
>   and 142 round-2 exclusions of width 23 have fewer); "U at most 18/29" holds for distinct placements, the stored
>   round-0 maximum 10/13 comes from a lift with no eligible placement; on four classes 46 of 102 lift rows on 27 stages
>   and on eight 6 of 6 on two move classes; at the rings' first round there is one motion class, so the old-shared sign
>   is a character there; A2's "need only" should read "require"; the two-reader bound for the change-read direction
>   covers the stated observables only; a fixed-width square could overflow at 2^30 entries (no published value
>   affected); the blow-up start's round 2 and the excluded not-all-equal searches were not run.

Epic `SIDE-SIGN-20261126-001` (G18, at the coordinator's pick after the owner's message "it might be a symmetry thing
too where there's a sign to the sides or something. It'd be a complex meeting pattern"; register entry A292), closed
26 November 2026. A census with arguments: computed, with proofs where marked; referee pending.
[The note](README.md) · [advisor's question](advisor_question_1.md) and [answer](advisor_answer_1.md) ·
[census tally](census_tally.md)

## What stands

1. **Swaps are made and kept by growth (computed, with an argument).** A renaming of order two that moves a knot (a swap)
   is found in 2,164 of the 7,075 census arrangements and in more stages after growth; ordinary growth never removes a
   swap of the knots (0 of 7,383 start, law and round triples), because it reads only what every renaming keeps (Lemma R).
   Which distinctions a swap pairs can change from round to round.
2. **The sides exchanged round a loop are real (proved).** One-sided swaps, where a chain of knots joined through moved
   distinctions leads from a knot to its image, occur at every round; no renaming removes them (the literature's
   nontrivial double cover). A state sees the twist only as the sort into kept and flipped states: a flipped state is an
   assignment that changes value each time a twisted loop is gone round.
3. **The sort into kept and flipped carries no weight (proved, checked).** It is the action of one renaming, so the
   counting weighting gives every state the same weight. Flipped states need a swap that moves every distinction, and
   under parity they vanish once growth makes a three-place knot (0 exceptions in the census).
4. **Swaps and the preserved class sign (proved for two classes, computed beyond).** Where the record's preserved sign has
   two classes every swap keeps both (all 1,076 swaps on 624 stages); where it has four or eight, 52 of 108 swap rows move
   classes, and on four classes such a swap exchanges two of the three class signs and keeps their product. The sides can
   each carry a class sign that the swap exchanges, at equal weight; a swap is a permutation of the states and gives no
   relative sign between classes.
5. **With values read, no sign acts (proved, A6).** Forgetting the unread distinctions with each completion counted by
   its squared weight gives one nonnegative weighting, so CHSH is at most 2 for every sign.
6. **Under the readings that sum signed completions, the excess belongs to the reading (computed).** R1 (signed counts)
   and R2 (squared signed sums) give tables above 2, up to the PR box (CHSH 4, beyond the quantum 2√2), with free
   settings and no signalling: under parity from the exchange cost on the swap's own pairs (W1: 109,936 placements at 838
   of 2,304 round-2 stages with a swap), under not-all-equal also from the swap's own sign on kept states (W1k, reaching 4)
   and the sector signs (up to 10/3). But under parity random pairings with the swap's number of pairs do as well (94 of
   200 at CHSH 4), and under not-all-equal products of signs on single distinctions do (156 of 231 pairs above 2; W1k is
   itself such a product on the kept states). The hits also mostly belong to one lift (1,173 of 1,316 swaps). Under
   parity every hit has one read of each reader tied, as the exhaustive four-read check requires.

**Not shown.** That no sign acts through reads of changes (A144) or a reading the model makes itself; swaps of order more
than two or several swaps together; signs of degree three or more; 1,294 not-all-equal round-2 stages (too many states);
the blow-up start's round 2.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a sign from a swap of two sides | **Status:** Successful (a negative with reasons) | The swap and its twist are native; their labels weigh nothing, and the signed excess appears only under readings where random pairings and single-distinction signs do as well |
| Local direction — the swap as the source of a native sign | **STOP** (obstruction learned) | A6 closes value reads for every sign; R1 and R2 reward any sign |
| Broader exploration — the swap's pairs read with reads of changes | Unmapped | The pairs make the literature's graph state on the allowed states; only a three-reader test of changes could show a bounded excess |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | The quantum part needs both a sign and a way of reading changes; the swap supplies neither natively |

**Next step:** Research directions — #1 proposed; no direction rates 3/3, so the choice is the coordinator's

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The swap's pairs as a graph state read with changes by three readers | 2/3 — would show whether a swap's pairing gives a quantum-bounded excess once changes are read | 2/3 — needs three exchanged sides (two commuting swaps or a renaming of order three) and A144's change reads made of allowed changes | Find census stages with three exchanged sides; freeze a GHZ-type test against random pairings → a pass beyond the random control, or none | Proposed |
| 2 | Swaps that move classes, with a supplied change read | 2/3 — the most literal "sign to the sides" in the record: each side's class sign, exchanged by the swap | 2/3 — the 29 stages are listed (named_classes.jsonl) | Hand to the second-check line: does a swap exchanging two class signs, with its change read, give the classes a relative sign → yes or no on those stages | Proposed (for the line that owns the classes) |
| 3 | Record that R1 and R2 reward any sign | 1/3 — saves later studies a false positive | 3/3 — done here | A standing fact in the advisor hivemind and a history line on A144 → done | Done in this epic |

1. Under parity, W1 on the counting weighting is a graph state on the allowed states (one controlled sign per pair); read
   with values and changes by two readers its correlations are 0 or ±1, so CHSH stays at 2 (3 or 4 would exceed the quantum
   bound), and the first honest test has three readers. Random pairings are the control.
2. The other thread found no native second check; a swap that exchanges two class signs is a second structure acting on
   the classes, which is worth one look by that line rather than a duplicate here.
3. Already done.

**Intuitions (exact links, not evidence).**
- *A phase is invisible in the basis it is written in.* A6 is the literature's fact that a diagonal phase changes no
  statistics of reads in the value basis; R1 and R2 make phases visible by adding the completions of a reading before
  squaring, which is a post-selection of every unread distinction, and post-selection is known to give boxes beyond the
  quantum bound (pre- and post-selected realizations of the PR box; Marcovitch, Reznik and Vaidman 2007, as recalled). The
  cheapest test of a native sign is therefore a reading of changes, not another sign.
- *A symmetry that exchanges two sectors.* On four classes, a swap that moves classes acts as the literature's symmetry of a
  code that exchanges its two independent sectors and keeps their product (a renaming of a doubly periodic code that
  exchanges its two cycles). Cheapest test: on the 29 stages, read whether each moved class sign is readable on one side
  only.

**Corrections:** none. The not-all-equal hits from single-distinction signs agree with the beyond-rejection referee's
narrowing that summing unread witnesses before squaring can change a value read.
**Goals:** checkpoint row added (G18; obstruction learned); no goal changed.
**Assumptions:** A292 entered with the design (the lift, the weightings, the readings, the readers, the census) and given
a history line; history lines on A144 (summing signed completions before squaring rewards any sign) and A275 (its cost on
a swap's own pairs gives the PR box, as do random pairings).
**Scaffolds:** the lift (minimal against maximal: hits mostly belong to one), the value convention (W1 against W1c: no
change, and an empty test on 11,110 rows), the reading (R1 against R2: parity hits identical; not-all-equal only W1k
survives R2), the readers (sides against moved distinctions: hits under both), rounds (0 against 1 and 2), the law
(parity against not-all-equal), the pattern weighting (the census against named rings, the 16-knot end and a blow-up
start). The result is about the readings, not the model: under the reading the model's own forgetting gives (A6) every
sign vanishes. The model is not expected to replace R1 or R2; it would need its own way of reading changes.
**Advisor:** consulted before the freeze (its by-hand hit at start 3097 held exactly; its counterexample to the lift's
extension, its four-class objection to A4 and its G0 argument for characters were taken and checked; its numbers are in
the frozen table).
