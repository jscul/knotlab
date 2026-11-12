# Referee job TRAVEL-READ-R1: the brief

The coordinator handed this job over on 2026-11-12 (12:03 UTC), with an update at 12:24 UTC. It comes from the knots-alone thread:
`TRAVEL-READ-20261112-001`, closed with commits e50c5121c and e8fcf8b56. Everything in it is computed, and nothing new is proved.

## Claims under review

- **T1, rank.** At r = 4 and 5, 70 of 108 bases have rank 2, and 65 of those share a common pattern. Across all r, 35 of 169 bases
  travel along all ten shifts.
- **T2, bounded across.** 56 of 66 rank-1 bases are bounded across, 2 grow across, and 8 are undecided.
- **T3.** 99 of 104 bases have the same b at α = 14 as at α = 10.
- **T4.** 77 of 103 bases meet the ring criterion.

## The risk the owning thread flagged

Window bonds are not certificates. Only 296 of the 650 bonds are certified.

## The update

The owning thread rechecked its result (FAR-BOUND-20261112-001). On certified bonds, T2 narrows to 34 of 66. The recheck also
introduces a new certificate, eventually periodic strips, and a proof that holds on one base.

## Questions

- **(i)** Does the headline survive on certified bonds only?
- **(ii)** Were the class thresholds frozen before the census ran?
- **(iii)** Is "bounded across" forced, either by a second unlengthened shift or by definition?
- **(iv)** Use a method independent of the larger-window recheck.

Also referee the narrowed claim and the new certificate.
