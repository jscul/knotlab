# Where a loop's presence comes from: first pass

Ticket `KNOT-FOUNDATION-20261019-001B`, 2026-10-19. This is an exploratory
pass recorded in the scope's decision notes, not a proof family. The ticket
stays open for the owner's review before ticket C starts.

## Question

K1–K3 takes each loop's presence as a given variable. Can presence be
computed from the loop itself, with no outside input and a verdict that does
not depend on presentation? Or is presence primitive?

## Answer

- **In static semantics a loop adds nothing.** Written as constraints, it
  collapses to one free bit, so its presence can only be that bit. Making a
  loop contradictory empties every system that contains it, rather than
  erasing the loop.
- **Under a declared update law a loop adds two things.** It keeps its
  presence, because running versus frozen is conserved by the loop's own
  update. And it makes presence readable from inside, by comparing
  neighboring points: for two points, 01/10 means running and 00/11 means
  frozen.
- **The knot appears on computed presence.** A contact that is set when both
  loops run, and otherwise keeps its value, gives exactly the K1–K3 knot over
  the computed presences, across every initial state.
- **Nothing creates presence.** Whether a loop is running is set by its
  initial state.

So presence is a distinction, and a loop is what makes a distinction persist.

## Nearest known results

The facts used are elementary: rotating a pattern preserves whether it is
constant, odd inverter rings always oscillate (ring oscillators), and set
latches hold their value. The contribution is the reading: which candidates
give K1–K3 on computed presence, and which do not.

## Static candidates

`knotlab presence` and `tests/test_knotlab.py` (`PresenceTest`, `LoopTest`)
check each item.

- **Implication loops and consistent equal/unequal loops.** They leave
  exactly two states, which are complements of each other. A presence that
  is a nonconstant function of a two-state space is the bit or its
  complement.
- **A cycle of atoms with side inputs** (`A ∧ X → B`, `B ∧ Y → A`). It
  collapses to 00/11 while both side inputs are present and opens into a
  one-way chain when either is absent. Its presence is a free bit gated by
  other presences.
- **Contradictory loops** (an odd number of unequal steps). They allow no
  state, so a system containing one allows no state at all. Erasing a loop
  by making it contradictory excludes everything, which is the opposite of
  K2.
- **Presence as "the loop's constraints are in the system".** With the loop
  present, K1 needs the contact constrained. The loop's constraints alone
  leave its bit free, so they must force it, which takes a fact. Presence is
  then the existence of a fact, again primitive.

## Dynamic candidates

A loop is a ring of n ≥ 2 bits under one synchronous update. A state is
*running* when it lies on a cycle of length at least two, and *frozen* at a
fixed point.

- **Copy ring.** Each bit takes the value of the bit before it, so the
  pattern rotates.
  - Its frozen states are all 0s and all 1s.
  - Running means non-constant, and rotation preserves that.
  - "Some neighbors differ" reads running exactly at every instant. For
    n = 2 it is the comparison of the two points.
- **Inverter ring of odd length.** It has no frozen state, so no state can
  erase its presence.

**Two copy rings and a contact.** Two copy rings A and B and a contact bit c
share one update. Over every initial state, the settled relation over
(A running, B running, c) gives:

| Contact rule | K1–K3 over computed presence | Contact free whatever a frozen ring is left at |
| --- | --- | --- |
| latch: `c' = c ∨ (A running ∧ B running)` | yes, exactly `¬A ∨ ¬B ∨ c` | yes |
| driven: `c' = A running ∧ B running` | no: AND forces c off when a loop is frozen (K2 fails) | no |
| hub: `c' = c ∨ A running ∨ B running` | no (K2 fails) | no |
| single point: `c' = c ∨ (a1 ∧ b1)` | no for equal ring lengths: whether c is made depends on the rings' relative phase (K1 fails) | no: a ring frozen at all 1s still drives c |

These were checked exhaustively for ring sizes up to 4. A short argument
covers every size, for the latch:
- if both rings run, the reader is true at every step, so c is set within
  one step and then held;
- if a ring is frozen, its reader is false forever, so c keeps its initial
  value, which ranges over both values.

## What this means

- **Presence is a distinction:** which of the loop's states holds. Static
  constraints do not create it, and neither does an update law. The update
  law makes it persist and makes it readable.
- **The 00/11 versus 01/10 intuition is exactly the reader.** Comparing two
  points of a loop tells a running loop from a frozen one. A one-point
  reader cannot: it mistakes a ring frozen at 11 for a running ring.
- **In time, the knot is a set-and-hold contact.** It is made when both
  loops run and is otherwise not driven. A contact that is reset or driven
  when a loop stops is AND, a gate, which fails K2.
- **This is where the old program's leak came from.** Its executor-based
  recurrences took presence from the executor's knowledge of which loop was
  running. Here presence is read inside the system, from the loop's own
  state.

## Prior work

- `EMERGENCE-RECONSTRUCTION-BRIDGE-20261014-001-D005`, `-D008` and `-D009`
  derive recurrent roles and contact dependence from supplied local support
  laws. They are labeled "earlier gate" in the
  [triage](foundation_triage.md). Restated as relations, they are candidates
  for the same test.
- `FINITE-LOGICAL-HARMONIC-CALCULUS-001` shows that relative phase is
  intrinsic while absolute phase needs an anchor.

## An observation for later, not a claim

Two running copy rings of equal length have a conserved relative phase. It
exists only while both run, and neither ring shows it alone. The
single-point contact depends on it. Is relative phase a candidate for
information that belongs to the pair rather than to either loop? That is a
question for tickets C and D.

## Stop rule

The epic's stop rule asks whether this ticket ends at "presence is
primitive". It ends one step further:
- presence is primitive as a distinction;
- a loop under an update law keeps that distinction and makes it readable;
- two such loops bound by a set-and-hold contact form the knot.

The ingredients are classical, but this reading is not just a restatement,
so the epic continues. The owner should review this result before ticket C
(whether choice is native) starts.

## After the owner's feedback

The owner clarified that a loop is not spatial: it is a logical structure that
can get entwined with another logical structure. The ring construction above
brings in a cyclic arrangement and time, so it is set aside as the definition
of a loop. Its results stand as recorded.

The static formalization in `docs/KNOT_INTUITION.md` ("Entwinement and two
readings of erasure") replaces it: a loop is a structure with an open
distinction. Under the forgetting reading of erasure, presence is not a
variable at all, and this ticket's question becomes which open distinctions a
structure carries. The choice between forgetting and absence is open and
belongs to the owner.

Later on 2026-10-19 the owner chose forgetting. Ticket B is retired: under
that reading a loop's presence is not a variable, and the knot test applies to
the loops' open distinctions (`KNOT-FOUNDATION-20261019-001E-P001`). The
dynamic results above stand as an exploration under the absence reading. The
contact rules were tested with `check_knot(..., erasure="absence")`.
