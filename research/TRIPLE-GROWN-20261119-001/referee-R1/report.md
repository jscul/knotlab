# Referee report TRIPLE-GROWN-001-R1 (own arrangements, bonds, readings and exact search, on every pair)

**Verdict: confirmed. No Block; two corrections, both Not a block, one of which strengthens the result.**
- **Every pair is separated, with exact readings throughout.** The referee checked all pairs, not a sample.
  - **The static pairs:** the 1,034 pairs of its own PARENT-RULE-R1 grouping, rebuilt from the atlas.
  - **The reached pairs:** all 87 of GROW-SMALL, regrown by its own engine, the created pair included.
  - **The readings:** from every bond (UNIQUE-TABLE-R1's enumeration), with no reading pooled, for all 87 reached pairs too, not
    only the 64 the study could read exactly.
  - **The test:** THREE-WAY-R1's exact search.
  - **In all 1,121 pairs** a renaming keeps the pair table, and none keeps pair and three-way readings together.
- **The created pair:**
  - 12 junctions and 28 distinctions each;
  - its pair tables are isometric, and pair plus three-way readings separate it;
  - the counts of triples per reading differ;
  - the three-distinction bonds have rank 5 against an equation rank of 12.
- **The rank claim holds: the three-distinction bonds never span the equations.** In none of the 2,242 arrangements.
  - **Static:** ranks 0 to 6 against 6 to 7.
  - **Reached:** ranks 2 to 11 against 9 to 17.
  - **So the separation is a finding**, not a restatement. The study's own data give these same ranges.
- **Correction 1: the counts of readings separate every pair, not 1,000 and 73.** `triples.py` counts a pair as separated by counts
  when `sum((Counter(ta) − Counter(tb)).values()) > 0`. That subtraction is one-sided: it misses pairs where one side has more read
  triples at some reading but none fewer. Compared both ways, as the referee did with "none" counted as a reading, the counts of
  triples per reading differ in all 1,034 static and all 87 reached pairs. This strengthens the result. **Not a block.**
- **Correction 2: the stated rank ranges.** "Rank 2 to 6 against 6 to 9" matches neither part. The ranges are 0 to 6 against 6 to 7
  (static) and 2 to 11 against 9 to 17 (reached), in the study's `triples.json` and in the referee's run. "Never span" stands.
  **Not a block.**

## The checks (`job_triple.py` under `scripts/longrun.py`; 105 cases, all ok)

| | Static (6 and 7 junctions) | Reached (9 to 17 junctions) |
| --- | ---: | ---: |
| Pairs | 1,034 | 87 (86 carried, 1 created) |
| Pair tables kept by some renaming (exact search) | 1,034 | 87 |
| Pair and three-way readings kept by some renaming | **0** | **0** |
| Counts of triples per reading differ (compared both ways, "none" included) | **1,034** | **87** |
| Three-distinction bonds span the equations | **0** of 2,068 arrangements | **0** of 174 |
| Ranks: three-distinction bonds / equations | 0–6 / 6–7 | 2–11 / 9–17 |

## Corrections for the owner (listed, not folded in)

1. **"In 1,000 and 73 of them the counts of triples per reading already differ"** should be **all 1,034 and all 87**. The count in
   `triples.py` subtracts one way only. **Not a block** (it strengthens the finding).
2. **"Rank 2 to 6 against 6 to 9"** should be **0 to 6 against 6 to 7 (static) and 2 to 11 against 9 to 17 (reached)**. "Never
   span" is right. **Not a block.**

## How the work was split

- **The referee:**
  - read `triple_grown.md` and `triples.py` with its output;
  - wrote `job_triple.py`. It uses its own arrangements (PARENT-RULE-R1's grouping, the atlas), its FIRST-KNOT-R1 engine with the
    program's rule, UNIQUE-TABLE-R1's bond enumeration, and THREE-WAY-R1's readings and exact search.
- **Read as data:** GROW-SMALL's `origin.json`, and the study's `triples.json` for the comparison of ranges.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 164 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
