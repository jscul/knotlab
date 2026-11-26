# A real signed knot gives the four three-reader predictions

One real sign law already tested by Prespatial in October gives every probability in the four-setting GHZ experiment. A two-bit factor from the same month's signed-witness work supplies a real measurement kernel. Two documented preparations also give opposite signs with certainty on one fixed reading while agreeing on their entire ordinary distribution. The construction specifies which factors to join, which joint value to read out, and how to weight surviving outcomes. The canonical allowed words alone leave all three choices open. [October signed laws, Proposition 5](../../proofs/INTERFERENCE-20261029-001B/INTERFERENCE-20261029-001B-P001_signed_laws_survive_native_coarse_graining/proof.md) · [Earlier signed pair factor](../../proofs/INTERFERENCE-20261029-001A/INTERFERENCE-20261029-001A-P001_one_cancelling_witness_per_knot/proof.md) · [Fixed benchmark and its local bound](../FOUR-SETTINGS-PARITY-20261125-001/results.md) · [Mermin's three-reader experiment](https://physics.umd.edu/courses/Phys622/bedaque/mermin.pdf)

## What the two preparations change

In the ordinary reading there are four equally weighted words, in order **000, 011, 101, 110**. These pass the canonical K1–K3 test with the first two distinctions as loops and the last as contact. On these words the original one-witness sum gives `++++`. Its two terms add on every even word and cancel on every odd word. October's separate coarse-graining proof explicitly studied both symmetric sign choices, `++++` and `+---`, as well as `+++-`, a minus on the one word whose first two bits are both 1. These are older inputs to the present test. The original November root-of-unity weighting for even parity is positive. [Signed witness sum](../../proofs/INTERFERENCE-20261029-001A/INTERFERENCE-20261029-001A-P001_one_cancelling_witness_per_knot/proof.md) · [Two symmetric laws and one-pair control](../../proofs/INTERFERENCE-20261029-001B/INTERFERENCE-20261029-001B-P001_signed_laws_survive_native_coarse_graining/proof.md) · [November prescription](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001/phase_comparison.md)

Setting 0 reads a reader's own bit. Setting 1 uses the same real two-bit factor at every reader. All three ordinary reads must give even parity. With exactly two changed reads, the target is odd parity. Each of these four settings permits four equally weighted outcomes. The other four settings permit all eight outcomes equally. “Win” is the chance of the required parity on the four equally weighted scored settings. An exact cell includes its probability, including zero.

| Preparation and changed read | Win | Exact cells out of 64 |
| --- | ---: | ---: |
| Symmetric `+---`, real flip X | 1 | 64 |
| Witness-summed `++++`, same X | 5/8 | 44 |
| Single-pair `+++-`, same X | 1/2 | 48 |
| `++++`, quarter-turned Y | 1 | 64 |
| `+---`, same Y | 5/8 | 44 |
| Relative signs erased by mixing the four words, X or Y | 5/8 | 40 |

For example, fix setting **011** before choosing the source. Read the first bit ordinarily and change the readings at the other two. With `+---`, all four **odd** outcomes have probability 1/4. With `+++-`, all four **even** outcomes have probability 1/4. Both preparations yield exactly the same distribution at **000**. Even the all-positive coherent control behaves differently from erasing coherence. Its two changed readers always agree at 011, while erasing coherence gives all eight outcomes equal weight. [Full tables and local controls](../../artifacts/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001-E001_signed_tables/results.json)

## Building the real read from an earlier factor

The signed counting rule adds contributions of hidden distinctions and multiplies the factors of a joint assignment. Use the archived two-bit factor $F(x,y)=(-1)^{xy}$, which is negative only at $(1,1)$. Joining two copies in succession gives $\sum_h F(x,h)F(h,y)=2[x=y]$, an ordinary read up to a common scale. One copy mixes both possible values of the input into each output. After normalization these two arrays give the standard Z and X readings. The integer calculation uses their entries directly, with no complex numbers.

The same factor constructs the signed source with no new sign entries. For $w=(a,b,c)$,

$$
2T_-(w)=\left[\sum_{h=0}^1 F(h,a)F(h,b)F(h,c)\right]F(a,b)F(a,c)F(b,c).
$$

The bracket is 2 on even parity and zero elsewhere. The three final factors together are +1 at 000 and −1 at every two-one word. Omitting those factors gives the positive source. Using only $F(a,b)$ gives the single-pair source. The wiring is a preparation choice. The finite test keeps the same readers and output labels throughout.

At setting 011 and output 001, the possible source words are 000 and 011. With the signed source their contributions are $1$ and $(-1)(-1)=1$. With the positive source the contributions are $1$ and $-1$. The first sum gives probability 1/4 under squared projection. The second sum gives zero. This is the specific sense in which the archived signs can act as amplitudes. [Direct integer contractions](verify_laws.py)

Among all 16 equal-magnitude real assignments, only `+---` and its overall negative match every cell with fixed X. With fixed Y only `++++` and its overall negative do so. Independent projection and moment calculations agree on all 2,048 cells. Simultaneously changing the preparation and the two read bases by the same local calibration leaves every outcome probability unchanged. In quantum notation, $D=\operatorname{diag}(1,-i)$ transforms the positive state into the signed state when used at all three readers, leaves Z fixed and sends Y to X. [Exact census](../../artifacts/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001-E001_signed_tables/check.py)

For the positive source with fixed ordinary Z, the three perfect mixed parities actually force Y up to one common reversal *if* each other reading is a local two-outcome projective measurement on that same two-dimensional signal. Conditioning on any ordinary bit being zero leaves the other two in the equal sum of 00 and 11. Their outputs must have product −1, so their two observables satisfy $Q_k=-Q_j^{\mathsf T}$. Applying this to all three pairs gives one common Hermitian $Q$ with $Q^{\mathsf T}=-Q$ and $Q^2=I$, hence $Q=\pm Y$. The sign comparison with X answers a different question by changing the source while keeping the ordinary readings the same.

## Which operations come from the ternary alone?

The October joined-copy rule requires each hidden distinction to occur in exactly two copies. Summing the even constraints modulo two cancels every hidden bit in pairs. The exterior has even parity in every contributing history, at every size. For two exterior bits this forces equality, so those joins alone cannot give a two-bit matrix with all four entries nonzero. This applies to the two named physical bits of a single reader. Broader encodings require their own preparation and decoding rules.

If one further permits summing one unused distinction of a single signed ternary *before* reading the final outcomes, that same law supplies both transfers. Two copies sharing two distinctions give $2I$. The open sum of one copy gives the array $\left(\begin{smallmatrix}1&-1\\-1&-1\end{smallmatrix}\right)$, a normalized read of $-X$. A common reversal of the changed outputs gives the same complete target table. An open sum with coefficients $(1,-1)$ gives $F$ itself. Keeping the summed mark as an ordinary record until after squaring instead gives 5/8. In the wider calculus where $F$ is already a primitive, the direct two-bit reader above needs no such open sum. [Alternative readers and retained-record control](../../artifacts/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001-E001_signed_tables/real_contractions.json)

There are concrete ways to distinguish the two symmetric sign laws independently of the GHZ target, but the choice of criterion matters. October's three closed-system scalar comparisons accepted both. Joining three copies so each pair shares one internal distinction gives twice the positive law and the zero array for the symmetric signed law. In the latter case the two completions of each even exterior have opposite signs. Conversely, ask that the real map obtained by summing one open bit against *any* nonzero pair $(u,v)$ be reversible. The signed map $\left(\begin{smallmatrix}u&-v\\-v&-u\end{smallmatrix}\right)$ squares to $(u^2+v^2)I$. The positive map $\left(\begin{smallmatrix}u&v\\v&u\end{smallmatrix}\right)$ is singular at $u=v$. This extra operational requirement selects the signed law from the two permutation-invariant choices. The earlier knot definition imposes no such requirement.

A restricted source obstruction also helps locate the additional sign. A single real two-valued witness with three independent attachments gives two products of three one-bit factors. For any such sum the determinant of its first slice plus $t$ times its second slice factors into two real linear forms, up to constant determinants from the other two attachments. For $T_-$ the slices are Z and $-X$ and this determinant is $-1-t^2$. Thus the simple witness by itself cannot give this preparation. The three documented visible pair factors in the construction above change that conclusion.

## What can be inferred about probabilities?

Within every successful setting the surviving signed sums have a common magnitude. Equal weighting on the nonzero outcomes, normalized absolute weight and normalized squared weight give exactly the same 64 probabilities. Signed counting already specifies which histories cancel. The weighting of survivors remains an explicit choice.

The old unequal-magnitude control exposes the difference. Give 000 coefficient 2 and the three other even words coefficient 1. The three prescriptions give the ordinary outcome 000 probabilities **1/4**, **2/5**, and **4/7**, respectively. When the other two readers switch to the same real factor, the chance that the first ordinary bit is zero changes from 1/2 to 2/3 under uniform support, from 3/5 to 2/3 under absolute weight, and stays at **5/7** under squared weight. Requiring that an untouched reader's probability be independent of the other settings distinguishes these three prescriptions on this control. Uniqueness of a probability law over all possible prescriptions is a further question. [Magnitude control in the original proof](../../proofs/INTERFERENCE-20261029-001B/INTERFERENCE-20261029-001B-P001_signed_laws_survive_native_coarse_graining/proof.md) · [Exact fractions](../../artifacts/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001-E001_signed_tables/real_contractions.json)

## Replay

This is a known-answer algebraic experiment. It tests an existing mathematical construction against a benchmark, with no observed detector frequencies. A four-source prefix took 0.0124 seconds in the primary checker. The complete run took 0.17 seconds and used less than 15 MiB. The direct real-factor follow-up took less than a tenth of a second. The signed-support semantics is an extension of the ordinary existential reading. [Original design](preregistration.md) · [Follow-up design](reader_check_plan.md)

```sh
id=WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001
family="artifacts/$id/${id}-E001_signed_tables"
PYTHONPATH=tools python3 -B -m knotlab check --cnf 'A B ~c; A ~B c; ~A B c; ~A ~B ~c' --loops A B --contact c
python3 -B "$family/check.py" --check
python3 -B "research/$id/verify_laws.py" --check "$family/real_contractions.json"
```

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| Earlier signs as amplitudes | Successful | The signed law with fixed real readers matches 64 of 64 cells |
| A reader from the knot's rules | Conditional construction | The signed pair calculus supplies both real kernels |
| Autonomous preparation and measurement | Unresolved | The wiring and the setting switch are supplied |
| G5 Dynamics and G9 Witnesses | Capability gained | Real witness factors can prepare and read a relative sign |

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A knot process makes and records the relative sign | 3/3 — Barrier | 1/3 — Stated | Identify one existing selection rule → obtain preparation and switch without fitting | Alternative · deferred |
| 2 | Vary the angle of the same reader | 1/3 — Incremental | 3/3 — Ready | Scan local angles → stop at a new selection criterion | Alternative · deferred |

**STOP.** The finite sign question and the follow-up on the source of the real reader are settled under their declared rules. An independent operation that selects the preparation and implements its measurement would move G5. No such selection follows from the two archived criteria compared here. The two-dimensional reader on the positive source is already fixed up to common reversal by the perfect target. Another angle scan would leave the preparation choice open.

**Corrections:** None. The earlier four-setting result uses the positive source and a specified quarter-turned read.

**Goals:** G5 Dynamics and G9 Witnesses gain a conditional signed construction. Sub-goal B243 records the gap between signed counting and a physical record.

**Assumptions:** A271 and A272 record the preparation, reading and open summation choices. A144 gains the unequal-magnitude test.

**Scaffolds:** Selection of the preparation and detector attachments, coherent summation and weighting of surviving outcomes. The controls change each of these choices.
