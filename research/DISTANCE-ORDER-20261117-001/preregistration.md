# Which distance carries a base's information, and which gives an order with nothing skipped: pre-registration

Epic `DISTANCE-ORDER-20261117-001`, 17 November 2026, by Claude. It follows `DISTANCE-INFO-20261117-001` and its referee, and the
owner's answer on A97. Goals G1 and G16. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

The owner's reading A97: "Distance is the only form of information. That's the entire basis of the 'this versus that' distinction
in the smallest emergent unit." Asked whether his distance includes which way, he answered: "Distance is topological, so it will
have some starting point, then go off outward from there. So for example, 0 might be a starting point on the number line. In my
view, there isn't really any such thing as "direction". Everything is just "relative", but it's also topological, so if you're at 3
on the number line, you can't just skip 4 to get to 5, so there is an order."

The coordinator asked for two things. (1) Prove or refute that the **disagreement count**, the number of allowed states in which two
distinctions take different values, determines every not-all-equal base. (2) Test the owner's "no skipping" directly for the
candidate distances: the disagreement count, bond distance, and steps apart. Is each built from unit steps, and does betweenness
give an order from any starting distinction?

## Ticket A: the proof (written before this freeze)

`proofs/DISTANCE-ORDER-20261117-001A/DISTANCE-ORDER-20261117-001A-P001_betweenness/proof.md`, checked by its `check.py` (passed,
39 s). It proves seven statements:
- **betweenness is a three-place constraint**: c lies between a and b iff no allowed state has a = b ≠ c;
- **a not-all-equal knot is a sum**: the three counts add to 2N;
- **the disagreement table determines every nonempty not-all-equal base on n ≥ 4 distinctions**, and with N every base of
  complement-closed constraints on at most three places; it **fails at n = 3**, where one knot and none share the table;
- **parity is invisible to pairs**; four-place parity on five distinctions is the witness inside the complement-closed class;
- **a line made of betweenness** gives 2|i − j|;
- **order costs states**: a chain of m distinctions allows at most 2m of their joint values;
- **on knot trees** the rate is (1 − (−1/3)^s)/2, so τ = −log₃ |1 − 2d/N| equals steps apart.

Question (1) is answered by the proof. Ticket B tests question (2).

## Ticket B: definitions

For a base and a candidate distance D on its distinctions (the unit is the least positive value):
- **P1, built from unit steps.** D is a whole multiple of the unit, and every pair k > 1 units apart has a w one unit from u and k −
  1 units from v. In the literature, D is a graphic metric up to scale.
- **Strict betweenness.** v lies strictly between o and w when D(o, w) = D(o, v) + D(v, w), with both parts positive.
- **Gap graph.** Gaps are the pairs with nothing strictly between. Every finite D is the path distance of its gap graph, weighted
  by D. A **line** is a gap graph that is a path. A complete gap graph means that nothing lies between anything.
- **Longest chain from a start o.** The longest sequence o, v1, …, vk with each v_i strictly between o and v_(i+1), counted with o.
  It is computed on distinctions alone, and with flips (the flip ū of u, at D(u, ū) = N). With flips it is reported with and
  without the start's own flip, since every v lies between o and ō trivially.
- **τ** = −log₃ |1 − 2d/N|, with its largest difference from steps apart, and whether it increases with steps apart (every pair at
  s + 1 steps has a larger τ than every pair at s).

An earlier draft also had P2, "from every start, every v above the unit has a unit neighbour nearer the start". It was dropped on
the advisor's advice: an exact least value is attained by very few pairs, so P2 fails on bookkeeping, not on order.

## Bases

| Base | What | Size | Method |
| --- | --- | --- | --- |
| b1 | the not-all-equal thread: knots {i, i+1, i+2} | n = 30 | exact, frontier programme |
| b2 | a chain of knots sharing one distinction: (w_i, m_i, w_(i+1)) | 15 knots, n = 31 | exact, frontier programme |
| b3 | the six-regular weave W(L) of `SPACE-ORDER-20261117-001` (a torus in the literature's word) | L = 6, 9, 12 | exact: frontier programme at 6; transfer matrices modulo five primes, joined by the Chinese remainder theorem, at 9 and 12 |
| b4 | control: the threshold line | n = 10 | exact |
| b5 | every not-all-equal relation (exploratory) | n = 4, 5, 6 | exact |

Bond distance is computed by brute force on b1 at n = 10 and on b2 at four knots, with bonds of three or more distinctions (the
glossary's). On b3 it is cited from the ruler theorems (`RULER-20261111-001`, `RULER-FLAT-20261111-001`). Steps apart passes P1 by
definition, which is a code check.

## Predictions (frozen; checked with the advisor)

| # | Prediction | Fails when |
| --- | --- | --- |
| C | Control b4: P1 holds with unit 2; the gap graph is a path with one gap value; longest chain 10, with flips 11, and 10 without the start's flip | any differs |
| E1 | The disagreement count fails P1 on b1, b2 and b3 (L = 6, 9, 12) | P1 holds on any of them |
| E2 | On b1, b2 and b3, no distinction lies strictly between two others (distinctions alone): no betweenness triple, a complete gap graph, longest chain 2 | any betweenness triple |
| E3 | With flips, the longest chain is 4 counting the start's own flip, and 3 without it, on b1 and b2; the same on b3 (lower confidence) | any other value on b1 or b2 (b3 reported separately) |
| E4 | b2: τ equals steps apart for every pair (statement 7; a code check of the theorem) | otherwise |
| E5 | b1: τ is not steps apart and does not increase with steps apart (period-three oscillation) | τ increases with steps apart |
| E6 | b3: rate exactly 2/3 at one step; from v(0, 0) to the distinctions v(r, 0), r = 1, …, L − 1, rate below 1/2 at r ≡ 0 mod 3 and above 1/2 otherwise | any r on the wrong side, or a rate other than 2/3 at one step |
| E7 | b2 (four knots): bond distance is steps apart plus one for every pair (`RANDOM-FATES-20261112-001`, proved), so it fails P1 by the offset and has no betweenness triple | otherwise |
| E8 | b5: no strict betweenness among distinctions at n = 4; some at n = 5 and at n = 6 (the advisor's smallest: knots abx, aby, cxy force c = a when a = b); the chain bound of statement 6 holds everywhere (a code check) | otherwise |

No prediction for:
- b1's bond distance;
- b3's τ monotonicity;
- b5's counts of P1 bases, line gap graphs, and distinct (N, |1 − 2d/N|) tables.

**What each outcome would mean, stated before running.**
- **E1 to E3 hold.** The distance that carries everything, the disagreement count, has no order of its own in the program's spatial
  bases. Nothing lies between two distinctions, and a short chain appears only through a knot read with a flip. The distances with
  an order and nothing skipped, steps apart and bond distance (by the ruler theorems), do not carry everything (the
  `DISTANCE-INFO-20261117-001` census). No single candidate does both on these bases. The owner's "order" would then live in the
  knots: by statement 1, "c lies between a and b" is a knot.
- **E4 and E5 hold.** A quantity read from the allowed states alone gives steps apart, with nothing skipped, on knot trees. It does
  not on the thread, which has cycles of knots. So reading steps apart from the states' pair counts works exactly where there are no
  cycles.
- **E2 fails on a spatial base.** The disagreement count does carry some order there, and that would be read for its size.
- **E8 fails.** The advisor's hand analysis of betweenness in plain not-all-equal bases is wrong.

## Prior work in the program

`python3 -B scripts/track.py objects "disagreement count betweenness order steps apart" --until 2026-11-17 --exclude DISTANCE-ORDER-20261117-001`

`python3 -B scripts/track.py objects "pair counts determine relation not-all-equal" --until 2026-11-17 --exclude DISTANCE-ORDER-20261117-001`

`python3 -B scripts/track.py objects "patterns with no cycle of knots bond distance steps apart" --until 2026-11-17 --exclude DISTANCE-ORDER-20261117-001`

- `DISTANCE-INFO-20261117-001` and its referee: the predecessor. Bond distance between pairs fails, and the disagreement count
  passed every case tested.
- `OVERLAP-READ-20261111-001`: the law reads pair counts of knots, the dual of statement 3.
- `RANDOM-FATES-20261112-001`: on patterns with no cycle of knots, bond distance is steps apart plus one (proved).
- `RULER-20261111-001`, `RULER-FLAT-20261111-001`, `LOGIC-AXIS-20261107-001`: the rulers.
- `EMERGENCE-BITS-20261021-001`: the bits a knot hides from pairs, where pairs are read as distributions rather than among the
  bases of a known law.
- `JOINT-RECORDS-20261116-001`: a relative. Two-place shadows, read as sets of allowed pairs, fail to determine the seam reports of
  not-all-equal patterns at three seam distinctions, on not-all-equal itself; the disagreement count is a count of pairs, not a set.
- `SPACE-ORDER-20261117-001`: a relative. Its weave W(L) is b3, and its withdrawn "only through steps apart" reading is not used.
- `BASES-WITHIN-20261112-001`: unrelated (ties and steps apart in a drawn nesting; matched on "steps apart").
- `TWO-PRODUCT-SKETCHES-20261115-001`: unrelated (observation thresholds for affine cases; matched on "count").

## Prior work outside the program

- Metric betweenness (Menger 1928); Hamming and cut metrics, the triangle facets of the cut polytope, and ℓ1 embedding (Deza and
  Laurent 1997).
- Graphic metrics.
- The zero-temperature triangular Ising antiferromagnet, which is not-all-equal on the weave: Wannier 1950 for the count of states;
  Stephenson 1964 (J. Math. Phys. 5, 1009) and 1970 (J. Math. Phys. 11, 413) for correlations decaying as r^(−1/2) with period
  three.
- Additive tree distances from correlations (Cavender–Farris–Neyman).
- The co-clone IN₂ (Böhler, Reith, Schnoor and Vollmer 2005).

## Runs and stop rule

One script, `run.py`, one process, expected under twenty minutes. The study stops after its read-out, followed by A97's status, the
decision note, the referee hand-off and the report.

The advisor model (`claude -p --model claude-fable-5-2`) was consulted before this freeze. It:
- confirmed statements 1 to 5;
- corrected two of my predictions (the chain distinctions are not independent; the with-flips chain is 4, not 3);
- showed that P2 fails for bookkeeping reasons;
- gave the n = 5 betweenness example, the four-place parity witness, the chain bound and the log transform;
- suggested the word "disagreement count".
