# Knot test of the study of a made count of returns

**Confirmed with fixes.** The study correctly reports that its hand prediction P11 failed. Its two-method comparison and comparison-run coverage need narrower wording. There is no Block from the knot test.

## What holds

The recorded knot test covers 28,590 source runs. One verdict was computed per knot, covering all rounds kept by extension. Of these runs, 23,308 reached their round bound, 3,484 stopped at the knot bound, and 1,798 stopped at the guard. No knot check was recorded as unfinished or untested.

| Knot law | Source runs | Knot verdicts | Compared | Distinct methods | Failing knots | Runs with a failure |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Not-all-equal | 14,295 | 14,202,628 | 14,201,704 | 14,105,679 | 0 | 0 |
| Parity | 14,295 | 14,149,583 | 14,149,583 | 14,149,583 | 25 | 20 |
| Total | 28,590 | 28,352,211 | 28,351,287 | 28,255,262 | 25 | 20 |

Distinct methods agreed where both ran. The recorded `compared` total includes 96,025 not-all-equal start knots whose direct test was repeated at the last round. The widest start knot had eight places, so the direct test's 12-place limit excluded no start knots. The other 924 not-all-equal verdicts had a single check. The smaller source runs also recorded 15,943,565 literal knot-round checks. Their failing knot identities agreed with the extension-based checks.

The 25 failures are joins under parity with 4 to 38 parents. The two predicted joins, each with twelve parents, failed in round 5 under the cap of three with short knots waiting and the rule that takes from knots the parents meet, choosing the newest name, on the two-knot start. The other 23 failed in 19 further runs. All 44 original runs supplying the 78 positive tests of the weaker reading passed the registered projection test. Eight contained two-place births.

Independent growth reproduced the knot count at every recorded round of all 20 failing runs, and reproduced all 25 failure identities, birth rounds, parent counts, and numbers of places. Twenty-three of these joins received one fresh distinction and two received two. The relation on each failing join's places has two independent parity equations at its birth and at the last round kept. With any one place forgotten some nonzero equation remains, so K2 fails. For example, at round 5 of the eight-knot start with four members holding three loose distinctions each and four dead knots sharing two distinctions with each of two consecutive members (`D2(4,3)`), the join on distinctions 100, 106, 114, 115, and 116 inherits equality of 100 and 106 in addition to its own even parity. This is the run under the cap of three, short knots waiting, taking from two parent steps above and choosing the oldest name, with demand read before takes. The canonical check found eight joint states and failed K2. The same join's parity rule alone and its first parent's relation in the grown pattern passed, with sixteen and eight joint states respectively.

Under the parity rule that leaves an implied birth with no fresh distinction, an initially open distinction stays open. Each fresh distinction is either free alongside another fresh one, or is the sum of inputs whose parity would otherwise be implied. An offshoot takes at most two old distinctions under the registered rules. Two open distinctions are jointly free or equal in all allowed states, since their linear forms are nonzero over the two-element field. In the first case a fresh distinction gives the offshoot exactly its own parity relation. In the second case the birth receives no fresh distinction and the equality is exactly its parity relation. One open input is free. Under these hypotheses an offshoot could not have contradicted P11's restriction to joins using the registered projection test.

## The fixes

- **Narrowing.** In `results.md` P11, replace “28,352,211 verdicts on 28,590 runs, the two methods never disagreeing” with “28,352,211 distinct-knot verdicts on 28,590 source runs, covering all rounds kept by extension. Distinct methods agreed on all 28,255,262 verdicts both computed. On 96,025 not-all-equal start knots the direct test agreed with its own later check. The remaining 924 verdicts had a single check.” Replace “none is in the run of a C-iii case” with “none is in the 44 original runs supplying the 78 positive C-iii tests.” Apply the same scope to `referee_handoff.md` and to the brief summary of P11 in `decision.md`.
- **Narrowing.** In `results.md` under “Not run,” replace the comparison-coverage sentence with “The knot test covered neither the numbering runs nor the swap runs. The comparison sample took 100 sources from the 5,000 in saved completion order, each of those sources weighted once at selection. Of these, 87 sources contributed 2,383 comparison runs and 8,339,008 verdicts on knots made after the comparison diverged. A separate timing sample of 36 sources from the full run-1 pool with recorded clocks contributed 665 comparison runs and 2,383,121 verdicts. No new knot failed in either sample.” The saved source keys reproduce both samples at seed 2026112508. The two source samples are disjoint. Neither sample contains a source with a reported failure or a positive C-iii test. Two failing sources had a clock and one reached the 5,000-source pool. In deviation 44, say “100 runs A sampled from the first 5,000 clock-bearing sources in saved completion order.”
- **Narrowing.** In `referee_handoff.md` and `results.md` call P11 “the registered projection test.” Add “The parity check can count a two-place equality as passing the projection test. The canonical knot check requires two loop distinctions and a contact. C-iii is a reading verdict independent of the knot clause in C.” In eight positive parity sources, 46 births had only two places. These sources supply 15 of the 78 positive tests. In 69 comparison paths from 18 of the positive parity sources, 275 more such births occur after divergence. In all, 25 positive tests have a two-place birth in their original or comparison runs, and 17 do when masked comparisons are excluded. This limits whole-run knot coverage and leaves the C-iii reading verdicts and the failed prediction under the registered projection test intact.
- **Not a block.** In `referee_handoff.md` replace “P11, which fails as predicted by hand” with “P11, the hand prediction that only the specified joins would fail, was contradicted by 23 additional failures.” In the inherited knot-test wording for not-all-equal, use “the direct check asks whether the projected relation equals the rule's own relation, which is sufficient for K1–K3.” The proposed wording concerns the direct test in the shared definitions' knot-test section. Equality to not-all-equal is stronger as a general test. A four-place relation that excludes `0000`, `1111`, `0011`, and `1100` passes K1–K3, as the canonical check confirmed, since no two forbidden words differ in just one place. This distinction changes none of the recorded not-all-equal passes. With a private fresh distinction at birth, the old inputs must be jointly free for K2, since forgetting that distinction would otherwise leave their constraint.

## Comparisons checked directly

The referee check rebuilt every recorded comparison used in the 78 positive tests, using the saved clock parts at tick rounds. Equal interventions at the same round and through the same last round are counted once per source, even when used in two roles. It matched the recorded own-birth counts by round and the joint-birth counts for all ordinary bars and matched the recorded endpoints where those were saved. The two ancillary bars for which only comparison verdicts were saved were grown through their registered bounds. Masked paths were checked through the recorded endpoints.

| Comparison source | Distinct paths | New projection verdicts | Joins | Implied births under parity | New projection failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| 39 positive tests under not-all-equal | 285 | 363,306 | 52,141 | 0 | 0 |
| 39 positive tests under parity | 285 | 358,857 | 52,149 | 275 | 0 |
| 8 tests from the predicted failing source under parity | 9 | 576 | 573 | 0 | 0 |

The nine comparisons from the predicted failing source leave their original run after round 5. Both original failures persist in every one. These comparisons are additional referee checks and are outside the two recorded samples.

For a two-place source example, take the five-knot start whose consecutive knots share one distinction each and each hold three loose distinctions (`Ring(5,3)`), under parity, FLOOR1, short knots making offshoots, taking at two parent steps, and choosing by the parent's place count. Birth 153 at round 9 is an offshoot of knot 137, with places 172 and 136 and no fresh distinction. Its induced relation is exactly `00, 11`. The canonical checker rejects this input for lacking two loop distinctions beside the contact. The [arity recount](knot_arity.json) gives the corresponding positive tests and comparison roles.

## What was not run

Independent growth was limited to the failing source runs and sources of the positive tests, with their comparisons as described above. The remaining comparison paths and the knot tests of the numbering and swap runs were not independently replayed. The reported samples do not establish absence of a failure across those runs.

## How it was checked

The recount reads the saved rows. Growth follows the frozen definitions, taking the named starts as supplied and reconstructing the selected census starts from their listed meeting patterns and loose counts. Parity growth expresses each distinction in free variables. Eliminating all other distinctions from the full parity system gives a separate check of the failures and their exact induced equations. For not-all-equal the check queries the allowed states after each forgetting at the start, and checks freedom of the inputs immediately before each birth by satisfiability. New private fresh distinctions make every round extend, preserving earlier verdicts. No growth, reading, or analysis modules from the study are imported. The four canonical checks use the induced relations as explicit Boolean clauses.

```bash
referee_dir=research/TIME-AS-FOLD-20261125-001/referee-R1
ulimit -v 2097152
.venv/bin/python -B "$referee_dir/knot_counts.py" > "$referee_dir/knot_counts.json"
.venv/bin/python -B "$referee_dir/knot_replay.py" > "$referee_dir/knot_replay.json"
.venv/bin/python -B "$referee_dir/knot_comparisons.py" > "$referee_dir/knot_comparisons.json"
PYTHONPATH=tools .venv/bin/python -B "$referee_dir/knot_cli.py" > "$referee_dir/knot_cli.json"
PYTHONPATH=tools .venv/bin/python -B "$referee_dir/knot_arity.py" > "$referee_dir/knot_arity.json"
```
