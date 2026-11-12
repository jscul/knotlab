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
  ties are made by the substitution. The frozen criterion for influence growing with the pattern is met. *Referee R1: 30 of the 47
  blocks hold no tie of their own; and once one knot pins, the reach across the whole pattern is the pattern's connectivity, so "16
  steps on the chain of 16", "tie extent equals the farthest distinction" and the growth criterion add nothing beyond the local fact
  (logged, Not a block).*
- **Which block distinctions tie (now proved both ways: `PIN-RULE-20261112-001`, and independently by referee R1).** A spare distinction's part is never tied (proved: it can take any
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

**Review (referee R1, folded in 2026-11-12).** The background referee thread confirmed the epic with fixes
([report](referee-R1/report.md)), from its own code (Glucose, the whole tie relation of every substituted pattern). Every census number
reproduces. It found a closed form for the whole tie relation, checked on all 870 living tests with the block's knots: for a connected
pattern with a knot, (v, p) and (w, q) are tied exactly when p = q or p and q are tied in the block, and v = w or p is not spare;
ties between copies of one distinction are equalities, and 150 ties between different distinctions in different copies are
inequalities, the block's own opposite ties carried across. It proved the pinning rule's converse independently (a majority over
three copies with Hall's condition). Fixes, logged in `docs/CORRECTIONS.md` (all Not a block): the Fano gadget's level 4 has 1,039
distinctions, not 1,051 (share 175/1,039, as computed; N3 and the proof's table carry 1,051); N2's "no distinction tied at any level"
is computed (levels 0 to 5 here, 0 to 7 by `BASES-WITHIN-20261112-001`'s referee), not implied by all eight on the terminals; and the
reach across the pattern is connectivity once one knot pins.

**Prior work and novelty.** The rule's ingredients are standard: a majority over three solutions with Hall's theorem, and a freedom
to flip one variable close to the free and frozen variables of the random-constraint literature ("whitening"; Achlioptas and
Ricci-Tersenghi; Montanari and Semerjian). Novelty of the rule is not claimed; the record claims only that it holds and what it means
for the owner's question.

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

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 08:29 UTC, verbatim:

> Done. Nesting by substitution does make influence travel: it can pin a value across an entire pattern, using blocks that force nothing on their own. The write-up is research/SUBST-NEST-20261112-001/subst_nest.md. The referee is pending with the background referee thread.
>
> • **Global pins (exact).** Replace each distinction with a copy of a small block, and bind the copies to each other through the block's own knots. In 47 of 87 small blocks, some distinction of the block then gets tied in every copy, all the way across the pattern. On a chain of 16 knots, fixing it at one end fixes it 16 steps away at the other end. A second round of nesting keeps this. Neither the test patterns nor most of the blocks hold a tie of their own.
> • **The block decides (one direction proved, the other exact).** If a block can spare a distinction (its knots hold whatever that distinction does), that distinction never gets pinned. Every other distinction did get pinned, in all 4,850 cases and in 300 blocks one size larger. Four distinctions with all four triples knotted spares none, so the whole nested pattern collapses to six states.
> • **Depth carries the pins but adds none.** A second substitution created nothing new.
> • **Your reading matters.** Bound side by side as endless series (the last epic), nothing gets pinned. Nested inside by substitution, values get pinned across everything.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — nesting by substitution | **Status:** Successful, referee pending | influence across the whole pattern found and characterised; one frozen lemma narrowed |
> | Local direction — nesting | Continue | the pinning rule is one proof away from a theorem |
> | Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random periodic bases (knots alone) |
> | Long-term goal — G17 Typical and rare meeting patterns | Capability gained | "globally influential" now has a native mechanism: what a block can't spare gets pinned everywhere it is nested |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Prove the pinning rule | 2/3 — Substantial | 3/3 — Ready | show a non-spare distinction is tied between any two knotted copies → a theorem, or a counterexample block | Selected · awaiting go-ahead |
> | 2 | Pins that vary across the pattern | 2/3 — Substantial | 2/3 — Testable | look for pinned relations that change from copy to copy, a structure rather than one repeated state → one, or a proof they're always uniform | Alternative · deferred |
> | 3 | Endless blocks | 2/3 — Substantial | 2/3 — Testable | substitute a harmony bound by its own kinds, joining both readings → pins along both shifts, or none | Alternative · deferred |
> | 4 | Which nesting you meant | 1/3 — Incremental | 3/3 — Ready | side by side (stitches) or inside (substitution)? → A75 confirmed or replaced | Alternative · deferred |
>
> **Corrections:** three, each logged in docs/CORRECTIONS.md.
> • Narrowing: the last epic's "nesting spreads no influence" holds only for stitches.
> • Narrowing: one of my frozen lemmas (N5) fails for blocks of 5 or more when every triple is bound.
> • Not a block: I had written "bond distance" where I meant steps apart.
>
> **Goals:** G17 checkpoint (capability gained), no goal change. **Assumptions:** A75 was challenged and has now been answered both ways, so it stays Assumed. **Words:** the advisor checked the new terms, and the glossary now has spare distinction, block triples, gadget, terminals, tie extent, and unlagged/lagged stitches. **Basket:** #1 to #4 recorded.
>
> One question for you, whenever convenient: when you said each variable is its own infinite series "bound to others", did you picture the series side by side, or nested inside one another?
