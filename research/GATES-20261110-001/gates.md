# A learned network that computes

Epic `GATES-20261110-001` (sub-goal B118, G15; program learning), 2026-11-10, at the coordinator's go-ahead after the owner's "Yes, let's
do that." Pre-registered in [preregistration.md](preregistration.md), frozen in commit `6c0331519` before any run. Proof family:
`proofs/GATES-20261110-001A/`.

## The answer

Not in the families tried: cuts and names together read AND and OR of the stored acting bits, and single bits and constants, but never
a negation, so they do not compute every function of those bits here.

- **Proved by hand.** A cut reads AND (P1). A component with no satisfying state makes the whole network unsatisfiable (P2), so every
  reading is 1 where both bits are 1, and XOR, NAND and the rest of the functions that are 0 there cannot be read by one such network. A
  cut leaf read only from outside can never be negated (lemma C): a negation needs names that look inside the leaf.
- **Computed.** 43,091 networks in five frozen families: AND in the cut family, OR in the two families with two components joined by
  names, a_2 in the satisfiable-host family, and in the one-bit family 0, a_1 and 1 but never NOT a_1 (17,710 networks, every naming
  of its component, inside the leaf included).
- **Post hoc.** Names read more than the acting bit of a closed leaf: some networks read the parity of a leaf's two class bits, a reading
  that is not monotone. Whether the full class, read through names, gives every function is the next question.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| P1: a cut reads AND | proved (theorem N) |
| P2: an unsatisfiable component forces O = 1; nothing 0 at (1, 1) in one network | proved by hand |
| Lemma C: no negation through a cut read from outside | proved by hand |
| The census of 43,091 networks: AND, OR, a_1, a_2, constants; no NOT | exhaustive computation per network |
| Names read the parity of a leaf's class bits | computed, post hoc |

## Against the pre-registration

P1, P2 and P3 held; P4 failed: NOT a_1 was predicted in F4′ and was not found. The failure line (a violation of P1 or P2) was not crossed.
Lemma C and the parity reading were found after the run.

## What it changes

- **For the owner's "it's like a computer".** With acting bits as the stored state, the layers built so far compute only monotone
  functions: AND through cuts, OR through names joining separate contradictions. A computer needs a negation, and none appeared.
- **Where a negation could come from.** Lemma C rules out cut leaves read from outside, and P2 rules out leaves whose contradiction is a
  whole component. What is left is names reading inside a cut leaf (none found for the smallest leaf), and the full class of a leaf, whose
  bits names read through parity.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52. None added or changed.

## Corrections

None.

## In the owner's words

The layered memory can already say "all of these" and "any of these" about what it has stored. It has not yet said "not this": every
network tried says yes whenever a stored pattern holds its tension, and none says yes only when it doesn't. The patterns do carry a finer
signal, which way their tension is wound, and that one comes through as an odd-or-even count.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a learned network that computes (B118) | **Status:** Partially successful | AND and OR read and three limits proved; the predicted negation not found |
| Local direction — gates from cuts and names | Obstruction learned | no negation of an acting bit in the frozen families; lemma C says where one would have to come from |
| Broader exploration — learning program | Known alternatives | reading the full class, negation inside a cut leaf, composing gates, native writing |
| Long-term goal — G15 Learning: a point in a learned knot space | No demonstrated advance toward "computes" | monotone readings only, so far |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Reading the class, not the bit (B122) | 2/3 — Substantial | 2/3 — Testable | take each leaf's two class bits as the stored state and census which functions of them the frozen families read; names already read their parity → AND, OR and parity (a complete basis with constants), or a class confined | Selected · awaiting go-ahead |
| 2 | Negation inside a cut leaf (B123) | 2/3 — Substantial | 2/3 — Testable | F4′ with larger leaves (thin (3,2,2), the Fano atom) and hosts, names inside the leaf → a NOT, or a proof that names inside a cut leaf stay monotone too | Alternative · deferred |
| 3 | Native writing (B119) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |
| 4 | Composing gates (B124) | 2/3 — Substantial | 1/3 — Exploratory | make a gate's reading a stored bit of the next network (a role with two values) → gates wired, or readings that do not compose | Alternative · deferred |
| 5 | Inputs and outputs (B120) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |

- **#1, #2 and #3** tie at the top rating and are independent. #1 is selected because the run already shows names reading a parity of class
  bits; with AND and OR that would be a complete basis, if it holds as a frozen test.

**Corrections:** none. **Goals:** G15 checkpoint (no demonstrated advance toward "computes"; obstruction learned); B118 taken; B122, B123
and B124 added. **Assumptions:** none new or changed.
**Basket:** B119 (native writing), B120 (inputs and outputs); taken: none, because #1 continues this result directly and ties with B119,
which stays in the basket.
