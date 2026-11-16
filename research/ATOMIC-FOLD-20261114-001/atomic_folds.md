# Which parts of a logical fold can an agent discover?

On November 14, 2026 we followed the local-agent experiment with a new task using only elementary Boolean instructions. The search had to choose the operands and determine what information to communicate to a later reader. This is an exploratory experiment with a small, fully checkable instruction language. [Earlier local agent](../LOCAL-RULE-ACTIONS-20261114-001/local_agent.md) · [Prespecified experiment](preregistration.md)

## An example of the question

Let three local rules each allow any subset of two possible values, 0 and 1. A later reader cares about the values permitted by a particular pair. A familiar context indicates the type of reader. Training gives examples of the reader's answers. Only the scorer knows which two local rules matter for that reader.

Suppose the relevant pair happens to be A and B. “Do both allow 0?” and “Do both allow 1?” have independent answers. If the next reader always asks whether either value remains possible, a single bit can summarize the two answers. If it might instead ask specifically about 0 or 1, the encoder must keep enough information to distinguish neither, only 0, only 1, and both. A code that says “yes, some value remains” cannot distinguish only 0 from only 1.

In the experiment the program gets six individual bits. Its three available instructions each perform one AND, OR, XOR or NAND on two input or scratch bits and write one result. At submission it emits one or two registers and loses its scratch memory. The specific later question is then revealed. A lookup fitted only on training examples reads the emitted bits. Unused instructions can be ignored. The search sees a terminal score for a complete candidate program. It receives no target pair or intermediate values. This is direct policy search over short programs. The earlier experiment used a tabular agent with a supplied fold.

Three pairs of rules and two possible uses give six contexts. Each context has an arbitrary name. We fit a separate policy for each name. We trained on the 32 even-parity settings of the six input bits, then froze the learned programs and decoders and tested all 32 odd-parity settings. Both splits contain every setting of the four bits belonging to any given pair. Exact means that **every** applicable downstream question had the right answer on **all 64** settings. The selected width was determined from training scores with a preference for a smaller code in a tie. The code's information content and the minimum feasible width were checked separately.

## First search

The initial policy maintained a categorical distribution over each of the three instruction positions and the registers to emit. It updated these distributions using its highest-scoring complete programs. Blind search drew from the same starting distribution and retained its best complete program. Each method received exactly 12,288 program evaluations per context, width and seed. Seeds were 17, 31 and 53. One reported fit is one context and seed, with the width selected using training alone.

| Use of the summary | Reward-fitted policy, exact | Blind search, exact | Reward-fitted, exact at minimum width | Blind, exact at minimum width |
| --- | ---: | ---: | ---: | ---: |
| Ask whether either value survives | 2/9 | 3/9 | 0/9 | 0/9 |
| May ask about either value individually | 0/9 | 2/9 | 0/9 | 2/9 |

The first policy's two exact broad answers kept four distinguishable code values despite the task requiring only two. In a typical selective fit it learned whether the relevant pair both permitted 0. Knowing that fact lets its learned decoder get 82/96 downstream answers right on each split. The remaining mistakes matter if a later rule specifically needs the other value. Under the uniform test distribution even the best unrestricted one-bit summary can answer only 7/8 of the selective queries correctly. [Programs, training trajectories and scores](../../artifacts/ATOMIC-FOLD-20261114-001/ATOMIC-FOLD-20261114-001-E001_atomic_actions/results.jsonl) · [Independent analysis](../../artifacts/ATOMIC-FOLD-20261114-001/ATOMIC-FOLD-20261114-001-E001_atomic_actions/analysis.json)

## Retaining and changing whole programs

After seeing the first result, we registered one follow-up. Each of 12 groups kept a candidate program and tried small changes to its gates or output registers. In the guided condition, downstream correctness determined which program became the next parent. In the neutral condition, the next parent was chosen randomly. Both conditions could retain the best answer they saw. They used the same initial program populations as the first experiment, the same elementary instructions, the same budget and matching random choices about the kinds of mutations to try. [Follow-up design](mutation_design.md)

| Use of the summary | Reward-guided mutation, exact | Neutral mutation, exact | Guided, exact at minimum width | Neutral, exact at minimum width |
| --- | ---: | ---: | ---: | ---: |
| Ask whether either value survives | 9/9 | 2/9 | 0/9 | 0/9 |
| May ask about either value individually | 9/9 | 3/9 | 9/9 | 3/9 |

Guided search selected the right pair in all 18 fits. Changing any bit of the third rule never changed the emitted code or decoded answer. Each selected program had two live gates and emitted two bits. On some runs these indicated which values remained possible directly. Others inverted one or both bits or emitted them in the opposite order. For example, for the selective A-and-B reader with seed 17 the encoder emitted “both allow 1” and “at least one forbids 0.” The decoder recovered every later answer from these two bits. No names or target values were assigned to the emitted bits. Each of the nine selective programs could pass the surviving possibilities to two further rules. Every one of the 3,072 assignments and later queries per program was correct.

The nine broad-task programs retained the same four possibilities even though their readers only distinguished “none” from “some.” Their fitted decoders could already answer the broad question from those two bits. We also gave the one-bit search its full budget in every broad fit. Its best programs scored 52/64 across all worlds in all nine runs. Shorter encodings were preferred on a training tie, but the one-bit search never found the exact three-gate expression. This is a reproducible difference between learning which information is sufficient and finding the smallest sufficient summary.

Held-out correctness for the guided condition was 288/288 broad answers and 864/864 selective answers, counting the same tasks across three training seeds. Neutral mutation gave 261/288 and 781/864. The matched comparison supports an effect of using terminal reward to select which whole programs to vary in this panel. It leaves open which part of the change from the first optimizer accounted for the difference between experiments. [Programs and parent-selection histories](../../artifacts/ATOMIC-FOLD-20261114-001/ATOMIC-FOLD-20261114-001-E002_program_mutation/results.jsonl) · [Independent checks](../../artifacts/ATOMIC-FOLD-20261114-001/ATOMIC-FOLD-20261114-001-E002_program_mutation/analysis.json)

## What the finite task makes possible

Size-ordered search over the same primitive gates, using the labeled training rows and their downstream answer patterns, found an exact program at the minimum width for all six contexts. All six programs gave every answer correctly on held-out worlds. The following is the shortest construction it found for the pair A and B.

```text
u = AND(A0, B0)
v = AND(A1, B1)
```

For the reader that might ask about either value separately, emit both bits. For the reader that only asks whether some value remains, apply one more gate, `OR(u,v)`, and emit that bit. Other perfect representations may encode the same four possibilities with inverted or otherwise recoded bits. Those alternatives count as exact if the decoder can recover all requested answers.

This reference searched in order of gate count and compared 640,920 candidate gate applications across all six contexts, including repeated prefixes. Its supervised equivalence test has access to the answer pattern for each training world. Its counts use different units from complete program evaluations in the stochastic searches. Its success establishes attainability, minimum live gate counts of two and three in this language, and a constructive way to find these programs from examples. [Size-ordered search](enumerate_programs.py) · [Comparison design](comparisons.md)

A fixed choice of the wrong pair loses information even if it can send all four of its raw bits to the best possible decoder. For example, using A and C when the reader needs A and B caps the broad task at 44/64 correct answers and the selective task at 140/192 across all possible inputs. The verifier also checked that changing a correct AND gate to OR causes errors, and that a correct selective code retains enough information to intersect with two further arbitrary unary rules. This latter check supplies the schedule of further combinations. [Independent evaluator and controls](independent.py)

The next reader changes the size of a sufficient summary. When the pair is known to the encoder, the two uses above require two or four distinguishable cases, respectively. If the pair **and** queried value are both announced only *after* compression, all three pairwise answers for each value must be recoverable. For a single value there are five distinct possibilities: no pair jointly permits it, just AB, just AC, just BC, or all three. The two values vary independently. Exhausting the 64 worlds gives 25 downstream answer patterns, requiring at least five fixed-width bits. An unfamiliar consumer whose wiring is entirely hidden cannot be identified from local rule values alone. Visible connections or new feedback would provide additional information.

For the connection to Lesson 4.7, we derived unary input relations directly from the 256 possible eight-bit states of each of four archived signed systems. All four source readings agreed with the earlier independent output tables. Choosing three sources, fixing their two other inputs, and specifying the read and required output generated 16,384 instances covering all 64 local worlds. These are concrete source realizations within the exhaustive test domain. [Source adapter](lesson_inputs.py)

## Reproduce

From the research checkout, the first two commands independently execute all saved programs, recompute their training-only decoders, and check every held-out answer. The third repeats the deterministic size-ordered search. The last command refits one complete mutation-search seed and emits its programs, comparison and training histories. Both experiments' complete three-seed training histories were replayed.

```sh
PYTHONHASHSEED=0 .venv/bin/python -B research/ATOMIC-FOLD-20261114-001/analyze.py
PYTHONHASHSEED=0 .venv/bin/python -B research/ATOMIC-FOLD-20261114-001/analyze.py --follow-up
.venv/bin/python -B research/ATOMIC-FOLD-20261114-001/enumerate_programs.py
PYTHONHASHSEED=0 .venv/bin/python -B experiments/ATOMIC-FOLD-20261114-001/ATOMIC-FOLD-20261114-001-E002_program_mutation/job.py --seed 17
```

The encoder's programs were chosen separately for six familiar downstream contexts. A stronger test would freeze a single policy, change the visible connections to a downstream reader, permute rule names and positions, and test whether its choice follows those connections. The present positive result concerns new local values under known kinds of demand.
