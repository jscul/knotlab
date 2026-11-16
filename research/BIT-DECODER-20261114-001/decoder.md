# Letting a sender choose bits for a frozen logical decoder

The sender learned to transmit three bits for the original four questions. After freezing, the decoder trained on varied wiring also answered the held-out exactly-one question. Across 168 held wirings it answered **344,064/344,064** delayed questions correctly. Its sender used minimum width on **150/168** wirings. Training only on the original disjunction also yielded three bits there, but that decoder missed every case where changing “any” to “exactly one” changed the answer. The architecture, training conditions and test sets were fixed in advance. [Frozen training inputs and sources](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/freeze.json) · [Full experiment results](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/result.json)

| Four possible delayed reads, varied-training checkpoint | Held wirings | All 512 inputs answered exactly | Minimum bits | Actual bits per wiring |
| --- | ---: | ---: | ---: | --- |
| Three cells and whether **any** is true | 33 | 33/33 | 3 | 3 on 30, 5 on 3 |
| Three cells and whether **exactly one** is true | 33 | 33/33 | 3 | 3 on 30, 5 on 3 |
| Four independent cells | 33 | 33/33 | 4 | 4 on 30, 6 on 3 |
| Same signed occurrence counts, different grouping | 33 | 33/33 | 3 | 3 on 30, 5 on 3 |
| Three cells and a repeated cell | 9 | 9/9 | 3 | 3 on all 9 |
| Four copies of the same derived question | 9 | 9/9 | 1 | 1 on all 9 |
| Three cells and an exclusive-or of two of them | 9 | 9/9 | 3 | 3 on 6, 5 on 3 |
| Same exclusive-or wiring with a fresh operand | 9 | 9/9 | 4 | 4 on 6, 6 on 3 |

Training used 256 even-parity raw tables. Half of the 344,064 held answers used both unfamiliar wiring and the 256 odd-parity tables. All **172,032/172,032** of these answers were correct. In all 24 port orders of the canonical layout, the varied checkpoint attained the three-bit and four-bit minima. Always omitting any one fixed port could recover all four answers on only six of the 24 disjunction orders.

## What was learned

There were 13 possible transmission candidates per menu. Nine were raw cell bits and four were question values computed by the candidate parser. A shared learned expression decided which to send from public incidence and structural repetition. Neither the optimal width nor a label for the redundant port was part of the feedback. The receiver could copy an already-transmitted question value shared by structurally identical queries, or compute a question from transmitted source slots. On the canonical three-bit tests the sender chose the three source bits and the receiver used computation to answer the fourth question.

The search started by scoring parser candidates on their four terminal answers. It enumerated **16,384** settings for three shared two-input operations and their initial scan bits. It then scored candidate emission rules with the retained parsers, prioritizing exact answers and then shorter messages. With only the original examples, 24 parsers fit training. Four of them could compute every held exactly-one port on even-parity tables when supplied the whole raw input. The chosen parser treated negative occurrences as automatically satisfying their group. It therefore answered exactly-one as “any”, including on all 8,448 changed trials. With examples using one or two pair exclusions added, all four remaining training-perfect parsers could compute those unseen questions. No exactly-one question was present in either fit. [Parser ambiguity diagnostic](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/parser_controls.json)

The varied fit learned NAND expressions equivalent, in combination, to testing a signed literal, accepting a row when some literal is true, and accepting a query when every row is met. The program was given constants, NAND, copies, public addressing and the two nested scans. No special disjunction, exclusive-or, count or exactly-one instruction ran on the packet. On the physical packet `110`, the same frozen receiver returned **1** for “any” and **0** for “exactly one”. Each answer trace executed 71 NANDs under its wiring. Across all 8,448 changed fourth-question answers, the physical packet was identical before and after rewiring and the frozen decoder changed its answer correctly every time. The matched signed-count rewire similarly changed all 2,112 required answers correctly on identical packets. [Frozen learned programs](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/varied_checkpoint.json) · [Action traces and coding failures](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/mechanism.json)

## Why the sender sometimes used extra bits

When all four question descriptions were structurally distinct, the varied sender learned to transmit each source appearing positively in a three-pin group. When descriptions repeated, it sent one computed answer per distinct description. On 18 held wirings, a logically equivalent representation of a cell read put two irrelevant source names into a positive group. One such cell read has the four rows (v or s or t), (v or not s), (v or not t), and (s or not s). If v is false the first row needs s or t, while the next two require both to be false. The answer is therefore exactly v. The sender nevertheless included s and t. Replacing both of those transmitted slot values with zero preserved all **36,864/36,864** delayed answers on the affected wirings. The frozen policy still sent the longer packet. [Per-wiring intervention](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/mechanism.json)

Two additional stress wirings had four compound exactly-one questions. The first repeated one question in a different order. The sender transmitted the three distinct computed answers and was exact at the three-bit minimum. Changing the fourth question to use one source from each of the other three yielded all sixteen possible answer vectors, with every one of the nine raw cells essential. The sender transmitted **nine** raw bits. It was exact on all 512 inputs, although transmitting the four computed answers would have sufficed.

The restricted sender features explain this last miss. In both the original disjunction menu and the hard compound menu, all four distinct query candidates have the very same public feature vector. A shared emission rule on those features can emit all four query candidates in both menus or leave them all out in both. The former costs at least four bits on the original three-bit task. The latter forces it to use raw cells on the compound menu, where all nine matter. A sender that can inspect more of each candidate's wiring could make a different choice. This is a finite limit of the tested sender interface.

## What counts as using three bits

The raw state is any of 512 binary tables over nine cells. Four public questions concern that same state. The sender commits a physical tuple of zeroes and ones before the questioner chooses a port. The receiver has the wiring, that tuple and the port. It cannot access the raw table. Its public routing convention is fixed by the checkpoint. The number of transmitted bits is the actual tuple length, which is constant over raw inputs for a fixed wiring. [Pre-registration](preregistration.md)

For any wiring, let N be the number of different four-answer vectors across the 512 inputs. Two different answer vectors must have different physical messages for a receiver to answer every port. A fixed packet of b bits provides at most 2 raised to b distinct messages. With unrestricted encoding the bound is attained by giving each vector its own code. The study checks the learned sender and the real decoder against that independent lower bound, including every answer on every raw table.

In the original question, three ports read cells a, b and c and a fourth asks whether any of those cells is present. In the new question, the same three bits remain available to ask about and the fourth asks whether exactly one is present. In each case the three independent cell values give eight possible answer vectors. Four independent reads have all sixteen answer vectors. If a sender forced them into three bits, two vectors would share a message and would disagree on at least one possible delayed port. The older decoder could copy just one stored bit for each question. With four distinct, nonconstant answer functions it needed four slots even for the disjunction. [Preceding decoder](../BRAID-ACTIONS-20261114-001/braid_actions.md)

## How the question is identifiable

Every question has the same public shape. It has four groups of signed source occurrences. One group contains three occurrences and the other three contain two. For the scorer, the question accepts when each group contains at least one true literal. Source indices, signs and grouping are public. A family name, a correct answer, and an instruction labelled “exactly one” never enter the policies. A singleton or a simpler question can fill unused groups with tautologies. The tests include equivalent representations with extra source names. [Wirings and oracle](wirings.py)

For the exactly-one question the three positive occurrences say that at least one cell must be present. The three negative pairs rule out a and b together, a and c together, and b and c together. No individual training port computes exactly-one even up to complementing or permuting its three inputs or complementing its output. A further control rearranges the negative occurrences into pairs aa, bc, bc. It has precisely the same shape, signs and number of occurrences for each named source. Its answer can differ after rewiring. Other controls reuse a source in an exclusive-or question or connect the same pins to a new fourth source. [Wiring controls](wirings.py)

The one-question training condition has a genuine identifiability limit. An alternative rule can read only the three-pin group of each port, ignoring the two-pin groups. It answers every original training question correctly. On the new fourth question it reports yes whenever *any* of the three cells is set, and therefore fails on the four assignments with two or three cells set. A frozen policy's transfer beyond what these examples determine depends on the operations and the other examples it learned from.

## Reproduction

Refitting from the saved training specification reproduced both checkpoints byte for byte and recovered the same search trajectories and training losses. An independent scalar NAND interpreter reconstructed the public wirings, physical packets, information bounds and delayed answers. It matched all 412 wiring records across the two checkpoints, including the cases where the sender used extra bits. The records cover 36 training-panel wirings, 168 held wirings and two compound stress wirings per checkpoint. The original-disjunction fit trained on six of the 36 training-panel wirings. [Repeat fits](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/replay.json) · [Independent interpreter](audit.py) · [Independent results](../../artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/audit.json)

The following commands reproduce training, the freeze, the held assessment and the independent check in a fresh directory. Run them from the repository root.

```sh
study=BIT-DECODER-20261114-001
family=${study}-E001_atomic_codec
out=$(mktemp -d)
export OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0
cp "artifacts/$study/$family/freeze.json" "$out/freeze.json"
.venv/bin/python -B scripts/longrun.py launch "experiments/$study/$family/job.py" \
  --out "$out" --unit bit-decoder-replay --workers 1 --case-timeout 1200 \
  --case-mem 3G --mem-max 4G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$out" --foreground --limit 2
.venv/bin/python -B "research/$study/assess.py" freeze --out "$out"
.venv/bin/python -B "research/$study/assess.py" assess --out "$out"
.venv/bin/python -B "research/$study/audit.py" --out "$out" --write
```
