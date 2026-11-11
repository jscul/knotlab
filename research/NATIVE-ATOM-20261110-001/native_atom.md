# Which atom a growth law grows

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `NATIVE-ATOM-20261110-001` (backlog B106, G15 with G16; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered
in [preregistration.md](preregistration.md), frozen in commit `4a6ce578f` before any run. Proof families:
`proofs/NATIVE-ATOM-20261110-001A/` (uniform growth), `…B/` (growth, then learning).

## The answer

Within the frozen class (splice a lattice torus less a point at a violated line, with one sign pattern on every line), growth alone grows
a remembering atom only with the Fano piece and its plain law; every other class-forced atom, the four-point thin atom included, is grown as
a transparent atom. But a transparent atom is still memory in waiting: learning writes it into its unsatisfiable class.

- **Proved by hand (claim U).** A uniform pattern that is not constant is satisfied by the all-zero state; a constant one is the plain law,
  and on a point- and line-transitive triple system that is unsatisfiable only on the Fano plane (`UNIFORM-FANO-20261107-001`). With lemma 2
  and freeness from `OTHER-ATOMS-20261110-001`, the uniform rule's atom acts exactly for Fano with a constant pattern.
- **Census (computed).** 1,256 uniform laws on 157 types: satisfiable every one except the Fano torus's two constant laws.
- **Growth (exact).** On K_2 and K_3 the uniform Fano piece keeps the dissonance and holds it; the uniform thin atom resolves it.
- **Then learning (computed).** On K_3 with two uniform thin atoms, both starting transparent, the frozen search wrote and held every single
  address, 9 of 9.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| U: the uniform rule's atom remembers only for Fano with a constant pattern | proved by hand (from `UNIFORM-FANO-20261107-001A` and `OTHER-ATOMS-20261110-001`) |
| Census of 1,256 uniform laws | exhaustive computation |
| B1: Fano keeps and holds the dissonance, thin resolves it, on K_2 and K_3 | exact |
| B2: learning writes 9 of 9 single addresses into uniform thin atoms | computed |

## Against the pre-registration

Everything held as frozen: U, the census, B1 and B2. The stop rule applies: the answer is stated for the frozen class, and the other
classes (atoms built from the line's own neighbourhood, rules reading more than one violated line) are recorded as backlog B117, not
searched.

## What it changes

- **A52, read again.** The premise says the experimenter chooses the atom and the line. For the Fano piece nothing has to be chosen: it is
  the one handle whose uniform law contradicts itself, so a uniform growth rule fired at a dissonance grows it acting. For any other
  class-forced atom the class has to be supplied, and learning supplies it. So A48's choice of the Fano plane was the choice that lets
  growth alone keep the memory; the memory itself does not need it.
- **For the owner's "nothing designed".** Memory can grow with nothing designed in two ways: a uniform rule growing Fano handles at
  dissonances, or a uniform rule growing any class-forced handle followed by learning.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52 (a history line added). None added or changed in status.

## Corrections

None.

## In the owner's words

A rule that grows the same handle everywhere, with the same signs on every line, makes a handle that remembers only if the handle is the
Fano plane: it is the one pattern whose plain law contradicts itself. Any other handle grows open, and learning then closes it into a
memory.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which atom a growth law grows (B106) | **Status:** Successful | answered for the frozen class: only Fano by growth alone, any class-forced atom with learning |
| Local direction — the layered memory | Practically complete for this phase | rule, nesting, units, parallel moves, function and native growth all settled |
| Broader exploration — learning program | Known alternatives | naming knots as layers, whether every host is critical, growth beyond substitution |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | memory grown natively, by uniform growth and learning |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Layers through a naming knot (`NEST-ATOMS-20261110-001`#4) | 2/3 — Substantial | 1/3 — Exploratory | compare a parity name with a three-edge cut as the channel between levels → one reading of layers, or two | Selected · awaiting go-ahead |
| 2 | Is every host critical (B115) | 1/3 — Incremental | 2/3 — Testable | the Hall count on the torus → AND for every host, or a non-critical host | Alternative · deferred |
| 3 | Growth rules beyond substitution (B117) | 1/3 — Incremental | 1/3 — Exploratory | atoms built from a line's own neighbourhood → a second native source of handles, or none | Alternative · deferred |
| 4 | A writing search that reads roles (B113) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |
| 5 | Capacity of the learned memory (B98) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** is the line's last item at payoff 2; after it the learning line has only incremental work left in this phase, and the coordinator
  may prefer another line.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B106 taken; B117 added. **Assumptions:** none new or changed in status;
A52 history line.
**Basket:** `NEST-ATOMS-20261110-001`#4 (layers through a naming knot), the line's only item at payoff 2; taken: it, as the selected next step.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (05:56 UTC): the answer (a uniform growth rule remembers only with the Fano plane;
every other class-forced handle grows open and learning closes it), claim U and why, the census and the checks, what it says about A48,
the learning note brought up to date, the staging slip in `cefd5dbc0` (another thread's goals hunks committed under this epic's message),
both tables above with layers through a naming knot selected, the Corrections, Goals and Assumptions lines, and the Basket line.
