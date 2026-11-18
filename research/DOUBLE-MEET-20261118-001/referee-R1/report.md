# Referee report DOUBLE-MEET-R1 (fresh code, no Codex)

**Verdict: Block on one reading; the rest confirmed with fixes.**
- **The Block.** "A patch is a true distance exactly when no pair is unbonded" (P5, and the answer's "bond distance fails to be a
  true distance exactly when some pair is held by no bond") is false one size past the census.
  - A hole-free disc of 12 knots has every pair bonded, yet fails the triangle inequality with all three distances finite: 7 > 2 + 4.
  - Two discs of 13 knots do the same.
- **What survives, and is sharpened.** In every failure the referee found, the long side is still a lone pair of opposite classes
  facing each other.
  - Either it is unbonded, as the study found, or it is bonded too far: b = steps apart + 3.
  - So the obstruction is still the rim, and the double meetings inside are still harmless. But "no unbonded pair" does not suffice.
- **Everything else reproduces with the referee's own code, one size past.**
  - **Every disc to 10 knots:** the same unbonded-pair law, the same b ≥ steps + 1, and the steps + 2 exceptions from 10 knots.
  - **2,500 random discs each of 12 and 13 knots:** every unbonded pair is lone, of opposite classes and facing.
  - **Parallelograms to 18 distinctions:** exactly one unbonded pair, the acute lone pair.
- **The owner's flags.**
  - **The H and L sketches** are labelled as sketches throughout, except in one table cell (§3).
  - **The facing definition and the disc test** are right (§3).
  - **P2 and P5** are computed claims only, and P5 is the one that fails.
  - **The headline "harmless"** stands only with the corrected mechanism (§2).

## What holds (recomputed; `referee_double.py`)

- **The referee's code.** Its own weave, disc enumeration, facing test (solved in integers) and bond search.
- **The disc counts.** Discs counted up to translation are 2, 3, 6, 14, 36, 94, 250, 675, 1,832 and 5,005 for 1 to 10 knots. These are
  the fixed polyiamonds (the literature's word) less those with holes or pinches: 6 at nine knots and 48 at ten.

| Reading | Every disc to 10 knots (7,917) | 2,500 random discs of 12 knots | 2,500 random discs of 13 knots |
| --- | --- | --- | --- |
| Unbonded pairs; of them lone, opposite classes, facing both ways | 4,272; 4,272 | 1,263; 1,263 | 1,175; 1,175 |
| Bonded pairs below steps + 1 | 0 | 0 | 0 |
| Bonded pairs at steps + 2; at steps + 3 | 12; 0 | 15; 1 | 22; 2 |
| Facing pairs of opposite classes; of them bonded | 4,962; 690 | 2,115; 852 | 2,353; 1,178 |
| Metric exactly when no pair is unbonded | 7,917 of 7,917 | **2,499 of 2,500** | **2,498 of 2,500** |
| Discs with a failure among finite distances | 0 | **1** (6 triples) | **2** (6 triples each) |

- **The study's census agrees:**
  - P2 holds on its 12,318 unbonded pairs, and P5 on all its discs;
  - its first steps + 2 pairs come at ten knots, as the referee's do.
- **The smallest case (T)** is right. With a missing middle distinction set opposite to the other, both knots hold, and a set holding
  all four contains a knot.
- **Parallelograms** (`referee_double_pars.json`): 2 × 2 to 2 × 9, 3 × 3 to 3 × 6, and 4 × 4, up to 18 distinctions. Each has
  exactly two lone distinctions, its acute corners (0, 0) and (a − 1, b − 1), and exactly one unbonded pair, those two. This holds
  one size past the study's 16.

## 1. The finite failure (Block on the reading "metric exactly when no pair is unbonded")

- **The disc** (`referee_double_finite_example.json`): 12 knots on 14 distinctions, d(0,1), d(0,2), d(1,0), d(1,1), d(2,0), d(2,1),
  u(1,1), u(1,2), u(2,1), u(2,2), u(3,0), u(3,1).
  - It passes the disc test, and allows 1,088 states.
  - Every pair is held by some bond.
- **The failing triple**, with x = (0, 3), y = (1, 2) and z = (4, 0):
  - b(x, y) = 2, with {(0,3), (1,2), (1,3)};
  - b(y, z) = 4, with {(1,2), (4,0), (1,1), (1,3), (3,0)};
  - b(x, z) = 7, with {(0,3), (4,0), (0,2), (1,3), (2,0), (2,3), (3,0), (4,1)}.
  - So 7 > 2 + 4. Steps apart from x to z is 4, so b is steps apart + 3.
- **The checks.** An independent bond search confirmed all three values: np.unique freedom, every set holding the pair, smallest
  first.
- **The same picture at 13 knots** (`referee_double_finite_failures.json`): two discs, each with b = 7 at steps 4 on its long side,
  and no unbonded pair.
- **In all three discs the long side is two lone distinctions, of opposite classes, facing each other both ways.**
- **What this refutes.**
  - P5 read beyond its census, the answer's first claim, and the table row "every patch without holes to eleven knots: exactly when
    no lone pair … is unbonded" read as a law.
  - The census statements to eleven knots stand.
  - The pairs at steps + 2, which "do not break the triangle inequality", become steps + 3 one size up, and those do break it.
  - A Block on this reading, as with CUMULANT-DIST's "every knot tree". The census stands, the general reading does not.

## 2. Is "harmless" still fair? (the owner's question)

- **Yes, with the mechanism corrected.**
  - Every failure the referee found runs through a lone pair of opposite classes facing each other: unbonded at all sizes, or bonded
    at steps + 3 from 12 knots.
  - No failure ran through a double meeting inside the patch.
  - So the corollaries survive on these samples: a patch with no lone distinctions, or whose lone distinctions are all of one class
    or never face each other, had no failure.
- **But the criterion changes.** Read "a patch fails exactly when a facing lone pair of opposite classes is unbonded, or bonded too
  far to satisfy the triangle inequality". The bonded facing pairs (690, 852 and 1,178 above) are not all harmless.
- **The P1 miss belongs here.** The steps + 2 pairs are the start of a growing excess at the rim, not a curiosity. The answer's "they
  do not break the triangle inequality" holds only to eleven knots.
- **Fair headline.** "Inside the weave double meetings are harmless: on every patch checked, bond distance fails only through lone
  distinctions of opposite classes facing each other, when no bond holds them or, from 12 knots, when the bond that holds them is
  too large."

## 3. The flags: sketches, the facing definition, the disc test

- **H and L are labelled sketches** in the proof ("the advisor's sketch", "Corollary (sketch)"), in the note's answer ("sketched by
  the advisor … checked on 1.56 million pairs") and in the limitations.
  - **One place drops the qualifier:** the position table's "at least steps apart + 1 throughout" (Local direction). Add "(sketched;
    computed)".
  - The referee's census found no pair below steps + 1, to 13 knots.
- **The facing definition.**
  - **The study's test.** `weavelib.facing` solves z − x = p(u − x) + q(v − x) with floats and checks integers with p, q ≥ 1.
  - **The referee's test.** It solves the same in exact integer arithmetic. The two agree on every pair of the census (P2 reproduced
    exactly).
  - **"Both ways" is required**, and the study's judge applies it.
- **The disc test.** "χ = 1 and every vertex star joined through shared pairs" is right for edge-connected sets of triangles of the
  weave. The referee's counts are the fixed polyiamonds less the holed ones.
- **P2 and P5** are computed claims, labelled so in the note. P2 holds one size past. P5 does not (§1).

## Fixes for the thread (listed for the owner, not folded in)

1. **P5 and the answer's first claim.**
   - Replace "fails exactly when some pair is held by no bond" with §2's criterion.
   - Add the 12-knot disc as the counterexample: b(x, z) = 7 against b(x, y) + b(y, z) = 6, every pair bonded.
   - Score P5 as holding to eleven knots and failing beyond.
   - **Block on that reading;** the census stands.
2. **The steps + 2 sentence.** "They do not break the triangle inequality" holds to eleven knots. From 12 knots pairs at steps + 3
   appear, and they do break it. **Narrowing.**
3. **The headline.** Keep "double meetings are harmless", with the corrected rim mechanism (§2). **Narrowing (wording).**
4. **The position table.** Mark "at least steps apart + 1" as sketched and computed. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof (T, H, L), and `weavelib.py` and `job.py`;
  - checked T by hand, and the sketches' labelling;
  - wrote `referee_double.py` and `referee_double_finite.py`: its own weave, discs, integer facing test, bond search, and the
    census to 10 knots plus 12- and 13-knot samples and parallelograms to 18 distinctions;
  - confirmed the finite failure by a second, independent bond search.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_double.py` and `referee_double_finite.py`.**
- **`referee_double_discs.json`, `_pars.json`, `_finite_failures.json` and `_finite_example.json`.**

Reproduce, from `research/DOUBLE-MEET-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_double.py discs > referee_double_discs.json
../../../.venv/bin/python -B referee_double.py pars > referee_double_pars.json
../../../.venv/bin/python -B referee_double_finite.py
```
