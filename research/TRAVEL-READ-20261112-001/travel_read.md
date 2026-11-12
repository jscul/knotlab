# What the law reads on travelling bases

Epic `TRAVEL-READ-20261112-001` (`COMMON-FOLD-20261112-001` direction 1; G1 with G17, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead. Pre-registered in commit b0c33480e after the advisor model's critique of the design, with a
pilot on unregistered bases disclosed; the census ran after. The canonical K1–K3 test is unchanged. **Referee pending** (handed to
the referee thread).

## Words

As in the pre-registration: frame, along-count and across-count, rank, window bond (certified when every proper part is also carried
by a doubly periodic state), cross profile b(α, y). The pre-registration's class names "flat", "line" and "open" are words the
glossary reserves (flat and line for the owner's and the literature's uses, open for a distinction free on its own); this note calls
the same classes **bounded across**, **growing across** and **undecided** (one correction, below).

## The question

On the 169 travelling bases of the COMMON-FOLD census, what does the law read? Base 16 reads no length along its shift and one
dimension across. Is that typical?

## The question in standard terms

For random periodic 3-uniform hypergraphs on ℤ² under proper 2-colouring that have a finite pattern forcing its own translate: the
rank of the set of such directions, and the least size of minimal non-shattered sets (up to a window) holding the origin and a far
vertex, against the transverse offset.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Most travelling bases have two independent unlengthened shifts.** At r = 4 and 5, 70 of 108 (65%, Wilson 55–73%) travel along two independent directions, 65 of them by one common pattern (so bond distance is bounded on a whole cone and its mirror); 35 of the 169 travel along all ten shifts tried. Base 16 has one. | computed, frozen (T1 held) | A |
| 2 | **Most of the rest read no growth across either.** Of the 66 bases with one direction found, 56 (85%, Wilson 74–92%) are bounded across: the least window bond to a distinction 10 along and up to 6 across stays within one of its value at 2 across, mostly 4 (bond distance 3) at every across-count. Two (3%) grow across as base 16 does: one with base 16's profile (4, 4, 5, 5, 6, 6 upward, nothing beyond 2 downward in one cross-section), one growing the other way (4 to 6 downward) and bounded at 4 upward. Eight are undecided: six have bonds of 4 or 5 only at some across-counts or only through two cross-sections, two have none in the families searched. | computed, frozen (T2 held) | A |
| 3 | **Depth along does not matter.** The least window bond at 14 along equals that at 10 along in 99 of 104 cases. | computed, frozen (T3 held) | A |
| 4 | **Bases with two directions read no length around the origin.** On 77 of 103 (75%, Wilson 66–82%), at least 80% of the targets on the ring of radius 6 are reached by a window bond of at most five from the 3 × 3 cells around the origin, none larger than on the ring of radius 3 (median 4 on both rings). | computed, frozen, exploratory (T4 held) | A |
| 5 | **Certification.** 296 of the 650 window bonds found in one cross-section are certified by doubly periodic states; the rest are bonds up to the window. On base 16 the uncertified ones are exactly those the theorem proves, because doubly periodic states cannot carry two of the sixteen patterns of a heddle part. | computed | A |

**Rank and class by number of kinds** (bases with a certified travelling pattern):

| r | Bases | Rank 2 | Rank 1: bounded across | Growing across | Undecided | Rank 2 with no length on the rings |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 33 | 15 | 11 | 1 | 6 | 9 of 15 |
| 4 | 55 | 35 | 19 | 0 | 1 | 24 of 35 |
| 5 | 53 | 35 | 17 | 0 | 1 | 26 of 35 |
| 6 | 28 | 18 | 9 | 1 | 0 | 18 of 18 |

## Answer

No: base 16's reading is rare. On the typical travelling base the law reads zero dimensions in the measured range: a few
distinctions at the origin decide distinctions far along and at every across-count measured, at bond distance about 3, and two thirds
of the bases do so along two independent shifts. Only 2 of the 169 travelling bases grow across like base 16 (the rank-2 bases were read on rings: 26 of 103 have
unreached or larger targets on the ring of radius 6, none a profile like base 16's), so under this weighting the law's one-dimensional
reading of base 16 is about a one-in-eighty case among bases that travel at all. The measured range is across-counts to 6,
along-counts to 14 and rings to radius 6; within it, most bases show no growth.

## Reading

**Interpretation, not a theorem.**
- **For the owner's "globally influential".** In the middle regime, where bases still have many states, influence is usually total:
  the law keeps every distinction measured within a few bonds of every other. It compresses the base not along one direction but
  in all of them, to a point in the measured range: the strongest form of "fold in immensely complex ways and be globally
  influential" that a reading by bond distance can show.
- **Base 16 is the exception that shows a line.** It reads one dimension because its knots pass values on only through two partners
  (one more and two fewer across), so what travels must climb across one step in two. Random families of kinds typically give values
  more ways to be passed on, and the climb costs nothing.
- **For question 9.** A space the law makes is a shape of its own reading, and here it is usually degenerate (zero dimensions);
  lower-dimensional geometry like base 16's line exists but is rare under this weighting. Whether bounded stays bounded beyond the
  measured range, or grows slowly, is the next question.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** Nothing new (the lemma and the cone are COMMON-FOLD's and the pre-registration's).
  **Computed.** Every rate, within the measured range, at window level with certified shares stated.

## Stress test

The control reproduces base 16's theorem (one cross-section 4, 5, 5, 6, 6 upward, none downward; two cross-sections 5, 5 downward).
One size past the range (across-counts beyond 6, rings beyond 6) is the first step of direction 1 below.

## Review

Referee pending: handed to the referee thread on 2026-11-12.

## Literature and provenance

- **Known.** Directions of determinism and expansive subdynamics (Boyle and Lind; Guillon, Kari and Zinoviadis); stable directions
  and cones in bootstrap percolation (Bollobás, Smith and Uzzell), the closest analogue of one direction against two; algebraic
  examples deterministic in many directions (Ledrappier; Kitchens and Schmidt; Einsiedler, Lind, Miles and Ward).
- **Not found** (bounded search): the typical cross profile of bond distance in random families of not-all-equal kinds.
- **Classification.** New as stated, folklore risk moderate.

## Workspace assumptions

- **Relied on.** A64, A67, A71, A74 (dimension across read by across-counts; here it reads zero), A76. **Changed.** None.

## Advisor model

Consulted before freezing on the design: it replaced a beam over travelling sets (which bounded reach, not bond distance, and could
force its own slope) with exhaustive enumeration in the strip, added the second along depth, the rank labels, the common pattern as
settled, and the per-base failure criteria. Not consulted on the reading.

## Ratio

- **Substantive.** One frozen census of four parts.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**): the pre-registration named its classes "flat", "line" and "open", words the
glossary reserves for other senses; this note uses bounded across, growing across and undecided for the same classes.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what the law reads on travelling bases | **Status:** Successful, referee pending | T1 to T4 held; base 16's line is rare; most read zero dimensions in range |
| Local direction — the bounded bases | Continue | Bounded within 6 across: bounded at every distance, or slow growth? |
| Broader exploration — G1 on overlapping bases | Known alternatives | Why base 16 grows; certificates that repeat along no step (the corner-knot line) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Under this weighting the law's own geometry is usually degenerate; lower-dimensional readings are rare |

**Corrections:** one, Not a block (class names). **Goals:** a G1 checkpoint (obstruction learned, with G17); no goal change.
**Assumptions:** none changed. **Basket:** `COMMON-FOLD-20261112-001#2` (why ties take over, 2/3, 2/3), `COMMON-FOLD-20261112-001#3` (other
weightings, 2/3, 3/3), `ACROSS-FOLD-20261112-001#2` (all bonds across, 2/3, 2/3); taken: `COMMON-FOLD-20261112-001#1` by this epic.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Bounded at every distance? | 3/3 — Major | 2/3 — Testable | On the bounded bases, push across-counts to 20 and rings to 15, and seek a proof on one base (a finite seed whose forced closure covers a cone in each direction) → the law provably reads zero dimensions on a typical base, or the bound grows | Selected · awaiting go-ahead |
| 2 | What makes a base grow across | 2/3 — Substantial | 2/3 — Testable | Compare the two growing bases with base 16 (how many partners pass a value on) and test a criterion on all 169 → a rule for when the law reads a line | Alternative · deferred |
| 3 | Certificates that repeat along no step | 2/3 — Substantial | 2/3 — Testable | With the corner-knot line, certify the window bonds by states periodic across only → every window bond certified or refuted | Alternative · deferred |

1. **Bounded at every distance.** Payoff 3: a proof that the typical travelling base reads zero dimensions would settle what the law
   makes of dense overlap. Concreteness 2: base 16's flip form does not apply, so the proof needs a new forcing argument.
2. **Growing across.** Payoff 2, concreteness 2.
3. **Certificates.** Payoff 2, concreteness 2, and it joins the other line.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
