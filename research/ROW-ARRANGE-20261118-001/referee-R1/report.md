# Referee report ROW-ARRANGE-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **Every number reproduces exactly.** The referee used its own populations, readings and canonical forms:
  - every reading's groups and k-mixing groups at seven and eight distinctions;
  - the cheapest growth to twelve;
  - the least local reach (8 and 10);
  - the two failing pairs, rebuilt from the splits the note prints.
- **The proofs hold.**
  - R1, R3 and R5 hold as written.
  - R2 holds, and its condition a, b, c, d ≥ r is tight in the referee's tests.
  - R4 is classical, but its last sentence is misstated (§2).
- **The owner's four flags.**
  - R2's view equality: holds (§1).
  - R3's equitable partition: right (§1).
  - The canonical view form: correct. It gives the same partition as the referee's own form on every view at seven, and is unchanged under 81,144 random relabellings.
  - The families design: described fairly in the table's footnote, but not in the headline (§3).
- **One Narrowing from a replicate.** With 300 other random parents, N1 has two groups at nine that mix k (4 against 3). A 900-parent replicate has one. So "no pair with different orders among those at nine" belongs to the study's sample. **W2 stays complete** on both replicates (54,805 and 162,381 classes).

## What holds

- **The populations** come from the referee's COUNT-BALLS-R1 census engine (`referee_census`):
  - one-split growth gives 1,656 classes at seven and 59,675 at eight;
  - cheapest growth gives 1, 1, 2, 3, 1, 1, 2, 8, 8, 14 classes from four to twelve distinctions.
- **The readings** are written from the note's words, in `referee_rows.py`:
  - a, N1, W2 and WL use shared colour names, one dictionary per round;
  - BW4 is refinement started from each start's view within count 4;
  - B_r uses the referee's own canonical form: refinement inside the view, then every order of the remaining cells, branching when that would be too large.

  | Population | a | N1 | W2 | WL | BW4 | B2 | B4 | B6 | B8 | B10 | Rows distinct |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | One-split, 7 (1,656) | 1,651 / 3 | complete | complete | complete | complete | 43 / 34 | 934 / 183 | 1,649 / 3 | complete | complete | 868 |
  | One-split, 8 (59,675) | 58,985 / 227 | 59,663 / 1 | complete | complete | complete | 86 / 69 | 9,699 / 4,222 | 56,473 / 1,132 | 59,667 / 5 | complete | 35,993 |
  | Cheapest, 4 to 12 | complete | complete | complete | complete | complete | 5 / 2 at 10; 13 / 0 at 12 | complete | complete | complete | complete | 0 |

  - Each cell gives groups / groups mixing k. Every cell equals the study's results.json.
- **The failing pairs** (`referee_rows_pairs.json`), rebuilt from the printed splits:
  - **N1 at eight:** k = λ = 2 against 3, 14 states each. a, N1 and B2 agree; W2, WL and B4 tell them apart.
  - **B6 at seven:** k = 2 against 3, 14 against 12 states. B2, B4 and B6 agree; B8, a, N1 and W2 tell them apart.
- **R0 (the ladder)** is right.
  - a is read from N1 and from W2. N1 is read from W2, since the round-two colour lists every (count, row) pair.
  - Each B_r is read from B_(r+2).
  - B_r at the largest count is the table.
- **R1** is right.
  - A and its complement must both be closed under lying on shortest paths. An edge ab crossing A then forces W_ab ⊆ A and W_ba into the complement. Bipartiteness makes W_ab ∪ W_ba everything, and Djoković's theorem gives the converse.
  - The referee's brute force found the solution set equal to the halfspaces on F(2, 4), F(3, 3), κ(C₆) and κ(P₅).
- **R5** is right: distinct rows name the starts.
  - It covers 52% of the classes at seven, 60% at eight and 78% of the families at nine. On the rest, W2's completeness is computed.

## 1. R2 and R3 (the owner's first two flags)

- **R2's view equality holds, and the condition is the right one.**
  - **Far points.** A point more than r/2 steps from p sees a window of r + 1 points of its ring. Its table is the path's only if every arc of at most r steps is a shortest way round. That needs a ≥ r for every ring.
  - **Points near p.** A point at t ≤ r/2 steps from p sees p and four runs leaving it. One has t + r/2 points and three have r/2 − t. Within them every arc is at most r ≤ a, so the table depends only on t.
  - **The proof's wording.** "Four runs of at least r/2 points leaving p" should describe these lengths. Read as the rings' legs, of at least r points, it is the condition, not the view.
  - **The referee's tests** (`referee_rows_proofs.json`):
    - F(2, 4) against F(3, 3) and F(2, 6) against F(4, 4) agree at B2.
    - F(4, 8) against F(6, 6) and F(4, 12) against F(8, 8) agree to B4.
    - F(6, 10) against F(8, 8) agrees to B6.
    - Each pair differs one step further out. k differs: 4, 6, 8, 12 and 10 against 3, 4, 6, 8 and 8.
  - **One step below the condition, the equality fails.** F(3, 9) against F(6, 6) and F(3, 5) against F(4, 4), both with a = 3 < 4, differ at B4. F(5, 7) against F(6, 6), with a = 5 < 6, differs at B6.
  - **Reading a separates every R2 pair.** So R2's pairs are local-view failures, not refinement failures, as R3 needs for "incomparable".
- **R3's equitable partition is right.** The kinds are the empty set, ten vertices and ten pairs.
  - **The empty set:** 10 vertices at count 2 and 10 pairs at 4.
  - **A vertex:** the empty set at 2, 9 vertices at 4, 2 incident pairs at 2 and 8 others at 6.
  - **A pair:** the empty set at 4, 2 vertices at 2 and 8 at 6, and 2 pairs at 4 (sharing a vertex) and 7 at 8.
  - These numbers are the same in κ(C₁₀) and κ(C₅ ⊔ C₅), because both graphs are 2-regular with every edge meeting two others. The three kinds already differ in their rows, so refinement stops at them.
  - **Recomputed:**
    - a, N1, W2 and refinement over 21 rounds agree, and B2 agrees too;
    - B4 differs (the empty set sees everything within count 4);
    - k = 2 against 3, with λ = 5 for both.

## 2. R4's last sentence (Narrowing, wording)

- **The problem.** "No reading computable in polynomial time determines k on every base unless P = NP" is false as written.
  - The table itself is such a reading, and R0 says it determines k.
  - What the reduction shows is that k cannot be computed from the table in polynomial time unless P = NP.
- **The note's "finding it is as hard as three-colouring" is right.** The sentence in R4 should say the same: "k is a function of the table, but not one computable in polynomial time unless P = NP."
- **The classical parts are right:**
  - simplex graphs of graphs without triangles;
  - three-colouring them is NP-complete;
  - the tree number (Bandelt and van de Vel 1989);
  - λ by a matching (Eppstein 2005).

## 3. The families at nine (the owner's last flag)

- **The design is honest in the table's footnote:** "they show merges that exist, not that none exist". But the calibration at eight overstates the families' reach at nine.
  - **At eight:** the 12 shards sample 25 parents each, independently. The 300 draws hold 278 distinct parents (22 repeats), 17% of the 1,656 classes at seven. Their children are 42% of the classes at eight.
  - **At nine:** the 300 parents are 0.5% of the 59,675 at eight. A parent at eight has about 192 one-split children, and a base at nine has at most nine parents. So there are at least about 1.2 million classes at nine, and the 55,394 are a few percent of them.
  - **The fix.** Say this beside "it does the same on the 55,394 bases reached at nine".
  - **The garbled phrase.** "By growing every child of 300 random bases of eight" should read "every one-split child of 300 random bases at eight".
- **The referee's replicates** (`referee_rows_families_9_300.json` and `_9_900.json`) used its own random parents, other seeds and its own class form (the canonical form of the count table, which determines these bases):

  | Families at nine | Children | Classes | a: groups / mixing k | N1 | W2, WL, BW4 | B8 | B10 | Least reach |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | The study (300 parents) | 57,851 | 55,394 | 55,336 / 14 | 55,385 / 0 | complete | 55,325 / 26 | complete | 10 |
  | Referee, 300 other parents | 57,693 | 54,805 | 54,757 / 26 | 54,799 / **2** | complete | 54,755 / 15 | complete | 10 |
  | Referee, 900 parents | 172,836 | 162,381 | 162,127 / 73 | 162,367 / **1** | complete | 162,211 / 60 | complete | 10 |

  - **N1 fails at nine too.** One of the referee's pairs: bcde|afghi, ceg|abdfhi, bcdfg|aehi, bcdefg|ahi, cdh|abefgi and bcdehi|afg (k = λ = 4) against bcdf|aeghi, cdg|abefhi, ceh|abdfgi, bcdeh|afgi, bcdefh|agi and bcdegi|afh (k = λ = 3), both with 14 states.
  - So the headline's "no pair with different orders among those at nine" is a fact about one sample, and it reads as if N1 recovered at nine. **Narrowing.**
  - **W2 holds on about three times more classes at nine,** and the least local reach is again 10.

## 4. Smaller points (Not a block)

- **What W2's completeness says.**
  - W2 tells every two classes apart, so it determines every property of them. The number of orders is one of them. It does not show how to read k off W2, and nothing in it is specific to orders.
  - **Known, and worth citing once:** a few rounds of colour refinement identify almost every graph (Babai and Kučera 1979; Babai, Erdős and Selkow 1980).
  - **What the study adds:** the thresholds on the program's grown bases, and the proved limits (R2, R3).
- **"So the one round that works on small grown bases works because they are small."** This is an interpretation. R3's pair is not shown to be reachable by growth, and the note's limitations say so. Write "may work because they are small".
- **"One round" and "two rounds."** The note calls W2 one round, and the proof calls it two rounds from equal colours. Both are right, but the note should say once that they are the same thing.
- **The citation for the full table.** R0 in the proof cites DISTANCE-ORDER statement 3(a), which needs N. The note's table cites statement 1. The views carry no N, so statement 1 is the right one.
- **"Every base grown to eight"** means every base the one-split growth reaches. The limitations say so, and the headline should too.
- **BW4.** Its completeness follows from WL's, so P6 adds nothing once P3 holds.
- **The canonical form.** The referee's own first version forgot which distinction is the start and merged 44 of its view classes. The comparison with the study's form caught it. After the fix, the two forms give the same 14,869 classes at seven. The study's form needs no fix.

## Fixes for the thread (listed for the owner, not folded in)

1. **N1 at nine.** Replace "no pair with different orders among those at nine" with "fails at nine too (two pairs in a second sample of 300 parents, one in a sample of 900)". **Narrowing.**
2. **R4.** Rewrite the last sentence as "k is a function of the table, but not computable from it in polynomial time unless P = NP". **Narrowing (wording).**
3. **The families at nine.** Say the 300 parents are 0.5% of the bases at eight. Say the families are a few percent of the bases at nine, of which there are at least about 1.2 million. Say the calibration at eight had 278 distinct parents and 42% coverage. Fix "growing every child". **Not a block.**
4. **R2's wording.** Describe the near-p view as p plus runs of t + r/2 and three of r/2 − t. Name a, b, c, d ≥ r as the condition that makes every arc within the view a shortest way. **Not a block.**
5. **W2 as a complete invariant.** Say that this is what it is, and cite colour refinement identifying almost every graph. **Not a block.**
6. **Small wording.** "May work because they are small". Say once that "one round" and "two rounds" are the same. Cite statement 1 in R0. Name the population in the headline. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs R0 to R6, and `readings.py`, `families.py`, `job.py` and `merge.py`;
  - checked R1 to R5 by hand;
  - wrote `referee_rows.py` (own readings and canonical form, the proofs' families, the failing pairs, the canonical-form test and the replicates at nine) on its COUNT-BALLS-R1 census engine.
- **The study's code** was imported once, to test its `canon_view` against the referee's form. It was not used for any result.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_rows.py`.**
- **`referee_rows_one-split_8.json`:** n = 7 and 8.
- **`referee_rows_cheap_12.json`.**
- **`referee_rows_pairs.json`.**
- **`referee_rows_proofs.json`:** R1 to R3.
- **`referee_rows_canon_7.json`.**
- **`referee_rows_families_9_300.json` and `_9_900.json`.**

Reproduce, from `research/ROW-ARRANGE-20261118-001/referee-R1/` (`REFEREE_POP_CACHE` optional, a folder that caches the
populations):

```sh
../../../.venv/bin/python -B referee_rows.py census one-split 8 8 > referee_rows_one-split_8.json
../../../.venv/bin/python -B referee_rows.py census cheap 12 4 > referee_rows_cheap_12.json
../../../.venv/bin/python -B referee_rows.py pairs > referee_rows_pairs.json
../../../.venv/bin/python -B referee_rows.py proofs > referee_rows_proofs.json
../../../.venv/bin/python -B referee_rows.py check_canon 7 > referee_rows_canon_7.json
../../../.venv/bin/python -B referee_rows.py families 9 300 1 8 > referee_rows_families_9_300.json
../../../.venv/bin/python -B referee_rows.py families 9 900 2 14 > referee_rows_families_9_900.json
```
