# Pre-registration: nesting by substitution

Epic `SUBST-NEST-20261112-001` (`BASES-WITHIN-20261112-001` direction 1, the named challenge to A75; G17 with G8; program
mathematics, group arithmetic), written on 2026-11-12 before any census runs, at the coordinator's go-ahead under the owner's
standing mandate. Code frozen with this file in
`proofs/SUBST-NEST-20261112-001A/SUBST-NEST-20261112-001A-P001_block_substitution/` (`subst_lib.py`, `check.py`). The canonical K1–K3
test is unchanged.

## The owner's words, and the reading under test

"Each boolean variable could be its own micro infinite series of logic, that's bound to others"; and of overlapping, "like fractal,
or meeting patterns that are more complex than just triangle edges meeting. Like they can fold in immensely complex ways and can be
kind of globally influential." `BASES-WITHIN-20261112-001` read nesting as stitching inner harmonies at one place (A75) and proved it
keeps the outer law exactly and spreads no influence. This epic tests the reading A75 names as its challenge: substitution, where a
distinction (or a knot) is replaced by a finite pattern, again and again.

## Words

As in the guide's glossary: distinction, knot, base, block (a finite pattern of distinctions and knots), tie class, bond distance,
the farthest tie (`BASES-WITHIN-20261112-001`). New here, plain compounds:

- **Block substitution.** A block B on m distinctions and a **cross set** T of ordered triples of B's places. σ(P) replaces each
  distinction v of a pattern P by a copy of B, distinctions (v, p), and each knot (x, y, z) of P by the **cross knots**
  ((x, p), (y, q), (z, r)), (p, q, r) in T. The native cross sets, which do not depend on how B's places are named: the diagonal
  {(p, p, p)}; the block's own knots in every order; every ordered triple of distinct places. Doing it again: σ(σ(P)).
- **Knot substitution.** A **motif** (the hierarchical-lattice literature's word for the cell that replaces each bond): a pattern with
  three **attached distinctions**. Level k + 1 replaces every knot of level k by a copy of the motif glued at its three attached
  distinctions (the drawn three-copy nesting of `BASES-WITHIN-20261112-001` is one motif).
- **A tie outside the copy.** For σ^k(P), a distinction tied to the root whose address begins with a different distinction of P. For a
  P with no ties of its own (every test pattern below), such a tie is created by the substitution.

## What is settled by definition (proved by hand before the run; four from the advisor model)

- **N1 (knot substitution is decided at one level; the advisor's).** The values a level allows on its three attached distinctions form
  a relation closed under the mirror; with a motif whose symmetries move its attached distinctions in every way, it is one of four:
  none, all equal, not-all-equal, or all eight. Each of none, all equal (for a connected motif) and all eight is fixed by the next
  level, so the outcome at every depth is the one read at level 1. And the values a level allows on the distinctions of the level
  before are exactly those of the level before read with the level-1 relation. So knot substitution either keeps not-all-equal at
  every level (the law reproduces itself), frees everything, forces the attached distinctions equal at every level, or ends.
- **N2 (the drawn nesting frees; the advisor's).** For the three-copy motif, setting its three new distinctions to 1 allows 000 on its
  attached distinctions, so level 1 allows all eight, and no distinction is tied to any other at any level: what was found to level 7.
- **N3 (the Fano motif forces equality).** The Fano plane less one knot, attached at that knot's three distinctions, allows exactly
  000 and 111 on them (else the Fano plane would allow a state). So at level k every distinction of level k − 1 is tied to every other,
  and the tied share of an attached distinction is (distinctions at level k − 1) / (distinctions at level k): 3/7, 7/31, 31/175,
  175/1,051. This forcing is the motif's own, not created by nesting: the motif already ties its attached distinctions.
- **N4 (the diagonal keeps the outer law; from the mirror lift).** With T the diagonal, σ(P) is the Cartesian product of P and B, and
  `BASES-WITHIN-20261112-001`'s lemma L7 applies: ties are products, and nothing outside a copy is tied when P has no ties.
- **N5 (a block always lifts; the advisor's).** With T the block's knots or every distinct triple, every state t of B gives the state
  (v, p) ↦ t(p) of σ(P): substitution never ends a pattern. So two distinctions (v, p), (w, q) can be tied only if p = q or p and q are
  tied in B.
- **N6 (loose places free their column; the advisor's).** Call a place p of B **loose** when the other places can be given values so
  that every knot of B holds both values among its places other than p. Then, with T the block's knots, the values at (v, p) can be
  anything while every other place keeps those values: every cross knot and every block knot holds both values among its other
  places. So nothing is tied to (v, p). If every place is loose, σ(P) has no ties at all, at every depth. One knot is such a block.
- **N7 (a rigid block locks the whole pattern; the advisor's, to be checked).** If the only knots of the template (the literature's
  word: the base whose points are B's states, with a knot (t₁, t₂, t₃) when every cross knot holds) are (t, t, t), then for a connected
  P every copy takes the same state of B: σ(P) has exactly as many states as B, and each column {(v, p) : v in P} is tied across the
  whole of P. The advisor reports that all four knots on four distinctions (six states, no ties of its own, no loose place) is such a
  block with T its knots.

## The census (frozen; exact on stated ranges)

- **Arm D, blocks.** Every living connected block on 3 to 5 distinctions with any knots, and on 6 with up to 5 knots, one per
  isomorphism class (87); each of the three native cross sets. For each: the block's states, the template's knots, rigid or not, the
  loose places. Test patterns P, none with ties of its own: chains of 4, 8 and 16 knots (each sharing one distinction with the next),
  and the drawn three-copy nestings of levels 1 to 3, substituted once; chains of 4 and 8 knots and nestings of levels 1 and 2,
  substituted twice. On each: lives, and for a root in every column of P's first distinction, its tie class, its ties outside the
  copy, its farthest tie and its farthest distinction.
- **Arm K, motifs.** The three-copy motif to level 5 and the Fano motif to level 4: the relation on the attached distinctions, the tie
  class of one attached distinction, its share, farthest tie and farthest distinction.
- **Caps.** Each part 1 hour and 16 GB by its systemd unit, registered as long-running; a part over its cap is dropped.
- **Seen before the freeze:** the two motifs' level-1 relations (all eight; 000 and 111), which N2 and N3 state; and the timing of the
  one-knot block, whose outcome N6 decides.

## What counts (frozen)

- **Influence created by substitution, growing with the pattern:** some block and cross set for which, on the chains of 4, 8 and 16
  knots substituted once, the root has ties outside its copy and its farthest tie is at least half its farthest distinction every
  time (the farthest distinction grows with the chain, so the tie keeps up with it).
- **Created only deeper:** ties outside the copy that appear after two substitutions and not after one.
- **None:** no tie outside the copy on any test pattern. Shares are reported beside reach, never in place of it.

## Predictions (frozen)

The advisor model (Fable 5.2) was consulted cold before this freeze (three times on this line, the rule since 2026-11-12); S2 to S5 and
K1, K2 are its, S1 and S6 this epic's.

- **S1.** The diagonal gives no tie outside the copy, for every block (N4; certain).
- **S2.** Every block whose places are all loose gives no tie outside the copy with T its knots (N6; certain), and most blocks are such
  blocks (the advisor's).
- **S3.** All four knots on four distinctions, T its knots: a rigid template; on every test, ties outside the copy with farthest tie
  equal to the farthest distinction in its column, share 1/4, after one substitution and after two (the advisor's; checked by hand).
- **S4.** Rigid templates occur only for dense blocks (the advisor's).
- **S5.** Some block is neither loose everywhere nor rigid and has ties outside the copy: an intermediate case, where folding in the
  owner's sense could live (the advisor: 50%).
- **S6.** No tie outside the copy appears only after two substitutions (this epic's, moderate): ties come from the block's template,
  which a second substitution does not change in kind.
- **K1, K2.** N2 and N3 hold on the explicit levels (theorems).
- **Controls.** The diagonal (S1) and the one-knot block (no ties, N6).
- **Answer by rule.** S1 to S6, K1, K2 and what they say about the owner's "globally influential"; stop there, report and hold.

## Known mathematics, checked before the freeze

Hierarchical lattices and exact decimation (Berker and Ostlund, 1979; Kaufman and Griffiths, 1981; McKay, Berker and Kirkpatrick,
1982, on frustrated ones with chaotic flows); substitution tilings forced by local matching rules in two or more dimensions and never
in one (Mozes; Goodman-Strauss, Annals 1998; Fernique and Ollinger; Vereshchagin 2025); the co-clone of relations closed under the
mirror generated by not-all-equal (Böhler, Reith, Schnoor and Vollmer; Schaefer 1978); functors between relational structures and
their adjoints (Pultr; Foniok and Tardif; Krokhin, Opršal, Wrochna and Živný); unique colourability of products (Greenwell and Lovász,
1974) and Hedetniemi's conjecture (Shitov, 2019), the frame for when every colouring of a product comes from one factor; property B
and the Fano plane as the least triple system with no 2-colouring. The program's own: `BASES-WITHIN-20261112-001`. The folding census
of the knots-alone line measures influence among random periodic bases and is not duplicated here.

**Referee.** The background referee thread, after the run (referee pending).

Assumptions in force: A70, A75 (under challenge by this epic). Nothing here bears on P versus NP.
