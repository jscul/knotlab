# Referee report VARIABLE-OUTPUT-READER-001I-R1 (fresh code, no Codex)

**Verdict: confirmed. No Block.** The four items the coordinator listed all hold:
- **The cycle obstruction:** the proof checks by hand and reproduces on all six fixtures.
- **The three cutoffs** reproduce with their sharp witnesses, including the 71-distinction swap. Two all-rival claims were checked
  exhaustively at width 24 against every reachable type.
- **The all-size result:** exhaustive against every rival at widths 12 to 23, and its structural conditions hold on 300 random
  sources.
- **The seven-to-six lemma** checks by hand.

There are no fixes beyond one counting note. The law is the serial two-or-three-fresh law of 001D to 001H.

## 1. The cycle obstruction (question 1)

**The proof checks by hand** (`obstruction.md`).
- **The certificate word.** W △ T △ Q = {wc, pb, ut, q₀}: T = {ut, tp, tq, tc} and Q = {tq, qw, qb, q₀} cancel tp, tc, tq, qw and
  qb.
- **T is forced.** tp and tq were born at t, a three-output site. By the small-shore classification they lie in bonds of size at most
  four only at t and at their four-place other endpoints. So N₄(tp) ∩ N₄(tq) = T, and a rival bond attaining K(tp, tq) = 4 must be T.
- **The same argument forces Q** (from qw, qb), **P** (from pw, pb) **and A** (from pw, qw).
- **The contradiction.** If W were a rival equation, the four-bit word would be one too. It must be a bond: no singleton or two-bit
  bonds exist, and a split would need two parts of three or more. That puts pb and wc within K ≤ 4, which the source forbids.
- **It persists under continuation and renaming.** The classification is a statement about the current presentation, so it survives
  every continuation, and every step commutes with renaming.
- **The non-graphic remark (the Fano minor) checks.** The seven displayed forms are all seven nonzero vectors of GF(2)³, and a graphic
  space of rank 3 has at most six distinct nonzero columns.

**Computed on all six fixtures**, replayed from `fixtures.json` and legal under the referee's law (`referee_i_fixtures.json`):

| Fact | Base (20) | 2-2 (24) | 2-3 (25) | 3-2 (25) | 3-3 (26) | mirrored 3-3 (26) |
| --- | --- | --- | --- | --- | --- | --- |
| W's 15 pair minima (K = 4, 5, 6) | 4, 2, 9 | 4, 2, 9 | 4, 2, 9 | 4, 2, 9 | 4, 2, 9 | 4, 2, 9 |
| T, P, Q, A forced (K = 4, common N₄ = the star) | all four | all four | all four | all four | all four | all four |
| W △ T △ Q | {0, 7, 11, 12} | same | same | same | same | same |
| K(pb, wc) | 6 | 6 | 6 | 6 | 6 | 6 |
| W in the physical space | no | no | no | no | no | no |
| Space enlarged by W: agrees with the physical table through | K = 3 | 3 | 3 | 3 | 3 | 3 |
| … full entries changed | **61** | 79 | 84 | 87 | 94 | 100 |
| Legal triples | 0 | 4 | 6 | 4 | 6 | 6 |

## 2. The three cutoffs and their sharpness (question 2)

The cutoffs are stated in D. In K they read 4, 5 and 6.

| What is read | Cutoff | Sharp witness (referee) |
| --- | --- | --- |
| Whether the six form an equation | D through 3 | On the mirrored 3-3 fixture, (5 8)(10 13) agrees through K = 3 only. It sends W to the genuine bond P △ A, which lies in the physical space. It sends all six legal triples to forbidden ones, for example {8, 18, 23} to {5, 18, 23} |
| Every legal triple of the five live continuations | D through 4 | (7 8) on the mirrored fixture, and (10 11) on the four others, agree through K = 4 and send every legal triple to a forbidden one |
| Every legal join, at every size, in the one-exception family | D through 5 | The 71-distinction swap (section 3) |

**Exhaustive, against every reachable type of width 24** (`referee_i_w24.json`, 672,424 types from the referee's census):

| Source | Through K = 4 | Through K = 5 | Through K = 6 |
| --- | --- | --- | --- |
| Fixture 2-2 (width 24, 4 legal triples) | 27 other types are isometric, all 27 changing a triple verdict; clipped symmetries move supports | **no other type is isometric; every clipped symmetry keeps the supports and triples** | the same |
| Intersecting cycles, one repetition (three two-fresh joins) | 19 other types are isometric, all changing a verdict | **none** | **none** |

So the fixtures' claim checks against every rival at that width: K through 5 fixes every support. The block proof's claim for the
repeated family checks at its first member. That member is even read at K through 5.

**The 62 one-junction extensions** of the base fixture are 22 unary and 40 binary choices on named distinctions, counting both fresh
counts. Up to the choice of bit at a holder they are 13 parent sets times 2. None has a legal triple.

## 3. The 71-distinction witness and the all-size scope (questions 2 and 3)

**The witness** (`referee_i_w71.json`, exact bonds through K = 7 by the referee's flow-pruned search over every shore):
- **The history is legal.** It has 24 junctions, of arities 3, 4, 5 and 6 (1, 9, 11 and 3 of them).
- **It is in the family.** Exactly one join is not three-fresh: site 20, two parents and two fresh.
- **9 legal triples.** The mark is legal, and its image under the swap repeats a holder.
- **All 2,485 entries are equal through K = 5** (D through 4) after the swap, and **20 change at K = 6**.
- **The new four-place sites (17 to 20) and the three marked holders lie in one part** after every ordinary bridge is removed.

**The scope, as the referee reads it.**
- **The theorem's sources:** a ternary seed; at most one two-parent two-fresh join, anywhere; every other join three-fresh, whether
  unary, binary or a three-parent six-place join.
- **The rivals:** any reachable presentation.
- **The structural form:** condition 1 (short shores), condition 2 (an identifying pair at every five- and six-place star) and
  condition 3 (the four-place graph is a cactus).
- **It covers arbitrarily many binary exceptions,** each on two unary four-place children of one four-place site whose two meetings
  are bridges at that moment, so the cycles are separate. It also covers six-place sites with no loose output left.
- **The extension to four-place blocks** that are simple cycles or have at most six junctions rests on `blocks.md` and its local finite
  checks. The referee did not re-derive those.

**Checked.**
- **Exhaustive against every rival at widths 12 to 23** (`referee_i_family.json`). Every type with a family history was tested: 89,
  359, 432 and 2,587 sources at widths 18, 20, 21 and 23, the last with 393 legal-triple holders.
  - Through K = 6: no other type is isometric, and every clipped symmetry keeps the supports.
  - Through K = 5: also no isometric rival and no triple flip in this range. 21 width-23 sources have a clipped symmetry moving a
    support, so junction identity, though not any verdict, already needs K = 6 there. The verdict-changing witness first comes at
    71 distinctions.
- **300 random one-exception sources** (widths 30 to 62; 265 with the exception, 82 with six-place junctions, 117 with legal
  triples): conditions 1 to 3 hold in all 300. The least cut around three or more sites is exactly 7 every time (`referee_i_conditions.json`).
- **The intersecting-cycle family** (1, 2 and 4 repetitions; widths 24, 45 and 87; 3, 6 and 12 two-fresh joins):
  - legal;
  - least cut 7;
  - identifying pairs present;
  - not cacti, with every nontrivial block six four-place sites and eight meetings, as the text says;
  - 3, 5 and 9 legal triples, as stated (`referee_i_blocks.json`).
- **Read; the main reductions checked:**
  - the verification of conditions 1 to 3 in the one-exception family (the monotone boundary, and the forest or single four-cycle);
  - the minimum-weight extra-equation argument: at most half a star, at most two selected bits per site, the |W| = 5 case and the
    forest case;
  - the confinement to one cycle. Its length-four case analysis is consistent; it was not re-derived line by line.

## 4. The seven-to-six lemma (question 4)

**It checks by hand** (`nonshrinking.md`).
- **The boundary changes one site at a time.** Built in birth order, adding a site with p inputs, h outputs and j selected earlier
  neighbours changes the boundary by p + h − 2j.
- **Only one step can shrink it.** This is ≥ −1, with −1 only for a three-parent, two-fresh join whose three parents are all inside.
- **The start is at least seven.** With a single ternary site, the first three selected sites export at least 11 − 4 = 7.
- **So the first boundary of six or less is a step from exactly 7 to 6.** That step consumes three boundary bits and adds two.
- **The six-bit word is a bond.** A split would need two disjoint ternary bonds, and there is only one ternary site.
- **Why one side must take that step.** The within-class reader shows that two sources both free of a light three-site path agree
  entirely through D = 5. So any opposing pair needs one side with a short bond of three or more shore sites. In the single-ternary
  branch, that side must take the step.
- **The control replays:** a three-parent, two-fresh join takes the boundary of the whole prefix from 9 to 8 (`referee_i_shrink.json`).

**Scope.** It is a necessary condition on one side of a hypothetical opposing pair, in the single-ternary branch. It is not a
construction.

## Fixes for the owner (listed, not folded in)

There is one, and it is not a block.

1. **`fixtures.md`'s "62 legal one-junction extensions"** counts named input choices with both fresh counts (22 unary, 40 binary).
   Up to the bit chosen at a holder there are 26 distinct extensions. Saying which count is meant would help.

## How the work was split

- **The referee:**
  - read `decision.md`, `obstruction.md`, `fixtures.md`, `cycle_inverse.md` and `nonshrinking.md` in full;
  - wrote `referee_i.py` (fixtures, w71, family, conditions, shrink, w24) and `blocks_check.py`. They use the referee's 001F-R1
    machinery (census, shore tables, twin-quotient symmetries) and the RING-READ-R1 exact max-flow bond search.
- **Study code** was not imported or run; its JSON files were read as data.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Reproduction

Run from this folder.

| Command | Wall time |
| --- | --- |
| `referee_i.py fixtures` | 1 s |
| `referee_i.py w71` | 1 s |
| `referee_i.py family 23 12` | 4 min |
| `referee_i.py conditions 300` | 2 s |
| `referee_i.py shrink` | under 1 s |
| `referee_i.py w24` | 9 min |
| `blocks_check.py` | 1 s |
