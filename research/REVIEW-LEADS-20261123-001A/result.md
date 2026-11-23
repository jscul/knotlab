# The operator test as a yes-or-no reading of growth: result

Ticket `REVIEW-LEADS-20261123-001A` (B310; G1 with G18 and G17), 2026-11-23. Computed; scientific referee pending.
[Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[deviations](../../experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test/deviations.md)

**With the test supplied as a reading, ordinary growth keeps passing it where a rewiring with the same births fails
within a few steps; every recorded source fails it by its second step; and it says more than the number of independent
loops.** The test: the pattern of which knot holds which distinction is, in the literature's words, a planar graph
(one that can be drawn without crossings). For a closed parity part with two holders per distinction, failing is
exactly having a signed operator reading with no ordinary state (Arkhipov 2012). On an open stage it is a reading of
shape only.

## What happened

**Fresh draws** (seed 2026112301; labelled trees on four to eight knots with 0 to 3 extra meetings; 1,024 starts per
law, 12 parent steps). Under each law 744 starts stall at once, 280 are funded, and **33 of the 280 fail** within the
horizon; the other 247 pass at every stage. Sixty of the 66 failing histories first fail at step 3.

**Against the rewiring.** A rewiring keeps each step's births, their numbers of parents and of fresh distinctions,
and draws the parents with no regard to who shares with whom. In 444 funded histories the start or one of its eight
rewirings fails. In **378 of those the start passes every stage while its rewirings fail**, at a median step between 2
and 4 in most. The start's first failing step is no earlier than its rewirings' median in 442 of 444 (189 of 190 under
parity, 253 of 254 under not-all-equal). The two exceptions are one start under both laws.

**Recorded sources.** All seven fail, at step 1 or 2, under both laws:

| Source | First failing step | Knots at that stage | Kind |
| --- | ---: | ---: | --- |
| Five-founder clock | 1 | 10 | bounded (five births every step) |
| Seven-knot source | 1 | 15 | growing |
| Nine-knot drawn source | 1 | 24 | growing |
| 21-knot structure with two clocks | 2 | 57 | growing |
| Three archived explosive starts | 1 | 14, 16, 22 | growing |

The five-founder clock at step 1 contains five groups of knots each meeting the other four, the least pattern the
six-rule study found for a signed reading.

**Growth kind does not decide the test.** Stalled starts never fail (0 of 1,488). Bounded starts fail in 17 of 182
histories and growing starts in 63 of 392, so neither kind decides it.

**Loop rank does not decide it either.** No stage of loop rank 4 or less fails (2,471 stages). From rank 5 up, 104 of
the 210 ranks seen have both a passing and a failing reached stage.

**Closed parity parts.** Ninety-one were met, all in the fresh draws. Ninety pass and admit no signed reading; one
fails and admits it (8 knots, 14 distinctions). All 91 agree with the theorem.

**Benchmark.** As seen before the freeze: the cubic construction passes to depth 3 and fails from depth 4 (35 knots);
the pinwheel passes to depth 5 (3,125 knots) and the polygonal control to depth 8; the bounded-bond pattern fails from
its second window. The fitted exponent of the shape study had called the cubic construction 2.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed, with one clause false as worded | 173 of 173 recorded patterns agree (115 admit); the routine agrees with a brute-force search; the knot-side reading of change answers agrees exactly on five structures. The mutant passes everything with at most two holders per distinction, and does not pass the bounded-bond windows, where a distinction has up to six: the clause should have said so |
| P1 | Held | Benchmark replicated |
| P2 | Held | 104 of 210 loop ranks have both verdicts; least failing rank 5 |
| P3 | Held | 442 of 444 (99.5%), against a bar of three quarters |
| P4 | Held | 91 of 91 closed parity parts |

The thread rebuilt the first three stages of four recorded sources and ran the planarity routine directly, without the
study's shortcut: each passes at step 0 and fails at the step given above.

## What this is about

The reading, the populations and the rewiring are supplied. The rewiring ignores who shares with whom, so the
comparison shows that ordinary growth's parent groups keep the pattern drawable far longer than groups formed blindly;
it does not compare ordinary growth with other local laws. The lower removal bound was 0 throughout for two-holder
patterns and is not valid with more holders. The upper bound at the first failing stage was between 1 and 6 for the
fresh draws (median 1): one shared distinction usually separates a failing stage from a passing one.

**Verdict.** The reading works and costs almost nothing: it separates the benchmark constructions exactly, and it
shows two things nobody had measured. Ordinary growth mostly keeps a start drawable, and every structure in the record
that keeps producing does not stay so. Whether repeated release needs a failing pattern is the question this leaves.
