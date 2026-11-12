# Which loops lock

Epic `LOOP-LOCK-20261112-001` (`ENDLESS-BLOCK-20261112-001` direction 1; G17 with G8; program mathematics, group arithmetic),
2026-11-12, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `36fd0e934`.
Proof family: `proofs/LOOP-LOCK-20261112-001A/`. **Referee pending.**

## The question

Endless blocks stitched in one order showed loop-born locking. Which loops lock, can the open chain's freedom be proved at every length,
and, for the owner's "meeting patterns that fold in complex ways and are globally influential", what do overlapping loops do?

## The answer

**A loop locks exactly when it is shorter than the shortest round trip of the step between two stitched copies; an open chain never
locks; and overlapping loops can lock together, in ways that depend on how they overlap and, on rings, on the arithmetic of their
length.**

- **The rule (proved; 495 of 495).** Drop each loop's hanging copies: two stitched copies are then joined by one step relation, which
  can always stay put. A loop of k knots is a round trip of k steps, so it locks every copy into one state exactly when the relation has
  no other round trip of k steps or fewer. An open chain of any length is free whenever one step exists. For harmonies that are shifts
  of one word, the shortest round trip is a zero-sum question on their period.
- **Overlap through one copy changes nothing (proved; 75 of 75).** A loop's lock does not cross a single shared copy.
- **Through a shared knot, a lock spreads but is never created (proved; 75 of 75).** A loop that fails alone is locked by a loop that
  locks and shares a knot with it, when the leftover path is short enough; two loops that both fail alone never lock through a knot.
- **Through two shared copies, loops lock together (exact).** Two loops sharing two copies and no knot, each failing alone, lock as a
  pair for both harmonies with round trips of 4; and the circulant patterns (copies stepped by 1 and by 2) lock collectively in 7
  cells, once strictly, with no round trip shorter than the harmony's.
- **Rings of overlapping knots lock by arithmetic (exact).** On the one-shift ring, where each knot shares two distinctions with the
  next, whole rings lock even for harmonies whose simple loops never lock, and whether they do depends on the ring's length against
  the period: 0011 locks rings of 5, 6, 7, 9, 10, 11 and not of 4, 8, 12.

## Bounded by the period, or at every size? (after the run; the coordinator's question)

- **Single loops: bounded.** A loop locks only below the girth, and every girth is at most the period (a step that shifts the phase
  winds back after at most P steps).
- **Collective locks through two shared copies: bounded.** The crossed pair needs its paths shorter than the girth; the circulant locks
  for one step offset exactly when ⌊n/2⌋ < g (the advisor's proof), so it stops before 2g ≤ 2P copies.
- **Rings of overlapping knots: for some harmonies, at every size in a residue class.** A ring of n knots is a closed walk of length n
  of the transfer on pairs of states, and it locks exactly when no such walk leaves the diagonal (descriptive, `after_run_rings.py`,
  n to 60). Then: 0011 locks every ring whose length is not a multiple of 4; 00001111 every length not a multiple of 8; 00101101,
  001010110101, 00100101101101 + 01 and 0010101011010101 every odd length; 0010011011, 00101101 + 0011 and the alternation every length
  from 3 to 60. Others lock at finitely many lengths only (000111 at 4 and 7; 0011 + 01 at 5; 0000011111 at 3, 4, 6, 8, 11, 13). So
  dense overlap gives locking that is not bounded by the period: it holds at every size the residue class allows.
- **Known mathematics.** Ring states are the periodic points of a one-dimensional shift of finite type whose symbols are the
  harmony's states; which lengths have a non-constant periodic point is fixed by the cyclic (Perron–Frobenius) periods of the
  off-diagonal part of the transfer (Lind and Marcus). The residue classes are an instance of that, and novelty is not claimed for the
  mechanism; the harmonies' own lists are new data. The same applies to single loops (closed walks of a reflexive transfer) and to the
  overlap rules (homomorphisms into a reflexive digraph; tree networks globally consistent; cycle against cover), as the endless-blocks
  referee found for its loops.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| A loop of k knots locks iff k < girth; open chains free at every length; one-orbit girth is a zero-sum length | proved by hand (with the advisor model); exact on 495 + 495 cells |
| Figure eights independent; through a shared knot, locks spread and are never created | proved (the advisor's); exact on 75 + 75 cells |
| Collective locks through two shared copies; rings lock by the arithmetic of their length | exact on the range |
| Which ring lengths lock, to 60: residue classes at every size for some harmonies, finitely many for others | descriptive, after the run |

## Against the pre-registration

Every theorem check held (L1, L2 on 495 cells each; figure eights and thetas 75 of 75); the crossed pair locked on both harmonies with
g = 4 (predicted 95%); a strict collective lock appeared at n = 2g − 1 (for a multi-orbit harmony); the one-generator case at
n = 2g − 1 was out of the frozen range (n ≤ 9 against 2g − 1 ≥ 15); rings were non-monotone (predicted 65%); the nestings' tie share
was zero except for the alternation, whose share fell (0.40, 0.29, 0.20) rather than settled (60%: not met as worded). The control
held. Both parts inside their caps.

## What it changes

- **For the owner's "globally influential".** Influence through loops has a precise anatomy: it stays inside a loop shorter than the
  harmony's round trip, does not cross a single shared copy, spreads across a shared knot from a loop that locks, and can arise from two
  loops together only when they share more than a knot. Where knots overlap densely, as along a ring, the whole pattern locks or not
  by its length's arithmetic. How the pattern folds decides it.
- **Prior work.** The rule is the girth of a reflexive digraph and a zero-sum length; tree networks are globally consistent (path
  consistency); local consistency cannot tell a cycle from its cover. Novelty is not claimed for the rule.

## Assumptions

A70 used; A75 (Assumed): these are stitches, its own reading.

## Corrections

None.

## In the owner's words

Tie endless patterns to each other one way round, and a closed loop of ties locks every pattern on it into step when the loop is
short enough, while an open line of the same ties never locks. Two loops touching at a single pattern don't affect each other; loops
sharing a tie pass a lock along; loops sharing two patterns can lock each other even when neither would alone; and a ring where each
tie overlaps the next locks or not depending on how its length fits the pattern's period. So the shape of the overlaps decides how
far the influence goes.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which loops lock | **Status:** Successful, referee pending | rule proved; overlap anatomy mapped |
| Local direction — nesting | Continue | rings lock by arithmetic not yet explained |
| Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random bases |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | how overlapping loops carry influence, natively |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why rings lock by arithmetic | 2/3 — Substantial | 2/3 — Testable | the ring's transfer on pairs of states (the advisor's): closed walks of length n that leave the diagonal → a rule in n and the period, or a counterexample | Selected · awaiting go-ahead |
| 2 | Collective locks at scale | 1/3 — Incremental | 3/3 — Ready | circulants to n = 2g − 1 for the one-generator harmonies (15, 23, 31) → the advisor's strict lock, or not | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained, with G8; no goal change). **Assumptions:** A70 used, A75 unchanged.
**Basket:** #1, #2 recorded. **Advisor:** consulted once before the freeze (L1 to L3's checks, the overlap facts, the crossed pair and
circulant, the criteria).

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 09:54 UTC, verbatim:

> Done: which loops lock. The write-up is research/LOOP-LOCK-20261112-001/loop_lock.md. The referee is pending.
>
> • **The rule (proved; 495 of 495).** Between two stitched copies there is one step relation, and it can always stand still. A loop of k knots locks every copy on it exactly when that relation has no round trip of k steps or fewer. An open chain never locks, at any length.
> • **How overlaps carry a lock (proved and exact).** A lock never crosses a single shared copy. Across a shared knot it spreads from a loop that locks to one that doesn't, but two failing loops never lock that way. Through two shared copies, loops that each fail alone can lock together.
> • **Bounded or at every size?** Single loops and collective locks are bounded: they only work below the girth, which is at most the period. Rings where each knot overlaps the next in two places are different. There, some harmonies lock at every size in a whole arithmetic class (computed to 60). For example, 0011 locks every ring whose length isn't a multiple of 4, and four other harmonies lock every odd ring.
> • **Prior work.** All of these mechanisms are classical in kind: closed walks of a transfer relation, periodic points of shifts of finite type, homomorphisms into reflexive digraphs. I'm not claiming novelty, only the harmonies' own data.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — which loops lock | **Status:** Successful, referee pending | rule proved; overlap anatomy mapped; known mechanisms |
> | Local direction — nesting | Continue | why the rings fall into residue classes |
> | Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random bases |
> | Long-term goal — G17 Typical and rare meeting patterns | Capability gained | how overlapping loops carry influence, natively |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Why rings lock by arithmetic | 2/3 — Substantial | 2/3 — Testable | read the period structure of the pair transfer for each harmony → a rule from the harmony to its residue classes | Selected · awaiting go-ahead |
> | 2 | Collective locks at scale | 1/3 — Incremental | 3/3 — Ready | circulants up to n = 2g − 1 for the one-offset harmonies → the predicted strict lock, or not | Alternative · deferred |
>
> **Corrections:** none this epic. Separately, I folded in the referee's verdict on endless blocks with one Narrowing: only loops shorter than the girth lock, and longer loops don't. **Goals:** G17 checkpoint, no goal change. **Assumptions:** A75 unchanged. **Basket:** #1, #2 recorded. **Advisor:** consulted once before the freeze.
