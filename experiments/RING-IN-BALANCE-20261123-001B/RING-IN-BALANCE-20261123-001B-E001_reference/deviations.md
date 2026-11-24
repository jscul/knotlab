# Deviations and readings, RING-IN-BALANCE-20261123-001B-E001

Written by ticket B's helper before the registered runs B1 to B5 were started (the only computation before this file
was the enumeration check of the census, `census_count.py`, which reads no outcome of any growth). The frozen files
(`definitions.md`, ticket B's `preregistration.md` and `contract.json`) are unchanged; their SHA-256 sums were checked
against `contract.json` before any code was written (definitions e7c001a4..., pre-registration f9378d0b...).

Every run uses ticket A's engine (`experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/
engine.py`), imported, not copied and not changed. Every run is under parity (the knot law of the three named laws).

## Ticket A's readings relied on

So that the two tickets mean the same thing by "returns", "gives parts off" and the kinds of outcome, ticket A's
readings (its `deviations.md`) are taken over unchanged:

- A-D2 (a met set does not contain its common knot), built into the engine.
- A-D3 (a part is past its start when none of its members meets a member), A-D4 (a member that kept a usable distinction
  descends from itself), A-D5 (a part with descendants of two parts is mixed, neither the return nor a part given off;
  the count of mixed parts is recorded for every run).
- A-D6: returns are searched for every part of every round s that is past its start, each with its least t; listed by
  least s, then least t; the first is the run's first return. The census kind is the first that applies over the whole
  run (stalled; jammed; stopped; returns giving parts off; returns giving none off; grows to the bound). "Has a part
  that returns giving parts off" (P2, P3, P4, P5) is the existence of such a return within the run, whatever the run's
  kind; the kind is reported beside it.
- A-D9: the round in which the structure first passes the knot bound is completed and kept; the run stops after it.
- A-D10: a run is grown through all R rounds even after it stalls or jams.
- A-D22: any part counts as returning, however small (no narrower reading is used for a verdict; sizes are recorded).

## B1. The census: enumeration and identity of a start

*Reading.* The meeting graphs are the connected graphs on 3 to 6 vertices of networkx's graph atlas (each isomorphism
class once: 2, 6, 21, 112). A loose-count tuple (0 to 3 on each knot, degree + loose count at least 3 on every knot, at
least one knot with a loose distinction) is kept when it is the least tuple of its orbit under the graph's
automorphism group. A start is identified by (atlas index, that tuple). Its stars: one shared distinction for each
edge, numbered in sorted edge order, then the loose distinctions of knot 0, knot 1, and so on. The counts come out as
registered (19, 200, 3,157, 82,656; 0, 59, 1,564, 54,148 with a dead knot), checked independently by brute force over
all relabellings for 3 and 4 knots and by Burnside's lemma for every size (`census_count.json`). A start's **members**
are its live knots (every start distinction is usable); a **dead knot** is a knot with loose count 0.

*The knot test of a census start* is the parity test by both methods (ranks and cut) on the start only. A start is set
aside when some knot fails either method; a disagreement between the two methods is recorded separately (none is
expected; it would be an engine bug and would be reported).

## B2. G: "no knot is a member for two rounds" under the ordinary law

*Question.* Under (ORD, STALL) a round in which a member is short stalls: no birth is made, nothing changes, and every
member is a member again after it (A-D10 keeps such rounds running). Read literally, every stalled run would break G
for a reason the settled statement ("every member spends all it holds in one round") does not cover.
*Reading.* For every round t that does not stall, no member of the roster after round t - 1 is a member after round t.
The number of stalled rounds is recorded beside it. Together with "no return giving parts off", this is checked on
every ordinary run of B1, B2, B4 and B5.

## B3. P1: "D2(n, 3) returns every two rounds giving n parts off"

*Reading.* D2's start is past its start (its members meet only dead knots), so its roster after round 0 (one part, the
n members) is a part Y_0 that can return. P1 holds for n when Y_0 returns at round 2 giving exactly n parts off, the
part it returns as returns at round 4 giving n parts off, and so on at every even round through R = 12 (the chain of
least returns, as in ticket A's D14 and D17). The chain that starts at the part after round 1 (odd rounds) is reported
beside it without a prediction. DW(n, 3) is run and reported the same way.

## B4. P3: which part "returns", and what "waited" means (ambiguity in the frozen text)

*Question.* P3: "every member of a part that returns giving parts off waited in the round at which it returns". The
knots that can wait in round t are the members after round t - 1 that are still members after round t, so the members
in question are those of the **copy**: the part after round t that is the same as Y. By the definition of a return,
every part past its start is searched, at every s. In ticket A's rings under the two added rules the part after round
1 (n joins and n offshoots, past its start) returns at round 3 giving n parts off (ticket A's D7), and its copy after
round 3 is made of the n joins and n offshoots of round 3, none of which waited. The same is expected for D2 and DW from
round 1. So under the literal reading P3 is expected to fail on those runs for a reason in the definition of a return
(the odd-round returns), not only for the small parts of laws without waiting.

*Reading taken for the verdict (P3-literal).* For every return giving parts off, in every run of B3 under a law with
waiting: every member of the copy is in the round-t list of members that waited (`records[t-1]['waiting']`).

*Also computed and reported, without changing the verdict:*
- (P3-Y) every member of Y, after round s, waited in round s (Y is made of knots that waited); undefined for s = 0.
- each return split by the size of the returning part (1 to 3 members; 4 or more, called "ring-sized" in the report),
  by whether it is ring-like (every inclusion-maximal met set of the part has two members and they form one cycle
  through all its members), and by the parity of s.

*Laws with waiting* are those with the treatment CANCEL-WAIT (the two and the three added rules; in ticket A's A4 the
20 laws with CANCEL-WAIT, with or without NO-OFFSHOOT). *Laws without waiting*: STALL, CANCEL-OFFSHOOT, CANCEL-RETIRE
(with or without NO-OFFSHOOT), including the ordinary law. P3's second sentence is checked on every run under a law
without waiting.

*B3's runs.* B1's runs (D2, DW and Ring(n, 3) under the three laws), the census, and ticket A's A4 rerun here with the
engine (Ring(n, 3), n = 5, 7, 9, the 70 laws of `engine.a4_laws()`, which are the list of ticket A's pre-registration,
R = 16, cut off past 6,000 knots); no result file of ticket A is read for them. A4's knot and extension tests are not
rerun (P3 does not need them).

## B5. P2 and P4: which starts

*Reading.* P2: "with every knot live" is a start with no dead knot. "Every such start of five knots has the five-cycle
as its pattern of meetings": every five-knot start with no dead knot that has a part returning giving parts off under
the two added rules has the cycle on five vertices as its meeting graph. P4: "fewer than five members" counts the
start's members (its live knots), whatever its number of dead knots.

## B6. P5: the matched pairs

*Reading.* For each census start of six knots with exactly one dead knot, the matched start is the same meeting graph
with that knot's loose count changed from 0 to 1, reduced to its canonical tuple; it is a census start. A pair in
which either start was set aside by the knot test is not counted in the four classes and is reported separately. The
four counts are over pairs (each start with a dead knot once); several starts with a dead knot can have the same
matched start, and the number of distinct matched starts is reported. "Has a part that returns giving parts off" as in
A-D6.

## B7. P6(a): the round formula and e

*Reading.* For every knot x made in rounds 1 to R of Ring(n, 3) (a leftover on every knot), with r its round, p its
number of parents and f its number of fresh distinctions: e = (f + 2p - 3 - r)/2, and the formula holds when
f + 2p - r is 3, 5 or 7. The leftover of start knot i is the distinction its round-1 offshoot takes (which of i's
three loose distinctions it is makes no difference up to renaming).

Where the knot's stretch is shorter than the ring, e is also recovered from its line of descent: L is the number of
start knots among its ancestors, j the number of start knots whose round-1 offshoot is among its ancestors or is x
itself, and the stretch is the set of those start knots in the cycle of met pairs of the start's roster (for odd n the
cycle 0, 2, 4, ... of length n; for even n the cycle of the part, length n/2). The stretch is shorter than the ring
when L is less than that cycle's length; it is then a path in the cycle (checked), its ends are its two end knots (one
when L = 1), and e from the line of descent is the number of ends whose leftover is absent. **e is recovered this way
only for stretches shorter than the ring**; for longer stretches the set of start knots among the ancestors is the
whole cycle and does not show where the stretch ends. Where it is recovered, r = L + j - 1 (ROUND-FREE), p = j + e and
D = L - j + 2 are checked and reported beside it.

## B8. P6(b): "somewhere"

*Reading.* The table of rounds by (p, f) is made for each start of B4 over the knots made in rounds 1 to R. P6(b)'s
second sentence fails when, on all six rings with some leftovers removed and for every (p, f), the greatest round less
the least is at most 4 (the frozen "fails when ... the spread never exceeds 4"); whether it holds on each ring alone is
reported beside it. "By round 12" uses the knots made in rounds 1 to 12.

## B9. P7: "holds at least (t + 9)/5 fresh distinctions"

*Reading.* The number of fresh distinctions the knot received at its birth (it holds them as places for good, loose or
shared later). The bound is checked for every knot made in rounds 1 to 9.

## B10. Bounds that cut runs short

*Reading.* The knot bounds are applied as registered (A-D9); a run that passes its bound before its last round is
reported with the rounds it completed. Ring(5, 3) under the ordinary law passes 6,000 knots before round 14 (B4).

## B11. G: "Ticket A's gate has passed"

*Reading.* Ticket A's `gate.json` (read only) reports every item its engine computes as passed (G1 to G5 and G7 to
G10); its item G6, the comparison with the pilot's programs, is not computed by the engine and is the thread's.

## B12. B1's knot test "under both knot laws"

*Reading.* The parity test (both methods) and the not-all-equal test (SAT) are run on every B1 start (round 0). The
runs of B1 are under parity; no not-all-equal growth is registered in ticket B.

## B13. Added during B1 (a method, not a reading; changes no verdict)

The first attempt at `b1.py` was stopped by its ten-minute limit while comparing the rosters of D2(4, 3) and DW(4, 3)
under the ordinary law: the engine's exact sameness test (`same_rosters`: invariants, then VF2 isomorphism) took 152 s
on the roster after round 11 (932 members, 576 met sets) and longer after round 12, because those rosters are highly
symmetric. This is the engine's running time, not a bug; nothing was patched. `b1.py` now first tests the identity
renaming (same member numbers, same h and k, same inclusion-maximal met sets), which is an exact sufficient test of
sameness and applies because D2(n, a) and DW(n, a) number their knots alike (members 0 to n - 1, w_i = n + i) and the
engine numbers births by a fixed rule; VF2 is called only where the identity renaming fails. In the rerun every one of
the 387 comparisons passed by identity, so VF2 was never needed. Of the first attempt only its log (runs up to
DW(5, 3)) was seen; it was overwritten by the rerun, which gives the same lines.

## B14. Three census blocks completed outside the runner (written after the census ran, before they were rerun)

*What happened.* The thread resumed the census (unit `ring-balance-b-census`). 429 of its 432 blocks finished; three
(`n6-b0032`, `n6-b0065`, `n6-b0152`) passed the 1 GB case memory limit on every attempt and the unit was stopped.

*Diagnosis* (scratch diagnosis: each (start, law) of the three blocks in its own process, 4 GB and 120 s; then the
failing rounds interrupted and their place in the engine printed). Seven runs fail, all under the **ordinary law**, on
three dense meeting graphs with nearly every loose count 3: block 32 starts 38 and 48 (atlas graph 115, loose counts
[3,2,3,3,3,3] and all 3), block 65 starts 32 and 62 (graph 127, [3,2,3,3,3,3] and all 3), block 152 starts 112, 113 and
114 (graph 153, [3,3,3,2,2,3], [3,3,3,2,3,3] and all 3). Every other run of those blocks, under every law, finishes in
under 6 s. The cause is the ordinary ration in a round that would pass the 1,500-knot bound: the cut-off is applied
after a round (A-D9), and these rounds cannot be computed. Example, block 152 start 112: after round 6 (177 knots) the
demand roster of round 7 has 63,690 groups, 63,673 of them of three or more members (maximal sets of pairwise joinable
members), so one new knot has demand D = 62,682 and receives f = D = 62,682 fresh distinctions (round 7 takes 14 s;
376 knots after it). In round 8 that knot makes about 62,600 offshoots, which form one met set, and the engine's step 6
(`groups_from` in the demand step) adds all pairs of that met set, about 1.96 x 10^9, to a networkx graph: memory
runs out (traceback at `engine.py` line 502). Block 65 start 32: before round 8 a knot holds 917 usable distinctions
and the round's demand step spends more than 90 s in the enumeration of maximal cliques (`nx.find_cliques`, line 504)
with little memory. So it is a growth that explodes inside the round that would pass the cut-off, in the engine's
demand step (its pairs and its maximal cliques); not the sameness test (no return search is reached), and not the
lineage bookkeeping. The engine is not changed; this is its running time on these rounds, not a bug.

*What is done.* `job.py` is not changed (its SHA-256 stays the one frozen in `census/job.json`). A new script,
`extra_blocks.py`, imports `job.py` and uses its parameters and functions (R = 10, cut-off past 1,500 knots,
`compact_run`, `run_record`, `ordinary_checks`); the only difference is isolation: each (start, law) run is computed
in a forked child with its own address-space limit and time limit, so that one run that cannot finish does not take
the block with it. Each process is run on its own, one at a time, under `ulimit -v 12000000` and `timeout 1200`:
the three blocks are split into ranges of starts, with each of the seven heavy starts in a process of its own (child
limits 10 GB and 1,080 s for each law) and the other starts in ranges (child limits 10 GB and 240 s). The records go
to `census/extra_blocks.jsonl`, one line per range, in the runner's record format (status `ok`, the job's `result`
format), with the source, job hash and limits; `summarize.py` reads both files and checks that the ranges of each block
cover its starts exactly once.

*Check that the isolation changes nothing.* Before the rerun, `extra_blocks.py --verify` recomputes five blocks that
the runner finished (`n3-b0000`, `n5-b0005`, `n6-b0000`, `n6-b0200`, `n6-b0413`) and compares the start records
with the runner's, apart from the timing fields (`sec`, `seconds`).

*A run that still cannot be completed* is recorded as not completed, with the reason (memory or time limit), the round
that could not be completed, the record of the rounds before it (the same run with R lowered to the last completed
round), and a description of that round (knots and members before it, its groups, its births by steps 1 to 5, the
largest h, the pairs in the largest met set its new knots would form). Its kind is not given. The reading of the
cut-off (A-D9) is unchanged: the round that passes the bound is completed when it can be; the run is not cut short
one round earlier, which would be a different reading. In the analysis such a run is counted as "not completed" in its
law's tables; the census part of G is checked over its completed rounds and the uncompleted round is named; if a run
of the two or the three added rules is among them, P2 to P5 and P3 are reported with that run as not completed (none
was among the seven above).

## B15. P3 over the census in detail, and "the ring itself" (added at the thread's request, before the analysis)

*Detail.* The census record of a run keeps only totals over its returns giving parts off (and the first, the smallest
and the first whose copy did not all wait). For P3 over the census, `p3_detail.py` computes again, with the engine and
job.py's parameters, every census run that has a return giving parts off (454 runs among the 429 runner blocks: 227
under each of the two and the three added rules, none under the ordinary law), lists every such return, and checks that
each run's compact record is identical to its census record (the count of mismatches is reported).

*The ring itself.* Beside P3 under the frozen wording (deviations B4), every return giving parts off is classed: **the
ring itself** when the returning part is ring-like (every inclusion-maximal met set of the part has two members and
they form one cycle through all its members) and every member holds the same h and the same k; **ring-like, not
uniform** otherwise for a ring-like part; **small** for a part of one to three members that is not ring-like; **other**
for a larger part that is not ring-like. The count of returns whose part is the ring itself, and how many of them have a
copy made entirely of knots that waited, is reported for B1, A4 and the census, so that the returns of the part made
after round 1 (made of new knots, by the definition of a return) can be told apart from the ring's own returns. This
classification changes no verdict.

## B16. Added after the rerun of the three blocks: a correction to B14's diagnosis, and what came out

*Correction.* B14 says the seven runs explode "in a round that would pass the 1,500-knot bound". That holds for four of
them, not for three. In every one the round fails in the engine's step 6 (the demand step, `groups_from`): either the
enumeration of maximal cliques (`nx.find_cliques`, time, and memory for the groups of three or more it keeps) or the
pairs of one very large met set (memory). For graph 153 with loose counts [3,3,3,2,3,3] and with all 3, at round 7,
and for graph 115 with all 3, at round 8, steps 1 to 5 of the failing round would make 343, 602 and 1,170 births
(541, 830 and 1,472 knots after it), so the structure would not pass the bound in that round; the explosion is in the
number of groups of the round's demand roster, which under the ordinary ration also sets the fresh counts. Tracebacks:
`engine.py` line 504 (`find_cliques`) for graph 153 all 3 and graph 115 all 3, line 502 (pairs of a met set) for graph
153 [3,3,3,2,2,3]. So applying the cut-off before the round would not have completed these runs either. Nothing else
in B14 changes.

*Outcome.* All 600 starts of the three blocks were run; 593 x 3 runs completed, and 7 runs, all under the ordinary law
and listed in B14, did not complete within 10 GB and 1,080 s each (block 32 start 38: time, round 9; start 48: memory,
round 8; block 65 starts 32 and 62: time, round 8; block 152 start 112: memory, round 8; starts 113 and 114: memory and
time, round 7). In their completed rounds none of the seven stalls, jams or stops and none has a return; their kind is
not given. Every run of the two and the three added rules in the three blocks completed. The five-block check of B14
passed (identical records apart from timings), before the small change that caps the time of the rerun of a failed
run's completed rounds at 120 s (it touches only runs that do not complete).
