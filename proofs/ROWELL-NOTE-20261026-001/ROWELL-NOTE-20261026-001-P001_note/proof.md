# A note: counting homomorphisms from knot groups to solvable groups can be #P-hard

Status: Proved

This artifact is a presentation with two small new results: the note `note/rowell_note.tex` (PDF alongside), a replay
driver, a check, the link evidence in `links/`, and an external-review package (`review_package.md`). Most theorems are
proved in the cited repository proofs; the note restates them for an outside reader, with the follow-up review's
qualifications. New here: Proposition 1 (S₃ and the odd dihedral groups are #P-hard on links), the statement that S₄ is the
smallest group with #P-hard knot counting, and Proposition 18 (approximating the count for UT₃(F₄) ⋊ C₃ is #BIS-hard).

## Standard statement

For a finite group G and a link L ⊂ S³, H_L(G) = |Hom(π₁(S³ ∖ L), G)|. Links are given by diagrams; all reductions are
polynomial-time Turing reductions; "unless FP = #P" means unless every #P function is computable in polynomial time.
Numbering follows the note.

**Proposition 1 (links).** For the dihedral group D_n of order 2n with n ≥ 3 odd (D₃ = S₃), computing H_L(D_n) is #P-hard.
For each fixed C and metabelian G, H_L(G) is polynomial-time computable on links with at most C components.

**Theorem 2 (S₄).** Computing H_K(G) from a knot diagram is #P-hard for G = S₄, GL(2,3) and the binary octahedral group 2O,
and so is the count of maps sending the meridian to a transposition. Every group of order less than 24, and SL(2,3), gives a
polynomial-time count on knots, so S₄ is the smallest group with #P-hard knot counting unless FP = #P.

**Theorem 3 (UT₃(F₄) ⋊ C₃, order 192, Fitting height 2).** For every knot K, H_K(G) = |Hom(π₁ S³₃(K), G)| + 63, and computing
either number is #P-hard.

**Theorem 4 (Heisenberg dichotomy).** Let p be an odd prime, r ≥ 2 a divisor of p − 1, and G = H(F_p) ⋊ C_r with
h·(x, y, z) = (αx, βy, αβz).
1. If α = 1, β = 1 or αβ = 1, then H_K(G) is polynomial-time computable, and so is |Hom(π₁M, G)| for closed orientable M with
   |H₁(M)| ≤ C, for each fixed C.
2. Otherwise (a hard pair), computing H_K(G) and |Hom(π₁ S³_r(K), G)| is #P-hard.

**Corollary 5.** Unless FP = #P, Rowell's Conjecture 3.2(b) (2009) fails on links for the odd dihedral groups, and already on
knots for every group shown hard in Theorems 2–4.

**Proposition 18.** For G = UT₃(F₄) ⋊ C₃, approximating H_K(G) is #BIS-hard under approximation-preserving reductions.

## Nearest known result

- **Rowell (Contemp. Math. 482, 2009, arXiv:0803.1258), §3.3.5, Conjecture 3.2.** Stated for links; verified in the primary
  text.
- **Kuperberg–Samperton.** Simple targets on knots, with the meridian in a fixed class (AGT 2021); doubt about part (b)
  (Geom. Topol. 2018, §5.3).
- **Krovi–Russell (CMP 2015).** Exact #P-hardness on links for A_m, m ≥ 5.
- **Galindo (arXiv:2605.06984, 2026).** Reshetikhin–Turaev evaluation #P-hard for every non-pointed modular category, on
  closed manifolds with planar 0-framed surgery diagrams; nothing on knots or links. Remark 7 of the note combines it with a
  cabling argument to get link hardness for every centreless nonabelian G (conditional on his theorem).
- **Samperton–Weiß (arXiv:2602.02885v2, 2026).** Class-2 targets polynomial with bounded H²(M; Z(G)); S₃ on 3-manifold groups
  named as open.
- **Fan (arXiv:2609.13326, 2026).** A signature-sum formula for dihedral link counts, with no complexity claim.
- **Livingston (JKTR 1995), Theorem 9; Massuyeau (AGT 2003); Moussard (Ann. Toulouse 2017); Jaeger–Vertigan–Welsh (1990);
  Vertigan (2005); Goldberg–Jerrum (J. ACM 2012).**
- **What is new, and folklore risk.**
  - Proposition 1 (this artifact, `links/`): candidate new; folklore risk medium, since local knots and cabling interpolation
    are standard tools, but no statement was found in bounded searches.
  - Theorem 2 (`BOUNDED-H1-20261025-001A` with `SL23-BOUNDED-20261025-001B`): candidate new; folklore risk low to medium. The
    smallest-group statement is a short consequence plus standard group theory.
  - Theorems 3 and 4 (`CORRECTIONS-20261026-001D`, `COPRIME-CLASS2-20261026-001C/D`): candidate new; folklore risk medium.
  - Proposition 18 (from scouting lane `NEXT-DIRECTION-SCAN-20261026-001B`): a direct consequence of Theorem 3's single-query
    reduction and Goldberg–Jerrum; folklore risk low.
  - Corollary 5: no earlier refutation was found in bounded literature passes on 2026-10-25 and 2026-10-26.

## What the note adds to the source proofs

- The framing: on links Rowell's part (b) fails for a homological reason (unboundedly many components), already for S₃; on
  knots it needs derived length three, and S₄ is the smallest example.
- The follow-up review's qualifications: the pure-leaf lemma assumes ψ onto (counterexample L(7,1), p = 7, r = 3, ψ = 0);
  the general easy side (Remark 14) keeps hypotheses (K); coordinates are counted once per distinct character space; each
  private cap only needs to be disjoint from the other Y-graphs (parallel caps when a coordinate is reused); the testing
  boundary is explicit (the band-and-projector recipe was not run end to end; pattern 1 has no complete instance).
- The knot-exterior form of the easy side for Heisenberg groups.

## Check

- `replay.py` copies the ten cited proofs (and the library they import) to a temporary directory, reruns every check there with
  `--write`, and compares each fresh result with the frozen one, ignoring timing. All ten pass and match exactly
  (`replay_result.json`, about 200 s).
- `links/run_all.py` runs the link checks (workspace `.venv` Python, numpy): the sector method against brute force on random
  braids; the sector formula on 1,000 random links; the cable and local-knot lemmas; closed counts from cable counts (lens
  spaces, trefoil surgeries, T³ from the Borromean rings = 48); the S₃ reduction end to end on five graphs (B₀ = 108, 3888,
  48114, 669222, 1692738; largest link 2088 crossings, 12 components); proper 3-colourings recovered on a path and a triangle
  (12 and 6); D₅ and D₇ on three graphs each; the D₄/Q₈ cut-rank formula on 60 random links each; and a separately written
  brute force of the two smallest instances (228 and 1188). Results in `links/links_result.json` and `links/logs/`.
- `check.py` (standard library; about 3 s): the replay and link summaries are complete and passing; every number the note
  quotes from the cited proofs is found in the fresh replayed results; the link logs contain the end-to-end reductions with the
  stated values; the note's own facts are recomputed (gadget algebra, Tutte points, group orders and derived lengths, the two
  smallest hard-pair orders, twist-knot roots, H_K(SL(2,3)) = 2 H_K(A₄) on four knots); the note compiles twice without errors
  or undefined references and contains every quoted string; five tampering controls are caught.

## Scope

- **Covered.** Exact counting on links (dihedral groups), on knot groups and on r-surgeries of knots, under Turing reductions;
  approximation for UT₃(F₄) ⋊ C₃ (#BIS-hardness).
- **Not claimed.** Hardness of approximation for the other groups; nilpotent groups on links; link hardness for all centreless
  groups beyond the conditional Remark 7; closed manifolds with bounded homology for GL(2,3) and 2O; general coprime class-2
  groups beyond Heisenberg groups (scouting lane `NEXT-DIRECTION-SCAN-20261026-001A` sketches the route); P versus NP.
- **Review.** The cited proofs had AI reviews (`COPRIME-CLASS2-20261026-001A` and a follow-up review); no human expert has
  reviewed the note. Nothing is sent outside the repository; sharing is the owner's decision.
