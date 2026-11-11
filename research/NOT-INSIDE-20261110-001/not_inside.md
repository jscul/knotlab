# Negation inside a cut leaf

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `NOT-INSIDE-20261110-001` (backlog B123, G15; program learning), 2026-11-10, at the coordinator's go-ahead, as the deciding epic for
the gates question. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `904fce672` before any run. Proof family:
`proofs/NOT-INSIDE-20261110-001A/`.

## The answer

The gates question closes with a proof: **every class-level reading is monotone.** Whatever network reads the stored classes, if its reading
depends only on the classes (not on which signing of a class learning happened to leave), it is non-decreasing in each acting bit and cannot
tell two non-acting classes apart (theorem M, proved by hand). A NOT does exist, but only in a fixed frame: with one fixed signing per class,
an explicit network reads NOT a_1 for each of three cut leaves, and another signing of a non-acting class makes it read 0.

- **Theorem M (by hand).** If a network has a satisfying state with a leaf in some signing of class c, and the leaf allows in class c′
  every outer pattern it allows in c, then some signing of c′ admits the same state: flip the leaf's inner points where a completion under
  c′ differs. For atoms that act in one class and are transparent in the rest, that gives monotone readings and no distinction among
  non-acting classes. Scope: any network whose other constraints do not involve a leaf's signs, of any size.
- **Census N (computed).** In the frame of the labelled class laws, the thin tori (3,2,2) and (4,3,2) and the Fano piece, cut into the
  torus (2,0,2), each have states only the acting class allows (10, 14 and 12); a network pinning names to one reads NOT a_1 there.
- **Check F (computed).** Each of the 718 networks that read σ in `CLASS-READ-20261110-001` has a satisfying state under another signing of
  σ. That reading, and the parity reading noted after `GATES-20261110-001`, were frame-level: corrected below.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Theorem M: class-level readings are monotone, constant on non-acting classes | proved by hand |
| A frame-level NOT for three cut leaves, with explicit networks | exhaustive computation |
| The σ readings read the frame (718 of 718) | exhaustive computation |

## Against the pre-registration

All held: M proved as planned, N (a frame-level NOT for every one of the three leaves), F (718 of 718). The failure line was not crossed.

## What it changes

- **The gates question is closed.** Reading stored classes, knots and names give AND, OR and monotone combinations, never a negation. A
  network that negates must carry a frame, a fixed choice of signing, which is not stored memory but the record of how it was written.
- **Stored memory or the law, answered again.** The earlier answer (`CLASS-READ-20261110-001`) said names read the stored class against
  two law-fixed landmarks. Corrected: a class-level reading sees only whether a leaf acts; the σ landmark was visible only through the frame.
- **A way a NOT could still be native.** If learning wrote classes along fixed windings, it would leave a fixed frame, and frame-level
  readings, NOT included, would become readings of what was written (backlog B126).

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52. None added or changed.

## Corrections

One, logged in `docs/CORRECTIONS.md`: the σ and parity readings of `CLASS-READ-20261110-001` and `GATES-20261110-001` read the frame, not
the class (**Narrowing**, worded beyond its evidence).

## In the owner's words

The layered memory can say "all of these" and "any of these" about what it has stored, and that is all it can say about the stored
patterns themselves. To say "not this" a network has to know exactly how each pattern was wound, not only which way it ended up, and that
is a record of the path learning took, not of what it stored.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — negation inside a cut leaf (B123) | **Status:** Successful | a definite ending: class-level readings proved monotone; a frame-level NOT exhibited |
| Local direction — gates from cuts and names | Exhausted for this phase | the readable functions of stored classes are monotone, by proof |
| Broader exploration — learning program | Known alternatives | native writing, inputs and outputs, a frame fixed by learning |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Obstruction learned | a learned knot memory computes monotone functions only |

**Next step:** Research directions — selected: #1 (the line leaves gates, as agreed)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Native writing (B119) | 2/3 — Substantial | 2/3 — Testable | a learner that sees only its own dissonance and the address asked for writes into the layered memory → native writing, or a reason it needs an outside map | Selected · awaiting go-ahead |
| 2 | Inputs and outputs (B120) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |
| 3 | A frame fixed by learning (B126) | 1/3 — Incremental | 1/3 — Exploratory | a writing rule that winds along fixed cycles, then frame-level NOT read as memory → a native negation, or a frame learning cannot keep | Alternative · deferred |
| 4 | Composing gates (B124) | 1/3 — Incremental | 1/3 — Exploratory | now known to compose only monotone gates | Alternative · deferred |

**Corrections:** one, Narrowing: the σ and parity readings read the frame, not the class (`CLASS-READ-20261110-001`, `GATES-20261110-001`).
**Goals:** G15 checkpoint (obstruction learned); B123 taken; B126 added; B124's payoff lowered to 1/3. **Assumptions:** none new or changed.
**Basket:** B119 (native writing), B120 (inputs and outputs); taken: B119 as the selected next step.

## Final report as sent

Posted in the thread on 2026-11-10:

**B123 is closed, and the gates question ends with a proof.** Every reading of the stored classes is monotone. If a network's reading depends only on the classes, and not on which signing of a class learning happened to leave, it can only rise as more atoms act, and it cannot tell two non-acting classes apart (theorem M, proved by hand). A NOT does exist, but only in a fixed frame: with one signing fixed per class, explicit networks read NOT a₁ for three cut leaves, and another signing of the same class switches it off (computed). So the layered memory can say "all of these" and "any of these" about what it stores, but to say "not this" it needs a record of how each pattern was written.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: negation inside a cut leaf (B123) | **Status:** Successful | a definite ending: class readings proved monotone, a frame-level NOT exhibited |
| Local direction: gates from cuts and names | Exhausted for this phase | what stored classes can be read as is monotone, by proof |
| Broader exploration: learning program | Known alternatives | native writing, inputs and outputs, a frame fixed by learning |
| Long-term goal: G15, a point in a learned knot pattern | Obstruction learned | a learned knot memory computes monotone functions only |

**Next step:** Research directions, selected #1. The line leaves gates, as agreed.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Native writing (B119) | 2/3 Substantial | 2/3 Testable | a learner that sees only its own dissonance and the address asked for writes into the layered memory → native writing, or a reason it needs an outside map | Selected, awaiting go-ahead |
| 2 | Inputs and outputs (B120) | 2/3 Substantial | 1/3 Exploratory | as recorded | Deferred |
| 3 | A frame fixed by learning (B126) | 1/3 Incremental | 1/3 Exploratory | a writing rule that winds along fixed cycles, then the frame-level NOT read on what it writes → a native negation, or a frame learning cannot keep | Deferred |
| 4 | Composing gates (B124) | 1/3 Incremental | 1/3 Exploratory | composed gates now known to stay monotone | Deferred |

**Corrections:** one, Narrowing: the σ and parity readings from the last two epics read the frame, not the class (718 of 718 networks have a satisfying state under another signing). It's logged in docs/CORRECTIONS.md with dated lines in both notes.
**Goals:** G15 checkpoint (obstruction learned); B123 taken; B126 added; B124's payoff lowered to 1/3.
**Assumptions:** none new or changed.
**Basket:** B119 (native writing), B120 (inputs and outputs); taken: B119 as the selected next step.

I haven't started B119; it waits for a go-ahead.
