# Across the unlengthened shift

Epic `ACROSS-FOLD-20261112-001` (`FOLD-20261112-001` direction 1; G1, question 9; program topology, group spacing), 2026-11-12, at
the coordinator's go-ahead under the owner's standing mandate. Pre-registered in commit 635c3e640; ticket A's check was run before
freezing and is disclosed as such; ticket B's census ran after, and a soundness audit of its negatives was designed after it ran. The
hand proof was found during the work with the advisor model's help, after freezing, and is stated as such. The canonical K1–K3 test is
unchanged.

## Words

As in the guide's glossary and `FOLD-20261112-001`: bond, bond distance, steps apart, ball, base 16, the travelling triple. New here,
chosen with the advisor model and entered in the glossary in this epic's commit: the **unlengthened shift** (what the pre-registration
called the fold) and a distinction's **along-count** and **across-count** (its column and row in the sheared frame); a
**self-keeping set** and a pattern's **self-keeping part**; a **heddle** (what the pre-registration called the ladder L_y) and a
**heddle bond** (a heddle with one far distinction at its last across-count). Counts are taken from the origin.

## The question

How does the law's bond distance grow across the unlengthened shift of base 16, between the origin and a distinction y across and far
along? Does the law read the base as a line across it?

## The question in standard terms

For the proper 2-colourings of the 3-uniform hypergraph on ℤ² with edges {z, z+(0,1), z+(1,0)} and {z, z+(0,2), z+(1,2)}, what is
the least size of a minimal non-shattered set containing (0,0) and (k, y), as a function of y, for large k?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Heddles travel (Theorem L).** For every y ≥ 2 and every k ≥ ⌊(y+1)/2⌋ + 1, the heddle reaching y across, with the distinction k along and y across, is a bond of ⌊(y+1)/2⌋ + 3. So bond distance from the origin to (k, y) is at most ⌊(y+1)/2⌋ + 2 at every such k. At nearer along-counts other sets are constrained first (runs of every second across-count lose one member per step along) and the heddle is not minimal there. | proved (hand proof; exact checks for y ≤ 8, and at y = 9, 10 for k = 8, 11); refereed | A |
| 2 | **What one along-count forces far along is its self-keeping part.** In flip form (each value counted with the parity of its along-count) the law passes a value on unchanged where it has an equal partner one more or two fewer across, and lets it flip anywhere else; every set of values at one along-count extends both ways. Far along (k at least the number of distinctions) a pattern at one along-count forces exactly the values of its self-keeping part. | proved; exhaustive check of 30,048 cases; refereed | A |
| 3 | **The heddle is the least bond of one along-count (Theorem C).** A bond made of distinctions at one along-count, containing the origin, with one distinction y across and at least that many along-counts further, has at least ⌊(y+1)/2⌋ + 2 distinctions at the along-count: a self-keeping set starts with three consecutive across-counts and never misses two in a row. | proved; refereed; the census and its audit agree on every candidate (46,935 sets; 150 at rows 9 and 10, beyond the periods computed, settled by the proof) | A, B |
| 4 | **One along-count reaches only one way (Theorem D).** No such bond reaches a distinction three or more fewer across: a minimal self-keeping set never extends more than two across beyond its far distinction, so it misses the origin. | proved; refereed; the census found none to size 7 | A, B |
| 5 | **Two along-counts reach the other way, at the same sizes.** The knot holding (0, r − 2), (0, r) and (1, r) lets equal values at (0, r) and (1, r) force (0, r − 2), two across back. Chaining it through every second distinction at along-count 1 and closing with a triple gives, for y = −3 to −10, a bond of ⌊(|y|+1)/2⌋ + 3 with the origin and (k, y), the heddle's size at +|y|. | computed (y = −3 to −10 at k = 5, 8, 11, 20; the referee's bonds at rows −3 and −4 for every k) | review |
| 6 | **No shorter bond found across, either way.** Inside generous boxes no bond containing the origin and (k, y) is smaller than the heddle for y = 2 to 8 (sizes 3 to 6; size 6 at (5, 7), (5, 8), (8, 8), the run at (8, 7) unfinished), none of size at most 4 reaches rows −3 to −5 and none of size 5 row −5; the frozen N found none of size at most 4 to (5, 3) or (5, 4). Results at k = 5 and 8 are identical. | computed (referee; N frozen) | B, review |
| 7 | **The registered prediction M failed as written on 4 of 31 targets, by its own range:** at rows 9 and 10 it predicted bonds of 8 but searched only to size 7. The audit found the heddle bonds of 8 there, and Theorem C proves nothing smaller of that kind exists, so M's decision rule ("a shorter way across") does not apply. | computed; design slip, recorded as a correction | B |

## Answer

Yes. Across the unlengthened shift the law's bond distance from the origin to a distinction y across and far along is at most
⌊(|y|+1)/2⌋ + 2 both ways: one more for every two across-counts (proved upward for every y by heddles; computed downward to
y = −10). It is exactly that among bonds of one along-count (proved), and no smaller bond of any shape turned up in the boxes searched,
to eight across either way. So a ball of bond radius r holds at least the across-counts −(2r − 4) to 2r − 4 at every far along-count,
4r − 7 of them, growing linearly in r. Read by the law alone, base 16 has no length along one shift and one dimension across it.
Whether bonds spread over several along-counts can ever cross more cheaply is the open part.

## Reading

**Interpretation, not a theorem.**
- **A line the law makes.** The meeting pattern gives base 16 two shifts with steps apart growing along both. The law alone collapses
  one and keeps the other as a line, counted at half the rate of across-counts. This is the first base where the program reads a
  dimension natively that differs from the meeting pattern's.
- **Why it is a line.** What travels is what keeps itself: the law passes on only values that have an equal partner one more or two
  fewer across, so a set that reaches far along must start with three consecutive across-counts and step at most two at a time. The
  other way across, a second along-count passes values back two at a time. Either way the bond distance across counts these steps.
- **No handedness.** One along-count reaches only one way across, which suggested the law tells the two senses across apart. It does
  not: with a second along-count the other sense is reached at the same sizes, so the asymmetry belongs to the family of bonds, not
  to the law. (Drafted and withdrawn before publication.)
- **For question 9.** A dimension read by the law's own balls is now shown on one infinite base with overlap: zero along one shift and
  one across it, proved as an upper bound one way and among one-along-count bonds, computed the other way.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** Theorem L for every row, the self-keeping lemma, and Theorems C and D for bonds of
  one along-count and one distinction further along (C and D for k at least the number of distinctions at the along-count), base 16
  only. **Computed.** The downward family to y = −10 at four k; no smaller bond in the referee's boxes; no bond of size at most 4 to
  (5, 3) or (5, 4) in the frozen box.

## Stress test

Theorem L was checked one size past its frozen range (rows 9 and 10, k = 8 and 11: bonds, by the audit's exact freeness with periods
to 15), and is now proved for every row. The census's negatives, which it did not certify, were certified by the audit for every
target to row 8 and for D and N (`soundness_audit.py`, `soundness_audit.json` with periods 3 to 12, `soundness_audit_deep.json` with
3 to 15). The downward family was checked to row −10 and at k = 20 (`downward_family.py`).

## Review

An independent referee (a fresh agent with its own code in the original frame: window SAT for constraint, periodic states of period 9
to 17 for freeness, transfer periodicity for every k) found:
- **Theorem L confirmed** for y = 2 to 8 at every k ≥ ⌊(y+1)/2⌋ + 1, the nearer failures exactly as listed; the hand proof (flip form,
  self-keeping lemma, Theorems L, C, D) **correct, no gap**, with 600 random instances agreeing; the two trivial parts (without the far
  distinction; without its row) to be stated, as they now are.
- **No shorter bond** in boxes for sizes 3 to 6 (conclusion 6), and the same at k = 5 and 8.
- **Downward reached by two along-counts:** {(0,0), (0,−1), (1,−3), (1,−2), (k,−3)} for every k ≥ 3, {(0,0), (1,0), (0,−4), (0,−3),
  (k,−4)} for every k ≥ 2, and one of six at row −5. The pre-registration's "forcing never moves below the lowest known row" holds only
  from one along-count, and its expected asymmetry is an artefact of that family.
- **Soundness:** periodic states and window refutations are sound certificates; the census's negatives were not (it counted a set as no
  bond when it failed to certify a part), now certified by the audit. Check C3 had used a window alone to show a set free; the referee
  certified those five sets free, and C3 now does so with periodic states.
- **Wording:** "at most ⌊(y+1)/2⌋ + 2 at every k ≥ 3" in the pre-registration overstates the start of Theorem L; M's failure at rows 9
  and 10 is of range, not a shorter bond.
- **Literature:** Kitchens and Schmidt, Ward's minimal non-mixing shapes, Derksen and Masser, Boyle and Lind, Zinoviadis, Colle, Franks
  and Kra: all linear or algebraic; nothing on not-all-equal, or on bond distance.

## Literature and provenance

- **Known.** The forcing mechanism is FOLD's; the nearest precedent is Ledrappier's three-dot shift and its non-mixing shapes
  (Kitchens and Schmidt), proved through group structure that not-all-equal lacks. The self-keeping part is the stable set of a
  constrained flip dynamics, the kind bootstrap percolation and kinetically constrained models study (named by the advisor model);
  extender and follower sets of two-dimensional shifts (Kass and Madden; Ormes and Pavlov) and strong spatial mixing (Briceño) are
  related notions.
- **Not found** (bounded searches, the referee's and ours): the self-keeping lemma, or bond distance across a direction of no length,
  for not-all-equal; the referee's search of non-mixing shapes and expansive directions found only linear or algebraic cases.
- **Classification.** Known-with-delta for the mechanism; the lemma and its count not found.

## Workspace assumptions

- **Relied on.** A64, A67. **Added.** A74 (dimension across an unlengthened shift is read by across-counts at far along-counts). **Changed.** None.

## Advisor model

Consulted twice under the owner's rule of 2026-11-12, both after freezing (the rule came after it): on the lower bound, where it
sketched the flip form and the self-keeping lemma (checked and completed here, one step of the minimality argument rewritten; the
referee checked the result), and on the new words (it proposed "skip bond", which collides with the record's skip model, and named
"heddle" as the reserve, adopted).

## Ratio

- **Substantive.** The hand proof and its checks, the census, its soundness audit and the downward family, one referee pass.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**), on the published pre-registration (commit 635c3e640) and its tickets:
- the three tickets' objectives still stated the guess made before freezing (column segments, bond distance max(3, |y| + 1), balls
  of 2r − 1 rows), which the pre-registration itself disclosed as failed; they now state the frozen claims;
- "d(origin, (k, y)) ≤ ⌊(y+1)/2⌋ + 2 at every k ≥ 3" overstated where the heddle bond starts (k ≥ ⌊(y+1)/2⌋ + 1, as Theorem L said);
- "forcing never moves below the lowest known row" holds only from one along-count, and the expected asymmetry downward does not
  exist (conclusion 5);
- the census contract called its two tests sound; only their positives are, and its negatives were not certified (now certified by
  the audit and by Theorem C); M's size cap was below its own prediction at rows 9 and 10;
- "ladder" and "rung" already meant other things in the record; the object is now a heddle.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — across the unlengthened shift | **Status:** Successful | Heddles proved for every row; least among one-along-count bonds proved; the other way reached at the same sizes (computed) |
| Local direction — base 16's distance across | Continue, parked | Upper bound one way proved, the other computed; lower bound beyond one along-count open |
| Broader exploration — G17 with G1, how common folding is | Pivot, owner-approved | Base 16 is one sample nobody chose; the owner asked how typical folds and global influence are |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | The first dimension read natively that differs from the meeting pattern's: zero along one shift, one across |

**Corrections:** one, Not a block (the pre-registration's ticket objectives, its "every k ≥ 3", its "never below", the census's
soundness claim and range, and the word "ladder"). **Goals:** a G1 checkpoint (capability gained); no goal change; the next epic
serves G17 with G1. **Assumptions:** A74 added (dimension across an unlengthened shift read by across-counts at far along-counts).
**Basket:** `FOLD-20261112-001#2` (the other shortcuts, 2/3, 3/3), `PERIODIC-READ-20261111-001#2` (rigid periodic states, 2/3, 2/3),
`OVERLAP-READ-20261111-001#4` (reading by pair counts, 2/3, 1/3); taken: `FOLD-20261112-001#1` by this epic; `FOLD-20261112-001#3`
merged into direction 3 below.

**Next step:** Research directions — selected: #1 (owner-approved, 2026-11-12)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | How common folding is among random samples | 3/3 — Major | 2/3 — Testable | With `RANDOM-FATES-20261112-001`'s samplers and words, measure global influence (how far one distinction's value forces others: bonds at many steps) and unlengthened shifts, under several declared weightings, on samples with pairs in many knots → typical, rare or absent, per weighting | Selected · owner-approved |
| 2 | The distance across, all bonds | 2/3 — Substantial | 2/3 — Testable | Prove the heddle optimal among bonds over several along-counts (the advisor's invariant: values forced at an along-count at most the bond's members up to it), and the downward family by hand → the line proved both ways, or a shorter bond | Alternative · deferred |
| 3 | The other folding classes (was `FOLD-20261112-001#3`) | 2/3 — Substantial | 3/3 — Ready | Write the flip form of each of the 14 folding classes and find its self-keeping sets → which fold and what lies across each | Alternative · deferred |

1. **Folding among samples.** Payoff 3: whether a law's own geometry, and the global influence the owner described, is typical or
   rare decides whether base 16 is a curiosity or the rule. Concreteness 2: the samplers exist, but global influence needs a declared
   measure on finite samples.
2. **All bonds across.** Payoff 2: turns the computed half into a theorem; concreteness 2.
3. **Other classes.** Payoff 2, concreteness 3: the flip form generalizes directly.

**Recommendation.** Research directions, #1, owner-approved; it starts after this close, with the advisor consulted before freezing.

## Final report as sent

Sent to the owner on 2026-11-12 at about 06:52 UTC, summarized here (the tables are those above, directions 1 to 3, with 1 starting
at once as the owner approved). Headline: on base 16 the law reads a line across the direction it does not lengthen, bond distance
to a far distinction y across at most floor((|y|+1)/2) + 2, one more for every two across-counts both ways, so zero dimensions along
one shift and one across it: the first dimension the law reads natively that differs from the meeting pattern's. The advisor model
sketched the key lemma, checked and completed here; the referee found no gap, and found the two-along-count bonds downward that
withdrew a draft "handedness" reading. One correction, Not a block; A74 added; new words heddle, unlengthened shift, along-count and
across-count, self-keeping part.
