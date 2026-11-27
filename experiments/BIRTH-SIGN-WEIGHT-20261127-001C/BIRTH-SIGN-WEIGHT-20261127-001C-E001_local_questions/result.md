# Two fixed questions from the allowed changes of each sibling

The two siblings receiving 0 from the fixed founder 001 can each take the values 01, 10 and 11. No knot joins these readers on this prepared support. Under the chosen joint weighting, the nine pairs of words have probability 1/12 each except for 11 with 11, which has probability 1/3. Two preparations can have exactly this same table of values. Giving each pair of words a coherent positive amplitude equal to the square root of its probability yields a two-reader CHSH score of **2.1078403054**. Mixing the nine words with the same probabilities gives **0** with those same questions. The common-list limit is 2. [Joint weighting and support](../../BIRTH-SIGN-WEIGHT-20261127-001B/BIRTH-SIGN-WEIGHT-20261127-001B-E001_joint_weights/results.md)

## How the questions were chosen

Flipping either fresh distinction exchanges two allowed words and leaves the third where it was if the proposed change is forbidden. Let $Z$ answer whether the fresh values agree. For $X$, sum the two matrices of permitted flips, remove the stays and take the sign of each eigenvalue. For $R$, reflect about the uniform vector, the common fixed vector of the two flips. The first reader uses $X$ or $Z$, and the second uses $-ZRZ$ or $R$. These choices were made with the target in view. Their entries are fixed by the three allowed words, with either choice of sign on the zero eigenvalue. Measuring the projectors of these operators and preparing coherent amplitudes are additional rules. [Pre-run predictions](../../../research/BIRTH-SIGN-WEIGHT-20261127-001C/preregistration.md)

In the basis consisting of 11 and the equal-amplitude sum of 01 and 10, $X$ exchanges these two states and $R=(2\sqrt{2}X-Z)/3$. The four correlations are $2\sqrt{2}/3,2\sqrt{2}/3,1/9,-1/9$. Adding the first three and subtracting the fourth gives $(2+12\sqrt{2})/9$. Each local answer distribution is independent of the other reader’s choice. The exact calculation covers all 16 joint answers per preparation, all six local name orders, complementary founder values and both zero-eigenvalue conventions. [Exact tables](../../../artifacts/BIRTH-SIGN-WEIGHT-20261127-001C/BIRTH-SIGN-WEIGHT-20261127-001C-E001_local_questions/results.json)

| Same four questions, different preparation | CHSH |
| --- | ---: |
| Coherent positive square roots of the joint weighting | 2.107840 |
| Fully mixed over named words, same probabilities | 0 |
| Mixed only between equal and mixed classes | 0.222222 |
| Independent coherent siblings, same local word probabilities | 1.885618 |
| Product preserving each reader’s entire local state | 1.676105 |
| Coherent reinforcing weighting preserving ordinary one-birth probabilities | 1.939424 |

The pre-run prediction of $2/9$ for the full mixture failed. That value applies when the two orders 01 and 10 still combine coherently. Against a fully named mixture, the coherent fraction must exceed 94.8838% for these questions to beat 2. Against the class mixture it must exceed 94.2809%. Reversing the zero-eigenvalue convention changes individual probabilities in the full mixture by up to 1/6 and preserves its score of 0. [Independent calculations](../../../research/BIRTH-SIGN-WEIGHT-20261127-001/review/report.md)

Replacing $X$ by either available one-bit toggle gives 2, even with the coherent preparation and the same two questions on the other side. The independent check also maximized over all 20 two-outcome signed permutations of the three words per reader and obtained 2. The step that exceeds 2 is a measurement combining permitted changes. The uniform reflection has an exact counterpart in the literature. Here its coefficients come from the current local words. [Grover](https://arxiv.org/abs/quant-ph/9605043)

## Reproduction

From the repository root, run the following command, adding `--pilot` for the first correlation only. That pilot took 0.27 seconds and used 51,960 KiB. The full exact calculation took under two seconds under a 1 GiB memory cap with one computation thread. The independent calculation uses the full named-word basis and its own diagonalization. [Implementation](local_questions.py) · [Contract](contract.json)

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 prlimit --as=1073741824 -- .venv/bin/python -B experiments/BIRTH-SIGN-WEIGHT-20261127-001C/BIRTH-SIGN-WEIGHT-20261127-001C-E001_local_questions/local_questions.py
```
