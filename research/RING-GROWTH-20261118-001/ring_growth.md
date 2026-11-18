# Why do rings of five knots grow faster than any power under the cheapest counts?

Epic `RING-GROWTH-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead for `TOUCH-CENSUS-20261118-001`'s
direction 1. Goals G17, G2 and G1. **Referee pending.**

**Record.**
- Pre-registration (the predictions for the other rings, frozen before they were read): [preregistration.md](preregistration.md),
  commit `90e20f510`.
- Proof: [proof.md](../../proofs/RING-GROWTH-20261118-001A/RING-GROWTH-20261118-001A-P001_ring/proof.md).
- Checks: [check.py and the ring code](../../experiments/RING-GROWTH-20261118-001B/RING-GROWTH-20261118-001B-E001_rings/);
  results: [results.json](../../artifacts/RING-GROWTH-20261118-001B/RING-GROWTH-20261118-001B-E001_rings/results.json),
  [other_rings.json](../../artifacts/RING-GROWTH-20261118-001B/RING-GROWTH-20261118-001B-E001_rings/other_rings.json).

## The answer

**In the owner's terms.**
- **The ring grows exponentially, at about 13.5% more junctions every round.** For the ring of four four-place knots and one
  five-place knot under the cheapest counts, the number of junctions made in round t is the number made five rounds earlier plus
  the number made six rounds earlier, exactly: c(t) = c(t − 5) + c(t − 6). Its rate is the real root of x⁶ = x + 1, about 1.1347
  (computed exactly through round 40 here and 57 by the referee; the count follows from the model by Pascal's rule, proved; the model
  is the growth, proved in outline and checked exactly through round 20).
- **What the ring does that a chain cannot.** The five-place knot's one spare distinction opens one more independent way to grow, on
  the cone above that knot. On a chain that cone never meets itself, and the growth stays at most two-dimensional. On a ring of five
  the cone goes round and comes back over its own start every five rounds. The cheapest rule does not merge the returning copy with
  the first: it adds it as a new independent way, and wherever several laps overlap it fills in every combination of them. So the
  number of independent ways grows by one per lap, and the junctions per round grow exponentially. A lap costs five rounds without
  the new way and six with it, which is the recurrence.
- **Folded and overlapping, in the owner's words: yes, literally.** It is one cone wound over the ring, overlapping itself once per
  lap. **A "logic based fractal": only loosely.** The counts are diagonal sums of Pascal's triangle wound around the ring, like
  Fibonacci numbers, which are the case of five five-place knots (base 1.618, the golden ratio); there is no self-similarity at every
  scale (the advisor's caution).
- **The rule for every clean ring.** With j spare distinctions on a ring of n four-place knots, the rate is the root of
  x^(n + j) = (1 + x)^j: 1.135 (n = 5, j = 1), 1.263 (j = 2), 1.385 (j = 3), the golden ratio 1.618 (j = 5), and c(t) = c(t − 7) +
  c(t − 8) for a ring of seven (the advisor's formula; checked here for n = 5, 7 and 8, and by the referee's runs for j = 2, 3 and 5).
- **Rings of other lengths differ.** A ring of four knots grows by one junction a round; a ring of six grows polynomially (per-round
  counts quadratic); both are degenerate in the joining rule (two common neighbours, or a group wrapping the ring).

| Ring (sizes in order) | Spare distinctions | Junctions per round | Rate | Evidence |
| --- | --- | --- | --- | --- |
| 4,4,4,4,4 | 0 | 5 every round (a cylinder) | 1 | proved |
| 4,4,4,4,5 | 1 | c(t) = c(t − 5) + c(t − 6) | 1.1347 | proved (model) + checked to 40 (referee 57) |
| 4,4,4,4,4,4,5 | 1 | c(t) = c(t − 7) + c(t − 8) | 1.0970 | computed, as predicted (R1) |
| 4,4,4,4,4,4,4,5 | 1 | c − 4 satisfies g(t) = g(t − 4) + g(t − 5) | 1.1673 | computed, as predicted (R2) |
| two five-place knots | 2 | root of x⁷ = (1 + x)² | 1.2628 | the referee's runs (its recurrence x⁵ = x⁴ − x² + x + 1 divides it) |
| three five-place knots | 3 | root of x⁸ = (1 + x)³ | ≈ 1.38 | the referee's runs (flat ratio 1.38) |
| five five-place knots | 5 | Fibonacci | 1.618 | the referee's runs |
| 4,4,4,5 (ring of four) | 1 | one more each round | 1 | computed |
| 4,4,4,4,4,5 (ring of six) | 1 | quadratic per round | 1 | computed |

## Predictions and verdicts

| # | Prediction (frozen before reading) | Verdict |
| --- | --- | --- |
| R1 | ring of seven: c(t) = c(t − 7) + c(t − 8) | held (Berlekamp–Massey order 8 on 31 terms) |
| R2 | ring of eight: c − 4 satisfies g(t) = g(t − 4) + g(t − 5) | held (the fitted recurrence c(t) = c(t − 1) + c(t − 4) − c(t − 6) is (x − 1)(x⁵ − x − 1)) |
| R3–R5 | two or three five-place knots, or one six-place knot: the advisor's recurrences | not scored here: the runs did not finish within twenty minutes; the TOUCH-CENSUS referee's runs give the predicted bases |

## How it is proved

The advisor gave the model; this study checked it and wrote the proof
([proof](../../proofs/RING-GROWTH-20261118-001A/RING-GROWTH-20261118-001A-P001_ring/proof.md)):
- **The model.** Unroll the ring's cylinder into coordinates v = (a, b), round a + b. A junction is a position v with a set S of the
  five-place knot's lifts lying below it; its round is a + b + |S|.
- **The count.** Summing, round by round, the number of ways to choose S gives c(t) = Σ C(m(v), t − h(v)). Pascal's rule turns that
  into the recurrence (proved).
- **The identification.** The growth is the model, by induction in four steps.
  - No surplus after the first offshoot.
  - Candidates are elements one direction apart over a common lower element.
  - Groups are the lower covers of one element. This is the predecessor's lemma in the unrolled product.
  - Groups never wrap the ring, since a group spans at most six steps and the ring takes ten.
- **What is checked.** The third step is written at the level of the predecessor's lemma, so the identification is also checked
  exactly. The grown pattern is isomorphic to the model's at rounds 8, 12, 16 and 20 (526 junctions). The parent and demand counts
  agree at every round to 22, including the advisor's two forecasts (the first six-parent junction at round 21, the first demand 7 at
  round 20).

## Known results, and what this adds

Known: Pascal's rule, linear recurrences of this kind (x⁶ = x + 1; the golden ratio for x² = x + 1), median graphs and cube
completion. What this adds: the cheapest parity growth of a ring of knots with spare distinctions is a cone wound over the ring whose
laps add independent directions, so it grows exponentially at the root of x^(n + j) = (1 + x)^j; this is the census's faster-than-power
growth explained.

## Limitations

- The identification's third step is written at the level of the earlier lemma, not line by line; it is checked exactly to round 20.
- "Rate" counts junctions per round; bond balls are not measured.
- R3–R5 were not scored by this study's own runs.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2). It corrected my first reading, which compared the growth with a tiling of the literature's
hyperbolic plane. Its counter-reading is the cylinder times a cube whose dimension grows by one per lap. It gave the (v, S) model,
the count formula, the four-step proof strategy, two forecasts (both confirmed), and the predictions for other rings (R1 and R2
confirmed). It also cautioned against calling the growth a fractal.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the ring of four four-place knots and one five-place knot | **Status:** Successful | Exponential growth with c(t) = c(t − 5) + c(t − 6), rate 1.1347, proved through the model, the model checked exactly |
| Local direction: rings of knots with spare distinctions | Continue | One formula, x^(n + j) = (1 + x)^j, fits every clean ring checked; its general proof is open |
| Broader exploration: what the cheapest growth builds | Known alternatives | Lattice-like growth from trees of knots (polynomial), wound cones from rings (exponential) |
| Long-term goal: G17 Typical and rare meeting patterns (with G2) | Capability gained | The census's rarest growth is explained: a ring makes its own extra directions, one per lap |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The "plus one" when separately born chains combine (`TOUCH-CENSUS-20261118-001#2`) | 2/3 — would make the chain rule exact | 3/3 — 145 cases, all plus one | state when two births' partners are linked, freeze "largest class + 1", test on the census and six knots → stop at a proof or a counterexample | Selected · started next in this thread |
| 2 | The general ring formula: prove x^(n + j) = (1 + x)^j for every clean ring | 2/3 — closes the ring family | 2/3 — the model generalises | write the model for j spare distinctions and n odd → stop at a proof or a ring that breaks it | Alternative · deferred |
| 3 | Bond balls on the wound cone | 1/3 — the program's own measure of dimension | 2/3 | bond distances on the ring's first rounds → stop at a growth rate or an obstruction | Alternative · deferred |

**Corrections:** none here; the census's "about 1.25 to 1.4" was corrected with its referee (`TOUCH-CENSUS-20261118-001`).

**Goals:** G17 checkpoint (capability gained: the census's exponential growth explained); no goal changed.

**Assumptions:** none new.

**Basket:** B196, `FRESH-COUNT-20261118-001#1`, B202; #1 here is `TOUCH-CENSUS-20261118-001#2`, taken next.

## Final report as sent (2026-11-18 22:41 UTC)

**Outcome:** The ring grows exponentially, about 13.5% more junctions every round. For the ring of four four-place knots and one five-place knot under the cheapest counts, the junctions made in round t are exactly those of five rounds earlier plus those of six rounds earlier: c(t) = c(t − 5) + c(t − 6), at the rate 1.1347 (the root of x⁶ = x + 1). The count is proved from the advisor's model, and the model is proved to be the growth in outline and checked exactly through round 20. Closed, referee pending.

- **What the ring does that a chain cannot.** The five-place knot's one spare distinction opens one more independent way to grow, on the cone above it. On a chain that cone never meets itself. On a ring of five it comes back over its own start every five rounds, and the cheapest rule adds the returning copy as a new independent way rather than merging it. So each lap adds a way to grow, and the overlaps fill in every combination.
- **In John's terms.** It is folded, overlapping structure, literally: one cone wound over the ring, overlapping itself once per lap. It is a "fractal" only loosely, since the counts are sums along Pascal's triangle wound around the ring. Five five-place knots give exactly the Fibonacci numbers (rate 1.618), but there is no self-similarity at every scale.
- **One formula for clean rings.** With j spare distinctions on a ring of n knots, the rate is the root of x^(n+j) = (1 + x)^j. The rings of seven and eight follow the frozen predictions; the census referee's runs match j = 2, 3 and 5. Rings of four and six are degenerate, growing linearly and polynomially.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the ring of four four-place knots and one five-place knot | **Status:** Successful | Exponential growth, c(t) = c(t − 5) + c(t − 6), rate 1.1347, proved through the model, the model checked exactly |
| Local direction: rings of knots with spare distinctions | Continue | One formula fits every clean ring checked; its general proof is open |
| Broader exploration: what the cheapest growth builds | Known alternatives | Polynomial growth from trees of knots; exponential growth from rings |
| Long-term goal: G17 Typical and rare meeting patterns (with G2) | Capability gained | The census's rarest growth is explained: a ring makes its own extra directions, one per lap |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The "plus one" when separately born chains combine (`TOUCH-CENSUS-20261118-001#2`) | 2/3 — would make the chain rule exact | 3/3 — 145 cases, all plus one | state when two births' partners are linked, freeze "largest class + 1", test on the census and six knots → stop at a proof or a counterexample | Selected · started next in this thread |
| 2 | The general ring formula x^(n + j) = (1 + x)^j | 2/3 — closes the ring family | 2/3 — the model generalises | write the model for j spare distinctions and odd n → stop at a proof or a ring that breaks it | Alternative · deferred |
| 3 | Bond balls on the wound cone | 1/3 — the program's own measure | 2/3 | bond distances on the first rounds → stop at a rate or an obstruction | Alternative · deferred |

**Corrections:** none here. The census's "about 1.25 to 1.4" was corrected with its own referee. **Goals:** G17 checkpoint (capability gained). **Assumptions:** none new. **Basket:** B196, `FRESH-COUNT-20261118-001#1`, B202. **Advisor:** Fable 5.2 gave the model, the proof strategy and the predictions. It corrected my first reading, a hyperbolic-tiling picture, and warned against calling the growth a fractal.

Referee hand-off: the decision note is `research/RING-GROWTH-20261118-001/ring_growth.md`. Check step 3 of the proof (groups in the unrolled product) most closely.
