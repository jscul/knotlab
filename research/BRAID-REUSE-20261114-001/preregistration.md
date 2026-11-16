# Frozen transfer test on a three-input problem

Fixed on November 14, 2026 Pacific before fitting this target. Home ticket `FOLD-TRANSFER-20261114-001`. The learned crossing and undo had previously been scored on frozen wiring. That did not measure the cost of learning a different task. Here the independent variable is whether the search language can call the previously learned **forward** crossing. The original guarded instruction sequence has SHA-256 `a740b9a93061a75b78ce24a135b5adc94ca55a0206872c7b69e97117837f4246`, 12 toggles and 60 elementary Boolean operations.

## Prior work in the program

`python3 -B scripts/track.py objects "frozen operation reuse search cost transfer" --until 2026-11-14 --exclude BRAID-REUSE-20261114-001`

`python3 -B scripts/track.py objects "program synthesis primitive search speed baseline" --until 2026-11-14 --exclude BRAID-REUSE-20261114-001`

`python3 -B scripts/track.py objects "paired held out training search amortization" --until 2026-11-14 --exclude BRAID-REUSE-20261114-001`

`BRAID-ACTIONS-20261114-001` supplies the frozen artifact. `SEARCH-AUDIT-20261112-001`, `CLAMP-LEARN-20261112-001` and `CHEAP-COUNT-20261112-001` motivate fair search costs. Related records include `SHORT-DESC-20261112-001`, `ENDLESS-BLOCK-20261112-001`, `LOOP-LOCK-20261112-001`, `FORGET-RULE-20261114-001`, `TIE-CYCLE-20261114-001` and `AGE-NEST-20261112-001`.

## Task and held-out success

Inputs are **three** arbitrary ternary registers `x`, `y`, `z`. Answer yes when the three labels are all equal or all distinct. Read yes if and only if the final physical register `z` holds zero. The other two outputs are free. The definition is invariant under renaming labels and specifies no desired transformation table, braid word, intermediate state, or use of the library call. All three inputs matter. There are multiple reversible completions, and an independent primitive-only eight-toggle construction. No solution, intermediate labels, or construction enters fitting. On the nine held-out triples satisfying `z=(x+y+1) mod 3`, require nine correct answers. The eighteen other triples (six positive, twelve negative) train the program. There are three positives and six negatives held out. The training reward gives two points for a correct positive and one for a correct negative, at most 24. A validated target must be exact on both splits.

## Paired search and budget

Run paired seeds 17, 29, 43, 59 and 71. Each arm gets 32 populations, one identical all-raw initial candidate per population, then 512 generations of 12 children, **196,640 candidate evaluations per arm per seed**. The original 12 guarded Boolean flips may act on any of six ordered choices of register pair. Both arms have the same 72 exposed raw instructions (two encodings can perform the same raw move). A reuse arm may additionally call the verified frozen crossing on one of the same six ordered pairs. Both conditions share the input distribution, terminal reward, population update, mutation and restart rules, no-op accounting, and a maximum **36 expanded guarded flips** per candidate. Use the crossed operation in its original label orientation. No inverse call, learned basis change, or warm-start solution.

Initialize with raw programs of length 2–12. Draw the same edit and primitive choices in both arms. At proposal sites a uniform one-in-thirteen opportunity substitutes a crossing in the reuse arm; the raw arm uses the pre-drawn ordinary instruction. Account for over-cap proposals with the declared common raw fallback. Parent choice uses only training scores, uniform ties and the shared restart schedule. Keep the best-ever checkpoint by training score, then shorter expanded length, then first encounter. Alternate which arm runs first by paired seed and keep execution serial for timing. Freeze the implementation before fitting; smoke tests may use synthetic scorers. No rerolls, parameter changes, seed changes or follow-on budgets based on this panel.

The mutation kernel uses 30% insertion, 25% deletion, 30% substitution and 15% relocation. Every brood's last child is a fresh program and every 32nd generation selects it. If a proposed call would exceed the common expanded bound, use the pre-drawn raw token. If even a raw insertion would exceed the bound, substitute instead. The paired initial populations contain only primitives. The returned best training program uses fewer expanded toggles to break score ties. The independent raw-program feasibility witness and held-completion count are withheld from the search itself.

## Outcomes, censoring and cost

Continue to the fixed budget without consulting held-out answers. Save the first training-perfect candidate and all first occurrences needed to determine the first globally exact discovery afterward, including evaluation indices and cumulative execution costs. Seal the training-selected checkpoint before the held-out replay. Report its genuine held-out score separately from the retrospective time to the first completely correct program sampled. A run with no globally correct candidate is right-censored at 196,640. Also report the realized full-budget spend. Count every proposed program, including duplicates and initialization.

Charge the actual guarded toggles and primitive NOT, AND and XOR operations executed as expanded across each training case. Separately record gate operations executed using parallel representations, any fitness-cache or table costs, and wall time. Include the candidate's own inference cost and every call's expansion. Independently reconstruct the acquisition cost of the **single guided forward** stage that selected the frozen 12-step program. Undo training, neutral controls and prior scientific audits are separate expenses. The first maximum-score program in that earlier run can differ from the final shortest retained program.

Compare paired validated success, capped time and compute through first valid candidate (or censor) under the same convention. Show all five rows; success-only means can erase failed searches. Distinguish execution of a known solution from cost to find it. A finite payback in matched work units requires positive savings for comparable future successful uses. If failures or unequal verified success prevent a like-for-like estimate, say so. Five seeded repetitions examine one task and cannot establish a distribution of new tasks or a self-improvement rate.
