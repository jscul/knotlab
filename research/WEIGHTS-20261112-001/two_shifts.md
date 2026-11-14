# Two unlengthened shifts beyond one box

Epic `WEIGHTS-20261112-001` (`SHIFT-COUNT-20261112-001` direction 2; G17 with G1, question 9; program topology, group spacing),
2026-11-12 to 2026-11-14. Pre-registered in commit 9d760a7dc after the advisor model's critique; paused at the owner's request on
2026-11-12 with partial results (b3af3f5c7) and resumed at his go-ahead on 2026-11-14. The canonical K1–K3 test is unchanged.
**Referee pending** (handed to the referee thread).

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
| 1 | **Two unlengthened shifts stay the rule under all three weightings.** Among travelling bases with a new kind, those with two certified directions are 39 of 40 at β = 0 (uniform over the 738 kinds; Wilson 87–99.6%), 35 of 40 at β = 1 (74–95%) and 38 of 41 at β = 2 (81–97%). W1 passes under all three (frozen: Wilson lower bound at least 50%, point at least 70%). The three weightings share kinds and seeding, so they are not three independent confirmations. | computed, frozen | A |
| 2 | **Travelling itself is rarer with big knots.** Travelling bases are 13.5% of the new-kind bases at β = 0, 27% at β = 1 and 34% at β = 2 (and 38% of the old-box bases at β = 2), against about a third at four and five kinds in COMMON-FOLD's box: the denominator shrinks as knots get bigger, the two-shift share does not. | computed, frozen | A |
| 3 | **The old box replicates.** Under β = 2 the old-box stratum has 46 of 54 travelling bases with two certified directions (85%, against COMMON-FOLD's 87%); under β = 0 that stratum is empty at r = 3 to 5, so the frozen replication check (W2) has no data. | computed | A |
| 4 | **What is left unresolved.** 9 travelling new-kind bases have one certified direction only (1, 5 and 3 at β = 0, 1, 2), counted as unresolved, never against the rule, because the enlarged search arm could not be run. The 4 whose second direction was forced but not certified by the main arm are certified by states repeating along and across outside a finite box (the completion pass agreed in advance). | computed | A |

## Answer

Yes, under these weightings: among random periodic bases that travel at all, two unlengthened shifts are the rule whether the kinds
are drawn uniformly from a larger box or with a preference for short knots, at 88 to 98% by weighting. What changes with the weighting
is how often a base travels: big knots make it rarer.

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
  those bases and the sample was recorded as dropped at the cap (7 samples). The resumption reran them.
- **The enlarged arm was infeasible.** With its window fixed it took over 30 minutes on one base (minutes for the main arm), so the
  resumption ran the main arm only; bases with one certified direction are unresolved. The calibration (the enlarged arm on
  COMMON-FOLD's one-direction bases) ran 4 of 23 (none gained a second direction) and was not completed; W3 is undecided.
- **The stopping rule** (40 travelling new-kind bases, samples in index order) is applied to the prefix of samples; samples run past a
  stopping index (parallel workers) are not counted.

## Review

Referee pending: handed to the referee thread on 2026-11-14.

## Workspace assumptions

- **Relied on.** A64, A67, A71, A76. **Changed.** None.

## Advisor model

Consulted before freezing: it made the new-kinds stratum primary, asked for an enlarged arm and a calibration (both proved infeasible
or partial, as recorded), widened β to 1 and 2 after tabulating the kind mix, and set the three-way outcome and a minimum denominator.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two shifts beyond one box | **Status:** Successful, referee pending | W1 passes under all three weightings |
| Local direction — the weighting family | Stop here | The rule held across the family tried; more weightings would refine a share already near 90% |
| Broader exploration — G17 with G1 | Known alternatives | The basket below |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | Two-way folding is typical among travelling bases under four declared weightings |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G1); no goal change. **Assumptions:** none changed.
**Basket:** what gives the bonds on the uncovered side of sample 24 at r = 3 (small non-travelling sets); the cone rule (failed its
pilot); the plateau of certified upper bounds at 6 (a lower bound needs an audit of every candidate); the 9 unresolved one-direction
bases here (a feasible enlarged arm); the 8 weak repeat-size survivors.

**Next step:** Stop: the owner asked to curb token use; the line holds here until he reopens it.
