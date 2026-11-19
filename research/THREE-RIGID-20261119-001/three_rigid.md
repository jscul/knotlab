# Do pair and three-way distances force the allowed states of what the law grows?

Epic `THREE-RIGID-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `PROVE-B-20261119-001#1`.
Assumptions A97, A108; goal G1. **Referee pending.**

**Record.**
- **Pre-registration,** frozen before the run (commit `c71e9be18`): [preregistration.md](preregistration.md).
- **Proof:** [proof.md](../../proofs/THREE-RIGID-20261119-001B/THREE-RIGID-20261119-001B-P001_largest_knot/proof.md), ticket B,
  written after the hunt.
- **Code:** [the experiment family](../../experiments/THREE-RIGID-20261119-001A/THREE-RIGID-20261119-001A-E001_rigid/)
  (`rigid_job.py`, `control.py`; after the freeze `reproduce_239.py`).
- **Results:**
  - [rigid.json](../../artifacts/THREE-RIGID-20261119-001A/THREE-RIGID-20261119-001A-E001_rigid/rigid.json);
  - [control.json](../../artifacts/THREE-RIGID-20261119-001A/THREE-RIGID-20261119-001A-E001_rigid/control.json);
  - [reproduce_239.json](../../artifacts/THREE-RIGID-20261119-001A/THREE-RIGID-20261119-001A-E001_rigid/reproduce_239.json).

## The answer

**In the owner's terms.**
- **On every stage tested, yes; at size, no.**
  - **The test.** 211,643 stages that the law reaches, of up to 14 junctions, from three populations: the census, small starts
    whose knots share up to four distinctions, and every meet-once start of seven junctions.
  - **The result there.** Every renaming that keeps all pair and three-way distances also keeps the allowed states (1,243,789
    renamings). This is real evidence, not a replay of a lemma: in 209,559 of those stages the small bonds do not span the
    equations.
  - **At size.** Codex built a stage of 239 junctions where such a renaming changes the allowed states
    (`GROWN-END-READING-20261119-001`, refereed). Codex then built one of 104 junctions where such a renaming, keeping the growing
    end too, fails on an old pair one round later (`LATER-BOND-READING-20261119-001`, **referee pending**). Codex also reports a
    construction showing that no fixed number of distinctions read together suffices on every stage.
- **What does suffice, proved.** Read the bond distance of every set of as many distinctions as the largest knot holds. A renaming
  that keeps all of those keeps the allowed states, and with the growing end it carries every later round (Theorem M). The proof
  is short: a set is a bond exactly when it reads one less than its size, each knot's distinctions split into bonds no larger than
  the knot, and those bonds span the equations.
  - **Why fixed numbers fail.** Codex's constructions that need more and more distinctions have knots holding more and more: each
    index junction of the 239-junction stage holds 20.
- **For the premise.** Distance carries what grows when it is read over sets as large as the largest knot. Read over pairs, or
  over triples, it does not, though up to 14 junctions triples were enough everywhere tested.

| Population (stages of round ≥ 1, ≤ 14 junctions) | Stages | Small bonds span (settled by the lemma) | Symmetries breaking three-way readings | Three-way-keeping symmetries | … that change the equations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Census starts (≤ 5 knots), rounds 1–8 | 25,722 | 1,589 | 1,096,252 | 580,039 | **0** |
| Starts of 3–4 knots sharing up to 4 (3), rounds 1–3 | 47,470 | 135 | 1,574,021 | 224,835 | **0** |
| Meet-once 7-junction starts, round 1 | 138,451 | 360 | 423,714 | 438,915 | **0** |
| Total | 211,643 | 2,084 | 3,093,987 | 1,243,789 | **0** (37 stages capped, 4 late) |

| # | Prediction | Verdict |
| --- | --- | --- |
| Q0 | The three known failures break three-way readings | **held** (control) |
| Q1 | No R3 counterexample in the three populations (≤ 14 junctions) | **held** (0 of 1,243,789) |
| Q2 | No Claim B3 failure there | **held** (none can occur without an R3 counterexample) |
| R3 at every size (the epic's conjecture) | — | **refuted** by Codex's 239-junction stage (refereed): a Block to R3 at all sizes, graded by the referee; Q1 and Q2 untouched |

## How it was done

- **The hunt (`rigid_job.py`, shared runner, 663 cases).** For every stage:
  - its full table by bonds;
  - every table symmetry, one per holder-class coset, holder-breaking ones included. VF2 was restricted by each distinction's
    multiset of three-way readings, which is sound;
  - each symmetry tested for keeping every three-way reading and for carrying the equations;
  - the advisor's discriminator: whether the bonds of at most three distinctions span the equations.
- **The 239-junction stage (`reproduce_239.py`, after the freeze).** It was rebuilt from Codex's description:
  - a lawful round takes 235 junctions and 635 distinctions to 239 and 643;
  - the swap of indices 2 and 3 fixes the growing end and does not carry the equations;
  - 105 edge-disjoint paths join the two hubs.
  The pair and three-way readings at that size were not recomputed. They rest on Codex's hub argument, which the referee confirmed
  piece by piece.
- **Theorem M (ticket B),** proved after the hunt.

## Known results, and what this adds

Known:
- the advisor's lemma (small bonds spanning);
- Codex's GROWN-END-READING (refereed) and LATER-BOND-READING (pending);
- its referee's census (all 100,233 triple-keeping maps carry the equations to 11 junctions);
- EXTEND-ROUND's Claim B\*;
- THREE-WAY and TRIPLE-GROWN;
- that vertex cocycles are disjoint unions of bonds and span the cut space, which is classical.
- Codex's `BOND-READING-SCALE-20261119-001` (committed nine minutes after Theorem M, found independently; **referee pending**). It
  proves the same mechanism in a sharper form: testing which sets of shared distinctions are bonds, with the growing end, recovers
  the equations; reading through J, the number of junctions, always suffices; and the worst-case order is Θ(J) (between √n and
  linear in distinctions). Theorem M's bound, the largest knot, is the stage-specific form that its note mentions; the two bounds
  are incomparable on a given stage.

What this adds:
- three-way rigidity on 211,643 reached stages of up to 14 junctions, most of them not settled by the lemma, with no exception;
- Theorem M, the bound that does suffice for every stage: the largest knot;
- an explanation of Codex's unbounded construction through that bound.

## Limitations

- Stages of at most 14 junctions; holder-class cosets with a cap of 20,000 (37 stages capped, 4 late).
- Theorem M's bound may not be tight: fewer distinctions suffice wherever smaller bonds span.
- LATER-BOND-READING is referee pending; the all-size failure of pair plus three-way plus the growing end rests on it.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **What it supplied.** The lemma and the rank-deficit discriminator. The discriminator made the hunt real evidence: 99% of
  stages have a deficit.
- **Its expectations.** It expected R3 to fail at size in graphs whose bonds are all large, and Codex's 239-junction stage is of
  that kind.
- **Its bets.** It put 85% on R3 holding on the hunt, and it held. It put 60% on R3 for all reached stages, and R3 fails there.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three-way rigidity on reached stages | **Status:** Successful (bounded) | Holds on 211,643 stages to 14 junctions; refuted at size (Codex); the bound that suffices proved (Theorem M) |
| Local direction: what reading of a base is complete | Continue | Bond distance over sets as large as the largest knot is complete; pairs and triples are not |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | Classical cocycle facts give the bound; Codex's BOND-READING-SCALE (referee pending) gives the worst-case law |
| Long-term goal: G1 with A97 | Capability gained | A proved form of the premise: distance over sets as large as the largest knot plus the growing end carries what grows |

**Next step:** Research directions. The coordinator's (a) and (b) are both covered by Codex's BOND-READING-SCALE (referee
pending), so neither is ours to start. Paused here at the owner's request (19 November, tokens); resume from #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What typical growth needs: does the largest exhausted knot stay bounded along cheapest-count growth from each start? If so, Theorem M gives one fixed order per start for every round, against Codex's Θ(J) worst case | 3/3: the worst case needs large knots; if typical growth never makes them, a fixed reading suffices for what the law typically grows | 3/3: an unrecorded probe (1 in 200 census starts, rounds 1 to 10) found the largest exhausted knot fixed after round 3 and at most 8, while stages grew to 165 junctions | freeze the probe on the full census and the small starts, and try to prove that new junctions stay no larger than a bound set by the start → stop at that theorem or a start whose knots grow without end (MERGE-BURST's runaway starts are the first place to look) | Proposed |
| 2 | The least order r actually needed on sampled grown stages, under a named weighting, against the largest knot and J | 2/3 | 2/3: exact readings above 14 junctions are costly | after #1 | Proposed |
| 3 | The quantitative law and the limiting statement (the coordinator's (a) and (b)) | — | — | taken by Codex's BOND-READING-SCALE | Taken elsewhere |

**Corrections:** one, for R3 at all sizes: a Block to the epic's conjecture, from Codex's refereed 239-junction stage, logged in
`docs/CORRECTIONS.md`. Q1 and Q2 stand. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this
study, status unchanged.

## Final report as sent (2026-11-19, about 21:20 UTC)

THREE-RIGID closes as frozen. On all 211,643 stages tested, of up to 14 junctions, pair and three-way distances force the allowed
states: none of 1,243,789 renamings that keep them changes the equations, and in 209,559 of those stages small bonds do not
settle it. At size this fails: Codex's refereed 239-junction stage is a Block to R3 at all sizes, logged in CORRECTIONS. Proved
(Theorem M): reading bond distance over sets as large as the largest knot forces the states and, with the growing end, carries
every round. Codex's BOND-READING-SCALE, referee pending, proves the same mechanism with a sharper bound and the worst-case law
Θ(J). Proposed next: whether typical growth keeps its largest knot bounded. A quick probe says it does, at most 8 through
round 10, which would give one fixed order of reading per start. Paused at the owner's request. Corrections: one Block (R3 at
all sizes). Goals: G1 checkpoint. Assumptions: A97 and A108 gain the study, status unchanged. Advisor: before the freeze. Referee
pending.
