# Why the meeting pattern grows on its own: moving the ends' pair: pre-registration

Epic `MEET-TWIST-20261118-001` (`MEET-GROW-20261118-001#1`; goal G16; tests A97), 18 November 2026, by Claude, on the
coordinator's go-ahead. Frozen before the run. The canonical K1–K3 test is unchanged.

## The question

`MEET-GROW-20261118-001` found by computation that KF3 grows the co-knotted pairs by the same law from every presentation of a line
with one meeting pattern, state by state. What map of states does it, and does it carry KF3's options for every n?

## In standard terms

A triangulated polygon with two marked sides one step apart; two Markov chains on (allowed split systems, co-knotted pairs); an
explicit coupling (a GF(2)-affine change of state coordinates with a renaming) under which their transition structures agree,
until the first step that adds a state.

## Prior work in the program

`python3 -B scripts/track.py objects "pair graph grown by KF3 from presentations with the same meeting pattern" --until 2026-11-18 --exclude MEET-TWIST-20261118-001`

`python3 -B scripts/track.py objects "presentations of a line by betweenness knots, bracketings, meeting pattern" --until 2026-11-18 --exclude MEET-TWIST-20261118-001`

- `MEET-GROW-20261118-001`: same object; the computed fact this study proves (its P1, P3, P4).
- `MEET-ORDERS-20261118-001`: the parity form (odd sets), Lemma 0 and Lemma C used here.
- `OVERLAP-READ-20261111-001`: unrelated (not-all-equal patterns read back).
- `STATE-RULES-20261117-001`: KF3 itself (a relative).

## Prior work outside the program

The advisor's twist (moving the marked side past a distinction v with neighbours u, w substitutes the parity u ⊕ v ⊕ w for v). The
unique Hamiltonian cycle of a maximal outerplanar graph (classical). Nothing found for KF3.

## Exploration before this freeze (disclosed)

The map was found in the scratchpad: substituting the moved distinction alone (new distinctions kept as columns) fails from the
first new distinction; keeping every distinction's odd set and moving the mark carries the joint law of (states, pairs) exactly for
every bracketing of five to n0 + 4 and of six to n0 + 3. The frozen code passed the smoke test on all five bracketings of five to
n0 + 4 and two of six to n0 + 4.

## Ticket A: the proof (written before this freeze)

`proofs/MEET-TWIST-20261118-001A/MEET-TWIST-20261118-001A-P001_mark_move/proof.md`: Lemma 1 (moving the mark one step flips the
parity of an even set exactly when it holds the passed distinction), Lemma 2 (knot by knot, with a role change, the same pinned
steps), Theorem 2 (the two chains have the same law under the coupling until a step adds a state) and its corollary for every pair
of presentations with one meeting pattern. Checked by the advisor (holds with fixes, folded in).

## Ticket B: computations

Code: `job.py` and `checks.py` with `melib.py` (MEET-ORDERS-20261118-001B's engine, unchanged) in
`experiments/MEET-TWIST-20261118-001B/MEET-TWIST-20261118-001B-E001_knotmap/`. 5 gate checks pass (the engine's hash; the twist maps
the line's states onto themselves; moved bracketings are bracketings; a mutant without role changes fails on 18 states of five;
the map passes on five to depth 2).

Cases: every bracketing of 5 and 6 (to n0 + 4), 7 (to n0 + 4), 8 and 9 (to n0 + 3), against its one-step move: 622 cases.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | The 5 gate checks pass | any fails |
| T1 | At every reached state below the depth, KF3's options map knot by knot by Lemma 2's table onto the moved presentation's options at the image state (as multisets), both at zero cost | one state fails |
| T2 | At every level the joint labelled law of (states, pairs) is carried by the twist | one level fails |
| T3 | No reached state in these ranges has had a state added (the zero-cost range holds throughout) | a state is added (then T1 and T2 are scored up to it) |

**What would count against the proof.** A failure of T1 at a zero-cost state is a counterexample to Lemma 2 or Theorem 2.

## Runs and stop rule

The shared runner, 622 cases, 12 workers at 1 GB, registered as MEET-TWIST-B1; expected under half an hour. The study stops at the
read-out: a proof with its check, or the first failing state.

**Advisor.** Consulted once before the freeze, on the proof (holds with fixes: the inverse's witness step, nonempty differences
from "no copies", irredundancy judged on states, the parity of one odd set justified, the corollary's reflection and scope, and
"the same law under the coupling").
