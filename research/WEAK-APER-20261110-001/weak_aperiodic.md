# Weakly aperiodic laws under Leibniz's rule

Epic `WEAK-APER-20261110-001` (program topology, group `spacing`, `LEIBNIZ-BOARDS-20261110-001` direction 2, G1), 2026-11-10.
Pre-registered in commit 15131fc29, with ticket B's census frozen there.

## The question

- **Where it comes from.** `LEIBNIZ-BOARDS-20261110-001` proved that under Leibniz's rule, "names whose views agree at every radius
  are one place", a law's boards are the Schreier graphs of its solutions' stabilizers. It also proved the dichotomy W, an infinite
  board brings the tree, for every one-bit Life-like law. For arbitrary finite alphabets it reduced W to excluding one rigid kind of
  solution. Those solutions could only come from weakly aperiodic laws, which have solutions but no finite board. The owner's
  go-ahead of 2026-11-10 ("Yes, let's do that") took this direction.
- **The question.** Does a weakly aperiodic law still have a solution with trivial stabilizer, so that the tree is a board? And does
  W hold in general?

## The question in standard terms

Does every infinite shift of finite type on the free group F2 contain a point with trivial stabilizer? Which level laws on Z/3 are
weakly aperiodic?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Every infinite law has a free solution (Theorem W).** Every infinite shift of finite type on F2, over any finite alphabet and for any finite window, has a solution with trivial stabilizer. The same holds on F_n for n ≥ 2. | proved | A |
| 2 | **W and P in general.** Under Leibniz's rule the tree is a board exactly when a law has infinitely many solutions. So no law forces a single infinite board, and none forces the plane. Every infinite shift of finite type on F2 is uncountable. | proved | A |
| 3 | **Why there is no finite board.** A finite board exists iff the balance equations have a solution. Otherwise a potential on the values along edges makes every used pattern gain, and the gains cancel on any finite board. | proved; the criterion is known (Piantadosi 2008; Hellouin de Menibus and Maturana Cornejo) | A |
| 4 | **No finite board means a drift (found after the census).** A level law on Z/3 that has solutions has no finite board exactly when every pattern its solutions use has more neighbours one level up than one level down, or every one more down than up. | proved after the census; the census agrees exactly | A, B |
| 5 | **The census.** Of the 32,768 level laws on Z/3, 31 have no solution and 33 finitely many. 32,604 have a finite board with a free choice and 4 have finite boards without one. 96 are weakly aperiodic: 48 drift up and 48 down. Every verdict was re-decided exactly. | computed, exact, frozen | B, and A's check |
| 6 | **The frozen certificates were incomplete (C1 failed).** They decided 88 of the 96 weakly aperiodic laws and 2 of the 4 periodic ones without a free choice. The 10 left all contain (3, 0, 1), the mirror image of the horofunction pattern, and the mirrored horofunction gives each a free solution. C2 held. | prediction failed; settled by proof | A, B |

## Answer

Yes. Every law with infinitely many solutions on the tree has a solution that no element of the group fixes, so under Leibniz's rule
the tree is among its boards. The rule therefore never forces the plane, or any one infinite board, for any law with finite windows
over a finite alphabet. Weakly aperiodic laws are no exception. Their freedom runs toward ends of the tree, and an end that no element
fixes gives a solution that no element fixes. In the three-value family the only obstruction to a finite board is a drift, a law
under which every place climbs on balance.

## Reading

**Interpretation, not a theorem.**
- **Why the tree always comes back.** There are two ways for a law to leave freedom.
  - Free choices can sit in infinitely many disjoint branches. Then they can be made independently, so that nothing repeats.
  - The freedom can run out toward a few ends in each solution. Collected over all solutions, those ends form a closed set that every
    element maps to itself, and on a free group that set is every end. An end that no element fixes then carries a solution no
    element fixes.
- **A drift needs an infinite world.** On a finite board every step up along an edge is a step down from its other end, so the steps
  cancel. A law that makes every place climb on balance has an arrow, and an arrow cannot close up. Its solutions point toward an end,
  and the free ones toward an end no element fixes.
- **For the owner's idea.** Taking the identity rule to its infinitary limit does not let a value law choose the plane. The plane is
  still allowed often (891 of the 896 one-bit laws with a free choice, `LEIBNIZ-BOARDS-20261110-001`), but the tree is always
  allowed beside it. With names as words in two letters (A54), the tree is the naming's own shape.
- **Nothing here is a length.**

## Lag cutoffs and census-only claims

- **Exact.** Conclusions 1 to 4 are proved. Every census verdict is certified: each weakly aperiodic law by a potential, each law with
  a finite board by an explicit board checked place by place.
- **Census-only.** The counts of conclusions 5 and 6.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusions 1 and 2 (Theorem W) | — (a proof) | read by an independent referee before publication: no error (see "Review") |
| Conclusion 4 (drift) | — (proved for Z/3; on Z/4 the same argument gives a drift, since steps of 2 are their own reverse) | the census agrees, 96 of 96 |
| Conclusion 5 (census counts) | every verdict re-decided exactly, on tree patterns pruned by independent code | passed (88 s): 96 potentials, 32,604 boards (the largest 2,292 places), 4 boards with potentials |

## Review

An independent referee, a fresh Claude agent given only ticket A's proof, read it before publication on 2026-11-10.
- **Verdict.** No error in any target. It checked every step of Theorem W and tried to build an infinite law whose solutions all
  have nontrivial stabilizers: the horofunction law falls in Case II with one non-rigid end per solution, and a law of pointers
  toward a sink turned out uncountable, as the corollary says. Its own run over the 32,768 laws, with separate pruning and linear
  programs, agreed with the census and with the drift theorem.
- **Changes asked for and made.**
  - Target 6 was false as stated for a law with no solutions, which uses no patterns; it now speaks of laws that have solutions.
  - "No law forces one infinite board" needs Piantadosi's weakly periodic points when the board would be the tree; the corollary
    now says so.
  - Target 1 is known (Piantadosi 2008, Theorem 3.6; the Chazottes–Gambaudo–Gautero condition, proved equivalent by Hellouin de
    Menibus and Maturana Cornejo, arXiv 1904.03907) and is credited.
  - Several steps were written out: why no tail lies in another half-tree (Lemma A″), how a second completion extends, and why the
    non-rigid ends of a solution are finite in Case II.

## Literature and provenance

- **Sources.**
  - Shifts of finite type on free groups: Piantadosi (2008, and his thesis), every nonempty SFT has a weakly periodic point and some
    have no strongly periodic point; Cohen (2017), a group with two or more ends has no strongly aperiodic SFT; Carroll and Penland
    on weak and strong periodicity.
  - Stabilizers: Bitar (arXiv 2406.04132), which subgroups SFTs realize as stabilizers. Its Lemma 5.8 is the analogue on Z: a
    nearest-neighbour SFT has an aperiodic point iff it has points of infinitely many periods.
  - Tools: the Baire category theorem, König's lemma, Farkas' lemma, Busemann functions, minimality of a free group's action on the
    ends of its tree.
  - The finite-board criterion: Piantadosi (2008, Theorem 3.6); Chazottes, Gambaudo and Gautero; Hellouin de Menibus and Maturana
    Cornejo (arXiv 1904.03907, Theorems 3.5 and 3.11).
- **Classification.** Theorem W was not found stated (bounded searches, 2026-11-10, including Piantadosi's thesis, the papers of
  Cohen and Bitar, and the referee's own searches). The argument is short and uses standard tools, so the folklore risk is moderate;
  this is not a priority claim. Conclusion 3's criterion is known, and conclusion 4 is elementary.

## Workspace assumptions

- **Relied on.** A53 (nativeness counted per name) and A54 (two-letter naming), from `BOARD-DIST-20261110-001`.
- **Bearing on A51.** Its extension under Leibniz's rule now covers every law with finite windows over a finite alphabet, and its
  history records it.
- **Bearing on A54.** With this naming the tree is a board of every law with infinitely many solutions, so the challenge of A54
  (names without letters) is the remaining test of whether the obstruction belongs to the naming.
- **Added.** None.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (targets 1 to 6 and the exact check) and ticket B (the census).
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

Two, logged in `docs/CORRECTIONS.md`, both **Not a block**.
- **The census's exactness.** Ticket B's frozen contract says the balance program was "solved exactly in rationals by HiGHS".
  HiGHS works in floating point. Ticket A's check re-decided every verdict exactly, and all agree, so no result changes.
- **A known criterion.** Part 2 of Theorem 7 of `BOARD-DIST-20261110-001A` (view boards exist iff the class counts match) is the
  known periodic-point criterion for tree shifts (Piantadosi 2008; Hellouin de Menibus and Maturana Cornejo). That epic rated
  Theorem 7's folklore risk low to moderate. Credit changes; every result stands. Its decision note now says so.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — weakly aperiodic laws under Leibniz's rule | **Status:** Successful | W and P proved for every law with finite windows; every weakly aperiodic law of the family has free solutions, and drift is its only obstruction to a finite board; C1 failed, settled by proof |
| Local direction — the identity rule in the limit | Complete | Leibniz's rule never forces the plane, for any such law; nothing is left on this line |
| Broader exploration — question 9, boards made of distinctions | Known alternatives | Abstract names (A54), the boards beside the tree, accretion laws |
| Long-term goal — G1 Space from a law | Obstruction learned | With names as words in two letters, every identity rule tried leaves the tree open: the plane is allowed, never forced |

**Corrections:** two, both Not a block (the contract's "exactly in rationals by HiGHS", every verdict since re-decided exactly;
`BOARD-DIST-20261110-001A`'s view-board count is a known criterion).
**Goals:** a G1 checkpoint (obstruction learned); LEIBNIZ-BOARDS-20261110-001#3 (W in general) answered.
**Assumptions:** none added; A51's and A54's histories record the bearing.

- **What the attempt leaves open.** Which boards beside the tree a law can have, and whether the obstruction survives names without
  letters.

**Next step:** Research directions — selected: #1 (RIGID-WORLDS-20261110-001#3), unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Abstract names (RIGID-WORLDS-20261110-001#3, A54) | 2/3 — Substantial | 2/3 — Testable | As recorded there | Selected · not started |
| 2 | Every accretion law (RIGID-WORLDS-20261110-001#2) | 2/3 — Substantial | 2/3 — Testable | As recorded there | Alternative · not started |
| 3 | The boards beside the tree | 1/3 — Modest | 2/3 — Testable | Prove that every infinite shift of finite type on F2 has a point with infinite cyclic stabilizer, or find a law whose non-free solutions all factor through Z² → the theorem, or such a law | Alternative · not started |
| 4 | Theorem W as a short note for outside review | 1/3 — Modest | 3/3 — Ready | Write W, its corollaries and the drift theorem as a short note, after one more search (surveys of SFTs on groups) → a note ready for review, or W found in print | Alternative · not started |

1. **Abstract names.** Payoff 2: this epic shows the tree is the shape of the naming itself, so names without letters are the one test
   left of whether a law can choose its space. Concreteness 2: as rated there.
2. **Accretion laws.** Payoff 2: growth as the remaining route to a chosen plane. Concreteness 2: as rated there.
3. **The boards beside the tree.** Payoff 1: the plane is already never forced; this asks only whether it can be the one structured
   board beside the tree. Concreteness 2: Piantadosi's construction gives a periodic point along one axis, and its stabilizer has to be
   pinned down.
4. **A note.** Payoff 1: an outside check of a short theorem that may be folklore. Concreteness 3: the proof is written.

**Recommendation.** Research directions, selected #1: the Leibniz line is complete, and the naming is what this line has not yet
questioned. #1 and #2 tie at the top and are independent.

## Final report as sent

Sent to the owner on 2026-11-10 at 17:51 UTC and copied here verbatim.

I've closed and published weakly aperiodic laws under Leibniz's rule. The dichotomy now holds for every law: if a law has infinitely many solutions on the tree of names, one of them repeats nowhere. So under Leibniz's rule the tree is always one of its boards and the plane is never forced. The Leibniz line is complete.

**What I proved.** Every infinite shift of finite type on the free group has a point with trivial stabilizer. A law's freedom either sits in infinitely many disjoint branches, where the choices can be made independently, or it runs toward a few ends in each solution. Taken over all solutions, those ends make up every end of the tree, including ends that no group element fixes. An independent referee read the proof before publication and found no errors. One ingredient, the finite-board criterion, turned out to be known and is now credited.

**The census.** 96 of the 32,768 three-value level laws have solutions but no finite board. After the census I proved these are exactly the laws that drift: every place has more neighbours one level up than down, or every place has more down than up. My frozen certificates left 10 laws undecided, so prediction C1 failed. The mirrored horofunction settles all 10. Every verdict has now been re-checked in exact arithmetic.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: weakly aperiodic laws | **Status:** Successful | W and P proved for every law with finite windows; in the family, drift is the only thing that rules out a finite board; C1 failed and was settled by proof |
| Local direction: the identity rule in the limit | Complete | Leibniz's rule never forces the plane |
| Broader exploration: question 9 | Known alternatives | Abstract names, accretion laws, the boards beside the tree |
| Long-term goal: G1 | Obstruction learned | When places are named by words in two letters, the tree is always a board |

**Next step:** Research directions. My pick is #1. It ties with #2, and the two are independent.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | Abstract names (A54) | 2/3 | 2/3 | As recorded | Selected |
| 2 | Every accretion law | 2/3 | 2/3 | As recorded | Alternative |
| 3 | The boards beside the tree | 1/3 | 2/3 | Prove every infinite law also has a cycle-with-trees board, or find a law whose only other boards are planes | Alternative |
| 4 | Theorem W as a short note for outside review | 1/3 | 3/3 | Write it up after one more literature search | Alternative |

**Corrections:** two, both Not a block ([history](https://github.com/jscul/knotlab/blob/main/HISTORY.md)). The census contract said HiGHS solved the balance program "exactly in rationals". HiGHS uses floating point, and every verdict has since been re-checked exactly. Separately, the view-board count in BOARD-DIST's Theorem 7 is a known criterion (Piantadosi 2008) and is now credited.
**Goals:** G1 checkpoint (obstruction learned); "W in general" answered. **Assumptions:** none added; the A51 and A54 histories are updated.
**Basket:** spacing's WEAK-APER-20261110-001#1 (abstract names), #2 (every accretion law) and B16 (edge labels). Taken: none yet; #1 is selected and waiting for a go-ahead.

Commits: 794eec810 (epic), 9bb9a90c4 (shared docs), cc237504a and e3ceee237 (tracking), d436148f1 (history).
