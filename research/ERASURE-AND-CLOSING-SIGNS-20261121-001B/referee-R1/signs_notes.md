# Component signs on the named holdings

All 294 actual component closures had ordinary words before and after the prescribed even closure. Reversing the new sign alone removed every ordinary word in every case. Of these 294 reversals, 162 admitted an explicit signed operator reading. For the other 132, cancelling the named involutions gave the contradiction \(I=-I\). [All closure and union records](signs_archive_cases.json.gz) · [Structural certificates and cancellations](signs_structure.md)

| Source weighting | New closures | Explicit odd readings | Arbitrary operator refusals |
| --- | ---: | ---: | ---: |
| Labelled trees | 6 | 1 | 5 |
| Connected explosive starts | 0 | 0 | 0 |
| Explosive starts with two added founders | 256 | 129 | 127 |
| Four mutually meeting founders | 32 | 32 | 0 |

The sign calculation took the archived named rows before and after every funded cut in both laws. It rebuilt the connected components from the two holders of each shared distinction. At each new closure it identified the old loose names, summed the old rules, and recovered the exact input names and the implied even sign. Row reduction on the actual named holdings also checked every paid parity birth's implication and the extension count across its entire cut. For the unsigned law every birth received a positive grant and no component closed. [Reconstruction](signs_checks.py) · [Population totals](signs_archive.json)

For a closed component let \(C\) contain all its even words. For each named distinction \(e\), solve for a physical bit string \(t_e\) and a sign bit \(g_e\) such that

\[
A_e|w\rangle=(-1)^{w_e+g_e}|w+t_e\rangle,\qquad w\in C.
\]

Each shift must preserve every old and new even equation. Its own bit must stay fixed for the signed permutation to be an involution. At each knot, require pairwise commutation, zero total shift and the specified product sign. These conditions are linear binary equations in the physical shift entries and sign bits. A solution gives Hermitian involutions on the named carrier. A second calculation read back each solution and applied its named operators in both orders to zero and a basis of \(C\). Each composed shift is constant and its sign exponent is affine on \(C\), so equality there checks every carrier word. This gave 77,549 involution, 233,605 commutation and 38,698 signed product checks. A changed physical sign failed the readback. An absent solution to these specific equations requires additional evidence for general operator refusal. The separate named word reductions supplied it on every refusing case. [Readback program](signs_readback.py) · [Readback counts](signs_readback.json)

The complete unions supplied 842 sign assignments, including all 766 recorded for the mixed explosive weighting. For each assignment the check computed the ordinary rank on the full union and again on each component. For an admitted assignment it composed the operators at every knot in the whole union, including each continuing or already closed component. For a refusal, restriction to the inconsistent component gives the corresponding cancellation proof. At the 63 double closures, 32 unions admitted all four operator assignments and 31 admitted only even/even. On all 63, each of the other three assignments left zero ordinary words. [Union assignments](signs_archive_cases.json.gz)

On the separate forward reconstruction, the 72 seeded draws had 40 closing components, 26 admitting, and six double closures. Four of the six admitted all four operator assignments. Adding the four named controls gave 76 independently rebuilt draws. Their full derived closure and sign records agreed with the archived-input calculation. This sign program used the named rows of those rebuilt histories directly. [Forward-input sign results](signs_forward.json) · [Separate growth reconstruction](growth_replay.json)

## Sign and erasure controls

- In all 294 connected closures, removing any one equation restored the even ordinary count on the same named distinctions. The 3,306 single-equation deletions all passed. Reversing the new sign and one older sign together also restored the even count in every one of 3,012 tests. On the five-knot whole, reversing old holder 2 and closing holder 4 admitted 64 words. The word with only distinction 0 set was one. This intervention changes an older rule. Ordinary growth kept its original even rule. [Named sign controls](signs_archive_cases.json.gz)
- At the fourth cut of the first mixed explosive draw, both four-place founders closed and the complete whole contained 67 knots. With closing holder 58 alone odd, erasing any one of the 16 equations of its component restored \(2^{90}\) whole words. Each of the other 51 deletions left zero. With both closing holders 58 and 59 odd, each of the 67 single-equation deletions left zero. Projecting an empty full relation onto any subset of named distinctions also leaves it empty. The goal register's phrase “every part does” needs the connected component and the operation of erasing an equation. [Mixed draw control](signs_archive_cases.json.gz) · [Goal under review](../../../docs/RESEARCH_GOALS.md#b251--a-closing-knot-whose-sign-nothing-chooses-g18-with-g17-and-g5--2026-11-20)
- On the first cut of the second labelled-tree draw, the newborn held distinctions 2, 3, 17 and 18. The last two were fresh. Changing this newborn's sign gave 65,536 complete words at either sign. The all-zero word was even only. Setting only distinction 17 gave an odd word. Flipping 17 exchanges the complete word sets and preserves the older word. The goal register's “change nothing” applies to existence and extension counts on each old word. [Fresh-grant control](signs_archive_cases.json.gz)

The seven-draw pilots took 0.11 seconds on the archive and 0.03 seconds on the separate forward histories. The expanded runs took 0.74 and 0.10 seconds respectively before writing. The nine-certificate readback pilot took 0.12 seconds and the complete readback took 0.33 seconds. All used one thread per process and peaked below 67 MiB per process. The repeated-meeting negative control is an additional signed example constructed from an observed negative. The sample contained no negative with repeated meetings. [Archive pilot](signs_pilot_archive.json) · [Forward pilot](signs_pilot_forward.json) · [Structural control](signs_structure.json)

```sh
folder=research/ERASURE-AND-CLOSING-SIGNS-20261121-001B/referee-R1
export OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python -B "$folder/signs_checks.py" --source archive --selection all --summary "$folder/signs_archive.json" --details "$folder/signs_archive_cases.json.gz"
.venv/bin/python -B "$folder/signs_checks.py" --source forward --selection all --summary "$folder/signs_forward.json" --details "$folder/signs_forward_cases.json.gz"
.venv/bin/python -B "$folder/signs_readback.py" --output "$folder/signs_readback.json"
```
