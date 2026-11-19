# Referee report REDUCE-BLOCKS-001-R1 (Lemma R read line by line; three realizations compared parent by parent)

**Verdict: confirmed. Lemma R and Corollary 1 hold. No Block. Two points, Not a block. Part of the random-start check is a stress
test pending (stopped at the owner's request).**

## The points asked

1. **Lemma R, step 3 (later rounds read only parents): correct.**
   - **Why.** A round-t junction holds one loose distinction from each parent and otherwise only fresh ones, so its neighbours are
     exactly its parents until the next round. Two of them have a common neighbour exactly when they share a parent. The next
     groups, demands, fresh counts and the structural implied test ("takes every loose distinction") are therefore functions of
     the parent incidence, and the induction closes.
   - **Checked on the referee's own engine.** In 603,307 live-junction checks, no junction's neighbours differed from its parents.
     In 79,038 rounds, the candidate pairs equalled the pairs sharing a parent.
2. **The hub realization's blocks are exactly the maximal blocks: correct.**
   - **Why.** No live knot touches a live knot, no connector holds two, and extra shares are dead to dead. So the sets
     N(w) ∩ live with two or more points are the hubs' blocks. The places argument, the padding to three and the connectivity
     all hold.
   - **Checked.** The study's `hub_realization` (the object under test) and the referee's own realization were both tested on every
     comparison below. Both have exactly X's maximal blocks and no other blocks, are connected, give every dead knot three places,
     and keep the open counts.
3. **The amendment for empty hub realizations: correct.** All 234 census arrangements with no live knot make nothing under the
   referee's engine, and `hub_realization` returns an empty start for exactly those.

## The referee's comparison (stronger than the study's)

The study compares per-round multisets of (parent count, fresh count). The referee names every junction by its round, its parents'
names and its fresh count, so equal signatures mean the same junctions with the same parents round by round. X was compared with
three realizations:
- **mine:** one hub per maximal block, hubs chained hub to hub;
- **theirs:** `hub_realization`;
- **random:** extra hubs on random sub-blocks, duplicate hubs, a live-to-live touch where it adds no block, and extra dead shares.

A **control** that changes the down-closure (a maximal block of three or more split into its sub-blocks) shows the test has power.

| Population | Compared | mine, theirs, random grow like X | Control differs |
| --- | ---: | ---: | ---: |
| Every touch-census arrangement, 6 rounds | 26,207 with live knots (+ 234 with none) | all | 6,631 of 9,757 |
| Random starts of 11, 12 and 14 knots within eight places (one past seven), 7 rounds | about 370 | all | most |
| EXPLOSIVE's explosive starts, stages 1–7 as starts (one past 6), 3 rounds | 59 | all, and each stage grows like its own continuation | most |

**Stress test pending.** The random cases at 6 to 10 and 13 knots were stopped by the job's memory cap, then all runs were stopped at
the owner's request. They can be rerun with `job_rb.py` with a larger per-case memory.

## Points for the owner (listed, not folded in)

1. **The machine check compares counts, not parents.** "Grow identically: the same junctions, with the same parents" is proved.
   H1–H3 test only multisets of (parent count, fresh count), which the advisor also flagged (its point 5). The referee's
   parent-by-parent comparison closes this. **Not a block.**
2. **H2 is filtered.** "No class filter" is described, but its sampler keeps only starts that do not stall. **Not a block.**

## How the work was split

- **The referee:**
  - read `proof.md`, `hublib.py`, `job.py`, `job_census.py`, the note and the advisor's answer;
  - wrote `job_rb.py`, with its own engine (EXPLOSIVE-R1), realizations, signatures and step-3 check.
- **Run as the object under test only:** `hublib.hub_realization`.
- **Where it ran.** Under `scripts/longrun.py`: `runs/referee-rb` and `runs/referee-rb2`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
