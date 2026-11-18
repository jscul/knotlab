You have NO tools and no shell: answer from analysis only and do not describe running code or files. Check the mathematics in the pre-registration below and the predictions; be concrete and brief.

Definitions: a base is a set of allowed 0/1 states; a bond is a set S of variables whose projection of the allowed states is not the full cube {0,1}^S (K1) while the projection onto every subset of size |S| - 1 is full (K2); bond distance(x, y) = (size of the least bond containing x and y) - 1. Knots are 3-place: parity (even sum), not-all-equal, betweenness (forbid a = c != b). A knot tree: the knot-variable incidence graph is a tree.

Questions: (1) Is the upper-bound argument right (S = {x, y, third distinctions of path knots} is a bond, constrained by the forcing choice, every proper subset free)? Check carefully that forgetting x or y frees S, and that forgetting a pendant p_j frees it for each law. (2) Is the lower-bound argument right (a bond must meet every path knot's third branch, because otherwise the projection of S is a product of its two sides)? Is the product claim exact for supports on a tree? (3) Does the theorem hold for any 3-place knot law satisfying K1-K3, or only these laws (the constraint of the composed chain might vanish)? Give a counterexample law if it fails. (4) Are predictions P3-P5 right: on the closed path (NAE path of k from x to y plus parity knot (x, y, z)), is delta (min over S of (|S|-2) - log3|kappa_S|, kappa the joint cumulant) at most 1.1, and delta_K (same over sets S with kappa_S != 0 and kappa_T = 0 for every {x,y} <= T < S) = k? On rings of knots, is bond distance - 1 = steps apart under NAE, = delta under parity, <= steps under alternating laws? (5) Known literature for this statement (minimal non-free sets of a relation; tree-structured CSPs; "bond" as circuit of a relation)? (6) Anything that would make this study more valuable.

# The distance that reads freedom: pre-registration

Epic `FREE-READ-20261118-001` (coordinator's go-ahead after `TREE-STEPS-20261118-001`'s referee; G1 and G16; tests A97; B200),
18 November 2026. Frozen before the run. Code by the thread (Claude); the run through the shared runner. The canonical K1–K3 test is
unchanged.

## The question, and the answer found while designing it

The go-ahead: on a mixed cycle (a not-all-equal path of k knots from x to y closed by a parity knot (x, y, z)) the irreducible-set
distance δ_K reads x and y as k steps apart, though {x, y, z} is a knot. Find a distance that reads freedom (the knot test's K2)
rather than zero correlation, agreeing with bond distance there and keeping the tree results, or prove none exists.

While designing it I checked bond distance itself: the size of the least set on which the allowed states form a knot (K1–K3:
constrained as a whole, every set of one fewer free), minus one. On all 2,686 pairs of every knot tree to four knots under every
mixture of parity and not-all-equal, bond distance is steps apart plus one, and on the mixed cycle it puts x and y at two (the
parity knot). It reads freedom by definition, ignores hubs (a hub's binding is a correlation, not a constraint) and is invariant
under switching values. So the distance asked for is bond distance. This study proves the tree statement, checks it one size past,
and compares freedom with correlation on cycles, where the readings part. It also corrected my earlier claim that bond distance
gives not-all-equal trees nothing (`docs/CORRECTIONS.md`, commit `01941028d`).

## In standard terms

Bonds are the minimal "obstructions" of the projected relation: a set whose projection is not the full cube while every proper
projection is (the literature's minimal non-free sets, the circuits of the relation's "freeness" structure). On a linear code they
are the circuits of the dual matroid.

## Prior work in the program

`python3 -B scripts/track.py objects "bond distance on knot trees steps apart freedom" --until 2026-11-18 --exclude FREE-READ-20261118-001`
`python3 -B scripts/track.py objects "bond distance ruler weave steps apart plus one" --until 2026-11-18 --exclude FREE-READ-20261118-001`
`python3 -B scripts/track.py objects "rings of knots mixed cycles parity not-all-equal correlation" --until 2026-11-18 --exclude FREE-READ-20261118-001`

PRIORWORK

## Settled by construction (proof in ticket A)

- **Upper bound.** On a knot tree with a path x = v₀, K₁, v₁, …, K_k, v_k = y, let p_j be K_j's third distinction. S = {x, y, p₁, …, p_k}
  is a bond: forgetting any member frees the chain (a knot with a free third distinction leaves its other two free, by K2), and S
  itself is constrained, since choosing each not-all-equal p_j equal to the value forced on v_{j−1} forces every v_j (parity forces it
  always), so y is forced. So bond distance ≤ k + 1. (Betweenness is not-all-equal after a switch, and bonds are switching invariant.)
- **Lower bound.** If a bond S holding x and y missed the third branch of some path knot K_j, forgetting that branch leaves K_j's two
  path distinctions free of each other (K2), so S's projection is a product of the projections of its two sides; S constrained then
  forces one side, a proper subset, to be constrained, against K2 for S. So S meets all k third branches and |S| ≥ k + 2.
- So bond distance = steps apart + 1 on every knot tree of parity, not-all-equal and betweenness knots. On the mixed cycle, {x, y, z}
  is a parity knot, so bond distance(x, y) = 2.
- On a parity base bond distance − 1 = δ (`CUMULANT-DIST-20261118-001A`, D1).

## Exploration disclosed

Before the freeze: bond distance on all trees to four knots (2,686 pairs) and on the mixed cycle at k = 2, 3; the gates. Earlier,
in `CUMULANT-DIST-20261118-001`, δ on rings of three to six knots under one law (its `rings` part) was seen.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): projection supports; one knot is a bond under each law; switching invariance; the path set is a bond on random P/N/B chains | any fails |
| P1 | Every six-knot tree under every law assignment (1,216 bases): bond distance = steps apart + 1 on every pair | any pair differs |
| P2 | 80 random seven-knot trees (≤ 3 knots per distinction, random laws): the same | any pair differs |
| P3 | Mixed cycles, k = 2 to 5: bond distance − 1 = 1 for x, y; δ_K = k; δ ≤ 1.1 | any fails |
| P4 | Rings of three to six knots: under parity bond distance − 1 = δ on every pair; under not-all-equal bond distance − 1 = steps apart on every pair; alternating, bond distance − 1 ≤ steps apart | any fails |
| P5 | What correlation adds: on every not-all-equal ring τ differs from bond distance − 1 on some pair | some ring with none |

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 152 cases at six knots (19 shapes × 8 blocks), 80 random trees and one case of cycles;
`merge.py` scores. Registered as FREE-READ-B1. One run; no change after seeing results; later looks labelled post hoc. Stop at the
read-out, the proof, the referee hand-off and the report.

Advisor. Not consulted for this study: the answer was found by a direct check and the proof is short; the referee will read it cold.
