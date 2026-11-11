# Reading the class, not the bit

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `CLASS-READ-20261110-001` (backlog B122, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen in commit `10e19e0a3` before any run. Proof family: `proofs/CLASS-READ-20261110-001A/`.

## The answer

*Corrected on 2026-11-10 (`NOT-INSIDE-20261110-001`).* The readings below were computed with one fixed signing per class, and they read
that frame, not the class: under another signing of σ each σ-reading network has a satisfying state, and no reading that depends only on
the classes can tell non-acting classes apart (theorem M there). A class-level reading sees only whether a leaf acts. See
`docs/CORRECTIONS.md`.


Reading the full class does not complete the basis. The parity reading found after `GATES-20261110-001` holds up on new networks, but it is
the only one: names tell apart just one non-acting class, and only upward.

- **R1 held (the re-test).** On a thin torus (3,2,2), 718 of 6,800 one-leaf networks read exactly the line through the acting class in
  direction (1,1), the same direction as before.
- **R2 failed.** On two leaves, only one of the nine joint minterms of the non-acting classes is read, the one where both leaves sit in
  that special class; 67,500 networks give four readings of the nine non-acting pairs.
- **The structure.** A leaf's readings form a chain: its acting class; its acting class or the special class σ; everything. So every
  reading is monotone in two indicators per leaf, and "parity + AND + OR + constants" is not reached: the parity reading always includes
  the acting class, so its negation is never available.

## Stored memory or the law?

Plainly: the class is stored memory. It is a property of the learned signs, set by learning when it winds a leaf's handle, and kept while no
dissonance sits in the leaf; nothing in the triangulation or the plain law chooses it. But both references the readings use are fixed by the
law: ω is the class the torus cannot satisfy, and σ is the class it satisfies most tightly (4 states against 16 and 20, computed after the
run). So what the networks read is the stored class compared with two law-fixed landmarks. Had "parity + AND + OR + constants" appeared, it
would have been reading stored memory, but only through those landmarks, and the computing would have lived in where the landmarks sit.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| R0: every reading 1 where a leaf acts | proved (from `GATES-20261110-001A`) |
| R1: the line through ω in direction (1,1) read, on new networks | exhaustive computation |
| R2 failed: one joint minterm of nine | exhaustive computation |
| The chain {ω} ⊂ {ω, σ} ⊂ all; σ the most constrained class | computed (the state counts post hoc) |

## Against the pre-registration

R0 and R1 held; R2 failed. The failure line was not crossed. The state counts that explain σ were computed after the run.

## What it changes

- **For "computes".** Every gate found so far reads upward: "all of these", "any of these", "the stored class is at least σ". Negation is
  still missing, now with the class as the stored state too. The only route left open by `GATES-20261110-001`'s lemma C is names reading
  inside a cut leaf (backlog B123).
- **A second readable distinction.** Each leaf carries two readable levels above its plain transparent classes, not one: acting, and the
  rigid class σ. A memory that writes σ as well as ω could hold three readable values per leaf, read monotonically.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52. None added or changed.

## Corrections

None.

## In the owner's words

A stored pattern can be wound four ways, and the network can read two of them: the way that holds a contradiction, and the way that holds
its states most tightly. The other two ways look alike from outside. The network still says only "yes, at least this much", never "not this".

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — reading the class, not the bit (B122) | **Status:** Partially successful | the parity reading re-found (R1); the complete basis not reached (R2 failed) |
| Local direction — gates from cuts and names | Obstruction learned | readings stay monotone with classes as stored state; the readable levels form a chain |
| Broader exploration — learning program | Known alternatives | negation inside a cut leaf, native writing, composing gates |
| Long-term goal — G15 Learning: a point in a learned knot pattern | No demonstrated advance toward "computes" | still no negation |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Negation inside a cut leaf (B123) | 2/3 — Substantial | 2/3 — Testable | the census of `GATES-20261110-001`'s F4′ with larger leaves (thin (3,2,2), the Fano piece) and names inside them → a NOT, or a proof that every reading is monotone, which would close the gates question | Selected · awaiting go-ahead |
| 2 | Native writing (B119) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |
| 3 | Composing gates (B124) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |
| 4 | Inputs and outputs (B120) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |

- **#1** is the last route to a negation that the proved limits leave open; if it fails too, the next step is to prove that these networks
  only ever read monotone functions, and the gates question closes.

**Corrections:** none. **Goals:** G15 checkpoint (obstruction learned); B122 taken. **Assumptions:** none new or changed.
**Basket:** B123 (negation inside a cut leaf), B119 (native writing); taken: B123 as the selected next step.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (17:04 UTC): the partial answer (the parity reading re-found, the basis not
completed), R1 and R2's verdicts, the chain of readings and σ's post hoc explanation, the plain answer on stored memory against law-fixed
landmarks, both tables above with B123 selected, the Corrections, Goals and Assumptions lines, and the Basket line.
