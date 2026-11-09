# Full reach on the cut-open torus: the proof

Epic `FULL-REACH-PROOF-20261108-001` (program foundations), opened 2026-11-09. It continues the in-progress note of 2026-11-08
(`research/FULL-REACH-PROOF-20261108-draft/`, commits de223fb38 and b070f2f72), which this note replaces.

## The question

- **Where it comes from.** `FULL-REACH-20261108-001` computed that on the n × n torus of rule-60 rings cut open by a ring of cuts each
  way, every uncut contact needs every ring on every side from 3 to 48 except 8, 16 and 32. Its direction 1, a proof, had the
  coordinator's go-ahead on 2026-11-08; work paused that day with three lemmas (mirror duality, four layers, an invertible walk), and the
  coordinator renewed it at this thread's spawn on 2026-11-09.
- **The question.** Does full reach fail exactly at the powers of two from 8? Stop with a proof, at the first side where the pattern
  breaks, or with the reduction reached and the gap stated.

## The question in standard terms

Let G be the n × n grid graph (vertices: rings; edges: contacts) and A the adjacency matrix over GF(2) of its medial digraph with the
alternating orientation, with the outer face's arcs removed: a contact reads the next contact around each of its two rings, in one
fixed rotational sense, and a read that would need a cut contact dies. Full reach at side n: for every contact c and every ring r,
some power A^k has a 1 in row c at a contact of r. Equivalently (Theorem 2), the contacts of every ring together read every contact.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The walk and its mirror add up to a product.** A + Aᵀ = T ⊗ T, T the null-boundary path walk (rule 90) on the 2n − 1 sites of a side. | proved | A |
| 2 | **Symmetries.** The quarter turn commutes with A; the mirror and the diagonal reflection carry A to Aᵀ, so reach is symmetric under them, and every failing set is invariant under the quarter turn. The draft's mirror lemma is one case. | proved | A |
| 3 | **The box is the torus minus a cross.** A is the principal submatrix of the uncut torus's walk M off the two cut lines, so the box's walk counts are the torus's corrected through a 2n × 2n matrix on the cut lines. | proved | A |
| 4 | **At powers of two the torus dies and the cut lines are circles.** M^n = 0; the torus's Green's function on each cut line is a circle's; the whole spectrum of A is det R_CC(w), a 2n × 2n determinant of polynomials of degree below n. | proved | A |
| 5 | **A transfer identity at every side.** det(xI − A² on h) = det(u_n(y) + u_(n−1)(y) L + R u_(n−1)(y) + R u_(n−2)(y) L), y = xI + T_(n−1), with Chebyshev polynomials over GF(2). | proved | A |
| 6 | **When a layer is a field.** If A⁴'s polynomial on a layer is irreducible of full degree, every contact reads every contact; this happens at 3, 5, 7 and 11 and at no other side to 24. | proved; the sides computed | A |
| 7 | **The collapse belongs to the powers of two.** Among sides 3 to 64, every eigenvalue of A is a (2n − 1)-th root of unity exactly at 4, 8, 16, 32 and 64, where A^(e(2n − 1)) = I with e = 4, 8, 16, 16 and 32. | computed, exact | A, stress test |
| 8 | **Triangular multiplicities.** At 4, 8, 16, 32 and 64 every eigenvalue of A⁴ on a layer has multiplicity k(k + 1)/2 and geometric multiplicity 2k − 1. | computed, exact | A, stress test |

## Answer

The theorem is not proved. What changed is where the difficulty sits. At a power of two the uncut torus's walk dies after n steps, so
everything the cut-open box does comes from its two cut lines, and its whole spectrum is one 2n × 2n determinant of torus walk counts
(Theorem 4). There, and only there among the 62 sides from 3 to 64, every eigenvalue is a (2n − 1)-th root of unity, which is what lets a
few contacts cancel out. The census pattern does not break anywhere it was read. Three things stay open: the collapse at every power
of two (now a finite-looking determinant), the failing set at every power of two, and full reach at every other side, where the spectrum
is generic (one irreducible factor of degree n(n − 1)/2 at 5, 7 and 11) and no reduction is in hand.

## Reading

**Interpretation, not a theorem.**
- **A boundary effect.** The torus with both ways round open is nilpotent at powers of two, so the box's long-time behaviour is carried
  by two circles of n contacts; the field GF(2n) and the cancellations live there.
- **Why the obvious tools failed.** Mirrors carry the walk to its transpose (Theorem 2), so images do not kill, and four steps do not
  renormalize the box (the draft); the cut lines, not a mirror, are the right object.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Walk counts are exact; minimal polynomials come from Krylov spans; the collapse at powers of two is an exact matrix
  power; elsewhere a random vector's minimal polynomial is a rigorous certificate against it.
- **Census-only.** Conclusions 7 and 8; the failing set at 64 and the census at 49 and 50 (stress test).

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The collapse (the draft: 4, 8, 16, read to 16) | every side to 64 | pass: 32 and 64 collapse, no other side does |
| Triangular multiplicities (4, 8, 16 in check 10) | 32 and 64 | pass: at 64 the 17 eigenvalue classes have multiplicities 1, 1, 1, 3, 6, 10, 10, 10, 15, 15, 21, 21, 28, 28, 36, 45, 55 |
| The failing set (`FULL-REACH-20261108-001A`: 8, 16, 32) | 64 | pending |
| Only powers of two fail (`FULL-REACH-20261108-001A`: to 48) | 49 and 50 | pending (FULL-REACH-PROOF-S1, `docs/LONG_RUNNING.md`) |

The script is `stress_test.py` beside this note, with `stress_test.json` (read by check 12 of ticket A) and `stress_test_log.txt`. The census stage runs in the background (FULL-REACH-PROOF-S1 in `docs/LONG_RUNNING.md`) and is folded in when it ends.

## Literature and provenance

- **Sources.** Rule 90 with null boundaries and its Chebyshev polynomials over GF(2) (Martin, Odlyzko and Wolfram 1984; Sutner's
  σ-automata); medial graphs and their GF(2) structure (Rosenstiehl and Read); Schur complements; Lucas' theorem.
- **Related records here.** `HONEY-REACH-20261109-001` and `LATTICE-REACH-20261109-001` (2026-11-09, another thread) explain failures on
  uncut tori by symmetries that pair up walks; no symmetry of the cut-open box fixes a contact and keeps the walk's direction
  (Theorem 2), so that mechanism does not reach these failures.
- **Classification.** New as far as found; no search beyond these sources was made.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`.
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (five theorems and a proposition, thirteen checks) and the stress run.
- **Administrative.** This note and the closure.

## Corrections

None to published claims. The coordinator's relay put the draft's last claim as "only powers of two have all eigenvalues in GF(2^n)";
the draft said GF(2n), and since GF(2n) exists only when n is a power of two, the statement that carries content is the one about
(2n − 1)-th roots of unity (conclusion 7). This is wording in an unpublished draft, not a correction.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the full-reach proof | **Status:** Inconclusive | Five theorems and a reduction; the theorem is not proved |
| Local direction — composed topology across time on the cut-open torus | Continue | At powers of two the question is one 2n × 2n determinant |
| Broader exploration — G5 with G1 | Known alternatives | Honeycomb and lattice reach closed today; backlog B22 to B31 |
| Long-term goal — G5 Dynamics (question 4) | No demonstrated advance | Why powers of two are special is located, not proved |

**Corrections:** none. **Goals:** a G5 checkpoint (no demonstrated advance). **Assumptions:** none added.

- **What the attempt leaves open.** The collapse at every power of two, the failing set there, and full reach at every other side.

**Next step:** Continue — selected: #1, deferred while the tie-law epic runs first at the coordinator's instruction.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The collapse at every power of two | 2/3 — Substantial | 2/3 — Testable | The Smith form of R_CC(w) at 4, 8, 16, then a row reduction that holds for every m → a proof, or a power of two where it fails | Selected · deferred |
| 2 | The failing set from the cut-line identity | 2/3 — Substantial | 1/3 — Stated | Write c's walks to the corner through Theorem 3 at 8 and 16 → why they cancel, or no pattern | Alternative · deferred |
| 3 | Full reach at the other sides | 2/3 — Substantial | 1/3 — Stated | Look for an odd first arrival at the farthest ring on sides to 40 → an argument, or sides with none | Alternative · deferred |

1. **The collapse.** Payoff 2: it would prove the mechanism behind every failing side; Concreteness 2: the matrix is explicit, with
   monomial entries off its circulant blocks at 4 and 8, but its determinant has no closed form yet.
2. **The failing set.** Payoff 2: it would prove the failures; Concreteness 1: Theorem 3 gives the identity to prove, with no method yet.
3. **The other sides.** Payoff 2: the theorem's other half; Concreteness 1: the spectrum there is generic, and only sides 3, 5, 7 and 11
   have a one-line reason (Proposition 6).

**Recommendation.** Continue with #1 after the tie-law epic.

## Final report as sent

Sent to the owner on 2026-11-09 at 20:32 UTC and copied here verbatim.

The full-reach proof epic is closed and published, but the theorem itself is still unproved. Here is what's new. The cut-open torus is the uncut torus with two lines of contacts deleted. At powers of two the uncut torus's walk dies after n steps. So the box's whole spectrum reduces to one 2n × 2n determinant on the two cut lines. Computed exactly: every eigenvalue is a (2n−1)-th root of unity at sides 4, 8, 16, 32 and 64, and at no other side from 3 to 64.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the full-reach proof | **Status:** Inconclusive | Five theorems and a reduction; the theorem is not proved |
| Local direction: topology across time on the cut-open torus | Continue | At powers of two the question is one 2n × 2n determinant |
| Broader exploration: G5 with G1 | Known alternatives | Honeycomb and lattice reach closed today; backlog B22–B31 |
| Long-term goal: G5 Dynamics | No demonstrated advance | We now know where the powers-of-two effect sits, but it isn't proved |

**Next step:** Continue, selected #1, deferred while the tie law runs first.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | Collapse at every power of two | 2/3 | 2/3 | Smith form of the cut-line matrix at 4, 8, 16 → a proof, or a power of two where it fails | Selected · deferred |
| 2 | Failing set from the cut-line identity | 2/3 | 1/3 | Corner walks through the cut lines at 8 and 16 → why they cancel | Alternative · deferred |
| 3 | Full reach at other sides | 2/3 | 1/3 | Odd first arrivals at the farthest ring, sides to 40 → an argument | Alternative · deferred |

**Corrections:** none. **Goals:** G5 checkpoint (no demonstrated advance). **Assumptions:** none added. The census at sides 49, 50 and 64 is still running in the background (FULL-REACH-PROOF-S1), and I'll fold it in when it finishes. Commits 752cbe7fb and 689454586. Next I'm starting the tie law.
