# Independent ordinary growth reconstruction

The complete pass independently rebuilt four cuts or the earlier stop on all 544 archived named founders under both ordinary laws. Every compared field of the named histories agreed, including the funded parent rosters, grants, consumed and fresh distinctions, old-row certificates, and complete component memberships at every funded cut. [Complete pass summary](growth_all_summary.json)

| Founder weighting | Founders | Parity cuts and births | Whole parity closures | New parity closing components | Not-all-equal cuts and births |
| --- | ---: | ---: | ---: | ---: | ---: |
| Labelled trees (T) | 256 | 248 and 1,587 | 6 | 6 | 256 and 1,598 |
| Explosive connected sources (E) | 128 | 512 and 4,257 | 0 | 0 | 512 and 4,257 |
| Explosive sources with two added components (M) | 128 | 512 and 7,105 | 0 | 256 | 512 and 7,232 |
| Designed positive sources (S) | 32 | 32 and 32 | 32 | 32 | 128 and 224 |
| Total | 544 | 1,304 and 12,981 | 38 | 294 | 1,408 and 13,311 |

Each law stalled on the same 192 tree founders and encountered no resource censor. Not-all-equal closed zero components and yielded a literal older state with all chosen input distinctions equal to zero for each of its 13,311 proposed and funded births. The 294 zero parity grants comprised 133 three-place and 161 four-place births. The 63 doubly closing cuts all belonged to the mixed weighting. Becoming twice held was counted directly from older and newer incidence, yielding 26,082 distinctions under parity and 26,444 under not-all-equal across all funded cuts.

The ordinary five-knot whole from designed-positive draw 2 had 64 older words, the same 64 even completions, and zero when only the closing sign was reversed. The exact projected relation on the four closing inputs had the same eight even words before and after the ordinary birth. It was empty after reversal. The matched unsigned law funded fresh distinction 10 with 1,106 full words and the full local five-place not-all-equal relation. Applying the unsigned rule to the ten-distinction parity incidence gave 512 words. In labelled-tree draw 2, toggling fresh distinction 17 reverses the sign on holder 7 alone and preserves the count of 65,536 full words. [Named checks](growth_replay.json) · [Canonical projection tests](growth_verification.json)

## Method and coverage

- Consume only the named founder rows and their recorded holder order when rebuilding. Use actual twice-held distinctions to find the old witnesses, enumerate inclusion-maximal pairwise witnessed sets of three or more with no common witness, and retain residual pairs. Make one global funding decision and allocate one further unary birth per remaining loose distinction. Order the larger groups lexicographically, then the pairs lexicographically, then the unary proposals by holder. Each parent spends its lowest remaining numbered loose distinction. The lexicographic convention reproduces the archive's labelled sequence.
- Apply the same proposal rule to the provisional new holders through their parent rosters to derive the next demand. For parity, reduce the old named equations and verify each zero birth by literal symmetric difference of the old rows and by exhaustion of its old component's loose distinctions. Verify each not-all-equal positive grant against a satisfying old word with equal selected inputs. Check every founder's full local projections and essential rules by conditioning on the shared distinctions and counting the possible independent loose completions.
- Recompute old and new components from the full named incidence at every cut. A new closed component contains one zero-grant birth and all distinctions in its own older component. Its entire union can continue. The saved comparison preserves older closed components, exact loose names and the twice-held count separately from funded prices.
- The detailed run used one `random.Random(20261126)` and consecutive samples of sizes 32, 16, 16 and 8 without replacement from the sorted draw indices in panels T, E, M and S. Execution sorted the selected indices in each panel. Add the only positive labelled-tree closure (draw 201) and the five-knot whole (designed-positive draw 2) as named positives. The smallest positive closed component of a continuing union, mixed draw 1, was already seeded. Add the eight-knot negative comparator (labelled-tree draw 57) and the positive-grant comparator (labelled-tree draw 2) as named controls. The detailed and complete results remain separate. [Detailed replay and seed](growth_replay.json)
- Compare the proposal routine against direct subset enumeration on all 2,048 families of witnessed subsets of four holders. A second pass on the detailed receipts verifies 43 certificates by odd multiplicity and all 1,743 unsigned words by literal row satisfaction, and applies the canonical knot test to the four named minimum projections. [Verification](growth_verification.json)

The full run covers the named archived founder rows and the stated four-cut horizon. Original source draws and their label permutations were supplied as archived input to this reconstruction. The archive records funded rosters and termination status. At stalls the new code records the proposed groups and shortages, with archive comparison available for the stop alone. No later cuts, additional founders, or unsigned compatibility with imposed parity signs were scored. The separate component and operator checks cover the sign comparisons.

## Reproduction and cost

The pilot used the lowest selected draw index from each weighting and the four extra named cases. Eight paired reconstructions matched in 0.22 s wall time before the selected pass and 0.24 s before the complete pass. Scaling by the largest elapsed case in each pilot weighting projected about ten seconds for the complete pass. The selected pass used 0.85 s and peaked at 69,272 KiB RSS. The complete pass used 4.94 s and peaked at 69,160 KiB RSS. The verification used 0.19 s and peaked at 26,628 KiB RSS. All execution used one process, single-thread numerical library settings and an address-space cap of 2.5 GiB. [Pilot](growth_pilot.json) · [Reconstruction](growth_replay.py) · [Verification code](growth_verify.py)

```bash
audit=research/ERASURE-AND-CLOSING-SIGNS-20261121-001B/referee-R1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
prlimit --as=2684354560 -- .venv/bin/python -B "$audit/growth_replay.py" --pilot
prlimit --as=2684354560 -- .venv/bin/python -B "$audit/growth_replay.py"
prlimit --as=2684354560 -- .venv/bin/python -B "$audit/growth_replay.py" --all
PYTHONPATH=tools prlimit --as=2684354560 -- .venv/bin/python -B "$audit/growth_verify.py"
```
