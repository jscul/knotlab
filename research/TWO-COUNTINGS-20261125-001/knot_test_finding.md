# The knot test in the whole structure, on the setting line's structures

Epic `TWO-COUNTINGS-20261125-001`, 25 November 2026. Computed before the ticket's freeze by the drafter's prototype and
checked with the canonical checker; the ticket's run (part 8) repeats it with its own engine. Not refereed. Verdict
proposed: a **Narrowing** for SETTING-AS-REREAD-20261123-001, ONE-PARENT-REREAD-20261123-001 and the 8-knot row of
THIRD-HOLDER-20261123-001B. Structures: [structures.json](../TWO-COUNTINGS-20261125-001A/structures.json).

> **Referee report R1, 26 November 2026: confirmed with fixes, no block** ([the report](referee-R1/report.md)). The four statements
> of the knot-test finding hold, and every registered comparison counted from a common stage before both settings
> gives 2 over all two-valued outcome functions, with both records hidden (1,816 verdicts). Read this note with these
> narrowings.
> - **Settings made by a law.** The law does make the two standard setting knots on the 11-rule start, but from a
>   start whose only holders of the two distinctions they take both fail the knot test in the whole. Read "an 11-rule
>   start with nine knots" for "a structure of 11 knots".
> - **The one-parent gain.** In all 280 histories with a failing rule the failure belongs to a setting that was
>   supplied; every birth the law made passes.
> - **The least size.** Seven old rules (nine with both settings) remains the least for a hidden excess under the
>   earlier census's parity outcomes and bounds, not over arbitrary two-valued outcomes. The eight-rule witness of
>   20/9 fails the knot test; the nine-rule one passes.
> - **The lemma.** Its hypotheses are sufficient on the registered form of a setting; "each hypothesis is needed" is
>   not shown. It needs one more condition said outright: given the old state, the setting stage gives a product of
>   two distributions, each depending on its own setting alone. With other rules added at the same stage an example
>   of six rules, every one a knot, scores 61/30 and changes the second record by 1/60.
> - **"The excess above 2 appears only under counting from the finish."** Read: all registered common-stage
>   comparisons that satisfy the lemma score 2. Both mixed stages of the 8/3 example score 7/3 with a record changed;
>   and counting from nothing under a supplied order of construction gives a hidden 104/45, and a hidden 20/9 under
>   93 orders.
> - **Orders of construction.** All 329 orders in the class score 2, and so do 490 outside it. The greatest hidden
>   score is 104/45; the greatest of all is 6117/2470.
> - **When the countings part.** For "under not-all-equal they part at once" read: of 477 growths that make a birth,
>   436 part in round one, 38 in round two, one in round three, and two still agree. The formula for one birth holds
>   for a not-all-equal birth with old inputs and at least one fresh distinction.
> - **Equal finishes and pair tables.** All 466 equal finishes in the renumbering check also had equal histories, so
>   that check never met a finish reached two ways. No two of the 194 pair tables are the same, so "the pair tables
>   decide the next birth count" was tested by no pair.
> - **Smaller fixes.** Of the 512 sign assignments 256 score above 2, 128 of them hidden at 20/9; the one-parent
>   failure is 280 of 680 histories and the shared-payment failure 33 of 214; 33 structures were projected and 28
>   given the canonical command; the file of recorded readings is under version control; and the direct checks ran
>   to a narrower limit than reading 35 says, leaving out 345 rounds that the referee checked with no verdict changed.

## Finding

1. In the 11-knot structure of SETTING-AS-REREAD-20261123-001A, the two four-place parity rules even(x1,x2,x3,c) and
   even(y1,y2,y3,t) fail K2 in the whole structure, in the start and in all four finished structures. With the sign
   assignment of the record each induces {0011, 0101, 1010, 1100} on its places (x2 ≠ x3 and c the opposite of x1,
   likewise for the second observer): forgetting x1 leaves x2 ≠ x3, so K2 fails. The other 9 knots and both setting
   knots pass. So the structure is 9 knots and two rules that are not knots in the whole.
2. In the finished structures of ONE-PARENT-REREAD-20261123-001A's smallest gain (61/30), the first observer's setting
   knot nae(x1,x2,za) fails K2 at a = 0: the part forces x1 ≠ x2 (even(x1,h1,h2) with odd(x2,h1,h2)), so it induces
   {010, 011, 100, 101} and constrains nothing (za is free). At a = 1 every knot passes. The 61/30 compares a knot with
   a non-knot.
3. THIRD-HOLDER-20261123-001B's 8-knot structure (20/9) has even(y1,y2,y3,s1) failing K2 in the whole. The 7-knot
   (19/9) and pencil 9-knot (20/9) structures pass knot by knot in the whole, in the start and every finished
   structure, and so does the 18-knot structure of THIRD-HOLDER-20261123-001A (20/9), by projection only. **A hidden
   excess also stands on structures whose every knot passes; a failing rule is not necessary for one.**
4. Every rule of every structure tested passes on its own. The earlier "every knot passes" was a test on its own:
   THIRD-HOLDER-20261123-001A's gate builds each knot's relation from that knot's own clauses, with no other knot and no
   witness ([common.py](../../experiments/THIRD-HOLDER-20261123-001A/THIRD-HOLDER-20261123-001A-E001_witness/common.py),
   lines 355–368); REVIEW-LEADS-20261123-001C says "Each knot passes the canonical test on its own"
   ([result](../REVIEW-LEADS-20261123-001C/result.md), line 71). SETTING-AS-REREAD-20261123-001A,
   ONE-PARENT-REREAD-20261123-001A and THIRD-HOLDER-20261123-001B ran no knot test.

## The sentence the earlier results carry

"The rules here were called knots by a test of each rule on its own, or by none; in the whole structure (canonical
test, TWO-COUNTINGS-20261125-001A) [the named rules] are not knots; the scores stand as arithmetic on the stated rules,
and a hidden score above 2 under counting from the finish also stands on the 7-knot, pencil 9-knot and 18-knot
structures, whose every knot passes (the 18-knot by projection only)."

For SETTING-AS-REREAD-20261123-001: [the named rules] = even(x1,x2,x3,c) and even(y1,y2,y3,t). For
ONE-PARENT-REREAD-20261123-001: the setting knot nae(x1,x2,za) at a = 0 of the smallest gain. For
THIRD-HOLDER-20261123-001B: even(y1,y2,y3,s1) of the 8-knot structure; its minimum of 7 knots stands, since that
structure passes.

## Definitions used

- **In the whole structure** (the record's own: [SD](../RING-IN-BALANCE-20261123-001/definitions.md), lines 130–139,
  "A knot with place set S passes K1–K3 in the whole structure when the allowed states of the structure, restricted to
  S, are exactly the even assignments of S", and for not-all-equal "the assignments of S that extend to an allowed
  state of the whole structure are exactly the assignments that are not constant";
  [FD](../PARTS-MEET-AGAIN-20261124-001/definitions.md), lines 286–287, "A knot that passes has, in the whole
  structure, exactly its own rule on its places: constrained as a whole, every part free, some state allowed (K1–K3
  with forgetting)"; and the canonical foundation: a system read as its set of allowed states, witnesses quantified
  away). The **induced relation** of a knot: the assignments of its places that extend to an allowed state of the
  whole structure. K1, K2, K3 tested on it by `knotlab.knots.check_knot` (forgetting reading), every other distinction
  a witness. "Passes in the whole" and "induces exactly its own rule" agreed on every knot tested.
- **On its own**: the same test on the knot's own rule.
- Every knot under its own rule (even, odd or not-all-equal), as the records wrote them.

## The tie and the failing rule

The record says the 128 of 512 sign assignments that give the hidden 20/9 are those forcing x2 ≠ x3 and y2 ≠ y3
([result](../SETTING-AS-REREAD-20261123-001A/result.md), lines 40–41). Recomputed on all 512: the 128 at 20/9 are
exactly those forcing both inequalities. The two four-place rules **fail K2 in all 512**; the induced relation is
{0011, 0101, 1010, 1100} only where the tie is an inequality, and another relation where it is an equality. The two
knots on (x2, h1, h2) and (x3, h1, h2) always tie x2 and x3, as equal or unequal by their signs, and a tie of either kind
between two places of a four-place parity rule breaks K2. So a failing rule is not sufficient for the 20/9 (384
assignments fail without it) and not necessary for an excess (item 3). No other knot fails in any of the 512.

## Per structure

| Structure | Knots | Distinctions | Fail in the whole (K2 in every case) | Fail on their own | Method |
| --- | ---: | ---: | --- | --- | --- |
| 11-knot start | 11 | 16 | even(x1,x2,x3,c), even(y1,y2,y3,t) | none | projection and canonical |
| 11-knot + setting knots (each of 00, 01, 10, 11) | 13 | 18 | the same two | none | projection and canonical |
| 10-knot start A (less even(y2,k1,k2)) | 10 | 16 | even(x1,x2,x3,c) | none | projection and canonical |
| 10-knot start B (less odd(y3,k1,k2)) | 10 | 16 | even(x1,x2,x3,c) | none | projection and canonical |
| smallest gain: part; part + rule-Q round 1 | 7; 9 | 12; 14 | none | none | projection and canonical |
| smallest gain finished, a = 0 (b = 0, 1) | 11 | 16 | nae(x1,x2,za) | none | projection and canonical |
| smallest gain finished, a = 1 | 11 | 16 | none | none | projection and canonical |
| 7-knot start; + setting knots | 7; 9 | 12; 14 | none | none | projection and canonical |
| 8-knot start; + setting knots | 8; 10 | 12; 14 | even(y1,y2,y3,s1) | none | projection and canonical |
| pencil 9-knot start; + setting knots | 9; 11 | 14; 16 | none | none | projection and canonical |
| 18-knot start; + setting knots (one birth per setting) | 18; 20 | 26; 28 | none | none | projection only |

The 10-knot **finished** structures (the 55/27 row, with their three rule-Q births) are untested; the ticket's part 8
tests them. Canonical checks: 287 knots of the structures of at most 20 distinctions, agreeing with projection on all
287; the 98 knots of the 18-knot structures by projection only.

## How to rerun

From the repository root, for each knot of each structure of structures.json:
`PYTHONPATH=tools python3 -B -m knotlab check --cnf "<the whole structure's clauses>" --loops <the knot's places but the
last> --contact <its last place> --witnesses <every other distinction>`. A parity rule is written as the clauses
forbidding each assignment of its places of the wrong parity; a not-all-equal rule as the two clauses (all places) and
(all places negated). The checker enumerates every assignment, so it is practical up to about 20 distinctions; at load
10 a check took 0.14–0.25 s at 16 distinctions and 0.83 s at 18.

## Later tickets, one sentence each

- The smallest gain of the rule-Q line among structures whose every rule is a knot in the whole is reopened, not
  refuted, since the search winner's setting knot at a = 0 constrains nothing.
- A rule-Q birth that is not a knot in the whole structure is an observation about that law, to be recorded as its own
  ticket.
