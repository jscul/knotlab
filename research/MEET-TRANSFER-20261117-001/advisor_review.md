# Advisor review of the draft design

Epic `MEET-TRANSFER-20261117-001`, 2026-11-17. The advisor model (`claude -p --model claude-fable-5-2 --tools ""`, reply's
`modelUsage` named `claude-fable-5-2`) was given both earlier studies' results, their referees' findings, the calibration and the
draft, cold. Its first point: "a negative result is currently uninterpretable: add an oracle arm." Its points, checked here:

| Point | Taken? | Change |
| --- | --- | --- |
| Add an oracle trained on `local` to separate transfer from representation | yes | Dl: D's reads, trained on the mix plus `local` window 10 |
| G-learn checked one family only | yes | G-learn on every training pattern of each arm |
| `local` is a development pattern, not truly held out; add untouched families | yes | windows 40 and 160 at density 4.0, and `heavy` (a heavy-tailed degree spread), chosen at the freeze |
| X mixes structure with degree exposure; Z bundles reads, counts and schedule | relabelled | X and Z labelled as packages; an extra arm not added (compute) |
| The B191 bar and the decision rule disagree; medians are the wrong bar for an inner loop; 1.5 is tight | yes | an inner-loop bar: R ≤ 2 (upper below 2.5), solved fraction no lower, 95th-percentile ratio ≤ 3; the main reading |
| The recurrent state counts steps implicitly; flags and candidate composition still carry the pattern | noted | stated as limitations; the oracle answers whether the reads suffice |
| A covariate-shift table | no | the engine does not log reads; reason stated |
| Comparator tuning picks noise | yes | two stages (screen 8 × 3, confirm top 5 on 20 × 5), ranked by the test metric; top three Novelty+ tested as a sensitivity check; probSAT exp and WalkSAT added; comparator censoring reported |
| Two seeds and a both-sides rule give many inconclusives | yes | four seeds for D and Dl; a split read as learner variance |
