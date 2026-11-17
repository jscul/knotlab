# Advisor review of the draft design

Epic `SCALE-MEMORY-20261116-001`, 2026-11-16. The advisor model (`claude -p --model claude-fable-5-2 --tools ""`, reply's
`modelUsage` named `claude-fable-5-2`) was given WHERE-NEXT's results and the first draft cold. Its verdict was "don't freeze
yet: the 2x2 cannot separate reads from training range as drafted." Its points, checked here, and what changed:

| Point | Taken? | Change |
| --- | --- | --- |
| Single ES outcomes compared; seed variance could explain S | yes | both seeds of every arm tested, L3's two seeds give the noise floor; claims need the arm-level interval and both seeds |
| G-learn passes an untrained mixed stage (L3 already ties at 3200) | yes | G-train: the mixed stage must improve validation at 3200 by at least 5% |
| A memoryless mixed arm is missing | yes | L2m replaces the what-only arm (whose real-win chance was 10%) |
| The scale-free arm dropped the short-horizon recency (50-step counts) and added whole-run totals that never forget | yes | the 50-step counts kept; only the clipped log ages replaced by ratios; totals dropped |
| Never-flipped ages undefined | yes | age t + 1 (reads as the oldest), stated |
| Candidate composition changes with n | noted | stated as part of the candidate set, not a read; unchanged |
| The recurrent input's log count ratio falls with n | yes | replaced in the scale-free arms by the violated fraction (×10, clipped) |
| A hand-wired Novelty+ zero-training control | no | every read Novelty+ uses is among the network's, and Novelty+ runs in the same engine; reason stated |
| The diagnosis ignores the interaction | yes | interaction ratios I and a "both needed" reading pre-registered |
| The curriculum change is bundled (schedule, budget, selection) | yes | control L3c: same schedule and selection, last stage at 800 only; ratio C |
| Mixed-stage fitness: scale imbalance, unequal caps | yes | centred ranks within each size, averaged; caps about 40 times probSAT's median at both sizes |
| Power at 12800 with 50 instances; censoring at 51200 | yes | 100 instances at 12800 and 51200; a censored median is a bound |
| The slow loop faces a shift in structure, not size; `local` is the relevant evidence | yes | stated in the plan before the results |
