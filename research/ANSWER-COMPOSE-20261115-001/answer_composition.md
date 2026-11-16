# Learning to recover a fourth answer from three

On November 15, 2026, a frozen sender and decoder chose the minimum packet on all 24 layouts of a new nonlinear dependency and all 24 matched layouts where a single source changed. They answered all 98,304 delayed questions on those wirings before the correctness check. On the full panel of 89 wirings, checking repaired six incorrect proposals. A cached compiler returned correct answers with fewer transmitted bits and lower total cost than the learned system throughout the tested workload range. [Frozen study design](preregistration.md) · [Results by wiring](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/result.json)

## What changed when one wire moved

The sender sees nine source bits and four public questions about them. It sends three or four question answers before it knows which question the receiver will be asked. Both parties see the wiring. The receiver sees only the packet as evidence of the actual source values. The sender can choose any answer to omit, and the decoder can combine the retained answers using NAND gates. [Packet rules](../../experiments/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/contract.json)

One layout asks for `p = a OR (b AND c)`, `q = a OR (b AND NOT c)`, `r = d`, and `z = a XOR d`. Whenever `a` is true, both `p` and `q` are true. When `a` is false, making both true would require both `c` and `NOT c`. This gives `p AND q = a`, so the receiver can compute `z = (p AND q) XOR r`. It can also recover `r = (p AND q) XOR z`. All eight combinations of `p, q, r` actually occur. Changing the last question to `z = e XOR d` introduces an independent source. All sixteen four-answer patterns then occur, making four bits necessary. [Question definitions](panels.py)

| Frozen choice on the primary pair | Original wiring | One source changed |
| --- | ---: | ---: |
| Number of layouts | 24 | 24 |
| Minimum packet | 3 bits | 4 bits |
| Packet chosen before checking | 3 bits on 24/24 | 4 bits on 24/24 |
| Correct delayed answers | 49,152/49,152 | 49,152/49,152 |
| Same policy limited to one learned operation | 4 bits on 24/24 | 4 bits on 24/24 |

Across all 24 question orderings, with shuffled clauses and recoded sources, the sender omitted `z` twelve times and `r` twelve times. The missing answer took seven NAND gates, two for AND and five for XOR. A decoder assuming that all four answers have even parity would satisfy only 128 of 512 inputs per original layout. The experiment covers one new nonlinear answer relation in all question orders. A separate four-layout set kept that relation while changing which source occurrences the first two questions shared. The learned policy selected the correct three or four bits on both sides of all four of those pairs, and also on four previously studied parity pairs. [Recorded proposals before checking](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/raw_proposals.json)

## What the examples taught

The training data gave four terminal answers on each of 256 even-parity inputs for each of 32 other wirings. The search chose among 3,480 combinations of a NAND-defined library and a probe count. It retained AND, OR and XOR, and selected 32 hypothetical inputs for inspecting a new wiring. It made zero errors on the 32,768 supplied training answers. The primary nonlinear relation and the held four-way parity relation were both absent from training, even after permuting the answer order and complementing any subset of the four answers. [Training record](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/results.jsonl) · [Frozen checkpoint](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/checkpoint.json)

The experiment supplied a catalogue of all 16 binary Boolean functions implemented in NAND, the limit of three retained functions, a search over circuits with up to two calls, and the previously learned parser for public questions. At each new wiring, both endpoints separately tried candidate circuits against the parser's predictions on the 32 hypothetical inputs. Neither the omitted port nor the target reconstruction was a training label. The reproducible capability is selection and composition under this supplied search. Its per-wiring computation is included in the cost comparison. [Learner](../../experiments/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/learner.py) · [Source and panel bindings](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/freeze.json)

## What the correctness check caught

A three-bit proposal was recorded before either certification or grading. Each endpoint then checked it against its public parser on every possible input. If any input failed, both used four bits. An independently implemented grader checked all four delayed questions on all 512 actual inputs to every wiring, including all 91,136 questions on odd-parity inputs. The exact compiler used the same parser and examined all four possible omissions. When a triple determined the fourth answer, it cached an eight-entry lookup table. Copying all four answers provided a second exact baseline. [Bound plans](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/plans.json) · [Compiler and checker](../../experiments/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/compiler.py)

| Method | Correct delayed answers out of 182,272 | Completely correct wirings | Wirings using 3 bits | Bits for one packet on each of 89 wirings |
| --- | ---: | ---: | ---: | ---: |
| Frozen proposal before checking | 182,048 | 83/89 | 42 | 314 |
| Frozen proposal after checking | 182,272 | 89/89 | 36 | 320 |
| Exact cached compiler | 182,272 | 89/89 | 44 | 312 |
| Send four answers directly | 182,272 | 89/89 | 0 | 356 |

The six incorrect omissions produced 224 wrong answers. Three layouts with an AND/OR dependency and one with a rare conjunction each failed on 32 inputs. Two multiplexer layouts each failed on 48 inputs. All six were on wirings where a suitable three-bit encoding really did exist. Two more multiplexer layouts went directly to four bits. These eight layouts account for the entire gap in packet size between the certified learner and the compiler. The compiler certifies its choice while building its lookup table. [Per-wiring errors and exact widths](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/result.json)

One further wiring had exactly eight possible answer patterns. Each choice of three existing answers mapped two distinct patterns to the same packet. Both exact protocols consequently sent four. A sender free to give each of the eight patterns its own three-bit code could use three. The learned system used the best exact choice of three or four existing answers on 81/89 wirings and met the unrestricted information minimum on 80/89. The compiler reached 89/89 and 88/89, respectively. [Information bounds and possible omissions](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/result.json)

## Total cost of returning a correct answer

The timings below use process CPU on this host. Setup includes independently making and checking a plan at each endpoint for all 89 wirings. A use means sending a fresh packet and answering one subsequently requested question on **each** wiring. CPU medians use three fresh process pairs per method and 128 balanced, distinct input/query events per wiring per pair. The physical parser was available to all arms. Only the learned arm incurred a new fit and transferred a new 980-byte checkpoint once. Public plans were cached. Actual packets and answers were computed anew. [Raw timing and transfer model](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/costs.json)

| Exact method | New fit | Both endpoints' setup | Warm CPU per use of each wiring | Data bits per use of each wiring |
| --- | ---: | ---: | ---: | ---: |
| Certified learner | 7.073 s | 428.8 ms | 1.303 ms | 320 |
| Cached compiler | 0 | 20.85 ms | 1.322 ms | 312 |
| Direct four answers | 0 | 4.84 ms | 1.487 ms | 356 |

Across all 20 predeclared combinations of use counts (1 through 65,536 per wiring) and transfer prices (0, 1, 10 or 100 microseconds per bit), a baseline was cheaper. For example, at 256 uses and 10 microseconds per bit, the projected totals were **8.73 s** for the learner, **1.16 s** for the compiler and **1.30 s** for direct transmission. Direct transmission won at one use for all four prices. The compiler won at 256 and above for all four. Transfer prices and repeated-use totals are modeled. Planning, certification and per-packet CPU were measured. [Cost measurement code](costs.py) · [All operating points](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/costs.json)

The warm CPU ranges overlapped for the learner (1.301–1.336 ms) and the compiler (1.298–1.350 ms). Extrapolating only the medians gives a first crossover at 384,571 uses per wiring for free transfer and 653,871 at one microsecond per bit. Both lie beyond the tested range, and the small difference in warm CPU changes sign across runs. At 10 and 100 microseconds per bit the fitted cost lines give no crossover. The evidence supports reuse of a learned operation on an unseen dependency. An end-to-end saving on this workload remains unestablished. [Measured ranges and projected crossovers](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/costs.json)

## Reproduction

The independent replay reproduced 445 wiring-and-method outcomes, covering 911,360 delayed answers across the five methods. It verified the selected training loss, the saved ranking, the counterexamples, and the cost arithmetic from all 18 timed endpoint runs. It used its own Boolean evaluator, NAND and lookup executors, and reconstruction of the frozen candidate search. The other 3,479 training candidates retain their original recorded losses. From the repository root, the following command checks these records without repeating the fit or timings. [Independent audit](../../artifacts/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/audit.json) · [Audit implementation](audit.py)

```sh
.venv/bin/python -B research/ANSWER-COMPOSE-20261115-001/audit.py
```

To repeat the full experiment in a fresh directory, use these commands from the repository root. The fit, raw proposals, checked plans and grader run in that order. CPU observations depend on the host. [Training entry point](../../experiments/ANSWER-COMPOSE-20261115-001/ANSWER-COMPOSE-20261115-001-E001_packet_nand/job.py) · [Evaluation entry point](assess.py)

```sh
s=ANSWER-COMPOSE-20261115-001
f=${s}-E001_packet_nand
out=$(mktemp -d)
.venv/bin/python -B "research/$s/assess.py" sources --out "$out"
.venv/bin/python -B scripts/longrun.py launch "experiments/$s/$f/job.py" --out "$out" --unit answer-compose-replay --workers 1 --case-timeout 1200 --case-mem 4G --mem-max 5G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$out" --foreground --limit 1
for step in freeze propose compile grade
do
  .venv/bin/python -B "research/$s/assess.py" "$step" --out "$out"
done
.venv/bin/python -B "research/$s/costs.py" benchmark --out "$out"
.venv/bin/python -B "research/$s/audit.py" --out "$out"
```
