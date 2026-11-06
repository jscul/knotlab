# Exact torus values of strongly-connected percolation

Epic `SC-TORUS-EXACT-20261022-001`, closed 2026-10-22.

## The question

`NAE-INVARIANT-20261022-001` located not-all-equal's critical invariant in
strongly-connected percolation on twisted tori. It left two exact-looking
values:
- **half a bit:** on square tori twisted along one axis, P(consistent)
  looked like 1/√2 (E∞ = 0.4993 ± 0.0011 bits);
- **3/4:** Newman, Grassberger and Ziff's untwisted one-direction wrapping is
  0.75001(7). They conjecture it is exactly 3/4, "although we know of no
  formal argument in favor of this value".

The owner approved a fresh epic:
- test 1/√2 and 3/4 at five times the precision;
- scan other twisted shapes;
- make one attempt to derive the values from the new duality identities.

**The evidence:**
- [The directed cone of a random orientation on a torus](../../proofs/SC-TORUS-EXACT-20261022-001A/SC-TORUS-EXACT-20261022-001A-P001_directed_cone/proof.md)
  (A, proof);
- [Precision tests of the exact-looking torus values](../../experiments/SC-TORUS-EXACT-20261022-001B/SC-TORUS-EXACT-20261022-001B-E001_precision_tests/contract.json)
  (B, confirmatory experiment;
  [result](../../artifacts/SC-TORUS-EXACT-20261022-001B/SC-TORUS-EXACT-20261022-001B-E001_precision_tests/result.json));
- **Literature:**
  - [Newman, Grassberger and Ziff (2026)](https://arxiv.org/abs/2607.24975):
    strongly-connected percolation and its wrapping probabilities;
  - [Chambers, Erickson and Nayyeri (2009)](https://cs.slu.edu/~chambers/papers/surflow.pdf):
    homology flows and cohomology cuts in surface graphs, the nearest known
    duality;
  - [Kook, Reiner and Stanton (1999)](https://arxiv.org/abs/math/9712232):
    the convolution formula for the Tutte polynomial.

## Outcome in one paragraph

- **Half a bit is refuted.** On squares twisted along one axis,
  E∞ = 0.49627 ± 0.00028 bits, 13 standard errors below 1/2, so
  P(consistent) tends to 0.7089, not 1/√2. The previous epic's acceptance
  came from its noisier raw estimator: its own rows, re-estimated with the
  symmetrized estimator, give 0.4973 ± 0.0006.
- **3/4 survives.** W∞ = 0.75041 ± 0.00019, 2.2 standard errors above 3/4.
- **What the two values mean, and why the identities cannot supply them.**
  The cone theorem says what each value means in directed terms. Neither
  duality nor symmetry fixes either value, and 3/4 is not a finite-size
  identity.
- **Two secondary regularities hold:**
  - the twist sectors add up on rectangles;
  - inconsistency on long twisted tori decays with exponent β/ν.

## The cone theorem (proved in A)

**The object.** For an orientation D of a square-lattice torus, collect the
classes of its directed closed walks and take the closed convex cone C they
generate. On a torus, C is one of six types: {0}, a ray, a line, a sector, a
half-plane or the whole plane.

**Directional duality.** For every primitive period d, exactly one of two
things happens:
- (i) D has a directed closed walk W with det([W], d) < 0;
- (ii) the rotated dual orientation D* has a directed closed walk of class
  exactly d.

It is the toroidal form of "either a directed cycle goes around an annulus or
a dual directed path goes across", with Minty's painting lemma as the
ingredient.

**The cone theorem.**
- **Realized classes.** The primitive classes realized by D are exactly the
  primitive periods in C. Those realized by D* are exactly those in the polar
  C° = {y : det(c, y) ≥ 0 for all c in C}.
- **Polar pairs.** {0} ↔ plane, ray ↔ half-plane, line ↔ the same line,
  sector of opening α ↔ sector of opening π − α.
- **Twisted tori.** The swap makes C = −C, so C is {0}, a line or the plane.
  This recovers the previous epic's exact duality (contractible ↔ cross).

**Laws.** Polarity maps the uniform orientation to itself, so the law of C is
invariant under C ↦ C°.
- **Four equal probabilities.** On square tori,
  P(C ⊆ V) = P(C ⊇ V) = P(C ⊆ H) = P(C ⊇ H), where V and H are the vertical
  and horizontal lines.
- **Positive versus pure winding.** P(a walk winds positively horizontally) =
  1 − P(a pure (1, 0) directed cycle), which is at least 1/2.

**What the candidate values mean.**
- **3/4.** With probability exactly 1/4, no directed closed walk winds
  horizontally. By the law identities, this is also the probability that
  directed cycles of both pure horizontal classes exist.
- **Half a bit.** On the x-twisted square, the cone is {0} or a line in an
  even class with probability exactly 1/√2.

## The derivation attempt

**One attempt, as approved. It found what the values mean, not the values.**
- **Duality and symmetry fix four equal probabilities, not their size.**
  - **What they relate.** The four events overlap in {0}, the plane and the
    axis lines. They miss every cone that neither lies in nor contains an
    axis line.
  - **What 3/4 would need.** P({0}) + P(plane) + P(axis lines) would have to
    equal the probability of those missed cones. No symmetry relates the two
    sides.
- **The identities hold at every size, and 3/4 does not.** Every identity
  above is exact on every finite torus.
  - **The 3 × 3 torus.** Enumerating all 2¹⁸ orientations gives
    P(no horizontal winding) = 13425/65536 ≈ 0.2048, so one-direction
    wrapping is 0.795. This was a scratch enumeration, not an evidence
    artifact; it takes about ten lines with the checker's helpers.
  - **The 16 × 16 torus.** The estimate is 0.758.
  - **Consequence.** 3/4 is not a consequence of any identity that holds
    exactly at finite size. A derivation would need scaling-limit input.
- **No symmetric coin.** On 128 × 128 tori the directed law is:
  - "positive only" 0.232;
  - "negative only" 0.230;
  - "both" 0.290;
  - "neither" 0.248.

  These are not four equal quarters.
- **No theory to supply the law of the cone.**
  - **Coulomb gas.** The Pinson–Arguin family was rejected in the previous
    epic.
  - **Literature.** A bounded scan found no exact theory of
    strongly-connected percolation. Newman, Grassberger and Ziff measure its
    exponents numerically.
  - **The Kook–Reiner–Stanton convolution.** It gives the exact law of the
    cyclic part: P(cyclic edges = A) is proportional to
    T(G|A; 0, 2) · T(G/A; 2, 0), the totally cyclic orientations of A times
    the acyclic orientations of G/A. Both factors are chromatic-type
    evaluations at q = −1, and no route from them to torus values was found.

## The precision tests (B, confirmatory)

**Design.** 30 rows, about 51 million samples, all decision rules frozen
in advance.
- **Estimators.** Symmetrized, built on the proved identities:
  - P(consistent) = 1/2 + (P(even) − P(odd))/2;
  - one-direction wrapping = (P(H) + P(V))/2.
- **Controls, all passing:**
  - the strong-component and odd-cluster tests agree on every sample;
  - contractible and cross counts agree on every twisted torus;
  - the rectangle identity of the cone theorem holds;
  - directed and undirected wrapping agree.
- **The independent checker.** It recomputes every estimate and decision. It
  replays three 16 × 16 tori by different methods:
  - consistency by propagation on the two-literal clauses;
  - wrapping by Kosaraju components;
  - directed winding by Bellman–Ford, with zero sample-by-sample
    disagreements against the undirected test.

  It also confirms the exact mirror symmetry of the half-sheared square.

**Half a bit: decisively rejected.**

| Side | P(consistent) | Bits |
| --- | --- | --- |
| 64 | 0.71128 ± 0.00010 | 0.49152 ± 0.00020 |
| 128 | 0.71015 ± 0.00010 | 0.49380 ± 0.00020 |
| 256 | 0.70955 ± 0.00015 | 0.49503 ± 0.00030 |
| 512 | 0.70904 ± 0.00025 | 0.49605 ± 0.00051 |
| ∞ (1/L fit, χ² = 0.75 on 2 degrees of freedom) | 0.7089 ± 0.0001 | **0.49627 ± 0.00028** |

- **Robustness.** With an added 1/L² term the limit is 0.4967 ± 0.0006,
  still 5.4 standard errors below 1/2.
- **Where the earlier acceptance came from.** The previous epic used the raw
  estimator (contractible + even)/n. At its largest size, contractible and
  cross counts happened to differ by 2.2 standard errors, although the
  duality makes them equal in law. Its own rows, re-estimated with the
  symmetrized estimator, give 0.4973 ± 0.0006: 4.5 standard errors below
  1/2, and 1.5 from the value here. Combined, 0.4964 ± 0.0003 bits.

**3/4: accepted, not explained.**

| Side | One-direction wrapping |
| --- | --- |
| 64 | 0.75271 ± 0.00015 |
| 128 | 0.75173 ± 0.00015 |
| 256 | 0.75081 ± 0.00020 |
| 512 | 0.75073 ± 0.00031 |
| ∞ (1/L fit, χ² = 1.96 on 2 degrees of freedom) | **0.75041 ± 0.00019** |

- **The decision.** 2.2 standard errors above 3/4, accepted by the frozen
  rule. With a 1/L² term the limit is 0.75007 ± 0.00039.
- **A caution.** Newman, Grassberger and Ziff's own extrapolation for this
  model (the random diode) is 0.75034(19), also about 2 standard errors
  high. Their average over four lattices is 0.75001(7). Either corrections
  beyond 1/L are specific to this model, or 3/4 is close but not exact. A
  universal value must be the same on every lattice, which favours the
  first.
- **The directed meaning, measured.** The directed estimate of
  P(no horizontal winding) is 0.2466 at side 64 and 0.2483 at side 128.

**Secondary candidates: both accepted.**
- **The twist sectors add up on rectangles.** D is the second difference
  P₀₀ − P₁₀ − P₀₁ + P₁₁ of P(contractible) over the four twist sectors, on
  common random numbers.
  - **On squares** it is +0.0032, +0.0020 and +0.0015 at sides 64, 128 and
    256, extrapolating to 0.0008 ± 0.0005.
  - **On the 2 : 1 rectangle** it is 0.00002 ± 0.00034 already at
    128 × 64.
  - **On sheared tori** scoping found it far from zero (−0.009 to −0.133),
    so this is a property of rectangular shapes, not of the model. Its
    meaning is unknown.
- **Long twisted tori decay with β/ν.** Inconsistency falls as
  e^(−2πxk) in the aspect k, with x = 0.1965 ± 0.0004 against the class's
  β/ν = 0.19635. The knot's emergence on tori twisted along their long side
  is governed by the exponent of one strong cluster spanning a long
  cylinder.
- **Reported, no candidate.** The short-side twist exponent is
  0.0655 ± 0.0002 at aspects 2–4. Its increments per unit aspect (0.597,
  then 0.588 bits) approach the 0.585 bits that the previous epic measured
  on long cylinders.

**Deviations.**
- **Wall time.** The run took 19,130 s against a declared budget of
  10,800 s. Large tori on 24 workers are memory-bound.
- **A lost first launch.** The tool's 2-hour limit on background commands
  stopped the first launch before it wrote any output. It was rerun
  unchanged with the same seeds; no data were seen in between.
- **Checker replay sizes.** These were raised after the first check, which
  passed with a 2.9-standard-error replay fluctuation. More replay samples
  make that check stricter, not looser.

## Other twisted shapes (descriptive)

| Torus | Twist | P(consistent) | Bits |
| --- | --- | --- | --- |
| Square 256 | both axes | 0.5557 ± 0.0003 | 0.8476 ± 0.0009 |
| Half-sheared square 128 | along x, or both (mirror images) | 0.63811, 0.63806 | 0.648 |
| Half-sheared square 128 | along the sheared period | 0.7118 ± 0.0004 | 0.4905 ± 0.0008 |
| 2 : 1, twisted along the long side | sides 128 × 64, 256 × 128 | 0.9174, 0.9166 | 0.1244, 0.1256 |
| 2 : 1, twisted along the short side | sides 64 × 128, 128 × 256 | 0.4484, 0.4483 | 1.1572, 1.1575 |
| 2 : 1, twisted along both | 256 × 128 | 0.4347 ± 0.0004 | 1.2019 ± 0.0013 |

**What the shapes show:**
- **The mirror pair agrees to 0.1 standard errors,** as the exact symmetry
  requires.
- **The both-axes square agrees with the previous epic's odd squares**
  (0.8455 ± 0.0029).
- **One pattern is post hoc, not tested.** The previous epic's table showed
  1/8 bit for the 2 : 1 torus twisted along its long side. Here it rises
  with size (0.1244, then 0.1256), so 1/8 looks like a passing value rather
  than the limit.
- **No other value in the scan looks exact.**

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Half a bit is the exact value on squares with one odd side | `research/NAE-INVARIANT-20261022-001/nae_invariant.md`, `docs/KNOT_INTUITION.md` (question 9), `docs/FOUNDATION_READING.md` | **Refuted.** 0.4963 ± 0.0003 bits. The earlier acceptance was an estimator artifact; the symmetrized estimator would have rejected it then. |
| The duality identities might derive the values | The previous epic's recommendation | **No.** They fix what the values mean, not the values. Since 3/4 fails at finite size, no exact identity can force it. |
| Newman, Grassberger and Ziff's 3/4 is a statement about undirected wrapping | Their paper and the previous note | **Reframed.** It is equivalent to a directed statement: no directed closed walk winds horizontally with probability 1/4. |
| The cone theorem's duality was not known | `SC-TORUS-EXACT-20261022-001A-P001` ("moderate folklore risk") | **Folklore risk raised to moderate–high.** It has the Farkas-type form of the homology-flow and cohomology-cut duality of Chambers, Erickson and Nayyeri. |
| The 2 : 1 torus twisted along its long side holds 1/8 bit | The previous epic's shape table (0.1250 ± 0.0010) | **Not supported** (post hoc): it drifts upward with size. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Directional duality and the cone theorem | Minty's lemma on the cylinder cover; the polar of the realized cone | Not found in a bounded search; moderate–high folklore risk (homology flows and cohomology cuts) |
| The directed meaning of 3/4 and of the half bit | The cone theorem applied to the uniform law | New |
| Refutation of the half bit, and the corrected value 0.4963 bits | This experiment; the previous epic's own rows re-estimated | Corrects the program's own candidate |
| 3/4 at 2 · 10⁻⁴ for the random diode model | This experiment | An independent confirmation of published numerics, with the same mild excess as theirs |
| β/ν as the long twisted decay exponent; sector additivity on rectangles | This experiment | Empirical; the identification is new to the program, and the additivity is unexplained |

**Did the base-level lens do real work?**
- **The cone theorem.** It came from asking what the knot's twisted duality
  says about directed cycles, the base logic's implications.
- **The correction.** It came from reading the knot's own identity
  P(contractible) = P(cross) as an estimator. That identity was available
  in the previous epic and unused there.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the proof and the experiment.
- 2 are administrative: this note and the ledger.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Full pivot: a bounded search for the next barrier question** (recommended) | Leave exact values of strongly-connected percolation. Compare three candidates by their cheapest discriminator, then let the owner choose. (a) The lower bound for not-all-equal's emergence, now P(C = plane) ≥ c by polarity: a crossing estimate without positive correlation. (b) Question 9, space from a law: the critical contact already gives a conformally invariant, scale-free pattern on a declared lattice; can a law generate the lattice too? (c) Question 4, dynamics: does critical emergence carry signals, a first step toward the simulation barrier? | 1/3 |
| 2. Pursue 3/4 directly | A mechanism for P(no directed horizontal winding) = 1/4 in the scaling limit. No candidate mechanism exists, and the identities provably cannot supply it. | 1/3 |
| 3. Share the reformulation | A short note to Newman, Grassberger and Ziff: the directed meaning of 3/4, the twisted exact duality, and the half bit's refutation. This is conversion, and sharing is the owner's call. | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — exact torus values | **Partially successful** | One candidate is refuted decisively (half a bit; corrected value 0.4963 bits) and one survives (3/4 at 2 · 10⁻⁴, unexplained). The cone theorem is proved. The derivation attempt shows the identities fix meanings, not values. |
| Local direction — exact values of strongly-connected percolation | Retire | The stop rule is met: the proof attempt found no mechanism, and the half bit did not survive the fivefold increase. What remains (3/4, a formula) belongs to strongly-connected percolation itself, not to emergence. |
| Broader exploration — critical emergence of single fair contacts | Practically complete | Reduction, class, duality, exponents and values are identified. Open: the lower bound (P(C = plane) ≥ c), and why the sectors add up on rectangles. |
| Long-term goal — emergence from logic (the Boolean thesis) | Capability gained | The canonical knot's critical emergence now has a corrected value (0.4963 bits on squares with one odd side) and a directed-cone description. It is a known class with one unexplained exact-looking value. |
| Next recommendation — the program's next barrier question | **Next step:** Full pivot. Leave this branch and run a bounded direction search over the lower bound, space from a law, and dynamics; the owner chooses. | Retained: the cone theorem, the corrected value, the β/ν identification, the additivity regularity. Reopen if a mechanism for 3/4 appears, or if a crossing estimate for strongly-connected percolation becomes available. |
| Interest — that search | **1/3 — Exploratory poking** | Each candidate is plausible, but none has evidence yet that it would break a barrier. The main uncertainty is which barrier the owner wants to aim at. |
| Execution — that search | Deferred to the owner | None started. Bound: one session of reading and cheap discriminators. Stop when one candidate has a falsifiable first test, or when all three look cold. |
