# Does a saved fold make learning a new rule cheaper?

On November 15, 2026, we defined an exploratory experiment under FOLD-TRANSFER-20261114-001. The source is the seven-NAND decoder actually returned for public wiring `d406ab6ea3ee6c83`. An earlier fit chose its binary operations and probe budget. A frozen public search composed those operations on the source wiring, and the source checker accepted the resulting circuit. The second learner may call that exact circuit inside a new program. [Source experiment](../ANSWER-COMPOSE-20261115-001/answer_composition.md)

Each target is an unknown rule on four or five essential Boolean inputs. We supply the family of formulas built with AND, OR and XOR in which each input occurs once. Both learners can express the transferred fold using their primitives. Five labeled rows for four inputs or seven for five inputs are initially available from a total of 16 or 32 respectively. The learner sees the input count, the initial labeled rows, and a checker. It has no access to the target formula, full set of labels, family, task ID, or applicability of the fold. Its task-specific fitted program resets for every rule. The learner retains only its public catalogue between rules.

For each input count, use four new tasks with the fold, four matched changes, and eight neutral tasks drawn without conditioning on success. Reserve neutral examples independently of either learner's performance. Keep the collection distinct under input renaming where possible. All experiments share the same saved panel and initial labels. The checker evaluates a submitted program's physical NAND circuit on inputs in descending integer order. It returns the first counterexample, or acceptance after every row. Save the first program before that feedback. Charge every attempt, including compilation of the physical program and partial checks that failed. The adaptive data after the initial examples may differ across methods.

The primary pair takes the first hypothesis consistent with all labels. The transfer method tries programs containing the saved fold first, then the same public primitive order. Catalogue construction, redundant candidates, semantic deduplication and cache use are charged. An additional pair sorts the identical possible truth functions by their numerical truth tables. It fits a lower-median consistent function and uses the known order of the checker to discard alternatives after a counterexample. This comparator has a different search strategy available to either arm and also provides a causal check. Matching candidate functions in matching order must give matching predictions and feedback, even if their implementations use different gates.

The primary quantity is total elapsed work to return correct programs for the actual mixed workload. Charge earlier recorded time for the successful varied parser training case and the original composition training case once per inherited workload. Charge regaining and verifying the particular source program at one endpoint and loading it in the second learner. Record the transfer size. Both arms pay once for their fresh catalogues at each size plus all fitting and physical checking. Time the whole fresh panel in three independent workers per method. Rotate method order. Report medians and ranges, checker calls, rows, NAND gates, candidate inspections and first-proposal accuracy. Report marginal cost assuming the existing fold is already paid for separately. Report any extrapolated reuse threshold only conditionally and only for comparable fresh tasks. Positive, matched and neutral subsets should also be inspectable.

Test complete correctness, identical available truth functions, novelty in essential input count, and semantic agreement under the common-order control. The stop is these paired results on the fixed panel. Engineering time, fixture generation and independent scientific replay are outside the deployment costs of all methods. A synthetic finite result supports only the conditions actually measured. The external design advisor reported its weekly use limit. The separate referee identified common candidate order and inherited acquisition as the decisive controls.

## Prior work in the program

`python3 -B scripts/track.py objects "learn a new rule by reusing a saved fold in a second learner" --until 2026-11-15 --exclude FOLD-REUSE-20261115-001`

`python3 -B scripts/track.py objects "read-once Boolean formula library learning counterexample guided synthesis amortized verification cost" --until 2026-11-15 --exclude FOLD-REUSE-20261115-001`

`python3 -B scripts/track.py objects "four and five variable Boolean rules from sparse examples counterexamples full truth tables" --until 2026-11-15 --exclude FOLD-REUSE-20261115-001`

- `SEARCH-AUDIT-20261112-001` — a relative. Its search controls motivate matching the hypothesis order.
- `CLAMP-LEARN-20261112-001` — a relative. It motivates counting failed attempts to reach a correct answer.
- `LAW-RIGIDITY-20261112-001` — a relative. It distinguishes reaching an answer from holding it.
- `RANDOM-FATES-20261112-001` — unrelated. It concerns a different growth process.
- `ROUTE-PARITY-TRANSFER-20261115-001` — a relative. It counts resources in a proof translation.
- `BRAID-READOUT-20261114-001` — a relative. It studies distinctions recoverable from limited observations.
- `BRAID-COUNTS-20261114-001` — a relative. It studies how additional observations distinguish possible answers.

Here the output is a newly fitted rule and the measured resource includes producing the inherited operation and verifying the new rule. The immediate predecessor supplies the circuit itself.

Using counterexamples as feedback on a proposed rule is an equivalence-query model of learning. Learning a library of program components and reusing it on later synthesis tasks also has established precedents. This experiment measures one particular saved component against the same underlying function class. [Dana Angluin, Queries and Concept Learning](https://doi.org/10.1007/BF00116828) · [Ellis et al., DreamCoder](https://dspace.mit.edu/entities/publication/86d768ab-558f-4fb1-b92e-9288de643ccb)
