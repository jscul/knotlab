# Does one formula give the growth rate of every ring of knots?

Epic `RING-FORMULA-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead for `RING-GROWTH-20261118-001`'s
direction 2. Goal G17. **Referee pending.**

**Record.** Proof: [proof.md](../../proofs/RING-FORMULA-20261118-001A/RING-FORMULA-20261118-001A-P001_formula/proof.md). Code:
[formula.py, check.py, ring.py](../../experiments/RING-FORMULA-20261118-001B/RING-FORMULA-20261118-001B-E001_formula/). Results:
[results.json](../../artifacts/RING-FORMULA-20261118-001B/RING-FORMULA-20261118-001B-E001_formula/results.json). No new
pre-registration: the formula is the advisor's, frozen in `RING-GROWTH-20261118-001`'s pre-registration, and this study proves it
and checks it on 17 rings chosen before any was grown.

## The answer

**In the owner's terms.**
- **Yes, for every ring of an odd number of knots, five or more.** Say a ring of n knots has j spare distinctions in all (a
  five-place knot has one, a six-place knot two). Under the cheapest counts, the junctions made in round t are then a fixed mix of
  those made n to n + j rounds earlier: c(t) = Σ_i C(j, i) c(t − n − i). The growth rate is the root above 1 of
  x^(n+j) = (1 + x)^j. Where the spares sit on the ring changes the early rounds, not the rate.
- **Each spare distinction adds one way to grow per lap.** Going once round the ring raises the number of independent ways above
  each position by exactly j. A lap costs n rounds, plus one round for each new way taken. That is the folded, overlapping structure
  of `RING-GROWTH-20261118-001`, now with any number of spares.
- **The ring of five five-place knots, every round.** Every knot has a spare. Every position of the growth then lies above as many
  spares as its round plus one, and the junctions made in round t are exactly 5 × F(t + 2): 5, 10, 15, 25, 40, 65, 105, 170, …,
  with F the Fibonacci numbers. This is proved for every round, not only after a transient, and the grown ring matches it in every
  round computed. Any odd ring with a spare at every knot gives n × F(t + 2) and grows at the golden ratio.
- **Why rings of three, four and six are different.** The joining rule pairs knots two apart along the ring.
  - On an odd ring of five or more knots, "two apart" goes once round all of them, so the growth is a single winding.
  - On a ring of three, all three knots join at once: the crossed start of `FIRST-KNOT-20261118-001`, three-dimensional.
  - On a ring of four, opposite knots have two common neighbours, so each knot joins once instead of twice.
  - On a ring of six, "two apart" splits the knots into two triples, each joining as one group of three.
  - So rings of four and six leave a surplus offshoot at every knot and grow polynomially, not exponentially.
  - Even rings of eight or more split into two windings of half the length, each with its own spares. This is computed for eight
    and not proved.

**In standard terms.** For an odd cycle of n ≥ 5 even-parity constraints with j extra variables in all, under the complete-round
joining policy and the fewest counts, the model's count c(t) = Σ_v C(m(v), t − h(v)) satisfies c(t) = Σ_i C(j, i) c(t − n − i)
after a transient (Vandermonde's identity), and the growth rate is the unique root above 1 of x^(n+j) = (1 + x)^j. With one extra
variable at every constraint, m(v) = h(v) + 1 and c(t) = n F(t + 2) for every t (diagonal sums of Pascal's triangle). The growth is
the model by `RING-GROWTH-20261118-001A`'s identification, whose four steps do not use j = 1, and the counts agree on 17 rings.

## The check

Each ring grown 13 rounds and compared with the model's count in every round; the recurrence and the rate then tested on the model
to round 80.

| Ring (places of each knot) | n | j | Grown = model, 13 rounds | Recurrence holds from round | Rate predicted | Ratio at round 80 |
| --- | --- | --- | --- | --- | --- | --- |
| 4,4,4,4,5 | 5 | 1 | yes | 6 | 1.1347 | 1.1354 |
| 4,4,4,5,5 | 5 | 2 | yes | 7 | 1.2628 | 1.2629 |
| 4,4,5,4,5 | 5 | 2 | yes | 7 | 1.2628 | 1.2636 |
| 4,4,4,4,6 | 5 | 2 | yes | 7 | 1.2628 | 1.2638 |
| 4,4,5,5,5 | 5 | 3 | yes | 8 | 1.3854 | 1.3854 |
| 4,4,4,5,6 | 5 | 3 | yes | 8 | 1.3854 | 1.3852 |
| 4,5,5,5,5 | 5 | 4 | yes | 9 | 1.5036 | 1.5036 |
| 5,5,5,5,5 | 5 | 5 | yes: 5 F(t + 2) | 10 | 1.6180 | 1.6180 |
| 4,4,4,4,4,4,5 | 7 | 1 | yes | 8 | 1.0970 | 1.0918 |
| 4,4,4,4,4,5,5 | 7 | 2 | yes | 9 | 1.1903 | 1.1902 |
| 4,4,4,4,5,4,5 | 7 | 2 | yes | 9 | 1.1903 | 1.1905 |
| 4,4,4,5,4,4,5 | 7 | 2 | yes | 9 | 1.1903 | 1.1898 |
| 6,4,4,4,4,4,4 | 7 | 2 | yes | 9 | 1.1903 | 1.1933 |
| 4,4,5,5,5,4,4 | 7 | 3 | yes | 10 | 1.2806 | 1.2804 |
| 5,5,5,5,5,5,5 | 7 | 7 | yes: 7 F(t + 2) | 14 | 1.6180 | 1.6180 |
| eight four-place knots and one five-place knot | 9 | 1 | yes | 10 | 1.0758 | 1.0830 |
| seven four-place knots and two five-place knots | 9 | 2 | yes | 11 | 1.1493 | 1.1460 |

In all 17 rings the recurrence holds on the model from round n + j, earlier than the proof's bound of about 3n + j. The ratio of
successive counts still oscillates at round 80 for the long rings with few spares (n = 7 and 9, j = 1). The recurrence's other
roots are close to the leading one in size there, so the ratio settles slowly; the rate is the leading root because the recurrence
is exact.

## Known results, and what this adds

Known: Vandermonde's identity; the diagonal sums of Pascal's triangle are the Fibonacci numbers; cube completion of products. What
this adds: the growth rate of the cheapest parity growth of every odd ring of knots, from the ring's length and its number of spare
distinctions alone, and the ring with a spare at every knot as an exact Fibonacci growth in every round.

## Limitations

- The identification of the growth with the model is proved in outline: its third step, the groups as the lower covers of one
  element, is written at the level of the predecessor's lemma, as in `RING-GROWTH-20261118-001`. Here it is checked by counts on
  17 rings to 13 rounds; graph isomorphism was checked only for the ring with one spare (`RING-GROWTH-20261118-001`).
- Even rings of eight or more: one ring computed, not proved.
- Rates count junctions per round; bond balls are not measured.
- The advisor was not consulted again; the formula and its predictions are its answer from `RING-GROWTH-20261118-001`.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: one formula for every ring of knots | **Status:** Successful | For odd rings of five or more, x^(n+j) = (1 + x)^j is proved through the model and matched on 17 rings; the ring of five five-place knots is 5 F(t + 2) every round |
| Local direction: rings of knots under the cheapest counts | Practically exhausted | Odd rings are solved; rings of three, four and six are explained; even rings of eight or more are one proof away |
| Broader exploration: what the cheapest growth builds | Known alternatives | Trees of knots grow polynomially; rings grow at this formula; chains born apart combine by `PLUS-ONE-20261118-001`'s link |
| Long-term goal: G17 Typical and rare meeting patterns | Capability gained | The census's rare exponential growth is predicted from a ring's length and spares alone |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Serial growth read from distances (`FRESH-COUNT-20261118-001#1`) | 2/3 — tests A104, on which every growth result of this line rests | 2/3 — moves and reader exist | compare its descent orders with the complete round's on seeds of three to five → stop at a proof they agree, or a seed where they differ | Selected · awaiting go-ahead |
| 2 | Even rings: prove the split into two windings of half the length | 1/3 — completes the ring formula | 3/3 — the model for even n | write the model for even n ≥ 8 → stop at a proof or a ring that breaks it | Alternative · deferred |
| 3 | The second link of the chain rule (`PLUS-ONE-20261118-001#1`) | 1/3 | 3/3 | as before | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** none new. **Basket:** B196,
`FRESH-COUNT-20261118-001#1`, B202, `PLUS-ONE-20261118-001#1`; none taken. **Advisor:** not consulted in this study.

## Final report as sent (2026-11-18, with the closing commit)

**Outcome:** One formula gives the growth rate of every ring of an odd number of knots, five or more: the root above 1 of
x^(n+j) = (1 + x)^j, with n the ring's length and j its spare distinctions. No ring broke it; all 17 grown rings match the model
in every round. Closed, successful, referee pending.

- **Each spare adds one way to grow per lap.** A lap of the ring costs n rounds, plus one for each new way taken. Where the spares
  sit changes the early rounds, not the rate.
- **The ring of five five-place knots is 5 × Fibonacci in every round** (5, 10, 15, 25, 40, 65, …), proved, not only in the long
  run. Any odd ring with a spare at every knot grows at the golden ratio.
- **Rings of three, four and six are different.** The rule joins knots two apart. On three knots all three join at once; on four,
  opposite knots share two neighbours; on six, the knots split into two triples. Each leaves surplus offshoots, and the growth is
  polynomial. Even rings of eight or more split into two windings of half the length (computed, not proved).

The position table and the ranked directions are above. Referee hand-off: the decision note is
`research/RING-FORMULA-20261118-001/ring_formula.md`.
