# Referee report BOND-NEXT-JOIN-R1 (fresh code, no Codex)

**Verdict: Confirmed. No Block, no correction.** Three framing points for John's summary.
- **What holds.**
  - The theorem is proved for every finite stage. The referee checked the proof line by line: the bipartite and triangle-free
    growth, the bound of seven for three or more junctions, the minimality of single and adjacent-pair cuts, and the reader's
    induction.
  - The census is confirmed one size past in the referee's own code. It enumerated legal assemblies up to renaming:
    - 1, 1, 2, 6, 21, 89, 432 patterns through seven junctions (552 in all, as stated), and 2,334 at eight;
    - every bond distance computed with no lemma, from every sum of junction equations;
    - the reader returns every junction exactly on all 2,886 patterns;
    - distinct patterns have distinct tables;
    - 489 patterns through seven are blocked for the simultaneous round, as stated;
    - the two worked examples give 5 and 2, and 3 and 3.
- **The framing points.** None is an error in Codex's files.
  - **What the reader is told.** It is told the growth law. The law's arity, three fresh bits and at most three parents, is what
    makes the numbers six and five work. Distances supply the rest: which bits meet at which junction.
  - **How it relates to Whitney.** It is not a corollary of Whitney. It uses much less input, one thresholded number per pair, but
    only for this class of growths. Its last step is classical: stars are the maximal cliques of a triangle-free graph's line graph.
  - **For A97.** This is a genuine positive case. For this law, the bond-distance table alone, unnamed and pooled above five,
    determines the junctions, hence the allowed states and every next step. That holds with the law given. It does not hold for the
    disagreement count, which carries nothing here. And it is not shown for the mixed system that keeps the original cube.

## What holds

- **The proof (the claims' point 4).**
  - **The growth is simple, bipartite and triangle-free.**
    - A new junction takes one bit from each distinct parent.
    - Parents pairwise share a neighbour, so they lie in one part.
    - The new junction goes in the other part.
  - **Short sums.** Take any set U of at least three junctions, and its last three in a serial history. Their nine outputs can be
    consumed inside U only by a later one of the three. That is at most two bits, since three vertices with no triangle have at most
    two edges. So |∂U| ≥ 7.
  - **Every bond of size at most six** is therefore one star (3 to 6 bits) or the cut of two adjacent junctions (|S| + |T| − 2).
    Both are minimal, since deleting one or two junctions leaves every other junction connected to the outside along its outputs.
    Two non-adjacent junctions give a disjoint union, which is not minimal.
  - **The reader.**
    - At thresholds k = 3 to 6 it links the pairs at distance at most k − 1.
    - It removes the cross pairs of already-recovered adjacent stars whose joint cut has size at most k. A cross pair cannot share
      a star, or it would close a triangle.
    - It reads the maximal cliques of size at least three. Two linked bits share exactly one junction, and a third bit linked to
      both meets it there (no triangle), so the cliques are exactly the stars.
  - **What it uses.** Only the comparisons with 2, 3, 4 and 5.
  - **The bounds, reachable.** The reachable bound is 7, while two adjacent junctions can reach 6 + 6 − 2 = 10. So the threshold
    order is what lets the reader set aside two-star bonds of size up to 6.
- **Proved for every size, or a census? (the coordinator's question).** Proved for every finite stage of every legal serial
  assembly, and so for complete rounds. The census is a check, not the proof.
- **The census, recomputed (`referee_next.py`).**
  - **Enumeration.** The referee's own enumeration applies every legal move (one loose bit from each of one, two or three
    junctions; pairwise common neighbours; for three, none common to all) to every pattern. It dedupes by isomorphism of the
    junction–bit incidence, loose bits included, with a WL hash and then VF2.
  - **Bond distances.** For each pattern they are computed exactly: every nonzero sum of junction equations, the inclusion-minimal
    supports, and the least one through each pair.

  | Junctions | Patterns (distinct up to renaming) | Reader exact | Distinct tables (above 5 pooled) | Simultaneous round blocked |
  | --- | --- | --- | --- | --- |
  | 1–4 | 1, 1, 2, 6 | all | 1, 1, 2, 6 | 0 |
  | 5 | 21 | 21 | 21 | 8 |
  | 6 | 89 | 89 | 89 | 77 |
  | 7 | 432 | 432 | 432 | 404 |
  | 8 | 2,334 | 2,334 | 2,334 | 2,204 |

  - Through seven these are 552 patterns and 489 blocked, as stated. They are **distinct patterns, not descriptions**: each is a
    junction–bit incidence up to renaming.
  - The worked examples, read from the recovered stars, have twelve distinctions and 2⁸ = 256 states. The chain of four gives 5
    single and 2 two-parent joins. The seed with three children gives 3 and 3.

## 1. What is read and what is given (the coordinator's question)

- **Given.**
  - The growth law: even parity, three fresh bits, one to three parents with the common-neighbour tests.
  - That the system was grown by it.
  - The reader's correctness rests on three consequences of the law: junctions of 3 to 6 bits, |∂U| ≥ 7 for three or more, and no
    triangles. These fix the thresholds 3 to 6, and so "five".
  - In CUBIC-FROM-A-KNOT the law's arity put in the "three". Here the same arity puts in the "six" and the "five".
- **Read from distances.** Which bits meet at which junction, which bits are loose, and which junctions neighbour each other. From
  these the law gives every next join.
- **Against Whitney.**
  - Whitney's theorem recovers the junction graph from the whole state set, for any 3-connected graph.
  - This reader uses far less input, one number per pair thresholded at five, but only for this class: triangle-free graphs whose
    short sums are large.
  - So it is a different and more economical recovery, not a corollary.
  - Its last step is classical. In a triangle-free graph, the maximal cliques of size at least three of the line graph are the
    stars (Whitney's line-graph theorem, 1932; Krausz, 1943). Steps 1 and 2 build the line graph from bond distances.

## 2. A97 (the coordinator's question)

- **A positive case.**
  - For the pure parity rule, the table of bond distances alone (no names, no history, everything above five pooled) determines the
    junctions.
  - So it determines the allowed states: impose even parity on the recovered stars.
  - And it determines every next step.
  - Within this family no two bases with equal tables differ in states or in next joins. That is the converse of A97's challenge.
- **The scope.**
  - The growth law is given to the reader.
  - The distance is bond distance. The disagreement count is flat here (every pair free; CUBIC-R1).
  - The result holds only for this designed parity law.
  - It is the opposite of DISTANCE-INFO's finding for not-all-equal bases, where pairwise bond distance fails at four
    distinctions.
  - The mixed system, which keeps the original betweenness cube, is open. The reader fails at its first threshold, as Codex says.
- **A contrast with MEET-DIST.** There the unnamed disagreement tables of KF3 growth lost part of the nesting. Here the unnamed
  bond-distance table of parity growth loses nothing. The two laws differ in which ruler carries their structure.

## 3. Known mathematics, per John's folklore direction

- **Cited once.**
  - Cut–cycle duality, with bonds as the cocircuits of the cycle matroid.
  - Whitney's 2-isomorphism theorem (the full-state recovery).
  - Whitney's and Krausz's line-graph results (stars as the maximal cliques of the line graph of a triangle-free graph).
- **New, as far as the referee knows.** The program's bond distance, thresholded at five, yields that line graph for this growth
  class, after removing the two-star artefacts. And the reader commutes with renaming, so it predicts every legal next join.

## Fixes for John's summary (none to Codex's files)

1. Say the reader is told the growth law, and that the law's arity sets the thresholds (six bits, five).
2. Say it is a positive case for A97 in the bond-distance reading, for this law. The mixed system stays open.
3. Optional: name the line-graph step as classical.

## How the work was split

- **The referee:**
  - read the note, the pre-registration and the proof;
  - wrote its own enumeration of legal assemblies up to isomorphism, exact bond distances by every sum of junction equations, the
    reader from the proof's text, the parallel round, and the worked examples (`referee_next.py`).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_next.py`** and **`referee_next.json`.**

Reproduce, from `research/BOND-NEXT-JOIN-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_next.py 8 > referee_next.json
```
