# Referee report EXPLOSIVE-001-R1 (read under A110: what a sample of this kind shows)

**Verdict: the sample's findings stand, with three Narrowings of wording and one strengthening. No Block.**
- **The smallest explosive start closes at round 23.** The referee's own engine reproduces it exactly.
- **The filled reading is better than X1's tally says.** Three of X1's 29 "failures" are artefacts of the horizon, where the reading
  was right, including the one non-overlapping miss.
- **What does not stand:**
  - "explosive" means a jump in the counts seen before a stop, not growth without bound;
  - "none within five places" is a sampled statement with a horizon;
  - "the explosive kind has its own regularity" rests on one case of 16.

## The points asked

- **The filled reading's rays come from the true round-1 demand: correct.** Not a block.
  - `filllib.structure` takes d_k from the program's round-1 groups, a group of three counting once, and rays s_k · R(open_k).
  - The pieces come from the incidence graph, with b₁ over GF(2) after a cell is glued on each cycle of three blocks.
  - The referee's own reading uses its own groups (maximal cliques of the candidate graph with no common neighbour, plus
    uncovered pairs), its own cells and its own GF(2) rank. It equals the study's reading on **all 3,200 starts** of the run.
- **The class rule is exclusive, and the child limits are as stated.**
  - **The rule.** The order (closes, dimension, explosive, exponential-like, undecided) makes it exclusive. The child's 2.5 GB and
    30 s are applied as written, and a stopped child keeps its rounds.
  - **But the order lets "explosive" take a start that closes after the horizon.** "Explosive" means "some ratio ≥ 3 from round 4
    on, before the growth ended or was stopped".
- **The smallest explosive start closes at round 23: confirmed.** The referee's engine, with groups found as maximal cliques (it
  reaches the 309-parent group), gives exactly the study's counts and largest groups:
  - counts 6, 8, 12, 15, 15, 14, 14, 15, 9, 19, 26, 31, 67, 322, 9, 36, 84, 126, 126, 84, 36, 9, 1, 0;
  - largest groups 1, 3, 3, 4, 4, 5, 5, 6, 10, 4, 5, 6, 15, 52, 309, 2, 3, …, 9.

  The burst's counts are C(9, k) with largest groups of k, for k = 2 to 9. The referee did not list every parent set, so "join in
  every way exactly once" is supported by the counts and the group sizes, not checked set by set.

## The points the coordinator added

- **Is "explosive" a property of the growth or of the limits? Of the counts seen before a stop. Narrowing.**
  - The run's 16 explosive cap7 starts are the ones with a ×3 jump. 15 were stopped by the child's limits and one was alive at round
    20.
  - That one, the smallest, **closes at round 23**. Its filled reading said "closes".
  - The referee regrew all 21 explosive starts (16 cap7 and 5 reference) with its own engine to round 40, 150,000 junctions, 4.5 GB
    or 240 s. Every count agrees with the study's on common rounds. Apart from the smallest, every one is again stopped, by memory or
    time, at rounds 5 to 12.
  - So "16 of 1,000 are explosive" means 16 jumped. Whether any grows without bound is unread, as the note's Limitations say. The
    headline should not read the label as unbounded growth.
- **Were starts called polynomial only because rounds were too few? Not in the referee's sample.**
  - It regrew 346 decided starts (one in eight by hash, from every population) to round 40 or 30,000 junctions.
  - Its class at 20 rounds equals the study's on all 346, and at 40 rounds every class is unchanged.
- **"None within five places" is sampled, with a horizon. Narrowing.**
  - It is 0 of 2,191 sampled starts within 20 rounds or 6,000 junctions: 1,717 fresh and 474 census, under these two weightings.
  - "Within five places it never occurs" should say so. With zero found, the 95% upper bound is about 0.14% of such starts under
    this weighting.
  - The referee's horizon check found no class change from 20 to 40 rounds in its sample, so the horizon is not a known problem.
  - "Rare" for five places follows only as that one-sided bound. 1.6% within seven places is a sampled frequency.
- **"The explosive kind has its own regularity" is earned for one case. Narrowing.** Only the smallest of the 16 was followed to its
  end, and post hoc. The other 15 are unread. The headline and the final report state the regularity as the kind's. They should
  state it as the smallest case's: one merge, a binomial burst, then closing.
- **The one non-overlapping miss (775 of 776) is not a miss.**
  - Its counts' second differences are 44 on the last five rounds before the 6,000-junction cap at round 13. That is quadratic
    per-round growth, three dimensions, as the filled reading says. The rule needs six vanishing third differences and had four.
  - The referee's engine grows it to round 31 and reads dimension 3.
  - Likewise, one overlapping X1 "failure" (sizes 5, 6, 4, 7, 6, 6, 4), read as exponential-like at the cap, is two-dimensional to
    round 40, as the reading says.
  - With the smallest explosive start, read "closes", that makes **at least 3 of X1's 29 failures horizon artefacts**, where the
    filled reading was right. So the reading holds on **776 of 776** non-overlapping starts within seven places. **Strengthening;
    Not a block.**
- **"Overlap drives it" is a necessary condition seen in the sample, not a cause. Narrowing of wording.**
  - Within seven places, 117 starts have groups of three sharing a knot and a block together with a seven-place knot. 16 are
    explosive, 35 undecided, 17 exponential-like, and the rest polynomial or closing.
  - So "every explosive start has overlap and a seven-place knot" is right, and "overlap drives it" outruns it.

## Points for the owner (listed, not folded in)

1. "16 of 1,000 are explosive" should say "show a ×3 jump in their counts before the run stopped". The smallest closes at round 23.
2. "Within five places it never occurs" should say "none in 2,191 sampled starts, to round 20 or 6,000 junctions".
3. "The explosive kind has its own regularity" should say "the smallest explosive start has one", until the other 15 are read.
4. X1's failure count includes at least three horizon artefacts. The non-overlapping stratum is 776 of 776, and "28 of 29 failures
   overlap" overstates the filled reading's failures.
5. "Overlap drives it" should say "every explosive start has overlap (16 of the 117 overlapping seven-place starts are explosive)".

All are **Not a block**. The direction (#1, merge and burst) is the right test of points 1 and 3.

## How the work was split

- **The referee:**
  - read `explosive.md`, the pre-registration, `filllib.py`, `job.py`, `merge.py` and `posthoc_smallest.py`;
  - wrote `job_expl.py`, with its own engine and maximal-clique groups, its own filled reading, and the study's class rule
    re-applied to its own counts.
- **Read as data:** the study's starts and records from `runs/explosive`.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap, each start in its own child with an address-space and time
  limit (peak 11 GB for the job).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
