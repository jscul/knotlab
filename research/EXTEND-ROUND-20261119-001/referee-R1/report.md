# Referee report EXTEND-ROUND-001-R1 (Lemma A and Claim B* read line by line; own growth, tables, isometries and extensions)

**Verdict: confirmed. Lemma A and Claim B\* are correct. Claim B held on every instance, including well past what the study
tested. No Block. Two wording points, both Not a block.**
- **Lemma A is correct, step by step, against the round as the program runs it.** The referee checked it against its own
  FRESH-COUNT-R1 statement of the round and its engine.
  - **Candidates.** Two live junctions are candidates when they have a common neighbour w, live or not. That is "lie in a common
    member of F". Whether two live junctions meet each other directly is never read, as the note says.
  - **Sets.** The round's sets are the maximal valid sets: candidate cliques of three or more with no common neighbour. These
    coincide with the maximal candidate cliques of three or more contained in no member of F.
    - A maximal clique containing a valid set S cannot lie inside some N(w), since S would too.
    - So a maximal valid set is a maximal clique, and every valid maximal clique is a maximal valid set.
    - The pairs are the candidate pairs in no set. Valid sets and sets cover the same pairs.
  - **Offshoots and stall.** These read the loose counts and the number of groups containing each junction.
  - **After the round.** Each loose distinction goes to exactly one new junction, and fresh distinctions are new. So a new junction
    meets only its parents (PARENT-RULE Lemma 1). The lookahead demand, with every new junction counted live, therefore reads only
    the parent sets, and so do p and the fresh count.
  - **The implied test** is taken against the old equations, before any new row is added, in both the program's engine and the
    referee's. By PARENT-RULE Lemma 2 (connected, at most two holders), a set of loose distinctions lies in their span exactly
    when it is all of them. So it reads only the loose counts and the parent set.
  - **A slightly stronger form holds.** Every step reads F only through its maximal members. That is the form `extend.py` tests,
    and on these pairs the two give the same counts.
- **Claim B\* is correct.**
  - **"Carries a's equations"** must mean the span, the allowed states. Re-pairing loose distinctions inside one junction fixes
    every old row as a set, so the span and the table are both kept.
  - **The next equations** are the old rows plus the new junctions' rows, with their fresh distinctions. The extension carries the
    first by hypothesis and the second by Lemma A, so it carries the next span.
  - **The next tables then agree.** That step is left implicit, and it holds: the table is a function of the span. Its bonds are
    the minimal words of the cut space, which the junctions' rows span; with loose distinctions, the outside vertex's row is their
    sum.
  - **The next reading is kept.** The live junctions are the new ones with fresh distinctions, their loose counts are the fresh
    counts, and F is read from parent sets alone, which the extension carries. The next stage is connected, so the induction runs.
- **Claim B on every R-keeping isometry, not 50 per pair.** The referee used its own enumeration (CREATED-PAIR-R1's: no WL, no twin
  quotient), its own reading test, its own extension and its own next full tables (shore enumeration):
  - **The 63 small carried pairs.** All **14,556** R-keeping isometries extend to isometries of the next tables, checked entry by
    entry. The study tested 2,198 of these. There were 0 failures, and the rounds always corresponded (X2). Each pair agrees with
    the study's row.
  - **One size past: the 23 larger carried pairs** (stages of 15 and 17 junctions, which the study left out). All **21,504** of
    their isometries keep R, and all 21,504 extend. For 10 of them the next tables come from flow-bounded bonds, raised until every
    pair of one block has its least bond, so they are exact.
  - **A control.** In each of the 80 pairs, swapping the images of two fresh distinctions of different new junctions is refused by
    the same check. The check discriminates.
- **The rest reproduces.**
  - **The six 9-junction pairs** have no R-keeping isometry. Their next tables are isometric, with an isometry carrying old
    distinctions onto old ones.
  - **The created pair:** 0 of 96 keep R, and it parts.
  - **The static pairs:** 96 of 1,034 grow on both sides, none keeps R, 43 persist (each with an isometry carrying old onto old)
    and 53 part.

## The checks (`job_extend.py` under `scripts/longrun.py`; 113 cases, all ok)

| | Reached carried, small (63) | Reached carried, larger (23; one size past) | Created (1) | Static (1,034) |
| --- | ---: | ---: | ---: | ---: |
| Both grow a round | 63 | 23 | 1 | 96 |
| Table isometries (own enumeration) | 23,496 | 21,504 | 96 | 183,970 |
| … keeping R (F whole / maximal members) | 14,556 / 14,556 | 21,504 / 21,504 | 0 | 0 |
| Pairs with an R-keeping isometry | 57 | 23 | 0 | 0 |
| Extensions tested / isometries of the next tables | **14,556 / 14,556** (study 2,198) | **21,504 / 21,504** | — | — |
| Next tables isometric: with R kept / without | 57 / 6 | 23 / 0 | 0 / 0 | 0 / 43 |
| … with an isometry carrying old onto old | 63 | 23 | — | 43 |
| Part | 0 | 0 | 1 | 53 |

## Points for the owner (listed, not folded in)

1. **Lemma A, "the stall test compares each junction's number of sets with its loose count"**, should say groups, sets and pairs
   together: a junction stalls when it lies in more groups than it has loose distinctions. **Not a block.**
2. **Claim B\*, "carries a's equations onto b's"**, should say "carries the span of a's equations (its allowed states)". The proof
   could also add one line: the table is a function of the span, since bonds are the span's minimal words. **Not a block.**

## Remark (no correction)

- **Claim B stays unproved, but the evidence is now complete on GROW-SMALL's pairs.** Every R-keeping isometry of all 86 carried
  pairs extends one round: 36,060 of 36,060. The advisor's configuration did not occur here either: a pair-junction with one fresh
  distinction whose parents' three-way readings differ between the sides. Direction #1 remains the test.

## How the work was split

- **The referee:**
  - read `extend_round.md`, the pre-registration, `extend.py` and `extend.json`, and PARENT-RULE's Lemmas 1 and 2;
  - checked Lemma A against its own FRESH-COUNT-R1 statement of the round and its engine;
  - wrote `job_extend.py` and `extend_readout.py`. They use its own FIRST-KNOT-R1 engine with the program's rule, the
    CREATED-PAIR-R1 isometry enumerator, GROW-SMALL-R1's full tables (CENSUS-READ-R1's shore enumeration, MEET-ONCE-R1's
    flow-bounded bonds), and PARENT-RULE-R1's starts and static grouping.
- **Read as data:** GROW-SMALL's `origin.json`, and `extend.json` for the row-by-row comparison.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 748 MB, about a minute).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
