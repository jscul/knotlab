# Can nested patterns count? Pre-registration

Epic `NEST-COUNT-20261112-001` (`WITNESS-COUNT-20261112-001` direction 2; G17, with G1), 2026-11-12, agreed by the owner ("Sure.")
after he asked how Gödel's work relates to ours. Frozen before the proofs are written out. The canonical K1–K3 test is unchanged.
The law is NAE on three-place knots on distinct distinctions.

## The question

Compactness (Gödel 1930) is where the limit-only families came from; incompleteness (1931) needs a system that can count. Can nested
patterns of the A79 language count, and is whether they live decided by a procedure that always ends? If not, what is the smallest
extension in which living becomes undecidable and a counter can be built?

## Statements (frozen; the advisor's review folded in, `advisor_review_answer.md`)

The A79 language: finitely many definitions, called only by later ones (no cycles apart from SELF), arguments of a call distinct,
each definition with at most six ports and six own distinctions, SELF only in three-port definitions; depth t, depth 1 making SELF a
knot; the usual limit keeps the knots present at all but finitely many depths.

- **T1 (finite state).** The self-holding definitions' port relations at depth t form a tuple X_t in a set of at most 16^s values
  (s self-holding definitions), with X_{t+1} = Φ(X_t) for a map fixed by the description. So X_t, every definition's relation at
  depth t and "the depth-t pattern lives" are eventually periodic in t, with preperiod plus period at most 16^s. The bottomless
  pattern lives iff the main relation is non-empty at the greatest fixed point reached from "nothing" by Kleene iteration, in at most
  4s strict decreases (compactness). The usual limit is the bottomless pattern of a modified description: in each self-holding
  definition with a SELF call on a permutation of its own ports, add the knot on its ports and delete those calls; so it is decided
  the same way. Whether the depth-t patterns live and whether the limit lives can differ (`LIMIT-ONLY-20261112-001`).
- **T2 (no counter in a top window).** For each fixed b, the states the depth-t pattern allows on the distinctions of levels below b
  are a function of X_{t−b}; so they take at most 16^s values and are eventually periodic in t. A bounded top window reads depth only
  modulo the period. Nothing is claimed about windows deep in the pattern, or about readings inside it such as least bonds.
- **P3a (gadget).** x ≠ y holds iff some a, b, c have NAE(x,y,a), NAE(x,y,b), NAE(x,y,c), NAE(a,b,c); equality is two inequalities
  through a fresh distinction (seven own distinctions, so inside A79 it takes two nested definitions).
- **P3b (every complement-closed relation).** NAE is a base of the co-clone of complement-closed Boolean relations (Böhler, Reith,
  Schnoor and Vollmer 2005); with P3a, every complement-closed relation is defined by NAE knots on distinct distinctions and fresh
  existential distinctions. Concretely, a clause read relative to a reference distinction r (a literal true when it differs from r)
  is a knot or two.
- **P3c (what breaks T1).** For translation-invariant meeting patterns on Z² (a finite fundamental domain copied by every
  translation), "the infinite pattern lives" is undecidable: a Wang tile set tiles the plane iff its encoding lives (one-hot tile
  bits per site read relative to a per-site reference, references of neighbours tied equal, valid-code and compatibility clauses by
  P3b; translation-invariant because every auxiliary is per site). Berger 1966; known in this form (Freedman 1998, k-SAT on groups).
  A counter in the sense of the seeded domino problem (Wang 1961) is then also expressible. What fails is the bounded interface.

## What is not claimed

That counting needs unbounded interfaces (only that bounded Boolean interfaces with uniform recursion are finite-state, and that one
unbounded-interface setting is undecidable); anything about substitution tilings beyond analogy (Robinson 1971, Mozes 1989); any
bearing on P versus NP.

## Failure conditions (frozen)

- A description in the language whose relation sequence is not eventually periodic within 16^s, or whose usual limit differs from
  the modified description's bottomless pattern.
- A top-window state set at depth t that is not determined by X_{t−b}.
- A failure of the gadget, of a pp-definition of one of the 16 complement-closed three-place relations, or of the tile encoding on a
  finite torus (check.py: random tile sets on 2 × 2 and 3 × 3 tori, the encoding's life against direct tiling).

## Rarity under the weighting

Under the A79 weighting no description has a top-window counter beyond a period (T1, T2 hold for every one).

## Stop rule

Proofs and check.py, one run of the checks, a hand-off to the referee thread, report.
