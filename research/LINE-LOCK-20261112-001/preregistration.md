# Pre-registration: lines in the increments

Epic `LINE-LOCK-20261112-001` (`SHIFT-LOCK-20261112-001` direction 1, influence beyond cycles; G17 with G8; program mathematics, group
arithmetic), written on 2026-11-12 before the census runs, at the coordinator's go-ahead under the owner's standing mandate. Code frozen
with this file in `proofs/LINE-LOCK-20261112-001A/LINE-LOCK-20261112-001A-P001_lines_in_increments/` (`line_lib.py`, `check.py`). The
canonical K1–K3 test is unchanged.

## The question and what is already known

`SHIFT-LOCK-20261112-001` found states of copies along two shifts that repeat along no step, but no influence beyond cycles: locks that
hold at every size come from strips and short-step arithmetic. Influence of Ledrappier's kind (lock sets that follow polynomial
arithmetic, not eventually periodic) would need a **linear automaton inside the stitch**. Does any harmony's one-order stitch hold one?

Prior work, stated first: Ledrappier's shift (1978); Markov subgroups and periodic points of algebraic actions of ℤ² (Kitchens and
Schmidt, 1988–1992; Schmidt's *Dynamical Systems of Algebraic Origin*); linear and permutive cellular automata (Hedlund, 1969;
Ito, Osato and Nasu, 1983; Martin, Odlyzko and Wolfram, 1984; Moore on quasigroup automata); three-point permutive (Latin) shapes, the
totally extremally permutive subshifts, of which Ledrappier's is the prime example (Salo, "Cutting corners", 2022); not-all-equal has
only trivial polymorphisms (Schaefer), so no Mal'tsev structure. What would be new: the obstruction below (the advisor model has not
seen it stated) and the census of cosets in this family.

## Words

As in `SHIFT-LOCK-20261112-001` and the glossary: harmony (A70: every state on the integers repeats), one-order stitch R ⊆ W³, copy
shifts, mixed knot, the harmony's shift σ and flip κ. For one orbit O of ⟨σ, κ⟩, Q is the group acting simply transitively on it
(shifts by the orbit's own period with the flip, the flip read as a half shift when the orbit is antiperiodic), and the **increments**
are A = {(y, z) ∈ Q² : R(u, y·u, z·u)}. New, plain: a **Latin sub-law** of R is a set T of triples of states, inside R, in which any two
entries determine the third (the literature's quasigroup or permutive law); a **line** is a cyclic subgroup of Q² inside A whose
order-q part, for an odd prime q, is ⟨(g, λg)⟩ with λ not 0 or 1 modulo q; the three **degenerate lines** {(a, 0)}, {(a, a)}, {(0, b)}
give states constant along a direction. A line gives the linear automaton t(x + q) = (1 − λ) t(x) + λ t(x + p) over F_q on any
three-member knot shape {0, p, q} (the advisor's convention); a lagged stitch translates A, so a **coset** d + Λ inside A gives an affine
automaton on the lagged stitch.

## Settled by hand (before the run; the advisor model's lemma, rechecked here)

- **Theorem (two constant fibres).** If H is a harmony, R contains no Latin sub-law on a set S of at least two states with all three
  entries ranging over S. *Proof.* Fix a kind (0, a, b) and a place i, and read each state's bit at i, i + a, i + b as three fibres
  x, y, z over S. If x and y were both non-constant, with X₀ = {x = 0} of size r and Y₀ of size c, the Latin rectangle X₀ × Y₀ would
  need at least max(r, c) third entries all with z = 1 and X₁ × Y₁ at least max(n − r, n − c) all with z = 0, so r = c and X₀ × Y₀ is
  a Latin subsquare on the symbol set Σ = {z = 1}; then a column of Y₁ meets the rows of X₀ in r symbols outside Σ and the rows of X₁ in
  symbols with z = 0, also outside Σ, so it misses Σ, which a Latin column cannot. So at most one fibre is non-constant, and then the
  other two are constant and opposite. Two distinct states differ at some place i; the fibre at i is then non-constant in each of its
  three roles (first member at i, second at i − a, third at i − b), so in every state of S every knot through i has its other two
  members opposite. Flipping place i of such a state at a single place on the integers keeps every knot, giving a state that does not
  repeat: not a harmony. ∎
- **Corollaries.** No orbit's increments hold a line (on the coset of the order-q subgroup through u, a line is a Latin sub-law), nor
  the Z₂ × Z₂ graph block (the advisor's F₄ automaton), nor a free pair (H × H inside A). This covers every harmony at every period,
  including the odd harmonies at 61, 73 and 193 (where the advisor's earlier antiperiod argument also works), and every two-way knot
  shape and slot order: **settled by the theorem, not by a run.** So the unlagged one-order stitch of a harmony never holds a linear
  automaton.
- **What the theorem leaves open (where the census has content).** Cosets d + Λ with d outside Λ: there the three entries range over
  different sets of states (d₁·S and d₂·S), the fibres in different roles belong to different states, and only a necessary condition
  follows. A coset whose offset has no flip part is realised by a lagged stitch (lags translate A by shifts); one with a flip part is
  not realised by any lag. Also open: Latin sub-laws whose entries lie in different orbits, laws seen only after blocking several copies,
  and functional but not permutive sub-laws (automata without polynomial arithmetic).

## The census (frozen; exact)

Every orbit of every harmony in range, chosen by no outcome: the 66 harmonies of span at most 8 (every period from 2 to 240; the
`BASES-WITHIN-20261112-001` enumeration with the period bound removed) and the 7 odd step sets of `ODD-FAMILY-20261112-001` (61, 73 and
193; three up to a multiplier), every state enumerated. For each orbit: A; every cyclic subgroup of Q² inside A and every coset of one
inside A, each classified at every odd prime of its order (genuine or degenerate, with λ); the F₄ blocks; free pairs; which genuine
cosets a lag can give. For each harmony: whether some state has a free site on the integers (the theorem's premise). Cap: 1 hour and
16 GB.

## What counts (frozen)

- **Theorem checks.** Any genuine subgroup, F₄ block or free pair found, or any harmony with a free site, is a counterexample to the
  proof or its premise: a correction of this file before anything else.
- **The open part.** Genuine cosets a lag can give: if some exist, the lagged stitch holds an affine automaton over F_q, and the
  natural follow-up (not run here) is its lock arithmetic on the lagged arrangement against the automaton's polynomial prediction. If
  none exist, **the obstruction is complete for one-order stitches with or without lags**: stitched harmonies hold no linear automaton,
  so two-way influence of Ledrappier's kind cannot come from them.

## Predictions (frozen)

- Theorem checks all pass (the theorem; 99%).
- No harmony in range has a free site (premise; 99%).
- Genuine cosets a lag can give: none in range (mine, 55%); some genuine cosets with a flip part (mine, 40%).

## A test proposed for the knots-alone thread (frozen here, run there; the advisor's design)

On base 16 (not-all-equal on single bits with knot kinds {0, (0, 1), (1, 0)} and {0, (0, 2), (1, 2)} in the sheared frame), for each
travelling pattern whose freeness no doubly periodic state of period at most 8 certifies:

- **Run.** C = the set of period lattices up to 24 × 24 that certify it, including sheared lattices ⟨(n, 0), (k, m)⟩, since a slope
  that is not a whole number may fit no small rectangle; and, in every certifying doubly periodic state, the count of a local feature
  (a pattern on two or three cells) along each line of each of the three directions (rows, columns, diagonals).
- **The tiling cause predicts:** C is non-empty and cut out by a divisibility condition (d₁ | n, d₂ | m, or one congruence on
  (n, k, m)); the same condition for every pattern with the same travel vector; large coprime sizes fail; and some line count is equal
  across all parallel lines of a state and takes the value the slope predicts (the flux of a height function).
- **Refuted if:** C is empty to 24 × 24; or C holds every size past a threshold (a size effect, not a slope); or every line count varies
  between parallel lines within one state (no height function).
- **Rival control, computed without solving:** wrap-around self-overlap of the pattern's images A + jkt on the repeat, which can destroy
  freeness on small repeats; if the lattices where those images are disjoint or identical match C, the cause is wrap-around, not tiling.

## Seen before the freeze (disclosed)

Smoke tests of the code on the three smallest harmonies (01, 0011, 000111): no subgroup, coset, block or free pair beyond one degenerate
order-2 subgroup of 01; no free site. The counts of harmonies by period (66, periods 2 to 240) and their state counts.

**Referee.** The background referee thread (referee pending). Assumptions in force: A70, A75, A77. Nothing here bears on P versus NP.
