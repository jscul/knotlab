# Closure of the geometry-from-a-law epic

Status: Proved

Epic `GEOMETRY-LAW-20261029-001` closed on 2026-10-29. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/GEOMETRY-LAW-20261029-001/geometry_from_a_law.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every connected loopless gadget of copies of a parity relation on three bits, with three free variables, gives back the parity relation. | Classical (linear algebra over GF(2)) | `GEOMETRY-LAW-20261029-001A-P001`, Theorem 1 |
| 2 | For every other relation on three bits whose pairs of coordinates are unconstrained, such gadgets exclude strictly fewer tuples: none without a wire face, at most one when two tuples at distance two are excluded (only the triangle of three copies), at most two when three are excluded. So the relation is never rebuilt, and repeated substitution reaches the full relation within three levels. | Candidate local delta (no overlap found in a bounded scan) | `…001A-P001`, Lemma 2, Theorem 3, Corollary 4 |
| 3 | No such three-bit relation has its coordinate symmetry group inside the rotations of a cyclic order, so placements never orient a vertex; 96 of the 742 four-bit analogues (6 classes) do. | Elementary; the four-bit count is computed | `…001A-P001`, Proposition 5; `…001B-P001`, Proposition 3 |
| 4 | Among the 106 classes of four-bit relations with every three coordinates unconstrained, gadgets of two and three copies rebuild exactly the even parity class, the odd parity class (odd numbers of copies) and the implication between parities of two complementary pairs (exactly the chains). Every other class loses excluded tuples, and no orienting class is rebuilt. | Candidate local delta (exhaustive census; larger gadgets sampled) | `GEOMETRY-LAW-20261029-001B-P001`, Theorem 1 and Proposition 2 |
| 5 | A set-level Boolean law glued natively fixes topology and curvature type but nothing geometric that survives patterns of patterns: the survivors are shapeless (parity) or one-dimensional (pairwise chains). | Synthesis | Conclusions 1–4; decision note |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- that geometry might follow once a law fixes topology (refined: only curvature type, and nothing geometric survives patterns of
  patterns);
- that three-place knots can carry an orientation (false; it needs four places and does not survive);
- that counting hidden witnesses might supply what sets lack (not under substitution, in scoping).

## Recommendation

**Research directions: a bounded comparison of two ways forward.**
- **Hubs with counts.** Can a law fix a dimension through self-duality, with nothing drawn but a substitution rule? First
  discriminator: fair contacts on self-dual hierarchical substitutions (the Wheatstone bridge, critical at 1/2) against
  non-self-dual ones (the diamond, critical at (√5 − 1)/2).
- **The universally influential cycles.** Make "only parity survives every coarse-graining" precise for infinite towers
  (question 7).
- **Interest:** 2/3. The main uncertainty: hierarchical-lattice percolation is classical, and hubs sit outside native contact.
- **Owner's decision:** whether hub laws are in scope.
- **Execution:** deferred to the owner.
