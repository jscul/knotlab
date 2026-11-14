# Two unlengthened shifts beyond one box

Epic `WEIGHTS-20261112-001` (`SHIFT-COUNT-20261112-001` direction 2; G17 with G1, question 9; program topology, group spacing),
2026-11-12 to 2026-11-14. Pre-registered in commit 9d760a7dc after the advisor model's critique; paused at the owner's request on
2026-11-12 with partial results (b3af3f5c7) and resumed at his go-ahead on 2026-11-14. The canonical K1–K3 test is unchanged.
Refereed: confirmed with fixes, no Block (Review).

## Words

As in SHIFT-COUNT and COMMON-FOLD: knot kind, travelling, unlengthened shift, certified; the **new-kinds stratum**, bases with a kind
outside COMMON-FOLD's box; the **old-box stratum**, bases whose kinds all lie in it.

## The question

Under COMMON-FOLD's weighting, 147 of 169 travelling bases have two certified unlengthened shifts. Is that the rule under other
declared weightings, or a feature of one box of kinds?

## The question in standard terms

For random periodic 3-uniform hypergraphs on ℤ² under proper 2-colouring, drawn from the 738 edge orbits with offsets in
[0, 3] × [−3, 3] with weights exp(−β · diameter): among those with a finite pattern forcing its own translate, the share with two
independent certified translation directions.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Two unlengthened shifts stay the rule under all three weightings.** Among travelling bases with a new kind identified by this search, those with two certified directions are 39 of 40 at β = 0 (uniform over the 738 kinds), 35 of 40 at β = 1 and 38 of 41 at β = 2 (97.5%, 87.5%, 92.7%; Wilson intervals 87–99.6%, 74–95% and 81–97%, descriptive only, since the readings are nested and the stop depends on observed counts). W1 passes under all three (frozen: Wilson lower bound at least 50%, point at least 70%), and also when every completed sample is counted (47 of 48, 73 of 82, 41 of 45; the referee). The weightings share the kind universe and the pipeline, not their seeds (70000 + 1000·w + i), and the r-prefixes of one sample share a draw, so they are not three independent confirmations. | computed, frozen; refereed | A |
| 2 | **Travelling is found less often under weightings favouring larger kinds.** Travelling bases are 13.5% of the new-kind bases at β = 0, 27% at β = 1 and 34% at β = 2 (13.8%, 26.6% and 34.1% with r = 3, 4, 5 weighted equally; 38% of the old-box bases at β = 2), against about a third at four and five kinds in COMMON-FOLD's box; the two-shift share does not fall with it. Within one weighting the association with knot size is mixed: none by largest diameter, and by mean diameter one that reverses at fixed r (β = 1, r = 5: 7 of 27 against 9 of 22); the weighting also changes the stratum's make-up (the referee, `referee-R1/codex/diameter_tables.md`). | computed, frozen; refereed, narrowed | A |
| 3 | **The old box replicates.** Under β = 2 the old-box stratum has 46 of 54 travelling bases with two certified directions (85%, against COMMON-FOLD's 87%); under β = 0 that stratum holds one base and no travelling ones at r = 3 to 5, so the frozen replication check (W2) has no data. | computed | A |
| 4 | **What is left unresolved.** 9 travelling new-kind bases have one certified direction only (1, 5 and 3 at β = 0, 1, 2), counted as unresolved, never against the rule, because the enlarged search arm could not be run. The 4 whose second direction was forced but not certified by the main arm are certified by states repeating along and across outside a finite box (the completion pass agreed in advance), each with polarity σ = 1 (the pattern forces its complement on the translate); the referee certified all four independently and stores the frame and witness states (`referee-R1/codex/completion_checks.json`). | computed; refereed | A |

## Answer

Yes, under these weightings: among random periodic bases this search finds travelling, two unlengthened shifts are the rule whether
the kinds are drawn uniformly from a larger box or with a preference for short knots, at 88 to 98% by weighting. What changes with the
weighting is how often a base is found to travel: less often where larger kinds are favoured.

## Reading

**Interpretation, not a theorem.** For the owner's question of what is typical among samples nobody chose: where a law makes an
unlengthened shift, it usually makes two, under every weighting tried, so the law's reading of no length in two directions is the
typical one; base 16's single shift and the line it reads remain the rare case. The weightings are three members of one natural
family; others could differ (A71).

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Computed.** Every share, within the main search family (sets of 2 to 4 cells in [0, 2]²,
  primitive shifts with entries up to 6 both senses, multiples up to 4) and certificate families stated; lower bounds on the two-shift
  share.

## Deviations (recorded)

- **Paused and resumed.** The run was stopped at the owner's pause with every finished sample saved; the resumption (shared runner,
  `resume_census_job.py`) ran the missing samples with the frozen code imported unchanged.
- **A window bug in the enlarged arm.** Its shifts reach 32 cells, beyond SHIFT-COUNT's window of 30; the frozen run's worker died on
  those bases and the sample was recorded as dropped at the cap (7 samples). The enlarged arm runs only where the main arm misses a
  second direction, so those drops were exactly samples with a miss; with 3 more still running at the pause, every such sample was
  missing from the paused record (corrected, below). The resumption reran all 10 with the main arm only: its ±42 window patch for the
  enlarged arm is dead code, since that arm was then stubbed out, and the main arm's shifts (up to 24 cells) stay inside the frozen
  window (the referee).
- **The enlarged arm was infeasible.** With its window fixed it took over 30 minutes on one base (minutes for the main arm), so the
  resumption ran the main arm only; bases with one certified direction are unresolved. The calibration (the enlarged arm on
  COMMON-FOLD's one-direction bases) attempted 4 of 23 items, all capped with no outcome, and was not continued; W3 is undecided with
  no observation.
- **The stopping rule** (40 travelling new-kind bases, samples in index order) is applied to the prefix of samples; samples run past a
  stopping index (parallel workers) are not counted. The boundary is fixed by the count, not by outcomes, and counting every completed
  sample instead also passes (the referee).

## Review

The background referee thread (report `research/WEIGHTS-20261112-001/referee-R1/report.md`, feae830e2; Codex-assisted, fresh code)
confirmed the epic with fixes, no Block. The summary reruns identically; the prefix rule is a fair reading and the all-samples reading
passes too; the four completion certificates and ten main-arm bases (20 directions) are independently certified; the window patch
changes nothing. Narrowings, each logged in `docs/CORRECTIONS.md`: the paused record's selection; the calibration with no outcome;
travelling and knot size only across weightings; the Wilson intervals descriptive; the "four weightings" of the long-term row. Not a
block: seeds differ per weighting; the reruns used the main arm only; σ with the certificates; the β = 0 old box holds one base; the
pre-registration has no prior-work section, since it was frozen on 2026-11-12, before that rule.

## Workspace assumptions

- **Relied on.** A64, A67, A71, A76. **Changed.** None.

## Advisor model

Consulted before freezing: it made the new-kinds stratum primary, asked for an enlarged arm and a calibration (both proved infeasible
or partial, as recorded), widened β to 1 and 2 after tabulating the kind mix, and set the three-way outcome and a minimum denominator.

## Corrections

Five entries in `docs/CORRECTIONS.md`, all Narrowing, none changing a verdict:
- the pause note's partial counts ("all 46" at β = 0, all 27 at β = 1, no forced-but-uncertified case) left out every sample with a
  main-arm miss (found at the close and by the referee);
- the calibration ("4 of 23, none gained") has no outcome: all 4 attempts were capped;
- "big knots make travelling rarer" holds across weightings only;
- the Wilson intervals are descriptive;
- "under four declared weightings": COMMON-FOLD's census has r = 3 to 6, another stratum and another certificate family.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two shifts beyond one box | **Status:** Successful, refereed (confirmed with fixes) | W1 passes under all three weightings |
| Local direction — the weighting family | Stop here | The rule held across the family tried; more weightings would refine a share already near 90% |
| Broader exploration — G17 with G1 | Known alternatives | The basket below |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | Two-way folding is typical among identified travelling bases under COMMON-FOLD's weighting (r = 3 to 6, its own stratum and certificates) and three of a second family |

**Corrections:** five, all Narrowing (the pause note's counts; the calibration; travelling and knot size; the Wilson intervals; "four weightings"). **Goals:** a G17 checkpoint (capability gained, with G1); no goal change. **Assumptions:** none changed.
**Basket:** what gives the bonds on the uncovered side of sample 24 at r = 3 (small non-travelling sets); the cone rule (failed its
pilot); the plateau of certified upper bounds at 6 (a lower bound needs an audit of every candidate); the 9 unresolved one-direction
bases here (a feasible enlarged arm); the 8 weak repeat-size survivors.

**Next step:** Stop: the owner asked to curb token use; the line holds here until he reopens it.
