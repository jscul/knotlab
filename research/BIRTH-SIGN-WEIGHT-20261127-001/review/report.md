# Independent check of the birth sign and the sibling readers

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the sign and two sibling readers | **Status:** Successful | Independently reproduced the operational comparisons and found a failed control prediction |
| Local direction — fixed questions on permitted changes | Bounded test complete | One coherent preparation gives CHSH 2.1078403054 |
| Broader exploration — readers available to growth | Unresolved | The preparation and projective questions are supplied |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | A present birth supplies the weights and move possibilities under the rival rule |

**Next step:** Research directions — no further action within this independent check.

| # | Direction | Payoff | Concreteness | First step → stop when |
| --- | --- | --- | --- | --- |
| 1 | A reader made by growth | 3/3 | 1/3 | State one permitted operation that preserves and compares amplitudes → an operational witness or an access obstruction |
| 2 | Convert the present comparisons | 2/3 | 3/3 | Use the complete tables and both dephasing controls → every supplied operation is named |

**Corrections:** The pre-run prediction of 2/9 for the named-word diagonal preparation failed. It holds when only the equal/mixed classes are dephased.  
**Goals:** Evidence for the parent epic's G18 checkpoint.  
**Assumptions:** The founder is prepared before either setting. The coherent square roots, their phases and the projective reads are choices.  
**Scaffolds:** Signed shifts, preparation phases, allowed local operators and the basis of dephasing were varied. These are independent calculations on the specified fixtures and weighting. The advisor was unavailable.

## The pre-birth sign

Give each parent one loose reading equal to the parity of its shared distinctions. On the three-parent ring each parent has precisely one nonzero allowed change invisible to it. It flips the opposite shared distinction and the other two loose distinctions. Multiplying each change by the sign of that parent's loose value produces a relative minus when all three are applied, against the same simultaneous unsigned change. Every application writes outside its assigned reader's two distinctions. On the four-parent ring the corresponding invisible choices number three per parent. When all four parents meet pairwise, they number seven. Each four-parent example has one nonzero choice fixed by every renaming preserving its parent, and the relative sign for those choices is plus.

Write the three shared bits as $s_0,s_1,s_2$, with $s_i$ opposite its parent. The phase $(-1)^{s_0s_1+s_0s_2+s_1s_2}$ conjugates the unsigned shifts to the signed ones while fixing every value read. With the positive uniform coherent preparation, the signed questions reproduce all 64 of the three-reader target probabilities. With unsigned shifts the same 64 are recovered by rephasing the preparation. Opposite value and shift anticommute in both choices, and the product over the four context operators is minus the identity in both choices. A sequence of value and shift measurements on the all-zero word shows the same order effect on both arms. Comparing two opposite orders coherently would require an added reference.

With supplied projectors acting only on each reader's two named distinctions in the 64-word space, the rephased preparation also gives the full target. Each separate one-bit flip in these projectors takes every allowed word outside the original support. With ordinary value questions all three phase choices give the same table. Seven preparation and reader comparisons matched the producer on **448 of 448 probabilities**, exactly. [Exact calculations and tables](results.json)

## Two stopping rounds and the sibling weights

The archived not-all-equal start with rules on 012, 0345 and 123467 has 164 allowed initial words. For every one of them, first-round probabilities from counting whole completions depend on the stopping round. On the initial word 11000000, three first-round completions have 3, 6 and 3 later completions. The event that the two inputs of the next join agree has weight 2/3 after one round and 1/2 after two. A single current kernel cannot give both marginals. [Archived input](../../FACTOR-WEIGHTS-20261126-001/referee-R1/part_a_full.json) · [Recount](results.json)

On the separate founder 001 the 27 fresh words divide into six classes of sizes 1, 2, 4, 4, 8, 8. Equal class weights give the two equal-input siblings weight 1/3 each for equal/equal and mixed/mixed, and 1/6 each for the other two combinations. One classical construction draws a common $q$ uniformly on $[0,1]$. Each sibling then independently receives an equal pair with probability $q$ or a mixed pair with probability $1-q$. Each mixed pair orders its two words by a fair independent choice. Under fixed 001 all 27 allowed words factor as a product of three local supports. Checking all 512 subsets finds no canonical knot. Across all six founders there are 162 allowed words and 11 knots, two of which join the two readers. One joins their four fresh bits with the third founder bit. The canonical command finds 30 of 32 five-bit patterns allowed and every one-bit deletion full. [Support and canonical checks](results.json)

## What reads the coherence

Under fixed 001, write $E=11$ and $M=(01+10)/\sqrt 2$. In the order 11, 01, 10 the named-word amplitude matrix has one entry $2/\sqrt{12}$ at 11/11 and eight entries $1/\sqrt{12}$. Each of the eight signed involutions respecting the exchange of the two fresh distinctions is diagonal on $E,M$. Including all 20 signed involutions with names distinguished introduces noncommuting questions. Both full families have maximum CHSH 2 on this state. The unrestricted two-dimensional coherent maximum is $2\sqrt{10}/3$.

The fixed projective questions derived from the actual one-bit changes give correlations $(2\sqrt2/3,2\sqrt2/3,1/9,-1/9)$. Either actual one-bit toggle in place of the spectral change question gives exactly 2. The reconstruction on named words matches **80 of 80** producer probabilities across five preparations, within $6\times10^{-16}$. All four setting pairs had matching local marginals under either remote choice. [Eigenvector calculation and tables](reader_results.json)

| Preparation | Fixed-question CHSH |
| --- | ---: |
| Coherent positive square roots | $(12\sqrt2+2)/9 \approx 2.1078403054$ |
| Diagonal over named words | 0 |
| Diagonal over $E,M$, retaining coherence within $M$ | $2/9$ |
| Coherent product with the same named probabilities at each reader | $4\sqrt2/3$ |
| Product of the actual local density matrices | $32\sqrt2/27$ |
| Coherent reinforcement preserving ordinary one-birth probabilities | $[4\sqrt2(1+\sqrt3)+2]/9 \approx 1.9394236912$ |

In the mixture of the coherent and named-diagonal preparations, the fraction coherent must exceed 0.94883848. With only $E,M$ dephased the threshold is 0.94280904. The fully named-diagonal preparation has positive weight on the antisymmetric state. Changing the sign assigned to that state moves an outcome probability by up to 1/6 while its CHSH remains zero. Every other tested preparation has the same table under both choices. [Pilots](pilot.json) · [Reader pilot](reader_pilot.json)

The initial samples projected under two seconds for each run. The full runs took under 0.2 seconds of measured calculation each, used one computation thread and stayed below 31 MiB peak resident memory under a 512 MiB cap. All probabilities in the first script use exact rational arithmetic. The second independently diagonalizes the actual move matrices and tests the printed formulas to $10^{-12}$.

Run both checks from the repository root.

```sh
python3 -B research/BIRTH-SIGN-WEIGHT-20261127-001/review/check.py
.venv/bin/python -B research/BIRTH-SIGN-WEIGHT-20261127-001/review/reader_check.py
```
