# Signed counts: does the signed form of a count show a reader anything?

Epic `SIGNED-COUNT-20261126-001`, under G18, a short scoping study at the coordinator's pick before taking stock with the
owner. Question: under a count weighting, when a reader's statistics are written through the signed form of the count
(not-all-equal on k places is 1 − 2^(1−k) times the sum of even products of its spins; parity's indicator is the mean of
its characters), do terms cancel in a way that depends on a far reader's free setting, or is the signed form only a
rewriting of a nonnegative count? Computed on two small starts, with an argument; advisor consulted read-only in the
repository ([question](advisor_question.md), [answer](advisor_answer.md)); referee pending.


> **Refereed (R1, [report](referee-R1/report.md)): the count-weighting result confirmed; one Block.** "A signed sum that is not
> a count exists only in supplied readings that square it" is false: the side-swap study's reading R1 normalizes signed
> sums directly, without squaring, and gives a four-correlation score of 4 on an eight-word control where equal counting
> gives 1; absolute weighting and nonzero signed support also use cancellation. All are supplied; none comes from growth,
> so the conclusion stands with "square" replaced by "use signed sums as weights". **Narrowings:** only the ring of four
> has reader knots that share nothing; the mixture identity was checked for events on the old distinctions (every old
> word on three, four and five knots); probabilities are ratios of nonnegative counts while a signed mean uses their
> difference. **Not a block:** the term through Bob's knot stays at ±3 and falls only relative to the direct term; odd
> parity also allows a character sum of minus the number of allowed words. Logged in `docs/CORRECTIONS.md`.
## What was found ([`signed.py`](signed.py), [output](signed_out.jsonl))

Two starts with a loop (the advisor's): a ring of four three-place knots, Alice's knot and Bob's sharing no distinction,
and a ring of three. Alice reads the product of the two distinctions her knot shares; Bob's setting adds one loose
distinction to his knot or not. The count weighting counts every allowed state equally.

| Start | Count, no edit → Bob's edit | Alice's statistic | Its signed parts (positive, negative) |
|---|---|---|---|
| Ring of four | 82 → 190 | −15/41 → −33/95 | (0, −30) → (0, −66) |
| Ring of three | 26 → 62 | −3/13 → −9/31 | (3, −9) → (3, −21) |

- **The far setting does move the near reader's statistic** under this weighting (the edit changes how many states each
  old state counts for), and in the signed form it shows as the loop terms through Bob's knot contributing less (on the
  ring of three, a positive term cancelling a third, then a seventh, of the direct term).
- **The same change is a nonnegative mixture.** An edited not-all-equal knot has 2 − [its other places all equal] =
  (not-all-equal) + 1 completions, so for every event the edited count is the unedited count plus the count with Bob's
  knot deleted (its own distinctions left free): checked exactly on both starts (190 = 82 + 2 × 54; the same for Alice's
  sum).
- **So the signed form is only a rewriting.** Every reader statistic under a count weighting is a ratio of nonnegative
  counts; any signed expansion sums to the same numbers; a far dependence it shows is the counts' own, visible to the
  reader only as a change of its own statistic, which is signalling when the far setting is free, never a correlation the
  counts do not give. (Under the forbidding study's kept preparation an edit alone moves no weight, and this dependence
  is gone.) Under parity the expansion collapses further: on a nonempty allowed space a character sums to zero or to ±
  its size.

## Where a signed sum is not a count

Only in readings that sum unread distinctions with signs before squaring, which the record has and supplies: the reading
R2 of `SIDE-SIGN-20261126-001` ("every unread distinction summed before squaring") and the three-reader calculations of
`WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001`. That is the literature's sum over histories, and it is where interference
lives. The counting proof of `THREEFOLD-AMPLITUDE-20261030-001C` (Lemma 2) has no reader: its signed coefficients enter
only an identity between counts.

**Stop.** Under the count weighting nothing a reader can see comes from the signed form. The sum that could cancel must be
a reading that squares a signed sum, and the record has that only as a supplied reading.

*A correction made before anything left the thread:* the first version of `signed.py` kept the constant 1 and the
empty-subset term apart, which split each count into positive and negative parts that are not the structure's (the
advisor's catch); merged, a start without a loop has no negative part at all.
