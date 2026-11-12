**Flaws**
- **P1 is not a prediction.** If the gadget projects exactly to parity and the fresh distinctions are disjoint per position, the network is rule 60 by composition, so MOW gives the pattern. S2 is a wiring test.
- **Depth 64 is too shallow.** It adds one band (59–62, if the 2^k−5..2^k−2 pattern holds), and no finite horizon shows non-periodicity; cite the algebra or go to 256 or more.
- **P2 is near-vacuous.** Zero hits in 2,000 only bounds the rate below about 0.15%, while the true share is probably many orders smaller. "Counts" also needs a decidable classifier for random rules (long transients give false positives).
- **S1 needs two guards.** Break fresh-permutation and complement symmetry, and report whether m*(f) has plateaued by f=5; otherwise it is not m*.

**Settled by construction**
- No knot can sit on three named distinctions, because it would kill 0000.
- f=0, 1 and 2 are infeasible. I checked this by hand: f=2 forces all four knots (x_i, y1, y2), and the two pair-sets must then each hit every triangle of K4 while being complementary on each matching, which is impossible.
- So the standalone gadget needs f ≥ 3, and SAT only has to decide f = 3..5.

**Known**
Definability (Boehler) and the counting pattern (MOW) are known. I know of no published exact m* for 4-parity; the gadget-optimality literature (Trevisan et al.) covers approximation gadgets, not exact pp-size, so check before claiming.

**New**
- The m*(f) table with UNSAT certificates.
- The threshold in distinctions per position. Helpers are per-position distinctions, so your earlier result reads "2 or fewer never counts" and this construction reads "1+h counts". The open question is whether 3 per position suffices, via helpers shared across positions or a non-parity route. S1 does not answer that, and the lower side is only as strong as the sampled census.

**Rarity**
Use the weight share (bits of the cheapest counting description, with 60/90/150/102 and mirror variants in the numerator) as the headline. Keep random-of-size as a secondary density, and add single-knot mutations of the counter to measure fragility, since blind sampling will return zero.
