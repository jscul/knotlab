# Advisor question 1 (SCALE-SHARE-20261119-001, before the freeze)

Analysis please; I will check it. Background: CLUSTER-ALL's cluster rule predicts the cheapest parity growth exactly on every
in-scope touch-census arrangement through five knots, where knots have 3 to 5 places sharing distinctions with any multiplicity,
connected, and round 1 gives each knot its groups. It breaks at six knots where two first-round sunflowers share two knots,
making a merged block with a missing pair; there one cluster carries two junctions. By the rule a start either:
- stalls (round-1 demand > open);
- closes;
- grows with dimension = the largest number of endless chains feeding one piece;
- or holds a ring and grows exponentially.

Now I classify large starts by the rule alone. The sampler is a Metropolis chain uniform over labelled descriptions (sizes 3–5
and multiplicities; one multiplicity or one size moved by one; feasible states only), with importance weights |Aut|/n! to distinct
arrangements.

Pilot, labelled shares (my n = 5 sample reproduces the exact census within noise):

| n | samples | stall | closes | dim 1 | dim 2 | dim 3 | out of scope | exponential |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 200 | 0.445 | 0.125 | 0.08 | 0.345 | 0.005 | 0 | 0 |
| 6 | 200 | 0.505 | 0.095 | 0.07 | 0.32 | 0.005 | 0.005 | 0 |
| 8 | 60 | 0.55 | 0.05 | 0.067 | 0.333 | 0 | 0 | 0 |
| 10 | 60 | 0.717 | 0.033 | 0.05 | 0.2 | 0 | 0 | 0 |
| 12 | 60 | 0.883 | 0 | 0.033 | 0.083 | 0 | 0 | 0 |
| 16 | 60 | 0.883 | 0.017 | 0 | 0.1 | 0 | 0 | 0 |

No break shape seen yet.

**Plan.** n = 5, 6, 7, 8, 10, 12, 16, 20; 8 chains × 1,000 samples each; both weightings. Growth spot checks: 200 samples per n
for n = 6, 7, 8, compared with the rule for 15 rounds.

## Questions

1. Why should stalls take over as n grows? My reading: more neighbours raise round-1 demand, places are capped at 5, and the
   uniform measure over labelled multigraphs favours many shared distinctions. Can you predict the stall share's limit, or its
   rate (e.g. the probability that no knot is over-demanded decays like q^n)?
2. Among growing starts, will two dimensions stay the most common? Will rings (exponential) become common, or stay rare? A ring
   needs a cycle of five or more knots in the candidate map with something extra, but a long uniform multigraph has many cycles,
   and an over-demanded knot anywhere stalls the whole start.
3. The break shape (two sunflowers sharing two knots, with knots of their own on both sides): how often should it occur as n
   grows, given that stalls remove much of the space?
4. Is the uniform-labelled measure the right one to freeze? The census used it and the distinct one; any trap at large n, such as
   the chain mixing badly, or importance weights degenerating because almost all descriptions have trivial automorphisms?
5. Sharp predictions to freeze, and a falsifier.
