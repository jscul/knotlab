# Can the distances version of the one-round extension be proved?

Epic `PROVE-B-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `HUNT-SHORTEN-20261119-001#1`.
Assumptions A97, A108; goal G1. **Referee pending. Stress test pending:** part M's last 9 of 27 cases are still running
(`docs/LONG_RUNNING.md`, PROVE-B-M1).

**Record.** Pre-registration, frozen before the hunt (commit `5042a81dc`), and Amendment 1 (commit `8fba03a6e`, after Codex's
counterexample and before part M): [preregistration.md](preregistration.md). Proof:
[proof.md](../../proofs/PROVE-B-20261119-001A/PROVE-B-20261119-001A-P001_split/proof.md). Code:
[the experiment family](../../experiments/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt/) (`reached_job.py`,
`control.py`, `meetonce_job.py`; after the read-out `threeway_check.py`, `codex_reproduce.py`). Results:
[reached.json](../../artifacts/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt/reached.json),
[control.json](../../artifacts/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt/control.json),
[threeway_check.json](../../artifacts/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt/threeway_check.json),
[codex_reproduce.json](../../artifacts/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt/codex_reproduce.json).

## The answer

**In the owner's terms.**
- **Claim B is false, even on what the law grows, and even where junctions meet once.** Pair distances plus the growing end do
  not carry one round.
  - **For arrangements in general.** The proof stalled at a precise point, and the advisor built a seven-junction arrangement
    there that breaks the claim (Proposition X, checked).
  - **On grown stages.** Codex then built two: one whose start junctions meet twice (`GROWN-END-SWAP-20261119-001`, refereed)
    and one whose start junctions all meet once (`GROWN-END-MEET-ONCE-20261119-001`, referee pending).
  - **Reproduced.** Both reproduce exactly in this program's engine. Each keeps the round's reading exactly, and each fails at
    the next round.
- **What breaks it.** All three cases use one mechanism, which is what the proof's formula sees:
  - Some old junction's distinctions are split between two sides of a tie, so swapping two of them keeps every distance.
  - The next round's join with one fresh distinction then shortens a bond on one side only. The table recorded the tie, but not
    which growing junctions each tied bond holds.
  - "Three distinctions already shared at the start" are what make the swap free, and "a dead holder" bounds the bond that holds
    no growing junction.
- **What is proved.**
  - The exact formula for the next table, in which old bonds and new junctions combine with a discount (Lemma C).
  - Offshoots never change any old distance, and rounds of offshoots only carry every matching (Lemma O).
  - Matchings that keep the equations, not only the distances, carry every round (EXTEND-ROUND's Claim B\*).
- **Where the clean premise may still live: three-way distances.** All three failing swaps break three-way readings: 48, 34 and
  74 triples change. In a sample of 164,052 table symmetries that keep the round's reading but not the equations, from part B's
  starts, **none keeps the three-way readings** (exploratory). So on everything seen, a matching that keeps pair distances,
  three-way distances and the growing end also keeps the equations, and then it carries every round (Claim B\*). That is the next
  question.

| Test | Cases | Verdict |
| --- | ---: | --- |
| P0: Proposition X through the test | 32 symmetries | all fail (held) |
| P1: starts of 3 or 4 knots sharing up to 4 (3) distinctions, up to three rounds | 35,735 starts; 42,771 open stages; 1,249,716 reading-keeping symmetries | **no failure** (held; 6 stages late, 38 capped) |
| P2, P3 (Amendment 1): meet-once starts of at most 6 junctions, the start and its round-1 stage | 44,426 starts so far (18 of 27 cases); 23,577 reading-keeping symmetries | no failure so far (**pending**) |
| Codex's two reached counterexamples (meeting twice; meeting once) | 8 and 48 symmetries | all fail, reproduced |
| Exploratory: reading-keeping, equation-breaking symmetries that keep three-way readings | 164,052 sampled | **0** |

## What the split formula and the tie lemma see in the counterexamples

| Ingredient | In Lemma C | In Codex's meet-twice case | In Codex's meet-once case |
| --- | --- | --- | --- |
| A swap that keeps every distance | moving one junction across a tie keeps all bond sizes | dead A = {0, 1, 2, 3}, split 2 / 2 between two holders | four junctions with five shared distinctions give two separate connections, making the two meetings 0 and 1 interchangeable |
| A tie | a bond holding no live junction against a bond holding a full parent set | A's own distinctions against a bond on one holder's side | the same, on A's side |
| A discount | a join with k parents and f < k fresh inside | a pair with one fresh distinction | a three-parent join with one fresh distinction (23) |
| What the table misses | which live junctions each bond holds | {0, 1, 21} becomes a bond of three; every bond through 2 and 1 keeps four | {0, 2, 23} becomes a bond of three; every bond through 1 and 2 keeps four |

## Known results, and what this adds

Known:
- EXTEND-ROUND's Lemma A and Claim B\*;
- HUNT-SHORTEN's hand-made joins and self-pairs;
- Codex's two reached counterexamples, which Codex found and the referee confirmed for the meet-twice one;
- Codex's census: no meet-once failure at 11 or fewer current junctions, or 22 or fewer distinctions, and a safe single start;
- Whitney's theorems.

What this adds:
- the split formula and the offshoot lemma, proved;
- Proposition X, a counterexample to Claim B for arrangements in general;
- both of Codex's counterexamples reproduced in this program's engine and read through the formula;
- no failure from 35,735 starts of 3 or 4 knots;
- the observation that every failing swap, and every one of 164,052 sampled reading-keeping symmetries that break the equations,
  breaks three-way readings.

## Limitations

- The meet-once hunt is part-finished. Its stages are rounds 0 and 1 from starts of at most 6 junctions, and Codex's six-junction
  failures appear only at round 2.
- The three-way observation is a sample after the read-out: every 25th start of part B. It is a lead, not a result.
- Claim B with three-way readings added is not proved.

## Advisor

Fable 5.2 ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), consulted on the proof.
- **What it confirmed.** The split formula and the offshoot lemma.
- **What it built.** Proposition X, by hand. Its mechanism is the one Codex realised on grown stages.
- **What it named.** The tie lemma, and the hunt target.
- **Its bets.** It put 60% on Claim B holding for all reached stages, and it does not hold. It put 10% on Claim B for all
  arrangements, and Proposition X refutes that.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: prove Claim B, or hunt where the proof stalls | **Status:** Successful (refuted) | Claim B false in general (Proposition X) and on reached stages (Codex, both cases, reproduced); the split formula and offshoots proved |
| Local direction: what reading of a base is complete | Pivot within the direction | Pair distances plus the growing end are not enough; pair plus three-way distances plus the growing end may be |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | The same mechanism in three constructions: a dead holder split by a tie, broken by a join's discount |
| Long-term goal: G1 with A97 | Obstruction learned | The table misses which growing junctions a tied bond holds; three-way readings see it in every case known |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do pair plus three-way readings plus the growing end carry one round? Test three-way rigidity: does every table symmetry keeping pair and three-way readings carry the equations? | 3/3: the premise's corrected form, and a route to a proof through Claim B\* | 3/3: the populations, the readings and the tests exist | all reading-keeping symmetries of part B, part M and the census, with three-way readings → stop at one that keeps them and breaks the equations, or none; then try to prove rigidity | Proposed (the coordinator's suggestion) |
| 2 | Codex's flip reading (can the marked pair flip together with everything else fixed?) as the extra bit | 2/3 | 2/3 | compare with three-way readings on the same symmetries | Alternative · deferred |
| 3 | Part M's round-2 stages, where Codex's six-junction failures appear | 2/3 | 2/3 | extend part M by a round | Alternative · deferred |

**Corrections:** none from this study. Codex's GROWN-END-SWAP Narrowings were folded (commit 032d8e54d). **Goals:** G1
checkpoint (obstruction learned). **Assumptions:** A97 and A108 gain this study, status unchanged.

## Final report as sent (2026-11-19 18:50 UTC)

**Outcome:** Claim B is false. Pair distances plus the growing end do not carry one round, even on what the law grows, and even where junctions meet once. What is proved is the exact formula behind it, and the next question is three-way distances. Closed, referee pending; one hunt still finishing.

- **Three counterexamples, one mechanism.**
  - My proof stalled at a precise point, and the advisor built a 7-junction arrangement there that breaks the claim.
  - Codex then built two grown ones: one from starts that meet twice (refereed), and one from a 7-junction start that meets once (referee pending).
  - I reproduced both exactly in our engine. Each keeps every distance and the round's reading, and fails one round later.
  - In each, an old junction's distinctions split across a tie, so swapping two of them keeps all distances. The next round's join then shortens a bond on one side only. The table never recorded which growing junctions each tied bond holds.
- **Proved.** The exact formula for the next table, and that offshoots never change any old distance.
- **Hunts.** From 35,735 starts of 3 or 4 knots sharing up to four distinctions there is no failure: 1,249,716 symmetries extend. The meet-once hunt on starts of up to 6 junctions is 18 of 27 cases in, also with no failure. Both agree with Codex's minimum of a 7-junction start.
- **Where the clean premise may live.** All three failing swaps break three-way readings. So do all 164,052 sampled symmetries that keep the reading but not the equations. On everything seen, keeping three-way distances too forces the equations, and then a matching carries every round (already proved).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: prove Claim B or hunt its stall | **Status:** Successful (refuted) | False in general and on grown stages; the formula and offshoots proved |
| Local direction: what reading of a base is complete | Pivot within the direction | Add three-way distances |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | One mechanism in all three counterexamples |
| Long-term goal: G1 with A97 | Obstruction learned | The table misses which growing junctions a tied bond holds |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Pair plus three-way distances plus the growing end: test three-way rigidity, then try to prove it | 3/3 | 3/3 | every reading-keeping symmetry of our populations, with three-way readings → one that keeps them but not the equations, or none | Proposed |
| 2 | Codex's flip reading as the extra bit | 2/3 | 2/3 | compare on the same symmetries | Alternative · deferred |
| 3 | Round-2 stages of meet-once 6-junction starts | 2/3 | 2/3 | extend part M | Alternative · deferred |

**Corrections:** one since my last report. Codex's GROWN-END-SWAP narrows EXTEND-ROUND and HUNT-SHORTEN to meet-once pairs and census stages, graded Narrowing (commit 032d8e54d). **Goals:** G1 checkpoint (obstruction learned). **Assumptions:** A97 and A108 gain this study, status unchanged. **Advisor:** Fable 5.2, on the proof. It confirmed the formula, built Proposition X, and named the mechanism Codex realised. It bet 60% on Claim B for grown stages, and that failed. **Stress test pending:** part M's last 9 cases.

Referee hand-off: the decision note is `research/PROVE-B-20261119-001/prove_b.md`. Check most closely Lemmas C and O in the proof, the coset search in `reached_job.py`, and `codex_reproduce.py`.
