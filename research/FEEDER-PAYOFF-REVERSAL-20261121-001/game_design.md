# Paired access to an ordinary ration

The two supplied versions change whether a particular approach opens a ration at a three-exit feeder. They use the same source, growth attempts, physical holdings, ration allocations, movement tape, costs, energy and death rule as the B306 feeder game. The extra rule is an experimental input supplied by the game. Ordinary growth still determines each birth and its holdings. [Archived feeder game](../FEEDER-MEMORY-20261121-001/feeder_game.py)

| Item | Specification |
| --- | --- |
| Branch | Code analysis and validation of the paired input to the separately frozen learning and evaluation study |
| Public inputs | The B306 feeder marker, energy, previous action, outward anonymous controls, the emitted ON/OFF bit, the outward control used by a move and the public energy receipt |
| Private inputs | Founder, names, law, version, movement tape, holder identity, stock, accepted approach and any training override |
| Action | ON attempts a bite. OFF uses the existing movement draw or refusal. Each attempt costs one energy. An opened ration supplies four energy subject to the existing capacity of ten. |
| Output | The original B306 observation and transition. The scorer also receives the existing private event ledger with the approach and access decision. |
| Comparisons | Versions 0 and 1 share one initial ledger and one movement tape. The unmodified current-only decision chooses ON at a marked feeder when the previous action was any action other than eat. |
| Stop | Verify the private ledger and public boundary on archived development starts, then freeze the input and move to the separately authorized study. |

An actual move supplies one approach bit if its anonymous outward control has a partner in the departure menu. The partners are 0 and 1, 2 and 3, and so on. Within each pair, the even control supplies A and the odd one supplies B. An unpaired last control supplies no cue and clears any previous approach. The cue persists during stays. At a marked feeder offering exactly three controls, a bite from a known approach may consume an available ration only when its approach agrees with the supplied opening. A declined bite costs one energy and leaves the ration in stock. A retry at the same feeder uses the retained approach and still checks its present menu. If growth changes the menu away from three, the ordinary action applies. A consumed ration remains spent.

For any given source seed, movement tape and feeder holder, a domain-separated hash supplies one exception bit. Its low two bits encode an exception when both are zero. Version 0 opens with A and version 1 with B before applying that same bit by XOR. The two versions therefore admit opposite approaches at each eligible feeder even when an exception is present. The experiment can fix the bit at a training target to prepare matched opportunities. Pass-only preparation, exactly three exits and an actually available ration are checked privately before the charged training query.

A prospective pairing control swaps the displayed labels within each departure pair. It transports the existing uniform OFF movement draw to the same physical distinction and retains the unpaired label if present. In opposite access versions with and without this swap, every supported approach changes with its accepted value, and all unpaired arrivals agree. Thus equal action bits supply the same physical opportunities and receipts. The reader receives only the ordinary public menu and the actually used anonymous control. It has no version or relabeling input.

## Founder draws

The source recipe draws up to 16,384 candidate seeds from its own hash domain. It uses the B208/B304 ordinary tree sampler and groups whole starts by its canonical holdings key. Both preceding feeder-cue banks and their exclusion lists supply the archive key set. Existing ration-game and feeder-memory selection records are also included directly. Distinct eligible keys take their first occurrence. A separate hash assigns the train, mechanism and held-out folds in proportions 1:1:2. The first 96, 48 and 128 keys in those folds are kept. No growth, route, stock or payoff result participates in selecting a source. Stalled starts remain in their chosen fold.

The same source and trial tape are paired under both knot laws and both access versions. Training uses the sampled names. Mechanism and held-out worlds independently permute distinction names per founder and use the archived anonymous control ranking on those names. The rename is shared across the laws. No founder key, private opening or tape enters the reader.
