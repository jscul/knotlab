# For the advisor (26 November 2026): is the signed form of a count only a rewriting?

Read `docs/ADVISOR_HIVEMIND.md` first; then `research/SIGNED-COUNT-20261126-001/signed.py` and `signed_out.jsonl`, and for
context `research/THREEFOLD-AMPLITUDE-20261030-001C` (the counting proof whose Lemma 2 sums signed coefficients) and
`research/SETTING-AS-REREAD-20261123-001/decision.md` (the 20/9 under the weighting that counts finished configurations
equally). Counterexamples and checks, not a verdict.

The coordinator's question: under the count weighting, when a reader's statistics are written through the signed form
(not-all-equal on k places is 1 minus 2^(1-k) times the sum of even products of its spins; parity's indicator is the mean
of its characters), do terms cancel in a way that depends on a far reader's free setting, or is the signed form only a
rewriting of a nonnegative count with nothing a reader could see?

My argument (unverified): (1) every reader statistic under a count weighting is a ratio of nonnegative counts, P(event) =
N(event) / N; any signed expansion of N(event) sums to the same number, so a reader sees only the total; (2) the terms do
depend on the settings (in `signed_out.jsonl` the count 126 = 288 − 162 at settings 00 becomes 294 = 552 − 258 and
686 = 1072 − 386), but that dependence is the count's own, carried through linear arithmetic, and it cannot produce a
table that the nonnegative counts do not already give; (3) interference would need a reader's probability to be a
nonlinear function of a signed sum over alternatives the reader cannot tell apart (a square of a sum, as in the
literature's sum over histories), and no recorded reading squares a sum; (4) under parity the signed form collapses: a
character sum over the allowed space is 0 or its size, so no partial cancellation exists at all.

1. A counterexample: a reading in the record whose value is not a linear function of nonnegative counts, or a place
   where the signed coefficients (as in Lemma 2) enter a reader's statistic other than through their total.
2. Is (4) right as stated for every reading (affine readings, the complete record)?
3. Is there a cheap frozen test that would distinguish the two readings, or is the argument enough?
