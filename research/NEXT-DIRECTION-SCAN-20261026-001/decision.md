# Scouting the next direction after the Rowell result

Epic `NEXT-DIRECTION-SCAN-20261026-001`, closed 2026-10-26. Program: portfolio.

## The request

After `COPRIME-CLASS2-20261026-001`, the owner was offered three alternatives to the short note: general class-2 hardness (2/3),
approximate counting, which bears on Rowell's part (a) (2/3), and a return to the core program through the Borromean bridge
(2/3). The owner asked: "Could you pursue all 3 of these in sub-agents in 5.5 max so that we can get a sense of what the next
direction should be?" Three fresh-context scouting agents ran at maximum effort, one lane each. The top-level task added one
prior-art check needed by the note (is S₃ already #P-hard on links?), reran every lane's scripts in a temporary mirror of the
repository, and wrote the lane reports, which the agents' harness refused to save.

## What the lanes found

| Lane | Question | Finding | Replay | Interest | Lane's recommendation |
| --- | --- | --- | --- | --- | --- |
| A (`…001A`) | Hardness for every coprime class-2 group of class (K) with a hard pair | One alternating invariant 3-form carries every obstruction component; with the edge gadgets the count is a Bulatov–Grohe partition function whose weight matrix has rank one exactly when there is no hard pair (199 enumerated cases, 15 groups). For p odd over prime fields this sketches the dichotomy for the whole class, on r-surgeries of knots (Bulatov–Grohe with Goldberg–Grohe–Jerrum–Thurley Lemma 6.4). Gaps: sector isolation written out, an end-to-end pattern-1 knot, knot groups when some κ_{1,σ} ≠ 0. | 5 scripts, identical | 2/3 | For, bounded: prove the p-odd prime-field dichotomy, gated on a pattern-1 projector knot (predicted N = 133 and 2737) |
| B (`…001B`) | Approximate counting, Rowell's part (a) | For UT₃(F₄) ⋊ C₃ the reduction is one query and a known constant, so approximation is #BIS-hard (Goldberg–Jerrum at Q = 64); folded into the note as Proposition 18. Heisenberg: the pure-leaf recipe is exact but not approximation-preserving (the ψ⁻¹ sector stays maximal). S₄: no verdict (interpolation; planar ferromagnetic Potts; series-parallel gadgets never penalize equal states). | 7 scripts, identical | 1/3 | Against a standalone epic; optional S₄ tangle scan |
| C (`…001C`) | A bridge from the hardness to the knot test K1–K3 | Negative: every nonzero trilinear zero set is a knot in the vector reading, only the parity atom in the bit reading, and every group law is a Latin knot, so K1–K3 does not see the hard pair. The kernel count is an affine function of the allowed states of the vector-level knot; the signed reading (pairwise phases are Gauss sums, three-place phases #P-hard) is classical. "Three nontrivial characters" means "no bounded place", not "three places". | `scan_c.py`, identical | 1/3 | Against; optional signed-atom Holant discriminator |
| Check (top-level) | Is H_L(S₃) already #P-hard on links? | Yes: local torus knots isolate the rotation sector and 2-cables weight it, giving the Potts model n^(2m) Z_Γ(n, 1) for the dihedral groups D_n, n odd; checked end to end on five graphs, with 3-colourings recovered, and for D₅ and D₇. With Galindo 2026 and a cabling lemma, every centreless nonabelian group would be hard on links (conditional). Nilpotent groups on links are open (D₄, Q₈: 4^c Σ_S 4^(−cutrank S)). | 10 runs plus a separate brute force | — | Folded into the note as Proposition 1; the note's contribution is the knot case |

## What changed

- **Rowell's part (b).** It fails on links for a homological reason (unboundedly many components), already for S₃. On knots,
  where metabelian targets are easy, it needs derived length three, and S₄ is the smallest example. The note
  (`ROWELL-NOTE-20261026-001`) is reframed accordingly.
- **The knot line.** For coprime class-2 groups the criterion is a hard pair: three nontrivial characters, so no bounded place
  for the three-way obstruction. Lane A indicates that it holds for the whole class (K) over prime fields, with Bulatov–Grohe
  replacing the Potts gadgets.
- **The core program.** The K1–K3 test does not see this line. The pairwise versus three-way reading remains an interpretation
  on the complexity side, not a knot-test statement.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the three-lane scan | **Status:** Successful | Every lane returned decision-ready evidence, and every replay reproduced its outputs exactly. |
| Local direction: counting complexity of solvable targets with bounded homology | Continue, bounded | The class-(K) dichotomy is the open lead with evidence behind it. Approximation and the K1–K3 bridge are 1/3 each. |
| Broader exploration: the complexity program | Known alternatives | (i) The class-(K) dichotomy, 2/3. (ii) Nilpotent groups on links, where the count is a cut-rank sum of the linking matrix, 1/3. (iii) An S₄ tangle scan for approximation, 1/3. (iv) Signed-atom Holant networks, 1/3. A return to the core program through K1–K3 found no bridge. |
| Long-term goal: the complexity side of the 2-versus-3 thesis | Obstruction learned; no capability gained | The easy/hard line for these groups is pairwise versus three-way with no bounded place. K1–K3 does not certify it, so the bridge to native knots is still missing. |
| Next recommendation: the class-(K) dichotomy | **Next step:** Continue. Run a short epic proving the p-odd, prime-field dichotomy for coprime class-2 groups of class (K). Gate it on building the pattern-1 projector knot (p = 7, r = 6; predicted N = 133 and 2737). | It turns a family into a class. Its first discriminator costs about a day, and a mismatch would refute the realization route. Stop if the gate fails, or if a published statement is found. |
| Interest: that recommendation | **2/3: Promising** | The main uncertainty is value: the criterion does not change, and the gain is generality. The knot-group gap may also need a separate argument. |
| Execution: that action | Planned | It awaits the owner's choice; the request was to get a sense of direction, not to start one. The approved note is completed separately. |
