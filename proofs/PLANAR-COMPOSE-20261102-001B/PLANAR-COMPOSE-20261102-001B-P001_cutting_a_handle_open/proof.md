# Cutting a handle open

Status: Proved (a finite classification by exhaustive computation; the hypothesis tested fails as stated)

Ticket `PLANAR-COMPOSE-20261102-001B`, 2026-11-02.

## Question

- **From HANDLE-EMERGENCE C.** A handle trades two faces for two homology parities. On the Fano plane those parities, rather than
  counting, decide which face-odd assignments are solutions.
- **The question.** Does a handle create exactly what its homology parities add? Concretely: does creation at an opened cut disappear
  when the handle is cut open?

## Dependencies

- **`PLANAR-COMPOSE-20261102-001A`.**
- **`HANDLE-EMERGENCE-20261102-001`.** Planar spaces and the skip model.
- **`SPLICE-TREE-20261102-001C`.** `elim_lib.py`.

## Setting

- **Twists.** Fix a torus embedding of the near side. An edge set Z of the incidence graph that meets every face in an even number of
  edges is a sign twist that keeps every face condition.
- **Classes.** Modulo point and line switchings, such twists form two homology classes Za, Zb: the incidences crossed by
  non-contractible cut curves.
- **Cutting open.** Twisting changes the homology parity of the cycles crossing the curve. The union of the knot's near solutions
  over the four sectors {0, Za, Zb, Za + Zb} forgets both parities: the handle cut open along the two curves. Over {0, Z} it forgets
  one, which leaves a cylinder.
- **The test.** For each splice (line 0 of the near side into point 0 of the far side) and each creating removal: glue the united near
  relation to the far side, then count new knots as before.

## Results

1. **Embeddings.**
   - The Fano plane has 16 torus embeddings, each with seven hexagons. Census 58 has 36, of two face types.
   - On every one, the knot's signs satisfy the face condition, and the knot fails on none of the three twisted sectors.
2. **Cutting open, along the first curves elimination finds.**

   | Splice | Embeddings removing all creation |
   | --- | --- |
   | Fano > census 6 | 16 of 16 |
   | Fano > census 14 | 8 of 16 |
   | Fano > census 21 (Fano) | 8 of 16 |
   | Fano > census 38 | 16 of 16 |
   | Fano > census 45 | 12 of 16 |
   | Fano > census 58 | 8 of 16 |
   | census 58 > K4^(3) | 36 of 36 |
   | census 58 > census 6 | 28 of 36 |
   | census 58 > Fano | 24 of 36 |

   Most crossing knots survive the cut, so this is not a trivial collapse.
3. **The cut position matters.** On Fano > Fano, 20 further cuts per embedding were taken in the same two classes (the twists changed by
   random switchings). On each of four embeddings they split between removing all creation and leaving new knots: 25 against 55 in all.
4. **One parity dropped, and the control.**
   - **One parity.** On the Fano splices' 26 creating removals, the 240 new knots fall to 17, 23 or 9 when one parity is dropped,
     depending on which.
   - **Control.** Uniting the true near solutions with themselves after flipping one near point never removes creation: 104 of 104
     such unions still create.

## Reading

- **Homology carries most of it.** Dropping one parity removes about nine tenths of a handle's new knots, which no local relaxation
  does.
- **Not canonical.** Forgetting the parities in point values needs cut curves. Whether all creation disappears depends on where those
  curves run, even within one homology class and one embedding.
- **The hypothesis fails as stated.** "A handle creates exactly what its homology parities add" is not a well-posed statement about
  point values.
- **What a correct version would need.** A formulation in the choices of odd points (the skip model), where the face parities are
  canonical and the homology parities are separate conditions.

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Embeddings, face condition, twists | 16 and 36 embeddings; face condition on all; no twisted sector fails |
| 2 | Cut open with the first curves | as tabulated |
| 3 | Cut position | 25 removing against 55 leaving, every embedding mixed |
| 4 | One parity; control | 240 → 17 / 23 / 9; 104 of 104 controls still create |

## Novelty

- **New here.**
- **Classical.** Torus embeddings and spin-structure twists. The four sectors are the genus-1 analogue of Kasteleyn's four Pfaffians.
