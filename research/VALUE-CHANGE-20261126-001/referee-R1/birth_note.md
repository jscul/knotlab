# Rule R on births and closed patterns

The independent replay agrees with every field of the 300 stored rows. It sampled the same 7,075-start census uniformly without replacement, using seed 20261128, and rebuilt ordinary parity growth through six birth rounds. The resulting sample had 96 closers, 70 stalls and 134 structures that grew through round six. The largest had 80 knots. A settled failing pair occurred on 290 starts. [Checker](birth_rebuild.py) · [Rows and witnesses](birth_results.json)

| Settled pair of births | Rebuilt | Matches the formula |
| --- | ---: | ---: |
| Same round | 8,684 | 8,684 |
| Parent and child | 6,013 | 6,013 |
| Two rounds apart | 18,547 | 18,547 |
| Three or more rounds apart | 22,870 | 22,870 |
| Adjacent rounds without a parent and child relation | 19,110 | 19,110 |
| Total | 75,224 | 75,224 |

The formula totals omit 5,206 open pairs and 23,547 settled pairs involving at least one start knot. The checker uses each distinction's holders to realize the signed swaps, adds the operator exponents to obtain each knot law, and computes the interchange sign from those exponents. It compares the result with formulas using birth rounds and parent sets. It reads the archived results after the replay.

## Why six rounds force a failure

A funded round uses every loose distinction. A birth takes at most one per parent. Thus a shared distinction of a born knot connects it only to a parent or child, and it shares at most one distinction with each.

For two born knots with `p` and `q` places, the swap parity starts at `pq`. Subtract one for each co-held pair of places and for any pair consisting of the same distinction twice. In the same round the subtracted count is the number of common parents and children. For a parent and child it is `p + q − 1`, since all pairs using their single shared distinction commute and there is no third holder that is one round from both. Two rounds apart, each common intermediate knot contributes one. Three or more rounds apart, the count is zero. It is also zero for adjacent rounds without a parent and child relation. These births have no shared distinction, and a third holder would have to be one round from both. This proves the fifth formula.

Take any ancestry chain from a sixth-round birth back through one birth in each of the preceding five rounds. If the first two or last two place counts are both even, that pair anticommutes by the parent and child formula. Otherwise choose an odd count from each of those two pairs. Their births are at least three rounds apart and anticommute. Each possible witness uses two different rounds, so it is already settled. All 134 sixth-round replays have one of these witnesses. At length five, the parity sequences `EOEOE` and `EOOOE` pass these two tests alone.

## When a list of noncommuting distinctions is an allowed change

For a knot `U`, let `N(U)` be the distinctions whose values anticommute with its law. The swap parity with another knot `V` is the parity of the number of places of `V` that belong to `N(U)`. Hence `N(U)` is an allowed change exactly when the law of `U` commutes with every knot law. This gives all 56 lists on the ten commuting closers, of which 14 are empty. The replay recovered the same ten closers and all ten archived per-closer counts. [Per-knot lists](birth_results.json)

The sampled five-knot census start at index 4376 is closed from the start. Its supports are `{0,1,2,3}`, `{0,4,5}`, `{1,6,7}`, `{2,3,4,5,8}` and `{6,7,8}`. For the second knot, direct counting of the unheld pairs gives `N = {6,7,8}`. The fourth knot holds one of those distinctions and the fifth holds three. Each odd intersection witnesses that the list fails to be an allowed change. [Census source](../../FORBID-EDITS-20261126-001/starts.json)

**Narrowing.** The decision says “every knot's non-commuting values form an allowed change (56 of 56).” State the condition that the knot law commutes with every knot law. The README gives the condition in its description of the ten closers. [Decision, item 1](../decision.md#L10) · [README, item A.3](../README.md#L27)

**Not a block.** The README says “Anything about not-all-equal, sampled starts, or more than two rounds of growth.” The decision says “**Not shown.** Any native change read or coherent state; three readers; sampled starts; not-all-equal.” Specify that these scope exclusions concern the joined-ring reader experiment. The signed rule R check used sampled starts through six rounds. [README, scope](../README.md#L109) · [Decision, scope](../decision.md#L26)

## Reproduction

From the repository root, use the command below. The timed pilot added `--limit 10` and used the same settings.

```sh
ulimit -v 1900000
ulimit -t 590
/usr/bin/time -f 'elapsed=%e user=%U system=%S peak_kib=%M' \
  .venv/bin/python -B research/VALUE-CHANGE-20261126-001/referee-R1/birth_rebuild.py
```

The pilot took 0.05 seconds elapsed. The full run took 0.24 seconds elapsed and peaked at 21,896 KiB. Each used one computation process. A separate direct check of the closed counterexample used 0.03 seconds elapsed. The other 6,775 census starts, census regeneration, subsequent birth rounds and alternative growth laws were not run.
