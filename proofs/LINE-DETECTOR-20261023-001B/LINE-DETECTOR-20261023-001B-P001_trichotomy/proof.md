# Two-literal contradictions are all or nothing in direction; three-place ones can be selective

Status: Proved

Ticket `LINE-DETECTOR-20261023-001B`, 2026-10-23.

**What it uses:**
- from `TRIPLE-SHIELD-20261023-001B-P001`:
  - Theorem 1 (cylinders contradict only along classes odd relative to every fitting twist);
  - Lemma 3 (rank-two contradictions contain odd walks of every odd class);
  - Lemma 4 (clusters with nonzero periods are parallel unless one has rank two).

  Both lemmas are proved there for any two-literal world on the torus whose closed walks have a parity that depends only on
  their class. Lemma 2 below supplies that parity for every two-literal tiling world.
- from `TRIPLE-TWIST-20261023-001A-P001`: the twisted three-place model, tiling placements and doubly allowed assignments;
- from `LOOP-SHIELD-20261023-001C-P001`: the line event and the wall, which needs one fair independent coin per edge;
- from `LINE-DETECTOR-20261023-001A-E001` (frozen, exhaustive on 3 × 3 and 3 × 4, sampled on 4 × 4; partially supported, its
  fourth prediction having failed): the counts in Proposition 5.

## Standard statement

**Setting.**
- **Worlds.** A world is a tiling placement R on the L × M triangular torus, a twist q and a configuration x of the visible bits,
  as in `TRIPLE-SHIELD-20261023-001B-P001`.
- **The contradiction set.** For a configuration, S(x) is the set of primitive classes whose cylinder cover has no hidden
  assignment.
- **Odd classes.** A class is odd when it is odd relative to every fitting twist. By Theorem 1 there, S(x) contains only odd
  classes.
- **Two-literal placements.** A placement is two-literal when R is closed under majority. These are the 24 orientation,
  diagonal-clause and shared-coin placements, where a coin may set several clauses of its triangle at once.

**Lemma 1 (clauses).**
- **R is its clauses.** A two-literal tiling placement is the conjunction of the two-literal clauses it implies, with no clause
  of one literal.
- **One type per edge.** On every edge of the triangular lattice, the clauses from the edge's up and down triangles all have the
  same type: a same-sign clause on every one, or an implication on every one.
- **The complement keeps the types.** Flipping a coin replaces R by its complement, which keeps every clause's pair of places and
  its type.

**Lemma 2 (parity).** In a two-literal tiling world, follow a walk in the implication graph whose projection is a closed walk of
class γ. The value of the literal changes by r(γ) mod 2, where r = q − q_f for a fitting twist q_f. All fitting twists agree on
the classes of closed walks of the clause graph.

**Theorem 3 (the trichotomy).** In every two-literal tiling world on a triangular torus, for every twist and configuration, S(x)
is one of three sets:
- empty;
- {±δ} for one primitive class δ;
- the set of all classes on which r is odd.

The third case occurs exactly when some contradicting component's cluster has a period lattice of rank two. The second occurs
exactly when every cluster's periods lie in ℤδ.

**Corollary (lone lines are line events on the two-literal side).**
- **One other tracked class always suffices.** For a nonzero r, two of the three classes (1, 0), (0, 1), (1, 1) are odd.
- **What follows.** In every two-literal tiling world, the lone line along c (only the cylinder along c contradicts among the
  three) is the pure line along c (S(x) = {±c}), and it is the line event of `LOOP-SHIELD-20261023-001C-P001` in the
  implication graph.
- **Shared coins.** The unequal dual pairs of shared-coin worlds found by `TRIPLE-SHIELD-20261023-001A-E001` (for example 942
  against 876 on 3 × 3) are therefore failures of the line event itself. That theorem's wall needs one independent coin per
  edge, and these worlds share coins.

**Proposition 4 (three places break the trichotomy).** Each of these configurations on the 3 × 3 torus contradicts along some
odd classes and has an assignment along others. Each verdict is certified both ways.

| Placement | Twist | Configuration | Contradicts along | Has an assignment along (odd classes) |
| --- | --- | --- | --- | --- |
| 54 | 01 | 91 | (1,0), (1,−1), (1,−2) | (1,1), (1,2), (3,−1), (3,1) |
| 62 | 01 | 27 | (1,0), (1,−1), (1,−2) | (1,1), (1,2), (3,−1), (3,1) |
| 111 | 00 | 681 | (1,0), (1,2), (3,2) | (0,1), (2,1), (1,−2) |

In each, the configuration is a lone line along (1,0) in the sense of the three tracked classes, yet it contradicts along further
odd classes that the lone event never checks.

**Proposition 5 (how widespread, from the frozen counts).** These counts come from `LINE-DETECTOR-20261023-001A-E001` (frozen,
partially supported, independently checked). The patterns are taken among eight classes: (1,0), (0,1), (1,1), (1,−1), (1,2),
(2,1), (1,−2), (2,−1).
- **The two-literal side follows the trichotomy everywhere examined.** This covers all 24 two-literal placements on 3 × 3 and
  3 × 4 (every configuration), and their 4 × 4 representatives (2^22 sampled configurations per twist).
- **Selectivity at three places is robust.**
  - The same 12 three-place placements are selective on 3 × 3 and on 3 × 4: 54, 62, 109, 110, 111, 125, 147, 151, 155, 159,
    203 and 215, four orbits.
  - On 3 × 4, 17712440 configurations have selective patterns.
  - On 4 × 4 the four orbit representatives, 54, 62, 109 and 111, are selective in the sample.
  - The other three-place placements show no selective pattern among the eight classes on these tori.
- **Where the dual-pair ratios were largest, the lone lines are mostly not pure.** On 3 × 4:
  - placement 54 has 20586 lone lines along (1,0) in twist 00, of which only 6 are pure among the eight; none of its 696 in
    twist 01 are;
  - placement 62 has 788304 lone lines, of which 1176 are pure; none of its 29088 in the other twist are.
- **Lines pure among the eight still differ across dual pairs.** On 3 × 4:
  - placement 111 along (1,0): 395160 against 547584;
  - placement 109 along (1,1): 144442 against 91728;
  - placement 109 along (1,0): the lone counts run one way (570852 against 635736) and the pure counts the other (456216
    against 423504).
- **The prediction that failed.** It was that no lone line of the 54 and 62 families is pure on 3 × 4. It fails: in one twist of
  each pair a few are (6 and 1176).

**Remark 6 (what this changes in `TRIPLE-SHIELD-20261023-001`).**
- **Unchanged.**
  - Its frozen counts.
  - The theorem for orientation worlds.
  - The failure of the dual-pair identity in shared-coin worlds, which the Corollary shows is a failure of the line event itself.
- **Changed.** At three places a lone line is not a line event. Its count mixes lines with contradictions along classes the event
  never checks.
  - So the ratios reported there (up to 2114 on 3 × 4) overstate the difference between lines pure among eight classes.
  - For placement 109 along (1,0) they even reverse it.
- **Still true.** Lines pure among eight classes differ across dual pairs for several three-place placements. In that sense a
  three-place line does see the twist that crosses it.
- **A qualification.** The reading "the line falls at a coin's reach, not clause width" (`TRIPLE-SHIELD-20261023-001-D001`)
  holds for the dual-pair identity of the line event, which is a law of independent pairwise coins. The direction structure of
  contradictions, the trichotomy, follows clause width.

## Nearest known result

- **Lemma 2.** Elementary: the doubly allowed tiling turns every clause type into a coboundary of the fitting twist.
- **Theorem 3.** It rests on the classical tools behind `TRIPLE-SHIELD-20261023-001B-P001`: the skew symmetry of implication
  graphs (Aspvall, Plass and Tarjan), directed ear decompositions, a cone argument and Lefschetz purity. The statement for twisted
  two-literal worlds on tori is new to the program. Moderate folklore risk.
- **Proposition 4.** A certified computation.
- **Proposition 5.** A recorded computation, frozen and independently checked.
- **Related literature.** That a shift space on ℤ² can have periodic points in some directions and not others is classical, in
  the theory of expansive directions of two-dimensional subshifts (Boyle and Lind). Proposition 4 exhibits it for three-place
  worlds, so its novelty is the contrast with Theorem 3, not the phenomenon itself.

## Proof

### Lemma 1

- **Majority closure.** A relation on three places that is closed under majority is the conjunction of the binary constraints it
  implies (a standard fact).
- **No one-literal clauses.**
  - Suppose R forced a place to a value.
  - Its complement would force the opposite value.
  - So R ∩ R̄, the doubly allowed patterns, would be empty, and no tiling would exist.
- **One type per edge.**
  - A doubly allowed tiling τ satisfies every clause of R and of R̄ on every triangle.
  - A same-sign clause and its complement together force the two values on their edge to differ.
  - An implication and its complement together force them to be equal.
  - So on any edge carrying clauses from both its triangles, the clauses must agree in type; otherwise τ would need the edge's
    values to be equal and different.
- **The complement.** Complementing all three places maps "not (u = a and w = b)" to "not (u = 1 − a and w = 1 − b)", which has
  the same pair of places and the same type. ∎

### Lemma 2

- **One step.**
  - A clause "not (h_u + t_u = β₁ and h_w + t_w = β₂)" gives the arcs (h_u = β₁ + t_u) → (h_w = 1 + β₂ + t_w) and its reverse
    partner.
  - Along either arc the value changes by s + t_u + t_w, where s = 1 + β₁ + β₂ is 1 for a same-sign clause and 0 for an
    implication.
- **Around a closed walk of class γ.**
  - The gauges contribute q(γ), since they come from deck offsets.
  - The clause types contribute Σ s. By Lemma 1 this is the type of the edges walked, the same for any clause on each edge.
- **The tiling fixes Σ s.**
  - The fitting tiling τ, in twist q_f, satisfies τ(u) + t_u + τ(w) + t_w = s on every edge, with q_f's gauges.
  - Summing around the walk, the τ terms telescope, so Σ s = q_f(γ).
- **So the change is q(γ) + q_f(γ) = r(γ).** Two fitting twists give the same Σ s, so they agree on the classes of closed walks
  of the clause graph. ∎

### Theorem 3

- **No contradiction on the torus.** Then S(x) is empty: a torus assignment lifts to every cylinder.
- **Otherwise, the contradicting components.**
  - Let S be a strong component of the torus's implication graph containing both literals of a variable.
  - A walk between those literals changes the value, so by Lemma 2 its class γ has r(γ) odd. In particular γ is nonzero, and
    S's cluster has a nonzero period.
- **Case of rank two.**
  - Suppose some contradicting component's cluster has period lattice ℤ².
  - Lemma 3 of `TRIPLE-SHIELD-20261023-001B-P001` applies, with the parity of Lemma 2. Its proof uses only the skew symmetry, the
    parity and strong connectivity, not the coins. So for every γ with r(γ) odd, the component contains walks between the two
    literals, both ways, whose projections have class exactly γ, and the cylinder along γ contradicts.
  - No class with r even contradicts, by Lemma 2. So S(x) is the set of r-odd classes.
- **Case of rank one.**
  - Otherwise every contradicting cluster has rank one.
  - No cluster at all has rank two: by Lemma 4 that would give every other cluster, including a contradicting one, period 0.
  - So by Lemma 4 every cluster with nonzero periods lies along one primitive δ.
- **The cylinders in that case.**
  - The cylinder along γ contradicts exactly when some contradicting component has walks between two literals of one vertex,
    both ways, with projected classes in ℤγ.
  - Those classes lie in ℤδ and are nonzero, so γ = ±δ.
  - Conversely, the cylinder along δ contradicts, since the component's walks close on it.
  - So S(x) = {±δ}.

The two cases are distinguished exactly as stated. ∎

**Corollary.**
- **Which tracked cylinders contradict.** For nonzero r, exactly one of the three tracked classes is even.
  - If S(x) is all odd classes, two tracked cylinders contradict, so the configuration is not lone.
  - If S(x) = {±δ}, the tracked cylinders that contradict are the one along δ, if δ is tracked, and none otherwise.
  - So "lone along c" means exactly S(x) = {±c}.
- **The line event.** By the case of rank one, S(x) = {±c} holds exactly when every cluster's periods lie in ℤc and one is
  nonzero. That is the line event, defined in the implication graph. ∎

### Proposition 4

`check.py` certifies each verdict both ways with its own search:
- a contradiction along a class by a strip of 12, 24 or 36 periods that has no assignment;
- an assignment along a class by a cyclic cover of at most 12 sheets, whose assignment is then verified clause by clause.

Every class listed was decided. ∎

## Checks

`check.py` uses the standard library only (seed 20261023). Every result below was obtained:

- **Lemma 1.**
  - All 24 two-literal tiling placements equal the conjunction of their two-literal clauses and have one clause type per edge.
  - No three-place tiling placement is such a conjunction.
- **Lemma 2.** On 3 × 3, 3 × 4 and 4 × 4, in every twist, the value change equals the relative twist on all 32296 fundamental
  cycles of the 24 placements' clause graphs.
- **Theorem 3, on 576 sampled configurations of the 24 placements on 3 × 3 and 3 × 4 in every twist.**
  - Of these, 329 contradict.
  - Each cylinder along the eight classes is certified by the check's own two-literal solver: a strip of 30 periods, or a cyclic
    cover of at most 24 sheets. None is undetermined.
  - All 329 follow the trichotomy, and the cause matches in all 329: 323 contradict along every odd class, with a rank-two
    cluster, and 6 along one class, with every cluster along it.
- **Proposition 4.** Certified for the three configurations, with no class undetermined.
- **Control.** The 47 local two-literal placements whose edge clauses clash in type all have an odd contractible closed walk, so
  Lemma 2 needs the tiling.

## What this does not show

- That three-place lines pure among all classes are or are not shielded. Purity needs every class, and Proposition 5 can only use
  eight.
- Anything about tori larger than those computed, or about other triangulations.
- Anything about space or physics. Lattices and twists are declared.
