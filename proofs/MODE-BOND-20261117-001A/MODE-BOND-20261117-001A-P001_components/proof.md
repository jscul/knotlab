# The 13 grow: the carried link lies outside the top's component

`MODE-BOND-20261117-001A-P001`, epic `MODE-BOND-20261117-001`, 2026-11-17. Written by Claude. The advisor checked the design before
the freeze (`research/MODE-BOND-20261117-001/advisor/design_answer.md`). Proof by hand with finite checks: `check.py`, with its result
in `result.json`, and the gates of `research/MODE-BOND-20261117-001/`. It uses Theorem G of `TWO-ENDS-20261117-001A`, which its
referee confirmed as written (TWO-ENDS-R1), and nothing that rests on Theorem N.

## Setting

As in `TWO-ENDS-20261117-001A`. P_N is the addressed not-all-equal pattern of depth N, a tree of blocks. L_N(k, s) is the least bond
with a member at level k and one at level k + s, and k = 3. A child orbit is **joined** to its parent when some knot of the parent's
block has a member in it. The **components** are those of the pattern's knots, read as a hypergraph on addresses.

## Lemma J (a bond lies in one component)

*Every bond of P_N lies inside one component.*

*Proof.* Split a set B across two components as B₁ ∪ B₂. Every state of one component combines with every state of the other, so
the projection onto B is the product of the projections onto B₁ and B₂. If B is constrained, B₁ or B₂ is, and B is not minimal. ∎

## Theorem G on a component

*Let C be the component of the level-k addresses, and suppose every saturated composite of exactly ℓ₀ steps along joined children,
between orbits of types found in C, is a product. Then L_N(k, s) ≥ (⌊n/ℓ₀⌋ + 3)/2, with n = min(s − 1, s + r − R).*

*Proof.* By Lemma J a bond meeting level k lies in C. Take an orbit of its skeleton S (the orbits holding a member and those above
them) below level k. The step from its parent to it is joined. If it were not, the orbit's subtree would meet the rest of the pattern
only through its parent's block, which holds no knot on it, so its component would lie below level k and hold no member of the bond.
So every crossing of a member-free window of S runs along joined children, and Theorem G's proof (`TWO-ENDS-20261117-001A`) applies
with these composites. ∎

## The 13 mutants of 8db5da810c00 (5 distinct patterns)

*For each of −73, −76, −81, −89 and −100 (the 5 distinct patterns of the 13 descriptions), L_N(3, s) ≥ (⌊(s − 1)/5⌋ + 3)/2 for every
s ≥ 1 and every N ≥ 3 + s. The reach grows linearly.*

*Proof.* Read from the blocks (`growth13.py`, `growth13.json`):
1. **The self-similar type sits in its own components.**
   - In the blocks of types 4, 5 and 7, every knot lies in the orbit and its first child. The second child is not joined: it is the
     self-similar type 7.
   - Type 7 occurs only as a child of types 4, 5 and 7, and the joined child of a type-7 orbit is again type 7. So the component of
     any type-7 orbit lies in the subtree of a type-7 orbit that is an unjoined second child, at level 4 or below.
   - It never reaches level 3, at every depth. At depth 11 the census's component labelling confirms it: none of the 3,512
     addresses of type-7 orbits shares a component with a level-3 address.
2. **On the top's component every long composite is a product.** The types joined to level 3 are 2, 3, 4, 5, 6 and 8. Along joined
   children their saturated composite automaton has 52 to 54 states, threshold 5 and period 2. Every composite of 5 steps is a
   product, so ℓ₀ = 5. Here F holds every assignment, so r₀ = 0, R = 1 and n = s − 1.

Theorem G on the component gives the bound. ∎

The one non-product composite that blocked the product test in `TWO-ENDS-20261117-001` (the all-equal and split links) runs only along
the self-similar type, inside components that never meet level 3. No bond with a member at level 3 can use it.

## Computed

- **The decorated test** (`decorated.py`, `run_decorated.py`, `decorated.json`; the frozen design) finds no gadget for any of the 5
  patterns. Its closure has nontrivial pairs only at the self-similar type: the entry blocks (types 4 and 5) give a product with
  their type-7 child for each of the 426 and 347 sibling restrictions, since no knot joins them. On the bounded controls it finds
  gadgets: 70,260, 904 and 62 for bace53f8f952-58, -111 and -147. The two ca1efb37ad88 controls had not finished when this was written.
- **The product test along joined children** (`joined_census.py`, `joined_census.json`), on the census's 786 small-orbit
  descriptions alive at every depth (181 distinct patterns), passes for exactly the 740 that forget and fails for the 46 that do not,
  as Theorem G requires of the bounded ones.
  - Of KEEP-REACH's 39 third-class descriptions it passes the 13.
  - It fails the 12 bounded ones, as it must.
  - It fails the 14 that grow by Theorem F′, so it is a sufficient test, not a complete one.
- **The SAT gate** (`gate_growth.py`, `gate_growth.json`). At depth 11, for each of the 5 patterns, 92 pairs (an orbit at level 3
  or 4 of the top's component, and a joined descendant 5 or 6 levels down) all have product pair projections. The 9 unjoined type-7
  children at levels 4 to 6 have product pair projections with their parents.

## What this settles

With CARRIER's carriers, Theorem F′ and this proposition, all 39 third-class descriptions of KEEP-REACH (16 distinct patterns) are
decided:
- 14 descriptions (6 patterns) grow by Theorem F′;
- 12 (5 patterns) are bounded by orbit-and-block or stem bonds;
- 13 (5 patterns) grow by Theorem G on the component.

So every one of KEEP-REACH's 2,380 fresh and mutated small-orbit descriptions (583 distinct patterns) is decided. In every bounded
one, the reach is held by a bond inside bounded pieces at two ends, the top and the lower member. So C* with two ends fits the whole
population, and the bottom band is never needed there.

## Dependencies

- `TWO-ENDS-20261117-001A`: Theorem G (refereed) and the composite automaton.
- `CARRIER-20261117-001A`: the carriers of the 12.
- `KEEP-REACH-20261117-001A`: Theorem F′ and the 39.
- `LEVEL-REACH-20261114-001`: the census, its pattern construction and component labelling.
