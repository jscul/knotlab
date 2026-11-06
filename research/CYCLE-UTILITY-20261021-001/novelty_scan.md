# Novelty scan: composing like cycles is affine structure modulo the tops

Scan for epic `CYCLE-UTILITY-20261021-001`, 2026-10-21. This is read-only
external calibration, not proof lineage. No outside theorem enters a claim
through this note.

## The question

Is the following already in the literature?
- **The claim.** A finite law composes like cycles exactly when four
  conditions hold:
  - every range has a top;
  - ties are bijections modulo the tops;
  - some ternary polymorphism is Mal'tsev modulo the tops of the knot ranges;
  - the tops of knot ranges are then affine over elementary abelian p-groups.
- **The matroids.** Such laws carry exactly the direct sums of matroids
  representable over finite fields.
- **The results checked.** `AFFINE-TOPS-20261021-001A-P001` and
  `…001B-P001`, building on `THOMSEN-KNOTS-20261021-001A-P001` (no circuit
  overlaps).

## Query families and scope

There were about twenty web queries and three page reads, in seven families:
1. matroids or exchange properties of pp-definable relations, relational
   clones and polymorphisms;
2. strong rectangularity, balance and Mal'tsev polymorphisms in counting
   constraint satisfaction;
3. almost affine codes, entropic and partition-representable matroids, and
   ideal secret sharing;
4. common information, the copy lemma, and group-characterizable entropy
   functions;
5. independence algebras (v\*-algebras);
6. model-theoretic pregeometries over finite structures;
7. biased expansions and multiary quasigroups, and amalgams of matroids.

**Limits.** These are abstracts, surveys and two full papers. Universal
algebra's tame congruence theory and the full secret-sharing literature were
not read in depth. The search was in English only.

## Sources and exact relevance

| Source | What it says | Relation to our results |
| --- | --- | --- |
| [Dyer and Richerby, An effective dichotomy for the counting CSP](https://arxiv.org/abs/1003.3879) | Strongly rectangular relations are exactly those invariant under a Mal'tsev polymorphism; counting is tractable exactly for strongly balanced languages | The step from rectangular top images to a Mal'tsev operation is this classical argument, read modulo the tops. Balance marks the limit of our results for counting. |
| [Modular counting CSP](https://arxiv.org/abs/2501.04224) | Restates strong rectangularity ⇔ Mal'tsev for the pp-closure | The same |
| [Kearnes and Szendrei](https://arxiv.org/abs/math/9604246) | Extends Herrmann's theorem: abelian algebras with a Mal'tsev term are affine | Our affine-tops theorem reaches the same shape by a direct self-commuting argument |
| [Zaslavsky, Associativity in multary quasigroups](https://arxiv.org/abs/math/0411268) | A biased expansion of a 3-connected graph is a group expansion. Multiary quasigroups with 3-connected factorization graphs are iterated group isotopes. | The closest "composition forces groups" mechanism. Zaslavsky fixes a base graph. We quantify over all pp-definitions and assume only circuit elimination. |
| [Abbe and Spirkl, Entropic matroids and their representation](https://arxiv.org/abs/1909.12175) | p-entropic matroids are linear for p = 2, 3, but not for p = 9 (the Simonis–Ashikhmin non-Pappus almost affine code over F₃²). The question is open for primes p ≥ 5. | The single-code analogue. A code with uniform fibres can carry a non-representable matroid. Our theorem says its composition closure then cannot compose like cycles. |
| [Kalantari and Khazaei, Four-entropic matroids are quaternary](https://arxiv.org/abs/2608.20553) | 4-entropic matroids are F₄-representable, via excluded minors and quasigroups of order four | A single-code result for one alphabet size, by different means |
| [Bamiloshin, Ben-Efraim, Farràs and Padró](https://arxiv.org/abs/2002.08108) | Classifies matroids by the common-information properties of their representations, for secret sharing | Rectangular top images supply "common information" modulo the tops. Their setting is single matroids and linear-rank inequalities. |
| [Independence algebras (St Andrews)](https://research-portal.st-andrews.ac.uk/en/publications/independence-algebras/) | v\*-algebras, whose subalgebra closure is a matroid with free bases, are classified as affine or linear over division rings, among other types (Urbanik; Cameron and Szabó) | A different closure: subalgebras of one algebra, not free sets of all pp-definable relations. Its conclusion has the same shape. |
| [Cherlin, Finite structures with few types](https://ow3.math.rutgers.edu/~cherlin/Paper/2003FSFT.pdf) | In model theory, finite or ω-categorical structures are coordinatized by affine and projective geometries over finite fields (Cherlin, Hrushovski and Lachlan) | An analogue at the level of first-order definable sets, with different hypotheses |
| [Barto, Krokhin and Willard, Polymorphisms and how to use them](https://drops.dagstuhl.de/storage/02dagstuhl-follow-ups/dfu-vol007/DFU.Vol7.15301.1/DFU.Vol7.15301.1.pdf) | Background: pp-definability equals invariance under polymorphisms | Background only |

## Nearest overlaps and barriers

- **No source states the characterization,** or the statement that circuit
  elimination for every pp-definable relation forces affine structure modulo a
  top.
- **The individual steps are classical:**
  - rectangularity ⇔ Mal'tsev;
  - abelian Mal'tsev ⇒ affine;
  - Schur and density for representability.
- **The program's own input is the step into rectangularity.** That is no
  overlap (THOMSEN-KNOTS) plus uniform fibres.
- **Single codes versus closed laws.** For one code, uniform fibres do not
  force linearity: the non-Pappus code is the standard counterexample. Our
  results concern laws closed under composition. The difference is the
  composition hypothesis, which the entropic literature does not assume.
- **Terminology differs.**
  - "Composes like cycles" is circuit elimination for every pp-definable
    relation.
  - "Free set" is range-relative independence.
  - "Top" is the unique maximal pp-definable equivalence on a range.
  - A search under the coding names (almost affine, entropic) or the algebraic
    names (strongly rectangular, abelian) finds the neighbours, but not this
    statement.

## Effect on the work

- **Selection.** The owner's condition ("if it's novel") is met in the only
  sense the program allows: no overlap in a bounded search. Ticket A explores
  utility.
- **Claim scope.** The step from rectangularity to an operation is credited
  to the counting-CSP literature, and affinity to Herrmann's theorem.
- **Controls.** The non-Pappus code becomes a test of what the theorem says
  about codes.
- **Imported ideas and their local discriminators:**
  - Balance (Dyer and Richerby) predicts the counting limit. Discriminator:
    the lifted Z₃ law's counting matrix.
  - The almost affine non-Pappus code predicts a failure of composing like
    cycles. Discriminator: an explicit failing system.
  - The Taylor criterion predicts tractability when constants keep composing
    like cycles. Discriminator: no two-element projection algebra in HS.

## Novelty status

**`no-overlap-in-bounded-search`** for the characterization and the
matroid statement.

This is not a novelty or priority claim. A deeper reading of tame congruence
theory, matroid representation and the secret-sharing literature could still
find it. Contacting experts is the owner's decision.
