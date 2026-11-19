# Referee report RING-CORES-001-R1 (proof read line by line; own words, formula, brute-force clusters and growth)

**Verdict: confirmed. Lemma 1, Lemma 2, Theorems 3 and 4, Corollary 5 and Proposition 6 are correct. "Exactly" is earned in both
directions. No Block. One Narrowing of wording, on the scope of the golden-ratio ceiling.**

## The points asked

- **Theorem 3, the cluster description and orbit count: correct.** Not a block.
  - **The cover.** A piece's incidence graph has one cycle, its ring of blocks; leaves and spares hang as trees. So the universal
    cover is the decorated bi-infinite line, with the deck group shifting by n.
  - **Line points form an interval.** Removing a line point x_k cuts the cover in two: the leaf of (x_{k−1}, x_k) falls on the left
    and the leaf of (x_k, x_{k+1}) on the right. So the line points of a connected set form an interval.
  - **Clusters without a line point** are one leaf with any of its spares.
  - **Clusters on an interval [i, j]** take any spares of its points and any of the j − i + 2 leaves in the blocks meeting it, each
    with any of its spares. That gives the weight λ_{i−1} Π_{k=i}^{j} v_k.
  - **The orbit count.** The shift acts freely, and one representative per orbit has its leftmost line point in {0, …, n − 1}.
    Writing j = i + m + qn gives the geometric series in W.
  - **Brute force agrees.** The referee counted every connected set of points holding a knot directly on the unrolled cover, one
    per orbit, with its own enumeration. On every word of 5 to 9 knots (454 words, to round 7) it equals the formula.
- **The even-ring piece rule: correct.** Not a block.
  - **The rule.** A leaf of c_i sits in the block N(c_i) with c_{i±1}, so it joins the walk of the opposite parity. A spare hangs
    on its own knot.
  - **Checked on the referee's own relayed map** of every one of the 23,098 words: each hung knot's component holds only core knots
    of the opposite parity (on even rings) and contains both of c_i's neighbours. Every spare lies in its own knot's component,
    with no ray.
- **Theorem 4, the dominant root: correct.** Not a block.
  - **One root in (0, 1).** W has non-negative coefficients, W(0) = 0, and W(1) > 1 unless the piece is bare. So W = 1 has one
    simple root ρ there.
  - **No other root of that modulus.** A non-bare W has terms of degrees n and n + 1. On |z| = ρ, |W| = 1 forces z^n and z^{n+1}
    to point the same way, so z = ρ.
  - **No cancellation.** The numerator has positive coefficients, so the pole at ρ is simple with a positive residue.
  - **The bare case** collapses to nz/(1 − z).
  - **Checked against growth.** The referee's growth equals the formula on every round of every grown word: 3,132 words, 44,532
    rounds, every word to 10 knots and one in ten above.
- **Proposition 6, the golden-ratio ceiling: correct as stated, for ring starts in the class with every knot live.** Not a block.
  - **The factors.** At z₀ = 1/φ a spared line point gives 1 and an unspared one gives z₀. A hung knot with its two flanking line
    points gives z₀²(1 + z₀(1 + z₀)^b) ≤ z₀²(2 + z₀) = 1, with equality only at b = 2.
  - **The flanking pairs are disjoint,** since hung knots are at least three apart, and no line point flanks two.
  - **Checked exactly**, in Q(√5), on all 39,155 pieces of the 23,098 words: W(1/φ) ≤ 1 everywhere. Equality holds on exactly the
    208 pieces the proposition names, the second option only on even rings.
  - **The fastest rate is φ at every length from 5 to 14.**
  - **"At any length" holds for the ring of five.** Every knot plain with a spare (five places each) is in the class, and its single
    piece has W = (z(1 + z))^5. Its rate is φ.
- **"Exactly" is earned in both directions.**
  - **The shape list is complete under the cap.** Lemma 1's counts are right: p_c ≥ 4 + ℓ_{c−1} + ℓ_c + ℓ_{c+1}, and the open
    ranges follow from (S0) and p ≤ 5. A leaf cannot touch twice.
    - **The referee's check:** every connected graph to 14 knots meeting the cap study's conditions whose core is a cycle (36
      graphs, from its own CAP-CHAINS-R1 enumeration), under every assignment of open counts (42,911 all-live simple starts),
      read by its own classification.
    - **The result:** every one is in the class and is a word. The words met are exactly the 6,908 words with at most 14 knots,
      no more and no fewer.
    - **Its own enumeration of the words** gives the study's counts at every length: 17, 60, 129, 248, 543, 1,128, 2,551, 5,588
      and 12,834.
  - **The converse, by growth rather than by classifier.** The study's K6 reads the starts with DOUBLE-IDENT's `dims.predict`. Its
    "exponential" comes from the same structural reading of cycles that the proof formalises, so K6 checks that two structural
    readings agree, not that the starts grow so. The referee instead grew every in-class simple start of 2 to 9 knots on those
    graphs with its own engine:
    - every ring core equals the referee's formula on every round, bare ones constant and decorated ones exponential by Theorem 4;
    - every path or star core is polynomial, its exact minimal recurrence a power of (x − 1);
    - the totals over all 162,576 starts are 150,355 stall, 11,119 path or star cores all polynomial, 4 bare rings constant and 1,098 decorated rings exponential, with no exception. The counts are the study's, now obtained from growth.

## Point for the owner (listed, not folded in)

1. **"Nothing within five places grows faster than the golden ratio"** (the answer and the final report) is wider than Proposition 6,
   which covers ring starts in the class with every knot live. The proposition should name its scope: in the class, with no dead
   knot. Starts within five places but outside the class, or with dead knots, are not covered. The referee grew the census's 2,958
   non-stalling starts outside the class and its 11,510 in-class starts with a dead knot, all within five places. None exceeded φ:
   the fastest ratio by round 16 is 1.2288. So the wider claim is not contradicted where tested, but it is not proved.
   **Narrowing,** of wording only.

## How the work was split

- **The referee:**
  - read `ring_cores.md`, `proof.md` line by line, and `ringlib.py`, `job.py` and `merge.py`;
  - wrote `job_rings.py` and `rings_readout.py`:
    - its own word enumeration;
    - its own series formula;
    - the brute-force cluster count on the cover;
    - the exact Q(√5) test of Proposition 6;
    - the piece rule read from DOUBLE-IDENT-R1's X⁺;
  - used its own FIRST-KNOT-R1 engine with the program's rule (structural implied test, CAP-CHAINS-R1), CAP-CHAINS-R1's graph
    enumeration, WEIGHTINGS-R1's bare sizes and BREAK-EDDIES-R1's exact recurrence.
- **Run as a labelled cross-check of the object under test:** the study's `ringlib.formula`. It equals the referee's formula on
  all 23,098 words, to round 40.
- **Read as data:** the touch census in `runs/touch-census`.
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 725 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
