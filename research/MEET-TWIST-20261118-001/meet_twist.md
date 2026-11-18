# Why the meeting pattern grows the same wherever it sits: moving the ends' pair

Epic `MEET-TWIST-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes the selected direction of
`MEET-GROW-20261118-001`. Goal G16; tests A97. Refereed: report [R1](referee-R1/report.md), confirmed, no Block, one wording fix folded
in on 18 November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `0aabfbd2c` at about 04:00 UTC on 18 November. The
  check (long run MEET-TWIST-B1, 622 cases on the shared runner) ran from 04:00 to 04:14 UTC, 622 of 622 cases ok.
- Proof: [proof.md](../../proofs/MEET-TWIST-20261118-001A/MEET-TWIST-20261118-001A-P001_mark_move/proof.md). After the freeze and
  before the read-out, Theorem 2's name and one sentence were narrowed to follow `MEET-GROW-20261118-001`'s referee ("grows by the
  same law wherever it sits", not "on its own"); nothing in the lemmas changed.
- Code: [job.py, checks.py, merge.py and melib.py](../../experiments/MEET-TWIST-20261118-001B/MEET-TWIST-20261118-001B-E001_knotmap/).
- Results: [results.json](../../artifacts/MEET-TWIST-20261118-001B/MEET-TWIST-20261118-001B-E001_knotmap/results.json).

## The answer

- **Moving the ends' pair carries KF3 exactly** (proved, Theorem 2). Read a presentation of a line as a bracketing of the cycle of
  its distinctions, cut at the ends' pair. While no new distinction has added a state, every distinction is the parity of an odd
  set of the line's distinctions. Keep every odd set and move the ends' pair one step round the cycle: under this map KF3's options
  correspond knot by knot. A knot may change its role (a knot with the new distinction between the pair's two distinctions becomes
  one with a distinction of the pair between, or back), but it pins exactly the same states, adds the same co-knotted pairs and
  makes the same new odd set (Lemma 2). So the two growths have the same law under that map until the first step that adds a
  state, which comes at the same point in both.
- **Every two presentations with one meeting pattern are linked this way** (proved). Their knots are one bracketing of the cycle
  with the ends' pair at different steps, since the co-knotted pairs have one Hamiltonian cycle (the literature's word; classical).
  So `MEET-GROW-20261118-001`'s computed findings, one law for the co-knotted pairs wherever the pattern sits (P1), the same
  labelled counts (P3) and the same option profiles (P4), are now proved for every line length, through the steps before the first added state (a range that ends by 2^(n0 − 1) distinctions: while no state is added every distinction is one of the 2^(n0 − 1) odd sets of the line's distinctions; the referee).
- **What the ends' pair still decides is the number of orders.** The same odd sets read against a different ends' pair have
  different middles (the middle of a fill is the one of its three distinctions that does not bound the run of the cycle between them that holds
  the ends' pair), and
  `MEET-ORDERS-20261118-001`'s Lemma C reads the orders from the middles. The states correspond by their index, not by renaming, so
  the values differ.
- **The frozen check** (T1 to T3, all held): at all 74,972 reached states of every bracketing of 5 to 9 distinctions, to n0 + 4
  for five to seven and n0 + 3 for eight and nine, the options mapped knot by knot by Lemma 2's table equal the moved presentation's
  options, and the joint law of (states, pairs) is carried at all 2,549 levels. No state was added in these ranges.

**In the owner's terms.**
- The knots of a line, read as a ring of distinctions, do not care where the line's two ends are cut. Moving the cut one step
  changes which distinction each knot holds between the other two, but every knot then rules out the same states as before, so
  the growth makes the same choices with the same chances.
- What the cut does decide is how many orders the grown knots make: the same knots, cut at a different place, line up into a
  different number of orders.
- The pairs still do not grow by themselves (the states steer them); what is proved is that where the ends sit does not matter to
  how they grow.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 5 gate checks pass | held | including the mutant without role changes, which fails on 18 states of five |
| T1 | Options carried knot by knot at every reached state below the depth | held | 74,972 states (1,220; 6,118; 28,364; 7,524; 31,746 for n0 = 5 to 9), none failing |
| T2 | Joint law of (states, pairs) carried at every level | held | 2,549 of 2,549 levels |
| T3 | No state added in these ranges | held | none |

3 of 3 held (and the gates). The check runs the proof's Lemma 2 table directly, so it would have found a wrong row at the first
state where it mattered; the mutant shows the role changes are needed.

## What the knot picture explained

- **Why the roles must change.** Moving the ends' pair past a distinction w flips which pairs agree and which disagree, exactly for
  the pairs whose odd sets differ at w (Lemma 1). A knot that pinned the states where its pair agrees must, after the move, pin the
  same states, which are now the states where the pair disagrees: so it becomes a knot with one of the pair between.
- **Why the number of orders is not carried.** The orders are read along the line, and the line is the cycle cut at the ends' pair.

Known mathematics, labelled: polygon triangulations, the unique Hamiltonian cycle of a maximal outerplanar graph, parity over
GF(2). Local: Lemmas 1 and 2 and Theorem 2 for KF3.

## What it means for A97 and the goals

- **A97** stays under challenge. How the knots meet (the bracketing) is information the states lack; its growth under KF3 is now
  proved independent of where the line's ends sit, while the number of orders depends on it. Whether this information is a
  distance is open, and is the next direction.
- **G16:** capability gained. An exact symmetry of the growth law, proved for every line length through the steps before the first
  added state.

## Limitations

- Until the first new distinction that adds a state. On lines that range lasted through every case run (to n0 + 4).
- Fewest-knot presentations and KF3 only (A99, A100).
- The proof is by hand, with the advisor's review and the frozen check; the referee is pending.

## Reproduce

```sh
cd experiments/MEET-TWIST-20261118-001B/MEET-TWIST-20261118-001B-E001_knotmap
../../../.venv/bin/python -B checks.py
cd ../../..
.venv/bin/python -B scripts/longrun.py launch experiments/MEET-TWIST-20261118-001B/MEET-TWIST-20261118-001B-E001_knotmap/job.py \
  --out <dir> --unit <name> --workers 12 --case-mem 1G
.venv/bin/python -B experiments/MEET-TWIST-20261118-001B/MEET-TWIST-20261118-001B-E001_knotmap/merge.py <dir>
```

## Advisor

Consulted once, on the written proof before the freeze: holds with fixes (the inverse's witness step, nonempty differences from
"no copies", irredundancy judged on states, the parity of one odd set justified, the corollary's reflection and scope, and "the
same law under the coupling"), all folded in. The twist itself was its suggestion in `MEET-GROW-20261118-001`; the exact form
(keep every odd set) was found by computation.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh code: confirmed, no Block.
- Lemma 2's five rows and the inverse hold (checked by hand), as do the parity of one odd set for every zero-cost option, Lemma 1
  at h = g, reflections (a run becomes its complement, odd sets unchanged) and KF3's irredundancy being judged on states.
- A fresh test without Lemma 2's table: the exact joint law of (odd sets, co-knotted pairs) before and after one move of the ends'
  pair is carried at 263 of 263 levels for every bracketing of five and six (to n0 + 4) and seven (to n0 + 3), with no state added;
  the move changes the two-order chance in 4 of 5, 10 of 14 and 24 of 42 bracketings.
- Prior work, cited once: the dihedral symmetry of triangulations (moving the marked side re-roots the binary tree) and the
  outerplanar Hamiltonian cycle are classical. Nothing was found on a growth rule that is invariant under the move while its
  number of orders is not, which is what this study adds.

Folded in the same day (logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`):
1. **Not a block** (wording). "For every n" is earned only as "for every line length, through the steps before the first added
   state". That range is finite on each line: while no state is added every distinction is one of the 2^(n0 − 1) odd sets, so a
   state is added by 2^(n0 − 1) distinctions (from the line of five one bracketing runs with no added state through n = 10). After a
   state is added the theorem says nothing. Fixed in the note, the proof, the intuition entry, the goals row, A97 and the objects
   row.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the map of states behind placement independence | **Status:** Successful (refereed R1, confirmed) | Constructed and proved for every line length, before the first added state; the frozen check passed at 74,972 states |
| Local direction: the two layers of how knots meet | Practically exhausted for this rule | Growth's independence of the ends is proved; the orders' dependence is explained by Lemma C |
| Broader exploration: is how knots meet a distance (A97) | Unmapped | The bracketing is outside the line's states; whether grown states' disagreement counts carry it is untested |
| Long-term goal: G16 Learning the rules behind what a system allows | Capability gained | An exact symmetry of the growth law, proved |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Is the bracketing a distance? After k new distinctions, does the table of disagreement counts of the grown base determine the bare bracketing (in law), and from which k? | 3/3 | 2/3 | Exact laws of the disagreement tables (up to renaming) from every presentation of 5 to 8, k = 1 to 4 → stop at the first k where the tables separate the bare bracketings, or a proof that they never do | Selected · awaiting go-ahead |
| 2 | Past the first added state: does the coupling extend once KF3 must add states (the cube full)? | 2/3 | 2/3 | Run lines to the first costly step and test the law there → stop at an extension or the first failing state | Alternative · deferred |
| 3 | Beyond lines and fewest knots: presentations of the 2 × 2 pattern and of branching trees, and redundant knots (A100) | 2/3 | 2/3 | Enumerate and rerun MEET-GROW's test → stop when it fails or holds one size past | Alternative · deferred |

- **#1.** Payoff: it asks A97's question directly: the information that changes the number of orders is not in the line's
  states, but the grown states carry its trace, and the test is whether that trace is a distance (the disagreement count, the
  program's reading). Concreteness: the engine computes exact laws; the risk is that the answer depends on the reading of "a
  distance" (A98). Awaiting the coordinator, since this thread has run three studies in a row.
- **#2.** Payoff: completes the theorem's range. Concreteness: the costly steps are known to come when the cube is full.
- **#3.** Payoff: whether the findings are about lines or about knots. Concreteness: new enumeration code.

**Corrections:** none in this study (the narrowing of `MEET-GROW-20261118-001`'s wording was logged with that study's referee
fold-in and carried into Theorem 2's name).

**Goals:** a G16 checkpoint (capability gained); no goal changed. Direction #1, a 3/3 direction awaiting a go-ahead, is filed as
sub-goal B198.

**Assumptions:** A97 under challenge, with this finding added; A99 and A100 gain this study among what rests on them; no new entry.

**Basket:** read; `MEET-GROW-20261118-001#1` taken by this epic.

## Final report as sent

Posted in the project thread at about 04:18 UTC on 18 November 2026 (the tables are those of the Position section above, with the
directions shortened):

> **Third study done (referee pending): why the meeting pattern grows the same wherever it sits is now proved.** Read a
> presentation's knots as a ring of distinctions cut at the line's two ends. Move the cut one step and keep each distinction's odd
> set. Some knots then change which distinction they hold between the other two, but each still rules out exactly the same states.
> So KF3's choices correspond one for one, with the same chances. This holds for every size, until a step adds a state. The cut
> decides only how many orders the grown knots line up into. The frozen check passed at all 74,972 reached states of every
> presentation of 5 to 9 distinctions (3 of 3 predictions).
>
> Corrections: none new. Goals: G16 checkpoint. Assumptions: A97 under challenge, with the placement independence proved.
