# Polynomial calculus size of Tseitin formulas on grids

Epic `PC-SIZE-GRID-20261020-001`, closed 2026-10-20.

## What was found

Over any field of characteristic other than 2:
- **PC and PCR.** Every refutation of the Tseitin formula of the a × b grid
  in polynomial calculus over the 0/1 basis, or with twin variables (PCR),
  has size 2^{Ω(min(a,b))}. Refutations of size 2^{O(min(a,b))}·poly(ab)
  exist, so the size is 2^{Θ(min(a,b))}
  ([proof](../../proofs/PC-SIZE-GRID-20261020-001B/PC-SIZE-GRID-20261020-001B-P001_grid_size/proof.md)).
- **Resolution.** Since PCR simulates resolution, resolution also needs size
  2^{Ω(min(a,b))} on grids. That is the tight exponent; the known
  bounded-depth Frege bounds give exp(n/polylog n).

The size–degree relation cannot give this. Degree is Θ(min(a,b)) while the
number of variables is about 2ab.

## Why it works

- **Restriction.** A random restriction sets the edges of faces that lie far
  apart (L∞-distance at least 3, no corner faces).
- **The key lemma, by planar duality.** Such a restriction keeps at least a
  fifth of every cut. A dual cycle can cross at most four deleted edges in a
  row, and only by passing through the outer face. The factor 5 is sharp.
- **Degree survives.** So the restricted formula is a Tseitin formula on a
  connected grid with holes. Its balanced cuts give an explicit tangle, and
  the tangle lemma of `PC-DEGREE-20261020-001` bounds its degree below by
  about min(a,b)/30.
- **Size.** Each literal dies with constant probability, independently at
  bounded range. A refutation smaller than 2^{Ω(min(a,b))} would therefore
  shrink to that degree.

## What is known around it

- **Beck, Nordström and Tang (2013)** proved PCR lower bounds for the
  XOR-substituted grid, where every edge is doubled. They noted that random
  restrictions break plain bounded-degree grids. Separated faces avoid that.
- **General resolution.** Whether Tseitin on every bounded-degree graph
  needs size 2^{Ω(tw)} is open (Itsykson, Riazanov and Smirnov 2022). The best
  general bounds are 2^{tw²/n} and 2^{tw^{Ω(1)}}.

## Open

- **All bounded-degree graphs**, the real barrier. The argument needs short
  faces.
- **Planar graphs with short faces**, beyond grids. Take 3-connected planar
  graphs of bounded degree whose inner faces have bounded length. There the
  cut lemma should hold as is, since faces meet in at most one edge. A tangle
  of order cvw(G) from the Robertson–Seymour duality would transfer to the
  restricted graph at a fifth of its order. That would give 2^{Θ(tw)} for
  resolution, PC and PCR on that class.

## Recommendation

**Continue**, rated by barrier potential.

| | A. 3-connected planar graphs with short faces | B. All bounded-degree graphs | C. Return to the foundations (question 9) |
| --- | --- | --- | --- |
| Interest | 2/3. Settles 2^{Θ(tw)} for resolution, PC and PCR on a natural class. The open problem is still open in general. | 2/3 if achievable; the actual barrier. No approach yet: graphs without short cycles defeat face restrictions. | 1/3 |
| Execution | One epic: generalize Lemmas 1 and 4, transfer the tangle, check on random triangulations and quadrangulations. Stop if a step needs more than bounded face length. | A bounded idea search first; stop if no restriction family keeps a large tangle without short cycles. | A fresh epic. |

Execution is the owner's decision.
