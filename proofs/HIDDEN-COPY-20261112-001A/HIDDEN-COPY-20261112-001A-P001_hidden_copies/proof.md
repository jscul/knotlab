# Influence through hidden copies

Status: Proved where stated (the algebra, by hand with the advisor model, by known theorems) with an exact census; the endo part stopped
at its cap; **referee pending** (the background referee thread). Ticket A of `research/HIDDEN-COPY-20261112-001/preregistration.md`,
frozen with the code in commit `44e339263`.

Words and the algebra as in the pre-registration: gadgets of stitched harmony copies (not bare not-all-equal knots); End, Aut, E-small,
E-large; essentially unary or affine (Pálfy); factor-permutive.

## 1. The census (frozen)

- **endo.** Stopped at its one-hour cap with 1,001 of the 1,267 (harmony, kind set) pairs, covering 17 of the 40 harmonies (the
  alternation alone has 496 kind sets); reported with the pairs reached, as frozen (`assemble_after_cap.py`). 814 pairs are E-small and
  187 E-large; 69 have automorphisms beyond the shifts and flips. Under the census's kind sets, 10 of the 16 harmonies whose census kind
  set was reached are E-small: every single-orbit one (the alternation among them), and 000111 + 01. Multi-orbit harmonies are mostly E-large. No E-small pair has
  three or more Aut-orbits.
- **binary.** Its first launch failed because the endo part, killed at its cap, had written no result; it was relaunched on the assembled
  rows. Of 318 E-small pairs with 3 to 12 states, 136 have no essential binary polymorphism (essentially unary) and none has one
  (affine); 182 are not settled within 3,000 rounds.
- **gadgets.** For the 18 harmonies with at most 12 states, under their census kind sets, none of the 486,000 gadgets (1 or 2 hidden
  copies, 2 or 3 stitches) gives a factor-permutive relation with Z₂ readouts constant on the shift-and-flip classes. Of the 54 random
  baseline relations, 2 do (both for the three-orbit harmony 000111 + 0011 + 01; 3,396 of their gadgets).
- **The frozen failure criterion is met as worded:** no E-small, essentially unary pair has three Aut-orbits, the condition of the frozen
  construction, and no gadget in the census is factor-permutive.

## 2. After the run (the advisor's second check; descriptive and by known theorems; `after_run_factor.py`)

- **Every E-small pair with at least three states is essentially unary**, the 182 unsettled ones included, without the search: the
  affine branch of Pálfy's theorem needs |W| a prime power and Aut = {λx + c}, a transitive group none of whose elements is a single
  cycle through W unless |W| is prime; each of the 318 pairs has Aut intransitive, |W| not a prime power, or an automorphism (the shift)
  that is one cycle through W with |W| not prime. With constants among the polymorphisms, no essential binary polymorphism already gives
  essentially unary (the advisor's elementary argument; Pálfy is needed only for the other branch).
- **A wider construction than the frozen one.** In the essentially unary case the gadget relations are exactly those containing the
  diagonal and invariant under Aut. Any Aut-invariant partition of W into **three classes** then gives a factor-permutive gadget relation:
  "the three copies' classes are all equal or all different" (Ledrappier's law over Z₃ on the classes), kept by every permutation of the
  classes. A partition into two or four classes gives a four-member one (x + y + z + w = 0 over Z₂ or Z₂²) only.
- **Counts.** Of the 318 E-small pairs, 102 have an invariant three-class partition, so a ternary factor-permutive gadget relation;
  the other 216 have only four-member ones. Six harmonies have the ternary one under every E-small kind set reached: 000111,
  000000111111, 001010110101, 000111 + 01, 0000011111 + 01 and 0010011011 + 01.
- **Gadget size.** The argument bounds the gadget by |W|^m copies (m the number of Aut-orbits of non-diagonal triples of the relation),
  impractical (about 6^11 for 000111); none appeared within the census's bound, which also looked only at Z₂ readouts.

## What this establishes

- Settled by definition: gadgets of stitched harmony copies never give flip-blind parity (they allow all copies equal).
- Proved (known theorems applied; the referee to check): every E-small pair reached is essentially unary; then gadget relations are the
  diagonal-containing Aut-invariant ones, and three invariant classes give a ternary factor-permutive relation.
- Exact on the range: E-small is common for single-orbit harmonies and rare for multi-orbit ones; no small gadget (≤ 2 hidden copies,
  ≤ 3 stitches) gives a factor-permutive relation with Z₂ readouts, while 2 of 54 random relations of the same size do.
- Not established: the endo classification of the 23 harmonies the cap did not reach; an explicit gadget of practical size for the
  mod-3 relation; whether such gadgets, used as knots, carry Ledrappier-type influence in an arrangement.
