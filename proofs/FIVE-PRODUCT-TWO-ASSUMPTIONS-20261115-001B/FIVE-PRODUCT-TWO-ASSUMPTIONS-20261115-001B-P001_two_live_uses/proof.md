# Paying for both premises of a reused deduction

Status: Proved

## Standard statement

On six input bits put \(Q=\sum_{i=0}^4 x_i x_{i+1}\) over \(\mathbb F_2\). The rich evaluator requires \(s=Q,\ u=x_0x_1,\ v=x_2(x_1+x_3)\). The plain evaluator requires \(s=1+Q\) and leaves both summaries free. This is the fixed pair of masks \((1,6)\). The only visible coordinates are \((x_0,\ldots,x_5,s,u,v)\). A binary question about any affine parity, a check of one evaluator, and a citation each cost one. A check under raw affine assumptions \(C\) replaces them by \(\operatorname{aff}(C\cap D)\) for that evaluator's set \(D\). Discharge and affine consequences of established assumptions have no additional cost.

For either \(a\in\{0,1\}\), train the single statement

\[
         (x_2=a,\ v=0)\quad\Longrightarrow\quad x_0=0.
\]

**Training costs exactly five. The same five operations also train the one-premise rule \(x_2=a\Rightarrow x_0=0\).** Consequently neither selected two-equation guard can improve the best 23-unit proof, even with all 511 visible affine questions and arbitrary citation placements. Each claimed use of the two-premise rule still has to establish both of its own premises.

There are explicit certificates that cite the same learned statement on two incomparable, still-live branches. For \(a=0\) one costs **31** and for \(a=1\) one costs **35**. These are exact repeated-use minima in the 14-question menu specified below. The comparison is also tight on how many live uses a single proof can contain, with maxima **four** and **two** respectively, even when every visible parity is available. [Programs](certificates.json) · [Numerical evidence](checks.json)

## Nearest known result

The preceding study proves that the ordinary tree costs 23 and that at most one stored implication from one affine equation to one affine equation still costs at least 23. It trained \(v=0\Rightarrow x_0=0\) for seven units and exhibited uses below two live contexts distinguished by \(x_2\). The present question fixes one of those \(x_2\) values as a prerequisite of every citation. Here training is cheaper, and establishment of the new raw prerequisite is charged explicitly. [Single-equation theorem](../../FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/one_premise.md) · [Previous named-literal training](../../FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/sector_proof.md)

## Five operations suffice with one premise

Train by refuting the countercase \(x_0=1,x_2=a,v=0\). Ask \(x_4=c\). At either answer,

\[
        Q=x_1+a(x_1+x_3)+c(x_3+x_5)
\]

is affine. The rich check gives \(s=Q\). The plain check then returns empty, for five operations in the complete binary proof. The identity holds for both values of \(v\), so the identical proof works from \(x_0=1,x_2=a\).

The lower bound already holds in the two-premise countercase. Set \(x_1=x_3=u=v=0\) there and leave \((x_4,x_5,s)=(y,w,p)\) free. The two evaluators restrict to \(p=yw\) and \(p=1+yw\). Each set of four points spans all three bits. A useful first operation must be a question, and both answer cells contain rows from both sources. Each child therefore needs at least two units, giving five. This affine restriction pulls an arbitrary larger proof back at no greater cost. The checker tests both memberships on all eight image rows. Before specialization, the two-premise training case contains 16 rich and 32 plain rows for \(a=0\), and 8 rich and 32 plain rows for \(a=1\).

For any proof that trains the two-premise rule, substitute the five-unit proof of the one-premise rule. Every legal old citation still satisfies \(x_2=a\), the paid citation adds exactly the same \(x_0=0\), and all its raw assumptions remain in force. A more expensive old training derivation can only increase that difference. The predecessor's 23-unit lower bound for one single-equation implication applies to the resulting proof. The ordinary 23-unit tree remains available when training is optional. This argument treats each value of \(a\) as one fixed stored statement.

## Two genuinely live uses

Write \(A(C)\) for the greatest common fixed point of the separate affine-hull operations inside \(C\). At a citation the checker requires raw \(C\subseteq\{x_2=a,v=0\}\), some point of \(A(C)\) with \(x_0=1\), and nonempty \(A(C\cap\{x_0=0\})\). Thus both call sites use information that ordinary saturation leaves unresolved, and each still needs a continuation. The named proof is stored once. Structural child references are listed separately.

- For \(a=0\), ask \(x_2\). At \(x_2=0\) one rich check establishes \(v=0\). Ask \(x_1\) and cite the same stored statement under each answer. Each fixed set drops from 32 to 16 points. On either continuation asking \(x_4\) and checking rich then plain in each answer costs five. The opposite \(x_2=1\) branch has its own ordinary refutation.
- For \(a=1\), ask \(x_2+v\). A rich row with answer 1 must have \(x_2=1\), \(v=0\), and \(x_1=x_3\), since \(x_2+v=x_2(1+x_1+x_3)\) there. One paid rich check establishes all three affine equations. Again ask \(x_1\), cite in both answers and continue with \(x_4\). Both fixed sets drop from 16 to 8. The answer \(x_2+v=0\) has its own ordinary refutation.

| Single cached proof, used twice | Questions | Rich checks | Plain checks | Citations | Total | Specialized ordinary expansion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| \(a=0\), two guard equations established at common ancestor | 8 | 11 | 10 | 2 | **31** | 36 |
| \(a=0\), each branch establishes its guard after the common ancestor | 8 | 12 | 10 | 2 | **32** | 37 |
| \(a=0\), ask both displayed guard bits separately before branching | 9 | 11 | 10 | 2 | **32** | 37 |
| \(a=1\), two guard equations established at common ancestor | 8 | 15 | 10 | 2 | **35** | 40 |
| \(a=1\), each branch establishes its guard after the common ancestor | 8 | 16 | 10 | 2 | **36** | 41 |
| \(a=1\), ask both displayed guard bits separately before branching | 12 | 14 | 14 | 2 | **42** | 47 |

Each total includes training. The two certificates whose common ancestor establishes neither premise ask \(x_1\) first, then establish the appropriate guard independently under its two answers. Applying the conclusion once before that split costs 24 for \(a=0\) and 28 for \(a=1\). In these constructions, applying it on two branches saves five against its own ordinary expansion and costs seven more than applying it once before the split. The difference comes from the still-nonlinear third product, which now needs two continuations. [Raw assumption and cost verifier](replay.py) · [All branch instructions](certificates.json)

For exactly two live uses in the same answer to the first question, the lower bound of 31 holds even with every visible parity. Both unrestricted sources span the full space and the premise has codimension two, so the first useful main operation is a proper question. Its other answer contains an affine copy of the complete two-product-group problem, of ordinary cost 11, by the predecessor's untouched-group embedding. Each nonempty fixed point at a retained continuation costs at least five. Its two source sets span it and any useful question either splits it, leaving both source types in each answer, or preserves it for the continuation. Counting the five-unit training, the root question, the eleven-unit opposite branch, a question separating the two uses, two citations, and their two five-unit continuations gives 30. At equality the two raw children of the separating question would already entail both premises. Their union would be the entire first-answer hyperplane, which cannot fit inside a codimension-two guard. Thus another paid operation is necessary. The 31-unit program attains this bound for \(a=0\). The comparison here requires both citations to be live and to be the only two citations.

## Capacity for live uses

After saturating \(x_2=a,v=0,x_0=0\) the fixed set has 32 points for \(a=0\) and 16 for \(a=1\). In both cases the rich source forces \(u=0\). When \(a=1\) it additionally forces \(x_1=x_3\). On these resulting affine spaces the surviving checksums are the graphs of the remaining product \(x_4(x_3+x_5)\) and its complement, both spanning the spaces. Thus at a positive continuation the nonlinear work persists. The corresponding saturated countercases have sizes 32 and 16 as well.

Every nonempty common fixed point of these disjoint sources has dimension at least three. In dimension \(d\), each source needs at least \(d+1\) distinct points to span, and \(2(d+1)>2^d\) for \(d\le2\). Two live uses of the same consequence cannot be nested because after a citation \(x_0=0\) holds on all descendants. Incomparable use sites in a tree lie under opposite answers to some question. Their retained fixed points are therefore disjoint and each occupies at least eight points of the 32- or 16-point parent set. Four and two are the respective upper bounds.

Both are attained using true raw input questions. For \(a=0\) partition the guard by \(x_1,x_3\). For \(a=1\) partition by \(x_1\). In each part the saturated positive and counter-conclusion sets have eight points, with four rich and four plain rows in each. Each positive continuation costs exactly five there because asking \(x_4\) makes the remaining product affine. The four-use program for \(a=0\) costs 45. [Capacity and per-use counts](checks.json)

## Finite optimisation and negative controls

The coordinate menu uses just the nine displayed bits. The 14-question menu also admits all nonzero parities on the three affine observations \((x_2,x_1+x_3,v)\). On each reachable affine guard the ordinary dynamic program considers each proper question split and each strictly shrinking one-source check. An empty tested source costs one. For the two-premise rule, the second recursion compares those alternatives with a live paid citation wherever the raw guard entails both equations. After a citation the continuation is ordinary because the conclusion remains true. A question adds its two child costs plus one. If both children have uses, their common ancestor is the current guard and its two individual entailments are recorded. When the fixed point has no point of either \(G\cap\{x_0=0\}\) or \(G\cap\{x_0=1\}\), no smaller guard can yield a live citation. Every remaining transition reduces the affine-guard size. A separate recurrence counts the exact number of uses by summing over its possible splits between children.

| Menu and fixed value | No training | Exactly one live use | Exactly two | Exactly three | Exactly four |
| --- | ---: | ---: | ---: | ---: | ---: |
| Nine coordinates, \(a=0\) | 23 | 24 | 31 | 38 | 45 |
| Nine coordinates, \(a=1\) | 23 | 35 | 42 | impossible | impossible |
| Fourteen questions, \(a=0\) | 23 | 24 | 31 | 38 | 45 |
| Fourteen questions, \(a=1\) | 23 | 28 | 35 | impossible | impossible |

The two menus reach 33,715 and 81,874 raw affine guards respectively. Training counts once whenever a citation is used. The checker reconstructs every saved program, verifies each step on the original 512 visible words, and also replays it with the single-premise declaration. The finite menu optima above exclude nonlive citations. The 23-unit dominance bound allows them. [Dynamic programs](programs.py) · [Checking routine](check.py)

The two displayed requirements have separate tests. Removing the question about \(v\) from an explicitly guarded program leaves a live raw branch with \(x_2=a\) and an actual plain row with \(v=1\). Removing the question about \(x_2\) instead leaves \(v=0\) and actual rich and plain rows with \(x_2=1-a\). The raw verifier rejects both citations. In the training proof, removing \(x_2=a\) while retaining \(v=0\) also breaks the proposed five-operation proof. At \(x_4=0\) the plain word 13 survives the rich hull (the low bits represent \(x_0,x_2,x_3\)). Removing \(v=0\) from the training proof succeeds, as the explicit affine calculation predicts. Giving the two evaluators matching totals yields 64 full solutions and invalidates the refutations.

## Replay

From the repository root run

```sh
python3 -B proofs/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B-P001_two_live_uses/check.py
```

The checker emits the actual training, main and total costs, the operation that established each premise, fixed-point sizes before and after each call, both menu censuses and the rejected malformed proofs. [Numerical record](checks.json)
