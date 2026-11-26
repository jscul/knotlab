# Independent referee report on the second check

**Confirmed with fixes. No Block.**

All 26 pinned exchanged holders pass the canonical knot test. The bare ring returns at five, seven and eight knots. At six the exchange has no loose distinctions, and the grown preparation has one class. Neither reading of the exchange selects a relative sign.

## What was rebuilt

Each ring started with two loose distinctions per knot and grew for one ordinary round under even parity. Moves keep every tied shortest allowed change through each distinction. Ranks count independent allowed changes / independent moves. Distances count distinctions needed to read / change class.

| Starting knots | Loose values | Ranks | Classes | Exchanged pieces, two-place / four-place | Most holders of one distinction | Least read / change |
|---:|---|---:|---:|---:|---:|---:|
| 5 | Free | 15 / 14 | 2 | 5 / 25 | 5 | 5 / 5 |
| 6 | Free | 22 / 21 | 2 | 12 / 42 | 8 | 6 / 5 |
| 7 | Free | 21 / 20 | 2 | 7 / 35 | 5 | 7 / 5 |
| 8 | Free | 24 / 23 | 2 | 8 / 40 | 5 | 8 / 5 |
| 5 | Pinned | 6 / 5 | 2 | 0 / 5 | 2 | 3 / 5 |
| 6 | Pinned | 5 / 5 | 1 | 0 / 6 | 2 | Undefined |
| 7 | Pinned | 8 / 7 | 2 | 0 / 7 | 2 | 3 / 7 |
| 8 | Pinned | 9 / 8 | 2 | 0 / 8 | 2 | 3 / 8 |

**Growth and exchange.** The three positive renamings map every holder and distinction. At six, 12 distinctions each have two holders. The bare ring has six shared and 12 loose distinctions. In the reverse order, the pinned bare ring exchanges to one holder of the old ring. It grows to $n+1$ holders of $n$ places each. The orders differ at all four sizes. [Moves and witnesses](rings.json) · [Renamings and reverse-order counts](structure.json)

**Canonical knot test.** Pinning fixes the grown stage’s loose values when finding moves. The exchange then puts a parity rule on each move. On every four-place holder, projection of the whole exchange gave eight even states. Forgetting any distinction gave all eight states of the other three. **26/26 pinned** and **142/142 free** four-place holders passed K1–K3. The 32 free two-place pieces lack the required two loops and contact. The free pattern also exceeds the two-holder limit. All passing distinctions can flip by a finite allowed change. [Projected states and checker verdicts](forgetting.json)

In the original pinned preparation every new holder failed K2. Old holders passed at five, seven and eight, and failed at six. Imposing the original and exchanged laws *together* left **4, 8, 4, 8** pinned states, in size order. All exchanged holders then failed K2 except the six at size six. [Projection results](forgetting.json) · [State counts](signs.json)

**The sign argument.** If the moves generate $H$, invariance gives one independent weighting value per class $x+H$. With two classes, the weightings $(1,1)$ and $(1,-1)$ satisfy every move and give identical squared weight on every assignment. The value-law interpretation restricts assignments as counted above. Neither reading selects a sign. At eight, the old-ring change belongs to the free move span and lies outside the pinned move span. Pinning therefore creates the tested class distinction there. [Rebuilt ranks and membership](rings.json) · [Motion study’s argument](../../READS-HOLDERS-SOURCES-20261120-001A/motion.md#two-meanings-of-least)

**Supplied readers.** At each free size, four neighbouring knots hold a five-distinction allowed change that flips the class label. Its supplied read gives sign $s$ with certainty. Summing over all 32,768 five-knot states gave expectations $+1$ and $-1$. At five, seven and eight I checked all 30, 126 and 254 ordered nonempty splits of the pinned old ring. Either part alone leaves the allowed set. Each reader is fair, and their product is $s$. Outputs $(r,sr)$ for one shared fair value $r$ reproduce this setting pair. The six-knot control has only the positive invariant preparation up to normalization and overall sign. [Reader holdings and exact counts](signs.json)

## Fixes

1. **Narrowing — the six-knot exception.** The decision says “**The exchanged pattern** (each move read as a knot on the distinctions it changes) is lawful by the local test only with loose values pinned, and then it is the bare ring itself: the exchange undoes growth, and growth does not commute with it.” The handoff says “The distances (`rings_dual.jsonl.gz`): free, least class label n and least class change 5; pinned, 3 and n.” Six is the only tested size where the first round includes two three-parent births and six one-parent births. The pinned moves span all 32 allowed grown states. Both class distances are undefined. The README records the failed renaming. The same exception belongs in the distance and sign claims. [Decision, item 1](../decision.md#what-stands) · [Handoff, item 2](../referee_handoff.md) · [Rebuilt counts](rings.json)

2. **Narrowing — minimum size does not specify a unique support.** “Free, the class is read only across a whole cycle but changed by five distinctions; pinned, read by three and changed only across the whole ring.” At eight, two of the 117 minimum free labels consist entirely of loose distinctions. Two of the 47 minimum pinned changes avoid every old ring distinction. Thus eight distinctions are necessary in the respective readings. The old ring gives one way to attain each minimum. [Study note, distance paragraph](../README.md#what-was-found-dualpy-rings_dualjsonl-commutepy-output) · [Witnesses naming the distinctions](signs.json)

3. **Narrowing — what the second check would select.** “**No native second check.**” The introduction describes a second kind of check “that puts a relative sign between sectors”. Under the supplied action on weightings, invariance under the short translations already gives check equations. Each acts within a class. A class-changing translation sends $(a,b)$ to $(b,a)$, distinguishing $(1,1)$ from $(1,-1)$ by its eigenvalue. Applying it to equal positive values leaves them equal. The supported conclusion is that the recorded exchange supplies no law selecting or preparing a relative sign. [Decision, item 3](../decision.md#what-stands) · [Introduction](../README.md) · [Supplied sign trial](signs.json)

4. **Not a block — exchanging twice.** “The grown ring and its exchanged pattern are each other's dual in the literature's sense: the exchange of the grown ring returns the start, as the dual of a dual returns the lattice.” At five, exchanging the ten-holder grown ring gives the five-holder bare ring. Applying the same pinned exchange again gives **one** holder. This gives a one-way identity on the stated sizes. [Decision, intuition paragraph](../decision.md#position-and-next-directions) · [Both exchanges](structure.json)

5. **Not a block — repetition-code comparison.** “The structure is the literature's repetition code in one reading or the other, not the toric code, where both distances grow.” An ordinary repetition encoding has two constant words and one distinction reads the encoded bit. Even the five-knot pinned preparation here has 64 allowed states in two classes and its least label uses three distinctions. The measured resemblance is a bounded distance in one reading. Identifying a repetition encoding would require an explicit equivalence and a statement of which operations it preserves. [Study note, distance paragraph](../README.md) · [Computed distances](rings.json)

6. **Not a block — holdings for the proposed two-ring test.** “On a pinned ring a knot's row lies across the split of 3b and meets each reader's part of the old ring once, so the two readers hold one such pair under either sign.” Splitting just the old shared distinctions supplies the two partial changes. On five and seven knots their ordinary values realize all $2^5$ and $2^7$ assignments, so they support no nonempty fixed joint parity read. The proposed knot read also needs its parent-to-child distinctions assigned to the readers. This qualification leaves the checked split-change table intact. [Advisor answer, argument 3c](../advisor_answer.md) · [Proposed reading](../README.md#is-it-a-second-check-the-argument-with-the-advisors-counterexamples) · [Old-distinction ranks](signs.json)

## How it was checked and what was not run

Fresh code rebuilt growth from eligible parent groups and next-round demand. The move search finished each size to keep every tie. To certify a minimum it sufficed to match parity-equation outputs from two sets of at most $r$ distinctions. Every change of size at most $2r$ splits into two such sets. Each holder projection was computed by two methods, testing extensions and restricting generating changes. Its exact CNF was passed to the repository’s `knotlab check` with forgetting, reusing results for identical truth tables. [Rebuild](rebuild.py) · [Structural comparison](structure.py) · [Canonical check](forgetting.py) · [Sign checks](signs.py)

From the repository root, set `R=research/SECOND-CHECK-20261126-001/referee-R1`. Run `.venv/bin/python -B "$R/rebuild.py" 5 6 7 8 --output "$R/rings.json"`, then the same command with `structure.py`, `forgetting.py` and `signs.py` and their correspondingly named JSON outputs. Every stage used a timed five-knot pilot at the same configuration. Pilot/full elapsed seconds were 0.03/0.29 for the rebuild, 0.02/0.03 for renaming, 0.19/0.60 for forgetting and 0.03/0.08 for the sign checks. Runs were serial with a 1 GiB address-space limit per process. Only the canonical test used a child process. Peak reported resident memory was under 24 MiB.

**Read only.** The distance archive agrees where it reports numbers. It marks free eight and the pinned read minima at seven and eight as not run. This replay supplies all three. The motion study’s signed trial used a two-knot source. The ring reader counts above are independent. [Archived distances](../rings_dual.jsonl.gz) · [Two-class study](../../TWO-CLASS-SIGN-20261126-001/README.md) · [Motion study’s signed trial](../../READS-HOLDERS-SOURCES-20261120-001A/motion.md#what-response-probabilities-motion-determines)

**Not run.** Sizes outside five through eight, later growth rounds, other laws or move rules, and the two-ring Mermin–Peres square. The finite distance results do not establish an all-size formula.

| Scope | Verdict | Why |
|---|---|---|
| Independent referee check | Successful | All four requested sizes and both preparations rebuilt |
| Exchanged pattern as a sign-selecting law | STOP | The two invariant weightings give opposite answers |
| Other sign-selecting laws | Unassessed | Outside the referee brief |
| G18 Comparing growth laws | Obstruction upheld | Pinning changes the classes and the read and change distances |

**Next step:** Research directions — No next action selected. The requested independent check is complete.

**Corrections:** Six fixes above, no Block.  
**Goals:** No change.  
**Assumptions:** The conclusion uses the recorded move rule and the supplied change read.  
**Scaffolds:** One ordinary round, rings, free or pinned loose distinctions, and explicit reader holdings.
