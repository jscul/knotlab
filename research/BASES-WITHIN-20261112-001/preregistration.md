# Pre-registration: bases within bases

Epic `BASES-WITHIN-20261112-001` (backlog B164, G17 with G8 and G6; program mathematics, group arithmetic), written on 2026-11-12
before any census runs, at the coordinator's go-ahead with the owner's approval of the redirect ("Sure, do that."). Code frozen with
this file in `proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series/` (`nest_lib.py`, `check.py`). The
canonical K1–K3 test is unchanged.

## The owner's words

- "I imagine it like we could have infinite recursions. In fact each boolean variable could be its own micro infinite series of
  logic, that's bound to others" (2026-11-11), with fractals as consequences of rules.
- On overlapping (2026-11-12): "By overlapping, I kind of mean like fractal, or meeting patterns that are more complex than just
  triangle edges meeting. Like they can fold in immensely complex ways and can be kind of globally influential."

## Words

As in the guide's glossary: base, distinction, knot, harmony (A70: a one-shift base all of whose states repeat; its states W, closed
under shifts and the mirror; P the least common multiple of their periods), stitch, offset, tie class (distinctions forced equal or
unequal in every state), bond distance (fewest knots in a chain). For this epic:

- **Inner harmony, outer base, stitched.** Each distinction X_j of an outer base O becomes a copy of an inner harmony I (distinctions
  x_(j,i) at every whole number i, with I's knots). Each outer knot on (X_a, X_b, X_c) becomes a knot on (x_(a,i+s), x_(b,i+t),
  x_(c,i+u)) at every place i: a stitch, as in the glossary, now holding distinctions of three harmonies, with offsets (s, t, u). A
  **stitch at one place** has all offsets 0; a **stitch with offsets** has some not 0. The result is written O[I]. ("Binding" is not
  used: the guide uses it for the knot's own constraint.)
- **Levels.** Doing it again with the same harmony H at every level gives level k: distinctions at every point of Z^k, H's knots along
  every line (all coordinates but one fixed) (the literature's axial power of H, Louidor, Marcus and Pavlov). For a finite seed
  pattern S on m distinctions, level k has the addresses {0..m−1}^k, and the addresses that agree except at one digit form a copy of S
  (the literature's Cartesian product of S with itself k times).
- **The farthest tie** of a distinction: the largest bond distance to a distinction tied to it. Fixing one distinction forces exactly
  its tie class (the mirror keeps every knot), so the farthest tie is how far fixing it reaches.

## What is settled by definition (proved by hand before the run)

- **L1 (the outer level reads disagreement counts).** A stitch at one place of inner states w_a, w_b, w_c holds exactly when
  D_ab + D_bc + D_ac = 2L, D_xy the number of places in a common period L where w_x and w_y differ: each place has no differing pair or
  exactly two. So the outer level reads, for each pair, how often their states disagree at the offset they sit at: more than periods
  and offsets, as `HARMONY-ARITH-20261112-001` found for stitches of two.
- **L2 (harmonies of harmonies are harmonies).** If O and I are harmonies, every state of O[I] has rows that are I-states and columns
  that are O-states, so it repeats along both shifts and there are finitely many.
- **L3 (only the alternation is one distinction exactly).** A reading β: W → {0, 1} with "a stitch at one place holds exactly when
  β(w_a), β(w_b), β(w_c) are not all equal" exists only if |W| = 2, that is, I is the alternation 0101…: (w, w, w') is allowed exactly
  when w' is w's mirror, which forces β(w') = β(w) for every other w', a contradiction once |W| > 2.
- **L4 (the mirror lift; the advisor's).** For any outer base O, any O-state s and any inner state w, x_(j,i) = s_j ⊕ w(i) is a state of
  O[I] under stitches at one place: each row is w or its mirror, and each stitched knot reads s's values, flipped together or not. So
  O[I] lives exactly when O lives, the column at any place realises exactly O's states, and two harmonies stitched at one place never
  end. In the literature's terms, the inner template is homomorphically equivalent to plain not-all-equal (Barto, Opršal and Pinsker):
  bases within bases stitched at one place keep the outer law exactly, at every level, and only add states.
- **L5 (the alternation is a fixed point).** With I the alternation, O[I] is O again (x_(j,i) = s_j ⊕ (i mod 2)), at every level.
- **L6 (levels never end).** u(c_1 + … + c_k + a) and u_1(c_1) ⊕ … ⊕ u_k(c_k), each u a state, are states of level k.
- **L7 (ties multiply; the advisor's form).** At level k of a seed (a harmony or a finite pattern that lives), two distinctions are tied
  exactly when, at every coordinate where they differ, the two coordinates are tied in the seed; the forced relations add. *If:* each
  copy of the seed along one coordinate is a seed state; chain coordinate by coordinate. *Only if:* a mirror-lift state with one
  coordinate's seed state swapped separates them. So the tie class at level k is the k-fold product of the seed's, the farthest tie
  grows as k times the seed's, exactly as the farthest distinction does, and a seed with no ties forces nothing at any level.
- **L8 (offsets matter only around closed chains).** If no chain of distinct knots returns to its start (the literature's
  Berge-acyclic pattern), shifting each inner copy absorbs every offset, and a stitch with offsets lives exactly when O does.
- **L9 (the alternation's offsets are signs).** With I the alternation, an odd offset flips a member: O[I] with offsets is the
  signed not-all-equal pattern with those signs.

So, before any computation: stitched at one place, the inner harmonies are invisible to what the outer base allows; nesting adds states,
never constraints, and never forcing beyond the seed's own. The census tests the parts the lemmas do not decide.

## The census (frozen; exact on stated ranges)

- **E1, levels of each harmony.** Every not-all-equal harmony of one to three kinds, span 2 to 8, with P ≤ 16 (45 state sets): the
  number of states at levels 2 and 3 on Z_P^k (capped at 100,000), the linear and mirror-lift states of L6, rigid when only linear
  states occur; and the tie class of the origin at level 2 against L7.
- **E2, stitches with offsets.** Every one of the 45 harmonies against every connected outer pattern of up to 6 distinctions and 4
  knots (31, one per isomorphism class), the Fano plane less one knot and the Fano plane: stitches at one place, and 60 assignments
  of offsets (0, s, t) per knot, s and t uniform modulo P (seeded); for the alternation every offset in {0, 1}, compared with signed
  not-all-equal. Measured: how many end while the outer base lives.
- **E3, levels of finite seeds.** Seeds: one knot; two knots sharing one distinction; two sharing two; a closed chain of three knots;
  the Fano plane less one knot. Levels 1 to 4 (up to 2,401 distinctions): lives; for each diagonal origin (a, …, a), its tie class
  against L7, its farthest tie and its farthest distinction.
- **E4, a drawn three-copy nesting.** One knot at level 0; level n is three copies of level n − 1 sharing their meeting corners (a
  drawn construction, the literature's Sierpinski gasket), levels 0 to 7 (up to 3,282 distinctions and 2,187 knots): lives; tie class,
  farthest tie and farthest distinction for a corner and for a shared corner. Its farthest distinction grows as 2^n, so how far
  forcing reaches against depth is a real question here, not settled by L7.
- **Control (the advisor's).** Under the exactly-one law, with I the shifts of 001 and O the knots (0,1,2), (0,1,3), (2,3,4) (two
  states), stitches at one place must end: the harness must detect an outer base that lives while O[I] ends. Run before the freeze on
  this control only: it ends, as it must.
- **Caps.** Each part 1 hour and 16 GB by its systemd unit; a count over its cap is reported as such.

## Predictions and failure criteria (frozen)

The advisor model was consulted twice before this freeze (the rule since 2026-11-12); P1 to P6 are its predictions, recorded as its,
and P7 is this epic's.

- **Checks of the lemmas (a failure is a code error or a wrong lemma, to be found before anything else):** L4 (every outer base stitched at
  one place lives exactly when it lives alone), L7 (E1 and E3 ties equal the product), L8 (no chain-free pattern ends under offsets),
  L9 (the alternation agrees with signed not-all-equal on every offset), no level below its known states, and the control ends.
- **P1.** Level 2 of 0011 has 16 states and level 3 has 256 (certain).
- **P2.** Level 2 of 000111 has 102 states (about 90%).
- **P3.** Level 2 is rigid (only linear states) exactly for the alternation (certain).
- **P4.** For every harmony, some assignment of offsets ends an outer base that lives (high).
- **P5.** E3: every seed lives at every level; only the Fano plane less one knot has ties, its tie class from an origin on the removed
  knot's three distinctions is that set to the power k, with farthest tie 2k equal to its farthest distinction; every other seed's
  origins are tied to nothing (theorem, by L7 and the seeds' own ties, found by brute force on the seeds before the freeze: only the
  removed knot's three distinctions are tied, pairwise).
- **P6.** For the Fano seed, the tied share of an origin falls as (3/7)^k (theorem): reach spans the whole pattern while the share
  forced shrinks. The headline measure, frozen now: the farthest tie against the farthest distinction, with the share beside it.
- **P7.** E4: the nesting lives at every level and no corner is tied to any other distinction: fixing one forces nothing, at every
  depth. Predicted with moderate confidence. If ties appear, how far they reach against 2^n is the result.
- **Answer by rule.** The checks, P1 to P7, and what the four arms say about the owner's three questions (what the outer level reads,
  whether repeating changes anything, which combinations end); stop there, report and hold. A native rule for offsets that does not
  reduce to stitches at one place was not found before the freeze (the advisor: offsets that respect the pattern's own symmetries
  are flat); E2's offsets are sampled, not chosen.

## Known mathematics, checked before the freeze

Axial powers of one-dimensional shifts and their entropy (Louidor, Marcus and Pavlov, "Independence entropy of Z^d shift spaces";
Meyerovitch and Pavlov, arXiv 1112.1351), whose finite case has no entropy, so counts on Z_P^k are the right measure here; rows and
columns from two one-dimensional shifts (arXiv 2203.00434); homomorphic equivalence and reflections of templates (Barto, Opršal and
Pinsker, "The wonderland of reflections"); Cartesian products of hypergraphs; bundles and covering (voltage) graphs for offsets
(Pisanski, Shawe-Taylor and Vrabec; Gross and Tucker); self-simulating tile sets whose macro-tiles obey the same rules (Durand,
Romashchenko and Shen, "Fixed-point tile sets and their applications"); hierarchical lattices (Berker and Ostlund; Kaufman and
Griffiths) and finitely ramified fractals (Gefen, Aharony and Mandelbrot); frozen variables and correlation length in random
constraint problems (Achlioptas and Ricci-Tersenghi; Montanari and Semerjian). The program's own: `HARMONY-ARITH-20261112-001`
(stitches), `OVERLAP-READ-20261111-001`, `NEST-ATOMS-20261110-001`, `GEOMETRY-LAW-20261029-001`, and the counting epics on drawn
three-copy nestings of 2026-10-29.

**Referee.** By the arrangement of 2026-11-12, the background referee thread, after the run (referee pending until its verdict).

Assumptions in force: A70. A new one, recorded with this epic: the owner's "bound to others" is read as stitches at one place, with
stitches with offsets as the variant (A75, challengeable: a substitution reading, each distinction replaced by a finite block,
would differ). Nothing here bears on P versus NP.
