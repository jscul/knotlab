# Nesting by substitution

Epic `SUBST-NEST-20261112-001` (`BASES-WITHIN-20261112-001` direction 1, the challenge to A75; G17 with G8; program mathematics,
group arithmetic), 2026-11-12, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in
commit `456d7a49e` before any census ran. Proof family: `proofs/SUBST-NEST-20261112-001A/`. **Referee pending** (the background
referee thread).

## Words

As in the guide's glossary: distinction, knot, block, tie class, steps apart. After the run the advisor model checked the new words,
and these replace the pre-registration's (the frozen file keeps its own):

| Pre-registration | Here and in the glossary | Meaning |
| --- | --- | --- |
| block substitution | **distinction substitution** (by a block) | each distinction v of a pattern becomes a copy of the block, distinctions (v, p) |
| cross set T, cross knots | **block triples** T, **between-copy knots** | each knot (x, y, z) becomes the knots ((x, p), (y, q), (z, r)), (p, q, r) in T, triples of the block's distinctions |
| loose place | **spare distinction** | a distinction p of the block such that its other distinctions can be given values with every knot of the block holding both values without p ("place" keeps the guide's meaning, an argument position) |
| a locked column | a **tied part** | p's part, the distinctions (v, p) for v in the pattern, all in one tie class |
| motif, attached distinctions | **gadget**, **terminals** | the pattern that replaces each knot in **knot substitution**, and its three distinctions glued to the knot's |
| the farthest tie; bond distance (fewest knots in a chain) | **tie extent**; **steps apart** | the most steps apart from a distinction to one tied to it; the guide's bond distance is read from states, not from chains |
| stitch at one place, shifted stitch, shifts (`BASES-WITHIN-20261112-001`) | **unlagged stitch**, **lagged stitch**, **lags** | "place" there meant the index i, and "shift" is the translation of a base |

## The question

The owner's "each boolean variable could be its own micro infinite series of logic, that's bound to others", and of overlapping,
"like fractal ... globally influential". `BASES-WITHIN-20261112-001` read nesting as unlagged stitching of inner harmonies (A75) and
proved it keeps the outer law exactly and creates no tie. Does substitution, the reading A75 names as its challenge, do differently:
does fixing one distinction then force values across the whole pattern, and does that grow with depth?

## The answer

**Yes. Substitution creates influence that spans the whole pattern, from blocks that force nothing alone; nesting by stitches did
not.**

- **A part ties across the whole pattern (exact).** Replace each distinction of a pattern by a copy of a block, and each knot by the
  block's own knots laid between the copies. Then, in 47 of the 87 small blocks, some block distinction's part is tied across the entire
  pattern: fixing one distinction forces that block distinction in every copy, at every distance. On a chain of 16 knots the tie extent is 16 steps, the
  whole chain, and the same after a second substitution. The test patterns and most of these blocks hold no ties of their own, so the
  ties are made by the substitution. The frozen criterion for influence growing with the pattern is met.
- **Which block distinctions tie (proved one way; exact the other).** A spare distinction's part is never tied (proved: it can take any
  values while everything else holds). With the block's knots as block triples, every other part was tied across the whole pattern, in
  all 4,850 roots tested. So the rule found is: a nested pattern pins exactly the block distinctions its block cannot spare.
- **One block pins everything.** All four knots on four distinctions has no spare distinction and six states: every copy must take the same
  state, so the whole nested pattern has just six states, at every depth (proved as N7, checked).
- **Depth adds nothing new.** Ties appear after one substitution or not at all; a second substitution keeps them and makes no new
  ones (S6). The influence is in the block, carried to every scale.
- **Knot substitution is decided at one level (proved).** Replacing each knot by a gadget that treats its terminals alike either keeps
  the law, frees everything (the drawn three-copy nesting), forces the terminals equal (the Fano plane less a knot, whose own tie then
  reaches every scale), or ends, and the first level says which.
- **Substitution can also end a pattern.** With every triple of distinct block distinctions as block triples, every block on 5 or more
  distinctions ends every pattern with a knot: no state of such a block avoids three equal values. This contradicts a lemma I froze
  (N5), narrowed and logged as a correction.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Knot substitution is decided at the first level; the drawn nesting frees; the Fano gadget ties its terminals | proved by hand (N1 to N3, two from the advisor model) |
| Unlagged (diagonal) block triples keep the outer law | proved by hand (N4, from `BASES-WITHIN-20261112-001`) |
| With the block's knots, substitution never ends; a spare distinction's part is never tied; a rigid template pins every part | proved by hand (N5 narrowed, N6, N7, from the advisor model) |
| With every distinct triple and 5 or more distinctions, substitution ends every pattern with a knot | proved by hand after the run (the corrected N5) |
| 47 of 87 blocks, with their own knots, tie some part across the whole pattern; the tied parts are exactly those of the distinctions that are not spare | exact on the frozen range (chains of 4, 8, 16 knots, drawn nestings of levels 1 to 3, one or two substitutions); the second half descriptive, after the run |

## Against the pre-registration

| Item | Outcome |
| --- | --- |
| S1 unlagged block triples: nothing tied outside a copy | held, 87 of 87 |
| S2 blocks whose every distinction is spare: nothing tied; most blocks are such (the advisor's) | held for the first part (40 blocks); 40 of 87 is not most |
| S3 all four knots on four distinctions (the advisor's) | held: rigid, every part tied across the whole pattern, share 1/4, once and twice |
| S4 rigid templates only for dense blocks (the advisor's) | held for the block's knots; **failed** for every distinct triple |
| S5 an intermediate case exists (the advisor's, 50%) | **held**: 42 blocks tie some parts and not others |
| S6 nothing only after two substitutions (this epic's) | held |
| K1, K2 the two gadgets | held |
| Influence created by substitution, growing with the pattern (the frozen criterion) | **met**, by 50 of 261 cells (47 blocks with their own knots, 3 with every distinct triple) |
| N5 for every distinct triple | **failed** for 5 or more distinctions; narrowed (a correction) |

Both parts ran inside their caps (the blocks in under 3 minutes of processor time). Seen before the freeze: the two gadgets' first
levels and the timing of the one-knot block, as disclosed.

## Stress test one size past (after the run, descriptive)

The pinning rule (with the block's own knots, a part is tied across the whole pattern exactly when its distinction is not spare)
was found on blocks of up to 6 distinctions and 5 knots. On 300 random living blocks past that range (150 on 6 distinctions with 6
to 12 knots, 150 on 7 with 5 to 12, seeded), each substituted once into the chain of 8 knots, it held for every block and every
distinction, and every pinned part reached the far end of the chain. The blocks ranged from none to all of their distinctions
pinned. Still exact on its range, not proved.

**Review.** Referee pending: the background referee thread has the hand-off (arrangement of 2026-11-12).

## What it changes

- **For the owner's "globally influential".** It depends on how a distinction is nested. Bound to the others by stitches, an endless
  inner series adds hidden room and influences nothing. Replaced by a finite block whose own knots bind the copies, it can pin a value
  across everything: change one distinction and every copy of it changes with it, however far away. What decides it is
  local, a property of the block alone (which of its distinctions it can spare), and depth only carries it.
- **For A75.** The reading matters: "nesting spreads no influence" holds for stitches and fails for substitution. A75 stays a reading
  of the owner's words, now with both outcomes known; which he meant is his to say.

## Assumptions

A70 not used. A75 (bases within bases are unlagged stitches) challenged by this epic: the substitution reading gives the opposite
answer on influence; status back to Assumed, with the outcome in its history.

## Corrections

Three, logged in `docs/CORRECTIONS.md`: **Narrowing**, lemma N5 of this pre-registration (every distinct triple does not always lift);
**Narrowing**, `BASES-WITHIN-20261112-001`'s "nesting spreads no influence" holds for stitches, not for substitution; **Not a block**,
"bond distance" and "bonds" used in both epics for steps apart.

## In the owner's words

If each yes-or-no is replaced by a small block of yes-or-nos, and the blocks are tied to each other by the block's own rules, the
whole thing can become globally influential: some positions in the block get locked to the same value everywhere, so changing one of
them anywhere changes all of them. Which positions lock is decided by the block alone: exactly the ones it cannot spare. Nesting
deeper keeps the lock but adds no new ones. Tied together the other way, by endless patterns side by side, nothing locks at all.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — nesting by substitution | **Status:** Successful, referee pending | influence created by substitution, spanning the whole pattern, found and characterised on 87 blocks and 300 past them; one frozen lemma narrowed |
| Local direction — nesting | Continue | the pinning rule is one proof away from a theorem |
| Broader exploration — G17's census | Known alternatives | random patterns' outcomes and jumps (`RANDOM-FATES-20261112-001`); folding among random periodic bases (knots alone) |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | the owner's "globally influential" has a native mechanism: a block it cannot spare pins a value everywhere it is nested |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the pinning rule | 2/3 — Substantial | 3/3 — Ready | show that a distinction a block cannot spare is tied between any two co-knotted copies (then across any connected pattern) → a theorem, or the first block that breaks it | Selected · awaiting go-ahead |
| 2 | Pins that vary across the pattern | 2/3 — Substantial | 2/3 — Testable | search blocks and patterns for pinned parts whose forced relation changes from copy to copy (unequal across some knots), a structure rather than one copy of a state → one, or a proof that pins are always uniform | Alternative · deferred |
| 3 | Endless blocks | 2/3 — Substantial | 2/3 — Testable | substitute a harmony for each distinction with its own kinds between copies, joining the two readings → pins along both shifts, or none | Alternative · deferred |
| 4 | Which nesting the owner meant | 1/3 — Incremental | 3/3 — Ready | ask him whether "bound to others" is side by side (stitches) or inside (substitution) → A75 confirmed, or replaced | Alternative · deferred |

- **#1** would turn the census's rule into a theorem: what nesting pins is exactly what the block cannot spare.
- **#2** is where "folding in immensely complex ways" could live: so far every pin is uniform, the same relation in every copy.

**Corrections:** three (two Narrowing, one Not a block), logged in `docs/CORRECTIONS.md`. **Goals:** G17 checkpoint (capability
gained, with G8; no goal change). **Assumptions:** A75 challenged by this epic and answered both ways; status Assumed, with the outcome
in its history. **Basket:** #1 to #4 recorded; in the arithmetic line's basket ODD-FAMILY #1 and #2 rate 3/3 for concreteness but were
set aside by the coordinator, none ahead of #1 for the owner's goals. **Advisor:** consulted three times on this line before the
freeze (the readings, the lemmas N1, N2, N5 to N7, the criteria) and once after it on the new words, whose proposals replaced six of
the pre-registration's eight.
