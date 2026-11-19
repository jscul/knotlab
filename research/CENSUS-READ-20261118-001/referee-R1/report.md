# Referee report CENSUS-READ-001-R1 (own growth, tables and symmetry test)

**Verdict: confirmed, with two wording points. No Block.**
- **The exact table is right** (the owner's first point), closed stages included.
  - On **every** stage of at most 16 junctions in the census (56,036 stages, 2,966 of them closed), `exact_table_v2` equals the
    referee's own table.
  - It also agrees on a sample of 942 stages of 17 to 40 junctions.
- **The symmetry test is sound and slightly conservative** (the second point).
  - It agrees with the referee's exact test on every stage it decided.
  - Its 64 "unknown" stages, where the search cap was reached, have no junction-moving symmetry.
- **Amendment 5's fixes are honest** (the third point). Every verdict that changed from pass 3 to pass 5 changed for one of the two
  named faults, and the scoring is labelled post hoc.
  - **One wording point.** The "same states" class includes outputs with one junction too many: 154 of its 488 at meet-once
    stages. Those are not another arrangement.
- **The headline numbers reproduce** from pass 5's own records.
- **On R3n and names**, the referee's earlier check supports the note's diagnosis of the 51 stages.

## 1. The exact table, including closed stages

**The method** (`exact_table_v2.py`), checked at the argument level:
- **Enumeration.** Every connected inner side J is grown from its least junction r, with r's smaller junctions excluded, by
  include/exclude branching on a frontier junction. Each connected set is reached exactly once.
- **The cut.** A branch is cut when the maximum flow from J to the excluded junctions and the outside exceeds L. That is a valid
  lower bound on the cut of every side that contains J and avoids them.
- **The leaf.** At a leaf, J is a bond when its cut is at most L and its complement is connected. With a loose distinction the
  outside is in the complement. On a closed stage the outside is isolated and left out, the complement must be a non-empty
  connected set of junctions, and "everything" is correctly not a bond.
- **The closed-stage fault was real.** The referee's own shore code had the same fault (an exterior assumed) and missed every bond
  of the 45 closed presentations in NAE-GROWTH's part B.

**Computed** (`referee_census.py tables`, `large`). The referee regrew every census arrangement with its own engine (FRESH-COUNT-R1
and FIRST-KNOT-R1: the fewest counts, GF(2) implication), kept every stage to round 8 (closed stages included), and matched each to
pass 5's record of the same arrangement and round.

| Check | Stages | Agree |
| --- | --- | --- |
| Stage matches the record (junctions, largest junction, loose count) | 56,036 (all stages of at most 16 junctions, all 26,441 arrangements) | **56,036** |
| `exact_table_v2` = the referee's shore table (every bond, both sides connected; closed-aware), through the study's horizon | 56,036, of which 2,966 closed | **56,036** (2,966 closed) |
| The referee's shore table = its brute force over the allowed states' minimal non-free sets | 21,546 (at most 14 distinctions) | **21,546** |
| The least distance = pass 5's recorded value | 56,036 | **56,036** |
| `exact_table_v2` = the referee's all-sides bond search (its RING-READ `search_root`), or its shore table on closed stages | 942 of 17 to 40 junctions, from 600 sampled arrangements (10 closed; 10 closed ones over 20 junctions skipped) | **942** |

**Not checked:** the other 43,000 or so stages of 17 to 40 junctions, and the stages over 40. The method is exact by the argument
above, and it agrees wherever it was compared.

## 2. The symmetry test

**What `job_exact3.symmetry` does**, read:
- **Twins.** Two distinctions held by different junctions with the same distance to every other distinction. Their exchange is a
  table symmetry.
  - **Where junctions meet at most once, it always moves a junction.** A junction holding one of the two would have to map onto a
    junction sharing all but one of its places, and no two junctions share two. So the test is sufficient there.
  - **Where two junctions share two, it is not.** For example, two three-place knots sharing two distinctions have their loose
    distinctions as twins, and their exchange swaps the two knots. But the note uses the twin flag only in the meet-once rows.
- **The search.** At most 10 junctions: VF2 over the table's automorphisms, up to 20,000 of them. "Fixes" needs the full
  enumeration, so it is sound; "unknown" is excluded from the counts.

**Against the referee's exact test** (`referee_census.py sym`). The referee's twin quotient finds every table symmetry, with no cap
reached, at every meet-once stage of at most 14 junctions:

| Junctions | Stages | Referee / study |
| --- | --- | --- |
| 1 to 10 | 2,557 | moves / moves 549; fixes / fixes **1,944**; **fixes / unknown 64** |
| 11 to 14 (beyond the study's search) | 707 | moves 187; fixes 520 (the study: not checked, or twins only) |

- **No disagreement where the study decided.**
- **The 64 "unknown" have no junction-moving symmetry.** So the class "no exchange moves a junction" at ten junctions or fewer has
  2,008 stages, not 1,944. R3n reads 1,389 of them exactly (69%; the note's 68% on 1,944 is 1,330), and misreads 527.
- **One size past, at 11 to 14 junctions,** R3n reads 317 of the 520 symmetry-free stages exactly (61%) and misreads 158.

## 3. Amendment 5 (were the post hoc fixes honest?)

`referee_census.py amend5` compares pass 3 (before the fixes) with pass 5 on the 1,925 arrangements both read: 7,587 stages.

| Verdict change, pass 3 → pass 5 | Stages | Cause |
| --- | --- | --- |
| R3: misread → exact | 1 | closed stage |
| R3: misread → same states | 24 | closed stage |
| R3n: misread → exact | 7 | closed stage |
| R3n: misread → same states | 14 | closed stage |
| R3n: misread → same states | 87 | the dependent-candidate flag (`dependent_kept`) |
| **Any other change** | **0** | |

- **Honest.** The fixes did exactly what Amendment 5 says. Both faults are real instrument faults; the closed-stage one is
  independently confirmed (Section 1). The note labels the pass-5 scoring post hoc and keeps the superseded preliminary numbers.
- **The fixes changed no prediction's direction.** Every change moves a misread to exact or same states, and the predictions that
  failed (C1, C1b, C3, N3, N4 first part) fail on pass 5 as well.
- **The wording point.** The dependent-candidate fix makes R3n return all n + 1 jointly dependent stars, the truth plus the loose
  set, when the table cannot say which star is the outside. The verdict then counts as "same states", since the extra star lies in
  the span.
  - **But it is not "another arrangement with the same allowed states".** It has one junction too many.
  - At meet-once stages, 154 of the 488 "same states" outputs are the truth plus one junction (`r3n_extra = 1, r3n_missed = 0` in
    pass 5's records).
  - So the note's "8% together" should be split: 334 other arrangements with the same states (5.4%), 40 outside swaps (0.6%) and
    154 the truth with the outside junction undecided (2.5%).

## 4. The headline numbers

Recounted from `runs/census-exact5` with the referee's own tally. **All of the following reproduce:**
- 100,024 stages and 2,353 read exactly;
- 24,385 arrangements (92%) with two knots sharing two;
- 93,808 such stages: 3 exact, 102 swaps, 8,471 same states, 85,232 misread;
- 6,216 meet-once stages: 2,350, 40, 488 and 3,338;
- 1,480 junction-moving stages: 549 by the search and 931 by twins beyond ten junctions; R3n exact on none;
- 1,944 stages with no such exchange: 1,330, 13, 79 and 522.

The horizon law, C4 and N4's second part, were not re-derived; they are read from the same records.

## 5. R3n and names

The referee's earlier check of R3n's tie rule (`research/RING-READ-20261118-001/referee-R1/r3n_check.py`, version 1 of R3n, run
read-only on the referee's own tables) supports the note's diagnosis:
- **R3n was exact** on Codex's 27-distinction history under 100 random renamings, both through D = 4 and with every distance, and
  on the ring under 10 renamings at each of rounds 10, 15, 20 and 25.
- **But the sum-growth step it shares with R3** prunes a running support by the order of the known junctions. On the ring's true
  junctions at round 25, 9 of 10 random orders returned a different set of sums at s = 10, though no output changed.
- **That is the step the note names** for its 51 stages that change under renaming. The referee did not prove it is the only
  source either.

## Corrections for the owner (listed, not folded in)

1. **"Same states" includes the truth plus the loose set** (R3n's dependent stars kept): 154 of the 488 at meet-once stages. Split
   them from "another arrangement with the same allowed states": 334 (5.4%) such arrangements, 40 outside swaps and 154 (2.5%)
   with the outside undecided, rather than "8% together".
   **Not a block (wording).**
2. **The symmetry-free class is 2,008 stages at ten junctions or fewer, not 1,944.** The 64 "unknown" stages have no
   junction-moving symmetry. R3n's exact share there is 69%. **Not a block (number).**

## How the work was split

- **The referee:**
  - read `census_read.md`, the pre-registration (Amendments 1 to 5), `exact_table_v2.py` and `job_exact3.py`;
  - wrote `referee_census.py` (tables, large, sym, amend5), on its FRESH-COUNT-R1, FIRST-KNOT-R1, 001F-R1, NAE-GROWTH-R1 and
    RING-READ-R1 code.
- **Read-only:** `exact_table_v2.py`, as the object under test.
- **Read as data:** passes 3 and 5's records (`runs/census-exact`, `runs/census-exact5`).
- **No reader or growth code of the study was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
