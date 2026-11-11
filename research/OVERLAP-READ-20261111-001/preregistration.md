# What not-all-equal makes of overlapping bases: pre-registration

Epic `OVERLAP-READ-20261111-001` (`RULER-FLAT-20261111-001` direction 1; G1, question 9; program topology, group spacing),
2026-11-11, at the owner's go-ahead ("Please investigate that", relayed by the coordinator: start with a census of small bases with
no limit on knots per pair and the 160 faithful non-weave bases of B145, pre-registered with frozen failure criteria and a prior-work
check). Frozen before any registered run. The canonical K1–K3 test is unchanged. What overlapping bases compute belongs to the
learning line and is not asked here.

## Words

As in the guide's glossary (`publication/knotlab/INTUITIONS.md`, "Words for space"). A **base** is a set of knots, each on three
distinctions, with no limit on how many knots a pair lies in or how many knots a knot meets; a pair in two knots everywhere, with one
cycle of knots at each distinction, is a **two-fold weave** (literature: a closed triangulated surface). Under the not-all-equal law
(NAE) a base's allowed states may bind sets no knot names. For a set S of at most three distinctions:
- **frozen**: S = {v} takes one value in every state;
- **tie**: S = {u, v}, both free, takes two of its four patterns;
- **emergent knot**: S = {u, v, w}, not a knot, every pair free, takes fewer than eight patterns.

A base with states is read **faithfully** when it has none of these and every knot's pairs are free (KNOTS-ALONE's definition). A
set of knots K **forces** S when S lies in K's distinctions and the states of K alone leave S below its full pattern count; it does
so **minimally** when no knot of K can be dropped with S still forced. An emergent knot is **plain** when it forbids 000 and 111, and
**signed** when it forbids another complementary pair (NAE with some of its distinctions read negated: still a knot by K1–K3). The
**locality radius** of an emergent set is the least r for which the knots lying within graph distance r of S already force it.

## The question

Where each co-knotted pair lies in two knots, NAE measures the base exactly (`RULER-FLAT-20261111-001`). In an overlapping base, what
does the law make that no knot names, from which configurations of knots, and is it local? Which overlapping bases does it read
faithfully?

## Disclosed before freezing

Pilots outside the registered run, with code in the scratchpad, not part of the record:
- **Every labeled base on 6 distinctions with states, all distinctions used:** 7,453 read faithfully; 985,187 contain adjacent apices
  (`GROW-COUNT-20261111-001`'s lemma: a pair's two knots whose other corners share a knot with a third distinction outside the pair)
  and none of them is faithful; the other 450 are unfaithful only by emergent knots, and every one contains a Pasch configuration
  ({a,b,c}, {a,y,z}, {x,b,z}, {x,y,c}) whose complementary four triples are not all knots. Faithful bases there have pairs in up to
  four knots; a book (one pair in every knot) is faithful at every size tried, 1 to 10 pages.
- **Two-fold weaves (tori 12 to 48):** 66 unfaithful ones of loop length 3 or 4 contain neither configuration: loops force too.
- **The catalogue to 4 knots, up to isomorphism (S marked):** five entries. Three knots: adjacent apices, forcing a signed emergent knot.
  Four knots: adjacent apices closed by a knot on its forced triple (an unequal tie); adjacent apices with one more knot on its third
  corner (a plain and a signed emergent knot, two entries); the Pasch (a plain emergent knot on each complementary triple). To 6 knots
  there are 2,090 configurations of six knots and 113 minimal forcing pairs before the isomorphism check.
- **A reduced dry run of the frozen code** (300 random bases per size, 60 swap-made bases, catalogue to 5 knots): every emergent knot
  plain or signed and every tie an equality or an inequality; the swap-made bases matched NAE-SURFACE's recorded readings on all 60;
  their locality radii 1 (31), 2 (24) and 3 (1); greedy forcing sets above the catalogue's size were all explained by the catalogue.
- **Three-fold weaves** (every co-knotted pair in exactly three knots), 30 per size by SAT: states only at 7 to 9 distinctions, never
  faithful, always with adjacent apices.

## Families and readings (frozen; `contract.json`)

- **C1, the catalogue.** Every connected configuration of at most 6 knots, up to isomorphism, in which every distinction outside S
  lies in at least two knots (a knot with a private distinction never forces anything), and each minimal forcing pair (configuration,
  S), up to isomorphism, with S's relation.
- **C2, small bases.** Every labeled connected base on 4 to 6 distinctions, read through its set of states, with the two pilot
  configurations marked; 20,000 random connected bases on each of 7 to 10 distinctions (knot count uniform from 2 to a third of the
  triples; seed 20261118 + n), read by brute force. For the first 2,000 unfaithful bases with states per size, a forcing set for an
  emergent set by greedy deletion (up to five emergent sets, three random orders each), and when it exceeds 6 knots, an exact check of
  whether some catalogue entry maps onto one of the base's emergent sets.
- **C3, bases re-read as objects.** NAE-SURFACE-20261111-001's 822 swap-made bases, regenerated by its frozen recipe (copied verbatim),
  read by SAT, with the locality radius of their emergent sets (to 4); GROW-COUNT-20261111-001's 90 NAE-grown bases, compacted (its
  runs left unused numbers behind).
- **C4, three-fold weaves.** 30 per size on 7 to 14 distinctions by SAT (seed 20261119 + n).
- **C5, rulers.** Bond distance from distinction 0 at graph distance 2 and 3 on faithful bases with a pair in three or more knots:
  brute force (bonds to 5) on C2's bases with at least 7 distinctions; LONG-LOOP's frozen ruler on C3's grown bases.

## Predictions

- **P1 (the small catalogue).** With at most 4 knots the catalogue is exactly the five pilot entries.
- **P2 (signs).** Every emergent knot found anywhere is plain or signed (it forbids one complementary pair of patterns), every tie is
  an equality or an inequality, and nothing is frozen. This is Lemma L1 below; a failure is a bug or a wrong proof.
- **P3 (small bases are local).** Every unfaithful base with states among C2's forcing samples has an emergent set forced by at most
  6 of its knots (greedy, else the exact catalogue check).
- **P4 (the swap-made bases' defects are local).** Every unfaithful swap-made base has an emergent set of locality radius at most 3.
- **P5 (uniform overlap three is not read).** No three-fold weave in C4 is read faithfully.
- **Checks.** X1: the regenerated swap-made bases' faithfulness matches NAE-SURFACE's record on all 822 (160 faithful). X2: every
  forcing set of at most 6 knots found in C2 is isomorphic to a catalogue entry. X3: the 6-distinction table is recorded.

Measured, not predicted: faithful share by size and by most knots per pair; plain against signed emergent knots per family; the
rulers of C5.

## Decision rules

- **P3 and P4 hold:** what NAE adds to these bases is local, and the catalogue is the local list of what overlap makes.
- **P3 or P4 fails:** the first base whose emergent sets all need more is reported with its smallest forcing set; it is the next
  object (a long obstruction, as loops are in two-fold weaves).
- **P5 fails:** an overlapping base read natively at uniform overlap three; its ruler is the next step. **P5 holds:** uniform overlap
  three is never read in range.
- **P1, P2, X1 or X2 fails:** a bug or a wrong lemma; stop, fix, report.

## Lemmas (ticket B, proved after the run and refereed)

- **L1 (what NAE can add).** Under NAE no distinction is ever frozen, every tie is an equality or an inequality, and every emergent
  knot forbids exactly one complementary pair of patterns: it is NAE with some distinctions read negated.
- **L2 (the Pasch).** The four knots of a Pasch force NAE on each of its four complementary triples: half of the octahedron's eight
  knots allow exactly the octahedron's states.
- **L3 (books).** A pair in any number k of knots whose other corners lie in no other knot is read faithfully: overlap at a pair is
  unbounded in faithful bases.
- **L4 (overlap as weight).** In any base, a two-valued assignment cuts each co-knotted pair p with weight c(p), the number of knots on
  p; the weighted cut is at most twice the number of knots, with equality exactly at the states. So in a λ-fold weave (every
  co-knotted pair in exactly λ knots) the states are the assignments cutting two thirds of the co-knotted pairs, and where every pair
  lies in exactly λ knots (a 2-(v, 3, λ) design) there is no state beyond four distinctions.

## Prior work (bounded search, 2026-11-11)

- **Known.** The Pasch configuration, the smallest trade in a Steiner triple system; the octahedron K(2,2,2) of triples splits into two
  Pasch configurations (Encyclopedia of Mathematics; arXiv 2503.23252). No Steiner triple system on 7 or more points is 2-colourable
  (Rosa, 1970). 2-colourability of 3-uniform hypergraphs (property B) and NAE-3SAT are NP-complete (Lovász 1973; Schaefer 1978), and
  NAE-3SAT reduces to maximum cut through triangles (Garey, Johnson and Stockmeyer 1976), which is L4's counting. A connected NAE-3SAT
  instance with fewer clauses than variables and each variable in at most three has a free variable (arXiv 1611.08850).
- **Not found.** A catalogue of what the proper 2-colourings of a 3-uniform hypergraph force on triples outside it, or of the minimal
  configurations that force them. Classification expected: known-with-delta (the tools are classical; the catalogue and its reading
  are the delta).

## Stop rule

One registered run, the lemmas proved, one referee pass over the census and the lemmas; report and hold.

## Runtime

About ten to fifteen minutes on 12 workers; registered in `docs/LONG_RUNNING.md`; `systemd-run --user -p MemoryMax=16G -p
MemorySwapMax=0`.
