# Bounded scan: where hardness lives

Date 2026-10-24. Scope: one bounded idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and
enter claims only as cited hypotheses, never as admitted evidence.

## Question

Hub-free networks of three-place knots are constraint problems in which every variable occurs in exactly two constraints. What is known
about their complexity, and about the effect of letting a variable occur three times?

## Query families

- Boolean edge constraint problems, delta-matroids and Feder's fan-out theorem.
- The full text of Kazda, Kolmogorov and Rolinek: definitions of even-neighbours, reachability and coverability; Theorems 7, 8 and 11;
  Proposition 52.
- The general factor problem: degree sets with gaps.
- Planar counting dichotomies, for a possible later counting question.

## Sources and relevance

| Source | Relevance |
| --- | --- |
| Feder, "Fanout limitations on constraint systems", Theoret. Comput. Sci. 255 (2001), as stated in KKR Theorem 7 | With constants, if CSP(Γ) is NP-hard and some relation is not a delta-matroid, then the edge problem is NP-hard. |
| [Kazda, Kolmogorov, Rolinek, "Even delta-matroids and the complexity of planar Boolean CSPs", arXiv:1602.03124](https://arxiv.org/abs/1602.03124) (ACM Trans. Algorithms 2019) | Theorem 8: edge problems with even delta-matroids are polynomial. Theorem 11: so are edge problems with efficiently coverable delta-matroids. Definition 10 defines coverable. Coverable delta-matroids are closed under gadgets. Not all delta-matroids are coverable, and no example is given. |
| [Faster algorithms on linear delta-matroids, arXiv:2402.11596](https://arxiv.org/abs/2402.11596) | The current landscape: the general delta-matroid edge problem is open. |
| [Degree two approximate Boolean #CSPs, arXiv:1204.5714](https://arxiv.org/abs/1204.5714) | Fan-out constructions adapted to counting; delta-matroids need special handling. |
| [Degrees and gaps: general factor problems, arXiv:2105.08980](https://arxiv.org/abs/2105.08980); [weighted general factors, arXiv:2301.11761](https://arxiv.org/abs/2301.11761) | General factor: polynomial when every degree set has gaps of length at most one (Cornuejols 1988); NP-complete with the degree set {0, 3} (Lovasz 1972). |
| [Cai, Lu, Xia, arXiv:1008.0683](https://arxiv.org/abs/1008.0683); [arXiv:1212.2284](https://arxiv.org/abs/1212.2284); [Cai, Fu, arXiv:1603.07046](https://arxiv.org/abs/1603.07046); [Fu, arXiv:1707.00373](https://arxiv.org/abs/1707.00373) | Planar Boolean counting: three classes (tractable, planar-only via matchgates, hard). Relevant if emergence (a log-count) is studied on surfaces. |

## Imported ideas and local discriminators

- **A hub is the all-equal relation on three places.** It is not a delta-matroid. As a degree set it is {0, 3}, Lovasz's hard case.
- **Discriminators.** Which of the 34 knots are delta-matroids, which are even, and which are coverable by Definition 10? All are
  finite checks on three places.

## Overlaps and barriers

- **The tractability and hardness statements are classical:** Feder, Kazda–Kolmogorov–Rolinek, Lovasz, Cornuejols. The local
  contribution is the census of the program's knots and the reading.
- **Two open problems lie outside the knots.** The general delta-matroid edge problem is open, but not needed if every knot is
  coverable. Counting on surfaces is governed by the planar dichotomy.

## Effect on selection

- Ticket A: the census and conditional statements, with the cited theorems as hypotheses.
- Ticket B: resolution hardness without hubs, through the parity gadgets of `SURFACE-GLUING-20261024-001B`.

## Novelty status

- `known-overlap-found` for the complexity statements.
- The census ("all 155 nonempty three-place delta-matroids are coverable") is `no-overlap-in-bounded-search`. It may well be implicit
  in the literature; this is not a novelty claim.
