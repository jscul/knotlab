# Referee report PARENT-RULE-001-R1 (proofs read; own growth, own enumeration, own tables and states)

**Verdict: confirmed. No Block; three wording points; the pending shard is covered here.**
- **Theorems 1 to 3 are correct as proved** (Section 1). The referee also checked them with its own engine on every census start,
  the study's pending shard included:
  - 70,480 stages of round ≥ 1 to 40 junctions;
  - 0 violations of live junctions apart, of backing by a closed junction, of exact peeling, and of peel depth at least the round;
  - on all 17,934 open stages of at most 12 junctions, Theorem 3 holds: 1,626,615 previous-stage pairs equal, 94,885 shorter, none
    farther.
- **The static enumeration is right.**
  - **The count.** Burnside's lemma over each graph's automorphisms, with the referee's own legality test, gives 503,039 legal
    orbits: 3, 19, 198, 3,131, 82,391 and 417,297 at 2 to 7 junctions.
  - **The representatives.** One per orbit, and their properties, equal the study's: P1 58,972; P1 in the backed stratum 58,747;
    depth ≥ 1, 4,671; depth ≥ 2, 77.
  - **Tables and states.** The referee's own tables, exact isometry groups and exact states search reproduce every figure: 38,301
    table groups, 37,829 with the same states only, 472 with other states, 1,034 pairs, 242 with both sides backed, 38 with both of
    depth ≥ 1, and 0 with both of depth ≥ 2.
- **`plib.states` is sound.**
  - A junction-graph isomorphism, with the outside a plain point, fixes the cut space.
  - The twin-class lift is valid, because every carrier maps distinctions with the same holders onto such distinctions.
  - The double rank test is equality of spans.
  - "Other" is exact when every quotient isomorphism is enumerated, and no test reached the cap.
- **UNIQUE-TABLE's 11 rivals.** All fail backed pairs (5 to 8 violations each), while every truth is backed by a closed junction,
  keeps its live junctions apart, and has peel depth 1.

## 1. The proof (ticket A)

- **Lemma 1** (induction on the round).
  - Before round r, the live junctions are the round-(r − 1) junctions with fresh distinctions.
  - Each gives every loose distinction to exactly one new junction (a group, a pair, or an offshoot for the rest), so the old
    junctions are left with none.
  - A new junction takes one distinction from each parent and fresh ones, so it meets its parents once each, and new junctions
    share nothing.
  - **Correct.** It matches the referee's engine, which takes every loose distinction in the round: one per group or pair, the rest
    as offshoots.
- **Lemma 2.**
  - The stage is connected, since a new junction meets its parents. All 26,441 census starts are connected, as the referee
    checked.
  - So a set of loose distinctions lies in the cut space only if it is all of them. A cut made only of lines to the outside cuts
    off every junction.
  - Under the GF(2) fewest rule, a junction with no fresh distinction is implied, so it holds every loose distinction and closes
    the stage.
  - **Correct.** Note that it needs connectivity. DROPPED-JUNCTION's re-choices can be disconnected, which is where JOIN-GROWTH's
    structural test fails (DROPPED-JUNCTION-001-R1).
- **Theorem 1.**
  - **P2:** the live junctions all date from the same round, so they share nothing.
  - **P1⁺:** a live junction's neighbours are its parents, which were candidates, so an older junction meets both. That junction
    holds no loose distinction after the round.
  - **Correct.** Round 0 is rightly excluded.
- **Theorem 2.**
  - In an open stage every new junction is live (Lemma 2), so removing the live junctions removes exactly round r.
  - Distinctions never change after their round.
  - So peeling gives stage r − 1, and depth ≥ r follows by repetition.
  - **Correct.**
- **Theorem 3.**
  - **The cut.** The same side S, the one without the outside, gives the same cut in stage r: S's former loose distinctions now
    lead to round-r junctions on the other side, and round-r junctions meet only their parents.
  - **Connectivity.** The other side stays connected through o, because every round-r junction holds a fresh distinction (an open
    stage).
  - **Correct.**
- **Scope of "at any size".** "The law can never build them" holds for every stage of round ≥ 1 from a connected start. A rival
  taken as a start (round 0) is not covered. The census's starts have at most five knots and the rivals seven or eight junctions,
  so nothing changes here, but the statement should name its scope.

## 2. The census (`job_parent.py`, C-*; all 53 shards of 500, covering the study's pending shard)

| Check | Result |
| --- | --- |
| Stages of round ≥ 1, at most 40 junctions | 70,480 (meet once: 3,906); the study's 264 shards: 70,228 (3,889) |
| Live junctions apart / backed by a closed junction / peel gives the previous stage / depth ≥ round | **0 / 0 / 0 / 0 violations** |
| Theorem 3, open stages of at most 12 junctions (17,934): previous-stage pairs equal / shorter / farther | 1,626,615 / 94,885 / **0** |

**The study's pending shard (starts 26,100 to 26,199).** It adds 252 stages and 17 meet-once ones, with no violation, so the
"stress test pending" can be closed on this evidence.

## 3. The static enumeration (`job_parent.py`, S-*; `job_parent_groups.py`)

**The referee's own enumeration:**
- **The graphs and the counts.** Every connected atlas graph on 2 to 7 points, with loose counts 0 to 3 (0 to 2 at 7).
- **Legality.** Every junction has at least three places, and there is no cut point but the outside. The test is precomputed per
  set of junctions holding loose distinctions.
- **The count.** Burnside's lemma: the fixed legal vectors of each automorphism, averaged.
- **The representatives.** One per orbit (its least image), each with its exact table, from the referee's shore enumeration.
- **Grouping.** By exact isometry (the referee's twin-quotient search).
- **States.** By a junction-graph isomorphism, or else by GROWN-PAIR-R1's exact search.

| | Referee | Study |
| --- | ---: | ---: |
| Legal orbits (Burnside) / representatives | 503,039 / 503,039 | 503,039 |
| P1 / P1 in the backed stratum / depth ≥ 1 / depth ≥ 2 | 58,972 / 58,747 / 4,671 / 77 | the same |
| Table groups of two or more / same states only / other states | 38,301 / 37,829 / 472 | the same |
| Other-states pairs / both P1 / both P1 backed / both depth ≥ 1 / both depth ≥ 2 | 1,034 / 242 / 242 / 38 / 0 | the same |
| Undecided | 0 | 0 |

## 4. Rigidity (R1; `job_rigid.py`)

**The population** is the referee's own meet-once grown census stages of up to 14 junctions: 1,104 open ones, 1,099 outside the
pending shard, the study's number.

**The test.** Every symmetry of the table was checked. Each one is a lift of a map of the table's twin classes composed with a
permutation inside the classes. So the states are kept by every symmetry exactly when they are kept by every lift and by every swap
of two neighbours inside a class.

**The result:** **181 of the 1,099** have a table symmetry that does not keep the states, against the study's 178.
- **Why three more.** The study enumerated maps of classes of distinctions with the same holders. The table's own twins can be
  coarser: distinctions with equal rows but other holders. A swap of these is a symmetry that its test does not try.
- **What it changes.** The conclusion, that the advisor's rigidity theorem is false, only gains.

## Wording points for the owner (listed, not folded in)

1. **"The law can never build them, at any size":** add "in any round from a connected start". Round 0 is outside the theorem.
   **Not a block.**
2. **R1's 178 of 1,099 is 181** by every table symmetry. The study's test misses symmetries that swap table twins with different
   holders. **Not a block.**
3. **The pending shard** passes all of C1 here (252 stages, no violation). It can be folded in and the "stress test pending" note
   closed. **Not a block.**

## How the work was split

- **The referee:**
  - read `parent_rule.md`, the pre-registration, ticket A's `proof.md`, `plib.py`, `static_job.py` and `static_pairs.py`;
  - wrote `job_parent.py`, `job_parent_groups.py` and `job_rigid.py`, on its FRESH-COUNT-R1, FIRST-KNOT-R1, CENSUS-READ-R1,
    VARIABLE-OUTPUT-READER-001F-R1, GROWN-PAIR-R1 and MEET-ONCE-R1 code.
- **Read as data:** the census keys, the networkx graph atlas, the study's summaries, and `verify_rivals.json`.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap, 6 workers (peak 1.0 GB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
