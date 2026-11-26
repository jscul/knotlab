# Independent referee report on read and change distances after ordinary growth
**Confirmed with fixes. No Block.**

On the five-, seven- and nine-knot rings, ordinary parity growth produced two classes. Reading or changing the class eventually required as many distinctions as there were starting knots. All 50 ring preparations matched the archive. The bound by the starting size applies to the **smaller** of the two measured distances. That minimum reached 4 in the recorded sample of 350 starts. Ordinary growth leaves the choice between uniform and signed weighting open.

## Rings rebuilt first

Each cell gives **read / change** in distinctions. Each starting knot has two loose distinctions. At round zero all ten preparations had one class. A dash means one class, so both class distances are undefined.

| Starting knots | Loose values | Round 1 | Round 2 | Round 3 | Round 4 |
|---:|---|---:|---:|---:|---:|
| 5 | Free | 5/5 | 5/5 | 5/5 | 5/5 |
| 5 | Pinned | 3/5 | 5/5 | 5/5 | 5/5 |
| 6 | Free | 6/5 | 6/7 | 6/9 | 6/11 |
| 6 | Pinned | — | — | — | — |
| 7 | Free | 7/5 | 7/7 | 7/7 | 7/7 |
| 7 | Pinned | 3/7 | 5/7 | 7/7 | 7/7 |
| 8 | Free | 8/5 | 8/7 | 8/9 | 8/11 |
| 8 | Pinned | 3/8 | 5/8 | 7/8 | 9/8 |
| 9 | Free | 9/5 | 9/7 | 9/9 | 9/9 |
| 9 | Pinned | 3/9 | 5/9 | 7/9 | 9/9 |

All 36 cells giving distances have two classes. Direct enumeration through rank 22 checked all allowed changes and every tied move in 27 preparations (14,773,098 states), and all move-invariant parities in 26 preparations (10,613,200 parity sets). The larger cases used exact minimization. The original archive extends the odd-ring results to eleven knots and through round six. Those additional entries were read from the archive. [Rebuilt ranks, distances and witnesses](rings.json) · [Original ring archive](../rings_dist.jsonl.gz)

## Sample checked second

The recorded seed 20261127 reproduces both lists of selected indices. It selects 200 entries without replacement from the 7,075-entry census up to renaming, and uses the same seed separately to select 150 from the 3,000-entry labelled extension. The extension roster was itself drawn with replacement under its stated acceptance conditions.

| Archive tally | Starts | Stages read | Reached round 4 | No class distance at any stage | Best smaller distance 2 / 3 / 4 |
|---|---:|---:|---:|---:|---:|
| Census of small starts | 200 | 617 | 93 | 173 | 26 / 0 / 1 |
| Extension of larger starts | 150 | 397 | 60 | 102 | 46 / 2 / 0 |

Six starts were chosen deliberately for replay. All **44** free and pinned preparations matched on holder count, distinction count, both ranks, class count and every numeric distance. The four-knot ring, census entry 424, attained 4 free in all four rounds. A different four-knot start with a double meeting (entry 98) gave 2/5 through 2/11 free. The four-knot one-class control (entry 201) had no funded round. In the extension, the six-knot four-class start (entry 407) gave 2/3 under both settings, the seven-knot start attaining the extension maximum (entry 1001) gave 3/5 through 3/11 free, and the eight-knot start with two free starting classes (entry 2342) gave 2/4 there. The original six four-class preparations report read upper bounds of 2. These bounds suffice for the archived maximum. [Archive tally](archive.json) · [Rebuilt starts and distances](samples.json)

## The argument

Let *S* be the allowed changes and *H* the sums of moves. With two classes, *S/H* has a unique nontrivial character. Every class label induces that same character on *S*. Translation by any change outside *H* pairs the two classes bijectively, reversing the character, so its sum over *S* is zero. Multiplying by this character gives a signed weighting. The unsigned counting rule gives each state weight one, and every move preserves either assignment of signs to classes.

On **all 24** rebuilt odd-ring preparations after growth, the old shared distinctions both label and change class. Their self-overlap is odd. The first round with *both* minima was 1, 2 and 3 with loose values free, and 2, 3 and 4 pinned, in order of ring size. The first-grown free five-knot ring gave 16,384 states of each sign by enumeration, agreeing with the earlier two-class count. [Sign counts](arguments.json) · [Two-class referee](../../TWO-CLASS-SIGN-20261126-001/referee-R1/report.md) · [Second-check referee](../../SECOND-CHECK-20261126-001/referee-R1/report.md)

## Fixes

1. **Narrowing — the ring bound and the one-class exceptions.** “Neither ever exceeds n: the length is the built start's.” At eight knots in round four the pairs are **8/11 free** and **9/8 pinned**. Across the original ring archive, 23 preparations have a reported distance above *n*. Every class-bearing row with both values reported has min(read, change) ≤ *n*. The decision's preceding even-ring formula needs the README's exception for four and six knots pinned, where there is only one class. Growth by two was measured over finitely many rounds. [Decision, item 1](../decision.md#what-stands) · [Study table](../README.md#what-was-found) · [Rebuilt rings](rings.json)

2. **Narrowing — sample coverage.** “In 350 sampled starts of three to eight knots grown to round 4, the largest min(read, change) is 4, at the four-knot ring itself.” The archive includes all 350 selected starts, **153** at round four. The last recorded round was zero for 151 starts, one for 40, and two for six. The realized sample contains 34 four-knot, 166 five-knot, 53 six-knot, 48 seven-knot and 49 eight-knot starts. The census also admitted three-knot starts. Only 75 starts ever had a class distance. [Decision, item 2](../decision.md#what-stands) · [Tally](archive.json)

3. **Narrowing — what a starting cycle predicts.** “Under these weightings a start with a long cycle is rare, and without one growth does not lengthen both distances.” No length threshold is specified. Counting a simple cycle of shared distinctions by its number of distinct knots, **99/200** sampled census starts and **85/150** sampled extension starts already have one of length at least five. At length eight the counts are 0 and 5. The maximum of 4 describes the funded rounds of this sample. A necessary condition for other starts or later growth would need a separate argument. [Study note, sampled starts](../README.md#what-was-found) · [Starting cycle counts](source_cycles.json)

4. **Narrowing — the old ring is one minimizing support.** “A grown odd ring holds one bit that only the whole ring can read and only the whole ring can change, the literature's logical qubit of a code of distance n, with the twist that the reading set and the changing set are the same, which on n odd makes them anticommute.” In the first-grown free five-knot ring, the replay numbers the old shared distinctions 0 through 4. Another least label is {0, 8, 11, 19, 20}, and another least change is {1, 2, 3, 6, 11}. Both have size five and omit old distinctions. The old ring is a simultaneous witness when both minima reach *n*. At five knots pinned in round one it is a label of size five and the minimum read is three. At seven knots free in round one it already changes class and flips its own read, although the minimum change is five. The advisor’s early-round exception concerns the selected least change. [Decision, intuition](../decision.md#position-and-next-directions) · [Explicit witnesses](rings.json)

5. **Narrowing — tie counts cover the ring archive.** “The tie cap of 64 was never reached; the solver timed out on five late rows of the largest rings (not run).” All 126 archived ring preparations report zero cap hits, and the rebuilt rings had at most 20 ties through a distinction. The sample archives contain no cap-hit field. On the seven-knot extension start attaining 3, the free preparation reached **64** ties through a distinction in round three and **128** in round four. Keeping every tie still gave the recorded ranks and distances in both rounds. Five ring rows contain **six missing reads**, including both settings at twelve knots in round six. The advisor read an earlier archive. The final one reports pinned twelve through round five. [Study note](../README.md#what-was-found) · [Archive coverage](archive.json) · [Uncapped replay](samples.json)

6. **Narrowing — a recorded reading does weight by the character.** “No recorded reading weights by it (searched: the motion study uses the old ring's parity as a read; the sign studies' weightings are quadratic, products of parities or differences of indicators); using it as a weight is the motion study's supplied signed read.” The swap study explicitly passes the old-ring character as its fifth weighting, W5, and sums it over completions of readings. Its first-grown five-knot parity record gives total signed weight zero for both lifts of the swap. The motion study also records the signed indicator. These are supplied weightings. The narrower claim holds for ordinary growth, its unsigned counts and its value reads. [Study note, relative sign](../README.md#is-the-relative-sign-set-by-the-structure-an-argument-with-the-advisors-corrections) · [Swap study, named ring calculation](../../SIDE-SIGN-20261126-001/named.py) · [Recorded signed sums](../../SIDE-SIGN-20261126-001/named_rings.jsonl) · [Motion study](../../READS-HOLDERS-SOURCES-20261120-001A/motion.md)

7. **Narrowing — nonzero pins can still distinguish a positive class.** “The character is fixed by the structure only because the all-zero state is allowed (with loose values pinned at other values there is no canonical choice), and it sums to zero over the allowed states, so it is a signed function, not a weighting of samples.” On a translated set of allowed states, the nontrivial character fixes the relative sign of a class exchange. Choosing which class gets plus can require a reference. On the first-grown five-knot ring, pin both loose distinctions of one new knot to one and the rest to zero. The two ones cancel at their holder. All shared distinctions zero then specifies a unique allowed reference, and enumeration gives **32 states of each sign**. A named old-ring read also specifies its sign directly. Ordinary growth still admits both weightings. [Study note, relative sign](../README.md#is-the-relative-sign-set-by-the-structure-an-argument-with-the-advisors-corrections) · [Nonzero-pin check](arguments.json)

8. **Not a block — the proposed test for a further knot.** “The advisor's test, not run here: grow two or three odd rings that meet, read the classes and their labels, and ask whether some sum of ring labels is forced on every allowed state while no single label is (a next-layer parity knot), and whether a least class change changes exactly two of them (a next-layer move).” Three labels (*u*, *u*, *v*) with *u* and *v* free meet both numerical descriptions if changing *u* is a least change. Forgetting *v* leaves the first two tied. The canonical checker rejected those four states and accepted the four states of full three-way even parity. For three open binary linear labels, fixing their **full three-way** parity suffices. A one-dimensional variation that changes all three would reverse that parity, so the projection has rank two and contains all four parity states. A meeting-ring study would still have to identify the two loop distinctions and the contact, project their joint states and test erasure. [Proposed test](../README.md#the-next-layer-question-for-the-other-thread) · [Checker results](arguments.json)

## How it was checked and what was not run

Fresh code reconstructed ordinary growth from the parent groups and their following demand. For each distinction the move search removed it, found all shortest returns between its holders, and restored it. All ties were kept. Pinning removed loose distinctions from allowed changes. With them free, one extra holder represents all loose distinctions in the computation. Its parity equation is already the sum of the knot equations.

For **change distance**, tracking a holder and the parity accumulated along a sequence finds the shortest return with odd character, over all starting holders and a basis of characters. Every allowed odd change contains an odd cycle, and every odd return yields an allowed change of at most its length. This independently checks the study's candidate search. The study’s argument using the literature’s shortest-path tree also holds. Root it on a shortest cycle outside *H*. At least one fundamental cycle in its decomposition lies outside *H*. The two routes along the original cycle to the ends of the omitted distinction bound that candidate’s length by the original length.

For **read distance**, all labels giving a specified character differ by sums of the holder equations. Starting with one label for each nonzero character, binary variable elimination minimized the number of distinctions left after adding holder equations. It recovered witnesses and checked their overlaps. The largest table on rebuilt rings used eleven binary variables. Direct enumeration wherever the relevant rank was at most 22 checked the separate minima. [Growth and source loaders](starts.py) · [Distance algorithms](measure.py)

From the repository root, set `R=research/BOTH-LONG-20261126-001/referee-R1`. Run `.venv/bin/python -B "$R/rings.py"`, then `archive.py`, `samples.py`, `source_cycles.py` and `arguments.py` with the same interpreter and directory. Each accepts `--pilot`. With one numerical thread, a 1 GiB per-process limit and timed prefixes at the same configuration, pilot/full elapsed seconds were 0.14/15.41 for rings, 0.06/0.08 for archive counts, 0.34/15.38 for the six-start replay, 3.36/2.55 for starting cycles including roster reads, and 0.33/0.50 for sign and erasure checks. Peak reported resident memory in those runs was under 38 MiB.

**Not run.** Independent ring distances outside five through nine knots or after round four, including the six original missing reads. Growth and distance replay for the other 344 sampled starts. Exhaustive state or label enumeration above rank 22. Generation of the original source rosters, other growth or move rules, and growth of meeting rings. The sign audit covers the specified ordinary and signed readings.

| Scope | Verdict | Why |
|---|---|---|
| Ring distances and sampled maximum | Confirmed with fixes | All 50 ring and 44 selected sample preparations matched |
| Sign selection by ordinary growth | STOP | Both class weightings are move-invariant |
| Several ring labels | Unassessed | Erasure must be tested on their joint values |
| G18 Comparing growth laws | Scope clarified | The supplied move rule yields two long minima on the tested odd rings |

**Next step:** Research directions — the requested independent check is complete.

| Direction | Payoff | Concreteness | Status |
|---|---|---|---|
| Test three designated labels on meeting rings | 3/3 for deciding whether the joint labels form a knot | 3/3 once holdings and projected states are specified | Outside this referee brief |

**Corrections:** Seven Narrowings and one Not a block.  
**Goals:** No change.  
**Assumptions:** The distances are relative to the shortest-change move rule.  
**Scaffolds:** Built rings, one growth rule, two loose-value settings and the two stated sample weightings.
