# Balanced loops of rings persist at every size

Epic `LOOP-PROOF-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `LOOP-RINGS-20261108-001` found closed loops of rings whose contacts all persist while influence returns
  round the loop, and 54 four-ring families that persist at every size from 4 to 16, with no proof. The coordinator relayed its
  direction 1 on 2026-11-08: a proof by generating functions over GF(2), and, if it stalls, a record of where feedback breaks the path
  lemma rather than a wider search.
- **The question.** Do the four-ring loops persist at every ring size, and why?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Feedback cancels in balanced loops.** With each contact reading the chain ends (and possibly its partners) on both rings, a contact's generating function satisfies C_i = S_i + z a^(f_i) C_(i−1) + z a^(b_(i+1)) C_(i+1), a = z/(1 + z). After one substitution the term in C_i always cancels, and the term in the opposite contact cancels exactly when the positions sum to 2s: two contacts at cell 2 and two at cell s − 2. Then each contact has a closed form with no feedback left. | proved | A |
| 2 | **Balanced loops persist at every size.** Under a no-overlap condition on partner reads, every contact binds both of its rings at every lag at every ring size, through the ends of the two chains it reads. With every contact reading its left neighbours this holds from size 4 for all six balanced position patterns. | proved; checked on 516,672 lags at sizes 4 to 30 and on full state spaces at 4 and 5 | A |
| 3 | **Influence returns at binomial lags.** Each contact needs the two rings it does not touch exactly where C(T − 2, m) is odd for some m in an interval fixed by the chain lengths: recurring lags, by Lucas' theorem. | proved; checked on 186,576 lags | A |
| 4 | **Where the argument stops.** It covers 16 of the 54 families. In 26 others a contact's partner is also the end of a chain another contact reads, and persistence holds through witnesses that change from lag to lag. In 12 a contact reads one partner only and so feeds itself. And in unbalanced loops the feedback term stays: none is persistent at sizes 5 to 30 (236 of 260 lose persistence, 24 stay undecided). | proved for the 16; computed for the rest | A |

## Answer

The stop rule's first outcome holds for the loops the argument covers. In a balanced loop the influence that returns round the loop
cancels in pairs, mod 2, so each contact's value has a closed form, and its dependence on its own two rings never lapses: persistence
at every ring size. Influence still returns, at recurring binomial lags. The argument stops at overlapping partners, at contacts that
read one partner, and at unbalanced positions, whose feedback does not cancel.

## Reading

**Interpretation, not a theorem.**
- **Why balance.** Going round the loop, the two ways from a contact to the opposite one have chain lengths f_i + f_(i−1) and
  b_(i+1) + b_(i+2). When they are equal the two contributions are the same power of a and cancel mod 2. Balance is a condition on
  the loop as a whole, not on any one ring, which is why every family that persists across sizes mixes the positions.
- **For composed topology across time.** A closed route of contacts now holds at every size, by proof, in these loops: a cycle of
  native adjacencies whose influence returns, with every contact complete.
- **What feedback does.** In the path proofs influence flowed one way. Here it returns, and survives exactly when the return cancels.
  Where it does not cancel, persistence fails.
- **Not a metric.** The binomial lags measure nothing; no length or distance is formed.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Balanced loops persist (2) | sizes 4 to 30, every balanced pattern and every allowed law, every lag to 300 | pass: 516,672 lags |
| Influence returns at binomial lags (3) | sizes 5 to 30 | pass: 186,576 lags |
| Unbalanced loops do not persist (4) | sizes 5 to 30 | pass, narrowed: none persistent; 24 undecided at sizes 25 to 29 (first stated as "fail at every size") |

## Literature and provenance

- **Sources.** Generating functions over GF(2) for linear recurrences; Pascal's triangle mod 2 and Lucas' theorem.
- **Classification.** Known-with-delta: the ingredients are classical, and the delta is the pairwise cancellation of a loop's
  feedback under balance.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Scope.** Four rule-60 rings (rule 102 by mirror symmetry), the stated laws, sizes s ≥ 4.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A), with its checks and the record of where it stops.
- **Administrative.** This note and the closure.

## Pending the owner

- **Counted length as a native magnitude**, which gates distance across time; put to the owner by the coordinator.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the four-ring loops at every size | **Status:** Successful | Proved for balanced loops; where it stops recorded |
| Local direction — composed topology across time | Continue | Loops of more rings, where the two ways round no longer meet at one opposite contact |
| Broader exploration — G5 with G1 | Known alternatives | The 38 families outside the proof; the rule-90 mechanism (B13); restrictions (B14); distance, once the owner rules |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Closed routes of contacts across time hold at every size, by proof, when balanced |

**Corrections:** none logged; one claim narrowed before it was recorded (unbalanced loops). **Goals:** a G5 checkpoint (capability
gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Loops of r ≥ 5 rings, where the feedback terms land on different contacts and may need higher-order cancellation.
  - The 38 four-ring families that persist without the argument's witnesses.
- **The missing bridge to the program's composed topology.** Loops of any length, and then loops that share rings.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Balanced loops of any number of rings (G5, with G1) | 3/3 — Major | 2/3 — Testable | Write the r-ring system over GF(2) and find when the returning feedback cancels (a balance condition on the chain lengths round the loop); check r = 5 to 8 at sizes 4 to 16 → a theorem for every r, or the first r where no balanced loop persists | Selected · not started |
| 2 | The 38 four-ring families outside the proof (G5) | 2/3 — Substantial | 2/3 — Testable | Track the union of witness cells under overlapping partners and one-partner self-feedback → a proof, or the families that fail at some size | Alternative · deferred |
| 3 | The rule-90 mechanism (backlog B13) | 2/3 — Substantial | 2/3 — Testable | Parked | Backlog |
| 4 | Distance across time | 3/3 — Major | 1/3 — Stated | Waits on the owner's ruling on counted length | Alternative · deferred |

1. **Loops of any length.**
   - **Payoff 3.** Closed routes of every length would complete the cycle side of composed topology across time.
   - **Concreteness 2.** The same generating functions apply; the cancellation pattern for r ≥ 5 is the open part.
   - **Uncertainty.** Whether a balance condition still makes the feedback cancel when the two ways round meet at no single contact.
2. **The other families.** Narrower; the union of witnesses is the obstacle.
3. **The rule-90 mechanism.** Parked as B13.
4. **Distance.** Waits on the owner.

**Recommendation.** Continue with direction 1. If no balance condition makes the feedback cancel for five rings, record that loops
of more than four rings need a different argument and pause the line for the owner's ruling on distance.

## Final report as sent

Sent to the owner on 2026-11-08 at 14:11 UTC and copied here verbatim.

The four-ring loop proof is done and published (epic 5a702b939, shared docs 408a1ce86). In a balanced loop, the influence coming back round cancels in pairs, mod 2, so every contact keeps both of its rings at every lag, at every ring size. Balanced means two contacts at cell 2 and two at cell s−2.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the four-ring loops at every size | Successful | Proved for balanced loops; where it stops is recorded |
| Local direction: composed topology across time | Continue | Next are loops of more rings, where the two ways round no longer meet at one opposite contact |
| Broader exploration: G5 with G1 | Known alternatives | The 38 families outside the proof; the rule-90 mechanism (B13); restrictions (B14); distance, once you rule |
| Long-term goal: G5 (question 4) | Capability gained | Closed routes of contacts across time hold at every size, by proof, when balanced |

- **Why it works:** going round the loop to the opposite contact, the two ways have chain lengths that agree exactly when the loop is balanced. The two contributions are then the same power of z/(1+z) and cancel mod 2. So balance is a property of the whole loop, which is why every family that held across sizes mixed its positions.
- **Influence still returns:** each contact needs the two rings it doesn't touch at lags where a binomial coefficient is odd.
- **Checked:** 516,672 lags at sizes 4 to 30, plus full state spaces.
- **Where it stops:** the proof covers 16 of the 54 families. In 26, a contact's partner is also the end of a chain another contact reads. In 12, a contact reads only one partner and feeds back into itself. Those still persist computationally, but this argument doesn't track them. Unbalanced loops keep their feedback, and none of them persists.
- **One claim narrowed:** the checklist first said unbalanced loops "fail at every size". In fact 236 of 260 fail and 24, at sizes 25 to 29, stayed undecided. None persists. It was fixed before anything was recorded.

Next step: Continue, selected #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Balanced loops of any number of rings | 3/3 | 2/3 | Find when feedback cancels in an r-ring loop; check r = 5 to 8 at sizes 4 to 16 → a theorem for every r, or the first r with no persistent balanced loop | Awaiting go-ahead |
| 2 | The 38 families outside the proof | 2/3 | 2/3 | Track the union of witness cells → a proof, or a size where they fail | Alternative |
| 3 | The rule-90 mechanism (B13) | 2/3 | 2/3 | Parked | Backlog |
| 4 | Distance across time | 3/3 | 1/3 | Waits on your counted-length ruling | Deferred |

**Corrections:** none logged. **Goals:** G5 checkpoint, capability gained. **Assumptions:** none added.

[Decision note](https://github.com/jscul/knotlab/blob/main/research/LOOP-PROOF-20261108-001/loop_proof.md)
