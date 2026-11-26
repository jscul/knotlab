# Referee hand-off: MADE-COPIER-20261125-001

**Refereed, 26 November 2026: confirmed with fixes** ([report R1](referee-R1/report.md)); its fixes are folded into the records it names. The last point below is wrong about ticket A: its primary values case and form case both take from a knot the parent meets.

Tickets A, B and C are referee pending. Each pre-registration has the prior-work searches under "Prior work in the
program"; run `python3 -B scripts/track.py objects-gate` on each. The study builds on
`PARTS-MEET-AGAIN-20261124-001`, `COPYING-PARTS-20261123-001` and `RING-IN-BALANCE-20261123-001`, all referee
pending. Nothing waits on this hand-off.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| Ticket A, [result](../MADE-COPIER-20261125-001A/results.md), with the arm's three arguments in [the owner's arm](owner_arm.md) | That no copier exists in the three readings for the registered classes, laws and choice rules; that under not-all-equal no made distinction is tied; that the one case is gone under renaming | Computed, bounded; recounted by a second helper; the arguments not refereed | `experiments/MADE-COPIER-20261125-001A/`, `artifacts/MADE-COPIER-20261125-001A/` |
| Ticket B, [result](../MADE-COPIER-20261125-001B/results.md) | That where two parts of the second pattern's form appear from both, the second pattern alone leaves two as well, in all 100 runs; that arm 2 leaves none | Computed, bounded; two counts recounted by the thread; 2,718 runs not run | `experiments/MADE-COPIER-20261125-001B/`, `artifacts/MADE-COPIER-20261125-001B/` |
| Ticket C, [result](../MADE-COPIER-20261125-001C/results.md), the cases | That 17 cases of the form reading are confirmed at the registered levels (5 in the main family at 0.01 over 5, 12 in the conditional family at 0.01 over 12), all through joining, 2 needing the meeting, none in a growth with a failing knot | Computed, sampled; the cases recounted by the thread from `R3.json` and `Rcond.json` | `experiments/MADE-COPIER-20261125-001C/`, `artifacts/MADE-COPIER-20261125-001C/` |
| Ticket C, no candidate | That under each law every first-pattern form with confirmed cases has them for one second-pattern form | Computed by the engine; not recounted by the thread | `summary.json`, entry PC4 |
| Ticket C, supplied | That in all 17 cases a start knot is among the linking knots | Computed; recounted by the thread from the cases' answers to the three questions | `R3.json`, `Rcond.json` |
| Ticket C, the renaming argument C-S1 and its checks | That every rate is the same for every numbering of the start | An argument, not refereed; 157 checks equal, no rejection in 210 tests | `R7.jsonl`, `R8.json` |

Points a referee should press:

- **The main prediction failed.** The drafter predicted no confirmed case and there are five, then twelve more. The
  result is reported as found, not explained away; what keeps it from being a copier is the absence of a candidate
  and the start knot in every meeting.
- **The levels.** Confirmation is at 0.01 over the claimed cases that pass the first stage, in two families. Check
  that the conditional family's level was fixed before its runs (the engine's notes say so) and that a case passing
  only the 300 swap belongs to it.
- **The fully masked control was added after the scratch** and leans toward a positive; the pre-registration says so.
- **"Through a start knot" is the study's own third question**, answered from the linking knots. A referee should
  check two cases by hand, one of the two that also have a made knot among the links.
- **The cuts.** Rates are for prefixes of a random order of starts, under the census weighting and the labelled
  weighting; nothing is claimed for the starts not run. One run passed the hour before it was cut.
- **One disclosed sentence is false**: one of the 96 disclosed cases has the second part's form equal to the
  first's. The pre-registration's table has no "Fails when" column; each prediction was judged by its statement.
- **Ticket A's one case and ticket C's cases are under rules that reach back along descent**; the take from a met
  knot gives none in either.
