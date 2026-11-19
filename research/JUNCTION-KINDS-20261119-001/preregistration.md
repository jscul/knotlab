# Pre-registration: a transfer between kinds of junction

Epic `JUNCTION-KINDS-20261119-001`, ticket `JUNCTION-KINDS-20261119-001B`, 19 November 2026, by Claude, on the coordinator's
go-ahead after `BREAK-EDDIES-20261119-001`'s referee verdict (taking `JUNCTION-MAP-20261119-001#1`). Goal G17.

## The question

The break-shape eddies grow at rates of the catalogue's family, but the cluster rule's cover is wrong for them
(`JUNCTION-MAP-20261119-001`). The direction asked for a finite set of kinds of junction whose counts follow a fixed matrix, each
junction shared 1/p among its p parents. It starts on the ten starts whose round-weight, read from every factor of the counts'
minimal recurrence (the referee's divisibility test), is W = y²(1 + y): their counts satisfy c(t) = c(t − 2) + c(t − 3).

## Pilot (disclosed)

On one start of the ten (population index 28) and the catalogue's five eddies, before this freeze:
- A round's largest parent count and fresh count grow by about one every three rounds, in the catalogue's eddies too; local labels
  refined by neighbours' kinds (depth 0 to 3) grow per round; forward kinds by multisets of shares grow per round.
- On index 28: distinct out-shares per round 4 → 88 in 18 rounds; sum-equitable kinds 7 → 133; the spine relation at lags (2, 3)
  has a perfect matching at rounds 4 to 16; its single-chain version does not; no set of up to 3 of the 10 most frequent interval
  types is biregular on the first half.
- The catalogue's counts carry a constant part (a factor x − 1 in their recurrence), so their spine test saturates the smaller side
  instead.

## Words

- The **out-share** of a junction j is s(j) = Σ over its children c of 1/p(c).
- **Sum-equitable kinds** (forward): kind_0 is one kind, and kind_h(j) is the map from kind_{h−1} classes to the total share j sends
  into each. Depth 6, on junctions whose futures reach it.
- An **exact per-junction transfer** is a partition of the junctions such that every junction of class l sends total share
  M[k, l] into class k. Then s is constant on each class (the advisor's statement, checked), so if s takes infinitely many values,
  no finite partition is one. Class totals can still follow a finite matrix on average: the substitution a → b, b → c, c → ab has
  characteristic polynomial x³ − x − 1.
- The **spine relation** at lags (l1, l2) relates a junction of round t to its ancestors exactly l1 or l2 parent steps up. Its
  **single-chain** version keeps only ancestors reached by one chain. The **interval type** of an ancestor a of j is the unfolded
  chain structure of [a, j]: depth 0 is (), and depth k is the sorted tuple of the types of [a, p] over j's parents p reaching a.
- A **native spine** is a set T of interval types for which the relation is biregular with one constant e on every round: every
  junction of round t has e T-ancestors, and every junction of rounds t − l has e T-descendants in round t.

## Population

30 starts (`job.py`), one case each:
- **T:** the ten (population indices 28, 44, 52, 55, 56, 58, 61, 65, 66, 68), lags (2, 3), 26 rounds or 40,000 junctions.
- **Q:** the fifteen whose corrected W is y⁴(1 + y)², with the same rate but another W, lags (2, 3) for the count check.
- **C:** the catalogue's five minimal eddies, each with its own lags from its W, read by the same divisibility test: C-0 and C-1
  y⁵(1 + y), C-2 and C-3 y⁷(1 + y), C-4 y⁴(1 + y). They grow to 40 rounds.

## Predictions (frozen; scored by `merge.py`)

| # | Prediction | Falsified by |
| --- | --- | --- |
| J1 | (the cheapest discriminator) out-shares are unbounded: in all 30 starts the most distinct out-shares in a round of the last third of the window exceed the most in the first third | one start where they do not |
| J2 | the coarsest exact transfer grows too: sum-equitable kinds per round, by the same thirds, in all 30 | one start where they do not |
| J3 | the counts can be carried by ancestry: in T, at every round from 4 on, the recurrence holds and the spine relation has a perfect matching; in C, a matching saturates the smaller side at every round past the lags | one round without it |
| J4 | (risky) no native spine of interval types: in none of T does a set of up to 3 of the 10 most frequent types make the relation biregular on both halves of the rounds tested | one start with such a set |
| J5 | the controls separate by count: in T, d(t) = c(t) − c(t − 2) − c(t − 3) is 0 from round 4; in Q, d is not identically 0 and satisfies d(t) = −d(t − 2) − d(t − 3) from round 9 | one start that differs |

Readouts: the single-chain matching per round, the number of interval types, and the type sets biregular on the first half.

## What would follow

- J1 and J2 holding: the direction's second stop case, kinds that never settle. No finite partition of junctions carries an exact
  transfer, here or in the catalogue's eddies, where the cover gives an exact one.
- J3 holding and J4 holding: ancestry can carry the counts, but not by any fixed set of local interval types up to the size
  searched. The finite object is then not a kind of junction or a typed spine.
- J4 failing would give a native spine, the advisor's candidate, and a bijection behind c(t) = c(t − 2) + c(t − 3).

## Prior work in the program

`python3 -B scripts/track.py objects "transfer kinds of junction spine ancestor out-share equitable partition substitution" --until 2026-11-19 --exclude JUNCTION-KINDS-20261119-001`

- `JUNCTION-MAP-20261119-001`: the junction map, the direction's source.
- `BREAK-EDDIES-20261119-001`: the population and the corrected W table.
- `RING-PAIR-20261119-001`: the cover model, junctions as connected sets of t + 1 points.
- `PARENT-RULE-20261119-001`: complete rounds peel back exactly, a related property of parents.
- `ADDR-KNOTS-20261113-001`, `ROUND-FREE-20261119-001`, `EARN-BUDGET-20261117-001`, `MEET-TRANSFER-20261117-001`,
  `AGENT-LOOP-20261117-001` and `LOOP-CATALOGUE-20261119-001`: the same words, other objects (the catalogue gives the controls).

**Known, cited once.** Equitable partitions and their quotient matrices (graph theory); substitutions and their matrices (the
Padovan substitution a → b → c → ab); Hall's marriage theorem and Hopcroft–Karp matching.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before this freeze. Adopted: the out-share argument and its cheapest test (J1), the
sum-equitable refinement (J2), the Hall test (J3), the spine by interval types (J4) and the controls (J5). Checked: the
substitution's characteristic polynomial (x³ − x − 1) and the Q control's d recurrence (x⁶ − (x + 1)² = (x³ − x − 1)(x³ + x + 1)).
Not adopted: running the spine on the catalogue's eddies with their own exponents, which the constant part of their counts rules out.

## Runs and stop rule

One frozen run through the shared runner (`JUNCTION-KINDS-B1`, `runs/junction-kinds`). Stop at the five verdicts.
