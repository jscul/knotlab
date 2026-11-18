# Referee report MEET-ORDERS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - Lemmas 0, A, B and C and Theorem 1 hold. The referee checked them by hand, including the owner's three points.
  - The referee's own engine, which does not import `melib.py`, reproduces every census value it was asked about:
    - Theorem 1 on every bracketing of 4 to 9 distinctions, and on samples at 10, 11 and 12 (one size past);
    - the five-starts at n = 9 to the last digit;
    - the n0 = 8 tie at n0 + 4;
    - the six-starts' labelled counts.
  - The correction to KNOT-CAP agrees with the referee's own KNOT-CAP numbers.
- **What changes.**
  - **The post hoc meeting-pattern reading, one size past (n0 = 8, to n0 + 3).**
    - Its first half holds: every meeting pattern has one signature, 12 of 12.
    - Its second half fails at that depth: 12 patterns give only 8 signatures.
  - **A100 is material.** One redundant knot moves the five-starts' chance at n = 7 off 5/12 and 11/18, and the placements no longer
    sort by bare bracketing.
  - **"The knots nest" as the reason.** It is proved for the second new distinction and computed through the third, and the
    intuition entry should say so.
  - **Two small points in the proof of Lemma B.**

## What holds

- **Lemma 0, both directions (the owner's point 2).**
  - **(1) and (2).** They are right: the state with only c at 1 is ruled out only by a knot with middle c, so |K| ≥ n − 2.
  - **(3), every bracketing presents the line.** The induction on monotone halves is right.
  - **(4), the converse.**
    - *The cycle case.* X is the closure of the cycle under "both outer distinctions in X". The state 1 on X is allowed:
      - cycle members agree with their successor;
      - added members agree with both outer distinctions;
      - every other interior c has an outer distinction outside X, so 0 is among its values.

      Both ends lie outside X, and X is not empty, so this state is not a line state. Hence the arrows have no directed cycle.
    - *The rest.* A source c appears only in κ_c, so dropping it leaves a presentation of the line of n − 1. If a_c ≤ c − 2, the
      prefix state 0..a_c with x_c = 1 breaks the line, so κ_c = (c − 1, c, c + 1). The induction closes.
- **Lemma A.** The first step's options are the n − 2 fills, one knot set each. It is confirmed in every run below.
- **Lemma C (the owner's point 3).**
  - **The matching argument.** A matched pair {X, Y} of sides with X ∪ Y = everything gives comp(X) ⊂ Y. Paths of matched pairs are
    nested chains, with no cycles since the inclusions are strict, and a chain of L splits gives L − 1 pairs. So
    λ = splits − matching = the least number of chains.
  - **It is the program's λ.** This is Eppstein's formula as STATE-RULES's `lattice_dimension` and the referee's own KNOT-CAP-R1
    `measure` compute it.
  - **The two-order criterion.** It follows: steps k < l cross exactly when a fill holds them in different halves. A middle strictly
    inside another fill's span, other than its own middle, gives three pairwise crossing steps. Otherwise the parity colouring of
    steps gives two chains.
- **Lemma B: compression, pull-back and the finite check (the owner's point 1).**
  - **Compression.** Every pin of a knot on a pair (x, y) is constant between consecutive positions of P. That includes pairs with
    q, whose agreement with a line distinction s changes only at a, c, b and s. So compatibility, covering, irredundancy, cost and
    "not a copy" are statements about segments.
  - **Pull-back.** The used line pairs are chords of the triangulation, and they stay non-crossing after compression, so they extend
    to a bracketing T′. Pairs with q are (q, a), (q, c) and (q, b), which compression keeps. And three pairwise co-knotted
    distinctions of a bracketing form one of its knots.
  - **The finite check M1** (`classify_second_step`). It takes every knot set that `moves` admits: 1 to 3 knot-local knots, pairwise
    compatible, irredundant, constrained, no copy, using the same semantics as the referee's KNOT-CAP code. It keeps the cheapest and
    asserts that their cost is 0. Every one is then classified F or E, none "other". There is one F per other knot, and exactly two E
    per knot sharing a pair, with the stated odd sets and verdicts. So it enumerates every zero-cost knot-local set, as claimed.
  - **One small gap, now checked.** When a = 0, b = m and the set uses only κ's and q's pairs, the compressed line has three
    distinctions, but M1 starts at n0 = 4. The referee ran the line of three: after its first fill, the cheapest second step costs 2
    (40 options), so it has no zero-cost option and nothing is missed. The proof should say so.
  - **A wording point.** "As chords of the polygon they do not cross" should exclude q's pairs, which are not chords.
- **Theorem 1, fresh (`referee_meet.py thm1`).** The referee computed the exact chance of two orders after the second new
  distinction with its own engine, and Theorem 1's formula from its own reading of s, p and c. They agree:
  - on every bracketing of 4 to 9 distinctions (624);
  - on 200 random bracketings each of 10 and 11 distinctions, and 120 of 12.

  The study's M1 ran every bracketing to 11.
- **The five-starts, exact (`five`, the owner's point 4).**

  | n | End | Next to an end | Middle |
  | --- | --- | --- | --- |
  | 6 | 1 | 1 | 1 |
  | 7 | 5/12 | 5/12 | 11/18 |
  | 8 | 173/6552 | 173/6552 | 233/2457 |
  | 9 | 1810423/995045688 | 163213/181890072 | 985399/81070416 |

  - The whole distribution of λ is equal for the end and next to an end through n = 8, and they first differ at n = 9. The middle
    differs from n = 7.
  - Every value equals the study's. All three have 6,752 labelled bases at n = 9.
- **The n0 = 8 tie (`tie`).** (x,((x,(x,x)),(x,(x,x)))) and (x,(((x,x),x),((x,x),x))) have identical λ distributions at every n
  from 8 to 12 (n0 + 4), with 34,520 labelled bases each at 12.
  - **Controls.** Two other pairs with one bare bracketing (a chain against its one-step variant, and the same with a leading step)
    differ at n0 + 4, as Q4 expected generally.
- **The six-starts (`extra`).** With this engine they have 13,368 and 13,364 labelled (S, G) bases at n = 10, as stated. Their
  two-order chances are 51/140 at 8, 9409/339822 at 9, and at 10 the KNOT-CAP-R1 values.
- **The correction to KNOT-CAP (the coordinator's question).** The referee's KNOT-CAP numbers give the five-starts two orders with
  probability 1 and 1 at n = 6, and 5/12 against 11/18 at n = 7. So "from the second new distinction" is right, and the logged
  Narrowing ("Not a block") is right.

## 1. The meeting-pattern reading, one size past (owner's least sure; Narrowing of a post hoc reading)

- **The reading.** For n0 = 5 to 7, the labelled-base counts and the mass by largest odd set at each level depend exactly on the
  meeting pattern: the knots and distinctions as an abstract incidence, up to renaming. And each pattern has its own values.
- **One size past (`meet`, n0 = 8, to n0 + 3 as for n0 = 7).** 66 presentations up to mirror fall into 12 meeting patterns.
  - **Within a pattern: holds.** Every one of the 12 groups has a single signature. This is the half that says the meeting pattern
    decides the branching.
  - **Between patterns: fails at this depth.** The 12 patterns give only 8 distinct signatures, and 4 coincide with another
    pattern's. "Each meeting pattern has its own values" holds through n0 = 7 but not at 8 to n0 + 3. Deeper levels might still
    separate them; that was not run.
- **What it means for direction #1.** Freeze the "decides" half as the prediction. The "own values" half needs a depth, or should
  be dropped.

## 2. A100: the fewest-knot population hides how redundant knots act (owner's least sure; Not a block, but material)

- **The test.** A betweenness knot (a, c, b) with a < c < b holds on every line state, so adding one keeps the states but adds
  co-knotted pairs, which KF3 reads. The referee added each of the 7 missing knots, one at a time, to each five-start (`extra`).
- **The chance of two orders at n = 7:**
  - end (fewest-knot 5/12): 57/100 (twice), 29/63, 371/600 (twice), 515/882, 365/588;
  - next to an end (5/12): 57/100 (twice), 14/25 (twice), 1523/2352, 365/588, 31/42;
  - middle (11/18): 1523/2352 (twice), 371/600 (four times), 16/21.
- **So one redundant knot changes the chance in every case**, by 0.04 to 0.33.
  - The end and next to an end no longer agree.
  - Values cross between the chains and the middle: 371/600 and 1523/2352 occur on both sides.
- **The consequence.** The bracketing account is a statement about fewest-knot presentations, as A100 and the Limitations say.
  Where more knots than needed are present, how they meet is more than the bracketing.
- **The fix.** Add this to A100 as a first challenge result: "one redundant knot changes the second-step chance in all 21 cases
  tried, and mixes the placements".

## 3. "The knots' nesting is the reason" (the coordinator's question; Not a block, wording)

- **Proved.** At the second new distinction, Theorem 1 gives the chance of two orders exactly from s, p and c: which knots are
  step-disjoint, held and holding. That is the bare bracketing, so nesting is the reason there, proved for every n.
- **Computed.** Through the third new distinction, the bare bracketing decides the whole distribution, for every presentation of 5
  to 9 distinctions. The referee confirmed this for the five-starts and the tie pair, but it is not proved.
- **Neither.** From the fourth new distinction, the order of the halves enters ("same way / other way") and ties appear (one pair at
  n0 = 8, 24 at 9). So "nesting" is not the whole reason there.
- **The fix.** The intuition entry's "Because the knots nest … Through three new distinctions only that nesting matters" should
  mark the second clause "computed, 5 to 9 distinctions". The note already labels it.
- **For KNOT-CAP's five-starts.** Nesting explains the difference at n = 7 (proved) and n = 8 (computed). The parting of the end
  and next to an end at n = 9 is the halves' order.

## 4. Literature, per John's folklore direction (the owner's point 5)

- **Known, cited once.**
  - Triangulations, bracketings and binary trees (Catalan).
  - Rotations and the Tamari lattice (Sleator, Tarjan and Thurston, 1988).
  - Lattice dimension (Eppstein, 2005).
  - In phylogenetics, every rooted binary tree on n leaves is defined by a set of n − 2 rooted triples, and all minimal defining sets
    have that size. This is Steel's result, characterised by Grünewald, Steel and Swenson (2007, closure operations); see the
    discussion in [arXiv 1707.01667](https://arxiv.org/abs/1707.01667) and the induction in
    [arXiv 1710.08946](https://arxiv.org/abs/1710.08946).
  - The count n − 2 is the same as Lemma 0's, but the object differs. There one tree has many minimal defining triple sets. Here one
    line has many minimal presentations, and they are exactly its triangulations.
- **What differs from the order literature.** Lemma 0 is about the *states* (cuts), not order.
  - In the order-theoretic betweenness problem (Opatrny, 1979), the n − 2 consecutive triples (i, i + 1, i + 2) already fix the
    order up to reversal.
  - In the program's semantics they do not present the line: for four distinctions, B(0,1,2) and B(1,2,3) allow the state 0110.
  - Presentations must be nested under the ends' knot. That is the triangulation condition.
- **Not found.** Two searches found no source stating that the fewest betweenness presentations of a line's cuts are the
  triangulations. Lemma 0 is "proved here, not found in the literature so far", as the pre-registration says.
- **The perspective's addition.** The states hold the line, and how its knots meet is a triangulation that the states do not show.
  KF3 reads that triangulation through co-knotted pairs.
- **Specific to the program.** Theorem 1's formula is about KF3 and is new as far as the searches show.

## 5. Smaller points (Not a block)

- **"Same way / other way".** The definition (χ within ν within π; whether χ sits in ν at the end ν shares with π) is clear, and it
  matches the bracket strings. Keep it.
- **Q8's failure.** It is reported correctly. Its replacement is post hoc (§1).
- **The chain as the least for every n.** This is computed to 13 only, as stated.

## Fixes for the thread (listed for the owner, not folded in)

1. **The meeting-pattern reading.** Within a pattern it holds one size past (12/12 at n0 = 8 to n0 + 3). "Each pattern has its own
   values" fails there (8 signatures for 12 patterns). **Narrowing** (of a post hoc reading).
2. **A100.** A redundant knot changes the second-step chance in 21 of 21 cases and mixes the placements. Record it in A100.
   **Not a block.**
3. **The intuition entry.** Mark "through three new distinctions only that nesting matters" as computed (5 to 9). **Not a block.**
4. **Lemma B's proof.**
   - Add the line-of-three case: no zero-cost second option, checked.
   - Say that q's pairs are not chords.

   **Not a block.**
5. **Literature.** Cite Steel and Grünewald–Steel–Swenson for the n − 2 count. Note that Lemma 0 differs from order-theoretic
   betweenness, where consecutive triples suffice. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `melib.py` (`moves`, `canon`, `classify_second_step`), `job.py`,
    `posthoc_meeting.py` and the outputs;
  - checked Lemmas 0, A, B and C by hand;
  - wrote its own KF3 enumeration (vectorised over the third knot), bracketings, random bracketings, Theorem 1's s, p and c, odd
    sets, signatures and incidence grouping (`referee_meet.py`), reusing `measure` and `base` from its KNOT-CAP-R1 code;
  - searched the literature.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_meet.py`**, with parts `thm1`, `five`, `tie`, `meet` and `extra`.
- **Outputs:** `referee_meet_<part>.json`.

Reproduce, from `research/MEET-ORDERS-20261118-001/referee-R1/`:

```sh
for P in thm1 five tie meet extra; do ../../../.venv/bin/python -B referee_meet.py $P > referee_meet_$P.json; done
```
