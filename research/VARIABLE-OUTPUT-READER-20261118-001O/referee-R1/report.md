# Referee report VARIABLE-OUTPUT-READER-001O-R1 (fresh code, no Codex)

**Verdict: confirmed. No Block.**
- **Every number the coordinator listed reproduces** in the referee's own code:
  - the width-25 survival: six triples before the spend, exactly the four avoiding 18 after it, the fourth junction still holding
    19 or 20;
  - the census of 3,476 types through width 29, with distance four failing at 23;
  - the width-31 case with eight legal triples.
- **One width past, at 31** (8,621 types), distance five still fixes every junction and every legal triple of every member. No two
  distinct members match through D = 5 or in full. Against every presentation
  the full law reaches at width 23 (273,842 types), none of another type matches a member through D = 5. Wider rival censuses
  were not run, for time and memory, so beyond 23 the all-rival part rests on the study's rank certificate and support-level
  inverse.
- **The all-size step John quotes is sound at the argument level.** The low equations span everything but the two surviving
  outputs, so every rival equation restricts to them as 00 or 11. Two sites cannot share two distinctions, so both outputs are
  loose at one site.
  - The rest of the proof chains earlier results (the formation closure, the protected-bit lemma, the equal-state rigidity
    theorem). They were read, not re-derived.
  - As the note says, the overlapping-attachment case is open, so the menu is proved at all sizes only on the stated branches.

The one-spent family: a ternary seed, the only three-place site; two unary three-fresh additions; a third three-fresh addition
with one, two or three parents; a fourth with three parents; exactly one of the fourth junction's outputs then used, by a two- or
three-parent two-fresh join; every other addition two- or three-parent with two fresh, never using the fourth junction again. Its
width is 2n + 5.

## 1. The census through 29, and one past

`family_o.py`. Members were grown with the fourth junction marked, by the family's own moves, and then counted as unmarked
physical types. Each member's table was tested exactly (twin quotient) through D = 3, 4 and 5 and in full.

| Width | Physical types (study) | Live (study) | Live: a D ≤ 4 symmetry moves a triple | Any member: a D ≤ 5 symmetry moves a support or a triple | Distinct types matching through D = 4 (menu changed) | Through D = 5 or in full |
| --- | --- | --- | --- | --- | --- | --- |
| 23 | 4 (4) | 2 (2) | 2 | **none** | 0 | 0 |
| 25 | 74 (74) | 27 (27) | 13 | **none** | 1 (1) | 0 |
| 27 | 544 (544) | 214 (214) | 138 | **none** | 94 (63) | 0 |
| 29 | 2,854 (2,854) | 895 (895) | 348 | **none** | 500 (272) | 0 |
| **31** | 8,621 (not run) | 2,394 | 1,010 | **none** | 2,358 (1,100) | 0 |

- **The populations agree with the study: 3,476 through 29.** The study's 2,858 "tag orbits" at 29 also mark the child and the
  spend's timing; the physical count is the same.
- **The cross matches through D = 4 agree.** 0 + 1 + 94 + 500 = 595, the study's figure. The referee's count of those changing a
  menu is 336, against the study's 337 "admitting an opposing mark". The referee tests one isometry per pair, so its count is a
  lower bound.
- **Distance five suffices** at every width to 31, for empty and live members alike; four fails first at 23.
- **Every surviving pair of outputs stays loose together.** Because every symmetry through D = 5 keeps every support, the two
  surviving outputs of the fourth junction always map to the two loose distinctions of one junction.

**Against every rival the full law reaches** (`rivals_o.py`). At width 23, the family's first width, all 273,842 full-law types
were tested. No rival of another type matches a member through D = 5, or through D = 4. So at width 23 the D ≤ 4 failures are
self-symmetries.

## 2. The witnesses

`referee_o_w23.json`, `referee_o_w25.json`, `referee_o_w31.json`, replayed from `frontier.md` and the study's JSON files:
- **Width 23** (`frontier.md`). The spend creates the first two triples. The menu is empty just before and {5, 11, 21}, {5, 11,
  22} just after. Through D = 4, symmetries move the menu and the supports; through D = 5 and in full they keep both.
  - `census.json`'s swap (10 16) keeps all 253 entries through D = 4, with 10 differing at D = 5 and 16 in full. It takes the legal
    {14, 16, 21} to the forbidden {10, 14, 21}. The least bonds through them are 9 and 11.
- **Width 25** (the first eight sites, then (5, 8, 21, 22), then the spending child (13, 18, 23, 24)).
  - **The fourth junction is {7, 10, 16, 18, 19, 20}.**
  - **Before the spend the menu is the six triples {15} × {18, 19, 20} × {21, 22}. After it the menu is exactly the four of them
    that avoid 18,** so each surviving triple still takes 19 or 20 from the fourth junction.
  - Through D = 5 every symmetry keeps the menu and the supports. Through D = 4 the menu is kept but supports move.
- **Width 31** (`residual.json`'s fixture).
  - It is in the family. The fourth junction {8, 10, 20, 22, 23, 24} has spent 22 to the child {13, 22, 25, 26}, and both of the
    child's outputs 25 and 26 have been spent by later joins.
  - **The menu is the stated eight triples.**
  - **Every symmetry of the table, in full, through D = 5 and even through D = 4, keeps all eight and every support.**
- **The study's rival inverse at width 31** (forced rank 13 through D = 5, one physical explanation) was read, not re-run. The
  referee's checks there are of the table's own symmetries.

## 3. The all-size theorem (`live_low_span.md`), at the argument level

- **The rank step** (the sentence in John's summary).
  - The n − 1 low equations are forced and span L, whose supports avoid the surviving outputs F = {a, b} and cover every other
    distinction.
  - The width identity bounds the rival's rank by n, so exactly one more independent equation meets F, and its restriction to F is
    11.
  - Every rival star therefore contains both a and b or neither. Two stars cannot share both, so a and b are loose together at
    one rival site, six-place by their row minimum. The step is correct.
- **"Two different completions must share an attachment."** Shores of size six containing the six-place site are closed under
  union, by submodularity and the minimum of six. So a disjoint alternative attachment would make the rival's six-place star a
  source equation. Equal-state rigidity, a result from 001M that the referee confirmed, then forbids a support change. The
  argument holds.
- **Not re-derived:**
  - the formation closure (47,640 records; at most two shrinks on a live one-spent source);
  - the recovery of the low sites when two shrinking joins are present;
  - the exclusion of the shrink-to-boundary exchange.

  The census above agrees with all of them to width 31.
- **Open, as the note says:** an overlapping attachment that keeps the table and changes a triple. The census finds none to width
  31.

## Corrections for the owner (listed, not folded in)

None. The decision note states its scope: the branch theorems, the finite interval through 29, and the open overlapping-attachment
case. One count differs by one (337 against the referee's 336 opposing cross matches through D = 4). The referee's count is a
lower bound, and the difference does not change any claim.

## How the work was split

- **The referee:**
  - read `decision.md`, the pre-registration, `census.md`, `frontier.md` and `live_low_span.md`;
  - wrote `family_o.py` (from its 001N `family_n.py`), `cross5.py`, `rivals_o.py` and `referee_o.py` (w23, w25, w31), on its 001F,
    001G, 001L and 001N machinery.
- **The study's histories** (`frontier.md`'s listed supports, `census.json`, `residual.json`) were read as data.
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
