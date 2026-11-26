# Is the sign about the model or about the order we supply? Pre-registration

Ticket `REORDER-CONFIRM-20261126-001` (item 2 of the coordinator's proposal of 26 November, approved by the owner: "Yes, take
them"; goals G5 Dynamics and G9 Witnesses; assumptions A275 and A276), 26 November 2026. Frozen before the code is written. Code
by this thread (Claude). The canonical K1–K3 test is unchanged.

It confirms or narrows `REORDER-SIGN-20261126-001` (the reordering-sign study: with one added rule, swapping two distinctions that
both hold 1 costs −1, a growth round's commit order carries the sign the three-detector experiment needs; six of seven frozen
predictions held and P7 failed, so its main finding was exploratory). That study's referee (report R1, confirmed with fixes, in
`research/REORDER-SIGN-20261126-001/referee-R1/codex/report.md`) rebuilt its numbers and found two things this design builds on:
at four readers the carrying orders are the four cyclic shifts of the parents' creation order, two of them odd, so "even" does not
extend; and the parents' creation order works as a reference only through the start's relative signs, which the parity rule alone
does not fix.

## The model (as in the predecessor, unchanged)

A parity knot on n old distinctions x_1, …, x_n (allowed words: even weight). One round gives each x_j one child: two fresh
distinctions y_j, z_j with y_j ⊕ z_j = x_j (a one-parent child of the parity round). The swap rule (A275) is the fermionic sign:
each distinction is a mode with creator c⁺ and annihilator c, and modes anticommute. The start is created by applying c⁺_{x_j} for
the occupied x_j in a stated order σ (σ_1 first), summed over even words with coefficient +1. The birth of child j is

K_j = (1 − n_j)(1 + c⁺_y c⁺_z) + n_j (c⁺_y + c⁺_z)   (normalisation dropped; all amplitudes are ±1)

applied in commit order π (a later birth acts on the left). Reader j (A276) has the ordinary reading Z_j = (−1)^{n_{x_j}} and the
flip F1_j = −i γ′_{x_j} γ_{y_j}, with γ = c + c⁺ and γ′ = i(c⁺ − c). The **full contradiction** is: every correlation
c(T) = ⟨F_T Z_rest⟩ over even-size sets T of readers is ±1 and T ↦ c(T) is not a character. (Once every c(T) is ±1 with the
polar form below, the second clause holds automatically for n ≥ 3; it is kept as a check.) The **target** for n readers is the
table of the reversal-signed n-knot, amplitude (−1)^{C(|x|,2)} on each even word x, read with Z and X: at n = 3 it is the 64-cell
target of `WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001`.

## Why P7 failed (an argument, checked as P1)

P7 predicted that once the swap rule also governs the readings, the table is the same for every commit order ("order is gauge").
Write K_j = E_j + O_j with E_j = (1 − n_j)(1 + c⁺_y c⁺_z), which has an even number of creators, and O_j = n_j(c⁺_y + c⁺_z), which
has an odd number. Even pieces commute with everything on other modes; O_i O_j = −O_j O_i; and O_i O_j is nonzero only where both
parents hold 1, where the E terms vanish. So, exactly,

K_i K_j = K_j K_i (−1)^{n_i n_j}.

Exchanging two births costs −1 exactly when both parents hold 1: the swap rule reappears on the parents, because a child's fresh
parity equals its parent's value. The listing (the order in which modes are written down, the literature's Jordan–Wigner order)
is a convention, and every table is the same under every listing. The commit order is not a convention: it is the order of
operations, and births whose parent holds 1 change parity, so reordering them changes the state. P7 treated the commit order as if
it were a listing.

## The account under test

Write everything in the listing in which each reader's three distinctions are adjacent (x_j, y_j, z_j). Then F1_j = X_{x_j}
X_{y_j}, the child's two fresh distinctions carry no sign, and the grown state reads as a three-reader (n-reader) signed knot with
amplitude (−1)^{C(|x|,2) + d(σ,π;x)} on old word x, where d counts the occupied pairs ordered differently by σ and π.

- **The reversal sign is the cost of the round.** C(|x|,2) appears because every parent is created before any child is born. If
  each child is born right after its own parent is created (depth-first), each reader's three distinctions are created together
  as an even block, blocks commute, and the sign is gone.
- **Which orders carry it.** A sign (−1)^q on the even words, read with real Z and X, carries the full contradiction exactly when q
  is quadratic with polar form q(x + t) + q(x) + q(t) equal to the dot product x·t on the even words (Dehaene and De Moor 2003;
  for even n the all-ones word is the dot form's radical and the all-reader flip is still ±1). C(|x|,2) has this polar form. The
  polar form of d vanishes on the even words exactly when the set of pairs ordered differently is a split of the readers into two
  groups with every pair across the split differing (a cut), and an order differing from σ by a cut is a cyclic shift of σ. So the
  carrying commit orders are the n cyclic shifts of σ, for every n ≥ 3; π = σ (first created, first born) gives the target with
  fixed labels; a shift by k gives it after relabelling the X outcomes of the k readers it moves (or, equivalently, of the others).
- **General schedules.** Take any sequence of the 2n events (each creation c_j and birth b_j, with c_j before b_j). For two
  occupied parents, disjoint or nested pairs of events cost nothing and crossing ones (c_i < c_j < b_i < b_j or the reverse) cost
  −1. With real readers a schedule carries the contradiction exactly when its crossing pairs, as a relation on the readers, differ
  from "every pair crosses" by a cut: the readers fall into at most two groups, every pair within a group crosses and no pair across
  groups does. The round structure with π = σ is "every pair crosses"; depth-first is "none crosses". The literature's name for
  this equivalence of relations up to a cut is Seidel switching.
- **The sign is a local adjustment.** On even words (−1)^{C(|x|,2)} = i^{|x|}, which is diag(1, i) at every reader: the reversal-
  signed knot with X is the unsigned knot with the complex reading Y (the predecessor's L1). So every statement here is relative to
  the fixed real readings. With the flip F3_j = i γ_{x_j} γ_{y_j} (Hermitian, Y on the old distinction), the carrying schedules are
  the other class: those whose crossing pairs form a cut, including depth-first and the cyclic shifts of the reversed σ.

## Prior work in the program

`python3 -B scripts/track.py objects "commit order of births cyclic rotation sign fermion" --until 2026-11-26 --exclude REORDER-CONFIRM-20261126-001 --limit 4`

`python3 -B scripts/track.py objects "sign of reordering births commit order exchange" --until 2026-11-26 --exclude REORDER-CONFIRM-20261126-001 --limit 4`

`python3 -B scripts/track.py objects "creation order of the start phase reference parity knot" --until 2026-11-26 --exclude REORDER-CONFIRM-20261126-001 --limit 4`

`python3 -B scripts/track.py objects "births anticommute parent holds 1 swap" --until 2026-11-26 --exclude REORDER-CONFIRM-20261126-001 --limit 4`

`python3 -B scripts/track.py objects "depth-first versus rounds order of creation" --until 2026-11-26 --exclude REORDER-CONFIRM-20261126-001 --limit 4`

- `REORDER-SIGN-20261126-001` — the predecessor: same model, same readers, same target; this study confirms or narrows it. Its
  referee report R1 is read and built on (the four-reader shifts, the start signs, the reader conventions).
- `WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001` — the signed preparation and its 64-cell target.
- `ROUND-FREE-20261119-001` — a relative: parity growth without rounds under serial orders, where order decides outcomes. A
  different object (a change of which births happen), not a sign on one outcome.
- `LOCAL-ROUND-20261123-001` — a relative: births one at a time from a record of parents reproduce the rounds in every order
  searched. It concerns which births happen; here every schedule makes the same births and only the sign differs.
- `DESCENT-HELD-20261125-001` — a relative: the order of descent is shown in a knot's places only where a ration writes it; bears
  on whether any record could fix a schedule (direction, not tested here).
- `IDLE-PHASE-AND-TREE-CLOSURE-20261121-001` and `ERASURE-AND-CLOSING-SIGNS-20261121-001` — relatives: supplied coherent references
  and sign-sensitive keepers.
- `INFLUENCE-CONE-20261120-001` — a relative: a round's commit order is free under the ordinary law.
- `REVIEW-LEADS-20261123-001`, `PARTS-MEET-AGAIN-20261124-001`, `PARENTS-FROM-HOLDERS-20261124-001`, `GROWTH-STATISTICS-20261121-001`,
  `FEEDER-PAYOFF-REVERSAL-20261121-001`, `JOINT-BRAID-READS-20261114-001`, `ODD-FAMILY-20261112-001`, `WHICH-SEQUENCES-20261112-001`,
  `SPACE-ORDER-20261117-001`, `TWO-BIT-ROWS-20261112-001` — unrelated (matched on "order", "birth", "swap", "cyclic", "rotation",
  "round" or "depth" only).

## Prior work outside the program

The swap sign is Jordan and Wigner's (1928); Bravyi and Kitaev (2002) give the occupied-swap sign and fermionic gates. Quadratic
phases on a code and their polar forms: Dehaene and De Moor (2003); graph states (Hein, Eisert and Briegel 2004). Relations up to a
cut: Seidel switching and two-graphs (Seidel 1976; Cameron). Inversion and crossing relations: permutation and circle graphs. The
reversal sign (−1)^{k(k−1)/2} is the Clifford reversion (Lounesto 2001). The contradiction: Mermin (1990); real amplitudes suffice
(McKague, Mosca and Gisin 2009); as an obstruction to a character, Abramsky and Brandenburger (2011) and Okay, Roberts, Bartlett
and Raussendorf (2017). No source known to us states the cyclic-shift class or the crossing criterion for this growth; both follow
from the pieces above.

## Predictions (frozen)

Engine checks are labelled: they can fail only through a fault of the code, and are there to catch one.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | **Gate (engine checks).** (a) An exact sparse fermion engine written here reproduces every recorded n = 3 row of the predecessor's `verify_fock.json` (correlations, product, full contradiction, scored win, words of the coherent sum; both parent orders; F1 and F2). (b) The anticommutation relations hold on every basis state at n = 3 under two listings. (c) A second code path built from sparse Jordan–Wigner matrices agrees with the engine on every table of P2 at n = 3 and 4 and of P5 at n = 3. (d) Listing is gauge: every table is the same under the ascending, block, reversed and 20 seeded random listings at n = 3 (all orders, both σ, F1, F2) and n = 4 (all orders, σ ascending, F1). | any fails |
| P1 | **Why P7 failed (engine check of the argument).** K_i K_j = K_j K_i (−1)^{n_i n_j} on every basis state at n = 3; for every pair of commit orders at n = 3 and 4, the two grown states differ word by word by (−1)^(number of occupied parent pairs they order differently). | any word differs |
| P2 | **Cyclic shifts (the main test).** For n = 3, 4, 5, 6 and σ ascending, descending and one seeded random order, over all n! commit orders under the round: exactly the n cyclic shifts of σ carry the full contradiction; π = σ matches the target on all 4^n cells with fixed labels; every other shift matches after relabelling the X outcomes of the readers it moves. n = 3 and 4 replay known results; 5 and 6 are fresh. | another order carries it, a shift does not, or π = σ is not exact |
| P3 | **General schedules.** Over all schedules at n = 3 (90) and n = 4 (2,520) and a seeded sample of 2,000 of the 113,400 at n = 5: with F1 a schedule carries the contradiction exactly when its crossing relation differs from "every pair crosses" by a cut; with F3, exactly when it differs from "no pair crosses" by a cut. The share of schedules that carry it under the uniform weighting over schedules is reported for n = 3 to 6 (exact counts of crossing relations; at n = 6 by full enumeration if a timed part puts it under ten minutes, otherwise a seeded sample of 200,000). | any schedule disagrees with its class |
| P4 | **Depth-first.** With each child born right after its parent is created: with F1, no contradiction for any σ (n = 3, 4, 5, all σ); with F3, every σ carries it. | either fails |
| P5 | **Start signs.** Convention: h(x) is the coefficient of c⁺_{i1} ⋯ c⁺_{ik}\|0⟩ with i1 < ⋯ < ik; anchor row: h = (+, −, −, −) on 000, 011, 101, 110 with π = abc carries and is exact. At n = 3, over the 8 sign patterns with h(000) = + and 6 orders: contradiction exactly when h_ab h_ac h_bc sgn(π) = −1, and 6 of the 8 patterns have an exact fixed-label order. At n = 4, of the 128 patterns: exactly 48 have a carrying order, each exactly one cyclic class of 4 orders; they are exactly the set given by the formula (log h quadratic on the even words with polar form equal to the dot product plus that of some order's inversions), computed before the runs; exactly 24 have an exact fixed-label order. | any count or set differs |
| P6 | **Swap rules.** (a) On one n-knot listed in all n! ways (n = 3 to 6), for each of the 8 sign rules giving a swap of two distinctions holding (u, v) the cost c(u, v) ∈ {±1} (c00, c01 = c10, c11): the listings that carry the contradiction are those of the fermion rule when c00·c11 = −1 and none when c00·c11 = +1 (the rule "pairs both holding 0" is the fermion rule; the others differ from it or from no rule by a relabelling or a global sign). (b) The phase family: weight s^(number of inverted occupied pairs) with s = e^{iθ}, θ = kπ/12: the full contradiction only at θ = π; at n = 3 the reversal's best score ⟨ZZZ⟩ − ⟨XXZ⟩ − ⟨XZX⟩ − ⟨ZXX⟩ over relabellings is 1 + 3(1 − cos θ)/2, above the local bound 2 exactly when cos θ < 1/3. | any differs |
| P7 | **Weightings of orders** (round, F1, σ ascending, n = 3 to 6). Uniform weighting over commit orders: n of n! carry it. The equal mixture of all orders: not every correlation is ±1. The coherent equal-weight sum: only the blank old word survives. The uniform joint weighting over (σ, π): the same share n/n!, since only the relative order enters (n = 3, 4). | any differs |
| P8 | **Reader conventions.** Each reader has a within-pair order (written c⁺_y c⁺_z or c⁺_z c⁺_y), a record (the fresh distinction its flip touches, y or z) and a flip (F1 or F2); it is *matched* when its flip is F1 exactly if its record is the left written creator. At n = 3 over all 512 assignments, 6 orders and σ ascending and descending, and at n = 4 over the 256 matched and 256 seeded unmatched assignments with all 24 orders (σ ascending): with every reader matched, the carrying orders are exactly the cyclic shifts of σ; with any reader unmatched, no order carries it; for matched assignments a fixed-label exact order exists exactly when the set of readers with F2 or its complement is σ_1, …, σ_k for some k, and it is then the shift by k. With F3 at every reader (record y, written c⁺_y c⁺_z), the carrying commit orders are the cyclic shifts of the reversed σ. | any differs |

Not run: a second growth round (a grandchild's reader would have to flip three distinctions, an odd number, so no local even flip
exists and the reader would have to be redefined: a new scaffold, not a replay); squared weights other than equal magnitudes (A144
is only exercised at equal magnitudes).

## Verdict rule

- If P2 (at n = 5 and 6), P3 and P4 hold: the sign is a property of the schedule of creations and births, measured against a fixed
  real reader convention. The study then says so plainly: **it is about the orderings supplied** (the start's creation order and the
  commit order, or in general the schedule), with the swap rule as an added scaffold. The share under the uniform weighting over
  schedules is the number reported as "how often", with its weighting named. The rounds of the growth law are one schedule class
  among several; depth-first is another and gives no sign with the real readers, so the round structure is itself an ordering, not
  an order-free source.
- If P2 fails at n = 5 or 6 or P3 fails anywhere: the cyclic or crossing account is wrong, and the result depends on something more
  than the relative order; report what.
- If P4 fails with F1 (depth-first carries with real readers): the round structure is not the source of the reversal sign.
- Any other failure is reported as a failed prediction; the predecessor's numbers stand or fall with the gate.

Stop after the gate and P1–P8. A **GO** for the line needs a native rule that fixes the schedule (a record of the program that
makes FIFO or depth-first follow from the growth), named as a separate direction; without one the order line **STOP**s.

## Runs and stop rule

Exact integer arithmetic: amplitudes ±1 on at most 2^{n−1}·2^n = 2,048 basis states (n = 6), correlations as fractions. At most
720 commit orders, 2,520 schedules plus a sample of 2,000 at n = 5, 4,096 matched or sampled reader assignments at n = 4, and the
crossing-relation count at n = 6 (7,484,400 schedules, combinatorial only). The first small case is timed before the rest; the
expected total is a few minutes, one process, under 2 GiB. If any part times over ten minutes it is registered in
`docs/LONG_RUNNING.md` and run through the shared runner.

## What this cannot show

No claim about physical fermions, about exchange statistics as distinct from one CZ per crossing (A275), about physical time, or
about any growth law other than one round of one-parent births of a parity knot. "n of n!" and the share over schedules hold only
under the uniform weightings named. "Unique among sign rules" covers only the eight rules whose cost depends on the two
distinctions' holdings. Nothing here supplies a rule that fixes the schedule.

## Review before the freeze

The advisor model was consulted on a draft of this design. It found no error in the argument for P7's failure, the cyclic-shift
class, depth-first, the start-sign counts or the weightings; it pointed out that the non-character clause is redundant, that the
start-sign rule depends on a basis convention (frozen above with an anchor row), that the linear part of a sign rule is a
relabelling and not nothing, that a phase per swap is only well defined as a power of the number of inversions, that several
predictions are engine checks (labelled), and that P2 must cover every order at n = 5 and 6. It proposed the general schedules
(P3), the complex flip F3 and the point that the sign is a local adjustment at every reader, so that every "no contradiction"
means "none with the real readings", and it named Seidel switching. Its answer is a colleague's view; the run checks it.
