# What a living state of the bottomless pattern looks like

Epic `LIMIT-STATE-20261112-001` (`LIMIT-ONLY-20261112-001` direction 2; G17, with G7), 2026-11-12, at the owner's go-ahead and the
coordinator's steer. Pre-registered in commit 9a97fb05e before the registered run. The canonical K1–K3 test is unchanged.
**Referee pending** (handed to the referee thread).

## Words

As in the pre-registration: the **usual limit**, the **genuine** families (alive only in it), the **calls of depth t** (SELF calls
made from copies at level t − 1), a **witness** (a call whose three ends are all equal in a state), **single** (one witness at each
of depths T, T+1, T+2), **single ray** (each witness inside the copy of the one before), **loose**, **branching**. Shares are of
LIMIT-ONLY's families drawn by the description code (A71, A79).

## The question

Every living state of the usual limit must have a witness at each dead depth. Does the limit live only because everything comes
loose, and can one witness per depth, on one ray, carry the need, or must the all-equal state spread?

## The question in standard terms

For satisfiable infinite iterated hyperedge-replacement NAE instances whose capped finite members are unsatisfiable: whether some
satisfying assignment has exactly one monochromatic replaced hyperedge at each of three consecutive dead depths, and whether these
can form a chain in the derivation tree.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Checks.** 894 genuine families (the referee's count); the lemma's gate holds at every dead depth read and every finite part read is alive. | computed | G passed |
| 2 | **The bottom comes loose in most, not the interior.** 87% of genuine families are loose: their limit relations and main relation allow every state of the ends, so the bottom imposes nothing; by the lemma the interior still must place all-equal ends at every dead depth. Limit relations: free 921, a knot 101, three tied 2. | exact per family | reported |
| 3 | **One witness per depth almost never suffices.** In only 3 of 800 branching families (0.4%) does some living state have exactly one witness at each of depths T to T+2; in the other 797 every living state has two or more witnesses at some depth among them. None of the 702 loose branching families allows it. | exact per family, census frozen | P1 failed |
| 4 | **A single ray is rarer still:** 2 of 800 (0.25%). | exact per family, census frozen | P2 failed |
| 5 | **The patterns branch fast.** The median number of calls is 64, 256 and 1,296 at depths T, T+1, T+2; 92 genuine families were too large to read (over 60,000 knots) and one recurrent family was left out. | computed | reported |

## Answer

The infinite pattern does not live by coming loose everywhere. Its bottom comes loose in most families, but every living state has
to set the three ends of some self-holding knot all equal at each depth where the finite versions die, and it cannot do that with
one knot per depth: in 797 of 800 branching families every living state spreads the all-equal state over two or more knots at some
depth, and a single thread of such knots down the nesting almost never works. So the state that only the infinite pattern allows is
spread out, not carried along one line.

## Reading

**Interpretation, not a theorem.**
- **For the owner's nested parts.** The larger pattern does not hand its one forbidden state down a single path to the smaller
  ones; it needs it in several of its inner parts at once, at every depth. The influence that keeps the infinite whole alive is
  spread across its branches, not threaded.
- **What is open.** Whether the number of witnesses needed per depth stays small, or grows with the number of calls (a fixed share
  of copies, which would make the all-equal state a density of the limit).

## Lag cutoffs and census-only claims

801 of the 894 genuine families read, depths T to T+2 of the finite part to depth T+3 with the limit relation at its bottom. The
queries are exact; the families are LIMIT-ONLY's sample of the description code. The split by pass-through call differs slightly
from the referee's (812 without, 82 with, against 821 and 73), by how a pass-through call is detected; the genuine total agrees.

## Review

Referee pending (the referee thread). The advisor model reviewed the draft cold (`advisor_review_answer.md`): per-call marginals are
periodic by construction and the loose test nearly settled, so it proposed the joint queries used here.

## Literature and provenance

Known: compactness; fixed points; satisfiability of tree-structured instances by message passing; hyperedge-replacement grammars.
Not found: the arrangement of the all-equal state in limit-only NAE patterns. Classification: known-with-delta.

## Workspace assumptions

A71, A79 used, unchanged.

## Ratio

Substantive: the exact queries on 801 families. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what a living state of the bottomless pattern looks like | **Status:** Partially successful (referee pending) | Gate held; P1 and P2 failed: the all-equal state must spread |
| Local direction — states of the limit | Continue | How many witnesses each depth needs is the next exact question |
| Broader exploration — G17 | Searching | Other lines paused by the owner |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | What the infinite pattern alone allows is spread across its branches |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71, A79 used.
**Basket:** `PREFIX-END-20261112-001#2` (2/3 Payoff, 3/3 Concreteness), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3),
`LIMIT-ONLY-20261112-001#1` (2/3, 2/3), `NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | How the all-equal state spreads | 2/3 — Substantial | 3/3 — Ready | The least number of witnesses per dead depth, exactly (SAT with a cardinality bound), against depth and calls, frozen → a constant, a fixed share of copies (a density of the limit), or growth | Selected · awaiting go-ahead |
| 2 | A rule for the mixed kind | 2/3 — Substantial | 2/3 — Testable | From LIMIT-ONLY: decide life at every depth from the orbit's cycle in closed form → a rule, or none | Alternative · deferred |

1. Payoff 2: a density would be a number the infinite pattern alone carries. Concreteness 3: the queries exist; only the bound
   changes.
2. Payoff 2, Concreteness 2, as recorded.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
