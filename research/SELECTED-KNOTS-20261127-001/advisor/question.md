Advisor consultation for `SELECTED-KNOTS-20261127-001` (directory research/SELECTED-KNOTS-20261127-001; nothing frozen).
Read docs/ADVISOR_HIVEMIND.md first (your THIRD-LAYER entry and its referee's judgement), then
research/THIRD-LAYER-20261126-001/referee-R1/report.md and argument.md, research/THIRD-LAYER-20261126-001/decision.md,
and research/SELECTED-KNOTS-20261127-001/overlap.py with overlap.json (my reproduction of the referee's shared-fact
witness: three rings of four, five disjoint carriers R, S, T, P, Q, two equations R+S+T and P+Q+R, all five held by no
part at scale 12 at rounds 5 and 6). Answer with counterexamples, constructions and checks; mark each claim's status;
add one dated entry to the hivemind; touch nothing else.

What stands (refereed): under ordinary parity growth the families' facts l_A obey exactly one relation; every nonzero
sum of them has least flip growing by exactly two a round; every start parity outside their span is flipped by a change
of at most max(4, number of start knots); so at a scale k above that bound and rounds past about k/2 the class facts
are exactly span(l_A) modulo laws. Your "one second-layer knot per connected start" was overturned because sums of
family facts can be carried separately: the class-fact space V (dimension m - 1) has many dependent triples with
disjoint carriers.

The coordinator's question: which second-layer knots does growth ITSELF select? State it so it can be tested without a
reading of ours choosing them; say whether that set is determined by the start and the law alone; name the reading and
the scale as scaffolds and test under another choice of each; then whether the selected knots meet as first-layer
knots do, and whether a third-layer whole-held fact exists without a chosen reading.

My first thoughts, to attack:
- At large scale V is a vector space; as functions every dependent triple is "a sum", so a second-layer knot's content
  is only in its carriers. The stage itself supplies carriers: for a fact f in V, its carriers are the supports of its
  representatives (f plus a sum of laws), and the natural growth-made ones are the minimal supports (least size) or
  the supports a lineage produces (a family's newest loose distinctions, Lemma 3 of the referee's argument).
- Candidate native object: the set F_t of (fact, carrier) pairs where the carrier is a minimal support of the fact and
  is held by no part at scale k; second-layer knots are the circuits (minimal dependent sets, size >= 3) of the linear
  matroid on F_t whose carriers can be chosen pairwise disjoint. This is determined by the stage once k and "minimal"
  are fixed. Is it choice-free enough? Is "minimal support" a reading of ours?
- Meeting: two such knots meet when they share a fact; a layer-2 pattern is then the hypergraph of these circuits.
  Layer-3 facts: parities on the layer-2 values (the code C2) even on C2's own shortest changes, read by no single
  second-layer knot. The referee found C2's own shortest changes span C2 on the five-fact witness (no layer-3 fact),
  and built a third-layer knot on thirteen five-knot rings only with 18 chosen second-layer knots.
Questions.
1. Give the cleanest testable statement of "the second-layer knots growth selects", and say exactly which choices
   remain (scale, minimality, reading of small change). If every statement needs a choice, say which choice is least
   arbitrary and why.
2. On the three-rings-of-four witness and on three or four rings of five, what does your statement select at rounds 4
   to 6? Predict the layer-2 pattern (which knots, which shared facts) and whether C2 has a fact its own small changes
   keep.
3. Is the selected set determined by the start and the law alone (does it depend on the round, once past k/2)? Where
   could it depend on representatives or ties?
4. Smallest start where your statement predicts a third-layer fact without a chosen reading, or the reason none exists
   (for example: if the selected knots are all circuits of a matroid whose small changes span C2).
