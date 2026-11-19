# Referee reports VARIABLE-OUTPUT-READER-001F-R1, 001G-R1 and 001H-R1 (fresh code, no Codex)

**Verdict on all three: confirmed. No Block.** Each study supersedes part of the one before, so this report leads with what stands
at the end.

## What stands after 001F, 001G and 001H

The law throughout is the serial law. A ternary seed comes first. Each later junction takes one loose distinction from each of one,
two or three junctions and makes two or three fresh ones. Two parents need an ordinary common neighbour. Three parents need one for
each pair and none common to all three. This is not A104's complete-round rule.

1. **Finite and complete (001F, together with 001A to 001E).**
   - **The claim.** At every width from 15 to 26 the full bond-distance table separates every reachable arrangement type. Every
     symmetry of a table keeps that arrangement's legal triples. So a first full-table counterexample for three-parent joins needs at
     least **27 distinctions**.
   - **The referee's independent census counts every type at widths 20 to 25 exactly as the study does.** Width 26 was spot-checked
     through its 197 hard cases. Section 1 gives the details.
2. **Every size, when one side has small junctions (001G).**
   - **The claim.** Suppose one presentation has at most four distinctions at every junction. Then pair distances through D = 5
     give back every junction, and so every next choice, against any reachable rival. The rival may use any junction and any history.
   - **The horizons are sharp.** D through 3, 4 and 5 suffice for zero or one, exactly two, and three or more three-fresh joins.
   - **This supersedes 001F's restricted theorem**, which is the case of zero or one three-fresh joins.
   - **The referee checked it exhaustively at widths 15 to 21 against every rival.** The proof's two key steps check by hand.
     **Sharpness for two three-fresh joins is already reached at width 21** (two pairs), below the study's width-27 example; section 2.
3. **Every size, on the three-dimensional family (001H).**
   - **The claim.** Distances through D = 5 also suffice for finite downsets of the coordinate growth. Each three-parent junction there
     may drop an output that has no successor. The rival is unrestricted, and five is sharp.
   - **The referee checked the key step by hand and computed one size past the study's box.** The 51-distinction witness and all
     116,997 comparisons reproduce exactly (section 3).
4. **Still open.** The general mixed law, when *both* presentations carry a five- or six-place junction in the part holding the
   marks. 001H's four-place cycle marks exactly where the proof stops, and the referee confirms it: six distinctions are pairwise
   within K ≤ 6, no junction holds more than two of them, and they form no equation.
5. **The full menu is a separate question.** 001A's width-18 witness has identical allowed states on the same names (section 1.4).
   So no reading derived from states can give back one- and two-parent permissions when fresh counts vary. That witness lies outside
   001G's family, since both of its sides have a six-place junction.

# Part 1: VARIABLE-OUTPUT-READER-20261118-001F

## 1.1 The exhaustive claim at widths 21 to 26 (question 1)

**Which law's reachable set it is.** It is the serial two-or-three-fresh law above, with the seed unmarked. A type is a site graph
(sharing is simple, so this is the whole incidence) with a loose count at each site, up to isomorphism.

**Recount.** The referee wrote its own census (`referee_f.py census`):
- each width is grown from the two widths below it;
- duplicates are removed by a Weisfeiler–Lehman hash with VF2 isomorphism inside each hash class;
- the full table is built by enumerating every shore, with the bond test "both sides connected";
- table symmetries are found exactly through the twin quotient. Twins are distinctions with equal entries to every other one; the
  adjacent swaps inside twin classes, plus a lift of every symmetry of the quotient, generate the whole group.

The bond table was checked against the referee's GF(2) table from 001D-R1 on 30 width-17 types: no difference.

| Width | Types (referee = study) | With a legal triple | Legal triple occurrences | Distinct types with isometric full tables | Types whose table has a symmetry moving a legal triple to a forbidden one |
| --- | --- | --- | --- | --- | --- |
| 20 | 19,414 | 1,585 | 6,358 | 0 | 0 |
| 21 | 46,449 | 4,303 | 17,259 | 0 | 0 |
| 22 | 112,335 | 11,445 | 46,004 | 0 | 0 |
| 23 | 273,842 | 30,541 | 121,697 | 0 | 0 |
| 24 | 672,424 | 81,484 | 323,484 | 0 | 0 |
| 25 | 1,661,752 | 216,788 | 856,726 | 0 | 0 |

- **Every count equals the study's,** including by junction number at width 20.
- **Width 25 is now folded in** (it was pending at first publication). Its 1,661,752 types match, with 0 isometric pairs and 0 symmetries moving a legal triple.
- **The tables are distinct.** At every width the referee's refinement invariant already gives every type a different value. An
  isometry preserves the invariant, so no two types have isometric full tables.
- **No symmetry search was capped.**
- **Width 26** (4,131,343 types) was not recounted; section 1.2 spot-checks it.
- **The study's second completeness check was not redone.** That is the reverse count of 8,585,343,953 histories at width 26.

## 1.2 The 311 hard cases (question 2)

The 311 cases are read from `residual_cases.jsonl` (`referee_f_hard.json`). They split 4, 12, 31, 67 and 197 across widths 22 to 26.

| Check | Result |
| --- | --- |
| A legal birth order exists | **311 of 311**, found by the referee's own search over orders, which applies the parent rule step by step |
| Width as stated | 311 of 311 |
| Legal-triple count as stated | 311 of 311 (3,505 in all) |
| Every table symmetry keeps the legal triples | **311 of 311** (exact group, never capped) |
| Orbits of legal triples under the symmetries, summed | **786**, as the study finds |

## 1.3 The all-size family (question 3)

**Proved, including against a rival with unrestricted mixed counts.** The argument has three steps, and the referee checked each by
hand:
1. **The short-equation theorem puts every equation of H in R.**
   - It needs no four-bit bond with a shore of three or more junctions. That holds because a source whose junctions have at most four
     distinctions joins at most two parents, so each join makes at least as many distinctions as it takes.
   - The equations of size three and four then agree, and they generate H's space, so C_H ⊆ C_R.
2. **The rank count closes the gap.**
   - Width is w = 3 + 2(j − 1) + s for any reachable presentation, and its j stars are independent, so the rank is j.
   - Hence the rank is at most 1 + ⌊(w − 3)/2⌋, and with s ≤ 1 the source reaches it.
   - Containment with equal rank gives C_H = C_R.
3. **The menus agree.** By 001D's allowed-state theorem, equal states on the same names give equal three-parent menus.

The rival enters only through the rank bound, which holds for every reachable presentation, so "even a rival with unrestricted mixed
counts" is proved. The exhaustive check in section 2.2 agrees: no failure for s ≤ 1 at K through 4 at widths 15 to 21.

The five-bit-bond theorem and the six-bit family were read, not re-derived. The terminal-junction theorem was read too; it is
correctly scoped (a common prefix and one appended junction per side).

## 1.4 The width-18 witness (question 4, and 001G's question 4)

Replayed from 001A's `witness.json` (`referee_f_w18.json`):
- **Both histories are legal under the referee's law.** The eighth junction is a three-parent, three-fresh join on 9, 10, 11 in one
  history and on 12, 13, 14 in the other, with the same fresh 15, 16, 17.
- **Identical allowed states on the same names.** The two parity-check spaces are equal (rank 8, 1,024 allowed rows).
- **Identical full tables.**
- **Isomorphic as incidence types,** so 001F's census counts them once.
- **The menus differ.**
  - One-parent choices: {12}, {13}, {14} and the fresh 15, 16, 17 against {9}, {10}, {11} and the same fresh.
  - Two-parent choices: {12, 13}, {12, 14}, {13, 14} against {9, 10}, {9, 11}, {10, 11}.
  - There are no three-parent choices on either side.
- **What it means.** The one- and two-parent permissions are not a function of the allowed states once the fresh count varies. The
  older equations sum to the six loose distinctions, so the two eighth equations are equal modulo them. So no state-derived reading,
  pair, triple or full, can recover those permissions here.
- **No conflict with 001G.** Both sides carry a six-place junction, so the witness is outside 001G's family. 001G's "every next
  choice" claim needs one side with junctions of at most four distinctions.

# Part 2: VARIABLE-OUTPUT-READER-20261118-001G

## 2.1 The all-size theorem (question 1)

**The key steps check by hand** (`extension.md`):
- **The excess identity.** |δ_H U| = Σ d(u) + 2I(U), with d = h − p + 2k ≥ 0 on the sites that survive in H. It follows from the
  orientation by R's birth order.
- **The five-place step.**
  - Take two output distinctions of a five-place rival site x. They are loose in H at its children s and t, so both children lie on
    any shore through them, and Σ d ≥ 4.
  - I ≥ 1 gives a cut of at least 6. When I = 0, the first site of U has no incoming distinction and excess at least 3, so it must
    be s or t.
  - Equality then forces the second site to be the other child, with its one surviving parent the first. But s and t are both
    children of x, so they have one colour and are not adjacent.
  - So K_H ≥ 6 against K_R ≤ 5.
- **The six-place step.**
  - Two children that both keep an input give a pair with K_H ≥ 7, by the same count with I = 1. So at least two children keep no
    input.
  - For such a child s, and the latest old parent a (which had two distinct earlier parents), the pair (xs, xa) has K_H ≥ 7 in each
    of the cases I = 0, 1 and 2 or more.
  - The six-place star gives K_R ≤ 6.
  - Induction on the earliest high site then removes all of them.
- **Not checked line by line:** the nesting of large four-bit shores and the bridge recognition. They are read and consistent with
  the computations below.

## 2.2 The cutoff table and its sharpness (question 2)

**Exhaustive, against every reachable rival** (`referee_g.py cutoff 21`, `referee_g_cutoff.json`). At every width from 15 to 21
the referee tested every source H whose junctions all have at most four distinctions. The tests were run at its stated horizon
(K through 4, 5 or 6 for s ≤ 1, s = 2, s ≥ 3) and one below it. Two tests:
1. Does any other type of the same width have an isometric clipped table?
2. Does every symmetry of H's clipped table keep H's junction supports?

If both hold, every rival of any arity has H's junctions.

| s | Sources (widths 15 to 21) | At the stated horizon | One below it |
| --- | --- | --- | --- |
| 0 | 5,371 | **no failure** | fails, for example 3,881 of 3,938 sources at width 21 have a clipped-table symmetry moving a support, and triple verdicts flip |
| 1 | 5,694 | **no failure** | fails, likewise (4,374 of 4,390 at width 20) |
| 2 | 10,756 | **no failure** | **fails at width 21 only: two rival pairs, each isometric through K = 4, with opposite triple verdicts**; no candidate rival at widths 15, 17 or 19 |
| 3 | 2,547 | **no failure** | no failure (no rival even shares the invariant) |
| 4 to 6 | 2,201 | **no failure** | no failure |

**The referee's width-21 witness for the two-addition row** (`w21_witness.py`, `referee_g_w21_witness.json`). It is smaller than the
study's width-27 one, which the study did not claim to minimize (`proof.md`: "Their widths have not been minimized").
- **The source** has nine junctions, at most four distinctions each:
  - the seed {0, 1, 2};
  - unary joins {0, 3, 4} and {1, 5, 11};
  - the pair join {3, 5, 6, 7};
  - a three-fresh unary join {6, 12, 13, 14};
  - the unary join {2, 8, 15};
  - the pair join {4, 8, 9, 10};
  - a three-fresh unary join {9, 16, 17, 18};
  - the pair join {7, 10, 19, 20}.
- **Its legal triples** are {11, 15, 19} and {11, 15, 20}.
- **The rival** has ten junctions, one of them five-place: {6, 8, 13, 14, 15}, a three-parent, two-fresh join. Its legal triples: none.
- **The isometry through K = 4** sends {11, 15, 19} to {6, 8, 13}, exactly the five-place junction's inputs. The rival has already
  joined them. This is the same mechanism as the study's width-27 example.
- **Separation:** the clipped tables are not isometric through K = 5, and the full tables are not isometric.

**The study's named pairs, all replayed from the seed** (`referee_g_witnesses.json`). Every history is legal under the referee's law.

| Pair | Three-fresh joins (source, rival) | Ranks | Bonds | Every pair equal through | Mark (source, rival) | Named pairs |
| --- | --- | --- | --- | --- | --- | --- |
| width 27, rank gap | 2, 0 | 12, 13 | 278, 983 | K = 4 | legal, forbidden | K(19, 22) = 7, 5, i.e. D = 6 against 4 as stated; K(9, 11) = 6, 5 |
| width 26 | 3, 1 | 11, 12 | 274, 1,075 | K = 5 | legal, forbidden | K(13, 15) = 7, 6; K(16, 17) = 8, 6 |
| width 27 (only non-root children) | 4, 2 | 11, 12 | 274, 1,075 | K = 5 | legal, forbidden | K = 8, 6 on the three outputs |
| width 29 (common attachment) | 4, 2 | 12, 13 | 380, 1,565 | K = 5 | legal, forbidden | |
| **width 32, one size past (one more matched three-fresh join on bit 28)** | **5, 3** | 13, 14 | 487, 2,056 | **K = 5** | **legal, forbidden** | |
| width 15, swap (10 11) | 0 | 7 | 63 | K = 3 | legal, forbidden image | |
| width 18, swap (10 11) | 1 | 8 | 89 | K = 3 | legal, forbidden image | |

Every full histogram differs where the study says so.

## 2.3 The width-27 witness (question 3)

- **All 351 pair readings agree through D = 3** (K = 4) on the same names.
- **The two outputs 19 and 22 of the rival's extra junction** have D = 6 in the source and 4 in the rival.
- **The marked triple {9, 11, 13}** is legal in the source and consumed in the rival.
- **Ranks** are 12 and 13; the full K histograms differ.

## 2.4 The width-18 witness (question 4)

See section 1.4.

# Part 3: VARIABLE-OUTPUT-READER-20261118-001H

## 3.1 The all-size theorem and its scope (question 1)

**The scope, as the referee reads it.**
- **The sources:** finite downsets S of ℕ³ grown in increasing coordinate sum. Each site takes one input from each immediate
  predecessor and makes an output in each increasing direction. A three-parent site may drop one output whose successor is not in S,
  and any number of sites may do so, adjacent or not.
- **The rivals:** every reachable presentation under the mixed law, with any history.
- **The reader:** gets only the anonymous table through D = 5.

**The key step, the short-shore condition, checks by hand** (`coordinate_growth.md`). The condition is that three or more sites
always export at least seven distinctions.
- **Each occupied layer has two horizontal crossings.** This takes three cases: both minima positive, one minimum zero, both zero.
  Sites on a coordinate plane never drop an output.
- **Four layers give eight.**
- **Three layers with no vertical crossing** force positive horizontal coordinates. Then any layer of two or more sites has an
  incoming crossing for every occupied row and every occupied column, and three singleton layers give nine.
- **Otherwise U lies in a 2 × 2 × 2 cube.** Its internal meetings are at most 2t − 4; the induced edges of the cube graph on 3 to 8
  vertices are at most 2, 4, 5, 7, 9 and 12. Its arities sum to at least 4t − 1, which leaves seven.
- **The other two hypotheses are immediate.** Only the seed is ternary, and four-place sites are unary.

**Computed, one size past the study's 2 × 3 × 3 box** (`referee_h_shore.json`). For every nonempty downset, with an output dropped at
every eligible site (this minimises every cut, since a dropped output would otherwise be loose), the referee checked four things:
- the construction is legal under the referee's law;
- both hypotheses hold;
- the least cut around three or more sites, by max-flow with each three-site path forced inside;
- that least cut against brute force on every downset of at most 14 sites.

| Box | Nonempty downsets | Legal and hypotheses hold | Least cut around three or more sites | Brute force agrees |
| --- | --- | --- | --- | --- |
| 2 × 3 × 3 (the study's) | 174 | 174 | **7 in all 170** with three or more sites | 160 of 160 |
| **3 × 3 × 3** | 979 | 979 | **7 in all 975** | 568 of 568 |
| **2 × 4 × 4** | 1,763 | 1,763 | **7 in all 1,759** | 682 of 682 |
| **2 × 2 × 10** (the family of the study's 88- and 99-distinction checks) | 1,715 | 1,715 | **7 in all 1,711** | 370 of 370 |

The theorem then follows from `high_inverse.md`'s theorem. The referee checked that theorem's arity-five forcing pair by hand: an
outside distinction within K ≤ 5 of an output must meet its child. The arity-six case and the exclusion of an extra five- or six-bit
equation were read, not re-derived.

## 3.2 Five is sharp: the 51-distinction witness (question 2)

Replayed from `horizon.json` (`referee_h_witness.json`).
- **The history is legal.** It has 17 junctions of arities 3, 4, 5 and 6 (1, 5, 8 and 3 of them) and 36,250 bonds, as stated.
- **The mark {42, 46, 50} is legal,** and 27 triples are legal in all.
- **D(42, 46) = 13** (K = 14). This is the largest distance between two members of any legal triple there, and the stated upper bound
  of 13 checks by hand: the cut around the holders and their common witness has at most 6 + 6 + 6 − 4 = 14 distinctions.
- **The swap (42 45) preserves all 1,275 entries through D = 4** (K = 5).
- **The image {45, 46, 50} puts two inputs at one junction,** so it is forbidden.
- **Entry (42, 46) becomes D = 5** under the swap, so distance five exposes it. The full table changes in **76** entries.
- **The 21-distinction companion** (maximum arity five) agrees through D = 3 and separates at D = 4. Its K goes from 10 to 5, with 28
  entries changed.

## 3.3 The obstruction and the comparisons (question 3)

**The four-place cycle** (`referee_h_cycle.json`). The construction:
- t is unary on the seed; p and q are unary on t;
- w is a two-fresh join on p and q; b is a three-fresh join on p and q; c is a three-fresh join on t and w.

The checks:
- **The history is legal.**
- **All 15 pairs among tc, wc, pb, qb, tp and wq have K ≤ 6**, with values 4 to 6.
- **No junction holds more than two of them.**
- **The six are not an equation.** They are not in the cut space.

So the pair table makes them look like one six-place junction that is not there, exactly as described.

**The 116,997 comparisons, regenerated rather than sampled** (`referee_h_cross.json`). The generation follows the study's
definitions, recomputed with the referee's own law and tables:
- start from 001G's two base pairs;
- add up to two serial additions that never consume the mark, taking one representative distinction per holder;
- keep the continuations with a high junction that keep the base verdict;
- pair them at equal width.

| | Referee | Study |
| --- | --- | --- |
| Generation (source: paths 1, 18, 332, of which 0, 4, 125 eligible; rival: 1, 30, 672 or 764, all eligible) | as stated | the same |
| Equal-width pairs by width 29 to 33 | 120, 732, 36,890, 68,750, 10,505 (**116,997**) | the same |
| Opposing pairs through D = 4 (an isometry of the clipped tables carrying the mark to itself, opposite verdicts, different site graphs), by width | 6, 10, 234, 817, 451 (**1,518**) | the same |
| Opposing pairs through D = 5 | **0** | 0 |

**Not checked:**
- the 17,105-presentation self-symmetry search;
- the five-exception theorem;
- the terminal high-junction theorem;
- the 88- and 99-distinction reader runs. Their family's shore condition is covered by the 2 × 2 × 10 box above.

# Fixes for the owner (listed, not folded in)

None of these is a block.

1. **001G, an addition.** The two-addition row's sharpness is attained at width 21. The exhaustive census shows no candidate at
   widths 15, 17 or 19, so 21 is the smallest width for that row. It could be cited beside the width-27 example.
2. **001F and 001G, a scope line.** The width-18 witness's two sides have identical allowed states and are isomorphic types. It could
   be stated where the one- and two-parent obstruction is cited: the menus differ on named distinctions only, so it says nothing
   about types.
3. **001H, a wording point.** "Distance five" is D = 5 (K = 6); the proof file works in K. One line tying the two would help a reader
   moving between `decision.md` and `high_inverse.md`.

# How the work was split

- **The referee:**
  - read the three decision notes;
  - read `proof.md`, `structural.md`, `population.md` and `history_balance.md` for 001F;
  - read `proof.md`, `cutoff.md` and `extension.md` for 001G;
  - read `coordinate_growth.md`, `high_inverse.md`, `marked_distances.md` and `cross_search.py`'s definitions (data only, not run)
    for 001H;
  - wrote `referee_f.py` (shared machinery, census, hard cases, width 18), `referee_g.py` and `w21_witness.py` (001G), and
    `referee_h.py` (001H).
- **Study code** was not imported or run; study files were read as data.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

# Files and reproduction

Run from each folder.

| Folder | Command | Wall time |
| --- | --- | --- |
| 001F | `referee_f.py census 23 20` | 3 min |
| 001F | `referee_f.py census 25 24` | 40 min, memory-capped (MemoryMax 36G) |
| 001F | `referee_f.py hard` | 1 s |
| 001F | `referee_f.py w18` | 1 s |
| 001G | `referee_g.py witnesses` | 1 s |
| 001G | `referee_g.py cutoff 21 15` | 4 min |
| 001G | `w21_witness.py` | 35 s |
| 001H | `referee_h.py witness` | 2 s |
| 001H | `referee_h.py shore` | 30 s |
| 001H | `referee_h.py cycle` | 1 s |
| 001H | `referee_h.py cross` | 20 s |
