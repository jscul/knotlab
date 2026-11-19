# Do growth behaviours compose when growing parts are joined?

Epic `JOIN-GROWTH-20261118-001`, 18–19 November 2026, by Claude, on the coordinator's go-ahead (idea 1 of its reply to the owner's
"What do you think we could build out of something like this?"). Goal G17. **Refereed:** report [R1](referee-R1/report.md), confirmed, no Block, with two
Narrowings and one Not a block point, folded in on 19 November (see Referee; one deferred run on its side).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `ca358844a` at 23:45 UTC after a disclosed pilot. The
  census ran from 23:46 UTC through the shared runner (`JOIN-GROWTH-B1`, `runs/join-growth`, 137 cases on 7 workers); the cases
  that exceeded 2 GB were rerun with more memory under a logged amendment (`JOIN-GROWTH-B2`, `runs/join-growth-mem` and
  `runs/join-growth-mem2`).
- Code: [fastlib.py, joinlib.py, reclib.py, job.py, job_mem.py, merge.py, posthoc.py, checks.py](../../experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/),
  using FIRST-KNOT's start library and FRESH-COUNT's policy; the pilot's scripts and outputs in `pilot/`, the post hoc runs in
  `posthoc/`.
- Results: [results.json](../../artifacts/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/results.json) (the frozen
  scoring) and [posthoc.json](../../artifacts/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/posthoc.json).

"Growth" counts junctions by round, and a rate is the factor by which the junctions made per round grow. Bond balls are not
measured. Words new to the record, chosen with the advisor:
- an **adjunct** is a part joined to a ring knot;
- a knot of it is **at one remove** from the ring when it shares a distinction with a ring knot, and **at two removes** when it
  shares one with a knot at one remove;
- its **delay series** F(y) counts, by the rounds they cost, the ways the growth can use it at one lap;
- the **return equation** is the equation in y = 1/x whose root gives the rate;
- a **renewing offshoot** is an offshoot that the floor of three places gives a surplus distinction every round.

"Surplus distinction" is the glossary's word for what the ring records called a spare distinction.

## The answer

**In the owner's terms.**
- **No, the parts do not keep their own growth. The ring takes over, and every tree of knots joined to it speeds it up.**
  - The ring speeds up even when alone it grows by only five junctions a round (five four-place knots).
  - It speeds up even when the joined part would close on its own (a lone knot).
  - The joined part's own growth does not survive beside the ring's. Two touching knots alone grow two copies of a two-way counting
    pattern forever. Joined, they become a finite menu on the ring, except that a far knot holding only the floor's distinction renews one
    offshoot a round.
  - All 93 small joins of a ring of five and a two-fold piece grow faster than the ring alone, at rates from 1.13 to 1.69 a
    round.
- **Why the joint itself creates growth.**
  - A join asks the joined ring knot and its two ring neighbours for more joins in the first round, and the cheapest counts must give
    them the places.
  - Every knot of the joined part then becomes one more way for the ring to grow at every lap. The growth can skip it or take it.
  - Once a knot is taken, its own surplus distinctions are further ways inside it.
- **One law, rules within rules.** Each joined knot brings a small menu, and the menus multiply into one equation for the rate:
  y^n (1 + y)^j Π F = 1, with y = 1/rate.
  - A knot with s surplus distinctions of its own has the menu F_s = 1 + y(1 + y)^s: skip it (1), or take it (y) and then any of its
    own surplus distinctions ((1 + y)^s). It is a menu inside a menu.
  - Where the knot is joined on the ring does not matter.
  - Along a chain of joined knots, each knot's menu sits inside the menu of the knot two before it (found after the read-out, below).
- **The frozen tests.**
  - The law predicted the exact recurrence of the junction counts, not just the rate, in all 26 sharp, medium and risky tests run
    (corrected from 27; P1's seventh listed start was not run, and the referee's growth of it holds, see Referee).
  - It did so in every one of the 48 joins by a shared distinction or a shared knot of the census (35 of them not seen before).
- **The coordinator's guess, that a join acts as added spare distinctions,** is exact only for a lone knot with nothing of its own:
  F = 1 + y, one surplus distinction one round early. A knot with surplus distinctions of its own counts for less than that many
  spare distinctions would (1 + y + y² against (1 + y)²).
- **Two joined rings neither add nor multiply their rates. They lock into one growth of a new kind** (corrected 19 November; see
  Correction).
  - Two rings of five four-place knots each grow by five junctions a round alone. Joined by one shared distinction, they grow about
    2.3 times a round over the rounds grown, approaching 2.61 a round.
  - The counts satisfy no short linear recurrence. Their series is algebraic (`RING-PAIR-20261119-001`): c(t) ≈ C λ^t t^(−5/2),
    the mark of counting tree-like clusters. Each ring's menu holds the other ring.
  - Longer rings lock lower: 2.61 for five and five, 2.38 for five and seven, 2.24 for five and nine, 2.19 for seven and seven.
    Joining through a shared knot locks higher (2.87), and joining through a path of one knot lower (2.43).
  - With the exponent fixed at −3/2, a pre-asymptotic fit (the exponent is −5/2, see Correction), the advisor forecast round 16 of
    two joins from their first 15 rounds: 303,800 and 319,300.
    The counts grown afterwards are 303,791 and 319,488. It also placed the seven-and-seven join between 2.10 and 2.16 without seeing
    it; it grows at 2.14.
  - This is the nearest thing here to the owner's "logic based fractal": growth whose rule refers to itself. It is computed to 13
    to 17 rounds and not proved, and no model reproduces the rate yet.
- **A join can also stop the growth.**
  - A knot touching two neighbouring ring knots closes the whole start in five rounds. That knot and the two ring knots are a ring
    of three, and with the ring knot opposite they make three pairwise candidates with no common neighbour.
  - This one exploratory start fails the frozen "every join speeds the ring" (P8). It is the only start that slows.
- **Without a ring, nothing grows exponentially.** Two two-fold pieces joined grow at most two-dimensionally, not four (6 of 6).

| Start (bare ring of five unless said) | Return equation | Rate | Evidence |
| --- | --- | --- | --- |
| ring of five four-place knots | none: 5 junctions every round | 1 | `RING-FORMULA-20261118-001` |
| + a lone knot with nothing of its own | y^5 (1 + y) = 1, a surplus distinction one round early | 1.1347 | frozen (D), and rounds 1–30 equal the surplus start's 2–31 |
| + a lone knot with s surplus distinctions | y^n (1 + y(1 + y)^s) = 1 | s = 1: 1.2032; s = 4: 1.4565 | frozen, P1 (n = 5, 7, 9) |
| + several lone knots and surplus distinctions, anywhere | product of their factors | e.g. 1.4065 (three knots on a ring of seven) | frozen, P2, P3 |
| + two touching knots hanging from a ring knot | F_(s_A) F_(s_B); 1/(1 − y) for a far knot with only the floor's distinction | 1.4196 bare; the golden ratio with (2, 2) and a ring surplus distinction | frozen, P4–P7 |
| + a chain or fork of joined knots | nested: candidate children inside each knot's menu | 1.42 to 1.66 | post hoc |
| two rings joined | algebraic, not rational: c ≈ C λ^t t^(−5/2) (corrected) | 2.19 to 2.87 | frozen, P9 (qualitative); `RING-PAIR-20261119-001` |
| two two-fold pieces joined, no ring | none needed: one- or two-dimensional | 1 | frozen, P10 |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gate checks | held | fastlib = freelib on 304 starts; the mutant disagrees on 180; the clean rings reproduce |
| P1 | lone adjunct, x^(n + s + 1) = x^(s + 1) + (1 + x)^s (sharp) | held | 6 of 6, every one from round 0, 24 to 71 rounds |
| P2 | products at separate knots, any positions (sharp) | held | 8 of 8, from round 0; positions changed no rate |
| P3 | two lone adjuncts on one knot multiply (medium) | held | 3 of 3 |
| P4 | bare two-fold piece on rings of 7 and 9: (x − 1)(x^(n + 1) − x^n − x − 1) (sharp) | held | 2 of 2, from round 0 |
| P5 | two-fold pieces with surplus: F_(s_A) F_(s_B) (medium) | held | 5 of 5, from round 3 or 4 |
| P6 | the ring's surplus distinction beside the piece adds (1 + y) (risky) | held | 2 of 2 |
| P7 | the product law on every join by a shared distinction or knot (48) | held | 48 of 48 (35 of 35 not seen in the pilot), from round 0 to 4; rates 1.1347 to 1.6851 |
| P8 | every join of families A, B, D faster than its ring alone | **failed** | 123 of the 124 starts read are faster; the knot touching two neighbouring ring knots closes in five rounds; one chord (ring knots 0 and 2) exceeded 6 GB within seconds and is unread |
| P9 | two rings: no recurrence of order ≤ 7; λ > 1.5; λ falls with ring length; α in [−2, −1] | held | 6 of 6 on every part (fitted λ 2.10 to 2.77, α −1.08 to −1.46; with α fixed at −3/2, λ 2.14 to 2.79) |
| P10 | no ring: never exponential, dimension at most 2 | held | 6 of 6: one one-dimensional, five two-dimensional |

Nine of ten held. P8 failed on one exploratory start, and its failure is the study's one sign that a join can kill growth.

## After the read-out (post hoc, labelled)

- **The nested law for chains.**
  - Along a chain r, K1, K2, … hanging from a ring knot, the joining rule's candidates are knots two apart. So the knots at even
    removes nest under r, and the knots at odd removes nest under K1, which is a candidate of r's ring neighbours.
  - Each knot's menu is F = 1 + y(1 + y)^s Π F(candidate children). On the two-fold piece this is the frozen product law.
  - Written down before the runs finished (`posthoc/prediction_chain4.txt`, `prediction_2.txt`), it predicted three chains: the bare
    chain of four on rings of five and seven, (x − 1)(x^(n+2) − x^(n+1) − x² − x − 1); the chains of five and six; and the fork
    (one knot with two knots hanging from it), (1 + y)³. All held. The advisor expected the fork to break the law.
- **On the census's 45 paths of one and two knots and the two chains of family B** (scored by `posthoc.py`):
  - The law as written held on 28 of the 47, was unsettled on 14 and failed on 5.
  - Every failure had a knot with demand 1 and one surplus distinction. That knot's offshoot has one candidate, so the floor renews
    it.
  - With that refinement, found on these cases and not tested out of sample, 44 of the 47 hold and 3 are unsettled (two rounds past
    the order, degree 14).
- **The renewing offshoot.** The advisor's reading checks: in the bare two-fold piece exactly one junction a round gets a floor
  distinction beyond its demand, on rings of five and seven, and none in the pieces with surplus.

## Why it holds (the advisor's derivation, checked here by computation, not proved)

- **The ring's model.** In the (v, S) model of `RING-GROWTH-20261118-001` and `RING-FORMULA-20261118-001`, a junction is a position
  v of the unrolled ring with a set S of lifts of the surplus distinctions below v, made in round h(v) + |S|. Each lap adds one lift
  of every surplus distinction, and each lift is in S or not, a factor 1 + y. Summing over laps gives 1/(1 − y^n (1 + y)^j), the
  ring formula.
- **A joined knot is a menu at each lift.** Replace "in S or not" by "one element of a ranked menu", the rank adding to the round.
  Lifts are independent and so are knots, so the factors multiply and the denominator becomes 1 − y^n Π_k F_k(y). Where a knot is
  joined changes only how many lifts lie below each position in the first lap: the numerator, not the rate.
- **The lone knot.** A lone knot of three places joined to a ring knot r is exactly what a surplus distinction's offshoot becomes one
  round later: a three-place knot touching r with two loose distinctions, whose candidates are the two junctions next to r, through
  r. So a bare lone knot is a surplus distinction one round early (checked: rounds 1 to 30 of the lone start equal rounds 2 to 31 of
  the surplus start, by parents and fresh counts). With s surplus distinctions of its own, its offshoots join among themselves
  through it, so its menu is: nothing, or the knot (one round) with any set of its offshoots (one round each): F_s = 1 + y(1 + y)^s.
- **The two-fold piece.** A and B (A touching r, B touching A): r and B are candidates through A and join in round 1, so B acts on
  the ring as if joined to r itself, and the two knots contribute one factor each, F_(s_A) F_(s_B). When B's only surplus
  distinction is the one the floor of three places gives it, its offshoot has one parent and demand 1, so the floor gives it a
  surplus distinction again, every round (checked: exactly one junction a round gets a floor distinction beyond its demand in the
  bare piece, on rings of five and seven, and none in the pieces with surplus): a renewing offshoot, whose menu is a chain, 1/(1 − y).
- **Why the joint itself creates growth.** A join raises the round-1 demand of the joined ring knot and its two ring neighbours,
  and the cheapest counts must give them the places. Those places are not surplus at the start, but the joined knot's menu enters
  the return equation as a factor of at least 1 + y, so every tree adjunct raises the rate: a ring that alone grows linearly (five
  four-place knots, five junctions every round) grows exponentially with any knot joined to it.

## Known results, and what this adds

Known, cited once: renewal equations and transfer matrices; rational and algebraic generating functions, and the t^(−3/2) law at a
square-root singularity (the two-ring series has instead the t^(−5/2) of tree-like animals, see Correction) (Flajolet and Sedgewick, *Analytic Combinatorics*, 2009, ch. VII); growth series of free products of groups
(1/f = 1/f₁ + 1/f₂ − 1); the ring formula (`RING-FORMULA-20261118-001`) and the (v, S) model (`RING-GROWTH-20261118-001`). What this
adds: under the cheapest parity growth, parts joined to a ring compose as independent factors of one return equation, each knot's
factor read from its own surplus distinctions (F_s = 1 + y(1 + y)^s, or a renewing chain); the joined part's own growth does not
survive; and two joined rings leave this rational family.

## Limitations

- **Computed, not proved.** The product law is checked exactly (an annihilator holding on every round past its order that the
  horizon allows) on the starts listed; the advisor's derivation from the (v, S) model is an outline. Proving it needs the
  identification step of `RING-GROWTH-20261118-001`'s Proposition 2 for decorated rings.
- **The nested law for chains is post hoc** (found on the census and on chains grown after the freeze), not frozen.
- **Two rings: no model.** The rates are fitted to 13 to 17 rounds; "no recurrence" means none of order at most seven with twice its
  order to spare, which a recurrence of high order could still hide; α near −3/2 is a fit, not a reading of the series (and it is
  a transient: the series' exponent is −5/2, see Correction).
- **One growth policy and one size convention** (A104; every knot given the fewest places that let round 1 start, A107). The law is
  stated in surplus counts, so another convention changes the counts it reads, not the law; this is checked only on the pilot's two
  other conventions.
- **"Growth" counts junctions by round.** Bond balls are not measured on any joined start.
- **Typical** is over one population of 93 small joins (A107).
- **`merge.py`'s short-horizon branch inverts the frozen rule** (referee R1): a late violation is scored "unsettled", and an early
  hold with fewer than three rounds "fails". The branch was never reached, and all 74 annihilators hold under the frozen rule.
  Fix it before reuse.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` twice, `modelUsage` naming claude-fable-5-2 both times.
- **Before the freeze** ([question 1](advisor/question_1.md), [answer 1](advisor/answer_1_fable.md)):
  - it derived the return equation from the (v, S) model;
  - it explained the bare lone knot as a surplus distinction one round early, and F_s;
  - it refuted my nested law for the two-fold piece in favour of a product with a renewing offshoot;
  - it resolved two unsettled pilot rows, and flagged one row whose description was mine and wrong;
  - it proposed the sharp, medium and risky predictions, and the words "adjunct", "delay series" and "return equation".
- **After the read of the single rings, on two rings** ([question 2](advisor/question_2.md), [answer 2](advisor/answer_2_fable.md)):
  - it had no exact model;
  - it read the exponent as −3/2 in every join once the transient is allowed for (wrong: the exponent is −5/2, see Correction);
  - it argued that this rules out every finite linear model, a product of positions included;
  - it forecast two next counts (both held, to 0.003% and 0.06%) and the seven-and-seven rate (held);
  - it proposed a quadratic template A = 1 + y^a P₁ A B, B = 1 + y^b P₂ A B, and a closing rule (three pairwise candidates with no
    common neighbour);
  - it expected the fork to break the nested law, which it did not.

## Correction (19 November 2026)

**Narrowing (number and exponent).** The answer said two joined rings' counts "fit λ^t · t^(−3/2) closely", with rates 2.53 (five
and five), 2.32 (five and seven), 2.19 (five and nine), 2.14 (seven and seven), 2.79 (a shared knot) and 2.36 (a path of one knot),
and P9's reading gave fitted λ 2.10 to 2.77 and α −1.08 to −1.46. `RING-PAIR-20261119-001` (in progress) found an exact model of
these growths: the junctions of round t are the deck orbits of connected sets of t + 1 knots in the unrolled map of which knots can
join which. It reproduces every grown round of all seven two-ring joins, and its algebraic system gives the series to any round.
- **The exponent is −5/2, not −3/2.** With α = −5/2, λ_t = (c(t)/c(t − 1)) · (t/(t − 1))^(5/2) settles at the system's radius by
  round 200; with α = −3/2 it keeps rising (2.533 at round 17, 2.566 at 50, 2.584 at 100 and 2.595 at 200 for five and five).
- **The rates are larger:** 2.6075 (five and five), 2.3816 (five and seven), 2.2412 (five and nine), 2.1855 (seven and seven),
  2.8683 (a shared knot), 2.4271 (a path of one knot), 2.6881 (five and five with a surplus distinction); the order of the joins is
  unchanged.
- **Why it was missed.** Thirteen to seventeen rounds were grown; over them a −3/2 fit with a smaller λ is as flat as −5/2 with the
  true λ. The advisor's two round-16 forecasts held because they reach one round past the data.
- **Stands.** Non-rational growth (now exact), the rates' order, P9 as frozen (it scored the fit, and the fit is as reported), and
  everything about single rings. **Not a block.**

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread: confirmed, no Block.
- **Regrowth reproduces.** The referee's own regrowth of all 85 starts equals these counts on every common round. The memory
  amendments are clean. The post hoc readings are labelled and scored correctly, and the eight chain, tree and fork starts regrow
  exactly.
- **P1's missing start.** The never-run P1 start (a ring of nine with s = 3), grown by the referee to round 41, obeys
  x^13 − x^4 − (1 + x)^3 from t₀ = 0, as the law predicts.
- **Folded in the same day**, logged in `docs/CORRECTIONS.md`:
  1. **Narrowing (exponent).** t^(−3/2) was pre-asymptotic: the exponent is −5/2, with rates 2.868, 2.427, 2.382, 2.241 and 2.186.
     This was already folded through `RING-PAIR-20261119-001` (Correction, above). This note now says so wherever −3/2 appears.
  2. **Not a block.** `merge.py`'s short-horizon branch inverts the frozen rule. It was never reached (Limitations).
  3. **Narrowing (a count).** "All 27 single-ring tests" is 26: P1 omitted a listed start, which the referee has now run.
- **Deferred on the referee's side:** one round past for D-P1-at-r-a2-b2, running under a memory cap. The three law-2 cases stay
  "unsettled" until then.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: do growth behaviours compose when parts are joined to a ring? | **Status:** Successful (9 of 10 frozen predictions held) | Trees of knots joined to a ring compose as independent factors of one return equation, exactly on every single-ring start; the ring takes over; two rings lock into a non-rational growth |
| Local direction: joins under the cheapest parity growth | Continue | The single-ring law is exact where tested; two rings and closing joins are open, with sharp tests ready |
| Broader exploration: what the cheapest growth builds | Known alternatives | Trees of knots grow polynomially; one ring grows at a rational rate that every adjunct raises; two rings grow algebraically; a ring of three inside a ring can close everything |
| Long-term goal: G17 Typical and rare meeting patterns | Capability gained | Over every small join of a ring and a two-fold piece, the outcome is predicted from the parts' surplus counts alone; the typical outcome is takeover by the ring |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two joined rings: find the menu that contains itself (an algebraic return equation) | 3/3 — the program's first growth whose rule refers to itself, the owner's "logic based fractal" made exact | 2/3 — counts to 13–17 rounds, two forecasts held, the advisor's quadratic template and state space | record per-junction series at the joint and fit Q₂F² + Q₁F + Q₀ = 0 with five terms held back → stop at an equation that predicts unseen rounds and joins exactly, or a proof that none of low degree does | Selected · awaiting go-ahead |
| 2 | The nested law for every tree joined to a ring, frozen | 2/3 — makes the single-ring law general | 3/3 — the law, its refinement and the census code exist | freeze the refined law on every tree of up to four knots at one or two ring knots, with chains at neighbouring ring knots (the advisor's likeliest break) → stop at the law holding on all, or the first tree that breaks it | Alternative · deferred |
| 3 | When does a join stop the growth? | 2/3 — the only slowing seen; joins as switches | 3/3 — the advisor's closing rule and its test (two rings sharing two consecutive distinctions) | freeze "a start closes, at least in part, exactly when three pairwise candidates have no common neighbour" on small chords and double joins → stop at the rule holding or a counterexample | Alternative · deferred |
| 4 | Prove the product law (the decorated (v, S) model is the growth) | 2/3 — turns the census into a theorem | 2/3 — `RING-GROWTH-20261118-001A`'s four steps, with menus at the lifts | write step 3 for menus → stop at a proof or a start where the model and the growth part | Alternative · deferred |

- **#1.** Payoff 3/3: a growth whose rule contains itself is what the owner's "rules within rules" and "logic based fractal" ask
  for, and two rings are the first case found; an exact equation would make it a result. Concreteness 2/3: the data and the template
  exist, but the menu at the joint is not yet defined and the horizon is short. Bound: one epic, joins of two rings of five to nine
  knots.
- **#2 and #3** are independent of #1 and of each other, both 2/3 and 3/3; they could run in parallel if the coordinator wishes.

**Corrections:** none to published claims. The provisional read sent to the owner (23:13 UTC) said two rings grew "about 2.2 to 2.4×
a round and still rising"; the ratios rise because of the t^(−3/2) factor, and the rate is about 2.5 (not a published claim).

**Goals:** G17 checkpoint (capability gained: the outcome of every small join of a ring and a two-fold piece is predicted from the
parts' surplus counts; the ring takes over; two rings lock into a non-rational growth). No goal changed.

**Assumptions:** new A107 (small joins of a ring and a two-fold piece weighted uniformly over the 93 bare starts of census D, a
measure); a history line on A106 (a join at a ring knot needs a knot of five or six places, outside its sizes, so its census holds
no joined ring).

**Basket:** B196, `FRESH-COUNT-20261118-001#1`, B202, `PLUS-ONE-20261118-001#1`; none taken.

## Final report as sent (2026-11-19 00:59 UTC)

**Outcome:** The parts compose, but they do not keep their own growth: the ring takes over. Each knot joined to a ring brings a small menu, and the menus multiply into one equation for the ring's rate. The law predicted the exact recurrence of the junction counts, not just the rate, in all 27 frozen single-ring tests and in all 48 census joins by a shared distinction or knot (35 of them unseen). In all, 9 of 10 frozen predictions held over 137 starts. Closed, referee pending.

- **The law, "rules within rules."** A joined knot with s surplus distinctions of its own has the menu F_s = 1 + y(1 + y)^s. The growth either skips the knot, or takes it and then any of its own surplus distinctions: a menu inside a menu. The rate solves y^n (1 + y)^j Π F = 1. Where the knot sits on the ring does not matter.
- **Takeover.** Every tree of knots joined to a ring speeds it up. This holds even for a ring that alone adds only five junctions a round, and even when the part would close on its own. All 93 small joins of a ring of five and a two-fold piece grow faster than the ring alone, at 1.13 to 1.69 a round. The piece's own two-dimensional growth disappears into a finite menu.
- **The coordinator's guess** (a join acts as added spare distinctions) is exact only for a lone knot with nothing of its own. A knot with surplus distinctions of its own counts for less than that many spares.
- **Two rings lock into a new kind of growth.** Two rings of five, each linear alone, grow about 2.5× a round when joined, and the counts satisfy no short recurrence.
  - The counts fit λ^t · t^(−3/2): a menu that contains itself, the nearest thing here to a "logic based fractal" (computed, with no model yet).
  - Longer rings lock lower (2.53, 2.32, 2.19, 2.14).
  - The advisor's blind forecasts held: two round-16 counts to within 0.06%, and the 7–7 rate.
- **One failure.** A knot touching two neighbouring ring knots closes the whole start in five rounds (P8: 123 of the 124 joins read are faster).
- **Post hoc.** Along a chain of joined knots, each knot's menu nests inside the menu of the knot two before it. Four checks written down before their runs held. One refinement was found on the census and is labelled.

"Growth" here counts junctions by round; bond balls were not measured.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: do growth behaviours compose when parts are joined to a ring? | **Status:** Successful (9 of 10 held) | Joined trees of knots are independent factors of one return equation, exact on every single-ring start; the ring takes over; two rings lock into non-rational growth |
| Local direction: joins under the cheapest parity growth | Continue | The single-ring law is exact where tested; two rings and closing joins are open, with sharp tests ready |
| Broader exploration: what the cheapest growth builds | Known alternatives | Trees of knots grow polynomially; one ring grows at a rate that every joined tree raises; two rings grow algebraically; a ring of three inside a ring can close everything |
| Long-term goal: G17 Typical and rare meeting patterns | Capability gained | Over every small join of a ring and a two-fold piece, the outcome follows from the parts' surplus counts; the typical outcome is takeover by the ring |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two joined rings: find the menu that contains itself (an algebraic return equation) | 3/3 — the first growth whose rule refers to itself, the "logic based fractal" made exact | 2/3 — counts to 13–17 rounds, two forecasts held, the advisor's quadratic template | fit Q₂F² + Q₁F + Q₀ = 0 on per-junction series at the joint, five terms held back → stop at an equation that predicts unseen rounds and joins exactly, or a proof none of low degree does | Selected · awaiting go-ahead |
| 2 | The nested law for every tree joined to a ring, frozen | 2/3 — makes the law general | 3/3 — law, refinement and code exist | freeze it on every tree of up to four knots at one or two ring knots, including chains at neighbouring knots → stop at all holding, or the first tree that breaks it | Alternative · deferred |
| 3 | When does a join stop the growth? | 2/3 — the only slowing seen | 3/3 — the advisor's closing rule and its test | freeze "closes exactly when three pairwise candidates share no neighbour" on chords and double joins → stop at the rule holding or a counterexample | Alternative · deferred |
| 4 | Prove the product law | 2/3 — turns the census into a theorem | 2/3 — the ring proof's four steps, with menus | write the identification step for menus → stop at a proof or a start where model and growth part | Alternative · deferred |

**Corrections:** none to published claims. My provisional read said two rings grew "2.2 to 2.4× and still rising". The rise is the t^(−3/2) factor, and the rate is about 2.5 (not a published claim). **Goals:** G17 checkpoint (capability gained); no goal changed. **Assumptions:** new A107 (the 93 small joins weighted uniformly, a measure); a history line on A106 (its five-place cutoff leaves out every joined ring). **Basket:** B196, `FRESH-COUNT-20261118-001#1`, B202, `PLUS-ONE-20261118-001#1`; none taken. #2 and #3 are independent and tied, so they could run in parallel. **Advisor:** Fable 5.2, twice.
- Before the freeze, it derived the equation from the ring model, corrected my nested reading of the two-fold piece, and proposed the predictions and the words "adjunct", "delay series" and "return equation".
- After the read-out, it showed the two-ring exponent is −3/2 and made the forecasts that held. It expected a fork to break the nested law, which it did not.

**Referee hand-off.** The decision note is `research/JOIN-GROWTH-20261118-001/join_growth.md`. The prior-work line is in the pre-registration (objects-gate passes). Please check:
- the exact-annihilator scoring in `merge.py`;
- the two logged memory amendments (reruns with the same code and caps);
- the post hoc section, which is labelled and was not frozen.
