# Pre-registration: influence through hidden copies

Epic `HIDDEN-COPY-20261112-001` (the open route of `LINE-LOCK-R1`, chosen by the coordinator in place of `LINE-LOCK-20261112-001`
#R1, which is settled by definition; G17 with G8; program mathematics, group arithmetic), written on 2026-11-12 before the census runs,
at the coordinator's go-ahead under the owner's standing mandate. Code frozen with this file in
`proofs/HIDDEN-COPY-20261112-001A/HIDDEN-COPY-20261112-001A-P001_hidden_copies/` (`hidden_lib.py`, `check.py`). The canonical K1–K3 test
is unchanged.

## The question

A harmony's stitch holds no additive law exactly (`LINE-LOCK-20261112-001` and its referee's product lemma). Influence of Ledrappier's
kind could still come through **hidden copies**: a gadget of harmony copies joined by one-order stitches, three of them observed and the
rest hidden (quantified away). Can such gadgets give an additive relation on the observed copies, and how common is that?

## Two kinds of gadget, kept apart

- **Gadgets of stitched harmony copies (this epic).** Every unit is a whole copy, a state of the harmony; every constraint is the
  one-order stitch R between three copies. All copies equal is always a state (R holds the diagonal, being the harmony's own knots),
  so every such gadget's relation contains every all-equal triple. Hence flip-blind parity on copies, which excludes them, is never a
  gadget relation of this kind, at any size: settled by definition.
- **Gadgets of bare not-all-equal knots on single distinctions** (A78; `PARITY-MIX-R1`'s explicit gadget, 57 knots and 53 hidden
  distinctions per place). All-equal is not a solution of bare not-all-equal, so parity among places is buildable there. That is a
  different object and not what this epic asks.

## The algebra (stated for the referee to check line by line)

Let A = (W; Pol(W; R)), the set of states with every polymorphism of R as an operation.

1. Every constant map W → W keeps R, because R contains (w, w, w) for every state w. So every constant is a term operation of A, and A's
   polynomial operations (term operations with constants put in) are its term operations: the term clone and the polynomial clone agree.
2. The unary term operations of A are exactly End(W; R), the maps W → W keeping R; by 1, these are also its unary polynomials.
3. **E-small** means End(W; R) = Aut(W; R) ∪ {constants}. Then every unary polynomial of A is a permutation or a constant, which is the
   hypothesis of Pálfy's theorem (1984) for a finite algebra with at least three elements: such an algebra is either **essentially
   unary** (every polynomial depends on at most one variable) or **polynomially equivalent to a vector space** over a finite field
   (**affine**).
4. In the affine case, A has an essential binary polynomial (x + y − c), which by 1 is a binary polymorphism of R depending on both
   arguments. In the essentially unary case, no polymorphism depends on two arguments. So, for E-small harmonies with at least three
   states, **an essential binary polymorphism exists exactly in the affine case**: a SAT search for one decides the branch.
5. In the essentially unary case, Pol(W; R) = {e(x_i) : e ∈ End}. By the Galois correspondence (Geiger, 1968; Bodnarchuk, Kaluzhnin,
   Kotov and Romov, 1969), a relation is pp-definable from R, that is a gadget relation (stitches among copies, hidden copies quantified,
   copies identified or repeated in a stitch allowed), exactly when every polymorphism keeps it: exactly when it contains every
   all-equal triple and is invariant under Aut. **With at least three Aut-orbits, some gadget relation is factor-permutive** (Z₂ readouts
   π₁, π₂, π₃ constant on Aut-orbits with π₃ = π₁ + π₂, the advisor's construction: π₁(u) + π₂(v) + π₃(w) = 0 contains the diagonal, is
   Aut-invariant, and its readout image is the graph of addition on Z₂ with full pair projections). This existence is close to settled
   by definition once the clone is known; its gadget size is not bounded by the argument.
6. Degenerate case: the alternation 01 has two states and R = {(u, u, w)}; every operation keeps R, so the gadget relations are those
   built from equality, and none is factor-permutive. Pálfy's theorem is not used for it.
7. **E-large** (a non-injective, non-constant endomorphism): the argument above does not apply; gadget relations are invariant under that
   endomorphism too. These are left undecided except by the gadget census.

## The census (frozen; each harmony and kind set is one sample looked at)

- **endo.** The 40 harmonies of period at most 16 with at most 36 states (of the 45: those with 48, 64, 64, 66 and 128 states left
  out), with each of their 1,267 kind sets of 1 to 3 kinds and span at most 8 (the presentation matters: `PARITY-MIX-R1`): E-small or
  E-large (SAT for a non-injective, non-constant endomorphism, preservation added lazily, at most 3,000 rounds, else "not settled");
  automorphisms beyond the shifts and flips (up to 200); the number of Aut-orbits.
- **binary.** For every E-small (harmony, kind set) with 3 to 12 states: an essential binary polymorphism (affine) or none (essentially
  unary); at most 3,000 rounds, else "not settled".
- **gadgets.** For every harmony with at most 12 states, its census kind set: every gadget with three observed copies, one or two hidden
  copies and two or three stitches among distinct copies, every copy in some stitch (the search bound); its relation, and whether Z₂
  readouts constant on the shift-and-flip classes make it factor-permutive. **Baseline:** the same gadgets with R replaced by 3 random
  relations per harmony that contain the diagonal, are invariant under the shifts and flips, and have as many triples as R (unions of
  random orbits of W³), so that what any such relation gives is not counted as the harmony's doing.
- **Cap.** 1 hour and 16 GB per part, rows saved as they finish.

## What counts (frozen)

- Not settled by definition, and reported: how many of the 40 harmonies (and of the 1,267 kind sets) are E-small; unary against affine
  among them; Aut-orbit counts; so how many admit gadget-definable factor-permutive relations by item 5; the smallest gadget found for
  one (within the search bound), and how common factor-permutive relations are among the gadgets, against the baseline.
- **Failure (for the claim that the harmony format makes such influence):** no (harmony, kind set) is E-small and essentially unary
  with at least three Aut-orbits, and no gadget in the census is factor-permutive. If the baseline relations are factor-permutive as
  often as the harmonies', the harmonies are not special.
- **Publication hold.** A gadget is an ordinary reduction device. If anything looked like an efficient general method for SAT, it would
  not be committed (owner's rule); nothing here is expected to.

## Predictions (frozen; the advisor's unless marked)

- Every E-small harmony with at least three states is essentially unary (95%); the affine branch never occurs with more than 4 states
  (90%).
- Aut equals the shifts and flips for most pairs (70%); most of the 40 harmonies are E-small (55%).
- Some (harmony, kind set) admits gadget-definable factor-permutive influence (75%).
- A gadget with at most two hidden copies shows it (20%).

## Known mathematics

Geiger (1968) and Bodnarchuk, Kaluzhnin, Kotov and Romov (1969) for the Galois correspondence; Pálfy (1984) on algebras whose unary
polynomials are permutations or constants; bounded width and the ability to count (Feder and Vardi; Larose and Zádori; Barto and
Kozik) for the variants with pinned copies; Ledrappier's three-dot system as the target; Schaefer for bare not-all-equal. The algebra is
not new; the classification of the harmonies and the gadget sizes are new data.

## Seen before the freeze (disclosed)

The enumeration (40 harmonies, 1,267 kind sets) and a smoke test on the alternation 01 only (two states: E-small trivially, 2
automorphisms, 27,000 gadgets with 5 distinct relations, none factor-permutive). The state and stitch-triple counts of the 45 harmonies.

**Referee.** The background referee thread (referee pending). Assumptions in force: A70, A78. Nothing here bears on P versus NP.
