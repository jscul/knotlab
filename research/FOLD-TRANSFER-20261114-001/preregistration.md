# Reusing a local rule when the next task hides what it reads

Owner-assigned ticket `FOLD-TRANSFER-20261114-001` in learning, serving G15 and G16. Frozen on 2026-11-14 before implementing or running this probe. The motivating question is whether logical compression can reduce the number of examples needed on a later problem.

## Question and interface

Recover the actual laws found at the first parity target in the four original bare-pattern runs with seeds 9000–9003. Freeze them. At each copy, distinctions 0, 1 and 4 are inputs. Either distinction 5 or 6 is read. The two possible output places and all copy boundaries are supplied. Enumerate each local law's allowed states and retain what can be read at those places for every input. Abort on a failed replay or an ambiguous or missing read. Only the original search uses the source labels. Charge the source search, the enumeration, and the later search separately.

Join two, three or four distinct copies in source-seed order. Each copy after the first shares its first input by identity with its predecessor's selected read. Each of the other inputs remains independent. The last selected read is the output. This gives 5, 7 and 9 external inputs. All `2^m` choices at length `m` are tasks. In each task which choices were used is hidden. The only feedback to the downstream learner is an output bit on a requested input. Candidate predictions are made from the local tables, before any target answers. Identical prediction functions count as one hypothesis.

## Prior work in the program

`python3 -B scripts/track.py objects "learned parity" --until 2026-11-14 --exclude FOLD-TRANSFER-20261114-001`

`python3 -B scripts/track.py objects "modular transfer learning" --until 2026-11-14 --exclude FOLD-TRANSFER-20261114-001`

`python3 -B scripts/track.py objects "shared distinction" --until 2026-11-14 --exclude FOLD-TRANSFER-20261114-001`

- `LEARN-PARITY-20261111-001` supplies the source procedure and archived first stops. `SEARCH-AUDIT-20261112-001` qualifies their interpretation. The examples served as a stopping test, with no demonstrated search advantage over blind sampling. `CLAMP-LEARN-20261112-001` is a related negative result about steering search.
- `SHARED-COUNT-20261111-001` supplies the serial identity join and its whole-pattern training comparison. Its own report explicitly left separate reuse open. `HOLD-COUNT-20261111-001` supplies the two candidate read places from its exact full-adder observation. The actual found laws may encode other input or output signs. Read them afresh.
- `PARITY-FIVE-20261111-001` previously tested other ways of joining copies. `PARITY-SURVIVE-20261112-001` measures compatibility of parity placements in a different family. `BONDS-AND-COUNT-20261112-001` and `ADDR-KNOTS-20261113-001` concern counts, addresses or bonds at other interfaces. `LOOP-LOCK-20261112-001` and `ENDLESS-BLOCK-20261112-001` concern different task families. None gives the hidden-read label counts measured here.

## Prior work outside the program

Part 1 of 3Blue1Brown's video motivates coding length through information and entropy. This experiment uses exact finite functions and a declared uniform distribution only for the majority-vote control. Reusable program abstractions were already studied by Dechter et al. (2013) and DreamCoder. Finite identification by querying labels is classical (Angluin, 1988). Here the new question is the behavior of a specified family from Lesson 4.7 under blind selection of the read places. [Video](https://www.youtube.com/watch?v=l6DKRf-fAAM) · [Modular concept discovery](https://ijcai.org/proceedings/2013/196) · [DreamCoder](https://dspace.mit.edu/entities/publication/86d768ab-558f-4fb1-b92e-9288de643ccb) · [Queries and concept learning](https://doi.org/10.1007/BF00116828)

## Frozen test

1. Replay the four source runs to their first held rule, check the archived first-target row including the disturbance, and retain the exact sign vectors.
2. Exhaust all external inputs and both possible output bits against a solver on the full signed constraints for each joined task. Candidate inference gets only the label for its chosen input. Other answers are reserved for scoring. At each query choose an input splitting the remaining distinct functions as evenly as possible, with the first input in binary order breaking ties. Record the transcript, candidate counts, exact held-out errors, and the binary information lower bound on worst-case query depth.
3. Compare against plain enumeration of complete candidate truth tables with the same information and query policy. It should match. For the known all-5 wiring, compare also with ordinary Boolean parity. Replacing exact local relations at supplied boundaries is valid by existential elimination. Neither this fact nor a match with ordinary lookup earns an algorithmic novelty claim.
4. Test information loss. For every source, find the smallest number of input classes that retain each read alone and the joint read. Find an explicit pair of inputs indistinguishable at 5 but distinguishable at 6, if it exists, and score the best prediction of 6 from 5 under uniform input. Split a shared identity to test the need for a real join. Flip one unqueried target answer to test whether the observed transcript certifies a task outside the supplied family.

Success on this panel means zero held-out disagreements and fewer target labels than all input assignments. A disagreement stops that claim. Report separately whether the equal-information baseline ties it and whether a single retained bit loses information. Even a perfect result leaves automatic discovery of the copy boundaries, acquiring a library from unrelated tasks, and any effect on AI research speed open.
