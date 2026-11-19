# Referee report VARIABLE-OUTPUT-READER-001M-R1 (fresh code, no Codex)

**Verdict: confirmed. No Block.**
- **Every number the coordinator listed reproduces** in the referee's own code: the width-22 swap, the census of 7,853 types
  through width 28, the width-32 pair (with {25, 27} a legal two-parent join on one side only), and the sixteen width-48 and
  width-49 continuations.
- **The finite frontier, rebuilt independently, matches the study's record for record:** 74,546 records and 484,418 transitions.
  - Every history keeps at least five loose distinctions (at most four shrinks).
  - No five-loose record has a legal triple.
- **The cutoff of four and the junction recovery hold** on every member to width 30, one width past the study's census.
  - In no member does a symmetry of the table through D = 4 move a junction or a legal triple.
  - Against every presentation the full law reaches at widths 18, 20, 22 and 24 (up to 672,424 types), none of another type
    matches a member through D = 4.
- **One scope point for the summary table** (Section 6). Against rivals from the other branches, three already fails for a
  one-parent source at width 20. There, a two-parent (001L) member with a legal triple shares its table through D = 3 with an
  empty-menu one-parent member. The study's 22 is the first width within the one-parent branch.
- **The summary table is now supported by the referee's own checks in all three rows** (Section 6), with the scope stated there.

The unary-third family: a ternary seed; two unary three-fresh additions; exactly one further unary three-fresh addition, at any
later time and any loose holder; every other addition two- or three-parent with two fresh. Its width is 2n + 4.

## 1. Cutoff four, sharp, at every size (the owner's first point)

**The census one width past the study** (`family_m.py`, `FAMILY=unary`; the referee's 001L code with the third addition's parent
count a parameter). Every member was grown by the family's own moves, the unary third at any legal time and holder. Symmetries of
each member's table were found exactly (twin quotient), through D = 3, through D = 4 and in full.

| Width | Members (study) | With a legal triple (study) | Live: a D ≤ 3 symmetry moves a triple | Live: a D ≤ 4 symmetry moves a support or a triple | Empty menu: a full-table symmetry moves a support |
| --- | --- | --- | --- | --- | --- |
| 18 | 21 (21) | 3 (3) | 0 | **none** | 0 |
| 20 | 54 (54) | 11 (11) | 0 | **none** | 0 |
| 22 | 160 (160) | 69 (69) | **6** | **none** | 0 |
| 24 | 523 (523) | 227 (227) | 21 | **none** | 0 |
| 26 | 1,719 (1,719) | 714 (714) | 143 | **none** | 0 |
| 28 | 5,359 (5,359) | 1,848 (1,848) | 430 | **none** | 0 |
| **30** | 14,754 (not run) | 3,947 | 1,268 | **none** | 0 |

- **The counts agree with the study's at every width,** 7,853 types through 28, including the members with at least two shrinks
  (10, 63 and 443 at 24, 26 and 28).
- **Width 22 is the first width where three fails;** at 18 and 20 no symmetry through D = 3 moves a triple.
- **No two distinct members have isometric tables**, through D = 4 or in full, at any width to 30.

**Against every rival the full law reaches** (`rivals_m.py`):

| Width | Full-law types | Members | Through D = 4: rivals of another type that match | Through D = 3: rivals of another type that match (live members, empty menus) |
| --- | --- | --- | --- | --- |
| 18 | 3,495 | 21 | **0** | 0 and 0 |
| 20 | 19,414 | 54 | **0** | 0 and 5; **4 of the 5 have a legal triple** where the member's menu is empty |
| 22 | 112,335 | 160 | **0** | 33 and 7; 31 and 1 change the menu |
| 24 | 672,424 | 523 | **0** | 73 and 216; 68 and 66 change the menu |

**The width-20 rivals.** The rivals that oppose an empty-menu one-parent member through D = 3 at width 20 (and the one at 22) are,
by isomorphism with the referee's 001L census, **members of the two-parent family** with legal triples. So against the whole class
of reachable rivals, three fails for a one-parent source at width 20. The study's own witness at 22 is the first *within* its
family, as `census.md` says ("the earliest such comparison within the unary-third family").

**The width-22 swap** (`referee_m_w22.json`), replayed from `census.json`:
- **It is legal and in the family.**
- **(12 18) keeps all 231 entries through D = 3.** 8 differ at D = 4 and 16 in full.
- **The verdicts.** {15, 18, 19} is legal and its image {12, 15, 19} is forbidden, because 12 is shared. The menu is {15, 18, 19},
  {16, 18, 19}.
- **The readings.** K(9, 12) = 5 and K(9, 18) = 7, that is D = 4 and 6. The least bonds through the mark and its image are 8 and 9.
- **Through D = 4, every symmetry keeps the menu and the supports.**
- **The width-28 J control** is in the family. Its swap (19 20) changes 0, 8, 16 and 30 entries through D = 3, 4, 5 and in full.

**"Four recovers the entire allowed-state relation."** The referee checked the consequence it can test literally. In every member
to width 30, every symmetry of the table through D = 4 keeps every junction support, and so the allowed states. With the rival
test, no other presentation reachable at widths 18 to 24 matches. The all-size statement rests on the study's forcing argument,
which the referee did not re-derive line by line. The rank bound it ends with is the one checked in the referee's 001L report.

## 2. At least five loose distinctions, at every size (the second frozen prediction)

`referee_m.py frontier`. The referee's 001L record closure was run with the unary third: a record holds the live holders' loose
counts, their adjacencies, and the exhausted holders' neighbourhoods projected to the live holders.
- **Every transition was also made literally** on a representative. The record was rebuilt from scratch, and the literal parent
  roster compared with the record's. **There were 0 mismatches.**
- **The study's fixed point, exactly.** Setting aside the referee's two start records and their three early unary transitions,
  there are **74,546 records and 484,418 transitions**, with 1,118 records before the unary third.
- **At most four shrinks**, so **at least five loose distinctions** at every depth. Four shrinks occur only with the unary third
  before all of them (the (0, 4) class: 27 records, no legal triple).
- **No five-loose record has a legal triple.**
- **No positive six-loose record has a shrink before the unary third.**

## 3. The width-32 pair (the owner's third point)

`referee_m_w32.json`, replayed from `examples.json`:
- **Both histories are legal and in the family.** The final supports are {24, 26, 28, 30, 31} and {25, 27, 29, 30, 31}.
- **All 496 entries agree on the same names, and the equation spaces are equal** (rank 14).
- **Both triple menus are empty.**
- **The two-parent menus differ.** One side has {25, 27}, {25, 29}, {27, 29}; the other {24, 26}, {24, 28}, {26, 28}. **{25, 27} is a
  legal pair on the first side, and both distinctions are already used on the second**, as stated.
- **So the table, and even the allowed states, do not fix a two-parent permission here.** The theorem is about three-parent
  choices, and the word "triple" is needed.
- **No full-table symmetry moves a support at any width below 32** (Section 1), consistent with 32 as the least width for this
  ambiguity.

## 4. The sixteen continuations of the width-46 example (the owner's fourth point)

`referee_m_cont46.json`. The referee rebuilt 001L's width-46 continuation of 001K's width-28 pair. It then joined each of the eight
legal triples, with two fresh distinctions (width 48) or three (width 49), the same on both sides:
- **All 16 are legal on both sides.**
- **All 16 keep identical tables on the same names**: all 1,128 entries at width 48 and all 1,176 at width 49.
- **All 16 next triple menus are empty on both sides.**

These continuations are outside all three families (they use further three-output joins), as the note says.

## 5. The ternary-third family, rechecked (for the summary table)

`family_m.py`, `FAMILY=ternary`, to width 30:
- **The first legal triples occur at width 26.** There, 7 live members have a symmetry through D = 4 that moves a legal triple, so
  four fails at 26, the first width it could.
- **Through D = 5, no symmetry moves a junction or a triple of a live member** at any width to 30.

## 6. The summary table (the coordinator's question)

| Parents at the third three-output join | Sharp cutoff | First width where one less fails | The referee's support |
| --- | ---: | ---: | --- |
| One (001M) | 4 | 22 | **Supported, with a scope note.** Within the branch three fails first at 22 (none at 18, 20). Against rivals from the two-parent branch it already fails at 20. Four holds on every member to width 30 and against every full-law rival at widths 18 to 24 |
| Two (001L) | 4 | 20 | **Supported.** Three fails at 20, the first width with a legal triple; four holds on every member to width 32 and against every full-law rival at widths 20 to 24 |
| Three (001K) | 5 | 26 | **Supported, with a lighter rival check.** Four fails at 26, the first width with a legal triple; five holds on every member to width 30. Against every full-law rival at widths 22 and 24 no other type opposes a member's (empty) menu through D = 4 or D = 5, so four does not fail earlier there. The rival census does not reach this family's first legal triple at 26, so against rivals the sufficiency of five rests on 001K's closure |

**So the table is supported** as a statement of the sharp cutoff for three-parent choices in each branch. The supporting evidence
differs by row:
- the census (self-symmetries) one width past each study;
- the literal all-rival test at widths up to 24;
- each study's all-size proof, checked by the referee at the argument level.

"The common sharp cutoff is five" follows (4, 4, 5).
- **The width column is the first width within each branch.**
- **Against rivals from all branches together**, three already fails for a one-parent source at width 20, the same width as the
  two-parent row. That changes no cutoff, so the table stands. If the column is read as "the first width at which one less fails
  for a source in this branch, against any reachable rival", the one-parent entry is 20.
- **Binary width 18:** the referee also tested the two-parent family against every full-law rival at width 18. No rival opposes
  there, so the two-parent row's 20 holds against rivals too.

## Corrections for the owner (listed, not folded in)

1. **The summary table's width column** (the one-parent row) is the first width within the branch. Against rivals from the
   two-parent branch, three already fails for a one-parent source at width 20. If the table is presented as the width "where one
   less fails" without "within the branch", say so or give 20. **Not a block (scope of a number)**; no cutoff changes.

The decision note already scopes the width-46 continuation ("in the wider law") and states the open cases.

## How the work was split

- **The referee:**
  - read `decision.md`, the pre-registration, `proof.md`, `census.md`, `frontier.md` and `incidence.md`;
  - wrote `family_m.py` (from its 001L `family_l.py`), `rivals_m.py`, `rivals_k.py` and `rivals_b18.py` (from `rivals_l.py`) and
    `referee_m.py` (frontier, w22, w32, cont46), on its 001F, 001G and 001L machinery.
- **The study's histories** (`census.json`, `examples.json`, 001L's `continuation.json`, 001K's `high_check.json`) were read as
  data.
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
