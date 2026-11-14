# Proof critique: Rule N and Rule A

Scope: `FORGET-RULE-20261114-001`, bounded referee lane, 2026-11-13. This is an advisory proof audit, not a canonical change. The only scientific sources read were `forget_rule.md`, `preregistration.md`, `advisor_review_answer.md`, and `CENSUS-FORGET-20261114-001/referee-R1/report.md`. No Python under `experiments/FORGET-RULE-20261114-001A` was opened or imported. The author is a separately authored same-task AI subagent, not an external or human referee.

**Verdict: Rule A is refuted as literally stated.** Its eligibility clause lets an untouched-from-above port eliminate a constraint even when that port is a retained child output. An alive, one-definition example is certified by that literal procedure with bound 3 and nevertheless never forgets. Protecting all selected-call arguments repairs this particular defect; correctness of the actual study implementation is outside this lane. Rule N survives for nonempty admitted word products, and the partition-tracking argument survives once peeling is valid.

## 1. Block: the F clause can eliminate a retained output

The rule permits an own distinction not among the selected call's arguments, **or a port in F** ([preregistration](../../preregistration.md), lines 45–47). Only the own-distinction arm explicitly excludes arguments. The proof then asserts that each such step eliminates a degree-one variable of the whole composite (lines 50–51). That assertion is false for the port arm: a port may have no occurrence above and still occur below, or be a final boundary output. Degree one among current constraints does not authorize quantifying a retained output away.

A minimal local discriminator is `NAE(x,v,w)` with top output `x` and bottom outputs `v,w`, where `v` has no occurrence above. Removing the constraint using `v` changes a nonrectangular relation into a full relation. Its projection is full only when `v` is existentially quantified; the bottom relation retains it.

A complete recursive counterexample has one definition, ports `(p0,p1,p2)`, own distinctions `u,v`, and block

```text
NAE(p0,p1,p2)
NAE(p0,p2,v)
SELF(p1,u,v)
```

The selected continuation is removed when constructing its per-call relation; no final child-support constraint is imposed. Thus, writing the child ports as `(d,e,f)`,

```text
R((a,b,c),(d,e,f)) iff NAE(a,b,c) and d=b and NAE(a,c,f).
```

This relation has 20 pairs. The family is alive: the triples `010` and `101` can alternate forever. Its identity-passing graph has only `1 -> 0`, hence is acyclic.

The literal automaton evolves as follows. In the table, marks are sets of whole partition blocks.

| After calls | Partition sigma | Marked blocks M | F | Peeling at that call |
| --- | --- | --- | --- | --- |
| 0 | `0 | 1 | 2` | all three | empty | none |
| 1 | `02 | 1` | `02` | `{1}` | none |
| 2 | `0 | 1 | 2` | `2` | `{0,1}` | Remove the first NAE using port 1, although port 1 is next argument 0. |
| 3 | `0 | 1 | 2` | empty | `{0,1,2}` | Again remove the first NAE using port 1; then remove the second using port 0. |

It therefore reports separation at depth 3. In the actual relation, for every positive integer n,

```text
R^n[010] = {101,111} if n is odd;  {000,010} if n is even.
R^n[101] = {000,010} if n is odd;  {101,111} if n is even.
```

The proof is uniform, not an inference from tested depths. From `010`, the second NAE forces `d=f=1`, leaving `e` free. Of its two outputs only `101` satisfies the first NAE needed to take another step. From `101` the complementary argument applies. Consequently the endpoint first and third bits retain an alternating dependence on the top at every depth. A product containing both top triples and both output sets would contain crossed pairs that are absent. No power is rectangular.

Independent direct enumeration, with no producer or earlier referee imports, found sizes `20,36,36,36,36,36` for powers 1 through 6 and exactly the rows displayed above. The arbitrary-length argument establishes non-forgetting. An initial scratch calculation imposed the final child support and produced singleton endpoint rows; that boundary convention was corrected before this report, and is not used here.

This is a **Block** for the written sufficiency theorem and its bound ([forget_rule](../../forget_rule.md), lines 32 and 58; [preregistration](../../preregistration.md), lines 41–56). It does not by itself establish that the forbidden study code has the same defect, or that any held-out census verdict is false. This lane did not audit census membership or run H2.

## 2. Required repair invariant for F

For a sound one-pass construction, let H_t be the retained constraints in the processed prefix, P_0 the original top variables, and P_t the current frontier. Sufficient invariants are:

1. `F_t` contains only frontier variables absent from every constraint in H_t **and absent by identity from P_0**.
2. Every peeled variable is absent from the next frontier P_(t+1), in addition to its other eligibility conditions.
3. A fresh own variable not in the next frontier is absent above and below by freshness. A current port in F is absent above by invariant 1 and absent below by invariant 2. Its occurrence count must then be exactly one among the remaining current constraints.
4. The removed constraint is ternary NAE, or a declared ternary side relation whose projection after the actual elimination is full.

Under these conditions every elimination preserves the relation on both boundaries. The processed prefix need not be revisited: it contains no occurrence of an eliminated F port. Never revisiting it may miss further valid eliminations, which only makes the test conservative.

The definition “no constraint above touches” is insufficient by itself to protect a top variable that is passed unchanged. Starting with F empty is correct, but the update must preserve that protection. A safe conservative update carries an old port into the next F only if it was already in F and no retained local constraint touches it; fresh own arguments enter F only when no retained local constraint touches them. An original top identity must never become free merely because no constraint happens to mention it.

These are proposed repairs, not a claim that any implementation has been changed or proved correct.

## 3. Not a block: partitions capture paths that climb back

For validly peeled constraints, the advisor's partition construction is sufficient ([advisor answer](../../advisor_review_answer.md), lines 28–34). The necessary invariant is precise:

```text
sigma_t equates exactly those current frontier variables connected in H_t.
M_t marks exactly the sigma_t blocks connected in H_t to an original top variable.
```

Joining sigma_t with the current block's retained connected components and then restricting to the next frontier computes the corresponding invariant for the extended prefix. Any portion of a path that returns into an earlier layer enters and leaves it at current frontier variables; sigma already records that connection. A prefix component missing the current frontier cannot later be reconnected, because fresh future constraints attach only through the frontier. Thus empty M is absorbing.

The advisor's own negative control illustrates why a directed downward test fails: the three components `p0--a1`, `p1--p2`, and `a0--a2` splice across layers. The partition after one layer is `02 | 1`, with block `1` marked; the next layer returns to that live state. The full partition sees the climb-back path. This part of the proof does not require storing the entire prefix graph.

Separation then gives rectangularity because connected components have independent variable sets and the two boundary groups lie in disjoint components. Empty solution sets cause no problem. Composing a rectangle `X x Y` with any compatible relation gives `X x image(Y)`, possibly empty. The eventual-bound argument is therefore valid once every transition's peeling is valid. The advisor's count of 22 states/17 live states concerns `(sigma,M)` alone; an automaton extended with F needs its own state count or the stated longest-live-path bound.

A positive control is a block consisting of `NAE(p0,p1,p2)` and `SELF(u,v,w)` with fresh own `u,v,w` and no coupling. Its relation is `NAE(P) x {0,1}^3`; the generic automaton loses all marks after one call without eliminating a retained output.

## 4. Narrowing: Rule N needs nonempty word powers

The identity argument is correct when the relevant repeated cycle word has a nonempty relation at every repetition ([preregistration](../../preregistration.md), lines 22–26). Identity then forces equality of the traced endpoint coordinates; simultaneous complement gives both diagonal values. A rectangle with both coordinate values would include the unequal crossed pair, which is impossible.

Complement closure alone does **not** imply both values occur: the empty relation is complement-closed and rectangular. An unsatisfiable family with identity passing is therefore outside the theorem's intended conclusion. Make the alive/admitted-support hypothesis explicit, or state directly that all repeated cycle-word products are nonempty. In an alive unfolding model this can follow from an actual solution restricted along each finite chosen call word, but that semantic fact must be stated.

The final quantifier step should also be explicit: if all length-r products were rectangular, every longer product would be rectangular by closure under composition; choose a sufficiently long power of the cycle word to contradict this. **Narrowing**, unless the unrestricted “every family” wording is intended literally, in which case emptiness is a counterexample to that wording.

## 5. Generic start: correct repair, eight cases not rechecked here

Starting from generic S with all ports marked, discrete sigma, and F empty tests the requested products R_w ([preregistration](../../preregistration.md), line 44). Starting from main can instead test a root-conditioned relation. A wrapper whose main ports do not occur among its fresh arguments to S can lose all main marks immediately even when S passes its own ports unchanged forever. Such a certificate says nothing about generic S forgetting.

Therefore the conceptual generic-start repair is **Not a block**. The eight training failures reported in [forget_rule](../../forget_rule.md), lines 63–66, are evidence against the earlier main-specific version, not automatically against the frozen generic version. The four permitted notes provide no keys or traces for those eight cases, so this lane cannot independently confirm their identities or the claim that all eight are fixed. That is a reproducibility boundary, not a fresh refutation.

## 6. Narrowing: rectangularity, bond growth, and identity conjecture

The purely relational statements N and repaired A do not use the gap argument, conditional on the per-call relations being exact. The several-definition caveat attached to H2 ([preregistration](../../preregistration.md), lines 75–76) should distinguish correctness of relation summaries from the downstream theorem about bonds. The gap argument's target-scope defect does not alter the algebraic meaning of H2.

Conversely, a relation theorem does not extend the gap bound to arbitrary recursive targets. The earlier referee restricts it to copies of S **whose ancestry after main consists of S calls**, uses `2 + floor((s-1)/r)` for wrappers, and excludes delayed S as well as other recursive definitions with own targets ([CENSUS referee](../../../CENSUS-FORGET-20261114-001/referee-R1/report.md), lines 53–64). Saying only “targets that are copies of S” ([forget_rule](../../forget_rule.md), lines 47–49) omits the delayed-S restriction. State the full ancestry qualification; an “any copy” conclusion needs the additional family-scope condition.

Finally, “every way down forgets unless … forced equality” ([forget_rule](../../forget_rule.md), lines 39–42) exceeds the two proved directions. The proposed forced-tie characterization is explicitly future work in lines 109–110. Treat the categorical identity-only explanation in lines 50–54 as a working hypothesis, not as a consequence of N plus A. **Narrowing**.

## Safe conclusion and next discriminator

The strongest surviving theorem is: valid existential peeling followed by boundary separation proves rectangularity; frontier partitions faithfully decide that separation. Direct identity cycles obstruct forgetting when their repeated products remain nonempty. The written F eligibility requires repair before Rule A's claimed general sufficiency can be accepted. First verify that the repaired transition excludes every selected-call argument from every peeling candidate and preserves original top identities; then run the counterexample above as a mandatory rejection control. No canonical definition, lifecycle status, publication record, or shared document was changed by this lane.
