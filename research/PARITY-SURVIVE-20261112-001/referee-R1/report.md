# Referee report PARITY-SURVIVE-R1: which parity placements survive

**Verdict: Confirmed, with three small fixes (all Not a block).**
- **Every computed claim reproduces exactly** with my own code:
  - B1's 705 lifting obstructions;
  - B2's 8 survivors with an isolated parity cell;
  - every one of the 27,500 scale samples, in both survival and class-level survival;
  - the fixing split, pair for pair, on all survivors and on the sampled ones.
- **The missing scale cell** (the seven-orbit harmony at 9 × 9) has no survivor in its 500 samples. So "none at 7 × 7 to 9 × 9"
  holds on 11,997 samples, not 11,497, and no claim moves.
- **The fixes.**
  - The "beyond arc consistency" shares are slightly low, because of the census's cap of 30 count-r₀ assignments. The exact values
    are 37.7% and 27.7%, not 36% and 25%.
  - The first-moment rate is an estimate, not a bound.
  - The pair totals count each placement n times. That is harmless for the shares.

Referee: the background referee thread, 2026-11-12.
- **Code.** It is my own: PARITY-MIX-R1's encodings (`ref_parity.py`, `ref_parity_fast.py`, `ref_parity_enum.py`, `ref_gac.py`), plus
  `ref_survive.py` and `ref_survive_tiers.py` here. It imports none of `survive_lib.py`, `check.py`, `parity_lib.py` or `shift_lib.py`.
- **Class-level survival** uses one class per copy, with support clauses for each cell's allowed class triples. That encoding is my own.
- **Validation:** V2. The advisor model was not consulted for this job.

## 1. The tier definitions and code (check 1)

I read `survive_lib.py`. The tiers mean what the pre-registration says, and they match the ones I built independently for
PARITY-MIX-R1.

| Tier | What it is | My equivalent |
| --- | --- | --- |
| **F** | the whole system, with two copies compared up to flips | the same |
| **P** | each copy with its own kinds, so a state of the harmony, plus the parity knots at K; no stitch | B2 |
| **L** | the parity equations on one F₂ coordinate per copy | B1 |
| **GAC** | arc consistency on class domains, with both relations projected to classes | the same |

- **On L.** A flip-blind knot acts on every coordinate of the classes, taken modulo all-ones, by the same equation. So the scalar
  system decides fixing for the vector one, which is correct.
- **On GAC.** It starts from each count-r₀ class assignment that some state has, as mine does.
- **The 216 pairs without a GAC verdict.** The census enumerated at most 30 count-r₀ assignments. Past that, GAC was left
  undecided, and the pair was counted in no numerator. My enumeration has no cap and was never more than 5,000.
  - On all survivors of 3 × 3 and 4 × 4, 3,621 of the 9,598 fixed, not flip-frozen pairs are beyond GAC: 37.7%. The census's 3,468
    plus the 216 undecided makes 3,684, so 153 of the undecided are beyond GAC and 63 are reached.
  - On the sampled survivors it is 96 of 347: 27.7%, against the census's 88, with 65 undecided.

**The split reproduces pair for pair.**
- On 3 × 3 and 4 × 4 (all placements):

  | Tier | Pairs | Share |
  | --- | --- | --- |
  | L | 916 | 9.5% |
  | P not L | 1,342 | 14.0% |
  | the stitches (F not P) | 7,340 | 76.5% |

- On the sampled survivors (each read at its n translates):

  | Tier | Pairs | Share |
  | --- | --- | --- |
  | L | 131 | 38% |
  | P not L | 86 | 25% |
  | the stitches | 130 | 37% |

**A note on the totals.** The census reads one placement per translation class, from every base count, and weights by class size.
Each placement's pairs therefore enter n times: 9,598 = 3 × 138 + 4 × 2,296, where 138 and 2,296 are my per-placement counts from
count 0. Every share is unaffected. The absolute pair numbers should not be read as placement counts.

## 2. B1's 705 lifting obstructions, recomputed (check 2)

On every placement of 3 × 3 and 4 × 4, for the 8 harmonies (528,384 placements):

| Measure | Placements |
| --- | --- |
| survive | 988 |
| survive at class level | 1,693 |
| class level only (lifting obstructions) | **705** |
| survive but not at class level | 0 |

**By harmony.**
- **3 × 3:** 9, all for 00101101 + 0011.
- **4 × 4:**

  | Harmony | Obstructions |
  | --- | --- |
  | 0011 + 01, 000000111111 + 0011 + 01, and the two largest | 136 each |
  | 00001111 + 0011 | 112 |
  | 00101101 + 0011 | 24 |
  | 00001111 + 00101101 + 01 | 16 |
  | 000111 + 0011 + 01 | 0 |

**What causes them.** Class-level survival forgets how the flips of one copy must agree across its three knots: a stitch's class
triple says that some flips work, knot by knot.

**B2.** 8 survivors have an isolated parity cell, all for 000111 + 0011 + 01 on 4 × 4, as reported.

## 3. The capped scale part and its missing cell (check 3)

**The census's samples, regenerated.** I regenerated every frozen sample, random.Random("PARITY-SURVIVE|i|n|ρ|s") with each cell parity
with probability ρ, for all 56 cells, the missing one included.
- **Agreement.** On the 55 cells the census saved, all 27,500 samples agree with its record, in survival and in class-level survival.
- **The missing cell** (the seven-orbit harmony at 9 × 9): none of its 500 samples survives. One is class-level only.

**So no claim changes.**
- **Survival.** At every ρ and n ≥ 6 it is at most 0.25%, the same table as the census's.
- **No survivor at 7 × 7 to 9 × 9,** now on 11,997 mixed samples.
- **B1 at scale** has 10 class-level-only samples, and **B2 at scale** none.

**`assemble_after_cap.py`** only gathers the saved cell files. It changes no row and names the missing cell, as frozen.

**Stopping at the cap is not a selection on outcome.** The cell order was fixed (sizes from 9 down, harmonies in index order), and
the missing cell is the slowest, the largest harmony at the largest size.

## 4. Other points

**The first-moment rate is not a bound.** λ(ρ) = ln|W| + ρ ln(|FB|/|W|³) + (1 − ρ) ln(|R|/|W|³) treats every cell's triple as if
drawn independently.
- **The exact first moment.** Over Bernoulli placements it is Σ_X Π_c (ρ·[X_c ∈ FB] + (1 − ρ)·[X_c ∈ R]). That is the partition
  function of a model on the repeat, in which copies are shared by three cells, so it does not factor. Markov's inequality bounds
  survival by it, not by e^{λ n²}.
- **The wording.** "So survival falls at least like e^{λ n²}" should be "the annealed estimate e^{λ n²}". Survival does fall in the
  data.
- **Where the estimate is positive.** For 0011 + 01, λ is positive at ρ = 3/4 and 7/8, and it predicts no decay there.

**Lemma A** is a property of the kind set, which the note now says, citing PARITY-MIX-R1: 12 of 96 kind sets meet.

**The definitional points** are correct as stated:
- with parity everywhere, a state exists iff 3 | n;
- every survivor repeated is a survivor of a multiple size;
- the 3 × 3 diagonal case is settled by its class system;
- fixing must be read from every base count.

## 5. Fixes for the thread (all Not a block)

1. **Beyond arc consistency.** With no cap on the count-r₀ enumeration it is 37.7% (all survivors on 3 × 3 and 4 × 4) and 27.7%
   (sampled), not 36% and 25%. The census's figures leave out 216 and 65 undecided pairs.
2. **The scale part.** The missing cell has no survivor (0 of 500), so "none in 11,997 samples at 7 × 7 to 9 × 9".
3. **The first-moment rate.** Call it an annealed estimate, not a rate survival falls at least as fast as. Note that it is positive
   for 0011 + 01 at high ρ. Also say that the pair totals count each placement n times.

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_survive.py classlevel` | `result_classlevel.json` | B1 and B2 on every 3 × 3 and 4 × 4 placement |
| `ref_survive.py scale` | `result_scale.jsonl` | the 28,000 frozen samples, the missing cell included |
| `ref_survive_tiers.py` | `result_survive_tiers.json` | the split on the sampled survivors |

The split on 3 × 3 and 4 × 4 is PARITY-MIX-R1's `summary_p*.json` and `result_gac_p*.json`, counted as in section 1.
