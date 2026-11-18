# Referee report WEAVE-PAIR-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.** Every frozen number recomputes in the referee's own code, which does not import `twistlib.py`:
  - **The twist.** The referee built it independently, by re-signing the two knots that cross the seam rather than reading values
    flipped. It reproduces every stored spectrum at widths 6, 9 and 12 to 6 × 10⁻¹².
  - **The transfer.** The referee's site-by-site transfer equals its dense one to 10⁻¹³, and its Arnoldi values at widths 15, 18
    and 21 equal the study's to 3 × 10⁻¹².
  - **The half-turn.** It is confirmed by an explicit gauge, antiperiodic with period three, so it closes exactly when w/3 is even.
  - **The rest.** The correlations, the single-row and two-row readings, and the fits all match to the last digit.
- **What changes.**
  - **"First on the weave" needs "coupled".** WEAVE-MIX's survivor 3 splits into independent two-column strips. Along those strips
    its distance carries all its information, decays at a fixed rate, and, newly found here, steps outward strictly at single-row
    resolution. So "a distance that both carries the information and steps outward strictly is still not found" holds only for
    coupled bases. **Narrowing.**
  - **The odd pair.** It is ± (real, phases 0 and π) in one sector and complex (phase 0.94π to 0.98π) in the other. Which sector is
    which alternates with the parity of w/3. As the width grows, both approach magnitude λ₀/√2 and phase π.
  - **Q6's failure is the fit window.** On longer windows the decay rate is the gap at every position and in both sectors.
  - **"Carries all its information"** is inherited from proofs. It is not from WEAVE-MIX's post hoc read, and the note should cite
    the proofs.
  - **"Third envelope-only case"** is right against the record.
  - **Two numbers.**
    - The energy gap is exactly log₃ 2 in one sector, from an exact eigenvalue λ₀/2.
    - The spin gap appears to approach ½ log₃ 2.

    Both point to an exact (Pfaffian) solution.

## What holds

- **The twist (the owner's first point; `referee_pair.py spec`).**
  - **The study's construction.** Every knot crossing the seam reads column 0 flipped.
  - **The referee's construction.** No value is read flipped. A flip of one place turns an excluded pair into another excluded pair
    (`flip` from WEAVE-LAWS-R1). So the referee re-signs the up knot U(s) at its second place and the down knot D(s) at its first and
    third, the places that lie in column s + 1.
  - **The comparison.**
    - Spectra: both arrangements, both sectors, widths 6, 9 and 12, the same to 6 × 10⁻¹² in per-site, spin and energy gaps.
    - The seam moved to column 0: the same spectra, as the study found by shifting the arrangement.
    - Since the knots are closed under the global flip, there are no other sectors.
- **The site-by-site transfer against the dense one (the owner's second point; `site`, `w21`).**
  - **The referee's site transfer.** It acts as v → vM on a front of w + 1 bits, the opposite way to the study's u = Mv. It is
    generalised to per-column knots, so the twist is the re-signed seam.
  - **Against the referee's dense transfer.** Equal to 1.1 × 10⁻¹³ at widths 6, 9 and 12, in both sectors, for both arrangements,
    on three random vectors.
  - **Arnoldi.** At widths 15 and 18, both arrangements and sectors, and at 21 for arr1 in both sectors (arr2 follows by Q2), the
    readings equal the study's to 3 × 10⁻¹²:
    - spin gap 0.3143, 0.3161, 0.3157, 0.3148, 0.3150, 0.3154;
    - energy gap 0.6300 to 0.6309.

    The two width-21 runs took 6.5 and 8.3 minutes.
- **One arrangement (Q1 and Q2; `sym`, `spec`).**
  - **The search.** Map arr1 by the half-turn (x, y) → (−x, −y) and a shift. Then search all gauges with period 6 around and 2
    along, which flip one bit per distinction.
  - **What it finds.** 8 maps turn the image into arr2 knot by knot: shifts of 2 or 5 columns, with 0 or 1 row, each with the
    gauge 001110 or its complement on every row (for the shift of 2).
  - **Why the seam appears.** Every gauge found is antiperiodic with period three, g(x + 3) = 1 − g(x). On a cylinder of w = 3m
    columns it therefore closes when m is even and leaves one seam when m is odd. That is the study's explanation, now with the gauge
    written down.
  - **The spectra.** arr1 = arr2 in the same sector at w = 6 and 12, and with sectors swapped at 9 (and at 15 and 21 from the
    Arnoldi values).
- **Disordered, with the twist fixed (Q3 and Q4).**
  - The gaps recompute as above, with 1.26312 states per distinction.
  - **The sector splitting.** It is |ln λ_per − ln λ_anti| per row: 1.655 × 10⁻³ at 12, 6.86 × 10⁻⁴ at 15, 2.11 × 10⁻⁴ at 18
    and 6.44 × 10⁻⁵ at 21. The ratios are 2.4, 3.3 and 3.3 per three columns, so it is exponential, as stated. These are natural
    logs, while the gaps are in log₃ (see 5).
- **The correlations (W3; `corr`).**
  - **Exact at width 12.** They equal the study's to every printed digit in both sectors.
  - **Single-row decrease.** It fails at every position, in both sectors, as the study says.
  - **The two-row tick.** It holds at positions 0 and 2 in the periodic sector and fails elsewhere, as the study says.
  - **The fits.** The fit on rows 10 to 30 gives 0.3171 at positions 0 and 2 in the periodic sector, 0.2422 at position 1, and
    0.3457 and 0.1691 in the twisted sector, as stored.

## 1. "First on the weave", and "a strict ruler is still not found" (the coordinator's question; Narrowing)

- **The record has an earlier base with both properties.** WEAVE-MIX-R1 found that survivor 3 (2 × 2, from WEAVE-MIX's post hoc
  survivors) is a product of independent two-column strips along the transfer axis. Its knots are of the not-all-equal class, so
  its pair counts carry it.
- **What the referee now finds** (`s3`, width 12, every start row and column of its period):
  - its correlation along the transfer decays at a fixed rate. The leading flip-odd pair is exactly ±(√2 − 1)λ₀, a gap of 0.401
    per row;
  - |C(r)| decreases strictly at single-row resolution, at both columns and from both start rows: for instance 0.646, 0.293, 0.232,
    0.172, 0.111, 0.050, … It is the study's own criterion for a ruler (the objects row: "|C(r)| strictly decreasing");
  - its sign alternates (− − + + or − + − +), so the signed correlation, and with it the pair count itself, is not monotone.
- **Why the referee's earlier report did not dismiss this.** WEAVE-MIX-R1 set survivor 3 aside as "decoupled, not a candidate". It
  printed only even rows and did not test monotonicity, so this was missed there.
- **So, against the record.**
  - **"The first base on the weave whose distance carries all its information and decays at a fixed rate."** True among coupled
    (two-way) bases. Survivor 3 has both properties along its strips.
  - **"A distance that both carries the information and steps outward strictly is still not found."** True for coupled bases. On the
    weave's knots, survivor 3's strips do it in |C|, one way only, with no relation across strips (C = 0 beyond one column).
- **How it bears on A97 for the weave.** A one-way strip ruler is the thread's ruler again, and LOGIC-AXIS already has that. The
  two-way premise stays unmet, as the note says.
- **Fix.** Write "coupled (two-way)" in the note's owner-terms paragraph, the G1 checkpoint row and the A97 line. Name survivor 3
  as the decoupled case. **Narrowing.**

## 2. The equal-magnitude odd pair: complex or ± (the owner's question)

- **The leading flip-odd eigenvalues** of arr1 as complex numbers (`phase`; arr2 is the same with sectors swapped at odd w/3):

  | Width | Periodic: \|μ\|/λ₀, phase/π | Twisted: \|μ\|/λ₀, phase/π |
  | --- | --- | --- |
  | 6 | 0.68649, ± (0 and 1) | 0.71765, ±0.9386 |
  | 9 | 0.71224, ±0.9572 | 0.70139, ± (0 and 1) |
  | 12 | 0.70594, ± (0 and 1) | 0.70863, ±0.9675 |
  | 15 | 0.70802, ±0.9738 | 0.70662, ± (0 and 1) |
  | 18 | 0.70696, ± (0 and 1) | 0.70763, ±0.9781 |

- **So the pair is both kinds.** It is a real ± pair in the sector without the exact λ₀/2 eigenvalue (see 4), and a complex
  conjugate pair near π in the other. The sector alternates with the parity of w/3.
- **As the width grows.**
  - Both kinds converge: magnitude → λ₀/√2 = 0.70711λ₀ and phase → π.
  - The next pair closes in: 0.70633 at width 18 in the periodic sector, against 0.70696. So the flip-odd sector forms a band whose
    top approaches λ₀/√2 with phases near π.
- **What this does to the correlation.**
  - **A ± pair** gives C(r) ≈ ρʳ(a + b(−1)ʳ). Its size alternates between |a + b| and |a − b|.
    - At positions 0 and 2 in the periodic sector, a > |b| and C stays positive through r = 30. The two-row tick holds there.
    - At position 1, |b| > |a| and the sign alternates. The near-degenerate complex pair beats against it with a period of about
      33 rows, so the tick fails.
  - **A complex pair at 0.967π** gives (−1)ʳ times a beat of about 61 rows. The signs at positions 0 and 2 in the twisted sector run
    ++++−−−−−−−−−−−−+++++++−+−+−+−, and the tick fails.
- **Wording.** The note's "a pair with opposite phases" fits the ± sector. In the other sector the pair is conjugate, near π.
  "Oscillates as it decays" is right in both.

## 3. The fit window (the owner's question; Not a block)

- **The frozen window.** Rows 10 to 30 at width 12 are shorter than the beat periods (about 33 and 61 rows).
- **Longer windows**, up to where |C| meets rounding near r = 90, give the gap everywhere:

  | Sector, position | Fit r = 10–30 | Fit r = 10–60 | Envelope, r = 30–84 | Spin gap |
  | --- | --- | --- | --- | --- |
  | periodic, 0 and 2 | 0.3171 | 0.3168 | 0.3184 | 0.3170 |
  | periodic, 1 | 0.2422 | 0.3192 | 0.3272 | 0.3170 |
  | twisted, 0 and 2 | 0.3457 | 0.3305 | 0.3248 | 0.3135 |
  | twisted, 1 | 0.1691 | 0.2916 | 0.3244 | 0.3135 |

  An asymptotic rate slower than the gap is impossible, so the 0.24 and 0.17 are window artifacts.
- **So Q6's failure is the window, not the rate.** The note's "a fit window of 20 rows … does not average out" says this.
- **Two wording points.**
  - "Decays at exactly the spin gap" should read "at the spin gap's rate, within 0.1% at positions 0 and 2 on rows 10–30 and within
    4% everywhere on longer windows".
  - The "envelope" in "a ruler only in envelope" is the envelope of a sign-alternating or beating correlation. It is not one fixed
    period.

## 4. Two exact features, and a route to a proof (an observation; Not a block)

- **The energy gap is exactly log₃ 2 in one sector.** At every width from 6 to 18, one sector's flip-even spectrum holds the
  eigenvalue λ₀/2 exactly:
  - for arr1, the twisted sector at w = 6, 12, 18 and the periodic sector at 9 and 15;
  - the energy gap there is 0.6309297536.
  - So in that sector it is an exact eigenvalue, not a measured two-excitation threshold.
  - At width 21 the two-excitation states rise just above it: 67.5177 and 67.5598 against λ₀/2 = 67.4976 and 67.5019.
- **Related exact values.**
  - At width 12, the periodic sector's flip-odd spectrum holds −λ₀(twisted)/2 = −8.240259 exactly.
  - At width 6, λ₀(twisted) = 4 and the top odd value of the periodic sector is 2√2.
- **The spin gap appears to tend to ½ log₃ 2 = 0.31546**, since |μ|/λ₀ → 1/√2 (§2). Then "the energy gap is twice the spin gap"
  would be exact in the limit. This is conjectured from widths to 21, not shown.
- **The route.** These are the marks of a free-fermion (Pfaffian) structure. WEAVE-MIX's N2 maps the base to dimers on a planar
  non-bipartite graph. Kasteleyn's method applies to any planar graph, as Fendley, Moessner and Sondhi used for the triangular
  lattice.
- **What that would give.** The free energy (1.26312 states per distinction), the gap and the oscillation phase are then computable
  in closed form, and "disordered" would become a theorem. Offered as a direction, not a fix.

## 5. Smaller points (Not a block)

- **"Carries all its information" (the coordinator's question).**
  - **Where it comes from.** It is established, by earlier proofs and not by this study:
    - WEAVE-LAWS's L1 (only the not-all-equal class is determined by its pair counts);
    - DISTANCE-ORDER's statement 3(a), which N and the pair counts make cover signed knots too, as WEAVE-LAWS-R1 rederived.
  - **It holds for this pair.** It is true of every finite base built from such knots, so of this pair in both sectors.
  - **It does not come from WEAVE-MIX's post hoc read.** What was post hoc there was the choice of these arrangements as disordered,
    and this study's frozen W2 now confirms that.
  - **The fix.** The pre-registration says "(proved)", while the note says only "pair counts determine it, for this class of knots".
    Cite the proofs in the note.
- **"Third envelope-only case, after OR and hard hexagons, and the first that carries all the information"** is right against the
  record.
  - WEAVE-LAWS has OR and hard hexagons as envelope rulers, which WEAVE-LAWS-R1 confirmed. Their information needs counts of three.
  - The record has no other envelope case.
  - Survivor 3 is not an envelope case: in |C| it is strict, along its strips.
- **Units.** The sector splitting is quoted in natural logs per row (1.66 × 10⁻³) and the gaps in log₃ per row. Say which.
- **"Moving the seam one column changes nothing"** is confirmed independently, with the seam at column 0.

## Fixes for the thread (listed for the owner, not folded in)

1. **"First" and "still not found".** Add "coupled (two-way)", and name WEAVE-MIX's survivor 3. Its decoupled strips carry their
   information and step outward strictly in |C|. Do this in the note, the G1 checkpoint row and the A97 line. **Narrowing.**
2. **The odd pair.** It is ± in one sector and complex near π in the other, alternating with w/3. Both tend to λ₀/√2 and phase π.
   **Not a block, wording.**
3. **The rate.** "Within 0.1% (rows 10–30, positions 0 and 2) and 4% everywhere on longer windows", not "exactly". **Not a block.**
4. **Citations and units.**
   - Cite WEAVE-LAWS L1 and DISTANCE-ORDER 3(a) for "carries all its information".
   - Say the splitting is in natural logs.
   - Note the exact λ₀/2 eigenvalue behind the energy gap in one sector.

   **Not a block.**
5. **Optional, a direction.** A Kasteleyn computation for the pair: the gap, ½ log₃ 2 if the trend is right, and the phase in
   closed form.

## How the work was split

- **The referee:**
  - read the note, the pre-registration, `twistlib.py`, `run.py`, `checks.py` and the results;
  - read WEAVE-MIX's and WEAVE-LAWS's records and its own earlier reports on them;
  - wrote its own twist (re-signed seam knots), dense and site transfers, Arnoldi, exact correlations, eigenvalue phases, the gauge
    search for the half-turn and survivor 3's single-row correlations (`referee_pair.py`), reusing its WEAVE-LAWS-R1 strip transfer.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_pair.py`**, with these parts and outputs:
  - `spec`: dense spectra, the twist and the seam moved;
  - `site`: site against dense, and Arnoldi at 15 and 18;
  - `w21`: width 21;
  - `corr`: correlations at width 12;
  - `phase`: the odd pair from width 6 to 18;
  - `s3`: survivor 3;
  - `sym`: the half-turn and its gauge.
- **Outputs:** `referee_pair_<part>.json`.

Reproduce, from `research/WEAVE-PAIR-20261118-001/referee-R1/`:

```sh
for P in spec site corr s3 sym phase w21; do ../../../.venv/bin/python -B referee_pair.py $P > referee_pair_$P.json; done
```

`w21` takes about 15 minutes in all, and the rest a few minutes each.
