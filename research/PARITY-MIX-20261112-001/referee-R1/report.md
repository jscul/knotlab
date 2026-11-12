# Referee report PARITY-MIX-R1: a parity knot among stitched copies

**Verdict: Confirmed with fixes, and the headline narrowed.**
- **What reproduces exactly.** The census of flip-blind triples (8 of 45 harmonies, all of dimension 2). Survival on every placement
  of 3 × 3 (114) and 4 × 4 (850). The frozen 6 × 6 and 8 × 8 samples (6 survivors, then none). A78's buildability.
- **Fix 1: the fixing numbers.** They come from one placement per translation class, weighted by class size. But fixing by count 0
  is not invariant when a placement is translated across counts. On every placement:

  | Repeat | Fixed but unreached | Full fixing |
  | --- | --- | --- |
  | 3 × 3 | 69 (as the census) | 39, not 24 |
  | 4 × 4 | 832, not 806 | 632, not 646 |
- **Fix 2: the baseline is weak.** The frozen propagation rule never uses a stitch for these 8 harmonies, which have no functional
  slots. Against fair baselines, count 0 still fixes what no knot by knot reasoning reaches, but in fewer survivors:

  | Repeat | Census | Needs both kinds of knot | Beyond arc consistency on classes |
  | --- | --- | --- | --- |
  | 3 × 3 | 69 of 114 | 33 of 114 | 15 of 114 |
  | 4 × 4 | 806 of 850 | 744 of 850 | 454 of 850 |
- **Fix 3: rarity depends on the kind set.** "No flip-blind triple is ever a stitch triple" holds for the kind sets the census used,
  but fails for 12 of the 96 kind sets of span at most 8 that present the 8 harmonies. Under those kind sets parity knots and stitches
  coexist far more often:
  - 21.8% of mixed placements survive on 3 × 3;
  - 12.6% on 4 × 4 for 0011 + 01, where one parity knot alone already survives.

  So "rare, not typical" is a statement about one kind set per harmony.

Referee: the background referee thread, 2026-11-12. The code is my own and imports none of `parity_lib.py`, `shift_lib.py`,
`check.py` or the after-run scripts; it reads the census only as data.
- **Encodings.** `ref_parity.py` holds each copy as a one-hot class plus a flip bit, the parity knots as placewise four-member parity
  with one hidden reference per knot, and the stitch bit by bit. For dense parity on the largest harmonies I used a lighter encoding,
  `ref_parity_fast.py` and `ref_parity_enum.py`: each copy's own kinds, and two copies compared up to flips bit by bit.
- **Agreement between the encodings.** On all 512 placements of 3 × 3 for the largest harmony they agree on survival. On every 3 × 3
  survivor of 0011 + 01 they agree on fixing.
- **Solvers and validation.** Glucose 4 and CaDiCaL. Validation: V2. The advisor model was not consulted for this job.

## 1. Re-derived (the owning thread's question 1)

**The census.** My code finds the same 8 harmonies with flip-blind triples (48 to 1,152 ordered triples), each with largest subspace
2, and the same functional slots: none for the 8; the first slot for 6 others.

**The up-to-flips semantics** match the pre-registration. Count r is flip-frozen when one class tuple occurs in every state. It is
fixed by count 0 when two states with the same classes on count 0 have the same classes on count r.

**Survival.** Survival is the same under translation, so the census's class weighting is valid for it.

| Repeat | Placements with 1 ≤ k < nm | With a state | At which k |
| --- | --- | --- | --- |
| 3 × 3 | 4,080 | 114 (2.8%) | k = 3 (45), k = 6 (69) |
| 4 × 4 | 524,272 | 850 (0.16%) | at most 0.5% at any k |
| 6 × 6, frozen samples | 1,760 | 6, the same sample (k = 6, two stars) in 6 harmonies | |
| 8 × 8, frozen samples | 1,200 | 0 | |

**Fixing: the class weighting is wrong.** Translating a placement by r counts turns "fixed by count 0" into "fixed by count −r".
- **3 × 3 example.** In one class of nine placements of 0011 + 01 at k = 3, six members have a count fixed but unreached and three
  do not. The census gave all nine its representative's value.
- **The totals on every placement.**

  | Repeat | Fixed but unreached (census) | Full fixing (census) |
  | --- | --- | --- |
  | 3 × 3 | 69 (69) | 39 (24) |
  | 4 × 4 | 832 (806) | 632 (646) |

- **The largest mixed share of full fixing** is 5.8% (3 × 3, k = 6), not 3.6%. On 4 × 4 it is under 0.4% at every k, as the census
  says.
- **"Every placement" was not run.** The pre-registration's p3 says every placement (512), but the code used translation classes for
  p3 as for p4.

## 2. The k = 0 split (the owning thread's question 2)

**The split is right and needed.** With no parity knot, not-all-equal locks already fix counts:
- on 3 × 3, 3 of the 8 harmonies (6 counts);
- on 4 × 4, 6 of the 8 (10 counts).

All of these hold with the stitches alone. So the frozen failure criterion, read literally with k < nm, would have been "not met" by
the locks alone, which makes it mis-specified. The note's 1 ≤ k < nm figures are the honest reading.

## 3. The baseline (coordinator's i) and where the fixing comes from (ii)

**The frozen rule is mostly parity's own closure.** No harmony among the 8 has a functional slot, so its stitches never propagate.
"Reached by propagation" is then the closure of the parity knots alone, so "fixed but unreached" counts anything else that fixes a
count: parity's own linear algebra, the harmony's states, or the stitches.

The baseline is not empty, so the result is not automatic. But it is weak.

**Each count fixed but unreached, by where its fixing already holds.** The tiers are nested: fixed in a relaxation implies fixed in
the whole.

| Source | 3 × 3 placements | 4 × 4 placements |
| --- | --- | --- |
| B1: the parity knots' linear algebra over F₂^P / ⟨1…1⟩ (copies free, no stitches) | 15 | 48 |
| B2: parity knots with each copy a state of the harmony (no stitches) | 21 | 40 |
| BN: the stitches alone (no parity knots) | 0 | 0 |
| Only the whole: both kinds of knot needed | 33 | 744 |
| **Total placements with a count fixed but unreached** | **69** | **832** |

**A fair local baseline** is generalized arc consistency on classes. For every class tuple on count 0 that some state has, prune each
copy's classes knot by knot, using each knot's relation projected to classes. A count is reached when every copy is left with one
class.
- **3 × 3.** It reaches 93 of the 108 counts. 15 placements keep a count fixed beyond it.
- **4 × 4.** It reaches 1,370 of 2,264 counts. 454 placements keep a count fixed beyond it.
- **All of them are in "only the whole".**

**(i) Not automatic, but a Narrowing.** A fair baseline is B2 together with BN, and then arc consistency on classes. Against it the
claim "count 0 fixes counts no local propagation reaches" holds in 15 of 114 survivors on 3 × 3 and 454 of 850 on 4 × 4. The
census's figures are 69 and 806 (my 832). The frozen failure criterion is still not met under every baseline.

**(ii) Both, by share.** On 3 × 3, 36 of the 69 placements are settled by parity's own linear algebra, or by it with the harmony's
states (definitional in the coordinator's sense). The other 33 pass through the not-all-equal stitches. On 4 × 4 the joint part
dominates (744 of 832).

**The survivors' shape.** I checked it on 3 × 3.
- At k = 3, the survivors are exactly the stars of copies, for 5 of the 8 harmonies.
- The other 3 harmonies survive only at k = 6, in 3 placements that are not unions of stars.
- 90 of the 114 survivors are unions of stars.

## 4. A78: buildable (the owning thread's question 3)

**Confirmed, by an explicit gadget** (`ref_gadget.py`, checked by exhaustive projection). It uses not-all-equal knots only, each with
three distinct members, no constants, and hidden distinctions.

| Part | What it builds | Knots | Hidden distinctions |
| --- | --- | --- | --- |
| Fano with one line removed | equality p = q | 6 | 5 |
| With NAE(u, q, p), u equal to p | p ≠ q | 7 | 6 |
| Four clause pieces relative to a reference r | x ⊕ y ⊕ z ⊕ r = 0, exactly | 57 | 53, per place |

A clause piece is NAE(l₁, l₂, t), t ≠ t′, NAE(t′, l₃, r). One reference per knot serves all its places.

**A wording fix.** The pre-registration's cited route, NAE(a, b, e) ∧ NAE(¬e, c, r), projects to 4-member not-all-equal, not to
parity: it allows (0, 1, 0, 0), which parity forbids, and forbids (0, 0, 0, 0), which parity allows.

**Plain parity cannot be built.** x ⊕ y ⊕ z = 0 is not closed under the flip, and everything not-all-equal knots define is. So the
point about the "zero" holds.

## 5. Is "no flip-blind triple is a stitch triple" provable for every harmony? (question 4)

**No: it is false at the level the stitch is defined.** The stitch depends on the kind set that presents a harmony, not on its states
alone.
- **Where it fails.** 12 of the 96 kind sets of 1 to 3 kinds of span at most 8 that present one of the 8 harmonies hold flip-blind
  stitch triples:
  - 10 kind sets of 0011 + 01, for example kinds (1, 3) and (5, 6) with the triple 1100, 1001, 0101;
  - 2 of 000000111111 + 0011 + 01.
- **Where it holds.** It holds for the kind sets the census used.
- **Wider search.** Over all 2,934 kind sets of span at most 9 (98 harmonies, 19 with a flip-blind triple), only those 12 meet. In
  not-all-equal laws that are not harmonies, 48 of the 109 laws and periods with a flip-blind triple have one in the stitch.

**Consequences.**

| Kind sets | Survival on 3 × 3 | Survival on 4 × 4 |
| --- | --- | --- |
| 0011 + 01, its 77 kind sets | 3, 21 or 111 of 510 mixed placements, by kind set | |
| The 12 where the triples meet | 111 of 510 (21.8%) | |
| 0011 + 01 with kinds (1, 3) and (5, 6) | | 8,242 of 65,534 (12.6%), at every k from 1 to 12 |
| 000000111111 + 0011 + 01 with kinds (1, 6), (2, 7), (6, 7) | | 8,242 of 65,534 (12.6%), at every k from 1 to 12 (folded in after the first commit) |

On 4 × 4, 5,108 of the 8,242 survivors of the first kind set have a count fixed but unreached, and 2,810 have full fixing. The second
kind set has the same survival counts at every k; 6,898 of its survivors have a count fixed but unreached, and 3,520 full fixing.

**The after-run explanation does not hold.** One parity knot empties 3 × 3 under all 96 kind sets, including the 12 whose stitch holds
flip-blind triples. So "no flip-blind triple is a stitch triple" is not why one knot empties 3 × 3.

## 6. Are the samples enough to say "none"? (coordinator's iii)

**Bounds** (exact binomial, 95%):

| Sample | Survivors | Bound on survival |
| --- | --- | --- |
| 8 × 8, pooled | 0 of 1,200 | below 0.25% (one-sided) |
| 8 × 8, one k pooled over harmonies | 0 of 80 | below 3.7% |
| 8 × 8, one harmony at one k | 0 of 10 | below 26% |
| 6 × 6, pooled | 6 of 1,760 | 0.13% to 0.74% |
| 6 × 6, at k = 6 | 6 of 160 | 1.4% to 8.0% |

So "none" supports "rare on average under this weighting", and says almost nothing at any single k.

**It is not "absent"** (`ref_structured.py`):
- **On 8 × 8,** the star of a single copy (k = 3) keeps a state for 00101101 + 0011. Two stars (k = 6) do for 3 of the 8 harmonies: at
  51, 5 and 2 of the 63 offsets.
- **On 6 × 6 and 7 × 7,** two stars survive at 29 of 35 and 42 of 48 offsets for 5 harmonies.
- **The sampling grid skips them.** The 8 × 8 grid of k (multiples of 4) never samples k = 3 or 6, where every structured survivor
  found lives. A uniform 3-set is a star with chance 64 / 41,664 = 0.15%.
- **What never survives.** One parity knot alone, and the stars of a whole count, survive at no size from 3 to 8, for any of the 8.

## 7. Proved against computed, frozen against after-run (coordinator's iv)

| Claim | Evidence | When |
| --- | --- | --- |
| Parity forbids all-equal copies; all-parity is Ledrappier's law; propagation is local | proved, definitional | frozen |
| No flip-blind triple ⇒ one parity knot ends every arrangement | proved, definitional | frozen |
| A78 buildable | proved by an explicit gadget (the referee's); the note's cited route is wrong | frozen claim, referee's proof |
| 8 of 45 with a flip-blind triple, dimension 2 | computed, exact | frozen |
| Survival on 3 × 3 and 4 × 4 and in the samples | computed, exact on its kind sets | frozen |
| Fixed but unreached; full fixing | computed; the class weighting is wrong (fix 1) | frozen |
| The 1 ≤ k < nm reading | a reading made after the run, and the right one | after the run |
| No flip-blind stitch triple; stars of copies | computed; true only for the census's kind sets (fix 3) | after the run |

## 8. Fixes for the thread

1. **The fixing numbers.** Recompute them on every placement, or state that they are class representatives:
   - fixed but unreached: 69 on 3 × 3, 832 on 4 × 4;
   - full fixing: 39 and 632;
   - largest mixed share: 5.8%.

   **Not a block** (Computation: a measure that is not the same under translation, weighted by class size).
2. **"Beyond local propagation".** Restate it against a fair baseline: needs both kinds of knot in 33 of 114 (3 × 3) and 744 of 850
   (4 × 4); beyond arc consistency on classes in 15 and 454. The rest is parity's own linear algebra, with or without the harmony's
   states. **Narrowing** (Overreading: a baseline with no stitch propagation).
3. **Rarity and the kind set.** "Parity knots and not-all-equal stitches almost never coexist" and "no flip-blind triple is ever a
   stitch triple" hold for the census's kind sets. For the 12 of 96 kind sets whose stitch holds flip-blind triples, survival is 21.8%
   on 3 × 3. For 0011 + 01 with kinds (1, 3) and (5, 6) it is 12.6% on 4 × 4, with a single parity knot surviving. Say "for one kind
   set per harmony". **Narrowing** (Scope: a property of a presentation stated for the harmony).
4. **The 3 × 3 explanation.** One parity knot empties 3 × 3 under every kind set, including those with flip-blind stitch triples. So
   that is not the reason. **Not a block** (after the run).
5. **A78's route.** The cited gadget builds 4-member not-all-equal. Replace it with a working construction, such as the referee's.
   **Not a block.**
6. **The samples.** "None on 8 × 8" bounds average survival below 0.25%, not survival at a given k. Single and paired stars of copies
   survive on 8 × 8, at k values the grid does not sample. **Not a block.**
7. **The frozen failure criterion.** With k < nm it is met by the not-all-equal locks at k = 0. Record the 1 ≤ k < nm reading as the
   operative one. The thread already does so. **Not a block.**

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_parity.py` | `result_census.json`, `result_p3.jsonl`, `result_p4.jsonl.gz` | the census; the encoding and analysis; every placement (4 × 4 merged with the two lighter runs, compressed) |
| `ref_parity_fast.py` | merged into `result_p4.jsonl.gz` | the lighter survival check for 5 harmonies on 4 × 4 |
| `ref_parity_enum.py` | `result_p4_rest.jsonl` | the lighter fixing check, for the last 21 dense classes |
| `summarise.py` | `summary_p3.json`, `summary_p4.json` | totals against the census |
| `ref_gac.py` | `result_gac_p3.json`, `result_gac_p4.json` | arc consistency on classes |
| `ref_gadget.py` | `result_gadget.json` | A78's gadget |
| `ref_fb.py` | `result_fb.json` | flip-blind against stitch triples over every kind set |
| `ref_presentations.py` | `result_presentations.json` | 3 × 3 for the 96 kind sets |
| `ref_samples.py` | `result_p6.jsonl`, `result_p8.jsonl`, `result_alt4.jsonl.gz` | the frozen samples; 4 × 4 for the first alternative kind set |
| `ref_parity_fast.py` (with REF_LIGHT_FIX after a timeout) | `result_alt4b.jsonl.gz` | 4 × 4 for the second alternative kind set |
| `ref_structured.py` | `result_structured.json` | stars on 3 × 3 to 8 × 8 |
