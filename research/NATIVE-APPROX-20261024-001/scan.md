# Bounded scan: approximate counting of native networks

Date 2026-10-24. Scope: one bounded idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and
enter claims only as cited hypotheses, never as admitted evidence.

## Question

Native networks are read-twice constraint problems: every variable lies in two constraints, plus pins. Exact counting is #P-hard for
30 of the 34 knots (`NATIVE-COUNTING-20261024-001`). What is known about approximate counting of such problems?

## Query families

- Holant problems with Markov chain approximation: windability, canonical paths, sink-free orientations.
- Approximate counting dichotomies for Boolean counting problems and degree-two counting problems.
- Correlation decay and uniqueness for two-spin systems; hardness beyond uniqueness.

## Sources and relevance

| Source | Relevance |
| --- | --- |
| [McQuillan, *Approximating Holant problems by winding*, arXiv:1301.2880](https://arxiv.org/abs/1301.2880) | Definition 2 (windable), Definition 3 (strictly terraced: a zero's one-flip neighbours all take equal values). Theorem 4: strictly terraced windable functions are closed under connected circuits, include Even, Odd and not-all-equal of every size, and every finite subset has an FPRAS. Theorem 6: a function on three bits is windable exactly when F(x)F(x̄) is at most the sum of the three split products, exactly when it has a matchings circuit. |
| [Huang, Lu and Zhang, *Canonical paths for MCMC: from art to science*, arXiv:1510.04099](https://arxiv.org/abs/1510.04099) | Windability reduces to linear equations; FPRAS for b-matchings and b-edge-covers in some ranges. |
| Bubley and Dyer (1997) | FPRAS for sink-free orientations, and for formulas in which every variable occurs at most twice: the single-clause knots. |
| [Yamakami, arXiv:1109.5789](https://arxiv.org/abs/1109.5789) | Approximate counting of degree-two problems with all unary functions free (complex weights). That is much stronger than two pins, so it does not settle our case. |
| Dyer, Goldberg and Jerrum (2004, 2010) | Boolean counting problems with arbitrary reuse of variables: FPRAS for affine relations, #BIS-equivalence for implication relations, #SAT-hardness otherwise. Relevant if hubs can be simulated approximately. |
| Sly and Sun (2014); Li, Lu and Yin (2013) | Antiferromagnetic two-spin systems on regular graphs: FPTAS up to uniqueness, no FPRAS beyond it unless NP = RP. |
| [Later work on windability, arXiv:2202.02999, arXiv:2309.04735](https://arxiv.org/abs/2202.02999) | FPRAS beyond windability for the six-vertex model; windable classes with Even constraints. |

## Imported ideas and local discriminators

- **K2 is McQuillan's terraced condition.** A knot excludes no two adjacent tuples, so every neighbour of an excluded tuple is
  allowed, which is "strictly terraced".
- **Discriminator for A.** Check McQuillan's arity-3 windability inequality on all 34 knots.
- **Discriminator for the rest.** For the knots that fail, test whether hub-free gadgets can concentrate a three-leg function on 000 and
  111, a soft hub. Windable gadgets cannot: their hub ratio is at most √3.

## Overlaps and barriers

- **The FPRAS statements are classical theorems applied.** The local contribution is that K2 is the terraced hypothesis, the census,
  and the structure of the knots left open.
- **No general approximate dichotomy for Holant problems with pins** was found. The non-windable knots may be open in the
  literature.

## Effect on selection

- Ticket A: K2, windability census, FPRAS.
- A second ticket after scoping: the knots left open.

## Novelty status

- `known-overlap-found` for the algorithms.
- `no-overlap-in-bounded-search` for the census of knots and the reading of K2 as terraced.
