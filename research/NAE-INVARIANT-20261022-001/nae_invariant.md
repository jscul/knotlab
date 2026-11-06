# Not-all-equal's critical invariant

Epic `NAE-INVARIANT-20261022-001`, closed 2026-10-22.

## The question

`CONTACT-CENSUS-20261022-001` found exactly two fair contacts with scale-free
emergence on square tori. "x or (h ≠ h′)" reduced to Pinson's percolation
formula; not-all-equal did not. The owner approved a continuation:
- scan not-all-equal over aspect ratios, both odd-side patterns and sheared
  tori;
- look for an exact reduction (two-way directed crossings in random
  orientations, or something like the percolation backbone) or a matching
  formula, and stop if nothing fits within the measured precision;
- take the lower bound as a side result if the simple certificates make it
  cheap.

**The evidence:**
- [Strong components decide not-all-equal](../../proofs/NAE-INVARIANT-20261022-001A/NAE-INVARIANT-20261022-001A-P001_strong_components/proof.md)
  (A, proof);
- [The shape scan and the identification tests](../../experiments/NAE-INVARIANT-20261022-001B/NAE-INVARIANT-20261022-001B-E001_shape_scan/contract.json)
  (B, confirmatory experiment;
  [result](../../artifacts/NAE-INVARIANT-20261022-001B/NAE-INVARIANT-20261022-001B-E001_shape_scan/result.json));
- **Literature:**
  - strongly-connected percolation:
    [Newman, Grassberger and Ziff (2026)](https://arxiv.org/abs/2607.24975) and
    [de Noronha et al. (2018)](https://arxiv.org/abs/1808.06644);
  - the Coulomb-gas torus formulas of Pinson (1994) and
    [Arguin (2002)](https://arxiv.org/abs/hep-th/0111193);
  - the two-literal strong-component test (Aspvall, Plass and Tarjan 1979)
    and Minty's painting lemma (1966).

## The exact reduction (proved in A)

**Two-way connections, not one-way crossings.**
- **The literal graph.** With fair spokes, the implication digraph of a
  not-all-equal world is a uniformly random orientation of the bipartite
  double cover. The deck swap (one variable's two literals) reverses every
  arrow.
- **The test.** The world is inconsistent exactly when some strongly connected
  component, a set of mutually reachable literals, is mapped to itself by the
  swap.
- **On a torus.** Equivalently, the edges lying on directed cycles ("cyclic
  edges") form a cluster with a cross topology, or one winding in a class of
  odd length.

**The twist makes the duality exact.** Going once around an odd cycle reverses
every arrow.
- **In the plane,** primal and dual cyclic edges are complementary (Minty).
- **On an ordinary torus** this fails: a directed primal winding cycle can
  cross a directed dual one.
- **On the twisted torus** the swap forces such a cycle to come with a
  reversed copy. That copy would have to cross the dual cycle with the wrong
  sign, so the crossing is impossible and the duality is exact.

**What the exact duality gives,** on every shape:
- P(all contractible) = P(cross);
- P(consistent) = P(contractible) + P(even winding);
- the emergence lies between −log₂(1 − P₀) and −log₂ P₀, where
  P₀ = P(contractible).

The experiment confirms the identities on every torus: contractible and cross
counts agree within noise, and consistency equals contractible plus even
windings sample by sample.

## What the class is

Strong components of a fair random orientation are the random diode model at
its threshold. Newman, Grassberger and Ziff (July 2026) measured it as a
universality class of its own. The experiment confirms the identification
independently:

| Quantity | Measured here | Published |
| --- | --- | --- |
| Fractal dimension of strong components | 1.809, 1.815, 1.798 (± 0.005–0.010) between sides 65–513 | 1.8035 |
| Untwisted square tori: wrapping in either / one / both directions | 0.8617 / 0.7498 / 0.6379 | 0.8612 / 0.7500 / 0.6387 |
| One-way (out, in) arm exponents | 0.1043, 0.1038 | 5/48 = 0.1042 (percolation, by the out-cluster coupling) |
| Two-way arm exponent (an out-arm and an in-arm) | 0.1969 ± 0.0009 | β/ν = 0.1964 |
| Fraction of cyclic edges in the bulk | 0.49985 | 1/2 (Minty duality) |

**So strong components are neither the backbone nor independent arms.**
- **Not the backbone.** Their dimension 1.80 is far from the backbone's
  1.643.
- **Not two independent arms.** Two-way connection is not two independent
  percolation arms (5/24 = 0.2083 is excluded by 12 standard errors). The
  forward and backward reach are positively correlated, and the two-way arm
  exponent equals the class's own one-arm exponent β/ν.

## The shape function (B, confirmatory)

Emergence in bits at the largest size, with the drift over the last
doubling:

| Torus (odd sides) | Emergence | Drift |
| --- | --- | --- |
| Square, both odd | 0.8455 ± 0.0029 | +0.002 |
| 5 : 3, both odd | 1.0327 ± 0.0023 | −0.001 |
| 3 : 1, both odd | 1.7514 ± 0.0035 | +0.007 |
| Square, one side odd (pair average) | 0.4970 ± 0.0010; extrapolated 0.4993 ± 0.0011 | +0.002 |
| 2 : 1, odd side short | 1.1641 ± 0.0036 | +0.005 |
| 2 : 1, odd side long | 0.1250 ± 0.0010 | +0.003 |
| 4 : 1, odd side short | 2.3392 ± 0.0046 | +0.006 |
| 4 : 1, odd side long | 0.0098 ± 0.0002 | +0.0007 |
| Sheared squares (mirror pair) | 0.6545, 0.6524 | +0.005, +0.001 |
| Rotated squares, two rotations | 0.8385, 0.8339 (sides 29–56 and 18–32) | — |
| Long cylinders, odd circumference 65 | 0.585 bits per unit of aspect | — |

**Observations:**
- **Scale-free on every shape.** Every family is scale-free within
  3 standard errors + 0.02 bits. Several still creep upward by 0.001–0.007
  per doubling, which is visible and reported.
- **Rotation.** Rotated squares give the axis square's value (within their
  smaller sizes) and its class probabilities.
- **Which side is odd matters enormously.** At 4 : 1, an odd short side
  gives 2.34 bits and an odd long side gives 0.01.

## Formulas tested

| Candidate (pre-registered) | Outcome |
| --- | --- |
| Pinson–Arguin Coulomb gas: free coupling, separate weights for odd and even winding loops | **Rejected.** χ² = 1330 per degree of freedom at the best fit. Odd windings in longer classes are suppressed far more steeply than any member allows. |
| Exactly half a bit on square tori with one odd side, i.e. P(consistent) = 1/√2 | **Accepted.** E∞ = 0.4993 ± 0.0011 (1/L extrapolation over sides 65–257). A scoping run, not evidence, gave 0.4949 ± 0.0013 at side 257, against 0.4970 ± 0.0010 here; together they leave the candidate at about 1.7 standard errors. |
| Long-cylinder exponent 1/16 | **Rejected.** x = 0.0645 ± 0.0003 (0.0639 at circumference 33). |
| Two-way arm exponent = β/ν | **Accepted** (0.1969 against 0.1964). |

**The stop rule.** No closed formula of the expected kind fits, so the
identification stops here, as planned. One exact-looking value survives: half
a bit. It sits beside Newman, Grassberger and Ziff's untwisted
one-direction wrapping, 0.75001(7), which they conjecture to be 3/4 with no
argument.

## The lower bound (side question)

**Not cheap.**
- **The reduction.** The sandwich reduces "emergence bounded away from 0" to
  a single statement: P₀, the probability that the twisted torus has no
  winding strong component, stays bounded below.
- **What that needs.** That is a crossing estimate of Russo–Seymour–Welsh
  type for strongly-connected percolation. The model lacks the positive
  correlation those proofs use.
- **The simple certificates.** They give a sufficient condition for
  inconsistency, not a probability bound.
- **Status.** The lower bound stays open, now reduced to one estimate.

## The underlying theory (interpretation, not theorem)

- **A three-literal knot's critical emergence is the topology of two-way
  connection in its two-literal residual.**
  - Fixing the visible bits leaves a world of pairs: two-literal clauses.
  - Pairs decide everything through their strong components (each literal
    reaching the other).
  - The whole hides something from its pairs exactly when a two-way-connected
    region wraps around an odd cycle.
- **The twist is the base logic's own topology.** "Going around an odd cycle
  swaps true and false" is the not-all-equal constraint's parity, read as a
  reversal of every implication. It is what makes the model exactly
  self-dual, like ordinary percolation.
- **The two critical contacts differ in the connection they use.**
  - "x or (h ≠ h′)" asks for undirected connection: ordinary percolation,
    whose torus theory is classical.
  - Not-all-equal asks for two-way directed connection: strongly-connected
    percolation, whose torus theory is unknown but has exact-looking values
    (3/4, and now half a bit).

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Not-all-equal's critical amount is an unidentified new invariant | `research/CONTACT-CENSUS-20261022-001/census.md` | **Located.** It is a twisted-torus wrapping probability of strongly-connected percolation, a known class without a known torus formula. |
| Not-all-equal is "a random orientation with a seam" | `research/BASE-CRITICALITY-20261022-001/criticality.md` | **Refined.** The seam is a gauge artifact. The invariant object is the swap-reversed orientation of the double cover, and what matters is two-way connection. |
| Inconsistency needs crossings both ways, though 18–41% of such worlds stay consistent | The same note | **Explained exactly.** Both crossings must lie in one strong component that wraps an odd class. |
| The lower bound might follow from simple certificates | `research/CONTACT-CENSUS-20261022-001/census.md` (recommendation) | **No.** Reduced exactly to one crossing estimate for strongly-connected percolation. |
| A Coulomb-gas formula with another coupling might fit | The same recommendation | **Refuted** (χ² per degree of freedom 1330). |
| Two-way connection might be like the percolation backbone | The owner's suggestion for this epic | **No:** dimension 1.80 against 1.643. Nor is it two independent arms (5/24). |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| The double-cover reduction and the odd-cluster criterion | The two-literal strong-component test, read through the program's knot lens | Elementary; new to the program; moderate folklore risk |
| Planar complementarity of cyclic edges | Minty's lemma with planar duality | Classical ingredients; consistent with p_c = 1 for the random diode model (Newman, Grassberger and Ziff, by another route) |
| Exact duality of twisted tori and its failure on ordinary tori | The twist in the double cover | Not found in a bounded search |
| Not-all-equal's invariant as strongly-connected percolation on twisted tori; the shape function; the rejected formula family | This epic | New to the program; the class was measured by others |
| The half-bit value | Scoping, then a pre-registered test | A candidate, not established; not found in the literature |

**Did the base-level lens do real work?**
- **What it asked.** It asked which connection the base logic's pairs use.
- **What that found.** The answer (two-way, through strong components)
  located the invariant in a known class within one epic. It also produced
  the twisted-torus duality, which the class's literature does not have.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the proof and the experiment.
- 2 are administrative: this note and the ledger.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Exact torus values of strongly-connected percolation** (recommended) | Test the half bit and the untwisted 3/4 at five times the precision. Scan other symmetric twisted shapes for further exact-looking values. Attempt a derivation from the duality identities. These are: on ordinary tori, P(a walk with positive horizontal winding) + P(a pure horizontal directed cycle) = 1; on twisted tori, the analogous relations between wrapping and pure directed cycles. | 2/3 |
| 2. Bank the result | A short note: not-all-equal worlds are strongly-connected percolation on twisted tori, with the exact duality. Sharing with Newman, Grassberger and Ziff is the owner's call. | 1/3 |
| 3. The lower bound | A crossing theory for strongly-connected percolation. | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — not-all-equal's critical invariant | **Successful** | The exact reduction is proved and the class identified. The shape function is measured on 13 families. The Coulomb-gas family is refuted. One candidate exact value is accepted (half a bit) and one rejected (1/16). |
| Local direction — single fair contacts on square tori | Practically complete | Both critical contacts are reduced: "x or (h ≠ h′)" to percolation, not-all-equal to twisted strongly-connected percolation. Open: exact values and the lower bound (now one crossing estimate). |
| Broader exploration — the base-level theory | Direction clarified | Critical emergence of a three-literal knot is the wrapping topology of its two-literal residual's two-way connections. |
| Long-term goal — emergence from logic | Capability gained | The canonical knot's emergence at criticality is identified with a known universality class, with exact identities supplied by the base logic's own twist. |
| Next recommendation — exact torus values | **Next step:** Continue. A fresh epic: precision tests of 1/√2 (twisted, one odd side) and 3/4 (untwisted), a scan for other exact-looking twisted values, and one bounded attempt to derive them from the duality identities. | Exact values in a non-integrable class would point to a hidden exact structure, a discovery about strongly-connected percolation itself. |
| Interest — that next step | **2/3 — Promising** | Two exact-looking values (3/4 to 10⁻⁴ by others; 1/√2 to about 2·10⁻³ here) and new exact identities. Main uncertainty: the half bit is at roughly one standard error, and exact values may be coincidences or beyond proof. |
| Execution — that next step | Deferred to the owner | One bounded epic. Stop if neither value survives a fivefold precision increase, or if one proof attempt finds no mechanism. |
