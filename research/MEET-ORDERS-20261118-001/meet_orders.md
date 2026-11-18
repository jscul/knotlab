# Why how the knots meet changes the number of orders

Epic `MEET-ORDERS-20261118-001`, 18 November 2026, by Claude, on the coordinator's pick. It takes the second direction of
`KNOT-CAP-20261117-001` (why the five-starts differ in the number of orders). Goals G1 and G16; tests A97. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no
Block, folded in on 18 November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `d636345d9` at 02:40 UTC on 18 November. The run
  (long run MEET-ORDERS-B1, 634 cases on the shared runner) went from 02:40 to 03:03 UTC, 634 of 634 cases ok.
- Proof: [proof.md](../../proofs/MEET-ORDERS-20261118-001A/MEET-ORDERS-20261118-001A-P001_second_fill/proof.md).
- Code: [melib.py, job.py, checks.py, merge.py and posthoc.py](../../experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/).
- Results: [results.json and posthoc.txt](../../artifacts/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/).

**Words** (new in the glossary, chosen with the advisor): a knot B(a, c, b) of a presentation of a line has its **halves**, the
line's steps from a to c and from c to b; a knot lies **within** a half of another when all its steps are steps of that half;
**step-disjoint** knots share no step; the **ends' knot** holds both ends; the **bracketing** says which knot lies directly
within which half of which, from the ends' knot, and the **bare bracketing** forgets which half; for χ within ν within π, χ lies
**the same way** when it sits in ν at the end ν shares with π, **the other way** otherwise; a new distinction's **odd set** is the
set of line distinctions whose parity it takes while nothing has added a state.

## The answer

- **What the states do not carry is the bracketing** (proved). Every fewest-knot presentation of a line, n − 2 betweenness knots,
  is a bracketing: each knot B(a, c, b) has its middle c between a and b, and each knot but the ends' knot lies directly within
  one half of exactly one other (Lemma 0, both directions; the literature's triangulation of a polygon, rooted at the side that
  joins the line's ends). The states are the same for all of them; which knot lies within which is how the knots meet, read
  against the line. *Scoped after the referee:* this holds for fewest-knot presentations. One redundant knot (the states
  unchanged) moves the five-starts' chance at n = 7 in all 21 cases tried, by 0.04 to 0.33, and the placements then no longer sort
  by bare bracketing (A100).
- **The shared distinction's place is a proxy for the bracketing** (proved). Per labelling, the line of five has five
  presentations:
  - **at an end** (two of them): a chain, each knot directly within the next, lying the same way;
  - **next to an end** (two): a chain lying the other way;
  - **in the middle** (one): the ends' knot holding one knot in each half.

  So the end and next-to-end placements have the same bare bracketing, and the middle has another.
- **Why that changes the number of orders, exactly** (Theorem 1, proved for every n). A fill makes every step of one half of its
  knot cross every step of the other: two orders. After a first fill at κ, KF3's options are:
  - the fill of each other knot (n − 3 options): it keeps two orders exactly when that knot is step-disjoint from κ, since a fill
    within a half of κ splits that half into two groups that cross each other and the other half, a third order;
  - for each knot sharing a pair with κ, the two fills that re-bracket κ with it (two options each): both keep two orders through
    the knot κ lies within, one of the two through a knot within κ.

  Uniform over those options:

  P(two orders after the second new distinction) = (1/(n − 2)) Σ_κ [s(κ) + 2 p(κ) + c(κ)] / [(n − 3) + 2 (p(κ) + c(κ))],

  with s(κ) the knots step-disjoint from κ, p(κ) = 1 when κ lies directly within a knot, and c(κ) the knots directly within κ.
  It depends only on the bare bracketing:
  - line of five: chains 5/12 (the end and next to an end), the middle 11/18, the values `KNOT-CAP-20261117-001` found;
  - line of six: chains 51/140 (both six-starts are chains), and 79/140 and 83/180 for the other two bare bracketings;
  - a chain of n − 2 knots: 3 [1/(n − 1) + (n − 4)/(n + 1)] / (n − 2), about 3/n, the least of all bare bracketings for every
    n from 5 to 13 (computed).
- **How long the bare bracketing decides it** (computed, exact, every presentation of 5 to 9 distinctions).
  - Through the third new distinction (n0 + 3) the whole distribution of the number of orders depends only on the bare
    bracketing, and different bare bracketings give different distributions (2, 3, 6, 11 and 23 values for n0 = 5 to 9).
  - At the fourth (n0 + 4) the bracketing's order enters: same way against other way. Every two presentations with the same bare
    bracketing differ for n0 = 5, 6 and 7 (22 of 22 distinct up to mirror at 7), but not all: one pair ties at n0 = 8 (65 of 66
    distinct) and 24 pairs at n0 = 9 (193 of 217), as the advisor expected for long bracketings.
- **The untested placement and the six-starts.**
  - Next to an end equals the end exactly through n = 8 (5/12, then 173/6552), and the two part at n = 9 (two orders
    163213/181890072 against 1810423/995045688): the fourth new distinction, where the other way parts from the same way. The
    middle differs from n = 7. At n = 10 three orders have chance 0.5191 (next to an end), 0.5194 (end) and 0.4210 (middle).
  - The six-starts' agreement through n = 9 follows from the same mechanism: both are chains, so the formula gives 51/140 at
    n = 8 and the bare bracketing decides n = 9; the fan lies the same way twice and the non-fan the other way twice, so they part at
    n = 10, the fourth new distinction (the values `KNOT-CAP`'s referee computed).
- **Two layers** (post hoc, computed). The prediction that the growth's branching depends only on which knots share a pair failed.
  What holds instead, for every presentation of 5, 6 and 7 distinctions: the number of labelled bases at each new distinction and
  how much weight has a new distinction whose odd set has five members depend exactly on the meeting pattern itself, read as an
  abstract pattern (which knots share which distinctions, up to renaming, the line ignored). Each meeting pattern has its own
  values (1, 3 and 4 patterns for n0 = 5, 6, 7), whatever its bracketing. *Narrowed after the referee:* one size past (eight
  distinctions, to n0 + 3) every pattern still has one set of values, but the 12 patterns share 8, so these counts do not tell
  every pattern apart; the patterns' laws of growth do (`MEET-GROW-20261118-001`, P2). So how the knots meet works twice:
  - the meeting pattern alone decides how the growth branches;
  - the same pattern placed against the line (the bracketing) decides how many orders the branches carry.

  The five-starts are one meeting pattern placed three ways, so they branch alike and differ in orders. The fan and non-fan of
  six are two meeting patterns placed alike (both chains), so they branch differently (13,368 against 13,364 labelled bases at
  n = 10) and agree in orders through n = 9.

**In the owner's terms.**
- How the knots meet is information the states do not hold, and now we know which: which knot lies within which. The line's
  states are the same for every presentation; the knots nest differently along it.
- One knot's growth makes two orders. A second growth within one of the first knot's halves makes a third; a second growth on steps
  the first does not touch keeps two. So the more the knots nest, the sooner a third order comes; a chain of knots, the most
  nested, loses two orders fastest.
- Whether the shared distinction sits at an end or next to an end does not matter at first, since both make a chain. Which way the
  chain lies matters only from the fourth new distinction.
- The knots' meeting pattern by itself decides how the growth can branch; where it sits against the states decides how many orders
  the branches make. Both are parts of how knots meet.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 15 gate checks pass | held | all pass before the freeze |
| Q1 | Lemma B and Theorem 1 on every bracketing with n0 = 4 to 11, every first knot | held | 6,916 of 6,916 bracketings (2, 5, 14, 42, 132, 429, 1,430, 4,862); Theorem 1 is now proved |
| Q2 | At n0 + 3 the distribution depends only on the bare bracketing (n0 = 7, 8, 9) | held | also n0 = 5, 6; 0 bare bracketings with two distributions |
| Q3 | At n0 + 3 different bare bracketings differ (n0 = 7, 8, 9) | held | 6, 11 and 23 distinct |
| Q4 | At n0 + 4 every two non-mirror presentations differ (n0 = 7, 8) | **failed** (n0 = 8) | 22 of 22 at 7; 65 of 66 at 8 (one tie); reported at 9: 193 of 217 |
| Q5 | Fewest-knot presentations = bracketings (n0 = 5 to 9) | held | 5, 14, 42, 132, 429 among 36 to 25,401,600 candidates; proved in A |
| Q6 | The chain is the unique least of Theorem 1 (n0 = 5 to 13) | held | 5/12, 51/140, 13/40, 37/126, 15/56, 65/264, 41/180, 303/1430, 61/308 |
| Q7 | Lemma C = the measured two orders on every labelled fills-only base | held | 125,765 bases, no disagreement |
| Q8 | Labelled counts and odd-set mass depend only on the pair-sharing tree, and trees differ | **failed** | the counts follow the tree through n0 + 3, but the weights do not: within the path tree of six two values at n = 9 (1121/54810 against 1189/58590) and of seven three at n = 10; post hoc they follow the meeting pattern exactly |

6 of 8 held, with the proof's finite check and both bare-bracketing predictions among them. The tie at n0 = 8 is between
(x,((x,(x,x)),(x,(x,x)))) and (x,(((x,x),x),((x,x),x))) (bracket strings, step first): the knot holding two chains of two, each
pair of bits swapped between them.

**Post hoc reads** (not predictions; scripts in the code directory).
- *Where the five-start chains part* (`posthoc.py`). Branch by branch, with the same first two fills, the end and next-to-end
  chains give the same chances of two orders at n = 7 and 8, and part at n = 9: most in the branch that fills the innermost knot
  first and then re-brackets it with the knot holding it (9/1846 against 6/1846 in each of its two sub-branches).
- *The meeting-pattern grouping* (`posthoc_meeting.py`), above.

## What the knot picture explained

- **Why the middle placement keeps two orders more often.** Its two inner knots are step-disjoint, so filling one and then the
  other keeps two orders; a chain has no step-disjoint pair at all (s(κ) = 0 everywhere).
- **Why the end and next to an end agree for three new distinctions.** Lemma C reads the number of orders from which fills'
  middles lie between which fills' ends. Swapping the two halves of a knot moves the middles but, through three fills, never
  changes how many pairs nest (computed; a proof is open).
- **Why the knots matter at all under KF3.** Knot-locality allows a fill only where three distinctions share knots pairwise, and in
  a bracketing those triples are exactly its knots, so the first fill is a knot and the second is a knot or a re-bracketing of
  the first with a neighbour. A rule that reads only the states could fill any of the C(n, 3) triples.

Known mathematics, labelled: triangulations, bracketings and binary trees (Catalan); lattice dimension by chains of splits
(Eppstein 2005); rotations of binary trees (Sleator, Tarjan and Thurston 1988). *Added after the referee:* the count n − 2 matches
phylogenetics, where every rooted binary tree on n leaves is defined by n − 2 rooted triples and all minimal defining sets have
that size (Steel; characterised by Grünewald, Steel and Swenson 2007); the object differs, since there one tree has many minimal
triple sets and here one line has many minimal presentations, exactly its triangulations. It also differs from order-theoretic
betweenness (Opatrny 1979), where the n − 2 consecutive triples fix the order: in this semantics they do not present the line's
states (B(0,1,2) and B(1,2,3) allow 0110). What this view adds: the states hold the line, and how its knots meet is a
triangulation the states do not show, which the growth reads through co-knotted pairs. Local: Lemma 0's characterization of
betweenness presentations of the cuts (proved here, not found in the literature so far), Lemmas A to C for KF3, Theorem 1, and
the census.

An observation on the earlier design: `KNOT-CAP-20261117-001` chose the five-starts as "the closest five-distinction analogue of
the fan and non-fan". The two comparisons are of opposite kinds. The fan and non-fan of six are two meeting patterns with one bare
bracketing; the five-starts are one meeting pattern with two. That is why the first agreed in orders and the second did not.

## What it means for A97 and the goals

- **A97** stays under challenge, with its sharpest positive finding so far. Information that is not in the states, how the knots
  nest along the line, changes how many orders grow, by an exact formula. The meeting pattern by itself changes how the growth
  branches. Whether that information is a distance is open: the bracketing is read from the states' disagreement counts (the line)
  together with the knots, and the states alone do not give it.
- **G16** (learning the rules behind what a system allows): capability gained. The distribution of the number of orders after the
  second new distinction is predicted exactly from the bracketing (proved), and through the third from the bare bracketing
  (computed, every presentation of 5 to 9).
- **G1** (space from a law): obstruction learned. Under KF3, nesting is what makes a third order. Even the least nested bracketing
  keeps two orders after the second new distinction with chance under 0.64 for every n up to 12, and the chain about 3/n.

## Limitations

- Fewest-knot presentations of a line, betweenness knots, and one rule (KF3); other knot kinds and weightings are untested. Extra
  knots matter (the referee): one redundant knot changes the second-step chance in all 21 cases tried and mixes the placements,
  so the bracketing account is a statement about fewest-knot presentations (A100).
- The proof covers the first two new distinctions. The third-step blindness and the fourth-step order are computed, exact, for
  every presentation of 5 to 9 distinctions only.
- The meeting-pattern layer is post hoc and covers 5 to 7 distinctions here; that the pattern decides the branching holds one size
  past (the referee, and `MEET-GROW-20261118-001` to nine), that each pattern has its own counts does not.
- Ties at n0 + 4 from n0 = 8 show the fourth-step distribution sees the bracketing's order only partly; what it sees is open.


## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh exact code (nothing imported from
`melib.py`): confirmed with fixes, no Block.
- Lemmas 0, A, B and C and Theorem 1 hold, checked by hand. The referee's own engine reproduces Theorem 1 on every bracketing of 4
  to 9 distinctions (624) and on 200 random bracketings each of 10 and 11 and 120 of 12, the five-starts to the last digit, the
  n0 = 8 tie (identical through n = 12, 34,520 labelled bases each), the six-starts' labelled counts, and the KNOT-CAP correction.

Folded in the same day, each item logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing** (of a post hoc reading). That the meeting pattern decides the branching holds one size past (12 of 12 patterns of
   eight have one signature), but "each pattern has its own values" fails there (12 patterns, 8 signatures).
2. **Not a block, but material** (A100). One redundant knot changes the five-starts' chance at n = 7 in all 21 cases, by 0.04 to
   0.33, and values cross between the placements (371/600 and 1523/2352 occur for chains and for the middle). The bracketing
   account is about fewest-knot presentations.
3. **Not a block** (wording). "The knots nest" is the reason, proved at the second new distinction, computed through the third
   (5 to 9 distinctions), and not the whole reason from the fourth, where the halves' order enters and ties appear. The intuition
   entry now marks the third-step clause as computed.
4. **Not a block** (the proof). Lemma B's proof now covers the case where the compressed line has three distinctions (a = 0, b =
   m, only κ's and q's pairs used): the line of three's cheapest second step costs 2, so it has no zero-cost option and nothing is
   missed (the referee's check); and the pull-back says that q's pairs are not chords.
5. **Not a block** (literature). Steel and Grünewald–Steel–Swenson for the n − 2 count, and the difference from order-theoretic
   betweenness, cited once with what this view adds.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: why the shared distinction's place changes the number of orders | **Status:** Successful (refereed R1, confirmed with fixes) | The bracketing decides it: an exact formula after the second new distinction (proved), the bare bracketing through the third (computed to 9); 6 of 8 predictions held |
| Local direction: how knots meet, read against the states | Continue | Two layers found: the meeting pattern decides the branching (post hoc), its placement the orders |
| Broader exploration: what in how knots meet is information | Searching | Whether the bracketing or the meeting pattern is a distance (A97) is open |
| Long-term goal: G16 Learning the rules behind what a system allows | Capability gained | The order distribution predicted exactly from the bracketing; G1 Space from a law: obstruction learned (nesting makes the third order) |

The attempt leaves the third-step blindness and the two layers without proofs, and the fourth step's order only partly read (ties
from n0 = 8).

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The two layers: does the meeting pattern alone decide how KF3 branches at every new distinction, and why? | 3/3 | 2/3 | Freeze the post hoc reading as predictions on unseen sizes (8 to n0 + 3, 7 to n0 + 4, 6 to n0 + 5), then seek the map that carries one placement's options to another's → stop at a proof, a counterexample or a size where it fails | Selected · started |
| 2 | A rule that keeps two orders by reading the bracketing: fill only knots step-disjoint from every earlier fill, or re-bracket through the knot holding one (Lemma C); does it grow two orders without end? | 3/3 | 2/3 | Run it exactly from every presentation of 5 to 8 and sample to n = 30 → stop when it stalls, adds a third order, or grows a two-order base to 30 | Alternative · deferred (independent; a parallel thread) |
| 3 | Prove the third-step blindness: a re-bracketing bijection of histories that keeps Lemma C's verdict | 2/3 | 2/3 | Classify the third step's options as Lemma B does, with the odd sets of five → stop at a proof or the first failing history | Alternative · deferred |
| 4 | The fade after erasure (KNOT-CAP's third direction) read through the two layers: does the meeting pattern or the bare bracketing set its rate? | 2/3 | 2/3 | Exact erased distances from every presentation of six to n = 11 → stop at a rate law or its failure | Alternative · deferred |

- **#1.** Payoff: it would show how the knots meet, with no states at all, governing the growth, the cleanest form of A97's
  question. Concreteness: exact and computed for every presentation of 5 to 7, but post hoc and with no mechanism yet; the main
  uncertainty is whether it survives one size past. Connection to the goal: G16 and A97. Bound: one frozen census of the same
  size as this run (under an hour) before any proof attempt. Started: the reading and its scripts are in this record.
- **#2.** Payoff: a rule that grows two orders and keeps them is G1's open target, and Lemma C says exactly which fills keep them.
  Concreteness: the rule is defined, but whether it stalls is unknown, and it reads the line's order through the bracketing. It
  shares nothing with #1, so it can run in parallel; filed as sub-goal B197.
- **#3.** Payoff: a theorem for why the six-starts agree through n = 9; it explains rather than extends. Concreteness: the
  advisor's sketch has a gap at the odd sets of five.
- **#4.** Payoff: the owner's erasure question, with a candidate mechanism. Concreteness: exact code exists (KNOT-CAP's) and this
  study's engine is faster; the rate is a guess.

**Corrections:** one, Not a block: `KNOT-CAP-20261117-001` said the five-starts "differ in the number of orders from the first
fill"; after the first fill both have two orders with chance 1, and they differ from the second new distinction (n = 7). Logged in
`docs/CORRECTIONS.md` and knotlab's `HISTORY.md`.

**Goals:** a G16 checkpoint (capability gained) and a G1 checkpoint (obstruction learned); no goal changed. Direction #2 filed as
sub-goal B197 of G1.

**Assumptions:** A97 under challenge, with this positive finding added; new entry A100: fewest-knot presentations as the population
for comparing how knots meet (Assumed); A99 gains this study among what rests on it.

**Basket:** read (holes-and-proofs); KNOT-CAP#2 taken by this epic.

## Reproduce

```sh
cd experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census
../../../.venv/bin/python -B checks.py                       # 15 gate checks
cd ../../..
.venv/bin/python -B scripts/longrun.py launch experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/job.py \
  --out <dir> --unit <name> --workers 12 --case-timeout 7200 --case-mem 1G --mem-max 16G
.venv/bin/python -B experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/merge.py <dir>
cd experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census && ../../../.venv/bin/python -B posthoc.py
```

## Advisor

Consulted twice before the freeze (Fable 5.2, no tools).
- The first consultation checked the analysis and found the hole in the proof's pull-back: a knot set classified in a small
  presentation must use all three pairs of a knot of the big one (now recorded by the finite check). It gave the agreement-form
  proof that every fewest-knot presentation is a bracketing, the parity form (odd sets), the two-order criterion (Lemma C), the
  probabilities for Q1 to Q5, the advice to state Q4 for finite sizes only (it expected ties among long chains), the literature
  pointers, and the words (it proposed "separate", which the glossary already uses, so "step-disjoint" was chosen).
- The second was asked about Q8 and the third-step blindness. It put Q8 at about 75%, proposed a twist (re-gluing along a
  shared pair) as the symmetry behind it, and a sketch for the blindness with a gap at the histories that hold an odd set of five.
- Not consulted after the read-out.

## Final report as sent

Posted in the project thread at 03:18 UTC on 18 November 2026 (the two tables and the Corrections, Goals and Assumptions lines are
those of the Position section above). Its text:

> **Done (referee pending): the knots' nesting is the reason, and the second fill now has a proved formula.** Every fewest-knot
> presentation of a line is a bracketing: each knot lies within one half of another, starting from the knot that holds both
> ends. A fill makes its knot's halves cross. A second fill inside one of those halves adds a third order; one on untouched steps
> keeps two. That gives an exact formula: 5/12 for chains, which are the end and next-to-end placements, and 11/18 for the middle
> placement.
> - Next to an end equals the end through n = 8 and parts at n = 9, because its chain lies the other way.
> - The six-starts are both chains: 51/140 at n = 8, equal through n = 9, parting at 10. Same mechanism.
> - Post hoc: the meeting pattern alone, with the line ignored, decides how the growth branches. Its placement along the line
>   decides how many orders the branches carry.
>
> (Position table and directions table as above, with the directions shortened.)
>
> What failed: at the fourth new distinction, presentations with different nestings can tie (one pair at eight distinctions, 24
> at nine). Branching does not follow which knots share pairs; it follows the full meeting pattern.
>
> Corrections: one, Not a block. KNOT-CAP said the five-starts differ "from the first fill"; they differ from the second new
> distinction. Fixed and logged. Goals: G16 and G1 checkpoints; no goal changed; B197 added as a sub-goal of G1. Assumptions: A97
> stays under challenge, with this finding added. New A100 records fewest-knot presentations as the population, set by default.
> Advisor: consulted twice before the freeze. It supplied the converse proof, the two-order criterion and the words, and flagged
> the hole in the proof's compression step, now closed.
