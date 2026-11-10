# Three held inputs

Epic `THREE-IN-20261110-001` (backlog B133, G15 with G16; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md) in two stages: the census's design (stage 0, commit `9387eb515`) before it ran, and the learning
test with its prediction (stage 1, commit `f3dff17a6`) after the census and before any learning run. Proof families:
`proofs/THREE-IN-20261110-001A/` (the census) and `proofs/THREE-IN-20261110-001B/` (learning).

## The answer

**No parity, no majority, nothing non-unate: at these interfaces a knot memory's maps of three held points are unate, and the only total
ones copy or negate a single input.** Self-duality (theorem D) would allow majority and parity with three inputs; none occurs.

- **The census (exact).** On every class of six spaces, at every group, 2,976,256 maps with three held points and an output in the
  group's neighbourhood: every one self-dual; no total majority, no total parity, no partial map that moves an input both ways. The only
  total maps (1,074) copy or negate one input, the other two never reaching the output; they come from frozen pairs in a few classes.
- **Why that covers every law (lemma G, by hand).** Every Kasteleyn law is its class's representative up to gauge flips and line
  complements; a gauge flip at an interface point negates that input or the output, which keeps a map's kind. So no knot law of these
  spaces computes parity or majority at these interfaces.
- **Learning (computed).** The credit learner with the sturdier probe, extended to three inputs, never stopped on parity or majority (8 of
  8), and learned and held the census's single-input map at 2 of 4 interfaces; on the two-level spaces that map lives in 12 of 256
  classes and was not found in the budget.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Every map with three held points is self-dual (theorem D) | proved by hand; checked on every map |
| No parity, majority or non-unate map at these interfaces, for every law of these spaces | exhaustive census with lemma G |
| The only total maps copy or negate one input (1,074) | exhaustive census |
| Parity and majority never stopped (8 of 8); the single-input map learned at 2 of 4 | computed, frozen |

## Against the pre-registration

Stage 1's predictions: I held (8 of 8 never stopped); **L3 failed** (2 of 4; the mark was 3). The census's question, frozen in stage 0,
had no predicted answer; its answer is that no non-unate map occurs.

## What it changes

- **The memory's power with held inputs is limited by more than self-duality.** At every interface tested, held inputs reach the output
  only unately: no input both raises and lowers it. With stored roles entering only monotonically (theorem M), the learned knot memory
  computes neither parity nor majority of three held points here. General NAE systems with hidden points can define parity (external:
  the standard co-clone bases), so the limit is the knot space's, not the logic's, and whether it holds for every knot space and interface
  is open (backlog B136).
- **The sturdier probe holds up with eight examples:** no false stop on two impossible targets.

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None.

## In the owner's words

Hold three points of a learned knot and read a fourth: the answer can follow one of them, or be forced only when they agree, but it never
counts them, never takes a vote, and never turns one input's push around. A learner told to make it count or vote never pretended it had.

## Position and next directions

The line pauses after this epic at the owner's decision (2026-11-10), not dropped; the directions are recorded for a later go-ahead.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three held inputs (B133) | **Status:** Successful | a definite answer: no non-unate map at these interfaces (exact); impossible targets never accepted |
| Local direction: maps of held points | Exhausted for this phase | every map tested is unate; the open question is whether that is a theorem |
| Broader exploration: learning program | Known alternatives | deeper memories, unateness as a theorem, the probe as a theorem |
| Long-term goal: G15 Learning: a point in a learned knot space | Obstruction learned | held inputs reach a knot memory's output only unately here |

**Next step:** Research directions — selected: #1 (paused: no epic starts until a new go-ahead)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Deeper memories from examples (B135) | 2/3 — Substantial | 2/3 — Testable | as recorded | Selected · paused |
| 2 | Are maps of held points unate (B136) | 2/3 — Substantial | 1/3 — Exploratory | the census at radius 2 and on spaces of genus 6, then a proof attempt from the knot law's local structure → a theorem that every map is unate, or a parity gadget | Alternative · deferred |
| 3 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |
| 4 | Single-input maps through rare classes (from this epic) | 1/3 — Incremental | 2/3 — Testable | a longer budget or credit on the frozen pair → the map learned on the two-level spaces, or a reason it is not | Alternative · deferred |

**Corrections:** none. **Goals:** G15 checkpoint (obstruction learned); B133 taken; B136 added. **Assumptions:** none new or changed.
**Basket:** B135 (deeper memories from examples), B136 (are maps of held points unate), B130 (a probe that is a theorem); taken: B135
as the selected next step, paused until a go-ahead.
