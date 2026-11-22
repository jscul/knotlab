# A companion changes what the two readers can measure

**If the unread knot shares the second reader's only place, the exact signed measurement succeeds on zero launches. If it shares one of the first reader's two places, a coherent not-all-equal first knot succeeds with optimal probability $1-\sqrt5/3$, about 25.46%.** The isolated knot succeeded on one third of launches. Either law at the unread knot gives the same answer. [Proof](../../proofs/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001A/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001A-P001_unread_companion/proof.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two knots sharing one distinction | **Successful** | A proof over all finite serial local instruments gives the exact optimum at both placements. A reached-word protocol attains the positive value. |
| Local direction — a companion the readers cannot inspect | Resolved for a single shared name under the stated condition | Each value of the shared place has an exclusive unread word. This prevents changing that physical value on a legal branch. |
| Broader exploration — more than one shared name | Open | Two shared names need not be individually fixed by any particular unread word. |
| Long-term goals — G18 Comparing growth laws and G5 Dynamics | Operational distinction established | The answer depends on which remaining names the two readers can use while obeying both physical rules. |

Let A read two names $a,c$, and B one name $b$. The companion holds one of those names and its own $d,e$, which neither reader can touch or hear from. The table gives the chance **per preparation of the complete five-name holding** of returning either measured sign with the entire required target state. The diagonal controls have the same ordinary word frequencies.

| First knot | Unread companion | Allowed five-place words | Coherent, $b$ shared at B | Coherent, $a$ shared at A | Fully dephased, either placement |
| --- | --- | ---: | ---: | ---: | ---: |
| Even parity | Even parity | 8 | 0 | 0 | 0 |
| Even parity | Not-all-equal | 12 | 0 | 0 | 0 |
| Not-all-equal | Even parity | 12 | 0 | $1-\sqrt5/3$ | 0 |
| Not-all-equal | Not-all-equal | 18 | 0 | $1-\sqrt5/3$ | 0 |

**Why the unread names matter.** Under not-all-equal the unread pair 11 forces the shared place to be 0, while 00 forces it to be 1. The other two unread words permit either value, so the two companion states have a substantial overlap of $2/3$. Nevertheless, a reader changing the shared value would also change it on an exclusive unread word. No finite history of lawful local operations and classical messages can do that. When the original source is traced out of the returned target, the interference between the two shared values vanishes. The readers may calculate this bound without having observed the unread pair. The same argument works on larger finite holdings which meet the readable knot at just that name and have an exclusive unread completion for each value. [Complete-word and reduced-density checks](word_checks.json)

**Who can still make the meter.** When the one-place reader holds the shared value, fixing it leaves that reader with a single basis word. On the independent target 00 the surviving state is a mixture of products on every branch. Both exact signs would instead return an entangled pair. When A holds the shared value in a not-all-equal first knot, A can read $a$, leave $c$ physically opposite to it, and let B safely store and clear $b$. Their private registers retain a coherent three-word preparation, and their two source knots stay lawful. A local filter balances its two surviving contributions. Coherently controlling the same operations from the retained $a$ also works when its value is kept private. It announces success with the probability in the table. No protocol can do better because a returned sign on 00 consumes at least half its probability from the smaller of the two Schmidt weights, $(3-\sqrt5)/6$. The filter may accept the *diagonal* comparison twice as often, yet its accepted states never perform the required signed measurement. [Source, accessible flags and returned targets](companion_evidence.json.gz)

The public measurement of $a$ gives each value with probability $1/2$. For each such value, source refusal weight per full launch is $\sqrt5/6$, the target is untouched, and all three keepers start and end blank. On 00 the eight successful records of shared value and binary analyzer flags each have weight $(1-\sqrt5/3)/8$. The two local flags identify the sign jointly. The third keeper writes 101 or 011 when both measured bits arrive. A missing message can leave it at 110 even when both target measurements occurred. A new successful meter repeats the sign and preserves every within-sign superposition. The replay retains 168 source records, 436 fine single-launch records, 300 fresh-repeat records and 968 writer and message settings. Exact checks cover both source preparations, all 16 real target matrix units, independent local spectators, postmeasurement faults and refusals. [Replay](companion_replay.py)

**Why averaging conditional guesses would be wrong.** With two not-all-equal knots, two thirds of the whole preparation has $d\ne e$. If an outside reader announced that fact, those branches could use the isolated-knot read. The corresponding per-launch success rates with that additional bit would be $2/9$ for a shared $b$ and $(5-\sqrt5)/9$ for a shared $a$. Neither figure applies when the companion is unread. [What resolving the unread words adds](../../proofs/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001A/UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001A-P001_unread_companion/proof.md)

**Next step:** Full pivot — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A companion sharing two readable names and retaining one unread name | 3/3 | 2/3 | Fix the rules on $a,c,b$ and $a,b,d$ with $d$ unread → establish an exact attainable probability or obstruction | Alternative · deferred to the joint decision |
| 2 | Scientific referee of the one-shared-place optimum | 2/3 | 3/3 | Reconstruct the exclusive-word argument and process probe → confirm or challenge the equality bound | Alternative · deferred |

The two-name case changes the physical restriction responsible for the present theorem. The referee has the exact matrices and named paths for the completed case. The [combined decision](../UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001/decision.md) records the project-wide recommendation.

**STOP** on a single shared distinction with exclusive unread completions. The isolated comparison, primary cases and crossed-law controls have reached the frozen stop. Independent scientific referee pending.

**Corrections:** None to earlier public claims. The earlier one-third result used an isolated coherent source.

**Goals:** B296 resolves this test under G18 Comparing growth laws and G5 Dynamics.

**Assumptions:** A184 keeps the companion's private names unread and both rules in force. A181 and A182 specify the surviving target and serial reader access.

**Scaffolds:** Uniform positive whole-source amplitudes, the diagonal comparison, real local filters, squared weights, private blanks, classical communication and ordinary keepers were supplied. The added companion report is a counterfactual comparison only.
