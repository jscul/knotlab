# Referee hand-off

Study `LOOK-ALIKE-20261126-001`, closed 26 November 2026 by the thread: a check, not registered; computed; referee
pending. Read [the decision](decision.md) and [the note](README.md): the design and six expectations were committed
before any start was grown (947486d0f4); phase 1 was exploratory; the criterion was frozen in an addendum
(bd7c6b57af) before phase 2 ran.

## Claims, each computed

1. **Ordinary growth.** Every census start of one to five knots (`cpcensus.starts`, each once up to its symmetries;
   3,380) grown under the ordinary count, not-all-equal, nothing taken, with a round that has a short knot recorded as a
   stall and nothing kept ([`alike.py`](alike.py)); kinds from the counts (rules in the note).
2. **Settling.** For every start of a fixed dimension, its view (each kind of birth counted per round, in sig0 and sig1)
   settles: from a round K the polynomial of degree D − 1 through rounds K − D + 1..K gives every later round read.
   K ≤ 12 (sig0) and ≤ 14 (sig1) for all but seven five-knot starts, which settle at 14 and 16 after a binomial burst of
   a block of ten ([`phase2.py`](phase2.py), [`phase2.json`](phase2.json), [`phase1_rule.json`](phase1_rule.json)).
3. **The pair rule.** For two starts of one dimension, the first round from which they agree up to the count (nested
   multisets in every later round read), computed from counts through round 14 and the fitted polynomials after, equals
   the observed one: in all 9,636 pairs of phase 1 and all 592,495 of phase 2 in sig0; in sig1 all but 5,614, every one of
   which includes one of the seven late starts.
4. **The control.** 116 pairs with the same Lemma R data are identical in sig0 from round 1 and, the 76 that grow, in
   sig1 from round 2 ([`control_r.py`](control_r.py)).
5. **Late views.** 16 distinct late sig0 views among 1,003 five-knot starts of dimension two (549 like a lone knot,
   176 like two touching knots); 29 among 409 of dimension one.

## Points to press

- Is the stall handled as the ordinary law says (no knot short after the start under the ordinary count; any short
  knot in round 1 stops the growth)? Check against REDUCE-BLOCKS-20261119-001's Lemma R and the frozen law.
- The kind thresholds and the settling definition: could a start be misclassified (a burst still under way at round 24,
  a rate read as a dimension)? The 11 unread starts: what are they?
- Claim 3 nearly follows from claim 2 wherever both views settle by round 14: say whether the pair rule adds anything.
- Regrow a sample of starts with code of your own (lesson 8.1's law) and recount a sample of pairs.
- The reading in the note that the largest block bounds the settling round: test it if cheap.
