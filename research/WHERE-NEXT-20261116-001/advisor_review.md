# Advisor review of the draft design

Epic `WHERE-NEXT-20261116-001`, 2026-11-16. The advisor model (`claude -p --model claude-fable-5-2 --tools ""`, reply's
`modelUsage` named `claude-fable-5-2`) was given the draft pre-registration and the calibration numbers cold and asked to
critique fairness, the agent's design, the predictions, the cost accounting, prior work and the second family. Its answer
is a colleague's view, checked here; it said it verified no citation.

## What it said, and what changed

| Point | Taken? | Change in the frozen design |
| --- | --- | --- |
| At n = 200 probSAT needs about 14 flips per distinction, so where and memory get little to learn; a loss would not separate "idea wrong" from "nothing to learn" | yes | curriculum 200 → 400 → 800, caps about 20 times probSAT's median, selection at n = 800 |
| Make the learner's competence a gate | yes | G-learn: L1 within 1.15 times probSAT at training size, else "learner failure" |
| Both layers zero gives an evolution signal of second order | yes (checked: output = w2·tanh(W1x), each factor zero) | first layers random, output weights zero |
| Add the sticky rule (follow what you just broke), focused Metropolis, clause weighting | sticky and focused Metropolis yes; clause weighting no | A6, A7 added; global clause weighting and survey propagation declared out of scope with the reason |
| Re-tune the hand-written rules at each test size; decide on that comparator | yes | two comparators; the real-win rule uses the re-tuned one |
| Re-choose the best rule inside each bootstrap resample; pair instances and initial states | yes | done; one run seed per instance for every arm |
| Ages saturate at large n | yes | ages clipped at 1,000 steps plus ranks among the candidates |
| `local` doubles the density, a confound | noted | stated under "Settled by construction"; no third family added |
| Where may be vacuous if few knots are violated | yes | distinct-candidate and just-violated diagnostics, with a reading rule |
| Isolate where from joint learning | yes | arm L2w (learned where, fixed probSAT what) |
| A CPU cap censors the slower-per-flip arms | yes | flip-only caps, identical across arms in a cell |
| Name one primary cell; correct for three cells | yes | primary `rand` n = 3200; secondary cells at 98.3% |
| P1 uninformative, P7 near-certain, P9 too loose, probabilities missing | yes | P1 dropped, P7 replaced by P10 and N*, P9 directional, a probability on every prediction |
| Amortizing over the study's own test count is arbitrary | yes | marginal cost per instance plus break-even N* |
| Citation fixes (NeuroCore did report more instances solved; configuration checking from 2011; the threshold estimate is a cavity result) and missing relatives (ChainSAT, FMS, Interian and Bernardini 2023, CLASS, SATenstein, ANYCSP) | yes | prior-work section rewritten; Interian and Bernardini checked by a web search |
| Drop CaDiCaL and P8 as a strawman | partly | kept as context only (not in the decision rule), since the question asks where exact search is costly |
| P4's 30% may be low: `local` hardness is likely walls between the planted state and its complement, which just-violated knots track | noted | kept at 30% against the best rule including the sticky rule; the wall reading is a diagnostic |
