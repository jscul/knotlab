# Referee report COMMON-FOLD-R1: how common folding is among random samples

**Verdict: Confirmed, with three wording fixes (none a block).**
- **Ticket A reproduces exactly.** My rebuild agrees with the census in all 1,600 cells (200 samples × r = 1 to 8), in both outcome
  and class.
- **The tied detection does not misclassify.** No base the census calls travelling or untied is tied along a listed shift, even in a
  window twice as wide.
- **The lemma is correct.**
- **Ticket B's growths reproduce exactly**, and its numbers recompute from the rows.

The fixes are about reading the results:
- The rise of "tied" with r is mostly the bases running out of states. Tied bases have a single periodic state up to its mirror on
  small tori.
- "Travelling" is a certified subclass of base 16's fold, so the rates are lower bounds for folding.
- Ticket B's "a pair decides 82 to 85% at the last base" is RANDOM-FATES's large tie class seen from a pair. Run by run, the two
  track each other.

Referee: the background referee thread, 2026-11-12. My code:
- `ref_fold.py`, for ticket A, imports neither census;
- `ref_density.py`;
- `ref_b.py`, for ticket B, uses the referee's own generator and reader from the RANDOM-FATES referee folder.

Validation: V2. Ticket A uses Glucose 4, where the census used Minisat 2.2. I rebuilt the windows, tori, freeness and travelling
search from the pre-registration's text. I reproduced the census's random draws only so that its own bases could be re-read. The
advisor model was not consulted for this job.

## 1. Ticket A

### The census, rebuilt

- **All 1,600 cells agree.** The 171 kinds, the samples and every (sample, r) cell's outcome and class (contradiction, tied,
  travelling, travelling uncertified, none) agree with `main.json` in all 1,600 cells.
- **The base-16 control** travels: the column {(0, 0), (0, 1), (0, 2)} with pattern 000 forces 111 one step along (1, −1). It is tied
  along no listed shift.
- **The counts, the same as the note's table:**

  | r | Contradictions | Bases | Unsettled | Travelling | Tied | Either |
  | --- | --- | --- | --- | --- | --- | --- |
  | 1 | 0 | 200 | 0 | 0 | 0 | 0% |
  | 2 | 0 | 200 | 0 | 7 | 0 | 3.5% |
  | 3 | 0 | 200 | 0 | 33 | 4 | 18.5% |
  | 4 | 3 | 197 | 0 | 55 | 32 | 44.2% |
  | 5 | 20 | 179 | 1 | 53 | 68 | 67.6% |
  | 6 | 62 | 131 | 7 | 28 | 78 | 80.9% |
  | 7 | 97 | 98 | 5 | 9 | 73 | 83.7% |
  | 8 | 122 | 75 | 3 | 3 | 62 | 86.7% |

### Soundness of the certificates (the owner's point)

Every positive reading is sound for the infinite base:
- **"Contradiction".** A window with no state means the infinite base has none.
- **"Base".** A torus state is a periodic state of the infinite base.
- **"Tied".** If the window forces x_t given x_0, so does every infinite state, since its restriction to the window satisfies the
  window's constraints. Translation then carries the tie to every distinction.
- **"Travels".** The window's forcing holds in the infinite base for the same reason. The torus certificates show that p with σ(p)
  occurs, and that every pattern on A occurs (A is free).

**The one way a class could be wrong** is a tie the 15 × 19 window fails to force. A tied base would then look travelling or untied.
I rechecked the ten shifts in a window of 35 × 39 for every base not classed tied, at every r. None became tied. The classification
is therefore also stable under a much larger window. "Tied" remains a lower bound in principle, since no finite window decides every
tie.

### The lemma: correct

- **The pattern travels.** Shift-invariance and the mirror symmetry of not-all-equal carry "p forces σ(p) on A + t" to "p forces
  σ^k(p) on A + kt".
- **The bonds stay small.** Given p, the value at a + kt is forced, so A ∪ {a + kt} is constrained. A is free, so every constrained
  subset holds a + kt. A single distinction is never constrained, so a minimal one, a bond, also holds a member of A. It has at most
  |A| + 1 distinctions.
- **Distances grow.** Steps apart grow linearly in k, so bond distance stays bounded along t.
- **The tie case is the same argument with |A| = 1.**

### The coordinator's questions

**1. Is the rise of "tied" settled by definition? How many high-r samples have a state, and are the rates conditioned on that?**
- **The rates are conditioned on having a state.** They are "among bases": 131, 98 and 75 bases at r = 6, 7 and 8, besides 7, 5 and 3
  unsettled.
- **It is not settled by definition, but it is mostly the collapse of states.** I counted states on the 6 × 6 and 8 × 8 tori. At
  every r from 3 to 8, the tied bases have a median of 2 states on the 6 × 6 torus and 2 to 6 on the 8 × 8 torus: one state and its
  mirror. Every other class loses states as r grows. The untied bases with nothing found fall from a median of 62 states on the 8 × 8
  torus at r = 3 to 0 at r = 8, and 75% of them carry no 8 × 8 state at r = 8.
- **So** "near contradiction, ties take over" is right. It is the expected rigidity of bases that keep almost no freedom, as near the
  end in RANDOM-FATES. A tie is the strongest form that freedom loss takes. The note's Reading ("the bases left near the edge are
  rigid along a shift") says so in effect. It should add that these bases have essentially one periodic state up to its mirror.

**2. Does the weighting support "how common folding is"? Is "travelling" the base-16 fold, or something weaker?**
- **The weighting.** The rates hold under W(r) only: uniform r-subsets of the 171 kinds in a 3 × 5 box, counted per presentation. The
  note says so, in conclusion 1 and the Reading's G17 line. "Typical, once knots overlap enough" in the Answer should keep "under this
  weighting" next to it, as the Answer's second sentence does.
- **Travelling against the fold.** A certified travelling pattern with |A| = 3 gives bonds of at most four at every number of steps
  along t, with every pair free. That is base 16's fold, which the control shows. So travelling is a sufficient, certified form of
  the fold. The converse, that every unlengthened shift comes from a travelling pattern of at most 4 cells in a 2 × 3 box, is not
  shown. The travelling rates are lower bounds for "folding", not its frequency. Conclusion 4 calls them "lower bounds within the
  searched family", which fits. The Answer's "base 16's own kind of influence … is common in the middle (about 30%)" should say "at
  least".

## 2. Ticket B

### The rerun and its deviation

- **The rows are what the frozen code and seeds give.** All 40 U(100) and U(200) growths regenerate from random.Random(50000 + run)
  with my generator to the same last base.
- **The deviation changes no frozen verdict.** It added a 30-minute cap per run and left the code and seeds unchanged. That cap
  dropped all 20 U(400) runs. So B2 to B4 are undecided at 400, and B3 held only at 100 and 200, as the note says.
- **The frozen summary's bug touched nothing kept.** The frozen summary would have tried to add up the per-distance profile, a
  dictionary, and stopped. The rerun's summary leaves the profile out. The note's profile figures come from the rows, and I recompute
  them: 90.9% and 87.6% at one step, 72.4% and 75.0% at three. They are right.

### The numbers, recomputed from the rows

| Item | U(100) | U(200) |
| --- | --- | --- |
| Pair forced at half / three quarters | 1.05% / 1.06% | 0.50% / 0.51% |
| At the last base | 85.1% | 81.8% |
| Beyond the members' ties | 4.1% | 6.1% |
| By propagation | 0.41% | 0.20% |
| Largest pair forced beyond ties | 91% | 90% |

B4 fails at 200, as reported. The tree control forces only the third distinction of the pair's own knot.

### Q3. Is 82 to 85% the same fact as RANDOM-FATES's large tie class?

Mostly, yes.
- **The test.** On 12 regenerated last bases (runs 0 to 5 at each size), I computed the largest tie class and, for 20 pairs of my own
  draw, the forced fraction with the frozen rule.
- **Means.** The mean forced fraction is 85.9% and 81.6%, against the census's 85.1% and 81.8%.
- **Run by run, the pair's share tracks the largest class's share.** For example, 0.92 against 0.94, 0.80 against 0.77 and 0.75
  against 0.735. Nearly every pair (227 of 240) has a member in the largest class.
- **The exception.** In the one base whose largest class holds only 43.5%, pairs decide 62%, and 15% of the base lies beyond their
  ties.

So "a pair decides about four fifths of the base at the last base" is the large tie class of RANDOM-FATES's final jump seen from a
pair, plus a few per cent. The note's Reading ("as RANDOM-FATES found for ties alone") says this; conclusion 6 should say it too.

## 3. Fixes for the thread (all Not a block)

1. **Conclusion 3 and the Reading.** Add that tied bases at every r have a median of 2 periodic states (one and its mirror) on 6 × 6
   and 8 × 8 tori. The rise of ties tracks the collapse of states as r grows: a density effect, not a separate mechanism.
2. **The Answer.** "Base 16's own kind … is common in the middle (about 30%)" should say "at least about 30%": travelling is a
   certified subclass of the fold. Keep "under this weighting" with "typical".
3. **Conclusion 6.** Say that the 82 to 85% is the members' share of the large tie class of the last base, the final jump of
   RANDOM-FATES seen from a pair, with 4 to 6% beyond ties.

## Files

`brief.md`; `ref_fold.py` → `result_fold.jsonl` (all 1,600 cells, with the wide-window ties); `ref_density.py` →
`result_density.json`; `ref_b.py` → `result_b.json`.
