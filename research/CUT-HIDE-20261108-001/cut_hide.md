# Why two-vertex cuts hide the contradiction

Epic `CUT-HIDE-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it came from.** CONTRA-PROOF found that one row of creation between glue lines reads the removed line's tie on every
  3-connected glue tested, and fails exactly at the lines lying in a two-vertex cut, each with a side K4^(3) without a line or larger.
- **The go-ahead.** The coordinator approved this step (2026-11-08); the owner then asked to wind down, so it closes here.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The cut theorem.** At a two-line cut {a, a'} whose side meeting a once is K4^(3) without a line, the contradictory class's restriction to the glue without a and the class with a''s sign changed at one of its points in that side have the same row of creation; only the first ties a's points. | proved | A |
| 2 | **The side is rigid.** Of its eight switching classes, one ties its three outer points and leaves the centre free; the contradictory class must use it, since otherwise the removed line's far point could not be tied. | proved (exhaustive, 512 signings) | A |
| 3 | **Local lemmas.** Free, independent, tied and complemented witnesses add nothing to creation; a witness tied to the gluing line is degenerate. | proved (exhaustive) | A |
| 4 | **Confirmed.** The prediction holds at all 16 failing lines of CONTRA-PROOF's random glues, including the 2 whose hanging side has six points. | computed | A |

## Answer

- **Why.** The contradiction runs through the cut. The removed line's tie reaches its far point only through the rigid side and the
  other cut line, and one sign on that line decides whether the side is coupled or free. Creation at every gluing line is blind to
  that sign: the side's lines are degenerate either way, and its points add nothing that the cut line's third point does not.
- **So the obstruction is structural.** Native creation cannot read the contradiction across such a cut, in every glue, not only
  in the random ones.

## Reading

- **For G4.** Native relations read where the contradiction lives on every 3-connected glue tested (23 glues), and provably cannot
  across a two-line cut with a rigid hanging side. The open question is a proof for 3-connected glues.
- **Doctrine.** Everything here is invariant under relabeling lines and points.

## Literature

- **Classical.** Two-vertex cuts and decomposition along them.
- **Ours.** CONTRA-PROOF, CONTRA-READ, PENDANT-LINE, CHAIN-TRANSFER.
- **New here.** The theorem and its lemmas.

## Stress test

- **Done in the check.** The theorem's prediction is checked at every failing line found, including two hanging sides beyond its
  hypothesis; no larger run is registered, since the owner paused work.

## Pending

- **Still open from earlier epics.** As listed in SWITCH-READ's ledger.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — why two-vertex cuts hide the contradiction | **Status:** Successful | Proved for hanging sides K4^(3) without a line |
| Local direction — what native creation sees of a signing | Unresolved | The 3-connected conjecture has no proof route yet |
| Broader exploration — reading contradiction in other families | Unmapped | Only cubic glues of 8 to 14 lines tested |
| Long-term goal — G4 Emergence lives in handles | Obstruction learned | A proved place where native creation cannot read the contradiction |

**Corrections:** none.
**Goals:** G4 checkpoint (obstruction learned, now proved).
**Assumptions:** none added or changed.
**Stress test:** within the check (16 failing lines).

**Next step:** Research directions (the owner paused work on 2026-11-08; resume by choosing among these)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the 3-connected conjecture | 2/3 — Substantial | 1/3 — Stated | Find what separates the tied class where K4^(3) creates → a lemma, or a 3-connected failure | Alternative · paused |
| 2 | Extend the cut theorem to every rigid hanging side | 1/3 — Incremental | 2/3 — Testable | A lemma for witnesses that see the gluing line through one point → the two six-point cases proved | Alternative · paused |
| 3 | Leave this line for another goal | 2/3 — Substantial | 2/3 — Testable | A bounded scan of the goals doc's idle goals and backlog → one selected direction | Alternative · paused |

1. **The conjecture** is the theorem the line wants, but the mechanism varies between glues and no route is in sight.
2. **The extension** is concrete but incremental.
3. **Another goal.** What native creation sees of a signing is now well mapped: the switching class (proved), not the count, the
   contradiction on 3-connected glues (computed), and a proved obstruction at two-vertex cuts. A fresh goal may pay more.

## Final report as sent

Sent to the owner on 2026-11-08 at 17:49 UTC and copied here verbatim.

Final report before the pause. CUT-HIDE is proved, closed and published (83563d6e2). The CONTRA-PROOF-S1 row is marked signed off, and I'm not starting anything new.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: why two-vertex cuts hide the contradiction | **Status:** Successful | Proved for hanging sides that are K4 minus a line; confirmed at all 16 failing lines |
| Local direction: what native creation sees of a signing | Unresolved | The 3-connected conjecture has no proof route yet |
| Broader exploration: reading contradiction in other families | Unmapped | Only cubic glues of 8 to 14 lines are tested |
| Long-term goal: G4, emergence lives in handles | Obstruction learned | There's now a proved place where native creation can't read the contradiction |

**The theorem:** at such a cut, the contradictory class and the class with one sign of the other cut line flipped have identical rows, and only the first ties the removed line. The hanging side has exactly one rigid class out of 8, and the contradiction is forced to use it. **Corrections:** none. **Goals:** G4 checkpoint. **Assumptions:** none.

**Next step:** Research directions (paused).

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | Prove the 3-connected conjecture | 2/3 | 1/3 | Paused |
| 2 | Extend the theorem to the two six-point sides | 1/3 | 2/3 | Paused |
| 3 | Move to another goal | 2/3 | 2/3 | Paused |

**On your question:** this line is now well mapped. Native creation sees a signing's switching class (proved), but not the count. It reads the contradiction on every 3-connected glue tested (23), and provably can't across these cuts. The one remaining prize, a proof for 3-connected glues, has no route yet, so tomorrow I'd lean toward #3 unless a new idea for #1 turns up.
