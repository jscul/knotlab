# Atoms within atoms

Epic `NEST-ATOMS-20261110-001` (backlog B104, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen in commit `4b27647cb` before any run. Proof families:
`proofs/NEST-ATOMS-20261110-001A/` (composite atoms), `…B/` (units at every level), `…C/` (a two-level address).

## The answer

A group of atoms behind a three-edge cut is itself an atom of the next level, and it stands for its line exactly when every atom inside
it does: from outside, a composite reads as the AND of the bits inside it.

- **Proved by hand** (theorem N, ticket A): a knot sphere that has a flat state at each line (a state violating that line only), carrying
  good closed atoms (free, with one unsatisfiable class), is again good. Its only unsatisfiable class is the one where every atom inside
  acts. So less any point it is an atom that acts as its line exactly where all its atoms act, and composites nest to any depth.
- **Units** (lemma U, by hand): a composite of genus g holds at least g − 1 units of the floor dissonance in its region, and g where it
  acts. One level up, the atom rule holds again, with the groups as atoms.
- **The role is monotone.** An acting atom only adds constraints, so whatever the host, a composite's role is a monotone function of
  its atoms' bits; on a knot sphere host it is exactly their AND.
- **Computed.** The AND held at all 274 removed points of seven named composites (128 off the replaced lines, as frozen; 44 on them; and
  102 inside a leaf when read on the closed composite), and at 146 more points one size up. In 576 classes of six two-level spaces every
  group held its units exactly. With the learner, 11 of 12 two-level addresses held after a disturbance, and every outer address held
  whenever its address did.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Theorem N: a sphere carrying good closed atoms is good; composites act as the AND of their atoms, at any depth | proved by hand, given flat states at every host line and good leaves |
| Lemma U: g − 1 units, g where it acts | proved by hand |
| Flat states at every line of K_2 and K_3 | exhaustive (SAT, every line) |
| The AND at 274 points of seven composites, 146 more one size up | exhaustive computation |
| R-a, R-b' and the AND on 576 classes | exact, SAT over every state |
| Two-level addresses: 11 of 12 held, 12 of 12 one size up | computed |

## Against the pre-registration

- **N1 held** at all 128 points off the replaced lines.
- **N2 held** at the 44 points on a replaced line. **It failed as stated** at all 102 points inside a leaf. The removed point cuts that
  leaf open: it then has six outer points and no role, so the AND read where the leaves are grown leaves it out. Yet the composite still
  acts in exactly one class. Read on the closed composite, where no leaf is cut open (a reading added after the run), the AND holds at all
  274 points, and theorem N proves it at every point.
- **Ticket B's expectation held** in every class, and its code control reproduced `OTHER-ATOMS-20261110-001B`'s split.
- **Ticket C** fell between its two marks with Fano leaves: 5 of 6 held, below the 95% expected and above the 80% failure line. The miss
  was a write: the frozen search stops when every named leaf holds a unit, and it stopped with a unit in a leaf that did not act. Thin
  leaves held 6 of 6, and the stress test held 12 of 12.
- The first full launch of ticket A stopped at an assertion, a 4-point leaf cut open whose own sides no longer reach its handle. Class
  representatives are now taken from all sides inside each top-level group.

## What it changes

- **Layers.** The owner's "the state is being effected at multiple layers" (G15) has a native form: a three-edge cut makes a level, and
  the level above reads the one below only through the AND of its bits. Nothing is drawn or named from outside; the cut is in the space.
- **The learned memory.** An address written in the leaves is read one level up with no extra rule, and the units sit where the rule says
  at each level.
- **Limits.** On a sphere host a composite computes only AND, and any host computes only monotone functions, since acting adds
  constraints. Whether some host gives OR is backlog B109.

## Perspective

In the language of constraint satisfaction, a sub-instance whose satisfiability is the AND of its gadgets' "on" states is a conjunction
of constraints, and the theorem is close to that observation. What the program adds is where it happens: in a surface, a group of handles
cut off by three sides, with the bits in the handles' sign classes. No novelty scan was run.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52 (now read for composites too). None added or changed in status.

## Corrections

None.

## Stress test

One size past the tickets ([stress_test.py](stress_test.py), [stress_test.json](stress_test.json)): the AND at every one of the 146
removed points of C(4, Fano) and C(4, thin), and ticket C on the outer host K_3, 12 of 12 held.

## In the owner's words

A group of patterns sealed off from the rest by three sides behaves, from outside, like a single pattern. It stands for the line it
replaced only when every pattern inside it does. So the layers read each other: the outer layer sees one bit, the AND of the bits below.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — atoms within atoms (B104) | **Status:** Successful | composites are atoms of the next level, proved by hand at any depth |
| Local direction — the layered memory | Capability gained | each level reads the one below as an AND; units counted at every level |
| Broader exploration — learning program | Known alternatives | many points at once, other functions than AND, a native choice of atom |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | a multi-layer memory with a proved rule |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Many points at once (B3) | 2/3 — Substantial | 2/3 — Testable | in the two-level space, move two units by learning in every order → independent moves, or units that meet, cancel or bind | Selected · awaiting go-ahead (a stretch goal the owner asked to hold) |
| 2 | Which functions a composite computes (B109) | 2/3 — Substantial | 1/3 — Exploratory | look for a host whose contradiction survives deleting either of two lines → an OR, or a proof that only AND occurs | Alternative · deferred |
| 3 | Which atom a growth law grows (B106) | 2/3 — Substantial | 1/3 — Exploratory | which uniform local rules can grow the 4-point atom → memory grown natively, or a reason none can | Alternative · deferred |
| 4 | Layers through a naming knot (`RESIGN-STEER-20261107-001`#3) | 2/3 — Substantial | 1/3 — Exploratory | compare a parity name with a three-edge cut as the channel between levels → the same reading, or a second kind of layer | Alternative · deferred |
| 5 | Capacity of the learned memory (B98) | 1/3 — Incremental | 3/3 — Ready | write every acting subset, at both levels → all written and held, or not | Alternative · deferred |
| 6 | Flat states at every line (B110) | 1/3 — Incremental | 2/3 — Testable | prove theorem N's host hypothesis for every octahedral sphere → the theorem for every K_k, or a line with no flat state | Alternative · deferred |
| 7 | Every torus is free (B105) | 1/3 — Incremental | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1** is the top of the learning line's basket and ties the owner's parallel picture to the layered memory. B3 was parked as a stretch
  goal awaiting the owner, so it needs the owner's go-ahead; if the owner holds it, #2 is the in-line step.
- **#2** decides whether the layers only conjoin or can also choose.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B104 taken; B109 and B110 added. **Assumptions:** none new or
changed in status; A52 read for composites (history line).
**Basket:** B3, `RESIGN-STEER-20261107-001`#3, B106; taken: B3 as the selected next step, pending the owner's go-ahead.
