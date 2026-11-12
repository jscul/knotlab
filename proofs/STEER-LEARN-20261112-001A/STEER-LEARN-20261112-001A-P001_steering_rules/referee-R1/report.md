# Referee report STEER-LEARN-R1: a learner whose examples steer its search

**Verdict: Confirmed, with two wording fixes and one open alternative.**
- The blind chances, the blind medians and the swap targets reproduce exactly.
- The marks reproduce from `runs.jsonl` with my own tallies.
- The candidate checks are charged as frozen.
- "No rule steers" does not depend on the charging: on world probes alone, no rule does better than the unchanged learner.
- Claim 3's reading, a bias of the walk, has direct support in the runs. It is one of two explanations, and the census does not
  separate them.

Referee: the background referee thread, 2026-11-12. The handoff was relayed by the coordinator from the learning thread. My code is
`ref_steer.py`, which writes `result_referee.json`. It takes the maps of the laws at rest as data from the frozen harness, which reads
them by SAT. It does not rebuild the engines F and GE or their rest sets; that census belongs to the earlier epics, so for this part
the check is V1. Everything else is V2: the flip shares, the chances, the choice of g, the blind medians, the tallies and the claim-3
analysis are recomputed with independent code. The advisor model was not consulted for this job.

## 1. Claim 1, exact: confirmed

- **F.** 4 laws at rest, with maps 10010110, u00uu11u, 0x1010x1 and xx1010xx. The count comes only from 10010110, in 8 of its 16
  interface flips, so p = 1/8 and the blind median is 6. Applying the frozen closest-chance rule to the other maps gives
  g = 0uu01uu1, with p = 1/16 and median 11.
- **GE.** 64 laws at rest and 31 distinct maps. p(count) = 1/32 with median 22; g = 00001111 with p = 1/64 and median 45.
- **The medians.** Each is the least m with 1 − (1 − p)^m ≥ 1/2, an exact geometric median (the audit's `blind`).
- **One assumption carried over from the audit.** The chance averages the 4 or 64 laws equally, taking one signing per law. That
  treats a uniform blind signing at rest as uniform over the laws. It holds when every law has the same number of signings at rest,
  which the audit's method assumes. It is not rechecked here.

## 2. Claim 2, computed: confirmed, and robust to charging

- **The tallies.** I recounted all 1,600 runs. There are 407 drops at the 5-minute cap, all in GE, and each counts as never found.
  Every median, every within-blind share and every mark matches `result_summary.json`. In both settings, no rule passes on the count,
  so steering is shown nowhere.
- **The charging matches the frozen text.** In the code, M charges one check per scored candidate sign change. A charges one per
  judged proposal, meaning a proposed sign change that clears the energy envelope, judged against stored states. B and P carry no
  candidate checks. Charged probes equal world probes plus candidate checks in every run.
- **The marks on world probes alone.** A judges about 100 proposals per world probe, so under charging it could pass only by
  finding a target in one or two world probes; its failure there is close to fixed by its own accounting. But on world probes alone
  the picture is the same:
  - on the count in F, every rule's median is 19 to 21 world probes, against a bar of 3;
  - on g in F, every rule's median is 5.5 to 6.
  So "no rule steers" stands without the charging: the steering hooks do not change the walk measurably.
- **Wording.** "Every check was charged" is right for M and A. P's reweighting also uses the stored end states and is uncharged.
  The frozen text does not charge it, and P passes nothing, so no verdict changes; the sentence could say "every candidate check".

## 3. Claim 3, computed: confirmed; the reading is supported but not singled out

- **The counts.**
  - All four rules find g in F in a median of 5.5 to 6 world probes.
  - B passes under the frozen bar (5.5 against 5.5, with 79% within 11).
  - P misses by half a probe (6.0, 81%).
  - M and A would pass on world probes (5.5; 82% and 79%).
  - The B/P difference is within the noise of 100 runs: the speed belongs to the walk the four rules share, not to any rule.
- **Direct evidence for a bias, from the runs.** The g runs record whether the walk's law computed the count at some probe before
  the stop.
  - In F, the count was met in 15 to 19 of 100 runs per rule. Blind draws over the same numbers of probes would meet it in 47 to 50%.
  - In GE, it was met in 13 to 26% of the runs that ended, against 71 to 82% for blind draws.
  - So the walk meets the count's laws about three times less often than chance would over the same probes, and meets g's laws about
    twice as often. The rest set is not sampled uniformly.
- **But "a preference of the dynamics" is one of two readings.** Every run starts from the same law, the base law at the solver's
  first state, relaxed by M1. Most stops come within the first few probes; g is found by the second probe in 19% of B's runs. So the
  bias may come from where the walk starts, not from the walk's long-run visiting frequencies. The census cannot tell these apart.
  B169 (exact visiting frequencies against uniform) tests the second reading only. It should also run from the frozen start and from
  random starts, or the start should be named as a possible cause in the note.
- **Not settled by its own definition.** The blind baselines are exact computations and the marks are runs. The one near-definitional
  piece is A's charged cost (above), which no conclusion rests on.

## 4. Fixes for the thread (Not a block)

1. **The reading in the answer and "What it changes".** "The learner's own walk favours g's law and disfavours the count's: a
   preference of the dynamics" should add that the bias may come from the fixed starting law rather than the walk's long-run visiting
   frequencies, and that the census does not separate the two. Cite the count's laws being met in 15 to 19% of g runs, against about
   half for blind draws.
2. **"Every check was charged."** Narrow it to "every candidate check (M and A)": P's reweighting uses stored states uncharged, as
   frozen.
