# Inner harmonies stitched into outer bases

Status: Proved (lemmas L1 to L9 by hand) with an exact census of four arms on frozen ranges; **referee pending** (the background
referee thread). Ticket A of `research/BASES-WITHIN-20261112-001/preregistration.md`, frozen with the code in commit `8e2e41275`
before any run. `check.py --part axial|offsets|box|gasket|summary` reproduces each part.

Words, as in the pre-registration: harmony (A70), inner harmony, outer base, stitch (now holding distinctions of three harmonies),
stitch at one place, O[I], level, tie class, bond distance, the farthest tie. The pre-registration's "stitch with offsets" is
called a **shifted stitch** here, with **shifts** (s, t, u), because the glossary's offset is the relative phase of two orbits.

## 1. What is settled by definition (by hand)

The nine lemmas are stated and proved in the pre-registration; in short:

- **L1.** A stitch at one place of inner states w_a, w_b, w_c holds exactly when D_ab + D_bc + D_ac = 2L: the outer level reads how
  often each pair of inner states disagrees at its offset.
- **L2.** Harmonies of harmonies are harmonies.
- **L3.** Only the alternation 0101… is read as one distinction exactly.
- **L4 (the mirror lift, the advisor's).** x_(j,i) = s_j ⊕ w(i) is a state of O[I] for every O-state s and inner state w. So O[I]
  lives exactly when O lives, each column realises exactly O's states, and nesting at one place never ends.
- **L5.** With the alternation as inner harmony, O[I] is O again, at every level.
- **L6.** Levels never end: sums and mirror lifts of states are states.
- **L7 (ties multiply).** At level k, two distinctions are tied exactly when every coordinate where they differ is tied in the seed.
- **L8.** Shifted stitches on an outer pattern with no closed chain of knots reduce to stitches at one place.
- **L9.** For the alternation, shifts are signs: O[I] with shifted stitches is signed not-all-equal.

## 2. The checks of the lemmas (all passed)

| Lemma | Check | Outcome |
| --- | --- | --- |
| L4 | 45 harmonies × 33 outer patterns, stitched at one place: lives exactly when the outer lives | 1,485 of 1,485 |
| L7 | E3: tie class of every diagonal origin of every seed at levels 1 to 4, against the product | 100 of 100 |
| L7 | tie class of the origin at level 2 of every harmony, against the product of its line ties (follow-up after the run) | 45 of 45 |
| L8 | no outer pattern without a closed chain ended under any shifts | none ended |
| L9 | the alternation, every shift in {0, 1}, against signed not-all-equal by brute force | agreed on all 26,340 |
| control | exactly-one law, inner shifts of 001, the advisor's outer pattern of two states | O[I] ends, as it must |

## 3. E3: levels of finite seeds (exact)

| Seed | Seed states | Tied pairs in the seed | Levels 1 to 4 | Tie class of an origin at level k | Farthest tie / farthest distinction |
| --- | --- | --- | --- | --- | --- |
| one knot | 6 | none | live | itself | 0 / k |
| two knots sharing one | 18 | none | live | itself | 0 / up to 2k |
| two knots sharing two | 10 | none | live | itself | 0 / up to 2k |
| closed chain of three | 26 | none | live | itself | 0 / 2k |
| Fano plane less one knot | 10 | the removed knot's three, pairwise | live | 3^k on the removed knot's distinctions (3, 9, 27, 81); else itself | 2k / 2k on those; else 0 / k |

So nesting forces nothing a seed does not already force. Where the seed forces (the Fano plane less a knot, whose removed knot's
three distinctions must be equal, else the Fano plane would live), the forcing reaches the whole level at every depth (farthest tie
equal to the farthest distinction, 2, 4, 6, 8), while the share it holds falls as (3/7)^k (3 of 7, 9 of 49, 27 of 343, 81 of
2,401).

## 4. E4: a drawn three-copy nesting (exact)

One knot at level 0; level n is three copies of level n − 1 sharing their meeting corners (the literature's Sierpinski gasket),
levels 0 to 7, up to 3,282 distinctions and 2,187 knots.

| Level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Distinctions | 3 | 6 | 15 | 42 | 123 | 366 | 1,095 | 3,282 |
| Farthest distinction from a corner | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 |
| Tied to the corner, or to a shared corner | itself | itself | itself | itself | itself | itself | itself | itself |

It lives at every level, and fixing a corner, or a shared corner, forces nothing, at every depth, while the farthest distinction
doubles with each level. The influence of one distinction stays local, at zero, at every depth.

## 5. E2: shifted stitches (exact on each sampled assignment)

45 harmonies against 33 outer patterns (31 connected ones of up to 6 distinctions and 4 knots, the Fano plane less one knot, the
Fano plane): every shift in {0, 1} for the alternation (26,340 assignments), 60 sampled assignments for each other pair.

- **Ending a living base: rare, and at one pattern only.** 46 assignments ended a living outer base, all of them on the same pattern:
  four distinctions with all four of their triples knotted (the literature's complete 3-uniform pattern on four points). For the
  alternation 8 of its 256 sign patterns end it; for 16 other harmonies 1 to 6 of 60 sampled assignments do; for 28 harmonies none of
  60 did.
- **Reviving a dead base: almost always.** The Fano plane, which no assignment allows under not-all-equal, lives under 16,320 of the
  alternation's 16,384 sign patterns and under all 60 sampled assignments of every other harmony. Shifts loosen far more often than
  they tighten.

## 6. E1: levels of each harmony (dropped; a follow-up after the run)

- **Frozen run: dropped.** E1 reached its 1-hour cap (5 h 48 min of processor time across 12 workers) in its level-3 enumerations,
  capped at 100,000 states on up to 4,096 distinctions, and wrote nothing. By the pre-registration it is reported as dropped, and P1
  to P3 were not tested by it.
- **Follow-up after the run (descriptive, not frozen; `after_run_levels.py`, the frozen functions, 5 minutes).** Level 2 of all 45
  harmonies capped at 20,000 states, and level 3 of 0011:

| Harmony (orbits) | 01 | 0011 | 000111 | 0011 + 01 | 00001111 | 00101101 | 0000011111 | 0010011011 | 000000111111 | 001010110101 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| States at level 1 | 2 | 4 | 6 | 6 | 8 | 8 | 10 | 10 | 12 | 12 |
| States at level 2 | 2 | 16 | 102 | 90 | 528 | 528 | 2,470 | 2,470 | 11,016 | 11,016 |

  - The advisor's counts hold: 0011 has 16 states at level 2 and 256 at level 3, 000111 has 102 at level 2.
  - Rigid (only the linear states u(m·c + a)) exactly for the alternation, at level 2: every other harmony has more states than its
    linear ones (the 26 over the cap a fortiori).
  - No count fell below the linear and mirror-lift states, and the tie class of the origin at level 2 was the product of the line
    ties for all 45 (L7).
  - One-orbit harmonies of the same period had the same count at level 2 in every case seen (8, 10 and 12), a regularity of the
    counts noticed after the run, not explained.

## 7. The referee

Pending: handed to the background referee thread (arrangement of 2026-11-12).

## What this establishes

- Proved: stitched at one place, inner harmonies keep the outer law exactly at every level, nesting never ends, and ties multiply,
  so nesting forces nothing beyond what the seed forces.
- Exact on the frozen ranges: the five seeds and the three-copy nesting to level 7 behave as the lemmas say, and in the nesting
  nothing is ever forced; with shifted stitches, inner harmonies end a living outer base only at the tightest pattern of four distinctions,
  and revive the dead Fano plane almost always.
- Not established: a native rule for shifts (none was found); whether some other nesting, such as a substitution reading (A75's
  challenge), creates forcing that grows with depth.
