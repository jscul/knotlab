# Nativeness up to renaming

Epic `PLACE-FLIP-20261110-001` (program topology, group `spacing`, `BARE-NAMES-20261110-001` direction 1, the challenge of A59, G1),
2026-11-10. Pre-registered in commit 75f8e2b79, with the definition of a flip in place, the mark and ticket B's census frozen there.

## The question

- **Where it comes from.** `BARE-NAMES-20261110-001` found that without letters a board changes by finite switches, and that in 90
  one-bit count laws a neighbour distinction knots with its two endpoint values. But exchanging finitely many names is also a finite
  change, so under abstract names the source-aware condition excludes nothing (A59). The coordinator's go-ahead of 18:43 UTC took
  the challenge: count changes up to renaming, with the definition frozen first.
- **The question.** Are the 90 knots still native when renamings do not count?

## The question in standard terms

For vertex-coloured 4-regular graphs obeying a local rule, taken as infinite disjoint unions of finite graphs or as universal covers:
which colourings admit a finite recolouring that no automorphism induces, and which edges a finite rewiring can change while the
rule holds.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Excluding renamings is not enough.** A place can be transplanted, cut out of one region and wired into another, by a finite change that is no renaming. So the frozen count holds the board fixed while values change, and the values fixed while neighbour distinctions change: flips in place. | proved | A (L4) |
| 2 | **In worlds of finite pieces every knot is native in place.** A change of values on one copy of a board is a renaming exactly when the new colouring is an automorphic image of the old one. All 90 knots are native in place in some world of copies of a finite board: 84 on frozen boards, and 6 on boards found by hand (2-lifts of the 3 × 3 torus, and a 21-place board with no automorphism). | proved; computed, exact | A (L1), B |
| 3 | **The neighbour distinction is always flipped in place.** The switch changes the board itself, joining two copies into a double cover or closing a cycle on a tree, with every value kept. | proved | A (L3) |
| 4 | **On the free board most values are rigid.** In a tree world no change of values is a renaming, so the only question is whether a finite recolouring exists, and least fixed points decide it. 26 knots are native in place in some tree world. The other 64 are not native in place in any: in 58 laws no value can flip by any finite change, among them the 31 that never put a 0 beside a 1 and law 48, where every flipped place forces all four of its neighbours to flip; in 6 a value can flip, but never at both ends of an edge. | proved (the fixed points; the cascades by hand), computed | A (L2, L5, L6), B |
| 5 | **The predictions.** C1 failed: laws 40 and 80 have no two-valued colouring on any frozen board. C2 failed for six laws without a frozen world of finite pieces, all six settled by hand. C3 held. | prediction failed; settled by hand | B |

## Answer

Yes, with a split. Excluding renamings alone changes little, because a place can be transplanted, so the count that means something
holds one kind of distinction fixed while the other changes. Under that count all 90 board-value knots are native in place in some
world made of finite pieces, so none of them rests on renamings, and A59 is confirmed for these knots. On the free board, a tree
world, renamings play no part, and the knots split: 26 are native in place, and 64 are not, in 58 laws because no value can change
by any finite change at all. The freedom comes from finite pieces; the infinite free board freezes most values.

## Reading

**Interpretation, not a theorem.**
- **Where the freedom comes from.** In a world of finite pieces a whole piece can be recoloured at finite cost. On the free board a
  recolouring has to stop somewhere, and for 58 laws it never can. So a knot's being native in place depends on the world having
  finite pieces.
- **Two kinds of distinction.** Neighbour distinctions are always native in place, through the switch. Values are native in place only
  where finite pieces or local freedom allow it.
- **For the owner's idea.** Without letters the board is itself a native distinction everywhere. The values on it are native in a dust
  of finite worlds, but frozen on the free board for most laws.
- **For the foundation, a question and not a proposal.** The source-aware reading as written cannot tell a renaming from a change.
  The count frozen here, one kind of distinction at a time and no renamings, is one way to read it under abstract names, recorded as
  assumption A60. Whether the canonical reading should say so is for the owner; this epic proposes no change.
- **Nothing here is a length.**

## Lag cutoffs and census-only claims

- **Exact.** L1 to L6 are proved. The marks in worlds of finite pieces are exact, every witness re-verified by independent code. The
  marks in tree worlds are exact for every tree world (the type-level and joint fixed points), and agree with the frozen covers.
- **Census-only.** The counts.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| L1 to L6 (proved) | — (proofs) | read by an independent referee before publication (see "Review") |
| The marks in worlds of finite pieces | every witness re-verified by brute force, with networkx's coloured isomorphism instead of the census's automorphism code | passed for all 90 |
| The census's tree marks, within distance 2 (frozen) | the exact fixed points, at any distance and over every tree world | 8 more laws native in place, 26 in all; none of the census's flips contradicted; the joint fixed point finds the same 26 |

## Review

An independent referee, a fresh Claude agent given only ticket A's proof, read it before publication on 2026-11-10.
- **Verdict.** L1 to L6 hold. Its own computations agreed: the depth-2 fixed point matched brute force on 1,326 roots, and every value
  flipped in a cover was one the type level allowed.
- **Changes asked for and made.**
  - L2 holds for four-regular trees (with leaves, two leaves can be exchanged), and degree four is now in the setting.
  - L3's minimality step said a place is left with three neighbours; it is a place whose number of neighbours is not four. Its
    hypotheses are written out, and a partner edge that closes a cycle is shown to exist in every cover.
  - The transplant's hypotheses (two non-adjacent pairs, two disjoint edges) and, on trees, its cycle are written out.
  - L5 got a simpler argument (the flipped places form whole components) and its hypothesis on T.
  - L6's part 2 needed the old values to add up to each count, and a reason the base case is sound; L6 is now tied to flips in place.
  - It proposed a joint recursion over two changes on one tree, which this epic ran (L6, part 3): it settles the six laws left open,
    none native in place on any tree.

## Literature and provenance

- **Sources.** Covering graphs; least fixed points over finite state sets; automorphism groups by the VF2 matcher (networkx); the
  2-switch of graph theory.
- **Classification.** Elementary; folklore risk high for every lemma. The reading for the board line is this epic's.

## Workspace assumptions

- **Challenged.** A59, by design. C2 failed as frozen, but the six laws it left were all native in place in worlds found by hand. So no
  knot is native only through renamings, the frozen rule's condition for A59 staying Assumed is not met, and A59 becomes Confirmed for
  these knots.
- **Bearing on A53.** Its challenge, counting changes per place with the board fixed, is the count frozen here. Its answer: yes in
  worlds of finite pieces; on the free board, for 58 laws, no.
- **Added.** A60, nativeness under abstract names is counted in place (a reading, Assumed).

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (L1 to L6 and the check) and ticket B (the census), with the by-hand examination of six laws.
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**), found while this epic's control was chosen.
`BARE-NAMES-20261110-001B`'s frozen contract says "No law of the family was run" before freezing, but its control, law 63 ("no
adjacent 1s"), is in the family. The control's run and result were disclosed in the same contract, and the frozen run agreed with
them, so no result changes.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — nativeness up to renaming | **Status:** Successful | Every board-value knot is native in place in some world of finite pieces, so none rests on renamings; on the free board 26 are native in place and 64 are not. C1 and C2 failed as frozen and were settled by hand |
| Local direction — boards made of distinctions | Obstruction confirmed | Nativeness, the open part of the line, is settled: the board is native without letters, its values only in finite pieces; forcing the plane is untouched |
| Broader exploration — question 9 | Known alternatives | Growth (accretion laws) is the one route this line has not tried |
| Long-term goal — G1 Space from a law | Obstruction learned | Static laws, with or without letters, force the plane only by naming a face |

**Corrections:** one, Not a block (`BARE-NAMES-20261110-001B`'s contract said no law of the family was run, but its control is in the
family). **Goals:** a G1 checkpoint (obstruction learned); BARE-NAMES-20261110-001#1 taken. **Assumptions:** A59 Confirmed for these
knots; A60 added (nativeness under abstract names counted in place); A53's history records the answer to its challenge.

- **What the attempt leaves open.** Nothing within its question: every one of the 90 knots has its mark in both kinds of world.
- **Would anything left change the line's verdict?** Of the line's basket, only growth could: every static route tried, with letters
  and without, forces the plane only by naming a face. Leibniz's rule with abstract names could at most force one connected world;
  edge labels (B16) and a growing radius would restate the verdict.

**Next step:** Research directions — selected: #1 (WEAK-APER-20261110-001#2), unless the coordinator redirects the line.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Every accretion law (WEAK-APER-20261110-001#2) | 2/3 — Substantial | 2/3 — Testable | As recorded there | Selected · not started |
| 2 | Leibniz's rule with abstract names (BARE-NAMES-20261110-001#2) | 1/3 — Modest | 2/3 — Testable | As recorded there | Alternative · not started |

1. **Accretion laws.** Payoff 2: growth is the one route left that could change the verdict, since every static law tried needs a
   named face. Concreteness 2: as rated there.
2. **Leibniz's rule with abstract names.** Payoff lowered to 1: it could force one connected world, but not the plane without a named
   face. Concreteness 2: as rated there.

**Recommendation.** Research directions, selected #1, the only item in the line's basket that could change its verdict; the
coordinator may prefer to redirect the line, and nothing else in this basket would be lost by it.
