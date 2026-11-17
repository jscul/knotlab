# Bonds in exactly projected pieces: an orbit and a block, and stems

`CARRIER-20261117-001A-P001`, epic `CARRIER-20261117-001`, 2026-11-17. Written by Claude. The advisor model was consulted on the
repaired conjecture and the word "stem" (`research/CARRIER-20261117-001/advisor/head_answer.md`). Checks: `check.py`, with its result
in `result.json`, and the gates of `research/CARRIER-20261117-001/` (`gate_two_block.json`, `gate_head.json`). The setting is that of
Theorems W, F and K
([W](../../DIRECT-REACH-20261115-001B/DIRECT-REACH-20261115-001B-P001_every_depth/proof.md),
[F](../../BLOCK-REACH-20261116-001A/BLOCK-REACH-20261116-001A-P001_forgetting_blocks/proof.md),
[K](../../KEEP-REACH-20261117-001A/KEEP-REACH-20261117-001A-P001_two_orbit/proof.md)):
- addressed not-all-equal patterns whose blocks of orbits meet only a block and the one above it;
- with orbits of at most four addresses, finitely many types and exact projections;
- L_N(k, s) is the least bond of P_N meeting level k and level k + s.

*Words.* The **block** of an orbit O is O with its child orbits one level down (glossary). For an orbit O_u at level k and an orbit
O_v at level k + s, the **stem of depth d** of the pair is O_u with O_v's ancestor orbits at levels k + 1, ..., k + d (the advisor's
word; the code calls it the head). When O_v descends from O_u, the stem is the start of the line of orbits from O_u to O_v. An
**orbit-and-block bond** is a bond inside O_u and the block of O_v containing a distinction of O_u and one of O_v; a **stem bond** is
a bond inside the stem and O_v containing a distinction of O_u and one of O_v.

## Lemma P (the two pieces project exactly)

*Let r = N − k − s. (a) The projection of the states of P_N onto O_u, O_v and O_v's children is the set of (a, x, y) with (a, x) in the
pair projection of O_u and O_v taken before O_v's own subtree is imposed, (x, y) allowed by O_v's window, and the part of y on each
child orbit c extendable to c's subtree of r − 1 further levels. (b) The projection onto the stem of depth d and O_v is obtained by
the descent of Theorem W from level k to O_v, keeping the assignment of each ancestor orbit at levels k + 1, ..., k + d.*

*Proof.* The windows form a tree, and a window shares addresses only with its parent's and its children's (Theorem W). So O_v's
subtree meets the rest of the pattern only at O_v, and each child's subtree meets the rest only at that child. A state of P_N is
therefore a state outside O_v's subtree and a state of O_v's subtree that agree on O_v, and the subtree's states, read on O_v and its
children, are exactly the window's allowed assignments whose child parts extend below. This gives (a). For (b), each step of the
descent composes the current relation with the step relation of one window, the other child orbits being quantified into their
feasible sets; Theorem W shows this is the exact projection onto the two ends. Keeping the intermediate orbit's assignment as another
coordinate keeps the same allowed states and forgets less, so the composed relation is the exact projection onto every orbit kept. ∎

## Theorem K* (bonds in exactly projected pieces)

*Let X be a set of addresses holding one at level k and one at level k + s, and let the projection of the states of P_N onto X be
exact. A bond of that projection containing a distinction at level k and one at level k + s is a bond of P_N, so L_N(k, s) is at most
its size. For the two pieces of Lemma P, the least such size is decided for every s and every N by a finite computation.*

*Proof.* A set inside X is constrained, or free, in P_N exactly when it is in the projection, so a bond of the projection is a bond of
P_N meeting both levels (Theorem K's argument). The computation is the every-depth routine of Theorems W and K
(`DIRECT-REACH-20261115-001`, `KEEP-REACH-20261117-001`) with the pair states extended: for blocks, the property is read after
joining O_v's window, whose children read the feasible sets one remaining level shallower, so the depth tiers run to r₀ + 1; for
stems, the states carry the stem's assignments, which are finitely many, so the sequence of states along the descent is again
eventually periodic. Every remaining depth below the stable tier is computed at its own depth. ∎

Two-orbit bonds are orbit-and-block bonds that use no child, and stem bonds of depth 0, so K* contains Theorem K.

## Computed

**The 25 open patterns of KEEP-REACH** (`run_block.py`, `block_25.json`; `run_head.py`, `head/`), from level 3, at every depth, bonds
searched to 8 members:

| Patterns | Kind in KEEP-REACH | Two-orbit bond from level 3 | Orbit-and-block bond | Stem bond of depth 2 | Verdict |
| --- | --- | --- | --- | --- | --- |
| bace53f8f952-147, -111 | unexposed dependence | to s = 2 only | every s: 4 below the bottom tiers, 5 at them | | bounded at every depth (5) |
| bace53f8f952-58 | unexposed dependence | to s = 4 only | to s = 4 only | every s ≥ 3: 5 | bounded at every depth (5) |
| ca1efb37ad88-361, -364, -367, -375, -378, -386, -389, -418, -835 | unexposed dependence | to s = 4 only | to s = 4 only | every s ≥ 3: 4, then 5 | bounded at every depth (5) |
| the 13 mutants of 8db5da810c00 | top pair projections become products | to s = 4 only | to s = 4 only | s = 3 to 6: 5, 5, 6, 6; none of at most 8 from s = 7 | open |

The values at s = 1, 2 come from the two-orbit and orbit-and-block bonds (3 and 4 or 5) at every tier, so each "bounded" row is
bounded at every s and every depth, by Theorem K*.

**Corollary (Conjecture C′ fails).** *The twelve patterns with an unexposed dependence have a bounded reach from level 3 at every
depth, yet none holds a two-orbit bond from level 3 at every distance. So C′'s "only if" is false.* Their dependence, unexposed inside
the two orbits, is exposed once the lower orbit's children or the lower orbit's ancestors below the top are held as well.

**Exact values for the 13 mutants.** The threshold run (`threshold_*.json`, certified by LRAT) finds no bond of at most 5 members at
s = 5 and 6 at depth 11 for each of the 12 besides −73, and −73's exact reading says the same. Their stem bonds of 6 hold at every depth.
So L₁₁(3, 5) = L₁₁(3, 6) = 6 for all 13, and L_N(3, 5), L_N(3, 6) ≤ 6 at every depth. Past the stems, the certified search finds no bond of at most 6 at s = 7
and 8 at depth 12 for −73 and −79 (`threshold_deep_*_c6.json`), so L₁₂(3, 7), L₁₂(3, 8) ≥ 7 there.

*Checks* (`gate_two_block.py`, `gate_head.py`, all passed):
- the least bond search agrees with an independent brute force on 2,000 and 1,000 random relations;
- the exact projections agree with SAT enumeration of the address-level pattern on 120 orbit-and-block pieces at depth 7 and on 120
  stem pieces at depth 8;
- the every-depth tiers agree with the computation at each depth on 1,200 and 720 values;
- no bound lies below any of 2,021 decided census cells at depth 9 and certified readings, or 40 certified readings for stems;
- for each of the 25 at depth 11 and s = 5, 6, a least bond on an actual pair of orbits, mapped to its addresses, is a bond of the
  whole pattern by SAT (`verify_bonds.py`).

## The repaired conjecture

The advisor's view, not checked here: a bond can also use orbits off the line from O_u to O_v (a sibling, a side child), so the right
pieces are bounded parts of the tree of blocks around each end.

- **Conjecture C\*.** *The reach from level k is bounded at every depth exactly when, for some fixed d and e, a bond inside the orbits
  at most d blocks from O_u and the orbits at most e blocks from O_v, holding a distinction at level k and one at level k + s, exists
  at every s and every depth.*
- **"If"** is Theorem K*, once the projection onto such pieces is exact, which Lemma P's argument gives for any connected part of the
  tree of blocks.
- **"Only if"** has the advisor's proof idea: a bond of at most c members spans at most 2c stretches of the tree with no member; the
  projection across a stretch is a product of finitely many transfer relations of blocks; a stretch longer than the size of that finite
  monoid times the number of types can be shortened or lengthened by a repeated factor without changing the projection onto the bond,
  so the bond can be moved, keeping s, until every stretch but one is short. The tiers below r₀ must be part of the type.

C* would make the open question for the 13 mutants a dichotomy: a bond in fixed pieces at both ends at every distance, or growth.

## Dependencies

- `DIRECT-REACH-20261115-001B`: Theorem W and its every-depth routine.
- `KEEP-REACH-20261117-001A`: Theorem K and the 25 open patterns.
- `LEVEL-REACH-20261114-001`: the census and its certified search.
