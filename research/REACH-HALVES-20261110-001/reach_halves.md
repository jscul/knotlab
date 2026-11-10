# Both halves of full reach on the square torus

Epic `REACH-HALVES-20261110-001` (program foundations, groups `collapse` and `reach`, B59), 2026-11-10. Pre-registered in commit
03bd5937b, before the proof attempt and before the census ran.

## The question

- **Where it comes from.** `FULL-REACH-20261108-001` computed that on the n × n torus of rule-60 rings cut open both ways every uncut
  contact needs every ring at every side from 3 to 48 except 8, 16 and 32, and `FULL-REACH-PROOF-20261108-001`'s stress test added 49,
  50 and 64. Eight epics since then worked on the spectrum at powers of two (the collapse) without proving it, and the collapse line was
  parked by `CODIST-THREE-20261110-001`'s frozen rule with B59 picked for a restart. On 2026-11-10 the owner asked for the harder 3/3
  direction and left the pick to the coordinator, who picked B59 and framed it as the full-reach theorem itself, both halves.
- **The question.** Does full reach fail exactly at the powers of two from 8? Stop with a proof of either half, a side where the census
  breaks, or the exact step that resists, stated and checked.

## The question in standard terms

A is the adjacency matrix over GF(2) of the alternating medial digraph of the n × n grid with the outer face's arcs removed; in
doubled coordinates its vertices are the points (X, Y) of [0, 2n − 2]² with X + Y odd. Full reach: for every vertex c and every grid
vertex (ring) r, some power A^k has a 1 in row c at an arc of r. Ticket A: prove that it fails at every n = 2^m ≥ 8; ticket B: prove
that it holds at every other n ≥ 3.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The failure follows from one walk count.** If the contact (1, 0) next to a corner never reads d* = (n + 3, n + 2), then c* = (n + 2, n + 3) never reads either contact of the corner ring, and full reach fails. On the h contacts A² is a grid walk with a conveyor belt: no step to the left on the bottom row, none to the right on the top row; the failure at n = 2^m needs only that walks from one corner of that grid to (n/2 + 1, n/2 + 1) are even in number at every length. | proved | A |
| 2 | **The symmetry the box hides.** The box's own reflections carry the walk to its transpose, but the reflection in the line X − Y = 1 through (1, 0) and d* is a symmetry of the walk. Mod 2 it pairs off every excursion off that line except those above it that reach the left or top wall; in the open plane nothing from (1, 0) reaches d* (only the empty walk and a single step along the line survive). | proved | A |
| 3 | **The strip at powers of two has one branch.** On the strip bounded in X, det(λI − A(t)) = λU_(n−1)((λ + t + t⁻¹)²), which is λ(λ + t + t⁻¹)^(2n−2) exactly when n is a power of two: besides the flat band λ = 0, only the free walk in Y, with one eigenvector of period 4 in X and one Jordan block; its decaying root at λ = 1/w is w²C(w⁴), C the Catalan series mod 2. | proved | A |
| 4 | **A conservation law.** On the conveyor grid the anti-diagonal sums of xM are read off the two side columns of x. | proved | A |
| 5 | **The failure through one corner, to 128.** At every power of two from 4 to 128 the corner (0, 1) reads every contact except exactly the points (X + 1, X), X = n + 2, n + 6, …, 2n − 6, d* among them. | computed, exact | A, stress test |
| 6 | **The corner return law.** The corner's return series is 1/(1 + L(w⁴)), L(z) = z + z² + z⁴ + ⋯ + z^n the trace polynomial of GF(2n): the corner returns at time 4j exactly when j + 1 is a power of two modulo 2n − 1. It is the quadrant's Catalan series folded modulo 2n − 1, that is z replaced by z + z^(2n). | computed, exact, 4 to 128 | A, stress test |
| 7 | **All four walls are needed.** In the quadrant and in both half-strips the corner reads d*; in both half-strips its return series is the quadrant's. The far corner contact meets the corner exactly as the corner meets itself, 4n − 2 steps later. | computed, exact | A, stress test |
| 8 | **The census to 130.** Full reach holds at every side from 3 to 130 except exactly 8, 16, 32, 64 and 128; there exactly n − 4 contacts miss a ring, each the three rings of one corner, and 3n + 20 miss some contact, as predicted before the run. | computed, exact | B |
| 9 | **A sufficient condition for the other half.** A cyclic contact in every ring gives full reach; among sides 3 to 20 this holds only at 3, 5, 7, 9, 11, 13, 18 and 19, so it is not the general mechanism. | proved; the sides computed | B |

## Answer

The theorem is not proved; its failing half now hangs on one even walk count. Proved: if the contact next to a corner never reaches the
point d* half a side away along the diagonal, a contact on the other side of the diagonal never reads the corner's ring, and full reach
fails (conclusion 1). On the sublattice of h contacts that is a count on a grid whose bottom row only moves right and whose top row only
moves left. A reflection in the line through the two points is a symmetry of the walk that the box's own mirrors are not, and mod 2 it
cancels every excursion off that line except the ones above it that reach the left or the top wall (conclusion 2). The vanishing itself is
computed at every power of two from 8 to 128, and at those sides the corner reads everything except d* and its few companions. The corner
also has an exact return law: 1/(1 + L(w⁴)), L the trace polynomial of GF(2n), which is the quadrant's Catalan series folded modulo
2n − 1. What resists is the closed form of the wall-reaching excursions, equivalently the corner's component at each eigenvalue, which
must vanish at d*. The other half is computed to side 130, with no proof for any infinite family.

## Reading

**Interpretation, not a theorem.**
- **The failure is not spectral.** Eight epics went through the spectrum; the failure needs only one walk count, from one corner, and the
  corner's cyclic space is small (40, 108 and 272 dimensions of 112, 480 and 1,984 at 8, 16 and 32). The collapse is not needed for it.
- **Where the trace of GF(2n) comes from.** In the quadrant the corner returns as often as the Catalan numbers are odd. The box folds that
  pattern modulo 2n − 1, and that folding is exactly the trace polynomial: 1 + L(z) vanishes on the elements of GF(2n) of trace 1, so the
  poles of the corner's return series are the eigenvalues λ with Tr(1/λ) = 1, exactly the eigenvalues of odd multiplicity (the parity law of
  `CONE-COLLAPSE-20261109-001`). This is a candidate for B59's single particle: the corner behaves as one particle whose spectrum is the
  trace-1 set, though no operator has been built from it.
- **Why all four walls.** With a far wall removed the corner's returns are the quadrant's and the corner reads d*. The cancellation comes
  from walks that reach both far walls, which a strip at a power of two makes possible through its single branch.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every count is exact over GF(2); powers of two are run over a whole period with A^P = I (or the orbit's period)
  checked, and the other sides stop only at a certificate.
- **Census-only.** Conclusions 5 to 8, and the sides of conclusion 9.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The corner return law (found at 4 to 32) | 64 and 128 | pass |
| The corner reads all but the d*'s (found at 8, 16, 32) | 64 and 128 | pass |
| The far-corner delay (found at 4 to 32) | 64 and 128 | pass |
| Full reach fails exactly at the powers of two from 8 (published to 50 and 64) | every side to 130, exact at 128 | pass: failures exactly at 8, 16, 32, 64, 128 |
| The failing set (published at 8, 16, 32, 64) | 128 | pass: 124 contacts, each missing the three rings of one corner; 404 missing some contact |
| Theorems 1 to 3, Lemma 4, Proposition 5 (proved) | — | proofs by hand; checks at sides 2 to 26; an independent referee pass (below) |

The scripts are `stress_test.py` (0.9 s) and `run_census.py` with `census.c` (1,064 s, REACH-HALVES-B2 in `docs/LONG_RUNNING.md`) beside
this note, with `stress_test.json`, `census.json` and their logs.

## Literature and provenance

- **Sources.** Reflection principles for lattice walks; Chebyshev polynomials over GF(2) and the nilpotency of rule 90 on 2^r − 1 sites
  (Martin, Odlyzko and Wolfram 1984; Sutner); the parity of the Catalan numbers; linearized polynomials and the trace (Lidl and
  Niederreiter); Theorem 2 and Theorem 5 of `FULL-REACH-PROOF-20261108-001A`.
- **Search.** A bounded web search on 2026-11-10 found nothing on reach in this walk, on GF(2) linear cellular automata whose influence
  fails exactly at powers of two on a square, or on a corner return series equal to 1/(1 + trace polynomial). Not a priority claim.
- **Classification.** New as far as found; the ingredients are classical.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`; reach is a contact-level reading (A45 does not bear on it).
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (three theorems and a lemma, six checks), ticket B (a proposition, the census to 130), the stress test.
- **Administrative.** The pre-registration, this note and the closure.

## Referee pass

An independent referee read both proofs and their checks on 2026-11-10, before publication, and reran them with its own code. Verdicts:
Theorems 1, 2(a), 2(b) and 3 and Proposition 5 correct; Theorem 2(c) correct except one sentence (the whole-plane claim fails for an h of
the line and its neighbour along it, the single step); Lemma 4 correct for 0 ≤ s ≤ 2n − 3 but stated for every s; Theorem 3's prose
omitted the flat band λ = 0 and misdescribed the branches at sides that are not powers of two, and its proof skipped the root τ = 0. It
also found computed claims without a check (the quadrant's and half-strips' return series, the criterion at 21 to 26) and checks weaker
than their labels (the census's failing-set test, one pair in the excursion check, "period" meaning only "a period"). All of these were
fixed before the first commit of the results: the statements corrected, the missing checks added (the return series below w^1200, the
criterion to 26, the failing sets recomputed from the census's ring lists, every pair of line points) and the labels made accurate. None
of them touched the main reduction or the computed laws.

## Corrections

None to published claims. The referee's findings were in unpublished drafts and are recorded above.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — both halves of full reach | **Status:** Partially successful | The failing half reduced by proof to one even walk count, computed to 128; the census to 130; neither half proved |
| Local direction — the corner count at powers of two | Continue | One explicit count, placed by a proved reflection lemma, with an exact return law beside it |
| Broader exploration — the collapse line's spectral route (G5) | Known alternatives | The failure does not need the collapse; B73 and B74 stay parked |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Why powers of two fail is one walk count from a corner, and the trace of GF(2n) shows in the corner's returns |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained); B59 rated again; sub-goal B137 and backlog B138, B139 added.
**Assumptions:** none added.
**Basket:** B137 (3/3, 1/3), B74 (3/3, 1/3), B66 (2/3, 3/3); none taken, because #1 (B138) is the cheaper route toward B137 and waits for
the coordinator's go-ahead.

- **What the attempt leaves open.** The count (★) at every power of two, the return law as a theorem, and full reach at any infinite
  family of other sides.
- **What a retired route keeps.** The collapse line's results stand; they are not needed for the failure.

**Next step:** Continue — selected: #1, awaiting the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The corner return law as a theorem (B138) | 2/3 — Substantial | 2/3 — Testable | Prove the half-strip case (one far wall invisible to the corner's returns) by a reflection, then the box's folding through 1/r_(2n)(w) = 1/r_n(w²) + w⁴ → a proof of the law, or the step where the walls interact | Selected · awaiting go-ahead |
| 2 | The corner count at every power of two (B137) | 3/3 — Barrier | 1/3 — Stated | The transfer along the diagonal of Theorem 2's wall-reaching excursions at 8, 16, 32 → a closed form and a proof of the failing half, or no pattern | Alternative · deferred |
| 3 | The single particle behind the corner (B59) | 3/3 — Barrier | 1/3 — Stated | An operator on n states with the corner's return series (spectrum the trace-1 elements of GF(2n)), tested against the cone's Jordan data at 8 and 16 → the mechanism, or a reason none exists | Alternative · deferred |
| 4 | A short-time certificate for the other half (B139) | 2/3 — Substantial | 1/3 — Stated | For every contact and ring at sides to 40, the first time within 6.4n with an odd count, and a rule for it → a proof for a family, or sides with no rule | Alternative · deferred |

1. **The return law.** Payoff 2: it would be the first proof tying this walk to the trace of GF(2n), and its method is the likeliest
   way into #2. Concreteness 2: the statement is exact and computed to 128, the half-strip case is a sharp first test of the kind
   Theorem 2 handles, and the doubling identity says what the folding must do; the uncertainty is whether a reflection reaches the
   second far wall. Connection to G5: the corner's returns are where the power-of-two effect is simplest. Bound: one epic; nothing done
   yet beyond the computations here.
2. **The count.** Payoff 3: it proves the failing half of the theorem after nine epics. Concreteness 1: the reduction is proved and the
   identity holds to 128, but the excursion transfer computed at 8 is dense with no visible pattern, so no method is in hand.
3. **The single particle.** Payoff 3: one object behind the multiplicities, blocks and field (B59 as recorded). Concreteness 1: the corner
   gives a candidate spectrum, the trace-1 set, but no operator.
4. **The other half.** Payoff 2: full reach at the other sides, the theorem's second half. Concreteness 1: the census certifies within
   6.4n steps everywhere to 130, but no rule for the certifying times is known.

**Recommendation.** Continue with #1 once the coordinator gives the go-ahead; it is the cheapest route with a definite outcome toward #2.

## Final report as sent

Sent to the owner on 2026-11-10 at 21:59 UTC and copied here verbatim.

The full-reach theorem is still unproved, but its failing half now rests on one even walk count, with the reduction proved and refereed. If the contact next to a corner never reaches the point half a side away just below the diagonal, a contact just above it never reads the corner's ring, so full reach fails. On half the contacts that is a grid walk with a conveyor belt: the bottom row only moves right and the top row only left. The count vanishes at every power of two from 8 to 128. The spectrum turned out not to be needed.

A reflection that the box's own mirrors hide is a true symmetry of the walk. Mod 2 it cancels everything except excursions above the diagonal that reach the left or top wall. The corner's return series is exactly 1/(1 + trace polynomial of GF(2n)), which is the quadrant's Catalan pattern folded modulo 2n − 1. The census confirms full reach at every other side up to 130. The independent referee found one false edge-case sentence, one lemma stated too broadly and a few missing checks; all were fixed before commit.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: both halves of full reach | **Status:** Partially successful | Failing half reduced by proof to one even walk count, computed to 128; census to 130; neither half proved |
| Local direction: the corner count | Continue | One explicit count, placed by a proved reflection lemma, with an exact return law beside it |
| Broader exploration: the spectral route (G5) | Known alternatives | The failure doesn't need the collapse; B73 and B74 stay parked |
| Long-term goal: G5 Dynamics | Capability gained | Why powers of two fail is one walk count from a corner, and GF(2n)'s trace shows in its returns |

**Next step:** Continue, selected #1, awaiting the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | The corner return law as a theorem (B138) | 2/3 | 2/3 | Prove the half-strip case by a reflection, then the box's folding → a proof, or where the two far walls interact | Selected · awaiting go-ahead |
| 2 | The corner count at every power of two (B137) | 3/3 | 1/3 | Wall-reaching excursions in closed form at 8, 16, 32 → a proof of the failing half, or no pattern | Alternative |
| 3 | The single particle behind the corner (B59) | 3/3 | 1/3 | An n-state operator with the corner's return series, tested against the cone's Jordan data → the mechanism, or none | Alternative |
| 4 | A short-time certificate for the other half (B139) | 2/3 | 1/3 | Odd counts within 6.4n for every contact and ring, sides to 40 → a rule, or sides with none | Alternative |

**Corrections:** none. **Goals:** G5 checkpoint (capability gained), no goal change. **Assumptions:** none added.
**Basket:** B137 (3/3, 1/3), B74 (3/3, 1/3), B66 (2/3, 3/3); none taken, because #1 (B138) is the cheaper route toward B137 and waits for your go-ahead.

Nothing here comes near the publication hold. Commits: 03bd5937b (pre-registration), 69811f0ea (epic), 36da8155f (goals and intuition), plus tracking. The census (REACH-HALVES-B2) passed and needs your sign-off.
