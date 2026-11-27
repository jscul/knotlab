# A sign from what each parent leaves free

On the old three-parent ring, each parent leaves exactly one nonzero allowed change invisible. Using its loose value to sign that change gives an odd close in all 48 combinations of eight old words and six parent orders. The ordinary birth on the same ring closes even. A reader choosing between the values of its two distinctions scores 3/4 on the fixed odd target under either preparation. The full three-reader table can also be read using only the two distinctions of each reader if each is supplied with coherent questions that can individually take an old word outside the allowed set.

## What the birth can determine

Call the shared distinction that parent \(i\) does not hold \(s_i\), and its loose distinction \(l_i\). Its old even law says \(l_i=s_j+s_k\), where sums are modulo two. The three shared values determine exactly eight old words. Fixing the whole view of parent \(i\) leaves only \(s_i\) free. Its unique nonzero invisible change \(T_i\) flips \(s_i,l_j,l_k\). This construction needs only the three old laws and the loose distinctions in the proposal. All three changes carried over correctly under all 720 renamings of the six distinctions.

The rival signs a step by the current loose value, then performs the change. It asks for a relative amplitude \(f\) satisfying

\[
f(s+e_i)=(-1)^{l_i(s)}f(s),\qquad
f(s)=(-1)^{s_0s_1+s_1s_2+s_2s_0}
\]

up to one common factor. Changing \(s_i\) changes the exponent by \(s_j+s_k\). The three changes can reach every old word, giving uniqueness up to the common factor. In any order each earlier change reverses the sign of each later loose read. The three pairs give a minus relative to reading all three loose values on the original word, where their sum is even. The calculation also checked 192 parent equations after translating the values by each allowed old word.

Each proposed input \((l_0,l_1,l_2)\) has two preimages, \(s\) and its complement. They have opposite relative amplitudes. For example the ordinary input 000 receives both 000 with sign plus and 111 with sign minus in the shared coordinates. A birth limited to its actual input values cannot recover the amplitude of its parent word. The sign comparing the pair is fixed by the rival's transport equation. The ordinary birth checks implication for its input parity and imposes no transport equation.

## What the reader can distinguish

The fixed target has even parity when one reader chooses its second question, and odd parity when all three choose it. These four settings have equal weight for the score. The four other settings have eight equally weighted answers each. Every preparation below gives probability 1/8 to each old word when values are read. An entry gives the score and the number of matches among all 64 probabilities.

| Preparation | Read the values \(s_i,l_i\) | Read \(Z_{s_i},T_i\) on the eight allowed words | Coherent questions confined to \(s_i,l_i\) |
| --- | --- | --- | --- |
| Signed state determined by the transport equation | 3/4, 56 | 1, 64 | 1, 64 |
| Uniform mixture of the same eight words | 3/4, 56 | 1/2, 32 | 1/2, 32 |
| All eight amplitudes positive and equal | 3/4, 56 | 3/8, 23 | 3/8, 32 |

Here \(Z_v\) reads a value as its sign and \(X_v\) flips the value. In the middle column the changes preserve all old laws. Each \(T_i\) flips two loose distinctions outside reader \(i\)'s pair. For an old-parent setting, the distinctions named in the question are its own loose distinction and the other two readers' shared distinctions, all three held by that parent. The actual change acts entirely outside that parent's places. No nonzero allowed change is supported on any one reader's pair. More generally, two distinct old words always differ outside such a pair. Any linear operator confined to the pair that preserves the allowed-word subspace acts diagonally on that subspace.

The referee proposed a distinct control that keeps the changes and moves the signs. Multiplication by the phase \(f(s)\) carries the equal-positive state into the signed state, leaves each value question fixed and carries the plain shift \(X_i\) into the signed shift \(X_i Z_{s_j}Z_{s_k}\). The equal-positive state with these rephased questions reproduces **all 64** entries of the winning table. With the same rephased questions the signed preparation scores 3/8 and the mixture scores 1/2. In both coherent descriptions the product of the four context operators is \(-I\). In the first, the three old-parent products are signed shifts and the closing question is the product of the plain shifts. In the other the old-parent products are plain shifts and the closing question is minus their product. This is a change in both the preparation and what the second question means. Removing the change altogether gives the ordinary-values column. The fixed-target controls establish what a given reader and preparation can see. They leave freedom over where the signs enter a coherent description.

The last column tests a further rival found after the first exact run. Reader \(i\)'s first question is \(Z_{s_i}X_{l_i}\), and its second is \(X_{s_i}\). Each acts only on the reader's pair. Individually each sends all eight allowed words outside the old relation. In a scored joint question with one reader using its second setting, the combined flip is precisely \(T_i\) with sign \((-1)^{s_j+s_k}\). At the close all three shared bits flip, preserving the loose input and reversing the signed amplitude. These questions use operators on the full six-bit space with zero initial amplitude on its forbidden words. The ordinary reader cannot implement them by choosing between its two existing values. Changing the sign of every amplitude together leaves every probability unchanged under both coherent readings. A separate direct calculation with 64-component integer vectors matched all 192 probabilities in the last column.

## One more parent

Both fixtures give a single closing proposal with no fresh distinction in the ordinary engine used by the archived [three-parent study](../../../research/NO-WHOLE-STATE-20261126-001/README.md#c-the-advisors-fixture-growths-smallest-closure-carries-the-three-reader-contradiction-fixturepy). With four parents each sharing one distinction with every other and each holding one loose distinction, seven nonzero allowed changes leave any one parent's view fixed. Exactly one survives every permutation of the other three parents. It flips the three shared distinctions outside that parent's places and leaves every loose value fixed. The same signed transport gives an even close for all 1,536 combinations of 64 words and 24 parent orders. The earlier rule that declares every unheld pair incompatible on the finished five-knot pattern gives odd. On the three-parent example the two rules give the same three exchange pairs. This comparison identifies where they first differ among the two fixtures studied. [Earlier operator witnesses](../../../research/NO-WHOLE-STATE-20261126-001/README.md#d-is-the-even-closing-sign-entailed-or-assumed-values_commutepy)

The construction fixes the exchanges before these proposals and uses them through the close. Their history before the specified starting parents and a law for general growth remain open. The native data specify the paired flips on the three-parent fixture. Using a loose value as the sign of transport, preparing a coherent state, and reading a change are choices a rival must account for. More than one placement of the signs yields the same table.

## Reproduction

From the repository root run the following. Omitting `--output` prints the same scientific record. `--pilot` restricts the parent order and skips the 720 distinction renamings.

```sh
ulimit -v 1048576
OPENBLAS_NUM_THREADS=1 .venv/bin/python -B \
  experiments/BIRTH-SIGN-WEIGHT-20261127-001A/BIRTH-SIGN-WEIGHT-20261127-001A-E001_closing_sign/run.py \
  --output artifacts/BIRTH-SIGN-WEIGHT-20261127-001A/BIRTH-SIGN-WEIGHT-20261127-001A-E001_closing_sign/results.json
```

The initial pilot took 0.007 seconds after import. Each ordinary proposal took about 0.00023 seconds, and 30 parses of renamed inputs took 0.00039 seconds. The retained run took 0.043 seconds after import, with peak process usage reported as 455,348 KiB under the 1 GiB cap. The run's [exact probabilities and controls](../../../artifacts/BIRTH-SIGN-WEIGHT-20261127-001A/BIRTH-SIGN-WEIGHT-20261127-001A-E001_closing_sign/results.json) include the first-sign and total timings. These are exact finite calculations in an exploratory study.
