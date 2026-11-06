# A note: native selection on regular systems, and why three places

Status: Proved

Ticket `SELECTION-NOTE-20261101-001` (root ticket, program foundations), 2026-11-01.

## What this artifact is

Option (a) of the three recommendations the owner approved ("Can we do all 3?"): the conversion of the selection arc into one reviewable
piece.

**Contents.**
- **The note.** `note/selection_note.tex` is a self-contained 5-page note. `check.py` builds it into `note/selection_note.pdf`, which
  is git-ignored.
- **The review package.** A claims table with novelty and folklore risk, replay steps, and reviewer questions (`review_package.md`).
- **Three scripts.**
  - `replay.py` reruns the sixteen cited checks in a temporary copy.
  - `independent.py` recomputes nine claims in separately written code.
  - `check.py` ties the note to both.

## What the note states

The theorems are inherited from the cited proofs; the note adds no mathematical claim beyond them. `review_package.md` maps each
statement to its proof.

1. **The knot's coupling.** The knot's coupling dichotomy on its spaces (`KNOT-COUPLING-20261031-001`).
2. **Three places.** The five three-place classes, the pinning theorem, and the uniqueness of not-all-equal (`PINNING-20261031-001`).
3. **Parity.** The recorded correction of the parity claim, the six easy couplings of parity's family, and the hardness of parity's
   family on its failing class (`PARITY-CORRECTION-20261031-001`).
4. **Four places.**
   - Signed not-all-equal never fails for k ≥ 4.
   - The twenty four-place classes.
   - Links and NP-completeness for twelve classes.
   - The five weak classes left open.

   Sources: `FOUR-PLACE-20261031-001`, `FOUR-PREFER-20261101-001`.
5. **Composition.** Complementarity, and composition only through hubs (`KNOT-COMPOSE-20261101-001`).

## Evidence

- **`replay.py`.** It copies the sixteen cited proofs, every proof directory they import or bind (transitively), and every research file
  they read or bind. It reruns each check there and compares the fresh result with the frozen one, ignoring timings
  (`replay_result.json`).
- **`independent.py`.** It imports no repository library and recomputes nine claims:
  - the three- and four-place censuses;
  - the knot's coupling on Fano at the dimer point;
  - the theta identity on Fano at λ = 2;
  - parity's weight enumerator on Fano;
  - signed not-all-equal on the five-point 4-regular system (16⁵ signings);
  - complementarity for k ≤ 4;
  - the knot-against-hub cut of the 13-point splice;
  - the parity piece's determinant.
- **`check.py`.**
  - It ties seventeen quotations in the note to the frozen results and the independent recomputation.
  - It checks that every cited ticket, or its epic, is named.
  - It compiles the note and catches three tampering controls.

## Literature

Each result's provenance is in the note's provenance paragraph and in `review_package.md`.

## Status

- **Review.** Not externally reviewed.
- **Sharing.** Nothing has been sent; sharing is the owner's decision.
