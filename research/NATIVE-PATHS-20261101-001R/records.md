# What the 2-edge cuts correct

Ticket `NATIVE-PATHS-20261101-001R` (documentation, no theorem), 2026-11-01.

## The error

- **What KNOT-COMPOSE claimed.** `KNOT-COMPOSE-20261101-001` concluded that the knot's spaces compose only through hubs (equality
  fan-outs).
- **Why it fails.** It classified 3-edge cuts and non-separating double cuts, but not the 2-edge cuts that separate a knot's space.
  `NATIVE-PATHS-20261101-001A` proves that across every nontrivial 2-edge cut one shore accepts exactly equality and the other exactly
  disequality: complementary two-place parity, with no hub. Such cuts occur in every odd cycle of Fano blocks, in the twisted cube, and
  in splices containing them.
- **A second inexactness.** The 3-edge statement "exactly not-all-equal and exactly equality" holds only up to an exchange of colours on
  some channels. The point side accepts one antipodal pair {v, v̄} and the line side its complement (A, item 3).
  - The cited point lemma applies to the piece H_X(τ) with a sign pattern τ, and KNOT-COMPOSE's proof dropped τ.
  - Its check (5/5) tested only splice trees, where v = 000.

## What stands

- **The lemmas.**
  - The balance lemma.
  - The failure-across-a-cut lemma.
  - The complementarity lemma (KNOT-COMPOSE Lemma 3).
- **The other parts of Theorem 4.** The double-cut classification (4(2)) and the transpose (4(4)).
- **The parity statement.** "A failing hub-free composition is a parity composition" stands, and 2-edge cuts realize it at k = 2.
- **The knot-against-hub reading of 3-edge cuts**, up to signs.
- **The native-network verdict.** The knot's spaces do not form a hub-free contact network. Across 2-edge cuts there is no hub, but a
  two-place relation has no contact variable, so it fails the complete-contact gate instead.
- **The computations.**
  - Every check of KNOT-COMPOSE A reproduces on its own instances.
  - The note's replay of it stands.
  - The note's independent part I8 (the 13-point splice, a splice tree) stands as stated.

## Records

The quoted text of each location is confirmed by `records_check.py` (`records_check.txt`). Closed artifacts stay unedited.

| # | Location | Statement | Disposition |
| --- | --- | --- | --- |
| 1 | KNOT-COMPOSE A `proof.md`, title | "Knot's spaces compose only through hubs" | **Withdrawn.** They compose through hubs across 3-edge cuts and by two-place parity across 2-edge cuts (NATIVE-PATHS A). |
| 2 | KNOT-COMPOSE A `proof.md`, Theorem 4(1) | "the point side accepts exactly equality on its three ports" | **Corrected:** exactly one antipodal pair {v, v̄}, and the line side its complement (A, item 3). Exact (v = 000) in splice trees. |
| 3 | KNOT-COMPOSE A `proof.md`, proof of item 1 | "Both constant patterns occur, by complementation. So the point side accepts exactly equality." | **Corrected proof** in A: the piece H_X(τ) carries a sign pattern τ. |
| 4 | KNOT-COMPOSE A `proof.md`, Theorem 4(3) | "Every failing composition of the knot's spaces passes through a hub." | **Withdrawn**, with counterexamples: every odd cycle of Fano blocks, the twisted cube, the 3-cycle spliced into Fano. Its next sentence, that knot-to-knot failure is parity, **stands**. |
| 5 | KNOT-COMPOSE A `proof.md`, novelty | "Knot's spaces meet only through hubs; hub-free failure is parity" | **First half withdrawn**, second half **stands**. |
| 6 | KNOT-COMPOSE A `manifest.json`, title and claim | "compose only through hubs", "the point side exactly equality on its ports", "always meets a hub" | **Withdrawn and corrected** as in 1, 2 and 4. |
| 7 | KNOT-COMPOSE A `result.json`, claim and check 3's name | the same claim; check 3 named for every knot's space | **Claim corrected** as in 6. **Check 3 stands** on its instances (Fano and three splices, all splice trees). |
| 8 | KNOT-COMPOSE A `check.py`, docstring | "the knot's spaces compose only through hubs" | **Withdrawn** as in 1. |
| 9 | ticket KNOT-COMPOSE A: title, objective, status | "compose only through hubs"; "the point side exactly equality" | **Withdrawn and corrected** as in 1 and 2. |
| 10 | KNOT-COMPOSE B `reading.md`, gate row "No larger common hub" | "Every composition of knot's spaces passes through a hub, an equality on three channels." | **Corrected.** Across 3-edge cuts a hub. Across 2-edge cuts none, but the two-place parity there is not a complete contact. **The verdict stands** for both reasons. |
| 11 | ticket KNOT-COMPOSE B, status | "every composition meets an equality hub" | **Corrected** as in 10. |
| 12 | KNOT-COMPOSE `compose.md` | "Yes, natively, but always through hubs."; "That the knot's spaces meet only through hubs was found in no source checked." | **Withdrawn** as in 1. "A direct knot-to-knot relation with nothing between them exists only for parity" **stands**. |
| 13 | KNOT-COMPOSE Z `proof.md`, ledger row 2 | "the line side is exactly the knot and the point side exactly a hub" | **Corrected** as in 2. Row 3 **stands**. Row 5 **stands** with the second reason of 10. |
| 14 | ticket KNOT-COMPOSE (epic): title and status | "knots meet through hubs"; "compose natively, but only through hubs"; "the point side exactly a hub" | **Withdrawn and corrected** as in 1 and 2. |
| 15 | discovery record `KNOT-COMPOSE-20261101-001-D001` | title "The knot's spaces meet only through hubs"; "compose natively only through hubs" | **Superseded in substance** by `NATIVE-PATHS-20261101-001-D001`. Its status is left active, awaiting the owner (see below). |
| 16 | SELECTION-NOTE `selection_note.tex`, abstract item (5) | "compose only through hubs: across every small cut a knot meets an equality" | **Erratum.** Across 3-edge cuts a knot meets an equality up to signs; across 2-edge cuts the parts meet as two-place parity. |
| 17 | SELECTION-NOTE `selection_note.tex`, Section 6 title | "Composition: knots meet through hubs" | **Erratum**, as in 16. |
| 18 | SELECTION-NOTE `selection_note.tex`, Theorem 12 | "the point side exactly $\EQ$"; "compose only through hubs" | **Erratum**, as in 2 and 4. Lemma 11 (complementarity) **stands**. |
| 19 | SELECTION-NOTE `review_package.md`, claims row | "Complementarity; the knot's spaces compose only through hubs." | **Erratum**, as in 16. |
| 20 | SELECTION-NOTE `proof.md`, item 5 | "Complementarity, and composition only through hubs" | **Erratum**, as in 16. |
| 21 | SELECTION-NOTE `manifest.json` claim (copied in `result.json`), ticket status | "the knot's spaces compose only through hubs" | **Erratum**, as in 16. |
| 22 | `docs/KNOT_INTUITION.md`, composition entry | "So every failing composition of the knot's spaces passes through a hub" | **Corrected** by a dated note after this epic closes. |
| 23 | `docs/KNOT_INTUITION.md`, the line side and point side | "the point side exactly as one point (an equality hub)" | **Corrected** (up to signs) by the same note. |
| 24 | `docs/KNOT_INTUITION.md`, note entry | "the knot's spaces compose only through hubs." | **Corrected** by a dated note. |

**Outside the repository.** The session memory summary of the composition epic is updated.

**Generated views.** `docs/programs/topology.md` lists D001 under its title. It is rebuilt from the records and is not edited here.

## The note

- **Its other claims are unaffected:** (1) coupling, (2) mutual selection, (3) parity, (4) four places.
- **Recommendation.** Before the note is shared, reissue it with:
  - item (5) of the abstract, Section 6 and Theorem 12 corrected to the two-interface statement, including the signs;
  - the replay row for KNOT-COMPOSE A kept;
  - NATIVE-PATHS A cited for the correction.
- **Status.** Nothing has been sent, so no reader has the erroneous statement.

## Awaiting the owner

- **The status of D001.** It should be marked superseded, with its text preserved, by `NATIVE-PATHS-20261101-001-D001`.
- **Precedent.** The one earlier cross-epic supersession (commit `bb2bed541`, 2026-10-26) was made at the owner's request. So the status
  change is left to the owner.
- **Until then.** The new record states the correction.

## Search for other uses

`records_check.py` searches every tracked text file for the phrases "only through hubs", "meet through hubs", "meets an equality" and
"always through hubs". It finds them only in:
- the locations above;
- this epic's own records, which quote them;
- the generated program views.
