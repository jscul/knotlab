# A principle for the free sign: do the birth choices with the most failing pairs force it?

Epic `MOST-FAILING-20261127-001`, at the owner's go-ahead on direction 1 of the commutation-at-birth study. Design,
frozen predictions, review and results: [README.md](README.md); code [most_failing.py](most_failing.py); outputs
[summary.json](summary.json), [gates.json](gates.json), [results.jsonl](results.jsonl),
[census_types.jsonl](census_types.jsonl). Exact integer programs solved to proven optimality, checked by exhaustive
enumeration at 386 closures; one vote per census start unless marked; independent referee pending (brief in
`referee-R1/`).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the most failing pairs as a principle for the free sign | **Status:** Successful | It forces the sign at 948 of 1,177 closures, even at 588 and odd at 360 |
| Local direction — selecting the sign by a principle over birth choices | Retire | The forced sign follows the principle's counting and the weighting; no tested principle selects odd |
| Broader exploration — the quantum part under the declared phase | Known alternatives | Readers on grown closures; a principle drawn from growth itself; or the sign kept as declared |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | With the declared phase, growth makes the quantum close possible, and no tested principle makes it the selected one |

The maximum does what a principle can: at 81% of the closures every birth choice with the most failing pairs closes with
the same sign. But the sign it forces is even more often than odd (588 against 360), and it is not a fact about the
structure alone. Counting failing pairs once per holder type, which removes the weight of doubled meetings, reverses the
lean (619 odd against 241 even). On the census types, where the two counts coincide, it splits (49 odd, 60 even, 64
free). The control, the least departure from classical, forces even almost everywhere (1,152 of 1,177). So the selected
sign belongs to the principle: which principle, and how it counts, decides it.

**Next step:** Full pivot — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Readers on grown closures: do the odd birth choices split into readers, each holding two values that fail to commute, with values of different readers commuting? | 2/3 — Substantial | 2/3 — Testable | At each of the 1,177 closures, search the odd choices for a reader split → a three-reader game on growth's own closures, or none | Selected · awaiting go-ahead |
| 2 | A principle drawn from growth itself, not imposed (for example, the sign the next round's births would need to keep a state) | 3/3 — Barrier | 1/3 — Stated | Name one such quantity at the closures → a candidate that forces odd, or none | Alternative · deferred |
| 3 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Read G1's open question and its last record → a bounded next test, or a reason to keep it idle | Alternative · deferred |
| 4 | Intuition link: the maximum as decoding rule R onto the birth choices | 1/3 — Incremental | 3/3 — Ready | State the verdicts as the nearest-code-word decoding of rule R (ties as decoding ties) → match on every closure, or the first mismatch | Alternative · deferred |

1. Payoff 2/3: it would put the declared phase's contradiction into the program's reader picture on structures growth
   makes, which is the closest form of "representing quantum mechanics" this line can reach; a closure whose odd choices
   never split into readers is contextuality without separated readers. Concreteness 2/3: a finite search per closure
   (choices whose failing pairs form a matching across reader pairs, with the checks commuting). The main uncertainty is
   whether split choices exist beyond the four-knot closure. It continues the declared extension, so it waits for the
   owner's word.
2. Payoff 3/3: a principle the model supplies would be a native source of the sign. Concreteness 1/3: no candidate is in
   hand, and three studies have now found every sign supplied.
3. Payoff 3/3: the program's central goal, idle for six days. Concreteness 1/3 until its open question is reread.
4. The intuition link for this stop. The birth choices with the most failing pairs are the code words nearest to rule R's
   all-pairs word, so the principle decodes rule R onto the code, and free verdicts are decoding ties; counting holder
   types changes the metric, and with it the decoded word and its sign. Payoff 1/3 (a restatement); concreteness 3/3.

**STOP** on selecting the sign by a principle over birth choices. Settled: the maximum forces the sign at most closures,
but in both directions, and the direction changes with how the principle counts and how closures are weighted; the
control forces even. Open: a principle the model itself supplies (row 2). A principle that forces odd under every
counting and weighting would reopen the line.

**Corrections:** none.

**Goals:** checkpoint row added under G18 (obstruction learned); no goal changed.

**Assumptions:** A315 (the most failing pairs) gets a history line: tested under the control, holder types, round by round
and the per-type weighting, the forced sign changes with the principle, so the result is about the scaffold.

**Scaffolds:** A315 and its tie-break. The verdicts hold under none of the alternative principles: the result is a fact
about the principles, not the model. The census starts and the four-round cap carry over from A314's study.

**Basket:** `BOTH-LONG-20261126-001#1` (3/3, 3/3), `VALUE-CHANGE-20261126-001#1` (3/3, 3/3) and B239 (3/3, 2/3). None
was taken: the first belongs to the layer line, the second was answered by the third-reader study, and the third is an
older selected study. This study took `LOCAL-COMMUTE-20261127-001#1`.

**Advisor:** unavailable (logged). An independent reviewer checked the design by hand, read-only, before the freeze. It
settled the first draft's P3 at start 24, showed P2's rationale empty, and gave the hand cases of P1 and two variants;
six changes followed, listed in the README.

## What was found

- **The principle forces the sign at most closures.** At 948 of the 1,177 closures where birth choices attain odd, every
  birth choice with the most failing pairs closes with the same sign; at 229 the maxima split.
- **In both directions.** It forces even at 588 and odd at 360. Where the natural rule keeps a state (82 closures), the
  maximum is that rule's choice and its sign (53 odd, 29 even); elsewhere even leads, 559 to 307.
- **The direction follows the counting.** Counting failing pairs once per holder type gives odd at 619, even at 241 and
  free at 317; where both force a sign, the two counts disagree at 199 of 719 closures. One vote per census type (173
  types, no doubled meetings) gives 49 odd, 60 even and 64 free under either count.
- **The least departure from classical is even.** The nonzero choices with the fewest failing pairs force even at 1,152
  closures; at all 1,135 where they have two failing pairs there is a doubled meeting, whose two pairs have identical
  checks and cost.
- **Round by round agrees.** At the 86 later closures, taking the most failing pairs at each round closes 19 odd and 67
  even, agreeing with the maximum at 62 of the 66 where the maximum forces a sign.
- **The reviewer's hand cases all hold**, including the wheel of five: 15 failing pairs at the maximum, 13 maximum words,
  both signs among them.

## Intuitions (exact links, not evidence)

- **Decoding.** The birth choices with the most failing pairs are the code words nearest to rule R's all-pairs word
  (the literature's nearest-code-word decoding). Where rule R keeps a state it decodes to itself; elsewhere the principle
  reads the sign of the decoded word, a free verdict is a decoding tie, and a different count (holder types) is a
  different metric with its own decoded words.

## Final report as sent

2026-11-27 17:19 PST

The principle "take the birth choices with as many failing pairs as a state allows" mostly fixes the sign, but it doesn't pick the quantum one. Which sign it picks depends on how it counts.

**What we found** (1,177 closures where an odd close is possible, one vote per census start)
- **The maximum forces the sign at 948 closures, 81%,** but it forces even more often than odd: 588 even, 360 odd, and 229 free.
- **The lean reverses when the counting changes.** Count failing pairs once per holder type, so a doubled meeting doesn't count twice, and you get 619 odd, 241 even, 317 free. The two counts disagree at 199 of the 719 closures where both force a sign.
- **The weighting matters too.** One vote per census type (173 types, where the two counts coincide) gives 49 odd, 60 even, 64 free.
- **The opposite principle forces even almost everywhere.** Taking the fewest failing pairs, the least departure from classical, forces even at 1,152 closures.
- **Choosing round by round agrees.** At the 86 later closures it gives 19 odd and 67 even, matching the maximum at 62 of the 66 where the maximum forces a sign.

So the sign belongs to the principle, not to the structure. Over three studies the quantum part now stands like this. With one declared primitive (which values commute, fixed at birth), growth's own closures can carry the three-reader contradiction at 1,177 of the 1,187 places where any choice could. Which closures do carry it is supplied: by the choice itself, or by a principle whose answer changes with how it counts.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the most failing pairs as a principle for the free sign | **Status:** Successful | Forces the sign at 948 of 1,177 closures: even 588, odd 360; referee pending |
| Local direction — selecting the sign by a principle over birth choices | Retire | The forced sign follows the counting and the weighting; no tested principle selects odd |
| Broader exploration — the quantum part under the declared phase | Known alternatives | Readers on grown closures; a principle drawn from growth itself; or the sign kept as declared |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | The quantum close is possible on growth's closures; no tested principle makes it the selected one |

**Next step:** Full pivot — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Readers on grown closures: do the odd choices split into readers, each holding two values that fail to commute, with different readers commuting? | 2/3 — Substantial | 2/3 — Testable | Search each closure's odd choices for a reader split → a three-reader game on growth's own closures, or none | Selected · awaiting go-ahead |
| 2 | A principle drawn from growth itself, not imposed | 3/3 — Barrier | 1/3 — Stated | Name one such quantity at the closures → a candidate that forces odd, or none | Alternative · deferred |
| 3 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Reread G1's open question → a bounded next test, or a reason to keep it idle | Alternative · deferred |
| 4 | Intuition link: the maximum as decoding rule R onto the birth choices | 1/3 — Incremental | 3/3 — Ready | Restate the verdicts as nearest-code-word decoding → match or first mismatch | Alternative · deferred |

1. This is the closest this line can come to representing quantum mechanics in the program's own picture: separated readers playing a three-reader game on structures growth makes. A closure whose odd choices never split into readers has the contradiction without separated readers. It continues the declared extension, so it needs your go-ahead.
2. A principle the model itself supplies would be a native source of the sign. There's no candidate yet: three studies have found every sign supplied.
3. The program's central goal has been idle for six days. I'd need to reread its open question first.
4. The intuition link for this stop: the choices with the most failing pairs are the code words nearest rule R's all-pairs word. A free verdict is then a decoding tie, and a different count is a different metric. It's a restatement, cheap to check.

**STOP** on selecting the sign by a principle over birth choices. The maximum forces the sign at most closures, but in both directions, and the direction changes with how the principle counts and how closures are weighted. Open: a principle the model supplies itself. The line would reopen if some principle forced odd under every counting and every weighting.

**Corrections:**
- **Commutation fixed at birth refereed: signs on closed starts, two pairs per loss, and what fixes the sign.** Five Narrowings and two Not a block, no Block ([referee report](https://github.com/jscul/knotlab/blob/main/research/LOCAL-COMMUTE-20261127-001/referee-R1/report.md)). The counts all reproduced. What changes from my last report:
  - "Every grown structure keeps a state" holds under the all-commuting choice, and for every birth choice from an open start. On starts already closed at round 0, the signs must match the reordering sign.
  - Each of the ten losses needs two forbidden pairs, not one. Present information can certify one of them, but allowing that one alone restores nothing.
  - The sign is half and half only under uniform weighting of complete choices, and the earlier rounds fix it, not the close.
  - "It has to be a maximum or something like it" was wrong: an affine condition can select odd.
  - The two-reader bound of 2 holds only for a specified preparation.
  - Two denominators were off. The natural birth rule loses its state on 4,966 of 5,111 funded starts. For round 5, 178 starts completed it and 22 were cut.
  - Credit: an earlier referee already had the same 1,819 closures.

**Goals:** G18 gets an "obstruction learned" checkpoint row. No goal changed.

**Assumptions:** New scaffold A315 (the most failing pairs). It changes its verdict under every alternative principle, so the result is about the principle, not the model.

**Scaffolds:** A315 was tested against the control (fewest failing pairs), the holder-type count, choosing round by round, and one vote per census type. Its verdicts survive none of them.

**Basket:** none of the line's top three was taken, for the same reasons as last time.

The advisor was still at its usage limit, so an independent reviewer checked the design before the freeze. It settled one of my predictions by hand (start 24: the maximum closes odd, the control even) and showed another rested on a sign that doesn't exist; I replaced both before running.

[Decision note](https://github.com/jscul/knotlab/blob/main/research/MOST-FAILING-20261127-001/decision.md) · [Design and results](https://github.com/jscul/knotlab/blob/main/research/MOST-FAILING-20261127-001/README.md)
