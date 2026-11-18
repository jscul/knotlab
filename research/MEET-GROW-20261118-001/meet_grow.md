# Does the meeting pattern grow on its own?

Epic `MEET-GROW-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes the selected direction of
`MEET-ORDERS-20261118-001`. Goals G16 and G1; tests A97. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block, folded in on 18
November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `73b8a25a0` at 03:33 UTC on 18 November. Two
  launches on the shared runner: MEET-GROW-B1 (3 cases, 03:33 to 03:36 UTC) and MEET-GROW-B2 (312 cases, 03:34 to 03:44 UTC), 315
  of 315 ok.
- Code: [job.py, checks.py, merge.py and melib.py](../../experiments/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph/)
  (melib.py is `MEET-ORDERS-20261118-001B`'s engine, unchanged).
- Results: [results.json](../../artifacts/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph/results.json).

## The answer

- **Under KF3 the meeting pattern grows by the same law wherever it sits along the line** (computed, exact). *Narrowed after the
  referee:* first written "grows on its own", which says more. The pair graph is not a process by itself: within one
  presentation, bases with the same pair graph give different laws for the next pairs from the third new distinction on (at six,
  6 of 18 pair graphs at n0 + 2 and 170 of 218 at n0 + 3), so the states steer which pairs come next. What holds is that the
  joint growth is the same for every placement of the pattern. Take two presentations of a line whose knots, read as
  sets of distinctions with the line ignored, are the same pattern up to renaming. The co-knotted pairs, which are all KF3 reads of
  the knots, then grow with the same law, label for label. One renaming of the starting pattern carries the whole distribution of
  the grown pairs from one presentation onto the other, after every new distinction.
  - It holds for all 1,049 such pairs of presentations: lines of 5 (to n0 + 5), 6, 7 and 8 (to n0 + 4) and 9 (to n0 + 3)
    distinctions, with 1, 3, 4, 12 and 27 meeting patterns.
  - It holds state by state as well (P4): the joint distribution of the pairs with each state's options, by their cost and the
    pairs each adds, is carried the same way through n0 + 3. So it is not an average over states. Something maps the states of one
    presentation to those of the other while keeping every option's effect on the pairs (the advisor's candidate is a twist, below;
  `MEET-TWIST-20261118-001` constructs and proves it).
- **The states differ, and so do the orders.** The same pair graph is reached with different state sets, and in every meeting
  pattern with more than one presentation the chance of two orders differs between presentations (all 46 such patterns). How
  many orders the grown pattern carries depends on where it sits along the line, the bracketing of `MEET-ORDERS-20261118-001`.
- **Different meeting patterns grow differently** (P2). Up to renaming, their pair-graph distributions differ after every new
  distinction through n0 + 3, even where their labelled counts coincide (two patterns of eight with 892 and then 30,868 labelled
  bases each).
- **The labelled base counts follow the meeting pattern** (P3), confirming `MEET-ORDERS-20261118-001`'s post hoc reading one size
  past.

**In the owner's terms.**
- How the knots meet grows by the same law wherever the pattern sits along the line: the pattern of which knots share which
  distinctions grows alike from every placement.
- It does not grow by itself: the states, together with the knots, steer which pairs come next. Where the pattern sits changes
  only how many orders the grown pattern carries. Same pattern, different placement: same growth, different number of orders.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 6 gate checks pass | held | all pass before the freeze |
| P1 | Same meeting pattern: labelled pair-graph distributions carried at every level | held | 1,049 of 1,049 pairs (3, 6, 54, 177, 809 for n0 = 5 to 9) |
| P2 | Different meeting patterns differ up to renaming at every level to n0 + 3 | held | no pair of patterns equal at any level |
| P3 | Labelled base counts depend only on the meeting pattern | held | all 47 patterns |
| P4 | The joint distribution with each state's option profile is carried (to n0 + 3) | held | every pair; a state-by-state correspondence, not averaging |

4 of 4 held. The advisor put P1 at about 85% and expected any failure at depth (six at n0 + 4); six holds there.

## What the knot picture explained

- **Why it holds for the first two new distinctions.** `MEET-ORDERS-20261118-001`'s Lemmas A and B list KF3's options by knots:
  the fill of a knot, and two re-bracketing fills per knot sharing a pair with the filled one. Each adds new pairs that depend only
  on which knots share which distinctions, so the pairs' law is the meeting pattern's (proved there).
- **Why it can hold beyond, state by state** (the advisor's account, not proved). Presentations with one meeting pattern are one
  triangulation (the literature's) with different marked sides. Moving the marked side past a distinction v whose neighbours are u
  and w replaces v by the parity of u, v and w on every state: a one-to-one map of states that keeps the co-knotted pairs and the
  number of states but not the number of orders. If it extends through growth, it carries KF3 from one presentation to the other.
  P4's success says some such map exists through n0 + 3.

## What it means for A97 and the goals

- **A97** stays under challenge, with a sharper positive finding. The growth of how the knots meet does not depend on where the
  pattern sits along the line, while the number of orders does. (Narrowed after the referee: the states still steer which pairs
  come next; what is independent of them is the placement, not the growth.) Whether the meeting pattern is a distance is open.
- **G16:** capability gained. A computable invariant, the meeting pattern up to renaming, predicts the whole law of KF3's pair
  growth from every presentation tested, and the bracketing predicts the orders.
- **G1:** no demonstrated advance; the result separates the pattern's growth from the orders without growing two orders.

## Limitations

- Computed, not proved: through n0 + 5 for five, n0 + 4 for six to eight, n0 + 3 for nine; P4 through n0 + 3. The twist is the
  advisor's reading.
- Fewest-knot presentations of a line under KF3 only (A99, A100). A100 is material: `MEET-ORDERS-20261118-001`'s referee found
  that one redundant knot changes the orders' chances; whether it changes the pairs' law across placements is untested.
- The coarse counts (labelled bases and odd-set weights) do not separate every pattern at eight (`MEET-ORDERS-20261118-001`'s
  referee: 12 patterns, 8 signatures); P2 compares the pair-graph laws themselves, which do separate them.
- Equality is tested by digests of exact distributions (24 hexadecimal characters of sha256), checked against a direct
  comparison on all ten pairs of five. That gate tests agreement where a pair is carried, not discrimination (at five every pair
  shares a pattern, the referee); discrimination is tested by the digest mutant (G3b) and by P2's separation of patterns.

## Reproduce

```sh
cd experiments/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph
../../../.venv/bin/python -B checks.py
cd ../../..
J=experiments/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph/job.py
.venv/bin/python -B scripts/longrun.py launch $J --out <dir1> --unit <u1> --workers 3 --case-mem 5G --param subset=heavy
.venv/bin/python -B scripts/longrun.py launch $J --out <dir2> --unit <u2> --workers 8 --case-mem 1500M --param subset=light
.venv/bin/python -B experiments/MEET-GROW-20261118-001B/MEET-GROW-20261118-001B-E001_pairgraph/merge.py <dir1> <dir2>
```

## Advisor

Consulted once before the freeze (Fable 5.2, no tools). It gave P1's probability and where it would fail, the twist as the
mechanism, the discriminator that became P4 (carried means state by state, not carried means averaging), and the remark that
different meeting patterns already differ at the start. Not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with its own exact engine and no digests:
confirmed with fixes, no Block. It recomputed P1 for every pair of presentations of five and six to n0 + 4 (9 of 9 carried, each
by both isomorphisms of the pattern), P3's counts (6,752 at five; 13,368, 13,364 and 16,272 at six) and the order control, and
found the digest method, `canonical_pattern` and the automorphism comparison correct. Folded in the same day, each logged in
`docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing.** "The meeting pattern grows on its own" said more than P1 and P4 show: the pair graph is not a process by itself
   (same pair graph, different next laws within one presentation from the third new distinction on). The finding is placement
   independence: "grows by the same law wherever it sits along the line". Corrected in the headline, the owner's-terms paragraph,
   A97, the intuition entry, the goals row, the objects row and `MEET-TWIST-20261118-001`'s proof.
2. **Not a block.** The G4 gate tests agreement on carried pairs only; the Limitations now say so.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: does the meeting pattern grow by one law wherever it sits | **Status:** Successful (refereed R1, confirmed with fixes) | Carried exactly for all 1,049 pairs of presentations of 5 to 9 distinctions, state by state through n0 + 3; 4 of 4 held |
| Local direction: the two layers of how knots meet | Continue | The pattern's growth is separate from the orders; the map between states is not yet known |
| Broader exploration: how knots meet as information | Searching | Other bases, knot kinds and rules untested (A99, A100) |
| Long-term goal: G16 Learning the rules behind what a system allows | Capability gained | The meeting pattern predicts the pairs' growth law exactly; the bracketing predicts the orders |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove that the meeting pattern grows by one law wherever it sits: construct the map of states (the advisor's twist) and show it carries KF3's options | 3/3 | 2/3 | Build the twist for one move of the marked side, check it maps options to options on every reached state of five and six → stop at a proof, or at the first state where no such map exists | Selected · started |
| 2 | Beyond lines: presentations of the 2 × 2 pattern and of branching trees, and redundant knots (A100's challenge) | 2/3 | 2/3 | Enumerate their fewest-knot presentations and rerun this test → stop when it fails or holds one size past | Alternative · deferred |
| 3 | The order layer past n0 + 3: what reading of the bracketing predicts the orders where its halves tie (from n0 = 8)? | 2/3 | 2/3 | Group the tied pairs by their same-way bits → stop at a reading that separates all of 9 or a counterexample | Alternative · deferred |

- **#1.** Payoff: it would make the separation of how knots meet from the states a theorem, the cleanest answer yet to A97's
  question for this growth. Concreteness: P4 says a state-by-state map exists through n0 + 3, and the advisor names a candidate;
  extending it through growth is the open step. Bound: one proof attempt with a computed check on five and six before writing.
- **#2.** Payoff: it would say whether the finding is about lines or about knots. Concreteness: the enumeration is new code.
- **#3.** Payoff: completes the picture of the orders. Concreteness: the tied pairs are listed in `MEET-ORDERS-20261118-001`'s
  results.

**Corrections:** none.

**Goals:** a G16 checkpoint (capability gained) and a G1 checkpoint (no demonstrated advance); no goal changed.

**Assumptions:** A97 under challenge, with this finding added; A99 and A100 gain this study among what rests on them; no new entry.

**Basket:** read; `MEET-ORDERS-20261118-001#1` taken by this epic.

## Final report as sent

Posted in the project thread at about 03:57 UTC on 18 November 2026, together with the fold-in of `MEET-ORDERS-20261118-001`'s
referee (the tables are those of the Position section above, with the directions shortened):

> **Second study done (referee pending): under KF3 the meeting pattern grows on its own.** Take any two presentations of a line
> whose knots form the same pattern, read as sets of distinctions with the line ignored. One renaming then carries the whole law of
> the grown co-knotted pairs from one to the other, after every new distinction. That held for all 1,049 such pairs (lines of 5 to
> 9) and also state by state, not just on average. Only the number of orders depends on where the pattern sits along the line. All
> 4 predictions held.
>
> Goals: G16 and G1 checkpoints. Assumptions: A97 under challenge with both findings; A100 gains its first challenge result.
