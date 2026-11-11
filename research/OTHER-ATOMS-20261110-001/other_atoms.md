# Other atoms, a challenge of A48

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `OTHER-ATOMS-20261110-001` (backlog B97, G15 with G16; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered
in [preregistration.md](preregistration.md), frozen in commit `1fd95cc5f` before any run, with an addendum for ticket D frozen in
`6f43acb56` before it ran. Proof families: `proofs/OTHER-ATOMS-20261110-001A/` (the role of every torus atom), `…B/` (holding a unit),
`…C/` (writing), `…D/` (free tori).

## The answer

The learned memory does not need the Fano plane. It needs a torus with a sign class that no state satisfies.

- **Proved by hand** (ticket A), given two facts about the atom's torus: a torus atom acts as the line it replaced exactly in the classes
  where its torus has no satisfying state, and is transparent where it has one, provided the torus is **free** at the removed point
  (flipping any one of that point's three sides leaves a satisfiable law). In a class where it acts, it holds a unit of the floor
  dissonance in every state that satisfies its lines. So the atom rule holds for such atoms grown on any orientable drawn knot pattern with a
  Kasteleyn law, not only octahedral spheres, and for atoms at any distance, adjacent ones included.
- **Computed, exhaustive per torus** (ticket D): all 157 lattice-torus types to 30 points (and the thin tori of even index to 40) are free
  in every class. The class-forced ones are the Fano torus and one thin torus of each even index, each with exactly one unsatisfiable class.
  So twenty atoms remember, the Fano piece and the thin-torus atoms with 4 to 40 points, and every other lattice-torus atom here is
  transparent in every class and remembers nothing.
- **The frozen tiers.** T1 (ticket A): on 60 splices each (every line orbit of K_2 to K_4, every compatible splice), the 8 class-forced
  types of the frozen 29 act in exactly their torus's unsatisfiable class with an unsatisfiable local system, and the 21 others are
  transparent in all four classes. T2 (ticket B, exact): with two and three atoms of four types on K_3, every one of 960 classes satisfies
  R-a and R-b. T3 (ticket C, computed): 72 of 72 addresses written in sequence were reached and held after a disturbance, for the Fano
  atom and three thin-torus atoms alike.
- **The smallest atom that remembers** is the thin torus of index 4 less a point: three points and four lines, against the Fano piece's six
  and seven. It wrote and held addresses with the fewest configurations searched.

By the frozen rule, A48 is **overturned as a limit** and replaced by A52 (a grown handle is a class-forced torus atom, free at its point).

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Lemma 1: two completions of the new sides, gauge-equivalent | proved by hand |
| Lemma 2: the atom's patterns are its torus's satisfiability, with P's sides flipped for the non-constant ones | proved by hand |
| Lemma 3: in an unsatisfiable class the atom holds a unit | proved by hand |
| The theorem: the atom rule on any Kasteleyn host, atoms adjacent or not | proved by hand, given freeness and one unsatisfiable class |
| Freeness and the unsatisfiable classes of 157 torus types | exhaustive computation by SAT (ticket D); stress test at 31 to 34 points |
| T1 on 29 types, 1,740 splices; lemma 2 on 6,960 class readings | exhaustive computation (tickets A and D) |
| T2: R-a and R-b on 960 classes | exact, SAT over every state (ticket B) |
| T3: 72 writes held | computed (ticket C) |
| Freeness in every class holding a uniform matching, on every lattice torus | proved by hand (a remark, not used) |

## Against the pre-registration

All seven predictions held: P1 (every class-forced atom passes T1, in its torus's unsatisfiable class), P2 (every all-satisfiable atom is
transparent everywhere), P3, P4, and D1 to D3. Both code controls passed: the Fano piece through the new code reproduced
`ATOM-RULE-20261110-001A`'s check on all 60 splices of K_2 to K_4, and `ADDRESS-SEQ-20261110-001A`'s K_3 rows exactly.

Two things were not in the frozen plan. The lemmas were found after ticket A ran, by reading its result (every role was the same on all 60
splices, which suggested the host did not matter); ticket D was then added and frozen before it ran. And the addendum first gave ticket
A's run time as 04:35 UTC; it was 04:13, from its result file, and was fixed in `fb861b112` before ticket D ran. Ticket A's committed
result is a re-run after the addendum, identical to the first run except for the pre-registration's hash.

## What it changes

- **The atom rule.** `ATOM-RULE-20261110-001`'s theorem is contained in this one, with both of its restrictions removed (separated atoms,
  octahedral spheres) and without its local check or its classification of line neighbourhoods: the local system it found unsatisfiable
  in the acting class is lemma 3's, unsatisfiable for lemma 3's reason. Backlog B96, the rule beyond octahedral spheres, is answered. The
  learning note's list of what lies outside the theorem (`LEARN-NOTE-20261110-001`, section 3) is overtaken for overlapping atoms and
  other spheres; it was accurate when written, so this is not a correction. Free units when fewer atoms act than there are units remain
  computed only.
- **Growth.** `GROW-HANDLE-20261110-001`'s reading, that growth alone does not remove a sphere's dissonance and learning then removes it
  through the handle, holds for every class-forced free atom. An atom whose torus satisfies every class is transparent in all four: it
  deletes its line's constraint.
- **The learning line.** Every result from `GROW-HANDLE-20261110-001` to `ADDRESS-SEQ-20261110-001` was computed with the Fano piece; the
  rule that explains them is now proved for twenty atoms, and writing was rerun with three of them.

## Perspective

In the language of constraint satisfaction an atom is a gadget: a sub-instance with three dangling variables that realizes a relation on
them. Lemma 2 says the relation it realizes is the deleted constraint exactly when the closed instance is unsatisfiable and its
one-side flips are satisfiable. That reading is close to folklore and no novelty scan was run. What the program adds is where the bit
lives: in a homology class of the signs, so a learned memory is a choice of handle class, made by learning and read from the atom's own
signs.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50. **A48 overturned as a limit** (the challenge): the memory does not need the Fano plane.
**A52 added** (kind scope): a grown handle is a class-forced torus atom, free at its point.

## Corrections

None.

## Stress test

One size past ticket D: every lattice-torus type with 31 to 34 points (38 types) is free in every class, and the class-forced ones are the
thin tori of index 32 and 34, each with one unsatisfiable class ([stress_test.py](stress_test.py), [stress_test.json](stress_test.json)).

## In the owner's words

A handle remembers because its torus has a sign class that no state can satisfy. In that class it stands for the line it replaced and
keeps the tension; in the classes its torus can satisfy, it lets everything through. Any torus like that works, and the smallest has four
points. A torus that can satisfy every class remembers nothing.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — other atoms, a challenge of A48 (B97) | **Status:** Successful | the memory needs class-forcing, not the Fano plane; proved for twenty atoms on any host |
| Local direction — the learned memory in atoms | Capability gained | the rule proved by hand for every class-forced free torus atom, atoms adjacent or not |
| Broader exploration — learning program | Known alternatives | atoms within atoms, capacity, freeness in general, a native choice of atom |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | a memory whose rule is proved by hand and does not depend on the atom chosen |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Atoms within atoms (B104) | 2/3 — Substantial | 3/3 — Ready | grow a knot sphere carrying two Fano pieces, less a point, as one atom: lemma 2 says it acts as its line exactly where its closed space has no satisfying state, on small cases where both inner atoms act → a two-level address, or a composite atom that is not free | Selected · awaiting go-ahead |
| 2 | Capacity of the learned memory (B98) | 1/3 — Incremental | 3/3 — Ready | write every acting subset of three and four atoms, smaller ones included → all 2^g − 1 written and held, or some not | Alternative · deferred |
| 3 | Every torus is free (B105) | 1/3 — Incremental | 2/3 — Testable | prove freeness in the unsatisfiable class from the least states, and in the classes no uniform matching reaches → freeness a theorem for lattice tori, or a torus that is not free | Alternative · deferred |
| 4 | Which atom a growth law grows (B106) | 2/3 — Substantial | 1/3 — Exploratory | ask which uniform local growth rules can produce a class-forced atom, the 4-point thin torus first → a native rule that grows memory, or none | Alternative · deferred |
| 5 | Learner local minima (B90) | 1/3 — Incremental | 3/3 — Ready | list the 10 stuck ends' dissonance, try the targeted search from each → described and escapable, or not | Alternative · deferred |
| 6 | The cost of writing (B99) | 1/3 — Incremental | 2/3 — Testable | shortest writing paths by bidirectional search → a cost per unit moved | Alternative · deferred |
| 7 | The rule beyond octahedral spheres (B96) | 0/3 — None | 3/3 — Ready | answered here: the theorem holds on any orientable Kasteleyn host | Alternative · deferred (closed as answered) |

- **#1** is the first step toward the owner's layers: by lemma 2 a composite atom stands for its line exactly when its own closed space
  is unsatisfiable (and it is free), which for a sphere with inner atoms happens when every inner atom acts (theorem part 2) and, on the
  small cases computed so far, only then; one level's address would then be read by the next.
- **#4** asks whether memory can grow without being designed (G16): the smallest remembering atom is small enough to search for.
- **#7** is answered and closed.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B97 taken; B104 (selected), B105 and B106 added; B96 closed as
answered. **Assumptions:** A48 overturned as a limit; A52 added (Assumed).

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (04:47 UTC): the answer (the memory needs a torus with a sign class no state
satisfies, not the Fano plane), the theorem proved by hand and its freeness condition, the computed census (157 torus types free;
twenty remembering atoms to 40 points, the smallest with 4 points), the exact and computed tiers (960 classes; 54 of 54 addresses with
thin-torus atoms), the freeze commits, both tables of the position and next directions above with B104 selected and awaiting a
go-ahead, and the Corrections, Goals and Assumptions lines (A48 overturned as a limit, A52 added).
