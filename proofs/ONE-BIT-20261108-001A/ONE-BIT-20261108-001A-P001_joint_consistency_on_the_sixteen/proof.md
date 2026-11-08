# Joint consistency on the sixteen one-bit candidates

Status: Proved. The reduction is ticket B of `ROUND-PRICE-20261108-001`; every finite statement here is computed exactly
(`check.py`, about five minutes with 16 workers; no collar reached the search budget).

Ticket `ONE-BIT-20261108-001A`, 2026-11-08.

## Standard statement

- **The question.** Sixteen ways of decorating the pinwheel tilings with one hidden bit per tile (eight up to exchanging the two
  labels) remain candidates for forcing the pinwheel by a local rule on labelled collars. Each one forces every parent's label;
  it would force the pinwheel if every labelled parent collar that can occur obeyed the rule again.
- **The result.** A joint consistency test, stronger than the pairwise one, still leaves labelled parent collars outside the rule
  for each of the sixteen: between 35 and 110 labelled pinwheel collars with labels the rule does not list, and between 13 and
  191 collars that are not pinwheel collars. So this route does not settle any of them.

## Nearest known result

- **Local consistency.** Arc consistency and its strengthening to all neighbours at once (pairwise, then path-like consistency) are
  standard constraint-propagation tests; a removed value cannot occur in any solution, a kept one may still be impossible.
- **The delta.** Their use on the decorated pinwheel's parent collars was not found in prior work (no-overlap-found).

## Terms

As in `ROUND-PRICE-20261108-001B`: the level-one law's arc-consistent core (156 collars per handedness), and Q(s), the labelled
core collars whose decorated cut gives every child a labelled collar of the law L(s).

- **The joint test.** A labelled collar (Y, p) of Q(s) passes when its neighbours can all be given surviving labelled collars
  that agree with p on the tiles they share with Y, and with each other:
  - each pair of neighbours' placed collars is compatible as two collars of one tiling (each lists the other's tiles that touch its
    centre, and no two distinct tiles overlap);
  - the pair agrees on the labels of shared tiles.
- **Iteration.** The test alternates with arc consistency until nothing changes.

## Lemma 1 (the test is sound)

A labelled collar of a tiling whose parents' labelled collars all lie in Q(s) passes the joint test: its neighbours' labelled
collars are collars of the same tiling. So Theorem 1 of `ROUND-PRICE-20261108-001B` holds with the joint test in place of arc
consistency: a decoration whose survivors all lie in L(s) forces the pinwheel. ∎

## Theorem 2 (the computation)

| s(0) | s(1) | Q(s) | After arc consistency | Survivors in L(s) | Keys outside L(s) | Non-keys |
| --- | --- | --- | --- | --- | --- | --- |
| 0 0 0 0 1 | 1 0 0 1 0 | 967 | 509 | 355 | 64 | 27 |
| 0 0 0 1 0 | 1 0 1 1 1 | 1,009 | 464 | 373 | 35 | 15 |
| 0 0 1 1 1 | 1 0 0 1 0 | 1,013 | 557 | 439 | 63 | 18 |
| 0 1 1 0 0 | 1 0 0 0 1 | 1,280 | 538 | 361 | 77 | 79 |
| 1 0 0 0 0 | 0 0 1 0 1 | 1,100 | 552 | 377 | 110 | 28 |
| 1 0 1 0 1 | 0 0 0 0 0 | 994 | 564 | 447 | 75 | 13 |
| 1 0 1 0 1 | 0 0 1 1 0 | 1,192 | 610 | 310 | 50 | 191 |
| 1 0 1 1 0 | 0 0 1 0 1 | 1,272 | 606 | 308 | 45 | 179 |

- **The joint test removes some.** Compared with arc consistency alone (`ROUND-PRICE-20261108-001B`), it removes up to 61 non-key
  survivors per decoration, but never all of the off-law ones.
- **So.** No decoration is shown to force the pinwheel by this route.

*Proof.* Computed: the neighbour-pair compatibilities (329,211 compatible pairs of placed collars, the same for every decoration),
Q(s) by enumeration, and the iterated test by exhaustive search over neighbour assignments; no collar reached the search budget. ∎

## What it says

- **Two kinds of survivor.** Most off-law survivors are pinwheel collars with labels the decoration does not produce. If they occur
  in planes at all, they are genuine pinwheel tilings with other labellings, which break the induction of the proof without giving
  a crystal. The non-key survivors are the ones a crystal would need.
- **The next discriminator** is therefore a search for a crystal, ticket B, and, if none appears, a test that tracks the
  undecorated geometry alone.

## The check

`check.py` computes everything above and writes `result.json`. Controls, each of which must hold:
- **The keys pass.** Every labelled key of each law survives the joint test.
- **The test can fail to settle.** The constant decoration (which admits the rhombus crystal) keeps 204 non-key survivors, and
  10001 / 01100 (which admits a period-4 brick crystal) keeps 79 keys outside its law and 26 non-keys.

## Nonclaims

- **Not a refutation.** Survivors of a local test need not occur in a plane; no decoration is shown to fail here.
- **Radius two.** Deeper consistency, or a test on geometry alone, may still settle some of the sixteen.
