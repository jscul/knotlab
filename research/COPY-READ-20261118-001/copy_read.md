# SEED's copy clause read in the knots

Epic `COPY-READ-20261118-001`, 18 November 2026, by Claude. It takes `MID-RULE-20261118-001`'s first direction, with the
coordinator's go-ahead. Goals G1 and G16; challenges A101. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `3b771378c` at 11:28:57 UTC.
- The run: from 11:29 to 11:42 UTC (105 runs).
- Proof: [proof.md](../../proofs/COPY-READ-20261118-001A/COPY-READ-20261118-001A-P001_absorb/proof.md).
- Code: [copylib.py, run.py, checks.py and readout.py](../../experiments/COPY-READ-20261118-001B/COPY-READ-20261118-001B-E001_copy/).
- Results: [results.json.gz and readout.json](../../artifacts/COPY-READ-20261118-001B/COPY-READ-20261118-001B-E001_copy/).

## The answer

**SEED's copy step cannot be told from a refused fill by the fill's own knots or by the betweenness among its distinctions. Every
one of the 566 fills that pulled an uncrossed split into the grid without adding an order looked, at both tiers, like a refused
fill. Absorbing fills are rare: 566 among 1,787,986 crossing-making fills (0.03%), offered early (median n = 10). One step out, the
ball covers 96% of the base, and only 4% of held-out absorbing fills had a picture class seen before, so that tier could not be
tested.**

- **Two end knots, always.** Every absorbing fill makes a new crossing, so each of its certificates has two end knots (A1). Each
  absorbing extension here had a single knot set.
- **Tier 0 and the closure tier.** The clean-witness fraction is 0, pooled and held out. Every test absorbing fill fell in a class
  seen before, and every such class also held refused fills. There are 86 confirmed look-alike pairs (exact isomorphism, within
  runs). As the advisor warned, at a 3,000-to-1 imbalance coarse classes mix on base rate alone. So this shows that the move's own
  knots carry no sign of absorbing, not that a finer local reading fails.
- **Tier 1.** The pooled clean fraction is 1.0, but the radius-one ball holds 96% of the base, and held-out only 4% of absorbing
  fills had a seen class. That is sparsity, not evidence either way, as in `KEEP-READ-20261118-001`.

**In the owner's terms.**
- Pulling a loose part of the line into the grid needs a fill tied by two knots that each extend a pair outward (proved earlier).
  Most such fills add a third order instead.
- Their own knots, and every betweenness among their distinctions, look the same either way.
- What decides is whether the new crossings copy an existing split's crossings exactly. That is a fact about the whole base's
  crossings, which these bases are too small to localise.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | Absorbing < 1% of crossing-making fills | held | 0.03% |
| P2 | Tier 0 and closure: clean witness 0 | held | 0 and 0; 86 confirmed look-alikes |
| P3 | Tier 1 held out: fewer than half with a seen clean class | held | 4% (all through unseen classes) |
| P4 | Median n of absorbing offers below 15 | held | 10 |

4 of 4 held. The disclosed exploration had already settled P1 and P2.

## What the knot picture explained

- **Why absorbing fills are rare.** Two end knots can make a fill's new distinction lie beyond two different old ones. Almost always,
  that puts it outside the grid as a third order. Only when the two crossings it makes line up with an existing split's crossings
  does it join the grid.
- **Why they come early.** Uncrossed splits exist only until the grid has absorbed them.

## What it means for A101 and the goals

- **A101** stays under challenge. Holding two orders can be read locally (`MID-RULE-20261118-001`). Growing them over the whole line
  needs the copy step, which shows no local sign at the move's own knots.
- **G1:** obstruction learned (at the move's own knots and its closure).
- **G16:** capability gained (held-out scoring of a local reading).

## Limitations

- Runs to n = 30; the absorbing fills come before n = 15, on bases of 10 to 20 distinctions, where one step out is the whole base.
- The base-rate caveat for tier 0 (the advisor's): with about 3,000 refused fills per absorbing one, mixed classes are expected
  even for a reading that carries a weak signal.
- The advisor was consulted after the freeze but before the read-out, not before the freeze as the standing rule asks. Its view
  shaped the caveats above.

## Reproduce

```sh
cd experiments/COPY-READ-20261118-001B/COPY-READ-20261118-001B-E001_copy
../../../.venv/bin/python -B checks.py
../../../.venv/bin/python -B run.py --procs 8 && ../../../.venv/bin/python -B readout.py
```

## Advisor

Consulted after the freeze and before the read-out. This was a lapse: the standing rule asks for a consultation before the freeze.
- **Its view.** The design was sound but mostly settled by the exploration, and only the tier-1 result could carry information.
  Tier-0 mixing at a 1000-to-1 imbalance says little about locality, and the tier-1 held-out score cannot separate "not local" from
  "too sparse".
- **Its suggestions** for an informative follow-up: break down the held-out score by class status, add a shuffled-label baseline,
  and measure the witness radius (how far from the move the copied split sits). It also proposed the copy predicate "the end
  pair (v, v′) shares a knot with an active split's ends", fixed on exploration runs and scored on the rest. These are taken as the
  next direction.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: SEED's copy step in the knots | **Status:** Successful (referee pending), 4 of 4 held | No sign at the move's own knots or closure; one step out untestable here |
| Local direction: growth by a local rule | Obstruction learned (move's own knots) | The copy step is rare and looks like raising |
| Broader exploration: how far the copy step's evidence sits | Unexplored | The witness radius is the direct measure |
| Long-term goal: G1 | Obstruction learned | Growing two orders over the whole line needs a non-local copy step |

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The witness radius: for each absorbing fill, how many knot-steps away the copied split and its crossers sit, on bases grown larger by NNF from long lines | 2/3 | 3/3 | Measure the distribution → stop at a bounded radius (a local rule exists at that radius) or growth with the base | Selected |
| 2 | The advisor's copy predicate ("the end pair shares a knot with an active split's ends"), fixed on exploration runs and scored on the rest for precision and recall | 2/3 | 3/3 | Score it → stop at its precision | Alternative |
| 3 | Step back: a summary of the two-order line (NEVER-NEST to COPY-READ) for the owner, with what is local and what is not | 2/3 | 3/3 | Write it → stop when written | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (obstruction learned) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A101 stays under challenge; A99 gains this study.

**Basket:** read; nothing taken.
