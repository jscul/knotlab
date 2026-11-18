# What the knots read in SEED's second phase

Epic `KEEP-READ-20261118-001`, 18 November 2026, by Claude. It takes `KNOT-SWITCH-20261118-001`'s first direction, chosen by the
coordinator. Goals G1 and G16; challenges A101. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `5d06adb51` at 08:53:13 UTC.
- The run: from 08:53 to 08:57 UTC (105 runs, 764,989 moves, 36,229 extensions after the switch).
- Proof: [proof.md](../../proofs/KEEP-READ-20261118-001A/KEEP-READ-20261118-001A-P001_local/proof.md).
- Code: [keeplib.py, run.py, checks.py and readout.py](../../experiments/KEEP-READ-20261118-001B/KEEP-READ-20261118-001B-E001_keep/).
- Results: [results.json.gz and readout.json](../../artifacts/KEEP-READ-20261118-001B/KEEP-READ-20261118-001B-E001_keep/).

## The answer

**No local reading of the knots is SEED's second phase. A move's own knots, and even every betweenness that the states imply among
the distinctions it uses, leave about one in five of the fills that keep two orders looking exactly like fills that raise them.
Reading one step further already takes in most of the base on these sizes, and still leaves a few undecided. So what keeps two
orders after the switch is not visible near the move. It is the crossing of splits, which depends on the whole base.** One local
sign works in one direction: when the new distinction is the middle of two or more of its knots, the fill never raises the orders.

- **At the move's own knots (tier 0) and at the betweenness among its distinctions (closure tier):** the best possible rule
  recognises 79% of the extensions that keep two orders, and 82% of those SEED accepts (R2's clean-witness fraction). 310 and 392
  pairs of moves, confirmed isomorphic, look the same and differ in outcome. The closure adds nothing over the move's knots.
- **One step out (tier 1):** 99.7% of keeping extensions have a clean witness, and 100% of SEED's accepted ones. But the radius-one
  ball holds 88% of the base on average, so this reading is nearly global. Even so, 3 confirmed pairs look the same and differ.
- **Two steps out (tier 2):** every keeping extension has a clean witness, but the ball holds 99.8% of the base. That is the whole
  base, so nothing local is shown.
- **The frozen knot rules:**
  - "No new filled knot", "no new even knot set" and "a disconnected pair graph" accept every keeping extension, and also 30,890
    to 31,180 raising ones.
  - "The new distinction is the middle of two or more knots" accepts no raising extension, and recalls 18% of SEED's accepted ones.
  - None matches SEED.
- **SEED's acceptance and keeping two orders differ slightly.** Of 3,457 extensions that keep two orders, SEED refuses 144: they
  keep two orders while giving a split crossings it did not copy.

**In the owner's terms.**
- The first fill shows itself in the knots: four knots close on four distinctions (`KNOT-SWITCH-20261118-001`).
- After that, whether a new fill keeps the two orders or adds a third cannot be seen in the fill's own knots. A fill completing a
  square's corner and a fill twisting three distinctions in a row use the same three knots. They differ only in whether the two
  splits they cross run in different orders or the same one, and that is a fact about the whole base.
- So the rule that keeps two orders must read something non-local after the switch, the way the never-nest rule reads the number
  of orders.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | Tier 0 is obstructed | held | clean-witness fraction 0.79 |
| P2 | Tier 1 obstructed; clean witness over repeated classes 0.3 to 0.6 | **failed** | obstructed (0.997), but 0.99 over repeated classes; the radius-one ball covers 88% of the base |
| P3 | Tier 2 obstructed, or its balls cover ≥ 3/4 of the base | held | coverage 99.8% |
| P4 | Closure tier: clean witness ≥ 0.8, not exact | **failed** | 0.79, no better than the move's own knots |
| P5 | No rule matches SEED; two middles has no false accept and recall 5–15% | **failed** (recall) | no match; no false accept; recall 18% |

2 of 5 held. The misses are one finding: the bases are small, so one step out is already nearly the whole base, and the closure among
the move's own distinctions carries no more than its knots.

## What the knot picture explained

- **Why the move's knots cannot decide.** The corner knot set is one pattern for a cell's fill and for a twisted corner (R1). Its
  three old distinctions are pairwise between one another in the same way in both cases, so the closure among them is the same too.
- **Why two middle knots seem safe** (an explanation, not proved). A fill whose new distinction lies between two different old
  pairs is pinned toward the majority of the distinctions around it, as a median of present distinctions is. A median of present
  distinctions never makes two splits of one order cross (`NEVER-NEST-20261118-001A`, N3).
- **Why one step out is nearly global here.** In a grid of 24 distinctions grown by fills, every distinction shares knots with most
  of the others.

Known mathematics, labelled: medians in a product of two chains; locality of a decision over isomorphism classes of neighbourhoods.
What this adds, in the program's terms: the second phase of the rule that keeps two orders reads the whole base, as the cap does.

## What it means for A101 and the goals

- **A101** stays under challenge. The one free step is read locally in the knots (the first filled knot), but keeping two orders
  afterwards is not: it needs the crossings, which are global.
- **G1:** obstruction learned. No local knot reading keeps two orders after the switch on these bases.
- **G16:** capability gained. The locality of a reading is measured by its clean-witness fraction, with coverage as the control.

## Limitations

- Bases of at most 24 distinctions: one step out covers most of the base, so tiers 1 and 2 cannot separate local from global here.
  A larger base, or a growth that keeps knots sparse, is needed to test radius one honestly.
- Picture classes by the Weisfeiler–Lehman hash; collisions confirmed by exact isomorphism within runs only.
- One seed per bracketing.

## Reproduce

```sh
cd experiments/KEEP-READ-20261118-001B/KEEP-READ-20261118-001B-E001_keep
../../../.venv/bin/python -B checks.py
../../../.venv/bin/python -B run.py --procs 12 && ../../../.venv/bin/python -B readout.py
```

## Advisor

Consulted once before the freeze. It corrected the unit of the obstruction: acceptance is over knot sets, so an obstruction must hold
for all of an extension's knot sets. It also proposed:
- R2's best-rule measure;
- the closure tier;
- the coverage control, with its warning that on small bases a radius-two ball is the whole base;
- the predictions P2 to P5, three of which missed.

It was not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: SEED's second phase in the knots | **Status:** Successful (referee pending), 2 of 5 held | Obstruction at the move's knots and its closure (79%); one step out is nearly the whole base here |
| Local direction: keeping two orders locally | Obstruction learned | The deciding fact is a crossing, which is global |
| Broader exploration: a local rule on larger bases | Unexplored | Radius one is not local on bases of 24 |
| Long-term goal: G1 | Obstruction learned | After the switch, two orders are kept by a global reading |

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A local rule built on the safe sign: after the first fill, take only fills whose new distinction is the middle of two or more of its knots, else subdivide. It reads only the move's knots after the switch. Does it keep two orders and refill full grids (the median refill of N3 has three middle knots)? | 3/3 | 3/3 | Run it from every bracketing and the 2 × 2 pattern, knot-local and free → stop at strong tiers, a raise, or starvation | Selected |
| 2 | Test radius one honestly: grow SEEDK grids to 60–100 distinctions, where a radius-one ball is a small part, and measure the clean-witness fraction there | 2/3 | 3/3 | Run SEEDK to n = 80 from a few bracketings with coverage recorded → stop at a radius with fraction 1 and coverage below a half, or an obstruction | Alternative |
| 3 | The 144 extensions SEED refuses though they keep two orders: what they make | 1/3 | 3/3 | Classify them by their crossings → stop at a description | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (obstruction learned) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A101 stays under challenge, with this study's reading; A99 gains it.

**Basket:** read; nothing taken.
