# What rule do two joined rings of knots grow by? Pre-registration

Epic `RING-PAIR-20261119-001` (`JOIN-GROWTH-20261118-001#1`, the coordinator's go-ahead; goal G17), 2026-11-19. Written after the
model below was found and checked on recorded growths (disclosed: all of that is fitting), before any start of the test was grown.
The canonical K1–K3 test is unchanged. "Growth" counts junctions by round.

## The question

Two joined rings of knots grow under the cheapest parity counts with a non-rational series (`JOIN-GROWTH-20261118-001`). Is there
an exact rule, a "menu that contains itself", that predicts every round of every such growth, including joins never grown?

## The model (found before the freeze; fitting)

The **candidate map** of a bare start (`JOIN-GROWTH-20261118-001`'s convention):
- its points are the knots;
- for every knot w, the knots sharing a distinction with w are pairwise candidates through w, and the map joins them all at
  once (one block per knot with two or more neighbours);
- each surplus distinction at a knot r adds a point joined to r alone.

The **unrolled map** is the map's universal cover. Every cycle of blocks is opened out, so it is a tree of blocks; a single ring
unrolls to a line, and two joined rings to an endlessly branching tree.

**Model H.** The junctions made in round t are the connected clusters of t + 1 points of the unrolled map that contain a knot,
counted once for each way of placing them on the start (deck orbits). In standard terms: connected vertex sets of the universal
cover of a block complex, by orbit under its deck group.

**Its series.** The cover is a tree of blocks, so the clusters are counted by a recursion in which each entry into a block refers
to the same kinds of entries further out:
- U(B, z) = y Π_{B' ∋ z, B' ≠ B} Φ(B', z), with Φ(B, z) = Π_{w ∈ B, w ≠ z} (1 + U(B, w));
- C(y) = Σ_x y Π_{B ∋ x} Φ(B, x) − Σ_B Σ_{S ⊆ B, |S| ≥ 2} (|S| − 1) Π_{v ∈ S} U(B, v) = Σ_t c(t) y^(t+1), by the dissymmetry of
  block trees.

The system is polynomial with positive coefficients, so C is algebraic, and rational when the map has at most one independent
cycle.

**Scope.** H is claimed only where:
- every knot has shared + round-1 demand ≥ 3 (no distinction from the floor);
- every listed surplus distinction is at a knot of demand ≥ 2;
- round 1 has no group of three;
- no two knots have two common neighbours.

**Checked before the freeze** (`pilot/`, `checks.py`):
- exact at every grown round on the seven two-ring joins of `JOIN-GROWTH-20261118-001` (13 to 17 rounds; one is its pilot);
- exact on all 36 of its census starts in the scope;
- different from round 1 on all 100 outside the scope;
- a brute-force count of clusters on the cover agrees to size 9;
- the rates, as 1/radius of the system: 5–5 by a distinction 2.6075, through a shared knot 2.8683, a path of one knot 2.4271, with
  a surplus distinction 2.6881; 5–7 2.3816, 5–9 2.2412, 7–7 2.1855;
- on the model's series to round 220, (c(t)/c(t − 1)) (t/(t − 1))^(5/2) settles at the rate: c ≈ C λ^t t^(−5/2) (published as a
  correction to `JOIN-GROWTH-20261118-001`, which had read t^(−3/2) from 17 rounds).

## Prior work in the program

`python3 -B scripts/track.py objects "two joined rings of knots exact growth series cheapest parity" --until 2026-11-19 --exclude RING-PAIR-20261119-001`
`python3 -B scripts/track.py objects "lattice animals connected subgraphs universal cover algebraic generating function" --until 2026-11-19 --exclude RING-PAIR-20261119-001`
`python3 -B scripts/track.py objects "candidate map clusters of knots unrolled growth model" --until 2026-11-19 --exclude RING-PAIR-20261119-001`

- `JOIN-GROWTH-20261118-001` — the same object (two joined rings, and single rings with adjuncts); this study gives their growth an
  exact model, and its product and nested laws are the model's one-cycle case.
- `RING-FORMULA-20261118-001` — a relative: the rate of every odd ring; in the model the unrolled ring is a line and the formula is
  the count of its clusters with surplus points.
- `NAE-METRIC-20261118-001` — unrelated object (bond distance on joints and rings).
- `QUADRATIC-ROUTE-TRANSFER-20261115-001` — unrelated (proof-system substitution).
- `LEIBNIZ-BOARDS-20261110-001` — unrelated (a board that is a three-cycle with trees attached).
- `BARE-NAMES-20261110-001` — unrelated (boards on abstract names).
- `PLACE-FLIP-20261110-001` — unrelated (board knots on four-regular tree boards).
- `TRUE-RATE-20261113-001` — unrelated (least-bond rates).
- `LEVEL-RETURN-20261113-001` — unrelated (addressed patterns).
- `LAW-RIGIDITY-20261112-001` — unrelated.
- `RING-GROWTH-20261118-001` — a relative: the (v, S) model of one ring, which is H on a line.
- `FRESH-COUNT-20261118-001` — a relative: one seed's growth is the down-closed sets of its descent order (Birkhoff); H is the
  counterpart for starts with cycles.

## Prior work outside the program

Cited once:
- lattice animals on the Bethe lattice, whose exponent θ = 5/2 is this t^(−5/2) (Fisher and Essam, J. Math. Phys. 2, 1961;
  Lubensky and Isaacson, Phys. Rev. A 20, 1979);
- animals on non-amenable graphs (Madras and Wu, 2010);
- block trees and dissymmetry (Otter 1948; Harary and Uhlenbeck 1953; Bergeron, Labelle and Leroux, *Combinatorial Species and
  Tree-like Structures*, 1998, ch. 4);
- positive polynomial systems and their square-root singularity (Drmota 1997; Lalley 1993; Woods 1997; Flajolet and Sedgewick
  2009, VII.5–VII.6; Banderier and Drmota 2015 for systems that are not strongly connected);
- free groups acting freely on trees (Bass–Serre).

What this adds, if P1 holds: the identification of the joining rule's rounds with this count, not the count itself.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | `checks.py` passes (G1–G3 as above; G4, the advisor's identity: the rooted count's coefficient of y^(t+1) is (t + 1) c(t)) | any check fails |
| P1 | on each of the 17 fresh starts in `fresh.starts()`, the grown counts equal H's at every round grown (80 rounds, 250,000 junctions or 900 seconds): F01–F15, and the advisor's two falsifiers F16 (a ring of eight with lone knots on knots 1, 3, 5, 7: two windings that never meet) and F17 (two rings of five sharing a knot, plus a path of three knots between them: a cycle of eight in the knot–distinction graph, the shortest the scope allows) | any start differs at any round |
| — | the three starts of `fresh.outside()` (groups of three in round 1) are grown and reported, with no prediction | — |

The model's counts for the first rounds are printed by `fresh.py` and recorded in the results; every number is fixed by the frozen
code before any test start is grown.

## Runs and stop rule

`job.py` through the shared runner, 3 workers, 4 GB per case; `merge.py` scores. Under an hour, registered in the long-running index. Stop at the read-out.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **Counting half.** It found it sound: two blocks share at most one point, so the cover is a tree and the deck group free. It
  gave the rooted identity, which is now gate G4, and derived −5/2 from it.
- **Growth half.** It outlined a proof: round = size − 1; parents = the set less a non-cut point; groups = the full parent set of
  each cluster. It named the groups step as the weakest. Its reading is that the scope's last two conditions say every deck element
  moves a cluster by at least four, that is, the knot–distinction graph has no cycle of length 3, 4 or 6. That reading is recorded,
  not tested.
- **Falsifiers.** It proposed F16 and F17, both added, and named F07 as the planned start most likely to fail.
- **Literature.** It gave the citations above.
- **Words.** For the owner: "self-similar (finitely many branch types)" is exact for two or more independent cycles, and "fractal"
  stays in quotation; the count does not show emergence.
