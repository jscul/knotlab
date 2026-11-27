# The binding step as a conjecture, and what the record already proves of it

`THIRD-LAYER-20261126-001`, at the coordinator's request: the general step stated with its hypotheses, and the
all-size proofs in the record that give parts of it. A statement to test, not a result.

## Setting and words

A start S grows by ordinary parity growth (the canonical engine, the ordinary count). A **small change** of a stage is,
in the reading SHORT, a shortest allowed change through some distinction (all tied ones), and in the reading UPTO_w an
allowed change of at most w distinctions (the studies use w = 5). A **class fact** is a parity of the distinctions that
every small change keeps and the laws do not fix. A **second-layer knot** is a family of m ≥ 3 class facts, each read
by no single knot, carried on pairwise disjoint sets of distinctions, whose values obey one parity rule with every
proper subfamily free (so the rule passes the knot test K1 to K3).

## What is proved for every size (the record)

| Part | Statement | Where | Standing |
| --- | --- | --- | --- |
| P1 | Ordinary growth keeps the start's allowed states on the start's distinctions (the projection lemma) | `LAYERS-20261126-001` referee R1, item 4, and `BINDING-20261126-001` referee R1, item 1 (a private fresh distinction satisfies its birth's law for any old state; a birth without one is implied) | argument, refereed; also the extension count in `ERASURE-AND-CLOSING-SIGNS-20261121-001B` (closing_law.md, line 15) |
| P2 | A parity birth gets no fresh distinction exactly when its inputs are every loose distinction of its connected structure | `ERASURE-AND-CLOSING-SIGNS-20261121-001B` (closing_law.md, lines 9 to 25) | proved; checked on every census and held-out birth here (`BUILT-BINDING-20261126-001`, closing.py) |
| P3 | Every class fact of an ordinarily grown stage is a function of the start's values, so every relation among class facts is a sum of start laws (the changes keeping every start value are spanned by pairs and loops of four, under both readings) | `BUILT-BINDING-20261126-001` referee R1, argument_note.md | proved for finite funded ordinary stages, refereed |
| P4 | The births of each round are the clusters of the unrolled map, with their parents and open distinctions | `RING-IDENT-20261119-001`, `CHAIN-IDENT-20261119-001`, `RELAY-IDENT-20261119-001`, `DOUBLE-IDENT-20261119-001` | proved, confirmed line by line |
| P5 | What a knot sees by round t lies within t + 1 steps of the map, for funded growth that does not close | `INFLUENCE-CONE-20261120-001` | proved (referee pending on its guards) |

## The binding step (layer one to layer two)

**Conjecture B.** Let G_1, ..., G_m (m ≥ 3) be pairwise disjoint sets of loose distinctions of S such that
(H1) the parity of G_1 ∪ ... ∪ G_m is the sum of the laws of a set D of knots of S, and every proper subfamily of the
parities is free on S's allowed states (for the ring starts, D is every knot, since the connecting knots hold no loose
distinction); (H2) S's growth is funded for t rounds (each round takes every loose distinction: engine fact E1);
(H3) every allowed change of S that flips the parity of one G_i alone (that is, an odd number of the G_i's parities
and not a sum of laws) has at least ℓ_0 distinctions, and flips two of them, through distinctions of D. Then at round t
the least allowed change flipping one G_i's parity has at least ℓ_0 + 2t distinctions; so for t > (w − ℓ_0)/2 (under
UPTO_w), and from the round at which no shortest change flips it (under SHORT), the parities are class facts, each read
by no single knot, and they form a second-layer knot whose rule is the start's sum of laws.

**Evidence.** The least flipping change was 5, 7, 9 and 11 at rounds 0 to 3 on all 32 built ring families
(`BUILT-BINDING-20261126-001` referee R1, ring_counts.json), matching ℓ_0 + 2t with ℓ_0 = 5. The binding itself and its
origin are P3's consequence once the parities are class facts.

**Proof idea, not checked.** By P4 a loose distinction of S is, after t rounds, joined to the newest round only through
a chain of t births; a change that flips one G_i's parity must leave through two such ends, each of which grows by one
distinction per round, and by P1 it cannot shortcut through a new law on old distinctions.

**What would break it.** A start meeting H1 to H3 whose least flipping change stops growing (for example where a
shortcut through a closed part appears, P2), or a reading in which loops of four are not small (then P3 fails).

## The general step (layer k to layer k + 1)

Stated after the advisor's review (advisor/), since the layer's own small changes must be fixed first.
