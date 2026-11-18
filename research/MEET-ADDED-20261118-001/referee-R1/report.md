# Referee report MEET-ADDED-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The numbers stand.** The referee's own engine and its own isomorphism classes (VF2, not `canon_struct`) reproduce every share
  to six digits:
  - the states with the added knots equal the all-named share at five (k ≤ 4) and six (k ≤ 3);
  - at seven, k = 3, they are 0.791456 against 0.791576.
- **The seven shortfall is real, not an artefact.** 44 classes of (states + added knots) merge named bases whose laws over bare
  bracketings differ, and VF2 confirms the merged structures are isomorphic. The example is the same three fills grown in two orders.
- **The scope is narrower than the wording.** The reader is told which knots growth added, and that is a piece of history.
  - **Given every knot without that label,** states and knots together carry the whole nesting at every k, even k = 0, because the
    starting knots are the presentation.
  - **The added knots alone, with middles and no states,** carry 0 to 0.41.
  - **So the finding is about states plus added knots.** It is not "the knots, not the distances".

## What holds

- **`exact_with_knots` (the owner's point 1).** Keying by (states, added knots) refines KF3's (states, pairs) state. The
  transitions read only the pairs, G = starting pairs ∪ the added knots' pairs, so the law is KF3's. The referee's own run, keyed
  the same way with its MEET-ORDERS-R1 options, reproduces it.
- **`canon_struct` (the owner's point 2).**
  - **How it works.** Exhaustive individualisation–refinement on the counts, pair and triple incidences and middle–end relations. Its
    certificate relabels the states, pairs, triples and knots.
  - **The check.** The referee read the same structures independently, as one coloured graph each: the distinctions joined by their
    counts, and one node per knot joined to its ends and its middle. It compared them by VF2. The shares agree to six digits, so the
    canonical forms agree in effect.
- **A fresh recomputation (the owner's point 4; `referee_added.py`).**

  | n0, k | U (states) | K1 (states + added knots) | T1 (no middles) | N (all named) | ADDK (added knots alone) | ALL (states + every knot, unlabelled) |
  | --- | --- | --- | --- | --- | --- | --- |
  | 5, 2 | 0.6035 | 1.0 | 1.0 | 1.0 | 0.043 | 1.0 |
  | 5, 3 | 0.3948 | 1.0 | 1.0 | 1.0 | 0.281 | 1.0 |
  | 5, 4 | 0.2230 | 1.0 | 1.0 | 1.0 | 0.408 | 1.0 |
  | 6, 2 | 0.6484 | 0.8313 | 0.8313 | 0.8313 | 0.019 | 1.0 |
  | 6, 3 | 0.6341 | 0.9113 | 0.9113 | 0.9113 | 0.124 | 1.0 |
  | 7, 2 | — | 0.682534 | — | 0.682534 | — | — |
  | 7, 3 | — | 0.791456 | — | 0.791576 | — | — |

  - Every U, K1, T1 and N value equals the study's results.json. ALL is 1.0 at k = 0 and 1 too.
  - The added pairs alone (the study's P0) were the referee's own MEET-HIST preview (0 to 0.05).

## 1. The seven shortfall (the owner's least sure; real)

- **Where it shows.** At seven, k = 3, 2,069 classes of (states + added knots) hold more than one named base. In 44 of them, the
  named bases' laws over bare bracketings differ. Merging them costs the 0.00012 share.
- **An example, VF2-isomorphic as (states + added knots):**
  - fills on {0, 1, 6}, {1, 2, 6} and {4, 5, 6}, in that order, with bare-bracketing law ½, ½;
  - the same three fills in the order {1, 2, 6}, {4, 5, 6}, {0, 1, 6}, with law 13/22, 9/22.

  The two differ only in the order of growth.
- **What it shows.** It is not a canonical-form artefact. A wrong canonical form could only split classes and raise the share; it
  cannot lower it. The states and added knots do not fix the order of growth, and at seven that order carries a sliver of the
  nesting.
- **The advisor's guess** was that an old distinction might pass for a late arrival. In this example the cause is different: three
  new distinctions exchanged.

## 2. Does the reading smuggle in history? (the coordinator's question; Narrowing)

- **Yes, one piece.** K1 and T1 hand the reader the added knots as a separate structure, which is knowing which knots growth made.
  That is history, as "the order of growth" is.
- **The coordinator's arm (ALL):** the states with every knot, starting and added, not told apart. Its share is 1.0 at every level,
  k = 0 included. Even the knots alone, with no states (ALLK), give 1.0.
  - The reason is that the starting knots are the presentation, and the knots up to renaming show how they nest.
  - That is MEET-HIST's "the knots record it directly", and it is trivial.
- **What carries the nesting, and what does not.**

  | Reading | Carries the nesting? |
  | --- | --- |
  | The added knots alone, no states (ADDK) | No: 0 to 0.41 at five, 0 to 0.12 at six |
  | The states alone (U) | Part: 0.22 to 0.65 |
  | States plus the added knots, labelled as added (K1) | What the full names give |
  | States plus all knots, unlabelled (ALL) | Everything, from the start |

- **A fair sentence.** "Given the grown states and told which knots the growth added, a reader recovers what the full names give
  about the nesting: exactly at five and six, within 0.0002 at seven. Neither the states nor the added knots suffice alone. And
  knowing which knots were added is itself history."
- **The reading for A97.** "The knots carry it; distances do not" is not fair. It is states plus added knots, with the added-knot
  label given. The note's own table shows that the added knots alone carry almost none of it.

## 3. Prior work (the owner's point 5)

- **Known.** The tools are standard information theory and graph isomorphism.
- **Specific to the program.** Nothing outside applies.

## Fixes for the thread (listed for the owner, not folded in)

1. **The A97 line, the owner's terms and the headline.** Replace "the knots carry it, not the distances" with "the states and the
   added knots together carry it, given which knots were added. Neither alone does." Note that the added/starting label is history,
   and that all knots unlabelled carry the nesting trivially. **Narrowing.**
2. **The seven shortfall.** It is real: the order of three fills, 44 classes. Give the example. **Not a block.**
3. **The arms.** Add ALL (1.0 everywhere) and ADDK (0 to 0.41) to frame the result. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, `job.py` (`exact_with_knots`, `canon_struct`, the arms) and the results;
  - wrote its own (states, added knots) KF3 run, VF2 classes of coloured knot–table graphs, the shares for seven arms, and the
    shortfall witness search (`referee_added.py`), on its MEET-ORDERS-R1 and MEET-DIST-R1 code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_added.py`.**
- **`referee_added_5_4.json`, `_6_3.json` and `_7_3.json`.** The last holds the witnesses, with arms K1 and N only.

Reproduce, from `research/MEET-ADDED-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_added.py 5 4 > referee_added_5_4.json
../../../.venv/bin/python -B referee_added.py 6 3 > referee_added_6_3.json
../../../.venv/bin/python -B referee_added.py 7 3 K1,N > referee_added_7_3.json
```
