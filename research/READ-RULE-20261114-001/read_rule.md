# Does reading decide whether the bond grows

Epic `READ-RULE-20261114-001` (`CARRY-BOUND-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. A proof epic
with a census check. Pre-registered in cf764f9e2 (objects gate passed; advisor consulted), with the proofs written in 27670ffe0 before
the census checks (the advisor checked them, and its check gave the dichotomy's proof). Census code by Codex in one hand-off. The
canonical K1–K3 test is unchanged. Refereed by the referee thread with Codex (READ-RULE-R1, `referee-R1/report.md`, commit
94e2641dc): **confirmed with fixes, one Block on the converse**. Theorems R and R1 and the dichotomy stand, the dichotomy's proof
with two repairs. The converse as stated is false: the referee found a family whose carried values are read, always in R's
exception, and whose bond grows. Read effectively, the converse is a theorem.

## Words

As in `CARRY-BOUND-20261114-001`: L(s), covered targets, carried ports, bounded. A knot **reads** a carried port when the port's
position and an own distinction of the same copy are in the knot. The **exception** of Theorem R: the third member of that knot is
tied opposite to the port or to the own distinction, while the two are free.

## The question

CARRY-BOUND found that the bond is bounded almost always where a carried value is read, and grows where every carried value is
unread. Is the first a theorem for a whole stratum? Does growth need every carried value unread? Together they would make the
census's 58 / 40 split a rule.

## The question in standard terms

Sufficient conditions in iterated hyperedge-replacement NAE instances for a three-element minimal non-shattered set through a root
vertex and a depth-s vertex; whether the least such set can grow sublinearly; whether linear growth forces the root's
identity-carried vertices to be unconstrained.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **A read carried port bounds the bond (Theorem R).** In every living in-scope family, if at depth s a covered copy holds a main port p at a position whose knot contains an own distinction x, then L(s) ≤ 3, unless the knot's third member is tied opposite to p or to x while {p, x} is free. The exception is exact in both directions, but *local* (narrowed after the referee): it says when this triple fails to give a bond, and is not a criterion for L > 3. | proved | — |
| 2 | **With a pendant third member there is no exception (Theorem R1).** If the third member is an own distinction occurring in no other constraint and no call, L(s) ≤ 3 always: a purely syntactic theorem. In the census it covers 471 in-scope families on every residue, 469 of them among the 5,067 window-bounded (9.1% of the bounded weight); the other two are undecided families that R1 bounds anyway. Its two implementations agree on all 5,964 families. | proved; computed | reported |
| 3 | **Bounded or linear (the dichotomy).** For every living in-scope family, on each residue of the depth modulo a computable period, L is either eventually bounded or has a positive linear lower bound (*narrowed after the referee*: the rate can be very weak, since the state count m runs from 5, a rate of 1/6, to 29,359 in the census samples; and the proof gives semi-decision of boundedness only, no finite growth test, onset bound or periodicity of L). Proof: a member-free stretch longer than the number of states (product, carry map) repeats a state and can be pumped without changing the bond's projection. If no least bond has a long stretch, every level within a fixed distance holds a member. This needs neither forgetting nor rectangularity. *Repaired after the referee (not a block):* the stretch's product runs over the blocks c_{a+1} to c_b, with interfaces the ports of c_{a+1} and c_{b+1}, and each member is counted at the copy that holds it as its own, not at every block where it sits as a carried port; the bound is n ≤ (m + 1)t + m with t ≤ \|W\| − 2 occupied levels. No sublinear growth was found. | proved | — |
| 4 | **The exception exists, but costs nothing here.** 9 in-scope families have a residue on which every reading knot is killed by an opposite tie (an independent audit confirms all 9). All 9 are still bounded at 3 by other bonds. After the referee, the quantifier settles the five open cases, and 68 capped families stay unknown. | computed | **Q1 failed** |
| 5 | **Theorem R covers most of the bounded weight.** On the reading that counts only states where the knot's position is carried, and requires every such state to avoid the exception, R applies on every residue in 87.5% of the bounded weight. That reading is stricter than the theorem needs. Under the theorem's own quantifier (some carried state with a surviving reading in every repeating phase), the referee counts 4,484 of 5,067, **87.6%**. Where R applies, the window's bound is at most 3 (no violation; 68 capped families unavailable). | computed | G: no violation |
| 6 | **The conditional gap is not the rule.** Only 37.2% of the in-scope weight is rectangular given its carried coordinates for some r ≤ 8: 32.6% of the bounded identity families, 85.0% of the growers, none of the order-label families. Conclusion 3 made this hypothesis unnecessary. Claim 1′ (a bond holding every carried port has its other members on one side of each member-free stretch) is proved; the cluster bound of Claim 2′ is open. | computed; proved | **Q2 failed** |
| 7 | **The advisor's counterexample fails; the referee's succeeds.** The advisor's family, in both variants, has L(s) = 2 at every depth 1 to 6, not s + 3: the constraint "u ≠ a" ties the carried port to an own distinction of every copy. *Corrected after the referee (Block):* ~~no family is known whose bond grows while a carried value is read~~. In the referee's family S(a, b, c), own x, w: NAE(a, x, b), NAE(c, x, w), SELF(a, b, x), under a wrapper main whose knots force p ≠ q and pass (p, q, r), the carried p and q are read at every copy by NAE(p, x, q), always in R's exception. The bond grows as L(d) = d + 2 (direct search 3 to 8 at depths 1 to 6). So growth does **not** need every carried value unread. **The effective converse is a theorem:** if on a residue some carried value is read outside the exception at infinitely many depths, Theorem R gives L ≤ 3 there, and the dichotomy makes L bounded on that residue. | computed; proved | **Q3 failed** |

## Answer

Half of the rule is now a theorem. A carried top port that a knot reads, together with an own distinction of the target copy, gives a
bond of at most three members at that depth, and the only way out is a tie that splits that knot. This covers 87.6% of the census's
bounded weight. With a pendant third member there is no way out at all, which is a purely syntactic theorem. On each residue of the
depth, the bond is eventually bounded or has a positive linear lower bound, in every family, though that rate can be very weak.
*Corrected after the referee:* ~~the converse is open, with no known exception~~. Read syntactically, the converse is false: carried
values can be read at every copy, always inside the exception, while the bond grows. Read effectively, it is a theorem: a reading
outside the exception at infinitely many depths of a residue bounds the bond there.

## Reading

**Interpretation, not a theorem.**
- **Effective reading bounds the reach.** Where a knot puts a carried value next to something of the deep copy's own, and no tie
  splits that knot, the family keeps its top within reach. *Corrected after the referee:* ~~exactly where~~. A reading that a tie
  always splits is no memory, and orders bound the reach with nothing carried.
- **Bounded or linear.** By the dichotomy, per residue, the law's reach either stays within a fixed number of members or has a
  positive linear lower bound, possibly very weak.

## Lag cutoffs and census-only claims

Theorems R, R1 and the dichotomy hold for every living in-scope family. Coverage and the exception's counts are census facts.

## Review

**READ-RULE-R1**: confirmed with fixes, one Block on the converse (above). The advisor model was consulted before the freeze (`advisor_review_answer.md`: the exact exception, R1's
condition, the repair of Claim 1′ and the proposed counterexample) and on the written proofs (`advisor_proof_answer.md`: no errors
found; the dichotomy by pumping). Its counterexample failed when computed. Its proof suggestion was checked and adopted: the stretch
must be pumped by its own product from the stretch's top, not from the start.

## Literature and provenance

Known: pumping finite semigroup states along words (as in regular languages and tree automata), ties in positive NAE. Ours: the
three theorems for nested NAE bonds, and the census coverage. Classification: known-with-delta.

## Workspace assumptions

A79 used. A81 used: Theorem R bounds bonds that start from a carried top port.

## Ratio

Substantive: three proved statements and a lemma, a census check of 5,964 families, the counterexample family. Administrative: the
freeze, this note.

## Corrections

From the referee (`docs/CORRECTIONS.md`, 2026-11-14):
- **Block.** The converse as stated, in conclusion 7, the Answer and the Reading. It is false syntactically (the referee's
  family) and proved effectively.
- **Narrowing.** R's exception is local to the triple.
- **Narrowing.** The dichotomy's wording: "per residue, eventually bounded or a positive linear lower bound", the rate possibly very
  weak; no finite growth test; the pre-registration's "decided by a finite local state" is not proved.
- **Narrowing.** No predicate was given for "the counterexample's shape", so no census count follows from it.
- **Not a block.** The dichotomy's two proof repairs; R's coverage 87.6% (87.5% the stricter bound); 68 capped unknowns; R1's two
  denominators.
- **Narrowing, carried to `CARRY-BOUND-20261114-001`.** Its reading "a read value gives a short bond" holds for a value read outside
  R's exception.

Q1 to Q3 are frozen predictions that failed; they correct no earlier claim.

## Data

- Proofs: `proofs/READ-RULE-20261114-001A/READ-RULE-20261114-001A-P001_read_rule/proof.md`.
- Census checks: `experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex/` (`coverage.py`, `r1_check.py`,
  `conditional.py`, `counterexample.py`, `exception_audit.py`, `summary.json`, `REPORT.md`).
- Codex left five questions open (REPORT.md, "Ambiguities"). The theorem-correct reading of the first is "some carried state", and
  conclusion 5 gives a lower bound under the stricter one. The "83 undecided" of the pre-registration is CARRY-BOUND's figure after its
  path DP; Codex used the 90 before it.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — reading as a rule | **Status:** Successful (refereed, confirmed with fixes, one Block) | Theorem R, R1 and the dichotomy proved; Q1–Q3 failed informatively; the converse false syntactically, proved effectively |
| Local direction — counting inside | Continue | Bounded where read, linear or bounded everywhere; the converse decides the rest |
| Broader exploration — G17 | Searching | The bounded half explained by a theorem |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | A proved mechanism for the law's bounded reach |

**Corrections:** from the referee, one Block, four Narrowing and the Not-a-block repairs; one Narrowing carried to CARRY-BOUND. **Goals:** a checkpoint for G17 and G1; no goal change. **Assumptions:** A79 and A81 used.
**Basket:** `B173` (2/3 Payoff, 2/3 Concreteness; next in line), `CARRY-BOUND-20261114-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other recursive definitions as targets (B173) | 2/3 — Substantial | 2/3 — Testable | The coordinator's next in line: CARRY-BOUND's window with targets in a second recursive definition's copies, on the 175 out-of-scope families → bounded or growing there | Selected · next in line |
| 2 | What else bounds the bond (*restated after the referee*: the converse is settled both ways) | 2/3 — Substantial | 2/3 — Testable | The rule's exceptions census-wide, bond-pinning and the two-block window → a characterisation of the bounded case | Taken by `TOP-INFO-20261114-001` |
| 3 | Why an order bounds the bond | 2/3 — Substantial | 2/3 — Testable | From the 93 order families, a sufficient condition → proved | Alternative |

1. Payoff 2: removes the covered-target caveat from four studies. Concreteness 2.
2. Payoff 2: would turn the split into a rule. Concreteness 2: census checks and finite windows (the dichotomy gives no finite growth test).
3. Payoff 2. Concreteness 2.

**Recommendation.** Research directions, #1, as the coordinator set, with #2 next.
