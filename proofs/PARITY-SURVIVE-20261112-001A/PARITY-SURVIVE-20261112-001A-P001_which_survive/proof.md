# Which parity placements survive

Status: Exact on the frozen range (lemma A as a census; every placement on 3 × 3 and 4 × 4; placements with each cell parity with
probability ρ to 9 × 9, the last part stopped at its cap with 55 of 56 cells); **referee pending** (the background referee thread).
Ticket A of `research/PARITY-SURVIVE-20261112-001/preregistration.md`, frozen with the code in commit `d4d3c753b`.

Words as in the pre-registration: flip-blind parity knot, count r, up to flips, flip-frozen, fixed by count r₀; classes; the
class-level system; an isolated parity cell; the tiers F (full system), P (parity knots and every copy a state of the harmony), L (the
parity equations alone on classes) and GAC (arc consistency on class domains with both relations), fixing measured from every base
count.

## 1. Lemma A (a census; `result_lemma.json`)

Of the 45 harmonies, the 8 with a flip-blind triple have 48 to 1,152 of them, and the not-all-equal stitch allows **none** (0 in all
8). This is the earlier after-run finding, now frozen; no conceptual proof came cheaply, so it stays a computed lemma on the range.
Only 0011 + 01 has exactly three classes (where the class-level system is a colouring with three colours).

## 2. Every placement on 3 × 3 and 4 × 4 (exact; `result_small.json`)

- **Survival.** 114 of 4,080 mixed placements survive on 3 × 3 and 850 of 524,272 on 4 × 4, as in `PARITY-MIX-20261112-001`.
- **B1, lifting binds (the prediction failed).** Class-level survival differs from survival on 705 placements (all on 4 × 4 but 9 on
  3 × 3 for 00101101 + 0011): the classes fit, but no choice of state within the classes satisfies every stitch. So the flip layer is
  not dead weight; it ends 705 of the 1,669 placements whose classes fit.
- **B2, isolated parity cells (failed narrowly).** One placement class of 000111 + 0011 + 01 on 4 × 4 (8 placements) survives with an
  isolated parity cell; every other survivor has none.
- **Where fixing comes from (the coordinator's question).** Over the survivors, 10,884 pairs (base count, other count), weighted by
  placement; 9,598 are fixed in F and not flip-frozen. Of these:

  | Source | Pairs | Share |
  | --- | --- | --- |
  | L: the parity equations alone | 916 | 10% |
  | P but not L: parity with every copy a state of the harmony | 1,342 | 14% |
  | **F but not P: needs the not-all-equal stitches** | **7,340** | **76%** |
  | not fixed by GAC (beyond arc consistency) | 3,468 | 36% |

  (216 pairs had more than 30 count-r₀ assignments and no GAC verdict.) So the fixing in survivors is not mostly parity's own
  arithmetic: three quarters of it needs the stitches, and a third is beyond the local baseline.

## 3. Placements with each cell parity with probability ρ (exact per sample; `result_scale.json`)

800 placements per (n, ρ) over the 8 harmonies (700 at 9 × 9: the seven-orbit harmony's 9 × 9 cell was cut off by the cap); the
share of all samples that are mixed (0 < k < nm) and keep a state:

| n | ρ = 1/8 | 1/4 | 1/2 | 3/4 | 7/8 |
| --- | --- | --- | --- | --- | --- |
| 3 | 1.0% | 1.25% | 2.5% | 2.75% | 0.88% |
| 4 | 0.5% | 0.25% | 0 | 0 | 0.13% |
| 5 | 0 | 0 | 0 | 0 | 0 |
| 6 | 0.25% | 0.13% | 0 | 0 | 0.13% |
| 7, 8, 9 | 0 | 0 | 0 | 0 | 0 |

- **Rare, by the frozen criterion:** under 1% at every ρ for every n ≥ 6; none of the 11,497 samples at 7 × 7 to 9 × 9 survives.
- **Arithmetic:** sizes divisible by 3 do best (6 above 5, 7 and 8); 4 above 5. The advisor's full order (3, 6, 9 ≫ 7 > 5 ≫ 4, 8) did
  not appear: 9 × 9 and 7 × 7 had no survivor in their samples.
- **The first-moment rate** λ(ρ) is negative for every harmony and ρ except 0011 + 01 at ρ ≥ 3/4 and 000000111111 + 0011 + 01 at
  ρ = 1/8, so for the rest survival at n × n is at most about e^{λ n²}, decaying in n².
- **B1 and B2 on the samples:** 10 placements survive at class level only; no survivor has an isolated parity cell.
- **Tiers on the sampled survivors:** 347 fixed pairs; 131 in L (38%), 86 in P but not L (25%), 130 need the stitches (37%), 88 beyond
  GAC (25%).

## What this establishes

- Exact on the range: survival of parity knots among stitched copies is rare under a stated weighting and decays with size; where it
  happens, most of the fixing passes through the not-all-equal stitches, and a quarter to a third of it needs more than arc
  consistency.
- Refuted predictions: lifting never binds; isolated parity cells always fatal (one exception); almost all fixing in L; the stitches'
  share under a tenth.
- Not established: an exact rule for which placements survive (B1 and B2 both fail as rules); survival beyond 9 × 9; a proof of lemma A.
