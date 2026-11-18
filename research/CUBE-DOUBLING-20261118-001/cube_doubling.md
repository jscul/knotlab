# Why the cheapest growth gains an order at each doubling

Epic `CUBE-DOUBLING-20261118-001`, 18 November 2026, by Claude, on the coordinator's queue. This is Codex's priority 2, passed on
by the owner. Goals G1 and G16; tests A99. Refereed: report [R1](referee-R1/report.md), confirmed, no Block, folded in on 18
November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `ad68fbab4` at 01:25:37 UTC. The check ran from
  01:25:39 to 01:26:40 UTC.
- Proof: [proof.md](../../proofs/CUBE-DOUBLING-20261118-001A/CUBE-DOUBLING-20261118-001A-P001_cube_doubling/proof.md).
- Code: [check.py](../../experiments/CUBE-DOUBLING-20261118-001B/CUBE-DOUBLING-20261118-001B-E001_certificates/check.py).
- Results: [results.json](../../artifacts/CUBE-DOUBLING-20261118-001B/CUBE-DOUBLING-20261118-001B-E001_certificates/results.json).

## The answer

**Proved: the cheapest growth from one knot reaches the cube of d orders at 2^d distinctions, for every d, in every run, whatever
breaks its ties.** It holds for any cap of three or more knots per step (the referee), under A99. `STATE-RULES-20261117-001`'s
conjecture S6 is now a theorem. Between doublings the base holds d + 1 splits, and the (d + 1)-th order arrives between
n = 2^d + 2 and n = 2^d + 2^(d−1) + 1 under every tie rule (the referee's addition, with a short proof, computed for d = 2, 3, 4).

The proof has three parts.
- **From the full cube of s orders, nothing is free.** Every combination of sides is taken, so a new distinction can only add
  states. The cheapest steps add exactly one split. There are s·2^(s−1) of them that put the new distinction between two
  neighbours, and 2^s that hang it off one point.
- **After either, every missing combination is forceable.** Each of the 2^s − 1 combinations of the s + 1 splits that no
  distinction yet holds has an explicit certificate: three knots on distinctions already there that force the new one to it
  without adding a state.
- **The certificates survive.** Filling one combination changes neither the splits nor anyone's sides, so the others stay
  forceable. The cheapest rule must take a free step whenever one exists, so it fills the whole cube before it can add another
  split.

The frozen check bears every part out (3 of 3 predictions held):

| Check | Result |
| --- | --- |
| Every certificate, s = 1 to 7, both kinds of step | all work; 1, 3, 7, 15, 31, 63, 127 distinct fills, exactly the missing combinations |
| Every extension of the cube by brute force, s = 2, 3, 4 | none free; 8, 20, 48 at the least cost, the subdivisions and pendants |
| The exact distribution from one knot to n = 20 | 2⌈log₂ n⌉ + 2 states at every n with probability 1; Q3 at n = 8 and Q4 at n = 16 with probability 1 |

**In the owner's terms.**
- The cheapest growth from one knot never stops at two orders: it gains exactly one order each time the number of distinctions
  doubles, with no exception, whichever of its tied choices it makes.
- What drives it is that any combination of sides not yet taken can be reached with three knots touching what is already there,
  so a new distinction is free until every combination is taken.
- The price of a new order is paid only when there is no free room left.

Known mathematics, labelled:
- hypercube cut systems and their lattice dimension;
- Mulder's convex expansion theorem (median graphs grown from one point), Chepoi's expansion theorem for partial cubes,
  Eppstein's lattice dimension, and Sholander's median algebras;
- the knot on states is the cube's coordinatewise betweenness, NAE(x, ¬y, z).

The referee's search found no cheapest growth under betweenness constraints and no cube-at-every-doubling theorem. Known parts are
cited, not held back (the owner, 18 November 2026: "it's about the perspective we're adding").

**What this adds.**
- The cube growth read as space from logic: built only from knots ("b lies between a and c"), the cheapest continuation adds one
  order each time the number of distinctions doubles.
- The rule is not median closure, so the expansion theorems do not cover it (the referee). After a subdivision the median hull is
  Q_(s−1) × P3, with 3·2^(s−1) points, and after a pendant it adds nothing. Yet the rule fills all 2^(s+1) combinations: its end
  knots reach what medians cannot.

Local: the step analysis and the three-knot certificates.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | Every certificate works for s = 1 to 7 in both classes, with 2^(s+1) − 2^s − 1 distinct fills | held | no failure; 1, 3, 7, 15, 31, 63, 127 distinct fills in both classes |
| P2 | From Q_s nothing is free, and exactly s·2^(s−1) + 2^s extensions cost N + 2, s = 2 to 4 | held | 0 free; 8, 20, 48 |
| P3 | 2⌈log₂ n⌉ + 2 states at every n = 4 to 20 with probability 1; Q3 at 8, Q4 at 16 | held | 6, 8, 8, 8, 8, then 10 from n = 9 to 16 and 12 from 17 to 20, each the only value; the cube at 8 and 16 with probability 1 |

P3's last clause was seen before the freeze (disclosed in the pre-registration). *After the referee:* the class counts printed
then also showed one class at n = 8, so both cube clauses of P3 were visible, and `STATE-RULES-20261117-001` had already sampled
both. P3 tests little beyond n = 17 to 20, and nothing rests on it.

Not predicted: between doublings the number of orders reaches d + 1 before the cube is full. Four orders appear at n = 10 with
probability 0.4 and at n = 13 with probability 1, and five at n = 18 with probability 0.38 and at n = 20 with probability 0.85. So
the new order arrives with the first fills after the split is added, and the cube completes it.

## What it means for the goals and A99

- **G1** (space from a law): obstruction confirmed and now proved. The cheapest law grows the cube, one order per doubling, never
  holding two. A law that stops at two orders needs something it lacks, and `KNOT-CAP-20261117-001` found the tight caps stop at
  two without growing.
- **G16:** capability gained. The cheapest law's growth is now predicted exactly for every size.
- **A99** stays assumed; this theorem holds under it.

## Limitations

- Betweenness knots, up to three per step, and every old state kept (A99).
- With fewer knots per step the free fills do not exist (`STATE-RULES-20261117-001A`, S2). With more, every free step is still
  a fill and the theorem holds (the referee, checked with four knots; *corrected: this line first said other free steps may
  exist*).
- The theorem is about the cheapest rule only, and says nothing about uniform or weighted choice.

## Reproduce

```sh
cd experiments/CUBE-DOUBLING-20261118-001B/CUBE-DOUBLING-20261118-001B-E001_certificates
../../../.venv/bin/python -B check.py
```

## Advisor

Checked the proof before the freeze. It found no error in the certificates or the induction, and asked for three lines and a base
case, all added:
- the use of A99 in L4;
- the no-doubling line in L2;
- that only the existence of a free step is used;
- the base from Q₁.

It gave the related literature from memory. Not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh code: confirmed, no Block.
- L1 to L5 and the induction are correct; every A set and consistency condition was checked by hand.
- Fresh code agrees one size past:
  - L4 at s = 5 (112 cheapest extensions, 80 subdivisions and 32 pendants);
  - L5 found by search without the certificates to s = 5;
  - the certificates work to s = 8.
- Every class reachable from one knot was enumerated to n = 33: Q2 to Q5 at 4, 8, 16 and 32, each the only class, with
  2⌈log₂ n⌉ + 2 states throughout.

Folded in the same day, each logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`, all **Not a block**:
1. The theorem holds for any cap of three or more knots per step; the Limitations line said otherwise.
2. A99 is named in the intuition entry, the G1 and G16 checkpoints and the A97 line, and A99's own entry gains this study.
3. The disclosure covers both cube clauses of P3.
4. The arrival of the (d + 1)-th order between n = 2^d + 2 and 2^d + 2^(d−1) + 1 is the referee's, attributed.
5. Novelty: the known results are cited, and the note says what the perspective adds.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: S6, the cube at each doubling | **Status:** Proved (refereed) | A proof for every d, every run and every tie rule; 3 of 3 checks held |
| Local direction: what the cheapest law grows | Settled | Cubes, one order per doubling |
| Broader exploration: a law that grows exactly two orders | Unexplored | The cheapest law passes two, and the tight caps stop at it |
| Long-term goal: G1 | Obstruction learned (proved) | The cheapest law never keeps two orders |

**Next step:** Research directions. The coordinator has queued the 3 × 1 weave pair next.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The 3 × 1 weave pair with the twist fixed and the ruler measured | 2/3 | 3/3 | Freeze the pair with sectors fixed → stop at a class and a ruler reading | Selected (coordinator) |
| 2 | Between a stop and a cube: a law whose free room is two-dimensional (forceable only along two orders), for instance certificates restricted to knots whose old pair is adjacent | 3/3 | 2/3 | Characterise which combinations stay forceable under that restriction → stop at a law or an obstruction | Alternative |
| 3 | Why the end-hub and middle-hub five-starts differ in the number of orders (from `KNOT-CAP-20261117-001`) | 2/3 | 3/3 | Enumerate the first two steps from both → stop at the explanation | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (obstruction learned, now proved) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A99 unchanged; no new entry.

**Basket:** read; nothing taken.
