# Is the far pair's sign SEED's copy step? Pre-registration

Epic `FAR-SIGN-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead after `COPY-CLASS-20261118-001`'s referee.
It is the last study on the two-order line. Goals G1 and G16; it challenges A101. Frozen before any read-out of ticket B. The canonical
K1–K3 test is unchanged.

## The question

COPY-CLASS's referee found one sign that decided SEED's copy step on 2,916 copy steps and 196,292 refused fills: the fill's far end
pair is separated by every crossed split. The coordinator asked for three things:
- freeze the sign;
- prove it equivalent to the copy step, or find a counterexample;
- then ask whether the copy class's betweenness reads it.

## Ticket A (written before this freeze)

`proofs/FAR-SIGN-20261118-001A/FAR-SIGN-20261118-001A-P001_sign/proof.md`. The knot set is a middle knot B(p, r, q), a near end knot
B(a, p, r) and a far end knot B(c, d, r). A split is moved when r lands off p's side.
- **L1, L2.** The moved splits are those with a, not q and not d on p's side. Two old splits come to cross exactly when one is moved,
  the other is not, and the unmoved one's p-side lies inside the moved one's.
- **L3, L4.** Under the sign, clause (a) holds, the new crossings are G × M (gainers by moved splits), and r sides with d on every
  crossed split.
- **L5.** Under the sign, a crossing-making fill is a copy step exactly when no uncrossed split is moved (T1) and the moved splits are
  the crossers of one unmoved crossed split (T2). On a base of two orders, (T2) says they are one whole order.
- **L6 (a pair pattern).** Suppose every crossed split separates p from q, none separates a from p, and some but not all separate p
  from d. Then the fill, if it makes a new crossing, is a copy step.
- **The sign in betweenness.** The sign holds exactly when every distinction lies between c and d over the crossed splits alone.
- **Proposition 7.** On a seven-distinction base of two orders, with knots on any pairs, there is a fill with the sign that SEED
  refuses, and a copy step without the sign. Neither half of the equivalence follows from the fill's knots and the two orders.

**Not proved**, and scored below, on SEEDK's knot-local fills:
- **F1:** a fill that gives an uncrossed split a crossing has the sign. This gives the converse.
- **T1** and **T2** under the sign. These give the sign's sufficiency.

## Ticket B

`experiments/FAR-SIGN-20261118-001B/FAR-SIGN-20261118-001B-E001_sign/`: `signlib.py`, `run.py`, `checks.py` and `readout.py`. They
build on `COPY-CLASS-20261118-001B`'s `classlib.py` and its pinned predecessors (the study line's own engine, not the referees').
Three gate checks pass:
- Proposition 7's base, with states equal to those its implied knots allow;
- both fills of Proposition 7, with their verdicts, signs and moved sets;
- this library's SEED verdict, equal to knotlib's on a gate run, with L1, L2 and K1 on its 2,058 knot sets.

**Part S** runs SEEDK on fresh starts, with fresh seeds, past the referee's sizes.
- Every bracketing of 5, 6 and 7, and the bracketings of 8 at indices 2, 5, 8, …: 105 starts to n = 32. COPY-CLASS took indices 0, 3,
  6, … and its referee 1, 4, 7, ….
- Random bracketings (recursive random split points, declared not uniform) of lines of 18 (30 starts, to n = 40), of 22 (20 starts,
  to n = 44) and of 26 (10 starts, to n = 48).
- Every crossing-making knot-local extension after the switch is kept with SEED's verdict. For each knot set of the treated shape
  the run records:
  - the sign;
  - the weak sign (r sides with d on every crossed split);
  - the near-pair sign (no crossed split separates the near pair);
  - F1's premise, T1, T2 and L6's pattern;
  - the sizes of the two orders, and whether p is an earlier fill's r;
  - the closure picture (COPY-READ's copy class);
  - the marked five-distinction picture: the closure picture together with what p, q, a, c and d see of every split, and one mark for
    whether that split is crossed.

**Part A** is the ablation, with no prediction (the advisor's replacement for an any-pairs control).
- The starts are the bracketings of 5 and 6, at the first three bases after the switch with n ≤ 14.
- It takes every fill with knots on any pairs. For each crossing-making knot set of the treated shape it records which of its three
  pairs ({p, q}, {a, p}, {c, d}) already share a knot.
- It reports, for each of the eight patterns, the failures of F1, of T1 and T2 under the sign, and of sign = copy step.

## Predictions (frozen)

| # | Prediction | Source |
| --- | --- | --- |
| R0 | Every copy step has a knot set of the treated shape (one middle knot, two end knots with exactly one end pair touching the middle pair, and the near knot pinning r to the shared distinction). Every crossing-making knot set of that shape has this orientation | exploration (below) |
| R1 | **Headline.** The sign equals the copy step on every crossing-making extension: no copy step without it, no refused fill with it | the referee; L5 with R2 and R3 |
| R2 | F1 on every treated knot set: when its fill gives an uncrossed split a crossing, it has the sign | exploration |
| R3 | T1 and T2 on every treated knot set with the sign | exploration |
| R4 | L6's pair pattern holds on every treated knot set of every copy step and on none of a refused fill | exploration |
| R5 | The weak sign and the near-pair sign each equal the copy step at the extension level | exploration |
| R6 | Every treated knot set is in one of two states. In state (α) it has the sign, T1 and T2, and gainers. In state (β) it has no sign and no gainer, and crossed splits come to cross. No fill has treated knot sets in both states | exploration |
| R7 | (i) Inside the copy class both verdicts occur, so the closure picture does not read the sign. (ii) No marked five-distinction picture occurs with both verdicts | L4's betweenness remark; advisor |

## Coverage and decision rules (frozen)

- **Coverage.**
  - R3 counts as tested where the smaller order has three or more splits only if at least 100 knot sets with the sign have such
    orders. Otherwise it is reported as untested there.
  - Copy steps where p is an earlier fill's r are counted, and so are copy steps after two or more earlier copy steps. If there are
    none, R1 to R6 are reported as untested there.
- **R1 decides.**
  - "The sign is SEED's copy step on SEEDK's fills (computed)" holds if there is no exception either way.
  - Every exception is printed. It is a counterexample to the referee's sign at the new sizes.
- **The harness, unscored.**
  - L1, L2 and K1 must hold on every treated knot set, since they are proved; this library's SEED verdict must equal knotlib's.
  - A failure there is a bug and stops the read-out.
- **The proof stays open.** "Proved" is claimed only for ticket A's statements. R1 to R6 remain computed, whatever their outcome.

## Exploration disclosed

Before this freeze, on runs with the referee's engine:
- every bracketing of 5 to 7 to n = 22, and a few lines of 12 and 18;
- random bases, and rectangles with pendant trees with knots on any pairs (Proposition 7's search).

What those runs showed:
- **On SEEDK's knot-local fills.** L1 and L2 held on 146,835 knot sets. Every treated knot set was in state (α) or state (β). The
  weak sign, the near-pair sign and L6's pattern each matched the copy step.
- **Off them.** With knots on any pairs both directions failed: 380 fills with the sign were refused and 190 copy steps lacked it, on
  300 small bases.
- **One smoke run.** The pipeline was run end to end on two bracketings of 6, which ticket B reruns with the same seeds.

The advisor was consulted before this freeze. It:
- re-derived L1 to L3 and gave L4's G × M form and "r sides with d";
- proposed scoring F1, T1 and T2 separately (R2, R3), the coverage condition and the one-pair-at-a-time ablation (part A);
- proposed the marked picture as the fair version of the copy-class question, since the plain closure picture cannot tell crossed
  splits from uncrossed ones.

It could not derive an invariant of SEEDK's co-knotted pairs that would prove F1, T1 and T2. It suggested looking for counterexamples
where p is an earlier copy step's r, and in larger orders.
