# Referee report VARIABLE-OUTPUT-READER-001N-R1 (fresh code, no Codex)

**Verdict: confirmed. No Block.**
- **Every number the coordinator listed reproduces** in the referee's own code:
  - the census of 50,681 four-addition types through width 27, with its live counts and its 296 opposing cross maps through D = 4;
  - the width-23 sharpness example;
  - the width-31 pair: 465 equal entries, different allowed states, the same three legal triples, the hidden junction holding an
    input of each.
- **"Settled through width 27" holds, and one width past.** On every member to width 29, no symmetry of the table through D = 5
  moves a junction or a legal triple of a live member. No two distinct members match through D = 5. Against every full-law rival
  at widths 19, 21 and 23, no other presentation matches through D = 5.
- **"The table loses which distinction was spent but keeps which joins can form next" is supported for the width-31 example.**
  - Of all 14 possible fourth junctions on the old prefix, exactly the two stated reproduce the table. Both have the same menu.
  - Every symmetry of the table keeps that menu while moving the junction.
  - Every common continuation to depth two keeps the named menus equal.
  - The all-rival step rests on the study's rank argument together with 001L's theorem, which the referee confirmed. It is a
    statement about this example and the studied branch, not yet a general law (Section 5).

The four-addition family: a ternary seed, the only three-place site; the first two additions unary with three fresh; exactly two
further three-fresh additions, each with one, two or three parents, at any time; every other addition two- or three-parent with
two fresh. Its width is 2n + 5.

## 1. The census through width 27, and one past

`family_n.py` (the referee's 001L and 001M family code with this family's moves) grew every member up to isomorphism. Each
member's table was tested exactly (twin quotient) through D = 3, 4 and 5 and in full.

| Width | Members (study) | Live (study) | Live: a D ≤ 4 symmetry moves a triple | Live: a D ≤ 5 symmetry moves a support or a triple | Cross-type maps through D = 4 that change a menu (study) | Distinct types matching through D = 5 or in full |
| --- | --- | --- | --- | --- | --- | --- |
| 19 | 168 (168) | 10 (10) | 0 | **none** | 0 (0) | 0 |
| 21 | 593 (593) | 116 (116) | 0 | **none** | 0 (0) | 0 |
| 23 | 2,267 (2,267) | 870 (870) | **6** | **none** | 3 (3) | 0 |
| 25 | 9,376 (9,376) | 4,230 (4,230) | 33 | **none** | 15 (15) | 0 |
| 27 | 38,204 (38,204) | 17,893 (17,893) | 257 | **none** | 278 (278) | 0 |
| **29** | 151,341 (not run) | 62,064 | 814 | **none** | 949 | 0 |

- **The populations agree with the study at every width** (21 and 52 at 15 and 17, as well). The total through 27 is 50,681, and
  23,119 are live.
- **The opposing cross maps agree too.** 3 + 15 + 278 = 296, as the study counts.
- **Five suffices and four fails first at 23,** in self-symmetries and in cross maps.
- **Width 29 holds one empty-menu member whose full table hides a junction** (`referee_n_w29_hidden.json`):
  - the exchange (22 25) keeps every distance;
  - it moves the six-place fourth junction {13, 20, 22, 26, 27, 28} to {13, 20, 25, 26, 27, 28};
  - it changes the allowed states and the two-parent menu.

  Its triple menu is empty, so no three-parent verdict changes. That agrees with the study's "width 31 is the first instance of the
  terminal sibling exchange with a live fresh mark".

**Against every rival the full law reaches** (`rivals_n.py`):

| Width | Full-law types | Members | Through D = 5: rivals of another type that match | Through D = 4: rivals of another type that match and change a live member's menu |
| --- | --- | --- | --- | --- |
| 19 | 8,191 | 168 | **0** | 0 |
| 21 | 46,449 | 593 | **0** | 0 |
| 23 | 273,842 | 2,267 | **0** | 6 |

The study's rival certificate is a rank argument (forced stars, the width identity, the minimum-width family). It was read and its
steps check: a matching rival has one ternary site and an even number of further three-output additions, so rank n + 1 would need
exactly two, and the minimum-width inverse excludes that. The literal rival test above agrees with it wherever it reaches.

## 2. The width-23 sharpness example

`referee_n_w23.json`, replayed from `census.json`:
- **It is legal and in the family.** The fourth site is {9, 12, 13, 20, 21, 22}: three parents, three loose outputs.
- **(12 18) keeps all 253 entries through D = 4;** 10 differ at D = 5 and in full.
- **The verdicts.** {15, 18, 19} is legal and {12, 15, 19} forbidden. D(9, 12) = 5 and D(9, 18) = 7. The least bond through either
  mark has 9 distinctions.
- **Through D = 4, symmetries move both the menu and the fourth site. Through D = 5, every symmetry keeps both.**

## 3. The width-31 pair (the coordinator's main point)

`referee_n_w31.json`, from `frontier.json`'s literal histories:
- **Both histories are legal and in the family.** The fourth supports are {15, 23, 26, 28, 29, 30} and {15, 23, 27, 28, 29, 30}.
- **All 465 entries agree on the same names.**
- **The equation spaces differ.** The state with ones at 24, 25, 27 is allowed on the first side only.
- **Both menus are exactly {17, 25, 28}, {17, 25, 29}, {17, 25, 30}.** The hidden junction holds a loose input of every one: it is
  the holder of 28, 29 and 30.
- **(26 27)** is a symmetry of the table and carries one history's supports onto the other's.
- **The least bonds** through {15, 26, 28} are 6 and 9; through {17, 25, 28}, 6 and 6.

**"Exactly two assignments fit this table."**
- **The old prefix** (the twelve earlier junctions, width 28) is legal and in 001L's binary-third family. Its menu is exactly
  {15, 23, 26} and {15, 23, 27}.
- **On that prefix, every possible fourth junction with three fresh outputs 28, 29, 30** was built: 14 candidates, every legal
  parent group of one, two or three holders, every choice of loose distinctions.
  - **Exactly 2 reproduce the table on the same names**: the two stated supports.
  - **Exactly 2 are isometric to it under any renaming**, and each such isometry carries the menu onto the candidate's.
- **The all-rival step.** Through D = 4 a rank-12 space is forced; 28, 29, 30 lie in none of its equations; one six-place sink
  must hold them; erasing it leaves the old space. These steps are the study's (`rank.md`, `inverse_fixtures.md`), and were read
  but not re-derived. 001L's theorem, which the referee confirmed, then fixes the old prefix's supports. So every rival is the
  prefix plus a sink on one of its two legal triples, which is what the referee enumerated.
- **The table's own symmetries keep the menu** (in full and through D = 4 and D = 5) **while moving the support.**
- **Four is sharp for this example.** (24 25) keeps all 465 entries through D = 3, with 8 differing at D = 4, and takes the legal
  {17, 25, 28} to the forbidden {17, 24, 28}.
- **Common continuations.** All 10 common two-output first moves, and all 12 second moves after them, keep the named triple menus
  equal on both sides. The study's 47-record closure covers every depth; the referee checked depth two.

## 4. Plainly: does the table lose which distinction was spent while keeping which joins can form next?

**Yes, for this example.**
- **It loses which distinction was spent.** The fourth junction spends 26 or 27, two distinctions of one older holder. The two
  choices give different equations and different allowed states on the named distinctions, yet identical distances.
- **It keeps which joins can form next.** Every presentation that fits the table has the same three legal triples. The hidden
  junction is the holder of the third input of each, so here, for the first time, the hidden junction is itself a parent of the
  legal joins. That stays so along every common continuation checked.

**What it does not show.**
- **This is not yet a general law for four additions.** The study's all-size theorem covers the branch where the fourth junction
  takes three parents and keeps its outputs loose. Beyond it, whether an exact table match can change a three-parent verdict is
  open (the note says so).
- **The referee's census to width 29 finds no such change,** live or empty.
- **The two-parent permissions are not kept** (at width 29 they change with the hidden junction), so "which joins" means
  three-parent joins.

## Corrections for the owner (listed, not folded in)

None. The decision note states its scope: the branch theorem, the finite interval through 27, and the open general case.

## How the work was split

- **The referee:**
  - read `decision.md`, the pre-registration, `census.md`, `inverse_fixtures.md`, the census's rank certificate and `frontier.json`'s
    histories;
  - wrote `family_n.py` (from its 001M `family_m.py`), `cross5.py`, `rivals_n.py` (from `rivals_l.py`) and `referee_n.py` (w23,
    w31), on its 001F, 001G and 001L machinery.
- **The study's histories** (`census.json`, `frontier.json`) were read as data.
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
