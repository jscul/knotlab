# Is the sign about the model or about the order we supply?

> **Referee report R1, 26 November 2026: confirmed with fixes, no block** ([the report](referee-R1/report.md)). Every frozen
> test was rebuilt with independent code and reproduced, including the cyclic shifts at three to six readers (9,235,584
> probability cells checked directly), the schedule shares through six readers (and at seven by crossing class: 216,720 of
> 681,080,400 with the real flip) and the 48 start signs as a set. The sentences below are corrected in place; the narrowings:
> - **Conditions on the headline.** The sign is decided by the schedule *for a start whose relative signs come from creating
>   its distinctions in order, with equal magnitudes and the stated real flip*. With the same orders, a start with all signs
>   positive does not carry it.
> - **Hidden orders.** A commit order unknown to the readers loses the contradiction at a fixed creation order, but if the
>   commit order follows the creation order the readers need know neither: all six hidden common orders at three readers give
>   the same exact table. What a growth rule would have to supply is the relative order, not a unique schedule.
> - **The complex flip does not take the other schedules.** Only the reversal sign is a local adjustment. With the complex
>   flip at every reader the carrying schedules are those whose crossing pairs are exactly the pairs across a split; at four
>   readers 312 schedules carry with the real flip, 480 with the complex flip and **1,728 of 2,520 with neither**.
> - **The mixture scores.** The predecessor's "odd orders" mixture is a mixture of orders that carry the contradiction here
>   (odd relative to its listing, even relative to the creation order); the mixture over all orders exceeds 2 in either
>   convention. The referee gives exact attainable scores 110/51 and 307/150, the values my optimiser found.
> - **Sign rules.** "Both hold 0" and the fermion rule carry on the same listings, but their tables differ by a relabelling;
>   the four other rules add only constant and linear signs.
> - **What could reopen the line.** A growth rule forcing the carrying crossing class (a unique schedule is not needed). The
>   records examined leave ties between siblings born in one round that change the verdict (at four readers, abcd against
>   abdc).
> - **Smaller fixes.** Denominators of the listing and reader checks; the polar form needs q(0) = 0 or the term q(0); A276's
>   title.

**About the order we supply.** Under the swap rule (swapping two distinctions that both hold 1 costs −1), the three-detector sign
is decided by the schedule in which the start's distinctions are created and their children born, for a start whose relative signs
come from creating its distinctions in order and read against a fixed choice of real readings, and nothing in the model fixes that
schedule. With the readings of the reordering-sign study, the contradiction
appears exactly when the children are committed in one of the n cyclic shifts of the order their parents were created (3 of 6,
4 of 24, 5 of 120, 6 of 720 orders); in general it appears exactly when every pair of parents' lifetimes, from creation to birth,
cross, up to a split of the readers into two groups. Every frozen prediction held. This confirms the numbers of
`REORDER-SIGN-20261126-001` (the reordering-sign study) and narrows two of its readings: "an even order" was a three-reader case,
and the parents' creation order is not a reference the history supplies for free.
[Pre-registration, frozen at 8515665ca6](preregistration.md) · [Predecessor](../REORDER-SIGN-20261126-001/results.md) ·
[Its referee report](../REORDER-SIGN-20261126-001/referee-R1/codex/report.md) · [Advisor's review](advisor/answer_1.md)

## Why the seventh prediction failed

The reordering-sign study predicted (its P7) that once the swap rule also governs the readings, every commit order gives the same
table, so order is only a convention. It failed because a commit order is an order of operations, not a listing. A birth whose
parent holds 1 occupies one of its two fresh distinctions in each term, and two such births anticommute: exactly,

K_i K_j = K_j K_i (−1)^{n_i n_j},

so exchanging two births costs −1 exactly when both parents hold 1. The swap rule reappears on the parents, because a child's
fresh distinctions carry its parent's value. The listing, by contrast, is a convention: at three and at four readers, 24 configurations each agreed across 23 listings
(552 evaluations each; P1, gate d).

## What the frozen predictions found

| # | Prediction | Result |
| --- | --- | --- |
| G | Gate: replay of the recorded three-reader rows, anticommutation, a second code path, listing is a convention | **Held.** 28 recorded rows replayed; 0 failures of the anticommutation relations on 512 basis states under two listings; 138 tables agree with a separate matrix construction; 1,104 tables identical across listings. |
| P1 | Two births commute up to (−1)^{n_i n_j}; any two commit orders differ word by word by −1 per occupied parent pair they order differently | **Held** on all 512 basis states and on all 15 and 276 pairs of orders at three and four readers. |
| P2 | The carrying commit orders are the n cyclic shifts of the creation order σ; σ itself is exact on all 4^n cells | **Held** at n = 3, 4, 5, 6, for σ ascending, descending and one seeded order each (at three readers the seeded order drew the ascending one). Each other shift matches after relabelling the X outcomes of the readers it moves. |
| P3 | Every schedule: real readers carry the contradiction exactly when the crossing pairs are "all cross" up to a split; the complex flip exactly when they are "none cross" up to a split | **Held** on all 90 and 2,520 schedules at three and four readers and a seeded 2,000 of 113,400 at five. |
| P4 | Each child born right after its own parent: never with the real readings, always with the complex flip | **Held**: 0 of 6, 24 and 120 creation orders with the real readings; all with the complex flip. |
| P5 | Start signs set by hand instead of by a creation order | **Held.** At three readers the contradiction appears exactly when h_ab·h_ac·h_bc·sgn(π) = −1, and 6 of the 8 sign patterns have an exact order. At four, 48 of 128 patterns carry it, each for exactly one cyclic class of 4 orders, the same 48 the formula gives; 24 have an exact order. |
| P6 | Swap rules | **Held.** Of the eight rules giving a swap a cost ±1 by what the two distinctions hold, the four with c00·c11 = −1 (among them "both hold 0") carry it on exactly the fermion rule's listings, and the other four on none, at n = 3 to 6. Of the phases s = e^{iθ}, θ = kπ/12, only s = −1 gives the full contradiction; at three readers the reversal's score is 1 + 3(1 − cos θ)/2, above 2 exactly when cos θ < 1/3. |
| P7 | Weightings of orders | **Held.** Counting commit orders equally, n of n! carry it (1/2, 1/6, 1/24, 1/120); counting creation and commit orders equally together, the same shares. The equal mixture of all orders has no sharp correlations; the equal-weight coherent sum keeps only the blank old word. |
| P8 | Reader conventions | **Held.** With every reader's flip matched to the order its pair is written in, the carrying orders are the cyclic shifts of σ in every one of 64 (three readers, two σ) and 256 (four readers) assignments; with any reader unmatched, no order carries it (512 assignments). An exact order exists exactly when the readers with the other flip, or the rest, are the first k of σ. With the complex flip at every reader, the shifts of the reversed σ carry it. |

[Exact receipt](../../artifacts/REORDER-CONFIRM-20261126-001/REORDER-CONFIRM-20261126-001-E001_schedules/results.json)

## The account, now checked

Write the state in the listing in which each reader's three distinctions sit together. The child's fresh pair then carries no
sign, the real flip acts as X on the old distinction, and the grown knot reads as an n-reader signed knot with amplitude
(−1)^(C(k,2) + d) on an old word of weight k, where d counts the occupied parent pairs whose creation and commit orders differ.
Real readings see the full contradiction exactly when that sign's polar form is the dot product on the even words (Dehaene and
De Moor). C(k,2) has it; d must then have none, which happens exactly when the pairs ordered differently are those across a split,
and those orders are the cyclic shifts.

**Where the reversal sign comes from.** C(k,2) is the cost of the round itself: every parent is created before any child is born,
so each child's odd creator passes the later parents. If each child is born right after its own parent, each reader's
distinctions are created together as an even block, the blocks commute, and the sign is gone (P4).

**Schedules.** For a general schedule, two occupied parents cost −1 exactly when their lifetimes cross (one is created, then the
other, then the first is born, then the second). This is the sign of a pairing in the literature's Wick expansion, (−1) to the
number of crossings. Counting every schedule equally, the share in which the real readings see the contradiction is:

| Readers | Schedules | Real flip | Complex flip |
| --- | --- | --- | --- |
| 3 | 90 | 7/15 | 8/15 |
| 4 | 2,520 | 13/105 | 4/21 |
| 5 | 113,400 | 1/45 | 52/945 |
| 6 | 7,484,400 | 31/10395 | 7/495 |

Under that weighting (A279), 312 of the 2,520 schedules at four readers carry it with the real flip (2,184 give a sign that is not
constant), and no rule of the model singles out a schedule that carries it: the round (all parents, then all children) carries it
for every cyclic shift and gives the fixed-label target for the identical order, and depth-first is another schedule with the
opposite verdict.

**The reversal sign is a local adjustment.** On even words (−1)^C(k,2) = i^k, which is diag(1, i) at every reader. So a reader
with the complex flip sees the contradiction in the unsigned knot; with the complex flip at every reader the carrying schedules are
those whose crossing pairs are exactly the pairs across a split (P3, P4, P8). Other schedules' signs need not be local
adjustments: at four readers 1,728 of 2,520 schedules carry it with neither flip. "The sign the
experiment needs" is the sign needed by readers held to real readings.

## What this does not show

- That the model supplies the sign. The growth law leaves the commit order free and the parity knot has no creation order; both
  orders, or the whole schedule, are supplied, and only a shrinking share of them carries it (1/2 to 1/120 of commit orders over
  three to six readers). The tested uniform mixture over commit orders and the equal-amplitude sum each lose the full contradiction; but a commit order
  that follows the creation order needs no reader to know either (all six hidden common orders at three readers give the same
  exact table).
- That the swap rule is native. It is added (A275). Among rules that charge a swap by what the two distinctions hold, it is the
  only one that carries it, up to relabelling and a global sign (the other four add only constant and linear signs); that is a statement about this class of rules, not a
  derivation.
- Anything about physical fermions. The births mix fermion parity (a birth whose parent holds 1 makes one fresh distinction), which
  physical fermions do not allow as a local operation; the referee of the predecessor made the same point.
- Anything past one round of one-parent births of a parity knot, or with weights other than equal magnitudes (A144). A second
  round was not run: its reader would need a new definition.
- That unknown orders remove every trace. The predecessor's referee found that with other real readings, the mixtures over orders
  score 168/(25√10) ≈ 2.13 (orders odd relative to its listing, which are the carrying orders here) and 308/(25√37) ≈ 2.03 (all
  orders), above the local bound 2, though without the full contradiction; a quick optimiser of mine found about 2.16 and 2.05, and
  this confirmation's referee gives readings attaining exactly 110/51 and 307/150. The all-order mixture is the one that says
  something: a commit order unknown to the readers still leaves a score above 2. Not part of the frozen predictions.

## Reproduce

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python -B artifacts/REORDER-CONFIRM-20261126-001/REORDER-CONFIRM-20261126-001-E001_schedules/check.py
```

About seven minutes in one process (under load). The engine (`engine.py`) is new; it imports nothing from the predecessor or its
referee, whose receipts are read only by the gate.

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: confirm or narrow the reordering sign | **Status: Successful** (confirmatory; every frozen prediction held) | The sign is a property of the supplied schedule against fixed real readings; the cyclic shifts are the class at every size checked |
| Local direction: commit order as the source of the sign | **STOP** | No rule of the model fixes the schedule; under counting schedules equally the share falls from 7/15 to 31/10395 over three to six readers |
| Broader exploration: native phase | Known alternatives | A swap rule makes any schedule a sign; the reader's reality decides which class needs it |
| G5 Dynamics, G9 Witnesses | Obstruction learned | One round's order can carry the sign only when it is supplied; the model's rounds give the reversal sign only with a matching commit order |

**Next step:** Research directions — No next action selected. **STOP** on the order line; it reopens if a growth rule forces the carrying
crossing class (a unique schedule is not needed).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A growth rule that forces a carrying crossing class (for a round: commit order following creation order) | 3/3 — Barrier: it would make the sign the model's | 1/3 — Stated: no candidate in the record | Search the growth and local-round records for a rule that orders births by their parents' creation → a rule found, or none | Alternative · deferred |
| 2 | A second round of births | 2/3 — Substantial: does crossing still decide the sign | 2/3 — Testable: a reader made of the old distinction and its grandchild's fresh one, both Majorana factors at the ends | Define the reader, predict by crossings over three generations, run at three readers → a pass or a counterexample | Alternative · deferred |
| 3 | Why real readings | 2/3 — Substantial: the need for a sign comes from fixing readings real | 2/3 — Testable: ask which readings a reader built from the record's own distinctions can make | List the readings the predecessor's readers can be built from → only real ones, or a complex one too | Alternative · deferred |
| 4 | Link: the sign is the Wick sign of a pairing, (−1) to the crossings (intuition-links) | 1/3 — Incremental: a known mechanism named | 3/3 — Ready: counted here on 7,484,400 schedules by crossing class | Write it as a lesson of the guide's sign chapter → a draft the owner accepts | Proposed |

1. This is the only route by which the result could become about the model. The study of descent held by the structure found
   that its tested forms write parent-step depth modulo three, which ties siblings of one round; the growth records the
   referee read leave choices among ready siblings that change the verdict (at four readers, abcd against abdc), and order
   them only by a supplied priority or by names.
2. The obvious extension; it needs one new scaffold (the reader), named in advance.
3. With the complex flip the unsigned knot already carries the contradiction, so the question moves to the readers.
4. An intuition, not evidence.

**Corrections:** One, logged: the reordering-sign study's "even order relative to the parents' creation order" holds only at three
readers (the class is the cyclic shifts), and its "the reference is not extra … every history already has it" is withdrawn (the
creation order acts through the start's relative signs and must be matched by the commit order, both supplied); with five
narrowings from its referee (Narrowing).

**Goals:** G5 Dynamics and G9 Witnesses: an obstruction learned; no goal changed.

**Assumptions:** A275 and A276: history lines (the swap rule's class of alternatives tested; the reader's flip and its pair order
tested). A279 added: schedules of one round counted equally (a measure).

**Scaffolds:** Varied: the commit order (all n!), the creation order (three per size), the schedule (all at three and four
readers), the start's signs (all at three and four), the swap rule (eight sign rules and 24 phases), the readers' flips, records
and pair orders, the listing (23 per size), the weighting of orders (four). The result changes with the commit order, the schedule,
the swap rule and the reader's flip, so it is about those choices; it does not change with the listing, so that part is about the
model. None of these is expected to be replaced by the model unless direction 1 finds a rule. Advisor: consulted before the
freeze (analysis and design); its proposals P3 and F3 became predictions and held.
