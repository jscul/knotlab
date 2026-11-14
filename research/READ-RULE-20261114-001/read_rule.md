# Does reading decide whether the bond grows

Epic `READ-RULE-20261114-001` (`CARRY-BOUND-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. A proof epic
with a census check. Pre-registered in cf764f9e2 (objects gate passed; advisor consulted), with the proofs written in 27670ffe0 before
the census checks (the advisor checked them, and its check gave the dichotomy's proof). Census code by Codex in one hand-off. The
canonical K1–K3 test is unchanged. **Referee pending.**

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
| 1 | **A read carried port bounds the bond (Theorem R).** In every living in-scope family, if at depth s a covered copy holds a main port p at a position whose knot contains an own distinction x, then L(s) ≤ 3, unless the knot's third member is tied opposite to p or to x while {p, x} is free. The exception is exact. | proved | — |
| 2 | **With a pendant third member there is no exception (Theorem R1).** If the third member is an own distinction occurring in no other constraint and no call, L(s) ≤ 3 always: a purely syntactic theorem. In the census it covers 469 of the 5,067 window-bounded in-scope families on every residue (9.1% of the bounded weight). Its two implementations agree on all 5,964 families. | proved; computed | reported |
| 3 | **Nothing grows slowly (the dichotomy).** For every living in-scope family, on each residue of the depth modulo a period, L is either eventually bounded or at least linear. Proof: a member-free stretch longer than the number of states (product, carry map) repeats a state and can be pumped without changing the bond's projection. If no least bond has a long stretch, every level within a fixed distance holds a member. This needs neither forgetting nor rectangularity. | proved | — |
| 4 | **The exception exists, but costs nothing here.** 9 in-scope families have a residue on which every reading knot is killed by an opposite tie (an independent audit confirms all 9). All 9 are still bounded at 3 by other bonds. 73 families stay unresolved, all capped windows except five where the quantifier question below decides it. | computed | **Q1 failed** |
| 5 | **Theorem R covers most of the bounded weight.** On the reading that counts only states where the knot's position is carried, and requires every such state to avoid the exception, R applies on every residue in 87.5% of the bounded weight. That reading is stricter than the theorem needs, since one such state suffices, so 87.5% is a lower bound. Where R applies, the window's bound is at most 3 (no violation; 68 capped families unavailable). | computed | G: no violation |
| 6 | **The conditional gap is not the rule.** Only 37.2% of the in-scope weight is rectangular given its carried coordinates for some r ≤ 8: 32.6% of the bounded identity families, 85.0% of the growers, none of the order-label families. Conclusion 3 made this hypothesis unnecessary. Claim 1′ (a bond holding every carried port has its other members on one side of each member-free stretch) is proved; the cluster bound of Claim 2′ is open. | computed; proved | **Q2 failed** |
| 7 | **The proposed counterexample to the converse fails.** The advisor's family, in both variants (u ≠ a written NAE(a, u, u), or by a positive gadget), has L(s) = 2 at every depth 1 to 6, not s + 3. The constraint "u ≠ a" itself ties the carried port to an own distinction of every copy, so it reads the carried value. No family is known whose bond grows while a carried value is effectively read. | computed | **Q3 failed** |

## Answer

Half of the rule is now a theorem. A carried top port that a knot reads, together with an own distinction of the target copy, gives a
bond of at most three members at that depth, and the only way out is a tie that splits the knot. This covers at least 87.5% of the
census's bounded weight. With a pendant third member there is no way out at all, which is a purely syntactic theorem. And the bond
never grows slowly: on each residue of the depth it is eventually bounded or at least linear, in every family. The converse,
that growth needs every carried value unread, survived the one counterexample tried, because the gadget meant to hide the value
read it instead. It is open, with no known exception.

## Reading

**Interpretation, not a theorem.**
- **Reading is the mechanism.** A family keeps its top within reach exactly where a knot puts a carried value next to something of
  the deep copy's own. A carried value no knot uses is no memory at all.
- **Two speeds only.** By the dichotomy, the law's reach either stays within a fixed number of members or grows at least in
  proportion to depth. There is no slow drift between.
- **The open half.** Whether "no carried value is read" is also necessary for growth is the remaining question. If it is, the
  58 / 40 split is decided by reading alone, with orders as the one other source of boundedness.

## Lag cutoffs and census-only claims

Theorems R, R1 and the dichotomy hold for every living in-scope family. Coverage and the exception's counts are census facts.

## Review

**Referee pending.** The advisor model was consulted before the freeze (`advisor_review_answer.md`: the exact exception, R1's
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

None. Q1 to Q3 are frozen predictions that failed; they correct no earlier claim.

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
| This attempt — reading as a rule | **Status:** Successful (referee pending) | Theorem R, R1 and the dichotomy proved; Q1–Q3 failed informatively; the converse open |
| Local direction — counting inside | Continue | Bounded where read, linear or bounded everywhere; the converse decides the rest |
| Broader exploration — G17 | Searching | The bounded half explained by a theorem |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | A proved mechanism for the law's bounded reach |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1; no goal change. **Assumptions:** A79 and A81 used.
**Basket:** `B173` (2/3 Payoff, 2/3 Concreteness; next in line), `CARRY-BOUND-20261114-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other recursive definitions as targets (B173) | 2/3 — Substantial | 2/3 — Testable | The coordinator's next in line: CARRY-BOUND's window with targets in a second recursive definition's copies, on the 175 out-of-scope families → bounded or growing there | Selected · next in line |
| 2 | The converse: growth needs every carried value unread | 2/3 — Substantial | 2/3 — Testable | Search small families for one whose carried value is read (with an own distinction, the exception avoided) yet whose window and path bounds both fail, then test growth by the dichotomy's long-stretch criterion → a counterexample, or a proof for families with one carried port | Alternative |
| 3 | Why an order bounds the bond | 2/3 — Substantial | 2/3 — Testable | From the 93 order families, a sufficient condition → proved | Alternative |

1. Payoff 2: removes the covered-target caveat from four studies. Concreteness 2.
2. Payoff 2: would turn the split into a rule. Concreteness 2: a bounded search, and the dichotomy gives a finite growth test.
3. Payoff 2. Concreteness 2.

**Recommendation.** Research directions, #1, as the coordinator set, with #2 next.
