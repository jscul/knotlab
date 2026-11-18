# Where the cumulant distance is steps apart, and a repair: pre-registration

Epic `TREE-STEPS-20261118-001` (`CUMULANT-DIST-20261118-001#1`; G1 and G16; tests A97; B200), 18 November 2026. Frozen before the
run. Code by the thread (Claude); the run through the shared runner. The canonical K1–K3 test is unchanged.

## The pivot, and why

The coordinator's go-ahead (07:28 UTC) was to prove that the cumulant distance δ is steps apart on every knot tree under any
mixture of the two laws. Asked for the lower bound before freezing, the advisor (claude-fable-5-2) showed it is false: the joint
cumulants of a fair coin grow factorially, and a not-all-equal tree with 32 knots hung on one distinction reaches a distinction 33
knots away for less than 33 (proved; checked here; logged as a Block in `docs/CORRECTIONS.md` on the reading "steps apart on every
knot tree"). The coordinator approved the pivot (07:37 UTC): where δ is steps apart, and a repaired distance. This contract records
it.

## The question

1. **Where δ holds.** How large must a hub be to shortcut, and does δ stay steps apart one size past the earlier computed range
   and on larger trees with few knots per distinction (the program's bases have at most six)?
2. **A repair.** The hub's shortcut uses a set that contains a smaller set already binding the pair. The knot test's K2 asks that a
   knot lose its binding when any one member is forgotten. Its cumulant form gives the irreducible-set distance:

   δ_K(x, y) = min over irreducible S ∋ x, y of (|S| − 2) + max(0, −log₃ |κ_S|),

   where S is irreducible when κ_S ≠ 0 and κ_T = 0 for every T with {x, y} ⊆ T ⊊ S. Is δ_K steps apart on every knot tree, with no
   hub exception?

## Prior work in the program

`python3 -B scripts/track.py objects "cumulant distance steps apart knot trees hubs irreducible sets" --until 2026-11-18 --exclude TREE-STEPS-20261118-001`
`python3 -B scripts/track.py objects "tangent numbers cumulants of a fair coin hub counterexample tree cumulants" --until 2026-11-18 --exclude TREE-STEPS-20261118-001`
`python3 -B scripts/track.py objects "knot trees parity not-all-equal mixed six knots random trees bounded degree" --until 2026-11-18 --exclude TREE-STEPS-20261118-001`

- `CUMULANT-DIST-20261118-001` — same object: δ, its proofs D0 to D6, its computed range (trees to five knots, mixed). This study
  extends the range one size and repairs the definition.
- `DISTANCE-ORDER-20261117-001` — τ = steps apart on not-all-equal trees (proved), used in K4.
- `MEET-ORDERS-20261118-001`, `GROW-FACE-20261110-001`, `LEVEL-REACH-20261114-001` — unrelated (matched on words).
- `WEAVE-MIX-20261117-001` — unrelated.

## Prior work outside the program

Cumulants of a fair coin are the tangent numbers (log cosh). Tree cumulants and L-cumulants (Zwiernik and Smith 2012; Zwiernik's
book) replace the partition lattice so that quantities factor along a tree. Irreducible correlations (Schneidman, Still, Berry and
Bialek 2003). Not found: an irreducible-set cumulant distance.

## Settled by construction (proofs in ticket A)

- **H1 (hub identity).** If σ is a uniform ±1 and u₁, …, u_n are independent of σ and of each other with means μ_i,
  κ(σu₁, …, σu_n) = κ_n(σ) ∏ μ_i. The two other distinctions of a not-all-equal knot hung on x both act as such copies (their joint
  conditional covariance is constant and drops out); a parity knot hung on x gives one exact copy for its two distinctions.
- **H2 (threshold).** A hub with 2j copies of s_x besides x and y gives κ = κ_{2j+2}(σ)·(−1/3)^{2j + k} (not-all-equal copies), so
  δ(x, y) < k exactly when log₃ |κ_{2j+2}(σ)| > 4j, first at 2j = 32: sixteen not-all-equal knots on one distinction (both their
  other distinctions in S), or thirty-two parity knots. A single hub on a distinction in at most fifteen knots never shortcuts.
- **K1.** If C(x, y) ≠ 0, {x, y} is the only irreducible set, so δ_K = τ.
- **K2.** On a parity base, irreducible sets through x and y are exactly the circuits through them (a non-circuit S with κ_S ≠ 0
  contains a circuit through x and y, by matroid connectivity), so δ_K = δ = bond distance − 1.
- **K3.** Every hub set contains a smaller set already binding the pair ({x, y} on a not-all-equal path, {x, y} with the path's
  parity third distinctions otherwise), so it is not irreducible: δ_K ignores hubs.
- **K4.** δ_K = steps apart on not-all-equal trees (K1 and τ = steps apart), on parity trees (K2 and D2), and on mixed trees whose
  path from x to y has no parity knot (K1). **Open:** mixed trees whose path has a parity knot; conjectured steps apart.

## Exploration disclosed

Before the freeze: the hub identity on (N, k) = (2, 1), (4, 1), (2, 2) with one child and (1, 1), (2, 1), (2, 2), (3, 1) with both
children (not-all-equal), and parity hubs of one and two knots; the coin's cumulants and the threshold N = 32; the gates on random
bases of up to seven distinctions. No tree of six knots or random tree of seven was read.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): `both` equals the earlier δ; δ_K ≥ δ; δ_K equals a brute-force irreducible search; the hub identity on small hubs; the coin's cumulants and the threshold 32 | any fails |
| P1 | On every knot tree with six knots (19 shapes) under every assignment of parity and not-all-equal (1,216 bases), δ = steps apart on every pair | any pair differs |
| P2 | On the same, δ_K = steps apart on every pair | any pair differs |
| P3 | On 80 random knot trees with seven knots, at most three knots per distinction and random laws, δ = δ_K = steps apart on every pair | any pair differs |
| P4 | δ and δ_K coincide on every pair of P1 and P3 (no hub on such trees can matter) | any pair differs |

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 76 cases at six knots (19 shapes × 4 blocks of 16 assignments) and 80 random trees; `merge.py`
scores. Registered as TREE-STEPS-B1. One run; no change after seeing results; later looks labelled post hoc. Stop at the read-out,
the proofs, the referee hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2): it found the counterexample (H1, H2), proved the parity-path lemma and the cases |S| ≤ 3, and
suggested tree cumulants or restricted sets as repairs. The irreducible-set repair (K1 to K4) is mine; the advisor was not asked
about it before the freeze.
