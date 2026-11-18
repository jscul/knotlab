# Hiding the knots at seven and eight distinctions

Ticket `ERASE-SEPARATELY-20261117-001` serves G1 and G16. This exploratory envelope was fixed before reading the nine- or ten-distinction outcomes. The four cut scores had already been computed.

Two presentations of the same 12 allowed six-distinction states use four knots apiece. One distinction belongs to all four in one start. No distinction belongs to all four in the other. Use the published knot-local fewest-states rule for one step in the seven-cut experiment, or two in the eight-cut experiment. Discard the entire knot list. From then on the rule has only the current states. Each observer sees the final states with every distinction anonymous, including the ones added after erasure.

## In standard terms

Compare two probability laws on isomorphism classes of finite binary relations. The signed equivalence also permits independently swapping the two values at each coordinate. The pre-cut transition is identical across all arms. The ordinary post-cut atom forbids an assignment and its complement where exactly the middle differs. Its orbit under local swaps consists of all four ways to forbid an antipodal pair, including 000 and 111. Use that whole orbit in the signed arm so the post-cut law is defined on precisely what survives erasure.

Minimize the number of allowed joint states over conservative extensions by one distinction using up to three ternary constraints. Exclude a fully free new distinction and any renamed copy of an old one. Give each distinct minimizing extension the same weight before forgetting which coordinate was added. This matches the weighting of the earlier states-only study. In signed coordinates a flip of the fresh distinction pairs the extensions with equal weight. Parent automorphisms can have different numbers of extensions in their orbits, so weighting is done before grouping final outcomes into classes.

## Observations and checks

Use equal prior probabilities for the two starts. Record the optimal probability of guessing the start, at nine and at ten, from the whole state table. Also pool the same probabilities by the histogram that counts how many pairs of allowed rows disagree on exactly *j* distinctions. This histogram requires neither coordinate names nor an alignment of values. An independent calculation of the scores uses the saved representatives and their two exact probabilities.

Before the cut, one and two local moves respectively give recognition of 7/8 and 249/280 with common values or 1/2 and 26/35 under independent swaps. At seven the signed input laws coincide. Applying the same state-only transition to identical distributions keeps them identical. At eight, any fully anonymous continuation has recognition at most 26/35. The finite run decides whether it remains above chance. The standard contraction for total variation follows directly by summing the triangle inequality after each stochastic step. [Gerold Alsmeyer, Lemma A.3.7, *Renewal, Recurrence and Regeneration*](https://www.uni-muenster.de/Stochastik/alsmeyer/Skripten/rt_book.pdf)

The competing label conventions and the two cutoffs are part of the question. Closing betweenness under independent value swaps changes the available attachments. A comparison between the shared-value and fully anonymous runs also reflects that change. Simply hiding the value names at the last reading allows growth to keep using their alignment. The advisor independently flagged the weighting, old-column copies and the need to erase the fresh-column mark. Check those against a renamed control and the frozen source rule. Stop at ten for these two starts.

## Prior work in the program

`python3 -B scripts/track.py objects "matched starts" --until 2026-11-17 --exclude ERASE-SEPARATELY-20261117-001`

`python3 -B scripts/track.py objects "distribution over classes of states" --until 2026-11-17 --exclude ERASE-SEPARATELY-20261117-001`

`python3 -B scripts/track.py objects "fan and non-fan" --until 2026-11-17 --exclude ERASE-SEPARATELY-20261117-001`

- `STATE-RULES-20261117-001` defines the two starts, the knot-local growth and the original states-only transition. Its closed experiment B and referee supply the comparison.
- `KNOT-CAP-20261117-001` preregistered the shared-value eight-cut arm to eleven in commit `3e41d8f112`. That arm is excluded from this computation. The seven-cut shared-value comparison and both signed interventions are the new calculations.
- `CARRY-FIFTH-20261117-001` treated common and independent value names in the four-to-five attachment test.
- The other indexed hits have different populations. `CLAMP-LEARN-20261112-001` varies the start of a learning walk. `ACROSS-FOLD-20261112-001`, `ADDR-KNOTS-20261113-001`, and `BOND-BALLS-20261111-001` measure bonds or addresses. `SIGNED-KNOT-OVERLAP-20261114-001` and `SEQUENTIAL-WALL-20261116-001` measure decision and circuit costs. `NAE-SURFACE-20261111-001` treats six-distinction regular patterns.
