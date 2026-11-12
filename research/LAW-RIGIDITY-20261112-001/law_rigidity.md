# What does the drawing's work on a base with no drawing

Epic `LAW-RIGIDITY-20261112-001` (sub-goal B158, G15 with G16; program learning), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in [preregistration.md](preregistration.md): stage 1 frozen in commit `94c87c2a7`, stage 2 in its addendum, commit
`d2bd7c40a`, each before its runs. Proof families: `proofs/LAW-RIGIDITY-20261112-001A/` (stage 1), `...001B/` (stage 2).

## The answer

**The drawing did two separable jobs, and on a base no drawing fits, a rule read from the knot pattern can do the first while a supplied
rule does the second: then the learner learns and holds the count in every run.**

- **Stage 1, one copy of (2, 0, 4) (computed, frozen).** Letting the learner rest only at the 4 laws the faces allow, with no face grade,
  it found the count in 10 of 10 runs, at about the speed it had with faces, but held it in only 4 of 10: its repairs re-signed knots and
  left the rest set. With a repair that flips distinctions only (A68, a rule we supply), all 30 writes held. The rest set finds; rigidity
  keeps; the grade itself was not needed.
- **Stage 2, a native rest set (exact, then computed).** A law's sum around each shortest cyclic sequence of knots and distinctions (here
  two knots sharing two distinctions) does not change under flipping a distinction or complementing a knot, so a rule on those sums reads
  nothing but the knot pattern and the law. On the 6-distinction base U, which no drawing fits, "every shortest sum 0" leaves the learner
  2 laws to rest at, the plain law and the counting law; with the rigid repair the learner learned and held the count in 10 of 10 runs,
  all 30 writes, at a median of 4,400 steps. That is the first map learned and held on a base no drawing fits.
- **The rule's value is not universal (exact).** On one copy, "every shortest sum 0" leaves no counting law to rest at, because every
  counting law there has sum 1 on each shortest sequence; "every shortest sum 1" leaves 32 laws, 4 counting, and the learner learned and
  held the count there in 10 of 10 runs; but on U "every shortest sum 1" leaves no law at all. No single value for every shortest sequence
  serves both bases. The drawing's faces on one copy are sequences of three knots, not the shortest, and the drawing chooses which of them
  to fix.

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| Learned rules need a cost to change or a slower clock to stay (stability against plasticity) | known: Grossberg 1980; McCloskey and Cohen 1989; Kirkpatrick and others 2017; Benna and Fusi 2016; in learning materials, Stern and others 2021, Keim and others 2019 |
| A law is a Z2 gauge field on the places where distinctions sit in knots; its sums around cyclic sequences are its gauge-invariant content; a drawing's faces play the plaquettes' part (Wegner 1971) | reading in the literature's terms; the analogy is ours |
| On one copy, resting where the faces allow finds the count 10 of 10 with no grade, holds 4 of 10; with a repair that flips distinctions only, 30 of 30 | computed, frozen |
| Rest sets of "every shortest sum 0" and "every shortest sum 1": one copy 32 (0 counting) and 32 (4); U 2 (1) and 0 | exhaustive |
| No rule of one value for every shortest sequence leaves a counting law at rest on both bases | exhaustive (the line above) |
| On U, with "every shortest sum 0" and the rigid repair, 30 of 30 writes learned and held; on one copy with "every shortest sum 1", 30 of 30 | computed, frozen |

## Against the pre-registration

- I predicted stage 1 would show neither job alone enough. Wrong: the rest set alone finds the count; holding needs rigidity.
- Stage 2's mark for one rule on both bases failed by definition, as the addendum said before any run; the two runs it left open passed,
  as predicted.
- A count was wrong in two records written after stage 1: A68 and the addendum first said R held 4 of 10 as "5 of 10". Corrected (Not a
  block, `docs/CORRECTIONS.md`).

## What it changes

- **The memory has two parts, and both can be separated from the drawing.** Where the learner may rest decides whether it finds a map;
  what makes a law cost something to change decides whether it keeps it. On U a rule of the knot pattern supplied the first; the second
  is still supplied by us (A68).
- **The rest set has to be chosen, and the knot pattern alone did not choose it the same way on both bases.** That is where the drawing
  still does work no rule here replaces: it says which cyclic sequences to fix.

## Assumptions

A68 added (a repair flips distinctions only; a rule we supply). Relied on: A20, A21, A46, A47, A49, A50, A52, A58, A66 (Confirmed).

## Corrections

One, Not a block: A68's "Why" and the addendum said R held "5 of 10"; it held 4 of 10.

## In the owner's words

Take the drawing away and the learner needs two things back: a short list of rules it may settle on, and a reason not to rewrite a rule
once it has one. On the small pattern no drawing fits, asking the rule's signs to add up to nothing around every smallest round of knots
gives it the list, and it learns to count every time, though for now we hand it the second thing. The catch: the same asking makes
counting impossible on the drawn copy, where the count needs those rounds to add up to one.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what does the drawing's work on a base with no drawing (B158) | **Status:** Partially successful | the two jobs separated; a native rest set lets the learner learn and hold on U, 30 of 30; no one rule serves both bases; rigidity still supplied |
| Local direction: native rest sets with supplied rigidity | Continue | it works on U; the open parts are native rigidity and a rule that serves every base |
| Broader exploration: learning program | Known alternatives | a native grade for rigidity (B160), which cyclic sequences to fix (B161), the tie (B157), the count of seven (B154), the two-histories test (B159) |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Capability gained | the first learned and held map on a base that no drawing fits |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A native grade for rigidity (B160; challenges A68) | 3/3 — Major | 3/3 — Ready | replace the flat cost of a wrong shortest sum by a count of them (2 per wrong sum), with the free repair, on U and on one copy → learned and held without A68, or a repair that still drifts | Selected · awaiting go-ahead |
| 2 | Which cyclic sequences to fix (B161) | 2/3 — Substantial | 2/3 — Testable | on one copy and on U, every uniform rule over sequences of up to three knots (by length and value), exact: which leave a counting law at rest on both → a rule that serves both, or a proof that the knot pattern does not choose | Alternative · deferred |
| 3 | A tie in place of the shared distinction (B157) | 2/3 — Substantial | 3/3 — Ready | as recorded | Alternative · deferred |
| 4 | The count of seven: where the time goes (B154) | 2/3 — Substantial | 3/3 — Ready | as recorded | Alternative · deferred |
| 5 | A learner that must end differently after two histories (B159) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1:** payoff 3/3, because rigidity is the part still supplied, and a native grade would make the learned law on U a memory of the base
  alone; concreteness 3/3, a one-term change to stage 2's engine, and stage 2's runs took under five minutes. The main uncertainty is
  whether a count of wrong sums makes a sign change cost more than a flip often enough near rest. Resource bound: stage 2's caps.
- **#2:** payoff 2/3, it asks whether the knot pattern can choose its own rest set on every base; concreteness 2/3, the census is exact
  and small, but "uniform rule" over longer sequences needs care to define.
- **#3, #4, #5:** as recorded.

**Corrections:** one, Not a block (R's held count written as 5 of 10; it is 4).
**Goals:** G15 checkpoint (capability gained, with G16); sub-goal B158 taken; sub-goal B160 and backlog B161 added.
**Assumptions:** A68 added (a repair flips distinctions only, supplied); B160 challenges it.
**Basket:** B160 (selected, awaiting a go-ahead), B161, B157, B154, B159, B155, B156, B150, B151, B130.
