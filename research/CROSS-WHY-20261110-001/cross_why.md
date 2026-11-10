# Why crossing breaks balance

Epic `CROSS-WHY-20261110-001` (program foundations), 2026-11-10. A frozen exploratory census (ticket A, pre-registered in
`6dd5ac7bd` with its exploration disclosed) and a proof (ticket B).

## The question

- **Where it comes from.** Backlog B64. `CROSS-BORDER-20261110-001` found that every uniform doubling schedule read at g = 2 to 5 in which
  original rings hear each other loses balance within two doublings of the crossing, and read it as an exclusion: while a network grows
  it keeps its knots or reads distance across its grown plane, never both. The coordinator gave B64 the go-ahead on 2026-11-10, asking
  for a lemma, or failing one, a plain statement of that.
- **The question.** Why does crossing a territory border break balance? Or does some schedule cross a border and keep every stage
  balanced?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Crossing is not the mechanism (W2 refuted).** At the second doubling, after one run of 1 to 24 lags, 2 of 11 failures at g = 2, 4 of 17 at g = 3 and 7 of 13 at g = 4 come with no crossing, and 10, 4 and 9 stages are balanced right after one. Failures are of two kinds: **internal** (a ring's parts on its own cells alone already fail: 5, 6 and 4 of them) and **heard** (those parts bind, and parts held by other rings cancel them: the rest). | exploratory, exact | A |
| 2 | **Uneven schedules cross with every stage balanced (W1 refuted).** At g = 3, 21 schedules of three runs, a pause and then short runs, cross a border and keep every stage balanced to 48 × 48; in 11 of them every original ring hears all eight others, as in [28, 1, 1] from lag 8. At g = 2 and 5, 97 and 55 schedules of two runs cross with every stage balanced to 24 × 24. Two of them, [1, 28, 1] and [1, 28, 12], are confirmed on the full state. | exploratory, exact | A |
| 3 | **Uniform long pauses still fail.** Repeating a pause fails where a pause followed by short runs does not: P = 28 at g = 3 is balanced at 12 × 12 and 24 × 24, both after crossing, and fails at 48 × 48. | exploratory, exact | A |
| 4 | **Balance is read on one territory, and newborn rings never fail.** The law commutes with the original lattice's translations, so a stage's balance is decided on one fundamental domain; every ring born at a doubling is bound at every later lag of its stage (the transfer lemma), so every failure is at a ring that lived through a run. | proved; checked against the full state | B |
| 5 | **One size past.** Four of the 21, each with one more run of 1 or 2 lags, read at 96 × 96: stress test pending (CROSS-WHY-A1). | exploratory, exact | A |

## Answer

No lemma, because the premise is false. Crossing a territory border does not break balance: what failed in the uniform schedules read
was the repetition of a long pause, through a ring's own cells losing hold of its born cells or through what its neighbours heard
cancelling what it holds, and both happen with no crossing at all. A schedule that pauses once, long enough for neighbouring territories
to hear each other, and then doubles quickly, keeps every stage balanced while its original rings hear their neighbours. So the exclusion
read by the last epics holds for the uniform schedules read and not as a law of growth: a growing plane can keep its knots and carry
what its territories heard of each other.

## Reading

**Interpretation, not a theorem.**
- **Pauses read, quick growth keeps.** In the schedules found, distance between territories is read during a pause, and the doublings
  that follow keep every knot; repeating the pause is what fails.
- **The schedule is declared.** Each schedule is a declared, time-dependent growth law. They were found by search: no native rule of the
  network has been shown to choose them, so "the network decides when to pause" is open.
- **For G1.** This reopens, on evidence this time, the route to a grown plane that keeps its knots and reads its own distance while it
  grows. What these schedules read is coarse: on the 3 × 3 tube, who hears whom among nine territories.

## Lag cutoffs and census-only claims

- **Exact per reading.** **Census-only.** Conclusions 1, 2, 3 and 5: one tube, the ranges frozen in the contract; balance computed,
  not proved.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Crossing with every stage balanced (2) | The first four schedules of conclusion 2 with one more run of 1 or 2 lags, at 96 × 96 | **stress test pending** (CROSS-WHY-A1 in `docs/LONG_RUNNING.md`) |
| The reduced reading (4) | eleven schedules against the full state, and two at 48 × 48 against `readings()` | pass (ticket B, check 1; ticket A, part V) |

## Literature and provenance

- **Classification.** New as far as found, a frozen exploratory census, with a known-with-delta proof (B: symmetry reduction and the
  transfer lemma).

## Workspace assumptions

- **Relied on.** A30, A32, A42 (stage reading), A44 (open births), A45. **Added.** None.

## Correction

**2026-11-10 · Not a block** (`docs/CORRECTIONS.md`). `CROSS-BORDER-20261110-001` read its census as "crossing breaks balance" and
as an exclusion: while a network grows it keeps its knots or reads distance across its grown plane, never both; `GROW-STOP-20261110-001`
read "making and reading are two phases", and `INVERT-STEP-20261110-001` listed B55 and B64 as the proof pair for that exclusion. The
computed results stand for the uniform schedules read; the exclusion and the causal reading do not. Correction sections were added to
both decision notes.

## Ratio

- **Substantive.** One frozen census (A) in four parts, one proof (B) with three checks. **Administrative.** The pre-registration, this
  note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — why crossing breaks balance | **Status:** Successful | No lemma, because the premise is false: crossing is not the mechanism, and uneven schedules cross with every stage balanced |
| Local direction — a grown plane that keeps its knots and reads distance | Continue | Reopened on evidence: a pause reads who hears whom, and quick doublings after it keep every knot |
| Broader exploration — G1 with G5 | Known alternatives | Why a run length keeps balance (the period of four at g = 2); B55; a pause the network chooses |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law, with a declared schedule, grows a plane whose territories hear each other while every stage keeps its knots, to 48 × 48 |

**Corrections:** one, Not a block: the exclusion between keeping knots and reading distance while growing held for the uniform
schedules read, not as a law of growth (`CROSS-BORDER-20261110-001`, `GROW-STOP-20261110-001`, `INVERT-STEP-20261110-001`). **Goals:** a
G1 and G5 checkpoint (capability gained); B64 taken; sub-goal B89 (reading distance while growing) recorded. **Assumptions:** none.

**Next step:** Research directions — selected: #1, awaiting the coordinator's go-ahead; B55 (#3) next in the meantime, as asked.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Reading distance while growing (B89) | 3/3 — Major | 2/3 — Testable | On the 5 × 5 tube, search schedules of pauses and quick doublings with the territory reader for one under which original rings are heard at distance 1 and then 2 while every stage stays balanced → a grown plane that keeps its knots and reads its distance as it grows, or the distance at which every schedule read fails | Selected · awaiting go-ahead |
| 2 | Why a run keeps balance | 2/3 — Substantial | 2/3 — Testable | At g = 2 one run keeps balance at the second doubling exactly for P = 1 and P ≡ 2, 3 (mod 4) to P = 24: prove the period from the stage's return map → a lemma for which runs keep balance | Alternative · deferred |
| 3 | Why g = 3 keeps balance (B55) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · started next, as the coordinator asked |
| 4 | A pause the network chooses | 2/3 — Substantial | 1/3 — Exploratory | A native rule that decides when to double from the network's own state, under which territories hear each other and every stage keeps its knots → such a rule, or none among a declared family | Alternative · deferred |

1. **Reading distance while growing.** Payoff 3: G1's question 9 asks for a space that a uniform local law makes and that reads its own
   distance; this would have both at once, while the plane grows. Concreteness 2: the territory reader handles any n, and the 3 × 3
   search took 77 minutes; the uncertainty is whether a second pause, needed to reach distance 2, can keep balance.
2. **Why a run keeps balance.** Payoff 2: a lemma about which runs are safe would replace search by a rule. Concreteness 2: the period
   of four at g = 2 is exact to P = 24, and the stage's return map is computable.
3. **B55.** Payoff 2, Concreteness 2: as recorded; the coordinator asked for it next.
4. **A pause the network chooses.** Payoff 2: removes the declared schedule. Concreteness 1: no candidate rule yet.

**Recommendation.** Research directions: #1 is the step toward G1, and a 3/3 recorded as a sub-goal; B55 next meanwhile, as the
coordinator asked.

## Final report as sent

Sent to the owner on 2026-11-10 at 02:42 UTC and copied here verbatim.

**Why crossing breaks balance (B64) is closed and published. There's no lemma, because the premise is false: crossing a territory border doesn't break balance.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/CROSS-WHY-20261110-001/cross_why.md))

- **Crossing isn't the mechanism** (frozen census, exact): a stage fails in one of two ways. Either a ring's own cells stop holding its born cells independently, or what its neighbours heard of it cancels what it holds. Both happen with no crossing at all, at g = 2, 3 and 4.
- **Uneven schedules cross and keep every knot:** pause once, long enough for neighbouring territories to hear each other, then double quickly. At g = 3, 21 such schedules keep every stage balanced to 48 × 48. In [28, 1, 1], every original ring hears all eight others from lag 8. Two of them were confirmed on the full state. Repeating the pause (every 28 lags) still fails.
- **Proved:** balance can be read exactly on one territory, and rings born at a doubling never fail.
- **Pending:** a 96 × 96 stress run (about two hours, in the background).

| Scope | Verdict | Why |
|---|---|---|
| This attempt: why crossing breaks balance | Successful | No lemma: the premise is false |
| Local direction: a grown plane that keeps its knots and reads distance | Continue | Reopened on evidence: a pause reads who hears whom, quick doublings keep the knots |
| Broader exploration: G1 with G5 | Known alternatives | Which runs keep balance; B55; a pause the network chooses |
| Long-term goal: G1 Space from a law | Capability gained | A local law with a declared schedule grows a plane whose territories hear each other while every stage keeps its knots |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Reading distance while growing (B89) | 3/3 | 2/3 | 5 × 5 tube: a schedule where original rings are heard at distance 1 then 2 with every stage balanced, or where every schedule fails |
| 2 | Why a run keeps balance | 2/3 | 2/3 | At g = 2 one run is safe exactly when P = 1 or P ≡ 2, 3 (mod 4): prove the period |
| 3 | Why g = 3 keeps balance (B55) | 2/3 | 2/3 | As recorded |
| 4 | A pause the network chooses | 2/3 | 1/3 | A native rule for when to double |

**Corrections:** one, Not a block. "Knots or distance while growing, never both" (CROSS-BORDER), "making and reading are two phases" (GROW-STOP) and the "proof pair for the exclusion" (INVERT-STEP) all held only for the uniform schedules we read. It's logged in CORRECTIONS.md with a new lesson (vary a schedule's shape, not just its period), and in knotlab's HISTORY.md. **Goals:** G1/G5 checkpoint (capability gained); B64 taken; sub-goal B89 recorded. **Assumptions:** none.

I recommend #1: it's the direct step toward a grown space that reads its own distance while it grows. As the coordinator asked, I'm starting B55 meanwhile.
