# One unlengthened shift against two

Epic `SHIFT-COUNT-20261112-001` (`FAR-BOUND-20261112-001` direction 1; G1 with G17, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead. Ticket C frozen in commit e78a582f9 (the harmony thread's design), tickets A and B in
0141e4230 after the advisor's critique; every run came after its freeze. The canonical K1–K3 test is unchanged. **Referee pending**
(handed to the referee thread).

## Words

As in the pre-registration and FAR-BOUND: travelling, unlengthened shift, certified, eventually periodic strip, frame, along-count,
across-count; relay and two clusters for the shape of a least bond (the largest across gap at most 6, or over half the offset).

## The question

On the 169 travelling bases (uniform r-sets of 171 knot kinds, r = 3 to 6), how many have two certified unlengthened shifts? On bases
with one, does bond distance across keep growing? And does the harmony thread's tiling reading explain the patterns doubly periodic
states miss?

## The question in standard terms

For random periodic 3-uniform hypergraphs on ℤ² under proper 2-colouring with a finite pattern forcing its own translate: the rank of
the set of certified translation directions of such patterns; the shape and growth of least minimal non-shattered sets across a single
direction; and which period lattices carry the non-periodic patterns.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Two unlengthened shifts are the rule.** 146 of the 169 travelling bases (86%) have two independent certified travelling directions (A1: at least 140, held); only 1 base has a forced second direction without a certificate (A2 held); base 16 has exactly one (control). | computed, frozen | A |
| 2 | **Growing across does not exclude a second shift.** Of the three bases that grow across near the origin, two have one certified direction, but one (sample 97 at r = 3, base 16's profile 4, 4, 5, 5, 6, 6 upward) has a second, whose cone lies on the other side (where its one-cross-section bonds were absent). A3 failed: what goes with growth is a side of the base no unlengthened cone covers, not the count of shifts. | computed, frozen (A3 failed) | A |
| 3 | **The creep stops at 6, so far.** On the four decided creeping bases the least certified bond at 27 across equals the one at 23 (6 on all four): no further rise (B3's "+1 on at least two" failed; the plateau is within the size cap). | computed, frozen (B3 failed) | B |
| 4 | **The far bonds are neither relays nor clean pairs of clusters.** No least far bond is a relay (B1 failed for the creeping bases: 0 of 4 decided); three of five bounded bases have two clusters (B1 held for them); a translated far cluster gives a bond at three offsets on 1 of the 4 two-cluster bases (B2 failed). | computed, frozen | B |
| 5 | **The tiling reading of the uncertified patterns is refuted on 13 of 21.** Of 21 patterns no doubly periodic state up to period 8 carries (base 16's two, and one on each of 19 unresolved bases; 10 more had none), no lattice up to 24 × 24, sheared included, carries 9 (base 16's two among them), and every lattice past a threshold carries 4 (a size effect). On 8 it survives the three criteria, but weakly: the divisibility fits cover 1 to 50% of the lattices they predict, and the line counts are equal on parallel lines in every state, which on sheared lattices with one line per direction is automatic. | computed, frozen (the harmony thread's test) | C |

## Answer

Two unlengthened shifts are the rule (86% certified), so on most travelling bases the law reads no length in two directions. On the
few with one, growth across is not simply set by the count: one growing base has a second shift on its other side, and the creeping
bases plateau at 6 between 23 and 27 across. Base 16's patterns that no doubly periodic state carries are carried by no lattice up to
24 × 24 either: they need states that repeat along no step, not a slope that fits some lattice.

## Reading

**Interpretation, not a theorem.**
- **What the growing bases share with base 16 (revised).** Each grows on a side of the base that no unlengthened cone covers: base 16
  and two others have one shift, and sample 97's second shift covers only its other side. So the law reads no length where cones of
  travel reach and a distance where they do not; how fast that distance grows (linearly on base 16, a plateau so far on the creeping
  bases) is open.
- **For the owner's "globally influential".** Under this weighting influence that ignores distance is the rule (86% of travelling
  bases fold two ways); lower-dimensional readings live on the sides the folds leave uncovered.
- **On the harmony thread's question.** The patterns base 16 cannot certify with repeats are not a tiling-slope effect: no lattice to
  24 × 24 carries them, while eventually periodic strips do. A "line" of states that changes once and never comes back is the
  mechanism, not a height function's slope.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** Nothing new (the cone corollary is settled by the definition and stated as
  such). **Computed.** Everything else, within its family and caps.

## Stress test

Ticket A's family strictly contains the referee's (which found 130); B3 is one step past FAR-BOUND's range (27 across).

## Review

Referee pending: handed to the referee thread on 2026-11-12.

## Literature and provenance

As in FAR-BOUND. The harmony thread's design and refutation criteria are theirs (`LINE-LOCK-20261112-001`), run here.

## Workspace assumptions

- **Relied on.** A64, A67, A71, A74, A76. **Changed.** None.

## Advisor model

Consulted before freezing A and B: it pointed out that the referee's count made "at least 125" settled by data (so A1 asked for more),
asked for the certification yield and a negative control, showed that "growing bases stay one-direction" is partly settled by the
lemma (so only cones missing the measured cells test it, which is how A3 failed), flagged censoring and selection in B, and proposed
the relay/two-cluster discriminator.

## Ratio

- **Substantive.** Three frozen censuses.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

None. Two frozen predictions failed (A3, and parts of B1, B2, B3) and are reported as such.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one shift against two | **Status:** Successful in part, referee pending | Two shifts are the rule; growth sits where cones do not reach; the creep plateaus so far |
| Local direction — the uncovered sides | Continue | Where no cone of travel reaches, what is the law's distance, and how does it grow? |
| Broader exploration — G1 with G17 | Pivot available | Other weightings (bigger boxes, three shifts) to see whether two-way folding stays the rule |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | The law's dimension follows the cones of its unlengthened shifts, under this weighting |

**Corrections:** none. **Goals:** a G1 checkpoint (capability gained, with G17); no goal change. **Assumptions:** none changed.
**Basket:** `FAR-BOUND-20261112-001#3` (growth rate, 2/3, 2/3), `TRAVEL-READ-20261112-001#2` (what makes a base grow, now refined),
`COMMON-FOLD-20261112-001#3` (other weightings, 2/3, 3/3); taken: `FAR-BOUND-20261112-001#1`.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The cone rule | 3/3 — Major | 2/3 — Testable | On all 169 bases, compute the union of the certified travel cones from the origin's sets and test: bond distance bounded inside it, growing outside it → a rule for the law's own geometry from its folds, or a counterexample | Selected · awaiting go-ahead |
| 2 | Other weightings | 2/3 — Substantial | 3/3 — Ready | Rerun COMMON-FOLD and ticket A with a larger box of kinds → two-way folding stays the rule, or depends on the box | Alternative · deferred |
| 3 | The plateau | 2/3 — Substantial | 2/3 — Testable | Push the four creeping bases to 40 and 60 across with the |S| ≤ 7 cap → a bound of 6, or growth | Alternative · deferred |

1. **The cone rule.** Payoff 3: a rule reading the law's dimension off its unlengthened shifts would be general. Concreteness 2.
2. **Other weightings.** Payoff 2, concreteness 3.
3. **The plateau.** Payoff 2, concreteness 2.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
