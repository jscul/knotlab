# The knot's count is PPADS-complete; the two-sided count is PPAD-complete

Status: Proved by hand, by composing proved reductions with cited characterizations. The new local facts are checked by computation
(`check.py`).

Ticket `COUNT-TFNP-20261107-001B`, 2026-11-07.

## Standard statement

Let K_k be the octahedral knot sphere and NAE(K_k) its Kasteleyn-signed not-all-equal formula, with n = 4k² variables and 8k² clauses of
width 3. A three-point face of the plane incidence graph is monochromatic when its three corners all agree; FACE(K_k) is the
3-clauses forbidding that. In the decision-tree (black-box) model, consider two total search problems:
- **the one-sided count:** given an assignment, find a violated clause of NAE(K_k), a monochromatic line;
- **the two-sided count:** find a violated clause of NAE(K_k) ∧ FACE(K_k), a monochromatic line or face.

**Theorem.**
1. The one-sided count is complete for PPADS^dt.
2. The two-sided count is complete for PPAD^dt.
3. Hence:
   - NAE(K_k) has a Sherali–Adams refutation of degree 3 with coefficients ±1;
   - it has no Nullstellensatz refutation over F2 of polylogarithmic degree;
   - it has no unary Nullstellensatz refutation of polylogarithmic degree and quasipolynomial size;
   - NAE(K_k) ∧ FACE(K_k) has a Nullstellensatz refutation of degree 3 with multipliers ±1.
4. The one-sided count is not in PLS^dt either: resolution needs width Ω(√n) on it (`COUNT-NOTE-20261107-001A`), and PLS^dt is
   characterized by resolution width.

## Nearest known result

- **Separations.** Beame–Cook–Edmonds–Impagliazzo–Pitassi (JCSS 1998), §3.3: PPADS ⊄ PPA relative to every generic oracle
  (SINK is not reducible to LONELY). Since PPAD ⊆ PPA, also PPADS ⊄ PPAD. A survey statement in the decision-tree setting: "Beame et al.
  proved all possible separations between PPA^dt, PPAD^dt, PPADS^dt and PPP^dt".
- **Characterizations.**
  - PPADS^dt = unary Sherali–Adams and PPAD^dt = unary Nullstellensatz (Göös, Hollender, Jain, Maystre, Pires, Robere, Tao, JACM 2024;
    corollary 4 for PPADS).
  - PPA^dt = Nullstellensatz degree over F2, and PLS^dt = resolution width (Göös, Kamath, Robere, Sokolov, ITCS 2019; restated by
    Davis–Robere, CCC 2023).
- **Reductions used.**
  - `COUNT-TFNP-20261107-001A`: SINK reduces to one-sided grid Sperner.
  - `FLAT-STATES-20261107-001B`: one-sided Sperner_m reduces to the count on K_{2m+4} by depth-2 decision trees.
  - `COUNT-NOTE-20261107-001B`: the degree-3, ±1 Sherali–Adams certificate.
- **Classification.** new as far as found. The formulas are this project's. The classification composes these reductions, and its new
  local facts are:
  - the two-sided map (monochromatic faces sit exactly in clockwise triangles);
  - the boundary shift;
  - the two-sided Nullstellensatz identity.

## Proof

**(1) One-sided, membership.** The certificate of `COUNT-NOTE-20261107-001B` is a unary Sherali–Adams refutation:
- degree 3 and width 3;
- 4n − 8 terms with coefficients ±1.

By corollary 4 of Göös et al., the false-clause search problem of NAE(K_k) is in PPADS^dt.

**(1) One-sided, hardness.** Compose three steps:
- SINK on N nodes → one-sided Sperner_m with m = O(N²) (`COUNT-TFNP-20261107-001A`; depth O(log N));
- a cyclic shift of all colours by −m (mod 3), which turns the canonical boundary into the one `FLAT-STATES-20261107-001B`'s map expects
  (check 1) and keeps fully labelled triangles and their orientations;
- that map, into K_{2m+4}, of depth 2.

The result is a decision-tree reduction of depth O(log N) into a sphere with n = O(N⁴) points. So the count is PPADS^dt-hard, and
complete.

**(2) Two-sided, membership.** Sum the corner agreements by lines and by faces, as in `COUNT-NOTE-20261107-001B`:
- Σ_l (two line-clause falsifiers) − Σ_f (two face-clause falsifiers) = 1 as multilinear polynomials;
- both sums are now sums of clause falsifiers of NAE(K_k) ∧ FACE(K_k), so this is a Nullstellensatz refutation with constant multipliers
  ±1 (check 3);
- by Göös et al., the two-sided count is in PPAD^dt.

**(2) Two-sided, hardness.** `COUNT-TFNP-20261107-001A`'s construction reduces SOURCE.OR.SINK to two-sided Sperner_m. On the sphere,
`FLAT-STATES-20261107-001B`'s map sends each fully labelled triangle to a solution of the two-sided count:
- counterclockwise ones to violated lines (as proved there);
- clockwise ones to monochromatic faces (check 2), and every monochromatic face of the image lies inside a clockwise fully labelled
  triangle.

A solution of the two-sided count therefore names a fully labelled triangle, read off from its position, and the composition is a
decision-tree reduction. So the two-sided count is PPAD^dt-complete.

**(3) Consequences.**
- If the one-sided count were in PPA^dt, composing with (1)'s hardness would put SINK in PPA^dt, against Beame et al. So it is not in
  PPA^dt, nor in PPAD^dt ⊆ PPA^dt.
- By the characterizations, NAE(K_k) has no polylogarithmic-degree Nullstellensatz refutation over F2.
- It has no unary Nullstellensatz refutation of polylogarithmic degree and quasipolynomial size.
- The Sherali–Adams refutation of degree 3 exists by (1), and the two-sided Nullstellensatz refutation by (2).

**(4) PLS.** A PLS^dt reduction for the count would give it resolution refutations of polylogarithmic width. Its width is Ω(√n)
(`COUNT-NOTE-20261107-001A`), so it is not in PLS^dt. ∎

## Reading

**Interpretation, not a theorem.**
- **What the clauses see.** The knot's Kasteleyn signs let the lines see only one orientation of the label vortex:
  - a counterclockwise vortex violates a line;
  - a clockwise one, an antivortex, only makes a face monochromatic, and faces are not clauses.
- **The classes.** With both orientations as solutions, the count is two-sided Sperner, a PPAD principle. With the lines alone it is
  one-sided Sperner, a PPADS principle.
- **So** the knot's orientation is exactly what lifts its count from PPAD to PPADS: it is the sink-versus-source information that
  END-OF-LINE cannot use. Resolution sees neither difference: both counts need size 2^Θ(√n).

## Checks

`check.py` (`result.json`), under a minute:

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The reduction's boundary for m = 3..12 | the canonical boundary shifted by −m (mod 3): a cyclic shift, which keeps orientations |
| 2 | The map on 160 random Sperner colourings, m = 4..7 (half seeded with clockwise triangles) | violated lines exactly inside counterclockwise triangles, monochromatic faces exactly inside clockwise ones, one per fully labelled triangle (m = 7: 352 triangles, 196 violated lines, 156 monochromatic faces); the count identity holds |
| 3 | The two-sided identity on K_2..K_6 | Σ line-clause falsifiers − Σ face-clause falsifiers = 1; multipliers ±1, degree 3 |
| 4 | Controls | a seeded clockwise triangle holds no violated line; auditing against a changed colouring is rejected; the identity fails without one face clause |

## What this does not establish

- **Concrete degrees.** The Nullstellensatz lower bounds are qualitative (not polylogarithmic). No explicit degree bound is proved
  for these formulas.
- **Circuit TFNP.** The white-box classification (PPADS-completeness with circuits) is not written out, although the same reductions
  apply.
- **Other systems.** Nothing here concerns cutting planes or Res(⊕).
