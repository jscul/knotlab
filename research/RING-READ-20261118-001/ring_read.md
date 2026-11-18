# Can the ring be regrown from its bond distances past six?

Epic `RING-READ-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead for the scouting probe's idea 2 ("a
system that carries no description of itself"). Goals G1 and G17; assumption A97. **Referee pending.**

**Record.**
- Pre-registration, frozen before each run: [preregistration.md](preregistration.md) (commit `a90132fcc` for ticket A; Amendment 1,
  commit `5d29c1931`, for ticket B after ticket A was read).
- Ticket A, tables and the first readers: [ringread.py and check.py](../../experiments/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables/);
  results: [results.json](../../artifacts/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables/results.json).
- Ticket B, the incremental reader: [reader3.py and check.py](../../experiments/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental/);
  results: [results.json](../../artifacts/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental/results.json).
- Advisor: [question 1](advisor/question_1.md), [answer 1](advisor/answer_1_fable.md), [question 2](advisor/question_2.md),
  [answer 2](advisor/answer_2_fable.md).

## The answer

**In the owner's terms.**
- **Yes, through round 25: the ring's distances carry everything its growth needs.** Grow the ring of four four-place knots and one
  five-place knot under the cheapest counts, then keep only the bond distance between every two of its distinctions, with no
  names, no rounds and no record of who came from whom. A reader that keeps what it has already read gives back every junction
  exactly at rounds 10, 12, 14, 15, 16, 18 and 20, where the largest junctions hold 7, 8 and 9 distinctions (526 junctions and
  1,887 distinctions at round 20), and in a stress test at rounds 22 and 25 (1,024 junctions of up to ten distinctions); one
  round grown from what it read is exactly the true next round. The growth rule itself
  needs nothing else: it reads only which junctions still have loose distinctions.
- **Where the old reader stops, and why.** `BOND-NEXT-JOIN-20261117-001`'s reader, proved when no junction holds more than six
  distinctions, rests on one fact: three or more junctions added together never make a consequence of fewer than seven
  distinctions. The ring breaks that near its start, where small junctions (one of three distinctions, many of four and five) add
  up to consequences of seven and eight. Run on past six, the reader invents three junctions at rounds 10 to 14 (a repair step
  removes them) and, from round 15, loses one and invents 104 to 148 more. The new reader keeps every junction it has read and
  sets aside the short pairs that sums of several of them already explain; that is enough at every round checked.
- **How far apart it needs to look.** Exactly as far as the largest junction: distances up to six at rounds 10 to 14, seven at 15
  to 18, eight at 20. One less and it fails.
- **The ring is rigid.** Its junctions, with one extra end for the loose distinctions, are joined three ways apart at every round
  checked, so by Whitney's theorem its allowed states fix the junctions, except which one holds the loose distinctions, and the law
  settles that.

| Round | Junctions | Distinctions | Largest junction | Old reader run on | Repair of the old reader | New reader | Regrown round | Least distance needed |
| ---: | ---: | ---: | ---: | --- | --- | --- | --- | ---: |
| 10 | 120 | 341 | 7 | 3 invented | exact | exact | equal | 6 |
| 12 | 165 | 491 | 7 | 3 invented | exact | exact | equal | 6 |
| 14 | 225 | 703 | 7 | 3 invented | exact | exact | equal | 6 |
| 15 | 261 | 833 | 8 | 1 lost, 104 invented | no legal repair | exact | equal | 7 |
| 16 | 301 | 981 | 8 | 1 lost, 104 invented | no legal repair | exact | equal | 7 |
| 18 | 398 | 1,363 | 8 | 1 lost, 104 invented | no legal repair | exact | equal | 7 |
| 20 | 526 | 1,887 | 9 | 17 lost, 148 invented | no legal repair | exact | equal | 8 |

Stress test one size past (after the frozen runs, not pre-registered; `check.py 22 25` and `stress_tables.py 25` in ticket B):

| Round | Junctions | Distinctions | Largest junction | New reader | Regrown round | Least distance needed |
| ---: | ---: | ---: | ---: | --- | --- | ---: |
| 22 | 687 | 2,572 | 9 | exact | equal | 8 |
| 25 | 1,024 | 4,110 | 10 | exact | equal | 9 |

Stress test pending: the round-25 table at sides of up to six against seven junctions (registered as `RING-READ-S25` in the
long-running index; the reader above read the six-junction table).


## Predictions and verdicts

Ticket A (frozen at `a90132fcc`):

| # | Prediction | Verdict |
| --- | --- | --- |
| G | Code gate: enumeration = brute force at rounds 1 and 2; the proved reader exact at round 9; a mutated table rejected | held |
| F1 | No one-parent junction after round 1 | held |
| F2 | No triangle; no two junctions sharing two distinctions | held |
| F3 | Every cut between early and late rounds at least 11 distinctions | held (11 at every round) |
| P1 | Tables with sides of up to 6, 7 (and 8 at rounds 10 to 14) junctions agree | held (no entry differs) |
| P2 | The old reader run on invents junctions at every round | held |
| P3′ | The advisor's linear prune makes it exact | failed (changed nothing at 10 to 18; at 20 it removes 16 of 148) |
| P3 | The old reader plus repair and table check: one survivor, the truth | held at 10 to 14; failed at 15 to 20 (no legal repair) |
| P4 | The regrown round equals the true one | held where P3 held; the rule's history-free step on the true junctions held at every round |
| P5 | The junction graph with the outside end is 3-connected | held (connectivity exactly 3 at every round) |
| P6 | Least distance needed = largest junction − 1 | held where P3 held |

Ticket B (Amendment 1, frozen at `5d29c1931` after ticket A was read):

| # | Prediction | Verdict |
| --- | --- | --- |
| Q0 | Gate: the new reader exact at rounds 3 to 9; a mutated round-10 table rejected by the table check | held |
| Q1 | The new reader alone exact at every round 10 to 20 (the advisor bet against) | held |
| Q2 | With repair and table check: one survivor, the truth | held (nothing to repair) |
| Q3 | The regrown round equals the true next round | held |
| Q4 | Least distance needed = largest junction − 1 | held (6, 7, 8) |

## How it works

- **The table.** Distinctions are the edges of the junction graph, with one outside end for the loose ones. The parity consequences
  of the junctions are this graph's cuts, the minimal ones are its bonds, and the bond distance of two distinctions is the size of
  the smallest bond holding both, minus one. The table is computed exactly over every bond with a side of at most six junctions;
  sides of seven and eight change no entry, and the shapes that could hide a smaller bond with two large sides (a chain of
  one-parent junctions, a cut between early and late rounds) are absent or too large (F1, F3). This is checked, not proved.
- **The new reader** reads stage by stage, s = 3, 4, …: a pair closer than s is set aside when some sum of junctions already read
  (connected, up to s of them, grown while the running sum stays within two of s, with at most s distinctions left) contains both, unless one read junction holds both; the new
  junctions are the cliques of what remains that are not sums of read ones and meet each read one in at most one distinction. The
  old reader recomputed everything at each stage and set aside only sums of two, so it lost the round-1 three-distinction junction at
  stage 8 and let sums of three or four small junctions (a two-by-two block of four-place junctions sums to eight distinctions) make
  cliques.
- **The growth reads only the junctions.** Under the cheapest counts the live junctions are exactly those with loose distinctions,
  the groups are read from shared distinctions, and the fresh counts from the next groups, so one round grown from the junctions
  alone, with every round and parent forgotten, equals the true round (checked at every round from the true junctions and from the
  read ones).

## The old reader's failure against Codex's obstruction

`VARIABLE-OUTPUT-READER-20261118-001H` (not yet refereed) names an obstruction outside its family: a cycle of four four-place
junctions whose six distinctions all look close enough for one six-place equation that is not there. The diagnosis here
([witness_shapes.py](../../experiments/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables/witness_shapes.py), after the run,
one smallest bond per pair inside each invented junction) finds two causes:
- **Round 10 (stage 7): a different obstruction.** All three invented junctions are made of pairs that are close through a path of
  three junctions, the round-1 three-distinction junction between two four-place ones (3 + 4 + 4 − 4 = 7); no cycle is involved.
  This is `BOND-NEXT-JOIN-20261117-001`'s lemma (three junctions together leave at least seven distinctions) failing because one
  junction has only three.
- **Round 15 (stage 8): Codex's kind, one size up, together with paths.** Of the 104 invented junctions, some are close only through
  paths of three four-place junctions (4 + 4 + 4 − 4 = 8), and many through cycles of four four-place junctions, whose sum is a bond
  of eight distinctions; that is the shape of Codex's obstruction. Like Codex's six distinctions, none of the invented junctions is
  a parity consequence (the linear prune, which discards only consequences, changed nothing).

The new reader handles both the same way: a pair is set aside when a connected sum of junctions already read, path or cycle,
explains it. This does not touch Codex's open step, which is under its law and asks whether such a phantom can change a live
triple; it shows only that on this ring the phantoms are explained by junctions read earlier.

## Known results, and what this adds

Known: Whitney's 2-isomorphism theorem (1933): a graph's cut space fixes a 3-connected graph and never marks a vertex; the program's
`KNOT-SPACE-20261020-001` (allowed states carry a graph exactly when the knot matroid is graphic); `BOND-NEXT-JOIN-20261117-001`
(the reader to six), `VARIABLE-OUTPUT-READER-20261118-001G` (an all-size reader for another law when every junction holds at most
four distinctions; the ring's junctions hold 4 to 10, so it lies outside that scope, and nothing here repeats its proof) and, the
same day, `-001H` (distance five is enough and sharp on a three-dimensional family of that law). There the needed distance stays
fixed; on the ring it grows with the largest junction. Reading a graph back from the sizes of the smallest bonds through pairs of edges is not a problem I found in the literature
(searched lightly). What this adds: for a growth whose junctions keep getting larger, the bond-distance table alone gives back every
junction and the next round through round 20, with a reader that sets aside sums of any number of read junctions and needs
distances exactly up to the largest junction less one; the junction graph is 3-connected throughout.

## Limitations

- Computed at seven rounds and two more in the stress test, not proved for every round. The table's completeness for bonds with two sides of
  more than six junctions is checked by agreement to eight, not proved.
- Uniqueness is the reader's: the repair step had nothing to repair, so this does not show that no other legal incidence has the
  same table. With 3-connectivity, a second incidence would need different allowed states with the same table, the kind found at
  width 32 under the other law (`VARIABLE-OUTPUT-READER-20261118-001E`). Not searched.
- The new reader was designed after the old one was seen to fail (disclosed; its predictions were frozen before it ran). Its set-
  aside step grows sums while their running size stays within two of s, the advisor's slack, not a proved bound.
- One ring and one law. Whether the reader reads the census's other growths is open.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""`, twice (`modelUsage` names claude-fable-5-2 both times). Before the first freeze it
said the table was only an upper bound (taken: sides to eight, and the facts F1 and F3), proposed the linear prune (taken as R1′;
it failed), bet that the junction graph could not be 3-connected because a live one-parent junction hangs on one parent (wrong
here: none is live after round 1), and warned that Whitney twists could give a second incidence with one table (none exists, since
the graph is 3-connected). Before the second freeze it said sums of three were too few and proposed the closure the new reader uses
(taken; it is what made the reader work), warned that kept junctions could poison later stages (no case seen) and bet against Q1
(wrong: the new reader was exact alone).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: reading the cheapest-count ring back from its bond distances past six | **Status:** Successful | The incremental reader gives back every junction at rounds 10 to 20 (and 22, 25), the regrown round is the true one, and it needs distances exactly to the largest junction less one; the old reader fails from round 10 |
| Local direction: distance readers for growths whose junctions keep growing | Continue | One reader works on one growth; whether the table also excludes every other legal incidence, and whether it reads other growths, is open |
| Broader exploration: what bond distances carry (A97) | Known alternatives | Under the other law the table reads three-parent joins to width 26 and a fixed horizon of five on a three-dimensional family, but loses one- and two-parent menus at width 18; the fewest counts from one knot misread 47 small mixed stages; the ring is now read to round 25 |
| Long-term goal: G1 Space from a law (with G17) | Capability gained | A growing base whose own distances, with no names or history, carry everything its law needs for the next round |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Run the new reader on other growths: the census's growing arrangements, the other fast rings, and the 47 mixed stages the threshold reader misread | 2/3 — says whether reading back is a property of the cheapest growth or of this ring | 3/3 — the reader, the tables and the census exist | read every TOUCH-CENSUS arrangement that grows, to its first junction of seven → stop at a growth the reader misreads, or all read | Selected · awaiting go-ahead |
| 2 | Does the table fix the allowed states? A second legal incidence with the ring's table, or a proof there is none (the junction graph is 3-connected, so only another set of allowed states could do it) | 2/3 — would make the table a complete description of the ring | 2/3 — the forced-equation inference of `VARIABLE-OUTPUT-READER-20261118-001D` exists, not at this size | infer the parity equations each pair's distance forces, in linear algebra, at rounds 10 to 20 → stop when they span the allowed states, or at a free equation the table cannot see | Alternative · deferred |
| 3 | Prove the reader for the ring at every round | 2/3 — an all-size result past six | 1/3 — needs a bound on bond sides in the ring's model and an exactness lemma for the set-aside step | bound the junctions on both sides of a bond of at most s distinctions in the (v, S) model → stop at the bound or a large-sided small bond | Alternative · deferred |
| 4 | B203, a clock inside the growing ring (scouting idea 3) | 2/3 — a native period and lap counter | 3/3 — the model gives the tick | prove the tick and record periods from the model → stop at a proof and a local reading or none | Alternative · deferred |
| 5 | B204, a learner who must discover three-way readings (scouting idea 4) | 2/3 — a fact reachable only by higher-arity questions | 2/3 — one example in hand | measure pair-invisible parity facts at widths 27 to 32 → stop at a rate, or a learner that finds the gap | Alternative · deferred |

**Corrections:** none. **Goals:** G1 and G17 checkpoint (capability gained); no goal changed. **Assumptions:** A97 gains this
study, status unchanged; none new. **Basket:** B196, B202, `BOND-BALLS-20261111-001#2` in the line; B203 and B204 (the scouting's
ideas 3 and 4, recorded this session) are #4 and #5 here.


## Final report as sent (2026-11-18 23:49 UTC)

**Outcome:** yes, through round 25. The bond-distance table alone gives back the ring of four four-place knots and one five-place knot, with no names, rounds or parents, and one round grown from it is the true next round. Closed, referee pending.

- **What was read.** At rounds 10 to 20 the largest junctions have 7, 8 and 9 distinctions (526 junctions at round 20). A stress test one size past went to round 25: 1,024 junctions, up to ten distinctions. A new reader gets every junction exactly at every round. It keeps what it has already read and sets aside the short pairs that sums of junctions already read explain. It needs distances exactly as far as the largest junction less one, and one less fails. The growth rule needs nothing beyond the junctions, because it only reads which junctions still have loose distinctions.
- **Why the old reader failed.** Codex's proved reader assumes three junctions added together always leave at least seven distinctions. Near the ring's start that is false. At round 10 the failure comes from a path through the one three-distinction junction (3 + 4 + 4 − 4 = 7), which is a different obstruction from Codex's newest. From round 15 it also comes from cycles of four four-place junctions, which is Codex's obstruction kind (VARIABLE-OUTPUT-READER-001H), one size larger. A repair step rescued rounds 10 to 14 but nothing after that.
- **Rigid.** No two junctions cut the rest apart at any round. By Whitney's theorem, the allowed states therefore fix the junctions.
- **Not shown.** This does not show that no other legal arrangement has the same table. It is computed, not proved for every round. One check is still running: the round-25 table compared at two enumeration sizes, registered as long-running.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: reading the ring back past six | **Status:** Successful | Exact at rounds 10 to 25; the regrown round is the true one; the needed distance is the largest junction less one |
| Local direction: distance readers for growing junctions | Continue | Uniqueness and other growths are open |
| Broader exploration: what distances carry (A97) | Known alternatives | Codex's readers under the other law; this ring is now read too |
| Long-term goal: G1 (with G17) | Capability gained | A growing base whose own distances carry its next round |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Run the new reader on the census's other growths and the 47 stages the old reader misread | 2/3 — is this the ring or the law? | 3/3 — code and census exist | read every growing census arrangement → stop at a misread or all read | Selected · awaiting go-ahead |
| 2 | Does the table fix the allowed states (uniqueness)? | 2/3 — the table as a complete description | 2/3 — Codex's forced-equation method, not at this size | forced equations at rounds 10 to 20 → stop when they span, or at a hidden one | Alternative · deferred |
| 3 | Prove the reader at every round | 2/3 | 1/3 | bound bond sides in the ring's model → stop at a bound or a counterexample | Alternative · deferred |
| 4 | B203, the clock (idea 3) | 2/3 | 3/3 | prove the tick from the model | Alternative · deferred |
| 5 | B204, the learner's gap (idea 4) | 2/3 | 2/3 | rate of pair-invisible facts at widths 27 to 32 | Alternative · deferred |

**Corrections:** none. **Goals:** G1 and G17 checkpoint (capability gained). **Assumptions:** A97 gains this study, status unchanged. **Advisor:** Fable 5.2, twice, before each freeze. It flagged the table's completeness, which led me to check enumerations of up to eight junctions. It proposed the closure step that made the new reader work. It also bet wrongly twice, against the graph's rigidity and against the new reader.

Referee hand-off: the decision note is `research/RING-READ-20261118-001/ring_read.md`. Check most closely that the table is complete for bonds with two large sides. The prior-work line is in the pre-registration under "Prior work in the program".
