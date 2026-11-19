# Referee report NAE-GROWTH-001-R1 (fresh code, no Codex)

**Verdict: confirmed, with one number to fix. No Block.**
- **T2 is correct, and Bondy and Murty's lemma is used correctly.**
  - The lemma holds in the multigraph form T2 needs: no exception among all 11,916 connected loopless multigraphs on up to five
    points and seven lines.
  - T2's conclusion holds on 26,868 random junction systems. Its stronger "free" form holds and is sharp.
- **The growth claims reproduce with an independent engine and a different SAT solver**, one size past the census:
  - no not-all-equal junction is ever implied;
  - every start grows identically under both laws, or relays exactly as predicted.
- **Part B reproduces exactly** with the referee's own tables and collision search.
  - **The same-states test is complete**, because every state-preserving renaming preserves the table.
  - **Its one undecided parity pair has different states.** So parity has 100 collisions with different states, not 99 and one
    undecided.
- **The two scoring notes are right.**
- **On "40% under parity" beside the Codex reader line and RING-READ:** it does not contradict them. It bounds where "distance
  carries what growth uses" applies (Section 5).

## 1. T2 and Bondy and Murty's lemma (the owner's first point)

**The argument, checked line by line.**
- **The setting.** Remove the new junction J's old distinctions and give them the value 0. Draw the remaining system as a
  multigraph: junctions are points; a shared distinction is a line between its two junctions; a loose one is a line to its own
  point of degree one.
- **Degrees.** Every junction has degree at least two. A parent gave exactly one distinction and had at least three places; any
  other junction keeps all of its three or more.
- **The lemma** (Bondy and Murty 1976, Lemma 6.1.1): a connected graph that is not an odd cycle has a 2-colouring of its lines in
  which every point of degree at least two sees both colours. With this, every junction is satisfied whatever J's distinctions
  are.
- **Odd-cycle components** have only points of degree two. Those can only be parents, since every other junction has degree at
  least three. Colouring such a component all 1 lets each of its parents see 1 on the cycle and 0 at its distinction to J.
- **So some allowed state makes J's old distinctions all 0,** and J is not implied.

**Where care is needed, and why it holds.**
- **Parallel lines.** Two knots sharing two distinctions make a multigraph, not a graph. Bondy and Murty's graphs allow multiple
  lines, and the Euler-tour proof works for any loopless multigraph. No loops arise, since a distinction lies in two different
  junctions or one.
- **The hypotheses hold in the growth.** The policy gives each new junction one distinction from each of up to three distinct
  parents, and every junction has three or more places.

**Brute force** (`referee_nae_lemma.json`):

| Check | Tested | Exceptions |
| --- | --- | --- |
| The lemma, every connected loopless multigraph on 1 to 5 points with up to 7 lines | 11,916 (13 odd cycles) | **0**; every odd cycle is correctly uncolourable |
| T2: one loose distinction from each of 1 to 3 junctions can be all equal (random systems, junctions of 3 to 5 places) | 26,868 sets | **0** |
| The stronger form: a set leaving every junction two places is free | 17,739 sets | **0** |
| Sharpness: sets leaving some junction one place | 13,516 sets | 162 not free (sharp, as the study's 41) |

## 2. The growth, independently (P1 to P5)

`referee_nae.py growth`. The referee's own engine (its FRESH-COUNT-R1 and FIRST-KNOT-R1 growth, the fewest rule) was run under
both laws. Not-all-equal implication was tested by **Glucose 4**: "the new junction's old distinctions can be all 0, or all 1".
The study used Minisat. Runs went to 14 rounds or 3,000 junctions.

| Starts | Identical under both laws | Parity closes; not-all-equal relays as predicted | Other | Not-all-equal junctions implied |
| --- | --- | --- | --- | --- |
| Random 3,000 of the census (seed 23) | 2,608 | 392 (tails 1, 2, 3, … on 306; 2, 3, 4, … on 86) | 0 | **0** |
| **1,000 six-knot arrangements (one size past)** | 954 | 46 (43 and 3) | 0 | **0** |

- **Spot checks.** The lone three-place knot closes at round 3 under parity, and under not-all-equal continues 1, 2, 3, 4, …. The
  five-place ring grows by the golden ratio under both, identically.

## 3. Part B (the owner's second point)

`referee_nae_partb.json`. The study's stages were read from `runs/nae-growth` as data. Everything else was recomputed:
- **The presentations.** There are 2,715 stages and **2,644 distinct presentations**, the same as the study.
- **The tables.** Both laws' bond tables were computed by the referee's own search for minimal non-free sets of the allowed
  states. **All 2,644 equal the recorded ones, under both laws.**
  - The referee's shore enumeration agrees on the 2,599 presentations that have a loose distinction.
  - The other 45 are closed (no loose distinction). There the shore method has no exterior and does not apply; the brute force
    does.
- **Collisions** were found by an exact table isometry (the twin quotient of the referee's 001F code).

| Law | Collisions | Presentations in one | Unique tables | Same states, redundant junction | Same states, none | Different states, redundant | Different states, none | Same next joins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Not-all-equal | 128 | 140 | 2,504 (94.7%) | 114 | 1 | 4 | 9 | 0 |
| Parity | 2,902 | 1,583 | 1,061 (40.1%) | 106 | 2,696 | 0 | **100** | 0 |

**The same-states test.** The study searches only the tables' isomorphisms. That is complete:
- A renaming that carries one presentation's allowed states onto the other's carries non-free sets to non-free sets, so bonds to
  bonds, so it preserves the table. No same-state renaming lies outside the search.
- **The only weakness was the cap** (20,000 isomorphisms), which left one parity pair undecided.

**The referee's exact search** runs over every table isometry, taking in increasing order the images of distinctions held by the
same junctions. Permuting those keeps the stars, and so the states. The search needed at most 61 leaves:
- **The undecided pair has different states.**
- **So B3c reads 2,802 same states and 100 different, none undecided.** The note's "99 with different states, 1 undecided" and
  "Under parity it misses 99" become 100. B3c's verdict (failed) is unchanged.

## 4. The two scoring notes (the owner's third point)

- **B5c is inverted in `merge.py`.** `out[b5]['pass'] = all(r['same_next_joins'] ...)` is used for both laws. The frozen B5c says
  some colliding parity pair without a redundant junction joins differently. All 2,796 such pairs do, so B5c held, as the note
  says. The frozen scorer reports it failed, which would make 7 of 12; the note's 8 of 12 is the correct reading.
- **The repeated pilot start.** `P-ring5-spare1` is five four-place knots, which is the bare ring (`bare_sizes` gives
  max(3, 2 + 2) = 4). Its counts equal `P-ring5-bare`'s (5 every round). The ring with one spare per knot is `P-ring5-five-place`,
  which grows by the golden ratio (5, 10, 15, 25, 40, 65, …, ratio 1.618) under both laws.

## 5. "40% under parity" beside the Codex reader line and RING-READ (the coordinator's question)

They do not conflict. They answer different questions on different populations, and part B shows where the earlier statement
applies.
- **What part B measures.** Small stages (up to 15 distinctions) of the cheapest growth from census starts of up to four knots.
  These often have two knots sharing two distinctions, closed pieces and redundant junctions. The question is whether the table
  fixes the whole next round of joins.
- **What fails, under parity, is mostly not the distance.** 2,802 of the 2,902 colliding pairs have the same allowed states.
  - Any reading of the allowed states, bond distance included, sees two identical systems.
  - The growth reads which junction holds which distinction. That is the presentation, and here it is not fixed by the states.
    Different presentations of one parity code are common when the junction graph is not three-connected.
  - Only 100 pairs (3%) are the table's own loss: different states, one table.
- **The Codex reader line works where the states fix the presentation.**
  - In its families (simple sharing, a three-connected wired graph), equal states give the same junctions up to the choice of
    exterior.
  - 001L shows a legal triple fixes the exterior. Its hidden-junction examples (widths 28, 32, 46) are exactly the cases where
    two presentations share a table or the states.
- **RING-READ's ring is such a family.** The reader returns every junction there.

**So "distance carries what growth uses under parity" should be said with its scope.** It holds where the allowed states fix the
presentation: the serial-law families of the Codex line and the ring. Across small census stages it does not. There 60% share
their table with a stage that joins differently, almost always because the two have the same allowed states, presented
differently (A108). **Narrowing (interpretation) of the summary as John has it, not of NAE-GROWTH's results.**

## Corrections for the owner (listed, not folded in)

1. **B3c's count.** "2,802 of 2,902 (99 with different states, 1 undecided)" should read **100 with different states**: the
   undecided pair is decided. Likewise "Under parity it misses 99" becomes 100. **Not a block (number).**
2. **How the parity reading is said to John.** "Distance carries what growth uses" holds where the allowed states fix the
   presentation (the Codex families, the ring). Among small census stages it does not, and almost every failure is a pair with
   the same allowed states. **Narrowing (interpretation); not a block.**

## How the work was split

- **The referee:**
  - read `nae_growth.md`, the pre-registration, `naelib.py`, `bondlib.py`, `job.py`, `merge.py` and `posthoc_b.py`;
  - wrote `referee_nae.py` (lemma, partb, growth), on its FRESH-COUNT-R1, FIRST-KNOT-R1 and 001F-R1 code.
- **The study's part-B stages** (stars, next parents, recorded tables) were read from `runs/nae-growth` as data. The study's
  results.json was read for the pilot counts and verdict fields.
- **No study code was run.** The SAT solver is pysat's Glucose 4, a library.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
