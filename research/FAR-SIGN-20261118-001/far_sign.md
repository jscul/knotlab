# Is the far pair's sign SEED's copy step?

Epic `FAR-SIGN-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead after `COPY-CLASS-20261118-001`'s referee.
It is the last study on the two-order line. Goals G1 and G16; it challenges A101. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `5999fc8ec` at 13:38:29 UTC.
- The run: from 13:39 to 13:57 UTC (165 starts and 19 ablation starts).
- Proof: [proof.md](../../proofs/FAR-SIGN-20261118-001A/FAR-SIGN-20261118-001A-P001_sign/proof.md).
- Code: [signlib.py, run.py, checks.py, readout.py](../../experiments/FAR-SIGN-20261118-001B/FAR-SIGN-20261118-001B-E001_sign/).
- Results: [part_S.json.gz, part_A.json.gz and readout.json](../../artifacts/FAR-SIGN-20261118-001B/FAR-SIGN-20261118-001B-E001_sign/).

## The answer

**On SEEDK's own fills the sign is exactly the copy step: no exception in 149,162 fresh crossing-making fills to n = 48 (computed).
As a theorem it is not: on a base of two orders with seven distinctions, a fill with the sign is refused and a copy step lacks it
(proved). What is proved is how close the sign comes: with it, SEED's copy step is one set comparison, "the moved splits are one whole
order". The copy class's betweenness does not read the sign, because betweenness cannot tell crossed splits from uncrossed ones. One
mark per split, crossed or not, added to what the move's five distinctions see, reads it exactly.**

- **What is proved (ticket A).** Take a fill with knots B(p, r, q), B(a, p, r) and B(c, d, r). Call a split moved when r lands off
  p's side.
  - **Moved splits and new crossings (L1, L2).** A split is moved exactly when it has a, but not q or d, on p's side. Two old splits
    come to cross exactly when one is moved, the other is not, and the unmoved one's p-side lies inside the moved one's.
  - **The sign (L4).** Under it, clause (a) holds (the referee's half), and r sides with d on every crossed split.
  - **The theorem (L5).** Under the sign, a crossing-making fill is a copy step exactly when no uncrossed split is moved and the moved
    splits are the crossers of one crossed split. On a base of two orders, that means exactly one whole order.
  - **A pattern that forces it (L6).** The fill is a copy step when every crossed split separates p from q, none separates a from p,
    and some but not all separate p from d.
  - **Proposition 7.** On a seven-distinction base of two orders, with knots on any pairs, both halves of "sign ⟺ copy step" fail.
    The copy step without the sign also makes a third order.
- **What is computed (ticket B, frozen, 8 of 8 held).**
  - **The sign.** It held on all 1,794 copy steps and on none of 147,368 refused fills. The run went to lines of 26 at n = 48, past
    the referee's 16 at 34.
  - **F1, T1 and T2,** the three pieces the proof leaves open, held on every knot set.
  - **The pair pattern, the weak sign (r sides with d on every crossed split) and the near-pair sign (no crossed split separates the
    near pair)** each matched the copy step exactly.
  - **Two states.** Every one of 1,470,259 knot sets was in one of them, either a copy (α) or crossed splits coming to cross with no
    gainer (β).
- **Where the knot-locality enters (the ablation, no prediction).** These are SEEDK bases at small n, with fills whose knots may sit
  on any pairs.
  - "Sign ⇒ copy step" never failed, in any pattern of which pairs already share a knot. All 223 knot sets with the sign were copy
    steps, and T1 and T2 held on every one of the 4,315 knot sets.
  - "Copy step ⇒ sign" failed whenever the middle pair or the near pair had no knot yet. 539 knot sets of copy steps lacked the sign,
    and F1 failed on 783. It held with no failure when both pairs already shared knots.
  - So SEEDK's bases carry the sign's sufficiency, and knot-locality of the middle and near pairs carries its necessity.
  Proposition 7's base, which SEEDK does not reach, breaks the sufficiency too.

**In the owner's terms.**
- A copy step pulls a split that crossed nothing into the two orders. It happens exactly when the far knot's pair is cut apart by
  every split that crosses something. Put another way, the crossed splits see the new distinction exactly where d is.
- That is a statement about the crossed splits only. The same five distinctions, with the same betweenness among them, make a copy
  step in one base and a refusal in another, and only the crossings tell the two apart.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| R0 | Every copy step has a treated knot set; every crossing-making knot set of the shape pins r to the shared distinction | held | 1,794 of 1,794; 1,470,259 of 1,470,259 |
| R1 | The sign equals the copy step on every crossing-making extension | held | 1,794 copy steps with it, 0 of 147,368 refused fills |
| R2 | F1 on every treated knot set | held | 1,794 of 1,794 with the premise have the sign |
| R3 | T1 and T2 under the sign | held | 1,794 of 1,794; 776 with both orders of three or more splits (the coverage needed 100) |
| R4 | The pair pattern on every copy step's knot sets and on none of a refused fill's | held | 1,794 and 0 of 1,468,465 |
| R5 | The weak sign and the near-pair sign each equal the copy step | held | both exact at the extension level |
| R6 | Every treated knot set in state α or β; no fill with both | held | 1,794 α, 1,468,465 β, none neither, no fill with both |
| R7 | (i) Both verdicts in the copy class; (ii) no marked picture with both | held | (i) 1,794 copy and 54,879 refused knot sets share the class; (ii) 138 marked pictures, none with both |

8 of 8 held. The harness held too:
- this library's SEED verdict equalled knotlib's on all 149,162 extensions;
- L1, L2 and K1 held on all 1,470,259 knot sets.

**Coverage.**
- **Earlier copy steps.** 994 copy steps came after two or more earlier copy steps in their run, and 382 after one.
- **p as an earlier fill's r.** No copy step had a p that was an earlier fill's new distinction. So "copy step ⇒ sign" is untested
  there. The other direction is tested: none of the 623,703 refused knot sets with such a p had the sign.
- **Ablation patterns.** In the ablation, all eight patterns occurred, with 120 to 957 knot sets each.

## What the knot picture explained

- **Why the sign decides (a).** An unmoved split that separates the far pair has d on p's side, and a moved split has it off. So no
  crossed split can come to cross a moved one: r already sits with d on every crossed split.
- **Why one whole order.** Under the sign every gainer gains exactly the moved splits (L3, L4). A model's crossers in two orders are
  the other order. So the copy works exactly when the moved splits are an order.
- **Why the closure picture is blind.** Betweenness counts every split. The sign is betweenness over the crossed splits alone: every
  distinction lies between c and d once uncrossed splits are forgotten.

Known mathematics, labelled: split systems and their crossing (Bandelt and Dress 1992), lattice dimension (Eppstein 2005), and
half-spaces of median graphs. What this adds:
- the reduction of SEED's copy step to "the moved splits are one whole order";
- a pair pattern that forces it;
- counterexamples showing that the referee's sign is a property of SEEDK's knot-local growth;
- an ablation that says which pairs' knots carry each direction.

## What it means for A101 and the goals

- **A101** stays under challenge, with a sharper reading.
  - Growing two orders over a line takes the copy step.
  - The copy step is exactly "r sits with d on every crossed split" (computed on SEEDK's runs), and under the sign it is one set
    comparison (proved).
  - Reading it still takes every crossed split, one bit each, so the obstruction for extent stands.
- **G1:** obstruction learned (extent), with the copy step reduced to one order comparison (proved). No local reading gained.
- **G16:** capability gained.
  - What a copy step is, in the knots' own roles: r sides with d on every crossed split, with p on every uncrossed one, and the moved
    splits are one order.
  - A five-distinction picture that decides it once crossed splits are marked.

## Limitations

- F1, T1 and T2 on SEEDK's fills are computed, not proved. The advisor found no invariant of SEEDK's co-knotted pairs that would prove
  them.
- No copy step had p as an earlier fill's new distinction, so the converse is untested there.
- The ablation ran at small n only (n ≤ 14, the first three bases after the switch).

## Reproduce

```sh
cd experiments/FAR-SIGN-20261118-001B/FAR-SIGN-20261118-001B-E001_sign
../../../.venv/bin/python -B checks.py
../../../.venv/bin/python -B run.py --procs 8 && ../../../.venv/bin/python -B readout.py
```

## Advisor

Consulted once, before the freeze, on the analysis and the design.
- **Analysis.** It re-derived L1 to L3 and gave the G × M form and "r sides with d" (L4). It also showed by hand that the pieces of
  the dichotomy are not formal consequences of the fill, which Proposition 7 then confirmed.
- **Design.** It asked for F1, T1 and T2 scored separately, a coverage condition, and the one-pair-at-a-time ablation. It also asked
  for the marked picture in place of a near-foregone copy-class test.
- **Where it pointed wrong, or could not help.** It suggested counterexamples where p is an earlier copy step's r. None arose, because
  no copy step had such a p. It could not supply the invariant.

It was not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is the sign SEED's copy step? | **Status:** Successful (referee pending), 8 of 8 held | Exact on SEEDK's fills (computed); not a theorem of the fill (Proposition 7); reduced to one order comparison (proved) |
| Local direction: reading the copy step | Obstruction learned | Betweenness cannot see which splits are crossed; with a crossed mark the five distinctions read it, but the marks take every split |
| Broader exploration: why SEEDK's growth makes it exact | Promising, unproved | The ablation: the bases carry sufficiency, the knots on the middle and near pairs carry necessity |
| Long-term goal: G1 | Obstruction learned | The copy step is global in what it reads, simple in what it says |

**Next step:** Full pivot. The coordinator ends the two-order line with this study. What is left is recorded, not started.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove F1 on SEEDK from the middle and near pairs' knots (the ablation says those two pairs carry it) | 2/3 | 2/3 | Characterise where co-knotted middle and near pairs sit after the first fill, by induction over fills → stop at a proof or a counterexample | Parked (line stopped) |
| 2 | Prove T1 and T2 on SEEDK's bases (they held with knots on any pairs there, so they belong to the bases) | 2/3 | 2/3 | Describe SEEDK's bases (two orders plus which uncrossed splits) → stop at a description that implies T1 and T2, or a base that breaks it | Parked (line stopped) |
| 3 | SEED's clauses make a third order off SEEDK's bases (Proposition 7 (B)); is there a base SEEDK reaches where they do? | 1/3 | 2/3 | Search reachable bases for a copy step that raises the lattice dimension → stop at one or a proof that none exists | Parked (line stopped) |

**Corrections:** none.

**Goals:** a G1 checkpoint (obstruction learned for extent; the copy step reduced to one order comparison) and a G16 checkpoint
(capability gained); no goal changed.

**Assumptions:** A101 stays under challenge; A99 gains this study.

**Basket:** read; nothing taken.
