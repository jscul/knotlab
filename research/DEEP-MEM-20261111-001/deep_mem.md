# Deeper memories from examples

Epic `DEEP-MEM-20261111-001` (backlog B135, G15; program learning), 2026-11-11, at the coordinator's go-ahead after the owner resumed the
learning line. Pre-registered in [preregistration.md](preregistration.md), frozen with the code in commit `6decb62ff` before any run on
the test spaces. Proof family: `proofs/DEEP-MEM-20261111-001A/`.

## The answer

**Yes: learning from examples reaches deeper and wider memories.** The credit learner with the sturdier probe, unchanged but for its
budget, learned and held every one of 40 composite writes on three new spaces: composites holding a leaf three levels down, and composites
of three atoms. Leaves gave 55 of 56. It never stopped on the impossible AND and never stopped inexactly.

- **Realizability (exact).** Every gate target is realizable at all 24 groups.
- **Learning (computed, frozen).** One-atom composites two levels down 16 of 16; two-atom composites three levels down 16 of 16;
  three-atom composites 8 of 8; leaves 55 of 56 (the miss ran out of budget).
- **Cost (computed).** Depth alone costs nothing: a one-atom composite two levels down needed about what a leaf needed (median 129,400
  against 120,200 steps to turn a gate on). A second atom under a composite multiplied it about eighteen times (2,300,700); a third added
  nothing more here (2,155,300). Lemma C predicts blind search to multiply with every atom; credit from pinned dissonance keeps the third
  atom cheap.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Every gate target is realizable at every group of the three spaces | exhaustive computation |
| 40 of 40 composite writes and 55 of 56 leaf writes learned and held, no false stop | computed, frozen |
| Depth costs nothing; a second atom about 18 times; a third nothing more | computed, frozen |

## Against the pre-registration

All six marks held (L, D1, D3, W3, A, R). **My predictions that D3 and W3 would fail at this budget were wrong**: the dev runs that
suggested them (3 of 4 and 5 of 8) were smaller samples on other spaces. The cost prediction held in part (atoms cost more than depth),
but the third atom did not cost more than the second. Mark A was settled by theorem D as to learning and tested only the probe, as the
pre-registration said.

## What it changes

- **The learning line's open question is answered for this range.** A learner that sees only its own dissonance under the world's clamps,
  with no address and no outside map, writes gates through memories three levels deep and through composites of three atoms.
- **What limits the memory now is what it can compute, not what it can learn.** Every map it learned is a gate; held inputs reach outputs
  only unately at every interface tested (`THREE-IN-20261110-001`). Whether that is a theorem (backlog B136) is the line's sharpest open
  question.

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None.

## In the owner's words

The learner found gates through patterns buried two levels inside others, and through patterns of three, from four examples and its own
tension, every time it was asked. Going deeper cost it nothing; each extra pattern beside the first cost it time, but less than blind trial
would.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: deeper memories from examples (B135) | **Status:** Successful | every composite write learned and held at depth 3 and with three atoms |
| Local direction: learning gates from examples | Exhausted for this phase | every gate target learned at every kind of group tested |
| Broader exploration: learning program | Known alternatives | unateness as a theorem, the probe as a theorem, cost with more atoms |
| Long-term goal: G15 Learning: a point in a learned knot space | Capability gained | learning from examples reaches deep and wide memories natively |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Are maps of held points unate (B136) | 2/3 — Substantial | 1/3 — Exploratory | the census at radius 2 and on the deeper spaces, then a proof attempt from forcing chains → a theorem that every map of held points is unate, or a parity gadget | Selected · awaiting go-ahead |
| 2 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |
| 3 | How learning cost grows with atoms (B143) | 1/3 — Incremental | 3/3 — Ready | composites of four and five atoms, same learner → cost flat, linear or multiplying in the atoms | Alternative · deferred |
| 4 | Composing gates (B124) | 1/3 — Incremental | 1/3 — Exploratory | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B135 taken; B143 added. **Assumptions:** none new or changed.
**Basket:** B136 (are maps of held points unate), B130 (a probe that is a theorem); taken: B136 as the selected next step.
