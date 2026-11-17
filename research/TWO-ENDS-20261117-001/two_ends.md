# Is bounded reach always held by bounded pieces at the two ends?

Epic `TWO-ENDS-20261117-001`. It takes direction #1 of `CARRIER-20261117-001` at the coordinator's go-ahead (2026-11-17 21:19
UTC), within John's request of 16:52 UTC to reopen the line. It serves G17, with G1, and ran on 2026-11-17. Proof note:
[proof.md](../../proofs/TWO-ENDS-20261117-001A/TWO-ENDS-20261117-001A-P001_pumping/proof.md). Code by the thread. The canonical K1–K3
test is unchanged. **Refereed** (TWO-ENDS-R1, [report](referee-R1/report.md), commit 9ebb6077c): **confirmed with fixes**, no Block.
Lemma S, Theorems D and G and Lemma R hold as written; Theorem N's step 3 is repaired for clusters; the summaries now say "a
three-end form of C\*" and "decidable in principle (proof sketch)"; the carried mode has two parts (below, "Referee"). *Counts narrowed on 2026-11-17, before this study's referee, after CARRIER's (CARRIER-R1):
several descriptions give the same pattern, so counts now give distinct patterns too. The 13 mutants are 5 patterns, −73 and −79
are one, and the census's 786 descriptions are 181 patterns.*

## The question

CARRIER found that bonds inside slightly larger pieces than two orbits keep the top bound where two-orbit bonds fail, and proposed,
with the advisor, Conjecture C*: the reach is bounded exactly when a bond inside bounded pieces at the two ends (the top orbit and
the lower orbit) survives at every distance. Its "if" was proved (Theorem K*). This epic asks for the "only if", by pumping, and
whether the 13 mutants of 8db5da810c00 (5 distinct patterns), which pass every carrier found, grow.

## Answer

**A three-end form of C\* holds; with two ends it stays open. On each depth tier, nothing grows slowly.**
- **Theorem N (proved; step 3 repaired for clusters after the referee).** Any bond of at most c members meeting levels k and k + s can be moved, keeping its size and those two
  levels, until every member lies within K(c) blocks of the top, of the lower member's orbit, or of the bottom band, the last few
  levels of the pattern.
  - The proof pumps the finite set of states of downward paths through blocks.
  - The bottom band is a third end. A member there cannot move, because the pattern reads the bottom levels differently, and nothing
    found removes it.
  - So a three-end form of C\* holds: bounded pieces near the top, near the lower member and near the bottom band. C\* with two
    ends, as first stated, is not shown.
- **Theorem D (proved).** On each depth tier and each residue of s, the reach is either eventually constant or grows at least
  linearly as s grows. Nothing grows between bounded and linear there, as `READ-RULE-20261114-001` found for nested families.
  Boundedness over every depth also involves the depth growing at fixed s, which Lemma R treats.
- **Decidable in principle (proof sketch).** For each c, whether the reach stays at most c at every depth reduces to finitely many
  cases; the reduction is outlined, not carried out, and no feasible constants are claimed. Boundedness would then be
  semi-decidable.
- **Theorem G (proved; the advisor's test).** If every long enough composite of steps through blocks is a product, the reach grows
  linearly. This is a finite computation. On the census it holds exactly for the 740 descriptions that forget (139 distinct
  patterns), which reproves their growth, and for none of the 46 that do not (42 patterns).

**The 13 remain open.** *(Superseded by `MODE-BOND-20261117-001`: they grow linearly, and the link below never meets the top.)* The
test fails for them, and the computation shows exactly why:
- **One carried link, in two parts.** One orbit type has both children of its own type, and along it one composite is not a
  product (narrowed after the referee, who checked it by SAT at depth 11):
  - **the all-equal link:** an upper orbit whose four addresses are all equal forces the lower orbit all equal, flipping at each
    step;
  - **the split link:** a lower orbit split as 0011 or 1100 forces the upper orbit to be split.

  Every other long composite is a product.
- **Its size.** Their automaton is tiny (88 states for −73, threshold 5, period 2).
- **What a bounded bond would need.** *(Superseded by MODE-BOND: the link never meets the top, so no bond meeting level 3 can
  use it.)* It must cross a long stretch through this link. So it would need a piece near the top that
  forces such an orbit to be all equal, or forbids its split, with the top member needed. None is in a stem: stems of depth 0 to 2 hold no bond of any size
  at s = 7 or 8.
- **The certified readings, for one pattern.** −73 and −79 are the same pattern (CARRIER's referee: their depth-12 runs refuted the
  same formulas). At depth 12 its least bond has exactly 7 members at s = 7 and 8: a bond of 7 exists (found under the name −79), and
  none of at most 6 (both certified by LRAT). So it reads exactly 6 at s = 5, 6 (depth 11) and exactly 7 at s = 7, 8 (depth 12).
  Reach need not be monotone in the depth, so these are readings at two depths.
  - Both bonds of 7 lie on the lower member's own line of orbits, which alternates between two types and never enters the
    self-similar one. There are two members at level 3, then one or two every two or three levels down to v (levels 3, 3, 4, 6, 6,
    7, 10 at s = 7; 3, 3, 5, 7, 8, 8, 11 at s = 8). That is a chain spread along the way, not a stem and not the advisor's off-line
    shape.
  - At depth 13 the same pattern's search did not decide s = 7 or 8 within 3,600 s per cell.

In the program's words: across a long stretch, the only thing a pattern carries is a strand that has frozen into one of two states.
Reach stays bounded only if the top can tie itself to such a frozen strand *(superseded by MODE-BOND: for the 13 it cannot,
since that strand never meets the top)*. Then a bond between the top's piece and the far end holds
at every distance. Otherwise each stretch needs its own member, and the reach grows linearly.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Lemma S: finitely many path states; lengths ultimately periodic | proved |
| 2 | Theorem N: normal form with three ends (top, lower member, bottom band) | proved by hand (the advisor's three repairs; step 3 repaired for clusters after the referee, not re-refereed) |
| 3 | Theorem D: per depth tier and residue, eventually constant or linear | proved |
| 4 | Lemma R and the corollary: "at most c at every depth" decidable in principle | Lemma R proved; the corollary a proof sketch |
| 5 | Theorem G: products of long composites force linear growth; on the census, exactly the 740 descriptions that forget (139 patterns) | proved; computed (`composite.json`) |
| 6 | The 13 (5 patterns): one carried link (all-equal and split parts) blocks the test; no stem bond at s = 7, 8 | computed |
| 7 | One pattern (8db5da810c00-73, also -79): L₁₂(3, 7) = L₁₂(3, 8) = 7, by bonds spread along the lower member's line | computed, certified (LRAT) |

## Predictions

Frozen in [predictions.md](predictions.md), commit d438a143e, before any Part B computation.
- **P1 holds.** −79 (the same pattern as −73) has a bond of 7 at s = 7 (and at s = 8) at depth 12, so L₁₂(3, 7) = L₁₂(3, 8) = 7.
- **P2 undecided.** At depth 13 the search for a bond of at most 6 for −73 at s = 7, 8 ran out of its 3,600 s per cell.
- **P3 holds.** The 13's automata have at most 88 states (fewer than 10,000).
- **P4 holds.** For all 13, non-product composites lie on the periodic part (the carried mode), so the product test does not prove growth.
- **P5 holds.** Every one of the 740 forgetting census descriptions (139 patterns) passes the test with ℓ₀ at most its forgetting length plus 1.
- **P6, not tested beyond −73.** No other pattern has exact readings at two depths.

## Referee

TWO-ENDS-R1 ([report](referee-R1/report.md)), confirmed with fixes, no Block. Folded in on 2026-11-17 and logged in
`docs/CORRECTIONS.md`:
- **Theorem N's step 3 (Narrowing).** Two branch points joined by a short edge could each be "near" only the other. The step now
  moves clusters of nodes joined by short edges as one unit, and K is recomputed (11c³(T + Q) + k + R). The repaired step has not been
  re-refereed.
- **Three ends, and decidability (Narrowing, wording).** The summaries said "C\* holds" and stated decidability as a result. They now
  say "a three-end form of C\*" and "decidable in principle (proof sketch)".
- **Counts (Narrowing).** As for CARRIER: the 740 and 46 are 139 and 42 of 181 distinct patterns, the 25 open are 10, and −73 and
  −79 are one pattern.
- **The carried link (Narrowing).** It has a split part as well as the all-equal part: a split lower orbit forces a split upper one.
  The next study's search includes it.

The referee also confirmed by its own SAT that both bonds of 7 at depth 12 are bonds of P₁₂, and that the product test equals
forgetting on every census description, with no mixed verdicts inside a group of identical descriptions.

## Lessons

- A finite-state reformulation can match a proved criterion exactly: the product test and forgetting agree on all 786 descriptions (181 patterns).
- What blocks a growth proof can be one link, small enough to name: an all-equal link and a split link passed down a self-similar
  type.
- Pumping on a pattern of finite depth leaves the bottom as an end of its own. Results stated for two ends need a reason to drop it.

## Advisor

Used twice:
- **The plan, before the freeze** (`advisor/plan_answer.md`).
  - Three repairs to the normal form: start replacements at a fixed child; move length only between segments at least T long; a
    branch point that cannot move is already near an anchor.
  - Pump a window of levels, not one segment, in the dichotomy.
  - Theorem D needs no normal form.
  - The product test, and the advice to compute the real automaton.
  - The third end cannot be removed by anything it saw.
- **The previous epic's question** (CARRIER's `advisor/head_answer.md`) supplied C* and the pumping idea.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt (C*'s converse; the 13) | **Status:** Successful | Normal form (three ends), dichotomy and product test proved; the 13 reduced to one carried link |
| Local direction (the 13) | Continue (settled by MODE-BOND: they grow) | A bounded bond for them must tie the top to the carried link (all-equal or split); that is a small, exact search |
| Broader exploration (G17's addressed line) | Known alternatives | B186, B188 |
| Long-term goal (G17, with G1) | Capability gained | Bounded reach is now characterised by pieces at three ends (semi-decidable, sketched); on each depth tier growth is linear when it happens |

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A83 used; none added.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Settle the 13 through the carried mode | 2/3 — Substantial | 3/3 — Ready | Search for the least set near the top whose assignment forces an orbit of the self-similar type all equal, or forbids its split (the split link, added after the referee), with the top member needed (exact, by the block automaton); if none exists, prove growth by a test that allows that one mode → a bound for the 13, or linear growth proved | Selected · awaiting go-ahead |
| 2 | Two ends or three: does any pattern need the bottom band? | 2/3 — Substantial | 2/3 — Testable | Compare least bonds with and without a bottom piece on the census's bounded patterns at large depth tiers → a pattern that needs it, or a proof that the bottom can be dropped | Alternative · deferred |
| 3 | Exact reach by least-mark costs (B186) | 2/3 — Substantial | 2/3 — Testable | As filed | Alternative · deferred |

The reasons for each rating:
1. **The carried mode.** Payoff 2: it decides the last open patterns of the line, either way. Concreteness 3: the obstacle is one
   named mode, and the automaton is tiny, so the search is exact and small.
2. **Two ends or three.** Payoff 2: it decides whether C* holds as first stated. Concreteness 2: the bottom pieces need a three-end
   every-depth routine.
3. **Least-mark costs.** As filed.

## Hand-off to the referee

**Files.**
- This folder: the note, the design and predictions, the advisor's Q/A, `composite.py`, `run_composite.py` and `composite.json`.
- The proof family `proofs/TWO-ENDS-20261117-001A/`: `proof.md`, `check.py` and `result.json`.
- The certified readings, in CARRIER's folder: `threshold_deep.py` and `threshold_deep_*.json`.

**Least sure.**
- (a) Theorem N's step 3, pushing branch points of the anchor tree upward, and its constant K.
- (b) Theorem D's window. Every orbit of S at the window's levels must lie on a crossing, which needs no special orbit there,
  including branch points.
- (c) Theorem G's factorisation across a window with several disjoint crossings.
