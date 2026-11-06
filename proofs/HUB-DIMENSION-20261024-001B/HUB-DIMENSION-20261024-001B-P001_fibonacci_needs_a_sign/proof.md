# The Fibonacci rule needs a negative weight in three dimensions

Status: Proved

Ticket `HUB-DIMENSION-20261024-001B`, 2026-10-24.

**What it uses:**
- from `HUB-DIMENSION-20261024-001A-P001`:
  - the 2–3 and 1–4 move identities;
  - the eleven classes of tetrahedron labellings;
  - the failure of the unweighted Fibonacci rule;
- from `SURFACE-GLUING-20261024-001` (closed): the "no lone one" knot is the Fibonacci fusion rule, and it sees surfaces exactly;
- classical background, cited and not admitted as local evidence: Turaev–Viro state sums (1992), and move connectivity (Pachner;
  Matveev and Piergallini).

## Standard statement

**Setting.**
- **Labels and the rule.** Edges carry labels 0 (vacuum) and 1 (τ). The Fibonacci rule allows a triangle with 0, 2 or 3 τ-edges.
- **The admissible tetrahedra.** A tetrahedron class is admissible when its four faces obey the rule. There are five classes:
  - 0, no τ-edge;
  - 4, three τ-edges at one vertex;
  - 8, a four-cycle of τ-edges;
  - 9, five τ-edges;
  - 10, all six.
- **Turaev–Viro form.** A weighting assigns real numbers:
  - d to each τ-edge (1 to each vacuum edge);
  - t₂ and t₃ to each triangle with two or three τ-edges (1 with none);
  - W₀, W₄, W₈, W₉ and W₁₀ to the admissible tetrahedra;
  - v to each vertex.
  - A labelling's weight is the product, and the state sum adds over admissible labellings.
- **The identities.** They are those of ticket A, with weights:
  - **2–3:** θ(equator) W W = Σ over the new edge of d^[τ] θ θ θ W W W, for every boundary labelling with admissible boundary
    triangles;
  - **1–4:** W(old) = v · Σ over the four new edges of their edge weights times the six new triangles' and four new tetrahedra's
    weights.
  - Together they make the state sum invariant under both moves, and so, given move connectivity, a three-manifold invariant.

**Theorem 1 (the sign).** Suppose the weights d, t₂, t₃, W₄, W₈ and W₉ are non-zero, so that every admissible configuration is
weighted. Then the identities force:
- d t₂ t₃ W₉ = 1, W₈ = W₉ t₃/t₂ and W₄² = W₉ t₃/t₂²;
- d² = d + 1, so d is φ or −1/φ;
- W₁₀ = −(W₉ t₂)².

**Corollary 2 (not a count).**
- **A negative weight.** With real weights and full support, the all-τ tetrahedron has a negative weight.
- **No witness count.** No non-negative weighting, in particular no count of hidden witnesses, makes the Fibonacci rule a
  three-manifold invariant in Turaev–Viro form.

**Proposition 3 (solutions exist).** The point d = φ, t₂ = 1/φ, t₃ = 1, W₀ = 1, W₄ = W₈ = φ, W₉ = 1, W₁₀ = −1/φ² and
v = (5 − √5)/10 satisfies all 19 distinct identities exactly. Here v is 1/D², the inverse global dimension of the Fibonacci theory.

**Reading.**
- **Two dimensions.** On surfaces the Fibonacci rule counts exactly: its counts are integers, the Verlinde dimensions, in which two
  incommensurable rates cancel.
- **Three dimensions.** On three-manifolds it needs a negative weight: counting alone cannot make the incommensurables cancel, and the
  weights must interfere.
- **Physics.** The physical name for this is the sign problem of the Fibonacci string-net. Nothing physical is claimed here.

## Nearest known result

- **The phenomenon is classical.**
  - **The Fibonacci data.** The Turaev–Viro invariants of the Fibonacci category exist, and its F-matrix has the gauge-invariant
    entry −1/φ.
  - **Physics.** Fibonacci string-nets have a sign problem (Velenich, Chamon, Cugliandolo and Kovrizhin, arXiv:0911.1132). Intrinsic
    sign problems of topological field theories are characterized by Smith, Golan and Ringel (arXiv:2005.05343).
- **The local contribution** is the elementary certificate: the negative weight is forced from three of the move identities, without
  6j-symbol theory. Novelty: `candidate-local-delta` for the certificate; folklore risk high for the phenomenon.

## Proof

### Theorem 1

The check generates the 19 distinct identities as exact polynomials and confirms that, up to sign, they contain these five:
- (i) W₄ W₉ t₂ (W₉ d t₂ t₃ − 1);
- (ii) W₉ t₂ (W₉² d t₃² − W₈);
- (iii) W₉ (W₁₀ W₉ d t₃³ + W₈² t₂³);
- (iv) W₈ t₂ (W₄² t₂ − W₈);
- (v) W₄² − W₈³ t₂³ − W₉³ d t₃³.

With the weights non-zero:
- (i) gives d t₂ t₃ W₉ = 1, so d = 1/(W₉ t₂ t₃).
- (ii) gives W₈ = W₉² d t₃² = W₉ t₃/t₂.
- (iv) gives W₄² = W₈/t₂ = W₉ t₃/t₂².
- (iii) gives W₁₀ = −W₈² t₂³/(W₉ d t₃³) = −(W₉ t₃/t₂)² t₂³ · (W₉ t₂ t₃)/(W₉ t₃³) = −W₉² t₂².
- In (v), put u = 1/d = W₉ t₂ t₃. Then
  W₄² − W₈³ t₂³ − W₉³ d t₃³ = W₉ t₃/t₂² − W₉³ t₃³ − W₉² t₃²/t₂ = (W₉ t₃/t₂²)(1 − u² − u).
  So 1 − u − u² = 0, and multiplying by d², d² = d + 1. ∎

### Corollary 2

- **A negative weight.** For real non-zero W₉ and t₂, W₁₀ = −(W₉ t₂)² < 0.
- **Partial support does not help.** A weighting with some of d, t₂, t₃, W₄, W₈, W₉ equal to zero gives zero weight to every labelling
  containing the corresponding configuration. So it does not weight all Fibonacci-admissible labellings.
- **Witness counts are non-negative,** so none realizes the identities with full support. ∎

### Proposition 3

The check evaluates the 19 identities at the point in exact arithmetic over Q(√5); all vanish. ∎

## Checks

`check.py` uses the standard library only (seed 20261024), with its own polynomial arithmetic and arithmetic in Q(√5). It confirms:
- the five identities used above are among the 19 generated;
- on 200 random non-zero rational values of W₉, t₂ and t₃, the relations derived from (i), (ii) and (iv) give W₁₀ = −(W₉ t₂)², and
  (v) equals (W₉ t₃/t₂²)(1 − u² − u) exactly;
- the explicit point satisfies every identity, with d² = d + 1 and W₁₀ = −(W₉ t₂)² = −1/φ²;
- with all weights 1, some identity fails: unweighted counting is not invariant, as in ticket A.

**Controls.**
- **The sign cannot be dropped.** The point with W₁₀ replaced by +1/φ² fails.
- **The edge weight matters.** Identities generated without the new edge's weight reject the point.
- **The arithmetic detects error.** Replacing d by the rational 8/5 leaves a residual.

## What this does not show

- **State sums of other forms.** These include labels on faces, larger label sets, and non-local weights. A positive model of a
  different local structure is not excluded.
- **Weights that are complex but not real.** W₁₀ = −(W₉ t₂)² is positive when W₉ t₂ is imaginary; such weights are not counts
  either.
