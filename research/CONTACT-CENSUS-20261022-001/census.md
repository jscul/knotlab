# Which three-literal contacts are critical?

Epic `CONTACT-CENSUS-20261022-001`, closed 2026-10-22.

## The question

`BASE-CRITICALITY-20261022-001` showed that not-all-equal contacts make
scale-free global emergence on square tori. The cause is that fair visible
distinctions make the hidden pair-world percolate at exactly 1/2, the
threshold. The owner approved the recommended continuation, with two parts:
- a census of every placed three-variable contact on square tori with odd
  sides;
- an exact test of "x or (h ≠ h′)" against Pinson's conformal formula for
  winding clusters.

**The evidence:**
- [The census of fair contacts on square tori](../../proofs/CONTACT-CENSUS-20261022-001A/CONTACT-CENSUS-20261022-001A-P001_contact_census/proof.md)
  (A, proof);
- [The census measured and the conformal test](../../experiments/CONTACT-CENSUS-20261022-001B/CONTACT-CENSUS-20261022-001B-E001_census_and_conformal_test/contract.json)
  (B, confirmatory experiment;
  [result](../../artifacts/CONTACT-CENSUS-20261022-001B/CONTACT-CENSUS-20261022-001B-E001_census_and_conformal_test/result.json));
- **Literature:**
  - [Pinson, "Critical percolation on the torus"](https://link.springer.com/article/10.1007/BF02186762)
    (*J. Stat. Phys.* 75, 1994), in the form restated by
    [Pruessner and Moloney (2003)](https://arxiv.org/abs/cond-mat/0310361).
    The implementation reproduces Newman and Ziff's reference values.
  - For random orientations: the out-cluster of a vertex has the law of its
    bond-percolation cluster at 1/2
    ([Linusson](https://arxiv.org/abs/0905.2881)). By that coupling,
    Grimmett's randomly oriented lattice has no infinite directed path at 1/2
    (recorded by [Zhelezov](https://arxiv.org/abs/1205.5873)).

## The census (proved in A)

There are 204 ways to place one of the 34 three-variable knots as a contact:
a joint at each end of an edge (hidden) and one spoke (visible, fair). Up to
swapping spoke values, swapping joint values and reversing edges, they form
10 classes, and each class has one law.

| Regime | Classes (transfer pairs) | Placements | Emergence on square tori |
| --- | --- | --- | --- |
| Nothing | {I, J}, {U, L}, {A1, I}, {A1, J}, {J, L}, {A1, L} | 144 | 0: each has a vacuum, a constant joint value that satisfies every edge |
| Grows with the area | parity {I, S}; swap-or-order {L, S} | 36 | Parity holds exactly the cycle rank. Swap-or-order is frustrated by a 2 × 3 domino. |
| Scale-free, set by shape | not-all-equal {A1, A2}; "x or (h ≠ h′)" {J, S} | 24 | No frustrating patch; global cycles only |

So exactly two fair contacts are critical on the square lattice, and they are
critical in different ways:
- **"x or (h ≠ h′)"** is undirected. Its disequality edges are a bond
  percolation at 1/2, and the world is consistent exactly when they are
  bipartite: no cluster with a cross topology and none winding in an odd class.
  - **Bounds.** Its emergence is bounded away from 0 and from infinity
    (crossing bounds), which is not yet proved for not-all-equal.
- **Not-all-equal** is directed: a random orientation plus a seam (the previous
  epic). Its lower bound is still open.

## The conformal test (B, supported)

Pinson's formulas give, in the scaling limit, the probability of each cluster
topology of critical percolation on a torus. With the reduction, it predicts the emergence of "x or
(h ≠ h′)" with no free parameter:

| Torus shape | Pinson's limit (bits) | Measured, two largest sizes | Deviation |
| --- | --- | --- | --- |
| Square, both sides odd (to side 65) | 1.5085 | 1.5121 ± 0.0139 | +0.004 |
| Odd rows, twice as many columns (to 65 × 130) | 1.9852 | 2.0115 ± 0.0178 | +0.026 |
| Odd columns, twice as many rows (to 66 × 33) | 1.9852 | 1.9753 ± 0.0175 | −0.010 |
| Rows 3k (odd), columns 2k (to 63 × 42) | 0.6774 | 0.6755 ± 0.0079 | −0.002 |
| Both odd, rows 3/5 of columns (to 39 × 65) | 1.7898 | 1.7971 ± 0.0160 | +0.007 |
| Rotated squares (four angles) | 1.5085 | 1.5168 ± 0.0098 | +0.008 |

Every shape agrees within about 1.5 standard errors.

**The rest of the census, measured:**
- **The vacuum classes** never failed.
- **Parity** gave 9.91 ± 0.10 and 15.6 ± 0.3 bits, against exactly 10 and 16.
- **Swap-or-order** grew from 4.29 to 11.46 bits.
- **The two critical contacts** are flat over sides 9–65 at distinct values,
  0.835 and 1.521 bits.
- **Placements.** All 12 placements of each critical class agree.

## The underlying theory (interpretation, not theorem)

**The base logic computes a conformal invariant.**
- **What is computed.** Weave a square torus from the contact "if the visible
  distinction is off, the two hidden ones differ" and ask how much the whole
  hides from its pairs.
- **The answer is a number from conformal field theory.** Its limit is a
  winding probability of critical percolation, the same kind of quantity that
  describes cluster topology at a phase transition. Pinson's formula predicts
  it (a conformal prediction, not a lattice theorem), and the measurements
  match to about 1%.
- **The bridge.** The visible distinctions are fair, which puts the hidden
  pair-world exactly at the percolation threshold. The odd topology of the
  torus is what the triples can sense and the pairs cannot.

**Two kinds of critical contact.**
- **Undirected.** Disequality switched by a visible distinction gives
  undirected percolation, whose torus topology is classically known.
- **Directed.** Not-all-equal, switched both ways, gives a random orientation
  with a seam. Its scale-free amount (0.835 bits on the square, 1.15–1.19 on
  1:2 tori) is a different invariant, not yet identified.

**Most contacts are not critical.**
- **The mechanism.** A contact is critical only when it has neither a vacuum
  (otherwise the world can always rest in it) nor a frustrating patch
  (otherwise local contradictions swamp the global ones).
- **The count.** Of the 204 placements, 24 meet both conditions.

**What this adds to "infinite cycles of logic that are universally
influential".**
- **Bipartiteness.** The cycles that carry the scale-free emergence of "x or
  (h ≠ h′)" are the winding clusters of odd length.
- **What is known about them.** Their probabilities are known in closed form,
  and they are the same at every scale.
- **The boundary.** The lattice is declared, and nothing is said about space
  or physics.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Not-all-equal is the critical contact | `research/BASE-CRITICALITY-20261022-001/criticality.md` | **Incomplete.** It is one of exactly two critical classes. The other, "x or (h ≠ h′)", is simpler and solvable. |
| The scale-free amount is a new, unidentified number | The same note ("the amount depends only on shape") | **Half identified.** For "x or (h ≠ h′)" it is a winding quantity of critical percolation; Pinson's conformal formula predicts it, and the measurements match within about 1.5 standard errors on six shapes. Not-all-equal's remains unidentified. |
| A lower bound at criticality is out of reach | The same note's open problem | **Not for every contact.** It is proved for "x or (h ≠ h′)" by its reduction to undirected percolation. It stays open for not-all-equal. |
| Most three-literal contacts carry emergence at scale | Implicit in the census framing | **False on the square lattice.** 144 of 204 placements have a vacuum and hold nothing, and 36 frustrate locally. |

## Provenance and novelty

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Ten classes and three regimes | Transfer pairs from the accounting proof, with the symmetries of the torus | Elementary; new to the program |
| "x or (h ≠ h′)" is bipartite percolation; two-sided bounds | Reading the census's simplest critical class | Elementary reduction. It is a bond-diluted antiferromagnet at concentration 1/2, whose frustration on odd tori may be studied under other names (moderate folklore risk). |
| Its emergence equals a Pinson winding quantity | The criticality epic's recommendation | Classical formula (Pinson 1994), new application. Three searches (bipartite or frustrated critical percolation on odd tori, random two-literal constraints on lattices, two-way crossings in random orientations) found nothing on this application. |
| The census measured; six-shape conformal test | The experiment | Empirical, confirmatory |

**Did the base-level lens do work?** Yes.
- **What it asked.** It asked which contacts the base logic makes critical.
- **What that found.** The answer led to a contact whose emergence is a
  closed-form conformal invariant: an independent and exact test of the
  "critical base" picture, which it passed.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the proof and the experiment.
- 2 are administrative: this note and the ledger.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Identify not-all-equal's invariant** (recommended) | Map its shape function on many shapes (both parity patterns, aspect ratios, shears). Look for an exact reduction to a known directed or two-component percolation topology, and test candidate Coulomb-gas formulas. A match would put both critical contacts on known conformal ground; a mismatch would mark a new critical observable from the base logic. | 2/3 |
| 2. Bank the three epics | A self-contained note: emergence in bits, fair contacts at criticality, and the census with its conformal test. Sharing is the owner's call. | 1/3: the results are solid, but the user asks for write-ups only of results of real magnitude |
| 3. The lower bound for not-all-equal | Prove that simple certificates occur with probability bounded below. | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the contact census | **Successful** | Every placement is classified, with proofs. Exactly two contacts are critical. One of them reproduces Pinson's conformal predictions on six shapes. |
| Local direction — fair contacts on square tori | Practically complete for single contacts | Remaining: not-all-equal's invariant and lower bound. Mixtures of contacts are untested. |
| Broader exploration — the base-level theory | Known alternatives | Not-all-equal's invariant; banking; mixtures and other lattices. |
| Long-term goal — emergence from logic | Capability gained | For one contact, the scale-free emergence of the base logic is a winding quantity of critical percolation with a known conformal prediction. |
| Next recommendation — not-all-equal's invariant | **Next step:** Continue. A fresh epic: a shape scan of not-all-equal plus a search for an exact reduction or a matching Coulomb-gas formula | Identification would complete the critical picture; a new observable would be a discovery in its own right. |
| Interest — that next step | **2/3 — Promising** | The value is scale-free, rotation-invariant and set by shape, and its undirected sibling was identified exactly. The main uncertainty: directed two-way connection in random orientations has no known formula (a bounded search found none), so the identification may fail and leave only a measured shape function. |
| Execution — that next step | Deferred to the owner | One bounded epic. Stop if no reduction or formula fits within the measured precision. |
