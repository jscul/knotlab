# Referee hand-off: TWO-COUNTINGS-20261125-001

**Refereed, 26 November 2026: confirmed with fixes** ([report R1](referee-R1/report.md)); its fixes are folded into the records it names. "That each hypothesis is needed" below is not shown: the hypotheses are sufficient on the registered form.

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/TWO-COUNTINGS-20261125-001A/preregistration.md`. It builds on
`SETTING-AS-REREAD-20261123-001`, `ONE-PARENT-REREAD-20261123-001`, `THIRD-HOLDER-20261123-001`,
`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` and `REVIEW-LEADS-20261123-001`, all referee pending, and it narrows three of
them (the knot test in the whole structure). Nothing waits on this hand-off.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| [Definitions](definitions.md), the lemma on settings added as births, with hypotheses h0, h1′, h2, h3′ and h4 | That, counted from a common stage before the setting knots, a four-correlation score is at most 2 for any class of outcome functions and exactly 2 when the class holds a constant, with both records hidden; that each hypothesis is needed | An argument, checked by the advisor by hand in two forms; not refereed. Seven built examples break it, but none breaks h1′ alone or h3′ alone | The definitions; the examples in the ticket's result |
| [The knot-test finding](knot_test_finding.md) and the ticket's [result](../TWO-COUNTINGS-20261125-001A/results.md), "The knot test in the whole" | Which rules of the 33 registered structures are knots in the whole structure (19 are not; each passes on its own); that a score above 2 under counting from the finish stands on structures whose every rule is a knot, the two seven-rule parts at 61/30 among them | Exact computation by two independent programs (the run's and the checker's), with the canonical command on every failing rule and on all 176 rules of the two parts' finished structures; the 18-knot structure by projection only | `experiments/TWO-COUNTINGS-20261125-001A/TWO-COUNTINGS-20261125-001A-E001_two_countings/` (`knottest.py`, `part8_early.py`); [the check](checks/check_report.md) with its scripts; `PYTHONPATH=tools python3 -B -m knotlab check` |
| Ticket A, [result](../TWO-COUNTINGS-20261125-001A/results.md), the verdicts | The gates; that every recorded score is reproduced under counting from the finish and every registered setting test scores exactly 2, hidden, from a stage before the settings; the classification of 1,200 orders of construction; the table's 15 recomputed rows | Exact arithmetic by a program written from the frozen text; the scores recounted by the checker; the hypothesis checks are the run's alone | the same experiment folder (`part1_gates.py` to `part9_engine.py`) and its artifacts |
| [Claim](claim.md), "settled" statements | That a law which uses no value makes the same structures under either counting, so no run decides between them | An argument, close to a tautology; not refereed | the claim |

Points a referee should press:

- **The hypothesis checks.** Whether each registered structure meets h0 to h4 was decided by the run's own program and
  not recomputed by the checker.
- **Readings taken after output was seen.** The absolute value in the parity score (the records' form, not the
  definitions'), and the comparison of grown histories by a key in the "grow again" part: neither decides a verdict,
  and both are listed in the result's "Deviations that matter".
- **The cut.** The canonical command stopped at its registered twenty minutes; 1,046 structures built during the run
  were tested by projection only.
- **The earlier studies' notes are not edited.** The narrowing is recorded in the corrections log, in the public
  history and in this study.
- **Words.** "Counting from the finish" and "counting from the start" were chosen with the advisor; "rule" is used
  until a rule has passed the knot test in the whole.
