# Referee report JOINT-RECORDS-R1 (light check, fresh code, no Codex)

**Verdict: Confirmed. No Block, no fix needed.** The reduction is exact and labelled as known. Every census number recomputes
exactly, the Platonic counts agree three ways, the connection to the Codex seam finding is correctly placed, and nothing known is
presented as new.

**How the work was split.** The referee read the note and the proof, and wrote `referee_seam.py` and `referee_realize.py` without
reading `seam.py`. No helper, no Codex and no advisor were used.

## 1. Theorem 1: the reduction

**It is exact.**
- **Runs give decompositions.** A run of the w-record law absorbs a knot only when all its members are carried, forgets a
  distinction only when no unabsorbed knot uses it, and combines two records on their shared distinctions. So a run's carried sets
  are the bags of a tree decomposition of width at most w − 1.
- **Decompositions give runs.** Each such decomposition gives a run: bucket elimination, or dynamic programming over a decomposition.
- **So** the least w is the treewidth + 1, and the pathwidth + 1 without combining.

**The labels are fair.** "Known" (Freuder; Dechter–Pearl; Samer–Szeider; Aji–McEliece) is right, and so are the attached facts:
- logarithmic space for bounded width (Elberfeld–Jakoby–Tantau);
- about 3 × width for logarithmically many combining stages (Bodlaender–Hagerup);
- O(√n) width on weaves (planar separators);
- lower bounds only under ETH.

**The escapes are correct and known.**
- **Parity:** affine records.
- **Counting on drawn patterns:** Pfaffians.
- **Zero-pair weaves.** The note says NAE colourings of a triangulated sphere are twice the perfect matchings of the dual cubic
  graph. That is right:
  - each non-monochromatic face has exactly one monochromatic edge, so the monochromatic edges' duals form a perfect matching;
  - conversely, the complement of a perfect matching is a 2-factor of the dual, which on the sphere is a cut of the primal;
  - so the two correspond up to the global flip;
  - Petersen's theorem then gives existence.

**Not a block.**

## 2. Theorem 2: the seam census (`referee_seam.py`, `referee_seam.json`)

| s | Complement-closed relations | Fixed by 2-place shadows | Fixed by 3-place shadows |
| --- | ---: | ---: | ---: |
| 1 | 2 | n/a | n/a |
| 2 | 4 | 4 (trivially) | n/a |
| 3 | 16 | 12 | n/a |
| 4 | 256 | 50 | 226 |

- **The four failures at s = 3** are exactly the relations missing one complementary pair: NAE, missing {000, 111}, and its three
  single-flip variants. All four pass K1–K3 (referee's own test).
- **The four-place NAE** is fixed by neither its 2-place nor its 3-place shadows.
- **"Every such relation occurs"** (`referee_realize.py`, `referee_realize.json`). Every complement-closed relation is the projection
  of a not-all-equal pattern of distinct-member knots: all 4 at s = 2 with 3 hidden distinctions, and all 16 at s = 3 with 2 hidden,
  by exhaustive search over knot sets. This agrees with Pol(NAE) = projections and negation.
- **The Platonic counts.** NAE face-colourings by brute force are 6, 18 and 72 on the tetrahedron, octahedron and icosahedron. Twice
  the perfect matchings of the dual (K₄, cube, dodecahedron) gives the same three numbers.
- **The labels.** "Known-with-delta" (majority-closed ⇔ fixed by two-place shadows: Baker–Pixley; Jeavons–Cohen–Cooper) with "the
  census is local" is fair. The census is a small computation; its one reading of interest, that the failures at s = 3 are the
  knots, is correct.

**Not a block.**

## 3. The relation to the Codex seam finding

**The attribution is right.** `GUARD-CHOICE-SEPARATION-20261115-001`'s bounded discriminator (decision note, paragraph 23) is the
pair {10} against {00, 01, 11}. Each coordinate agrees, but no joint assignment exists. `TWO-CHOICE-IMPLICATIONS-20261115-001` then
develops it. Citing that study too would help the reader.

**The placement is right.** It is one-place shadows against a two-place relation. The pair is not complement-closed, so it cannot
arise in pure NAE patterns: a one-place NAE report is only empty or full. "The level below" Theorem 2's two-place against
three-place is accurate.

**Not a block.**

## 4. Nothing presented as new that is not

- **The note's own framing.** It says the reduction "explains nothing beyond treewidth and the known algebraic and matching escapes",
  marks the goal checkpoint "no demonstrated advance", and claims as its own only the seam census. All of that is accurate.
- **The pre-registration** was frozen at 8fa8b0697 (22:58:54 UTC). `seam.py` and `seam.json` first appear in the next commit,
  6719e7293 (23:01:15 UTC). So the computation followed the freeze.

## Fixes for the thread

None required. Optional: cite `TWO-CHOICE-IMPLICATIONS-20261115-001` beside `GUARD-CHOICE-SEPARATION-20261115-001` for the
{10} / {00, 01, 11} pair.

## Files

- `referee_seam.py` and `referee_seam.json`: the census and the Platonic counts.
- `referee_realize.py` and `referee_realize.json`: realizability of every complement-closed report.
