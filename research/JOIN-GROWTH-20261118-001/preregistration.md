# Do growth behaviours compose when growing parts are joined? Pre-registration

Epic `JOIN-GROWTH-20261118-001` (the coordinator's go-ahead, idea 1 of its reply to the owner's "What do you think we could build
out of something like this?"; goals G17 and G2), 2026-11-18. Written after a pilot (disclosed below, all of it fitting) and the
advisor's answer, before any case of the census was grown. Code by the thread; the run launched by the thread with the shared
runner. The canonical K1–K3 test is unchanged.

"Growth" and "dimension" here count junctions by round (the referee's narrowing of `FIRST-KNOT-20261118-001`); bond balls are not
measured. A rate is the growth factor of the junctions made per round.

## The question

Under the parity law with the cheapest counts (the policy of `TOUCH-CENSUS-20261118-001` and `RING-GROWTH-20261118-001`), a ring
of five or more knots with surplus distinctions grows exponentially (`RING-FORMULA-20261118-001`: rate the root of
x^(n + j) = (1 + x)^j), and two touching knots grow two copies of a two-way counting pattern (`FIRST-KNOT-20261118-001`). When such
parts are joined (by one shared distinction, a shared knot or a short path of knots), does each part keep its own growth, does one
take over, or does something new appear; what is typical across the small ways of joining; and do two joined rings add, multiply
or lock their rates?

## What the pilot found (fitting, disclosed)

Pilot code and outputs are in the experiment family (`pilot/`). About 40 starts were grown before this freeze, 20 to 50 rounds each
with a faster engine (`fastlib.py`, same output as freelib's on 304 starts, `checks.py`).
- Joining a part at a ring knot raises the round-1 demand of that knot and of its two ring neighbours, so the start must give
  them more places or it stalls in round 1. Every such start needs a knot of five or six places at the joint, outside the census's
  sizes 3 to 5 (A106), which is why the census never saw one.
- **The bare convention** (used throughout): every knot gets the fewest places that let round 1 start, max(3, shared + round-1
  demand), plus the surplus distinctions listed for it.
- The ring takes over. Every join tried made the ring grow faster than alone, and the joined part's own growth did not survive as a
  separate term (except one renewing chain, below).
- **The product law fits every finite case exactly** (Berlekamp–Massey, recurrences annihilating 4 to 30 rounds past their order):
  write y = 1/x. The rate solves the **return equation** y^n (1 + y)^j Π_k F_k(y) = 1, where n is the ring's length, j its own
  surplus distinctions, and each knot of an adjunct contributes a factor, its **delay series** F:
  - a lone knot joined to a ring knot by one shared distinction, with s surplus distinctions: F_s = 1 + y(1 + y)^s (s = 0, 1, 2,
    3 fitted; s = 0 is a surplus distinction one round early, exactly);
  - the two knots of a two-fold piece hanging from a ring knot (A touching the ring knot, B touching A): one factor each,
    F_(s_A) · F_(s_B), not nested; when B's only surplus distinction is the one the floor of three places gives it, that distinction
    renews every round and B contributes 1/(1 − y) (the **renewing offshoot**, the advisor's reading), with a factor x − 1 in the
    recurrence.
  - Fitted rows: ring + two-fold piece with surplus (2, 2) and the ring's own surplus distinction: rate exactly the golden ratio
    (x^12 = (1 + x)(x^3 + x^2 + 2x + 1)^2, annihilating rounds 15–22 in three joins at different ring knots); without the ring's
    surplus: x^11 = (x^3 + x^2 + 2x + 1)^2, rate 1.5141.
- A path of one knot between the ring and the two-fold piece does not fit the law (no recurrence of order ≤ 9 in 22 rounds).
- **Two joined rings** of five knots: no recurrence found; ratios rising slowly to 2.28 at round 15; a fit c(t) ≈ C λ^t t^α gives
  λ ≈ 2.51, α ≈ −1.35 (the advisor: consistent with t^(−3/2) and λ = 2.52 ± 0.02, a square-root branch point, the signature of a
  self-referring, tree-like menu). Two two-fold pieces joined grew at most two-dimensionally.

## In standard terms

Constraint growth on a cycle of even-parity constraints with decorations. The pilot's law says the growth series is rational with
denominator 1 − y^n Π_k F_k(y): a renewal equation over laps of the cycle in which each decoration contributes its rank-generating
series independently (the advisor's derivation from the (v, S) model of `RING-GROWTH-20261118-001`: at each lift of a decorated knot
the growth chooses one element of the decoration's ranked menu, and lifts are independent). Two cycles joined would give an
algebraic, non-rational series.

## Prior work in the program

`python3 -B scripts/track.py objects "ring of knots joined to a growing part cheapest parity growth" --until 2026-11-18 --exclude JOIN-GROWTH-20261118-001`
`python3 -B scripts/track.py objects "growth rate of a cycle with attached trees generating function renewal equation" --until 2026-11-18 --exclude JOIN-GROWTH-20261118-001`
`python3 -B scripts/track.py objects "joined rings two rings sharing a distinction growth" --until 2026-11-18 --exclude JOIN-GROWTH-20261118-001`

- `RING-FORMULA-20261118-001` — a relative: the rate of every clean odd ring (x^(n + j) = (1 + x)^j); this study adds parts joined to
  the ring and two rings, and uses its formula for the ring's own surplus distinctions, citing it.
- `RING-GROWTH-20261118-001` — a relative: the (v, S) model and the ring of one five-place knot; the advisor's derivation of the
  return equation extends its model.
- `TOUCH-CENSUS-20261118-001` — the same policy and a population of arrangements of up to five knots of three to five places; none
  of this study's starts is in it (a joined ring needs a knot of five or six places at the joint and has six or more knots).
- `FIRST-KNOT-20261118-001` — the same policy: two touching knots grow two two-way patterns; this study joins such a piece to a ring.
- `NAE-METRIC-20261118-001` — unrelated object (bond distance on joints, blocks and rings), the same words.
- `LEIBNIZ-BOARDS-20261110-001` — unrelated (a three-value law whose board is a three-cycle with trees attached).
- `GROW-FACE-20261110-001` — unrelated (accretion laws; components with trees attached, a cell count), not the parity policy.
- `PLUS-ONE-20261118-001` — the same policy on trees of knots (linked chains add dimensions); this study's family E (no ring) is its
  population's neighbour.

## Prior work outside the program

Cited once: renewal equations and transfer matrices; rational and algebraic generating functions and the t^(−3/2) law at a
square-root singularity (Flajolet and Sedgewick, *Analytic Combinatorics*, 2009, ch. VII); growth series of free products of groups
(1/f = 1/f₁ + 1/f₂ − 1, rational when the factors are). Not found: a growth rule for constraint patterns whose joins act as
independent factors of a return equation.

## Settled by construction (stated, not tested)

- Bare starts never stall in round 1 (their sizes are chosen for it), and the fewest counts never stall later
  (`TOUCH-CENSUS-20261118-001`, Lemma 1).
- Counts are of junctions of one presentation; no arrangement is counted twice within a family (every case is a distinct start).

## Predictions (frozen)

Cases and predicted annihilators are listed by `job.py` (137 cases). "Holds" for a predicted annihilator means: it annihilates the
grown counts from some round t0 ≤ 12 with at least three rounds tested past its order; "unsettled" if the horizon gives fewer than
three such rounds; "fails" otherwise. Grown to 80 rounds, 250,000 junctions or 900 seconds.

| # | Family | Prediction | Fails when |
| --- | --- | --- | --- |
| G | gate | `checks.py` passes (fastlib = freelib on 304 starts; a mutant disagrees; the clean rings reproduce) | any fails |
| P1 | A1: a lone adjunct with s surplus distinctions on rings of 7 and 9 (s = 1, 2, 3), and s = 4 on the ring of five | x^(n + s + 1) = x^(s + 1) + (1 + x)^s | any fails (sharp) |
| P2 | A2: several lone adjuncts and ring surplus distinctions at separate ring knots, positions varied (8 starts) | the product y^n (1 + y)^j Π F_(s_i) = 1, whatever the positions | any fails (sharp) |
| P3 | A3: two lone adjuncts on the same ring knot (3 starts) | F_(s₁) F_(s₂) | any fails (medium) |
| P4 | A4: the bare two-fold piece hanging from a ring of 7 and of 9 | (x − 1)(x^(n + 1) − x^n − x − 1) | either fails (sharp) |
| P5 | A5: two-fold pieces with surplus (s_A, s_B) = (1, 3), (2, 3), (3, 2) on the ring of five, (1, 2), (2, 2) on the ring of seven | F_(s_A) F_(s_B) | any fails (medium) |
| P6 | A6: the (1, 2) piece with the ring's own surplus distinction at the joined knot, or two knots away | (1 + y) F_1 F_2 in both | either fails (risky) |
| P7 | D, joins by a shared distinction or a shared knot: every small join of a ring of five (bare, or one surplus distinction at the joined knot, one away or two away) and a two-fold piece with listed surplus 0 to 2 on each knot (48 starts) | the product law, with the renewing offshoot, in every start; scored on all and on the 35 not seen in the pilot | any fails |
| P8 | A, B, D (all join types, including paths of one and two knots) | every start grows exponentially faster than its ring alone (rate above 1 for a bare ring, above 1.1347 for a ring with one surplus distinction, by at least 0.01) | any start does not |
| P9 | C: two rings joined (5–5 by a shared knot, by a path of one knot, by a shared distinction with a surplus elsewhere; 5–7, 7–7, 5–9 by a shared distinction) | (a) no recurrence of order ≤ 7 (with twice its order to spare); (b) fitted λ above 1.5 in all; (c) λ(5–7) < 2.51 (the pilot's 5–5), λ(7–7) < λ(5–7), λ(5–9) < λ(5–7); (d) fitted α between −2 and −1 | any part fails |
| P10 | E: two two-fold pieces joined, no ring (6 starts) | none grows exponentially; each closes, or grows with dimension at most 2 | any fails |
| — | B: a chain of three hanging knots, a knot sharing two distinctions with a ring knot, a knot touching two ring knots | no prediction; reported | — |

Rates for P8: the dominant root of the predicted annihilator where it holds, else of the minimal recurrence found, else the geometric
mean of the last five ratios. λ and α for P9: least squares of log c(t) = a + t log λ + α log t over rounds 8 to the last.

**Seen in the pilot.** In family D, fourteen starts repeat pilot starts (thirteen in P7's scope and one path of one knot; listed by `merge.py`); P7 is scored with and without them. The two starts of A6 also occur in D.
Family A, B, C (except the 5–5 join by a shared distinction, which is the pilot's and is not in C) and E were not grown before this
freeze.

## Runs and stop rule

`job.py` through the shared runner, 7 workers, 2 GB per case, 900 seconds per case; `merge.py` scores. Expected 1 to 2 hours,
registered in the long-running index. Stop at the read-out: a law that predicts every case in its scope, or the cases that break it.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It derived the return equation from the (v, S) model (a ranked menu at each
lift, lifts independent, so factors multiply and positions change only the first lap), explained the bare lone knot as a surplus
distinction one round early and F_s = 1 + y(1 + y)^s, read the two-fold piece as a product with a renewing offshoot (refuting my
nested law), resolved two unsettled pilot rows (both then fitted exactly), flagged one row as inconsistent (my description of it was
wrong: the join had used up the ring's surplus distinction), had no model for two rings (its own attempt is refuted by the pilot's
rates) and proposed the sharp, medium and risky predictions frozen here, and the words "adjunct", "delay series" and "return
equation".
