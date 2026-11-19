# Referee report RING-READ-001-R1 (fresh code; one labelled cross-check runs the study's reader)

**Verdict: confirmed, with one Narrowing. No Block.**

The headline holds at every round, including one size past the study (round 30): the table gives back every junction, and the
reader needs distances exactly to the largest junction less one.

The study's completeness argument for the table does not hold as written. The owner asked about this point.
- **Bonds of ten distinctions with two large sides exist from round 10 on.** They are cuts near the start that wrap the ring.
- **Inside the reader's horizon they change no entry at rounds 10 to 25.** The side-limited table is exact there.
- **At round 25 they make 6 entries at D = 10 wrong.** That is the table's last kept value, one past the reader's horizon.
- **At round 30 those 6 entries fall inside the horizon.** The study's own reader still returns all 1,960 junctions from both the
  side-limited table and the exact one.

## 1. Is the table complete for bonds with two large sides? (the owner's question)

**Method.** The referee wrote an exact search for every bond, whatever the size of either side (`referee_ringread.py large`).
- **The search space.** Connected inner sides J, with the outside vertex o excluded, are grown from a least root by include/exclude
  branching.
- **The pruning is valid.** A branch is cut when the max-flow from J to the excluded vertices and o exceeds L. No superset of J
  that avoids them can have a smaller cut.
- **The search is complete.** Every connected J with |δ(J)| ≤ L is reached.
- **A control.** At every round, the search's bonds with sides of at most six equal a direct enumeration of all connected sides of
  at most six.
- **What it gives.** The exact table through K = L, with L = largest junction + 1. That is one past what the table must hold
  exactly, since the study keeps D up to the largest junction.
- **Growth.** The ring is grown by the referee's own engine (the FIRST-KNOT-R1 code).

**The growth matches the study at every round.** Junction counts, distinction counts and junction sizes all agree (for example 120,
341 and {3: 1, 4: 19, 5: 57, 6: 42, 7: 1} at round 10, and 1,024 and 4,110 at round 25). **The exact D histograms equal the study's
`distance_histogram` entry for entry at rounds 10 to 20**, through D = largest junction.

| Round | Junctions | Largest junction | Bonds of at most L with an inner side of 7+ junctions | Smallest such bond | Largest inner side among bonds of at most L | Pairs with K ≤ L | Pairs the table of sides ≤ 6 (or ≤ 7) gets wrong |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 120 | 7 | 0 | 10 | 4 | 3,483 | none |
| 12 | 165 | 7 | 0 | 10 | 4 | 4,263 | none |
| 14 | 225 | 7 | 0 | 10 | 4 | 5,372 | none |
| 15 | 261 | 8 | 0 | 10 | 4 | 7,766 | none |
| 16 | 301 | 8 | 0 | 10 | 4 | 8,598 | none |
| 18 | 398 | 8 | 0 | 10 | 4 | 10,815 | none |
| 20 | 526 | 9 | 7 | 10 | 10 | 20,670 | none |
| 22 | 687 | 9 | 7 | 10 | 10 | 25,162 | none |
| 25 | 1,024 | 10 | 19 | 10 | 11 | 41,761 | **6, all at D = 10** |
| **30 (one size past)** | 1,960 | 11 | 125 | 10 | 12 | 102,004 | **6 at D = 10, 22 at D = 11** |

**What the large-sided bonds are** (`referee_ringread_diag_10.json`, at round 10 with L = 11).
- **Their shapes.** There are 7 bonds of size 10 and 12 of size 11. Their inner sides hold four or five of the round-0 ring knots,
  with two or three round-1 junctions and a few round-2 and round-3 ones. These are cuts that wrap the ring near its start.
- **F3 does not check them.** F3 checks only layer cuts (rounds ≤ r against the rest), and these cuts mix rounds.
- **The same bonds appear at every round.** Their counts by size are constant from round 10 on.
- **The six wrong entries.** One size-11 bond, with an inner side of 11 junctions over rounds 0 to 3, gives the six pairs
  {13, 14, 15} × {52, 53} D = 10. No side of seven or fewer does.

**So:**
1. **Within the reader's horizon** (D through largest − 1), the side-6 table is exact at every round 10 to 25.
2. **Through D = largest**, it is exact at rounds 10 to 22 and wrong in 6 entries at round 25.
3. **The study's round-25 check is true as stated but does not establish completeness.** That check is "all 8,443,995 entries agree"
   between sides 6 and 7; both enumerations miss the same 6.
4. **The decision note's sentence "the shapes that could hide a smaller bond with two large sides … are absent or too large (F1, F3)"
   is not right.** Such bonds exist from size 10, and by round 30 they reach the reader's horizon.

## 2. Does the reader survive? (labelled cross-check, study code run read-only)

`crosscheck_reader.py 30` (`referee_ringread_crosscheck_30.json`) grows the ring with the study's own `ringread.py`, builds its side-6
table, and builds the referee's exact table on the same names. It then runs the study's `reader3.r3` on each:
- **The tables differ in 28 entries.** In the side-6 table these are pooled at 12; the exact values are D = 10 (6 pairs) and D = 11
  (22 pairs).
- **The study's reader is exact on both tables at full horizon and when pooled above D = 10.** It returns all 1,960 junctions,
  missing none and inventing none.
- **Pooled above D = 9, it misses one junction** on both tables.

So **one size past the study, the least distance needed is again the largest junction less one** (10 at round 30), as P6 and Q4
predict. The table's missing entries do not affect the reader there. Their pairs are early distinctions, read at earlier stages.

## 3. The other claims

| Claim | Referee |
| --- | --- |
| The junction graph with o is 3-connected (P5) | **Yes**: node connectivity exactly 3 at rounds 10, 12, 14, 15, 16, 18, 20, 22 and 25 (`referee_ringread_shape.json`) |
| By Whitney, the states fix the junctions (with o identified by the law) | Standard for a 3-connected graph. The parallel loose edges to o do not create a 2-separation |
| One round grown from the junctions alone is the true next round (P4) | **Yes at all nine rounds**: the referee's engine starts from the round-T supports alone, with rounds and parents forgotten, and grows one round under the fewest rule. Since the reader returns the true junctions, the regrown round from the read ones is the same |
| The old reader fails at round 10 through a path via the three-distinction junction | **The only short bonds that break its lemma at round 10** (size at most 7, three or more junctions inside) **are 3 paths with junction sizes 3, 4, 4** (`referee_ringread_shapes.json`) |
| From round 15, also through cycles of four four-place junctions | **At round 15 the bonds of size 8 with three or more junctions inside are:** 35 paths of 4, 4, 4; 8 paths of 3, 4, 5; 5 four-cycles of four-place junctions; and one cycle of 3, 4, 4, 5. The cycles have 001H's shape, one size up. The counts of invented junctions (3, 104, 148) were not recomputed |
| Not claimed: uniqueness of the table | Not checked |

## Correction for the owner (listed, not folded in)

1. **The table's completeness** (decision note, "How it works" and "Limitations"). Replace "sides of seven and eight change no
   entry, and the shapes that could hide a smaller bond with two large sides … are absent or too large (F1, F3)" with the exact
   finding:
   - bonds of ten and eleven distinctions with inner sides of 7 to 12 junctions exist at every round from 10 (cuts that wrap the ring
     near its start);
   - they change no entry within the reader's horizon at rounds 10 to 25;
   - they make 6 entries at D = 10 wrong in the round-25 table, one past the horizon;
   - at round 30 they enter the horizon, and the reader is unaffected (it is exact on both tables).

   **Verdict: Narrowing.** The headline stands, and the completeness claim was marked "checked, not proved". **Not a block.**

## How the work was split

- **The referee:**
  - read `ring_read.md`, both tickets' code and their results;
  - wrote `referee_ringread.py` (growth, shapes, 3-connectivity, the history-free step, the exact all-sides bond search),
    `diag_large.py`, `diag_shapes.py` and `crosscheck_reader.py`.
- **The cross-check** imports the study's `reader3.py` (and through it `ringread.py`) read-only. It is labelled as such. Every other
  result uses the referee's own code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Reproduction

Run from this folder. The 20-worker searches take 2 s at round 10, 3 min at round 25 and 12 min at round 30. The cross-check takes
13 min.

```sh
../../../.venv/bin/python -B referee_ringread.py shape 10 12 14 15 16 18 20 22 25 > referee_ringread_shape.json
for T in 10 12 14 15 16 18 20 22 25; do ../../../.venv/bin/python -B referee_ringread.py large $T > referee_ringread_large_$T.json; done
../../../.venv/bin/python -B -c "import json, referee_ringread as R; print(json.dumps(R.part_large(30, extra=1), indent=1))" > referee_ringread_large_30.json
../../../.venv/bin/python -B diag_large.py 10 > referee_ringread_diag_10.json
../../../.venv/bin/python -B diag_shapes.py > referee_ringread_shapes.json
../../../.venv/bin/python -B crosscheck_reader.py 30 > referee_ringread_crosscheck_30.json
```
