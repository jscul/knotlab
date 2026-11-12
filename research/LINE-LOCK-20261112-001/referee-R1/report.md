# Referee report LINE-LOCK-R1: no permutive sub-stitch in a harmony's stitch

**Verdict: Confirmed with fixes, and the headline narrowed.**
- **The theorem is correct.** I checked every step by hand and tested its lemma exhaustively on small cases and by SAT. It also
  sharpens: in **any** not-all-equal stitch, lagged or not, with the three entries over one set of states or over three, a permutive
  set of triples sits inside a free product of state sets. So no not-all-equal stitch ever holds an additive law exactly.
- **The census reproduces.** My own code gives 73 harmonies, 187 orbits, no free site, and 22 cyclic subgroups and 2 cosets inside
  the stitch pairs, all degenerate, with no ratio subgroup, Z₂ × Z₂ block, free pair or ratio coset. The 32 harmonies of span 9 give
  the same.
- **The fixes.**
  - The headline speaks of influence in arrangements, which nothing here decides.
  - The lagged claim holds only in the exact reading. In the containment reading the census used, lagged stitches of 20 harmonies hold
    free pairs, which contain z = x + y over F₂, the case the census did not search for lags.
  - The census covers one kind set per harmony, and the stitch depends on it. My check of every kind set gives the same zeros.

Referee: the background referee thread, 2026-11-12. The code is my own: `ref_line.py` and seven check scripts, built on the referee's
`ref_lib.py` from BASES-WITHIN-R1. It imports none of `line_lib.py`, `nest_lib.py`, `fam_lib.py` or `check.py`, and reads the census
only as data. I used Glucose 4. Validation: V2. The advisor model was not consulted for this job. Since the lemma came from it, I
checked the proof myself.

## 1. The theorem, step by step (coordinator's iii)

Every step holds. The words are those of the proof. A permutive set is the literature's Latin square, read as a transversal design
TD(3, n), with the three entries as its three classes.

1. **Two varying fibres are impossible.** In an r × c part of a permutive set there are at least max(r, c) distinct third entries.
   This gives max(r, c) + max(n − r, n − c) ≤ n, so r = c and |Σ| = r. Each first entry in X₀ then uses all of Σ within Y₀, so a second
   entry in Y₁ meets no member of Σ, which a permutive set forbids. Σ is not empty, since r ≥ 1. The same holds for any two roles, since
   the permutive property holds in all three roles.
2. **One varying fibre makes the other two constant and opposite.** A triple whose first bit equals the constant y₀ needs z₀ ≠ y₀.
3. **A free site.** At a place where two states of S differ, the fibre varies in all three roles. So every knot through the place has
   its other two members opposite in every state of S. Flipping one place on the integers then gives a state that does not repeat.

**Tests of the lemma** (steps 1 and 2):
- **Exhaustive.** For every reduced permutive set of order 2 to 5 (62 sets, which cover every class up to renaming), I took every
  not-all-equal colouring of the three classes (10,836 in all). None has two varying classes.
- **By SAT.** For 100 random permutive sets of order 6 to 10, "two varying classes" is unsatisfiable in every one.

**The chain where its premise can fail.** Its premise is that the law is a harmony. I tested laws that are not: 696 not-all-equal laws
and periods (1 to 3 kinds of span at most 5, periods 4 to 10). 112 hold a permutive set on one set of states: 4,630 of order 2 and
4,464 of order 3. In every one, the states differ only at sites free in all of them, as the proof concludes before its last step.

**Two things the proof gives that it does not say.**
- **(a) The product lemma.** Steps 1 and 2 never use that the three entries range over the same set, and never use the lag. At each
  kind and place, at most one of the three fibres varies and the other two are constant and opposite, or all three are constant and
  not all equal. Either way **every** triple of S₁ × S₂ × S₃ satisfies that knot. So a permutive set inside a not-all-equal stitch puts
  the whole product S₁ × S₂ × S₃ inside it. This holds for every lag, presentation, knot shape, slot order and pair of orbits.
  Computed checks:
  - all 3,858 three-range permutive pairs of 2-sets in the 64 harmonies with at most 64 states hold 8 of 8 triples;
  - in the laws that are not harmonies, all 9,094 one-set permutive sets and all 379,890 three-range pairs of 2-sets do too.
- **(b) The converse.** Take a not-all-equal law whose knots have distinct places modulo P. If a repeating state has a free site,
  flipping that site in every period gives a free pair, which holds both permutive laws of order 2. The check: in 576 such laws and periods, a free
  site and a permutive pair occur together in all of them, and all 6,092 free-site flips are free pairs.

**Novelty.** In a bounded search I found no statement of the lemma. I searched for 2-colourings and property B of transversal designs
and Latin squares, and for not-all-equal against quasigroup and Mal'tsev structure. In the literature's terms, the lemma says that
every proper 2-colouring of a TD(3, n) makes two classes constant and opposite. It is elementary and in the spirit of not-all-equal's
essentially unary polymorphisms (Schaefer; Post's lattice), so it may be folklore. Novelty should be claimed only as "not found".

## 2. Is it settled by definition? (coordinator's ii)

**Partly.** The definitional part is the last step: by (b), a permutive set on one set of states is the same thing as a free site in a
repeating state, and a harmony has none by definition. The content is one elementary lemma, steps 1 and 2. It is half a page and true
of every not-all-equal stitch, harmony or not.

So the theorem is not empty, but it says less about arithmetic than its wording suggests. Read with (a), a not-all-equal stitch never
holds an additive law exactly. A permutive set appears only inside a free product, where the copies choose their states independently,
the opposite of additive influence. For a harmony, the theorem then rules out the one-set case of that free product.

## 3. The census, rebuilt

| Item | Census | Referee |
| --- | --- | --- |
| Harmonies; orbits; with an odd prime in the period | 73; 187; 101 | 73; 187; 101 |
| Free sites | 0 | 0 |
| Cyclic subgroups inside the stitch pairs | 22, all degenerate | 22, all degenerate |
| Cosets inside | 2, both degenerate | 2, both degenerate |
| Ratio subgroups, ratio cosets (any; a lag can give) | 0; 0 | 0; 0 |
| Z₂ × Z₂ blocks; free pairs H × H (H cyclic) | 0; 0 | 0; 0, and no coset of either |
| Odd harmonies' stitch pairs | {(0, 0)} on every orbit | {(0, 0)} on every orbit |
| Span 9: harmonies, periods | 32, 12 to 252 | 32, the same periods, all zero |

**Row by row, 72 of 73 rows agree.** The exception is a presentation choice, not an error: the period-112 harmony 00000001111111 +
0001100011100111 + 01.
- **The two kind sets.** The census's sizes of stitch pairs (24, 9, 2) belong to the kind sets {(3, 7), (5, 8), (7, 8)} and {(4, 7),
  (1, 8), (3, 8)}. My enumerator took {(3, 7), (3, 8), (7, 8)}, which gives 19, 12, 2.
- **The stitch depends on the kind set.** In the census's family of 1 to 3 kinds of span at most 8, there are 1,383 kind sets that are
  harmonies. In 45 of the 66 harmonies, different kind sets give stitch pairs of
  different sizes.
- **Every kind set gives the same zeros.** On all 1,383, I find no free site and no ratio subgroup, ratio coset, block or free pair, as
  subgroups or as cosets. They hold 754 cyclic subgroups and 118 cosets, all degenerate.

## 4. Lagged stitches and three ranges (the open part)

**Lags, one set of states.** I took every lag (l₁, l₂) ∈ Z_P² and every set of 2 states in the 68 harmonies with at most 128 states,
and every set of 3 states in 58 of them.
- **20 harmonies hold a lagged permutive pair.** All are free pairs, holding all 8 triples. An example is 0000011111 with S = {u, σu}
  at lag (2, 1).
- **One harmony holds free 3-sets:** 00000001111111 + 00011001110011, at lag (8, 11).
- **None is exactly additive,** as (a) requires.

The census did not see these pairs. Its lagged search covered ratio cosets at odd primes. It searched free pairs and blocks only as
subgroups, and a pair {u, h·u} with h of order more than 2 is no coset at all.

**Three ranges.** I searched for permutive sets of order 2 with three arbitrary ranges S₁, S₂, S₃, which covers every lag and pair of
orbits at once. They exist in 28 of 68 harmonies. So the one-set condition is essential to the theorem, and only (a) carries over.

**Arrangements with ranges that depend on the site.** The theorem needs one set for every copy. I also tried copies along two shifts
whose ranges S_g depend on the site's class under a map of Z² onto Z₂ (3 maps) or Z₃ (4 maps). That covers 64 harmonies with 2-sets.
- **None found,** not even inside a free product. The map onto the trivial group, the theorem's own case, finds none either.
- **A control** on a law with free sites finds them under every map.

## 5. The headline (coordinator's i)

**It is wider than what is proved.** "Two-way influence of Ledrappier's kind cannot come from stitched harmonies in range", "their
reach stays tied to cycles" and the owner's-words line ("never ones that behave like arithmetic on a grid of numbers") are statements
about arrangements. What is proved is about the stitch itself. Three limits:
1. **The bridge is a premise, not a result.** "Influence of Ledrappier's kind needs an additive automaton inside the stitch" is
   assumed. With (a), no not-all-equal stitch has one exactly, harmony or not. So if such influence exists in stitched arrangements, it
   must come from elsewhere, and nothing here rules that out.
2. **Hidden copies are open.** Not-all-equal knots with hidden members define complement-closed parity, as A78 in PARITY-MIX records,
   so laws seen after blocking copies are not covered.
3. **Locks are not decided.** Lock arithmetic and influence in the arrangements were not computed here.

**Safe wording:**
- **What is proved.** A not-all-equal stitch, lagged or not, never holds an additive law exactly: any permutive set of triples in it
  lies inside a free product of state sets. A harmony's one-order stitch holds no permutive set on one set of states at all, for every
  harmony, kind set, period, knot shape and slot order. Equivalently, no repeating state of a harmony has a free site.
- **What is computed, in range.** There is no ratio coset in one orbit. Lagged stitches hold free pairs in 20 of 68 harmonies, and
  none exactly additive. Arrangements with ranges depending on the site over Z₂ or Z₃ hold no permutive pair.
- **So** no additive automaton of Ledrappier's kind is carried by the stitch of stitched harmonies. Whether arrangements of copies
  show Ledrappier-type influence another way, through hidden copies, is open.

## 6. Fixes for the thread

1. **Headline and "What it changes".** Replace "cannot come from stitched harmonies in range" and "their reach stays tied to cycles"
   with the safe wording of section 5. The owner's-words paragraph should say "never by an additive law in the stitch itself".
   **Narrowing** (Overreading: a statement about the stitch read as one about arrangements).
2. **The lagged claim.** "Checked for lagged stitches on all 105 harmonies; no lagged stitch holds an additive automaton" holds in the
   exact reading, and (a) now proves it for every not-all-equal stitch. In the containment reading the census used, as in corollary
   (c), it fails at F₂: lagged free pairs in 20 harmonies, and free 3-sets in one, which the census did not search. Restate it in the
   exact reading and cite (a), and note the free pairs. **Not a block.**
3. **Corollary (c) and the census's framing.** A ratio subgroup or coset inside the stitch pairs would give a free product containing
   the additive law, by (a), not an additive automaton. The census looked for what would have been free products. Say so where the
   note and the pre-registration call a coset "an affine automaton on the lagged stitch". **Not a block.**
4. **One kind set per harmony.** Say that the census holds one kind set per harmony, and cite the all-kind-sets check: 1,383 kind
   sets, the same zeros. **Not a block.**
5. **"What it leaves open".** "Permutive sub-stitches with entries in different orbits" is too broad. The theorem covers one set of
   states spread over orbits. The open case is three different ranges, and there only (a) holds. **Not a block.**
6. **Novelty.** Not found in a bounded search. The lemma is elementary and may be folklore (section 1).

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_line.py` | `result_line.json` | the census rebuilt |
| `ref_line_checks.py` | `result_checks.json` | row comparison, blocks, free pairs and cosets, span 9, the lemma exhaustive and by SAT, the chain on laws that are not harmonies |
| `ref_line_presentations.py` | `result_presentations.json` | every kind set |
| `ref_line_ranges.py` | `result_ranges.json` | three ranges |
| `ref_line_lagged.py` | `result_lagged.json` | lags, one set, orders 2 and 3 |
| `ref_line_sites.py` | `result_sites.json` | ranges that depend on the site |
| `ref_line_product.py` | `result_product.json` | the product lemma |
| `ref_line_converse.py` | `result_converse.json` | the converse |
