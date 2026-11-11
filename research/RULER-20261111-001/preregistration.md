# The not-all-equal ruler: pre-registration

Epic `RULER-20261111-001` (LONG-LOOP-20261111-001 direction 1; G1, question 9; program topology, group spacing), 2026-11-11, at the
coordinator's go-ahead. The statement is frozen before the proof is written out. The canonical K1–K3 test is unchanged.

## Frozen statement

Let Λ be the triangular lattice: sites Z², neighbours ±(1, 0), ±(0, 1), ±(1, 1), knots the triangles {x, x + (1,0), x + (1,1)} and
{x, x + (0,1), x + (1,1)}. Put the not-all-equal relation (NAE) on every triangle; the allowed states are the 2-colourings of Z² with
no monochromatic triangle (the ground states of the triangular Ising antiferromagnet). A set of sites is free when every pattern on
it occurs in an allowed state; a bond is a finite set of three or more sites that is not free while every co-1 subset is; bond
distance β(u, v) is the least size of a bond containing u and v, minus one; δ(u, v) is graph distance.

- **R1 (faithful).** Every pair of sites is free, and the non-free sets of three sites are exactly the triangles.
- **R2 (ruler).** For every two sites u ≠ v, β(u, v) = δ(u, v) + 1.
- **R3 (source label).** At the flat three-class state, every site is flipped by a change of finitely many sites, so every bond is
  native there.
- **Flat worlds** (tori and Klein bottles) are not claimed: there the result stays computed (`LONG-LOOP-20261111-001`, to distance 3
  on edge-width at least 6).

## Route and prior work

- **Known.** The ground states carry a height function (Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984): orient every
  triangle cyclically and step the height by +1 across an edge whose spins differ and by −2 across one whose spins agree. Extending a
  height function with prescribed values is a system of difference constraints, decided by the absence of negative cycles. These are
  the tools; no result on the minimal non-shattered sets of the ground-state space was found (bounded search).
- **Not used.** No edge-width or local-planarity result is needed in the plane; NAE-SAT on triangulations bears on existence only.

## Checks (finite, to support the proof)

The proof covers every site and distance. `check.py` checks: the height criterion against SAT on finite discs for every pattern on
every small set near the origin; the explicit bond for every distance to 8 in every direction; the absence of smaller bonds in a box
to distance 4; R1 in a box; R3's finite flip by SAT on a disc.

## Stop rule

A refereed proof of R1 to R3, or the least distance where R2 fails in the plane; then report and hold (the owner has paused new work
after this epic).

## Correction after freezing (2026-11-11)

Found by the referee, logged in `docs/CORRECTIONS.md` (Not a block); the text above is left as frozen. "Flat worlds (tori and Klein
bottles) ... there the result stays computed (to distance 3 on edge-width at least 6)" overstates `LONG-LOOP-20261111-001`: its
equality to distance 3 covered tori only; Klein bottles got faithfulness only.
