# One hidden bit per incidence lets a law lay out its own round sphere

Epic `SPHERE-GROWTH-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, let's update the skill, then let's pursue ii, then continue on to i". This epic is (i), from
  `UNIFORM-FANO-20261107-001`'s recommendation. It was started in the owner's local session and moved to a project thread at his
  request; nothing was redone.
- **The question.** Can a local law place the six digons of a sphere itself, so that a law grows its own sphere and with it the knot's
  contradiction, with nothing drawn?
- **Why it matters.** Uniform laws cannot contradict themselves, except the Fano plane (`UNIFORM-FANO-20261107-001`). So the knot's
  contradiction, and its hardness, needs a law that tells places apart. Question 9 asks for a law that lays out its own space.
- **Rating at the start.** Payoff 3/3 (Barrier), Concreteness 1/3 (Stated), so this epic is the scoping step: make "local law"
  precise and decide what such a law can force.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Six digons.** Every closed sphere of the two-kind law (co-lines of two or three points) has six digons. With the local Kasteleyn sign rule (the signs at a co-line of d points have parity d + 1) its knot contradicts itself. | proved (Euler and `COUNT-SURFACES-20261107-001A`) | A |
| 2 | **The tube lemma.** A law of radius r without hidden states that allows the octahedral knot sphere K_m (m ≥ 2r + 1) allows every capped tube T(m, L, τ), since each of the tube's balls occurs in K_m. The tube's knot still contradicts itself, but resolution refutes it in width O(m) at every length. | known-with-delta (local views); proved | A |
| 3 | **The seam law.** Put one hidden bit on each incidence. S1: all four incidences of a digon are seams. S2: a co-line of three points has no seam or one opposite pair. Then a two-kind sphere has a marking iff it is K_m, and K_m has exactly one (its octahedron's edges). Every sphere of the law carries a contradiction that needs width Θ(√n) and size 2^Θ(√n). | new as far as found; proved | A |
| 4 | **Growth needs branching.** A growth law without branching grows at most one closed surface from a seed; the seam law leaves only the size free. | proved (one line) | A |
| 5 | **Random growth.** A random local growth rule closed 60 spheres in 711 tries, up to 524 triangles. The only round ones were octahedra, even at the sizes of K_2 and K_4. | computed | A |

## Answer

- **Not without hidden states.** A local law with no hidden states cannot tell a round sphere from a long tube. It therefore cannot
  force roundness, and tubes carry easy contradictions.
- **With one hidden bit per incidence, yes.** The seam law's spheres are exactly the round knot spheres K_m at every size. So the law
  lays out its own sphere, six digons at the corners of an octahedron, and with it the hard contradiction.
- **What is left free is the size.** A law that grows spheres of every size must branch, and the seam law branches only on m.

## Reading

**Interpretation, not a theorem.**
- **What the hidden bit does.** The seams are straight lines the law draws for itself, a native ruler. Roundness is the statement that
  the twelve rulers between the six digons close up into equal triangles.
- **For question 9.** A uniform local law with one witness bit per incidence lays out a round sphere, nothing drawn. The witnesses are
  quantified away, as in the canonical knot test, so the law needs no executor to place them.
- **For hardness at three places.** The knot's hard contradiction needs a law that tells places apart. The seam law tells them apart by
  the six digons and the straight seams between them, with one bit and no coordinates.

## Literature and provenance

- **Classical inputs.**
  - Local views, and locally checkable proofs with certificate bits (Göös–Suomela, PODC 2011; *Theory of Computing* 2016).
  - Decorated matching rules (Penrose; Goodman-Strauss, *Annals of Mathematics* 1998; Radin's pinwheel, 1994).
  - Flat cone spheres (Thurston, *Shapes of polyhedra*, 1998); Gauss–Bonnet and developing maps of flat discs.
  - Elimination width and resolution (Davis–Putnam; width at most a tree decomposition's width plus a constant).
  - The width and size of the knot sphere's contradiction (`SPHERE-WIDTH-20261107-001A`, `SPHERE-SIZE-20261107-001B`).
- **The new part.** The seam law's characterization of the octahedral knot spheres, and its consequence for the knot's hardness.
  Folklore risk is moderate.

## Ratio

Since the epic opened:
- **Substantive.** One proof family.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — can a local law place the six digons itself? | **Status:** Successful | Not without hidden states; with one bit per incidence, exactly the round knot spheres |
| Local direction — laws that lay out their own sphere | Continue | The growth half is open |
| Broader exploration — question 9's space line | Known alternatives | Self-built surfaces, rulers, open-end growth, circles, pinwheel |
| Long-term goal — question 9 and hardness at three places | Capability gained | One hidden bit lays out the round sphere and its hard contradiction |

The attempt leaves open how a local process, rather than a law that checks a finished sphere, would build K_m. The missing bridge to
question 9's "grow" is a growth rule whose closed outputs are exactly the K_m.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Grow K_m by a local process | 2/3 — Substantial | 2/3 — Testable | Ring-by-ring growth from a digon, seams as signals → closes into K_m at every size, or a synchronization obstruction | Selected · awaiting go-ahead |
| 2 | Seams as a native knot | 2/3 — Substantial | 1/3 — Stated | Write S1 and S2 as relations and run knotlab's K1–K3 → a verdict on the seam law | Alternative · deferred |
| 3 | Other round families, GC(k, l) | 1/3 — Incremental | 2/3 — Testable | Seams of slope (k, l) with O(k + l) hidden states → a law per family, or an obstruction | Alternative · deferred |
| 4 | Write up the round-sphere results | 1/3 — Incremental | 3/3 — Ready | A short note with a replay → a reviewed note | Alternative · deferred |

1. **Grow K_m.** Payoff 2 because a growth process would complete question 9's "a law that grows its own sphere", whose law half is now
   proved. Concreteness 2 because the target is precise (closed outputs exactly the K_m), Theorem 4 says the process must branch, and
   the obstacle is named: twelve seams must reach equal length. The rings around a digon of K_m are squares until distance m, so growth
   by rings might synchronize them. The main uncertainty is whether synchronizing needs unbounded state, as growing squares by
   self-assembly needs Ω(log n / log log n) tile types. Bound: one scoping epic.
2. **Seams as a native knot.** Payoff 2 because it would tie laying out space back to the foundation: is the seam law itself a relation
   of open distinctions? Concreteness 1 because its variables and relation are not fixed yet.
3. **GC(k, l).** Payoff 1: the chiral octahedra are a refinement. Concreteness 2: the slope's period suggests a counter with O(k + l)
   states.
4. **Write-up.** Payoff 1: it makes the result reviewable without changing it. Concreteness 3: everything is in hand.

## Final report as sent

Sent to the owner on 2026-11-08 at 02:06 UTC and copied here verbatim.

**Step (i) is done and published.** A local law can place the six digons itself, but only with hidden information.

- **Without hidden states it can't.** Every small neighbourhood of a long capped tube already occurs in the round knot sphere K_m. So any law that allows K_m also allows the tubes, and their contradictions are easy: resolution width stays at 4m + 1 however long the tube gets.
- **With one hidden bit per incidence it can.** The bit marks straight "seams": all four incidences of a digon are seams, and a co-line of three points has none or one opposite pair. Then the law's spheres are exactly the K_m, at every size, each with a single marking. So every one of them carries the hard contradiction (width Θ(√n), size 2^Θ(√n)). The proof is that the seams cut any such sphere into eight equal flat triangles forming an octahedron.
- **What's still open is growth.** A growth rule without branching grows at most one surface, so only the size is left free. A local process that actually builds K_m isn't constructed yet.

Everything is in the [decision note](https://github.com/jscul/knotlab/blob/main/research/SPHERE-GROWTH-20261107-001/sphere_growth.md) and the [proof](https://github.com/jscul/knotlab/blob/main/proofs/SPHERE-GROWTH-20261107-001A/SPHERE-GROWTH-20261107-001A-P001_round_spheres_need_one_hidden_bit/proof.md). The commits are 4fb88a838 for the epic and 3cecf9bf2 for the intuition entry, and the 9 checks pass and reproduce. I also wrote the memory note UNIFORM-FANO was missing.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — can a local law place the six digons itself? | **Status:** Successful | Not without hidden states; with one bit, exactly the round knot spheres |
| Local direction — laws that lay out their own sphere | Continue | The growth half is open |
| Broader exploration — question 9's space line | Known alternatives | Self-built surfaces, rulers, open-end growth, circles, pinwheel |
| Long-term goal — question 9 and hardness at three places | Capability gained | One hidden bit lays out the round sphere and its hard contradiction |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Grow K_m by a local process | 2/3 — Substantial | 2/3 — Testable | Ring-by-ring growth from a digon, seams as signals → closes into K_m at every size, or a synchronization obstruction | Selected · awaiting go-ahead |
| 2 | Seams as a native knot | 2/3 — Substantial | 1/3 — Stated | Write S1 and S2 as relations, run K1–K3 → a verdict | Alternative · deferred |
| 3 | Goldberg–Coxeter octahedra | 1/3 — Incremental | 2/3 — Testable | Slanted seams with O(k + l) states → a law per family, or an obstruction | Alternative · deferred |
| 4 | Write up the round-sphere results | 1/3 — Incremental | 3/3 — Ready | A short note with a replay → reviewed note | Alternative · deferred |

1. Growing K_m would finish question 9's "a law that grows its own sphere", whose law half is now proved. The target is precise, and the obstacle is named: twelve seams must reach the same length. Rings around a digon stay squares out to distance m, which might keep them in step. The main uncertainty is whether that needs unbounded state, the way growing squares by self-assembly does.
2. This would tie laying out space back to the foundation, but its variables and relation aren't fixed yet.
3. This extends the result to the chiral octahedra, a refinement.
4. This makes the result reviewable without changing it.

Say go and I'll start #1 as a fresh epic.
