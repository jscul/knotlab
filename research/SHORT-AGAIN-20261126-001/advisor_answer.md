# The advisor's review of the design (Claude Fable 5.2, no tools), 26 November 2026

The question is [advisor_question.md](advisor_question.md), asked before any candidate was run. What was taken from it is in the [note](README.md), "The design".

1. **Run first: ODD-FEWER and a D histogram, not a second listed candidate.** Before any ration, run the ordinary count on the d = 1..8 test starts and tabulate D by class (A's own, joint descent, link descent, B's own) and by join versus offshoot. Each candidate's shortness is a function of (kind, p, D), so this table predicts how often each one makes knots short.

2. **What the rules already imply** (a new knot's loose count is f, so it is short iff D > f):
   - **ONE-FEWER:** a join is short whenever D ≥ 2, and an offshoot whenever D ≥ 3. This is the cap regime, so expect (i) to fail. It also gives f = 0 when p ≥ 3 and D = 1, producing a knot that is counted in a group but is not a member; fix or exclude that case.
   - **JOIN-FEWER:** every join with D ≥ 2 is short whatever B is. Shortness is then constant rather than "now and then", so (ii) fails by construction. (i) could survive only through offshoots and D = 1 joins.
   - **THIRD-FEWER:** joins with D = 2 are short. D = 2 is probably the typical demand along a chain, so the link descent likely severs itself and the mark never arrives.
   - **ODD-FEWER:** short iff D is odd and ≥ 3. Chain interiors (even D) pass and branch points go short, so it is the only listed candidate not predicted to fail.
   - None is certain to fail by the rules alone, but only ODD-FEWER is worth a full run.

3. **A's own knots are subject to the ration too.** Nothing can exempt them, so run A alone under each ration. If A's own joins collapse without B, (i) is dead for reasons unrelated to B.

4. **Better candidate: your threshold rule, run second.** A join gets D − 1 iff D > p (floor 1); everything else gets the ordinary count. Shortness then needs D ≥ 3 at a join, and offshoots are never short, so they keep carrying the signal. Unlike parity, the response is monotone: two changes cannot cancel each other. If the histogram shows D > p is common, narrow it to D = p + 1.

5. **Skip o for now.** The recorded o-rations failed alongside joins held at max(3 − p, 1), so that failure is confounded. o also only relays the parent's situation one step.

6. **(i) is not hopeless under waiting; try the ration first.** Losing all groups is tolerable if shortness is rare: partners divert to never-short offshoots and the waiter rejoins later. Set a kill criterion: if the unmarked A-own × joint join count reaches zero before round 16 under both ODD-FEWER and the threshold rule, redesign the treatment. Proportional cancellation needs a rule for which groups to drop, and without names that rule must be symmetric (for example, drop all tied groups). It also thins the only channel into A, so "never heard" becomes likelier.

7. **Controls:**
   - **Pairing:** compare marked and unmarked runs at the same d, since d itself changes D.
   - **Baseline:** same starts under the ordinary count, where A must never differ.
   - **Front lag:** report hearing round minus the round the joint-descent front reaches A's neighbours. A value of d + constant is only the light cone.
   - **Placement:** put the mark on a link knot at distance k. Hearing should track k, not d.
   - **Mark kind:** try two marks, a different B start knot, and a removed distinction. Parity rules may respond to one and not two.
   - **Second reading:** use the first differing cancelled group that contains an A-own knot. It should precede or coincide with the first difference in births.
   - **Censoring:** report "not heard by 16" as censored, never as 16, and give the fraction heard per d.
