# Referee report GROW-SMALL-001-R1 (all 87 pairs rebuilt from scratch: own starts, growth, full tables and exact searches)

**Verdict: confirmed. No Block, no Narrowing. The Narrowing of MEET-ONCE and PARENT-RULE stands.**
- **Every pair is real, the 23 large ones included.** The referee rebuilt all 87 pairs from their starts with its own engine, using
  the program's fewest rule (an implied junction gets exactly d). It computed full tables by its own shore enumeration, which is
  exact for every stage here: the largest have at most 22 junctions. In 87 of 87 the two stages:
  - meet once;
  - are not isomorphic;
  - have isometric full tables, with the renaming checked entry by entry;
  - have other allowed states, by GROWN-PAIR-R1's exact search over table isometries.

  That includes the 23 round-2 pairs the study could check only on the pipeline's own tables: 43 at round 1 and 43 at round 2
  carried, plus the created one.
- **The created pair holds, rebuilt from scratch.**
  - **The starts.** Atlas graph 448 with loose counts 1, 1, 2, 1, 2, 1, 2, and atlas graph 581 with 0, 2, 1, 2, 1, 2, 1. Each has 7
    junctions and 18 distinctions, and they are not isomorphic. Their full tables are not isometric, so the pair is created, not
    carried.
  - **One round.** Each grows into 12 junctions and 28 distinctions. The two stages meet once and are not isomorphic. Their full
    tables are isometric, with every one of the 378 pairs checked under the renaming. Their states differ, by the exact search, in
    49 steps.
  - **One round further** (19 junctions and 45 distinctions each), their full tables are not isometric. So the law separates them,
    as the note says.
- **Carried against created.** The 86 carried pairs' starts have isometric full tables and other states. The one created pair's
  starts do not.
- **One round further, on full tables, not only on tables read to 8:** all 86 carried pairs still have isometric full tables and
  other states. This settles the Limitations' "persistence checked on tables read to 8" one round on, for those.
- **Amendment 1 is sound.**
  - **Comparing arrangements on their junction graphs** (each junction labelled by its loose count, each line by its shared count)
    decides arrangement isomorphism exactly. Loose distinctions of one junction are interchangeable, and so are the shared
    distinctions of one pair of junctions. So the speed-up changes no verdict.
  - **The depth clause restricted to open stages** is PARENT-RULE's Theorem 2: a closed stage has no live junction.
  - **The order of events is disclosed:** `targeted.py` ran and was read before the amendment, and the amendment touches neither it
    nor G1, G2 or C0.

## The checks (`job_growsmall.py` under `scripts/longrun.py`; the pairs' starts read from `origin.json` as data)

| | Result |
| --- | --- |
| Pairs rebuilt | 87 (43 at round 1, 43 at round 2, carried; 1 at round 1, created) |
| Stages meet once / not isomorphic / full tables isometric (entry by entry) / other states (exact) | **87 / 87 / 87 / 87** |
| Full tables by the referee's shore enumeration (exact) | 87 of 87; the largest stages have at most 22 junctions |
| Starts: isometric with other states (carried) / not isometric (created) | **86 / 1**, as `origin.json` says |
| One round further: carried pairs isometric with other states (full tables) / created pair's tables differ | **86 / 1** |

## Remarks (no correction)

- **"Reached" now means grown from any small legal start.** These starts are legal meet-once arrangements of up to 7 junctions,
  beyond the census's starts of at most five knots. The note says this, and its Narrowing of MEET-ONCE ("a property of the
  census's starts") is the right one.
- **The count of 67 groups and 87 pairs rests on the pipeline's candidate grouping**, which the referee did not rebuild. The
  existence of each pair, and its kind, the referee confirmed.

## How the work was split

- **The referee:**
  - read `grow_small.md`, the pre-registration with Amendment 1, `origin.py` and `verify_main.py`'s output;
  - wrote `job_growsmall.py`. It uses its own starts from the atlas, its FIRST-KNOT-R1 engine with the program's rule, its
    CENSUS-READ-R1 shore enumeration, its VARIABLE-OUTPUT-READER-001F-R1 isometry, and GROWN-PAIR-R1's exact states search.
- **Read as data:** `origin.json` (the starts and rounds) and the networkx atlas.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 751 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
