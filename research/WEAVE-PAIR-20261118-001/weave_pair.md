# The surviving weave pair, with the twist fixed

Epic `WEAVE-PAIR-20261118-001`, 18 November 2026, by Claude, on the coordinator's queue. It is the first direction of
`WEAVE-MIX-20261117-001` after that study's referee. Goals G1 and G16; tests A97. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `2790acb70` at 01:35:56 UTC. The three parts ran from
  01:35:56 to 01:56:19 UTC.
- Code: [twistlib.py, run.py and checks.py](../../experiments/WEAVE-PAIR-20261118-001B/WEAVE-PAIR-20261118-001B-E001_twist/).
- Results: [results.json](../../artifacts/WEAVE-PAIR-20261118-001B/WEAVE-PAIR-20261118-001B-E001_twist/results.json).

## The answer

**The pair is one arrangement, and it is genuinely disordered on the weave, in both twist sectors to width 21. But the distance
its pair counts give is a ruler only in envelope: it decays at one steady rate while oscillating, so it does not step outward
without skipping.**
- **One, not two.** A half-turn of the weave, with a shift of two columns, carries the first arrangement's disagreeing bonds onto
  the second's. The two differ only by one seam per three columns, where the knots read the values flipped. So with an even number
  of periods around the cylinder they have identical spectra, and with an odd number each one's periodic spectrum is the other's
  twisted one. This held to every printed digit at widths 6 to 21.
- **Disordered, with the twist fixed.**
  - In both sectors the spin gap is 0.314 to 0.316 and the energy gap 0.630 at widths 15, 18 and 21. The energy gap is twice the
    spin gap, the threshold of two excitations.
  - There are 1.2631 states per distinction.
  - The splitting between the sectors shrinks from 1.7 × 10⁻³ at width 12 to 6.4 × 10⁻⁵ at width 21, about threefold for every
    three columns. That is exponential decay, the signature of a gapped, disordered phase rather than a critical or ordered one.
  - Moving the seam one column changes nothing.
- **A ruler only in envelope.**
  - At width 12 the correlation along the transfer, from which the pair-count distance is read, decays at exactly the spin gap.
    The fitted slope of its log on rows 10 to 30 is 0.3171 against a gap of 0.3170, at two of the three positions in the period.
  - But the top flip-odd eigenvalue comes as a pair of equal magnitude, so the correlation oscillates as it decays.
  - At single-row resolution its size never decreases strictly, at any position or in either sector.
  - Even the two-row tick, declared in advance as an envelope reading, holds only at two positions in the periodic sector. It
    fails at the third position, and at every position in the twisted sector, where the correlation crosses zero.

In the owner's terms: on the weave there is now a base whose distance carries all its information (pair counts determine it, for
this class of knots) and decays at a fixed rate from any start, about 2.9 rows per factor of e. It is the first such base found on
this pattern. But it skips: farther is not always less alike, because the likeness oscillates. A distance that both carries the
information and steps outward strictly is still not found. This is the third case in envelope only, after OR and hard hexagons,
and the first that carries all the information.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| Q1 | A point symmetry carries arr1's inconsistent bonds onto arr2's | held | the half-turn, shifted two columns |
| Q2 | Same spectra at w/3 even; arr1 twisted = arr2 periodic at w/3 odd | held | to every printed digit, widths 6 to 21 |
| Q3 | Gapped in both sectors at 15, 18, 21 (5%) | held | spin 0.3143, 0.3157, 0.3150 (periodic) and 0.3161, 0.3148, 0.3154 (twisted); energy 0.630 |
| Q4 | Sector splitting shrinks at least threefold from width 12 to 21 | held | 1.66 × 10⁻³ to 6.44 × 10⁻⁵, 26-fold |
| Q5 | Single-row ruler fails at positions 0 and 2; the two-row tick holds everywhere | **failed** | single-row fails everywhere; the two-row tick holds only at positions 0 and 2, periodic |
| Q6 | Slope of τ on r = 10 to 30 within 10% of the width-12 spin gap everywhere | **failed** | 0.3171 against 0.3170 at positions 0 and 2, periodic; 0.24 at position 1; 0.35 and 0.17 twisted |

4 of 6 held. The two failures are one finding: the leading correlation is an oscillating pair, which a fit window of 20 rows on a
width-12 cylinder does not average out at every position.

## What the knot picture explained

- **Why one arrangement.** A half-turn of the weave exchanges up and down knots and reverses the columns. The rest is a seam of
  flipped readings, which the gauge removes when the number of periods around is even.
- **Why disordered.** Each period has a distinction that meets an odd number of disagreeing bonds, so the matching graph is not
  bipartite (`WEAVE-MIX-20261117-001A`, N4). That is the case where Fendley, Moessner and Sondhi found gapped dimers on the
  triangular lattice.
- **Why it skips.** The slowest way a disagreement spreads along the cylinder comes as a pair with opposite phases, so likeness
  falls off in waves. A distance that only falls in envelope cannot say "farther" at every step.

Known mathematics, labelled: dimer liquids on non-bipartite lattices (Fendley, Moessner and Sondhi 2002), twisted boundary
conditions and the exponential sector splitting of a gapped phase. Local: the pair, its identification, and the ruler reading in
the program's terms.

## What it means for A97 and the goals

- **A97** stays under challenge. On the weave a base whose distance carries all its information, and decays at a fixed rate, now
  exists. It steps outward only in envelope, so the strict premise is still unmet there.
- **G1:** obstruction learned. The best periodic candidate is a ruler only in envelope.
- **G16:** capability gained. Twist sectors, the splitting diagnostic and the identification of the pair.

## Limitations

- Correlations were exact at width 12 only; at width 21 only the gaps were computed.
- One arrangement up to symmetry; the random 10% mix of signed knots is untested here.
- "Ruler" is read from the spin correlation along the transfer. Other pairs of distinctions were not read.

## Reproduce

```sh
cd experiments/WEAVE-PAIR-20261118-001B/WEAVE-PAIR-20261118-001B-E001_twist
../../../.venv/bin/python -B checks.py
for P in W1 W2 W3; do ../../../.venv/bin/python -B run.py --part $P; done
../../../.venv/bin/python -B run.py --merge
```

## Advisor

Consulted before the freeze. It found the half-turn with a seam, and predicted the gaps and the single-row failure. It asked for:
- the frozen fit window;
- the two-row tick declared in advance;
- the splitting diagnostic;
- more Arnoldi eigenvalues.

Its two-row-tick prediction failed. Not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: settle the 3 × 1 pair | **Status:** Successful (referee pending) | One arrangement; gapped in both sectors to width 21 with exponential sector splitting; a ruler only in envelope; 4 of 6 held |
| Local direction: a distance that carries information and steps outward on the weave | Narrowed | The one periodic candidate oscillates |
| Broader exploration: a strict ruler with full information | Unexplored | Needs a base whose slowest mode is a single real one |
| Long-term goal: G1 | Obstruction learned | The best candidate on the weave skips |

**Next step:** Research directions. The coordinator has queued direction 2 of `CUBE-DOUBLING-20261118-001` next.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A law whose free room runs only along two orders (from `CUBE-DOUBLING-20261118-001`) | 3/3 | 2/3 | Characterise which combinations stay forceable when certificates may use only adjacent pairs → stop at a law or an obstruction | Selected (coordinator) |
| 2 | The random 10% mix of signed knots, with the twist fixed and correlations measured | 2/3 | 2/3 | Lyapunov gaps and correlations in both sectors → stop at its class and ruler reading | Alternative |
| 3 | Which periodic arrangements have a single real slowest mode: a strict ruler with full information | 2/3 | 1/3 | Scan the odd-count families for a real leading odd eigenvalue → stop at one or an obstruction | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (obstruction learned) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 under challenge, with this case; no new entry.

**Basket:** read; nothing taken.
