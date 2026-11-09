# Distance without freezing

Epic `PLAIN-TIME-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `DISTANCE-20261108-001` found distance across time native when read through freezes, and the plain first need
  (no freezing) to be the light cone filtered by the parity of shortest routes: on time on every Platonic, genus-2 and genus-3 network
  it read, late on tori from side 5. The coordinator gave its direction 1 the go-ahead on 2026-11-08; it is also the cheapest test of A41.
- **The question.** For which networks of persistent contacts (equally spaced rule-60 rings with law (12, 12) contacts) is the plain
  first need always on time, κ(r, c) = δ(r, c) for every ring r and contact c? Stop at a criterion or at the first orientably regular map
  that fails, with the reason.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The sphere reads distance plainly.** Every loop of rings, every pair of rings sharing contacts and every Platonic network is on time at every size. | proved; Platonic exact | B |
| 2 | **Flat lattices do not.** The square plane has a late ring at distance 4 (its single closest contact reached by two shortest routes), the triangular plane at 6, the honeycomb plane at 5. | proved (square); exact | B |
| 3 | **The systole lemma.** A quotient of a tessellation whose medial systole is at least 2ℓ + m, ℓ the cover's first late distance, is late. | proved | B |
| 4 | **Exactly 26 tori are on time**: 9 square lattices (index at most 17), 11 triangular (at most 21), 6 honeycomb (at most 9), counting mirror images apart; every other torus is late. *Narrowed on 2026-11-09 to the rotation-invariant (regular) tori: thin tori of other shapes are on time at every size; see Correction.* | proved, with an exact reading of the 612 smaller tori | B |
| 5 | **The first failing map.** The twisted square torus {4,4}_(2,3), 13 rings, has one late ring per contact (δ 4, κ 5, cell-level lags 11 and 16); its mirror image is on time. The first failure from a non-abelian group is the 20-ring map of S5 with square faces (genus 6), late at 5 and 6 by wrap-around. | exact, at the cell level | A, B |
| 6 | **The covers' horizon.** In the cover of type (m, f), L = lcm(m, f), the first tie of two shortest routes comes at τ = L − L/m − L/f + 1 and the first late ring at τ + 1 (τ + 2 for triangular faces and larger rings), on every cover read; the formula predicted four types before they were read. | computed, two primes | B, stress test |
| 7 | **Finite curved maps are mixed.** 141 of 706 regular maps of genus 2 to 2,430 are on time; "unique routes" and "curvature" both fail as criteria. | exploratory census, exact | A |

## Answer

Only the sphere reads distance plainly at every size. Every flat and every hyperbolic tiling read hides it beyond a horizon set by its
ring and face sizes, τ + 1 = L − L/m − L/f + 2, from 4 on the square lattice to 26 for rings of 13 and triangular faces. A finite
network is on time only while it is too small to contain that horizon, and then whether it is on time depends on how it wraps, even on
its chirality: the first regular map that fails, a 13-ring torus, is on time in its mirror image. So there is no criterion by type,
genus, curvature or size for finite maps; there is one for the sphere, for the tori (a list of 26) and, by the systole lemma, for every
map large enough.

## Reading

**Interpretation, not a theorem.**
- **Freezing does real work, except on the sphere.** A41 holds wherever a network is two-dimensional and not tiny. The exceptions are
  loops, a pair of rings, and the five Platonic networks.
- **Curvature sets the horizon, not the verdict.** Flat lattices cancel at distance 4 to 6, hyperbolic ones only at (m − 1)(f − 1) + 1
  when m and f are coprime: curved networks read their distance plainly much further, but not forever.
- **Chirality is native.** Rule 60 reads leftward, so a network and its mirror image are different substrates, and the plain first need
  tells them apart.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Route counts are exact; least odd walk lengths follow rows mod 2 to their span; cell-level lags stop at g·κ + 1.
- **Census-only.** The census of regular maps (ticket A); the covers' first late distances and first ties, read on balls of up to two
  million contacts in PSL(2, p) for two primes that agree; the τ law's lower bound (that no shorter tie exists) is not proved.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The horizon formula (6) | rings of 3 with faces of 13, and rings of 13 with faces of 3, predicted 25 and 26 before the run | pass: 25 and 26, on balls of 1.3 and 2.0 million contacts |
| The census's first failing torus (5) | both chiralities of every torus, against the roster's one | the roster's first failing torus (16 rings) was not the smallest: the 13-ring mirror image is, now conclusion 5 |

The scripts are `stress_test.py` beside this note and check 6 of ticket B.

## Literature and provenance

- **Sources.** Geodesic counts in triangle groups and tessellations; systoles and injectivity radius of regular maps; regular maps of
  PSL(2, q) and their census (Macbeath; Conder); Lucas' theorem for the flat case.
- **The coordinator's sandbox (relayed 2026-11-08).** The 13-ring twisted torus and the τ law of first ties, with a proof of the tie's
  mechanism (two routes round a disc, one along ring corners and one along face corners, km = jf ≥ L). Both were re-read here with this
  epic's code (checks 6 and 7) and hold.
- **Classification.** New as far as found for the question asked; the ingredients are classical.

## Workspace assumptions

- **Relied on.** A30, A32, A38, A40, A41 (under challenge here, then confirmed for stated reasons).
- **Added.** None.
- **Scope.** Regular maps, tori and loops of rule-60 rings with law (12, 12) contacts; irregular networks are not classified.

## Ratio

Since the epic opened:
- **Substantive.** One frozen census (A), one proof (B) with eight checks, one stress test.
- **Administrative.** This note and the closure.

## Correction

**2026-11-09 · Narrowing** (`docs/CORRECTIONS.md`). Conclusion 4 and the answer's "only the sphere reads distance plainly at every size"
hold for regular maps, the rotation-invariant tori among them. The census built only rotation-invariant sublattices, and the bound that
made large tori late assumed the shortest lattice vector is at least √N long, which holds for those alone. `GROWN-DISTANCE-20261109-001`
proved every square torus whose lattice holds (2, 0) or (0, 2), the n × 2 ladder and its twisted forms, on time at every size
(`GROWN-DISTANCE-20261109-001A`, Theorem 2), and computed the square tori holding (2, 1) or a rotation of it (191 of 191 to index 100) and
the triangular tori holding a vector of length √3 (232 of 232 to index 80) on time too; every other on-time torus it read is small, and
the rotation-invariant ones are this epic's 26. So among tori of every shape the plain first need is on time at every size on the
thinnest tubes, which are one-dimensional at large scale. Theorems 1 to 3, the 26 regular tori, the first failing map, the covers'
horizon and the census stand ([distance in a grown network](../GROWN-DISTANCE-20261109-001/grown_distance.md)).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — distance without freezing | **Status:** Successful | The first failing map with its reason; a full answer for spheres and tori; the covers' horizon |
| Local direction — the plain first need | Research directions | The τ law's lower bound and the ring-level law are open; finite curved maps have no criterion |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B18 to B20; growing a network from a law |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Which networks read their own distance without intervention is now known: the sphere, and small networks below a horizon |

**Corrections:** none to published claims. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** A41 put under challenge and
confirmed for stated reasons.

**Next step:** Research directions — No next action selected. The owner asked to stop for today on 2026-11-08; the directions below
wait for the next session.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the τ law's lower bound | 2/3 — Substantial | 2/3 — Testable | A combinatorial Gauss–Bonnet count on the disc two tied routes bound → no shorter tie, or the first type with one | Alternative · deferred |
| 2 | Which quotients rescue locally late rings | 2/3 — Substantial | 2/3 — Testable | Compare mirror pairs of tori and maps ring by ring → the wrap-around rule, or none | Alternative · deferred |
| 3 | The ring-level law (the extra 1 for triangular faces) | 1/3 — Minor | 3/3 — Ready | Read the first late rings of the covers with faces of 3 → a proof of τ + 1 and τ + 2 | Alternative · deferred |

1. **Lower bound.** Payoff 2: it would make the horizon a theorem for every curved tiling; Concreteness 2: the coordinator's disc
   argument gives the tie, and the bound needs the same count to exclude shorter ones.
2. **Rescue.** Payoff 2: it would explain why finite maps differ from their mirror images; Concreteness 2: the tori give small cases.
3. **Ring law.** Payoff 1: a sharpening; Concreteness 3: the covers are in hand.

**Recommendation.** Research directions, none selected: the epic answered its question and the owner asked to stop for today.

## Final report as sent

Sent to the owner on 2026-11-08 at 17:53 UTC and copied here verbatim.

Distance without freezing is closed and published. Only the sphere reads distance without freezing at every size.
- **Sphere (proved):** every network there gets the plain first need on time at every size. That covers loops of rings, pairs of rings sharing contacts, and the Platonic networks.
- **Tori (complete list):** exactly 26 tori are on time. Large tori are proved to inherit the plane's failure, and the 612 smaller ones were all read exactly.
- **First failing map:** a twisted square torus with 13 rings. Its mirror image is on time. Rule 60 runs one way round each ring, so no rule by type, genus, curvature or size can decide finite maps.
- **Infinite tilings (computed):** with rings of m and faces of f, the first tie between shortest routes comes at lcm(m,f) − lcm/m − lcm/f + 1. This held on all 39 tilings read. Why no tie comes earlier is still unproved.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: distance without freezing | Successful | Full answer on the sphere and on tori; the first failing map and its reason |
| Local direction: the plain first need | Research directions | Proving the tie law, and the law for rings, are open; higher-genus maps have no rule (141 of 706 on time) |
| Broader exploration: G5 with G1 | Known alternatives | Backlog B18–B20; growing a network from a law |
| Long-term goal: G5 Dynamics | Capability gained | We know which networks read their own distance without freezing: the sphere, and small networks below a horizon |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Prove no tie comes earlier | 2/3 | 2/3 | Count corners on the disc two tied routes enclose → proof, or a tiling with an earlier tie |
| 2 | Which finite maps rescue late rings | 2/3 | 2/3 | Compare mirror pairs ring by ring → the wrap-around rule, or none |
| 3 | The law for rings | 1/3 | 3/3 | Read the first late rings in tilings with triangular faces → proved, or a counterexample |

**Corrections:** none to published claims. An unpublished progress note had named a 20-ring map as the first failure, and the 13-ring torus replaces it. **Goals:** a G5 checkpoint (capability gained); G5 paused for today. **Assumptions:** A41 (distance is read through freezes) was challenged and confirmed: freezing and the plain reading agree only on the sphere.

Commits on main: 802b129fa (the epic), 033f7c02a (register, goals, intuition page), acb932379 (backlog). All three directions are deferred, and I've stopped for today as you asked. Nothing is left running.
