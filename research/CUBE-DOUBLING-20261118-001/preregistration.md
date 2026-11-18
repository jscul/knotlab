# Why the cheapest growth gains an order at each doubling: pre-registration

Epic `CUBE-DOUBLING-20261118-001`, 18 November 2026, by Claude, on the coordinator's queue. This is Codex's priority 2, passed on
by the owner. Goals G1 and G16; tests A99. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

`STATE-RULES-20261117-001` computed that the cheapest growth with up to three betweenness knots per step reaches the cube Q_d at
n = 2^d: to d = 4 in 40 of 40 runs, and to d = 5 in 5 of 5 (its stress test). It left the general claim, S6, as a conjecture.

Here S6 must be proved, every missing combination being filled before a new split is needed, or a reachable exception found.

## Ticket A: the proof (written before this freeze)

`proofs/CUBE-DOUBLING-20261118-001A/CUBE-DOUBLING-20261118-001A-P001_cube_doubling/proof.md`:
- **L1.** Zero-cost steps are fills of unoccupied orientations.
- **L2.** When three knots force an orientation.
- **L3.** Certificates survive fills.
- **L4.** The cheapest steps from Q_s are the s·2^(s−1) subdivisions and the 2^s pendants.
- **L5.** After either, every unoccupied orientation has an explicit three-knot certificate.
- **The theorem.** Q_d at n = 2^d for every d, in every run and for every tie rule.

## Ticket B: the frozen check

`experiments/CUBE-DOUBLING-20261118-001B/CUBE-DOUBLING-20261118-001B-E001_certificates/check.py`, building on
`STATE-RULES-20261117-001B-E001`'s `rules.py` (closed, pinned by hash).
- **D1.** For s = 1 to 7 and both classes, every certificate of L5. Each must give a zero-cost admitted fill that is not a copy,
  the fills must be distinct, and their number must equal 2^(s+1) − 2^s − 1.
- **D2.** For s = 2 to 4, every admitted extension of Q_s with up to three knots, enumerated by brute force over knot sets.
- **D3.** The exact distribution of the cheapest rule from one knot to n = 20.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | D1: for every s = 1 to 7 and both classes, no certificate fails, and the distinct fills number 2^(s+1) − 2^s − 1 (1, 3, 7, 15, 31, 63, 127) | any failure or a short count |
| P2 | D2: from Q_s no extension costs nothing, and exactly s·2^(s−1) + 2^s cost N + 2 (8, 20, 48 for s = 2, 3, 4) | otherwise |
| P3 | D3: at every n from 4 to 20 the base has 2⌈log₂ n⌉ + 2 states with probability 1, and it is Q3 at n = 8 and Q4 at n = 16 with probability 1 | otherwise |

**What would count against the theorem.**
- A certificate that fails.
- An N + 2 extension of Q_s that is neither a subdivision nor a pendant.
- An exact run that adds a split before the cube is full.

Any of these is a reachable exception to look for.

**Disclosure.** While sizing D3, I printed the exact run's class counts to n = 16. There is one class at n = 16, so P3's last clause
was seen before the freeze. The proof was written independently of it, and the run to n = 20 is new.

The advisor checked the proof before this freeze. It found no error in the certificates or the induction, and asked for three
added lines (L4's use of A99, L2's no-doubling line, the theorem's use of existence only) and the base case from Q₁. All four are
in. It rates the folklore risk moderate to high.

## Prior work

- `STATE-RULES-20261117-001`: S1 to S5, the runs to n = 16 and the stress test to n = 32.
- `KNOT-CAP-20261117-001`: its consultation gave the forcing restatement used in L2.

## Runs and stop rule

One script, `check.py`, one process. The study stops after its read-out, followed by the decision note, the referee hand-off and
the report.
