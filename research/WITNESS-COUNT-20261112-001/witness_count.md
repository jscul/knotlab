# How many all-equal knots each dead depth needs

Epic `WITNESS-COUNT-20261112-001` (`LIMIT-STATE-20261112-001` direction 1; G17, with G7), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in commit 6be19d282, amended before any outcome was looked at in commit 92403fb31 (memory only). The canonical K1–K3
test is unchanged. Refereed by the referee thread (WITNESS-COUNT-R1, `referee-R1/report.md`, commit 749ac8386): **confirmed with
fixes**, folded in below; three corrections logged (one Narrowing, two Not a block).

## Words

As in the pre-registration: a **witness** (a call of depth t whose three ends are all equal), w_t (the least number of witnesses at
depth t over living states of the usual limit), N_t (calls of depth t), A_t (disjoint copies dead on their own), B_t (each such
copy weighted by its own least count; one-definition families), **multiplicative** (w = B at depths T+1 and T+2), **joint** (one
living state attains w_T, w_T+1 and w_T+2 together). Shares are of LIMIT-ONLY's families drawn by the description code (A71, A79).

## The question

What least number of witnesses does a living state need at each dead depth, how does it grow, does it follow the copies (one least
count per independent dead copy), and can one state attain every depth's least count together?

## The question in standard terms

For satisfiable infinite iterated hyperedge-replacement NAE instances whose capped finite members are unsatisfiable: the least
number of monochromatic replaced hyperedges per derivation depth over satisfying assignments, against the sum over disjoint
unsatisfiable sub-derivations of their own least numbers, and whether the per-depth minima are attained simultaneously.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The bounds hold.** No living state has fewer witnesses than A_t or B_t (0 violations in 798 families). | proved; checked | G passed |
| 2 | **Copies are not independent.** In only 69 of 593 one-definition families (11.6%) is the least count at depths T+1 and T+2 the sum of the copies' own least counts; in the rest it is larger, usually by a little (most often by 6 to 33% at one depth). *After the referee: the excess comes from the ends. A copy's three ends separate its insides from the rest, so its least count is a function of its end state, an 8-entry table per depth; the calling copy's own distinctions are the ends of several calls and tied by its knots, so not every copy can sit at its cheapest ends. All 524 non-multiplicative one-definition families have an end-dependent table (2 values in 214, 3 in 217, 4 in 93); none with a constant table is non-multiplicative. Recomputed by this table on all 798 families with no SAT.* | exact per family, census frozen | P1 failed |
| 3 | **Depths trade off.** In only 107 of 798 families (13.4%) does one living state attain the least count at all three depths; in the rest, keeping one depth at its least forces more witnesses at another. | exact per family, census frozen | P2 failed |
| 4 | **The count is a share of the calls, slowly rising.** Median w/N: 0.025, 0.031, 0.033 at depths T, T+1, T+2; 733 of 797 branching families keep a fixed share (within a factor of two), 61 lie between and 3 stay constant. *After the referee: by the table, on every family and to depth T+6, the median share levels at 0.030 from T+3 on.* At depth T, 418 families need one witness, 213 two, 68 three and the rest up to 21. | exact per family | reported (settled in kind by the bound) |
| 5 | **Few deeper witnesses sit inside shallower ones.** In the states that attain every least count, 10% of the depth-t+1 witnesses are made inside a depth-t witness's copy; the rest are in other branches. *After the referee: from one solver-chosen state per family, so not canonical.* | exact per family | reported |
| 6 | **Where one witness per depth suffices, only one chain dies.** The 4 such families have one dead copy per depth (A = 1): the dying self-holding definition calls itself once, and the branching, when there is any, is in a second definition that does not die, so the calls grow by a constant per depth (for example 5, 7, 9 or 16, 21, 26), not by a factor. In 9 more families a single dead copy per depth still needs two or more witnesses. | exact per family | reported |

## Answer

The all-equal state a living infinite pattern needs is a sum of local needs that depend on each copy's ends. Each dying copy needs
its own least count, as proved, but that count depends on the state of the copy's three ends, and the copies' ends are tied together
by the knots of the copy that calls them; so in 88% of one-definition families the whole needs more than the sum of each copy's
cheapest count, and in 87% of all families no single state keeps every depth at its least. *(Narrowed after the referee: "not a sum
of local needs" overstated it; given its ends a copy's need is local.)* The extra witnesses are not where the
earlier ones were: only a tenth of them sit inside a shallower witness. One witness per depth suffices only where a single chain of
copies dies.

## Reading

**Interpretation, not a theorem.**
- **For the owner's picture.** The copies are not independent parts; they share distinctions (one distinction meets many copies),
  and through those shared distinctions the copies constrain each other's ends, so each copy's need, local given its ends, is set
  by a choice made in the copy above: the forbidden state is placed part by part, but the parts' ends are chosen together. The influence hops: deeper all-equal knots mostly sit in other
  branches.
- **Settled against measured.** That the count grows as a share of the calls is the bound's; the excess over it and the trade-off
  between depths are measured.

## Lag cutoffs and census-only claims

798 of 894 genuine families read (92 over 60,000 knots, 3 over 20,000 calls per depth, 1 recurrent), depths T to T+2. Exact per
family. Where the extra witnesses sit was not located.

## Review

**WITNESS-COUNT-R1** (the referee thread, confirmed with fixes): every least count recomputes exactly by the end-state table with no
SAT (798 of 798, plus the 95 the census could not read, to T+6); its own SAT agrees on the joint query (262 of 262); the bound's
recursion and the totalizer are right, and the amendment changed memory only. Its fixes are made above. The advisor model reviewed the draft cold (`advisor_review_answer.md`): it gave the sharper
bound B, showed the draft's first prediction refuted by it in advance, and proposed the multiplicativity and simultaneity tests.

## Literature and provenance

Known: cardinality-bounded satisfiability (totalizers), tree decompositions. Not found: witness counts of limit-only NAE patterns.
Classification: known-with-delta.

## Workspace assumptions

A71, A79 used, unchanged.

## Ratio

Substantive: the exact counts on 798 families. Administrative: the pre-registration, its amendment, this note, the closure.

## Corrections

Three, from the referee (`docs/CORRECTIONS.md`, 2026-11-12): **Narrowing**, the least count is an end-dependent sum, local given the
ends; **Not a block**, the nested share is from one solver-chosen state; **Not a block**, the table extends the growth law. The run's
memory failure and its amendment are recorded in the pre-registration.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — how many all-equal knots each dead depth needs | **Status:** Partially successful (refereed, confirmed with fixes) | Gate held; P1 and P2 failed: copies interfere and depths trade off |
| Local direction — states of the limit | Continue | Where the extra witnesses sit, and through which shared distinctions, is open |
| Broader exploration — G17 | Searching | Can nested patterns count (queued, agreed by the owner) |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | The infinite pattern's need is global, not a sum of parts |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71, A79 used.
**Basket:** `PREFIX-END-20261112-001#2` (2/3 Payoff, 3/3 Concreteness), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3),
`LIMIT-ONLY-20261112-001#1` (2/3, 2/3), `NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #2 (agreed by the owner), then #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Where the extra witnesses sit | 2/3 — Substantial | 3/3 — Ready | In least states, locate each witness beyond the copies' own counts and the shared distinctions joining its copy to others → interference through shared ends, or something else | Alternative · after #2 |
| 2 | Can nested patterns count? | 3/3 — Breakthrough-scale if yes | 2/3 — Testable | Prove the finite-state theorem for this language and name the smallest extension where it fails, with a counter there → a proof and an extension, or a gap | Selected · go-ahead given |

1. Payoff 2: it would show how copies constrain each other. Concreteness 3: the queries exist.
2. Payoff 3 only if nested patterns can count (the doorway to Gödel-type questions the owner asked about); a proof that this language
   cannot is still worth having. Concreteness 2: mostly proof and literature.

**Recommendation.** Research directions: #2 now, as agreed; #1 after it.
