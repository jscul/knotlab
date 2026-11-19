# Referee report VARIABLE-OUTPUT-READER-001L-R1 (fresh code, no Codex)

**Verdict: confirmed. No Block.**
- **Every number the coordinator listed reproduces** in the referee's own code: the width-20 swap, the width-32 pair, the
  continuation of 001K's width-28 pair and the width-46 example.
- **The finite frontier, rebuilt independently, matches the study's record for record:** 28,108 records and 181,530 transitions,
  and every row of its table.
- **The cutoff of four and the junction recovery hold** on every family member to width 32, one width past the study's census.
  - In no member does a renaming that keeps the table through D = 4 move a junction or a legal triple.
  - The full law reaches 672,424 presentations at width 24. Against every presentation it reaches at widths 20, 22 and 24, none of
    another type matches a member through D = 4.
- **The all-size proof checks at the argument level** at the four steps the conclusion rests on (Section 2).
  - The forcing lemmas of `structural.md` were not re-derived line by line. Beyond the widths above, the all-rival claim rests on
    them.
- **On the referee's 001K wording (the coordinator's question).** The width-46 example does not contradict it as written, because
  that sentence was about the 001K family. But it shows the sentence must not be read as a general rule. Under the full law a
  table symmetry can move a junction while eight triples are legal (Section 7).

The binary-third family: a ternary seed; two unary three-fresh additions; exactly one two-parent three-fresh addition B; every other
addition two- or three-parent with two fresh. Its width is 2n + 4. Below, "through D = d" means the table of least bond sizes K =
D + 1, clipped above d + 1.

## 1. The cutoff four at every size, and a legal triple identifying every junction (the owner's first two points)

**A census one width past the study** (`family_l.py`). Every family member was grown by the family's own moves and deduplicated up
to isomorphism. For each member the referee computed its full table, its legal triples, and whether every symmetry of the table
keeps the junction supports and the legal triples. Symmetries are found exactly, by the twin quotient of the referee's 001F code,
through D = 3, through D = 4 and in full.

| Width | Members (study) | With a legal triple (study) | Live: a symmetry through D = 3 moves a triple | Live: a symmetry through D = 4 moves a support or a triple | Empty menu: a full-table symmetry moves a support |
| --- | --- | --- | --- | --- | --- |
| 20 | 78 (78) | 18 (18) | 7 | **none** | 0 |
| 22 | 257 (257) | 113 (113) | 54 | **none** | 0 |
| 24 | 919 (919) | 373 (373) | 188 | **none** | 0 |
| 26 | 2,979 (2,979) | 1,228 (1,228) | 738 | **none** | 0 |
| 28 | 9,617 (9,617) | 2,780 (2,780) | 1,553 | **none** | 0 |
| 30 | 25,055 (25,055) | 5,860 (5,860) | 3,778 | **none** | 0 |
| **32** | 61,235 (not run) | 8,617 | 4,820 | **none** | **5**, all with three shrinks; the study's width-32 pair is one of them |

- **The counts agree with the study's at every width**, including the members with at least two shrinks (19, 314 and 1,391 at 26,
  28 and 30) and the 352 such members with a legal triple.
- **Through D = 4, no symmetry moves a legal triple or a junction of a member with a legal triple,** at any width to 32.
- **Through D = 3, symmetries move legal triples at every width from 20.** So three is not enough at any size, as the study says.
- **Distinct types never match.** At every width to 32, no two distinct members have isometric tables, through D = 4 or in full.
  Every full-table invariant is unique to its type, as the study found through 30.
- **Width 32 is the first width where a symmetry of the table through D = 4, or of the full table, moves a junction, and it happens
  only where the menu is empty.** There are five such types, all with three shrinks, and the study's pair is one of them
  (Section 5). Below 32 there are none, live or empty. (Through D = 3, symmetries move junctions at every width.)

**Against every rival the full law reaches** (`rivals_l.py`). The rivals are every presentation of the full law at the member's
width (one to three parents, two or three fresh), from the referee's 001F census. Each was tested for an exact isometry wherever
its clipped table shares an invariant with a member's.

| Width | Full-law types | Members | Through D = 4: rivals of another type that match | Through D = 3: rivals of another type that match (live members, empty menus) |
| --- | --- | --- | --- | --- |
| 20 | 19,414 | 78 | **0** | 26 and 71; all 26 against live members change the menu |
| 22 | 112,335 | 257 | **0** | 211 and 194; 207 of the 211 change the menu |
| 24 | 672,424 | 919 | **0** | 736 and 1,348; 699 of the 736 change the menu |

**The study runs no such literal all-rival test.** Its rival part is a proof (a width identity, a rank bound and
forcing lemmas), plus a forced-code search on the four width-30 sources with three shrinks.

## 2. The all-size proof, at the argument level

The referee checked four steps:
- **The width identity and the rank bound.** A rival with r sites and a nonseed three-output additions has width 2r + 1 + a. Its
  only bond of size three is the seed, read at K = 3. So its first two additions are unary and three-fresh: a two-fresh unary site,
  or a binary second addition (the seed and its child have no common neighbour), is impossible. With an even width, a is odd and at
  least 3, so r ≤ n. Forced source equations then give r = n and equal equation spaces.
- **The exterior step.** With equal spaces and a three-connected wired graph, both presentations have the same augmented stars. A
  bit is loose in both exactly when it joins the two candidate exteriors, so all such bits have one ordinary holder. A legal triple
  transfers under equal allowed states and needs three holders, so the exterior, and with it every junction, is fixed. The width-32
  pair is exactly the exchanged-exterior case with an empty menu, as the argument predicts: the bits loose in both are 30 and 31, at
  the last junction.
- **The four-loose clique argument** (`four_loose.md`).
  - A rival with a legal triple needs at least five loose bits, because the exterior is a bond and triple pairs read K ≥ 5.
  - Building a large four-shore first would leave four loose bits, which cannot rise again. So such a rival has no large
    four-shore, and its bonds through four are single stars of three or four places.
  - The six bits of H₁ read pairwise K = 4, from the three four-words named in the note, which cover all fifteen pairs. In a
    triangle-free wired graph, pairwise-meeting edges share one vertex, so the six would lie in one star of size at most four.
    That is a contradiction. The step is sound.
- **The four-shrink rank count.** The H₁ pair forces two independent rival words, and each later binary site forces one more, for
  n in all. The count is correct as written.

**Not re-derived:** the protected-bit lemma and the three-shrink case analysis of `structural.md`. The census and the rival test
above are consistent with them at every width checked.

## 3. The frontier, rebuilt independently

`referee_l.py frontier` closes the loose-holder records with its own code. A record holds each live holder's loose count, the
adjacencies among live holders, and the distinct neighbourhoods of exhausted holders, projected to the live ones, with at least two
members. It also holds the phase and the shrinks before B. Records are canonical up to renaming the live holders.
- **Every transition was also made literally.** On a representative presentation, the record was rebuilt from scratch and compared;
  the literal parent roster was compared with the record's. **There were 0 mismatches in 28,110 records and 181,533 transitions.**
- **Setting aside the referee's two start records** (the seed and the seed with one child) **and their three unary transitions**,
  this is exactly the study's **28,108 records and 181,530 transitions**, with **1,118 records before B**.
- **Every row of the study's table reproduces:** records, records with a legal triple, earliest width and first positive width,
  for all ten (shrinks before B, total shrinks) classes. For example 19,356 / 7,062 / 12 / 20 at (0, 0), and 34 / 1 / 28 / 30 at
  (0, 3).
- **At most four shrinks,** and four only with B before every shrink.
- **Exactly one five-loose record has a legal triple:**
  - its loose counts are 1, 1, 1, 2 and its first width is 30;
  - it has no binary predecessor among the five-loose records;
  - none of its four successors has a legal triple.
- **The one four-loose record** (loose counts 1, 1, 2) has a single binary move, back to itself.

## 4. The width-20 witnesses (the owner's third point)

`referee_l_w20.json`, replayed under the referee's law with its own shore tables:

| Witness | In the family | Pairs equal through D = 3 | Differ at D = 4 | Differ in full | Mark | Least bond through the mark |
| --- | --- | --- | --- | --- | --- | --- |
| Self swap (9 14) | yes | **190 of 190** | **8** | 12 | {12, 14, 18} legal, image {9, 12, 18} forbidden | 8 and 9 |
| Cross (8→9→12→8, 11↔13) | both | 190 of 190 | 14 | 35 | {11, 15, 17} forbidden, image {13, 15, 17} legal | 10 and 8 |

- **The self swap moves the support {5, 9, 11, 16, 17}.** Every symmetry through D = 4 keeps both the menu and the supports.
- **In the cross witness,** the left menu is empty and the right has 12 triples. The two tables are not isometric through D = 4 at
  all.
- **The width-26 control** (the J witness plus a loose 25) is in the family. Its swap (19 20) changes 0, 8, 8 and 24 entries through
  D = 3, 4, 5 and in full; the mark is legal and its image forbidden.

## 5. The width-32 pair (the owner's fourth point)

`referee_l_w32.json`:
- **Both histories are legal and in the family.** The final supports are {22, 26, 28, 30, 31} and {23, 27, 29, 30, 31}.
- **All 496 entries agree on the same names.**
- **The equation spaces are equal:** rank 14 and 2¹⁸ = 262,144 allowed states, with 5,206 bonds on each side.
- **Both menus are empty.** The prefix had the eight triples stated.
- **The swap (22 23)(26 27)(28 29)** preserves the table and carries one history's supports onto the other's.
- **The minimum:** no full-table symmetry or cross-type isometry moves a support at any width below 32 (Section 1).

## 6. 001K's width-28 pair continued (the owner's fifth point)

`referee_l_cont28.json`:
- **The base.** Both histories are legal, and all 378 entries are equal.
- **The six common narrow first moves** are {23, 24} × {25, 26, 27}. **Each changes exactly 4 of 435 entries:** K(21, 28) =
  K(21, 29) = 8 on the left and 6 on the right, and the reverse for 22. **Each first separates at D = 5.**
- **One size past, every common second move** (12 histories) changes 8 entries. **Every common third move** after (23, 25)
  (8 histories) changes 12. All first separate at D = 5. This matches the proof's uniform D = 5 statement.
- **The binary menus after (23, 25)** are {22, 28}, {22, 29}, {24, 26}, {24, 27} on the left, with 21 for 22 on the right.
- **The six-step history** reaches width 40 on both sides with {33, 36, 38} legal.
- **Under the full law:**
  - 22 is loose only on the left and 21 only on the right;
  - all ten common unary first steps (23 to 27, two or three fresh) leave the tables equal;
  - every common binary three-output first step changes 6 entries, 7 against 9.
- **The swap (21 22)** carries the left presentation onto the right one, so every lawful future transports.

## 7. The width-46 continuation, and the referee's 001K wording (the coordinator's question)

`referee_l_cont28.json`, "width 46":
- **The history.** Unary three-fresh additions on 23, 28, 29 and 30, then binary two-fresh ones on (31, 34), (32, 37) and
  (35, 38). It is legal under the full law on both sides, and **not in the binary-third family**.
- **All 1,035 entries are equal on the same names.**
- **The equation spaces differ.** The six-place junction is {12, 20, 21, 25, 26, 27} on one side and {12, 20, 22, 25, 26, 27} on
  the other: the junction is hidden.
- **The menus are identical.** They have exactly the eight triples one from each of {40, 41}, {42, 43}, {44, 45}, and the
  control {40, 41, 42} is forbidden.
- **(21 22) is a symmetry of the left table** and carries the left supports onto the right.

**How it sits with the referee's 001K wording, plainly.** The 001K report said, of the 001K family's members to width 30: "Width 28
is the first width where a full-table symmetry moves a junction … It happens only where the menu is empty."
- **Within the 001K family, and within this family to width 32, that stands.**
- **It is not a general rule.** At width 46, under the full law, a full-table symmetry moves a junction while eight triples are
  legal. The menu is still the same on both sides there; what fails is the junction identification.
- **So "a hidden junction occurs only with an empty menu" holds inside the families checked and is false under the full law.**
- **The suggested 001K wording keeps** "the three-parent menu is still determined". Its last clause, "through distance five it is
  fixed whenever a triple can join", is about the 001K family. The referee has added a scope note to its 001K report.

## Corrections for the owner (listed, not folded in)

1. **The referee's 001K wording** "a full-table symmetry moves a junction only where the menu is empty" holds within the families
   checked (001K's to width 30, this one to width 32). Under the full law it is false (width 46). Scope it to the family. The
   referee's 001K report now carries that note. **Narrowing (the referee's own wording); not a block.**

No correction to 001L is needed. The decision note already scopes the width-46 example ("lies outside the present source class")
and states the open branches.

## How the work was split

- **The referee:**
  - read `proof.md`, `structural.md`, `four_loose.md`, `frontier.md`, `census.md`, `empty_witness.md`, `continuation.md` and
    `rival.md`;
  - wrote `referee_l.py` (frontier, w20, w32, cont28), `family_l.py` (gen, examine, cross) and `rivals_l.py`, on its 001F and 001G
    machinery.
- **The study's histories** (`census.json`, `empty_witness.json`, `continuation.json`, 001K's `high_check.json`) were read as data.
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
