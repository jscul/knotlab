# Blocks and motifs substituted for distinctions and knots

Status: Proved (lemmas N1 to N4, N6 and N7 by hand; N5 for the block's knots, narrowed below) with an exact census on frozen ranges;
**referee pending** (the background referee thread). Ticket A of `research/SUBST-NEST-20261112-001/preregistration.md`, frozen with
the code in commit `456d7a49e` before any run. `check.py --part blocks|motifs|summary` reproduces each part.

Words, as in the pre-registration: block, block substitution σ, cross set, cross knots, the native cross sets (the diagonal, the
block's knots in every order, every ordered triple of distinct places), template, loose place, motif, attached distinctions, a tie
outside the copy, the farthest tie. After the run these became distinction substitution, block triples, between-copy knots, spare
distinction, gadget, terminals and tie extent (the decision note's Words), and "bond distance"/"bonds" in the pre-registration should
be read as steps apart/steps (a correction). A place p is **locked** in σ(P) when the distinctions (v, p), v in P, are tied to one another
across the whole pattern.

## 1. The lemmas

As stated and proved in the pre-registration, with one narrowing:

- **N5, narrowed (an error found by the run).** The constant lift (v, p) ↦ t(p) is a state of σ(P) when the cross set is the block's
  knots, since each cross knot then reads a knot of B in the state t. It is not one for every ordered triple of distinct places once
  m ≥ 5: then t would need no three equal values among its m places. In fact the template is then empty: of three states of B, two
  share a value at three or more places each, and the third has that value somewhere, so three distinct places carry equal values.
  So with every distinct triple and m ≥ 5, substitution ends every pattern with a knot. Logged as a correction (Narrowing).
- The others hold as frozen. N6 in particular: a loose place's column is free, so nothing is tied to it.

## 2. Arm D: blocks (exact)

87 living connected blocks (one of 3 distinctions, 3 of 4, 28 of 5, 55 of 6 with up to 5 knots) × 3 cross sets = 261 cells, each on
ten tests (chains of 4, 8 and 16 knots and the drawn three-copy nestings of levels 1 to 3, substituted once; chains of 4 and 8 and
nestings of levels 1 and 2, substituted twice), a root in every column. The test patterns have no ties of their own, so every tie
outside a copy is created by the substitution.

| Cross set | None | Rigid template, locks every place | Locks some places (not rigid) | Ends |
| --- | --- | --- | --- | --- |
| the diagonal | 87 | 0 | 0 | 0 |
| the block's knots | 40 (every place loose) | 5 | 42 | 0 |
| every distinct triple | 1 (one knot) | 3 (the three blocks on 4 distinctions) | 0 | 83 (every block on 5 or 6) |

- **Where something locks, it locks the whole pattern.** In all 50 cells with a tie outside the copy, the root's farthest tie equals
  its farthest distinction on every test (1,090 roots, none short): on the chain of 16 knots, 16 bonds; after two substitutions, again the whole pattern. The
  criterion frozen for "influence created by substitution, growing with the pattern" (ties outside the copy, farthest tie at least half
  the farthest distinction on chains of 4, 8 and 16 knots) is met by all 50.
- **The locked places are exactly the places that are not loose (descriptive, after the run).** With the block's knots as cross set,
  a root had ties outside its copy exactly when its place is not loose, for all 4,850 roots tested, and each of the 970 roots at a
  place that is not loose reached its farthest distinction. N6 proves one direction; the other is a conjecture, exact on this range.
- **All four knots on four distinctions** (six states, no ties of its own, no loose place) has a rigid template: every copy takes the
  same state, every place is locked, the tied share is 1/4 after one substitution and after two (S3, as the advisor computed).
- **Nothing appears only deeper.** No cell had ties outside the copy after two substitutions and none after one.
- **Share.** The share tied to a locked root is the share of places locked together with it: from 1/6 to the whole pattern (the
  block of 9 knots on 5 distinctions has only two states, a word and its mirror, so every distinction is tied to every other).

## 3. Arm K: motifs (exact)

| Motif | Relation on the attached distinctions after one level | Levels | Tied to an attached distinction (share) | Farthest tie / farthest distinction |
| --- | --- | --- | --- | --- |
| three copies sharing corners (drawn) | all eight | 0 to 5 | only itself from level 1 on | 0 / grows |
| Fano plane less one knot | 000 and 111 | 0 to 4 | 1, 3, 7, 31, 175 (1/3, 3/7, 7/31, 31/175, 175/1,051) | 0/1, 2/2, 4/4, 8/8, 16/16 |

As N1 to N3 say: the drawn nesting frees everything and the Fano motif ties every older distinction, a tie the motif already holds,
reaching the whole pattern at every level while its share falls toward 1/6.

## 4. Against the predictions

| Item | Outcome |
| --- | --- |
| S1 the diagonal: no tie outside the copy | held (87 of 87) |
| S2 blocks loose at every place: none; most blocks are such | held: 40 such blocks, none with a tie outside the copy; 40 of 87 is not most |
| S3 all four knots on four distinctions | held: rigid, locks the whole pattern, share 1/4, once and twice |
| S4 rigid templates only for dense blocks | held for the block's knots (4 of the 4 triples on 4 distinctions; 7 (two blocks), 8 and 9 of the 10 on 5); **failed** for every distinct triple (two knots on 4 distinctions is rigid) |
| S5 an intermediate case exists (advisor: 50%) | **held**: 42 blocks lock some places and not others |
| S6 nothing only after two substitutions | held |
| K1, K2 | held |
| N5 for every distinct triple | **failed** for m ≥ 5 (all 83 such cells end); narrowed, a correction |

## 4b. Stress test one size past (after the run, descriptive; `stress_one_size_past.py`)

300 random living blocks past the frozen range (150 on 6 distinctions with 6 to 12 knots, 150 on 7 with 5 to 12; seed 20261112), each
substituted once into the chain of 8 knots with its own knots: for every block and every distinction, ties outside the copy exactly
when the distinction is not spare, and every such part reaching the far end of the chain. The rule stays exact on its range, not
proved.

## 5. The referee

Pending: handed to the background referee thread.

## What this establishes

- Proved: knot substitution is decided at one level (N1); the diagonal keeps the outer law (N4); with the block's knots substitution
  never ends (N5) and every loose place's column is free (N6); a rigid template locks every place (N7).
- Exact on the frozen ranges: block substitution creates ties across the whole pattern from blocks that hold none of their own, in 47
  of 87 blocks with their own knots as cross set, already after one substitution; the locked places were exactly the places that are
  not loose.
- Not established: the converse of N6 in general; behaviour beyond 6 distinctions per block, two substitutions and chains of 16 knots.
