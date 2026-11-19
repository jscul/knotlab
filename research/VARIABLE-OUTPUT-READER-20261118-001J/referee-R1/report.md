# Referee report VARIABLE-OUTPUT-READER-001J-R1 (fresh code; one labelled cross-check runs RING-READ's reader)

**Verdict: confirmed. No Block.** The seven-to-six example, the all-size family with cutoff D = 4 and its 25-distinction sharp swap
all reproduce. The family theorem holds exhaustively against every reachable rival at widths 9 to 23.

**The claim against our own RING-READ reader also reproduces.**
- **The finding.** On 001J's 27-distinction example, exchanging names 0 and 24 makes the published reader return the five loose
  distinctions as a junction and miss two real ones. This happens even from all 351 exact distances.
- **For RING-READ it is Not a block.**
  - The finding is outside RING-READ's class: it is a serial-law example, not the ring.
  - On the ring itself, 56 random renamings at seven rounds (10 to 25) all give every junction exactly.
  - No RING-READ claim fails. The tie rule is a property of the implementation that the ring never exercises.

## 1. The smallest seven-to-six event (21 distinctions)

`referee_j_event21.json`, replayed from `search.json` under the referee's law, with tables from the referee's own shore enumeration.

| | Before | After |
| --- | --- | --- |
| Junctions, width | 8, 19 | 9, 21 |
| History legal | yes | yes |
| Legal triples | **8** | **0** |
| Loose distinctions | 10, 13, 14, 15, 16, 17, 18 (seven) | 10, 14, 16, 18, 19, 20 (six) |
| The six are an equation | | **yes** (their 15 pair minima: one at K = 5, fourteen at K = 6) |

**The comparator** is the reachable history with a real six-place junction on exactly those six names. It is legal and has 8
junctions.
- **14 of the 15 internal pairs are equal** on the same names.
- **82 full entries differ.**
- **The clipped tables are isometric through K = 3 only.** No isometry exists at K = 4 or above (D through 3, as the decision note
  says), and the full tables are not isometric.

## 2. The all-size family (cutoff D = 4) and its sharpness

**The proof checks at the argument level** (`family.md`).
- **The width.** Width is m = 2n + 1 + r. The first two additions must be unary, and must be three-fresh under a single ternary seed,
  so the family is exactly the minimum-width branch, m = 2n + 3.
- **The loose count.** It is 7 after the two unary sites. Binary two-fresh joins keep it, and each shrinking join lowers it by one.
- **Short shores.** A shore of three or more sites has cut at least 5. A 5-cut must use both shrinking sites with all their parents
  inside, so no input of a shrinking site lies in it.
- **The five-place stars are forced.** Two input arms are chosen with distinct, same-colour opposite endpoints, one of which avoids
  the seed. Then no outside bit is within K ≤ 5 of both, so the rival bond realizing their K = 5 is the whole star.
- **The rank closes the gap.** The width bound gives n′ ≤ n for the rival, and n forced independent equations give n′ = n and equal
  spaces.
- **The exterior is identified.** When the exterior has five bits, a rival exterior would need complementary lawful triples one
  step earlier. The finite closure excludes that.
- **Not re-run:** the closure itself (1,118 records, 4,997 transitions).

**Exhaustive against every reachable rival** (`referee_g`-style check on the referee's census, `referee_j_family.json`). Every type
with a family history was tested: 163 sources at widths 9 to 23, 50 of them with legal triples.

| Width | Family sources | With a legal triple | Through K = 5 (D ≤ 4) | Through K = 4 (D ≤ 3) |
| --- | --- | --- | --- | --- |
| 9 to 17 | 14 | 0 | no failure | no failure |
| 19 | 14 | 4 | no failure | no failure |
| 21 | 36 | 17 | **no failure** | a clipped symmetry moves a support in 4; no triple verdict changes |
| 23 | 99 | 29 | **no failure** | supports moved in 23; 6 isometric rivals; no triple verdict changes |

**The 25-distinction sharp swap** (`referee_j_sharp25.json`):
- **It is in the family:** the seed, then two unary three-fresh additions, then only two- or three-parent two-fresh ones. It is legal.
- **All 300 pairs agree after (19 20) through K = 4** (D through 3), and **8 differ at K = 5**.
- **The mark {12, 20, 21} is legal**, and its image {12, 19, 21} is forbidden.
- **So D = 4 is sharp for a triple verdict at width 25.** Through width 23, D = 3 already loses junction identity but no verdict.

## 3. The claim against RING-READ's reader (the coordinator's main question)

`ring_tie.py` is a **labelled cross-check**. It imports the published `reader3.py` read-only and unmodified, and feeds it tables the
referee computed itself.

**On 001J's 27-distinction history** (two shrinking joins, 12 junctions, largest 5; `referee_j_ring_tie.json`), with the referee's
exact table:

| Table given to the reader | Original naming | Names 0 and 24 exchanged |
| --- | --- | --- |
| pooled above D = 4 | every junction | **misses {10, 16, 19, 21, 22} and {14, 18, 23, 25, 26}; returns {21, 22, 24, 25, 26}** (the five loose distinctions, a true bond) |
| pooled above D = 5 | every junction | the same failure |
| every exact D (through 8) | every junction | the same failure |

Only 5 of 8 further random renamings read it exactly at D = 4. **So the reader's answer depends on the names here**, exactly as
ring.md says: it accepts tied candidates in name order. By 001J's theorem, the table through D = 4 determines the answer uniquely.

**On the ring itself** (`referee_j_ring_tie.json`, `referee_j_ring_tie_late.json`), with the referee's exact all-sides table:

| Round | Junctions | Largest | The study's naming | Eight random renamings giving every junction exactly |
| --- | --- | --- | --- | --- |
| 10 | 120 | 7 | exact | 8 of 8 |
| 12 | 165 | 7 | exact | 8 of 8 |
| 14 | 225 | 7 | exact | 8 of 8 |
| 15 | 261 | 8 | exact | 8 of 8 |
| 16 | 301 | 8 | exact | 8 of 8 |
| 20 | 526 | 9 | exact | 8 of 8 |
| 25 | 1,024 | 10 | exact | 8 of 8 |

**Classification for RING-READ: Not a block.**
- **Every RING-READ claim stands.** That study claims its reader only for the ring, where the referee found no naming dependence in
  56 random renamings.
- **Why the ring never exercises the tie.** On the ring the exterior bond holds hundreds of loose distinctions, far above any
  junction's size. On 001J's example it has five, the size of a real junction.
- **No correction.** At most a clarifying line: RING-READ's reader breaks ties between equal candidates by distinction name; it was
  checked naming-independent on the ring only, and 001J gives a serial-law table on which a renaming changes its output.

## Fixes for the owner (listed, not folded in)

None for 001J. For RING-READ, the clarifying line above is optional and **Not a block**.

## How the work was split

- **The referee:**
  - read `decision.md`, `ring.md`, `family.md`, `search.md` and the data files;
  - wrote `referee_j.py` (event21, sharp25 and family, on the referee's 001F-R1 census, tables and exact isometries) and
    `ring_tie.py` (the labelled cross-check).
- **Codex's code** was not imported or run.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Reproduction

Run from this folder.

| Command | Wall time |
| --- | --- |
| `referee_j.py event21` | 1 s |
| `referee_j.py sharp25` | 1 s |
| `referee_j.py family 23 9` | 6 min |
| `ring_tie.py` | 22 s |
| `ring_tie.py late` | 5 min |
