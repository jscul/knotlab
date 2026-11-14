# Does reading decide whether the bond grows: pre-registration

Epic `READ-RULE-20261114-001` (`CARRY-BOUND-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. A proof
epic with a census check. The statements below are frozen before their proofs are written and before any census computation for
them. The advisor model was consulted before the freeze (`advisor_review_answer.md`). Census code by Codex in one hand-off, run by
the thread. The canonical K1–K3 test is unchanged.

## The question

`CARRY-BOUND-20261114-001` found that, among the census families whose first ray grows but which do not forget, the bond is bounded
at every large depth in 88%, almost always through a top port carried down and read by a knot together with an own distinction of
the target copy, and grows in 11%, where every carried value is unread. Two questions remain:
- Is "a read carried value bounds the bond" a theorem for a whole stratum?
- Does growth need every carried value unread?

## The question in standard terms

In iterated hyperedge-replacement NAE instances, sufficient conditions on the derivation for the least minimal non-shattered set
containing a root vertex and a vertex at depth s to have at most three members; a dichotomy (eventually periodic or at least linear)
under a conditional product condition on the port-relation semigroup; and whether linear growth forces the root's identity-carried
vertices to be unconstrained.

## Prior work in the program

`python3 -B scripts/track.py objects "carried top port read by a knot bounds the bond" --until 2026-11-14 --exclude READ-RULE-20261114-001`
`python3 -B scripts/track.py objects "growth of the bond requires unread carried values" --until 2026-11-14 --exclude READ-RULE-20261114-001`
`python3 -B scripts/track.py objects "conditional rectangularity given a carried coordinate gap argument" --until 2026-11-14 --exclude READ-RULE-20261114-001`

- `CARRY-BOUND-20261114-001`: the census split this study explains; Lemma W, Theorem B and the widened B, Lemma G.
- `TRUE-RATE-20261113-001`, `REACH-CENSUS-20261113-001`: carried top ports and their bounded bonds; relatives.
- `GROW-FACE-20261110-001`: a lexical hit, unrelated.

## Words

As in CARRY-BOUND: a **covered target**, **L(s)**, a **carried** port p at position k of a copy c (the same distinction by identity
along the call word), **bounded** (L(s) ≤ C at every large s), the census's in-scope families. A pair of distinctions is **tied**
when it is equal in every allowed state, or opposite in every allowed state. Census knots are plain NAE on three distinct
distinctions.

## Statements (frozen; proofs to be written in `proofs/READ-RULE-20261114-001A/`)

**Theorem R (a read carried value, exact form).** Let the family be living. Suppose that at depth s some covered copy c holds p at
position k, and S's block has a knot {k, x, z} with x an own distinction of S. Then L(s) ≤ 3, and L(s) ≤ 2 when {p, x} is tied,
unless {p, x} is free and z is tied opposite to p or to x. (z = p as distinctions gives x opposite to p, a 2-bond. If z is tied
opposite to both, then p = x, also a 2-bond.)

**Theorem R1 (syntactic, unconditional).** If in Theorem R the third member z is an own distinction of S that occurs in no other
constraint and in no call's arguments, then L(s) ≤ 3 with no exception. Applied on every residue of the carried sets R_s, it bounds
L at every large depth.

**Lemma C′ (conditional gap).** Fix r. Call a word w of r SELF calls **conditionally rectangular** when, for each assignment of the
coordinates that w carries by identity from start to end (equal at both ends), the slice of its product is a product relation.
Suppose every word of length r is. Then:
1. A bond containing every top port carried through a member-free stretch has its other members on one side of that stretch.
2. A bond that hides h of the carried coordinates is a union of at most 2^h products across the stretch. So it has at most 2^h
   clusters separated by member-free stretches, and a cluster may run below the target and into side copies.

**Dichotomy (to prove from C′).** Under C′'s hypothesis, on each residue of s, L(s) is either bounded or at least linear in s. Which
holds is decided by a finite local state: the carry map, the allowed values of the carried coordinates, and which of them a cluster
excludes. *(After the referee: the proved dichotomy is a post-registration generalisation without C′; its lower bound is positive
linear but possibly very weak, and the "decided by a finite local state" clause is not proved.)*

**The converse, in general (expected false).** The advisor's family, one definition S(a, b, c) with own u, x, w and constraints
"u ≠ a" (a positive NAE gadget), NAE(a, x, b), NAE(c, x, w), SELF(a, u, x), carries a down and reads it by the knot {a, x, b} at
every copy. Below the root, b holds ¬p, so that knot is killed by an opposite tie. The bond should grow: L(s) = s + 3 by the
advisor's count. If it does, then growth does not need every carried value unread. It needs every reading of a carried value to be
killed by a tie.

## Census checks (Codex, on CARRY-BOUND's 5,789 in-scope families and the 175 out of scope)

1. **R1 coverage:** the families where every residue of the repeating part of R_s has a carried position with a knot {k, x, z}, x own
   and z an own pendant distinction (no other constraint, no call argument). Also R1 on progressions only.
2. **R coverage and its exception:** per residue, the knots {k, x, z} at carried positions with x own, and whether the exception
   holds (ties read exactly in CARRY-BOUND's window states). Gate: wherever R applies without the exception, CARRY-BOUND's U ≤ 3 on
   that residue.
3. **Conditional rectangularity:** for r = 1 to 8, whether every word of length r is conditionally rectangular (from the length sets;
   capped is undecided). Reported by CARRY-BOUND's verdict: bounded, growing, undecided.
4. **The counterexample:** build the advisor's family with a positive x ≠ y gadget for "u ≠ a" (the gadget of
   `experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/gadget_control.py`) and a second variant with
   NAE(a, u, u), outside the census grammar. Run CARRY-BOUND's window and growth tests on both, and the direct members-anywhere search
   at s = 1 to 6 (CARRY-BOUND's `direct.py`).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate 2 holds on every residue, and R1-covered residues have U ≤ 3. Every count is reproduced by a second, separate check of the R1 syntax. | any fails |
| Q1 | **The exception is absent from the census.** No in-scope family has, on a residue, a knot {k, x, z} at a carried position with x own that is killed by the exception while no other such knot on that residue survives. | any such family |
| Q2 | **Conditional rectangularity is the rule.** At least 90% of the in-scope non-forgetting weight is conditionally rectangular for some r ≤ 8 (the order-label families cannot be: with nothing carried, the condition is plain rectangularity). | below 90% |
| Q3 | **The converse fails as the advisor counted.** In both variants of the counterexample family, the direct search gives L(s) = s + 3 at s = 1 to 6 (the NAE(a, u, u) variant), and grows by at least one per level in the gadget variant. The window gives no bound, and Lemma G gives no certificate (the carried port is read). | any depth differs |
| — | Reported: R1's and R's shares of the bounded weight (counts, not tests), conditional rectangularity among CARRY-BOUND's 83 undecided, and which undecided families the counterexample's shape describes. | — |

## Proof obligations and stop rule

Write the proofs of R, R1, C′ and the dichotomy in `proofs/READ-RULE-20261114-001A/READ-RULE-20261114-001A-P001_read_rule/proof.md`,
consult the advisor on them (a colleague's check, not a result), then run the census checks. Codex writes only in
`experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex/`, without commits. The shared runner is used if a run
needs more than a few minutes, with each run over about ten minutes registered. If the dichotomy's proof does not close, it is
recorded as a conjecture with the gap stated, and the epic still closes. Stop after the proofs, the census checks, the
counterexample, a referee hand-off and the report.
