# What not-all-equal makes of overlapping bases

Epic `OVERLAP-READ-20261111-001` (`RULER-FLAT-20261111-001` direction 1; G1, question 9; program topology, group spacing),
2026-11-11, at the owner's go-ahead. Pre-registered in commit 18e347a92 before any registered run. The canonical K1–K3 test is
unchanged. What overlapping bases compute belongs to the learning line.

## Words

The guide's glossary (`publication/knotlab/INTUITIONS.md`): a **knot pattern** is knots and which distinctions they share, with no
limit on how many knots lie on a pair; a **base** is one that allows a state; a **two-fold weave** has every co-knotted pair in two
knots and one cycle of knots at each distinction (literature: a closed triangulated surface); a **hollow triple** is three free pairs
whose triple is not free. In this record: a **tied pair** is a restricted pair of free distinctions; an **unnamed hollow triple** is a
hollow triple that is not a knot; together with frozen distinctions these are what a law **adds**. A base is read **faithfully** when
the law adds nothing and its knots' pairs are free. A set of knots **forces** a set S when its states alone restrict S. A hollow
triple is **plain** when it misses 000 and 111 and **signed** otherwise (not-all-equal with some distinctions read negated).

## The question

- **Where it comes from.** Everything proved on the knots-alone line needs each co-knotted pair in exactly two knots. The owner's
  object is unrestricted: a knot may share distinctions with any number of others, and a base is a pattern of overlap, infinite ones
  included (2026-11-11).
- **The question.** In bases with any overlap, what does the not-all-equal law (NAE) add, from which configurations of knots, and is
  it local? Which overlapping bases does it read faithfully?

## The question in standard terms

For a 3-uniform hypergraph with any number of edges on a pair, what do its proper 2-colourings force on vertex sets of size at most
three that are not edges; what are the minimal edge sets forcing them; and when are the restricted triples with unrestricted pairs
exactly the edges?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The law adds only its own kind.** Nothing is ever frozen; a tied pair is always equal or always unequal; every unnamed hollow triple misses exactly one complementary pair of patterns, so it is NAE with some distinctions read negated, itself a knot. In the census's catalogue, random small bases and re-read bases: 569,921 signed and 177,539 plain unnamed hollow triples, 188,914 equal and 285,338 unequal tied pairs, nothing else. | proved (L1; known: the co-clone of complement-closed relations); computed | B, A |
| 2 | **The law reads pair counts, not knots.** Two knot patterns with the same number of knots on every pair have the same states (L5, from L4: the cut weighted by those counts is twice the knots exactly at states). So at most one of them is read faithfully, and four knots arranged as a Pasch configuration (literature) read as the eight of the zero-pair weave on six distinctions (literature: the octahedron), which is read faithfully (L2). | proved (L2, L4, L5; L4 known) | B |
| 3 | **Overlap is readable.** A pair can lie in any number of knots in a base read faithfully (L3: k knots on one pair and nothing else, the literature's book). In the census, faithful bases with a pair in three or more knots: 509 of 2,521 at 7 distinctions, falling to 82 of 452 at 10; 22 of the 160 faithful swap-made bases; 26 of the 90 grown ones, with pairs in up to 9 knots. | proved (L3); computed | B, A |
| 4 | **Uniform overlap is not.** Where every co-knotted pair lies in exactly three knots, states exist only at 7 to 9 distinctions (40 of 240 patterns) and none is read faithfully (P5 held); where every pair of distinctions lies in exactly λ ≥ 1 knots there is no state beyond four distinctions (L4). | computed, frozen; proved | A, B |
| 5 | **The smallest configurations that force something** (minimal, up to isomorphism, with S marked): 1 with three knots (adjacent apices, a signed hollow triple), 4 with four (P1 held), 11 with five, 64 with six; 46 force signed hollow triples, 23 plain ones, 6 unequal and 5 equal tied pairs. | computed, exact | A |
| 6 | **What the law adds is not local (P3 and P4 failed).** Small bases: 3 of the 8,000 unfaithful ones examined, on 10 distinctions, need seven knots to force anything they add (eight for some of their sets; exhaustive). Swap-made two-fold weaves: 17 of 662 failed the registered radius test, and on a closer count 98 (72 of the 205 with one swap, 24 of 213 with two, 2 of 244 with four) have no added set that any proper part of the base around it forces: only the whole base does, through about half its knots and nearly every distinction. | computed, frozen; the closer count after the run | A |
| 7 | **Rulers on overlapping bases.** Grown bases read faithfully: at graph distance 2 every pair lies in a bond of four (767 of 767); at distance 3, 239 pairs have bond distance 4 and 52 have 3. Small bases: some pairs at graph distance 2 or 3 lie in no bond at all (115 of 1,223 distance-2 pairs at 7 distinctions lie in none of five or fewer, and every such pair at 7 and 8 distinctions, 281 in all, lies in none of any size), like two of a book's pages: bond distance is undefined there. | computed, frozen; the any-size check by the referee | A |

## Answer

Overlap makes new knots, and they are always the law's own kind: not-all-equal, sometimes with a distinction read negated. What the law
reads of a base is decided by how many knots lie on each pair, not by which triples are knots, so different overlaps with the same
counts are one base to it. Overlap is readable, with a pair in up to nine knots in a base read faithfully, but uniform overlap is not.
The configurations that make new knots do not form a short local list: their number grows with size (1, 4, 11, 64 at three to six
knots), some small bases need seven knots, and a single knot swap in a two-fold weave can make the law bind a triple that only the
whole base holds. In a base with overlap, some pairs a step or two apart lie in no bond at all.

## Reading

**Interpretation, not a theorem.**
- **The compressed structure is the pair counts.** In the owner's words the emergent structure is "folded" and "compressed". Under
  not-all-equal there is an exact sense of compression: the law forgets which triples are knots and keeps only how many knots lie on
  each pair. Two overlaps with the same counts fold to the same thing.
- **New knots from overlap.** Half the zero-pair weave on six distinctions is read as the whole: overlap supplies knots no one put in.
  Each is the same law seen through a negated distinction, so what emerges is more of the law, not a new law.
- **Global knots.** As loops gave the ruler its cutoff on closed weaves, a swap can create a binding that only the whole base holds.
  The emergent structure has global parts, not only local ones.
- **For question 9.** Overlap breaks the ruler in a new way: some pairs two steps apart lie in no bond at all, so bond distance is
  not defined everywhere on a base with overlap, and something beyond overlap is needed to measure it.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** L1 to L5 for every finite knot pattern. **Computed.** Conclusions 3 to 7 in the
  registered families only: the catalogue to six knots, bases on 4 to 10 distinctions, NAE-SURFACE's and GROW-COUNT's bases, uniform
  overlap three on 7 to 14 distinctions. Nothing here is claimed for infinite bases.

## Stress test

The lemmas cover every size. The census's own controls: X1 regenerated NAE-SURFACE's 822 readings exactly (160 faithful); X2 found
every forcing set of at most six knots in the small bases in the catalogue (7,667 of 7,667). The six-distinction marks were recomputed
after the run (see Corrections). One size past the catalogue: P3's three seven-knot cases are the first entries beyond it.

## Review

An independent referee (a fresh agent with its own NAE code and solver) checked the census:
- **P3's failure is real.** Exhaustive search over every subset of the three bases' knots finds no forcing set of six or fewer for
  any added set; the smallest have seven (eight for two sets of the third base), and the three seven-knot patterns are pairwise
  non-isomorphic. The fallback's other answers hold (59 of the 62 checked exhaustively explained, the same 3 failing; all 330
  embedded entries confirmed).
- **P4's failure is real and understated.** The 17 are the bases whose every added set has radius exactly 4, where the radius-4 ball
  is the whole base. The forcing ball is also the whole base in all 74 radius-3 passes and 7 of the 15 radius-2 passes, so 98 of the
  662 unfaithful swap-made bases (72 of the 205 with one swap) have no added set forced by a proper ball. The frozen radius
  histogram is not a minimum, since its rule stopped at the first set of radius at most 2 (the true minima: 556 at radius 1, 15 at
  radius 2). `global_obstructions.py` recomputes the count in the record: 98, and among the other 564 the least proper forcing radius is 1 for 556 and 2 for 8.
- **The catalogue is complete** to six knots under its definition: an unpruned enumeration with exact canonical forms (1, 2, 9, 51,
  361 and 3,683 connected configurations) gives the same 80 entries with the same kinds; the pruning and minimality tests are sound,
  and the "two knots outside S" condition loses nothing.
- **The Pasch test was wrong** (it always returned False): only X3's table was affected; the corrected recount agrees with the
  supplement (7,443 faithful; 450 unfaithful without adjacent apices, all with an incomplete Pasch; 985,187 with adjacent apices;
  49,552 with no state).
- **Other numbers agree:** X1 on all 822; all 80,000 small readings; the C5 rows (a "None" in the small bases means no bond of three
  to five; in the grown bases' third column it means not computed); the 240 uniform-overlap patterns. The SAT sampler's blocking
  clauses exclude supersets of found patterns, a bias in the sample, not an error in any count. P2's kinds were collected from the
  catalogue, the random small bases and the re-read bases, not from the six-distinction table or the uniform-overlap patterns.

The lemmas (ticket B) were refereed separately: proved, with wording fixes made (the proof's "Review" section). The referee found L1
and L4 known and suggested L5.

## Literature and provenance

- **Known.** L1 is the co-clone IN2 of complement-closed relations read on three distinctions (Böhler, Reith, Schnoor and Vollmer
  2005; Creignou, Khanna and Sudan 2001). L4 is the triangle gadget of the NAE-3SAT to maximum-cut reduction (Garey, Johnson and
  Stockmeyer 1976), with Rosa's 1970 counting for Steiner triple systems. The Pasch configuration is the smallest trade (Hedayat and Li
  1979), and the octahedron splits into two.
- **Not found** (bounded search): a catalogue of what proper 2-colourings force on non-edges, or of the minimal edge sets forcing them.
- **Classification.** Known-with-delta: the tools are classical; the catalogue, its growth, the global hollow triples and the reading
  are the delta.

## Workspace assumptions

- **Relied on.** A64 (the count of how knots meet names no face). **Added.** A67: a base is read on sets of at most three distinctions
  (what a law adds is counted there). **History.** A64 gains a line: the count of knots on each pair is exactly what NAE reads.

## Ratio

- **Substantive.** The catalogue and census (one registered run), the five lemmas, two after-run descriptions, two referee passes.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**), on the published pre-registration and frozen code:
- the pre-registration's L1 left out "when a state exists", and its L3 ("a pair in any number k of knots whose other corners lie in
  no other knot is read faithfully") is true only for the book as the whole pattern;
- the frozen code's Pasch test took the complementary triples to be those meeting each Pasch knot in one distinction; they are the
  other four transversals of the three pairs the Pasch never joins. It affected only the six-distinction marks (no prediction):
  recomputed, all 450 unfaithful patterns there without adjacent apices contain an incomplete Pasch, as the disclosed pilot said
  (`supplement.py`).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what NAE makes of overlapping bases | **Status:** Successful | Two predictions failed informatively; the law's additions characterized and the reading by pair counts proved |
| Local direction — NAE on finite overlapping bases | Continue | The global hollow triples are unexplained; the catalogue's growth is open |
| Broader exploration — G1 on bases of knots alone | Promising pivot available | The owner's infinite bases: periodic patterns of overlap |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | What the knot law reads of any overlap is now known in kind; its ruler on overlap is not |

**Corrections:** one, Not a block. **Goals:** a G1 checkpoint (capability gained), no goal change. **Assumptions:** A67 added; A64
gains a history line, status unchanged.
**Basket:** `LONG-LOOP-20261111-001#3` (bond balls read dimension 2, 2/3, 2/3), `RULER-20261111-001#3` (other laws, 2/3, 2/3),
`RULER-FLAT-20261111-001#2` (the local list on six-regular weaves, 2/3, 2/3); taken: none yet; direction 1 below is the first.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Infinite bases: periodic patterns of overlap | 3/3 — Major | 2/3 — Testable | Read a frozen family of periodic knot patterns (any knots per pair) between periodic and finite-window bounds, with source labels → an infinite overlapping base read faithfully and its ruler, or none in the family | Selected · awaiting go-ahead |
| 2 | What the global hollow triples are | 2/3 — Substantial | 3/3 — Ready | Test whether each of the 17 forcing sets is one of the weave's two classes of knots and whether the binding is a winding of the height (`RULER-FLAT-20261111-001`) → a proved description, or a counterexample | Alternative · deferred |
| 3 | The catalogue's growth | 1/3 — Modest | 2/3 — Testable | Extend to 7 and 8 knots and test whether every entry is built from adjacent apices and the Pasch by composition → a generating rule, or a primitive entry beyond them | Alternative · deferred |
| 4 | Reading by pair counts | 2/3 — Substantial | 1/3 — Stated | Characterize which pair-count functions some faithfully read base realizes → a criterion, or a counterexample family | Alternative · deferred |

1. **Infinite bases.** Payoff 3: the owner's object (infinite patterns of how knots overlap), and the first test of the law beyond
   finite bases. Concreteness 2: the reading with honest bounds is designed (the earlier outline), the enumeration is not written.
2. **Global hollow triples.** Payoff 2: they are where locality fails, and they may be the overlap version of the winding cutoff.
   Concreteness 3: seventeen cases and their forcing sets are recorded.
3. **The catalogue's growth.** Payoff 1, concreteness 2.
4. **Reading by pair counts.** Payoff 2: it would say what L5's compression keeps. Concreteness 1.

**Recommendation.** Research directions, #1, the owner's infinite bases, awaiting the go-ahead; #2 is small enough to run beside it.

## Final report as sent

Sent to the owner on 2026-11-11 at 20:51 UTC, summarized here (the two tables are those above, with directions 1 to 3). The headline:
the law makes new knots, always of its own kind, and reads only how many knots sit on each pair; overlap is readable but uniform
overlap three is not; what it adds is not local (98 of 662 swap-made bases bind a triple only through the whole base); and some pairs
two steps apart lie in no bond at all. Corrections: one, Not a block. Goals: a G1 checkpoint. Assumptions: A67 added, A64 a history
line. Holding for a go-ahead on #1, with #2 small enough to run beside it.
