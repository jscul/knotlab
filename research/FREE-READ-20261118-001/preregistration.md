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

- `TREE-STEPS-20261118-001`, `CUMULANT-DIST-20261118-001` — same question (one distance for both laws): the cumulant distances, and the
  false comparison with bond distance corrected the same day. This study replaces that comparison with a proof.
- `DISTANCE-ORDER-20261117-001` — τ = steps apart on not-all-equal trees; the correlation side of the comparison.
- `RULER-20261111-001` — same reading on another base: bond distance is steps apart + 1 on the endless six-regular weave under
  not-all-equal (proved). This study proves the same on every knot tree of either law.
- `RULER-FLAT-20261111-001`, `LONG-LOOP-20261111-001` — bond distance on finite weaves (relatives).
- `PARITY-MIX-20261112-001` — unrelated (parity stitches among harmony copies).

## Settled by construction (proof in ticket A)

- **Upper bound.** On a knot tree with a path x = v₀, K₁, v₁, …, K_k, v_k = y, let p_j be K_j's third distinction. S = {x, y, p₁, …, p_k}
  is a bond: forgetting any member frees the chain (a knot with a free third distinction leaves its other two free, by K2), and S
  itself is constrained, since choosing each not-all-equal p_j equal to the value forced on v_{j−1} forces every v_j (parity forces it
  always), so y is forced. So bond distance ≤ k + 1. (Betweenness is not-all-equal after a switch, and bonds are switching invariant.)
- **Lower bound.** If a bond S holding x and y missed the third branch of some path knot K_j, forgetting that branch leaves K_j's two
  path distinctions free of each other (K2), so S's projection is a product of the projections of its two sides; S constrained then
  forces one side, a proper subset, to be constrained, against K2 for S. So S meets all k third branches and |S| ≥ k + 2.
- So bond distance = steps apart + 1 on every knot tree of parity, not-all-equal and betweenness knots. The lower bound uses only K2,
  so bond distance ≥ steps apart + 1 on every tree of any three-place knots; equality needs the path chain to be constrained, which
  fails for the clause "not all ones" (forbid 111, K1 and K2 hold): setting the shared distinctions to 0 satisfies the chain, so no
  bond holds its ends (the advisor's counterexample; a negative control, P6).
- Missing lemmas, now stated (advisor): the base projected onto the path's distinctions is the chain's own solution set (hanging
  subtrees extend any value, by K2); forgetting x or y frees S by greedy extension from the other end; "third branch" means the whole
  subtree hanging at p_j. On the mixed cycle, {x, y, z}
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
| P4b | (advisor) alternating rings: bond distance − 1 = steps apart on every pair | any differs |
| P5 | What correlation adds: on every not-all-equal ring τ = −log₃ \|C\| differs from bond distance − 1 by more than 0.01 on some pair | some ring with none |
| P6 | Negative control: on chains of two to four "not all ones" clauses, no bond holds the chain's two ends | a bond found |

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 152 cases at six knots (19 shapes × 8 blocks), 80 random trees and one case of cycles and
clause chains;
`merge.py` scores. Registered as FREE-READ-B1. One run; no change after seeing results; later looks labelled post hoc. Stop at the
read-out, the proof, the referee hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` was asked before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It confirmed both halves of the proof with three lemmas
made explicit, showed the theorem is not law-independent (the clause counterexample, now P6), confirmed P3 (δ = 1 − log₃(1 − 9^(−k))
there) and P4, strengthened P4's alternating clause to equality (P4b), asked for a tolerance in P5, and named the literature:
bonds are the minimal non-shattered sets (Sauer–Shelah, Pajor; shattering-extremal families), and the product lemma is the acyclic
join-tree decomposition (Beeri, Fagin, Maier and Yannakakis 1983; Freuder 1982). It knows no published statement of the tree theorem.
