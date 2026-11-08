# Closure of networks of loops

Status: Proved

Ticket `LOOP-NET-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/LOOP-NET-20261108-001/loop_net.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In a network of rule-60 rings with law (12, 12) contacts, a contact keeps its two chain-end witnesses at every lag exactly when its returns in the contact graph cancel (D_cc = 1). | known-with-delta; proved | A |
| 2 | The positions embed the ring graph in an oriented surface; the contact graph is its directed medial graph, whose closed routes are the rings and the faces. | known-with-delta; proved | A |
| 3 | In a uniform network (equal spacing, or on the sphere every ring and face of one density) the returns to a contact cancel exactly when every count of returns is even. | known-with-delta; proved | A |
| 4 | A symmetry fixing a contact and exchanging its rings cancels its returns, so loops, two rings sharing m contacts, the five Platonic networks and square, triangular and honeycomb lattices of rings on a torus keep every contact persistent at every lag at every size. | known-with-delta; proved | A |
| 5 | A contact joining a ring of two contacts to a ring of three or more, with no two-contact face, has one unpaired return of length 2, so in a uniform network its witnesses lapse; figure-eights and chords have such contacts. | known-with-delta; proved | A |
| 6 | Of 170,502 figure-eights and chords with rings of one size 5 to 9, none cancels every return except 20 degenerate ones; 500 persist to lag 300 through other cells. | not found in prior work; exploratory census | B |
| 7 | Of 395 plane ring graphs of 2 to 7 rings, 8 have every return count even: the 7 with a symmetry at every contact and one six-ring graph without. | not found in prior work; exploratory census | B |

## Answer

Symmetric networks of loops persist at every size, by proof; where a loop of two-contact rings meets a shared ring the returns cannot
cancel, and at equal ring sizes no other placement cancels them.

## Pending the owner

- Counted length as a native magnitude, which gates distance across time.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Recommendation

**Continue** with composition and separation across a lattice of rings (Payoff 3/3, Concreteness 2/3). The table is in the decision
note.
