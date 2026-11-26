# Four detector settings on one parity knot

One even-parity knot specifies four possible words. Preparing them coherently and applying a particular pair of quantum measurements gives the full three-particle Greenberger–Horne–Zeilinger (GHZ) prediction. Reading a definite word, even with shared randomness and a separate choice at each detector, wins at most three quarters of the equally weighted scored trials. The difference survives a comparison of preparations that agree on every ordinary word probability.

This is a reconstruction of a known quantum result. The workspace's November 21 archive already contains the successful quantum calculation. Its ordinary value read and quarter-turned change were the sole pair among 21 tested on the even-parity preparation to attain the signed score of 4. The earlier correction about a score of 3 applies to a different preparation, the six allowed words of not-all-equal. The present study identifies the four-setting experiment in the archive, computes its full distributions independently, and tests the ordinary parity alternative on those same terms. [Prior archive](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A/observations.json.gz) · [Earlier signed-score comparison](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001/phase_comparison.md) · [Mermin's three-detector argument](https://physics.umd.edu/courses/Phys622/bedaque/mermin.pdf)

## What is being compared

Three detectors each receive one independently chosen fair bit telling them which of two measurements to make. Each returns a bit. All trials count. The four setting triples with an even number of ones are scored, equally. A run wins when the parity of the three answers is even at 000, and odd at 011, 101 and 110. The target gives each allowed answer triple probability 1/4. At each of the other four settings all eight answers have probability 1/8.

The ordinary relation allows 000, 011, 101 and 110. It passes K1–K3 under forgetting. Every pair of bits can take every value and the whole obeys even parity. For the ordinary sample, assign each word weight 1/4. The quantum comparison assigns each of the same words the real amplitude 1/2, then uses the ordinary value measurement Z for setting 0 and the quarter-turned flip Y for setting 1. At each reading the joint probability is the squared magnitude of the projection. In conventional notation the resulting state is the standard three-particle GHZ state with a Hadamard applied to each particle. The two local questions and the probability rule are supplied. [Existing measurement definition](../THREE-READERS-AND-GROWTH-20261120-001A/readings.md) · [Calibration menu](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A/reader_tables.py)

| Reading or preparation | Chance of winning a scored trial | Full outcome distributions |
| --- | --- | --- |
| Coherent preparation, Z or Y | 1 | All four scored and all four unscored settings match. |
| Incoherent mixture of the same words, Z or Y | 5/8 | At each two-Y setting the target assigns zero to four outcomes. The mixture gives each of them 1/8. |
| Same coherent preparation, Z or unturned X | 5/8 | At a two-X setting the two X answers agree. The target allows both equal and unequal pairs. |
| Best ordinary local answers, with setting-independent shared randomness | 3/4 | An optimal mixture places total probability 1/4 on forbidden words at every scored setting. |

One way to see why the quantum calculation works is to change two bits together. This exchanges pairs of even words, leaving their equal coherent sum intact. The product of the ordinary sign on the remaining bit and the two Y measurements acts on that sum as minus this exchange. The mixed settings therefore have odd answer parity. Measuring all three ordinary signs gives even parity. The calculation of every probability also checks the pair marginals. A single bit flip takes an even word to an odd word. The allowed words by themselves specify neither individual phase-sensitive measurements nor probabilities for their outcomes.

## What any ordinary local reading can do

For each prepared trial, preassign two potential answers to each detector, one for each local setting. Multiplying the four requested sign products counts each preassigned answer twice and gives +1. The four target signs multiply to −1. Thus each list fails at least one setting, and weighting such lists independently of the settings preserves the 3/4 bound. This reasoning permits arbitrary shared randomness. It requires that each returned answer depend only on its local setting and the prepared information.

Exactly 32 of the 64 lists win three settings, and 32 win one. Weight the 32 three-win lists equally. At every scored setting, each allowed word gets 3/16 and each forbidden word gets 1/16. The total variation distance from the target, half the sum of the absolute probability differences, is exactly 1/4 per scored setting. The parity bound proves that no local mixture can lower its average below 1/4. At the four unscored settings this mixture matches all probabilities.

The narrower one-knot check assigns each detector a Boolean function of its setting and its own bit of the ordinary word. Among all 4,096 triples of such functions, 3,232 match zero complete scored tables, 736 match one, 96 match two, and 32 match three. For an attainable example let A and B report their bits, and let C reverse its bit on setting 1. This reproduces the entire output distribution at 000, 011 and 101. It gives even parity at 110 when the target requires odd.

## Could the settings be further distinctions in one fixed parity system?

Combining any three solutions of fixed binary parity equations bit by bit, modulo two, gives another solution. The same is true after forgetting auxiliary bits, since their three witnessing assignments can also be combined. Requiring the three setting bits to have even parity is itself one such equation.

Write the three settings before the three answers. The desired relation contains `000|000`, `011|001` and `101|001`. Their sum is `110|000`, which the target forbids. Hence no fixed finite system consisting solely of parity equations produces the required joint support on the named inputs and outputs, even with hidden bits and signed parities. A setting that changes which laws operate, or a reader with a different outcome rule, is outside this argument.

Giving a device access to the combined settings makes the distinction concrete. It can choose the first two answer bits fairly and set the third to give the requested parity. Every pair then has the quantum marginals, although the device was supplied the parity to enforce. The full table establishes the statistics. The physical account also has to explain what information and operations the detectors can actually use.

## Relation to Carroll

Carroll starts from unitary quantum dynamics. His energy spectrum specifies the dynamics in the proposed description, and a particular state supplies the initial condition. He asks how one can identify subsystems and recover spatial nearness from their entanglement. Prespatial starts with rules on allowed joint states and asks what makes a first intrinsic contact possible. The detector example shows precisely how a logical pattern can participate in a quantum model. Its open step is obtaining the coherent preparation, measurements and probability rule from the logic's own operations. Carroll's paper concerns the emergence of spatial structure from quantum physics. The detector predictions tested here are the standard GHZ predictions. [Carroll, *Reality as a Vector in Hilbert Space*](https://arxiv.org/abs/2103.09780) · [Prespatial, *Locality before space*](https://prespatial.org/intuitions/locality-before-space)

## Reproduce

From the repository root, run

```sh
python3 -B artifacts/FOUR-SETTINGS-PARITY-20261125-001/FOUR-SETTINGS-PARITY-20261125-001-E001_four_settings/check.py --check
python3 -B research/FOUR-SETTINGS-PARITY-20261125-001/verify_comparison.py
PYTHONPATH=tools python3 -B -m knotlab check --cnf 'A B ~c; A ~B c; ~A B c; ~A ~B ~c' --loops A B --contact c
```

The replay uses integer arithmetic for the squared amplitudes and reproduces the stored probabilities byte for byte. It rejects a mutation that reverses the required parity at 011. A separate comparison against the earlier implementation agrees on all 64 Z/Y and 64 Z/X probabilities after reconciling the order of the bits. The three-word witness checks the fixed-parity obstruction. These are exact finite and analytic comparisons within the specified models, with same-task independent checks. The work stops at the source of the individual measurement. [Probability tables and local witnesses](../../artifacts/FOUR-SETTINGS-PARITY-20261125-001/FOUR-SETTINGS-PARITY-20261125-001-E001_four_settings/results.json) · [Frozen comparison](preregistration.md)
