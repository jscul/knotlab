# Closure of the open-end growth epic

Status: Proved

Ticket `OPEN-END-GROWTH-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new
  claim.
- **The decision note** is `research/OPEN-END-GROWTH-20261107-001/open_end_growth.md`.

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): open ends are now loose ends and threads chains, a two-sided cut one connected on both sides, and a small world a
small-world pattern. The mathematics is
unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Of five growth rules acting only at the free ends of a growing degree-3 parity system, growth at vertices holding two free ends gives a path (bond distance linear, dimension one). Random sprouting gives a tree. Greedy closing splits the system into parts joined by pinned edges. Closing without pins or ties gives a strip with bounded bond distance. Flat-face closing gives a small-world pattern. | exploratory experiment | A |
| 2 | In a Tseitin system with an unconstrained outside vertex, the least circuit through two edges is the least cut with both sides connected. A side with one cut edge and no free ends pins that edge and splits the system; cuts connected on both sides are circuits, so long regions with short boundaries are shortcuts. | classical core (bonds); reading new; proved | B |
| 3 | Growth at vertices holding at least two free ends always produces a path, with circuit size = vertices on the path + 2. | elementary; proved | B |
| 4 | In the tensor product of two binary codes, an L-shaped set (K1 × {q′}) Δ ({p} × K2) is a minimal dual codeword. For the product of two chain codes the finitely supported codewords are dense, so the product splits and its least circuits grow like taxicab distance, with quadratic balls. | delta new as far as found; proved | C |
| 5 | Conjecture: in a chain product, the least circuit through two entries has exactly |K1| + |K2| − 2 elements for the least axis circuits K1 and K2. That is bond distance δ1 + δ2 − 1. | conjecture; 855 pairs | C |

## Answer

- **A native rule grows the logical number line.** Local closing rules freeze, collapse or branch.
- **The Cartesian plane** is the product of two grown lines: a taxicab plane of dimension two, read from
  allowed states.

## Pending the owner

- **Carried.** Whether a native knot must also be natively bound (LOGIC-AXIS-20261107-001).
- **Carried from earlier epics.**
  - PHASE-HALO and FACE-CLAIM qualifications.
  - The SELECTION-NOTE erratum.
  - Superseding KNOT-COMPOSE D001.
  - Counted length as a native magnitude.

## Recommendation

**Continue** (2/3), as a fresh epic: circles from logic.
- **The question.** Can bond balls become round?
- **The plan.** Map the large-scale form of bond distance in shift-invariant laws without ends, where
  polygons are expected, and in random local laws, where roundness could appear only as a trend.
- **Alternatives.** Dimension under products of k lines (1/3); the exact taxicab formula (1/3).

The table is in the decision note.
