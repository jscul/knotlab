# Referee report VARIABLE-OUTPUT-READER-001D-R1 (fresh code, no Codex)

**Verdict: Confirmed. No Block.**
- **The separator converse holds:** it is checked by hand, and it held in 474,973 fresh separator tests one size past.
- **The pruning rule's two directions check.**
- **The width-32 example recomputes exactly from scratch.**
- **The open case is not settled, but its within-table form survives a targeted search past the study.**
  - The search covered 158 presentations of widths 34 to 38 that have legal triples and a table symmetry that loses a parity equation.
  - None of their 198,208 symmetries moves a legal triple to a forbidden one.
- **One wording point.** The decision note's "every finite arrangement of the parity growth law" should say the *serial* law. The
  proof's own statement does.

## 1. The separator converse: scope and proof (question 1)

**What is proved.**
- For every presentation reachable under the study's serial law, at every finite size, and every distinction t: the components of the
  links D(x, y) ≠ D(x, t) + D(t, y) − 1 are exactly the parts of the ordinary incidence after deleting t.
- The serial law is: a three-place seed; each join takes one loose distinction from 1, 2 or 3 distinct junctions (pairwise common
  neighbours, none common to all three) and adds 2 or 3 fresh distinctions.
- It is a structural proof, not a census.

**Under which growth.**
- **Mixed counts:** yes, any mix of 2 and 3 fresh distinctions.
- **It is not A104.** The serial law allows any legal join at any time.
  - It contains the complete-round patterns with one count of 2 or 3 (those joins have at most three parents).
  - It does not contain FRESH-COUNT's fewest rule (tops with one or no fresh distinction) or counts of four or more.
- **It is not about every parity presentation.** The study's own control shows two presentations with identical 29-distinction tables,
  one with t a separator and one without. The second needs a degree-8 junction, beyond the law.
- So the proof uses the law's degree bounds (3 to 6), its two fresh outputs per junction and its three-parent rule. That is what it
  should do.

**The proof, checked by hand** (`separator.md`):
- **Stars are bonds.** Each other vertex follows an output to the outside, because at most one output goes to the removed vertex.
- **Shortest bonds through t, y stay in y's component.** For z in the bond, c(y, z) − 2 ≤ w(y) < w(y) + w(z).
- **Short-cut bounds:**
  - with three or more selected vertices, at least four outputs leave;
  - a 3-bond is a trivalent star;
  - at a vertex of degree ≥ 5, no cut of size ≤ 4 holds both an input and an output;
  - a three-fresh vertex has at most two outputs with c(t, y) ≤ 4.
- **The mixed-star analysis.**
  - It reduces to a three-parent vertex with one exceptional bit of weight 1 going to a trivalent endpoint of t.
  - With t in the star, degrees 3 to 6 fall to inequality (1) and the opposite-direction weight-3 bits.
  - With t outside, there is at most one weight-1 bit (bipartite, simple), and degrees 4 to 6 fall the same way.
- **Both orientations are excluded.**
  - **v → u:** three edge-disjoint p-to-v paths, plus t, plus two outputs of U's last vertex, give six bits. For the 6-star with
    v ∈ U there is the extra old crossing on the witness path.
  - **u → v:** the four-cycle u, r, z, v. Here z has no weight-1 bit, and r's only candidate is excluded both ways.
- **The physical-to-scalar direction** uses 001C's one-distinction gluing formula. That formula was cited, not re-refereed here.

**Fresh code, one size past** (`referee_reader.py`). The test was run at every distinction of every presentation:

| Population | Presentations | Separator tests | Genuine separators | Mismatches |
| --- | --- | --- | --- | --- |
| Random, uniform over legal moves, widths 21 to 34 | 6,000 | 165,211 | 21,742 | **0** |
| Random, biased to joins, widths 21 to 34 | 6,000 | 165,720 | 5,995 | **0** |
| Continuations of the study's width-20 source, widths 22 to 34 | 4,000 | 115,440 | 2,206 | **0** |
| Continuations of the width-32 presentation, widths 34 to 38 | 800 | 28,602 | 144 | **0** |

- The study's exhaustive controls were at widths 19 and 20, with the 27/28 pairs.
- These are random, not exhaustive, but they run past every width the study checked.

## 2. The pruning rule's two directions (question 2)

- **A legal triple always survives.**
  - Its three parents and three distinct pair witnesses form a simple six-cycle. The witnesses are distinct because a repeated witness
    would be common to all three.
  - Deleting one shared distinction leaves a path, so the parents stay together.
  - A loose mark is never an ordinary separator.
- **For a surviving triple, eligibility in the retained part equals eligibility in the source.**
  - The marks' looseness and parents are unchanged.
  - Every common witness of two parents of the part lies in the part, since otherwise the path inside plus the two links would be a
    cycle across a bridge. The same holds for a witness common to all three.
  - So both the pairwise witnesses and the absence of a common witness transfer, in both directions.
- **The order matters.** A cut shared distinction looks loose in the retained part, so marks must be screened first: reject any
  triple containing a separator or straddling one. The study's 3,101 counterexamples to the reversed order show this.
- **Both directions are correct.**

## 3. The width-32 example, recomputed (question 3)

From the junction supports in the study's certificate (data only), with the referee's own code (`referee_reader_w32.json`):

| Claim | Referee |
| --- | --- |
| The 15-junction history is legal under the serial law | yes, every step |
| Pairs | 496 (distances 2 to 10) |
| The transposition (13 14) preserves every entry | **yes, all 496** |
| The six-place equation {11, 12, 13, 17, 18, 19} lies in the dual | yes |
| Its image {11, 12, 14, 17, 18, 19} lies in the dual | **no**: the swapped relation allows a state the true one forbids |
| Legal triples | **8**: one of {26, 27} × one of {28, 29} × one of {30, 31} |
| Order of the table's automorphism group | **384** |
| Automorphisms keeping the 8 legal triples | **384 of 384** |
| Automorphisms losing a parity equation | 192 of 384 |
| Separating distinctions; separator test | none; no mismatch |

The example is exactly as stated. The table forgets a six-place equation, and still every one of its symmetries keeps the verdicts.

## 4. The open case, one size past (question 4)

- **The question.** Can a scalar isometry that changes the allowed-state relation move a legal marked triple to a forbidden one? This
  can happen within one table, or between two histories with the same table.
- **It is not settled here.**
- **The within-table form**, probed past the study with every automorphism of each table (capped at 50,000):

| Population | Presentations with legal triples | … that also have an equation-losing symmetry | Automorphisms checked | Moving a legal triple to a forbidden one |
| --- | --- | --- | --- | --- |
| Random, uniform | 303 | 0 | 7,495,072 | **0** |
| Random, biased to joins | 618 | 0 | 1,530,850 | **0** |
| Width-20 continuations | 32 | 0 | 448,004 | **0** |
| **Width-32 continuations (widths 34 to 38)** | 172 | **158** | 198,208 (91,376 equation-losing) | **0** |

- **The fourth row is the open case's within-table form.** It covers 158 presentations, one and two joins past the width-32 example,
  where a table symmetry loses a parity equation and there are legal triples. No symmetry changes a verdict.
- **Gaps:**
  - 14 uniform-random presentations had automorphism groups beyond the cap and were checked only partially.
  - **The form between histories is not probed here**: two different presentations with isometric tables. The study's exhaustive
    comparison at widths 19 and 20 (1,429 legal marked classes) covers it there, and was not recomputed.
- **What would settle it.** A proof that every scalar isometry carries the three parents and their witnesses, or a census of marked
  canonical forms across all reachable presentations at one width past 20. The second is feasible but costly: the width-21 population
  is several tens of thousands of types.

## 5. Other points

- **Relation to FRESH-COUNT's T6.**
  - T6 proved distance-only reading only for one count.
  - This study proves the separation part for mixed counts of 2 and 3 under the serial law, at every size.
  - It proves a full uniform inverse for the subclass with at most one two-fresh junction, which needs at least two parents. The
    referee read that argument: any four sites have at least seven boundary bits, and the three-site equality case is impossible.
  - The general triple reading remains open.
- **Theorem 2** (equal allowed-state relations preserve the menu, `inverse.md`) was read.
  - The 3-connected torso argument, with the Whitney-type identification of stars from cycles and ranks, is plausible.
  - It rests on 001C's alternating-count and common-prefix results, which this referee did not re-referee.
  - **Not checked in full.**
- **The width-22 counterexample to the distance-four bit** was not recomputed.
- **The table-only certificate** (2,167 populations) was not recomputed.
- **Novelty:** unassessed, as stated.

## Fixes for the thread (listed for the owner, not folded in)

1. **The decision note's first line.** Write "every finite arrangement reachable under the serial law (one to three parents with the
   witness rules, two or three fresh distinctions)". The theorem fails for general parity presentations, by the study's own
   degree-8 control. It does not cover FRESH-COUNT's fewest rule or counts of four or more. **Not a block (wording).**
2. **The open case.** Cite the referee's within-table search as evidence past the study: 158 presentations of widths 34 to 38 with
   legal triples and equation-losing symmetries, and no verdict changed. Keep the case between histories open. **Not a block.**

## How the work was split

- **The referee:**
  - read the decision note, the pre-registration, `proof.md`, `separator.md` and `inverse.md`, and the width-32 certificate;
  - checked the separator proof (both orientations) and the pruning rule by hand;
  - wrote `referee_reader.py`:
    - the serial law;
    - the dual space and bonds by GF(2) enumeration with minimality;
    - the scalar separator test against physical deletion;
    - legal triples;
    - the table automorphisms with a refinement and backtracking search;
    - an equation-loss test for each symmetry;
    - the four search populations.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_reader.py`.**
- **`referee_reader_w32.json`, `_random.json`, `_cont.json` and `_cont32.json`.**

Reproduce, from `research/VARIABLE-OUTPUT-READER-20261118-001D/referee-R1/` (about five minutes on 16 workers):

```sh
for p in w32 random cont cont32; do ../../../.venv/bin/python -B referee_reader.py $p > referee_reader_$p.json; done
```
