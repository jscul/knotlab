# The advisor's answer (26 November 2026), on the scoping of weights that cancel

**Verdict:** write the note "none exists in the recorded laws", and attach the test as a cheap frozen confirmation, not as a candidate. I reasoned from your draft only; I did not open the records or `forbid.py` beyond its function list.

## 1. The table

- **Row 3 is misjudged in one respect: the reading is not stated.** The signed law is used two ways.
  - As an amplitude (squared at the read), value reads erase every phase and you get the unsigned table, trivially classical.
  - As a signed weight summed directly, it is a new reading that no record adopts. Your candidate uses this one without saying so, and it needs its own scaffold entry.
- **Row 4 holds only on words of fixed parity.** (−1)^C(k,2) = ∏ over pairs (−1)^(x_i x_j) is a pairwise sign. It equals a product of per-reader phases times a function of k's parity, so "absorbed into the reader" is true only where parity is fixed. Also, "cannot change any table of value reads" is true for amplitudes and false for a directly summed weight.
- **Row 5 is right.** It is the only row whose sign is truly pairwise without a parity condition, and it is supplied.
- **Missing: orientation signs of matching counts** (the literature's Pfaffian or Kasteleyn signs), if the native scan's matchgate identity is recorded as I recall. They are signed weights on whole configurations, exist structurally, and the orientation is ours. This is the same mechanism as row 5.
- **Missing: the linear program's own signed solutions.** If you drop nonnegativity in `lp.py`, what is the smallest negative mass that gives excess against a free sender? That is a number, not a yes or no.
- **Missing from the framing: signed weights give excess for free.** Every table in which far settings change nothing is the marginals of some signed joint weighting (Abramsky and Brandenburger 2011), including the literature's PR box. So the only question is whether a recorded sign does it, never whether signs can.

## 2. The candidate

- **Your parity argument is right for ±1 signs.** On a parity structure the weight is a character on an affine set. Either it is constant, giving the unsigned classical table, or it sums to zero, giving no table.
- **It is incomplete for the i phases and for pairwise signs.** Each context table is then zero or uniform on an affine set of outcomes, and PR is exactly that, so this step alone excludes nothing.
- **The missing step is the cross terms.** Summing the unread distinctions kills any table unless the cross terms between the two sides vanish, and what remains factorizes. I checked this only for real quadratic signs on four reads with full support. It is a sketch, not a proof for affine supports or for the i phases.
- **So the test is not pointless for parity, but it is weak either way.**
  - A miss is what the argument predicts.
  - A hit would be about the supplied sign and the new reading, not about growth. That is the same standing as the GHZ result.
  - A hit with normalizers that differ by context is local rejection in signed form.
- **Do not switch to phase-sensitive reads.** That reproduces a known result with a supplied reading.

## 3. The frozen test

Use `forbid.py`'s census starts, edits, readers and one round, unchanged. Use exact arithmetic over Gaussian integers.

**Variants**

| Variant | Weight on each allowed state |
|---|---|
| V1 | (−1)^(shared distinctions holding 1) |
| V2 | V1 times i^(loose distinctions holding 1) |
| V3 | V1 times the row 4 sign |

**Gates, per placement, counted in order**

| Gate | Condition |
|---|---|
| G0 | All four normalizers are nonzero |
| G1 | Every entry is real and nonnegative |
| G2 | The four normalizers are equal (a failure is recorded as signed local rejection, not a hit) |
| G3 | Every complete record is unchanged by far settings |
| G4 | CHSH is above 2 |

A hit passes G0 to G4.

**Controls**

- The unsigned weight reproduces the census counts exactly.
- A hand-built signed PR weighting passes G0 to G4, to show the counter can see a hit.

**Prediction:** zero hits in all three variants, at about 85% confidence.

- Parity structures fail G0 or reduce to the unsigned table.
- Not-all-equal structures mostly fail G1, and those that pass are classical or fail G2.

Any hit is reported as "the supplied sign under a supplied reading", with the sign law, the direct-sum reading and the reader set each named as a scaffold.
